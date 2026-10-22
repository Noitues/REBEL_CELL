#!/bin/bash
# CPU preview of a variant: prev2.sh <variant: warm|solar> <tag>
v=$1; t=$2; shift 2
cd D:/rc_scratch/hq_styles/solace_modernart
PYTHONDONTWRITEBYTECODE=1 python D:/rc_art/art-pass/docs/concepts/hq_styles/solace_modernart/scripts/modernart_run_hq.py solace mini $t cpu=true samples=8 res=[960,540] fog_k=2 "d.variant=\"$v\"" "post=$( [ $v = warm ] && echo '{"shadow_tint":[0.50,0.48,0.47],"sat":0.9}' || echo '{"shadow_tint":[0.50,0.48,0.46],"sat":0.95}')" "$@" > run_${t}.log 2>&1
tail -2 run_${t}.log
grep -n Traceback -A12 solace/$t/blender.log | head -24
