"""add_is_banned_to_users

Revision ID: 3cb2717e3d03
Revises: b605c0ed54d2
Create Date: 2026-05-14 20:28:19.894042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cb2717e3d03'
down_revision: Union[str, Sequence[str], None] = 'b605c0ed54d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_banned', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('users', 'is_banned')
