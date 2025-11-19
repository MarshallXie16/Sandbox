"""
Service for document checklist management.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import CaseRepository, DocRepository, EventRepository
from app.schemas.document import DocCreate, DocResponse, DocChecklist
from app.core.workflow import CaseStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


# Standard document checklist for Exit Ready
STANDARD_CHECKLIST = [
    {"doc_type": "pnl_current_year", "label": "P&L Statement (Current Year YTD)", "required": True},
    {"doc_type": "pnl_last_year", "label": "P&L Statement (Last Full Year)", "required": True},
    {"doc_type": "pnl_2_years_ago", "label": "P&L Statement (2 Years Ago)", "required": False},
    {"doc_type": "pnl_3_years_ago", "label": "P&L Statement (3 Years Ago)", "required": False},
    {"doc_type": "balance_sheet", "label": "Balance Sheet (Most Recent)", "required": True},
    {"doc_type": "tax_return_last_year", "label": "Tax Return (Last Year)", "required": True},
    {"doc_type": "tax_return_2_years_ago", "label": "Tax Return (2 Years Ago)", "required": False},
    {"doc_type": "accounts_receivable", "label": "Accounts Receivable Aging", "required": False},
    {"doc_type": "customer_list", "label": "Customer List (Top 10-20)", "required": False},
    {"doc_type": "lease_agreement", "label": "Lease Agreement (if applicable)", "required": False},
    {"doc_type": "contracts", "label": "Key Contracts or Agreements", "required": False},
    {"doc_type": "org_chart", "label": "Organizational Chart", "required": False},
    {"doc_type": "other", "label": "Other Supporting Documents", "required": False},
]


class DocsService:
    """Service for managing document checklists."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.doc_repo = DocRepository(session)
        self.event_repo = EventRepository(session)

    async def generate_checklist(
        self,
        case_id: int,
        custom_checklist: Optional[List[Dict[str, Any]]] = None,
        actor: Optional[str] = None
    ) -> DocChecklist:
        """
        Generate document checklist for a case.

        Args:
            case_id: Case ID
            custom_checklist: Optional custom checklist (otherwise uses standard)
            actor: Who generated the checklist

        Returns:
            Document checklist
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Use custom checklist or standard
        checklist_template = custom_checklist or STANDARD_CHECKLIST

        # Create document entries
        docs_data = []
        for item in checklist_template:
            docs_data.append({
                "case_id": case_id,
                "doc_type": item["doc_type"],
                "label": item["label"],
                "required": item.get("required", False),
                "status": "pending",
            })

        docs = await self.doc_repo.create_bulk(docs_data)

        # Update case status
        await self.case_repo.update_status(case_id, CaseStatus.DOCS_COLLECTING.value)

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "checklist_generated",
            "payload": {
                "total_docs": len(docs),
                "required_docs": sum(1 for d in docs if d.required),
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Generated checklist for case {case.case_code} ({len(docs)} documents)")

        return await self.get_checklist(case_id)

    async def get_checklist(self, case_id: int) -> DocChecklist:
        """
        Get document checklist for a case.

        Args:
            case_id: Case ID

        Returns:
            Document checklist with stats
        """
        docs = await self.doc_repo.get_by_case_id(case_id)
        stats = await self.doc_repo.get_checklist_stats(case_id)

        doc_responses = [DocResponse.model_validate(d) for d in docs]

        return DocChecklist(
            case_id=case_id,
            documents=doc_responses,
            **stats
        )

    async def mark_document_received(
        self,
        doc_id: int,
        file_url: str,
        notes: Optional[str] = None,
        actor: Optional[str] = None
    ) -> DocResponse:
        """
        Mark a document as received.

        Args:
            doc_id: Document ID
            file_url: URL to uploaded file
            notes: Optional notes
            actor: Who marked it received

        Returns:
            Updated document
        """
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        # Update document
        update_data = {
            "status": "received",
            "file_url": file_url,
        }
        if notes:
            update_data["notes"] = notes

        doc = await self.doc_repo.update(doc_id, update_data)

        # Log event
        await self.event_repo.create({
            "case_id": doc.case_id,
            "event_type": "document_received",
            "payload": {
                "doc_type": doc.doc_type,
                "file_url": file_url,
            },
            "actor": actor or "system",
        })

        # Check if all required docs are received
        await self._check_docs_complete(doc.case_id)

        await self.session.commit()

        logger.info(f"Marked document {doc.doc_type} as received for case {doc.case_id}")

        return DocResponse.model_validate(doc)

    async def waive_document(
        self,
        doc_id: int,
        notes: Optional[str] = None,
        actor: Optional[str] = None
    ) -> DocResponse:
        """
        Waive a document requirement.

        Args:
            doc_id: Document ID
            notes: Reason for waiving
            actor: Who waived it

        Returns:
            Updated document
        """
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        # Update document
        update_data = {"status": "waived"}
        if notes:
            update_data["notes"] = notes

        doc = await self.doc_repo.update(doc_id, update_data)

        # Log event
        await self.event_repo.create({
            "case_id": doc.case_id,
            "event_type": "document_waived",
            "payload": {
                "doc_type": doc.doc_type,
                "notes": notes,
            },
            "actor": actor or "system",
        })

        # Check if all required docs are complete
        await self._check_docs_complete(doc.case_id)

        await self.session.commit()

        logger.info(f"Waived document {doc.doc_type} for case {doc.case_id}")

        return DocResponse.model_validate(doc)

    async def _check_docs_complete(self, case_id: int) -> None:
        """
        Check if all required documents are received/waived.
        If yes, update case status to financials_ready.
        """
        stats = await self.doc_repo.get_checklist_stats(case_id)

        required = stats["required_docs"]
        received = stats["received_docs"]
        waived = stats["waived_docs"]

        if required > 0 and (received + waived) >= required:
            # All required docs are complete
            case = await self.case_repo.get_by_id(case_id)

            if case and case.status == CaseStatus.DOCS_COLLECTING.value:
                await self.case_repo.update_status(
                    case_id,
                    CaseStatus.FINANCIALS_READY.value
                )

                await self.event_repo.create({
                    "case_id": case_id,
                    "event_type": "docs_complete",
                    "payload": stats,
                    "actor": "system",
                })

                logger.info(f"All required documents complete for case {case_id}")
