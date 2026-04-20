import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def init_db() -> None:
    """Create ./data/ directory if needed and run table migrations."""
    db_path = DATABASE_URL.removeprefix("sqlite:///")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session; closes on exit."""
    with Session(engine) as session:
        yield session
