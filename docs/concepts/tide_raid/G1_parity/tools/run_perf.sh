#!/bin/bash
# Perf series of the raid city at the plate camera (GPU time of the city view, from RenderingServer measured render time; wall clock is vsync capped under run_windowed.py).
# usage: run_perf.sh <out dir>   -> <out>/log_perf_*.log. Each run takes the GPU lock itself (run_capture.sh).
OUT=$1
S=/d/rc_art/godot_look_tide/tools/look_parity/run_capture.sh
bash $S $OUT perf_legacy --perf --frames=500 --g1-level=0
bash $S $OUT perf_l1 --perf --frames=500 --g1-level=1
bash $S $OUT perf_l2 --perf --frames=500 --g1-level=2
bash $S $OUT perf_l3 --perf --frames=500
# per feature at level 3: reflection (4), bloom (8), rain (16), lamp pools (1)
for o in 4 8 16 1 28; do
  bash $S $OUT perf_off$o --perf --frames=400 --g1-off=$o
done
