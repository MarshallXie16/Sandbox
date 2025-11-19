"""
Report models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class ReportTemplate(Base):
    """Report templates - defines different types of reports"""

    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)  # 'QUICK_SUMMARY'
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    reports = relationship("Report", back_populates="report_template")

    def __repr__(self):
        return f"<ReportTemplate(code='{self.code}', version={self.version})>"


class Report(Base):
    """Reports - generated valuation reports in Markdown format"""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    report_template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates.id"), nullable=False)
    title = Column(String, nullable=False)
    language = Column(String, nullable=False, default='en')
    status = Column(String, nullable=False, default='draft')  # 'draft' or 'final'
    content_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="reports")
    report_template = relationship("ReportTemplate", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, title='{self.title}', status='{self.status}')>"
