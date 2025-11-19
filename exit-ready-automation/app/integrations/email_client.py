"""
Client for external Email Engine API.
"""
from typing import Dict, Any, Optional, List
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailEngineError(Exception):
    """Base exception for email engine errors."""
    pass


class EmailEngineClient:
    """
    Client for calling the external Email Engine API.

    Supports stub mode for development/testing.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        stub_mode: Optional[bool] = None,
    ):
        self.base_url = base_url or settings.email_engine_base_url
        self.api_key = api_key or settings.email_engine_api_key
        self.timeout = timeout or settings.email_engine_timeout
        self.stub_mode = stub_mode if stub_mode is not None else settings.email_engine_stub_mode

        logger.info(
            f"EmailEngineClient initialized "
            f"(stub_mode={self.stub_mode}, base_url={self.base_url})"
        )

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email via the email engine.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment dicts with {filename, url/content}
            template_id: Optional template ID
            template_data: Data for template rendering

        Returns:
            Dictionary with send status and message ID

        Raises:
            EmailEngineError: If sending fails
        """
        if self.stub_mode:
            return await self._send_stub_email(
                to, subject, body, cc, bcc, attachments, template_id, template_data
            )

        return await self._send_real_email(
            to, subject, body, cc, bcc, attachments, template_id, template_data
        )

    async def _send_real_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send email via real email engine."""
        try:
            payload = {
                "to": to,
                "subject": subject,
                "body": body,
            }

            if cc:
                payload["cc"] = cc
            if bcc:
                payload["bcc"] = bcc
            if attachments:
                payload["attachments"] = attachments
            if template_id:
                payload["template_id"] = template_id
            if template_data:
                payload["template_data"] = template_data

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/send",
                    json=payload,
                    headers=headers,
                )

                response.raise_for_status()
                data = response.json()

                logger.info(f"Email sent to {to} via email engine")
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Email API HTTP error: {e.response.status_code} - {e.response.text}")
            raise EmailEngineError(
                f"Email API returned {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Email API request error: {str(e)}")
            raise EmailEngineError(f"Failed to connect to Email API: {str(e)}")
        except Exception as e:
            logger.error(f"Email API unexpected error: {str(e)}")
            raise EmailEngineError(f"Unexpected error calling Email API: {str(e)}")

    async def _send_stub_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Stub implementation that logs instead of sending."""
        logger.info(
            f"[STUB] Email would be sent:\n"
            f"  To: {to}\n"
            f"  Subject: {subject}\n"
            f"  Body length: {len(body)} chars\n"
            f"  CC: {cc}\n"
            f"  BCC: {bcc}\n"
            f"  Attachments: {len(attachments or [])}\n"
            f"  Template: {template_id}\n"
            f"  Template data: {template_data is not None}"
        )

        return {
            "status": "stub_sent",
            "message_id": f"stub_{hash(to + subject)}",
            "to": to,
            "stub_mode": True,
        }

    async def send_intake_link(
        self,
        to: str,
        owner_name: str,
        company_name: str,
        intake_url: str,
        case_code: str,
    ) -> Dict[str, Any]:
        """
        Send intake form link to a seller.

        Args:
            to: Recipient email
            owner_name: Owner's name
            company_name: Company name
            intake_url: URL to intake form
            case_code: Case code for reference

        Returns:
            Send status
        """
        subject = f"Exit Ready - Complete Your Business Information Form"

        body = f"""
        <html>
        <body>
            <h2>Welcome to Exit Ready, {owner_name}!</h2>

            <p>Thank you for your interest in our Exit Ready service for <strong>{company_name}</strong>.</p>

            <p>To begin the process, please complete the intake form by clicking the link below:</p>

            <p><a href="{intake_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Complete Intake Form</a></p>

            <p>Or copy and paste this link into your browser:<br>
            {intake_url}</p>

            <p>Your case reference: <strong>{case_code}</strong></p>

            <p>If you have any questions, please don't hesitate to reach out.</p>

            <p>Best regards,<br>
            The Capital Link Team</p>
        </body>
        </html>
        """

        return await self.send_email(to=to, subject=subject, body=body)

    async def send_report_delivery(
        self,
        to: str,
        owner_name: str,
        company_name: str,
        report_url: str,
        case_code: str,
    ) -> Dict[str, Any]:
        """
        Send Exit Ready report to seller.

        Args:
            to: Recipient email
            owner_name: Owner's name
            company_name: Company name
            report_url: URL to download report PDF
            case_code: Case code for reference

        Returns:
            Send status
        """
        subject = f"Your Exit Ready Report for {company_name}"

        body = f"""
        <html>
        <body>
            <h2>Your Exit Ready Report is Ready, {owner_name}!</h2>

            <p>We're pleased to share your completed Exit Ready report for <strong>{company_name}</strong>.</p>

            <p>Download your report:</p>

            <p><a href="{report_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Report</a></p>

            <p>Or copy and paste this link into your browser:<br>
            {report_url}</p>

            <p>Your case reference: <strong>{case_code}</strong></p>

            <h3>Next Steps</h3>
            <p>Review your report and let us know if you'd like to discuss next steps, including:</p>
            <ul>
                <li>Business optimization recommendations</li>
                <li>Going to market with our Facilitator service</li>
                <li>Timing and preparation strategies</li>
            </ul>

            <p>We're here to help guide you through your exit journey.</p>

            <p>Best regards,<br>
            The Capital Link Team</p>
        </body>
        </html>
        """

        return await self.send_email(to=to, subject=subject, body=body)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the email engine is reachable.

        Returns:
            Dictionary with health status
        """
        if self.stub_mode:
            return {
                "status": "stub",
                "available": True,
                "message": "Running in stub mode",
            }

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()

                return {
                    "status": "healthy",
                    "available": True,
                    "message": "Email engine is reachable",
                }

        except Exception as e:
            logger.warning(f"Email engine health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "available": False,
                "message": f"Failed to reach email engine: {str(e)}",
            }
