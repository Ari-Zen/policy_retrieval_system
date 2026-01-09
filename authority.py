# Modules 
from retriever_model import RetrievalRequest
from policy_data_model import PolicyChunk, PolicyMetadata
from validate_result import ValidationResult
from decision_status import DecisionStatus

# Applicability Logic
def is_applicable(metadata: PolicyMetadata, request: RetrievalRequest) -> bool:
    if metadata.jurisdiction != request.jurisdiction:
        return False
    
    if metadata.effective_from > request.as_of_date:
        return False
    
    if metadata.effective_to and metadata.effective_to < request.as_of_date:
        return False
    
    return True

# Authority Resolution Logic
def resolve_authority(chunks: list[PolicyChunk]) -> list[PolicyChunk]:
    if not chunks:
        return []
    
    max_authority = max(
        chunk.metadata.authority_level for chunk in chunks
    )

    return [
        chunk for chunk in chunks
        if chunk.metadata.authority_level == max_authority
    ]

# Detect conflict
def detect_conflict(policies: list[PolicyChunk]) -> ValidationResult | None:
    if len(policies) <= 1:
        return None
    
    authority = policies[0].metadata.authority_level

    same_authority = [
        p for p in policies
        if p.metadata.authority_level == authority
    ]

    if len(same_authority) > 1:
        return ValidationResult(
            status=DecisionStatus.CONFLICT,
            reason='Multiple applicable policies with equal authority detected',
            supporting_policy_ids=[
                p.metadata.policy_id for p in same_authority
            ]
        )
    
    return None

# Coverage validation (depends on retrieva scores)
def validate_coverage(policies, similarity_scores) -> ValidationResult | None:
    if not policies:
        return ValidationResult(
            status=DecisionStatus.INSUFFICIENT_COVERAGE,
            reason='No applicable policy covers this question',
            supporting_policy_ids=[]
        )
    
    if max(similarity_scores) < 0.75:
        return ValidationResult(
            status=DecisionStatus.INSUFFICIENT_COVERAGE,
            reason='Policy relevance below confidence threshold',
            supporting_policy_ids=[
                p.metadata.policy_id for p in policies
            ]
        )
    
    return None