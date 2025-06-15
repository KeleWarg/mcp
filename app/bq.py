
"""BigQuery event logger stub."""
import os, json, logging, time
# Optionally install google-cloud-bigquery and uncomment imports
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

DATASET = os.getenv("BQ_DATASET", "leadgen_events")
TABLE   = os.getenv("BQ_TABLE", "mcp_events")

def write(event: dict):
    if not os.getenv("BQ_ENABLED") == "1":
        return
    if bigquery is None:
        logging.warning("google-cloud-bigquery not installed.")
        return
    client = bigquery.Client()
    table_id = f"{client.project}.{DATASET}.{TABLE}"
    event["ingested_at"] = time.time()
    errors = client.insert_rows_json(table_id, [event])
    if errors:
        logging.warning("BigQuery errors: %s", errors)
