"""add account lockout fields

Revision ID: b5f321cd1234
Revises: ac494d920e90
Create Date: 2025-12-11 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5f321cd1234'
down_revision = 'ac494d920e90'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add account security fields to users table
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove account security fields
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'failed_login_attempts')
