#!/bin/bash
# CPU render of one idea (no GPU lock): [BORDER=..] [FLAP=..] [LOOP_PHI=..] run_idea.sh <A..E> <tag> [res_k] [spp]
# Idea E also fills the HQ lot with copied drowned-city blocks (fill_city.py -> zoned_fill.json) and writes the shadow outline.
S=D:/rc_scratch/hq_styles/tethys_ideas
HERE="$(cd "$(dirname "$0")" && pwd)"
K=$1; TAG=$2; RK=${3:-1.0}; SPP=${4:-16}
mkdir -p $S/$TAG
export IDEA=$K TETHYS_SCR=D:/rc_scratch/hq_styles/tethys_abyssal/scr TETHYS_CPU=1 TETHYS_BORDER=${BORDER:-}
if [ "$K" = "E" ]; then export FILL_ZONED=$S/zoned_fill.json SHADOW_JSON=$S/$TAG/shadow.json; fi
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "$HERE/ideas_build.py" -- aaa t_over $S/$TAG $RK $SPP > $S/$TAG/blender.log 2>&1
grep -n Traceback -A12 $S/$TAG/blender.log | head -24
python "$HERE/../../tethys_abyssal/scripts/abyssal_post.py" $S/$TAG/t_over_aaa $S/$TAG/$TAG.png 0.16 | tail -1
if [ "$K" = "E" ] && [ -f $S/$TAG/shadow.json ]; then
  python "$HERE/manta_post.py" $S/$TAG/$TAG.png $S/$TAG/shadow.json $S/$TAG/t_over_aaa_index.npy $S/$TAG/${TAG}_sh.png 0.8
fi
