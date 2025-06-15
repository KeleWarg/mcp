
from fastapi import FastAPI, Request, HTTPException
from pathlib import Path
import json

app = FastAPI(title="MCP Gateway", version="0.1")

SCHEMA_DIR = Path(__file__).parent / "schemas"

def load_schema(vertical: str):
    p = SCHEMA_DIR / f"{vertical}.schema.jsonld"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Schema not found")
    return json.loads(p.read_text())

@app.get("/registry")
def registry():
    return {"verticals": [p.stem for p in SCHEMA_DIR.glob("*.schema.jsonld")]}

@app.get("/{vertical}/question/{step}")
def get_question(vertical: str, step: int):
    schema = load_schema(vertical)
    fields = [f for f in schema["fields"] if f["priority"] == "P0"]
    if step < 0 or step >= len(fields):
        raise HTTPException(status_code=404, detail="Step out of range")
    field = fields[step]
    return {
        "id": field["@id"],
        "prompt": field["prompt"],
        "type": field["@type"],
        "validation": field.get("validation", {}),
        "allowedValues": field.get("allowedValues", [])
    }

@app.post("/{vertical}/answer")
async def post_answer(vertical: str, request: Request):
    schema = load_schema(vertical)
    payload = await request.json()
    # Simple validation
    errors = []
    for field in schema["fields"]:
        fid = field["@id"]
        if field["priority"] == "P0" and fid not in payload:
            errors.append(f"Missing required field: {fid}")
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    # TODO: scoring & CRM forward
    return {"status": "accepted", "payload": payload}
