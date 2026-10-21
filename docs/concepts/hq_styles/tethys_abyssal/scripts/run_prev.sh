#!/bin/bash
# CPU look-dev preview: [BORDER=x0,y0,x1,y1] run_prev.sh <tag> [res_k] [spp]   (no GPU lock; output D:/rc_scratch/hq_styles/tethys_abyssal/<tag>)
S=D:/rc_scratch/hq_styles/tethys_abyssal
HERE="$(cd "$(dirname "$0")" && pwd)"
TAG=$1; RK=${2:-0.75}; SPP=${3:-8}
mkdir -p $S/$TAG
export TETHYS_SCR=$S/scr TETHYS_CPU=1 TETHYS_BORDER=${BORDER:-}
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "$HERE/abyssal_build.py" -- aaa t_over $S/$TAG $RK $SPP > $S/$TAG/blender.log 2>&1
tail -3 $S/$TAG/blender.log; grep -n Traceback -A12 $S/$TAG/blender.log | head -30
