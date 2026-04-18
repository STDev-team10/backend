from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import current_user
from ..schemas.compound import (
    CompoundCreate,
    CompoundDetail,
    CompoundListResponse,
    CompoundUnlockListResponse,
    CompoundUnlockResponse,
    CompoundPatch,
    CompoundSeedResponse,
)
from ..services import compound_service

router = APIRouter(prefix="/api/compounds", tags=["compounds"])


@router.get("", response_model=CompoundListResponse)
def list_compounds(difficulty: str | None = Query(default=None)) -> CompoundListResponse:
    compounds = compound_service.list_compounds(difficulty=difficulty)
    return CompoundListResponse(items=compounds, total=len(compounds))


@router.get("/{compound_id}", response_model=CompoundDetail)
def get_compound(compound_id: str) -> CompoundDetail:
    compound = compound_service.get_compound(compound_id)
    if not compound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="compound not found")
    return compound


@router.post("/bulk", response_model=CompoundSeedResponse, status_code=status.HTTP_201_CREATED)
def bulk_upsert_compounds(items: list[CompoundCreate]) -> CompoundSeedResponse:
    count = compound_service.bulk_upsert_compounds(items)
    return CompoundSeedResponse(imported=count)


@router.post("", response_model=CompoundDetail, status_code=status.HTTP_201_CREATED)
def create_compound(body: CompoundCreate) -> CompoundDetail:
    created = compound_service.create_compound(body)
    return created


@router.patch("/{compound_id}", response_model=CompoundDetail)
def update_compound(compound_id: str, body: CompoundPatch) -> CompoundDetail:
    updated = compound_service.update_compound(compound_id, body)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="compound not found")
    return updated


@router.get("/unlocks/me", response_model=CompoundUnlockListResponse)
def list_my_unlocked_compounds(user: dict = Depends(current_user)) -> CompoundUnlockListResponse:
    user_id = int(user["sub"])
    items = compound_service.list_unlocked_compound_ids(user_id)
    return CompoundUnlockListResponse(items=items, total=len(items))


@router.post("/{compound_id}/unlock", response_model=CompoundUnlockResponse)
def unlock_compound(compound_id: str, user: dict = Depends(current_user)) -> CompoundUnlockResponse:
    unlocked = compound_service.unlock_compound_for_user(int(user["sub"]), compound_id)
    if unlocked is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="compound not found")
    return CompoundUnlockResponse(compound_id=compound_id, unlocked=unlocked)
