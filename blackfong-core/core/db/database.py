from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import SETTINGS


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def create_db_engine() -> Engine:
    _ensure_parent_dir(SETTINGS.db_path)
    url = f"sqlite:///{SETTINGS.db_path}"
    return create_engine(
        url,
        future=True,
        connect_args={"check_same_thread": False},
    )


ENGINE = create_db_engine()
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

