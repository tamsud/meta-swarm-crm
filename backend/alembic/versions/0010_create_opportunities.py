"""Create opportunities table

Revision ID: 0010_create_opportunities
Revises: 0009_create_contacts
Create Date: 2026-06-17

Creates the opportunities table with 5-stage pipeline enum.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0010_create_opportunities'
down_revision: Union[str, None] = '0009_create_contacts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create opportunity_stage enum type
    opportunity_stage_enum = sa.Enum(
        'prospecting',
        'proposal',
        'negotiation',
        'closed_won',
        'closed_lost',
        name='opportunity_stage',
    )
    opportunity_stage_enum.create(op.get_bind(), checkfirst=True)

    # Create opportunities table
    op.create_table(
        'opportunities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column(
            'stage',
            opportunity_stage_enum,
            nullable=False,
            server_default='prospecting',
        ),
        sa.Column('value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('probability', sa.Integer(), nullable=True),
        sa.Column('expected_close_date', sa.Date(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['account_id'],
            ['accounts.id'],
            name='fk_opportunities_account_id',
            ondelete='RESTRICT',
        ),
        sa.ForeignKeyConstraint(
            ['contact_id'],
            ['contacts.id'],
            name='fk_opportunities_contact_id',
            ondelete='SET NULL',
        ),
        sa.CheckConstraint('value > 0', name='ck_opportunities_value_positive'),
        sa.CheckConstraint(
            'probability >= 0 AND probability <= 100',
            name='ck_opportunities_probability_range',
        ),
    )

    # Create index for filtering by stage
    op.create_index(
        'ix_opportunities_stage',
        'opportunities',
        ['stage'],
        unique=False,
    )

    # Create index for filtering by account
    op.create_index(
        'ix_opportunities_account_id',
        'opportunities',
        ['account_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_opportunities_account_id', table_name='opportunities')
    op.drop_index('ix_opportunities_stage', table_name='opportunities')
    op.drop_table('opportunities')

    # Drop the enum type
    opportunity_stage_enum = sa.Enum(name='opportunity_stage')
    opportunity_stage_enum.drop(op.get_bind(), checkfirst=True)
