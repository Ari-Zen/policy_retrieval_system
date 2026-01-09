# Quick Start Guide

Get the Policy-Aware Knowledge Retrieval System running in 3 steps.

## Prerequisites Check

Verify you have:
- ✓ Python 3.10+ installed
- ✓ Virtual environment activated
- ✓ API keys configured in `.env`

Check your `.env` file has:
```
PINECONE=pcsk_...
OPENAI=sk-proj-...
PINECONE_INDEX_NAME=semantic-search
```

## Step 1: Start the Server

Open a terminal and run:

```bash
uvicorn app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Step 2: Seed Sample Data

**Option A: Using curl**
```bash
curl -X POST http://localhost:8000/seed-data
```

**Option B: Using browser**
1. Open http://localhost:8000/docs
2. Click on `POST /seed-data`
3. Click "Try it out"
4. Click "Execute"

You should see:
```json
{
  "status": "success",
  "policies_uploaded": 4,
  "clauses_uploaded": 8
}
```

## Step 3: Test a Query

**Option A: Using the test script**
```bash
python test_system.py
```

**Option B: Using curl**
```bash
curl -X POST "http://localhost:8000/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I get a refund for a product I bought 2 weeks ago?",
    "jurisdiction": "US",
    "as_of_date": "2024-06-15",
    "role": "customer"
  }'
```

**Option C: Using the browser**
1. Open http://localhost:8000/docs
2. Click on `POST /answer`
3. Click "Try it out"
4. Use the sample request below
5. Click "Execute"

Sample request:
```json
{
  "query": "Can I get a refund for a product I bought 2 weeks ago?",
  "jurisdiction": "US",
  "as_of_date": "2024-06-15",
  "role": "customer"
}
```

Expected response:
```json
{
  "audit_id": "...",
  "timestamp": "...",
  "query": "Can I get a refund for a product I bought 2 weeks ago?",
  "role": "customer",
  "jurisdiction": "US",
  "as_of_date": "2024-06-15",
  "decision_status": "safe",
  "decision_reason": "Answer generated from validated clauses",
  "policy_ids": ["REFUND-001"],
  "clause_ids": ["REFUND-001-C1", "REFUND-001-C2"],
  "answer": "Yes, you can request a full refund..."
}
```

## That's It!

Your system is now running. Try these next:

### More Test Queries

**Premium member query:**
```json
{
  "query": "As a premium member, what is my refund window?",
  "jurisdiction": "US",
  "as_of_date": "2024-06-15",
  "role": "premium_customer"
}
```

**Digital product query:**
```json
{
  "query": "Can I get a refund for an ebook I already downloaded?",
  "jurisdiction": "US",
  "as_of_date": "2024-06-15",
  "role": "customer"
}
```

**EU jurisdiction query:**
```json
{
  "query": "What are my return rights as an EU customer?",
  "jurisdiction": "EU",
  "as_of_date": "2024-06-15",
  "role": "customer"
}
```

### View Audit Records

Visit: http://localhost:8000/audit

Or:
```bash
curl http://localhost:8000/audit
```

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Try a different port
uvicorn app:app --reload --port 8001
```

### Import errors
```bash
# Verify all dependencies installed
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+
```

### API key errors
- Check `.env` file exists in project root
- Verify API keys are valid
- Make sure no extra spaces in `.env` file

### Pinecone errors
- Verify your Pinecone API key is valid
- Check you have available indexes in your Pinecone account
- Wait a few seconds for index creation

### No results from queries
- Make sure you ran `/seed-data` endpoint first
- Check Pinecone dashboard to verify data uploaded
- Try restarting the server

## Next Steps

1. Read `IMPLEMENTATION_SUMMARY.md` for detailed architecture
2. Read `README.md` for full documentation
3. Explore the code in these key files:
   - `app.py` - API endpoints
   - `llm_client.py` - LLM abstraction
   - `vector_store.py` - Vector database
   - `retriever.py` - Core retrieval logic

## API Documentation

Full interactive API docs: http://localhost:8000/docs
Alternative docs: http://localhost:8000/redoc
