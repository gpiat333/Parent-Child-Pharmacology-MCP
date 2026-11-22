# Databricks notebook source
# MAGIC %md
# MAGIC # Mother & Child Health lakehouse: ingestion
# MAGIC Loads public NIH/NLM/FDA sources into Delta tables: PubMed, LactMed (Bookshelf), NIH RePORTER, DailyMed labels, openFDA FAERS.
# MAGIC **Needs outbound internet** from the compute (serverless or a cluster that allows egress to the hosts below).

# COMMAND ----------

dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "mother_child")
dbutils.widgets.text("ncbi_email", "your.name@gsa.gov")
dbutils.widgets.text("ncbi_api_key", "")  # optional; use a secret in real runs
dbutils.widgets.text("topics", "pregnancy,lactation,breastfeeding,pediatric")
CAT, SCH = dbutils.widgets.get("catalog"), dbutils.widgets.get("schema")
EMAIL, KEY = dbutils.widgets.get("ncbi_email"), dbutils.widgets.get("ncbi_api_key")
TOPICS = [t.strip() for t in dbutils.widgets.get("topics").split(",")]
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CAT}.{SCH}")

import time, re, requests
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DELAY = 0.11 if KEY else 0.35  # stay under NCBI rate limits
S = requests.Session(); S.headers["User-Agent"] = "mcp-mother-child-ingest/0.1"

def eutils(endpoint, **p):
    p.update(tool="mcp-mother-child", email=EMAIL)
    if KEY: p["api_key"] = KEY
    time.sleep(DELAY)
    r = S.get(f"{EUTILS}/{endpoint}.fcgi", params=p, timeout=60)
    r.raise_for_status()
    return r

