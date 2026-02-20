"""Add rooms and seat_assignments tables.

Revision ID: 005
Revises: 004
Create Date: 2026-02-20 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create rooms table
    op.create_table('rooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('competition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('competition_id', 'name', name='uq_room_competition_name'),
    )
    op.create_index('ix_rooms_competition_id', 'rooms', ['competition_id'])

    # Create seat_assignments table
    op.create_table('seat_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('registration_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('room_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('variant_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('room_id', 'seat_number', name='uq_room_seat'),
    )
    op.create_index('ix_seat_assignments_registration_id', 'seat_assignments', ['registration_id'])
    op.create_index('ix_seat_assignments_room_id', 'seat_assignments', ['room_id'])


def downgrade() -> None:
    op.drop_index('ix_seat_assignments_room_id', 'seat_assignments')
    op.drop_index('ix_seat_assignments_registration_id', 'seat_assignments')
    op.drop_table('seat_assignments')
    op.drop_index('ix_rooms_competition_id', 'rooms')
    op.drop_table('rooms')
