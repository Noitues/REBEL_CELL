#!/bin/bash
# usage: hq_net.sh <out dir> <log name> [hq_net args...]  (one capture batch under the GPU lock; windowed through run_windowed.py) -- worktree godot_look_hqnet
cd D:/rc_art/godot_look_hqnet
OUT=$1; NAME=$2; shift 2
mkdir -p "$OUT"
python tools/look_parity/hq_net_lock.py "godot hq_net $NAME" -- python tools/run_windowed.py --log "$OUT/log_$NAME.log" --timeout 1200 -- --resolution 1920x1080 res://tools/look_parity/hq_net.tscn -- --out="$OUT" "$@" < /dev/null
