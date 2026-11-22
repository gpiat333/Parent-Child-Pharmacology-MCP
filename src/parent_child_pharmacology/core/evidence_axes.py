"""Three visible axes using attributed source passages, never a safety inference."""

import re
from copy import deepcopy

AXES = {
    "maternal_effects": "Effect on the pregnant or lactating person",
    "fetal_infant_exposure": "Measured transfer or exposure to fetus or infant",
    "fetal_infant_outcomes": "Observed outcomes in fetus or infant",
}
PK = re.compile(
    r"pharmacokinetic|clearance|half.life|area under the curve|\bAUC\b|\bCmax\b|dose.adjust|concentration",
    re.I,
)
MISSING = re.compile(
    r"(?:no|not|insufficient|lack of|limited|inadequate|unavailable|absence of).{0,70}(?:data|information|studies|evidence)|(?:data|information).{0,40}(?:not available|unavailable|insufficient)",
    re.I,
)
PREDICTED = re.compile(r"predict|simulat|model(?:ing|ling|ed)|in vitro|ex vivo", re.I)
ANIMAL = re.compile(r"\b(?:rats?|mice|rabbits?|monkeys?|rodents?|animal)\b", re.I)
OFFSPRING = re.compile(
    r"fetal|foetal|fetus|foetus|infant|neonat|newborn|breastfed|cord blood|umbilical", re.I
)
EXPOSURE = re.compile(
    r"concentration|drug levels?|measured|detected|transfer|milk.{0,25}(?:level|amount)|(?:level|amount).{0,25}milk",
    re.I,
)
OUTCOME = re.compile(
    r"outcome|malformation|birth defect|observed|reported|adverse|development|prematur|birth weight|sedat|mortality",
    re.I,
)
MILK = re.compile(r"breast\s*milk|human milk|\bmilk\b", re.I)
MATERNAL_ENDPOINT = re.compile(
    r"maternal\s+(?:plasma|serum|blood|clearance|adverse|outcomes?|depression|symptoms?)|(?:women|mothers|patients)\s+(?:had|experienced|developed)\s+(?:increased\s+|decreased\s+)?(?:clearance|adverse|depression|symptoms?)|milk production|milk supply|prolactin|lactogenesis|onset of lactation",
    re.I,
)
PROTOCOL = re.compile(
    r"\bwill\s+(?:measure|assess|evaluate|investigate)|\baims?\s+to\s+(?:measure|assess|evaluate|investigate)|\bstudy protocol\b",
    re.I,
)


def record(text, source, url, *, kind="source_passage", pmid=None):
    study_context = (
        "predicted_or_experimental"
        if PREDICTED.search(text)
        else "animal"
        if ANIMAL.search(text)
        else "source_context_requires_review"
    )
    return {
        "text": text,
        "source": source,
        "url": url,
        "pmid": pmid,
        "evidence_kind": kind,
        "study_context": study_context,
        "clinical_interpretation_validated": False,
    }


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text or "") if s.strip()]


def report_context(row, population):
    """Keep aggregate spontaneous reports visible without making clinical findings."""
    source = row.get("adverse_events") or {}
    if source.get("error") or not source.get("top_reactions"):
        return []
    return [
        {
            "source": "FAERS spontaneous reports",
            "evidence_kind": "report_counts_only",
            "url": source.get("url"),
            "queried_at_utc": source.get("queried_at_utc"),
            "query_cohort": source.get("cohort"),
            "query_scope": source.get("cohort_scope"),
            "requested_population": population,
            "source_population_confirmed": False,
            "reported_terms": deepcopy(source["top_reactions"]),
            "confirmed_clinical_outcomes": False,
            "establishes_causation": False,
            "exposure_denominator_available": False,
            "incidence_or_risk_calculable": False,
            "interpretation": deepcopy(source.get("report_count_interpretation", {})),
            "message": "Spontaneous report terms and counts were retrieved. They are reporting volume, not confirmed outcomes or rates. Keep them separate from observed study findings; query terms do not confirm the source population.",
        }
    ]


