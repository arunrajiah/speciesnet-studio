import logging
import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def init_db() -> None:
    """Ensure the database directory exists and schema is up to date.

    Strategy:
    - If this is a **fresh install** (no alembic_version table) we run
      ``alembic upgrade head`` which creates all tables and stamps the DB.
    - If the DB was created by an older version of Studio that pre-dates
      alembic (tables exist but no alembic_version row) we stamp it at
      the baseline revision so future ``upgrade head`` calls are safe.
    - If alembic is not importable we fall back to SQLModel create_all so
      the app still starts in minimal environments.
    """
    db_path = DATABASE_URL.removeprefix("sqlite:///")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    try:
        from alembic.config import Config
        from sqlalchemy import inspect, text

        from alembic import command

        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "alembic.ini")
        alembic_cfg = Config(os.path.abspath(config_path))
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

        insp = inspect(engine)
        existing_tables = set(insp.get_table_names())

        if not existing_tables:
            # Completely fresh — let alembic create everything.
            logger.info("Fresh database — running alembic upgrade head")
            command.upgrade(alembic_cfg, "head")
        elif "alembic_version" not in existing_tables:
            # Pre-alembic install: tables exist but were not managed by migrations.
            # Stamp the baseline so future upgrades work correctly.
            logger.info("Existing pre-alembic database detected — stamping baseline revision")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))  # ensure connection is live
            command.stamp(alembic_cfg, "head")
        else:
            # Normal upgrade path.
            logger.info("Running alembic upgrade head")
            command.upgrade(alembic_cfg, "head")

    except ImportError:
        logger.warning("alembic not available — falling back to SQLModel create_all")
        SQLModel.metadata.create_all(engine)
    except Exception as exc:
        logger.error("alembic migration failed (%s) — falling back to create_all", exc)
        SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session; closes on exit."""
    with Session(engine) as session:
        yield session
