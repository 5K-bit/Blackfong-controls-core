from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.db.models import EventLog


router = APIRouter(prefix="/api/logs", tags=["logs"])


class EventOut(BaseModel):
    id: int
    at: datetime
    level: str
    event_type: str
    source: str
    severity: str
    message: str


@router.get("/events", response_model=list[EventOut])
def get_events(limit: int = 200, db: Session = Depends(get_db)):
    q = select(EventLog).order_by(EventLog.at.desc()).limit(min(1000, max(1, limit)))
    return list(db.execute(q).scalars().all())

