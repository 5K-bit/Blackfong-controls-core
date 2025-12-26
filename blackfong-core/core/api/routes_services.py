from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.system.events import log_event
from core.system.services import service_action


router = APIRouter(prefix="/api/services", tags=["services"])


@router.post("/{unit}/{action}")
def post_service_action(
    unit: str,
    action: str,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    requester = getattr(request.state, "requester", "unknown")
    try:
        result = service_action(unit=unit, action=action)
    except PermissionError as e:
        log_event(
            db,
            f"service denied: {unit} {action}",
            event_type="service",
            source="api",
            severity="warn",
        )
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    severity = "info" if result["return_code"] == 0 else "warn"
    log_event(
        db,
        f"service {action}: {unit} (rc={result['return_code']}) by {requester}",
        event_type="service",
        source="api",
        severity=severity,
    )
    return result

