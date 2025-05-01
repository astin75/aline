# PostgreSQL 15 버전 사용
FROM postgres:15

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

# PostgreSQL 설정
ENV POSTGRES_DB=aline_db
ENV POSTGRES_USER=aline_user
ENV POSTGRES_PASSWORD=aline_password

# PostgreSQL 설정 파일 복사 (필요한 경우)
# COPY ./postgresql.conf /etc/postgresql/postgresql.conf

# 데이터베이스 초기화 스크립트를 위한 디렉토리
WORKDIR /docker-entrypoint-initdb.d

# 포트 설정
EXPOSE 5432

# 헬스체크를 위한 설정
HEALTHCHECK --interval=30s --timeout=3s \
    CMD pg_isready -U aline_user -d aline_db || exit 1


# docker run -d \
#     --name aline-db \
#     -p 5432:5432 \
#     -v postgres_data:/var/lib/postgresql/data \
#     -v ./database/init:/docker-entrypoint-initdb.d \
#     aline-postgres