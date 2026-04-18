import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from ..auth import create_token, hash_password, verify_password
from ..database import get_conn
from ..dependencies import current_user, optional_current_user

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
    points: int


class MeResponse(BaseModel):
    user_id: int
    username: str
    points: int


class PointsUpdateBody(BaseModel):
    earned_points: int

    @field_validator("earned_points")
    @classmethod
    def earned_points_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("earned_points must be non-negative")
        return v


class PointsResponse(BaseModel):
    points: int


class PointsRankingEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    points: int


class PointsLeaderboardResponse(BaseModel):
    items: list[PointsRankingEntry]
    total: int
    my_item: PointsRankingEntry | None


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(body: AuthBody) -> TokenResponse:
    hashed = hash_password(body.password)
    try:
        with get_conn() as conn:
            row = conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?) RETURNING id, points",
                (body.username, hashed),
            ).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already taken")

    return TokenResponse(token=create_token(row["id"], body.username), username=body.username, points=int(row["points"]))


@router.post("/login", response_model=TokenResponse)
def login(body: AuthBody) -> TokenResponse:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (body.username,)).fetchone()

    if not row or not verify_password(body.password, row["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return TokenResponse(token=create_token(row["id"], row["username"]), username=row["username"], points=int(row["points"]))


@router.get("/me", response_model=MeResponse)
def me(user: dict = Depends(current_user)) -> MeResponse:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, points FROM users WHERE id = ?",
            (int(user["sub"]),),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

    return MeResponse(user_id=int(row["id"]), username=str(row["username"]), points=int(row["points"]))


@router.post("/points", response_model=PointsResponse)
def add_points(body: PointsUpdateBody, user: dict = Depends(current_user)) -> PointsResponse:
    with get_conn() as conn:
        row = conn.execute(
            """
            UPDATE users
            SET points = points + ?
            WHERE id = ?
            RETURNING points
            """,
            (body.earned_points, int(user["sub"])),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

    return PointsResponse(points=int(row["points"]))


def _list_points_rankings(limit: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            WITH leaderboard AS (
                SELECT
                    id AS user_id,
                    username,
                    points,
                    ROW_NUMBER() OVER (
                        ORDER BY points DESC, created_at ASC, id ASC
                    ) AS rank
                FROM users
            )
            SELECT rank, user_id, username, points
            FROM leaderboard
            ORDER BY rank
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def _get_my_points_ranking(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            WITH leaderboard AS (
                SELECT
                    id AS user_id,
                    username,
                    points,
                    ROW_NUMBER() OVER (
                        ORDER BY points DESC, created_at ASC, id ASC
                    ) AS rank
                FROM users
            )
            SELECT rank, user_id, username, points
            FROM leaderboard
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def _count_users() -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    return int(row["count"])


@router.get("/points-rankings", response_model=PointsLeaderboardResponse)
def get_points_rankings(
    limit: int = 5,
    user: dict | None = Depends(optional_current_user),
) -> PointsLeaderboardResponse:
    if limit < 1 or limit > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="limit must be between 1 and 5")

    items = [PointsRankingEntry(**row) for row in _list_points_rankings(limit)]
    my_item = None
    if user is not None:
        row = _get_my_points_ranking(int(user["sub"]))
        my_item = PointsRankingEntry(**row) if row else None

    return PointsLeaderboardResponse(items=items, total=_count_users(), my_item=my_item)
