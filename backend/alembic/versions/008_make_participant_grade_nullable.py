"""Make participant grade column nullable.

Revision ID: 008
Revises: 007
Create Date: 2026-02-20 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('participants', 'grade',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('participants', 'grade',
                    existing_type=sa.Integer(),
                    nullable=False)
