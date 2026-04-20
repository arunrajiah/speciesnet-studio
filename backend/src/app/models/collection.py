from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Collection(SQLModel, table=True):
    """A named project grouping a set of images for review."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    source_folder: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
