import sys
from pathlib import Path

from fastapi.testclient import TestClient
from jose import jwt

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def test_signup_login_and_me_flow(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    from main import app
    from app.database import init_db

    init_db()
    client = TestClient(app)

    signup_response = client.post(
        "/api/auth/signup",
        json={"username": "luke", "password": "secret123"},
    )
    assert signup_response.status_code == 201
    signup_body = signup_response.json()
    assert signup_body["username"] == "luke"
    assert signup_body["token"]
    assert signup_body["points"] == 0

    duplicate_response = client.post(
        "/api/auth/signup",
        json={"username": "luke", "password": "secret123"},
    )
    assert duplicate_response.status_code == 409

    login_response = client.post(
        "/api/auth/login",
        json={"username": "luke", "password": "secret123"},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["username"] == "luke"
    assert login_body["token"]
    assert login_body["points"] == 0

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_body['token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "luke"
    assert me_response.json()["points"] == 0


def test_login_rejects_invalid_password(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    from main import app
    from app.database import init_db

    init_db()
    client = TestClient(app)
    client.post("/api/auth/signup", json={"username": "luke", "password": "secret123"})

    response = client.post(
        "/api/auth/login",
        json={"username": "luke", "password": "wrong-pass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid credentials"


def test_add_points_returns_latest_total(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    from main import app
    from app.database import init_db

    init_db()
    client = TestClient(app)

    signup_response = client.post(
        "/api/auth/signup",
        json={"username": "aha", "password": "secret123"},
    )
    token = signup_response.json()["token"]

    first = client.post(
        "/api/auth/points",
        json={"earned_points": 500},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first.status_code == 200
    assert first.json() == {"points": 500}

    second = client.post(
        "/api/auth/points",
        json={"earned_points": 180},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second.status_code == 200
    assert second.json() == {"points": 680}


def test_points_rankings_return_top_five_and_my_rank(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    from main import app
    from app.database import get_conn, init_db

    init_db()
    client = TestClient(app)

    players = [
        ("luke", 120),
        ("maya", 300),
        ("aha", 180),
        ("noah", 250),
        ("zoe", 90),
        ("mina", 200),
    ]

    for username, _ in players:
        response = client.post("/api/auth/signup", json={"username": username, "password": "secret123"})
        assert response.status_code == 201

    with get_conn() as conn:
        for username, points in players:
            conn.execute("UPDATE users SET points = ? WHERE username = ?", (points, username))

    token = jwt.encode({"sub": "3", "username": "aha"}, "test-secret", algorithm="HS256")
    response = client.get(
        "/api/auth/points-rankings?limit=5",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"rank": 1, "user_id": 2, "username": "maya", "points": 300},
            {"rank": 2, "user_id": 4, "username": "noah", "points": 250},
            {"rank": 3, "user_id": 6, "username": "mina", "points": 200},
            {"rank": 4, "user_id": 3, "username": "aha", "points": 180},
            {"rank": 5, "user_id": 1, "username": "luke", "points": 120},
        ],
        "total": 6,
        "my_item": {"rank": 4, "user_id": 3, "username": "aha", "points": 180},
    }
