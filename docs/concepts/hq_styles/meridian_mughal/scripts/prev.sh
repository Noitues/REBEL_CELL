#!/bin/bash
# CPU look-dev preview (no GPU lock): prev.sh <tag> [extra runner args]
t=$1; shift
cd D:/rc_scratch/hq_styles/meridian_mughal
python D:/rc_art/art-pass/docs/concepts/hq_styles/meridian_mughal/scripts/mg_run_hq.py mini $t cpu=true samples=8 res=[1280,720] fog_k=1.2 "$@" > run_$t.log 2>&1
tail -3 run_$t.log
grep -n Traceback -A12 $t/blender.log | head -20
