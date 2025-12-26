from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.system.commands import list_allowed, list_runs, run_command
from core.system.events import log_event


router = APIRouter(prefix="/api/commands", tags=["commands"])


class CommandRunOut(BaseModel):
    id: int
    name: str
    requested_by: str | None
    requested_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    status: str
    return_code: int | None
    stdout: str | None
    stderr: str | None


@router.get("/allowed")
def get_allowed() -> dict:
    return {"allowed": list_allowed()}


@router.post("/{name}/run", response_model=CommandRunOut)
def post_run(name: str, request: Request, db: Session = Depends(get_db)):
    requester = getattr(request.state, "requester", "unknown")
    run = run_command(db, name=name, requested_by=requester)
    if run.status == "DENIED":
        log_event(
            db,
            f"command denied: {name} by {requester}",
            event_type="command",
            source="api",
            severity="warn",
        )
    else:
        severity = "info" if run.status == "OK" else "warn"
        log_event(
            db,
            f"command {run.status}: {name} (rc={run.return_code}) by {requester}",
            event_type="command",
            source="api",
            severity=severity,
        )
    return run


@router.get("/runs", response_model=list[CommandRunOut])
def get_runs(limit: int = 100, db: Session = Depends(get_db)):
    return list_runs(db, limit=limit)

