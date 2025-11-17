"""CheckIn model."""
from sqlalchemy import Column, String, Boolean, Text, Float, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class CheckIn(Base):
    """Check-in model for partnership updates."""

    __tablename__ = "check_ins"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id = Column(UUID(as_uuid=True), ForeignKey("partnerships.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Check-in content
    content_type = Column(String(50), default="text")  # 'text', 'voice', 'photo'
    text_content = Column(Text)
    media_url = Column(Text)  # S3 URL for voice/photo

    # Structured prompts
    what_i_did = Column(Text)
    what_i_struggled_with = Column(Text)
    what_i_need = Column(Text)

    # Sentiment analysis (future AI feature)
    sentiment_score = Column(Float)  # -1 (negative) to 1 (positive)

    # Engagement
    is_read = Column(Boolean, default=False)
    response_id = Column(UUID(as_uuid=True), ForeignKey("check_ins.id"))  # if this is a response

    # Timestamps
    created_at = Column(Date, server_default=func.now(), index=True)

    # Relationships
    partnership = relationship("Partnership", back_populates="check_ins")
    author = relationship("User", back_populates="check_ins")

    def __repr__(self) -> str:
        return f"<CheckIn(id={self.id}, partnership_id={self.partnership_id}, author_id={self.author_id})>"
