"""
Activity logging hook for external integrations.
"""
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.models import Campaign, Recipient, SendLog


class ActivityLogger(ABC):
    """
    Abstract base class for activity logging.

    Activity loggers push events to external systems for tracking.
    """

    @abstractmethod
    def log_send_event(
        self,
        campaign: Campaign,
        recipient: Recipient,
        send_log: SendLog,
        success: bool
    ) -> bool:
        """
        Log a send event.

        Args:
            campaign: Campaign that sent the email
            recipient: Recipient who received the email
            send_log: Send log entry
            success: Whether the send was successful

        Returns:
            True if logging succeeded, False otherwise
        """
        pass


class IndieStackWebhookLogger(ActivityLogger):
    """
    IndieStack webhook activity logger.

    Posts send events to IndieStack CRM via webhook.
    """

    def __init__(self, webhook_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize IndieStack webhook logger.

        Args:
            webhook_url: Webhook URL (defaults to settings)
            api_key: API key for authentication (defaults to settings)
        """
        self.webhook_url = webhook_url or settings.indiestack_webhook_url
        self.api_key = api_key or settings.indiestack_api_key

    def log_send_event(
        self,
        campaign: Campaign,
        recipient: Recipient,
        send_log: SendLog,
        success: bool
    ) -> bool:
        """
        Log send event to IndieStack webhook.

        Args:
            campaign: Campaign that sent the email
            recipient: Recipient who received the email
            send_log: Send log entry
            success: Whether the send was successful

        Returns:
            True if webhook call succeeded, False otherwise
        """
        if not self.webhook_url:
            logger.debug("IndieStack webhook URL not configured, skipping")
            return True  # Not an error, just not configured

        try:
            payload = {
                "event_type": "email_sent",
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "campaign_type": campaign.type.value,
                "recipient_email": recipient.email,
                "recipient_name": recipient.name,
                "recipient_segment": recipient.segment.value,
                "sent_at": send_log.sent_at.isoformat(),
                "success": success,
                "message_id": send_log.message_id,
                "backend": send_log.backend.value,
            }

            # Add error message if failed
            if not success and send_log.error_message:
                payload["error_message"] = send_log.error_message

            # Add API key if configured
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["X-API-Key"] = self.api_key

            logger.debug(f"Posting send event to IndieStack webhook: {self.webhook_url}")

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code in (200, 201, 202):
                logger.info(f"Successfully logged send event to IndieStack for {recipient.email}")
                return True
            else:
                logger.warning(
                    f"IndieStack webhook returned status {response.status_code}: {response.text}"
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Error posting to IndieStack webhook: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error logging to IndieStack: {e}")
            return False


class NoOpActivityLogger(ActivityLogger):
    """
    No-op activity logger.

    Does nothing - used when no external logging is needed.
    """

    def log_send_event(
        self,
        campaign: Campaign,
        recipient: Recipient,
        send_log: SendLog,
        success: bool
    ) -> bool:
        """Do nothing."""
        return True


def get_activity_logger() -> ActivityLogger:
    """
    Factory function to get the appropriate activity logger.

    Returns:
        ActivityLogger instance based on configuration
    """
    if settings.indiestack_webhook_url:
        logger.info("Using IndieStack webhook activity logger")
        return IndieStackWebhookLogger()
    else:
        logger.debug("No activity logger configured, using no-op logger")
        return NoOpActivityLogger()
