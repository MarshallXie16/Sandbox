"""Profile management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserProfile
from app.schemas.profile import UserProfileResponse, UserProfileUpdate
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("/profiles/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's matching profile.

    Returns profile information including:
    - Strengths and struggles (for matching)
    - Communication preferences
    - Availability and scheduling preferences
    - Matching metadata (active partnerships, seeking status)
    """
    # Fetch user profile
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. This should have been created during registration."
        )

    return profile


@router.patch("/profiles/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's matching profile.

    - **strengths**: 2-4 areas where you excel (e.g., career, fitness)
    - **struggles**: 2-4 areas where you need help (e.g., fashion, relationships)
    - **communication_style**: How you prefer to communicate (direct, supportive, motivational)
    - **commitment_level**: Your commitment level (casual, moderate, intense)
    - **preferred_check_in_frequency**: How often you want to check in (daily, 3x_week, weekly)
    - **available_days_of_week**: Days you're available (1=Monday, 7=Sunday)
    - **preferred_check_in_time**: Preferred time of day (morning, afternoon, evening)

    These preferences are used by the matching algorithm to find compatible partners.
    """
    # Fetch user profile
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    # Update only provided fields
    update_data = profile_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    # If user is updating their profile, they're likely seeking a partner
    if update_data:
        profile.is_seeking_partner = True

    await db.commit()
    await db.refresh(profile)

    return profile
