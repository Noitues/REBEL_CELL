#!/bin/bash
# v3-r3b: wait for the superseded dive job (its own lock) to finish, release that lock, then the batches, one lock each
cd "$(dirname "$0")"
until grep -q "^DONE" oc_fc_dive_275.log; do sleep 15; done
sleep 10
grep -q "^storyboard" D:/rc_scratch/GPU_LOCK 2>/dev/null && rm -f D:/rc_scratch/GPU_LOCK
echo "released superseded lock $(date +%T)"
for job in "fc_street" "fc_dive 275 299" "fc_dive 299 323" "fc_move"; do
  if ls D:/rc_scratch/GPU_WAITING_* 2>/dev/null | grep -qv storyboard; then sleep 120; fi
  bash gpu_oc.sh $job
done
echo "RUNNER DONE $(date +%T)"
