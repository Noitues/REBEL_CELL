#!/bin/bash
# usage: iterate.sh <iter name> [capture args...]  -> capture (GPU lock) + compare against the plate city target (with the plates light spill) and plate 01; sheet in $G1/sheets
G1=/d/rc_scratch/g1
N=$1; shift
bash /d/rc_art/godot_look_tide/tools/look_parity/run_capture.sh $G1/runs $N "$@"
grep -i "error\|SHADER" $G1/runs/log_$N.log | head -10
python /d/rc_art/godot_look_tide/tools/look_parity/parity_compare.py --godot D:/rc_scratch/g1/runs/$N.png --target D:/rc_scratch/g1/targetO_plan.png --plate D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/plates/01_plan.png --out D:/rc_scratch/g1/sheets --name $N
python /d/rc_scratch/g1/regions.py D:/rc_scratch/g1/runs/$N.png D:/rc_scratch/g1/targetO_plan.png
