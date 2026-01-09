# Modules
from pydantic import BaseModel
from datetime import date
from policy_data_model import PolicyMetadata

# Retrieval Contract
class RetrievalRequest(BaseModel):
    query: str
    jurisdiction: str
    as_of_date: date
    role: str

class RetrievedPolicy(BaseModel):
    policy_id: str
    text: str
    metadata: PolicyMetadata
    inclusion_reason: str

class RetrievalResponse(BaseModel):
    policies: list[RetrievedPolicy]
    excluded_count: int