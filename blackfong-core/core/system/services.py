from __future__ import annotations

import subprocess

from core.config import SETTINGS


def service_action(unit: str, action: str) -> dict:
    if action not in ("start", "stop", "restart", "status"):
        raise ValueError("Invalid action")

    if SETTINGS.allowed_systemd_units and unit not in SETTINGS.allowed_systemd_units:
        raise PermissionError("Unit not allowed")

    cmd = ["systemctl", action, unit]
    if action == "status":
        cmd = ["systemctl", "status", "--no-pager", unit]

    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "unit": unit,
        "action": action,
        "return_code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }

