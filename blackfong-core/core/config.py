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

    # Network
    api_host: str
    api_port: int

    # Security
    token: str | None

    # Safety rails
    allowed_systemd_units: set[str]


def load_settings() -> Settings:
    base_dir = Path(_env("BLACKFONG_BASE_DIR", "/opt/blackfong"))
    data_dir = Path(_env("BLACKFONG_DATA_DIR", str(base_dir / "data")))
    db_path = Path(_env("BLACKFONG_DB_PATH", str(data_dir / "blackfong.db")))
    log_dir = Path(_env("BLACKFONG_LOG_DIR", str(data_dir / "logs")))

    api_host = _env("BLACKFONG_API_HOST", "127.0.0.1")
    api_port = _env_int("BLACKFONG_API_PORT", 7331)

    token_raw = os.getenv("BLACKFONG_TOKEN")
    token = None if token_raw is None or token_raw.strip() == "" else token_raw.strip()

    allowed_units_raw = os.getenv("BLACKFONG_ALLOWED_SYSTEMD_UNITS", "")
    allowed_systemd_units = {
        u.strip() for u in allowed_units_raw.split(",") if u.strip()
    }

    return Settings(
        base_dir=base_dir,
        data_dir=data_dir,
        db_path=db_path,
        log_dir=log_dir,
        api_host=api_host,
        api_port=api_port,
        token=token,
        allowed_systemd_units=allowed_systemd_units,
    )


SETTINGS = load_settings()

