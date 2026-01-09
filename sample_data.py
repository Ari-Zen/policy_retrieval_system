# Sample Policy Data for Testing
from datetime import date
from policy_data_model import PolicyChunk, PolicyClause, PolicyMetadata
from vector_store import get_vector_store


# Sample policies covering refund scenarios
SAMPLE_POLICIES = [
    {
        "policy_id": "REFUND-001",
        "text": """
        Standard Refund Policy:
        Customers may request a full refund within 30 days of purchase if the product is unopened
        and in its original packaging. Refunds will be processed within 5-7 business days to the
        original payment method. Shipping costs are non-refundable unless the return is due to
        our error or a defective product.
        """,
        "metadata": PolicyMetadata(
            policy_id="REFUND-001",
            authority_level=4,  # Policy level (highest)
            jurisdiction="US",
            effective_from=date(2024, 1, 1),
            effective_to=None
        )
    },
    {
        "policy_id": "REFUND-002",
        "text": """
        Premium Customer Refund Policy:
        Premium members are eligible for extended refund windows of 60 days instead of the standard
        30 days. Premium members also receive free return shipping on all refund requests. This policy
        overrides the standard refund timeframe for premium members only.
        """,
        "metadata": PolicyMetadata(
            policy_id="REFUND-002",
            authority_level=4,  # Policy level
            jurisdiction="US",
            effective_from=date(2024, 3, 1),
            effective_to=None
        )
    },
    {
        "policy_id": "DIGITAL-001",
        "text": """
        Digital Products Refund Policy:
        Digital products (software, ebooks, digital licenses) are eligible for refund only within
        14 days of purchase and only if the product has not been downloaded or accessed. Once a
        digital product has been accessed or downloaded, no refunds will be issued except in cases
        of technical defects that cannot be resolved.
        """,
        "metadata": PolicyMetadata(
            policy_id="DIGITAL-001",
            authority_level=4,  # Policy level
            jurisdiction="US",
            effective_from=date(2024, 1, 1),
            effective_to=None
        )
    },
    {
        "policy_id": "EU-REFUND-001",
        "text": """
        EU Consumer Rights Directive Compliance:
        In accordance with EU consumer protection laws, customers in the European Union have the
        right to return products within 14 days without providing a reason. This applies to all
        physical products. For digital products, the right of withdrawal expires if the customer
        has explicitly agreed to immediate performance and acknowledged that they lose their right
        of withdrawal.
        """,
        "metadata": PolicyMetadata(
            policy_id="EU-REFUND-001",
            authority_level=4,  # Policy level
            jurisdiction="EU",
            effective_from=date(2024, 1, 1),
            effective_to=None
        )
    }
]

# Sample clauses (these would normally be extracted via LLM)
SAMPLE_CLAUSES = [
    PolicyClause(
        clause_id="REFUND-001-C1",
        policy_id="REFUND-001",
        text="Customers may request a full refund within 30 days of purchase",
        clause_type="allow",
        applies_to_roles=["customer", "support_agent"],
        overrides=[],
        exception_scope=None
    ),
    PolicyClause(
        clause_id="REFUND-001-C2",
        policy_id="REFUND-001",
        text="Product must be unopened and in original packaging",
        clause_type="require",
        applies_to_roles=["customer", "support_agent"],
        overrides=[],
        exception_scope=None
    ),
    PolicyClause(
        clause_id="REFUND-001-C3",
        policy_id="REFUND-001",
        text="Shipping costs are non-refundable",
        clause_type="deny",
        applies_to_roles=["customer", "support_agent"],
        overrides=[],
        exception_scope="unless return is due to our error or defective product"
    ),
    PolicyClause(
        clause_id="REFUND-002-C1",
        policy_id="REFUND-002",
        text="Premium members are eligible for extended refund windows of 60 days",
        clause_type="allow",
        applies_to_roles=["premium_customer", "support_agent"],
        overrides=["REFUND-001-C1"],  # Overrides the 30-day limit
        exception_scope="premium members only"
    ),
    PolicyClause(
        clause_id="REFUND-002-C2",
        policy_id="REFUND-002",
        text="Premium members receive free return shipping",
        clause_type="allow",
        applies_to_roles=["premium_customer", "support_agent"],
        overrides=["REFUND-001-C3"],  # Overrides shipping cost rule
        exception_scope="premium members only"
    ),
    PolicyClause(
        clause_id="DIGITAL-001-C1",
        policy_id="DIGITAL-001",
        text="Digital products eligible for refund within 14 days if not downloaded",
        clause_type="allow",
        applies_to_roles=["customer", "support_agent"],
        overrides=[],
        exception_scope="digital products only"
    ),
    PolicyClause(
        clause_id="DIGITAL-001-C2",
        policy_id="DIGITAL-001",
        text="No refunds after product has been accessed or downloaded",
        clause_type="deny",
        applies_to_roles=["customer", "support_agent"],
        overrides=[],
        exception_scope="except in cases of technical defects"
    ),
    PolicyClause(
        clause_id="EU-REFUND-001-C1",
        policy_id="EU-REFUND-001",
        text="EU customers have 14-day return right without providing reason",
        clause_type="allow",
        applies_to_roles=["customer", "support_agent"],
        overrides=[],
        exception_scope="EU customers only"
    )
]


def seed_sample_data():
    """
    Seed the vector store with sample policy data.

    This function uploads sample policies and clauses to Pinecone
    for testing and demonstration purposes.
    """
    print("[SEED] Starting sample data upload...")
    vector_store = get_vector_store()

    # Upload policy chunks
    print(f"[SEED] Uploading {len(SAMPLE_POLICIES)} policy chunks...")
    for policy_data in SAMPLE_POLICIES:
        # Create embedding
        embedding = vector_store.embed_text(policy_data["text"])

        # Create PolicyChunk
        chunk = PolicyChunk(
            text=policy_data["text"],
            metadata=policy_data["metadata"],
            embedding=embedding
        )

        # Upload to Pinecone
        vector_store.upsert_policy_chunk(chunk)
        print(f"[SEED]   ✓ Uploaded {chunk.metadata.policy_id}")

    # Upload clauses
    print(f"[SEED] Uploading {len(SAMPLE_CLAUSES)} clauses...")
    for clause in SAMPLE_CLAUSES:
        vector_store.upsert_clause(clause)
        print(f"[SEED]   ✓ Uploaded {clause.clause_id}")

    print("[SEED] Sample data upload complete!")
    return {
        "status": "success",
        "policies_uploaded": len(SAMPLE_POLICIES),
        "clauses_uploaded": len(SAMPLE_CLAUSES)
    }


if __name__ == "__main__":
    # Allow running this file directly to seed data
    seed_sample_data()
