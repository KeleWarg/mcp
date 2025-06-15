
from fastapi import FastAPI, Request, HTTPException
from pathlib import Path
import json, time, logging
from . import crm, bq

app = FastAPI(title="MCP Gateway", version="0.3")

SCHEMA_DIR = Path(__file__).parent / "schemas"
EVENT_LOG = Path(__file__).parent / "events.log"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------- Helpers ----------
def load_schema(vertical: str):
    p = SCHEMA_DIR / f"{vertical}.schema.jsonld"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Schema not found")
    return json.loads(p.read_text())

def score_payload(data: dict) -> float:
    score_map = {"<580":0.2,"580-669":0.4,"670-739":0.6,"740-799":0.8,"800+":1.0}
    credit_weight = score_map.get(data.get("credit_score_band"),0.1)
    income = float(data.get("annual_income",0))
    loan_amt = float(data.get("loan_amount",1))
    dti_weight = max(0, 1 - (loan_amt / income)) if income else 0
    return round(0.6*credit_weight + 0.4*dti_weight, 2)

def log_local(event: dict):
    line = json.dumps(event)
    EVENT_LOG.write_text((EVENT_LOG.read_text() if EVENT_LOG.exists() else "") + line + "\n")

# ---------- API ----------
@app.get("/registry")
def registry():
    return {"verticals":[p.stem for p in SCHEMA_DIR.glob("*.schema.jsonld")]}

@app.get("/{vertical}/question/{step}")
def get_question(vertical: str, step: int):
    schema = load_schema(vertical)
    fields = [f for f in schema["fields"] if f["priority"] == "P0"]
    if step < 0 or step >= len(fields):
        raise HTTPException(status_code=404, detail="Step out of range")
    f = fields[step]
    return {
        "id": f["@id"],
        "prompt": f["prompt"],
        "type": f["@type"],
        "validation": f.get("validation", {}),
        "allowedValues": f.get("allowedValues", [])
    }

@app.post("/{vertical}/answer")
async def post_answer(vertical: str, request: Request):
    t0 = time.time()
    schema = load_schema(vertical)
    payload = await request.json()
    # Required-field validation
    missing = [f["@id"] for f in schema["fields"] if f["priority"]=="P0" and f["@id"] not in payload]
    if missing:
        log_local({"event":"validation_error","vertical":vertical,"missing":missing})
        raise HTTPException(status_code=422, detail={"missing":missing})

    # Score + latency
    score = score_payload(payload)
    latency_ms = round((time.time() - t0)*1000, 2)
    payload_out = {**payload, "score":score}

    # Forward + logging
    crm.send(payload_out)
    event = {"event":"answer_submitted","vertical":vertical,"score":score,"latency_ms":latency_ms}
    log_local(event)
    bq.write(event)

    return {"status":"accepted","score":score,"latency_ms":latency_ms}
