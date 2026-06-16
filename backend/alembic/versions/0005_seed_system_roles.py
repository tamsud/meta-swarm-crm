"""Seed system roles with permission mappings

Revision ID: 0005_seed_system_roles
Revises: 0004_create_roles
Create Date: 2026-06-16

System roles:
- Admin: Full catalogue (22 permissions)
- Manager: All CRM operations + manage-all for leads/activities (16 permissions)
- Sales Rep: Basic CRM + manage-own for leads/activities (13 permissions)

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0005_seed_system_roles'
down_revision: Union[str, None] = '0004_create_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Permission codes for each role
ADMIN_PERMISSIONS = [
    # Admin gets ALL permissions (22 total)
    'accounts:create', 'accounts:read', 'accounts:update', 'accounts:delete',
    'contacts:create', 'contacts:read', 'contacts:update', 'contacts:delete',
    'leads:manage-own', 'leads:manage-all',
    'opportunities:create', 'opportunities:read', 'opportunities:update', 'opportunities:delete',
    'activities:manage-own', 'activities:manage-all',
    'users:manage', 'users:manage-self',
    'roles:read', 'roles:manage',
    'permissions:read',
    'seed:manage',
]

MANAGER_PERMISSIONS = [
    # Manager: Full CRM access + manage-all for leads/activities (16 total)
    'accounts:create', 'accounts:read', 'accounts:update', 'accounts:delete',
    'contacts:create', 'contacts:read', 'contacts:update', 'contacts:delete',
    'leads:manage-all',  # Can manage all leads, not just own
    'opportunities:create', 'opportunities:read', 'opportunities:update', 'opportunities:delete',
    'activities:manage-all',  # Can manage all activities, not just own
    'users:manage-self',
    'permissions:read',
]

SALES_REP_PERMISSIONS = [
    # Sales Rep: Basic CRM + manage-own for leads/activities (13 total)
    'accounts:create', 'accounts:read', 'accounts:update',  # NO delete
    'contacts:create', 'contacts:read', 'contacts:update', 'contacts:delete',
    'leads:manage-own',  # Can only manage own leads
    'opportunities:create', 'opportunities:read', 'opportunities:update',  # NO delete
    'activities:manage-own',  # Can only manage own activities
    'users:manage-self',
]


def upgrade() -> None:
    conn = op.get_bind()

    # Insert system roles
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('is_system', sa.Boolean),
    )

    op.bulk_insert(roles_table, [
        {'id': 1, 'name': 'Admin', 'description': 'Full system access', 'is_system': True},
        {'id': 2, 'name': 'Manager', 'description': 'Team management and full CRM access', 'is_system': True},
        {'id': 3, 'name': 'Sales Rep', 'description': 'Standard sales operations', 'is_system': True},
    ])

    # Get permission IDs by code
    permissions_result = conn.execute(
        sa.text("SELECT id, code FROM permissions")
    )
    permission_map = {row[1]: row[0] for row in permissions_result}

    # Build role_permissions rows
    role_permissions_data = []

    for perm_code in ADMIN_PERMISSIONS:
        if perm_code in permission_map:
            role_permissions_data.append({'role_id': 1, 'permission_id': permission_map[perm_code]})

    for perm_code in MANAGER_PERMISSIONS:
        if perm_code in permission_map:
            role_permissions_data.append({'role_id': 2, 'permission_id': permission_map[perm_code]})

    for perm_code in SALES_REP_PERMISSIONS:
        if perm_code in permission_map:
            role_permissions_data.append({'role_id': 3, 'permission_id': permission_map[perm_code]})

    # Insert role_permissions
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
    )

    op.bulk_insert(role_permissions_table, role_permissions_data)


def downgrade() -> None:
    # Delete in reverse order due to FK constraints
    op.execute("DELETE FROM role_permissions WHERE role_id IN (1, 2, 3)")
    op.execute("DELETE FROM roles WHERE is_system = 1")
