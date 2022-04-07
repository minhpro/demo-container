#!/bin/sh
set -e

# pgbouncer.iniの設定
## pgbouncer.iniにパラメータを追加したい場合は、以下のURLを参考にしてください
## https://pgbouncer.github.io/config.html

cat << PGBOUNCER > /etc/pgbouncer/pgbouncer.ini
[databases]
kong = host=${DB_HOST:-postgresql}\
 pool_size=${KONG_DB_POOL_SIZE:-15}\
 max_db_connections=${KONG_DB_MAX_CONNECTIONS:-100}

[pgbouncer]
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid

listen_addr = 127.0.0.1
listen_port = 6432

auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

ignore_startup_parameters = extra_float_digits

pool_mode = transaction

query_wait_timeout=60
max_client_conn=${MAX_CLIENT_CONNECTIONS:-1000}
PGBOUNCER


# userlist.txtの設定
MD5_KONG_PG_PASSWORD=`echo -n "${KONG_PG_PASSWORD}kong" | md5sum | cut -f 1 -d ' '`

cat << USERLIST > /etc/pgbouncer/userlist.txt
"kong" "md5${MD5_KONG_PG_PASSWORD}"
USERLIST

mkdir -p /var/run/pgbouncer /var/log/pgbouncer
chown -R postgres:postgres /var/run/pgbouncer /var/log/pgbouncer