"""
Repository for Exit Ready document database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExitReadyDoc
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocRepository:
    """Repository for Exit Ready document data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, doc_data: Dict[str, Any]) -> ExitReadyDoc:
        """
        Create a new document entry.

        Args:
            doc_data: Dictionary of document attributes

        Returns:
            Created ExitReadyDoc instance
        """
        doc = ExitReadyDoc(**doc_data)
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        logger.info(f"Created document {doc.doc_type} for case {doc.case_id}")
        return doc

    async def create_bulk(
        self,
        docs_data: List[Dict[str, Any]]
    ) -> List[ExitReadyDoc]:
        """
        Create multiple document entries.

        Args:
            docs_data: List of document dictionaries

        Returns:
            List of created ExitReadyDoc instances
        """
        docs = [ExitReadyDoc(**data) for data in docs_data]
        self.session.add_all(docs)
        await self.session.flush()

        # Refresh all
        for doc in docs:
            await self.session.refresh(doc)

        logger.info(f"Created {len(docs)} documents")
        return docs

    async def get_by_id(self, doc_id: int) -> Optional[ExitReadyDoc]:
        """
        Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            ExitReadyDoc or None if not found
        """
        query = select(ExitReadyDoc).where(ExitReadyDoc.id == doc_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_case_id(self, case_id: int) -> List[ExitReadyDoc]:
        """
        Get all documents for a case.

        Args:
            case_id: Case ID

        Returns:
            List of ExitReadyDoc instances
        """
        query = select(ExitReadyDoc).where(
            ExitReadyDoc.case_id == case_id
        ).order_by(ExitReadyDoc.doc_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_case_and_status(
        self,
        case_id: int,
        status: str
    ) -> List[ExitReadyDoc]:
        """
        Get documents by case and status.

        Args:
            case_id: Case ID
            status: Document status

        Returns:
            List of ExitReadyDoc instances
        """
        query = select(ExitReadyDoc).where(
            and_(
                ExitReadyDoc.case_id == case_id,
                ExitReadyDoc.status == status
            )
        ).order_by(ExitReadyDoc.doc_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        doc_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[ExitReadyDoc]:
        """
        Update a document.

        Args:
            doc_id: Document ID
            update_data: Dictionary of fields to update

        Returns:
            Updated ExitReadyDoc or None if not found
        """
        doc = await self.get_by_id(doc_id)
        if not doc:
            return None

        for key, value in update_data.items():
            if hasattr(doc, key):
                setattr(doc, key, value)

        doc.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(doc)
        logger.info(f"Updated document {doc.doc_type} (ID: {doc.id})")
        return doc

    async def update_status(
        self,
        doc_id: int,
        status: str,
        file_url: Optional[str] = None
    ) -> Optional[ExitReadyDoc]:
        """
        Update document status.

        Args:
            doc_id: Document ID
            status: New status
            file_url: Optional file URL

        Returns:
            Updated ExitReadyDoc or None if not found
        """
        update_data = {"status": status}

        if status == "received":
            update_data["received_at"] = datetime.utcnow()

        if file_url:
            update_data["file_url"] = file_url

        return await self.update(doc_id, update_data)

    async def delete(self, doc_id: int) -> bool:
        """
        Delete a document.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        doc = await self.get_by_id(doc_id)
        if not doc:
            return False

        await self.session.delete(doc)
        logger.info(f"Deleted document {doc.doc_type} (ID: {doc.id})")
        return True

    async def get_checklist_stats(self, case_id: int) -> Dict[str, Any]:
        """
        Get document checklist statistics for a case.

        Args:
            case_id: Case ID

        Returns:
            Dictionary of checklist statistics
        """
        # Total docs
        total_query = select(func.count(ExitReadyDoc.id)).where(
            ExitReadyDoc.case_id == case_id
        )
        total_result = await self.session.execute(total_query)
        total = total_result.scalar_one()

        # Required docs
        required_query = select(func.count(ExitReadyDoc.id)).where(
            and_(
                ExitReadyDoc.case_id == case_id,
                ExitReadyDoc.required == True
            )
        )
        required_result = await self.session.execute(required_query)
        required = required_result.scalar_one()

        # By status
        status_query = select(
            ExitReadyDoc.status,
            func.count(ExitReadyDoc.id)
        ).where(
            ExitReadyDoc.case_id == case_id
        ).group_by(ExitReadyDoc.status)

        status_result = await self.session.execute(status_query)
        status_counts = {status: count for status, count in status_result.all()}

        pending = status_counts.get("pending", 0)
        received = status_counts.get("received", 0)
        waived = status_counts.get("waived", 0)

        completion_pct = 0
        if required > 0:
            completion_pct = round((received / required) * 100, 2)

        return {
            "total_docs": total,
            "required_docs": required,
            "pending_docs": pending,
            "received_docs": received,
            "waived_docs": waived,
            "completion_percentage": completion_pct,
        }
