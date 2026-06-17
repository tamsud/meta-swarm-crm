"""Add mock-email:view permission and assign to all roles

Revision ID: 0012_add_mock_email_permission
Revises: 0011_create_mock_emails
Create Date: 2026-06-17

Adds the mock-email:view permission to the permissions catalogue and
assigns it to all 3 system roles (Admin, Manager, Sales Rep) since
this is a demo utility accessible to all logged-in users.

See specs/mock-email/spec.md for requirements.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0012_add_mock_email_permission'
down_revision: Union[str, None] = '0011_create_mock_emails'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Insert the mock-email:view permission
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
                'code': 'mock-email:view',
                'module': 'mock-email',
                'action': 'view',
                'description': 'View mock email inbox',
            }
        ]
    )

    # Get the permission ID
    permission_result = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code = 'mock-email:view'")
    )
    permission_id = permission_result.scalar_one()

    # Assign to all 3 system roles (Admin=1, Manager=2, Sales Rep=3)
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

    # Get the permission ID
    permission_result = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code = 'mock-email:view'")
    )
    permission_row = permission_result.fetchone()

    if permission_row:
        permission_id = permission_row[0]

        # Remove role_permissions entries
        conn.execute(
            sa.text("DELETE FROM role_permissions WHERE permission_id = :pid"),
            {'pid': permission_id}
        )

    # Remove the permission
    conn.execute(
        sa.text("DELETE FROM permissions WHERE code = 'mock-email:view'")
    )
