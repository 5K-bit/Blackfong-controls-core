from __future__ import annotations

import subprocess
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.models import CommandRun


ALLOWED_COMMANDS: dict[str, list[str]] = {
    "reboot": ["reboot"],
    "shutdown": ["shutdown", "-h", "now"],
    "update": ["apt", "update"],
}


def list_allowed() -> list[str]:
    return sorted(ALLOWED_COMMANDS.keys())


def run_command(db: Session, name: str) -> CommandRun:
    now = datetime.now(tz=timezone.utc)
    run = CommandRun(
        name=name,
        requested_at=now,
        started_at=None,
        finished_at=None,
        status="QUEUED",
        return_code=None,
        stdout=None,
        stderr=None,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    cmd = ALLOWED_COMMANDS.get(name)
    if not cmd:
        run.status = "DENIED"
        run.finished_at = datetime.now(tz=timezone.utc)
        db.commit()
        db.refresh(run)
        return run

    run.status = "RUNNING"
    run.started_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(run)

    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    run.return_code = p.returncode
    run.stdout = p.stdout
    run.stderr = p.stderr
    run.finished_at = datetime.now(tz=timezone.utc)
    run.status = "OK" if p.returncode == 0 else "FAIL"
    db.commit()
    db.refresh(run)
    return run


def list_runs(db: Session, limit: int = 100) -> list[CommandRun]:
    q = select(CommandRun).order_by(CommandRun.requested_at.desc()).limit(limit)
    return list(db.execute(q).scalars().all())

