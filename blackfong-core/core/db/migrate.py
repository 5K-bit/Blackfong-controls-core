from __future__ import annotations

from core.db.database import ENGINE
from core.db.models import Base


def migrate() -> None:
    # SQLite: simple "create if missing" is good enough for phase 1.
    Base.metadata.create_all(bind=ENGINE)

