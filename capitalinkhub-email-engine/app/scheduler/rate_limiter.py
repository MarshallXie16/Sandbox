"""
Rate limiting logic for email campaigns.
"""
import random
import time
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from app.core.logging import logger
from app.models import Campaign, RateLimitProfile
from app.repositories import SendLogRepository


@dataclass
class RateLimitDecision:
    """
    Decision from rate limiter about whether to proceed with sending.
    """
    can_send: bool
    reason: Optional[str] = None
    wait_seconds: Optional[int] = None
    delay_seconds: Optional[float] = None  # Random delay to apply before sending


class RateLimiter:
    """
    Rate limiting service for email campaigns.

    Enforces hourly and daily sending limits, and calculates random delays.
    """

    def __init__(self, send_log_repo: SendLogRepository):
        """
        Initialize rate limiter.

        Args:
            send_log_repo: SendLogRepository for querying send history
        """
        self.send_log_repo = send_log_repo

    def check_rate_limit(
        self,
        campaign: Campaign,
        profile: Optional[RateLimitProfile] = None
    ) -> RateLimitDecision:
        """
        Check if campaign can send another email based on rate limits.

        Args:
            campaign: Campaign to check
            profile: Rate limit profile (uses campaign's profile if None)

        Returns:
            RateLimitDecision with can_send status and details
        """
        # Get rate limit profile
        if profile is None:
            profile = campaign.rate_limit_profile

        if profile is None:
            logger.warning(f"Campaign {campaign.id} has no rate limit profile, allowing send")
            return RateLimitDecision(
                can_send=True,
                delay_seconds=random.uniform(2, 7)
            )

        # Check hourly limit
        sent_last_hour = self.send_log_repo.count_sent_last_hour(campaign.id)
        if sent_last_hour >= profile.max_per_hour:
            logger.info(
                f"Campaign {campaign.id} hit hourly limit: "
                f"{sent_last_hour}/{profile.max_per_hour}"
            )
            return RateLimitDecision(
                can_send=False,
                reason=f"Hourly limit reached ({sent_last_hour}/{profile.max_per_hour})",
                wait_seconds=self._calculate_wait_for_next_hour()
            )

        # Check daily limit
        sent_today = self.send_log_repo.count_sent_today(campaign.id)
        if sent_today >= profile.max_per_day:
            logger.info(
                f"Campaign {campaign.id} hit daily limit: "
                f"{sent_today}/{profile.max_per_day}"
            )
            return RateLimitDecision(
                can_send=False,
                reason=f"Daily limit reached ({sent_today}/{profile.max_per_day})",
                wait_seconds=self._calculate_wait_for_next_day()
            )

        # Calculate random delay
        delay = random.uniform(
            profile.min_delay_seconds,
            profile.max_delay_seconds
        )

        logger.debug(
            f"Campaign {campaign.id} rate check passed: "
            f"hourly={sent_last_hour}/{profile.max_per_hour}, "
            f"daily={sent_today}/{profile.max_per_day}, "
            f"delay={delay:.2f}s"
        )

        return RateLimitDecision(
            can_send=True,
            delay_seconds=delay
        )

    def should_delay_after_last_send(
        self,
        campaign: Campaign,
        profile: Optional[RateLimitProfile] = None
    ) -> Optional[float]:
        """
        Check if we should delay based on the last send time.

        Args:
            campaign: Campaign to check
            profile: Rate limit profile (uses campaign's profile if None)

        Returns:
            Seconds to wait, or None if no wait needed
        """
        if profile is None:
            profile = campaign.rate_limit_profile

        if profile is None:
            return None

        last_send_time = self.send_log_repo.get_last_send_time(campaign.id)
        if last_send_time is None:
            return None

        # Calculate time since last send
        time_since_last = (datetime.utcnow() - last_send_time).total_seconds()

        # If not enough time has passed, wait
        min_delay = profile.min_delay_seconds
        if time_since_last < min_delay:
            wait_time = min_delay - time_since_last
            logger.debug(f"Waiting {wait_time:.2f}s since last send")
            return wait_time

        return None

    @staticmethod
    def _calculate_wait_for_next_hour() -> int:
        """
        Calculate seconds until the start of the next hour.

        Returns:
            Seconds to wait
        """
        now = datetime.utcnow()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return int((next_hour - now).total_seconds())

    @staticmethod
    def _calculate_wait_for_next_day() -> int:
        """
        Calculate seconds until the start of the next day.

        Returns:
            Seconds to wait
        """
        now = datetime.utcnow()
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((next_day - now).total_seconds())

    def apply_delay(self, delay_seconds: float) -> None:
        """
        Apply a delay (sleep).

        Args:
            delay_seconds: Seconds to sleep
        """
        if delay_seconds > 0:
            logger.debug(f"Applying delay of {delay_seconds:.2f} seconds")
            time.sleep(delay_seconds)

    def get_sending_stats(self, campaign: Campaign) -> dict:
        """
        Get current sending statistics for a campaign.

        Args:
            campaign: Campaign to get stats for

        Returns:
            Dictionary with sending statistics
        """
        profile = campaign.rate_limit_profile

        stats = {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "sent_last_hour": self.send_log_repo.count_sent_last_hour(campaign.id),
            "sent_today": self.send_log_repo.count_sent_today(campaign.id),
            "last_send_time": self.send_log_repo.get_last_send_time(campaign.id),
        }

        if profile:
            stats.update({
                "max_per_hour": profile.max_per_hour,
                "max_per_day": profile.max_per_day,
                "hourly_remaining": profile.max_per_hour - stats["sent_last_hour"],
                "daily_remaining": profile.max_per_day - stats["sent_today"],
            })

        return stats
