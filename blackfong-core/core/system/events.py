from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.config import SETTINGS
from core.db.models import EventLog


def log_event(
    db: Session,
    message: str,
    *,
    event_type: str = "event",
    source: str = "system",
    severity: str = "info",
) -> EventLog:
    source_norm = source.strip().lower()
    if source_norm not in {"api", "system", "node"}:
        source_norm = "system"

    severity_norm = severity.strip().lower()
    if severity_norm not in {"info", "warn", "critical"}:
        severity_norm = "info"

    level_map = {"info": "INFO", "warn": "WARN", "critical": "ERROR"}
    level_norm = level_map.get(severity_norm, "INFO")

    at = datetime.now(tz=timezone.utc)
    row = EventLog(
        at=at,
        level=level_norm,
        event_type=event_type.strip()[:64] if event_type else "event",
        source=source_norm,
        severity=severity_norm,
        message=message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    # Also append to plain text file for tailing.
    try:
        SETTINGS.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = SETTINGS.log_dir / "events.log"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(
                f"{at.isoformat()} [{severity_norm.upper()}] ({source_norm}/{row.event_type}) {message}\n"
            )
    except Exception:
        # If the filesystem is unhappy, DB still has it.
        pass

    return row

