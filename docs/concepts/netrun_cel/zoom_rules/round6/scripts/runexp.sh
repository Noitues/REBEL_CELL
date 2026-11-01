#!/bin/bash
# usage: runexp.sh name set1 set2 ... ; captures stage 5 and prints lum
R=D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/round6
N=$1; shift
ARGS=""
for s in "$@"; do ARGS="$ARGS --set=$s"; done
bash /d/rc_art/godot_look_tide/tools/look_parity/nr_zoom.sh $R/scratch $N --zr --target --stages=5 --layers=1 --freeze $ARGS > /d/rc_tmp/exp_$N.out 2>&1
cp $R/scratch/stage_5_layers.png $R/scratch/$N.png
python $R/../round5/scripts/lum_profile.py $R/scratch/$N.png
python $R/../round5/scripts/rows.py $R/scratch/$N.png
grep -i "error" $R/scratch/log_$N.log | head -5
