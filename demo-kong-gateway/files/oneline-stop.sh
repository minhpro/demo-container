#!/bin/sh

sleep 3 ; /usr/local/openresty/nginx/sbin/nginx -c /etc/nginx/nginx.conf -s quit ; while pgrep -x nginx ; do sleep 1 ;  done 
