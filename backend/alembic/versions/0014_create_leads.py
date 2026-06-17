"""Create leads table

Revision ID: 0014_create_leads
Revises: 0013_create_activities
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0014_create_leads'
down_revision: Union[str, None] = '0013_create_activities'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    lead_status_enum = sa.Enum('new', 'contacted', 'qualified', 'lost', name='lead_status')
    lead_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=128), nullable=False),
        sa.Column('last_name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('company', sa.String(length=256), nullable=True),
        sa.Column('status', lead_status_enum, nullable=False, server_default='new'),
        sa.Column('source', sa.String(length=128), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('converted_opportunity_id', sa.Integer(), nullable=True),
        sa.Column('converted_at', sa.DateTime(), nullable=True),
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
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['converted_opportunity_id'], ['opportunities.id'], ondelete='SET NULL'),
    )


def downgrade() -> None:
    op.drop_table('leads')
    sa.Enum(name='lead_status').drop(op.get_bind(), checkfirst=True)
