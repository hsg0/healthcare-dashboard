# WHAT — Opens the connection to the Supabase Postgres database.
# WHY — Patient and note rows need one shared database connection for the whole API.
# HOW — Reads the database settings from .env, builds an async SQLAlchemy engine, and gives each request its own session.
# IMPORTANT — The password stays in .env. This file never prints it. SQL echo is off so patient rows are not written to the terminal. Supabase requires SSL, and its pooler breaks if asyncpg caches prepared statements, so that cache is turned off.

import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

# .env sits next to main.py, one folder above this file
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")


def convert_to_async_url(database_url: str) -> str:
    """SQLAlchemy's async engine needs the asyncpg driver named in the URL."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return database_url


if DB_USER and DB_PASSWORD and DB_HOST:
    safe_database_password = quote_plus(DB_PASSWORD)
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{safe_database_password}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    logger.info("Using DB_HOST=%s DB_PORT=%s DB_NAME=%s", DB_HOST, DB_PORT, DB_NAME)
else:
    database_url_from_env = os.getenv("DATABASE_URL")
    if not database_url_from_env:
        raise ValueError(
            "Database not configured. Copy .env.example to .env and set "
            "DB_USER, DB_PASSWORD, and DB_HOST, or set DATABASE_URL."
        )
    DATABASE_URL = convert_to_async_url(database_url_from_env)
    logger.info("Using DATABASE_URL from the environment")


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    connect_args={
        "ssl": "require",
        "statement_cache_size": 0,
    },
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class DatabaseBase(DeclarativeBase):
    """Patient and note table classes will inherit from this."""


async def database_session() -> AsyncIterator[AsyncSession]:
    """One database session for one request. Rolls back if that request fails."""
    async with SessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError:
            # Only a real database problem is worth a stack trace. A 404 or a 422 is not.
            logger.exception("Database session failed and was rolled back")
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise
