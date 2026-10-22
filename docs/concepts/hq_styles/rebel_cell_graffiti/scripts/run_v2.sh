#!/bin/sh
# F1b + graffiti (Eevee, no GPU lock): sh run_v2.sh <tag> [pct] [samples]  -> D:/rc_scratch/.../<tag>.png
S=/d/rc_scratch/hq_styles/rebel_cell_graffiti
H="$(cd "$(dirname "$0")" && pwd)"
export MF_PCT=${2:-100} MF_SAMPLES=${3:-48}
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "$H/gs2_scene.py" -- $S/$1 > $S/$1.log 2>&1
grep -i "traceback\|error\|DONE" -A6 $S/$1.log | head -30
python "$H/../../../round12_modem_facade/scripts/post.py" $S/$1 night $S/$1.png
