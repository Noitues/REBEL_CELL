#!/bin/bash
# v3-r3 re-render: one GPU lock per batch (gpu_oc.sh), a pause between batches so a waiting agent can take the lock
cd "$(dirname "$0")"
for job in "fc_street" "fc_dive 275 299" "fc_dive 299 323" "fc_move"; do
  bash gpu_oc.sh $job
  if ls D:/rc_scratch/GPU_WAITING_* 2>/dev/null | grep -qv storyboard; then sleep 120; fi
done
echo "RUNNER DONE $(date +%T)"
