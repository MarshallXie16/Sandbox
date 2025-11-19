"""
VaultAI Integration Layer - Embedding Model
Stores vector embeddings for semantic search using pgvector.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Embedding(Base):
    """
    Vector embeddings for semantic search.

    Stores embeddings of document chunks for:
    - Semantic similarity search
    - Retrieval-augmented generation (RAG)
    - Context injection for LLM requests
    """

    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Document reference
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to source document",
    )

    # Chunk information
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Index of this chunk within the document (0-based)",
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Text content of this chunk",
    )

    # Vector embedding
    # Note: Vector dimension must match EMBEDDINGS_DIMENSION in settings
    # Default is 1536 for OpenAI text-embedding-ada-002
    embedding: Mapped[list] = mapped_column(
        Vector(1536),  # Change dimension as needed
        nullable=False,
        comment="Vector embedding of chunk_text",
    )

    # Embedding metadata
    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Model used to generate embedding",
    )

    embedding_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Provider used (local, openai_compatible, etc.)",
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # Relationship
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="embeddings",
    )

    def __repr__(self) -> str:
        return (
            f"<Embedding(id={self.id}, document_id={self.document_id}, "
            f"chunk_index={self.chunk_index})>"
        )


# Composite index for document chunk retrieval
Index("idx_embeddings_document_chunk", Embedding.document_id, Embedding.chunk_index)

# Note: For vector similarity search, create an IVFFlat or HNSW index in Alembic migration:
# CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
# or
# CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);
