"""Add invigilator role, participant events, answer sheets.

Revision ID: 007
Revises: 006
Create Date: 2026-02-20 10:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add invigilator to userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'invigilator'")

    # Create event_type enum
    event_type_enum = postgresql.ENUM(
        'start_work', 'submit', 'exit_room', 'enter_room',
        name='eventtype', create_type=False
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)

    # Create sheet_kind enum
    sheet_kind_enum = postgresql.ENUM(
        'primary', 'extra',
        name='sheetkind', create_type=False
    )
    sheet_kind_enum.create(op.get_bind(), checkfirst=True)

    # Create participant_events table
    op.create_table('participant_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('recorded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_participant_events_attempt_id', 'participant_events', ['attempt_id'])
    op.create_index('ix_participant_events_recorded_by', 'participant_events', ['recorded_by'])

    # Create answer_sheets table
    op.create_table('answer_sheets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sheet_token_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('kind', sheet_kind_enum, nullable=False),
        sa.Column('pdf_file_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_answer_sheets_attempt_id', 'answer_sheets', ['attempt_id'])
    op.create_index('ix_answer_sheets_sheet_token_hash', 'answer_sheets', ['sheet_token_hash'])

    # Add answer_sheet_id to scans
    op.add_column('scans', sa.Column('answer_sheet_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_scans_answer_sheet_id',
        'scans', 'answer_sheets',
        ['answer_sheet_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_scans_answer_sheet_id', 'scans', ['answer_sheet_id'])

    # Data migration: create answer_sheets from existing attempts
    op.execute("""
        INSERT INTO answer_sheets (id, attempt_id, sheet_token_hash, kind, pdf_file_path, created_at)
        SELECT gen_random_uuid(), id, sheet_token_hash, 'primary', pdf_file_path, created_at
        FROM attempts
        WHERE sheet_token_hash IS NOT NULL
    """)

    # Link existing scans to their answer_sheets
    op.execute("""
        UPDATE scans s
        SET answer_sheet_id = a_s.id
        FROM answer_sheets a_s
        JOIN attempts att ON a_s.attempt_id = att.id
        WHERE s.attempt_id = att.id AND a_s.kind = 'primary'
    """)


def downgrade() -> None:
    op.drop_index('ix_scans_answer_sheet_id', 'scans')
    op.drop_constraint('fk_scans_answer_sheet_id', 'scans', type_='foreignkey')
    op.drop_column('scans', 'answer_sheet_id')

    op.drop_index('ix_answer_sheets_sheet_token_hash', 'answer_sheets')
    op.drop_index('ix_answer_sheets_attempt_id', 'answer_sheets')
    op.drop_table('answer_sheets')

    op.drop_index('ix_participant_events_recorded_by', 'participant_events')
    op.drop_index('ix_participant_events_attempt_id', 'participant_events')
    op.drop_table('participant_events')

    op.execute('DROP TYPE IF EXISTS sheetkind')
    op.execute('DROP TYPE IF EXISTS eventtype')
    # Note: cannot remove enum value from userrole in PostgreSQL
