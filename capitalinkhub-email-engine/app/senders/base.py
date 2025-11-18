"""
Base email sender interface using abstract base class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """
    Email message data structure.
    """
    to_email: str
    to_name: Optional[str]
    subject: str
    html_body: str
    text_body: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None


@dataclass
class SendResult:
    """
    Result of an email send attempt.
    """
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class EmailSender(ABC):
    """
    Abstract base class for email sending backends.

    All email senders must implement the send method.
    """

    @abstractmethod
    def send(self, message: EmailMessage) -> SendResult:
        """
        Send an email message.

        Args:
            message: EmailMessage object containing all email data

        Returns:
            SendResult object with success status and details

        Raises:
            Exception: If a critical error occurs during sending
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the sender is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
