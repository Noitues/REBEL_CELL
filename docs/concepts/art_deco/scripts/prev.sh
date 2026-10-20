#!/bin/bash
# CPU look-dev preview: prev.sh <corp> <tag> [extra runner args]
c=$1; t=$2; shift 2
cd D:/rc_scratch/art_deco
python D:/rc_art/art-pass/docs/concepts/art_deco/scripts/deco_run_hq.py $c mini $t cpu=true samples=8 res=[960,540] 'post={"shadow_tint":[0.50,0.50,0.52],"sat":0.80}' fog_k=2 "$@" > run_${c}_${t}.log 2>&1
tail -2 run_${c}_${t}.log
grep -n Traceback -A10 $c/$t/blender.log | head -16
