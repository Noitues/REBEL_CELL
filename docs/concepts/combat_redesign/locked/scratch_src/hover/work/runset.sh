#!/bin/sh
# usage: runset.sh LOGTAG jobs...   (env CORP passes through)
cd /d/rc_scratch/combat_redesign/locked/hover/src
tag=$1; shift
python hz_run.py "$@" > ../work/log_$tag.txt 2>&1
