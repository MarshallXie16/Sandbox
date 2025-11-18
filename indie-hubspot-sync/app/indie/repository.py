"""
Repository layer for accessing IndieStack CRM data.

Provides an abstraction over database access that can be swapped
for API access in the future.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.logging import get_logger
from app.indie.models import IndieContact, IndieCompany, IndieDeal, IndieBase
from app.models.tracking import EntityType

logger = get_logger(__name__)


class IndieRepository(Protocol):
    """Protocol defining the interface for IndieStack data access."""

    def get_contacts(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get contacts from IndieStack."""
        ...

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific contact by ID."""
        ...

    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact."""
        ...

    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact."""
        ...

    def get_companies(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get companies from IndieStack."""
        ...

    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific company by ID."""
        ...

    def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company."""
        ...

    def update_company(self, company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing company."""
        ...

    def get_deals(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get deals from IndieStack."""
        ...

    def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific deal by ID."""
        ...

    def create_deal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal."""
        ...

    def update_deal(self, deal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal."""
        ...


class IndieDatabaseRepository:
    """
    Database-based repository for IndieStack CRM.

    Accesses IndieStack data directly via PostgreSQL database.
    """

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database repository.

        Args:
            db_url: Database connection URL. If None, uses from settings.
        """
        self.db_url = db_url or settings.indie_db_dsn

        try:
            self.engine = create_engine(self.db_url, echo=settings.log_level == "DEBUG")
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("indie_db_repository_initialized", db_url=self.db_url)
        except Exception as e:
            logger.error("failed_to_initialize_indie_db", error=str(e))
            raise

    def _get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def _model_to_dict(self, model_instance: Any) -> Dict[str, Any]:
        """
        Convert SQLAlchemy model instance to dictionary.

        Handles JSON fields and datetime serialization.
        """
        result = {}
        for column in model_instance.__table__.columns:
            value = getattr(model_instance, column.name)

            # Parse JSON fields
            if column.name in ["details", "contacts"] and value:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

            # Convert datetime to ISO string
            if isinstance(value, datetime):
                value = value.isoformat()

            result[column.name] = value

        return result

    # Contact operations

    def get_contacts(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get contacts from IndieStack database."""
        session = self._get_session()
        try:
            query = session.query(IndieContact)

            if updated_since:
                query = query.filter(IndieContact.updated_at >= updated_since)

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)

            contacts = query.all()
            return [self._model_to_dict(c) for c in contacts]
        finally:
            session.close()

    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific contact by ID."""
        session = self._get_session()
        try:
            contact = session.query(IndieContact).filter(IndieContact.id == int(contact_id)).first()
            return self._model_to_dict(contact) if contact else None
        finally:
            session.close()

    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact."""
        session = self._get_session()
        try:
            # Handle JSON fields
            if "details" in data and isinstance(data["details"], dict):
                data["details"] = json.dumps(data["details"])

            contact = IndieContact(**data)
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return self._model_to_dict(contact)
        finally:
            session.close()

    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact."""
        session = self._get_session()
        try:
            contact = session.query(IndieContact).filter(IndieContact.id == int(contact_id)).first()

            if not contact:
                raise ValueError(f"Contact {contact_id} not found")

            # Handle JSON fields
            if "details" in data and isinstance(data["details"], dict):
                data["details"] = json.dumps(data["details"])

            for key, value in data.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)

            session.commit()
            session.refresh(contact)
            return self._model_to_dict(contact)
        finally:
            session.close()

    # Company operations

    def get_companies(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get companies from IndieStack database."""
        session = self._get_session()
        try:
            query = session.query(IndieCompany)

            if updated_since:
                query = query.filter(IndieCompany.updated_at >= updated_since)

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)

            companies = query.all()
            return [self._model_to_dict(c) for c in companies]
        finally:
            session.close()

    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific company by ID."""
        session = self._get_session()
        try:
            company = session.query(IndieCompany).filter(IndieCompany.id == int(company_id)).first()
            return self._model_to_dict(company) if company else None
        finally:
            session.close()

    def create_company(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company."""
        session = self._get_session()
        try:
            company = IndieCompany(**data)
            session.add(company)
            session.commit()
            session.refresh(company)
            return self._model_to_dict(company)
        finally:
            session.close()

    def update_company(self, company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing company."""
        session = self._get_session()
        try:
            company = session.query(IndieCompany).filter(IndieCompany.id == int(company_id)).first()

            if not company:
                raise ValueError(f"Company {company_id} not found")

            for key, value in data.items():
                if hasattr(company, key):
                    setattr(company, key, value)

            session.commit()
            session.refresh(company)
            return self._model_to_dict(company)
        finally:
            session.close()

    # Deal operations

    def get_deals(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        updated_since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get deals from IndieStack database."""
        session = self._get_session()
        try:
            query = session.query(IndieDeal)

            if updated_since:
                query = query.filter(IndieDeal.updated_at >= updated_since)

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)

            deals = query.all()
            return [self._model_to_dict(d) for d in deals]
        finally:
            session.close()

    def get_deal(self, deal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific deal by ID."""
        session = self._get_session()
        try:
            deal = session.query(IndieDeal).filter(IndieDeal.id == int(deal_id)).first()
            return self._model_to_dict(deal) if deal else None
        finally:
            session.close()

    def create_deal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal."""
        session = self._get_session()
        try:
            # Handle JSON fields
            if "contacts" in data and isinstance(data["contacts"], list):
                data["contacts"] = json.dumps(data["contacts"])

            deal = IndieDeal(**data)
            session.add(deal)
            session.commit()
            session.refresh(deal)
            return self._model_to_dict(deal)
        finally:
            session.close()

    def update_deal(self, deal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal."""
        session = self._get_session()
        try:
            deal = session.query(IndieDeal).filter(IndieDeal.id == int(deal_id)).first()

            if not deal:
                raise ValueError(f"Deal {deal_id} not found")

            # Handle JSON fields
            if "contacts" in data and isinstance(data["contacts"], list):
                data["contacts"] = json.dumps(data["contacts"])

            for key, value in data.items():
                if hasattr(deal, key):
                    setattr(deal, key, value)

            session.commit()
            session.refresh(deal)
            return self._model_to_dict(deal)
        finally:
            session.close()


def get_indie_repository() -> IndieRepository:
    """
    Factory function to get the appropriate IndieStack repository.

    Returns the repository based on INDIE_INTEGRATION_MODE setting.
    """
    if settings.indie_integration_mode == "database":
        return IndieDatabaseRepository()
    else:
        # Future: implement IndieAPIRepository
        raise NotImplementedError("API integration mode not yet implemented")
