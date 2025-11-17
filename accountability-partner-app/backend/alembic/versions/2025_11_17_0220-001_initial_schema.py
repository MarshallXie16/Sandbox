"""Initial schema with all models

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-17 02:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('full_name', sa.String(100)),
        sa.Column('profile_picture_url', sa.Text()),
        sa.Column('bio', sa.Text()),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verification_tier', sa.String(20), default='basic'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_banned', sa.Boolean(), default=False),
        sa.Column('total_points', sa.Integer(), default=0),
        sa.Column('streak_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('last_login_at', sa.Date())
    )

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('strengths', postgresql.ARRAY(sa.Text()), default=[]),
        sa.Column('struggles', postgresql.ARRAY(sa.Text()), default=[]),
        sa.Column('communication_style', sa.String(50)),
        sa.Column('commitment_level', sa.String(50)),
        sa.Column('preferred_check_in_frequency', sa.String(50)),
        sa.Column('available_days_of_week', postgresql.ARRAY(sa.Integer()), default=[]),
        sa.Column('preferred_check_in_time', sa.String(20)),
        sa.Column('current_goals', postgresql.JSONB(), default=[]),
        sa.Column('active_partnerships_count', sa.Integer(), default=0),
        sa.Column('max_partnerships', sa.Integer(), default=3),
        sa.Column('is_seeking_partner', sa.Boolean(), default=True),
        sa.Column('ghosting_score', sa.Float(), default=0.0),
        sa.Column('reciprocity_score', sa.Float(), default=0.5),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'))
    )
    op.create_index('idx_user_profiles_user_id', 'user_profiles', ['user_id'])
    op.create_index('idx_user_profiles_seeking', 'user_profiles', ['is_seeking_partner'])

    # Create partnerships table
    op.create_table(
        'partnerships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user1_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user2_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), default='active', index=True),
        sa.Column('season_number', sa.Integer(), default=1),
        sa.Column('current_season_start_date', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('current_season_end_date', sa.Date()),
        sa.Column('mutual_goals', postgresql.JSONB(), default=[]),
        sa.Column('check_in_frequency', sa.String(50), default='weekly'),
        sa.Column('check_in_days', postgresql.ARRAY(sa.Integer()), default=[1, 3, 5]),
        sa.Column('communication_methods', postgresql.ARRAY(sa.Text()), default=['text']),
        sa.Column('balance_score', sa.Float(), default=0.5),
        sa.Column('engagement_score', sa.Float(), default=0.0),
        sa.Column('last_interaction_at', sa.Date()),
        sa.Column('user1_last_active_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('user2_last_active_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('nudge_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.CheckConstraint('user1_id != user2_id', name='check_different_users')
    )
    op.create_index('idx_partnerships_user1', 'partnerships', ['user1_id'])
    op.create_index('idx_partnerships_user2', 'partnerships', ['user2_id'])

    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partnerships.id', ondelete='CASCADE'), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(50)),
        sa.Column('is_mutual', sa.Boolean(), default=False),
        sa.Column('status', sa.String(50), default='in_progress', index=True),
        sa.Column('target_date', sa.Date()),
        sa.Column('completed_at', sa.Date()),
        sa.Column('subtasks', postgresql.JSONB(), default=[]),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'))
    )
    op.create_index('idx_goals_partnership', 'goals', ['partnership_id'])
    op.create_index('idx_goals_owner', 'goals', ['owner_id'])

    # Create check_ins table
    op.create_table(
        'check_ins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partnerships.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_type', sa.String(50), default='text'),
        sa.Column('text_content', sa.Text()),
        sa.Column('media_url', sa.Text()),
        sa.Column('what_i_did', sa.Text()),
        sa.Column('what_i_struggled_with', sa.Text()),
        sa.Column('what_i_need', sa.Text()),
        sa.Column('sentiment_score', sa.Float()),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('response_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('check_ins.id')),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), index=True)
    )
    op.create_index('idx_check_ins_partnership', 'check_ins', ['partnership_id'])
    op.create_index('idx_check_ins_author', 'check_ins', ['author_id'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partnerships.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_to_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('task_type', sa.String(50)),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('completed_at', sa.Date()),
        sa.Column('completion_proof_url', sa.Text()),
        sa.Column('due_date', sa.Date()),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'))
    )
    op.create_index('idx_tasks_assigned_to', 'tasks', ['assigned_to_user_id'])
    op.create_index('idx_tasks_partnership', 'tasks', ['partnership_id'])

    # Create match_queue table
    op.create_table(
        'match_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), default='pending', index=True),
        sa.Column('priority_score', sa.Float(), default=0.5, index=True),
        sa.Column('proposed_matches', postgresql.JSONB(), default=[]),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('expires_at', sa.Date())
    )

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reported_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('partnership_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partnerships.id', ondelete='SET NULL')),
        sa.Column('reason', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('evidence_urls', postgresql.ARRAY(sa.Text())),
        sa.Column('status', sa.String(50), default='pending', index=True),
        sa.Column('admin_notes', sa.Text()),
        sa.Column('action_taken', sa.String(100)),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('resolved_at', sa.Date())
    )
    op.create_index('idx_reports_reported_user', 'reports', ['reported_user_id'])


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('match_queue')
    op.drop_table('tasks')
    op.drop_table('check_ins')
    op.drop_table('goals')
    op.drop_table('partnerships')
    op.drop_table('user_profiles')
    op.drop_table('users')
