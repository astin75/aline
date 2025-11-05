# Aline 프로젝트

## 프로젝트 간단 설명
Aline은 라인 메신저 기반 챗봇 서비스로, 사용자가 원하는 시간에 다음과 같은 정보를 자동으로 받아볼 수 있습니다:
	•	최신 뉴스
	•	날씨 정보
	•	지하철 도착 정보
	•	비트코인 시세
사용자는 시간 설정만 해두면, 원하는 정보를 자동으로 받아볼 수 있어 편리한 개인 맞춤 알림 서비스입니다.

## 프로젝트 폴더 구조 및 설명

```
aline/
├── schedule_service/     # 스케줄 실행을 담당하는 서비스
│   └── service.py       # 스케줄러 실행 및 작업 관리
├── api/                 # API 서비스
│   ├── service/        # API 서비스 구현
│   └── router/         # API 라우팅
├── agent_service/       # 각종 에이전트 서비스
│   ├── schedule/       # 스케줄 관련 에이전트
│   ├── user/          # 사용자 관련 에이전트
│   ├── head/          # 헤드 에이전트
│   ├── subway/        # 지하철 정보 에이전트
│   ├── news/          # 뉴스 에이전트
│   └── weather/       # 날씨 정보 에이전트
├── mongo_db/           # MongoDB 데이터베이스 관련
│   ├── service.py     # DB 서비스 구현
│   ├── schema.py      # DB 스키마 정의
│   └── connection.py  # DB 연결 관리
└── common/            # 공통 유틸리티
    ├── utils.py       # 유틸리티 함수
    ├── schemas.py     # 공통 스키마
    └── eval_utils.py  # 평가 관련 유틸리티
```

## 도커 컴포즈로 실행하기

### 프로젝트 구조

### 실행 방법

1. **도커 이미지 빌드**

   프로젝트 루트 디렉토리에서 다음 명령을 실행하여 모든 서비스를 빌드합니다:
   ```bash
   docker compose build
   ```

2. **컨테이너 실행**

   빌드가 완료되면 다음 명령을 실행하여 모든 서비스를 시작합니다:
   ```bash
   docker compose up -d
   ```
### 접속 정보

- **웹 서비스**: http://localhost
- **API 문서**: http://localhost/docs
- **MongoDB**:
  - 호스트: localhost
  - 포트: 27017
