
# MCP Gateway – Personal Loans Pilot (v0.4)

**Sprint 3 deliverables**
- BigQuery event export (enable with `BQ_ENABLED=1`, env vars for project/dataset/table)
- Variant flag via `?variant=X` or `X-Variant` header, echoed in events & API responses
- `/metrics` endpoint (token/cost usage stub)
- Pytest harness (`make test`)

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export CRM_URL=https://webhook.site/<uuid>      # optional
export BQ_ENABLED=0                             # set 1 when creds ready
export BQ_PROJECT=forbes-leadgen
export BQ_DATASET=leadgen
export BQ_TABLE=mcp_events

uvicorn app.main:app --reload --port 9000
```
