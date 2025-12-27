from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    public_key: Mapped[str | None] = mapped_column(Text)
    capabilities: Mapped[str | None] = mapped_column(Text)  # JSON/text
    last_command: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str | None] = mapped_column(String(64))
    load: Mapped[str | None] = mapped_column(String(64))
    status_flags: Mapped[str | None] = mapped_column(Text)  # JSON/text


class EventLog(Base):
    __tablename__ = "event_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Back-compat (phase 1)
    level: Mapped[str] = mapped_column(String(16), nullable=False, default="INFO")  # INFO/WARN/ERROR

    # Canonical log fields (filterable/auditable)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, default="event")
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="system")  # api/system/node
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="info")  # info/warn/critical
    message: Mapped[str] = mapped_column(Text, nullable=False)


class CommandRun(Base):
    __tablename__ = "command_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by: Mapped[str | None] = mapped_column(String(64))  # token id later
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # QUEUED/RUNNING/OK/FAIL/DENIED
    return_code: Mapped[int | None] = mapped_column(Integer)
    stdout: Mapped[str | None] = mapped_column(Text)
    stderr: Mapped[str | None] = mapped_column(Text)

