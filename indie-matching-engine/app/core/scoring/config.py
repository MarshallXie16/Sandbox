"""
Scoring configuration loaded from YAML.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class WeightsConfig(BaseModel):
    """Scoring weights configuration."""

    # Industry
    industry_exact: float = Field(default=30.0)
    industry_related: float = Field(default=15.0)
    industry_mismatch: float = Field(default=0.0)

    # Region
    region_exact: float = Field(default=20.0)
    region_nearby: float = Field(default=10.0)
    region_mismatch: float = Field(default=0.0)

    # Deal size
    deal_size_perfect: float = Field(default=25.0)
    deal_size_acceptable: float = Field(default=15.0)
    deal_size_stretch: float = Field(default=5.0)
    deal_size_mismatch: float = Field(default=-10.0)

    # Experience
    experience_strong: float = Field(default=10.0)
    experience_moderate: float = Field(default=5.0)
    experience_minimal: float = Field(default=0.0)

    # Engagement
    engagement_high: float = Field(default=10.0)
    engagement_medium: float = Field(default=5.0)
    engagement_low: float = Field(default=0.0)


class ThresholdsConfig(BaseModel):
    """Score thresholds configuration."""

    min_recommendation_score: float = Field(default=40.0)
    high_quality_match: float = Field(default=70.0)
    perfect_match: float = Field(default=85.0)


class DealSizeBand(BaseModel):
    """Deal size band definition."""

    min: float
    max: Optional[float] = None
    label: str


class DealSizeToleranceConfig(BaseModel):
    """Deal size tolerance thresholds."""

    perfect: float = Field(default=0.0)
    acceptable: float = Field(default=0.2)
    stretch: float = Field(default=0.5)


class EngagementThresholdsConfig(BaseModel):
    """Engagement score thresholds."""

    high: float = Field(default=75.0)
    medium: float = Field(default=50.0)
    low: float = Field(default=0.0)


class ScoringConfig(BaseModel):
    """
    Complete scoring configuration.
    """

    weights: WeightsConfig
    thresholds: ThresholdsConfig
    industry_relations: Dict[str, List[str]] = Field(default_factory=dict)
    region_relations: Dict[str, List[str]] = Field(default_factory=dict)
    deal_size_bands: Dict[str, DealSizeBand] = Field(default_factory=dict)
    deal_size_tolerance: DealSizeToleranceConfig = Field(
        default_factory=DealSizeToleranceConfig
    )
    engagement_thresholds: EngagementThresholdsConfig = Field(
        default_factory=EngagementThresholdsConfig
    )
    explanation_templates: Dict[str, str] = Field(default_factory=dict)


def load_scoring_config(config_path: str) -> ScoringConfig:
    """
    Load scoring configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        ScoringConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Scoring config not found: {config_path}")

    with open(path, "r") as f:
        raw_config = yaml.safe_load(f)

    # Parse deal size bands
    deal_size_bands = {}
    if "deal_size_bands" in raw_config:
        for band_name, band_data in raw_config["deal_size_bands"].items():
            deal_size_bands[band_name] = DealSizeBand(**band_data)

    # Build config
    config_data = {
        "weights": WeightsConfig(**raw_config.get("weights", {})),
        "thresholds": ThresholdsConfig(**raw_config.get("thresholds", {})),
        "industry_relations": raw_config.get("industry_relations", {}),
        "region_relations": raw_config.get("region_relations", {}),
        "deal_size_bands": deal_size_bands,
        "deal_size_tolerance": DealSizeToleranceConfig(
            **raw_config.get("deal_size_tolerance", {})
        ),
        "engagement_thresholds": EngagementThresholdsConfig(
            **raw_config.get("engagement_thresholds", {})
        ),
        "explanation_templates": raw_config.get("explanation_templates", {}),
    }

    return ScoringConfig(**config_data)


@lru_cache()
def get_scoring_config(config_path: Optional[str] = None) -> ScoringConfig:
    """
    Get cached scoring configuration.

    Args:
        config_path: Optional path override

    Returns:
        Cached ScoringConfig instance
    """
    from app.config import get_settings

    if config_path is None:
        config_path = get_settings().scoring_config_path

    return load_scoring_config(config_path)
