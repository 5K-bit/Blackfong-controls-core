from __future__ import annotations

from datetime import datetime, timezone

from core.config import SETTINGS


def classify_system_state(pulse: dict, *, stale_nodes: int, recent_critical_events: int) -> tuple[str, list[str]]:
    """
    Return (STABLE|DEGRADED|CRITICAL, reasons[]).
    """
    reasons: list[str] = []

    cpu = float(pulse.get("cpu_percent") or 0.0)
    mem = float(pulse.get("memory_percent") or 0.0)
    disk = float(pulse.get("disk_percent") or 0.0)
    temp = pulse.get("temp_c")
    temp_f = float(temp) if temp is not None else None

    degraded = False
    critical = False

    def bump(kind: str, msg: str) -> None:
        nonlocal degraded, critical
        if kind == "critical":
            critical = True
        elif kind == "degraded":
            degraded = True
        reasons.append(msg)

    if cpu >= 95:
        bump("critical", f"CPU {cpu:.0f}%")
    elif cpu >= 85:
        bump("degraded", f"CPU {cpu:.0f}%")

    if mem >= 95:
        bump("critical", f"RAM {mem:.0f}%")
    elif mem >= 85:
        bump("degraded", f"RAM {mem:.0f}%")

    if disk >= 95:
        bump("critical", f"Disk {disk:.0f}%")
    elif disk >= 85:
        bump("degraded", f"Disk {disk:.0f}%")

    if temp_f is not None:
        if temp_f >= 85:
            bump("critical", f"Temp {temp_f:.0f}C")
        elif temp_f >= 75:
            bump("degraded", f"Temp {temp_f:.0f}C")

    if stale_nodes > 0:
        bump("degraded", f"{stale_nodes} stale node(s) (> {SETTINGS.node_stale_seconds}s)")

    if recent_critical_events > 0:
        bump("critical", f"{recent_critical_events} critical event(s) (recent)")

    if critical:
        return "CRITICAL", reasons
    if degraded:
        return "DEGRADED", reasons
    return "STABLE", reasons


def node_is_stale(last_seen, *, now=None) -> bool:
    if now is None:
        now = datetime.now(tz=timezone.utc)
    try:
        age = (now - last_seen).total_seconds()
    except Exception:
        return True
    return age > SETTINGS.node_stale_seconds

