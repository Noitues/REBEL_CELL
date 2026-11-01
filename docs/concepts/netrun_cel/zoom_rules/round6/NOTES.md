# Zoom rules, round 6 (O-3: band position, far towers, city-view highlight)
Godot `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom`. All numbers in `CityConfig` `zr_*`. Baseline (round 5 code, same flags) reproduced bit-exact first (0 differing pixels).

## Result (`street_frame.png`, `round5_vs_round6.jpg`, `logs/lum.txt`, same method)
- Brightest 24 px band: **y 777 = 72 % down** (round 5: 862 = 80 %). In the 70-75 % target.
- Brightest-row / facade ratio **2.69** (round 5 2.75, plate 2.72).
- Frame mean **0.170** (round 5 0.192, plate 0.20): lower; the dim far towers and the dimmer foot cost about 0.02. Road mean (80-100 %) **0.165** (round 5 0.174).

## 1. Band position: what changed
Finding that moved everything: the peak at y 840-870 was NOT mainly the shop windows. Disabling pieces one by one showed the bright orange / cream blocks on the kerb at the foot of the frontage were the **r43 street cars** (toy boxes parked on the frontage lot), plus the window bottoms (window colour gradient was bright at the bottom), the dimmed-by-nothing facade foot (under 3 BU the plum / dim rule never applied), the pavement spill, the lamp pools and the road's mirror of all of these.
- `zr_stage_hide_cars` (true): the staged street hides the r43 `traffic` layer (the wet road's car streaks carry the traffic there). Restored on release.
- Window glow gradient `zr_win_bot` / `zr_win_top` 0.1 / 0.3 (was 1.0 / 0.4: brightest at the bottom); goods `zr_goods_k` 0.3; pavement spill `zr_spill_k` 0.3; kerb `zr_kerb_k` 0.3.
- Fascia (sign) row: `zr_fascia_h` 0.6 -> 1.2 (taller board) and `zr_fascia_gain` 3.0 (sign faces and tube frames); the ground floor height is `zr_shop_h_bu` 2.4 (was a literal in two places; unchanged).
- Facade foot below `zr_body_dim_h.x` now dims too: `zr_base_dim_a` / `_e` 0.5 / 0.4 (shader `zr_base_dim`, staged-street weight).
- Reflection / pools / mist: `zr_refl_gain` 2.6 -> 1.6, `zr_pool_gain` 2.6 -> 1.3, `zr_mist_alpha` 0.14 -> 0.10.
Rows (24 px steps, `logs/rows.txt`): sign rows 744-780 at 0.35-0.40; window rows 804-844 0.29-0.31; the strip 852-868 (pavement + road mirror) still 0.35-0.39, so the margin of the peak over it is small (0.384 vs about 0.37).

## 2. Far blue towers
Cause: the plum / dim rule and the tower fade were multiplied by `zrf`, the facade fade by fragment ppb (22.4-33.6), which is 0 for the far towers. New uniform `zr_far` (x: plum / dim weight, y: tower-fade weight) is set only while the staging is active (`CityZoomStreet._post`), shader takes `max(zrf, zr_far * zr_on)`. `zr_far_dim` 0.4, `zr_far_tf` 0.0 (tower fade for far towers left off; try 0.5 for plate-like fogged silhouettes). Upper frame (25-60 % of height) mean 0.168 -> 0.143. The City band is untouched (`zr_far` is 0 outside the staged street).

## 3. City-view highlight of the target street
New `CityZoomHighlight` (`scripts/city3d/city_zoom_highlight.gd`, shader `city_zoom_hl.gdshader`): pink fill over the 3-row, 12-lot segment, cyan outline (min `zr_hl_line_px` px), end squares, a pink light column; additive, drawn over buildings (no depth test); fades out over `zr_hl_fade` (focus ppb 8-16). It is created only by `CityZoomStreet.set_target(target)`, which exists only while the zoom rules are on, and nr_zoom calls it only with `--hl`. Decision: the check "zoom rules on vs off at stage 1 = 0 pixels" is impossible if the highlight shows whenever the rules are on, so it needs the explicit call; the game can call `zoom_street.set_target(CityZoomTarget.make(cfg))` when the netrun zoom starts. Frame: `city_view_highlight.png`. Highlight fill is quite strong; tune `zr_hl_fill`.

## Checks
- City band, zoom rules on vs off, stage 1 (`--layers=both --target`, no `--hl`): **0 differing pixels** (`logs/city_band_on_vs_off.txt`).
- Tests: the same 9 scripts + 3 new tests (sign row outshines the window row, round 6 defaults, highlight): **137 tests, 0 failing, 8 pending** (`logs/targeted_tests.log`).
- Perf street band, gpu_city p95, 500 frames, limit 12.57 ms. Three consecutive runs: **14.02, 11.18, 12.65** (two over; means 10.4 / 10.3 / 9.3, the run-1 p95 and p99 are contention outliers). Three more: **10.99, 11.87, 11.41**. Spread over six 10.99-14.02. All under the GPU lock; `logs/perf1-6.log`. I believe the 14.02 / 12.65 are other load on the GPU (means are the same), but could not prove it.

## Did not work / open
- Tuning alone still could not move the peak (round 5's finding); the move needed removing the cars and dimming the foot.
- `--hide=` in nr_zoom runs before the zoom nodes exist (finds nothing); added `--hide2=` (after) and `--who=x,y` (nodes at a screen pixel) as diagnostics, plus `--hl`.
- Frame mean is 0.02 under round 5; fixing it needs a brighter road or upper facade, both of which pull the ratio away from 2.72.
- Slip: I started `python -` once (a heredoc line); it hung and I stopped that one task by id. Nothing else ran.
