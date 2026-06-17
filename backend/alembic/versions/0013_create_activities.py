"""Create activities table

Revision ID: 0013_create_activities
Revises: 0012_add_mock_email_permission
Create Date: 2026-06-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0013_create_activities'
down_revision: Union[str, None] = '0012_add_mock_email_permission'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    activity_type_enum = sa.Enum('call', 'email', 'meeting', name='activity_type')
    activity_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', activity_type_enum, nullable=False),
        sa.Column('subject', sa.String(length=512), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'activity_date',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            'contact_id IS NOT NULL OR opportunity_id IS NOT NULL',
            name='ck_activities_link_required',
        ),
    )


def downgrade() -> None:
    op.drop_table('activities')
    sa.Enum(name='activity_type').drop(op.get_bind(), checkfirst=True)
