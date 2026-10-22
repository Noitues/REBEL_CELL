#!/bin/sh
# preview: sh run_prev.sh <tag> <res_w> <spp>   (CPU, no GPU lock)
S=/d/rc_scratch/hq_styles/rebel_cell_graffiti
H="$(cd "$(dirname "$0")" && pwd)"
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "$H/${SCENE:-gs_scene.py}" -- $S/$1 $2 $3 cpu > $S/$1.log 2>&1
grep "^\[gs\]\|Traceback\|Error" $S/$1.log
python "$H/gs_post.py" $S/$1_beauty.npy $S/$1.png 0.17 $2
