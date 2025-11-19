"""
VaultAI Integration Layer - Prompt Template Model
Stores reusable prompt templates with versioning support.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromptTemplate(Base):
    """
    Prompt templates for consistent AI interactions.

    Templates can include placeholders like {company_name}, {revenue}, etc.
    that are filled in at runtime.
    """

    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Template identification
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique template identifier (e.g., 'exit_ready_teaser_v1')",
    )

    domain: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Domain/module (exit_ready, facilitator, crm, analytics)",
    )

    task_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Specific task type (teaser, summary, checklist, etc.)",
    )

    # Template content
    system_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="System message for LLM",
    )

    user_prompt_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="User message template with placeholders",
    )

    # Configuration
    default_temperature: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Default temperature for this template",
    )

    default_max_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Default max tokens for this template",
    )

    # Metadata
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Template version number",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether template is currently active",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable description of template purpose",
    )

    placeholders: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="JSON schema of expected placeholders",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def render(self, **kwargs) -> str:
        """
        Render template with provided values.

        Args:
            **kwargs: Values to substitute into template placeholders.

        Returns:
            Rendered prompt string.

        Example:
            template = PromptTemplate(
                user_prompt_template="Company {company_name} has revenue of ${revenue}M"
            )
            rendered = template.render(company_name="Acme Corp", revenue=50)
            # Result: "Company Acme Corp has revenue of $50M"
        """
        return self.user_prompt_template.format(**kwargs)

    def __repr__(self) -> str:
        return f"<PromptTemplate(name='{self.name}', domain='{self.domain}', version={self.version})>"
