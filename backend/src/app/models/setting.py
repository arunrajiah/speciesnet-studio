from sqlmodel import Field, SQLModel


class AppSetting(SQLModel, table=True):
    """A saved setting, such as the WildNetwork key and location (see services/settings.py)."""

    key: str = Field(primary_key=True)
    value: str
