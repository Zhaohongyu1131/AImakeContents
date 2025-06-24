"""Create Volcano API Config Tables

Revision ID: create_volcano_api_config
Revises: add_volcano_api_support
Create Date: 2024-06-23 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_volcano_api_config'
down_revision = 'add_volcano_api_support'
branch_labels = None
depends_on = None


def upgrade():
    """Create Volcano API configuration tables"""
    
    # Create volcano_api_config table
    op.create_table(
        'volcano_api_config',
        sa.Column('config_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('config_name', sa.String(100), nullable=False),
        sa.Column('config_type', sa.String(50), nullable=False),
        sa.Column('config_category', sa.String(50), nullable=False),
        sa.Column('config_key', sa.String(100), nullable=False),
        sa.Column('config_label', sa.String(100), nullable=False),
        sa.Column('config_description', sa.Text(), nullable=True),
        sa.Column('config_data_type', sa.String(20), nullable=False),
        sa.Column('config_default_value', sa.Text(), nullable=True),
        sa.Column('config_options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('config_validation_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('config_display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('config_is_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('config_is_visible', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('config_group_name', sa.String(50), nullable=True),
        sa.Column('config_created_time', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('config_updated_time', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('config_id')
    )
    
    # Create user_volcano_preferences table
    op.create_table(
        'user_volcano_preferences',
        sa.Column('pref_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pref_type', sa.String(50), nullable=False),
        sa.Column('pref_config_key', sa.String(100), nullable=False),
        sa.Column('pref_value', sa.Text(), nullable=False),
        sa.Column('pref_created_time', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('pref_updated_time', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user_auth_basic.user_id']),
        sa.PrimaryKeyConstraint('pref_id'),
        sa.UniqueConstraint('user_id', 'pref_type', 'pref_config_key', name='uq_user_pref_config')
    )
    
    # Create indexes
    op.create_index('idx_volcano_api_config_type', 'volcano_api_config', ['config_type'])
    op.create_index('idx_volcano_api_config_category', 'volcano_api_config', ['config_category'])
    op.create_index('idx_volcano_api_config_group', 'volcano_api_config', ['config_group_name'])
    op.create_index('idx_user_volcano_preferences_user', 'user_volcano_preferences', ['user_id'])
    op.create_index('idx_user_volcano_preferences_type', 'user_volcano_preferences', ['pref_type'])


def downgrade():
    """Drop Volcano API configuration tables"""
    
    # Drop indexes
    op.drop_index('idx_user_volcano_preferences_type')
    op.drop_index('idx_user_volcano_preferences_user')
    op.drop_index('idx_volcano_api_config_group')
    op.drop_index('idx_volcano_api_config_category')
    op.drop_index('idx_volcano_api_config_type')
    
    # Drop tables
    op.drop_table('user_volcano_preferences')
    op.drop_table('volcano_api_config')