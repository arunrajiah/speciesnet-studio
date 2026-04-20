from datetime import datetime

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    """A single image file within a collection."""

    id: int | None = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="collection.id", index=True)
    filename: str
    path: str
    captured_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    width: int | None = None
    height: int | None = None
    thumbnail_path: str | None = None
