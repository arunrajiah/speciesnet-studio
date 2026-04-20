from sqlmodel import Field, SQLModel


class IngestionProgress(SQLModel, table=True):
    """Per-collection ingestion progress persisted to the database."""

    collection_id: int = Field(primary_key=True)
    processed: int = 0
    total: int = 0
    stage: str = "idle"
