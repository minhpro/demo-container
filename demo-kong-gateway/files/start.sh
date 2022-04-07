#!/bin/sh
set -e

/usr/bin/pgbouncer -u postgres /etc/pgbouncer/pgbouncer.ini &
/usr/local/openresty/nginx/sbin/nginx -c /usr/local/kong/nginx.conf -p /usr/local/kong/

fg%1
