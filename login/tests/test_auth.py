import sys
from pathlib import Path

from fastapi.testclient import TestClient

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

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_body['token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "luke"


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
