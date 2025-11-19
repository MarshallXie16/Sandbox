"""
Email Engine Client for Facilitator Automation.

Integrates with capitalinkhub-email-engine for sending emails.
"""

from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailEngineClient:
    """
    Client for Email Engine integration.

    Handles sending introduction emails, NDA requests, offer notifications, etc.
    """

    def __init__(self):
        self.base_url = settings.email_engine_base_url
        self.api_key = settings.email_engine_api_key
        self.stub_mode = settings.email_engine_stub_mode

    async def send_buyer_intro(
        self,
        seller: Dict[str, Any],
        buyer: Dict[str, Any],
        engagement: Dict[str, Any],
        listing_info: Dict[str, Any]
    ) -> bool:
        """
        Send introduction email to buyer.

        Args:
            seller: Seller contact information
            buyer: Buyer contact information
            engagement: Engagement details
            listing_info: Listing/company information

        Returns:
            True if sent successfully
        """
        if self.stub_mode:
            logger.info(
                f"[STUB MODE] Would send intro email: "
                f"seller={seller.get('name')}, buyer={buyer.get('name')}"
            )
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails/buyer-intro",
                    json={
                        "seller": seller,
                        "buyer": buyer,
                        "engagement": engagement,
                        "listing": listing_info
                    },
                    headers={"X-API-Key": self.api_key},
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Sent intro email to buyer {buyer.get('email')}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send intro email: {e}")
            return False

    async def send_nda_request(
        self,
        seller: Dict[str, Any],
        buyer: Dict[str, Any],
        engagement: Dict[str, Any]
    ) -> bool:
        """
        Send NDA request email to buyer.

        Args:
            seller: Seller contact information
            buyer: Buyer contact information
            engagement: Engagement details

        Returns:
            True if sent successfully
        """
        if self.stub_mode:
            logger.info(
                f"[STUB MODE] Would send NDA request: "
                f"buyer={buyer.get('name')}, engagement={engagement.get('code')}"
            )
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails/nda-request",
                    json={
                        "seller": seller,
                        "buyer": buyer,
                        "engagement": engagement
                    },
                    headers={"X-API-Key": self.api_key},
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Sent NDA request to buyer {buyer.get('email')}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send NDA request: {e}")
            return False

    async def send_offer_notification(
        self,
        seller: Dict[str, Any],
        buyer: Dict[str, Any],
        engagement: Dict[str, Any],
        offer: Dict[str, Any]
    ) -> bool:
        """
        Send offer notification email to seller.

        Args:
            seller: Seller contact information
            buyer: Buyer contact information
            engagement: Engagement details
            offer: Offer details

        Returns:
            True if sent successfully
        """
        if self.stub_mode:
            logger.info(
                f"[STUB MODE] Would send offer notification: "
                f"seller={seller.get('name')}, offer_amount={offer.get('amount')}"
            )
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails/offer-notification",
                    json={
                        "seller": seller,
                        "buyer": buyer,
                        "engagement": engagement,
                        "offer": offer
                    },
                    headers={"X-API-Key": self.api_key},
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Sent offer notification to seller {seller.get('email')}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send offer notification: {e}")
            return False
