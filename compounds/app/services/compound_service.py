from ..repositories import compound_repository
from ..schemas.compound import CompoundCreate, CompoundDetail, CompoundPatch


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
