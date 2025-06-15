
# MCP Gateway – Personal Loans Pilot (v0.3)

Fully self‑contained FastAPI service with:
- **Required‑field validation**
- **Creditworthiness scoring** (`score` 0–1)
- **Latency metric** (`latency_ms`)
- **CRM forwarder** (`CRM_URL` env var)
- **Local JSONL event log** (`app/events.log`)
- **BigQuery exporter stub** (`BQ_ENABLED=1`)

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export CRM_URL=https://webhook.site/<your-id>   # optional
# export BQ_ENABLED=1                            # optional BigQuery

uvicorn app.main:app --reload --port 9000
```

### Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/registry` | List available verticals |
| GET | `/personal_loan/question/0` | Get first question |
| POST | `/personal_loan/answer` | Submit answers & receive score |

Event entries look like:

```json
{"event":"answer_submitted","vertical":"personal_loan","score":0.78,"latency_ms":15.3}
```
