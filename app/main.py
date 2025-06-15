from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware   # ★ NEW
from pathlib import Path
import json, time, logging, os

from . import crm, bq, metrics

# ─────────────────────────────────────────────
# FastAPI app + CORS (needed for ChatGPT/Actions)
# ─────────────────────────────────────────────
app = FastAPI(title="MCP Gateway", version="0.5")

app.add_middleware(                           # ★ NEW
    CORSMiddleware,
    allow_origins=["*"],                      # tighten later if you want
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Globals & helpers
# ─────────────────────────────────────────────
SCHEMA_DIR = Path(__file__).parent / "schemas"
EVENT_LOG   = Path(__file__).parent / "events.log"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def load_schema(vertical: str):
    p = SCHEMA_DIR / f"{vertical}.schema.jsonld"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Schema not found")
    return json.loads(p.read_text())

def score_payload(data: dict) -> float:
    band_weight = {"<580":0.2,"580-669":0.4,"670-739":0.6,"740-799":0.8,"800+":1.0}
    credit = band_weight.get(data.get("credit_score_band"), 0.1)
    income = float(data.get("annual_income", 0))
    loan   = float(data.get("loan_amount", 1))
    dti    = max(0, 1 - (loan / income)) if income else 0
    return round(0.6 * credit + 0.4 * dti, 2)

def log_local(event: dict):
    try:
        with EVENT_LOG.open("a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        # Vercel FS is read-only; tolerate failures
        logging.warning(f"Local logging failed: {e}")

# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/registry")
def registry():
    """Return list of available verticals (currently just personal_loan)."""
    return {"verticals": [p.stem for p in SCHEMA_DIR.glob("*.schema.jsonld")]}

@app.get("/{vertical}/question/{step}")
def get_question(
    request: Request,
    vertical: str,
    step: int,
    variant: str | None = None
):
    schema  = load_schema(vertical)
    fields  = [f for f in schema["fields"] if f["priority"] == "P0"]
    if step < 0 or step >= len(fields):
        raise HTTPException(status_code=404, detail="Step out of range")

    f          = fields[step]
    variant_id = variant or request.headers.get("X-Variant")

    return {
        "id":            f["@id"],
        "prompt":        f["prompt"],
        "type":          f["@type"],
        "validation":    f.get("validation", {}),
        "allowedValues": f.get("allowedValues", []),
        "variant":       variant_id,
    }

@app.post("/{vertical}/answer")
async def post_answer(
    request: Request,
    vertical: str,
    variant: str | None = None
):
    try:
        t0       = time.time()
        schema   = load_schema(vertical)
        payload  = await request.json()
        variant_id = variant or request.headers.get("X-Variant")

        # -------- validation --------
        missing = [
            f["@id"] for f in schema["fields"]
            if f["priority"] == "P0" and f["@id"] not in payload
        ]
        if missing:
            event = {
                "event": "validation_error",
                "vertical": vertical,
                "missing": missing,
                "variant": variant_id,
            }
            log_local(event)
            try:
                bq.write(event)
            except Exception as e:
                logging.warning(f"BQ write failed: {e}")
            raise HTTPException(status_code=422, detail={"missing": missing})

        # -------- scoring --------
        score       = score_payload(payload)
        latency_ms  = round((time.time() - t0) * 1000, 2)

        # -------- forward lead --------
        try:
            crm.send({**payload, "score": score, "variant": variant_id})
        except Exception as e:
            logging.warning(f"CRM send failed: {e}")

        # -------- analytics --------
        event = {
            "event":       "answer_submitted",
            "vertical":    vertical,
            "score":       score,
            "latency_ms":  latency_ms,
            "variant":     variant_id,
        }
        log_local(event)
        try:
            bq.write(event)
        except Exception as e:
            logging.warning(f"BQ write failed: {e}")

        return {
            "status":     "accepted",
            "score":      score,
            "latency_ms": latency_ms,
            "variant":    variant_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error in post_answer: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@app.get("/metrics")
def get_metrics():
    """Return cumulative token usage (populated by the demo agent)."""
    return {"usage": metrics.meter.snapshot()}