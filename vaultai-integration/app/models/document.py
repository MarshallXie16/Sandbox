"""
VaultAI Integration Layer - Document Model
Stores documents for retrieval-augmented generation (RAG).
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    """
    Document storage for RAG workflows.

    Documents can be:
    - Industry reports
    - Deal templates
    - Best practice guides
    - Historical transaction data (anonymized)
    - FAQ content
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Document identification
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="External document ID (if from another system)",
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Document title",
    )

    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full document content",
    )

    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="SHA-256 hash of content for deduplication",
    )

    # Classification
    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type (report, template, faq, guide, transaction)",
    )

    domain: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Domain/module (exit_ready, facilitator, crm, analytics)",
    )

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata (author, source, tags, etc.)",
    )

    # Source information
    source: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Document source (URL, file path, system)",
    )

    source_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="URL if document is from web",
    )

    # Processing status
    is_processed: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        index=True,
        comment="Whether document has been chunked and embedded",
    )

    chunk_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of chunks created from this document",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title[:50]}...', type='{self.document_type}')>"


# Indexes for common queries
Index("idx_documents_type_domain_created", Document.document_type, Document.domain, Document.created_at)
