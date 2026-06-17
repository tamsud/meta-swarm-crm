"""Add dashboard:view permission and assign to all system roles

Revision ID: 0015_add_dashboard_permission
Revises: 0014_create_leads
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0015_add_dashboard_permission'
down_revision: Union[str, None] = '0014_create_leads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

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
            {
                'code': 'dashboard:view',
                'module': 'dashboard',
                'action': 'view',
                'description': 'View the dashboard summary and KPIs',
            }
        ]
    )

    permission_result = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code = 'dashboard:view'")
    )
    permission_id = permission_result.scalar_one()

    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
    )

    op.bulk_insert(
        role_permissions_table,
        [
            {'role_id': 1, 'permission_id': permission_id},  # Admin
            {'role_id': 2, 'permission_id': permission_id},  # Manager
            {'role_id': 3, 'permission_id': permission_id},  # Sales Rep
        ]
    )


def downgrade() -> None:
    conn = op.get_bind()

    permission_result = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code = 'dashboard:view'")
    )
    row = permission_result.fetchone()

    if row:
        pid = row[0]
        conn.execute(sa.text("DELETE FROM role_permissions WHERE permission_id = :pid"), {'pid': pid})

    conn.execute(sa.text("DELETE FROM permissions WHERE code = 'dashboard:view'"))
