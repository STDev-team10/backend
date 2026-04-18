from ..repositories import compound_repository
from ..schemas.compound import (
    CompoundCreate,
    CompoundDetail,
    CompoundPatch,
    TimeAttackLeaderboardResponse,
    TimeAttackRankingEntry,
    TimeAttackRecordCreate,
)


def list_compounds(difficulty: str | None = None) -> list[CompoundDetail]:
    return [CompoundDetail(**item) for item in compound_repository.list_compounds(difficulty=difficulty)]


def get_compound(compound_id: str) -> CompoundDetail | None:
    item = compound_repository.get_compound_by_id(compound_id)
    if not item:
        return None
    return CompoundDetail(**item)


def bulk_upsert_compounds(items: list[CompoundCreate]) -> int:
    return compound_repository.upsert_compounds([item.model_dump() for item in items])


def create_compound(body: CompoundCreate) -> CompoundDetail:
    created = compound_repository.create_compound(body.model_dump())
    return CompoundDetail(**created)


def update_compound(compound_id: str, body: CompoundPatch) -> CompoundDetail | None:
    updated = compound_repository.update_compound(
        compound_id,
        body.model_dump(exclude_none=True),
    )
    if not updated:
        return None
    return CompoundDetail(**updated)


def list_unlocked_compound_ids(user_id: int) -> list[str]:
    return compound_repository.list_unlocked_compound_ids(user_id)


def unlock_compound_for_user(user_id: int, compound_id: str) -> bool | None:
    return compound_repository.unlock_compound_for_user(user_id, compound_id)


def create_time_attack_record(user_id: int, username: str, body: TimeAttackRecordCreate) -> tuple[int, int, bool]:
    record_id = compound_repository.create_time_attack_record(
        user_id=user_id,
        username=username,
        play_mode=body.play_mode,
        difficulty=body.difficulty,
        clear_time_ms=body.clear_time_ms,
    )
    personal_best = compound_repository.get_time_attack_personal_best(user_id, body.play_mode, body.difficulty)
    if not personal_best:
        raise ValueError("personal best was not created")
    is_personal_best = int(personal_best["id"]) == record_id
    return record_id, int(personal_best["rank"]), is_personal_best


def list_time_attack_rankings(play_mode: str, difficulty: str, limit: int = 10) -> list[TimeAttackRankingEntry]:
    return [
        TimeAttackRankingEntry(**item)
        for item in compound_repository.list_time_attack_rankings(play_mode, difficulty, limit)
    ]


def get_time_attack_personal_best(user_id: int, play_mode: str, difficulty: str) -> TimeAttackRankingEntry | None:
    item = compound_repository.get_time_attack_personal_best(user_id, play_mode, difficulty)
    if not item:
        return None
    return TimeAttackRankingEntry(**item)


def get_time_attack_leaderboard(
    play_mode: str,
    difficulty: str,
    user_id: int | None = None,
    limit: int = 5,
) -> TimeAttackLeaderboardResponse:
    items = list_time_attack_rankings(play_mode, difficulty, limit)
    my_item = get_time_attack_personal_best(user_id, play_mode, difficulty) if user_id is not None else None
    total = compound_repository.count_time_attack_rankings(play_mode, difficulty)
    return TimeAttackLeaderboardResponse(items=items, total=total, my_item=my_item)
