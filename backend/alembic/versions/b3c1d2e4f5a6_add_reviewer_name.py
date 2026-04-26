"""add_reviewer_name

Revision ID: b3c1d2e4f5a6
Revises: a50917b77cf4
Create Date: 2026-04-23 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3c1d2e4f5a6"
down_revision: str | Sequence[str] | None = "a50917b77cf4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add reviewer_name column to reviewrecord."""
    with op.batch_alter_table("reviewrecord", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reviewer_name", sa.String(), nullable=True))


def downgrade() -> None:
    """Remove reviewer_name column from reviewrecord."""
    with op.batch_alter_table("reviewrecord", schema=None) as batch_op:
        batch_op.drop_column("reviewer_name")
