"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's profile.

    Returns:
        Current user's profile information
    """
    return current_user


@router.patch("/users/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's basic profile information.

    - **full_name**: User's full name
    - **bio**: Short biography (max 500 characters)
    - **date_of_birth**: Birth date (for age verification)
    - **timezone**: User's timezone for scheduling

    Note: For updating matching preferences (strengths/struggles),
    use the /profiles/me endpoint instead.
    """
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate current user's account.

    This sets is_active to False. The user can still reactivate
    by logging in again (future feature).

    For complete account deletion, contact support.
    """
    current_user.is_active = False
    await db.commit()

    return None
