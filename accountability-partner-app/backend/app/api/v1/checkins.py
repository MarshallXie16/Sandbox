"""Check-in endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.schemas.checkin import (
    CheckInCreate,
    CheckInResponse,
    CheckInListResponse,
    AuthorInfo
)
from app.services.checkin_service import (
    create_checkin,
    get_partnership_checkins,
    get_checkin_by_id,
    mark_checkin_read,
    get_checkin_with_author
)

router = APIRouter()


@router.post("/partnerships/{partnership_id}/check-ins", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
async def create_partnership_checkin(
    partnership_id: UUID,
    checkin_data: CheckInCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new check-in for a partnership.

    Updates partnership last_interaction_at and user's last_active_at.
    """
    try:
        checkin = await create_checkin(
            db,
            partnership_id,
            current_user.id,
            checkin_data.what_i_did,
            checkin_data.what_i_struggled_with,
            checkin_data.what_i_need,
            checkin_data.content_type,
            checkin_data.media_url
        )

        # Get author info for response
        checkin, author = await get_checkin_with_author(db, checkin)

        return CheckInResponse(
            id=checkin.id,
            partnership_id=checkin.partnership_id,
            author=AuthorInfo(
                id=author.id,
                username=author.username,
                full_name=author.full_name,
                profile_picture_url=author.profile_picture_url
            ),
            what_i_did=checkin.what_i_did,
            what_i_struggled_with=checkin.what_i_struggled_with,
            what_i_need=checkin.what_i_need,
            content_type=checkin.content_type,
            text_content=checkin.text_content,
            media_url=checkin.media_url,
            is_read=checkin.is_read,
            response_id=checkin.response_id,
            created_at=checkin.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/partnerships/{partnership_id}/check-ins", response_model=CheckInListResponse)
async def list_partnership_checkins(
    partnership_id: UUID,
    limit: int = Query(20, ge=1, le=50, description="Number of check-ins per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List check-ins for a partnership (paginated, newest first).

    Query Parameters:
    - limit: Number of check-ins per page (1-50, default 20)
    - offset: Offset for pagination (default 0)
    """
    try:
        checkins, total, has_more = await get_partnership_checkins(
            db,
            partnership_id,
            current_user.id,
            limit,
            offset
        )

        # Build response with author info
        checkin_responses = []
        for checkin in checkins:
            checkin, author = await get_checkin_with_author(db, checkin)
            checkin_responses.append(
                CheckInResponse(
                    id=checkin.id,
                    partnership_id=checkin.partnership_id,
                    author=AuthorInfo(
                        id=author.id,
                        username=author.username,
                        full_name=author.full_name,
                        profile_picture_url=author.profile_picture_url
                    ),
                    what_i_did=checkin.what_i_did,
                    what_i_struggled_with=checkin.what_i_struggled_with,
                    what_i_need=checkin.what_i_need,
                    content_type=checkin.content_type,
                    text_content=checkin.text_content,
                    media_url=checkin.media_url,
                    is_read=checkin.is_read,
                    response_id=checkin.response_id,
                    created_at=checkin.created_at
                )
            )

        return CheckInListResponse(
            check_ins=checkin_responses,
            total=total,
            has_more=has_more
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/check-ins/{checkin_id}", response_model=CheckInResponse)
async def get_checkin(
    checkin_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get check-in details by ID.

    Authorization: Only partnership members can access.
    """
    try:
        checkin = await get_checkin_by_id(db, checkin_id, current_user.id)
        if not checkin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Check-in not found"
            )

        # Get author info
        checkin, author = await get_checkin_with_author(db, checkin)

        return CheckInResponse(
            id=checkin.id,
            partnership_id=checkin.partnership_id,
            author=AuthorInfo(
                id=author.id,
                username=author.username,
                full_name=author.full_name,
                profile_picture_url=author.profile_picture_url
            ),
            what_i_did=checkin.what_i_did,
            what_i_struggled_with=checkin.what_i_struggled_with,
            what_i_need=checkin.what_i_need,
            content_type=checkin.content_type,
            text_content=checkin.text_content,
            media_url=checkin.media_url,
            is_read=checkin.is_read,
            response_id=checkin.response_id,
            created_at=checkin.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.patch("/check-ins/{checkin_id}/read", response_model=CheckInResponse)
async def mark_checkin_as_read(
    checkin_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a check-in as read.

    Authorization: Only the partner (not the author) can mark as read.
    """
    try:
        checkin = await mark_checkin_read(db, checkin_id, current_user.id)

        # Get author info
        checkin, author = await get_checkin_with_author(db, checkin)

        return CheckInResponse(
            id=checkin.id,
            partnership_id=checkin.partnership_id,
            author=AuthorInfo(
                id=author.id,
                username=author.username,
                full_name=author.full_name,
                profile_picture_url=author.profile_picture_url
            ),
            what_i_did=checkin.what_i_did,
            what_i_struggled_with=checkin.what_i_struggled_with,
            what_i_need=checkin.what_i_need,
            content_type=checkin.content_type,
            text_content=checkin.text_content,
            media_url=checkin.media_url,
            is_read=checkin.is_read,
            response_id=checkin.response_id,
            created_at=checkin.created_at
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
