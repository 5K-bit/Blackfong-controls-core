from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.system.events import log_event
from core.system.nodes import heartbeat, list_nodes, upsert_node


router = APIRouter(prefix="/api/nodes", tags=["nodes"])


class NodeRegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    ip: str | None = Field(default=None, max_length=64)
    public_key: str | None = None
    capabilities: dict | list | str | None = None


class NodeOut(BaseModel):
    id: int
    name: str
    ip: str
    last_seen: datetime
    public_key: str | None = None
    capabilities: str | None = None
    last_command: str | None = None
    version: str | None = None
    load: str | None = None
    status_flags: str | None = None


class HeartbeatIn(BaseModel):
    version: str | None = Field(default=None, max_length=64)
    load: str | None = Field(default=None, max_length=64)
    status_flags: dict | list | str | None = None


@router.post("/register", response_model=NodeOut)
def post_register(
    payload: NodeRegisterIn,
    request: Request,
    db: Session = Depends(get_db),
):
    requester = getattr(request.state, "requester", "unknown")
    ip = payload.ip or (request.client.host if request.client else "unknown")
    node = upsert_node(
        db,
        name=payload.name,
        ip=ip,
        public_key=payload.public_key,
        capabilities=payload.capabilities,
    )
    log_event(
        db,
        f"node register: {node.name} ({node.ip}) by {requester}",
        event_type="node.register",
        source="node",
        severity="info",
    )
    return node


@router.post("/{node_id}/heartbeat", response_model=NodeOut)
def post_heartbeat(
    node_id: int,
    payload: HeartbeatIn,
    request: Request,
    db: Session = Depends(get_db),
):
    requester = getattr(request.state, "requester", "unknown")
    node = heartbeat(
        db,
        node_id=node_id,
        version=payload.version,
        load=payload.load,
        status_flags=payload.status_flags,
    )
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    log_event(
        db,
        f"node heartbeat: {node.name} ({node.ip}) by {requester}",
        event_type="node.heartbeat",
        source="node",
        severity="info",
    )
    return node


@router.get("", response_model=list[NodeOut])
def get_nodes(limit: int = 200, db: Session = Depends(get_db)):
    return list_nodes(db, limit=limit)

