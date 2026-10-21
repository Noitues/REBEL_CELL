#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
P="scripts/sd_main.py --"
python scripts/batch.py "solace_v1 round3" log_batch_r3.log -- \
 "$BL" --factory-startup -b --python $P --dir D --mode map --view raid --tod night --size 1920x1080 --out out/R3_raid_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --dir D --mode ink --view raid --tod night --size 1920x1080 --out out/R3_raid_ink.png ';;' \
 "$BL" --factory-startup -b --python $P --dir D --mode map --view raid --tod day --size 1920x1080 --out out/R3_rday_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --dir D --mode ink --view raid --tod day --size 1920x1080 --out out/R3_rday_ink.png ';;' \
 "$BL" --factory-startup -b --python $P --dir D --mode night --tod day --size 1920x1080 --spp 72 --sun 3.0 --expo 0.15 --out out/D_day_raw.png
