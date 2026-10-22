#!/bin/bash
# usage: run_street.sh <wt> <out dir> <bloom front or "off"> [extra args]
WT=$1; OUT=$2; B=$3; shift 3
mkdir -p "$OUT"
ARGS="--seed=${SEED:-4} --states=${STATES:-decision} --shots=$OUT ${PLATE_ARG-"--plate_dir=D:/rc_art/art-pass/docs/concepts/golden_plates"} --reduce-effects=1 --settle=60"
if [ "$B" != "off" ]; then ARGS="$ARGS --bloom=$B"; fi
python $WT/tools/run_windowed.py --log "$OUT/run.log" --timeout 900 -- --resolution 1920x1080 res://tools/city/na23_lab.tscn -- $ARGS "$@"
