from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    """Inference job record persisted to the database."""

    id: str = Field(primary_key=True)
    status: str = "pending"
    stage: str = ""
    current: int = 0
    total: int = 0
    started_at: str = ""
    finished_at: str | None = None
    error: str | None = None
