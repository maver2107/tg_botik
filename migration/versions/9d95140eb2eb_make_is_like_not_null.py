"""make is_like NOT NULL

Revision ID: 9d95140eb2eb
Revises: 7e2ee870ec47
Create Date: 2026-05-21 17:31:36.738222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d95140eb2eb'
down_revision: Union[str, Sequence[str], None] = '7e2ee870ec47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("UPDATE likes SET is_like = FALSE WHERE is_like IS NULL"))
    op.alter_column('likes', 'is_like',
                    existing_type=sa.Boolean(),
                    nullable=False)


def downgrade() -> None:
    op.alter_column('likes', 'is_like',
                    existing_type=sa.Boolean(),
                    nullable=True)
