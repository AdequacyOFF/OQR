"""Add institutions table, participant institution_id and dob.

Revision ID: 004
Revises: 2126be9ffb45
Create Date: 2026-02-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '2126be9ffb45'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create institutions table
    op.create_table('institutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('short_name', sa.String(100), nullable=True),
        sa.Column('city', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_institutions_name', 'institutions', ['name'])

    # Add columns to participants
    op.add_column('participants', sa.Column('institution_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('participants', sa.Column('dob', sa.Date(), nullable=True))
    op.create_foreign_key(
        'fk_participants_institution_id',
        'participants', 'institutions',
        ['institution_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_participants_institution_id', 'participants', ['institution_id'])

    # Data migration: insert distinct school values into institutions
    op.execute("""
        INSERT INTO institutions (id, name, created_at)
        SELECT DISTINCT gen_random_uuid(), school, now()
        FROM participants
        WHERE school IS NOT NULL AND school != ''
        ON CONFLICT (name) DO NOTHING
    """)

    # Update participants.institution_id from matching school names
    op.execute("""
        UPDATE participants p
        SET institution_id = i.id
        FROM institutions i
        WHERE p.school = i.name
    """)

    # Make school column nullable for forward compat
    op.alter_column('participants', 'school', nullable=True)


def downgrade() -> None:
    op.alter_column('participants', 'school', nullable=False)
    op.drop_index('ix_participants_institution_id', 'participants')
    op.drop_constraint('fk_participants_institution_id', 'participants', type_='foreignkey')
    op.drop_column('participants', 'dob')
    op.drop_column('participants', 'institution_id')
    op.drop_index('ix_institutions_name', 'institutions')
    op.drop_table('institutions')
