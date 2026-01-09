# Modules
from datetime import date, datetime
from pydantic import BaseModel
from decision_status import DecisionStatus

# Audit
class AuditRecord(BaseModel):
    audit_id: str
    timestamp: datetime

    # Request context
    query: str
    role: str
    jurisdiction: str
    as_of_date: date

    # Decision state
    decision_status: DecisionStatus
    decision_reason: str

    # Evidence
    policy_ids: list[str]
    clause_ids: list[str]

    # Output
    answer: str | None