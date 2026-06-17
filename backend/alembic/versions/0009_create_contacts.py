"""Create contacts table

Revision ID: 0009_create_contacts
Revises: 0008_seed_demo_users
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0009_create_contacts'
down_revision: Union[str, None] = '0008_seed_demo_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=128), nullable=False),
        sa.Column('last_name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('job_title', sa.String(length=128), nullable=True),
        sa.Column('account_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='SET NULL'),
    )

    # Create functional index on lower(email) for case-insensitive lookups
    op.create_index(
        'ix_contacts_email_lower',
        'contacts',
        [sa.text('lower(email)')],
        unique=False,
    )

    # Create unique constraint on lower(email) for case-insensitive uniqueness
    op.create_index(
        'ix_contacts_email_unique',
        'contacts',
        [sa.text('lower(email)')],
        unique=True,
    )

    # Create index on account_id for efficient filtering
    op.create_index(
        'ix_contacts_account_id',
        'contacts',
        ['account_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_contacts_account_id', table_name='contacts')
    op.drop_index('ix_contacts_email_unique', table_name='contacts')
    op.drop_index('ix_contacts_email_lower', table_name='contacts')
    op.drop_table('contacts')
