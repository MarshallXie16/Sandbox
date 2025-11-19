"""Initial schema for Exit Ready Automation

Revision ID: 001
Revises:
Create Date: 2025-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create exit_ready_cases table
    op.create_table(
        'exit_ready_cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_code', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('owner_name', sa.String(length=255), nullable=False),
        sa.Column('owner_email', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('intake_form_url', sa.String(length=500), nullable=True),
        sa.Column('intake_sent_at', sa.DateTime(), nullable=True),
        sa.Column('intake_received_at', sa.DateTime(), nullable=True),
        sa.Column('intake_payload', JSON, nullable=True),
        sa.Column('normalized_financials', JSON, nullable=True),
        sa.Column('normalized_financials_last_run_at', sa.DateTime(), nullable=True),
        sa.Column('valuation_payload', JSON, nullable=True),
        sa.Column('valuation_last_run_at', sa.DateTime(), nullable=True),
        sa.Column('drafts', JSON, nullable=True),
        sa.Column('drafts_generated_at', sa.DateTime(), nullable=True),
        sa.Column('report_url', sa.String(length=500), nullable=True),
        sa.Column('teaser_url', sa.String(length=500), nullable=True),
        sa.Column('cim_url', sa.String(length=500), nullable=True),
        sa.Column('report_ready_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('delivery_channel', sa.String(length=50), nullable=True),
        sa.Column('next_step', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exit_ready_cases_case_code', 'exit_ready_cases', ['case_code'], unique=True)
    op.create_index('ix_exit_ready_cases_status', 'exit_ready_cases', ['status'])
    op.create_index('ix_exit_ready_cases_contact_id', 'exit_ready_cases', ['contact_id'])
    op.create_index('ix_exit_ready_cases_company_id', 'exit_ready_cases', ['company_id'])
    op.create_index('ix_exit_ready_cases_owner_email', 'exit_ready_cases', ['owner_email'])
    op.create_index('ix_exit_ready_cases_status_created', 'exit_ready_cases', ['status', 'created_at'])

    # Create exit_ready_docs table
    op.create_table(
        'exit_ready_docs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('doc_type', sa.String(length=100), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('required', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('received_at', sa.DateTime(), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['exit_ready_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exit_ready_docs_case_id', 'exit_ready_docs', ['case_id'])
    op.create_index('ix_exit_ready_docs_case_status', 'exit_ready_docs', ['case_id', 'status'])

    # Create exit_ready_events table
    op.create_table(
        'exit_ready_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', JSON, nullable=True),
        sa.Column('actor', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['exit_ready_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exit_ready_events_case_id', 'exit_ready_events', ['case_id'])
    op.create_index('ix_exit_ready_events_event_type', 'exit_ready_events', ['event_type'])
    op.create_index('ix_exit_ready_events_created_at', 'exit_ready_events', ['created_at'])
    op.create_index('ix_exit_ready_events_case_created', 'exit_ready_events', ['case_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_exit_ready_events_case_created', table_name='exit_ready_events')
    op.drop_index('ix_exit_ready_events_created_at', table_name='exit_ready_events')
    op.drop_index('ix_exit_ready_events_event_type', table_name='exit_ready_events')
    op.drop_index('ix_exit_ready_events_case_id', table_name='exit_ready_events')
    op.drop_table('exit_ready_events')

    op.drop_index('ix_exit_ready_docs_case_status', table_name='exit_ready_docs')
    op.drop_index('ix_exit_ready_docs_case_id', table_name='exit_ready_docs')
    op.drop_table('exit_ready_docs')

    op.drop_index('ix_exit_ready_cases_status_created', table_name='exit_ready_cases')
    op.drop_index('ix_exit_ready_cases_owner_email', table_name='exit_ready_cases')
    op.drop_index('ix_exit_ready_cases_company_id', table_name='exit_ready_cases')
    op.drop_index('ix_exit_ready_cases_contact_id', table_name='exit_ready_cases')
    op.drop_index('ix_exit_ready_cases_status', table_name='exit_ready_cases')
    op.drop_index('ix_exit_ready_cases_case_code', table_name='exit_ready_cases')
    op.drop_table('exit_ready_cases')
