import os, json, requests
from openai import OpenAI
from app.metrics import meter

BASE = "https://mcp-sandy.vercel.app"
FUNCTION = json.load(open("openai_function_spec.json"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise SystemExit("Set OPENAI_API_KEY env var first")

messages = [
    {"role":"system","content":"You are Forbes Lead Assistant."},
    {"role":"user","content":"I'd like a $15k loan to consolidate debt."}
]

while True:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=[{"type":"function","function":FUNCTION}]
    )
    m = resp.choices[0].message
    if m.tool_calls:
        args = json.loads(m.tool_calls[0].function.arguments)
        gw = requests.post(f"{BASE}/personal_loan/answer", json=args).json()
        messages.append({"role":"tool","tool_call_id":m.tool_calls[0].id,"content":json.dumps(gw)})
        meter.add("gpt-4o-mini", resp.usage.total_tokens)
    else:
        print("Assistant:", m.content)
        break

print("Token snapshot:", meter.snapshot())