def build_axes(row, population):
    axes = {
        key: {
            "axis": key,
            "label": label,
            "items": [],
            "context_only": [],
            "reported_gaps": [],
            "report_only_context": [],
            "not_evidence_of_safety": True,
        }
        for key, label in AXES.items()
    }
    maternal_pk = {
        "items": [],
        "reported_gaps": [],
        "sources_checked": [
            "label 8.1 Clinical Considerations",
            "curated PubMed search and retrieved abstracts",
        ],
        "no_data_found": True,
        "not_evidence_of_safety": True,
        "personal_dose_calculated": False,
    }
    label = row.get("label", {})
    pllr = label.get("pllr_8_1", {})
    lu = label.get("url")
    clinical = pllr.get("subsections", {}).get("clinical_considerations", {}).get("text") or ""

    def add(axis, text, source, url, kind="source_passage", pmid=None, context=None):
        item = record(text, source, url, kind=kind, pmid=pmid)
        if context:
            item["study_context"] = context
        if MISSING.search(text):
            axes[axis]["reported_gaps"].append(item)
        elif context == "protocol_not_results" or (
            axis in {"fetal_infant_exposure", "fetal_infant_outcomes"}
            and (
                context
                or PREDICTED.search(text)
                or ANIMAL.search(text)
                or re.search(r"\bmonitor|should|recommend", text, re.I)
            )
        ):
            axes[axis]["context_only"].append(item)
        else:
            axes[axis]["items"].append(item)

    if population == "pregnancy":
        topics = pllr.get("clinical_consideration_topics", {})
        for name in ["disease_associated_risk", "maternal_adverse_reactions"]:
            if topics.get(name):
                add(
                    "maternal_effects",
                    topics[name],
                    "DailyMed 8.1 Clinical Considerations",
                    lu,
                    "label_context",
                )
        if topics.get("fetal_neonatal_adverse_reactions"):
            add(
                "fetal_infant_outcomes",
                topics["fetal_neonatal_adverse_reactions"],
                "DailyMed 8.1 Clinical Considerations",
                lu,
                "label_context",
            )
        # Risk Summary/Data may contain human, animal or no-data statements.
        sources = [
            (
                "Risk Summary",
                pllr.get("subsections", {}).get("risk_summary", {}).get("text"),
                "label_risk_summary",
            )
        ]
        data_topics = pllr.get("data_topics", {})
        if any(data_topics.values()):
            sources += [
                ("Human Data", data_topics.get("human"), None),
                ("Animal Data", data_topics.get("animal"), "animal_label_data"),
            ]
        else:
            sources.append(
                (
                    "Data",
                    pllr.get("subsections", {}).get("data", {}).get("text"),
                    "unclassified_label_data",
                )
            )
        for key, text, context in sources:
            for s in sentences(text):
                if MISSING.search(s):
                    for axis in axes:
                        add(axis, s, "DailyMed 8.1 " + key, lu, "label_coverage_statement")
                elif OFFSPRING.search(s) and EXPOSURE.search(s):
                    add(
                        "fetal_infant_exposure",
                        s,
                        "DailyMed 8.1 " + key,
                        lu,
                        "label_context",
                        context=context,
                    )
                elif OFFSPRING.search(s) and OUTCOME.search(s):
                    add(
                        "fetal_infant_outcomes",
                        s,
                        "DailyMed 8.1 " + key,
                        lu,
                        "label_context",
                        context=context,
                    )
        for s in sentences(clinical):
            if PK.search(s):
                item = record(s, "DailyMed 8.1 Clinical Considerations", lu, kind="label_context")
                maternal_pk["reported_gaps" if MISSING.search(s) else "items"].append(item)
    if population == "lactation":
        lactmed = row.get("lactmed", {})
        text = lactmed.get("text", "")
        url = lactmed.get("url")
        names = {
            "Effects on Lactation and Breastmilk": "maternal_effects",
            "Drug Levels": "fetal_infant_exposure",
            "Effects in Breastfed Infants": "fetal_infant_outcomes",
        }
        headings = list(names) + ["Summary of Use during Lactation", "Alternate Drugs to Consider"]
        for heading, axis in names.items():
            section = lactmed.get("sections", {}).get(heading)
            if section is None:
                match = re.search(
                    re.escape(heading)
                    + r":\s*(.*?)(?=\n\n(?:"
                    + "|".join(map(re.escape, headings))
                    + r"):|\Z)",
                    text,
                    re.S,
                )
                section = match[1] if match else ""
            for s in sentences(section):
                add(axis, s, "LactMed (lactation only): " + heading, url, "lactmed_section")
    literature = row.get("literature", {})
    for article in literature.get("articles", []):
        abstract = article.get("abstract", "")
        source = "PubMed abstract: " + article.get("title", "")
        url = article.get("url")
        pmid = article.get("pmid")
        mesh = set(article.get("mesh_terms", []))
        types = set(article.get("publication_types", []))
        context = (
            "animal_study"
            if "Animals" in mesh and "Humans" not in mesh
            else "review_not_primary_outcome"
            if "Review" in types
            else None
        )
        for s in sentences(abstract):
            passage_context = (
                "protocol_not_results"
                if PROTOCOL.search(s) or "Clinical Trial Protocol" in types
                else context
            )
            if re.search(
                r"\bmaternal|\bmother|pregnant (?:women|patients|people)|lactating (?:women|patients|people)",
                s,
                re.I,
            ):
                # Mentioning a mother as the exposure source does not make milk
                # concentrations or infant outcomes a maternal clinical effect.
                offspring_only = (
                    OFFSPRING.search(s) or MILK.search(s)
                ) and not MATERNAL_ENDPOINT.search(s)
                if not offspring_only and (OUTCOME.search(s) or PK.search(s)):
                    add(
                        "maternal_effects",
                        s,
                        source,
                        url,
                        "abstract_candidate",
                        pmid,
                        passage_context,
                    )
            if OFFSPRING.search(s) or re.search(r"breast\s*milk|human milk", s, re.I):
                if EXPOSURE.search(s):
                    add(
                        "fetal_infant_exposure",
                        s,
                        source,
                        url,
                        "abstract_candidate",
                        pmid,
                        passage_context,
                    )
                if OUTCOME.search(s):
                    add(
                        "fetal_infant_outcomes",
                        s,
                        source,
                        url,
                        "abstract_candidate",
                        pmid,
                        passage_context,
                    )
            if (
                population == "pregnancy"
                and PK.search(s)
                and re.search(r"maternal|pregnan|gestation|women", s, re.I)
                and (not (OFFSPRING.search(s) or MILK.search(s)) or MATERNAL_ENDPOINT.search(s))
                and passage_context != "protocol_not_results"
            ):
                item = record(s, source, url, kind="abstract_candidate", pmid=pmid)
                if context:
                    item["study_context"] = context
                maternal_pk["reported_gaps" if MISSING.search(s) else "items"].append(item)
    axes["fetal_infant_outcomes"]["report_only_context"] = report_context(row, population)
    for axis in axes.values():
        # Exact duplicates may occur when all-axis and PK searches overlap.
        for key in ["items", "context_only", "reported_gaps"]:
            seen = set()
            axis[key] = [
                x
                for x in axis[key]
                if not ((x["text"], x["url"]) in seen or seen.add((x["text"], x["url"])))
            ]
        axis["outcome_or_effect_passages_retrieved"] = bool(axis["items"])
        axis["report_only_context_retrieved"] = bool(axis["report_only_context"])
        axis["no_evidence_retrieved"] = not bool(axis["items"] or axis["report_only_context"])
        axis["state"] = (
            "source_passages_retrieved"
            if axis["items"]
            else "report_context_only"
            if axis["report_only_context"]
            else "none_retrieved"
        )
        axis["empty_message"] = (
            None
            if axis["items"]
            else (
                "No observed-outcome findings retrieved for this axis. Spontaneous report context was retrieved separately; it does not establish an outcome, causation or safety."
                if axis["report_only_context"]
                else "No evidence retrieved for this axis; not evidence of safety."
            )
        )
        axis["interpretation"] = (
            "Passages are grouped heuristically, not adjudicated clinical findings. Preserve human/animal/modeling context and confirm study design. Source advice and planned study measurements are not observed outcomes. Milk/infant concentrations do not establish a maternal clinical effect. Keep empty axes visible."
        )
        from .source_context import evidence_base, item_population

        articles = {a.get("pmid"): a for a in literature.get("articles", [])}
        for key in ["items", "context_only", "reported_gaps"]:
            for item in axis[key]:
                article = articles.get(item.get("pmid"), {})
                item["population_context"] = item_population({**article, **item}, population)
                item["evidence_base"] = evidence_base(
                    article.get("abstract") or item["text"], article.get("publication_types")
                )
                if article:
                    context = article.get("abstract")
                elif "LactMed" in item["source"]:
                    context = row.get("lactmed", {}).get("source_balance_context", {}).get("text")
                else:
                    context = (
                        topics.get("disease_associated_risk") if population == "pregnancy" else None
                    )
                item["source_balance_context"] = {
                    "text": context[:4000] if context else None,
                    "truncated": bool(context and len(context) > 4000),
                    "notice": "Adjacent/linked source context is not a personalized benefit-risk assessment. Missing context is unknown; do not invent reassurance.",
                }
    maternal_pk["no_data_found"] = not bool(maternal_pk["items"])
    maternal_pk["human_data_confirmed"] = False
    for key in ["items", "reported_gaps"]:
        for item in maternal_pk[key]:
            item["population_context"] = item_population(item, population)
    maternal_pk["message"] = (
        "No maternal pharmacokinetic data were found in the retrieved Clinical Considerations and abstracts; not evidence of safety."
        if maternal_pk["no_data_found"]
        else "Candidate maternal pharmacokinetic passages retrieved; inspect study population/design. No personalized dose adjustment is inferred."
    )
    return list(axes.values()), maternal_pk
