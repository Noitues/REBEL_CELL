# Balance comparison: cal_dmg_12

- A: `cal_noop.json` (overrides: config.enemy_damage_by_tier=[1.0,1.3,1.69,2.2])
- B: `cal_damage_12.json` (overrides: config.enemy_damage_by_tier=[1.0,1.2,1.44,1.728])
- mode fight; A 240 records, B 240 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 17 of 264 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 3.900 | -0.650 | [-1.250, -0.100] | -14.3 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 16.896 | +1.578 | [+0.183, +2.937] | +10.3 % | **CHANGED** |
| fight:billing_daemon@t4 | ram_left_per_turn | 7.341 | 6.058 | -1.283 | [-2.257, -0.341] | -17.5 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 11.650 | 10.350 | -1.300 | [-2.250, -0.400] | -11.2 % | **CHANGED** |
| fight:collections_agent@t2 | combat_hash | 1614174098.100 | 2619214880.100 | +1005040782.000 | [+486517360.410, +1523776096.217] | +62.3 % | **CHANGED** |
| fight:collections_agent@t4 | hp_end | 16.850 | 27.300 | +10.450 | [+5.050, +16.050] | +62.0 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost | 43.150 | 32.700 | -10.450 | [-15.900, -5.450] | -24.2 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost_frac | 0.719 | 0.545 | -0.174 | [-0.265, -0.083] | -24.2 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 25.200 | -10.600 | [-15.750, -5.500] | -29.6 % | **CHANGED** |
| fight:collections_agent@t4 | taken | 43.150 | 32.700 | -10.450 | [-15.900, -5.100] | -24.2 % | **CHANGED** |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 3.275 | -1.100 | [-1.709, -0.525] | -25.1 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_end | 40.800 | 46.600 | +5.800 | [+1.350, +10.300] | +14.2 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 13.400 | -5.800 | [-10.200, -1.300] | -30.2 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost_frac | 0.320 | 0.223 | -0.097 | [-0.169, -0.024] | -30.2 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 11.000 | -4.600 | [-8.953, -0.150] | -29.5 % | **CHANGED** |
| fight:compliance_officer@t3 | taken | 19.200 | 13.400 | -5.800 | [-10.000, -1.550] | -30.2 % | **CHANGED** |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 1.571 | -0.706 | [-1.301, -0.132] | -31.0 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:billing_daemon@t1 | dealt_per_turn | 17.150 | 17.150 | +0.000 | [-2.100, +2.100] | +0.0 % | noise |
| fight:billing_daemon@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | hp_lost | 3.600 | 3.600 | +0.000 | [-1.750, +1.800] | +0.0 % | noise |
| fight:billing_daemon@t1 | intake | 3.150 | 3.150 | +0.000 | [-1.650, +1.700] | +0.0 % | noise |
| fight:billing_daemon@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | resistance_absorbed | 1.750 | 1.750 | +0.000 | [-0.400, +0.400] | +0.0 % | noise |
| fight:billing_daemon@t1 | taken_per_turn | 1.433 | 1.433 | +0.000 | [-0.743, +0.734] | +0.0 % | noise |
| fight:billing_daemon@t1 | turns | 2.600 | 2.600 | +0.000 | [-0.350, +0.350] | +0.0 % | noise |
| fight:billing_daemon@t1 | turns_both_share | 0.529 | 0.529 | +0.000 | [-0.163, +0.171] | +0.0 % | noise |
| fight:billing_daemon@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t2 | dealt_per_turn | 16.000 | 16.837 | +0.837 | [-1.452, +3.093] | +5.2 % | noise |
| fight:billing_daemon@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | hp_lost | 7.850 | 6.050 | -1.800 | [-4.850, +1.050] | -22.9 % | noise |
| fight:billing_daemon@t2 | intake | 6.950 | 4.850 | -2.100 | [-5.000, +0.900] | -30.2 % | noise |
| fight:billing_daemon@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | resistance_absorbed | 2.200 | 2.500 | +0.300 | [-0.150, +0.700] | +13.6 % | noise |
| fight:billing_daemon@t2 | taken_per_turn | 1.830 | 1.424 | -0.406 | [-1.128, +0.285] | -22.2 % | noise |
| fight:billing_daemon@t2 | turns | 4.500 | 4.300 | -0.200 | [-0.800, +0.450] | -4.4 % | noise |
| fight:billing_daemon@t2 | turns_both_share | 0.426 | 0.495 | +0.069 | [-0.060, +0.197] | +16.2 % | noise |
| fight:billing_daemon@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 16.537 | +0.023 | [-1.397, +1.517] | +0.1 % | noise |
| fight:billing_daemon@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | hp_lost | 11.550 | 11.600 | +0.050 | [-3.500, +3.550] | +0.4 % | noise |
| fight:billing_daemon@t3 | intake | 8.700 | 9.200 | +0.500 | [-2.553, +3.550] | +5.7 % | noise |
| fight:billing_daemon@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 3.900 | -0.650 | [-1.250, -0.100] | -14.3 % | **CHANGED** |
| fight:billing_daemon@t3 | taken_per_turn | 1.795 | 1.781 | -0.014 | [-0.619, +0.568] | -0.8 % | noise |
| fight:billing_daemon@t3 | turns | 6.750 | 6.700 | -0.050 | [-0.600, +0.550] | -0.7 % | noise |
| fight:billing_daemon@t3 | turns_both_share | 0.546 | 0.487 | -0.059 | [-0.159, +0.041] | -10.9 % | noise |
| fight:billing_daemon@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 16.896 | +1.578 | [+0.183, +2.937] | +10.3 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | hp_lost | 25.200 | 21.100 | -4.100 | [-10.950, +2.552] | -16.3 % | noise |
| fight:billing_daemon@t4 | intake | 19.800 | 15.700 | -4.100 | [-10.003, +1.700] | -20.7 % | noise |
| fight:billing_daemon@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | resistance_absorbed | 7.200 | 6.800 | -0.400 | [-1.250, +0.500] | -5.6 % | noise |
| fight:billing_daemon@t4 | taken_per_turn | 2.166 | 2.055 | -0.111 | [-0.639, +0.419] | -5.1 % | noise |
| fight:billing_daemon@t4 | turns | 11.650 | 10.350 | -1.300 | [-2.250, -0.400] | -11.2 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.510 | +0.033 | [-0.041, +0.107] | +7.0 % | noise |
| fight:billing_daemon@t4 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t1 | dealt_per_turn | 15.332 | 15.332 | +0.000 | [-2.167, +2.001] | +0.0 % | noise |
| fight:collections_agent@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | hp_lost | 5.850 | 5.850 | +0.000 | [-2.150, +2.100] | +0.0 % | noise |
| fight:collections_agent@t1 | intake | 5.550 | 5.550 | +0.000 | [-2.100, +2.200] | +0.0 % | noise |
| fight:collections_agent@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | resistance_absorbed | 1.200 | 1.200 | +0.000 | [-0.450, +0.400] | +0.0 % | noise |
| fight:collections_agent@t1 | taken_per_turn | 2.167 | 2.167 | +0.000 | [-0.875, +0.826] | +0.0 % | noise |
| fight:collections_agent@t1 | turns | 2.800 | 2.800 | +0.000 | [-0.400, +0.400] | +0.0 % | noise |
| fight:collections_agent@t1 | turns_both_share | 0.367 | 0.367 | +0.000 | [-0.175, +0.175] | +0.0 % | noise |
| fight:collections_agent@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t2 | dealt_per_turn | 16.811 | 16.811 | +0.000 | [-2.448, +2.350] | +0.0 % | noise |
| fight:collections_agent@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | hp_lost | 10.700 | 10.700 | +0.000 | [-2.950, +2.850] | +0.0 % | noise |
| fight:collections_agent@t2 | intake | 9.650 | 9.650 | +0.000 | [-2.550, +2.600] | +0.0 % | noise |
| fight:collections_agent@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | resistance_absorbed | 1.900 | 1.900 | +0.000 | [-0.500, +0.500] | +0.0 % | noise |
| fight:collections_agent@t2 | taken_per_turn | 2.863 | 2.863 | +0.000 | [-0.880, +0.932] | +0.0 % | noise |
| fight:collections_agent@t2 | turns | 4.200 | 4.200 | +0.000 | [-0.800, +0.800] | +0.0 % | noise |
| fight:collections_agent@t2 | turns_both_share | 0.439 | 0.439 | +0.000 | [-0.136, +0.145] | +0.0 % | noise |
| fight:collections_agent@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t3 | dealt_per_turn | 16.922 | 16.881 | -0.042 | [-2.117, +1.958] | -0.2 % | noise |
| fight:collections_agent@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | hp_lost | 18.850 | 17.850 | -1.000 | [-4.350, +2.252] | -5.3 % | noise |
| fight:collections_agent@t3 | intake | 16.150 | 15.900 | -0.250 | [-3.400, +2.950] | -1.5 % | noise |
| fight:collections_agent@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | resistance_absorbed | 3.450 | 3.000 | -0.450 | [-1.100, +0.200] | -13.0 % | noise |
| fight:collections_agent@t3 | taken_per_turn | 3.067 | 2.962 | -0.105 | [-0.705, +0.472] | -3.4 % | noise |
| fight:collections_agent@t3 | turns | 6.300 | 6.400 | +0.100 | [-0.650, +0.850] | +1.6 % | noise |
| fight:collections_agent@t3 | turns_both_share | 0.459 | 0.382 | -0.077 | [-0.169, +0.018] | -16.7 % | noise |
| fight:collections_agent@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t4 | dealt_per_turn | 16.698 | 16.590 | -0.108 | [-1.498, +1.273] | -0.6 % | noise |
| fight:collections_agent@t4 | died | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:collections_agent@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | hp_lost | 43.150 | 32.700 | -10.450 | [-15.900, -5.450] | -24.2 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 25.200 | -10.600 | [-15.750, -5.500] | -29.6 % | **CHANGED** |
| fight:collections_agent@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | resistance_absorbed | 5.450 | 5.550 | +0.100 | [-0.800, +0.950] | +1.8 % | noise |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 3.275 | -1.100 | [-1.709, -0.525] | -25.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 10.000 | 10.200 | +0.200 | [-0.650, +1.150] | +2.0 % | noise |
| fight:collections_agent@t4 | turns_both_share | 0.415 | 0.461 | +0.046 | [-0.018, +0.110] | +11.0 % | noise |
| fight:collections_agent@t4 | won | 0.950 | 1.000 | +0.050 | [+0.000, +0.150] | +5.3 % | noise |
| fight:compliance_officer@t1 | dealt_per_turn | 17.919 | 17.919 | +0.000 | [-2.291, +2.095] | +0.0 % | noise |
| fight:compliance_officer@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | hp_lost | 4.800 | 4.800 | +0.000 | [-2.000, +1.950] | +0.0 % | noise |
| fight:compliance_officer@t1 | intake | 4.200 | 4.200 | +0.000 | [-1.700, +1.800] | +0.0 % | noise |
| fight:compliance_officer@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | resistance_absorbed | 2.800 | 2.800 | +0.000 | [-0.905, +0.900] | +0.0 % | noise |
| fight:compliance_officer@t1 | taken_per_turn | 1.820 | 1.820 | +0.000 | [-0.796, +0.764] | +0.0 % | noise |
| fight:compliance_officer@t1 | turns | 2.950 | 2.950 | +0.000 | [-0.350, +0.350] | +0.0 % | noise |
| fight:compliance_officer@t1 | turns_both_share | 0.371 | 0.371 | +0.000 | [-0.125, +0.129] | +0.0 % | noise |
| fight:compliance_officer@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t2 | dealt_per_turn | 15.855 | 17.078 | +1.223 | [-1.001, +3.601] | +7.7 % | noise |
| fight:compliance_officer@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | hp_lost | 9.200 | 7.450 | -1.750 | [-3.803, +0.300] | -19.0 % | noise |
| fight:compliance_officer@t2 | intake | 7.850 | 5.950 | -1.900 | [-4.150, +0.350] | -24.2 % | noise |
| fight:compliance_officer@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | resistance_absorbed | 4.400 | 4.500 | +0.100 | [-1.100, +1.300] | +2.3 % | noise |
| fight:compliance_officer@t2 | taken_per_turn | 1.873 | 1.639 | -0.234 | [-0.848, +0.346] | -12.5 % | noise |
| fight:compliance_officer@t2 | turns | 5.450 | 5.050 | -0.400 | [-1.203, +0.400] | -7.3 % | noise |
| fight:compliance_officer@t2 | turns_both_share | 0.323 | 0.353 | +0.031 | [-0.051, +0.115] | +9.5 % | noise |
| fight:compliance_officer@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t3 | dealt_per_turn | 15.041 | 14.506 | -0.535 | [-1.999, +0.933] | -3.6 % | noise |
| fight:compliance_officer@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 13.400 | -5.800 | [-10.200, -1.300] | -30.2 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 11.000 | -4.600 | [-8.953, -0.150] | -29.5 % | **CHANGED** |
| fight:compliance_officer@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | resistance_absorbed | 8.600 | 8.200 | -0.400 | [-1.900, +1.000] | -4.7 % | noise |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 1.571 | -0.706 | [-1.301, -0.132] | -31.0 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 8.850 | 9.200 | +0.350 | [-0.553, +1.252] | +4.0 % | noise |
| fight:compliance_officer@t3 | turns_both_share | 0.353 | 0.338 | -0.015 | [-0.070, +0.044] | -4.2 % | noise |
| fight:compliance_officer@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t4 | dealt_per_turn | 15.738 | 15.841 | +0.103 | [-1.318, +1.489] | +0.7 % | noise |
| fight:compliance_officer@t4 | died | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:compliance_officer@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 35.050 | -4.750 | [-11.703, +1.352] | -11.9 % | noise |
| fight:compliance_officer@t4 | intake | 32.300 | 26.500 | -5.800 | [-12.300, +1.252] | -18.0 % | noise |
| fight:compliance_officer@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | resistance_absorbed | 12.000 | 12.700 | +0.700 | [-1.000, +2.400] | +5.8 % | noise |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 2.695 | -0.448 | [-1.090, +0.129] | -14.3 % | noise |
| fight:compliance_officer@t4 | turns | 13.300 | 13.400 | +0.100 | [-1.150, +1.400] | +0.8 % | noise |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.356 | -0.000 | [-0.060, +0.058] | -0.0 % | noise |
| fight:compliance_officer@t4 | won | 0.950 | 1.000 | +0.050 | [+0.000, +0.150] | +5.3 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A fight:billing_daemon@t1 | 20 | 0.50 | 2.60 | 0 | 0.0 | 3.1 | 1.8 | 0 | 0.50 |
| A fight:billing_daemon@t2 | 20 | 0.55 | 4.50 | 0 | 0.0 | 7.0 | 2.2 | 0 | 0.40 |
| A fight:billing_daemon@t3 | 20 | 0.00 | 6.75 | 0 | 0.0 | 8.7 | 4.5 | 0 | 0.53 |
| A fight:billing_daemon@t4 | 20 | 0.00 | 11.65 | 0 | 0.0 | 19.8 | 7.2 | 0 | 0.46 |
| A fight:collections_agent@t1 | 20 | 0.60 | 2.80 | 0 | 0.0 | 5.5 | 1.2 | 0 | 0.34 |
| A fight:collections_agent@t2 | 20 | 0.65 | 4.20 | 0 | 0.0 | 9.7 | 1.9 | 0 | 0.39 |
| A fight:collections_agent@t3 | 20 | 0.10 | 6.30 | 0 | 0.0 | 16.1 | 3.5 | 0 | 0.44 |
| A fight:collections_agent@t4 | 20 | 0.00 | 9.84 | 0 | 0.0 | 35.8 | 5.5 | 0 | 0.41 |
| A fight:compliance_officer@t1 | 20 | 0.75 | 2.95 | 0 | 0.0 | 4.2 | 2.8 | 0 | 0.37 |
| A fight:compliance_officer@t2 | 20 | 0.30 | 5.45 | 0 | 0.0 | 7.8 | 4.4 | 0 | 0.33 |
| A fight:compliance_officer@t3 | 20 | 0.00 | 8.85 | 0 | 0.0 | 15.6 | 8.6 | 0 | 0.36 |
| A fight:compliance_officer@t4 | 20 | 0.00 | 13.53 | 0 | 0.0 | 32.3 | 12.0 | 0 | 0.35 |
| B fight:billing_daemon@t1 | 20 | 0.50 | 2.60 | 0 | 0.0 | 3.1 | 1.8 | 0 | 0.50 |
| B fight:billing_daemon@t2 | 20 | 0.60 | 4.30 | 0 | 0.0 | 4.8 | 2.5 | 0 | 0.45 |
| B fight:billing_daemon@t3 | 20 | 0.00 | 6.70 | 0 | 0.0 | 9.2 | 3.9 | 0 | 0.48 |
| B fight:billing_daemon@t4 | 20 | 0.00 | 10.35 | 0 | 0.0 | 15.7 | 6.8 | 0 | 0.51 |
| B fight:collections_agent@t1 | 20 | 0.60 | 2.80 | 0 | 0.0 | 5.5 | 1.2 | 0 | 0.34 |
| B fight:collections_agent@t2 | 20 | 0.65 | 4.20 | 0 | 0.0 | 9.7 | 1.9 | 0 | 0.39 |
| B fight:collections_agent@t3 | 20 | 0.10 | 6.40 | 0 | 0.0 | 15.9 | 3.0 | 0 | 0.38 |
| B fight:collections_agent@t4 | 20 | 0.00 | 10.20 | 0 | 0.0 | 25.2 | 5.5 | 0 | 0.45 |
| B fight:compliance_officer@t1 | 20 | 0.75 | 2.95 | 0 | 0.0 | 4.2 | 2.8 | 0 | 0.37 |
| B fight:compliance_officer@t2 | 20 | 0.40 | 5.05 | 0 | 0.0 | 6.0 | 4.5 | 0 | 0.36 |
| B fight:compliance_officer@t3 | 20 | 0.00 | 9.20 | 0 | 0.0 | 11.0 | 8.2 | 0 | 0.34 |
| B fight:compliance_officer@t4 | 20 | 0.00 | 13.40 | 0 | 0.0 | 26.5 | 12.7 | 0 | 0.35 |

