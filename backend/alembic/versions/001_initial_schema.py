"""Initial schema with all tables and indexes.

Revision ID: 001
Revises:
Create Date: 2026-02-12 12:00:00.000000

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
    # Create enum types
    user_role_enum = postgresql.ENUM('participant', 'admitter', 'scanner', 'admin', name='userrole', create_type=False)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    competition_status_enum = postgresql.ENUM('draft', 'registration_open', 'in_progress', 'checking', 'published', name='competitionstatus', create_type=False)
    competition_status_enum.create(op.get_bind(), checkfirst=True)

    registration_status_enum = postgresql.ENUM('pending', 'admitted', 'completed', 'cancelled', name='registrationstatus', create_type=False)
    registration_status_enum.create(op.get_bind(), checkfirst=True)

    attempt_status_enum = postgresql.ENUM('printed', 'scanned', 'scored', 'published', 'invalidated', name='attemptstatus', create_type=False)
    attempt_status_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])

    # Create participants table
    op.create_table('participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('school', sa.String(255), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_participants_user_id', 'participants', ['user_id'])
    op.create_index('ix_participants_full_name', 'participants', ['full_name'])
    op.create_index('ix_participants_grade', 'participants', ['grade'])

    # Create competitions table
    op.create_table('competitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('registration_start', sa.DateTime(), nullable=False),
        sa.Column('registration_end', sa.DateTime(), nullable=False),
        sa.Column('variants_count', sa.Integer(), nullable=False),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('status', competition_status_enum, nullable=False, server_default='draft'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
    )
    op.create_index('ix_competitions_name', 'competitions', ['name'])
    op.create_index('ix_competitions_date', 'competitions', ['date'])
    op.create_index('ix_competitions_status', 'competitions', ['status'])
    op.create_index('ix_competitions_created_by', 'competitions', ['created_by'])

    # Create registrations table
    op.create_table('registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', registration_status_enum, nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('participant_id', 'competition_id', name='uq_participant_competition'),
    )
    op.create_index('ix_registrations_participant_id', 'registrations', ['participant_id'])
    op.create_index('ix_registrations_competition_id', 'registrations', ['competition_id'])
    op.create_index('ix_registrations_status', 'registrations', ['status'])
    op.create_index('ix_registrations_participant_status', 'registrations', ['participant_id', 'status'])
    op.create_index('ix_registrations_competition_status', 'registrations', ['competition_id', 'status'])

    # Create entry_tokens table
    op.create_table('entry_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('registration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('registration_id'),
    )
    op.create_index('ix_entry_tokens_token_hash', 'entry_tokens', ['token_hash'])
    op.create_index('ix_entry_tokens_registration_id', 'entry_tokens', ['registration_id'])
    op.create_index('ix_entry_tokens_expires_at', 'entry_tokens', ['expires_at'])

    # Create attempts table
    op.create_table('attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('registration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_number', sa.Integer(), nullable=False),
        sa.Column('sheet_token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('status', attempt_status_enum, nullable=False, server_default='printed'),
        sa.Column('score_total', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('pdf_file_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_attempts_registration_id', 'attempts', ['registration_id'])
    op.create_index('ix_attempts_sheet_token_hash', 'attempts', ['sheet_token_hash'])
    op.create_index('ix_attempts_status', 'attempts', ['status'])
    op.create_index('ix_attempts_registration_status', 'attempts', ['registration_id', 'status'])

    # Create scans table
    op.create_table('scans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('ocr_score', sa.Integer(), nullable=True),
        sa.Column('ocr_confidence', sa.Float(), nullable=True),
        sa.Column('ocr_raw_text', sa.Text(), nullable=True),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='RESTRICT'),
    )
    op.create_index('ix_scans_attempt_id', 'scans', ['attempt_id'])
    op.create_index('ix_scans_verified_by', 'scans', ['verified_by'])
    op.create_index('ix_scans_uploaded_by', 'scans', ['uploaded_by'])
    op.create_index('ix_scans_attempt_created', 'scans', ['attempt_id', 'created_at'])

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('ix_audit_logs_action_timestamp', 'audit_logs', ['action', 'timestamp'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('scans')
    op.drop_table('attempts')
    op.drop_table('entry_tokens')
    op.drop_table('registrations')
    op.drop_table('competitions')
    op.drop_table('participants')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS attemptstatus')
    op.execute('DROP TYPE IF EXISTS registrationstatus')
    op.execute('DROP TYPE IF EXISTS competitionstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
