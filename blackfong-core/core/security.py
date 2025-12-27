from __future__ import annotations

import hashlib

from fastapi import Header, HTTPException, Request, status

from core.config import SETTINGS


def require_token(request: Request, x_blackfong_token: str | None = Header(default=None)) -> str:
    """
    Optional auth: if BLACKFONG_TOKEN is set, require it in X-Blackfong-Token.
    """
    if SETTINGS.token is None:
        ident = "local"
        request.state.requester = ident
        return ident
    if x_blackfong_token != SETTINGS.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing/invalid token",
        )
    # Minimal identity for ledger/audit (no users/sessions).
    ident = hashlib.sha256(x_blackfong_token.encode("utf-8")).hexdigest()[:12]
    request.state.requester = ident
    return ident

