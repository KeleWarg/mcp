# --- add to app/bq.py (top) ---
import os, json, tempfile
cred_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if cred_json and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.write(cred_json.encode()); tmp.close()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name
# --- end snippet ---

import os, time, logging, json
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

PROJECT = os.getenv("BQ_PROJECT", "forbes-leadgen")
DATASET = os.getenv("BQ_DATASET", "leadgen")
TABLE   = os.getenv("BQ_TABLE", "mcp_events")

def write(event: dict):
    if os.getenv("BQ_ENABLED") != "1":
        return
    if bigquery is None:
        logging.warning("google-cloud-bigquery not installed")
        return
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.{DATASET}.{TABLE}"
    event["ingested_at"] = time.time()
    errors = client.insert_rows_json(table_id, [event])
    if errors:
        logging.warning("BQ errors: %s", errors)
