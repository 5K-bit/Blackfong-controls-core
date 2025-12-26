from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.security import require_token
from core.system.commands import list_allowed, list_runs, run_command
from core.system.events import log_event


router = APIRouter(prefix="/api/commands", tags=["commands"])


class CommandRunOut(BaseModel):
    id: int
    name: str
    requested_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    status: str
    return_code: int | None
    stdout: str | None
    stderr: str | None


@router.get("/allowed", dependencies=[Depends(require_token)])
def get_allowed() -> dict:
    return {"allowed": list_allowed()}


@router.post("/{name}/run", response_model=CommandRunOut, dependencies=[Depends(require_token)])
def post_run(name: str, db: Session = Depends(get_db)):
    run = run_command(db, name=name)
    if run.status == "DENIED":
        log_event(db, "WARN", f"command denied: {name}")
    else:
        level = "INFO" if run.status == "OK" else "WARN"
        log_event(db, level, f"command {run.status}: {name} (rc={run.return_code})")
    return run


@router.get("/runs", response_model=list[CommandRunOut], dependencies=[Depends(require_token)])
def get_runs(limit: int = 100, db: Session = Depends(get_db)):
    return list_runs(db, limit=limit)

