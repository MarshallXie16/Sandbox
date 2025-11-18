"""Repository for scoring profile operations."""
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models import ScoringProfile


class ScoringProfileRepository:
    """Repository for scoring profile database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def get_by_id(self, profile_id: int) -> Optional[ScoringProfile]:
        """Get scoring profile by ID."""
        return (
            self.db.query(ScoringProfile).filter(ScoringProfile.id == profile_id).first()
        )

    def get_by_name(self, name: str) -> Optional[ScoringProfile]:
        """Get scoring profile by name."""
        return self.db.query(ScoringProfile).filter(ScoringProfile.name == name).first()

    def get_default(self) -> Optional[ScoringProfile]:
        """Get the default scoring profile."""
        return (
            self.db.query(ScoringProfile).filter(ScoringProfile.is_default == True).first()
        )

    def get_all(self) -> List[ScoringProfile]:
        """Get all scoring profiles."""
        return self.db.query(ScoringProfile).all()

    def create(
        self,
        name: str,
        rules: Dict[str, Any],
        description: Optional[str] = None,
        is_default: bool = False,
    ) -> ScoringProfile:
        """Create a new scoring profile."""
        # If this is being set as default, unset other defaults
        if is_default:
            self.db.query(ScoringProfile).filter(ScoringProfile.is_default == True).update(
                {"is_default": False}
            )

        profile = ScoringProfile(
            name=name, description=description, rules=rules, is_default=is_default
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile

    def update(
        self,
        profile_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[ScoringProfile]:
        """Update a scoring profile."""
        profile = self.get_by_id(profile_id)
        if not profile:
            return None

        if name is not None:
            profile.name = name
        if description is not None:
            profile.description = description
        if rules is not None:
            profile.rules = rules
        if is_default is not None:
            if is_default:
                # Unset other defaults
                self.db.query(ScoringProfile).filter(
                    ScoringProfile.id != profile_id, ScoringProfile.is_default == True
                ).update({"is_default": False})
            profile.is_default = is_default

        self.db.commit()
        self.db.refresh(profile)

        return profile

    def delete(self, profile_id: int) -> bool:
        """Delete a scoring profile."""
        profile = self.get_by_id(profile_id)
        if not profile:
            return False

        # Don't allow deleting the default profile
        if profile.is_default:
            raise ValueError("Cannot delete the default scoring profile")

        self.db.delete(profile)
        self.db.commit()

        return True
