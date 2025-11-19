"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table('clients',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('contact_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # Create projects table
    op.create_table('projects',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('internal_code', sa.String(), nullable=True),
    sa.Column('business_name', sa.String(), nullable=False),
    sa.Column('industry_code', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('project_type', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create financial_inputs table
    op.create_table('financial_inputs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('revenue', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('sde', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('ebitda', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create industry_multiples table
    op.create_table('industry_multiples',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('industry_code', sa.String(), nullable=False),
    sa.Column('metric_type', sa.String(), nullable=False),
    sa.Column('size_min_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('size_max_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('multiple_low', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('multiple_mid', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('multiple_high', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('source', sa.String(), nullable=True),
    sa.Column('effective_date', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # Create valuation_methods table
    op.create_table('valuation_methods',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )

    # Create report_templates table
    op.create_table('report_templates',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )

    # Create valuation_inputs table
    op.create_table('valuation_inputs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('valuation_method_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('base_metric', sa.String(), nullable=False),
    sa.Column('base_metric_value', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('base_multiple', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('adjusted_multiple', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['valuation_method_id'], ['valuation_methods.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create valuation_results table
    op.create_table('valuation_results',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('valuation_method_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('scenario', sa.String(), nullable=False),
    sa.Column('value_low', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('value_mid', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('value_high', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['valuation_method_id'], ['valuation_methods.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create valuation_summary table
    op.create_table('valuation_summary',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('recommended_value_low', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('recommended_value_mid', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('recommended_value_high', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id')
    )

    # Create reports table
    op.create_table('reports',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('report_template_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('language', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('content_markdown', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['report_template_id'], ['report_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('valuation_summary')
    op.drop_table('valuation_results')
    op.drop_table('valuation_inputs')
    op.drop_table('report_templates')
    op.drop_table('valuation_methods')
    op.drop_table('industry_multiples')
    op.drop_table('financial_inputs')
    op.drop_table('projects')
    op.drop_table('clients')
