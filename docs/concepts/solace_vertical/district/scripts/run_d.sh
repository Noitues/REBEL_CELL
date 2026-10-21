#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python scripts/batch.py "solace_v1 round2 D" log_batch_D.log -- \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode map --size 1920x1080 --scale 330 --out out/D_map_raw.png ';;' \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode ink --size 1920x1080 --scale 330 --out out/D_ink.png ';;' \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode night --size 1920x1080 --spp 72 --out out/D_night_raw.png
