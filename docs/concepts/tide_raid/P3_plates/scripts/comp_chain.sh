#!/bin/bash
# comp_chain.sh beat... : waits for each beat's P3_DONE marker, then builds the 4K plate.
export P2_S=2
cd D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts
for b in "$@"; do
  until [ -f D:/rc_scratch/tide_concepts/p3_work/s2/$b/P3_DONE ]; do sleep 10; done
  python p1_final.py $b >> D:/rc_scratch/tide_concepts/p3_work/all4k.log 2>&1
  echo "built4k $b" >> D:/rc_scratch/tide_concepts/p3_work/all4k.log
done
echo "COMPSDONE $*" >> D:/rc_scratch/tide_concepts/p3_work/all4k.log
