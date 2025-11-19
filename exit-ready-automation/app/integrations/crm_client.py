"""
Client for accessing IndieStack CRM data.
"""
from typing import Optional, Dict, Any
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


class CrmClient:
    """
    Client for reading data from IndieStack CRM core.

    Assumes CRM tables exist in a separate database or schema.
    This is a read-only client.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """
        Get contact by ID from CRM.

        Args:
            contact_id: CRM contact ID

        Returns:
            Dictionary with contact data or None
        """
        try:
            # Assuming CRM has a contacts table
            # Adjust table/column names based on actual CRM schema
            query = text("""
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    created_at,
                    updated_at
                FROM contacts
                WHERE id = :contact_id
            """)

            result = await self.session.execute(query, {"contact_id": contact_id})
            row = result.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }

        except Exception as e:
            logger.warning(f"Failed to fetch contact {contact_id} from CRM: {str(e)}")
            return None

    async def get_company(self, company_id: int) -> Optional[Dict[str, Any]]:
        """
        Get company by ID from CRM.

        Args:
            company_id: CRM company ID

        Returns:
            Dictionary with company data or None
        """
        try:
            # Assuming CRM has a companies table
            query = text("""
                SELECT
                    id,
                    name,
                    industry,
                    region,
                    website,
                    created_at,
                    updated_at
                FROM companies
                WHERE id = :company_id
            """)

            result = await self.session.execute(query, {"company_id": company_id})
            row = result.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "industry": row[2],
                "region": row[3],
                "website": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }

        except Exception as e:
            logger.warning(f"Failed to fetch company {company_id} from CRM: {str(e)}")
            return None

    async def find_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find contact by email in CRM.

        Args:
            email: Email address

        Returns:
            Dictionary with contact data or None
        """
        try:
            query = text("""
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    created_at,
                    updated_at
                FROM contacts
                WHERE LOWER(email) = LOWER(:email)
                LIMIT 1
            """)

            result = await self.session.execute(query, {"email": email})
            row = result.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }

        except Exception as e:
            logger.warning(f"Failed to find contact by email {email} in CRM: {str(e)}")
            return None

    async def write_back_exit_ready_status(
        self,
        contact_id: int,
        case_code: str,
        status: str
    ) -> bool:
        """
        Write Exit Ready case status back to CRM (optional).

        This allows the CRM to display Exit Ready status in contact records.

        Args:
            contact_id: CRM contact ID
            case_code: Exit Ready case code
            status: Current case status

        Returns:
            True if successful, False otherwise
        """
        try:
            # This would update a custom field in the CRM contacts table
            # Adjust based on actual CRM schema
            query = text("""
                UPDATE contacts
                SET
                    exit_ready_case_code = :case_code,
                    exit_ready_status = :status,
                    exit_ready_updated_at = NOW()
                WHERE id = :contact_id
            """)

            await self.session.execute(
                query,
                {
                    "contact_id": contact_id,
                    "case_code": case_code,
                    "status": status,
                }
            )
            await self.session.commit()

            logger.info(
                f"Updated CRM contact {contact_id} with Exit Ready status: {status}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to write back Exit Ready status to CRM contact {contact_id}: {str(e)}"
            )
            return False
