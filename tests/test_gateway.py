
import json, pytest, asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_registry():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/registry")
        assert r.status_code == 200
        assert "personal_loan" in r.json()["verticals"]

@pytest.mark.asyncio
async def test_answer_ok():
    payload = {
        "loan_amount":15000,"loan_purpose":"debt_consolidation",
        "credit_score_band":"670-739","employment_status":"employed",
        "annual_income":85000,"state":"CA","consent_tcpa":True
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/personal_loan/answer", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["score"] >= 0
        assert "latency_ms" in body

@pytest.mark.asyncio
async def test_answer_missing():
    payload = {}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/personal_loan/answer", json=payload)
        assert r.status_code == 422
