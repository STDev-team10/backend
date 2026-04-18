import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from ..auth import create_token, hash_password, verify_password
from ..database import get_conn
from ..dependencies import current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthBody(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_length(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("username must be at least 2 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("password must be at least 4 characters")
        return v


class TokenResponse(BaseModel):
    token: str
    username: str


class MeResponse(BaseModel):
    user_id: int
    username: str


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(body: AuthBody) -> TokenResponse:
    hashed = hash_password(body.password)
    try:
        with get_conn() as conn:
            row = conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?) RETURNING id",
                (body.username, hashed),
            ).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already taken")

    return TokenResponse(token=create_token(row["id"], body.username), username=body.username)


@router.post("/login", response_model=TokenResponse)
def login(body: AuthBody) -> TokenResponse:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (body.username,)).fetchone()

    if not row or not verify_password(body.password, row["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return TokenResponse(token=create_token(row["id"], row["username"]), username=row["username"])


@router.get("/me", response_model=MeResponse)
def me(user: dict = Depends(current_user)) -> MeResponse:
    return MeResponse(user_id=int(user["sub"]), username=user["username"])
