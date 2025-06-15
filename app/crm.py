
import os, requests, logging
def send(payload: dict):
    crm_url = os.getenv("CRM_URL")
    if not crm_url:
        return
    try:
        r = requests.post(crm_url, json=payload, timeout=5)
        logging.info("CRM forward status %s", r.status_code)
    except Exception as e:
        logging.warning("CRM forward failed: %s", e)
