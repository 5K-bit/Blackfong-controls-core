from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.security import require_token
from core.system.events import log_event
from core.system.services import service_action


router = APIRouter(prefix="/api/services", tags=["services"])


@router.post("/{unit}/{action}", dependencies=[Depends(require_token)])
def post_service_action(unit: str, action: str, db: Session = Depends(get_db)) -> dict:
    try:
        result = service_action(unit=unit, action=action)
    except PermissionError as e:
        log_event(db, "WARN", f"service denied: {unit} {action}")
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    level = "INFO" if result["return_code"] == 0 else "WARN"
    log_event(db, level, f"service {action}: {unit} (rc={result['return_code']})")
    return result

