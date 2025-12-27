from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.models import Node


def _to_text(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, sort_keys=True)
    except Exception:
        return str(value)


def upsert_node(
    db: Session,
    *,
    name: str,
    ip: str,
    public_key: str | None = None,
    capabilities=None,
) -> Node:
    now = datetime.now(tz=timezone.utc)
    existing = db.execute(select(Node).where(Node.name == name)).scalar_one_or_none()
    if existing is None:
        node = Node(name=name, ip=ip, last_seen=now)
        node.public_key = public_key
        node.capabilities = _to_text(capabilities)
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    existing.ip = ip
    existing.last_seen = now
    if public_key is not None:
        existing.public_key = public_key
    if capabilities is not None:
        existing.capabilities = _to_text(capabilities)
    db.commit()
    db.refresh(existing)
    return existing


def heartbeat(db: Session, *, node_id: int, version: str | None, load: str | None, status_flags=None) -> Node | None:
    node = db.get(Node, node_id)
    if node is None:
        return None
    node.last_seen = datetime.now(tz=timezone.utc)
    if version is not None:
        node.version = version
    if load is not None:
        node.load = load
    if status_flags is not None:
        node.status_flags = _to_text(status_flags)
    db.commit()
    db.refresh(node)
    return node


def list_nodes(db: Session, limit: int = 200) -> list[Node]:
    q = select(Node).order_by(Node.last_seen.desc()).limit(limit)
    return list(db.execute(q).scalars().all())

