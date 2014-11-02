#!/bin/bash

PROJDIR=$( cd $(dirname $0) ; pwd -P )
PIDFILE="$PROJDIR/django.pid"
SOCKET="$PROJDIR/fastcgi.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

if [ $# -eq 0 ]; then
    ${PROJDIR}/ve/bin/python ./manage.py runfcgi method=prefork socket=$SOCKET pidfile=$PIDFILE maxchildren=3 maxspare=3
    chmod 777 $SOCKET
fi
