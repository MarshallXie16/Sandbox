"""
Email sender implementations and factory.
"""
from .base import EmailSender, EmailMessage, SendResult
from .sendy_sender import SendyEmailSender
from .smtp_sender import SmtpEmailSender
from .factory import EmailSenderFactory

__all__ = [
    "EmailSender",
    "EmailMessage",
    "SendResult",
    "SendyEmailSender",
    "SmtpEmailSender",
    "EmailSenderFactory",
]
