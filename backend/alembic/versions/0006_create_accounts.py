"""Create accounts table

Revision ID: 0006_create_accounts
Revises: 0005_seed_system_roles
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0006_create_accounts'
down_revision: Union[str, None] = '0005_seed_system_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=128), nullable=True),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create functional index on lower(name) for case-insensitive search
    op.create_index(
        'ix_accounts_name_lower',
        'accounts',
        [sa.text('lower(name)')],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_accounts_name_lower', table_name='accounts')
    op.drop_table('accounts')
