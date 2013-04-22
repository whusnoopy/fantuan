#!/bin/bash

DATE=` date +%Y%m%d `
BACKUP="/home/yewen/tmp/fantuan_v${DATE}.tar.gz"
PROJDIR="fantuan"

cd "/home/yewen"
tar -czf $BACKUP $PROJDIR
