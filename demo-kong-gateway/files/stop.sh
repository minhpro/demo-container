#!/bin/sh

sleep 3

 /usr/local/openresty/nginx/sbin/nginx -c /usr/local/kong/nginx.conf -p /usr/local/kong/ -s quit

while pgrep -x nginx
do
  sleep 1
done
