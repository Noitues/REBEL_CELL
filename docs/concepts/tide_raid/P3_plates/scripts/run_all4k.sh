#!/bin/bash
# full 4K rebuild: Blender passes (GPU lock per beat) then comps overlap with the next Blender job. usage: run_all4k.sh beat...
export P2_S=2
cd D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts
LOG=D:/rc_scratch/tide_concepts/p3_work/all4k.log
pid=""
for b in "$@"; do
  bash run_beats.sh $b >> $LOG 2>&1
  [ -n "$pid" ] && wait $pid
  (python p1_final.py $b >> $LOG 2>&1; echo "built4k $b" >> $LOG) &
  pid=$!
done
wait $pid
echo ALLDONE >> $LOG
