# Vector Store - Pinecone + OpenAI Embeddings
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from config import settings
from policy_data_model import PolicyChunk, PolicyClause, PolicyMetadata
from typing import Optional
from datetime import date


class VectorStore:
    """
    Vector store implementation using Pinecone and OpenAI embeddings.

    This class handles:
    - Embedding generation (OpenAI text-embedding-3-small)
    - Vector storage and retrieval (Pinecone)
    - Policy chunk and clause operations
    """

    def __init__(
        self,
        pinecone_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        index_name: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize vector store.

        Args:
            pinecone_api_key: Pinecone API key (defaults to config)
            openai_api_key: OpenAI API key (defaults to config)
            index_name: Pinecone index name (defaults to config)
            embedding_model: OpenAI embedding model to use
        """
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key or settings.pinecone_key)
        self.index_name = index_name or settings.pinecone_index_name

        # Get or create index
        self.index = self._get_or_create_index()

        # Initialize OpenAI for embeddings
        self.openai_client = OpenAI(api_key=openai_api_key or settings.openai_key)
        self.embedding_model = embedding_model
        self.embedding_dimension = 1536  # text-embedding-3-small dimension

    def _get_or_create_index(self):
        """Get existing index or create if it doesn't exist"""
        try:
            # Check if index exists
            if self.index_name not in [idx.name for idx in self.pc.list_indexes()]:
                # Create new index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )

            return self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Warning: Could not create/access Pinecone index: {e}")
            return self.pc.Index(self.index_name)  # Try to connect anyway

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [[0.0] * self.embedding_dimension for _ in texts]

    def upsert_policy_chunk(self, chunk: PolicyChunk):
        """
        Upsert a single policy chunk into Pinecone.

        Args:
            chunk: PolicyChunk to store
        """
        metadata = {
            "policy_id": chunk.metadata.policy_id,
            "authority_level": chunk.metadata.authority_level,
            "jurisdiction": chunk.metadata.jurisdiction,
            "effective_from": chunk.metadata.effective_from.isoformat(),
            "effective_to": chunk.metadata.effective_to.isoformat() if chunk.metadata.effective_to else None,
            "text": chunk.text,
            "type": "policy_chunk"
        }

        self.index.upsert(
            vectors=[(
                chunk.metadata.policy_id,
                chunk.embedding,
                metadata
            )],
            namespace="policies"
        )

    def upsert_clause(self, clause: PolicyClause):
        """
        Upsert a single clause into Pinecone.

        Args:
            clause: PolicyClause to store
        """
        if not clause.embedding:
            clause.embedding = self.embed_text(clause.text)

        metadata = {
            "clause_id": clause.clause_id,
            "policy_id": clause.policy_id,
            "clause_type": clause.clause_type,
            "text": clause.text,
            "type": "clause",
            "applies_to_roles": clause.applies_to_roles or [],
            "overrides": clause.overrides or [],
            "exception_scope": clause.exception_scope
        }

        self.index.upsert(
            vectors=[(
                clause.clause_id,
                clause.embedding,
                metadata
            )],
            namespace="clauses"
        )

    def query_policy_chunks(
        self,
        query: str,
        top_k: int = 20,
        filter_dict: Optional[dict] = None
    ) -> list[tuple[PolicyChunk, float]]:
        """
        Query for relevant policy chunks.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of (PolicyChunk, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.embed_text(query)

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace="policies",
            filter=filter_dict
        )

        # Convert results to PolicyChunk objects
        chunks_with_scores = []
        for match in results.matches:
            metadata = match.metadata

            chunk = PolicyChunk(
                text=metadata["text"],
                metadata=PolicyMetadata(
                    policy_id=metadata["policy_id"],
                    authority_level=metadata["authority_level"],
                    jurisdiction=metadata["jurisdiction"],
                    effective_from=date.fromisoformat(metadata["effective_from"]),
                    effective_to=date.fromisoformat(metadata["effective_to"]) if metadata.get("effective_to") else None
                ),
                embedding=match.values
            )

            chunks_with_scores.append((chunk, match.score))

        return chunks_with_scores

    def query_clauses(
        self,
        query: str,
        policy_ids: Optional[set[str]] = None,
        top_k: int = 10
    ) -> list[PolicyClause]:
        """
        Query for relevant clauses.

        Args:
            query: Search query
            policy_ids: Optional set of policy IDs to filter by
            top_k: Number of results to return

        Returns:
            List of PolicyClause objects
        """
        # Generate query embedding
        query_embedding = self.embed_text(query)

        # Build filter
        filter_dict = None
        if policy_ids:
            filter_dict = {"policy_id": {"$in": list(policy_ids)}}

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace="clauses",
            filter=filter_dict
        )

        # Convert results to PolicyClause objects
        clauses = []
        for match in results.matches:
            metadata = match.metadata

            clause = PolicyClause(
                clause_id=metadata["clause_id"],
                policy_id=metadata["policy_id"],
                text=metadata["text"],
                clause_type=metadata["clause_type"],
                embedding=match.values,
                applies_to_roles=metadata.get("applies_to_roles"),
                overrides=metadata.get("overrides", []),
                exception_scope=metadata.get("exception_scope")
            )

            clauses.append(clause)

        return clauses


# Global instance (singleton pattern for efficiency)
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Get or create the global vector store instance.

    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
