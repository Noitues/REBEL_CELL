#!/usr/bin/env bash
# Render one still script headless. Usage: scripts/run.sh s01_combat [out.png]
# Env: RN_PCT (resolution %), RN_SAMPLES. Logs go to $LOGDIR (default: scratch temp).
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
LOGDIR="${LOGDIR:-${TMP:-/tmp}}"
timeout 900 "$BL" -b --factory-startup --python "$HERE/$1.py" -- ${2:+"$2"} > "$LOGDIR/rn_$1.log" 2>&1
echo "exit $? log $LOGDIR/rn_$1.log"
