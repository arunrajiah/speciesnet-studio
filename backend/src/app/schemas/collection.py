from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, field_validator


class CollectionCreate(BaseModel):
    """Payload for creating a new collection."""

    name: str
    source_folder: str

    @field_validator("source_folder")
    @classmethod
    def no_path_traversal(cls, v: str) -> str:
        resolved = Path(v).resolve()
        # Reject if any traversal sequences remain after resolution
        if ".." in Path(v).parts:
            raise ValueError("source_folder must not contain '..' path components")
        if not resolved.exists():
            raise ValueError("source_folder does not exist")
        if not resolved.is_dir():
            raise ValueError("source_folder must be a directory")
        return str(resolved)


class CollectionRead(BaseModel):
    """Collection data returned to the client."""

    id: int
    name: str
    source_folder: str
    created_at: datetime
    item_count: int
