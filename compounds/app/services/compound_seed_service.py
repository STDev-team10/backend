import json
import os
from pathlib import Path

from ..repositories.compound_repository import count_compounds, upsert_compounds


def _seed_path_candidates() -> list[Path]:
    configured = os.getenv("COMPOUND_SEED_PATH")
    paths: list[Path] = []
    if configured:
        paths.append(Path(configured))

    current_dir = Path(__file__).resolve().parents[2]
    paths.append(current_dir / "compoundGameList.ts")
    paths.append(current_dir.parent / "compoundGameList.ts")
    return paths


def _load_compounds_from_seed_file(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8")
    prefix = "export const compoundGameList ="
    if prefix not in content:
        raise ValueError("compoundGameList export not found")

    raw_blob = content.split(prefix, 1)[1].strip()
    start = raw_blob.find("[")
    if start == -1:
        raise ValueError("compoundGameList array start not found")

    depth = 0
    end = -1
    for index, char in enumerate(raw_blob[start:], start=start):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                end = index
                break

    if end == -1:
        raise ValueError("compoundGameList array end not found")

    json_blob = raw_blob[start:end + 1]
    return json.loads(json_blob)


def seed_compounds_if_needed() -> int:
    for candidate in _seed_path_candidates():
        if candidate.exists():
            compounds = _load_compounds_from_seed_file(candidate)
            return upsert_compounds(compounds)

    if count_compounds() > 0:
        return 0

    raise FileNotFoundError("compoundGameList.ts not found for compounds seed")
