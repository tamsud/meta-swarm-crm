"""Create users table

Revision ID: 0007_create_users
Revises: 0006_create_accounts
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0007_create_users'
down_revision: Union[str, None] = '0006_create_accounts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=128), nullable=False),
        sa.Column('display_name', sa.String(length=128), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='RESTRICT'),
    )

    # Create functional index on lower(email) for case-insensitive uniqueness
    op.create_index(
        'ix_users_email_lower',
        'users',
        [sa.text('lower(email)')],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_users_email_lower', table_name='users')
    op.drop_table('users')
