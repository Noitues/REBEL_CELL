#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python scripts/batch.py "solace_v1 D day" log_batch_dday.log -- \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode night --tod day --size 1920x1080 --spp 72 --sun 3.0 --expo 0.1 --out out/D_day_raw.png
