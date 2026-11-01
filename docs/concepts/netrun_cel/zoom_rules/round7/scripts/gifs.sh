#!/bin/bash
R=D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/round7
S=D:/rc_art/godot_look_tide/tools/look_parity/nr_zoom.sh
rm -f $R/gif_street/gif_*.png $R/gif_city/gif_*.png
bash $S $R/gif_street gs --zr --target --stages=5 --layers=1 --gif=48,12,0 > /d/rc_tmp/r7_g1.out 2>&1
bash $S $R/gif_city gc --zr --target --stages=1 --layers=1 --gif=48,12,0 > /d/rc_tmp/r7_g2.out 2>&1
echo done > $R/gif_city/DONE
