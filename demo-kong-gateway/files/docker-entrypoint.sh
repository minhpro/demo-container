#!/bin/sh
set -e

# Disabling nginx daemon mode
export KONG_NGINX_DAEMON="off"

if [[ "$1" == "kong" ]]; then
  PREFIX=${KONG_PREFIX:=/usr/local/kong}
  mkdir -p $PREFIX

  if [[ "$2" == "docker-start" ]]; then
    kong prepare -p $PREFIX --nginx-conf /usr/local/kong/custom_nginx.template
  fi
fi

# Setting pgbouncer
./setting_pgbouncer.sh

./start.sh