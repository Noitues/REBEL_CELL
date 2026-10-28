#!/bin/bash
# rb.sh <gpu|cpu> beat... : spec + Blender passes at 4K, then touch the P3_DONE marker. cpu = Cycles on CPU, no GPU lock.
export P2_S=2
cd D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts
MODE=$1; shift
for b in "$@"; do
  rm -f D:/rc_scratch/tide_concepts/p3_work/s2/$b/P3_DONE
  if [ "$MODE" = "cpu" ]; then
    python p1_beats.py $b --device=CPU > /dev/null && python run_bl.py D:/rc_scratch/tide_concepts/p3_work/s2/$b/spec.json D:/rc_scratch/tide_concepts/p3_work/s2/$b/bl.log --nolock
  else
    python p1_beats.py $b > /dev/null && python run_bl.py D:/rc_scratch/tide_concepts/p3_work/s2/$b/spec.json D:/rc_scratch/tide_concepts/p3_work/s2/$b/bl.log
  fi
  touch D:/rc_scratch/tide_concepts/p3_work/s2/$b/P3_DONE
  echo "bl $MODE $b done" >> D:/rc_scratch/tide_concepts/p3_work/all4k.log
done
