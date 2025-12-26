from __future__ import annotations

import sys
import asyncio
from datetime import timedelta
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Allow running as a script via /opt/blackfong/core/main.py (systemd ExecStart)
# by ensuring the package root (/opt/blackfong) is on sys.path.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.api import (
    routes_commands,
    routes_logs,
    routes_nodes,
    routes_services,
    routes_system,
)
from core.config import SETTINGS
from core.db.migrate import migrate
from core.security import require_token
from core.system.backups import ensure_daily_sqlite_backup
from core.system.health import classify_system_state, node_is_stale
from core.system.metrics import system_pulse
from core.db.database import SessionLocal
from core.db.models import EventLog, Node
from sqlalchemy import select


def _format_uptime(seconds: int) -> str:
    td = timedelta(seconds=max(0, int(seconds)))
    days = td.days
    hours, rem = divmod(td.seconds, 3600)
    minutes, sec = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def create_app() -> FastAPI:
    migrate()

    # Token check once per request (if configured).
    app = FastAPI(title="Blackfong Control Core", dependencies=[Depends(require_token)])
    app.include_router(routes_system.router)
    app.include_router(routes_services.router)
    app.include_router(routes_nodes.router)
    app.include_router(routes_commands.router)
    app.include_router(routes_logs.router)

    static_dir = Path(__file__).parent / "ui" / "static"
    templates_dir = Path(__file__).parent / "ui" / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.on_event("startup")
    async def _startup_tasks() -> None:
        # Quiet insurance: make one backup per day, rotate last N.
        ensure_daily_sqlite_backup()

        async def _backup_loop() -> None:
            while True:
                try:
                    ensure_daily_sqlite_backup()
                except Exception:
                    pass
                await asyncio.sleep(3600)

        asyncio.create_task(_backup_loop())

    @app.get("/", response_class=HTMLResponse)
    def ui_index(request: Request):
        pulse = system_pulse()
        now = None
        alive = 0
        stale = 0
        last_events: list[EventLog] = []
        recent_critical = 0
        with SessionLocal() as db:
            nodes = list(db.execute(select(Node)).scalars().all())
            for n in nodes:
                if node_is_stale(n.last_seen, now=now):
                    stale += 1
                else:
                    alive += 1

            last_events = list(
                db.execute(select(EventLog).order_by(EventLog.at.desc()).limit(5))
                .scalars()
                .all()
            )
            recent_critical = sum(1 for e in last_events if (e.severity or "").lower() == "critical")

        state, reasons = classify_system_state(
            pulse, stale_nodes=stale, recent_critical_events=recent_critical
        )
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "pulse": pulse,
                "uptime_human": _format_uptime(pulse["uptime_seconds"]),
                "state": state,
                "state_reasons": reasons,
                "nodes_alive": alive,
                "nodes_stale": stale,
                "last_events": last_events,
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "core.main:app",
        host=SETTINGS.api_host,
        port=SETTINGS.api_port,
        log_level="info",
    )

