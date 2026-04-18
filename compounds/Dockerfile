FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY compounds/pyproject.toml ./pyproject.toml

RUN pip install --upgrade pip && \
    pip install .

COPY compounds/app ./app
COPY compounds/main.py ./main.py
COPY compoundGameList.ts ./compoundGameList.ts

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
