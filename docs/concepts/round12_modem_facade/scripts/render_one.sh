#!/bin/sh
# usage: render_one.sh <opt> <state>   (from the round12 folder) -> scratch/<opt>_<state>.png
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
D="$(cd "$(dirname "$0")/.." && pwd)"
"$B" -b --factory-startup --python "$D/scripts/scene.py" -- $1 $2 "$D/scratch/$1_$2" > "$D/scratch/log_$1_$2.txt" 2>&1
grep -i "traceback\|error" -A8 "$D/scratch/log_$1_$2.txt" | head -20
python "$D/scripts/post.py" "$D/scratch/$1_$2" $2 "$D/scratch/$1_$2.png"
