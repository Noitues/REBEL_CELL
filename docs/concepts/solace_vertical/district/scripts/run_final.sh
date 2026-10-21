#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python scripts/batch.py "solace_v1 finals $1" log_batch_final_$1.log -- \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir A --mode map --size 1920x1080 --scale 330 --out out/A_map_raw.png ';;' \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir B --mode map --size 1920x1080 --scale 330 --out out/B_map_raw.png ';;' \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir C --mode map --size 1920x1080 --scale 330 --out out/C_map_raw.png
