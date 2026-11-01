#!/bin/bash
# baseline (HEAD 22979681) captures: frozen street, frozen city band both modes, highlight
R=D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/round7
T=$R/before
S=D:/rc_art/godot_look_tide/tools/look_parity/nr_zoom.sh
bash $S $T street --zr --target --stages=5 --layers=1 --freeze > /d/rc_tmp/r7_b1.out 2>&1
bash $S $T city --zr --target --stages=1 --layers=both --freeze > /d/rc_tmp/r7_b2.out 2>&1
bash $S $T hl --zr --target --hl --stages=1 --layers=1 > /d/rc_tmp/r7_b3.out 2>&1
echo done > $T/DONE
