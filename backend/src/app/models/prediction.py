from sqlmodel import Field, SQLModel


class Prediction(SQLModel, table=True):
    """Top-N species predictions produced by the inference adapter for one image."""

    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    label: str = Field(index=True)
    confidence: float
    bbox_json: str | None = None
    model_version: str | None = None
    raw_json: str | None = None
