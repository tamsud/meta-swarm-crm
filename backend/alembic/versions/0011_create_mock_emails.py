"""Create mock_emails table

Revision ID: 0011_create_mock_emails
Revises: 0010_create_opportunities
Create Date: 2026-06-17

Mock emails table for simulated outbound email display.
See specs/mock-email/spec.md for requirements.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0011_create_mock_emails'
down_revision: Union[str, None] = '0010_create_opportunities'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create mock_emails table
    op.create_table(
        'mock_emails',
        sa.Column('id', sa.String(36), nullable=False),  # UUID stored as string for SQLite compatibility
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('from_email', sa.String(length=255), nullable=False),
        sa.Column('to_email', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column(
            'status',
            sa.String(length=20),
            nullable=False,
            server_default='unread',
        ),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('unread', 'read')", name='ck_mock_emails_status'),
    )

    # Index on subject for search performance
    op.create_index('ix_mock_emails_subject', 'mock_emails', ['subject'], unique=False)

    # Index on created_at for sort performance
    op.create_index('ix_mock_emails_created_at', 'mock_emails', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_mock_emails_created_at', table_name='mock_emails')
    op.drop_index('ix_mock_emails_subject', table_name='mock_emails')
    op.drop_table('mock_emails')
