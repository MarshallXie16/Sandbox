"""
SMTP email sender implementation.
Sends emails via standard SMTP protocol.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Optional

from app.core.config import settings
from app.core.logging import logger
from .base import EmailSender, EmailMessage, SendResult


class SmtpEmailSender(EmailSender):
    """
    SMTP email sender.

    Sends emails through a standard SMTP server.
    Requires: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD in configuration.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None,
        default_from_email: Optional[str] = None,
        default_from_name: Optional[str] = None
    ):
        """
        Initialize SMTP sender.

        Args:
            host: SMTP server host (defaults to settings)
            port: SMTP server port (defaults to settings)
            username: SMTP username (defaults to settings)
            password: SMTP password (defaults to settings)
            use_tls: Whether to use TLS (defaults to settings)
            default_from_email: Default sender email (defaults to settings)
            default_from_name: Default sender name (defaults to settings)
        """
        self.host = host or settings.smtp_host
        self.port = port or settings.smtp_port
        self.username = username or settings.smtp_username
        self.password = password or settings.smtp_password
        self.use_tls = use_tls if use_tls is not None else settings.smtp_use_tls
        self.default_from_email = default_from_email or settings.smtp_from_email
        self.default_from_name = default_from_name or settings.smtp_from_name

    def validate_config(self) -> bool:
        """Validate SMTP configuration."""
        if not self.host:
            logger.error("SMTP host is not configured")
            return False
        if not self.username:
            logger.error("SMTP username is not configured")
            return False
        if not self.password:
            logger.error("SMTP password is not configured")
            return False
        return True

    def send(self, message: EmailMessage) -> SendResult:
        """
        Send email via SMTP.

        Args:
            message: EmailMessage to send

        Returns:
            SendResult with success status
        """
        if not self.validate_config():
            return SendResult(
                success=False,
                error_message="SMTP is not properly configured"
            )

        try:
            # Create message
            msg = MIMEMultipart("alternative")

            # Set headers
            from_email = message.from_email or self.default_from_email
            from_name = message.from_name or self.default_from_name
            msg["From"] = formataddr((from_name, from_email))
            msg["To"] = formataddr((message.to_name or message.to_email, message.to_email))
            msg["Subject"] = message.subject

            if message.reply_to:
                msg["Reply-To"] = message.reply_to

            # Add custom headers
            if message.custom_headers:
                for key, value in message.custom_headers.items():
                    msg[key] = value

            # Add plain text version if provided
            if message.text_body:
                part1 = MIMEText(message.text_body, "plain")
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(message.html_body, "html")
            msg.attach(part2)

            logger.debug(f"Connecting to SMTP server {self.host}:{self.port}")

            # Connect and send
            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                if self.use_tls:
                    server.starttls()

                logger.debug(f"Logging in as {self.username}")
                server.login(self.username, self.password)

                logger.debug(f"Sending email to {message.to_email}")
                result = server.send_message(msg)

                logger.info(f"Email sent successfully to {message.to_email} via SMTP")

                return SendResult(
                    success=True,
                    message_id=msg.get("Message-ID"),
                    details={
                        "smtp_result": str(result),
                        "from": from_email,
                        "to": message.to_email
                    }
                )

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return SendResult(
                success=False,
                error_message=f"SMTP authentication failed: {str(e)}"
            )
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return SendResult(
                success=False,
                error_message=f"SMTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending via SMTP: {e}")
            return SendResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
