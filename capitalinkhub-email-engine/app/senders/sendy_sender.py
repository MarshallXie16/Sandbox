"""
Sendy email sender implementation.
Sends emails via Sendy HTTP API.
"""
import requests
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
from .base import EmailSender, EmailMessage, SendResult


class SendyEmailSender(EmailSender):
    """
    Sendy API email sender.

    Sends emails through Sendy's HTTP API.
    Requires: SENDY_BASE_URL, SENDY_API_KEY in configuration.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        list_id: Optional[str] = None
    ):
        """
        Initialize Sendy sender.

        Args:
            base_url: Sendy instance URL (defaults to settings)
            api_key: Sendy API key (defaults to settings)
            list_id: Default list ID (defaults to settings)
        """
        self.base_url = (base_url or settings.sendy_base_url or "").rstrip("/")
        self.api_key = api_key or settings.sendy_api_key
        self.list_id = list_id or settings.sendy_list_id

    def validate_config(self) -> bool:
        """Validate Sendy configuration."""
        if not self.base_url:
            logger.error("Sendy base URL is not configured")
            return False
        if not self.api_key:
            logger.error("Sendy API key is not configured")
            return False
        return True

    def send(self, message: EmailMessage) -> SendResult:
        """
        Send email via Sendy API.

        Uses the Sendy subscribe + trigger campaign API.
        For transactional emails, we'll use a direct API approach.

        Args:
            message: EmailMessage to send

        Returns:
            SendResult with success status
        """
        if not self.validate_config():
            return SendResult(
                success=False,
                error_message="Sendy is not properly configured"
            )

        try:
            # Sendy API endpoint for transactional emails
            # Note: Sendy primarily handles campaigns, not transactional emails
            # This is a simplified implementation - adjust based on your Sendy setup
            endpoint = f"{self.base_url}/api/campaigns/create.php"

            # Prepare the payload
            # This is a basic implementation - customize based on Sendy API docs
            payload = {
                "api_key": self.api_key,
                "from_name": message.from_name or settings.smtp_from_name,
                "from_email": message.from_email or settings.smtp_from_email,
                "reply_to": message.reply_to or message.from_email or settings.smtp_from_email,
                "subject": message.subject,
                "html_text": message.html_body,
                "query_string": f"email={message.to_email}",
                "send_campaign": "1",  # Send immediately
            }

            if self.list_id:
                payload["list_ids"] = self.list_id

            logger.debug(f"Sending email to {message.to_email} via Sendy")

            response = requests.post(endpoint, data=payload, timeout=30)

            # Sendy returns specific success/error messages
            response_text = response.text.strip()

            if response.status_code == 200 and "Campaign created" in response_text:
                logger.info(f"Email sent successfully to {message.to_email} via Sendy")
                return SendResult(
                    success=True,
                    message_id=f"sendy_{message.to_email}_{response_text}",
                    details={"response": response_text, "status_code": response.status_code}
                )
            else:
                logger.error(f"Sendy API error: {response_text}")
                return SendResult(
                    success=False,
                    error_message=f"Sendy API error: {response_text}",
                    details={"response": response_text, "status_code": response.status_code}
                )

        except requests.RequestException as e:
            logger.error(f"Network error sending via Sendy: {e}")
            return SendResult(
                success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending via Sendy: {e}")
            return SendResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
