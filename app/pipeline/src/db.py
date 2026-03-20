from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base


def _normalize_sqlite_url(url: str) -> str:
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url

    raw_path = url[len(prefix) :]
    path = Path(raw_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path.as_posix()}"


def get_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return _normalize_sqlite_url(explicit_url)

    # Default to local SQLite so the pipeline can run with minimal local setup.
    project_root = Path(__file__).resolve().parents[3]
    sqlite_path = project_root / ".data" / "ir.db"
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{sqlite_path.as_posix()}"


def get_postgres_url_from_parts() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ir")
    user = os.getenv("POSTGRES_USER", "ir")
    password = os.getenv("POSTGRES_PASSWORD", "ir")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


database_url = get_database_url()
if database_url.startswith("sqlite"):
    engine = create_engine(database_url)
else:
    engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_schema() -> None:
    # Keep schema.sql in the repo as a SQL reference, but create tables from ORM metadata.
    Base.metadata.create_all(bind=engine)
