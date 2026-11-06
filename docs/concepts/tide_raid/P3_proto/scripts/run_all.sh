#!/bin/bash
# Final captures and perf runs of the P3 prototype (each run alone, windowed through run_windowed.py).
cd D:/rc_art/godot_look_tide
S=D:/rc_scratch/tide_proto
for m in daemon home; do
  for r in normal reduce; do
    rm -rf $S/${m}_$r
    mkdir -p $S/${m}_$r
    flag=""
    if [ "$r" = "reduce" ]; then flag="--reduce"; fi
    python tools/run_windowed.py --log $S/log_${m}_$r.log --timeout 900 -- --resolution 1920x1080 res://tools/raid_tide/tide_proto_lab.tscn -- --out=$S/${m}_$r --moment=$m --capture $flag < /dev/null
  done
done
for m in daemon home; do
  python tools/run_windowed.py --log $S/log_perf_$m.log --timeout 900 -- --resolution 1920x1080 --disable-vsync res://tools/raid_tide/tide_proto_lab.tscn -- --out=$S/perf --moment=$m --perf < /dev/null
  python tools/run_windowed.py --log $S/log_perf_${m}_base.log --timeout 900 -- --resolution 1920x1080 --disable-vsync res://tools/raid_tide/tide_proto_lab.tscn -- --out=$S/perf --moment=$m --perf --baseline < /dev/null
done
python tools/run_windowed.py --log $S/log_perf_home_reduce.log --timeout 900 -- --resolution 1920x1080 --disable-vsync res://tools/raid_tide/tide_proto_lab.tscn -- --out=$S/perf --moment=home --perf --reduce < /dev/null
echo ALLDONE
