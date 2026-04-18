import os

from jose import JWTError, jwt

ALGORITHM = "HS256"


def get_secret_key() -> str:
    return os.getenv("JWT_SECRET", "dev-secret")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    except JWTError:
        return {}
