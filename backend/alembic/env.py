
from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy import create_engine

from alembic import context

import os
import sys

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure project root on path
root_path = Path(__file__).resolve().parents[1]
sys.path.append(str(root_path))

from src.infrastructure.adapters.models import Base

target_metadata = Base.metadata


def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        # Alembic runs sync, convert async driver to sync
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        return url
    # fallback to alembic.ini
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=url,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
