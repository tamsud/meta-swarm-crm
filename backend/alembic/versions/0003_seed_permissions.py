"""Seed permissions catalogue

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-16

The full permission catalogue for all CRM modules. This is the single source
of truth for all {module}:{action} codes referenced by require_permission()
across the codebase.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003_seed_permissions'
down_revision: Union[str, None] = '0002_create_permissions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSIONS = [
    # Accounts module (4 codes)
    ('accounts:create', 'accounts', 'create', 'Create new accounts'),
    ('accounts:read', 'accounts', 'read', 'View accounts'),
    ('accounts:update', 'accounts', 'update', 'Update existing accounts'),
    ('accounts:delete', 'accounts', 'delete', 'Delete accounts'),

    # Contacts module (4 codes)
    ('contacts:create', 'contacts', 'create', 'Create new contacts'),
    ('contacts:read', 'contacts', 'read', 'View contacts'),
    ('contacts:update', 'contacts', 'update', 'Update existing contacts'),
    ('contacts:delete', 'contacts', 'delete', 'Delete contacts'),

    # Leads module (2 codes - ownership-based)
    ('leads:manage-own', 'leads', 'manage-own', 'Manage leads created by self'),
    ('leads:manage-all', 'leads', 'manage-all', 'Manage all leads regardless of owner'),

    # Opportunities module (4 codes)
    ('opportunities:create', 'opportunities', 'create', 'Create new opportunities'),
    ('opportunities:read', 'opportunities', 'read', 'View opportunities'),
    ('opportunities:update', 'opportunities', 'update', 'Update existing opportunities'),
    ('opportunities:delete', 'opportunities', 'delete', 'Delete opportunities'),

    # Activities module (2 codes - ownership-based)
    ('activities:manage-own', 'activities', 'manage-own', 'Manage activities created by self'),
    ('activities:manage-all', 'activities', 'manage-all', 'Manage all activities regardless of owner'),

    # Users module (2 codes)
    ('users:manage', 'users', 'manage', 'Manage all user accounts (Admin only)'),
    ('users:manage-self', 'users', 'manage-self', 'Manage own user profile'),

    # Roles module (1 code)
    ('roles:manage', 'roles', 'manage', 'Manage roles and permission assignments'),

    # Permissions module (1 code)
    ('permissions:read', 'permissions', 'read', 'View the permission catalogue'),

    # Seed/Deployment module (1 code)
    ('seed:manage', 'seed', 'manage', 'Run seed data operations (Admin only)'),
]


def upgrade() -> None:
    permissions_table = sa.table(
        'permissions',
        sa.column('code', sa.String),
        sa.column('module', sa.String),
        sa.column('action', sa.String),
        sa.column('description', sa.String),
    )

    op.bulk_insert(
        permissions_table,
        [
            {'code': code, 'module': module, 'action': action, 'description': desc}
            for code, module, action, desc in PERMISSIONS
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM permissions")
