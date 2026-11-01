# Zoom rules, round 5 (O-2 street polish)
Godot `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom`. Config values only (plus two new `zr_*` for car slots).

Changes: `zr_body_dim` 0.45/0.3 -> 0.2/0.1; `zr_plum_k` 0.7 -> 0.9 (upper facades darker; shop band untouched). Cars: `zr_car_count` 110 -> 260, new `zr_car_slots` 8 (was a literal 4) and `zr_car_keep` 0.85 (was literal 0.7), `zr_car_w_bu` 0.1 -> 0.25 (thicker streaks). Corp-colour rule and 200 px/s threshold untouched.

Measured (`street_frame.png`, same method, `logs/lum.txt`): brightest-row ratio **2.75** (round 4 2.20, target 2.5, plate 2.72); frame mean 0.192; road mean 0.174 (round 4 0.165). Band position still **80 % down (y 862)**: not reached 70-75 %.
Baseline reproduced bit-exact first (round 4 frame, 0 differing pixels).

Band position, what did not work: the peak row (y 840-870) is the bottom of the lit shop windows, base props and the kerb/pavement line. Window gain 1.2 -> 0.15, pool gain, mist, reflection gain, fascia height 0.95, lantern share, sign/text gain 3.6/4.0 each only moved the ratio down (2.25-2.49) and never moved the peak above 80 %. Rows 768-792 (signs) stay at 0.35 against 0.38-0.45 at 840-864. Needs a geometry/layout change (taller or higher-set shop band), not tuning.
Streaks: they lift the road mean and add lane streaks on the centre road; cross-street streaks stay thin because only 1-3 staged road lots are in range (cap 260 is reached; 520 quads).

City band: zoom rules on vs off at stage 1, 0 differing pixels; also identical to round 4's.
Tests: 9 scripts (zoom layers/r2/rules/stage, neon kit, shaders, shaders render, city3d model, city motion): 134 tests, 0 failing, 8 pending (`logs/targeted_tests.log`).
Perf street band, 500 frames, gpu_city p95: 11.47, 11.31, 12.50 ms (limit 12.57; three consecutive runs, GPU looked quiet, spread 1.2 ms; wall p95 19.4-20.9). `logs/perf*.log`.
