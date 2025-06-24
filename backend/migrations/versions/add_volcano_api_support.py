"""Add Volcano API Support

Revision ID: add_volcano_api_support
Revises: 81b0cece660d
Create Date: 2024-06-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_volcano_api_support'
down_revision = '81b0cece660d'
branch_labels = None
depends_on = None


def upgrade():
    """Add columns for Volcano API support"""
    
    # Add columns to voice_timbre_basic table
    op.add_column('voice_timbre_basic', sa.Column('timbre_speaker_id', sa.String(100), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_model_type', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('voice_timbre_basic', sa.Column('timbre_source_duration', sa.Numeric(10, 2), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_training_text', sa.Text(), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_demo_audio_url', sa.String(500), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_version', sa.String(10), nullable=False, server_default='V1'))
    op.add_column('voice_timbre_basic', sa.Column('timbre_create_time_volcano', sa.BigInteger(), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_available_training_times', sa.Integer(), nullable=False, server_default='10'))
    op.add_column('voice_timbre_basic', sa.Column('timbre_instance_no', sa.String(100), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_is_activable', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('voice_timbre_basic', sa.Column('timbre_expire_time', sa.BigInteger(), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_order_time', sa.BigInteger(), nullable=True))
    op.add_column('voice_timbre_basic', sa.Column('timbre_alias', sa.String(100), nullable=True))
    
    # Add columns to voice_timbre_clone table
    op.add_column('voice_timbre_clone', sa.Column('clone_audio_format', sa.String(20), nullable=False, server_default='wav'))
    op.add_column('voice_timbre_clone', sa.Column('clone_audio_bytes_base64', sa.Text(), nullable=True))
    op.add_column('voice_timbre_clone', sa.Column('clone_reference_text', sa.Text(), nullable=True))
    op.add_column('voice_timbre_clone', sa.Column('clone_language', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('voice_timbre_clone', sa.Column('clone_model_type', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('voice_timbre_clone', sa.Column('clone_volcano_task_id', sa.String(100), nullable=True))
    op.add_column('voice_timbre_clone', sa.Column('clone_demo_audio_url', sa.String(500), nullable=True))
    op.add_column('voice_timbre_clone', sa.Column('clone_wer_score', sa.Numeric(5, 2), nullable=True))
    op.add_column('voice_timbre_clone', sa.Column('clone_snr_score', sa.Numeric(5, 2), nullable=True))
    op.add_column('voice_timbre_clone', sa.Column('clone_quality_check_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Add columns to voice_audio_basic table
    op.add_column('voice_audio_basic', sa.Column('audio_encoding', sa.String(20), nullable=False, server_default='mp3'))
    op.add_column('voice_audio_basic', sa.Column('audio_sample_rate', sa.Integer(), nullable=False, server_default='24000'))
    op.add_column('voice_audio_basic', sa.Column('audio_explicit_language', sa.String(20), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_context_language', sa.String(20), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_text_type', sa.String(20), nullable=False, server_default='plain'))
    op.add_column('voice_audio_basic', sa.Column('audio_with_timestamp', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('voice_audio_basic', sa.Column('audio_split_sentence', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('voice_audio_basic', sa.Column('audio_cluster', sa.String(50), nullable=False, server_default='volcano_icl'))
    op.add_column('voice_audio_basic', sa.Column('audio_reqid', sa.String(100), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_volcano_sequence', sa.Integer(), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_cache_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('voice_audio_basic', sa.Column('audio_synthesis_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_processing_time_ms', sa.Integer(), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_error_code', sa.Integer(), nullable=True))
    op.add_column('voice_audio_basic', sa.Column('audio_error_message', sa.Text(), nullable=True))
    
    # Add columns to voice_audio_template table
    op.add_column('voice_audio_template', sa.Column('template_basic_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('voice_audio_template', sa.Column('template_advanced_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Create new indexes for better query performance
    op.create_index('idx_voice_timbre_basic_speaker_id', 'voice_timbre_basic', ['timbre_speaker_id'])
    op.create_index('idx_voice_timbre_basic_model_type', 'voice_timbre_basic', ['timbre_model_type'])
    op.create_index('idx_voice_audio_basic_encoding', 'voice_audio_basic', ['audio_encoding'])
    op.create_index('idx_voice_audio_basic_language', 'voice_audio_basic', ['audio_explicit_language'])
    op.create_index('idx_voice_audio_basic_reqid', 'voice_audio_basic', ['audio_reqid'])


def downgrade():
    """Remove Volcano API support columns"""
    
    # Drop indexes
    op.drop_index('idx_voice_audio_basic_reqid')
    op.drop_index('idx_voice_audio_basic_language')
    op.drop_index('idx_voice_audio_basic_encoding')
    op.drop_index('idx_voice_timbre_basic_model_type')
    op.drop_index('idx_voice_timbre_basic_speaker_id')
    
    # Drop columns from voice_audio_template table
    op.drop_column('voice_audio_template', 'template_advanced_settings')
    op.drop_column('voice_audio_template', 'template_basic_settings')
    
    # Drop columns from voice_audio_basic table
    op.drop_column('voice_audio_basic', 'audio_error_message')
    op.drop_column('voice_audio_basic', 'audio_error_code')
    op.drop_column('voice_audio_basic', 'audio_processing_time_ms')
    op.drop_column('voice_audio_basic', 'audio_response_data')
    op.drop_column('voice_audio_basic', 'audio_synthesis_params')
    op.drop_column('voice_audio_basic', 'audio_cache_enabled')
    op.drop_column('voice_audio_basic', 'audio_volcano_sequence')
    op.drop_column('voice_audio_basic', 'audio_reqid')
    op.drop_column('voice_audio_basic', 'audio_cluster')
    op.drop_column('voice_audio_basic', 'audio_split_sentence')
    op.drop_column('voice_audio_basic', 'audio_with_timestamp')
    op.drop_column('voice_audio_basic', 'audio_text_type')
    op.drop_column('voice_audio_basic', 'audio_context_language')
    op.drop_column('voice_audio_basic', 'audio_explicit_language')
    op.drop_column('voice_audio_basic', 'audio_sample_rate')
    op.drop_column('voice_audio_basic', 'audio_encoding')
    
    # Drop columns from voice_timbre_clone table
    op.drop_column('voice_timbre_clone', 'clone_quality_check_result')
    op.drop_column('voice_timbre_clone', 'clone_snr_score')
    op.drop_column('voice_timbre_clone', 'clone_wer_score')
    op.drop_column('voice_timbre_clone', 'clone_demo_audio_url')
    op.drop_column('voice_timbre_clone', 'clone_volcano_task_id')
    op.drop_column('voice_timbre_clone', 'clone_model_type')
    op.drop_column('voice_timbre_clone', 'clone_language')
    op.drop_column('voice_timbre_clone', 'clone_reference_text')
    op.drop_column('voice_timbre_clone', 'clone_audio_bytes_base64')
    op.drop_column('voice_timbre_clone', 'clone_audio_format')
    
    # Drop columns from voice_timbre_basic table
    op.drop_column('voice_timbre_basic', 'timbre_alias')
    op.drop_column('voice_timbre_basic', 'timbre_order_time')
    op.drop_column('voice_timbre_basic', 'timbre_expire_time')
    op.drop_column('voice_timbre_basic', 'timbre_is_activable')
    op.drop_column('voice_timbre_basic', 'timbre_instance_no')
    op.drop_column('voice_timbre_basic', 'timbre_available_training_times')
    op.drop_column('voice_timbre_basic', 'timbre_create_time_volcano')
    op.drop_column('voice_timbre_basic', 'timbre_version')
    op.drop_column('voice_timbre_basic', 'timbre_demo_audio_url')
    op.drop_column('voice_timbre_basic', 'timbre_training_text')
    op.drop_column('voice_timbre_basic', 'timbre_source_duration')
    op.drop_column('voice_timbre_basic', 'timbre_model_type')
    op.drop_column('voice_timbre_basic', 'timbre_speaker_id')