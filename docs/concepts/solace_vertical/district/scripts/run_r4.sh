#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
P="scripts/sd_main.py -- --dir D --park 1"
python scripts/batch.py "solace_v1 round4 park" log_batch_r4.log -- \
 "$BL" --factory-startup -b --python $P --mode map --view raid --tod night --size 1920x1080 --out out/R4_raid_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --mode ink --view raid --tod night --size 1920x1080 --out out/R4_raid_ink.png ';;' \
 "$BL" --factory-startup -b --python $P --mode map --view raid --tod day --size 1920x1080 --out out/R4_rday_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --mode ink --view raid --tod day --size 1920x1080 --out out/R4_rday_ink.png ';;' \
 "$BL" --factory-startup -b --python $P --mode night --tod day --size 1920x1080 --spp 72 --sun 3.0 --expo 0.1 --out out/D_day_park_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --mode night --size 1920x1080 --spp 72 --moon 1.7 --sky 1.0 --expo -1.15 --out out/D_night_park_raw.png
