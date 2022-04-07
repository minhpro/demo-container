#!/bin/ash

now=`date +'%Y/%m/%d %H:%M:%S'`

echo "PING" | nc -w 5 $DB_HOST 5432 > /dev/null 2>&1 ; postgres_com=$?
if [ ${postgres_com} = 1 ]; then
    echo $now 'health check failed : connection refused with' $DB_HOST >> /usr/local/kong/logs/error.log
    exit 1
else
    exit 0
fi
