#!/bin/bash
cd D:/rc_scratch/solace_v1/district
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
P="scripts/sd_main.py -- --dir D --park 1 --plinth 1"
CAM="--cam -21.5,-46.0,43.6,0,0,8"
python scripts/batch.py "solace_v1 round5 plinth b" log_batch_r5b.log -- \
 "$BL" --factory-startup -b --python $P --mode night --tod day --size 1920x1080 --spp 72 --sun 3.0 --expo 0.1 --out out/D_day_r5_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --mode night --size 1920x1080 --spp 72 --moon 1.7 --sky 1.0 --expo -1.15 --out out/D_night_r5_raw.png ';;' \
 "$BL" --factory-startup -b --python $P --mode night --size 1920x1080 --spp 96 --moon 1.7 --sky 1.0 --expo -1.15 $CAM --out out/D_base_r5_raw.png
