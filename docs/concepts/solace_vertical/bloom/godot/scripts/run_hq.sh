#!/bin/bash
# usage: run_hq.sh <wt> <out dir> <states csv> [extra args]
WT=$1; OUT=$2; ST=$3; shift 3
mkdir -p "$OUT"
python $WT/tools/run_windowed.py --log "$OUT/run.log" --timeout 900 -- --resolution 1920x1080 res://tools/art_pipeline/hq_run/hq_run_lab.tscn -- --out=$OUT --states=$ST --plates=D:/rc_art/art-pass/docs/concepts/golden_plates --reduce-effects=1 --settle=90 --perf=2 "$@"
