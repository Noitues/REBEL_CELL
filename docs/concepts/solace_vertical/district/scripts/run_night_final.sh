#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python scripts/batch.py "solace_v1 night finals $1" log_batch_nightfinal_$1.log -- \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir A --mode night --size 1920x1080 --spp 72 --out out/A_night_raw.png ';;' \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir B --mode night --size 1920x1080 --spp 72 --out out/B_night_raw.png ';;' \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir C --mode night --size 1920x1080 --spp 72 --out out/C_night_raw.png
