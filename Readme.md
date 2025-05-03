# FastAPI Application

FastAPI를 사용한 기본 웹 애플리케이션입니다.

## 설치 방법

1. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

서버 실행:
```bash
uvicorn main:app --reload
```

서버가 실행되면 다음 URL에서 API를 확인할 수 있습니다:
- API 문서: http://localhost:8000/docs
- API 기본 엔드포인트: http://localhost:8000
- 헬스 체크: http://localhost:8000/health


###
docker build -t aline-postgres -f database/Dockerfile database/


docker run -d \
    --name aline-db \
    -p 5432:5432 \
    -v postgres_data:/var/lib/postgresql/data \
    -v ./database/init:/docker-entrypoint-initdb.d \
    aline-postgres

