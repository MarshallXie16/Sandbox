"""Goal service for managing goals within partnerships."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.models.goal import Goal
from app.models.partnership import Partnership


async def create_goal(
    db: AsyncSession,
    partnership_id: UUID,
    current_user_id: UUID,
    title: str,
    description: Optional[str],
    category: Optional[str],
    is_mutual: bool,
    target_date: Optional[str],
    subtasks: List[dict]
) -> Goal:
    """
    Create a new goal for a partnership.

    Args:
        db: Database session
        partnership_id: Partnership ID
        current_user_id: Current user's ID
        title: Goal title
        description: Optional description
        category: Optional category
        is_mutual: Whether this is a mutual goal
        target_date: Optional target date
        subtasks: List of subtasks

    Returns:
        Created Goal object

    Raises:
        ValueError: If partnership not found or user not a member
    """
    # Verify partnership exists and user is a member
    result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == partnership_id,
                or_(
                    Partnership.user1_id == current_user_id,
                    Partnership.user2_id == current_user_id
                )
            )
        )
    )
    partnership = result.scalar_one_or_none()

    if not partnership:
        raise ValueError("Partnership not found or you are not a member")

    # Create goal
    goal = Goal(
        partnership_id=partnership_id,
        owner_id=None if is_mutual else current_user_id,
        title=title,
        description=description,
        category=category,
        is_mutual=is_mutual,
        status='in_progress',
        target_date=target_date,
        subtasks=subtasks or []
    )

    db.add(goal)
    await db.commit()
    await db.refresh(goal)

    return goal


async def get_partnership_goals(
    db: AsyncSession,
    partnership_id: UUID,
    current_user_id: UUID,
    status_filter: Optional[str] = None,
    owner_filter: Optional[str] = None
) -> List[Goal]:
    """
    Get all goals for a partnership.

    Args:
        db: Database session
        partnership_id: Partnership ID
        current_user_id: Current user's ID
        status_filter: Optional status filter
        owner_filter: Optional owner filter ('me', 'partner', 'mutual')

    Returns:
        List of Goal objects
    """
    # Verify user is a member
    result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == partnership_id,
                or_(
                    Partnership.user1_id == current_user_id,
                    Partnership.user2_id == current_user_id
                )
            )
        )
    )
    partnership = result.scalar_one_or_none()

    if not partnership:
        raise ValueError("Partnership not found or you are not a member")

    # Get partner ID
    partner_id = partnership.user2_id if partnership.user1_id == current_user_id else partnership.user1_id

    # Build query
    query = select(Goal).where(Goal.partnership_id == partnership_id)

    if status_filter:
        query = query.where(Goal.status == status_filter)

    if owner_filter == 'me':
        query = query.where(Goal.owner_id == current_user_id)
    elif owner_filter == 'partner':
        query = query.where(Goal.owner_id == partner_id)
    elif owner_filter == 'mutual':
        query = query.where(Goal.is_mutual == True)

    query = query.order_by(Goal.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


async def get_goal_by_id(
    db: AsyncSession,
    goal_id: UUID,
    current_user_id: UUID
) -> Optional[Goal]:
    """
    Get a goal by ID.

    Args:
        db: Database session
        goal_id: Goal ID
        current_user_id: Current user's ID

    Returns:
        Goal object or None

    Raises:
        ValueError: If user is not a member of the partnership
    """
    # Get goal
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id)
    )
    goal = result.scalar_one_or_none()

    if not goal:
        return None

    # Verify user is a member of the partnership
    partnership_result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == goal.partnership_id,
                or_(
                    Partnership.user1_id == current_user_id,
                    Partnership.user2_id == current_user_id
                )
            )
        )
    )
    partnership = partnership_result.scalar_one_or_none()

    if not partnership:
        raise ValueError("You are not a member of this partnership")

    return goal


async def update_goal(
    db: AsyncSession,
    goal_id: UUID,
    current_user_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    target_date: Optional[str] = None,
    status: Optional[str] = None,
    subtasks: Optional[List[dict]] = None
) -> Goal:
    """
    Update a goal.

    Args:
        db: Database session
        goal_id: Goal ID
        current_user_id: Current user's ID
        title: Optional new title
        description: Optional new description
        category: Optional new category
        target_date: Optional new target date
        status: Optional new status
        subtasks: Optional new subtasks

    Returns:
        Updated Goal object

    Raises:
        ValueError: If goal not found or user not authorized
    """
    goal = await get_goal_by_id(db, goal_id, current_user_id)

    if not goal:
        raise ValueError("Goal not found")

    # Check if user can edit this goal
    # Individual goals can only be edited by owner
    # Mutual goals can be edited by either partner
    if not goal.is_mutual and goal.owner_id != current_user_id:
        raise ValueError("You can only edit your own goals")

    # Update fields
    if title is not None:
        goal.title = title
    if description is not None:
        goal.description = description
    if category is not None:
        goal.category = category
    if target_date is not None:
        goal.target_date = target_date
    if status is not None:
        goal.status = status
        if status == 'completed' and not goal.completed_at:
            goal.completed_at = datetime.utcnow()
    if subtasks is not None:
        goal.subtasks = subtasks

    await db.commit()
    await db.refresh(goal)

    return goal


async def delete_goal(
    db: AsyncSession,
    goal_id: UUID,
    current_user_id: UUID
) -> None:
    """
    Delete a goal.

    Args:
        db: Database session
        goal_id: Goal ID
        current_user_id: Current user's ID

    Raises:
        ValueError: If goal not found or user not authorized
    """
    goal = await get_goal_by_id(db, goal_id, current_user_id)

    if not goal:
        raise ValueError("Goal not found")

    # Check if user can delete this goal
    # Individual goals can only be deleted by owner
    # Mutual goals can be deleted by either partner
    if not goal.is_mutual and goal.owner_id != current_user_id:
        raise ValueError("You can only delete your own goals")

    await db.delete(goal)
    await db.commit()


async def complete_goal(
    db: AsyncSession,
    goal_id: UUID,
    current_user_id: UUID
) -> Goal:
    """
    Mark a goal as completed.

    For individual goals: owner can complete
    For mutual goals: either partner can complete (simplified for MVP)

    Args:
        db: Database session
        goal_id: Goal ID
        current_user_id: Current user's ID

    Returns:
        Updated Goal object

    Raises:
        ValueError: If goal not found, user not authorized, or already completed
    """
    goal = await get_goal_by_id(db, goal_id, current_user_id)

    if not goal:
        raise ValueError("Goal not found")

    if goal.status == 'completed':
        raise ValueError("Goal is already completed")

    # Check authorization
    # Individual goals can only be completed by owner
    # Mutual goals can be completed by either partner (simplified for MVP)
    if not goal.is_mutual and goal.owner_id != current_user_id:
        raise ValueError("You can only complete your own goals")

    # Mark as completed
    goal.status = 'completed'
    goal.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(goal)

    return goal
