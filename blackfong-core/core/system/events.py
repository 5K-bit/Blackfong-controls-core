from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.config import SETTINGS
from core.db.models import EventLog


def log_event(db: Session, level: str, message: str) -> EventLog:
    level_norm = level.upper().strip()
    if level_norm not in {"INFO", "WARN", "ERROR"}:
        level_norm = "INFO"

    at = datetime.now(tz=timezone.utc)
    row = EventLog(at=at, level=level_norm, message=message)
    db.add(row)
    db.commit()
    db.refresh(row)

    # Also append to plain text file for tailing.
    try:
        SETTINGS.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = SETTINGS.log_dir / "events.log"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"{at.isoformat()} [{level_norm}] {message}\n")
    except Exception:
        # If the filesystem is unhappy, DB still has it.
        pass

    return row

