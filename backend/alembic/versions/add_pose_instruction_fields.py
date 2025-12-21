"""Add pose instruction fields for TTS and guidance

Revision ID: add_pose_instructions
Revises: b1c2d3e4f5a6
Create Date: 2025-12-16 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_pose_instructions'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add instruction fields to poses table."""
    # Check if we're using PostgreSQL or SQLite
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # PostgreSQL supports native ARRAY type
        op.add_column('poses', sa.Column('entry_instructions', postgresql.ARRAY(sa.Text()), nullable=True))
        op.add_column('poses', sa.Column('exit_instructions', postgresql.ARRAY(sa.Text()), nullable=True))
    else:
        # SQLite: use JSON to store arrays
        op.add_column('poses', sa.Column('entry_instructions', sa.JSON(), nullable=True))
        op.add_column('poses', sa.Column('exit_instructions', sa.JSON(), nullable=True))

    # Add text columns for holding cues and breathing pattern
    op.add_column('poses', sa.Column('holding_cues', sa.Text(), nullable=True))
    op.add_column('poses', sa.Column('breathing_pattern', sa.Text(), nullable=True))

    # Add boolean flag for side variations
    op.add_column('poses', sa.Column('has_side_variation', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Remove instruction fields from poses table."""
    op.drop_column('poses', 'has_side_variation')
    op.drop_column('poses', 'breathing_pattern')
    op.drop_column('poses', 'holding_cues')
    op.drop_column('poses', 'exit_instructions')
    op.drop_column('poses', 'entry_instructions')
