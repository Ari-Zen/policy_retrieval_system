# Modules
from fastapi import FastAPI
from uuid import uuid4
from datetime import datetime
from audit import AuditRecord
from clause import retrieve_validate_clauses
from decision_status import DecisionStatus
from retriever_model import RetrievalRequest
from answer import generate_answer
from llm_client import get_llm_client

app = FastAPI()

# In-memory audit store (will be replaced with database later)
audit_store: dict[str, AuditRecord] = {}


def persist_audit_record(record: AuditRecord):
    """
    Persist audit record to in-memory store.

    In production, this would write to PostgreSQL.
    For now, stores in memory for demonstration.

    Args:
        record: AuditRecord to persist
    """
    audit_store[record.audit_id] = record
    print(f"[AUDIT] Stored record {record.audit_id}: {record.decision_status}")


# Initialize LLM client
llm_client = get_llm_client("openai", "gpt-4o-mini")

@app.post("/answer")
def answer_question(request: RetrievalRequest):
    audit_id = str(uuid4())
    timestamp = datetime.utcnow()

    validation, clauses = retrieve_validate_clauses(request)

    # Failure path
    if validation.status != DecisionStatus.SAFE:
        record = AuditRecord(
            audit_id=audit_id,
            timestamp=timestamp,
            query=request.query,
            role=request.role,
            jurisdiction=request.jurisdiction,
            as_of_date=request.as_of_date,
            decision_status=validation.status,
            decision_reason=validation.reason,
            policy_ids=validation.supporting_policy_ids,
            clause_ids=[],
            answer=None
        )
        persist_audit_record(record)
        return record

    # Success path
    answer = generate_answer(
        query=request.query,
        clauses=clauses,
        llm=llm_client
    )

    record = AuditRecord(
        audit_id=audit_id,
        timestamp=timestamp,
        query=request.query,
        role=request.role,
        jurisdiction=request.jurisdiction,
        as_of_date=request.as_of_date,
        decision_status=DecisionStatus.SAFE,
        decision_reason="Answer generated from validated clauses",
        policy_ids=list({c.policy_id for c in clauses}),
        clause_ids=[c.clause_id for c in clauses],
        answer=answer.answer
    )

    persist_audit_record(record)
    return record


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Policy-Aware Knowledge Retrieval System",
        "version": "1.0.0"
    }


@app.post("/seed-data")
def seed_test_data():
    """Seed the system with sample policy data for testing"""
    from sample_data import seed_sample_data
    result = seed_sample_data()
    return result


@app.get("/audit/{audit_id}")
def get_audit_record(audit_id: str):
    """Retrieve a specific audit record by ID"""
    if audit_id in audit_store:
        return audit_store[audit_id]
    return {"error": "Audit record not found"}


@app.get("/audit")
def list_audit_records():
    """List all audit records (for testing/demo)"""
    return {
        "total_records": len(audit_store),
        "records": list(audit_store.values())
    }