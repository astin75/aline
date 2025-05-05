FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 및 uv 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# 전체 프로젝트 파일 복사
COPY . .

# uv로 가상환경 생성 및 의존성 설치
RUN uv venv .venv --python=3.12 && \
    . .venv/bin/activate && \
    uv sync
