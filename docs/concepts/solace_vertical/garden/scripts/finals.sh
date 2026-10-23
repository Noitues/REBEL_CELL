#!/bin/bash
# all six Cycles finals (1920x1080, 128 spp), each under the GPU lock helper; then the three cel maps
cd /d/rc_scratch/solace_v1/garden
for k in A B C; do
  for v in street inside; do
    ./rs.sh $k $v F_${v}_$k 1920x1080 128 | tail -1
  done
done
echo FINALS_DONE
