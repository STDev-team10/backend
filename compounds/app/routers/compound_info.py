import os

import boto3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..compound_map import lookup, lookup_by_name_ko

router = APIRouter(prefix="/api/compound", tags=["compound-info"])

SYSTEM_PROMPT = "너는 화학 학습 앱의 AI 튜터야. 한국어로 2~4문장, 중학생도 이해할 수 있게 짧고 흥미롭게 설명해."
MODEL_ID = "apac.amazon.nova-micro-v1:0"


class CompoundRequest(BaseModel):
    id: str | None = None
    name_ko: str | None = None


class ExplainRequest(BaseModel):
    id: str | None = None
    name_ko: str | None = None
    question: str | None = None


def _resolve(id: str | None, name_ko: str | None):
    meta = None
    if id:
        meta = lookup(id)
    if meta is None and name_ko:
        meta = lookup_by_name_ko(name_ko)
    return meta


def _bedrock_client():
    key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not key or not secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service not configured")
    return boto3.client(
        "bedrock-runtime",
        region_name="ap-northeast-2",
        aws_access_key_id=key,
        aws_secret_access_key=secret,
    )


@router.post("/3d")
def get_3d_info(req: CompoundRequest) -> dict:
    meta = _resolve(req.id, req.name_ko)
    if not meta:
        return {
            "nameKo": req.name_ko or req.id or "알 수 없음",
            "nameEn": None,
            "formula": None,
            "pubchemCid": None,
            "has3d": False,
        }
    return {
        "nameKo": meta["name_ko"],
        "nameEn": meta["name_en"],
        "formula": meta["formula"],
        "pubchemCid": meta["pubchem_cid"],
        "has3d": meta["has_3d"],
    }


@router.post("/explain")
def explain_compound(req: ExplainRequest) -> dict:
    meta = _resolve(req.id, req.name_ko)

    if req.question:
        prompt = req.question
    elif meta:
        prompt = f"{meta['name_ko']}({meta['formula']})에 대해 설명해줘."
    else:
        name = req.name_ko or req.id or "이 화학물질"
        prompt = f"{name}에 대해 설명해줘."

    client = _bedrock_client()
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    answer = response["output"]["message"]["content"][0]["text"]
    return {"answer": answer}
