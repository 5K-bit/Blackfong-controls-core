from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return default if v is None or v.strip() == "" else v


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return int(v)


@dataclass(frozen=True)
class Settings:
    # Paths
    base_dir: Path
    data_dir: Path
    db_path: Path
    log_dir: Path
    backup_dir: Path
    backup_keep_days: int

    # Network
    api_host: str
    api_port: int

    # Security
    token: str | None

    # Safety rails
    allowed_systemd_units: set[str]
    node_stale_seconds: int


def load_settings() -> Settings:
    # Deployment target is /opt/blackfong, but default to the repo root when
    # running unprivileged (dev/test).
    default_base = Path("/opt/blackfong")
    repo_base = Path(__file__).resolve().parents[1]

    base_dir_raw = os.getenv("BLACKFONG_BASE_DIR")
    if base_dir_raw is not None and base_dir_raw.strip() != "":
        base_dir = Path(base_dir_raw)
    else:
        base_dir = default_base
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            base_dir = repo_base

    data_dir = Path(_env("BLACKFONG_DATA_DIR", str(base_dir / "data")))
    db_path = Path(_env("BLACKFONG_DB_PATH", str(data_dir / "blackfong.db")))
    log_dir = Path(_env("BLACKFONG_LOG_DIR", str(data_dir / "logs")))
    backup_dir = Path(_env("BLACKFONG_BACKUP_DIR", str(data_dir / "backups")))
    backup_keep_days = _env_int("BLACKFONG_BACKUP_KEEP_DAYS", 7)

    api_host = _env("BLACKFONG_API_HOST", "127.0.0.1")
    api_port = _env_int("BLACKFONG_API_PORT", 7331)

    token_raw = os.getenv("BLACKFONG_TOKEN")
    token = None if token_raw is None or token_raw.strip() == "" else token_raw.strip()

    allowed_units_raw = os.getenv("BLACKFONG_ALLOWED_SYSTEMD_UNITS", "")
    allowed_systemd_units = {
        u.strip() for u in allowed_units_raw.split(",") if u.strip()
    }

    node_stale_seconds = _env_int("BLACKFONG_NODE_STALE_SECONDS", 60)

    return Settings(
        base_dir=base_dir,
        data_dir=data_dir,
        db_path=db_path,
        log_dir=log_dir,
        backup_dir=backup_dir,
        backup_keep_days=backup_keep_days,
        api_host=api_host,
        api_port=api_port,
        token=token,
        allowed_systemd_units=allowed_systemd_units,
        node_stale_seconds=node_stale_seconds,
    )


SETTINGS = load_settings()

