#!/bin/bash
# candidates: name fill beam_k edge_color line_px
R=D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/round7b
S=D:/rc_art/godot_look_tide/tools/look_parity/nr_zoom.sh
F=D:/rc_art/godot_look_tide/scripts/city3d/city_config.gd
run() {
  sed -i -E "s|^(@export var zr_hl_fill: float = ).*|\1$2|; s|^(@export var zr_hl_beam_k: float = ).*|\1$3|; s|^(@export var zr_hl_edge_color: Color = ).*|\1$4|; s|^(@export var zr_hl_line_px: float = ).*|\1$5|" $F
  bash $S $R/$1 hl --zr --target --hl --stages=1 --layers=1 > /d/rc_tmp/r7b_$1.out 2>&1
}
run candA 0.22 3.0 "Color(1.0, 1.0, 1.0)" 3.0
run candB 0.22 3.0 "Color(1.0, 0.18, 0.62)" 4.0
run candC 0.22 3.0 "Color(1.0, 0.85, 0.2)" 4.0
echo done > $R/DONE
