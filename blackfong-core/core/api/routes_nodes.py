from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.security import require_token
from core.system.events import log_event
from core.system.nodes import heartbeat, list_nodes, upsert_node


router = APIRouter(prefix="/api/nodes", tags=["nodes"])


class NodeRegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    ip: str | None = Field(default=None, max_length=64)


class NodeOut(BaseModel):
    id: int
    name: str
    ip: str
    last_seen: datetime


@router.post("/register", response_model=NodeOut, dependencies=[Depends(require_token)])
def post_register(payload: NodeRegisterIn, request: Request, db: Session = Depends(get_db)):
    ip = payload.ip or (request.client.host if request.client else "unknown")
    node = upsert_node(db, name=payload.name, ip=ip)
    log_event(db, "INFO", f"node register: {node.name} ({node.ip})")
    return node


@router.post("/{node_id}/heartbeat", response_model=NodeOut, dependencies=[Depends(require_token)])
def post_heartbeat(node_id: int, db: Session = Depends(get_db)):
    node = heartbeat(db, node_id=node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    log_event(db, "INFO", f"node heartbeat: {node.name} ({node.ip})")
    return node


@router.get("", response_model=list[NodeOut], dependencies=[Depends(require_token)])
def get_nodes(limit: int = 200, db: Session = Depends(get_db)):
    return list_nodes(db, limit=limit)

