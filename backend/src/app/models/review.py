from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class ReviewStatus(StrEnum):
    unreviewed = "unreviewed"
    confirmed = "confirmed"
    overridden = "overridden"
    flagged = "flagged"


class ReviewRecord(SQLModel, table=True):
    """Human review decision attached to a single image."""

    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id", unique=True, index=True)
    status: ReviewStatus = ReviewStatus.unreviewed
    override_label: str | None = None
    reviewer_note: str | None = None
    reviewer_name: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
