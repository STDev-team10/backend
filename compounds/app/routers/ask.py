import os

from fastapi import APIRouter, HTTPException, status
from openai import OpenAI
from pydantic import BaseModel

router = APIRouter(tags=["ask"])


class AskRequest(BaseModel):
    question: str


def _get_client() -> OpenAI:
    token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK")
    if not token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service not configured")
    return OpenAI(
        base_url="https://bedrock-runtime.ap-northeast-2.amazonaws.com/openai/v1",
        api_key=token,
    )


@router.post("/ask")
def ask(req: AskRequest) -> dict:
    client = _get_client()
    response = client.chat.completions.create(
        model="amazon.nova-micro-v1:0",
        messages=[
            {
                "role": "system",
                "content": "너는 화학 학습 앱의 AI 튜터야. 한국어로 2~3문장, 중학생도 이해할 수 있게 짧고 흥미롭게 설명해.",
            },
            {"role": "user", "content": req.question},
        ],
    )
    return {"answer": response.choices[0].message.content}
