from datetime import datetime

from pydantic import BaseModel


class CollectionCreate(BaseModel):
    """Payload for creating a new collection."""

    name: str
    source_folder: str


class CollectionRead(BaseModel):
    """Collection data returned to the client."""

    id: int
    name: str
    source_folder: str
    created_at: datetime
    item_count: int
