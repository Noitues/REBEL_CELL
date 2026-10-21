#!/bin/bash
# tr.sh tag tod size  -> out/R_<tag>.png (cel raid + ink + post)
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
t=$1; tod=$2; sz=$3
"$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode map --view raid --tod $tod --size $sz --out out/R_${t}_raw.png > t_r.log 2>&1
"$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode ink --view raid --tod $tod --size $sz --out out/R_${t}_ink.png > t_ri.log 2>&1
python scripts/ink.py out/R_${t}_raw.png out/R_${t}_ink.png out/R_${t}_inked.png 2.6 > /dev/null
python scripts/post.py $( [ $tod = day ] && echo mapday || echo mapraid ) out/R_${t}_inked.png out/R_${t}.png
python scripts/stats.py out/R_${t}.png
