from __future__ import annotations

from fastapi import APIRouter, Depends

from core.security import require_token
from core.system.metrics import system_pulse


router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/pulse", dependencies=[Depends(require_token)])
def get_pulse() -> dict:
    return system_pulse()

