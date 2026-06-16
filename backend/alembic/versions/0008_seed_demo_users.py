"""Seed demo users for development

Revision ID: 0008_seed_demo_users
Revises: 0007_create_users
Create Date: 2026-06-17

Demo users (one per system role):
- admin@crm.local / admin123 -> Admin role
- manager@crm.local / manager123 -> Manager role
- rep@crm.local / rep123 -> Sales Rep role

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import bcrypt


revision: str = '0008_seed_demo_users'
down_revision: Union[str, None] = '0007_create_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


# Demo users configuration
DEMO_USERS = [
    {
        'email': 'admin@crm.local',
        'password': 'admin123',
        'display_name': 'Admin User',
        'role_id': 1,  # Admin role
    },
    {
        'email': 'manager@crm.local',
        'password': 'manager123',
        'display_name': 'Manager User',
        'role_id': 2,  # Manager role
    },
    {
        'email': 'rep@crm.local',
        'password': 'rep123',
        'display_name': 'Sales Rep User',
        'role_id': 3,  # Sales Rep role
    },
]


def upgrade() -> None:
    conn = op.get_bind()

    # Define users table for raw SQL operations
    users_table = sa.table(
        'users',
        sa.column('id', sa.Integer),
        sa.column('email', sa.String),
        sa.column('hashed_password', sa.String),
        sa.column('display_name', sa.String),
        sa.column('role_id', sa.Integer),
        sa.column('is_active', sa.Boolean),
    )

    for user_data in DEMO_USERS:
        # Check if user already exists (idempotent)
        result = conn.execute(
            sa.text("SELECT id FROM users WHERE lower(email) = lower(:email)"),
            {'email': user_data['email']}
        )
        existing_user = result.fetchone()

        if existing_user is None:
            # Hash password and insert user
            hashed_password = _hash_password(user_data['password'])
            conn.execute(
                users_table.insert().values(
                    email=user_data['email'],
                    hashed_password=hashed_password,
                    display_name=user_data['display_name'],
                    role_id=user_data['role_id'],
                    is_active=True,
                )
            )


def downgrade() -> None:
    # Delete demo users by email
    conn = op.get_bind()
    for user_data in DEMO_USERS:
        conn.execute(
            sa.text("DELETE FROM users WHERE lower(email) = lower(:email)"),
            {'email': user_data['email']}
        )
