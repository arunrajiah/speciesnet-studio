"""Alembic environment — wired to SQLModel metadata."""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import all models so their tables are registered on SQLModel.metadata
import app.models.collection  # noqa: F401
import app.models.ingestion_progress  # noqa: F401
import app.models.item  # noqa: F401
import app.models.job  # noqa: F401
import app.models.prediction  # noqa: F401
import app.models.review  # noqa: F401
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# Allow DATABASE_URL env var to override alembic.ini sqlalchemy.url
_db_url = os.environ.get("DATABASE_URL", "sqlite:///./data/app.db")
config.set_main_option("sqlalchemy.url", _db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # required for SQLite ALTER TABLE support
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
