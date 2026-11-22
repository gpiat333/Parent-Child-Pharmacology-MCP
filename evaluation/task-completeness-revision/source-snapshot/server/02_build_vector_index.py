# Databricks notebook source
# MAGIC %pip install -U databricks-vectorsearch
# MAGIC %restart_python

# COMMAND ----------
# MAGIC %md
# MAGIC # Build Vector Search indexes (run after `ingest_mother_child`)
# MAGIC Creates deduplicated, change-data-feed-enabled source tables, then Delta Sync indexes with
# MAGIC Databricks-managed embeddings, then grants the MCP app's service principal read access.

# COMMAND ----------

dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "mother_child")
dbutils.widgets.text("endpoint", "mother_child_vs")
dbutils.widgets.text("embedding_model", "databricks-gte-large-en")
dbutils.widgets.text("app_service_principal", "")  # application ID of the MCP app's service principal
CAT, SCH = dbutils.widgets.get("catalog"), dbutils.widgets.get("schema")
EP, EMB = dbutils.widgets.get("endpoint"), dbutils.widgets.get("embedding_model")
SP = dbutils.widgets.get("app_service_principal")
P = f"`{CAT}`.`{SCH}`"

# COMMAND ----------
# Source tables for indexing. CREATE IF NOT EXISTS + MERGE (not CREATE OR REPLACE) so the index's
# change feed stays valid across refreshes.
spark.sql(f"""CREATE TABLE IF NOT EXISTS {P}.pubmed_for_index
  (pmid STRING, title STRING, abstract STRING, journal STRING, year STRING, topics STRING)
  TBLPROPERTIES (delta.enableChangeDataFeed = true)""")
spark.sql(f"""MERGE INTO {P}.pubmed_for_index t USING (
  SELECT pmid, any_value(title) title, any_value(abstract) abstract, any_value(journal) journal,
         any_value(year) year, concat_ws(',', collect_set(topic)) topics
  FROM {P}.pubmed_articles WHERE abstract IS NOT NULL AND length(abstract) > 50 GROUP BY pmid) s
  ON t.pmid = s.pmid WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""")

spark.sql(f"""CREATE TABLE IF NOT EXISTS {P}.lactmed_for_index
  (book_id STRING, title STRING, accession STRING, text STRING)
  TBLPROPERTIES (delta.enableChangeDataFeed = true)""")
spark.sql(f"""MERGE INTO {P}.lactmed_for_index t USING (
  SELECT book_id, title, accession, substr(text, 1, 16000) text   -- keep under embedding token limit
  FROM {P}.lactmed_records WHERE text IS NOT NULL) s
  ON t.book_id = s.book_id WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""")

# COMMAND ----------
from databricks.vector_search.client import VectorSearchClient
vsc = VectorSearchClient(disable_notice=True)

try:
    vsc.get_endpoint(EP)
except Exception:
    vsc.create_endpoint_and_wait(name=EP, endpoint_type="STANDARD")

def ensure_index(source_table, index_name, pk, text_col):
    full = f"{CAT}.{SCH}.{index_name}"
    try:
        vsc.get_index(EP, full).sync()          # exists -> incremental sync
        print("synced", full)
    except Exception:
        vsc.create_delta_sync_index_and_wait(
            endpoint_name=EP, index_name=full, source_table_name=f"{CAT}.{SCH}.{source_table}",
            pipeline_type="TRIGGERED", primary_key=pk,
            embedding_source_column=text_col, embedding_model_endpoint_name=EMB)
        print("created", full)

ensure_index("pubmed_for_index", "pubmed_idx", "pmid", "abstract")
ensure_index("lactmed_for_index", "lactmed_idx", "book_id", "text")

# COMMAND ----------
# Quick sanity query
idx = vsc.get_index(EP, f"{CAT}.{SCH}.lactmed_idx")
print(idx.similarity_search(query_text="antidepressant while breastfeeding a newborn",
                            columns=["title"], num_results=3))

# COMMAND ----------
# Grants for the MCP app's service principal (find it on the app's page in the workspace).
if SP:
    for stmt in [f"GRANT USE CATALOG ON CATALOG `{CAT}` TO `{SP}`",
                 f"GRANT USE SCHEMA ON SCHEMA {P} TO `{SP}`",
                 f"GRANT SELECT ON SCHEMA {P} TO `{SP}`",
                 f"GRANT MODIFY ON SCHEMA {P} TO `{SP}`"]:   # MODIFY lets it write mcp_audit_log
        spark.sql(stmt)
    print("grants applied (also give the SP CAN USE on the SQL warehouse and CAN QUERY on the VS endpoint)")
else:
    print("Set app_service_principal widget to apply grants.")
