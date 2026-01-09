# Modules
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel

# Policy Data Model Architecture
class PolicyMetadata(BaseModel):
    policy_id: str
    authority_level: int
    jurisdiction: str
    effective_from: date
    effective_to: date | None

class PolicyChunk(BaseModel):
    text: str
    metadata: PolicyMetadata
    embedding: list[float]

class PolicyClause(BaseModel):
    clause_id: str
    policy_id: str
    text: str
    clause_type: Literal['allow', 'deny', 'require', 'limit', 'define']
    embedding: list[float] | None = None

    # Override metadata
    overrides: list[str] = []   # clause_ids this clause overrides
    exception_scope: str | None = None   # human-readable condition

    # Role scoping
    applies_to_roles: list[str] | None = None

