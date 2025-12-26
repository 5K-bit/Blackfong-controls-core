from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.config import SETTINGS


def _today_stamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def ensure_daily_sqlite_backup() -> Path | None:
    """
    Create one backup per UTC day, keep last N (rotating).
    """
    src = SETTINGS.db_path
    if not src.exists():
        return None

    SETTINGS.backup_dir.mkdir(parents=True, exist_ok=True)
    dst = SETTINGS.backup_dir / f"blackfong-{_today_stamp()}.db"
    if not dst.exists():
        # Use SQLite online backup for consistency.
        src_conn = sqlite3.connect(str(src))
        try:
            dst_conn = sqlite3.connect(str(dst))
            try:
                src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
        finally:
            src_conn.close()
    rotate_backups()
    return dst


def rotate_backups() -> None:
    keep = max(1, int(SETTINGS.backup_keep_days))
    if not SETTINGS.backup_dir.exists():
        return
    backups = sorted(
        SETTINGS.backup_dir.glob("blackfong-*.db"),
        key=lambda p: p.name,
        reverse=True,
    )
    for p in backups[keep:]:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass

