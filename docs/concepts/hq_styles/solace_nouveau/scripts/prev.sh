#!/bin/bash
# CPU look-dev preview: prev.sh <tag> [extra runner args]
t=$1; shift
cd D:/rc_scratch/hq_styles/solace_nouveau
python D:/rc_art/art-pass/docs/concepts/hq_styles/solace_nouveau/scripts/nouveau_run_hq.py solace mini $t cpu=true samples=8 res=[1280,720] fog_k=2 "$@" > run_${t}.log 2>&1
tail -3 run_${t}.log
grep -n Traceback -A12 solace/$t/blender.log | head -24
