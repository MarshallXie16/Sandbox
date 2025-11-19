"""
Report models
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ReportTemplate(Base):
    """
    Report templates (e.g., Quick Report, Standard Report)
    """
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)  # QUICK_REPORT, STANDARD_REPORT
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    reports = relationship("Report", back_populates="template")

    def __repr__(self):
        return f"<ReportTemplate(code={self.code}, name={self.name})>"


class Report(Base):
    """
    Generated reports for projects
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates.id"), nullable=False)
    content = Column(Text, nullable=False)  # Markdown content
    format = Column(String, default="markdown", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="reports")
    template = relationship("ReportTemplate", back_populates="reports")

    def __repr__(self):
        return f"<Report(project_id={self.project_id}, template={self.template.code if self.template else None})>"
