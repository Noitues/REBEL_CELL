#!/bin/bash
# the full set: E (still), B, C, D, A, then the two other frames of the manta strip along the loop. CPU, no GPU lock.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd $HERE
./run_idea.sh E E4 1.0 16
for k in B C D A; do ./run_idea.sh $k $k 1.0 16; done
FLAP=1.0 LOOP_PHI=-135 ./run_idea.sh E Eup 1.0 8
FLAP=-1.0 LOOP_PHI=-45 ./run_idea.sh E Edown 1.0 8
echo ALLDONE
