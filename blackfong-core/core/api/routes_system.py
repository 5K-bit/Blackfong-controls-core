from __future__ import annotations

from fastapi import APIRouter

from core.config import SETTINGS
from core.system.metrics import system_pulse


router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/pulse")
def get_pulse() -> dict:
    return system_pulse()


@router.get("/config")
def get_config() -> dict:
    # Read-only, redacted.
    return {
        "api": {"host": SETTINGS.api_host, "port": SETTINGS.api_port},
        "paths": {
            "base_dir": str(SETTINGS.base_dir),
            "data_dir": str(SETTINGS.data_dir),
            "db_path": str(SETTINGS.db_path),
            "log_dir": str(SETTINGS.log_dir),
            "backup_dir": str(SETTINGS.backup_dir),
        },
        "security": {
            "token_enabled": SETTINGS.token is not None,
            "allowed_systemd_units": sorted(SETTINGS.allowed_systemd_units),
        },
        "fleet": {"node_stale_seconds": SETTINGS.node_stale_seconds},
        "backups": {"keep_days": SETTINGS.backup_keep_days},
    }

