"""Add performance indexes for production readiness

Revision ID: b1c2d3e4f5a6
Revises: ac494d920e90
Create Date: 2025-12-11 16:45:00.000000

This migration adds critical indexes for:
- Users: email lookups, token lookups for authentication
- Practice Sessions: user history queries, time-based filtering
- Sequences: filtering by difficulty, focus area, style, preset status
- Poses: filtering by category and difficulty
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'b5f321cd1234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def index_exists(index_name: str, table_name: str) -> bool:
    """Check if an index already exists on the table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(idx['name'] == index_name for idx in indexes)


def create_index_if_not_exists(index_name: str, table_name: str, columns: list, unique: bool = False):
    """Create an index if it doesn't already exist."""
    if not index_exists(index_name, table_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def drop_index_if_exists(index_name: str, table_name: str):
    """Drop an index if it exists."""
    if index_exists(index_name, table_name):
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    """Add performance-critical indexes."""

    # Users table indexes
    # Index for password reset token lookups (used during password reset flow)
    create_index_if_not_exists(
        'ix_users_password_reset_token',
        'users',
        ['password_reset_token']
    )

    # Index for email verification token lookups (used during email verification)
    create_index_if_not_exists(
        'ix_users_email_verification_token',
        'users',
        ['email_verification_token']
    )

    # Practice Sessions table indexes
    # Composite index for user history queries with time filtering
    # This is the most critical index for dashboard performance
    create_index_if_not_exists(
        'ix_practice_sessions_user_started',
        'practice_sessions',
        ['user_id', 'started_at']
    )

    # Index for completion status filtering
    create_index_if_not_exists(
        'ix_practice_sessions_completion_status',
        'practice_sessions',
        ['completion_status']
    )

    # Composite index for user statistics aggregation
    create_index_if_not_exists(
        'ix_practice_sessions_user_status',
        'practice_sessions',
        ['user_id', 'completion_status']
    )

    # Sequences table indexes
    # Note: Many of these may already exist from model definitions,
    # but we explicitly ensure they're present

    # Composite index for common sequence filtering queries
    create_index_if_not_exists(
        'ix_sequences_difficulty_focus',
        'sequences',
        ['difficulty_level', 'focus_area']
    )

    # Composite index for preset + difficulty (common home page query)
    create_index_if_not_exists(
        'ix_sequences_preset_difficulty',
        'sequences',
        ['is_preset', 'difficulty_level']
    )

    # Poses table indexes
    # Composite index for category + difficulty filtering
    create_index_if_not_exists(
        'ix_poses_category_difficulty',
        'poses',
        ['category', 'difficulty_level']
    )

    # Sequence Poses table indexes
    # Composite index for efficient sequence loading
    create_index_if_not_exists(
        'ix_sequence_poses_seq_order',
        'sequence_poses',
        ['sequence_id', 'position_order']
    )


def downgrade() -> None:
    """Remove performance indexes."""

    # Remove in reverse order

    # Sequence Poses
    drop_index_if_exists('ix_sequence_poses_seq_order', 'sequence_poses')

    # Poses
    drop_index_if_exists('ix_poses_category_difficulty', 'poses')

    # Sequences
    drop_index_if_exists('ix_sequences_preset_difficulty', 'sequences')
    drop_index_if_exists('ix_sequences_difficulty_focus', 'sequences')

    # Practice Sessions
    drop_index_if_exists('ix_practice_sessions_user_status', 'practice_sessions')
    drop_index_if_exists('ix_practice_sessions_completion_status', 'practice_sessions')
    drop_index_if_exists('ix_practice_sessions_user_started', 'practice_sessions')

    # Users
    drop_index_if_exists('ix_users_email_verification_token', 'users')
    drop_index_if_exists('ix_users_password_reset_token', 'users')
