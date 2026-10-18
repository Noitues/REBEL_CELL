# Balance comparison: cal_skill_060_020

- A: `cal_builtin_s060.json` (overrides: none)
- B: `cal_builtin_s020.json` (overrides: none)
- mode fight; A 720 records, B 720 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 443 of 792 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:account_manager@t1 | dealt | 142.750 | 104.150 | -38.600 | [-51.460, -26.100] | -27.0 % | **CHANGED** |
| fight:account_manager@t1 | dealt_per_turn | 13.954 | 7.692 | -6.262 | [-7.945, -4.620] | -44.9 % | **CHANGED** |
| fight:account_manager@t1 | died | 0.450 | 0.900 | +0.450 | [+0.250, +0.650] | +100.0 % | **CHANGED** |
| fight:account_manager@t1 | enrage_step | 0.800 | 1.350 | +0.550 | [+0.300, +0.800] | +68.8 % | **CHANGED** |
| fight:account_manager@t1 | hp_end | 16.400 | 1.000 | -15.400 | [-22.903, -8.350] | -93.9 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost | 43.600 | 59.000 | +15.400 | [+8.150, +22.700] | +35.3 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost_frac | 0.727 | 0.983 | +0.257 | [+0.130, +0.383] | +35.3 % | **CHANGED** |
| fight:account_manager@t1 | intake | 36.450 | 48.400 | +11.950 | [+5.050, +19.200] | +32.8 % | **CHANGED** |
| fight:account_manager@t1 | perfect_rate | 0.618 | 0.346 | -0.272 | [-0.345, -0.202] | -44.0 % | **CHANGED** |
| fight:account_manager@t1 | ram_left_per_turn | 8.699 | 9.961 | +1.262 | [+0.760, +1.807] | +14.5 % | **CHANGED** |
| fight:account_manager@t1 | taken | 43.600 | 59.000 | +15.400 | [+8.398, +22.752] | +35.3 % | **CHANGED** |
| fight:account_manager@t1 | turns | 10.850 | 13.950 | +3.100 | [+1.900, +4.400] | +28.6 % | **CHANGED** |
| fight:account_manager@t1 | turns_both_share | 0.255 | 0.178 | -0.077 | [-0.148, -0.010] | -30.2 % | **CHANGED** |
| fight:account_manager@t1 | won | 0.550 | 0.100 | -0.450 | [-0.650, -0.250] | -81.8 % | **CHANGED** |
| fight:account_manager@t2 | dealt | 175.600 | 97.600 | -78.000 | [-96.700, -59.895] | -44.4 % | **CHANGED** |
| fight:account_manager@t2 | dealt_per_turn | 13.037 | 7.495 | -5.542 | [-7.000, -4.194] | -42.5 % | **CHANGED** |
| fight:account_manager@t2 | parked | 9.900 | 1.700 | -8.200 | [-12.453, -4.700] | -82.8 % | **CHANGED** |
| fight:account_manager@t2 | perfect_rate | 0.602 | 0.369 | -0.234 | [-0.301, -0.170] | -38.8 % | **CHANGED** |
| fight:account_manager@t2 | ram_left_per_turn | 8.941 | 9.791 | +0.851 | [+0.378, +1.318] | +9.5 % | **CHANGED** |
| fight:account_manager@t3 | dealt | 164.050 | 62.700 | -101.350 | [-131.252, -73.095] | -61.8 % | **CHANGED** |
| fight:account_manager@t3 | dealt_per_turn | 10.530 | 5.441 | -5.089 | [-6.506, -3.749] | -48.3 % | **CHANGED** |
| fight:account_manager@t3 | enrage_step | 1.750 | 0.750 | -1.000 | [-1.450, -0.550] | -57.1 % | **CHANGED** |
| fight:account_manager@t3 | intake | 45.250 | 52.700 | +7.450 | [+3.300, +11.400] | +16.5 % | **CHANGED** |
| fight:account_manager@t3 | parked | 2.200 | 0.000 | -2.200 | [-3.903, -0.850] | -100.0 % | **CHANGED** |
| fight:account_manager@t3 | perfect_rate | 0.563 | 0.326 | -0.237 | [-0.304, -0.170] | -42.0 % | **CHANGED** |
| fight:account_manager@t3 | ram_left_per_turn | 9.333 | 9.706 | +0.373 | [+0.021, +0.751] | +4.0 % | **CHANGED** |
| fight:account_manager@t3 | resistance_absorbed | 15.200 | 10.700 | -4.500 | [-8.000, -1.200] | -29.6 % | **CHANGED** |
| fight:account_manager@t3 | taken_per_turn | 4.222 | 6.343 | +2.121 | [+0.847, +3.593] | +50.2 % | **CHANGED** |
| fight:account_manager@t3 | turns | 15.600 | 11.400 | -4.200 | [-6.450, -1.800] | -26.9 % | **CHANGED** |
| fight:account_manager@t4 | dealt | 139.550 | 52.350 | -87.200 | [-116.002, -57.750] | -62.5 % | **CHANGED** |
| fight:account_manager@t4 | dealt_per_turn | 10.642 | 5.643 | -4.999 | [-6.540, -3.426] | -47.0 % | **CHANGED** |
| fight:account_manager@t4 | enrage_step | 1.300 | 0.450 | -0.850 | [-1.350, -0.350] | -65.4 % | **CHANGED** |
| fight:account_manager@t4 | intake | 49.500 | 54.600 | +5.100 | [+1.250, +9.200] | +10.3 % | **CHANGED** |
| fight:account_manager@t4 | perfect_rate | 0.556 | 0.327 | -0.229 | [-0.297, -0.156] | -41.3 % | **CHANGED** |
| fight:account_manager@t4 | ram_left_per_turn | 8.982 | 9.397 | +0.415 | [+0.011, +0.844] | +4.6 % | **CHANGED** |
| fight:account_manager@t4 | resistance_absorbed | 13.300 | 8.400 | -4.900 | [-7.850, -1.700] | -36.8 % | **CHANGED** |
| fight:account_manager@t4 | taken_per_turn | 5.620 | 8.579 | +2.959 | [+0.989, +5.006] | +52.6 % | **CHANGED** |
| fight:account_manager@t4 | turns | 13.300 | 8.800 | -4.500 | [-7.003, -2.050] | -33.8 % | **CHANGED** |
| fight:billing_daemon@t1 | combat_hash | 1938476090.250 | 2700574610.400 | +762098520.150 | [+209203508.587, +1284444804.907] | +39.3 % | **CHANGED** |
| fight:billing_daemon@t1 | dealt_per_turn | 14.125 | 8.998 | -5.127 | [-7.977, -2.167] | -36.3 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_end | 51.150 | 33.800 | -17.350 | [-23.650, -11.495] | -33.9 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_lost | 8.850 | 26.200 | +17.350 | [+11.250, +23.302] | +196.0 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_lost_frac | 0.148 | 0.437 | +0.289 | [+0.192, +0.392] | +196.0 % | **CHANGED** |
| fight:billing_daemon@t1 | intake | 8.550 | 25.750 | +17.200 | [+11.550, +23.250] | +201.2 % | **CHANGED** |
| fight:billing_daemon@t1 | perfect_rate | 0.676 | 0.471 | -0.204 | [-0.310, -0.099] | -30.3 % | **CHANGED** |
| fight:billing_daemon@t1 | ram_left_per_turn | 5.716 | 7.806 | +2.091 | [+0.976, +3.265] | +36.6 % | **CHANGED** |
| fight:billing_daemon@t1 | resistance_absorbed | 2.000 | 2.850 | +0.850 | [+0.150, +1.600] | +42.5 % | **CHANGED** |
| fight:billing_daemon@t1 | taken | 8.850 | 26.200 | +17.350 | [+11.900, +23.450] | +196.0 % | **CHANGED** |
| fight:billing_daemon@t1 | taken_per_turn | 2.667 | 4.146 | +1.478 | [+0.614, +2.324] | +55.4 % | **CHANGED** |
| fight:billing_daemon@t1 | turns | 3.450 | 6.500 | +3.050 | [+1.700, +4.500] | +88.4 % | **CHANGED** |
| fight:billing_daemon@t1 | turns_both_share | 0.448 | 0.222 | -0.225 | [-0.343, -0.112] | -50.4 % | **CHANGED** |
| fight:billing_daemon@t2 | dealt | 67.000 | 60.050 | -6.950 | [-11.750, -2.800] | -10.4 % | **CHANGED** |
| fight:billing_daemon@t2 | dealt_per_turn | 12.919 | 6.836 | -6.083 | [-7.592, -4.431] | -47.1 % | **CHANGED** |
| fight:billing_daemon@t2 | died | 0.000 | 0.400 | +0.400 | [+0.200, +0.550] | - | **CHANGED** |
| fight:billing_daemon@t2 | hp_end | 45.650 | 12.200 | -33.450 | [-39.803, -26.250] | -73.3 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_lost | 14.350 | 47.800 | +33.450 | [+26.600, +39.553] | +233.1 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_lost_frac | 0.239 | 0.797 | +0.558 | [+0.441, +0.666] | +233.1 % | **CHANGED** |
| fight:billing_daemon@t2 | intake | 14.050 | 45.700 | +31.650 | [+24.750, +38.403] | +225.3 % | **CHANGED** |
| fight:billing_daemon@t2 | perfect_rate | 0.721 | 0.392 | -0.329 | [-0.424, -0.235] | -45.6 % | **CHANGED** |
| fight:billing_daemon@t2 | ram_left_per_turn | 7.171 | 8.796 | +1.624 | [+0.738, +2.469] | +22.6 % | **CHANGED** |
| fight:billing_daemon@t2 | resistance_absorbed | 2.700 | 4.150 | +1.450 | [+0.550, +2.250] | +53.7 % | **CHANGED** |
| fight:billing_daemon@t2 | taken | 14.350 | 47.800 | +33.450 | [+26.800, +40.050] | +233.1 % | **CHANGED** |
| fight:billing_daemon@t2 | taken_per_turn | 2.579 | 4.978 | +2.399 | [+1.608, +3.151] | +93.0 % | **CHANGED** |
| fight:billing_daemon@t2 | turns | 5.700 | 9.650 | +3.950 | [+2.650, +5.150] | +69.3 % | **CHANGED** |
| fight:billing_daemon@t2 | turns_both_share | 0.356 | 0.227 | -0.130 | [-0.208, -0.054] | -36.4 % | **CHANGED** |
| fight:billing_daemon@t2 | won | 1.000 | 0.600 | -0.400 | [-0.550, -0.250] | -40.0 % | **CHANGED** |
| fight:billing_daemon@t3 | combat_hash | 1683331544.800 | 2510404803.200 | +827073258.400 | [+174708078.987, +1456286470.215] | +49.1 % | **CHANGED** |
| fight:billing_daemon@t3 | dealt | 106.950 | 63.950 | -43.000 | [-53.000, -32.648] | -40.2 % | **CHANGED** |
| fight:billing_daemon@t3 | dealt_per_turn | 11.200 | 6.944 | -4.256 | [-5.591, -2.881] | -38.0 % | **CHANGED** |
| fight:billing_daemon@t3 | died | 0.150 | 0.950 | +0.800 | [+0.650, +0.950] | +533.3 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_end | 26.350 | 0.500 | -25.850 | [-31.353, -19.450] | -98.1 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_lost | 33.650 | 59.500 | +25.850 | [+19.950, +31.650] | +76.8 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_lost_frac | 0.561 | 0.992 | +0.431 | [+0.334, +0.522] | +76.8 % | **CHANGED** |
| fight:billing_daemon@t3 | intake | 31.250 | 57.200 | +25.950 | [+20.350, +31.500] | +83.0 % | **CHANGED** |
| fight:billing_daemon@t3 | perfect_rate | 0.668 | 0.385 | -0.282 | [-0.375, -0.194] | -42.3 % | **CHANGED** |
| fight:billing_daemon@t3 | ram_left_per_turn | 7.706 | 8.536 | +0.830 | [+0.004, +1.670] | +10.8 % | **CHANGED** |
| fight:billing_daemon@t3 | resistance_absorbed | 5.550 | 4.350 | -1.200 | [-2.100, -0.250] | -21.6 % | **CHANGED** |
| fight:billing_daemon@t3 | taken | 33.650 | 59.500 | +25.850 | [+20.348, +31.500] | +76.8 % | **CHANGED** |
| fight:billing_daemon@t3 | taken_per_turn | 3.328 | 6.715 | +3.387 | [+2.662, +4.139] | +101.7 % | **CHANGED** |
| fight:billing_daemon@t3 | turns_both_share | 0.422 | 0.245 | -0.177 | [-0.262, -0.094] | -42.0 % | **CHANGED** |
| fight:billing_daemon@t3 | won | 0.850 | 0.050 | -0.800 | [-0.950, -0.650] | -94.1 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt | 138.650 | 50.850 | -87.800 | [-102.705, -72.443] | -63.3 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 11.519 | 6.442 | -5.077 | [-6.712, -3.355] | -44.1 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.700 | 1.000 | +0.300 | [+0.150, +0.450] | +42.9 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_end | 5.350 | 0.000 | -5.350 | [-9.100, -2.200] | -100.0 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_lost | 54.650 | 60.000 | +5.350 | [+2.200, +9.000] | +9.8 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_lost_frac | 0.911 | 1.000 | +0.089 | [+0.037, +0.151] | +9.8 % | **CHANGED** |
| fight:billing_daemon@t4 | intake | 51.200 | 59.400 | +8.200 | [+4.650, +12.150] | +16.0 % | **CHANGED** |
| fight:billing_daemon@t4 | perfect_rate | 0.638 | 0.320 | -0.318 | [-0.418, -0.225] | -49.9 % | **CHANGED** |
| fight:billing_daemon@t4 | resistance_absorbed | 6.600 | 3.800 | -2.800 | [-3.800, -1.700] | -42.4 % | **CHANGED** |
| fight:billing_daemon@t4 | taken | 54.650 | 60.000 | +5.350 | [+2.100, +9.000] | +9.8 % | **CHANGED** |
| fight:billing_daemon@t4 | taken_per_turn | 4.687 | 8.581 | +3.894 | [+2.626, +5.344] | +83.1 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 12.500 | 7.800 | -4.700 | [-6.050, -3.300] | -37.6 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.383 | 0.216 | -0.167 | [-0.247, -0.086] | -43.6 % | **CHANGED** |
| fight:billing_daemon@t4 | won | 0.300 | 0.000 | -0.300 | [-0.450, -0.150] | -100.0 % | **CHANGED** |
| fight:care_swarm@t1 | dealt | 25.000 | 27.750 | +2.750 | [+1.400, +4.300] | +11.0 % | **CHANGED** |
| fight:care_swarm@t1 | dealt_per_turn | 8.998 | 5.700 | -3.298 | [-6.185, -0.448] | -36.7 % | **CHANGED** |
| fight:care_swarm@t1 | heal_total | 1.100 | 5.400 | +4.300 | [+2.200, +6.500] | +390.9 % | **CHANGED** |
| fight:care_swarm@t1 | heal_turns | 0.450 | 1.650 | +1.200 | [+0.550, +1.900] | +266.7 % | **CHANGED** |
| fight:care_swarm@t1 | hp_end | 42.700 | 29.450 | -13.250 | [-18.700, -7.900] | -31.0 % | **CHANGED** |
| fight:care_swarm@t1 | hp_lost | 17.300 | 30.550 | +13.250 | [+7.850, +18.453] | +76.6 % | **CHANGED** |
| fight:care_swarm@t1 | hp_lost_frac | 0.288 | 0.509 | +0.221 | [+0.128, +0.303] | +76.6 % | **CHANGED** |
| fight:care_swarm@t1 | intake | 17.300 | 30.550 | +13.250 | [+7.750, +18.300] | +76.6 % | **CHANGED** |
| fight:care_swarm@t1 | perfect_rate | 0.639 | 0.384 | -0.255 | [-0.379, -0.137] | -40.0 % | **CHANGED** |
| fight:care_swarm@t1 | ram_left_per_turn | 6.867 | 8.614 | +1.747 | [+0.498, +2.835] | +25.4 % | **CHANGED** |
| fight:care_swarm@t1 | resistance_absorbed | 1.400 | 2.800 | +1.400 | [+0.650, +2.150] | +100.0 % | **CHANGED** |
| fight:care_swarm@t1 | taken | 17.300 | 30.550 | +13.250 | [+7.897, +18.250] | +76.6 % | **CHANGED** |
| fight:care_swarm@t1 | turns | 3.900 | 6.800 | +2.900 | [+1.400, +4.400] | +74.4 % | **CHANGED** |
| fight:care_swarm@t2 | dealt_per_turn | 7.917 | 5.496 | -2.421 | [-4.409, -0.270] | -30.6 % | **CHANGED** |
| fight:care_swarm@t2 | heal_total | 4.800 | 9.150 | +4.350 | [+0.700, +8.052] | +90.6 % | **CHANGED** |
| fight:care_swarm@t2 | heal_turns | 1.100 | 2.300 | +1.200 | [+0.300, +2.100] | +109.1 % | **CHANGED** |
| fight:care_swarm@t2 | hp_end | 22.700 | 11.950 | -10.750 | [-18.050, -3.298] | -47.4 % | **CHANGED** |
| fight:care_swarm@t2 | hp_lost | 37.300 | 48.050 | +10.750 | [+3.497, +17.900] | +28.8 % | **CHANGED** |
| fight:care_swarm@t2 | hp_lost_frac | 0.622 | 0.801 | +0.179 | [+0.052, +0.296] | +28.8 % | **CHANGED** |
| fight:care_swarm@t2 | intake | 36.850 | 48.050 | +11.200 | [+3.550, +18.250] | +30.4 % | **CHANGED** |
| fight:care_swarm@t2 | perfect_rate | 0.580 | 0.326 | -0.254 | [-0.344, -0.158] | -43.8 % | **CHANGED** |
| fight:care_swarm@t2 | ram_left_per_turn | 7.787 | 9.158 | +1.370 | [+0.366, +2.392] | +17.6 % | **CHANGED** |
| fight:care_swarm@t2 | resistance_absorbed | 2.300 | 3.800 | +1.500 | [+0.697, +2.300] | +65.2 % | **CHANGED** |
| fight:care_swarm@t2 | taken | 37.300 | 48.050 | +10.750 | [+3.197, +17.750] | +28.8 % | **CHANGED** |
| fight:care_swarm@t2 | turns | 6.250 | 9.000 | +2.750 | [+0.900, +4.700] | +44.0 % | **CHANGED** |
| fight:care_swarm@t3 | dealt | 53.350 | 26.200 | -27.150 | [-36.700, -17.648] | -50.9 % | **CHANGED** |
| fight:care_swarm@t3 | dealt_per_turn | 7.572 | 3.756 | -3.817 | [-5.497, -2.180] | -50.4 % | **CHANGED** |
| fight:care_swarm@t3 | died | 0.600 | 1.000 | +0.400 | [+0.250, +0.600] | +66.7 % | **CHANGED** |
| fight:care_swarm@t3 | hp_end | 6.600 | 0.000 | -6.600 | [-10.550, -3.000] | -100.0 % | **CHANGED** |
| fight:care_swarm@t3 | hp_lost | 53.400 | 60.000 | +6.600 | [+3.150, +10.652] | +12.4 % | **CHANGED** |
| fight:care_swarm@t3 | hp_lost_frac | 0.890 | 1.000 | +0.110 | [+0.056, +0.174] | +12.4 % | **CHANGED** |
| fight:care_swarm@t3 | intake | 52.650 | 59.600 | +6.950 | [+3.550, +10.950] | +13.2 % | **CHANGED** |
| fight:care_swarm@t3 | perfect_rate | 0.579 | 0.286 | -0.293 | [-0.391, -0.196] | -50.6 % | **CHANGED** |
| fight:care_swarm@t3 | taken | 53.400 | 60.000 | +6.600 | [+3.047, +10.302] | +12.4 % | **CHANGED** |
| fight:care_swarm@t3 | taken_per_turn | 7.357 | 8.873 | +1.516 | [+0.504, +2.664] | +20.6 % | **CHANGED** |
| fight:care_swarm@t3 | won | 0.400 | 0.000 | -0.400 | [-0.600, -0.250] | -100.0 % | **CHANGED** |
| fight:care_swarm@t4 | dealt | 46.200 | 22.000 | -24.200 | [-34.250, -14.100] | -52.4 % | **CHANGED** |
| fight:care_swarm@t4 | dealt_per_turn | 8.188 | 4.481 | -3.707 | [-5.746, -1.520] | -45.3 % | **CHANGED** |
| fight:care_swarm@t4 | perfect_rate | 0.587 | 0.303 | -0.284 | [-0.383, -0.186] | -48.4 % | **CHANGED** |
| fight:care_swarm@t4 | taken_per_turn | 10.797 | 12.807 | +2.009 | [+0.594, +3.446] | +18.6 % | **CHANGED** |
| fight:care_swarm@t4 | turns | 5.900 | 4.900 | -1.000 | [-1.650, -0.350] | -16.9 % | **CHANGED** |
| fight:claims_adjuster@t1 | dealt | 112.000 | 90.400 | -21.600 | [-33.205, -11.000] | -19.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | dealt_per_turn | 28.395 | 17.132 | -11.264 | [-16.957, -5.461] | -39.7 % | **CHANGED** |
| fight:claims_adjuster@t1 | died | 0.000 | 0.450 | +0.450 | [+0.250, +0.650] | - | **CHANGED** |
| fight:claims_adjuster@t1 | enrage_step | 0.050 | 0.250 | +0.200 | [+0.050, +0.400] | +400.0 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_end | 30.950 | 10.800 | -20.150 | [-27.000, -13.298] | -65.1 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost | 29.050 | 49.200 | +20.150 | [+13.447, +26.800] | +69.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost_frac | 0.484 | 0.820 | +0.336 | [+0.220, +0.448] | +69.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | intake | 26.800 | 46.700 | +19.900 | [+12.500, +26.550] | +74.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | perfect_rate | 0.662 | 0.408 | -0.254 | [-0.361, -0.138] | -38.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | ram_left_per_turn | 7.107 | 8.898 | +1.791 | [+0.691, +2.933] | +25.2 % | **CHANGED** |
| fight:claims_adjuster@t1 | taken | 29.050 | 49.200 | +20.150 | [+13.450, +26.852] | +69.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | taken_per_turn | 6.680 | 8.235 | +1.555 | [+0.364, +2.760] | +23.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns | 4.500 | 6.050 | +1.550 | [+0.700, +2.450] | +34.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns_both_share | 0.311 | 0.203 | -0.107 | [-0.201, -0.017] | -34.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | won | 1.000 | 0.550 | -0.450 | [-0.650, -0.250] | -45.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | dealt | 160.300 | 100.000 | -60.300 | [-82.355, -37.045] | -37.6 % | **CHANGED** |
| fight:claims_adjuster@t2 | dealt_per_turn | 24.977 | 15.016 | -9.961 | [-13.605, -6.041] | -39.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | died | 0.500 | 0.950 | +0.450 | [+0.250, +0.650] | +90.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_end | 11.350 | 0.450 | -10.900 | [-16.400, -5.850] | -96.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost | 48.650 | 59.550 | +10.900 | [+5.600, +16.352] | +22.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost_frac | 0.811 | 0.993 | +0.182 | [+0.093, +0.276] | +22.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | intake | 43.100 | 56.400 | +13.300 | [+7.550, +19.505] | +30.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | perfect_rate | 0.626 | 0.310 | -0.316 | [-0.414, -0.214] | -50.5 % | **CHANGED** |
| fight:claims_adjuster@t2 | ram_left_per_turn | 8.092 | 9.132 | +1.040 | [+0.325, +1.769] | +12.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | taken | 48.650 | 59.550 | +10.900 | [+5.847, +16.600] | +22.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | taken_per_turn | 7.344 | 10.628 | +3.284 | [+1.544, +5.125] | +44.7 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns_both_share | 0.335 | 0.173 | -0.162 | [-0.255, -0.069] | -48.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | won | 0.500 | 0.050 | -0.450 | [-0.650, -0.250] | -90.0 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt | 167.900 | 64.150 | -103.750 | [-134.707, -71.398] | -61.8 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt_per_turn | 26.787 | 13.851 | -12.936 | [-17.245, -8.641] | -48.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | enrage_step | 0.300 | 0.000 | -0.300 | [-0.500, -0.100] | -100.0 % | **CHANGED** |
| fight:claims_adjuster@t3 | intake | 53.350 | 58.850 | +5.500 | [+2.100, +9.750] | +10.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | perfect_rate | 0.639 | 0.296 | -0.342 | [-0.440, -0.242] | -53.6 % | **CHANGED** |
| fight:claims_adjuster@t3 | resistance_absorbed | 7.100 | 4.000 | -3.100 | [-5.653, -0.700] | -43.7 % | **CHANGED** |
| fight:claims_adjuster@t3 | taken_per_turn | 10.455 | 16.185 | +5.730 | [+2.723, +8.772] | +54.8 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns | 6.300 | 4.400 | -1.900 | [-3.003, -0.950] | -30.2 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt | 141.150 | 56.750 | -84.400 | [-120.953, -52.400] | -59.8 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt_per_turn | 25.920 | 14.232 | -11.688 | [-16.075, -7.399] | -45.1 % | **CHANGED** |
| fight:claims_adjuster@t4 | enrage_step | 0.300 | 0.000 | -0.300 | [-0.500, -0.100] | -100.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | intake | 56.700 | 59.250 | +2.550 | [+1.050, +4.350] | +4.5 % | **CHANGED** |
| fight:claims_adjuster@t4 | perfect_rate | 0.608 | 0.303 | -0.304 | [-0.404, -0.199] | -50.1 % | **CHANGED** |
| fight:claims_adjuster@t4 | resistance_absorbed | 6.350 | 2.650 | -3.700 | [-6.303, -1.450] | -58.3 % | **CHANGED** |
| fight:claims_adjuster@t4 | taken_per_turn | 13.007 | 18.100 | +5.093 | [+1.974, +8.222] | +39.2 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns | 5.550 | 3.800 | -1.750 | [-2.950, -0.700] | -31.5 % | **CHANGED** |
| fight:collections_agent@t1 | dealt_per_turn | 11.818 | 8.599 | -3.219 | [-5.485, -0.919] | -27.2 % | **CHANGED** |
| fight:collections_agent@t1 | hp_end | 49.800 | 32.400 | -17.400 | [-24.550, -10.300] | -34.9 % | **CHANGED** |
| fight:collections_agent@t1 | hp_lost | 10.200 | 27.600 | +17.400 | [+10.147, +24.750] | +170.6 % | **CHANGED** |
| fight:collections_agent@t1 | hp_lost_frac | 0.170 | 0.460 | +0.290 | [+0.172, +0.407] | +170.6 % | **CHANGED** |
| fight:collections_agent@t1 | intake | 9.900 | 25.800 | +15.900 | [+9.647, +22.352] | +160.6 % | **CHANGED** |
| fight:collections_agent@t1 | perfect_rate | 0.656 | 0.474 | -0.181 | [-0.311, -0.052] | -27.6 % | **CHANGED** |
| fight:collections_agent@t1 | ram_left_per_turn | 7.104 | 8.583 | +1.479 | [+0.661, +2.292] | +20.8 % | **CHANGED** |
| fight:collections_agent@t1 | resistance_absorbed | 1.650 | 2.500 | +0.850 | [+0.150, +1.500] | +51.5 % | **CHANGED** |
| fight:collections_agent@t1 | taken | 10.200 | 27.600 | +17.400 | [+10.200, +24.550] | +170.6 % | **CHANGED** |
| fight:collections_agent@t1 | taken_per_turn | 2.650 | 4.516 | +1.866 | [+0.823, +2.917] | +70.4 % | **CHANGED** |
| fight:collections_agent@t1 | turns | 3.750 | 6.100 | +2.350 | [+1.150, +3.650] | +62.7 % | **CHANGED** |
| fight:collections_agent@t2 | dealt | 64.000 | 57.000 | -7.000 | [-11.650, -2.600] | -10.9 % | **CHANGED** |
| fight:collections_agent@t2 | dealt_per_turn | 12.975 | 9.220 | -3.755 | [-6.193, -1.340] | -28.9 % | **CHANGED** |
| fight:collections_agent@t2 | died | 0.000 | 0.450 | +0.450 | [+0.300, +0.650] | - | **CHANGED** |
| fight:collections_agent@t2 | hp_end | 40.400 | 15.650 | -24.750 | [-31.903, -17.248] | -61.3 % | **CHANGED** |
| fight:collections_agent@t2 | hp_lost | 19.600 | 44.350 | +24.750 | [+16.700, +32.200] | +126.3 % | **CHANGED** |
| fight:collections_agent@t2 | hp_lost_frac | 0.327 | 0.739 | +0.413 | [+0.284, +0.533] | +126.3 % | **CHANGED** |
| fight:collections_agent@t2 | intake | 17.950 | 41.150 | +23.200 | [+15.450, +30.252] | +129.2 % | **CHANGED** |
| fight:collections_agent@t2 | perfect_rate | 0.686 | 0.432 | -0.254 | [-0.366, -0.144] | -37.0 % | **CHANGED** |
| fight:collections_agent@t2 | ram_left_per_turn | 7.737 | 8.898 | +1.161 | [+0.405, +1.919] | +15.0 % | **CHANGED** |
| fight:collections_agent@t2 | taken | 19.600 | 44.350 | +24.750 | [+17.000, +32.252] | +126.3 % | **CHANGED** |
| fight:collections_agent@t2 | taken_per_turn | 3.574 | 6.065 | +2.491 | [+1.389, +3.751] | +69.7 % | **CHANGED** |
| fight:collections_agent@t2 | turns | 5.400 | 7.650 | +2.250 | [+1.100, +3.450] | +41.7 % | **CHANGED** |
| fight:collections_agent@t2 | won | 1.000 | 0.550 | -0.450 | [-0.650, -0.250] | -45.0 % | **CHANGED** |
| fight:collections_agent@t3 | dealt | 96.300 | 57.300 | -39.000 | [-50.555, -27.400] | -40.5 % | **CHANGED** |
| fight:collections_agent@t3 | dealt_per_turn | 12.422 | 6.964 | -5.458 | [-7.218, -3.697] | -43.9 % | **CHANGED** |
| fight:collections_agent@t3 | died | 0.350 | 0.950 | +0.600 | [+0.400, +0.800] | +171.4 % | **CHANGED** |
| fight:collections_agent@t3 | hp_end | 18.900 | 1.350 | -17.550 | [-24.250, -10.600] | -92.9 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost | 41.100 | 58.650 | +17.550 | [+10.950, +24.302] | +42.7 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost_frac | 0.685 | 0.978 | +0.293 | [+0.180, +0.408] | +42.7 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 36.750 | 54.250 | +17.500 | [+11.000, +23.650] | +47.6 % | **CHANGED** |
| fight:collections_agent@t3 | perfect_rate | 0.622 | 0.312 | -0.310 | [-0.394, -0.227] | -49.9 % | **CHANGED** |
| fight:collections_agent@t3 | ram_left_per_turn | 8.473 | 9.320 | +0.847 | [+0.422, +1.280] | +10.0 % | **CHANGED** |
| fight:collections_agent@t3 | taken | 41.100 | 58.650 | +17.550 | [+10.650, +24.300] | +42.7 % | **CHANGED** |
| fight:collections_agent@t3 | taken_per_turn | 4.938 | 7.700 | +2.762 | [+1.655, +3.926] | +55.9 % | **CHANGED** |
| fight:collections_agent@t3 | won | 0.650 | 0.050 | -0.600 | [-0.800, -0.400] | -92.3 % | **CHANGED** |
| fight:collections_agent@t4 | dealt | 115.150 | 43.300 | -71.850 | [-90.703, -53.050] | -62.4 % | **CHANGED** |
| fight:collections_agent@t4 | dealt_per_turn | 12.533 | 6.186 | -6.347 | [-8.321, -4.480] | -50.6 % | **CHANGED** |
| fight:collections_agent@t4 | died | 0.750 | 1.000 | +0.250 | [+0.100, +0.400] | +33.3 % | **CHANGED** |
| fight:collections_agent@t4 | hp_end | 2.100 | 0.000 | -2.100 | [-4.200, -0.450] | -100.0 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost | 57.900 | 60.000 | +2.100 | [+0.500, +4.250] | +3.6 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost_frac | 0.965 | 1.000 | +0.035 | [+0.007, +0.071] | +3.6 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 52.350 | 56.700 | +4.350 | [+1.497, +7.350] | +8.3 % | **CHANGED** |
| fight:collections_agent@t4 | perfect_rate | 0.662 | 0.309 | -0.353 | [-0.448, -0.257] | -53.4 % | **CHANGED** |
| fight:collections_agent@t4 | ram_left_per_turn | 8.143 | 8.810 | +0.666 | [+0.029, +1.336] | +8.2 % | **CHANGED** |
| fight:collections_agent@t4 | resistance_absorbed | 4.500 | 3.100 | -1.400 | [-2.400, -0.350] | -31.1 % | **CHANGED** |
| fight:collections_agent@t4 | taken | 57.900 | 60.000 | +2.100 | [+0.450, +4.203] | +3.6 % | **CHANGED** |
| fight:collections_agent@t4 | taken_per_turn | 7.136 | 11.498 | +4.363 | [+1.995, +6.845] | +61.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 9.100 | 6.500 | -2.600 | [-4.050, -1.150] | -28.6 % | **CHANGED** |
| fight:collections_agent@t4 | turns_both_share | 0.330 | 0.204 | -0.125 | [-0.224, -0.027] | -38.1 % | **CHANGED** |
| fight:collections_agent@t4 | won | 0.250 | 0.000 | -0.250 | [-0.400, -0.100] | -100.0 % | **CHANGED** |
| fight:compliance_officer@t1 | dealt_per_turn | 13.554 | 7.311 | -6.242 | [-8.659, -3.830] | -46.1 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_end | 49.400 | 28.300 | -21.100 | [-27.550, -14.847] | -42.7 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_lost | 10.600 | 31.700 | +21.100 | [+14.750, +27.500] | +199.1 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_lost_frac | 0.177 | 0.528 | +0.352 | [+0.245, +0.466] | +199.1 % | **CHANGED** |
| fight:compliance_officer@t1 | intake | 10.150 | 30.950 | +20.800 | [+14.250, +27.052] | +204.9 % | **CHANGED** |
| fight:compliance_officer@t1 | perfect_rate | 0.720 | 0.414 | -0.306 | [-0.415, -0.202] | -42.5 % | **CHANGED** |
| fight:compliance_officer@t1 | ram_left_per_turn | 6.989 | 8.823 | +1.835 | [+0.825, +2.770] | +26.3 % | **CHANGED** |
| fight:compliance_officer@t1 | resistance_absorbed | 3.800 | 6.000 | +2.200 | [+1.050, +3.450] | +57.9 % | **CHANGED** |
| fight:compliance_officer@t1 | taken | 10.600 | 31.700 | +21.100 | [+14.700, +27.652] | +199.1 % | **CHANGED** |
| fight:compliance_officer@t1 | taken_per_turn | 2.545 | 3.829 | +1.284 | [+0.567, +2.016] | +50.4 % | **CHANGED** |
| fight:compliance_officer@t1 | turns | 4.300 | 8.200 | +3.900 | [+2.500, +5.250] | +90.7 % | **CHANGED** |
| fight:compliance_officer@t1 | turns_both_share | 0.348 | 0.214 | -0.134 | [-0.222, -0.036] | -38.5 % | **CHANGED** |
| fight:compliance_officer@t2 | dealt | 80.000 | 68.900 | -11.100 | [-17.453, -5.000] | -13.9 % | **CHANGED** |
| fight:compliance_officer@t2 | dealt_per_turn | 12.842 | 7.377 | -5.465 | [-6.996, -3.810] | -42.6 % | **CHANGED** |
| fight:compliance_officer@t2 | died | 0.000 | 0.400 | +0.400 | [+0.200, +0.600] | - | **CHANGED** |
| fight:compliance_officer@t2 | hp_end | 40.450 | 11.800 | -28.650 | [-35.155, -21.800] | -70.8 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_lost | 19.550 | 48.200 | +28.650 | [+21.797, +35.650] | +146.5 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_lost_frac | 0.326 | 0.803 | +0.478 | [+0.360, +0.585] | +146.5 % | **CHANGED** |
| fight:compliance_officer@t2 | intake | 17.900 | 46.250 | +28.350 | [+21.197, +34.602] | +158.4 % | **CHANGED** |
| fight:compliance_officer@t2 | perfect_rate | 0.738 | 0.436 | -0.301 | [-0.391, -0.206] | -40.9 % | **CHANGED** |
| fight:compliance_officer@t2 | ram_left_per_turn | 8.141 | 9.438 | +1.296 | [+0.650, +2.000] | +15.9 % | **CHANGED** |
| fight:compliance_officer@t2 | resistance_absorbed | 4.800 | 7.100 | +2.300 | [+1.050, +3.550] | +47.9 % | **CHANGED** |
| fight:compliance_officer@t2 | taken | 19.550 | 48.200 | +28.650 | [+21.500, +35.100] | +146.5 % | **CHANGED** |
| fight:compliance_officer@t2 | taken_per_turn | 2.932 | 4.800 | +1.868 | [+1.089, +2.691] | +63.7 % | **CHANGED** |
| fight:compliance_officer@t2 | turns | 6.550 | 10.350 | +3.800 | [+2.600, +5.000] | +58.0 % | **CHANGED** |
| fight:compliance_officer@t2 | turns_both_share | 0.282 | 0.178 | -0.104 | [-0.170, -0.042] | -37.0 % | **CHANGED** |
| fight:compliance_officer@t2 | won | 1.000 | 0.600 | -0.400 | [-0.600, -0.250] | -40.0 % | **CHANGED** |
| fight:compliance_officer@t3 | dealt | 124.200 | 69.350 | -54.850 | [-67.650, -41.200] | -44.2 % | **CHANGED** |
| fight:compliance_officer@t3 | dealt_per_turn | 11.985 | 7.104 | -4.880 | [-6.311, -3.453] | -40.7 % | **CHANGED** |
| fight:compliance_officer@t3 | died | 0.400 | 0.950 | +0.550 | [+0.350, +0.750] | +137.5 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_end | 15.700 | 0.150 | -15.550 | [-22.253, -9.348] | -99.0 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost | 44.300 | 59.850 | +15.550 | [+9.098, +22.150] | +35.1 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost_frac | 0.738 | 0.997 | +0.259 | [+0.152, +0.365] | +35.1 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 40.100 | 57.900 | +17.800 | [+11.300, +24.252] | +44.4 % | **CHANGED** |
| fight:compliance_officer@t3 | perfect_rate | 0.687 | 0.385 | -0.302 | [-0.402, -0.213] | -44.0 % | **CHANGED** |
| fight:compliance_officer@t3 | ram_left_per_turn | 8.581 | 9.221 | +0.640 | [+0.101, +1.170] | +7.5 % | **CHANGED** |
| fight:compliance_officer@t3 | taken | 44.300 | 59.850 | +15.550 | [+9.150, +22.500] | +35.1 % | **CHANGED** |
| fight:compliance_officer@t3 | taken_per_turn | 4.179 | 6.705 | +2.526 | [+1.538, +3.603] | +60.4 % | **CHANGED** |
| fight:compliance_officer@t3 | turns_both_share | 0.327 | 0.224 | -0.103 | [-0.182, -0.024] | -31.4 % | **CHANGED** |
| fight:compliance_officer@t3 | won | 0.600 | 0.050 | -0.550 | [-0.750, -0.350] | -91.7 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt | 134.400 | 49.350 | -85.050 | [-103.752, -66.395] | -63.3 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt_per_turn | 11.430 | 6.115 | -5.314 | [-6.709, -3.829] | -46.5 % | **CHANGED** |
| fight:compliance_officer@t4 | died | 0.850 | 1.000 | +0.150 | [+0.050, +0.300] | +17.6 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_end | 0.700 | 0.000 | -0.700 | [-1.400, -0.150] | -100.0 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost | 59.300 | 60.000 | +0.700 | [+0.150, +1.400] | +1.2 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost_frac | 0.988 | 1.000 | +0.012 | [+0.003, +0.023] | +1.2 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 55.200 | 59.250 | +4.050 | [+2.550, +5.602] | +7.3 % | **CHANGED** |
| fight:compliance_officer@t4 | perfect_rate | 0.651 | 0.343 | -0.307 | [-0.397, -0.218] | -47.2 % | **CHANGED** |
| fight:compliance_officer@t4 | resistance_absorbed | 10.200 | 6.700 | -3.500 | [-5.450, -1.550] | -34.3 % | **CHANGED** |
| fight:compliance_officer@t4 | taken | 59.300 | 60.000 | +0.700 | [+0.150, +1.450] | +1.2 % | **CHANGED** |
| fight:compliance_officer@t4 | taken_per_turn | 5.438 | 8.420 | +2.982 | [+1.642, +4.346] | +54.8 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 11.750 | 7.950 | -3.800 | [-5.200, -2.400] | -32.3 % | **CHANGED** |
| fight:compliance_officer@t4 | won | 0.150 | 0.000 | -0.150 | [-0.300, -0.050] | -100.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | dealt_per_turn | 12.889 | 8.829 | -4.059 | [-6.258, -1.692] | -31.5 % | **CHANGED** |
| fight:dosage_dispenser@t1 | hp_end | 57.900 | 53.550 | -4.350 | [-7.150, -1.648] | -7.5 % | **CHANGED** |
| fight:dosage_dispenser@t1 | hp_lost | 2.100 | 6.450 | +4.350 | [+1.700, +7.050] | +207.1 % | **CHANGED** |
| fight:dosage_dispenser@t1 | hp_lost_frac | 0.035 | 0.108 | +0.073 | [+0.027, +0.118] | +207.2 % | **CHANGED** |
| fight:dosage_dispenser@t1 | intake | 1.350 | 4.950 | +3.600 | [+1.450, +5.900] | +266.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | perfect_rate | 0.615 | 0.414 | -0.201 | [-0.329, -0.074] | -32.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | ram_left_per_turn | 6.792 | 8.402 | +1.610 | [+0.705, +2.458] | +23.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | resistance_absorbed | 1.050 | 1.750 | +0.700 | [+0.150, +1.250] | +66.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | taken | 2.100 | 6.450 | +4.350 | [+1.750, +7.000] | +207.1 % | **CHANGED** |
| fight:dosage_dispenser@t1 | taken_per_turn | 0.505 | 1.045 | +0.540 | [+0.097, +0.962] | +106.9 % | **CHANGED** |
| fight:dosage_dispenser@t1 | turns | 3.350 | 5.400 | +2.050 | [+1.050, +3.100] | +61.2 % | **CHANGED** |
| fight:dosage_dispenser@t2 | dealt_per_turn | 13.993 | 8.686 | -5.306 | [-7.363, -3.155] | -37.9 % | **CHANGED** |
| fight:dosage_dispenser@t2 | hp_end | 55.100 | 44.100 | -11.000 | [-15.953, -6.200] | -20.0 % | **CHANGED** |
| fight:dosage_dispenser@t2 | hp_lost | 4.900 | 15.900 | +11.000 | [+5.950, +15.950] | +224.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | hp_lost_frac | 0.082 | 0.265 | +0.183 | [+0.102, +0.266] | +224.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | intake | 2.800 | 11.100 | +8.300 | [+4.450, +12.800] | +296.4 % | **CHANGED** |
| fight:dosage_dispenser@t2 | perfect_rate | 0.663 | 0.407 | -0.256 | [-0.349, -0.163] | -38.6 % | **CHANGED** |
| fight:dosage_dispenser@t2 | ram_left_per_turn | 7.423 | 9.017 | +1.593 | [+0.729, +2.398] | +21.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | resistance_absorbed | 1.750 | 3.250 | +1.500 | [+0.850, +2.200] | +85.7 % | **CHANGED** |
| fight:dosage_dispenser@t2 | taken | 4.900 | 15.900 | +11.000 | [+6.000, +16.050] | +224.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | taken_per_turn | 0.997 | 1.665 | +0.668 | [+0.132, +1.164] | +67.0 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns | 4.700 | 8.550 | +3.850 | [+2.450, +5.350] | +81.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | dealt | 97.000 | 94.700 | -2.300 | [-4.600, -0.550] | -2.4 % | **CHANGED** |
| fight:dosage_dispenser@t3 | dealt_per_turn | 13.823 | 8.321 | -5.502 | [-7.009, -4.006] | -39.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | died | 0.000 | 0.150 | +0.150 | [+0.050, +0.300] | - | **CHANGED** |
| fight:dosage_dispenser@t3 | hp_end | 48.400 | 24.600 | -23.800 | [-31.005, -16.648] | -49.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | hp_lost | 11.600 | 35.400 | +23.800 | [+16.547, +31.050] | +205.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | hp_lost_frac | 0.193 | 0.590 | +0.397 | [+0.270, +0.518] | +205.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | intake | 5.750 | 23.200 | +17.450 | [+11.348, +23.500] | +303.5 % | **CHANGED** |
| fight:dosage_dispenser@t3 | perfect_rate | 0.658 | 0.375 | -0.282 | [-0.356, -0.207] | -42.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | ram_left_per_turn | 8.591 | 9.617 | +1.026 | [+0.602, +1.476] | +11.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | resistance_absorbed | 2.550 | 4.350 | +1.800 | [+1.200, +2.350] | +70.6 % | **CHANGED** |
| fight:dosage_dispenser@t3 | taken | 11.600 | 35.400 | +23.800 | [+16.547, +31.150] | +205.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | taken_per_turn | 1.567 | 2.779 | +1.211 | [+0.571, +1.841] | +77.3 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns | 7.400 | 12.500 | +5.100 | [+3.700, +6.550] | +68.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | won | 1.000 | 0.850 | -0.150 | [-0.300, -0.050] | -15.0 % | **CHANGED** |
| fight:dosage_dispenser@t4 | dealt | 152.100 | 118.850 | -33.250 | [-48.200, -18.547] | -21.9 % | **CHANGED** |
| fight:dosage_dispenser@t4 | dealt_per_turn | 14.665 | 7.753 | -6.912 | [-8.703, -5.282] | -47.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | died | 0.050 | 0.750 | +0.700 | [+0.500, +0.850] | +1400.0 % | **CHANGED** |
| fight:dosage_dispenser@t4 | hp_end | 36.750 | 4.350 | -32.400 | [-38.500, -26.297] | -88.2 % | **CHANGED** |
| fight:dosage_dispenser@t4 | hp_lost | 23.250 | 55.650 | +32.400 | [+25.747, +38.800] | +139.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | hp_lost_frac | 0.388 | 0.927 | +0.540 | [+0.434, +0.646] | +139.3 % | **CHANGED** |
| fight:dosage_dispenser@t4 | intake | 11.100 | 37.500 | +26.400 | [+19.850, +32.852] | +237.8 % | **CHANGED** |
| fight:dosage_dispenser@t4 | perfect_rate | 0.654 | 0.330 | -0.324 | [-0.391, -0.255] | -49.5 % | **CHANGED** |
| fight:dosage_dispenser@t4 | ram_left_per_turn | 8.914 | 9.944 | +1.030 | [+0.634, +1.463] | +11.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | resistance_absorbed | 4.500 | 5.550 | +1.050 | [+0.050, +2.000] | +23.3 % | **CHANGED** |
| fight:dosage_dispenser@t4 | taken | 23.250 | 55.650 | +32.400 | [+25.550, +38.750] | +139.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | taken_per_turn | 2.107 | 3.682 | +1.575 | [+0.924, +2.172] | +74.8 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns | 11.000 | 15.550 | +4.550 | [+3.150, +5.800] | +41.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns_both_share | 0.276 | 0.192 | -0.084 | [-0.163, -0.008] | -30.3 % | **CHANGED** |
| fight:dosage_dispenser@t4 | won | 0.950 | 0.250 | -0.700 | [-0.850, -0.500] | -73.7 % | **CHANGED** |
| fight:recall_unit@t1 | dealt | 106.000 | 81.600 | -24.400 | [-34.453, -14.797] | -23.0 % | **CHANGED** |
| fight:recall_unit@t1 | dealt_per_turn | 12.178 | 6.485 | -5.693 | [-7.461, -3.921] | -46.7 % | **CHANGED** |
| fight:recall_unit@t1 | died | 0.000 | 0.650 | +0.650 | [+0.450, +0.800] | - | **CHANGED** |
| fight:recall_unit@t1 | enrage_step | 0.900 | 1.650 | +0.750 | [+0.350, +1.150] | +83.3 % | **CHANGED** |
| fight:recall_unit@t1 | hp_end | 29.900 | 3.800 | -26.100 | [-31.600, -20.047] | -87.3 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost | 30.100 | 56.200 | +26.100 | [+20.147, +32.002] | +86.7 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost_frac | 0.502 | 0.937 | +0.435 | [+0.333, +0.530] | +86.7 % | **CHANGED** |
| fight:recall_unit@t1 | intake | 28.000 | 53.350 | +25.350 | [+19.700, +31.350] | +90.5 % | **CHANGED** |
| fight:recall_unit@t1 | perfect_rate | 0.727 | 0.365 | -0.363 | [-0.438, -0.286] | -49.9 % | **CHANGED** |
| fight:recall_unit@t1 | ram_left_per_turn | 8.850 | 9.805 | +0.955 | [+0.507, +1.378] | +10.8 % | **CHANGED** |
| fight:recall_unit@t1 | resistance_absorbed | 9.350 | 13.450 | +4.100 | [+1.300, +7.150] | +43.9 % | **CHANGED** |
| fight:recall_unit@t1 | taken | 30.100 | 56.200 | +26.100 | [+19.948, +32.000] | +86.7 % | **CHANGED** |
| fight:recall_unit@t1 | taken_per_turn | 3.183 | 4.478 | +1.296 | [+0.668, +1.950] | +40.7 % | **CHANGED** |
| fight:recall_unit@t1 | turns | 9.550 | 13.300 | +3.750 | [+2.200, +5.400] | +39.3 % | **CHANGED** |
| fight:recall_unit@t1 | won | 1.000 | 0.350 | -0.650 | [-0.800, -0.450] | -65.0 % | **CHANGED** |
| fight:recall_unit@t2 | dealt | 142.650 | 69.500 | -73.150 | [-90.850, -54.748] | -51.3 % | **CHANGED** |
| fight:recall_unit@t2 | dealt_per_turn | 10.902 | 5.979 | -4.922 | [-6.324, -3.489] | -45.1 % | **CHANGED** |
| fight:recall_unit@t2 | died | 0.650 | 1.000 | +0.350 | [+0.200, +0.500] | +53.8 % | **CHANGED** |
| fight:recall_unit@t2 | hp_end | 4.800 | 0.000 | -4.800 | [-8.003, -2.100] | -100.0 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost | 55.200 | 60.000 | +4.800 | [+1.950, +7.850] | +8.7 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost_frac | 0.920 | 1.000 | +0.080 | [+0.033, +0.136] | +8.7 % | **CHANGED** |
| fight:recall_unit@t2 | intake | 49.900 | 58.050 | +8.150 | [+5.000, +11.350] | +16.3 % | **CHANGED** |
| fight:recall_unit@t2 | perfect_rate | 0.652 | 0.368 | -0.284 | [-0.364, -0.207] | -43.5 % | **CHANGED** |
| fight:recall_unit@t2 | ram_left_per_turn | 9.101 | 9.784 | +0.682 | [+0.378, +0.976] | +7.5 % | **CHANGED** |
| fight:recall_unit@t2 | resistance_absorbed | 14.650 | 10.800 | -3.850 | [-6.400, -1.200] | -26.3 % | **CHANGED** |
| fight:recall_unit@t2 | taken | 55.200 | 60.000 | +4.800 | [+2.050, +8.000] | +8.7 % | **CHANGED** |
| fight:recall_unit@t2 | taken_per_turn | 4.220 | 5.512 | +1.292 | [+0.738, +1.876] | +30.6 % | **CHANGED** |
| fight:recall_unit@t2 | turns | 13.350 | 11.550 | -1.800 | [-3.100, -0.500] | -13.5 % | **CHANGED** |
| fight:recall_unit@t2 | turns_both_share | 0.263 | 0.197 | -0.066 | [-0.122, -0.008] | -25.1 % | **CHANGED** |
| fight:recall_unit@t2 | won | 0.350 | 0.000 | -0.350 | [-0.503, -0.200] | -100.0 % | **CHANGED** |
| fight:recall_unit@t3 | dealt | 133.400 | 53.650 | -79.750 | [-104.400, -56.800] | -59.8 % | **CHANGED** |
| fight:recall_unit@t3 | dealt_per_turn | 10.412 | 5.629 | -4.784 | [-6.557, -2.960] | -45.9 % | **CHANGED** |
| fight:recall_unit@t3 | enrage_step | 1.500 | 0.950 | -0.550 | [-0.900, -0.200] | -36.7 % | **CHANGED** |
| fight:recall_unit@t3 | intake | 56.100 | 59.200 | +3.100 | [+1.750, +4.550] | +5.5 % | **CHANGED** |
| fight:recall_unit@t3 | perfect_rate | 0.610 | 0.328 | -0.283 | [-0.371, -0.193] | -46.3 % | **CHANGED** |
| fight:recall_unit@t3 | resistance_absorbed | 12.900 | 9.450 | -3.450 | [-6.100, -0.800] | -26.7 % | **CHANGED** |
| fight:recall_unit@t3 | taken_per_turn | 5.392 | 6.720 | +1.328 | [+0.266, +2.339] | +24.6 % | **CHANGED** |
| fight:recall_unit@t3 | turns | 12.450 | 9.650 | -2.800 | [-4.500, -1.150] | -22.5 % | **CHANGED** |
| fight:recall_unit@t4 | dealt | 94.300 | 34.150 | -60.150 | [-81.150, -40.545] | -63.8 % | **CHANGED** |
| fight:recall_unit@t4 | dealt_per_turn | 9.301 | 4.454 | -4.847 | [-6.757, -3.120] | -52.1 % | **CHANGED** |
| fight:recall_unit@t4 | enrage_step | 1.050 | 0.600 | -0.450 | [-0.800, -0.100] | -42.9 % | **CHANGED** |
| fight:recall_unit@t4 | intake | 57.600 | 59.100 | +1.500 | [+0.450, +2.550] | +2.6 % | **CHANGED** |
| fight:recall_unit@t4 | perfect_rate | 0.588 | 0.268 | -0.320 | [-0.410, -0.231] | -54.4 % | **CHANGED** |
| fight:recall_unit@t4 | turns | 10.300 | 7.800 | -2.500 | [-4.200, -0.800] | -24.3 % | **CHANGED** |
| fight:triage_unit@t1 | dealt | 45.450 | 48.600 | +3.150 | [+0.900, +5.850] | +6.9 % | **CHANGED** |
| fight:triage_unit@t1 | dealt_per_turn | 12.912 | 6.917 | -5.995 | [-8.103, -3.933] | -46.4 % | **CHANGED** |
| fight:triage_unit@t1 | heal_total | 4.900 | 9.600 | +4.700 | [+0.800, +9.100] | +95.9 % | **CHANGED** |
| fight:triage_unit@t1 | heal_turns | 1.300 | 2.250 | +0.950 | [+0.100, +1.950] | +73.1 % | **CHANGED** |
| fight:triage_unit@t1 | hp_end | 58.500 | 52.350 | -6.150 | [-8.400, -4.043] | -10.5 % | **CHANGED** |
| fight:triage_unit@t1 | hp_lost | 1.500 | 7.650 | +6.150 | [+4.050, +8.400] | +410.0 % | **CHANGED** |
| fight:triage_unit@t1 | hp_lost_frac | 0.025 | 0.128 | +0.103 | [+0.065, +0.140] | +410.0 % | **CHANGED** |
| fight:triage_unit@t1 | intake | 1.350 | 6.150 | +4.800 | [+2.700, +7.050] | +355.6 % | **CHANGED** |
| fight:triage_unit@t1 | perfect_rate | 0.688 | 0.422 | -0.267 | [-0.377, -0.151] | -38.7 % | **CHANGED** |
| fight:triage_unit@t1 | ram_left_per_turn | 7.098 | 9.087 | +1.989 | [+1.089, +2.875] | +28.0 % | **CHANGED** |
| fight:triage_unit@t1 | resistance_absorbed | 1.600 | 3.450 | +1.850 | [+1.100, +2.650] | +115.6 % | **CHANGED** |
| fight:triage_unit@t1 | taken | 1.500 | 7.650 | +6.150 | [+3.900, +8.550] | +410.0 % | **CHANGED** |
| fight:triage_unit@t1 | taken_per_turn | 0.417 | 0.938 | +0.520 | [+0.099, +0.923] | +124.6 % | **CHANGED** |
| fight:triage_unit@t1 | turns | 3.950 | 9.200 | +5.250 | [+3.450, +7.300] | +132.9 % | **CHANGED** |
| fight:triage_unit@t1 | turns_both_share | 0.302 | 0.214 | -0.087 | [-0.171, -0.004] | -29.0 % | **CHANGED** |
| fight:triage_unit@t2 | dealt | 74.000 | 81.850 | +7.850 | [+3.900, +12.250] | +10.6 % | **CHANGED** |
| fight:triage_unit@t2 | dealt_per_turn | 12.868 | 7.251 | -5.617 | [-7.772, -3.363] | -43.7 % | **CHANGED** |
| fight:triage_unit@t2 | heal_total | 9.050 | 23.200 | +14.150 | [+6.600, +21.952] | +156.4 % | **CHANGED** |
| fight:triage_unit@t2 | heal_turns | 1.750 | 4.050 | +2.300 | [+1.100, +3.600] | +131.4 % | **CHANGED** |
| fight:triage_unit@t2 | hp_end | 54.900 | 42.650 | -12.250 | [-16.500, -7.750] | -22.3 % | **CHANGED** |
| fight:triage_unit@t2 | hp_lost | 5.100 | 17.350 | +12.250 | [+8.000, +16.452] | +240.2 % | **CHANGED** |
| fight:triage_unit@t2 | hp_lost_frac | 0.085 | 0.289 | +0.204 | [+0.125, +0.273] | +240.2 % | **CHANGED** |
| fight:triage_unit@t2 | intake | 3.450 | 13.000 | +9.550 | [+5.100, +13.650] | +276.8 % | **CHANGED** |
| fight:triage_unit@t2 | perfect_rate | 0.679 | 0.405 | -0.274 | [-0.369, -0.176] | -40.4 % | **CHANGED** |
| fight:triage_unit@t2 | ram_left_per_turn | 7.889 | 9.655 | +1.766 | [+0.969, +2.568] | +22.4 % | **CHANGED** |
| fight:triage_unit@t2 | resistance_absorbed | 2.950 | 5.650 | +2.700 | [+1.350, +4.150] | +91.5 % | **CHANGED** |
| fight:triage_unit@t2 | taken | 5.100 | 17.350 | +12.250 | [+7.700, +16.450] | +240.2 % | **CHANGED** |
| fight:triage_unit@t2 | taken_per_turn | 0.769 | 1.306 | +0.537 | [+0.074, +1.005] | +69.9 % | **CHANGED** |
| fight:triage_unit@t2 | turns | 6.350 | 14.600 | +8.250 | [+5.500, +11.150] | +129.9 % | **CHANGED** |
| fight:triage_unit@t2 | turns_both_share | 0.352 | 0.228 | -0.124 | [-0.220, -0.030] | -35.3 % | **CHANGED** |
| fight:triage_unit@t3 | dealt | 120.600 | 131.150 | +10.550 | [+4.800, +16.803] | +8.7 % | **CHANGED** |
| fight:triage_unit@t3 | dealt_per_turn | 12.346 | 6.473 | -5.873 | [-7.454, -4.347] | -47.6 % | **CHANGED** |
| fight:triage_unit@t3 | died | 0.000 | 0.250 | +0.250 | [+0.100, +0.400] | - | **CHANGED** |
| fight:triage_unit@t3 | heal_total | 21.800 | 53.950 | +32.150 | [+18.245, +47.450] | +147.5 % | **CHANGED** |
| fight:triage_unit@t3 | heal_turns | 3.300 | 7.400 | +4.100 | [+2.200, +6.000] | +124.2 % | **CHANGED** |
| fight:triage_unit@t3 | hp_end | 48.650 | 23.100 | -25.550 | [-33.352, -17.600] | -52.5 % | **CHANGED** |
| fight:triage_unit@t3 | hp_lost | 11.350 | 36.900 | +25.550 | [+17.797, +33.900] | +225.1 % | **CHANGED** |
| fight:triage_unit@t3 | hp_lost_frac | 0.189 | 0.615 | +0.426 | [+0.292, +0.552] | +225.1 % | **CHANGED** |
| fight:triage_unit@t3 | intake | 6.850 | 25.550 | +18.700 | [+12.350, +24.352] | +273.0 % | **CHANGED** |
| fight:triage_unit@t3 | perfect_rate | 0.653 | 0.383 | -0.270 | [-0.349, -0.193] | -41.3 % | **CHANGED** |
| fight:triage_unit@t3 | ram_left_per_turn | 8.842 | 10.088 | +1.246 | [+0.796, +1.700] | +14.1 % | **CHANGED** |
| fight:triage_unit@t3 | resistance_absorbed | 4.350 | 9.850 | +5.500 | [+3.797, +7.250] | +126.4 % | **CHANGED** |
| fight:triage_unit@t3 | taken | 11.350 | 36.900 | +25.550 | [+17.300, +33.500] | +225.1 % | **CHANGED** |
| fight:triage_unit@t3 | taken_per_turn | 0.999 | 1.547 | +0.548 | [+0.147, +0.947] | +54.9 % | **CHANGED** |
| fight:triage_unit@t3 | turns | 10.600 | 24.000 | +13.400 | [+9.600, +17.200] | +126.4 % | **CHANGED** |
| fight:triage_unit@t3 | turns_both_share | 0.310 | 0.232 | -0.078 | [-0.149, -0.006] | -25.2 % | **CHANGED** |
| fight:triage_unit@t3 | won | 1.000 | 0.750 | -0.250 | [-0.450, -0.100] | -25.0 % | **CHANGED** |
| fight:triage_unit@t4 | dealt | 199.050 | 162.650 | -36.400 | [-56.555, -17.548] | -18.3 % | **CHANGED** |
| fight:triage_unit@t4 | dealt_per_turn | 10.294 | 5.098 | -5.196 | [-6.136, -4.282] | -50.5 % | **CHANGED** |
| fight:triage_unit@t4 | died | 0.000 | 0.850 | +0.850 | [+0.700, +0.950] | - | **CHANGED** |
| fight:triage_unit@t4 | heal_total | 54.050 | 91.300 | +37.250 | [+20.945, +54.852] | +68.9 % | **CHANGED** |
| fight:triage_unit@t4 | heal_turns | 6.400 | 9.900 | +3.500 | [+1.550, +5.550] | +54.7 % | **CHANGED** |
| fight:triage_unit@t4 | hp_end | 30.550 | 0.650 | -29.900 | [-35.150, -24.498] | -97.9 % | **CHANGED** |
| fight:triage_unit@t4 | hp_lost | 29.450 | 59.350 | +29.900 | [+24.547, +35.200] | +101.5 % | **CHANGED** |
| fight:triage_unit@t4 | hp_lost_frac | 0.491 | 0.989 | +0.498 | [+0.402, +0.584] | +101.5 % | **CHANGED** |
| fight:triage_unit@t4 | intake | 16.700 | 41.850 | +25.150 | [+18.850, +31.350] | +150.6 % | **CHANGED** |
| fight:triage_unit@t4 | perfect_rate | 0.584 | 0.348 | -0.236 | [-0.286, -0.184] | -40.3 % | **CHANGED** |
| fight:triage_unit@t4 | ram_left_per_turn | 9.361 | 10.288 | +0.927 | [+0.550, +1.335] | +9.9 % | **CHANGED** |
| fight:triage_unit@t4 | resistance_absorbed | 9.700 | 14.050 | +4.350 | [+2.400, +6.500] | +44.8 % | **CHANGED** |
| fight:triage_unit@t4 | taken | 29.450 | 59.350 | +29.900 | [+24.350, +35.250] | +101.5 % | **CHANGED** |
| fight:triage_unit@t4 | taken_per_turn | 1.472 | 2.042 | +0.570 | [+0.181, +0.981] | +38.7 % | **CHANGED** |
| fight:triage_unit@t4 | turns | 20.400 | 32.650 | +12.250 | [+8.200, +16.350] | +60.0 % | **CHANGED** |
| fight:triage_unit@t4 | turns_both_share | 0.349 | 0.217 | -0.132 | [-0.187, -0.077] | -37.8 % | **CHANGED** |
| fight:triage_unit@t4 | won | 1.000 | 0.150 | -0.850 | [-0.950, -0.700] | -85.0 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:account_manager@t1 | dealt_per_turn | 13.954 | 7.692 | -6.262 | [-7.945, -4.620] | -44.9 % | **CHANGED** |
| fight:account_manager@t1 | died | 0.450 | 0.900 | +0.450 | [+0.250, +0.650] | +100.0 % | **CHANGED** |
| fight:account_manager@t1 | enrage_step | 0.800 | 1.350 | +0.550 | [+0.300, +0.800] | +68.8 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost | 43.600 | 59.000 | +15.400 | [+8.150, +22.700] | +35.3 % | **CHANGED** |
| fight:account_manager@t1 | intake | 36.450 | 48.400 | +11.950 | [+5.050, +19.200] | +32.8 % | **CHANGED** |
| fight:account_manager@t1 | parked | 14.400 | 10.050 | -4.350 | [-9.553, +0.652] | -30.2 % | noise |
| fight:account_manager@t1 | resistance_absorbed | 10.000 | 11.850 | +1.850 | [-0.100, +3.750] | +18.5 % | noise |
| fight:account_manager@t1 | taken_per_turn | 3.910 | 4.355 | +0.445 | [-0.236, +1.121] | +11.4 % | noise |
| fight:account_manager@t1 | turns | 10.850 | 13.950 | +3.100 | [+1.900, +4.400] | +28.6 % | **CHANGED** |
| fight:account_manager@t1 | turns_both_share | 0.255 | 0.178 | -0.077 | [-0.148, -0.010] | -30.2 % | **CHANGED** |
| fight:account_manager@t1 | won | 0.550 | 0.100 | -0.450 | [-0.650, -0.250] | -81.8 % | **CHANGED** |
| fight:account_manager@t2 | dealt_per_turn | 13.037 | 7.495 | -5.542 | [-7.000, -4.194] | -42.5 % | **CHANGED** |
| fight:account_manager@t2 | died | 0.900 | 1.000 | +0.100 | [+0.000, +0.200] | +11.1 % | noise |
| fight:account_manager@t2 | enrage_step | 1.400 | 1.250 | -0.150 | [-0.450, +0.150] | -10.7 % | noise |
| fight:account_manager@t2 | hp_lost | 58.700 | 60.000 | +1.300 | [+0.000, +3.050] | +2.2 % | noise |
| fight:account_manager@t2 | intake | 46.800 | 49.000 | +2.200 | [-1.903, +6.500] | +4.7 % | noise |
| fight:account_manager@t2 | parked | 9.900 | 1.700 | -8.200 | [-12.453, -4.700] | -82.8 % | **CHANGED** |
| fight:account_manager@t2 | resistance_absorbed | 13.900 | 11.600 | -2.300 | [-5.450, +0.750] | -16.5 % | noise |
| fight:account_manager@t2 | taken_per_turn | 4.406 | 4.845 | +0.439 | [-0.171, +1.147] | +10.0 % | noise |
| fight:account_manager@t2 | turns | 13.700 | 13.500 | -0.200 | [-1.750, +1.400] | -1.5 % | noise |
| fight:account_manager@t2 | turns_both_share | 0.260 | 0.203 | -0.057 | [-0.124, +0.011] | -22.1 % | noise |
| fight:account_manager@t2 | won | 0.100 | 0.000 | -0.100 | [-0.200, +0.000] | -100.0 % | noise |
| fight:account_manager@t3 | dealt_per_turn | 10.530 | 5.441 | -5.089 | [-6.506, -3.749] | -48.3 % | **CHANGED** |
| fight:account_manager@t3 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t3 | enrage_step | 1.750 | 0.750 | -1.000 | [-1.450, -0.550] | -57.1 % | **CHANGED** |
| fight:account_manager@t3 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t3 | intake | 45.250 | 52.700 | +7.450 | [+3.300, +11.400] | +16.5 % | **CHANGED** |
| fight:account_manager@t3 | parked | 2.200 | 0.000 | -2.200 | [-3.903, -0.850] | -100.0 % | **CHANGED** |
| fight:account_manager@t3 | resistance_absorbed | 15.200 | 10.700 | -4.500 | [-8.000, -1.200] | -29.6 % | **CHANGED** |
| fight:account_manager@t3 | taken_per_turn | 4.222 | 6.343 | +2.121 | [+0.847, +3.593] | +50.2 % | **CHANGED** |
| fight:account_manager@t3 | turns | 15.600 | 11.400 | -4.200 | [-6.450, -1.800] | -26.9 % | **CHANGED** |
| fight:account_manager@t3 | turns_both_share | 0.209 | 0.180 | -0.029 | [-0.085, +0.029] | -13.8 % | noise |
| fight:account_manager@t3 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:account_manager@t4 | dealt_per_turn | 10.642 | 5.643 | -4.999 | [-6.540, -3.426] | -47.0 % | **CHANGED** |
| fight:account_manager@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t4 | enrage_step | 1.300 | 0.450 | -0.850 | [-1.350, -0.350] | -65.4 % | **CHANGED** |
| fight:account_manager@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t4 | intake | 49.500 | 54.600 | +5.100 | [+1.250, +9.200] | +10.3 % | **CHANGED** |
| fight:account_manager@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:account_manager@t4 | resistance_absorbed | 13.300 | 8.400 | -4.900 | [-7.850, -1.700] | -36.8 % | **CHANGED** |
| fight:account_manager@t4 | taken_per_turn | 5.620 | 8.579 | +2.959 | [+0.989, +5.006] | +52.6 % | **CHANGED** |
| fight:account_manager@t4 | turns | 13.300 | 8.800 | -4.500 | [-7.003, -2.050] | -33.8 % | **CHANGED** |
| fight:account_manager@t4 | turns_both_share | 0.230 | 0.187 | -0.043 | [-0.112, +0.029] | -18.7 % | noise |
| fight:account_manager@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | dealt_per_turn | 14.125 | 8.998 | -5.127 | [-7.977, -2.167] | -36.3 % | **CHANGED** |
| fight:billing_daemon@t1 | died | 0.000 | 0.100 | +0.100 | [+0.000, +0.200] | - | noise |
| fight:billing_daemon@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | hp_lost | 8.850 | 26.200 | +17.350 | [+11.250, +23.302] | +196.0 % | **CHANGED** |
| fight:billing_daemon@t1 | intake | 8.550 | 25.750 | +17.200 | [+11.550, +23.250] | +201.2 % | **CHANGED** |
| fight:billing_daemon@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | resistance_absorbed | 2.000 | 2.850 | +0.850 | [+0.150, +1.600] | +42.5 % | **CHANGED** |
| fight:billing_daemon@t1 | taken_per_turn | 2.667 | 4.146 | +1.478 | [+0.614, +2.324] | +55.4 % | **CHANGED** |
| fight:billing_daemon@t1 | turns | 3.450 | 6.500 | +3.050 | [+1.700, +4.500] | +88.4 % | **CHANGED** |
| fight:billing_daemon@t1 | turns_both_share | 0.448 | 0.222 | -0.225 | [-0.343, -0.112] | -50.4 % | **CHANGED** |
| fight:billing_daemon@t1 | won | 1.000 | 0.900 | -0.100 | [-0.200, +0.000] | -10.0 % | noise |
| fight:billing_daemon@t2 | dealt_per_turn | 12.919 | 6.836 | -6.083 | [-7.592, -4.431] | -47.1 % | **CHANGED** |
| fight:billing_daemon@t2 | died | 0.000 | 0.400 | +0.400 | [+0.200, +0.550] | - | **CHANGED** |
| fight:billing_daemon@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | hp_lost | 14.350 | 47.800 | +33.450 | [+26.600, +39.553] | +233.1 % | **CHANGED** |
| fight:billing_daemon@t2 | intake | 14.050 | 45.700 | +31.650 | [+24.750, +38.403] | +225.3 % | **CHANGED** |
| fight:billing_daemon@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | resistance_absorbed | 2.700 | 4.150 | +1.450 | [+0.550, +2.250] | +53.7 % | **CHANGED** |
| fight:billing_daemon@t2 | taken_per_turn | 2.579 | 4.978 | +2.399 | [+1.608, +3.151] | +93.0 % | **CHANGED** |
| fight:billing_daemon@t2 | turns | 5.700 | 9.650 | +3.950 | [+2.650, +5.150] | +69.3 % | **CHANGED** |
| fight:billing_daemon@t2 | turns_both_share | 0.356 | 0.227 | -0.130 | [-0.208, -0.054] | -36.4 % | **CHANGED** |
| fight:billing_daemon@t2 | won | 1.000 | 0.600 | -0.400 | [-0.550, -0.250] | -40.0 % | **CHANGED** |
| fight:billing_daemon@t3 | dealt_per_turn | 11.200 | 6.944 | -4.256 | [-5.591, -2.881] | -38.0 % | **CHANGED** |
| fight:billing_daemon@t3 | died | 0.150 | 0.950 | +0.800 | [+0.650, +0.950] | +533.3 % | **CHANGED** |
| fight:billing_daemon@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | hp_lost | 33.650 | 59.500 | +25.850 | [+19.950, +31.650] | +76.8 % | **CHANGED** |
| fight:billing_daemon@t3 | intake | 31.250 | 57.200 | +25.950 | [+20.350, +31.500] | +83.0 % | **CHANGED** |
| fight:billing_daemon@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | resistance_absorbed | 5.550 | 4.350 | -1.200 | [-2.100, -0.250] | -21.6 % | **CHANGED** |
| fight:billing_daemon@t3 | taken_per_turn | 3.328 | 6.715 | +3.387 | [+2.662, +4.139] | +101.7 % | **CHANGED** |
| fight:billing_daemon@t3 | turns | 9.900 | 9.300 | -0.600 | [-1.650, +0.400] | -6.1 % | noise |
| fight:billing_daemon@t3 | turns_both_share | 0.422 | 0.245 | -0.177 | [-0.262, -0.094] | -42.0 % | **CHANGED** |
| fight:billing_daemon@t3 | won | 0.850 | 0.050 | -0.800 | [-0.950, -0.650] | -94.1 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 11.519 | 6.442 | -5.077 | [-6.712, -3.355] | -44.1 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.700 | 1.000 | +0.300 | [+0.150, +0.450] | +42.9 % | **CHANGED** |
| fight:billing_daemon@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | hp_lost | 54.650 | 60.000 | +5.350 | [+2.200, +9.000] | +9.8 % | **CHANGED** |
| fight:billing_daemon@t4 | intake | 51.200 | 59.400 | +8.200 | [+4.650, +12.150] | +16.0 % | **CHANGED** |
| fight:billing_daemon@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | resistance_absorbed | 6.600 | 3.800 | -2.800 | [-3.800, -1.700] | -42.4 % | **CHANGED** |
| fight:billing_daemon@t4 | taken_per_turn | 4.687 | 8.581 | +3.894 | [+2.626, +5.344] | +83.1 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 12.500 | 7.800 | -4.700 | [-6.050, -3.300] | -37.6 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.383 | 0.216 | -0.167 | [-0.247, -0.086] | -43.6 % | **CHANGED** |
| fight:billing_daemon@t4 | won | 0.300 | 0.000 | -0.300 | [-0.450, -0.150] | -100.0 % | **CHANGED** |
| fight:care_swarm@t1 | dealt_per_turn | 8.998 | 5.700 | -3.298 | [-6.185, -0.448] | -36.7 % | **CHANGED** |
| fight:care_swarm@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | hp_lost | 17.300 | 30.550 | +13.250 | [+7.850, +18.453] | +76.6 % | **CHANGED** |
| fight:care_swarm@t1 | intake | 17.300 | 30.550 | +13.250 | [+7.750, +18.300] | +76.6 % | **CHANGED** |
| fight:care_swarm@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | resistance_absorbed | 1.400 | 2.800 | +1.400 | [+0.650, +2.150] | +100.0 % | **CHANGED** |
| fight:care_swarm@t1 | taken_per_turn | 4.815 | 4.784 | -0.031 | [-0.818, +0.707] | -0.6 % | noise |
| fight:care_swarm@t1 | turns | 3.900 | 6.800 | +2.900 | [+1.400, +4.400] | +74.4 % | **CHANGED** |
| fight:care_swarm@t1 | turns_both_share | 0.245 | 0.210 | -0.036 | [-0.146, +0.065] | -14.6 % | noise |
| fight:care_swarm@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t2 | dealt_per_turn | 7.917 | 5.496 | -2.421 | [-4.409, -0.270] | -30.6 % | **CHANGED** |
| fight:care_swarm@t2 | died | 0.250 | 0.450 | +0.200 | [-0.050, +0.450] | +80.0 % | noise |
| fight:care_swarm@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | hp_lost | 37.300 | 48.050 | +10.750 | [+3.497, +17.900] | +28.8 % | **CHANGED** |
| fight:care_swarm@t2 | intake | 36.850 | 48.050 | +11.200 | [+3.550, +18.250] | +30.4 % | **CHANGED** |
| fight:care_swarm@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | resistance_absorbed | 2.300 | 3.800 | +1.500 | [+0.697, +2.300] | +65.2 % | **CHANGED** |
| fight:care_swarm@t2 | taken_per_turn | 6.286 | 6.026 | -0.260 | [-1.154, +0.602] | -4.1 % | noise |
| fight:care_swarm@t2 | turns | 6.250 | 9.000 | +2.750 | [+0.900, +4.700] | +44.0 % | **CHANGED** |
| fight:care_swarm@t2 | turns_both_share | 0.292 | 0.208 | -0.084 | [-0.182, +0.014] | -28.9 % | noise |
| fight:care_swarm@t2 | won | 0.750 | 0.550 | -0.200 | [-0.450, +0.050] | -26.7 % | noise |
| fight:care_swarm@t3 | dealt_per_turn | 7.572 | 3.756 | -3.817 | [-5.497, -2.180] | -50.4 % | **CHANGED** |
| fight:care_swarm@t3 | died | 0.600 | 1.000 | +0.400 | [+0.250, +0.600] | +66.7 % | **CHANGED** |
| fight:care_swarm@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t3 | hp_lost | 53.400 | 60.000 | +6.600 | [+3.150, +10.652] | +12.4 % | **CHANGED** |
| fight:care_swarm@t3 | intake | 52.650 | 59.600 | +6.950 | [+3.550, +10.950] | +13.2 % | **CHANGED** |
| fight:care_swarm@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t3 | resistance_absorbed | 2.850 | 3.000 | +0.150 | [-0.653, +0.950] | +5.3 % | noise |
| fight:care_swarm@t3 | taken_per_turn | 7.357 | 8.873 | +1.516 | [+0.504, +2.664] | +20.6 % | **CHANGED** |
| fight:care_swarm@t3 | turns | 7.800 | 7.100 | -0.700 | [-1.800, +0.302] | -9.0 % | noise |
| fight:care_swarm@t3 | turns_both_share | 0.246 | 0.237 | -0.009 | [-0.089, +0.072] | -3.6 % | noise |
| fight:care_swarm@t3 | won | 0.400 | 0.000 | -0.400 | [-0.600, -0.250] | -100.0 % | **CHANGED** |
| fight:care_swarm@t4 | dealt_per_turn | 8.188 | 4.481 | -3.707 | [-5.746, -1.520] | -45.3 % | **CHANGED** |
| fight:care_swarm@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t4 | intake | 59.100 | 59.750 | +0.650 | [+0.000, +1.350] | +1.1 % | noise |
| fight:care_swarm@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t4 | resistance_absorbed | 2.000 | 1.850 | -0.150 | [-0.800, +0.450] | -7.5 % | noise |
| fight:care_swarm@t4 | taken_per_turn | 10.797 | 12.807 | +2.009 | [+0.594, +3.446] | +18.6 % | **CHANGED** |
| fight:care_swarm@t4 | turns | 5.900 | 4.900 | -1.000 | [-1.650, -0.350] | -16.9 % | **CHANGED** |
| fight:care_swarm@t4 | turns_both_share | 0.264 | 0.181 | -0.083 | [-0.176, +0.011] | -31.3 % | noise |
| fight:care_swarm@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | dealt_per_turn | 28.395 | 17.132 | -11.264 | [-16.957, -5.461] | -39.7 % | **CHANGED** |
| fight:claims_adjuster@t1 | died | 0.000 | 0.450 | +0.450 | [+0.250, +0.650] | - | **CHANGED** |
| fight:claims_adjuster@t1 | enrage_step | 0.050 | 0.250 | +0.200 | [+0.050, +0.400] | +400.0 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost | 29.050 | 49.200 | +20.150 | [+13.447, +26.800] | +69.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | intake | 26.800 | 46.700 | +19.900 | [+12.500, +26.550] | +74.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | resistance_absorbed | 4.800 | 5.500 | +0.700 | [-1.200, +2.500] | +14.6 % | noise |
| fight:claims_adjuster@t1 | taken_per_turn | 6.680 | 8.235 | +1.555 | [+0.364, +2.760] | +23.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns | 4.500 | 6.050 | +1.550 | [+0.700, +2.450] | +34.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns_both_share | 0.311 | 0.203 | -0.107 | [-0.201, -0.017] | -34.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | won | 1.000 | 0.550 | -0.450 | [-0.650, -0.250] | -45.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | dealt_per_turn | 24.977 | 15.016 | -9.961 | [-13.605, -6.041] | -39.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | died | 0.500 | 0.950 | +0.450 | [+0.250, +0.650] | +90.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | enrage_step | 0.300 | 0.300 | +0.000 | [-0.250, +0.300] | +0.0 % | noise |
| fight:claims_adjuster@t2 | hp_lost | 48.650 | 59.550 | +10.900 | [+5.600, +16.352] | +22.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | intake | 43.100 | 56.400 | +13.300 | [+7.550, +19.505] | +30.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t2 | resistance_absorbed | 7.850 | 6.050 | -1.800 | [-4.100, +0.550] | -22.9 % | noise |
| fight:claims_adjuster@t2 | taken_per_turn | 7.344 | 10.628 | +3.284 | [+1.544, +5.125] | +44.7 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns | 6.800 | 6.350 | -0.450 | [-1.400, +0.600] | -6.6 % | noise |
| fight:claims_adjuster@t2 | turns_both_share | 0.335 | 0.173 | -0.162 | [-0.255, -0.069] | -48.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | won | 0.500 | 0.050 | -0.450 | [-0.650, -0.250] | -90.0 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt_per_turn | 26.787 | 13.851 | -12.936 | [-17.245, -8.641] | -48.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | died | 0.900 | 1.000 | +0.100 | [+0.000, +0.200] | +11.1 % | noise |
| fight:claims_adjuster@t3 | enrage_step | 0.300 | 0.000 | -0.300 | [-0.500, -0.100] | -100.0 % | **CHANGED** |
| fight:claims_adjuster@t3 | hp_lost | 58.000 | 60.000 | +2.000 | [+0.000, +4.500] | +3.4 % | noise |
| fight:claims_adjuster@t3 | intake | 53.350 | 58.850 | +5.500 | [+2.100, +9.750] | +10.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t3 | resistance_absorbed | 7.100 | 4.000 | -3.100 | [-5.653, -0.700] | -43.7 % | **CHANGED** |
| fight:claims_adjuster@t3 | taken_per_turn | 10.455 | 16.185 | +5.730 | [+2.723, +8.772] | +54.8 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns | 6.300 | 4.400 | -1.900 | [-3.003, -0.950] | -30.2 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns_both_share | 0.280 | 0.179 | -0.101 | [-0.204, +0.005] | -36.0 % | noise |
| fight:claims_adjuster@t3 | won | 0.100 | 0.000 | -0.100 | [-0.200, +0.000] | -100.0 % | noise |
| fight:claims_adjuster@t4 | dealt_per_turn | 25.920 | 14.232 | -11.688 | [-16.075, -7.399] | -45.1 % | **CHANGED** |
| fight:claims_adjuster@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:claims_adjuster@t4 | enrage_step | 0.300 | 0.000 | -0.300 | [-0.500, -0.100] | -100.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:claims_adjuster@t4 | intake | 56.700 | 59.250 | +2.550 | [+1.050, +4.350] | +4.5 % | **CHANGED** |
| fight:claims_adjuster@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t4 | resistance_absorbed | 6.350 | 2.650 | -3.700 | [-6.303, -1.450] | -58.3 % | **CHANGED** |
| fight:claims_adjuster@t4 | taken_per_turn | 13.007 | 18.100 | +5.093 | [+1.974, +8.222] | +39.2 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns | 5.550 | 3.800 | -1.750 | [-2.950, -0.700] | -31.5 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns_both_share | 0.234 | 0.154 | -0.080 | [-0.175, +0.013] | -34.2 % | noise |
| fight:claims_adjuster@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | dealt_per_turn | 11.818 | 8.599 | -3.219 | [-5.485, -0.919] | -27.2 % | **CHANGED** |
| fight:collections_agent@t1 | died | 0.000 | 0.050 | +0.050 | [+0.000, +0.150] | - | noise |
| fight:collections_agent@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | hp_lost | 10.200 | 27.600 | +17.400 | [+10.147, +24.750] | +170.6 % | **CHANGED** |
| fight:collections_agent@t1 | intake | 9.900 | 25.800 | +15.900 | [+9.647, +22.352] | +160.6 % | **CHANGED** |
| fight:collections_agent@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | resistance_absorbed | 1.650 | 2.500 | +0.850 | [+0.150, +1.500] | +51.5 % | **CHANGED** |
| fight:collections_agent@t1 | taken_per_turn | 2.650 | 4.516 | +1.866 | [+0.823, +2.917] | +70.4 % | **CHANGED** |
| fight:collections_agent@t1 | turns | 3.750 | 6.100 | +2.350 | [+1.150, +3.650] | +62.7 % | **CHANGED** |
| fight:collections_agent@t1 | turns_both_share | 0.264 | 0.223 | -0.041 | [-0.169, +0.093] | -15.6 % | noise |
| fight:collections_agent@t1 | won | 1.000 | 0.950 | -0.050 | [-0.150, +0.000] | -5.0 % | noise |
| fight:collections_agent@t2 | dealt_per_turn | 12.975 | 9.220 | -3.755 | [-6.193, -1.340] | -28.9 % | **CHANGED** |
| fight:collections_agent@t2 | died | 0.000 | 0.450 | +0.450 | [+0.300, +0.650] | - | **CHANGED** |
| fight:collections_agent@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | hp_lost | 19.600 | 44.350 | +24.750 | [+16.700, +32.200] | +126.3 % | **CHANGED** |
| fight:collections_agent@t2 | intake | 17.950 | 41.150 | +23.200 | [+15.450, +30.252] | +129.2 % | **CHANGED** |
| fight:collections_agent@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | resistance_absorbed | 2.500 | 3.300 | +0.800 | [-0.100, +1.650] | +32.0 % | noise |
| fight:collections_agent@t2 | taken_per_turn | 3.574 | 6.065 | +2.491 | [+1.389, +3.751] | +69.7 % | **CHANGED** |
| fight:collections_agent@t2 | turns | 5.400 | 7.650 | +2.250 | [+1.100, +3.450] | +41.7 % | **CHANGED** |
| fight:collections_agent@t2 | turns_both_share | 0.272 | 0.238 | -0.034 | [-0.147, +0.082] | -12.4 % | noise |
| fight:collections_agent@t2 | won | 1.000 | 0.550 | -0.450 | [-0.650, -0.250] | -45.0 % | **CHANGED** |
| fight:collections_agent@t3 | dealt_per_turn | 12.422 | 6.964 | -5.458 | [-7.218, -3.697] | -43.9 % | **CHANGED** |
| fight:collections_agent@t3 | died | 0.350 | 0.950 | +0.600 | [+0.400, +0.800] | +171.4 % | **CHANGED** |
| fight:collections_agent@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | hp_lost | 41.100 | 58.650 | +17.550 | [+10.950, +24.302] | +42.7 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 36.750 | 54.250 | +17.500 | [+11.000, +23.650] | +47.6 % | **CHANGED** |
| fight:collections_agent@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | resistance_absorbed | 3.900 | 3.850 | -0.050 | [-0.900, +0.800] | -1.3 % | noise |
| fight:collections_agent@t3 | taken_per_turn | 4.938 | 7.700 | +2.762 | [+1.655, +3.926] | +55.9 % | **CHANGED** |
| fight:collections_agent@t3 | turns | 8.150 | 8.250 | +0.100 | [-0.850, +1.050] | +1.2 % | noise |
| fight:collections_agent@t3 | turns_both_share | 0.302 | 0.231 | -0.071 | [-0.166, +0.023] | -23.4 % | noise |
| fight:collections_agent@t3 | won | 0.650 | 0.050 | -0.600 | [-0.800, -0.400] | -92.3 % | **CHANGED** |
| fight:collections_agent@t4 | dealt_per_turn | 12.533 | 6.186 | -6.347 | [-8.321, -4.480] | -50.6 % | **CHANGED** |
| fight:collections_agent@t4 | died | 0.750 | 1.000 | +0.250 | [+0.100, +0.400] | +33.3 % | **CHANGED** |
| fight:collections_agent@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | hp_lost | 57.900 | 60.000 | +2.100 | [+0.500, +4.250] | +3.6 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 52.350 | 56.700 | +4.350 | [+1.497, +7.350] | +8.3 % | **CHANGED** |
| fight:collections_agent@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | resistance_absorbed | 4.500 | 3.100 | -1.400 | [-2.400, -0.350] | -31.1 % | **CHANGED** |
| fight:collections_agent@t4 | taken_per_turn | 7.136 | 11.498 | +4.363 | [+1.995, +6.845] | +61.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 9.100 | 6.500 | -2.600 | [-4.050, -1.150] | -28.6 % | **CHANGED** |
| fight:collections_agent@t4 | turns_both_share | 0.330 | 0.204 | -0.125 | [-0.224, -0.027] | -38.1 % | **CHANGED** |
| fight:collections_agent@t4 | won | 0.250 | 0.000 | -0.250 | [-0.400, -0.100] | -100.0 % | **CHANGED** |
| fight:compliance_officer@t1 | dealt_per_turn | 13.554 | 7.311 | -6.242 | [-8.659, -3.830] | -46.1 % | **CHANGED** |
| fight:compliance_officer@t1 | died | 0.000 | 0.100 | +0.100 | [+0.000, +0.200] | - | noise |
| fight:compliance_officer@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | hp_lost | 10.600 | 31.700 | +21.100 | [+14.750, +27.500] | +199.1 % | **CHANGED** |
| fight:compliance_officer@t1 | intake | 10.150 | 30.950 | +20.800 | [+14.250, +27.052] | +204.9 % | **CHANGED** |
| fight:compliance_officer@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | resistance_absorbed | 3.800 | 6.000 | +2.200 | [+1.050, +3.450] | +57.9 % | **CHANGED** |
| fight:compliance_officer@t1 | taken_per_turn | 2.545 | 3.829 | +1.284 | [+0.567, +2.016] | +50.4 % | **CHANGED** |
| fight:compliance_officer@t1 | turns | 4.300 | 8.200 | +3.900 | [+2.500, +5.250] | +90.7 % | **CHANGED** |
| fight:compliance_officer@t1 | turns_both_share | 0.348 | 0.214 | -0.134 | [-0.222, -0.036] | -38.5 % | **CHANGED** |
| fight:compliance_officer@t1 | won | 1.000 | 0.900 | -0.100 | [-0.200, +0.000] | -10.0 % | noise |
| fight:compliance_officer@t2 | dealt_per_turn | 12.842 | 7.377 | -5.465 | [-6.996, -3.810] | -42.6 % | **CHANGED** |
| fight:compliance_officer@t2 | died | 0.000 | 0.400 | +0.400 | [+0.200, +0.600] | - | **CHANGED** |
| fight:compliance_officer@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | hp_lost | 19.550 | 48.200 | +28.650 | [+21.797, +35.650] | +146.5 % | **CHANGED** |
| fight:compliance_officer@t2 | intake | 17.900 | 46.250 | +28.350 | [+21.197, +34.602] | +158.4 % | **CHANGED** |
| fight:compliance_officer@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | resistance_absorbed | 4.800 | 7.100 | +2.300 | [+1.050, +3.550] | +47.9 % | **CHANGED** |
| fight:compliance_officer@t2 | taken_per_turn | 2.932 | 4.800 | +1.868 | [+1.089, +2.691] | +63.7 % | **CHANGED** |
| fight:compliance_officer@t2 | turns | 6.550 | 10.350 | +3.800 | [+2.600, +5.000] | +58.0 % | **CHANGED** |
| fight:compliance_officer@t2 | turns_both_share | 0.282 | 0.178 | -0.104 | [-0.170, -0.042] | -37.0 % | **CHANGED** |
| fight:compliance_officer@t2 | won | 1.000 | 0.600 | -0.400 | [-0.600, -0.250] | -40.0 % | **CHANGED** |
| fight:compliance_officer@t3 | dealt_per_turn | 11.985 | 7.104 | -4.880 | [-6.311, -3.453] | -40.7 % | **CHANGED** |
| fight:compliance_officer@t3 | died | 0.400 | 0.950 | +0.550 | [+0.350, +0.750] | +137.5 % | **CHANGED** |
| fight:compliance_officer@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | hp_lost | 44.300 | 59.850 | +15.550 | [+9.098, +22.150] | +35.1 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 40.100 | 57.900 | +17.800 | [+11.300, +24.252] | +44.4 % | **CHANGED** |
| fight:compliance_officer@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | resistance_absorbed | 9.050 | 7.500 | -1.550 | [-3.400, +0.252] | -17.1 % | noise |
| fight:compliance_officer@t3 | taken_per_turn | 4.179 | 6.705 | +2.526 | [+1.538, +3.603] | +60.4 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 10.850 | 9.650 | -1.200 | [-2.450, +0.000] | -11.1 % | noise |
| fight:compliance_officer@t3 | turns_both_share | 0.327 | 0.224 | -0.103 | [-0.182, -0.024] | -31.4 % | **CHANGED** |
| fight:compliance_officer@t3 | won | 0.600 | 0.050 | -0.550 | [-0.750, -0.350] | -91.7 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt_per_turn | 11.430 | 6.115 | -5.314 | [-6.709, -3.829] | -46.5 % | **CHANGED** |
| fight:compliance_officer@t4 | died | 0.850 | 1.000 | +0.150 | [+0.050, +0.300] | +17.6 % | **CHANGED** |
| fight:compliance_officer@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | hp_lost | 59.300 | 60.000 | +0.700 | [+0.150, +1.400] | +1.2 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 55.200 | 59.250 | +4.050 | [+2.550, +5.602] | +7.3 % | **CHANGED** |
| fight:compliance_officer@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | resistance_absorbed | 10.200 | 6.700 | -3.500 | [-5.450, -1.550] | -34.3 % | **CHANGED** |
| fight:compliance_officer@t4 | taken_per_turn | 5.438 | 8.420 | +2.982 | [+1.642, +4.346] | +54.8 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 11.750 | 7.950 | -3.800 | [-5.200, -2.400] | -32.3 % | **CHANGED** |
| fight:compliance_officer@t4 | turns_both_share | 0.294 | 0.231 | -0.063 | [-0.135, +0.006] | -21.3 % | noise |
| fight:compliance_officer@t4 | won | 0.150 | 0.000 | -0.150 | [-0.300, -0.050] | -100.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | dealt_per_turn | 12.889 | 8.829 | -4.059 | [-6.258, -1.692] | -31.5 % | **CHANGED** |
| fight:dosage_dispenser@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | hp_lost | 2.100 | 6.450 | +4.350 | [+1.700, +7.050] | +207.1 % | **CHANGED** |
| fight:dosage_dispenser@t1 | intake | 1.350 | 4.950 | +3.600 | [+1.450, +5.900] | +266.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | resistance_absorbed | 1.050 | 1.750 | +0.700 | [+0.150, +1.250] | +66.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | taken_per_turn | 0.505 | 1.045 | +0.540 | [+0.097, +0.962] | +106.9 % | **CHANGED** |
| fight:dosage_dispenser@t1 | turns | 3.350 | 5.400 | +2.050 | [+1.050, +3.100] | +61.2 % | **CHANGED** |
| fight:dosage_dispenser@t1 | turns_both_share | 0.218 | 0.195 | -0.023 | [-0.126, +0.077] | -10.5 % | noise |
| fight:dosage_dispenser@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t2 | dealt_per_turn | 13.993 | 8.686 | -5.306 | [-7.363, -3.155] | -37.9 % | **CHANGED** |
| fight:dosage_dispenser@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | hp_lost | 4.900 | 15.900 | +11.000 | [+5.950, +15.950] | +224.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | intake | 2.800 | 11.100 | +8.300 | [+4.450, +12.800] | +296.4 % | **CHANGED** |
| fight:dosage_dispenser@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | resistance_absorbed | 1.750 | 3.250 | +1.500 | [+0.850, +2.200] | +85.7 % | **CHANGED** |
| fight:dosage_dispenser@t2 | taken_per_turn | 0.997 | 1.665 | +0.668 | [+0.132, +1.164] | +67.0 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns | 4.700 | 8.550 | +3.850 | [+2.450, +5.350] | +81.9 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns_both_share | 0.293 | 0.224 | -0.069 | [-0.159, +0.018] | -23.5 % | noise |
| fight:dosage_dispenser@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t3 | dealt_per_turn | 13.823 | 8.321 | -5.502 | [-7.009, -4.006] | -39.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | died | 0.000 | 0.150 | +0.150 | [+0.050, +0.300] | - | **CHANGED** |
| fight:dosage_dispenser@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | hp_lost | 11.600 | 35.400 | +23.800 | [+16.547, +31.050] | +205.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | intake | 5.750 | 23.200 | +17.450 | [+11.348, +23.500] | +303.5 % | **CHANGED** |
| fight:dosage_dispenser@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | resistance_absorbed | 2.550 | 4.350 | +1.800 | [+1.200, +2.350] | +70.6 % | **CHANGED** |
| fight:dosage_dispenser@t3 | taken_per_turn | 1.567 | 2.779 | +1.211 | [+0.571, +1.841] | +77.3 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns | 7.400 | 12.500 | +5.100 | [+3.700, +6.550] | +68.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns_both_share | 0.255 | 0.221 | -0.034 | [-0.112, +0.039] | -13.3 % | noise |
| fight:dosage_dispenser@t3 | won | 1.000 | 0.850 | -0.150 | [-0.300, -0.050] | -15.0 % | **CHANGED** |
| fight:dosage_dispenser@t4 | dealt_per_turn | 14.665 | 7.753 | -6.912 | [-8.703, -5.282] | -47.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | died | 0.050 | 0.750 | +0.700 | [+0.500, +0.850] | +1400.0 % | **CHANGED** |
| fight:dosage_dispenser@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | hp_lost | 23.250 | 55.650 | +32.400 | [+25.747, +38.800] | +139.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | intake | 11.100 | 37.500 | +26.400 | [+19.850, +32.852] | +237.8 % | **CHANGED** |
| fight:dosage_dispenser@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | resistance_absorbed | 4.500 | 5.550 | +1.050 | [+0.050, +2.000] | +23.3 % | **CHANGED** |
| fight:dosage_dispenser@t4 | taken_per_turn | 2.107 | 3.682 | +1.575 | [+0.924, +2.172] | +74.8 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns | 11.000 | 15.550 | +4.550 | [+3.150, +5.800] | +41.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns_both_share | 0.276 | 0.192 | -0.084 | [-0.163, -0.008] | -30.3 % | **CHANGED** |
| fight:dosage_dispenser@t4 | won | 0.950 | 0.250 | -0.700 | [-0.850, -0.500] | -73.7 % | **CHANGED** |
| fight:recall_unit@t1 | dealt_per_turn | 12.178 | 6.485 | -5.693 | [-7.461, -3.921] | -46.7 % | **CHANGED** |
| fight:recall_unit@t1 | died | 0.000 | 0.650 | +0.650 | [+0.450, +0.800] | - | **CHANGED** |
| fight:recall_unit@t1 | enrage_step | 0.900 | 1.650 | +0.750 | [+0.350, +1.150] | +83.3 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost | 30.100 | 56.200 | +26.100 | [+20.147, +32.002] | +86.7 % | **CHANGED** |
| fight:recall_unit@t1 | intake | 28.000 | 53.350 | +25.350 | [+19.700, +31.350] | +90.5 % | **CHANGED** |
| fight:recall_unit@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t1 | resistance_absorbed | 9.350 | 13.450 | +4.100 | [+1.300, +7.150] | +43.9 % | **CHANGED** |
| fight:recall_unit@t1 | taken_per_turn | 3.183 | 4.478 | +1.296 | [+0.668, +1.950] | +40.7 % | **CHANGED** |
| fight:recall_unit@t1 | turns | 9.550 | 13.300 | +3.750 | [+2.200, +5.400] | +39.3 % | **CHANGED** |
| fight:recall_unit@t1 | turns_both_share | 0.232 | 0.215 | -0.017 | [-0.073, +0.036] | -7.2 % | noise |
| fight:recall_unit@t1 | won | 1.000 | 0.350 | -0.650 | [-0.800, -0.450] | -65.0 % | **CHANGED** |
| fight:recall_unit@t2 | dealt_per_turn | 10.902 | 5.979 | -4.922 | [-6.324, -3.489] | -45.1 % | **CHANGED** |
| fight:recall_unit@t2 | died | 0.650 | 1.000 | +0.350 | [+0.200, +0.500] | +53.8 % | **CHANGED** |
| fight:recall_unit@t2 | enrage_step | 1.600 | 1.400 | -0.200 | [-0.550, +0.150] | -12.5 % | noise |
| fight:recall_unit@t2 | hp_lost | 55.200 | 60.000 | +4.800 | [+1.950, +7.850] | +8.7 % | **CHANGED** |
| fight:recall_unit@t2 | intake | 49.900 | 58.050 | +8.150 | [+5.000, +11.350] | +16.3 % | **CHANGED** |
| fight:recall_unit@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t2 | resistance_absorbed | 14.650 | 10.800 | -3.850 | [-6.400, -1.200] | -26.3 % | **CHANGED** |
| fight:recall_unit@t2 | taken_per_turn | 4.220 | 5.512 | +1.292 | [+0.738, +1.876] | +30.6 % | **CHANGED** |
| fight:recall_unit@t2 | turns | 13.350 | 11.550 | -1.800 | [-3.100, -0.500] | -13.5 % | **CHANGED** |
| fight:recall_unit@t2 | turns_both_share | 0.263 | 0.197 | -0.066 | [-0.122, -0.008] | -25.1 % | **CHANGED** |
| fight:recall_unit@t2 | won | 0.350 | 0.000 | -0.350 | [-0.503, -0.200] | -100.0 % | **CHANGED** |
| fight:recall_unit@t3 | dealt_per_turn | 10.412 | 5.629 | -4.784 | [-6.557, -2.960] | -45.9 % | **CHANGED** |
| fight:recall_unit@t3 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t3 | enrage_step | 1.500 | 0.950 | -0.550 | [-0.900, -0.200] | -36.7 % | **CHANGED** |
| fight:recall_unit@t3 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t3 | intake | 56.100 | 59.200 | +3.100 | [+1.750, +4.550] | +5.5 % | **CHANGED** |
| fight:recall_unit@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t3 | resistance_absorbed | 12.900 | 9.450 | -3.450 | [-6.100, -0.800] | -26.7 % | **CHANGED** |
| fight:recall_unit@t3 | taken_per_turn | 5.392 | 6.720 | +1.328 | [+0.266, +2.339] | +24.6 % | **CHANGED** |
| fight:recall_unit@t3 | turns | 12.450 | 9.650 | -2.800 | [-4.500, -1.150] | -22.5 % | **CHANGED** |
| fight:recall_unit@t3 | turns_both_share | 0.250 | 0.210 | -0.040 | [-0.111, +0.029] | -16.1 % | noise |
| fight:recall_unit@t3 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t4 | dealt_per_turn | 9.301 | 4.454 | -4.847 | [-6.757, -3.120] | -52.1 % | **CHANGED** |
| fight:recall_unit@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t4 | enrage_step | 1.050 | 0.600 | -0.450 | [-0.800, -0.100] | -42.9 % | **CHANGED** |
| fight:recall_unit@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t4 | intake | 57.600 | 59.100 | +1.500 | [+0.450, +2.550] | +2.6 % | **CHANGED** |
| fight:recall_unit@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t4 | resistance_absorbed | 9.550 | 7.450 | -2.100 | [-5.053, +0.800] | -22.0 % | noise |
| fight:recall_unit@t4 | taken_per_turn | 7.156 | 9.155 | +1.999 | [-0.241, +4.246] | +27.9 % | noise |
| fight:recall_unit@t4 | turns | 10.300 | 7.800 | -2.500 | [-4.200, -0.800] | -24.3 % | **CHANGED** |
| fight:recall_unit@t4 | turns_both_share | 0.162 | 0.158 | -0.003 | [-0.071, +0.065] | -2.1 % | noise |
| fight:recall_unit@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | dealt_per_turn | 12.912 | 6.917 | -5.995 | [-8.103, -3.933] | -46.4 % | **CHANGED** |
| fight:triage_unit@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | hp_lost | 1.500 | 7.650 | +6.150 | [+4.050, +8.400] | +410.0 % | **CHANGED** |
| fight:triage_unit@t1 | intake | 1.350 | 6.150 | +4.800 | [+2.700, +7.050] | +355.6 % | **CHANGED** |
| fight:triage_unit@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | resistance_absorbed | 1.600 | 3.450 | +1.850 | [+1.100, +2.650] | +115.6 % | **CHANGED** |
| fight:triage_unit@t1 | taken_per_turn | 0.417 | 0.938 | +0.520 | [+0.099, +0.923] | +124.6 % | **CHANGED** |
| fight:triage_unit@t1 | turns | 3.950 | 9.200 | +5.250 | [+3.450, +7.300] | +132.9 % | **CHANGED** |
| fight:triage_unit@t1 | turns_both_share | 0.302 | 0.214 | -0.087 | [-0.171, -0.004] | -29.0 % | **CHANGED** |
| fight:triage_unit@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t2 | dealt_per_turn | 12.868 | 7.251 | -5.617 | [-7.772, -3.363] | -43.7 % | **CHANGED** |
| fight:triage_unit@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | hp_lost | 5.100 | 17.350 | +12.250 | [+8.000, +16.452] | +240.2 % | **CHANGED** |
| fight:triage_unit@t2 | intake | 3.450 | 13.000 | +9.550 | [+5.100, +13.650] | +276.8 % | **CHANGED** |
| fight:triage_unit@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | resistance_absorbed | 2.950 | 5.650 | +2.700 | [+1.350, +4.150] | +91.5 % | **CHANGED** |
| fight:triage_unit@t2 | taken_per_turn | 0.769 | 1.306 | +0.537 | [+0.074, +1.005] | +69.9 % | **CHANGED** |
| fight:triage_unit@t2 | turns | 6.350 | 14.600 | +8.250 | [+5.500, +11.150] | +129.9 % | **CHANGED** |
| fight:triage_unit@t2 | turns_both_share | 0.352 | 0.228 | -0.124 | [-0.220, -0.030] | -35.3 % | **CHANGED** |
| fight:triage_unit@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t3 | dealt_per_turn | 12.346 | 6.473 | -5.873 | [-7.454, -4.347] | -47.6 % | **CHANGED** |
| fight:triage_unit@t3 | died | 0.000 | 0.250 | +0.250 | [+0.100, +0.400] | - | **CHANGED** |
| fight:triage_unit@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | hp_lost | 11.350 | 36.900 | +25.550 | [+17.797, +33.900] | +225.1 % | **CHANGED** |
| fight:triage_unit@t3 | intake | 6.850 | 25.550 | +18.700 | [+12.350, +24.352] | +273.0 % | **CHANGED** |
| fight:triage_unit@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | resistance_absorbed | 4.350 | 9.850 | +5.500 | [+3.797, +7.250] | +126.4 % | **CHANGED** |
| fight:triage_unit@t3 | taken_per_turn | 0.999 | 1.547 | +0.548 | [+0.147, +0.947] | +54.9 % | **CHANGED** |
| fight:triage_unit@t3 | turns | 10.600 | 24.000 | +13.400 | [+9.600, +17.200] | +126.4 % | **CHANGED** |
| fight:triage_unit@t3 | turns_both_share | 0.310 | 0.232 | -0.078 | [-0.149, -0.006] | -25.2 % | **CHANGED** |
| fight:triage_unit@t3 | won | 1.000 | 0.750 | -0.250 | [-0.450, -0.100] | -25.0 % | **CHANGED** |
| fight:triage_unit@t4 | dealt_per_turn | 10.294 | 5.098 | -5.196 | [-6.136, -4.282] | -50.5 % | **CHANGED** |
| fight:triage_unit@t4 | died | 0.000 | 0.850 | +0.850 | [+0.700, +0.950] | - | **CHANGED** |
| fight:triage_unit@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | hp_lost | 29.450 | 59.350 | +29.900 | [+24.547, +35.200] | +101.5 % | **CHANGED** |
| fight:triage_unit@t4 | intake | 16.700 | 41.850 | +25.150 | [+18.850, +31.350] | +150.6 % | **CHANGED** |
| fight:triage_unit@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | resistance_absorbed | 9.700 | 14.050 | +4.350 | [+2.400, +6.500] | +44.8 % | **CHANGED** |
| fight:triage_unit@t4 | taken_per_turn | 1.472 | 2.042 | +0.570 | [+0.181, +0.981] | +38.7 % | **CHANGED** |
| fight:triage_unit@t4 | turns | 20.400 | 32.650 | +12.250 | [+8.200, +16.350] | +60.0 % | **CHANGED** |
| fight:triage_unit@t4 | turns_both_share | 0.349 | 0.217 | -0.132 | [-0.187, -0.077] | -37.8 % | **CHANGED** |
| fight:triage_unit@t4 | won | 1.000 | 0.150 | -0.850 | [-0.950, -0.700] | -85.0 % | **CHANGED** |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A fight:account_manager@t1 | 20 | 0.24 | 3.94 | 0 | 14.4 | 36.5 | 10.0 | 2 | 0.24 |
| A fight:account_manager@t2 | 20 | 0.12 | 8.16 | 0 | 9.9 | 46.8 | 13.9 | 2 | 0.25 |
| A fight:account_manager@t3 | 20 | 0.12 | 14.75 | 0 | 2.2 | 45.2 | 15.2 | 3 | 0.21 |
| A fight:account_manager@t4 | 20 | - | - | 0 | 0.0 | 49.5 | 13.3 | 3 | 0.22 |
| A fight:billing_daemon@t1 | 20 | 0.55 | 3.45 | 0 | 0.0 | 8.6 | 2.0 | 0 | 0.42 |
| A fight:billing_daemon@t2 | 20 | 0.35 | 5.70 | 0 | 0.0 | 14.1 | 2.7 | 0 | 0.37 |
| A fight:billing_daemon@t3 | 20 | 0.00 | 9.53 | 0 | 0.0 | 31.2 | 5.5 | 0 | 0.42 |
| A fight:billing_daemon@t4 | 20 | 0.00 | 13.83 | 0 | 0.0 | 51.2 | 6.6 | 0 | 0.38 |
| A fight:care_swarm@t1 | 20 | 0.50 | 3.90 | 3 | 0.0 | 17.3 | 1.4 | 0 | 0.22 |
| A fight:care_swarm@t2 | 20 | 0.33 | 4.73 | 3 | 0.0 | 36.9 | 2.3 | 0 | 0.25 |
| A fight:care_swarm@t3 | 20 | 0.00 | 7.50 | 5 | 0.0 | 52.6 | 2.9 | 0 | 0.24 |
| A fight:care_swarm@t4 | 20 | - | - | 3 | 0.0 | 59.1 | 2.0 | 0 | 0.27 |
| A fight:claims_adjuster@t1 | 20 | 0.55 | 4.50 | 0 | 0.0 | 26.8 | 4.8 | 1 | 0.30 |
| A fight:claims_adjuster@t2 | 20 | 0.00 | 6.10 | 0 | 0.0 | 43.1 | 7.8 | 1 | 0.32 |
| A fight:claims_adjuster@t3 | 20 | 0.00 | 10.50 | 0 | 0.0 | 53.4 | 7.1 | 2 | 0.29 |
| A fight:claims_adjuster@t4 | 20 | - | - | 0 | 0.0 | 56.7 | 6.3 | 2 | 0.26 |
| A fight:collections_agent@t1 | 20 | 0.65 | 3.75 | 0 | 0.0 | 9.9 | 1.6 | 0 | 0.28 |
| A fight:collections_agent@t2 | 20 | 0.40 | 5.40 | 0 | 0.0 | 17.9 | 2.5 | 0 | 0.26 |
| A fight:collections_agent@t3 | 20 | 0.00 | 7.77 | 0 | 0.0 | 36.8 | 3.9 | 0 | 0.29 |
| A fight:collections_agent@t4 | 20 | 0.00 | 11.20 | 0 | 0.0 | 52.4 | 4.5 | 0 | 0.34 |
| A fight:compliance_officer@t1 | 20 | 0.50 | 4.30 | 0 | 0.0 | 10.2 | 3.8 | 0 | 0.34 |
| A fight:compliance_officer@t2 | 20 | 0.05 | 6.55 | 0 | 0.0 | 17.9 | 4.8 | 0 | 0.28 |
| A fight:compliance_officer@t3 | 20 | 0.00 | 10.92 | 0 | 0.0 | 40.1 | 9.1 | 0 | 0.32 |
| A fight:compliance_officer@t4 | 20 | 0.00 | 15.33 | 0 | 0.0 | 55.2 | 10.2 | 0 | 0.31 |
| A fight:dosage_dispenser@t1 | 20 | 0.55 | 3.35 | 0 | 0.0 | 1.4 | 1.1 | 0 | 0.21 |
| A fight:dosage_dispenser@t2 | 20 | 0.60 | 4.70 | 0 | 0.0 | 2.8 | 1.8 | 0 | 0.29 |
| A fight:dosage_dispenser@t3 | 20 | 0.00 | 7.40 | 0 | 0.0 | 5.8 | 2.5 | 0 | 0.24 |
| A fight:dosage_dispenser@t4 | 20 | 0.00 | 11.05 | 0 | 0.0 | 11.1 | 4.5 | 0 | 0.26 |
| A fight:recall_unit@t1 | 20 | 0.00 | 9.55 | 0 | 0.0 | 28.0 | 9.3 | 2 | 0.23 |
| A fight:recall_unit@t2 | 20 | 0.00 | 12.57 | 0 | 0.0 | 49.9 | 14.7 | 3 | 0.26 |
| A fight:recall_unit@t3 | 20 | - | - | 0 | 0.0 | 56.1 | 12.9 | 3 | 0.27 |
| A fight:recall_unit@t4 | 20 | - | - | 0 | 0.0 | 57.6 | 9.6 | 3 | 0.17 |
| A fight:triage_unit@t1 | 20 | 0.55 | 3.95 | 3 | 0.0 | 1.4 | 1.6 | 0 | 0.28 |
| A fight:triage_unit@t2 | 20 | 0.20 | 6.35 | 5 | 0.0 | 3.5 | 3.0 | 0 | 0.33 |
| A fight:triage_unit@t3 | 20 | 0.00 | 10.60 | 7 | 0.0 | 6.8 | 4.3 | 0 | 0.29 |
| A fight:triage_unit@t4 | 20 | 0.00 | 20.40 | 11 | 0.0 | 16.7 | 9.7 | 0 | 0.33 |
| B fight:account_manager@t1 | 20 | 0.16 | 7.08 | 0 | 10.1 | 48.4 | 11.8 | 2 | 0.18 |
| B fight:account_manager@t2 | 20 | 0.00 | 12.80 | 0 | 1.7 | 49.0 | 11.6 | 2 | 0.20 |
| B fight:account_manager@t3 | 20 | - | - | 0 | 0.0 | 52.7 | 10.7 | 3 | 0.19 |
| B fight:account_manager@t4 | 20 | - | - | 0 | 0.0 | 54.6 | 8.4 | 2 | 0.21 |
| B fight:billing_daemon@t1 | 20 | 0.22 | 5.61 | 0 | 0.0 | 25.8 | 2.9 | 0 | 0.19 |
| B fight:billing_daemon@t2 | 20 | 0.00 | 9.25 | 0 | 0.0 | 45.7 | 4.2 | 0 | 0.21 |
| B fight:billing_daemon@t3 | 20 | 0.00 | 11.00 | 0 | 0.0 | 57.2 | 4.3 | 0 | 0.24 |
| B fight:billing_daemon@t4 | 20 | - | - | 0 | 0.0 | 59.4 | 3.8 | 0 | 0.22 |
| B fight:care_swarm@t1 | 20 | 0.10 | 6.80 | 5 | 0.0 | 30.6 | 2.8 | 0 | 0.21 |
| B fight:care_swarm@t2 | 20 | 0.18 | 9.09 | 8 | 0.0 | 48.0 | 3.8 | 0 | 0.20 |
| B fight:care_swarm@t3 | 20 | - | - | 5 | 0.0 | 59.6 | 3.0 | 0 | 0.23 |
| B fight:care_swarm@t4 | 20 | - | - | 2 | 0.0 | 59.8 | 1.9 | 0 | 0.17 |
| B fight:claims_adjuster@t1 | 20 | 0.18 | 5.73 | 0 | 0.0 | 46.7 | 5.5 | 1 | 0.21 |
| B fight:claims_adjuster@t2 | 20 | 0.00 | 6.00 | 0 | 0.0 | 56.4 | 6.0 | 2 | 0.19 |
| B fight:claims_adjuster@t3 | 20 | - | - | 0 | 0.0 | 58.9 | 4.0 | 0 | 0.18 |
| B fight:claims_adjuster@t4 | 20 | - | - | 0 | 0.0 | 59.2 | 2.6 | 0 | 0.16 |
| B fight:collections_agent@t1 | 20 | 0.32 | 5.68 | 0 | 0.0 | 25.8 | 2.5 | 0 | 0.20 |
| B fight:collections_agent@t2 | 20 | 0.36 | 6.64 | 0 | 0.0 | 41.1 | 3.3 | 0 | 0.22 |
| B fight:collections_agent@t3 | 20 | 0.00 | 7.00 | 0 | 0.0 | 54.2 | 3.9 | 0 | 0.25 |
| B fight:collections_agent@t4 | 20 | - | - | 0 | 0.0 | 56.7 | 3.1 | 0 | 0.24 |
| B fight:compliance_officer@t1 | 20 | 0.22 | 7.56 | 0 | 0.0 | 30.9 | 6.0 | 0 | 0.18 |
| B fight:compliance_officer@t2 | 20 | 0.00 | 9.25 | 0 | 0.0 | 46.2 | 7.1 | 0 | 0.17 |
| B fight:compliance_officer@t3 | 20 | 0.00 | 13.00 | 0 | 0.0 | 57.9 | 7.5 | 0 | 0.22 |
| B fight:compliance_officer@t4 | 20 | - | - | 0 | 0.0 | 59.2 | 6.7 | 0 | 0.25 |
| B fight:dosage_dispenser@t1 | 20 | 0.25 | 5.40 | 0 | 0.0 | 5.0 | 1.8 | 0 | 0.20 |
| B fight:dosage_dispenser@t2 | 20 | 0.15 | 8.55 | 0 | 0.0 | 11.1 | 3.2 | 0 | 0.20 |
| B fight:dosage_dispenser@t3 | 20 | 0.00 | 11.65 | 0 | 0.0 | 23.2 | 4.3 | 0 | 0.20 |
| B fight:dosage_dispenser@t4 | 20 | 0.00 | 16.00 | 0 | 0.0 | 37.5 | 5.5 | 0 | 0.19 |
| B fight:recall_unit@t1 | 20 | 0.00 | 12.43 | 0 | 0.0 | 53.4 | 13.4 | 3 | 0.21 |
| B fight:recall_unit@t2 | 20 | - | - | 0 | 0.0 | 58.0 | 10.8 | 3 | 0.20 |
| B fight:recall_unit@t3 | 20 | - | - | 0 | 0.0 | 59.2 | 9.4 | 2 | 0.21 |
| B fight:recall_unit@t4 | 20 | - | - | 0 | 0.0 | 59.1 | 7.5 | 2 | 0.17 |
| B fight:triage_unit@t1 | 20 | 0.20 | 9.20 | 11 | 0.0 | 6.2 | 3.5 | 0 | 0.18 |
| B fight:triage_unit@t2 | 20 | 0.05 | 14.60 | 11 | 0.0 | 13.0 | 5.7 | 0 | 0.20 |
| B fight:triage_unit@t3 | 20 | 0.00 | 21.13 | 20 | 0.0 | 25.6 | 9.8 | 0 | 0.21 |
| B fight:triage_unit@t4 | 20 | 0.00 | 37.33 | 23 | 0.0 | 41.9 | 14.1 | 0 | 0.21 |

