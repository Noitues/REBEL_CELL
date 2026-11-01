# Zoom rules round 7b (city highlight middle value)
Godot `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom`, on 0d1cdf78. Captured with nr_zoom `--hl` (`scripts/cands.sh`); sheet `crop_sheet.png` (r6, r7, candA-C, pick).
Common to all: `zr_hl_fill` 0.22 (r7 0.14), `zr_hl_beam_k` 3.0 (r7 1.5). New config `zr_hl_edge_color` (outline colour, default was cyan).
- candA: white outline, 3 px. Reads, but white blends with the lit building edges.
- candB: pink outline (1.0,0.18,0.62), 4 px. Separates cleanly from the highway cyan, ties to the pink fill and the beam.
- candC: yellow outline, 4 px. Most visible, but off-palette and reads as a new hazard marker.
PICK: candB (fill 0.22, beam_k 3.0, edge pink, line 4 px; `zr_hl_line_px` 3 -> 4). Segment is the first thing found; the fill stays on the road lots, so no floating pane. The beam is still thin at this scale.
Checks: city band zoom rules on vs off (frozen, no --hl) 0 differing pixels (`logs/city_band_on_vs_off.txt`); test_city_zoom_stage + test_city_zoom_flicker pass (`logs/targeted_tests.log`). Test change: fill ceiling in test_city_zoom_stage 0.2 -> 0.25.
