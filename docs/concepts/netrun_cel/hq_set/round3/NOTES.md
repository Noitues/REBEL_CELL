# HQ netrun round 3 (commit in godot_look_hqnet, art/hq-netrun)
1. Spill band removed. The plaza arcade is 19 real city-kit shop blocks on an arc (h 30-44) with ground-floor lit panes and dark mullions, an awning slab with a lit edge, first-floor lit windows, a fascia sign tier with glyph bars, a second sign tier, a window row, roof boards and blade signs. No additive cards for the band.
2. Root cause of the earlier "dim far band": the zoom-rule fog (zr_fog_d_bu 105, max 0.9) buried everything 100+ BU from the camera, so the arcade's lit faces were invisible (stats did not change with gain). New `hq_fog_d_bu` 200 applies only while the set piece stands (CityZoomStreet, the sky gradient is untouched). This is a fog DISTANCE change on real geometry, not a brightness lift of fog; flagging it because the brief said no fog lift. Revert by hq_fog_d_bu = 0.
3. Upper frame: HQ-only window override on the city building material while hq_on (`hq_win_share` 0.55, `hq_win_gain` 1.3, `hq_lit_k` 1.0; restored on release), plus three backdrop-tower roof logos/crowns (ring logo, four-pillar crown with lit ring, tall blade logo).
## Squint
| image | mean | p95 | loud | brightest row | upper |
|---|---|---|---|---|---|
| plate | 0.242 | 0.617 | 0.223 | 54 % | 0.393 |
| r2 hero | 0.222 | 0.592 | 0.174 | 59 % | 0.219 |
| **r3 hero** | **0.249** | **0.652** | **0.222** | **69 %** | **0.248** |
| alt_gate | 0.260 | 0.692 | 0.230 | 62 % | 0.277 |
| alt_high | 0.238 | 0.570 | 0.176 | 64 % | 0.225 |
| alt_far | 0.169 | 0.422 | 0.066 | 63 % | 0.190 |
Mean (0.249) and loud (0.222, top of the 0.18-0.22 band) hit; **brightest row 69 % misses the 50-65 % target** (r2 was 59 %, but that was the spill fake). The peak band is y 700-760 (rows 13 of 20 at 0.36) and does not come from the arcade ground panes (halving them changed nothing); it is the near flank / gate / road zone. Not resolved.
## Checks
City band on/off 0 px; street stage 5 vs round 6 0 px; targeted tests 144 pass, 0 failing, 8 pending.
Perf gpu_city (500 frames, limit 12.57): p95 12.92 / 11.12 / 3.49; p99 14.13 / 12.60 / 16.65; max 31.36 / 13.97 / 20.81; means 3.85 / 9.18 / 3.35. Run 1 is over (spike run, p50 3.0).
## Gaps
Brightest-row position; upper frame still 0.248 vs 0.393; the fog distance change; no `python -` used.
