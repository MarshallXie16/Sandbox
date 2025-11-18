"""Goal endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalListResponse,
    CompleteGoalRequest
)
from app.services.goal_service import (
    create_goal,
    get_partnership_goals,
    get_goal_by_id,
    update_goal,
    delete_goal,
    complete_goal
)

router = APIRouter()


@router.post("/partnerships/{partnership_id}/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_partnership_goal(
    partnership_id: UUID,
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new goal for a partnership.

    - Individual goals: Set owner to current user
    - Mutual goals: No owner (both partners work on it)
    """
    try:
        goal = await create_goal(
            db,
            partnership_id,
            current_user.id,
            goal_data.title,
            goal_data.description,
            goal_data.category,
            goal_data.is_mutual,
            goal_data.target_date,
            [s.model_dump() for s in goal_data.subtasks] if goal_data.subtasks else []
        )
        return goal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/partnerships/{partnership_id}/goals", response_model=GoalListResponse)
async def list_partnership_goals(
    partnership_id: UUID,
    status_filter: Optional[str] = Query(None, description="Filter by status (in_progress, completed, abandoned)"),
    owner: Optional[str] = Query(None, description="Filter by owner (me, partner, mutual)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all goals for a partnership.

    Query Parameters:
    - status: Filter by goal status
    - owner: Filter by owner (me, partner, mutual)
    """
    try:
        goals = await get_partnership_goals(
            db,
            partnership_id,
            current_user.id,
            status_filter,
            owner
        )
        return GoalListResponse(
            goals=goals,
            total=len(goals)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get goal details by ID.

    Authorization: Only partnership members can access.
    """
    try:
        goal = await get_goal_by_id(db, goal_id, current_user.id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        return goal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal_endpoint(
    goal_id: UUID,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a goal.

    Authorization:
    - Individual goals: Only owner can update
    - Mutual goals: Either partner can update
    """
    try:
        goal = await update_goal(
            db,
            goal_id,
            current_user.id,
            goal_data.title,
            goal_data.description,
            goal_data.category,
            goal_data.target_date,
            goal_data.status,
            [s.model_dump() for s in goal_data.subtasks] if goal_data.subtasks else None
        )
        return goal
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


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal_endpoint(
    goal_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a goal.

    Authorization:
    - Individual goals: Only owner can delete
    - Mutual goals: Either partner can delete
    """
    try:
        await delete_goal(db, goal_id, current_user.id)
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


@router.post("/goals/{goal_id}/complete", response_model=GoalResponse)
async def complete_goal_endpoint(
    goal_id: UUID,
    request: CompleteGoalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a goal as completed.

    Authorization:
    - Individual goals: Only owner can complete
    - Mutual goals: Either partner can complete (simplified for MVP)
    """
    try:
        goal = await complete_goal(db, goal_id, current_user.id)
        return goal
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "already completed" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
