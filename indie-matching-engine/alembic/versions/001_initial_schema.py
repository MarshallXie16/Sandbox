"""Initial schema for matching engine

Revision ID: 001
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create matching_runs table
    op.create_table(
        'matching_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_type', sa.String(length=50), nullable=False, comment='Type of run: full, buyer, listing, incremental'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Status: pending, running, completed, failed'),
        sa.Column('scope', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Scope parameters'),
        sa.Column('matches_computed', sa.Integer(), nullable=True, comment='Number of matches computed'),
        sa.Column('buyers_processed', sa.Integer(), nullable=True, comment='Number of buyers processed'),
        sa.Column('listings_processed', sa.Integer(), nullable=True, comment='Number of listings processed'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stats', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Run statistics'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create buyer_listing_matches table
    op.create_table(
        'buyer_listing_matches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('buyer_id', sa.Integer(), nullable=False, comment='Contact ID from indie-crm-core.contacts'),
        sa.Column('listing_id', sa.Integer(), nullable=False, comment='Deal ID from indie-crm-core.deals'),
        sa.Column('score', sa.Float(), nullable=False, comment='Overall match score (0-100)'),
        sa.Column('components', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='Score components'),
        sa.Column('reason_codes', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='List of reason codes'),
        sa.Column('matching_run_id', sa.Integer(), nullable=True, comment='ID of the matching run'),
        sa.Column('buyer_email', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Cached buyer email'),
        sa.Column('listing_name', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Cached listing name'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('buyer_id', 'listing_id', name='uix_buyer_listing')
    )

    # Create indexes
    op.create_index('ix_buyer_listing_matches_buyer_id', 'buyer_listing_matches', ['buyer_id'])
    op.create_index('ix_buyer_listing_matches_listing_id', 'buyer_listing_matches', ['listing_id'])
    op.create_index('ix_buyer_listing_matches_score', 'buyer_listing_matches', ['score'])
    op.create_index('ix_buyer_listing_matches_updated_at', 'buyer_listing_matches', ['updated_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_buyer_listing_matches_updated_at', table_name='buyer_listing_matches')
    op.drop_index('ix_buyer_listing_matches_score', table_name='buyer_listing_matches')
    op.drop_index('ix_buyer_listing_matches_listing_id', table_name='buyer_listing_matches')
    op.drop_index('ix_buyer_listing_matches_buyer_id', table_name='buyer_listing_matches')

    # Drop tables
    op.drop_table('buyer_listing_matches')
    op.drop_table('matching_runs')
