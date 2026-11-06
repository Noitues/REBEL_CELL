#!/bin/bash
# usage: run_capture.sh <out dir> <name> [extra user args...]  (one capture batch under the GPU lock; windowed through run_windowed.py)
cd D:/rc_art/godot_look_tide
OUT=$1; NAME=$2; shift 2
mkdir -p "$OUT"
python tools/look_parity/gpu_lock_run.py "godot parity $NAME" -- python tools/run_windowed.py --log "$OUT/log_$NAME.log" --timeout 900 -- --resolution 1920x1080 res://tools/look_parity/parity_capture.tscn -- --out="$OUT" --name="$NAME" "$@" < /dev/null
