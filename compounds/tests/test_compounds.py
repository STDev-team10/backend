import sys
from importlib import import_module, reload
from pathlib import Path

from fastapi.testclient import TestClient

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
