import json
import os

import boto3
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(tags=["ask"])

SYSTEM_PROMPT = "너는 화학 학습 앱의 AI 튜터야. 한국어로 2~3문장, 중학생도 이해할 수 있게 짧고 흥미롭게 설명해."
MODEL_ID = "amazon.nova-micro-v1:0"


class AskRequest(BaseModel):
    question: str


def _get_client():
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not access_key or not secret_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service not configured")
    return boto3.client(
        "bedrock-runtime",
        region_name="ap-northeast-2",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


@router.post("/ask")
def ask(req: AskRequest) -> dict:
    client = _get_client()
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": req.question}]}],
    )
    answer = response["output"]["message"]["content"][0]["text"]
    return {"answer": answer}
