# Module
from retriever_model import RetrievalRequest, RetrievalResponse, RetrievedPolicy
from policy_data_model import PolicyChunk
from authority import is_applicable, resolve_authority, detect_conflict, validate_coverage
from validate_result import ValidationResult
from decision_status import DecisionStatus
from vector_store import get_vector_store

# Vector Search Function
def vector_search(query: str, top_k: int = 20) -> list[PolicyChunk]:
    """
    Perform vector similarity search for policy chunks.

    Args:
        query: Search query text
        top_k: Number of top results to return

    Returns:
        List of PolicyChunk objects (without scores)
    """
    vector_store = get_vector_store()
    chunks_with_scores = vector_store.query_policy_chunks(query, top_k=top_k)

    # Return just the chunks (scores handled separately in retrieve_policies_with_scores)
    return [chunk for chunk, score in chunks_with_scores]


# Retrieval Functions
def retrieve_resolved_chunks(request: RetrievalRequest) -> list[PolicyChunk]:
    candidate = vector_search(request.query, top_k=20)

    valid = []
    for chunk in candidate:
        if is_applicable(chunk.metadata, request):
            valid.append(chunk)

    return resolve_authority(valid)

def retrieve_policies(request: RetrievalRequest) -> RetrievalResponse:
    candidates = vector_search(request.query, top_k=20)

    valid = []
    excluded = 0

    for chunk in candidates:
        if not is_applicable(chunk.metadata, request):
            excluded += 1
            continue

        valid.append(chunk)

    resolved = resolve_authority(valid)

    return build_response(resolved, excluded)


def build_response(resolved: list[PolicyChunk], excluded_count: int) -> RetrievalResponse:
    """
    Build a RetrievalResponse from resolved chunks.

    Args:
        resolved: List of resolved PolicyChunk objects
        excluded_count: Number of chunks excluded by filters

    Returns:
        RetrievalResponse with formatted policies
    """
    policies = []
    for chunk in resolved:
        policy = RetrievedPolicy(
            policy_id=chunk.metadata.policy_id,
            text=chunk.text,
            metadata=chunk.metadata,
            inclusion_reason=f"Authority level {chunk.metadata.authority_level}, applicable to jurisdiction"
        )
        policies.append(policy)

    return RetrievalResponse(
        policies=policies,
        excluded_count=excluded_count
    )

def retrieve_policies_with_scores(request: RetrievalRequest) -> tuple[list[PolicyChunk], list[float]]:
    """
    Retrieve policies with their similarity scores.

    Args:
        request: Retrieval request with query and filters

    Returns:
        Tuple of (policies, similarity_scores)
    """
    vector_store = get_vector_store()
    chunks_with_scores = vector_store.query_policy_chunks(request.query, top_k=20)

    valid_chunks = []
    valid_scores = []

    for chunk, score in chunks_with_scores:
        if is_applicable(chunk.metadata, request):
            valid_chunks.append(chunk)
            valid_scores.append(score)

    # Apply authority resolution
    resolved = resolve_authority(valid_chunks)

    # Extract scores for resolved chunks only
    resolved_scores = []
    for resolved_chunk in resolved:
        for idx, chunk in enumerate(valid_chunks):
            if chunk.metadata.policy_id == resolved_chunk.metadata.policy_id:
                resolved_scores.append(valid_scores[idx])
                break

    return resolved, resolved_scores


# Retrieve and validate chunks
def retrieve_and_validate(request):
    policies, scores = retrieve_policies_with_scores(request)

    conflict = detect_conflict(policies)
    if conflict:
        return conflict
    
    coverage = validate_coverage(policies, scores)
    if coverage:
        return coverage
    
    return ValidationResult(
        status=DecisionStatus.SAFE,
        reason='Policies applicable, authoritative, and sufficient',
        supporting_policy_ids=[
            p.metadata.policy_id for p in policies
        ]
    )