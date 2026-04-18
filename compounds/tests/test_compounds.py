import sys
from importlib import import_module, reload
from pathlib import Path

from fastapi.testclient import TestClient
from jose import jwt

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _load_app():
    if "main" in sys.modules:
        main_module = reload(sys.modules["main"])
    else:
        main_module = import_module("main")
    return main_module.app


def _write_seed_file(path: Path) -> None:
    path.write_text(
        """export const compoundGameList = [
  {
    "id": "water",
    "name": "물",
    "formula": "H2O",
    "emoji": "💧",
    "description": "seed",
    "difficulty": "easy",
    "elements": {"H": 2, "O": 1},
    "available_elements": ["H", "O", "Na"]
  }
];
""",
        encoding="utf-8",
    )


def test_seed_and_list_compounds(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "compounds.db"
    seed_path = tmp_path / "compoundGameList.ts"
    _write_seed_file(seed_path)

    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMPOUND_SEED_PATH", str(seed_path))

    client = TestClient(_load_app())
    response = client.get("/api/compounds?difficulty=easy")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == "water"


def test_create_and_patch_compound(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "compounds.db"
    seed_path = tmp_path / "compoundGameList.ts"
    _write_seed_file(seed_path)

    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMPOUND_SEED_PATH", str(seed_path))

    client = TestClient(_load_app())

    create_response = client.post(
        "/api/compounds",
        json={
            "id": "salt",
            "name": "소금",
            "formula": "NaCl",
            "emoji": "🧂",
            "description": "created",
            "difficulty": "easy",
            "elements": {"Na": 1, "Cl": 1},
            "available_elements": ["Na", "Cl", "H"],
        },
    )
    assert create_response.status_code == 201

    patch_response = client.patch(
        "/api/compounds/salt",
        json={"difficulty": "medium"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["difficulty"] == "medium"


def test_create_compound_includes_required_elements_in_available_elements(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "compounds.db"
    seed_path = tmp_path / "compoundGameList.ts"
    _write_seed_file(seed_path)

    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMPOUND_SEED_PATH", str(seed_path))

    client = TestClient(_load_app())

    create_response = client.post(
        "/api/compounds",
        json={
            "id": "carbon-dioxide",
            "name": "이산화탄소",
            "formula": "CO2",
            "emoji": "🌫️",
            "description": "created",
            "difficulty": "easy",
            "elements": {"C": 1, "O": 2},
            "available_elements": ["Na", "Cl", "O"],
        },
    )

    assert create_response.status_code == 201
    body = create_response.json()
    assert body["available_elements"] == ["Na", "Cl", "O", "C"]


def test_seeded_compound_response_repairs_missing_required_elements(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "compounds.db"
    seed_path = tmp_path / "compoundGameList.ts"
    seed_path.write_text(
        """export const compoundGameList = [
  {
    "id": "broken-water",
    "name": "고장난 물",
    "formula": "H2O",
    "emoji": "💧",
    "description": "seed",
    "difficulty": "easy",
    "elements": {"H": 2, "O": 1},
    "available_elements": ["Na"]
  }
];
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMPOUND_SEED_PATH", str(seed_path))

    client = TestClient(_load_app())
    response = client.get("/api/compounds?difficulty=easy")

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["available_elements"] == ["Na", "H", "O"]


def test_unlock_compound_for_authenticated_user(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "compounds.db"
    seed_path = tmp_path / "compoundGameList.ts"
    _write_seed_file(seed_path)

    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMPOUND_SEED_PATH", str(seed_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    client = TestClient(_load_app())
    token = jwt.encode({"sub": "7", "username": "luke"}, "test-secret", algorithm="HS256")

    unlock_response = client.post(
        "/api/compounds/water/unlock",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert unlock_response.status_code == 200
    assert unlock_response.json() == {"compound_id": "water", "unlocked": True}

    list_response = client.get(
        "/api/compounds/unlocks/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert list_response.json() == {"items": ["water"], "total": 1}

    repeat_unlock_response = client.post(
        "/api/compounds/water/unlock",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert repeat_unlock_response.status_code == 200
    assert repeat_unlock_response.json() == {"compound_id": "water", "unlocked": False}


def test_time_attack_rankings_keep_best_record_per_user(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "compounds.db"
    seed_path = tmp_path / "compoundGameList.ts"
    _write_seed_file(seed_path)

    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("COMPOUND_SEED_PATH", str(seed_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    client = TestClient(_load_app())
    luke_token = jwt.encode({"sub": "7", "username": "luke"}, "test-secret", algorithm="HS256")
    maya_token = jwt.encode({"sub": "9", "username": "maya"}, "test-secret", algorithm="HS256")

    first = client.post(
        "/api/compounds/time-attack-records",
        json={"play_mode": "normal", "difficulty": "easy", "clear_time_ms": 42000},
        headers={"Authorization": f"Bearer {luke_token}"},
    )
    assert first.status_code == 201
    assert first.json()["rank"] == 1
    assert first.json()["is_personal_best"] is True

    second = client.post(
        "/api/compounds/time-attack-records",
        json={"play_mode": "normal", "difficulty": "easy", "clear_time_ms": 51000},
        headers={"Authorization": f"Bearer {maya_token}"},
    )
    assert second.status_code == 201
    assert second.json()["rank"] == 2

    third = client.post(
        "/api/compounds/time-attack-records",
        json={"play_mode": "normal", "difficulty": "easy", "clear_time_ms": 40000},
        headers={"Authorization": f"Bearer {maya_token}"},
    )
    assert third.status_code == 201
    assert third.json()["rank"] == 1
    assert third.json()["is_personal_best"] is True

    slower_repeat = client.post(
        "/api/compounds/time-attack-records",
        json={"play_mode": "normal", "difficulty": "easy", "clear_time_ms": 53000},
        headers={"Authorization": f"Bearer {luke_token}"},
    )
    assert slower_repeat.status_code == 201
    assert slower_repeat.json()["rank"] == 2
    assert slower_repeat.json()["is_personal_best"] is False

    rankings = client.get(
        "/api/compounds/time-attack-rankings?play_mode=normal&difficulty=easy&limit=5",
        headers={"Authorization": f"Bearer {luke_token}"},
    )
    assert rankings.status_code == 200
    assert rankings.json() == {
        "items": [
            {
                "rank": 1,
                "user_id": 9,
                "username": "maya",
                "play_mode": "normal",
                "difficulty": "easy",
                "clear_time_ms": 40000,
                "cleared_at": rankings.json()["items"][0]["cleared_at"],
            },
            {
                "rank": 2,
                "user_id": 7,
                "username": "luke",
                "play_mode": "normal",
                "difficulty": "easy",
                "clear_time_ms": 42000,
                "cleared_at": rankings.json()["items"][1]["cleared_at"],
            },
        ],
        "total": 2,
        "my_item": {
            "rank": 2,
            "user_id": 7,
            "username": "luke",
            "play_mode": "normal",
            "difficulty": "easy",
            "clear_time_ms": 42000,
            "cleared_at": rankings.json()["my_item"]["cleared_at"],
        },
    }

    personal_best = client.get(
        "/api/compounds/time-attack-rankings/me?play_mode=normal&difficulty=easy",
        headers={"Authorization": f"Bearer {luke_token}"},
    )
    assert personal_best.status_code == 200
    assert personal_best.json() == {
        "item": {
            "rank": 2,
            "user_id": 7,
            "username": "luke",
            "play_mode": "normal",
            "difficulty": "easy",
            "clear_time_ms": 42000,
            "cleared_at": personal_best.json()["item"]["cleared_at"],
        }
    }
