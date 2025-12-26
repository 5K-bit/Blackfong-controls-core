from __future__ import annotations

from fastapi import Header, HTTPException, status

from core.config import SETTINGS


def require_token(x_blackfong_token: str | None = Header(default=None)) -> None:
    """
    Optional auth: if BLACKFONG_TOKEN is set, require it in X-Blackfong-Token.
    """
    if SETTINGS.token is None:
        return
    if x_blackfong_token != SETTINGS.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing/invalid token",
        )

