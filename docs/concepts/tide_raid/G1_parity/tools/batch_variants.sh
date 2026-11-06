#!/bin/bash
# usage: batch_variants.sh <tag> "k=v k=v" "k=v ..." ...  -> one capture + compare per variant of the current city_grade.tres; prints score / squint
B=D:/rc_art/godot_look_tide/content/config/city_grade.tres; D=D:/rc_scratch/g1/lt; TAG=$1; shift; i=0
for v in "$@"; do i=$((i+1))
  python /d/rc_art/godot_look_tide/tools/look_parity/variant.py $B $D/${TAG}$i.tres $v
  bash /d/rc_art/godot_look_tide/tools/look_parity/run_capture.sh $D ${TAG}$i --grade=$D/${TAG}$i.tres >/dev/null
  echo "== $v"
  python /d/rc_art/godot_look_tide/tools/look_parity/parity_compare.py --godot $D/${TAG}$i.png --target D:/rc_scratch/g1/targetO_plan.png --plate D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/plates/01_plan.png --out $D/sh --name ${TAG}$i 2>&1 | head -2
done
