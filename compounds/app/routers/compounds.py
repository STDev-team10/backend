from fastapi import APIRouter, HTTPException, Query, status

from ..schemas.compound import (
    CompoundCreate,
    CompoundDetail,
    CompoundListResponse,
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
