"""add performance indexes

Revision ID: c7d432ef5678
Revises: b5f321cd1234
Create Date: 2025-12-11 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7d432ef5678'
down_revision = 'b5f321cd1234'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes with if_not_exists for SQLite compatibility
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Helper function to check if index exists
    def create_index_if_not_exists(index_name, table_name, columns):
        existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
        if index_name not in existing_indexes:
            op.create_index(index_name, table_name, columns)

    # Add indexes to practice_sessions table for performance
    create_index_if_not_exists('ix_practice_sessions_started_at', 'practice_sessions', ['started_at'])
    create_index_if_not_exists('ix_practice_sessions_completed_at', 'practice_sessions', ['completed_at'])
    create_index_if_not_exists('ix_practice_sessions_user_started', 'practice_sessions', ['user_id', 'started_at'])

    # Add indexes to users table for common queries
    create_index_if_not_exists('ix_users_last_login', 'users', ['last_login'])
    create_index_if_not_exists('ix_users_created_at', 'users', ['created_at'])

    # Add indexes to poses table
    create_index_if_not_exists('ix_poses_difficulty', 'poses', ['difficulty_level'])
    create_index_if_not_exists('ix_poses_category', 'poses', ['category'])

    # Add indexes to sequences table
    create_index_if_not_exists('ix_sequences_difficulty', 'sequences', ['difficulty_level'])
    create_index_if_not_exists('ix_sequences_duration', 'sequences', ['duration_minutes'])
    create_index_if_not_exists('ix_sequences_created_by', 'sequences', ['created_by'])


def downgrade() -> None:
    # Remove all indexes
    op.drop_index('ix_sequences_created_by', table_name='sequences')
    op.drop_index('ix_sequences_duration', table_name='sequences')
    op.drop_index('ix_sequences_difficulty', table_name='sequences')

    op.drop_index('ix_poses_category', table_name='poses')
    op.drop_index('ix_poses_difficulty', table_name='poses')

    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_last_login', table_name='users')

    op.drop_index('ix_practice_sessions_user_started', table_name='practice_sessions')
    op.drop_index('ix_practice_sessions_completed_at', table_name='practice_sessions')
    op.drop_index('ix_practice_sessions_started_at', table_name='practice_sessions')
