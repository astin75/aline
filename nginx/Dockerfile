FROM nginx:alpine

# 타임존을 Asia/Seoul로 설정
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

# nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]

# docker build -t nginx-image .
# docker run -d -p 80:80 -p 443:443 nginx-image
# docker run --rm -it -p 80:80 -p 443:443 \
#   -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
#   -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
#   nginx-image