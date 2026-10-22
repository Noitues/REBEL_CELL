#!/bin/bash
# CPU preview of solarpunk v2: prev3.sh <tag>
t=$1; shift
cd D:/rc_scratch/hq_styles/solace_modernart
PYTHONDONTWRITEBYTECODE=1 python D:/rc_art/art-pass/docs/concepts/hq_styles/solace_modernart/scripts/modernart_run_hq.py solace mini $t cpu=true samples=8 res=[960,540] fog_k=2 'd.variant="solar2"' 'post={"shadow_tint":[0.42,0.52,0.56],"sat":1.0}' key_w=170000 fill_w=90000 "$@" > run_${t}.log 2>&1
tail -2 run_${t}.log
grep -n Traceback -A12 solace/$t/blender.log | head -24
