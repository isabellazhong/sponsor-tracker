"""initial baseline (no tables yet)

Creates no schema: it exists so a fresh database can be stamped and migrated,
and so the test fixture has a migration chain to run. Real tables arrive with
the data model in the next phase.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-09-22

"""

from collections.abc import Sequence

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