def txt(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else None

def save(rows, table, mode="overwrite"):
    if not rows:
        print(f"{table}: no rows"); return
    spark.createDataFrame(rows).write.mode(mode).option("overwriteSchema", "true") \
        .saveAsTable(f"{CAT}.{SCH}.{table}")
    print(f"{table}: {len(rows)} rows")

# COMMAND ----------
# MAGIC %md ## 1. PubMed (abstracts, last 10 years, maternal/child topics)

# COMMAND ----------

PUBMED_FILTERS = {
    "pregnancy": '"Pregnancy"[MeSH] AND (drug OR medication OR therapy)',
    "lactation": '("Lactation"[MeSH] OR "Breast Feeding"[MeSH]) AND (drug OR medication)',
    "breastfeeding": '"Breast Feeding"[MeSH] AND (drug OR medication)',
    "pediatric": '("Child"[MeSH] OR "Infant"[MeSH]) AND ("Drug Therapy"[MeSH] OR pharmacokinetics)',
}
PER_TOPIC = 2000  # raise for full load

def pubmed_ids(term, n):
    r = eutils("esearch", db="pubmed", term=term, retmax=n, datetype="pdat",
               reldate=3650, retmode="json")
    return r.json()["esearchresult"]["idlist"]

rows = []
for t in TOPICS:
    ids = pubmed_ids(PUBMED_FILTERS.get(t, t), PER_TOPIC)
    for i in range(0, len(ids), 200):
        x = eutils("efetch", db="pubmed", id=",".join(ids[i:i+200]), retmode="xml").text
        for a in ET.fromstring(x).iter("PubmedArticle"):
            rows.append(dict(
                pmid=a.findtext(".//PMID"), topic=t,
                title=txt(a.find(".//ArticleTitle")),
                abstract=" ".join(txt(b) for b in a.iterfind(".//AbstractText")),
                journal=a.findtext(".//Journal/Title"),
                year=a.findtext(".//PubDate/Year"),
                mesh=[m.findtext("DescriptorName") for m in a.iterfind(".//MeshHeading")]))
save(rows, "pubmed_articles")

# COMMAND ----------
# MAGIC %md ## 2. LactMed (NCBI Bookshelf)
# MAGIC **Verify the XML shape on a sample record**, then refine section parsing. Flat text is stored as a start.

# COMMAND ----------

term = 'lactmed[Book]'
ids = eutils("esearch", db="books", term=term, retmax=5000, retmode="json") \
        .json()["esearchresult"]["idlist"]
print("LactMed ids:", len(ids))
rows = []
for i in range(0, len(ids), 50):
    chunk = ids[i:i+50]
    summ = eutils("esummary", db="books", id=",".join(chunk), retmode="json").json()["result"]
    for bid in chunk:
        try:
            x = eutils("efetch", db="books", id=bid, retmode="xml").text
            rows.append(dict(book_id=bid, title=summ[bid].get("title"),
                             accession=summ[bid].get("accessionid"),
                             text=txt(ET.fromstring(x))))
        except Exception as e:
            print("skip", bid, e)
save(rows, "lactmed_records")

# COMMAND ----------
# MAGIC %md ## 3. NIH RePORTER (funded projects incl. NICHD / MPRINT-related)

# COMMAND ----------

REPORTER = "https://api.reporter.nih.gov/v2/projects/search"
FIELDS = ["ProjectNum", "ProjectTitle", "AbstractText", "FiscalYear", "AgencyIcAdmin",
          "Organization", "PrincipalInvestigators", "AwardAmount", "ProjectStartDate", "ProjectEndDate"]
rows = []
for fy in range(2019, 2027):
    off = 0
    while off < 14000:  # API hard-caps offset
        body = {"criteria": {"fiscal_years": [fy],
                             "advanced_text_search": {"operator": "or", "search_field": "all",
                                 "search_text": "pregnancy lactation breastfeeding maternal pediatric therapeutics MPRINT"}},
                "include_fields": FIELDS, "offset": off, "limit": 500}
        res = S.post(REPORTER, json=body, timeout=60).json().get("results", [])
        if not res: break
        for p in res:
            rows.append(dict(project_num=p.get("project_num"), title=p.get("project_title"),
                             abstract=p.get("abstract_text"), fiscal_year=p.get("fiscal_year"),
                             institute=(p.get("agency_ic_admin") or {}).get("abbreviation"),
                             organization=(p.get("organization") or {}).get("org_name"),
                             award_amount=p.get("award_amount")))
        off += 500
        time.sleep(1)  # RePORTER asks for ~1 req/sec
save(rows, "nih_reporter_projects")

# COMMAND ----------
# MAGIC %md ## 4. DailyMed labels (pregnancy 8.1 / lactation 8.2 sections)
# MAGIC Uses the DailyMed API per label. For full coverage switch to the bulk SPL zip files.

# COMMAND ----------

DM = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
NS = {"h": "urn:hl7-org:v3"}
CODES = {"42228-7": "pregnancy", "77290-5": "lactation"}  # LOINC, verify
rows, page = [], 1
while page <= 20:  # 100 labels/page -> raise for more
    d = S.get(f"{DM}/spls.json", params={"pagesize": 100, "page": page}, timeout=60).json()
    for item in d.get("data", []):
        try:
            x = S.get(f"{DM}/spls/{item['setid']}.xml", timeout=60).text
            secs = {}
            for sec in ET.fromstring(x).iterfind(".//h:section", NS):
                c = sec.find("h:code", NS)
                if c is not None and c.get("code") in CODES:
                    secs[CODES[c.get("code")]] = txt(sec)
            if secs:
                rows.append(dict(setid=item["setid"], title=item["title"],
                                 pregnancy=secs.get("pregnancy"), lactation=secs.get("lactation")))
        except Exception as e:
            print("skip", item.get("setid"), e)
    if page >= d.get("metadata", {}).get("total_pages", 1): break
    page += 1
save(rows, "dailymed_labels")

# COMMAND ----------
# MAGIC %md ## 5. openFDA FAERS (top adverse reactions in pregnancy/pediatric reports)

# COMMAND ----------

FAERS = "https://api.fda.gov/drug/event.json"
rows = []
for label, q in {"neonate": "patient.patientonsetageunit:802+AND+patient.patientonsetage:[0+TO+1]",
                 "pregnancy_reported": "patient.reaction.reactionmeddrapt:%22foetal+exposure+during+pregnancy%22"}.items():
    r = S.get(FAERS, params={"search": q, "count": "patient.drug.medicinalproduct.exact", "limit": 100}, timeout=60)
    if r.ok:
        rows += [dict(cohort=label, drug=x["term"], reports=x["count"]) for x in r.json()["results"]]
save(rows, "faers_drug_counts_by_cohort")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Next steps
# MAGIC 1. `ALTER TABLE ... SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` on `pubmed_articles` and `lactmed_records`.
# MAGIC 2. Create a Vector Search index on them (text column = `abstract` / `text`), then expose via managed MCP.
# MAGIC 3. Point Genie at the Delta tables for natural-language SQL.
# MAGIC 4. Add CDC data (data.cdc.gov Socrata / PRAMS) as further tables.
# MAGIC 5. Schedule as a Databricks Job (weekly).
