#!/bin/bash
# usage: labrun.sh <moment> <outdir> [args...]  one lab capture under the GPU lock (windowed through run_windowed.py)
M=$1; OUT=$2; shift 2
cd /d/rc_art/godot_look_tide
python D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/tools/gpu_lock_run.py "godot tide lab $M" -- python tools/run_windowed.py --log "$OUT/log_$M.log" --timeout 1500 --  --resolution 1920x1080 res://tools/raid_tide/tide_proto_lab.tscn -- --out="$OUT" --moment=$M --capture --plate-cam "$@" < /dev/null
