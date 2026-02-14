"""add raw_token to entry_tokens

Revision ID: 510093419eba
Revises: 001
Create Date: 2026-02-14 13:28:04.946724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '510093419eba'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add raw_token column to entry_tokens table
    op.add_column('entry_tokens', sa.Column('raw_token', sa.String(length=64), nullable=True))


def downgrade() -> None:
    # Remove raw_token column from entry_tokens table
    op.drop_column('entry_tokens', 'raw_token')
