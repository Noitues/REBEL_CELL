#!/bin/bash
# usage: run_beats.sh beat1 beat2 ...   (spec + Blender passes under the GPU lock)
cd D:/rc_art/art-pass/docs/concepts/tide_raid/P2_plates/scripts
WBD=D:/rc_scratch/tide_concepts/p2_work; [ "$P2_S" = "2" ] && WBD=$WBD/s2
for b in "$@"; do
  python p1_beats.py $b > /dev/null && python run_bl.py $WBD/$b/spec.json $WBD/$b/bl.log
  echo "done $b"
done
