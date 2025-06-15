
# MCP Gateway – Personal Loans Pilot

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

## Endpoints
- **GET /registry** — list available verticals  
- **GET /personal_loan/question/0** — get first question object  
- **POST /personal_loan/answer** — submit answers JSON  

## Next tasks
1. Full payload validation + scoring
2. CRM forwarding stub
3. BigQuery event logging
4. Postman collection + OpenAI function spec
# mcp
