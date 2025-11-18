"""Scoring engine for calculating engagement scores."""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models import EngagementEvent, EngagementEntity, ScoringProfile, ScoreHistory, EntityType


class ScoringEngine:
    """
    Calculates engagement scores based on events and scoring profiles.

    The engine applies:
    - Base weights per event type
    - Time decay for older events
    - Custom scoring rules from profiles
    """

    def __init__(self, db: Session, scoring_profile: ScoringProfile):
        """
        Initialize the scoring engine.

        Args:
            db: Database session
            scoring_profile: Scoring profile to use for calculations
        """
        self.db = db
        self.profile = scoring_profile
        self.rules = scoring_profile.rules

    def calculate_score(
        self,
        events: List[EngagementEvent],
        reference_date: Optional[datetime] = None,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate engagement score from a list of events.

        Args:
            events: List of engagement events
            reference_date: Date to calculate score from (defaults to now)

        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        if not events:
            return 0.0, {}

        reference_date = reference_date or datetime.utcnow()

        # Get configuration
        event_weights = self.rules.get("event_weights", {})
        decay_config = self.profile.get_decay_config()

        # Calculate score components
        breakdown = {
            "total_events": len(events),
            "by_event_type": {},
            "by_source": {},
            "time_decay_applied": decay_config.get("enabled", False),
        }

        total_score = 0.0

        for event in events:
            # Get base weight for this event type
            base_weight = event_weights.get(event.event_type, 0.0)

            # Apply time decay if enabled
            if decay_config.get("enabled", True):
                days_old = (reference_date - event.occurred_at).days
                decay_days = decay_config.get("decay_days", 90)
                decay_factor = decay_config.get("decay_factor", 0.5)

                if days_old > decay_days:
                    # Apply decay: weight * decay_factor
                    weight = base_weight * decay_factor
                    breakdown.setdefault("decayed_events", 0)
                    breakdown["decayed_events"] += 1
                else:
                    weight = base_weight
            else:
                weight = base_weight

            # Add to total
            total_score += weight

            # Update breakdown
            event_type = event.event_type
            breakdown["by_event_type"][event_type] = (
                breakdown["by_event_type"].get(event_type, 0.0) + weight
            )

            source = event.source_system
            breakdown["by_source"][source] = breakdown["by_source"].get(source, 0.0) + weight

        breakdown["total_score"] = round(total_score, 2)

        return round(total_score, 2), breakdown

    def calculate_entity_score(
        self,
        entity: EngagementEntity,
        save_history: bool = True,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate score for a specific engagement entity.

        Args:
            entity: The engagement entity to score
            save_history: Whether to save the score to history

        Returns:
            Tuple of (score, breakdown)
        """
        # Get all events for this entity
        events = (
            self.db.query(EngagementEvent)
            .filter(EngagementEvent.engagement_entity_id == entity.id)
            .all()
        )

        score, breakdown = self.calculate_score(events)

        # Update entity
        entity.latest_score = score
        entity.score_breakdown = breakdown

        if events:
            # Update last activity time
            latest_event = max(events, key=lambda e: e.occurred_at)
            entity.last_activity_at = latest_event.occurred_at

        self.db.commit()

        # Save to history
        if save_history:
            history = ScoreHistory(
                engagement_entity_id=entity.id,
                scoring_profile_id=self.profile.id,
                score_value=score,
                score_components=breakdown,
            )
            self.db.add(history)
            self.db.commit()

        logger.debug(
            f"Calculated score for entity {entity.external_id} ({entity.entity_type}): {score}"
        )

        return score, breakdown

    def recalculate_all_scores(
        self,
        entity_type: Optional[EntityType] = None,
        min_events: int = 0,
    ) -> Dict[str, Any]:
        """
        Recalculate scores for all entities.

        Args:
            entity_type: Optional filter by entity type
            min_events: Only recalculate entities with at least this many events

        Returns:
            Summary statistics
        """
        logger.info(f"Starting score recalculation with profile: {self.profile.name}")

        # Build query
        query = self.db.query(EngagementEntity)
        if entity_type:
            query = query.filter(EngagementEntity.entity_type == entity_type)

        entities = query.all()

        stats = {
            "total_entities": len(entities),
            "recalculated": 0,
            "skipped": 0,
            "errors": 0,
        }

        for entity in entities:
            try:
                # Check event count if min_events specified
                event_count = (
                    self.db.query(EngagementEvent)
                    .filter(EngagementEvent.engagement_entity_id == entity.id)
                    .count()
                )

                if event_count < min_events:
                    stats["skipped"] += 1
                    continue

                self.calculate_entity_score(entity, save_history=True)
                stats["recalculated"] += 1

            except Exception as e:
                logger.error(
                    f"Error calculating score for entity {entity.id}: {str(e)}"
                )
                stats["errors"] += 1

        logger.info(
            f"Recalculation complete. Processed: {stats['recalculated']}, "
            f"Skipped: {stats['skipped']}, Errors: {stats['errors']}"
        )

        return stats


def get_scoring_engine(
    db: Session, profile_id: Optional[int] = None
) -> ScoringEngine:
    """
    Get a scoring engine instance with the specified or default profile.

    Args:
        db: Database session
        profile_id: Optional profile ID (uses default if not specified)

    Returns:
        ScoringEngine instance

    Raises:
        ValueError: If profile not found
    """
    if profile_id:
        profile = db.query(ScoringProfile).filter(ScoringProfile.id == profile_id).first()
    else:
        profile = (
            db.query(ScoringProfile).filter(ScoringProfile.is_default == True).first()
        )

    if not profile:
        raise ValueError(
            f"Scoring profile not found: {profile_id or 'default profile'}"
        )

    return ScoringEngine(db, profile)
