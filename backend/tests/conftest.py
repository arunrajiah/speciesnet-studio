import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture()
def session():
    """In-memory SQLite session, schema created fresh for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
