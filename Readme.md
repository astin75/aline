# Aline 프로젝트

## 도커 컴포즈로 실행하기

### 사전 요구사항
- Docker 및 Docker Compose가 설치되어 있어야 합니다.
- 윈도우의 경우 Docker Desktop을 설치하세요.
- 리눅스의 경우 Docker Engine과 Docker Compose를 설치하세요.
- macOS의 경우 Docker Desktop을 설치하세요.

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
   
   `-d` 옵션은 백그라운드에서 컨테이너를 실행합니다.

3. **서비스 확인**

   다음 명령으로 실행 중인 컨테이너를 확인할 수 있습니다:
   ```bash
   docker compose ps
   ```

4. **로그 확인**

   모든 서비스의 로그를 확인하려면:
   ```bash
   docker-compose logs -f
   ```
   
   특정 서비스의 로그만 확인하려면 (예: API):
   ```bash
   docker-compose logs -f api
   ```

5. **서비스 중지**

   실행 중인 서비스를 중지하려면:
   ```bash
   docker-compose down
   ```

### 접속 정보

- **웹 서비스**: http://localhost
- **API 문서**: http://localhost/docs
- **데이터베이스**:
  - 호스트: localhost
  - 포트: 5432
  - 사용자: aline_user
  - 비밀번호: aline_password
  - 데이터베이스: aline_db

### 문제 해결

1. **포트 충돌**

   80, 443 또는 5432 포트가 이미 사용 중인 경우, `docker-compose.yaml` 파일에서 포트 매핑을 변경하세요.

2. **컨테이너 재시작**

   특정 서비스만 재시작하려면:
   ```bash
   docker-compose restart [서비스명]
   ```

3. **볼륨 및 데이터 초기화**

   모든 데이터와 볼륨을 삭제하려면:
   ```bash
   docker-compose down -v
   ```
