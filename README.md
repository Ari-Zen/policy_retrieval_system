# Policy-Aware Knowledge Retrieval & Decision Support System

A production-grade, compliance-focused AI system designed for policy-grade decision support. This is **not a chatbot** - it's a decision guardrail platform that prioritizes correctness, traceability, and audit survivability over fluency.

## Core Features

- **Policy-Aware Retrieval**: Respects authority hierarchy, jurisdiction, effective dates, and role-based access
- **Conflict Detection**: Automatically detects conflicting policies and flags them for human review
- **Audit Trail**: Every decision is logged with full traceability
- **Explainable Outputs**: All answers include mandatory citations and confidence levels
- **Hallucination Prevention**: Explicitly returns "no answer" states when coverage is insufficient
- **Production-Ready Architecture**: Built with FastAPI, Pinecone, and OpenAI with swappable components

## Architecture

### Backend
- **FastAPI** - High-performance API framework
- **Pinecone** - Vector database for semantic search
- **OpenAI** - Embeddings (text-embedding-3-small) and LLM (gpt-4o-mini)
- **In-memory storage** - Audit records (will migrate to PostgreSQL)

### Key Components

1. **Retrieval Agent** - Executes policy-scoped search with filters
2. **Validation Agent** - Detects conflicts, validates coverage, enforces precedence
3. **Authority Resolution** - Applies policy hierarchy (Policy > SOP > Guideline > Email)
4. **Clause Extraction** - Granular policy clause retrieval with role-based filtering

## Setup

### Prerequisites

- Python 3.10+
- Pinecone API key
- OpenAI API key

### Installation

1. Install dependencies (already done if using existing venv):
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env` file (already configured)

### Running the System

1. Start the FastAPI server:
```bash
uvicorn app:app --reload
```

The server will start at `http://localhost:8000`

2. Seed sample data:
```bash
curl -X POST http://localhost:8000/seed-data
```

Or visit: `http://localhost:8000/docs` and use the interactive UI

3. Run the test suite:
```bash
python test_system.py
```

## API Endpoints

### `POST /answer`
Main endpoint for policy-aware question answering.

**Request:**
```json
{
  "query": "Can I get a refund for a product I bought 2 weeks ago?",
  "jurisdiction": "US",
  "as_of_date": "2024-06-15",
  "role": "customer"
}
```

### `GET /health` - Health check
### `POST /seed-data` - Seed sample data
### `GET /audit` - List audit records
### `GET /audit/{audit_id}` - Get specific audit record

## System Behavior

### Decision States

1. **SAFE** - Policy provides clear guidance, answer generated
2. **CONFLICT** - Multiple policies with equal authority contradict
3. **INSUFFICIENT_COVERAGE** - No applicable policy or relevance too low

### Authority Levels

- **Level 4**: Policy (highest authority)
- **Level 3**: SOP (Standard Operating Procedure)
- **Level 2**: Guideline
- **Level 1**: Email (lowest authority)

## Design Principles

1. **Correctness over Fluency** - Never fabricate information
2. **Explicit Refusals** - Return "no answer" when coverage is insufficient
3. **Audit Survivability** - Every decision is traceable
4. **Authority Precedence** - Higher authority always wins
5. **Temporal Validity** - Only use policies valid on query date