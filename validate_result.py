# Modules
from pydantic import BaseModel
from decision_status import DecisionStatus

# Validate result
class ValidationResult(BaseModel):
    status: DecisionStatus
    reason: str
    supporting_policy_ids: list[str]