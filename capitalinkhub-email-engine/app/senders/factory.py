"""
Factory for creating email sender instances.
"""
from typing import Optional
from app.models import EmailBackend
from app.core.logging import logger
from .base import EmailSender
from .sendy_sender import SendyEmailSender
from .smtp_sender import SmtpEmailSender


class EmailSenderFactory:
    """
    Factory for creating email sender instances based on backend type.
    """

    @staticmethod
    def create(backend: EmailBackend) -> Optional[EmailSender]:
        """
        Create an email sender instance for the specified backend.

        Args:
            backend: EmailBackend enum value

        Returns:
            EmailSender instance or None if backend is not supported

        Raises:
            ValueError: If backend is not recognized
        """
        logger.debug(f"Creating email sender for backend: {backend}")

        if backend == EmailBackend.SENDY:
            sender = SendyEmailSender()
        elif backend == EmailBackend.SMTP:
            sender = SmtpEmailSender()
        else:
            raise ValueError(f"Unsupported email backend: {backend}")

        # Validate configuration
        if not sender.validate_config():
            logger.warning(f"{backend} sender is not properly configured")
            return None

        return sender

    @staticmethod
    def create_from_string(backend_name: str) -> Optional[EmailSender]:
        """
        Create an email sender from a string backend name.

        Args:
            backend_name: String name of the backend ('sendy' or 'smtp')

        Returns:
            EmailSender instance or None
        """
        try:
            backend = EmailBackend(backend_name.lower())
            return EmailSenderFactory.create(backend)
        except ValueError as e:
            logger.error(f"Invalid backend name: {backend_name}")
            raise
