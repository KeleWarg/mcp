# MCP Gateway v0.4

A conversational lead generation API for personal loans, built with FastAPI and deployed on Vercel. This gateway collects loan application data, scores applications, and integrates with CRM and analytics systems.

## 🚀 Live API

**Base URL**: `https://mcp-sandy.vercel.app/`

## 📋 Table of Contents

- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [ChatGPT Integration](#chatgpt-integration)
- [BigQuery Analytics](#bigquery-analytics)
- [Environment Variables](#environment-variables)
- [Development](#development)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChatGPT/UI    │───▶│  MCP Gateway    │───▶│   BigQuery      │
│                 │    │   (FastAPI)     │    │   Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   CRM System    │
                       │   (Webhook)     │
                       └─────────────────┘
```

### Core Components

- **FastAPI Application** (`app/main.py`) - Main API server
- **Schema Management** (`app/schemas/`) - JSON-LD schemas for loan verticals
- **BigQuery Integration** (`app/bq.py`) - Event logging and analytics
- **CRM Integration** (`app/crm.py`) - Lead forwarding
- **Metrics System** (`app/metrics.py`) - Usage tracking
- **Vercel Deployment** (`api/index.py`, `vercel.json`) - Serverless hosting

## 🔌 API Endpoints

### 1. Registry
```http
GET /registry
```
Returns available loan verticals.

**Response:**
```json
{
  "verticals": ["personal_loan.schema"]
}
```

### 2. Get Question
```http
GET /{vertical}/question/{step}?variant={variant}
```
Retrieves a specific question in the loan application flow.

**Parameters:**
- `vertical` - Loan type (e.g., "personal_loan")
- `step` - Question step number (0-based)
- `variant` - Optional A/B test variant

**Response:**
```json
{
  "id": "loan_amount",
  "prompt": "How much do you want to borrow?",
  "type": "MonetaryAmount",
  "validation": {
    "minValue": 1000,
    "maxValue": 100000,
    "currency": "USD"
  },
  "allowedValues": [],
  "variant": null
}
```

### 3. Submit Application
```http
POST /{vertical}/answer
```
Submits complete loan application and returns approval score.

**Request Body:**
```json
{
  "loan_amount": 15000,
  "loan_purpose": "debt_consolidation",
  "credit_score_band": "670-739",
  "employment_status": "employed",
  "annual_income": 85000,
  "state": "CA",
  "consent_tcpa": true
}
```

**Response:**
```json
{
  "status": "accepted",
  "score": 0.69,
  "latency_ms": 1.3,
  "variant": null
}
```

### 4. Metrics
```http
GET /metrics
```
Returns usage metrics and token consumption.

**Response:**
```json
{
  "usage": {
    "gpt-4o-mini": 1250
  }
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Google Cloud account (for BigQuery)
- Vercel account (for deployment)

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/KeleWarg/mcp.git
cd mcp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export BQ_ENABLED=1
export BQ_PROJECT=your-gcp-project
export GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account",...}'
export CRM_URL=https://your-crm-webhook.com/leads
```

4. **Run locally:**
```bash
uvicorn app.main:app --reload
```

5. **Test the API:**
```bash
curl http://localhost:8000/registry
```

## 🌐 Deployment

### Vercel Deployment

The project is configured for automatic deployment on Vercel:

1. **Connect GitHub repository** to Vercel
2. **Set environment variables** in Vercel dashboard
3. **Deploy automatically** on git push

**Configuration files:**
- `vercel.json` - Vercel deployment configuration
- `api/index.py` - Vercel serverless function entry point
- `requirements.txt` - Python dependencies

### Manual Deployment
```bash
vercel --prod
```

## 🤖 ChatGPT Integration

### Custom GPT Actions

1. **Create Custom GPT** in ChatGPT
2. **Add Action** with OpenAPI URL:
   ```
   https://mcp-sandy.vercel.app/.well-known/openapi.yaml
   ```
3. **Configure authentication** (None required)

### Available Operations
- `listVerticals` - Get available loan types
- `getQuestion` - Get individual questions
- `submitLoanApplication` - Submit complete application
- `getMetrics` - Get usage statistics

### Demo Script
Run the included ChatGPT demo:
```bash
OPENAI_API_KEY=your_key python3 demo/chatgpt_agent.py
```

## 📊 BigQuery Analytics

### Setup

1. **Create BigQuery dataset:**
```bash
bq mk --dataset your-project:leadgen
```

2. **Enable BigQuery logging:**
```bash
export BQ_ENABLED=1
export BQ_PROJECT=your-project
```

### Query Examples

**Recent submissions:**
```sql
SELECT event, COUNT(*) as count
FROM `your-project.leadgen.mcp_events`
WHERE ingested_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY event
```

**Average scores by credit band:**
```sql
SELECT 
  JSON_EXTRACT_SCALAR(event_data, '$.credit_score_band') as credit_band,
  AVG(CAST(JSON_EXTRACT_SCALAR(event_data, '$.score') AS FLOAT64)) as avg_score
FROM `your-project.leadgen.mcp_events`
WHERE event = 'answer_submitted'
GROUP BY credit_band
```

## ⚙️ Environment Variables

### Required
- `BQ_PROJECT` - Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` - Service account JSON (for production)

### Optional
- `BQ_ENABLED` - Enable BigQuery logging (default: disabled)
- `BQ_DATASET` - BigQuery dataset name (default: "leadgen")
- `BQ_TABLE` - BigQuery table name (default: "mcp_events")
- `CRM_URL` - CRM webhook URL for lead forwarding
- `OPENAI_API_KEY` - For ChatGPT demo script

## 🛠️ Development

### Project Structure
```
mcp_gateway_v0_3/
├── app/
│   ├── main.py              # FastAPI application
│   ├── bq.py               # BigQuery integration
│   ├── crm.py              # CRM integration
│   ├── metrics.py          # Usage metrics
│   ├── events.log          # Local event log
│   └── schemas/
│       └── personal_loan.schema.jsonld
├── api/
│   └── index.py            # Vercel entry point
├── demo/
│   └── chatgpt_agent.py    # ChatGPT demo
├── tests/
│   └── test_gateway.py     # Test suite
├── .well-known/
│   ├── ai-plugin.json      # ChatGPT plugin manifest
│   └── openapi.yaml        # API specification
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Scoring Algorithm

The loan scoring algorithm considers:
- **Credit Score Band** (60% weight)
- **Debt-to-Income Ratio** (40% weight)

```python
def score_payload(data):
    credit_map = {"<580":0.2, "580-669":0.4, "670-739":0.6, "740-799":0.8, "800+":1.0}
    credit_score = credit_map.get(data.get("credit_score_band"), 0.1)
    
    income = float(data.get("annual_income", 0))
    amount = float(data.get("loan_amount", 1))
    dti_score = max(0, 1 - (amount/income)) if income else 0
    
    return round(0.6 * credit_score + 0.4 * dti_score, 2)
```

### Testing

Run the test suite:
```bash
pytest tests/
```

Test individual endpoints:
```bash
# Test registry
curl https://mcp-sandy.vercel.app/registry

# Test question
curl https://mcp-sandy.vercel.app/personal_loan/question/0

# Test submission
curl -X POST https://mcp-sandy.vercel.app/personal_loan/answer \
  -H "Content-Type: application/json" \
  -d '{"loan_amount":15000,"loan_purpose":"debt_consolidation","credit_score_band":"670-739","employment_status":"employed","annual_income":85000,"state":"CA","consent_tcpa":true}'
```

## 📝 Schema Format

Loan schemas are defined in JSON-LD format with Forbes-specific extensions:

```json
{
  "@context": "https://schema.forbes.com/leadgen/v1",
  "@type": "LeadForm",
  "vertical": "personal_loan",
  "fields": [
    {
      "@id": "loan_amount",
      "@type": "MonetaryAmount",
      "prompt": "How much do you want to borrow?",
      "priority": "P0",
      "validation": {
        "minValue": 1000,
        "maxValue": 100000
      }
    }
  ]
}
```

## 🔒 Security

- **No authentication required** for public API
- **HTTPS enforced** via Vercel
- **Input validation** on all endpoints
- **Rate limiting** via Vercel
- **Error handling** prevents information leakage

## 📈 Monitoring

- **Event logging** to BigQuery
- **Metrics tracking** via `/metrics` endpoint
- **Error logging** to application logs
- **Performance monitoring** via Vercel dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary to Forbes/Kele.

## 🆘 Support

For support, contact: support@kele.dev

---

**Built with ❤️ using FastAPI, Vercel, and BigQuery**
