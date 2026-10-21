#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python scripts/batch.py "solace_v1 D night fix" log_batch_Dn2.log -- \
 "$BL" --factory-startup -b --python scripts/sd_main.py -- --dir D --mode night --size 1920x1080 --spp 72 --moon 1.7 --sky 1.0 --expo -1.15 --out out/D_night_raw.png
