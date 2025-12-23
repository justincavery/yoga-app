"""add_pose_relationships_table

Revision ID: f52918529497
Revises: 9b32766df525
Create Date: 2025-12-16 16:43:04.631705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f52918529497'
down_revision: Union[str, Sequence[str], None] = '9b32766df525'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pose_relationships table."""
    # Check if table already exists (may have been created by init_database)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'pose_relationships' not in existing_tables:
        # Create pose_relationships table
        op.create_table(
            'pose_relationships',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('pose_id', sa.Integer(), nullable=False),
            sa.Column('related_pose_id', sa.Integer(), nullable=False),
            sa.Column('relationship_type', sa.Enum('similar', 'progression', name='relationshiptype'), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['pose_id'], ['poses.pose_id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['related_pose_id'], ['poses.pose_id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

        # Create indexes for performance
        op.create_index('ix_pose_relationships_id', 'pose_relationships', ['id'])
        op.create_index('ix_pose_relationships_pose_id', 'pose_relationships', ['pose_id'])
        op.create_index('ix_pose_relationships_related_pose_id', 'pose_relationships', ['related_pose_id'])
        op.create_index('ix_pose_relationships_relationship_type', 'pose_relationships', ['relationship_type'])


def downgrade() -> None:
    """Drop pose_relationships table."""
    op.drop_index('ix_pose_relationships_relationship_type', table_name='pose_relationships')
    op.drop_index('ix_pose_relationships_related_pose_id', table_name='pose_relationships')
    op.drop_index('ix_pose_relationships_pose_id', table_name='pose_relationships')
    op.drop_index('ix_pose_relationships_id', table_name='pose_relationships')
    op.drop_table('pose_relationships')
