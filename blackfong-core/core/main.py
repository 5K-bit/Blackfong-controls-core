from __future__ import annotations

import sys
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
from core.system.metrics import system_pulse


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

    app = FastAPI(title="Blackfong Control Core")
    app.include_router(routes_system.router)
    app.include_router(routes_services.router)
    app.include_router(routes_nodes.router)
    app.include_router(routes_commands.router)
    app.include_router(routes_logs.router)

    static_dir = Path(__file__).parent / "ui" / "static"
    templates_dir = Path(__file__).parent / "ui" / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def ui_index(request: Request, _: None = Depends(require_token)):
        pulse = system_pulse()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "pulse": pulse,
                "uptime_human": _format_uptime(pulse["uptime_seconds"]),
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

