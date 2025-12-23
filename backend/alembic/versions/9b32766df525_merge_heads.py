"""merge heads

Revision ID: 9b32766df525
Revises: c7d432ef5678, add_pose_instructions
Create Date: 2025-12-16 16:42:54.299858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b32766df525'
down_revision: Union[str, Sequence[str], None] = ('c7d432ef5678', 'add_pose_instructions')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
