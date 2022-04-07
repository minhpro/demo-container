FROM kong:1.1.2

RUN set -x && \
 apk update && \
 apk upgrade && \
 apk add --no-cache --virtual build-dependencies build-base git && \
 apk add --no-cache luarocks postgresql-dev pgbouncer lua-cjson && \
 luarocks install pgmoon && \
 luarocks install lua-resty-redis && \
 luarocks install lua-resty-redis-connector && \
 apk del --purge build-dependencies

ENV TZ=Asia/Tokyo \
 KONG_SSL=off \
 KONG_DATABASE=postgres \
 KONG_PG_HOST=localhost \
 KONG_PG_PORT=6432 \
 KONG_PG_USER=kong \
 KONG_PG_PASSWORD=kong \
 KONG_PG_DATABASE=kong \
 DB_HOST=postgresql \
 KONG_HEADERS=off

COPY custom_nginx_template /usr/local/kong/
RUN mkdir -m 755 -p /usr/local/kong/logs \
 && ln -s /proc/1/fd/1 /usr/local/kong/logs/access.log \
 && ln -s /proc/1/fd/2 /usr/local/kong/logs/error.log \
 && ln -s /proc/1/fd/1 /usr/local/kong/logs/admin_access.log
COPY kong.conf /etc/kong/

COPY ./files/docker-entrypoint.sh /
COPY ./files/start.sh /
COPY ./files/setting_pgbouncer.sh /
COPY ./files/healthcheck.sh /

STOPSIGNAL SIGQUIT
