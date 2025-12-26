from __future__ import annotations

from sqlalchemy import inspect, text

from core.db.database import ENGINE
from core.db.models import Base


def _has_column(table: str, column: str) -> bool:
    insp = inspect(ENGINE)
    try:
        cols = insp.get_columns(table)
    except Exception:
        return False
    return any(c.get("name") == column for c in cols)


def _add_column(table: str, ddl: str) -> None:
    # SQLite supports: ALTER TABLE <t> ADD COLUMN <coldef>
    with ENGINE.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))


def migrate() -> None:
    # SQLite: simple "create if missing" is good enough for phase 1.
    Base.metadata.create_all(bind=ENGINE)

    # Phase 2: lightweight additive migrations (ALTER TABLE ADD COLUMN).
    # event_log: event_type/source/severity
    if not _has_column("event_log", "event_type"):
        _add_column("event_log", "event_type VARCHAR(64) NOT NULL DEFAULT 'event'")
    if not _has_column("event_log", "source"):
        _add_column("event_log", "source VARCHAR(16) NOT NULL DEFAULT 'system'")
    if not _has_column("event_log", "severity"):
        _add_column("event_log", "severity VARCHAR(16) NOT NULL DEFAULT 'info'")

    # nodes: trust + heartbeat payload
    for col, ddl in [
        ("public_key", "public_key TEXT"),
        ("capabilities", "capabilities TEXT"),
        ("last_command", "last_command TEXT"),
        ("version", "version VARCHAR(64)"),
        ("load", "load VARCHAR(64)"),
        ("status_flags", "status_flags TEXT"),
    ]:
        if not _has_column("nodes", col):
            _add_column("nodes", ddl)

    # command_runs: ledger identity
    if not _has_column("command_runs", "requested_by"):
        _add_column("command_runs", "requested_by VARCHAR(64)")

