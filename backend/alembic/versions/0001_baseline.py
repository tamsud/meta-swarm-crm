"""Baseline migration - empty database scaffold.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-06-16

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Empty baseline - no CRM tables created yet."""
    pass


def downgrade() -> None:
    """Reverse baseline - nothing to undo."""
    pass
