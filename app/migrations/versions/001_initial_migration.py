"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

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
    # Enable uuid-ossp extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create our_channels table
    op.create_table('our_channels',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('tg_chat_id_or_username', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), server_default='active', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sources table
    op.create_table('sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('our_channel_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('username', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_image_url', sa.Text(), nullable=True),
        sa.Column('source_type', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('last_guid', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['our_channel_id'], ['our_channels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_our_channel_id'), 'sources', ['our_channel_id'], unique=False)
    
    # Create posts table
    op.create_table('posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('guid', sa.Text(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('summary_text', sa.Text(), nullable=True),
        sa.Column('media_url', sa.Text(), nullable=True),
        sa.Column('extra_text', sa.Text(), nullable=True),
        sa.Column('hashtags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Text(), server_default='new', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id', 'guid', name='uq_source_guid')
    )
    op.create_index(op.f('ix_posts_guid'), 'posts', ['guid'], unique=False)
    op.create_index(op.f('ix_posts_source_id'), 'posts', ['source_id'], unique=False)
    op.create_index(op.f('ix_posts_status'), 'posts', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_posts_status'), table_name='posts')
    op.drop_index(op.f('ix_posts_source_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_guid'), table_name='posts')
    op.drop_table('posts')
    op.drop_index(op.f('ix_sources_our_channel_id'), table_name='sources')
    op.drop_table('sources')
    op.drop_table('our_channels')
