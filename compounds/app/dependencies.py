from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import decode_token

bearer = HTTPBearer(auto_error=False)


def optional_current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict | None:
    if not creds:
        return None

    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return payload


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")

    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return payload
