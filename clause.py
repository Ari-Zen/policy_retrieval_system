# Module
from policy_data_model import PolicyClause, PolicyChunk
from validate_result import ValidationResult
from decision_status import DecisionStatus
from retriever import retrieve_resolved_chunks, retrieve_and_validate
from vector_store import get_vector_store
import json

# Extract Clause
def extract_clauses(policy_id: str, text: str, llm) -> list[PolicyClause]:
    prompt = f''' 
You are extracting policy clauses.

Rules:
- Extract ONLY explicit rules stated in the text
- Do NOT infer intent
- Each clause must represent exactly one rule
- Assign exactly one clause_type

Valid clause types:
allow, deny, require, limit, define

Return JSON only.

policy text:
{text}
'''
    
    response = llm.invoke(prompt)

    clauses = json.loads(response.text)

    return [
        PolicyClause(
            clause_id=f'{policy_id}-{i}',
            policy_id=policy_id,
            text=c['text'],
            clause_type=c['clause_type']
        )
        for i, c in enumerate(clauses)
    ]

# Clause Embeddings & Indexing
def embed_clauses(clauses: list[PolicyClause], embedder):
    for clause in clauses:
        clause.embedding = embedder.encode(clause.text)

# Role applicabilty
def is_clause_applicable_for_role(
        clause: PolicyClause,
        role: str
) -> bool:
    if clause.applies_to_roles is None:
        return True
    return role in clause.applies_to_roles

# Clause vector search
def clause_vector_search(
        query: str,
        policy_ids: set[str],
        top_k: int = 10
) -> list[PolicyClause]:
    """
    Search for relevant clauses within approved policies.

    Args:
        query: Search query
        policy_ids: Set of approved policy IDs to search within
        top_k: Number of top results to return

    Returns:
        List of PolicyClause objects
    """
    vector_store = get_vector_store()
    clauses = vector_store.query_clauses(
        query=query,
        policy_ids=policy_ids,
        top_k=top_k
    )
    return clauses


# Retrieve clause
def retrieve_relevant_clauses(
        query: str,
        approved_policies: list[PolicyChunk],
        top_k: int = 10
) -> list[PolicyClause]:
    policy_ids = {p.metadata.policy_id for p in approved_policies}

    candidate_clauses = clause_vector_search(
        query=query,
        policy_ids=policy_ids,
        top_k=top_k
    )

    return candidate_clauses

# Clause coverage
def validate_clause_coverage(clauses: list[PolicyClause]) -> ValidationResult | None:
    if not clauses:
        return ValidationResult(
            status=DecisionStatus.INSUFFICIENT_COVERAGE,
            reason='No explicit policy clause addresses this question',
            supporting_policy_ids=[]
        )
    
    return None

# Clause confict
def detect_clause_conflict(clauses: list[PolicyClause]) -> ValidationResult | None:
    types = set(c.clause_type for c in clauses)

    if 'allow' in types and 'deny' in types:
        return ValidationResult(
            status=DecisionStatus.CONFLICT,
            reason='Conflicting allow/deny clauses detected',
            supporting_policy_ids=list(
                {c.policy_id for c in clauses}
            )
        )
    
    return None

# Clause retriever
def retrieve_validate_clauses(request):
    validation = retrieve_and_validate(request)
    if validation.status != DecisionStatus.SAFE:
        return validation, []
    
    policies = retrieve_resolved_chunks(request)

    # Clause retrieval
    clauses = retrieve_relevant_clauses(
        query=request.query,
        approved_policies=policies
    )

    # Filter role
    clauses = [
        c for c in clauses
        if is_clause_applicable_for_role(c, request.role)
    ]

    # Apply overrides first
    clauses = apply_overrides(clauses)

    # Clause conflict detection
    conflict = detect_clause_conflict(clauses)
    if conflict:
        return conflict, []
    
    # Clause coverage validation
    coverage = validate_clause_coverage(clauses)
    if coverage:
        return coverage, []
    
    return validation, clauses

# Overrides
def apply_overrides(
        clauses: list[PolicyClause]
) -> list[PolicyClause]:
    overridden_ids = set()

    for clause in clauses:
        overridden_ids.update(clause.overrides)

    return [
        c for c in clauses
        if c.clause_id not in overridden_ids
    ]

# Prompt
def build_clause_prompt(query: str, clauses: list[PolicyClause]) -> str:
    clause_block = "\n\n".join(
        f"[Policy ID: {c.policy_id} | {c.clause_type}]\n{c.text}"
        for c in clauses
    )

    return f'''
    User Question:
    {query}

    Application Policies:
    {clause_block}

    Answer:
    '''