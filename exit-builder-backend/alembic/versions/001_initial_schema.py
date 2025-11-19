"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-11-19

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
    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('project_type', sa.Enum('QUICK', 'STANDARD', name='projecttype'), nullable=False),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create financial_inputs table
    op.create_table('financial_inputs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('net_profit', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('ebitda', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_assets', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_liabilities', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create valuation_results table
    op.create_table('valuation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('confidence', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create valuation_summary table
    op.create_table('valuation_summary',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value_low', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('value_mid', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('value_high', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('primary_method', sa.String(), nullable=True),
        sa.Column('adjustment_factor', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id')
    )

    # Create report_templates table
    op.create_table('report_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Create reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('format', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create questionnaire_templates table
    op.create_table('questionnaire_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create questions table
    op.create_table('questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('questionnaire_template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('input_type', sa.Enum('SINGLE_CHOICE', 'MULTI_CHOICE', 'NUMBER', 'TEXT', 'YES_NO', name='inputtype'), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('help_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['questionnaire_template_id'], ['questionnaire_templates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Create question_options table
    op.create_table('question_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create answers table
    op.create_table('answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value_text', sa.Text(), nullable=True),
        sa.Column('value_numeric', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('selected_option_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create score_dimensions table
    op.create_table('score_dimensions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Create score_rules table
    op.create_table('score_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dimension_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_type', sa.Enum('OPTION_VALUE', 'NUMERIC_RANGE', 'YES_NO', 'TEXT_CONTAINS', name='matchtype'), nullable=False),
        sa.Column('match_value', sa.String(), nullable=False),
        sa.Column('score_delta', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['dimension_id'], ['score_dimensions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create score_results table
    op.create_table('score_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False),
        sa.Column('rating', sa.String(), nullable=False),
        sa.Column('valuation_adjustment_factor', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create score_dimension_results table
    op.create_table('score_dimension_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score_result_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dimension_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['dimension_id'], ['score_dimensions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['score_result_id'], ['score_results.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('score_dimension_results')
    op.drop_table('score_results')
    op.drop_table('score_rules')
    op.drop_table('score_dimensions')
    op.drop_table('answers')
    op.drop_table('question_options')
    op.drop_table('questions')
    op.drop_table('questionnaire_templates')
    op.drop_table('reports')
    op.drop_table('report_templates')
    op.drop_table('valuation_summary')
    op.drop_table('valuation_results')
    op.drop_table('financial_inputs')
    op.drop_table('projects')
    op.execute('DROP TYPE IF EXISTS matchtype')
    op.execute('DROP TYPE IF EXISTS inputtype')
    op.execute('DROP TYPE IF EXISTS projecttype')
