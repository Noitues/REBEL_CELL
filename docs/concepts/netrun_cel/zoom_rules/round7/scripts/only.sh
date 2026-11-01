#!/bin/bash
R=D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/round7
S=D:/rc_art/godot_look_tide/tools/look_parity/nr_zoom.sh
rm -f $R/gif_street_only/gif_*.png $R/gif_city_only/gif_*.png
bash $S $R/gif_street_only go_s --zr --target --stages=5 --layers=1 --freeze --flick-only --gif=48,12,0 > /d/rc_tmp/r7_o1.out 2>&1
bash $S $R/gif_city_only go_c --zr --target --stages=1 --layers=1 --freeze --flick-only --gif=48,12,0 > /d/rc_tmp/r7_o2.out 2>&1
