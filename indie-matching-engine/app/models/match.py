"""
Buyer-Listing match model for storing computed match scores.
"""

from typing import Optional

from sqlalchemy import Float, Index, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class BuyerListingMatch(Base, TimestampMixin):
    """
    Represents a computed match score between a buyer (contact) and a listing (deal).

    This table stores pre-computed or cached match scores for fast retrieval.
    """

    __tablename__ = "buyer_listing_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys (references to CRM database)
    buyer_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Contact ID from indie-crm-core.contacts",
    )

    listing_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Deal ID from indie-crm-core.deals",
    )

    # Match score (0-100 scale)
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Overall match score (0-100)",
    )

    # Score breakdown
    components: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Score components: industry_score, region_score, size_score, etc.",
    )

    # Explanation
    reason_codes: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="List of reason codes/explanations for the match",
    )

    # Metadata
    matching_run_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="ID of the matching run that created this record",
    )

    # Denormalized data for faster filtering (optional)
    buyer_email: Mapped[Optional[str]] = mapped_column(
        JSON,
        nullable=True,
        comment="Cached buyer email for convenience",
    )

    listing_name: Mapped[Optional[str]] = mapped_column(
        JSON,
        nullable=True,
        comment="Cached listing name for convenience",
    )

    # Constraints
    __table_args__ = (
        # Ensure one match per buyer-listing pair
        UniqueConstraint("buyer_id", "listing_id", name="uix_buyer_listing"),
        # Index for fast lookups
        Index("ix_buyer_listing_matches_buyer_id", "buyer_id"),
        Index("ix_buyer_listing_matches_listing_id", "listing_id"),
        Index("ix_buyer_listing_matches_score", "score"),
        Index("ix_buyer_listing_matches_updated_at", "updated_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<BuyerListingMatch(id={self.id}, buyer_id={self.buyer_id}, "
            f"listing_id={self.listing_id}, score={self.score:.1f})>"
        )
