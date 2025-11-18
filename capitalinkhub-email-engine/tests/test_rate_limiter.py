"""
Tests for rate limiting functionality.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from app.scheduler.rate_limiter import RateLimiter, RateLimitDecision
from app.models import Campaign, RateLimitProfile, CampaignType, CampaignStatus, EmailBackend


@pytest.fixture
def mock_send_log_repo():
    """Create a mock SendLogRepository."""
    return Mock()


@pytest.fixture
def rate_limiter(mock_send_log_repo):
    """Create a RateLimiter instance with mock repository."""
    return RateLimiter(mock_send_log_repo)


@pytest.fixture
def sample_campaign():
    """Create a sample campaign."""
    campaign = Campaign(
        id=1,
        name="Test Campaign",
        type=CampaignType.COLD,
        subject_template="Test",
        body_template_path="test.html",
        sender_name="Test",
        sender_email="test@example.com",
        backend=EmailBackend.SMTP,
        status=CampaignStatus.SCHEDULED
    )
    return campaign


@pytest.fixture
def sample_rate_limit_profile():
    """Create a sample rate limit profile."""
    profile = RateLimitProfile(
        id=1,
        name="default",
        max_per_hour=100,
        max_per_day=500,
        min_delay_seconds=2,
        max_delay_seconds=7
    )
    return profile


def test_check_rate_limit_no_profile(rate_limiter, sample_campaign, mock_send_log_repo):
    """Test rate limit check when no profile is set."""
    sample_campaign.rate_limit_profile = None

    decision = rate_limiter.check_rate_limit(sample_campaign)

    assert decision.can_send is True
    assert decision.delay_seconds is not None
    assert 2 <= decision.delay_seconds <= 7


def test_check_rate_limit_under_limits(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test rate limit check when under all limits."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    # Mock repository to return counts under limits
    mock_send_log_repo.count_sent_last_hour.return_value = 50
    mock_send_log_repo.count_sent_today.return_value = 200

    decision = rate_limiter.check_rate_limit(sample_campaign)

    assert decision.can_send is True
    assert decision.delay_seconds is not None
    assert 2 <= decision.delay_seconds <= 7
    assert decision.reason is None


def test_check_rate_limit_hourly_limit_reached(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test rate limit check when hourly limit is reached."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    # Mock repository to return count at hourly limit
    mock_send_log_repo.count_sent_last_hour.return_value = 100
    mock_send_log_repo.count_sent_today.return_value = 100

    decision = rate_limiter.check_rate_limit(sample_campaign)

    assert decision.can_send is False
    assert "Hourly limit" in decision.reason
    assert decision.wait_seconds is not None


def test_check_rate_limit_daily_limit_reached(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test rate limit check when daily limit is reached."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    # Mock repository to return count at daily limit
    mock_send_log_repo.count_sent_last_hour.return_value = 50
    mock_send_log_repo.count_sent_today.return_value = 500

    decision = rate_limiter.check_rate_limit(sample_campaign)

    assert decision.can_send is False
    assert "Daily limit" in decision.reason
    assert decision.wait_seconds is not None


def test_should_delay_after_last_send_no_recent_send(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test delay check when there's no recent send."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    # Mock no last send time
    mock_send_log_repo.get_last_send_time.return_value = None

    delay = rate_limiter.should_delay_after_last_send(sample_campaign)

    assert delay is None


def test_should_delay_after_last_send_recent_send(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test delay check when there was a very recent send."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    # Mock last send time 1 second ago
    last_send = datetime.utcnow() - timedelta(seconds=1)
    mock_send_log_repo.get_last_send_time.return_value = last_send

    delay = rate_limiter.should_delay_after_last_send(sample_campaign)

    # Should wait about 1 more second (min_delay is 2)
    assert delay is not None
    assert 0 < delay <= 2


def test_should_delay_after_last_send_enough_time_passed(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test delay check when enough time has passed since last send."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    # Mock last send time 10 seconds ago
    last_send = datetime.utcnow() - timedelta(seconds=10)
    mock_send_log_repo.get_last_send_time.return_value = last_send

    delay = rate_limiter.should_delay_after_last_send(sample_campaign)

    assert delay is None


def test_get_sending_stats(rate_limiter, sample_campaign, sample_rate_limit_profile, mock_send_log_repo):
    """Test getting sending statistics."""
    sample_campaign.rate_limit_profile = sample_rate_limit_profile

    mock_send_log_repo.count_sent_last_hour.return_value = 25
    mock_send_log_repo.count_sent_today.return_value = 150
    mock_send_log_repo.get_last_send_time.return_value = datetime.utcnow()

    stats = rate_limiter.get_sending_stats(sample_campaign)

    assert stats["campaign_id"] == 1
    assert stats["sent_last_hour"] == 25
    assert stats["sent_today"] == 150
    assert stats["max_per_hour"] == 100
    assert stats["max_per_day"] == 500
    assert stats["hourly_remaining"] == 75
    assert stats["daily_remaining"] == 350
