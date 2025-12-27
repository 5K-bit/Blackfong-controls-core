from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import psutil


def _read_cpu_temp_c() -> float | None:
    try:
        temps = psutil.sensors_temperatures(fahrenheit=False)
    except Exception:
        return None
    if not temps:
        return None

    # Prefer common Linux labels if present.
    preferred_keys = ("coretemp", "k10temp", "cpu_thermal", "soc_thermal")
    for key in preferred_keys:
        if key in temps and temps[key]:
            for entry in temps[key]:
                if entry.current is not None:
                    return float(entry.current)

    # Fallback: first available temperature.
    for entries in temps.values():
        for entry in entries:
            if entry.current is not None:
                return float(entry.current)
    return None


def system_pulse() -> dict:
    boot_time = psutil.boot_time()
    now = time.time()
    uptime_seconds = int(max(0, now - boot_time))

    load_1, load_5, load_15 = (None, None, None)
    try:
        load_1, load_5, load_15 = os.getloadavg()
    except OSError:
        pass

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "temp_c": _read_cpu_temp_c(),
        "uptime_seconds": uptime_seconds,
        "boot_time": datetime.fromtimestamp(boot_time, tz=timezone.utc).isoformat(),
        "load_avg": {"1m": load_1, "5m": load_5, "15m": load_15},
    }

