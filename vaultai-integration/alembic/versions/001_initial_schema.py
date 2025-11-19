"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create prompt_templates table
    op.create_table(
        'prompt_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=False),
        sa.Column('task_type', sa.String(length=100), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('user_prompt_template', sa.Text(), nullable=False),
        sa.Column('default_temperature', sa.Float(), nullable=True),
        sa.Column('default_max_tokens', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('placeholders', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_prompt_templates_name', 'prompt_templates', ['name'])
    op.create_index('ix_prompt_templates_domain', 'prompt_templates', ['domain'])
    op.create_index('ix_prompt_templates_task_type', 'prompt_templates', ['task_type'])
    op.create_index('ix_prompt_templates_is_active', 'prompt_templates', ['is_active'])

    # Create llm_logs table
    op.create_table(
        'llm_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_id', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=True),
        sa.Column('task_type', sa.String(length=100), nullable=True),
        sa.Column('service_identifier', sa.String(length=255), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('messages', postgresql.JSON(), nullable=False),
        sa.Column('request_params', postgresql.JSON(), nullable=True),
        sa.Column('response_content', sa.Text(), nullable=True),
        sa.Column('finish_reason', sa.String(length=50), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('pii_detected', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id'),
    )
    op.create_index('ix_llm_logs_request_id', 'llm_logs', ['request_id'])
    op.create_index('ix_llm_logs_domain', 'llm_logs', ['domain'])
    op.create_index('ix_llm_logs_task_type', 'llm_logs', ['task_type'])
    op.create_index('ix_llm_logs_service_identifier', 'llm_logs', ['service_identifier'])
    op.create_index('ix_llm_logs_provider', 'llm_logs', ['provider'])
    op.create_index('ix_llm_logs_status', 'llm_logs', ['status'])
    op.create_index('ix_llm_logs_total_tokens', 'llm_logs', ['total_tokens'])
    op.create_index('ix_llm_logs_created_at', 'llm_logs', ['created_at'])
    op.create_index('idx_llm_logs_domain_task_created', 'llm_logs', ['domain', 'task_type', 'created_at'])
    op.create_index('idx_llm_logs_provider_status_created', 'llm_logs', ['provider', 'status', 'created_at'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('chunk_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
    )
    op.create_index('ix_documents_external_id', 'documents', ['external_id'])
    op.create_index('ix_documents_content_hash', 'documents', ['content_hash'])
    op.create_index('ix_documents_document_type', 'documents', ['document_type'])
    op.create_index('ix_documents_domain', 'documents', ['domain'])
    op.create_index('ix_documents_is_processed', 'documents', ['is_processed'])
    op.create_index('ix_documents_created_at', 'documents', ['created_at'])
    op.create_index('idx_documents_type_domain_created', 'documents', ['document_type', 'domain', 'created_at'])

    # Create embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('embedding_provider', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_embeddings_document_id', 'embeddings', ['document_id'])
    op.create_index('ix_embeddings_created_at', 'embeddings', ['created_at'])
    op.create_index('idx_embeddings_document_chunk', 'embeddings', ['document_id', 'chunk_index'])

    # Create vector similarity search index (IVFFlat)
    # Note: This requires pgvector extension and sufficient data for training
    # For production, consider HNSW index instead
    # op.execute('CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade() -> None:
    op.drop_table('embeddings')
    op.drop_table('documents')
    op.drop_table('llm_logs')
    op.drop_table('prompt_templates')
    op.execute('DROP EXTENSION IF EXISTS vector')
