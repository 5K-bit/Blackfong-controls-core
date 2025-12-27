from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RuntimeState:
    started_at: datetime


STATE = RuntimeState(started_at=datetime.now(tz=timezone.utc))

