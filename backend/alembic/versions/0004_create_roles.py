"""Create roles and role_permissions tables

Revision ID: 0004_create_roles
Revises: 0003_seed_permissions
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0004_create_roles'
down_revision: Union[str, None] = '0003_seed_permissions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # Create role_permissions junction table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    # Create index for permission lookups by role
    op.create_index('ix_role_permissions_role_id', 'role_permissions', ['role_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_role_permissions_role_id', table_name='role_permissions')
    op.drop_table('role_permissions')
    op.drop_table('roles')
