"""Initial schema for Facilitator Automation

Revision ID: 001
Revises:
Create Date: 2025-01-19 12:00:00.000000

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
    # Create enum types
    op.execute("""
        CREATE TYPE engagementstatus AS ENUM (
            'draft', 'active', 'shortlisting', 'outreach_in_progress',
            'offers_in_play', 'under_agreement', 'closed_success',
            'closed_no_deal', 'terminated'
        )
    """)

    op.execute("""
        CREATE TYPE buyerintrostatus AS ENUM (
            'invited', 'nda_pending', 'nda_signed', 'teaser_sent',
            'info_access', 'offer_made', 'inactive', 'not_interested', 'dropped'
        )
    """)

    op.execute("""
        CREATE TYPE offerstatus AS ENUM (
            'received', 'under_review', 'accepted', 'declined',
            'withdrawn', 'superseded'
        )
    """)

    op.execute("""
        CREATE TYPE introductionchannel AS ENUM (
            'email', 'phone', 'event', 'referral', 'direct', 'other'
        )
    """)

    op.execute("""
        CREATE TYPE eventtype AS ENUM (
            'engagement_created', 'engagement_activated', 'engagement_status_changed',
            'buyer_introduced', 'buyer_status_changed', 'nda_sent', 'nda_signed',
            'teaser_sent', 'info_access_granted', 'offer_received', 'offer_status_changed',
            'offer_fee_invoiced', 'offer_fee_paid', 'closing_recorded',
            'success_fee_invoiced', 'success_fee_paid', 'engagement_terminated'
        )
    """)

    # Create facilitator_engagements table
    op.create_table(
        'facilitator_engagements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('engagement_code', sa.String(length=50), nullable=False),
        sa.Column('seller_contact_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('listing_id', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM(name='engagementstatus', create_type=False), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('tail_end_date', sa.DateTime(), nullable=True),
        sa.Column('offer_fee_fixed', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('success_fee_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('terms', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facilitator_engagements_id'), 'facilitator_engagements', ['id'], unique=False)
    op.create_index(op.f('ix_facilitator_engagements_engagement_code'), 'facilitator_engagements', ['engagement_code'], unique=True)
    op.create_index(op.f('ix_facilitator_engagements_seller_contact_id'), 'facilitator_engagements', ['seller_contact_id'], unique=False)
    op.create_index(op.f('ix_facilitator_engagements_company_id'), 'facilitator_engagements', ['company_id'], unique=False)
    op.create_index(op.f('ix_facilitator_engagements_listing_id'), 'facilitator_engagements', ['listing_id'], unique=False)
    op.create_index(op.f('ix_facilitator_engagements_status'), 'facilitator_engagements', ['status'], unique=False)

    # Create facilitator_buyer_intros table
    op.create_table(
        'facilitator_buyer_intros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('buyer_contact_id', sa.Integer(), nullable=False),
        sa.Column('introduced_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('introduction_channel', postgresql.ENUM(name='introductionchannel', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM(name='buyerintrostatus', create_type=False), nullable=False),
        sa.Column('nda_sent_at', sa.DateTime(), nullable=True),
        sa.Column('nda_signed_at', sa.DateTime(), nullable=True),
        sa.Column('teaser_sent_at', sa.DateTime(), nullable=True),
        sa.Column('info_access_granted_at', sa.DateTime(), nullable=True),
        sa.Column('last_contact_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['facilitator_engagements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facilitator_buyer_intros_id'), 'facilitator_buyer_intros', ['id'], unique=False)
    op.create_index(op.f('ix_facilitator_buyer_intros_engagement_id'), 'facilitator_buyer_intros', ['engagement_id'], unique=False)
    op.create_index(op.f('ix_facilitator_buyer_intros_buyer_contact_id'), 'facilitator_buyer_intros', ['buyer_contact_id'], unique=False)
    op.create_index(op.f('ix_facilitator_buyer_intros_status'), 'facilitator_buyer_intros', ['status'], unique=False)

    # Create facilitator_offers table
    op.create_table(
        'facilitator_offers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('buyer_intro_id', sa.Integer(), nullable=False),
        sa.Column('offer_date', sa.DateTime(), nullable=False),
        sa.Column('headline_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', postgresql.ENUM(name='offerstatus', create_type=False), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('offer_fee_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('offer_fee_invoiced', sa.Boolean(), nullable=False),
        sa.Column('offer_fee_paid', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['facilitator_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_intro_id'], ['facilitator_buyer_intros.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facilitator_offers_id'), 'facilitator_offers', ['id'], unique=False)
    op.create_index(op.f('ix_facilitator_offers_engagement_id'), 'facilitator_offers', ['engagement_id'], unique=False)
    op.create_index(op.f('ix_facilitator_offers_buyer_intro_id'), 'facilitator_offers', ['buyer_intro_id'], unique=False)
    op.create_index(op.f('ix_facilitator_offers_status'), 'facilitator_offers', ['status'], unique=False)

    # Create facilitator_closings table
    op.create_table(
        'facilitator_closings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=False),
        sa.Column('buyer_intro_id', sa.Integer(), nullable=False),
        sa.Column('closing_date', sa.DateTime(), nullable=False),
        sa.Column('final_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('final_structure', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('success_fee_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('success_fee_gross_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('offer_fee_credit_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('success_fee_net_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('invoiced', sa.Boolean(), nullable=False),
        sa.Column('paid', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['facilitator_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_intro_id'], ['facilitator_buyer_intros.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facilitator_closings_id'), 'facilitator_closings', ['id'], unique=False)
    op.create_index(op.f('ix_facilitator_closings_engagement_id'), 'facilitator_closings', ['engagement_id'], unique=False)
    op.create_index(op.f('ix_facilitator_closings_buyer_intro_id'), 'facilitator_closings', ['buyer_intro_id'], unique=False)

    # Create facilitator_events table
    op.create_table(
        'facilitator_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('engagement_id', sa.Integer(), nullable=True),
        sa.Column('buyer_intro_id', sa.Integer(), nullable=True),
        sa.Column('offer_id', sa.Integer(), nullable=True),
        sa.Column('closing_id', sa.Integer(), nullable=True),
        sa.Column('event_type', postgresql.ENUM(name='eventtype', create_type=False), nullable=False),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('actor', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['facilitator_engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_intro_id'], ['facilitator_buyer_intros.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['offer_id'], ['facilitator_offers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['closing_id'], ['facilitator_closings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facilitator_events_id'), 'facilitator_events', ['id'], unique=False)
    op.create_index(op.f('ix_facilitator_events_engagement_id'), 'facilitator_events', ['engagement_id'], unique=False)
    op.create_index(op.f('ix_facilitator_events_buyer_intro_id'), 'facilitator_events', ['buyer_intro_id'], unique=False)
    op.create_index(op.f('ix_facilitator_events_offer_id'), 'facilitator_events', ['offer_id'], unique=False)
    op.create_index(op.f('ix_facilitator_events_closing_id'), 'facilitator_events', ['closing_id'], unique=False)
    op.create_index(op.f('ix_facilitator_events_event_type'), 'facilitator_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_facilitator_events_created_at'), 'facilitator_events', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_table('facilitator_events')
    op.drop_table('facilitator_closings')
    op.drop_table('facilitator_offers')
    op.drop_table('facilitator_buyer_intros')
    op.drop_table('facilitator_engagements')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS eventtype')
    op.execute('DROP TYPE IF EXISTS introductionchannel')
    op.execute('DROP TYPE IF EXISTS offerstatus')
    op.execute('DROP TYPE IF EXISTS buyerintrostatus')
    op.execute('DROP TYPE IF EXISTS engagementstatus')
