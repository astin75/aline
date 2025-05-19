# MongoDB 최신 안정 버전 사용
FROM mongo:latest

# 시스템 로케일 설정
ENV LANG ko_KR.utf8
ENV TZ=Asia/Seoul

# 필요한 시스템 패키지 설치
RUN apt-get update \
    && apt-get install -y \
    locales \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    # 한국어 로케일 생성
    && localedef -i ko_KR -c -f UTF-8 -A /usr/share/locale/locale.alias ko_KR.UTF-8

# MongoDB 기본 설정
ENV MONGO_INITDB_ROOT_USERNAME=aline_user
ENV MONGO_INITDB_ROOT_PASSWORD=aline_password
ENV MONGO_INITDB_DATABASE=aline_db

# MongoDB 데이터 디렉토리 생성
RUN mkdir -p /data/db

# 포트 설정
EXPOSE 27017

# 헬스체크를 위한 설정
HEALTHCHECK --interval=30s --timeout=3s \
    CMD mongosh --eval "db.adminCommand('ping')" || exit 1

# docker build -t aline-mongodb ./mongo_db
# docker run -d \
#   --name aline-mongodb-local \
#   -p 27017:27017 \
#   -v mongodb_data:/data/db \
#   -e MONGO_INITDB_ROOT_USERNAME=aline_user \
#   -e MONGO_INITDB_ROOT_PASSWORD=aline_password \
#   -e MONGO_INITDB_DATABASE=aline_db \
#   aline-mongodb