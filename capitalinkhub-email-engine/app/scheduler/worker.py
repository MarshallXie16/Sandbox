"""
Email sending worker.

Processes campaigns and sends emails with rate limiting.
"""
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db_session
from app.core.logging import logger
from app.models import (
    Campaign,
    Recipient,
    CampaignStatus,
    RecipientStatus,
    SendStatus,
)
from app.repositories import (
    CampaignRepository,
    RecipientRepository,
    SendLogRepository,
)
from app.senders import EmailSenderFactory, EmailMessage
from app.utils import EmailRenderer
from .rate_limiter import RateLimiter
from .activity_logger import get_activity_logger


class EmailWorker:
    """
    Email sending worker.

    Processes scheduled campaigns and sends emails with rate limiting.
    """

    def __init__(self):
        """Initialize email worker."""
        self.db = get_db_session()
        self.campaign_repo = CampaignRepository(self.db)
        self.recipient_repo = RecipientRepository(self.db)
        self.send_log_repo = SendLogRepository(self.db)
        self.rate_limiter = RateLimiter(self.send_log_repo)
        self.email_renderer = EmailRenderer()
        self.activity_logger = get_activity_logger()

    def run_once(self, max_sends_per_run: int = 100) -> dict:
        """
        Run one iteration of the worker.

        Processes scheduled campaigns and sends up to max_sends_per_run emails.

        Args:
            max_sends_per_run: Maximum number of emails to send in this run

        Returns:
            Dictionary with run statistics
        """
        logger.info("Starting worker run")

        stats = {
            "campaigns_processed": 0,
            "emails_sent": 0,
            "emails_failed": 0,
            "campaigns_completed": 0,
            "start_time": datetime.utcnow(),
        }

        try:
            # Get campaigns that should be running
            campaigns = self.campaign_repo.get_scheduled_campaigns()

            if not campaigns:
                logger.info("No campaigns scheduled to run")
                return stats

            logger.info(f"Found {len(campaigns)} campaigns to process")

            # Process each campaign
            for campaign in campaigns:
                if stats["emails_sent"] >= max_sends_per_run:
                    logger.info(f"Reached max sends limit ({max_sends_per_run}), stopping")
                    break

                campaign_stats = self._process_campaign(
                    campaign,
                    max_sends=max_sends_per_run - stats["emails_sent"]
                )

                stats["campaigns_processed"] += 1
                stats["emails_sent"] += campaign_stats["sent"]
                stats["emails_failed"] += campaign_stats["failed"]
                if campaign_stats["completed"]:
                    stats["campaigns_completed"] += 1

            self.db.commit()

            stats["end_time"] = datetime.utcnow()
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()

            logger.info(
                f"Worker run completed: {stats['emails_sent']} sent, "
                f"{stats['emails_failed']} failed, "
                f"{stats['campaigns_completed']} campaigns completed "
                f"in {duration:.2f}s"
            )

            return stats

        except Exception as e:
            logger.error(f"Error in worker run: {e}", exc_info=True)
            self.db.rollback()
            raise
        finally:
            self.db.close()

    def _process_campaign(self, campaign: Campaign, max_sends: int) -> dict:
        """
        Process a single campaign.

        Args:
            campaign: Campaign to process
            max_sends: Maximum number of emails to send for this campaign

        Returns:
            Dictionary with campaign statistics
        """
        logger.info(f"Processing campaign: {campaign.name} (ID: {campaign.id})")

        stats = {
            "sent": 0,
            "failed": 0,
            "completed": False,
        }

        # Update status to sending if it was scheduled
        if campaign.status == CampaignStatus.SCHEDULED:
            self.campaign_repo.update_status(campaign, CampaignStatus.SENDING)

        # Get pending recipients
        pending_recipients = self.recipient_repo.get_pending_recipients(
            campaign.id,
            limit=max_sends
        )

        if not pending_recipients:
            logger.info(f"No pending recipients for campaign {campaign.id}")
            # Mark campaign as completed
            self.campaign_repo.update_status(campaign, CampaignStatus.COMPLETED)
            stats["completed"] = True
            return stats

        logger.info(f"Found {len(pending_recipients)} pending recipients")

        # Create email sender
        sender = EmailSenderFactory.create(campaign.backend)
        if not sender:
            logger.error(f"Failed to create email sender for backend {campaign.backend}")
            self.campaign_repo.update_status(campaign, CampaignStatus.FAILED)
            return stats

        # Send emails to recipients
        for recipient in pending_recipients:
            # Check rate limits
            rate_decision = self.rate_limiter.check_rate_limit(campaign)

            if not rate_decision.can_send:
                logger.info(
                    f"Rate limit reached for campaign {campaign.id}: {rate_decision.reason}"
                )
                break

            # Apply delay if needed
            if rate_decision.delay_seconds:
                self.rate_limiter.apply_delay(rate_decision.delay_seconds)

            # Send email
            send_result = self._send_email(campaign, recipient, sender)

            if send_result:
                stats["sent"] += 1
            else:
                stats["failed"] += 1

        # Check if campaign is completed
        remaining = self.recipient_repo.count_by_campaign_and_status(
            campaign.id,
            RecipientStatus.PENDING
        )

        if remaining == 0:
            logger.info(f"Campaign {campaign.id} completed")
            self.campaign_repo.update_status(campaign, CampaignStatus.COMPLETED)
            stats["completed"] = True

        return stats

    def _send_email(
        self,
        campaign: Campaign,
        recipient: Recipient,
        sender
    ) -> bool:
        """
        Send an email to a recipient.

        Args:
            campaign: Campaign
            recipient: Recipient
            sender: Email sender instance

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.debug(f"Sending email to {recipient.email} for campaign {campaign.id}")

            # Render email content
            merge_fields = recipient.get_merge_fields()
            subject, body = self.email_renderer.render_email(
                campaign.subject_template,
                campaign.body_template_path,
                merge_fields
            )

            # Create email message
            message = EmailMessage(
                to_email=recipient.email,
                to_name=recipient.name,
                subject=subject,
                html_body=body,
                from_email=campaign.sender_email,
                from_name=campaign.sender_name,
            )

            # Send email
            result = sender.send(message)

            # Create send log
            send_log = self.send_log_repo.create_log(
                campaign_id=campaign.id,
                recipient_id=recipient.id,
                backend=campaign.backend,
                status=SendStatus.SUCCESS if result.success else SendStatus.FAILED,
                message_id=result.message_id,
                error_message=result.error_message,
                details=result.details
            )

            # Update recipient status
            if result.success:
                self.recipient_repo.update_status(recipient, RecipientStatus.SENT)
                logger.info(f"Successfully sent email to {recipient.email}")
            else:
                self.recipient_repo.update_status(
                    recipient,
                    RecipientStatus.FAILED,
                    error=result.error_message
                )
                logger.error(f"Failed to send email to {recipient.email}: {result.error_message}")

            # Log to external system
            try:
                self.activity_logger.log_send_event(
                    campaign, recipient, send_log, result.success
                )
            except Exception as e:
                logger.error(f"Error logging to activity logger: {e}")
                # Don't fail the send because of logging error

            return result.success

        except Exception as e:
            logger.error(f"Error sending email to {recipient.email}: {e}", exc_info=True)

            # Create failed send log
            self.send_log_repo.create_log(
                campaign_id=campaign.id,
                recipient_id=recipient.id,
                backend=campaign.backend,
                status=SendStatus.FAILED,
                error_message=str(e)
            )

            # Update recipient status
            self.recipient_repo.update_status(
                recipient,
                RecipientStatus.FAILED,
                error=str(e)
            )

            return False
