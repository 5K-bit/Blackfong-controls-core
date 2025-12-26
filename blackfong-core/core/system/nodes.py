from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.db.models import Node


def upsert_node(db: Session, name: str, ip: str) -> Node:
    now = datetime.now(tz=timezone.utc)
    existing = db.execute(select(Node).where(Node.name == name)).scalar_one_or_none()
    if existing is None:
        node = Node(name=name, ip=ip, last_seen=now)
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    existing.ip = ip
    existing.last_seen = now
    db.commit()
    db.refresh(existing)
    return existing


def heartbeat(db: Session, node_id: int) -> Node | None:
    node = db.get(Node, node_id)
    if node is None:
        return None
    node.last_seen = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(node)
    return node


def list_nodes(db: Session, limit: int = 200) -> list[Node]:
    q = select(Node).order_by(Node.last_seen.desc()).limit(limit)
    return list(db.execute(q).scalars().all())

