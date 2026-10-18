# Balance comparison: cal_dmg_16

- A: `cal_noop.json` (overrides: config.enemy_damage_by_tier=[1.0,1.3,1.69,2.2])
- B: `cal_damage_16.json` (overrides: config.enemy_damage_by_tier=[1.0,1.6,2.56,4.096])
- mode fight; A 240 records, B 240 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 48 of 264 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 12.719 | -3.795 | [-5.457, -2.147] | -23.0 % | **CHANGED** |
| fight:billing_daemon@t3 | perfect_rate | 0.884 | 0.777 | -0.108 | [-0.176, -0.041] | -12.2 % | **CHANGED** |
| fight:billing_daemon@t3 | ram_left_per_turn | 5.345 | 7.127 | +1.781 | [+0.773, +2.810] | +33.3 % | **CHANGED** |
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 5.400 | +0.850 | [+0.200, +1.500] | +18.7 % | **CHANGED** |
| fight:billing_daemon@t3 | turns | 6.750 | 9.050 | +2.300 | [+1.400, +3.250] | +34.1 % | **CHANGED** |
| fight:billing_daemon@t3 | turns_both_share | 0.546 | 0.434 | -0.113 | [-0.208, -0.015] | -20.6 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 11.970 | -3.349 | [-4.675, -2.075] | -21.9 % | **CHANGED** |
| fight:billing_daemon@t4 | perfect_rate | 0.867 | 0.700 | -0.167 | [-0.231, -0.107] | -19.3 % | **CHANGED** |
| fight:billing_daemon@t4 | resistance_absorbed | 7.200 | 9.150 | +1.950 | [+0.950, +2.950] | +27.1 % | **CHANGED** |
| fight:billing_daemon@t4 | taken_per_turn | 2.166 | 1.589 | -0.577 | [-1.114, -0.056] | -26.7 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 11.650 | 14.700 | +3.050 | [+2.000, +4.250] | +26.2 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.390 | -0.086 | [-0.156, -0.015] | -18.0 % | **CHANGED** |
| fight:collections_agent@t2 | combat_hash | 1614174098.100 | 2404672275.050 | +790498176.950 | [+225813434.460, +1358999093.875] | +49.0 % | **CHANGED** |
| fight:collections_agent@t3 | hp_end | 41.150 | 27.950 | -13.200 | [-18.400, -8.400] | -32.1 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost | 18.850 | 32.050 | +13.200 | [+8.097, +18.150] | +70.0 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost_frac | 0.314 | 0.534 | +0.220 | [+0.142, +0.302] | +70.0 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 16.150 | 29.050 | +12.900 | [+8.150, +17.850] | +79.9 % | **CHANGED** |
| fight:collections_agent@t3 | taken | 18.850 | 32.050 | +13.200 | [+8.297, +18.350] | +70.0 % | **CHANGED** |
| fight:collections_agent@t3 | taken_per_turn | 3.067 | 5.093 | +2.026 | [+1.225, +2.902] | +66.0 % | **CHANGED** |
| fight:collections_agent@t4 | dealt | 163.600 | 135.400 | -28.200 | [-41.820, -15.100] | -17.2 % | **CHANGED** |
| fight:collections_agent@t4 | died | 0.050 | 0.550 | +0.500 | [+0.300, +0.700] | +1000.0 % | **CHANGED** |
| fight:collections_agent@t4 | hp_end | 16.850 | 6.100 | -10.750 | [-15.500, -5.500] | -63.8 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost | 43.150 | 53.900 | +10.750 | [+5.550, +15.600] | +24.9 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost_frac | 0.719 | 0.898 | +0.179 | [+0.091, +0.263] | +24.9 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 48.650 | +12.850 | [+7.297, +18.250] | +35.9 % | **CHANGED** |
| fight:collections_agent@t4 | resistance_absorbed | 5.450 | 4.350 | -1.100 | [-1.950, -0.250] | -20.2 % | **CHANGED** |
| fight:collections_agent@t4 | taken | 43.150 | 53.900 | +10.750 | [+5.500, +15.400] | +24.9 % | **CHANGED** |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 7.048 | +2.673 | [+1.683, +3.675] | +61.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 10.000 | 8.250 | -1.750 | [-2.650, -0.750] | -17.5 % | **CHANGED** |
| fight:collections_agent@t4 | won | 0.950 | 0.450 | -0.500 | [-0.700, -0.300] | -52.6 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_end | 40.800 | 33.150 | -7.650 | [-14.000, -1.648] | -18.8 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 26.850 | +7.650 | [+1.200, +13.900] | +39.8 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost_frac | 0.320 | 0.447 | +0.128 | [+0.019, +0.229] | +39.8 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 23.550 | +7.950 | [+1.750, +14.202] | +51.0 % | **CHANGED** |
| fight:compliance_officer@t3 | perfect_rate | 0.908 | 0.819 | -0.088 | [-0.147, -0.033] | -9.7 % | **CHANGED** |
| fight:compliance_officer@t3 | taken | 19.200 | 26.850 | +7.650 | [+1.447, +13.553] | +39.8 % | **CHANGED** |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 3.244 | +0.967 | [+0.124, +1.792] | +42.5 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt | 203.750 | 158.200 | -45.550 | [-61.950, -29.000] | -22.4 % | **CHANGED** |
| fight:compliance_officer@t4 | died | 0.050 | 0.800 | +0.750 | [+0.550, +0.900] | +1500.0 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_end | 20.200 | 5.450 | -14.750 | [-20.750, -8.650] | -73.0 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 54.550 | +14.750 | [+8.350, +20.350] | +37.1 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost_frac | 0.663 | 0.909 | +0.246 | [+0.141, +0.340] | +37.1 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 32.300 | 50.050 | +17.750 | [+11.300, +24.200] | +55.0 % | **CHANGED** |
| fight:compliance_officer@t4 | perfect_rate | 0.888 | 0.799 | -0.089 | [-0.138, -0.040] | -10.1 % | **CHANGED** |
| fight:compliance_officer@t4 | taken | 39.800 | 54.550 | +14.750 | [+8.850, +20.502] | +37.1 % | **CHANGED** |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 5.623 | +2.480 | [+1.250, +3.795] | +78.9 % | **CHANGED** |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.293 | -0.063 | [-0.132, -0.001] | -17.7 % | **CHANGED** |
| fight:compliance_officer@t4 | won | 0.950 | 0.200 | -0.750 | [-0.900, -0.550] | -78.9 % | **CHANGED** |

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
| fight:billing_daemon@t2 | dealt_per_turn | 16.000 | 16.638 | +0.638 | [-1.349, +2.640] | +4.0 % | noise |
| fight:billing_daemon@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | hp_lost | 7.850 | 6.450 | -1.400 | [-4.500, +1.500] | -17.8 % | noise |
| fight:billing_daemon@t2 | intake | 6.950 | 5.250 | -1.700 | [-4.550, +1.050] | -24.5 % | noise |
| fight:billing_daemon@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | resistance_absorbed | 2.200 | 2.600 | +0.400 | [-0.100, +0.900] | +18.2 % | noise |
| fight:billing_daemon@t2 | taken_per_turn | 1.830 | 1.625 | -0.205 | [-0.958, +0.544] | -11.2 % | noise |
| fight:billing_daemon@t2 | turns | 4.500 | 4.200 | -0.300 | [-0.850, +0.250] | -6.7 % | noise |
| fight:billing_daemon@t2 | turns_both_share | 0.426 | 0.508 | +0.082 | [-0.032, +0.194] | +19.1 % | noise |
| fight:billing_daemon@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 12.719 | -3.795 | [-5.457, -2.147] | -23.0 % | **CHANGED** |
| fight:billing_daemon@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | hp_lost | 11.550 | 14.700 | +3.150 | [-1.950, +8.550] | +27.3 % | noise |
| fight:billing_daemon@t3 | intake | 8.700 | 12.450 | +3.750 | [-1.200, +8.850] | +43.1 % | noise |
| fight:billing_daemon@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 5.400 | +0.850 | [+0.200, +1.500] | +18.7 % | **CHANGED** |
| fight:billing_daemon@t3 | taken_per_turn | 1.795 | 1.662 | -0.133 | [-0.792, +0.484] | -7.4 % | noise |
| fight:billing_daemon@t3 | turns | 6.750 | 9.050 | +2.300 | [+1.400, +3.250] | +34.1 % | **CHANGED** |
| fight:billing_daemon@t3 | turns_both_share | 0.546 | 0.434 | -0.113 | [-0.208, -0.015] | -20.6 % | **CHANGED** |
| fight:billing_daemon@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 11.970 | -3.349 | [-4.675, -2.075] | -21.9 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | hp_lost | 25.200 | 22.300 | -2.900 | [-9.853, +4.000] | -11.5 % | noise |
| fight:billing_daemon@t4 | intake | 19.800 | 18.700 | -1.100 | [-7.303, +5.100] | -5.6 % | noise |
| fight:billing_daemon@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | resistance_absorbed | 7.200 | 9.150 | +1.950 | [+0.950, +2.950] | +27.1 % | **CHANGED** |
| fight:billing_daemon@t4 | taken_per_turn | 2.166 | 1.589 | -0.577 | [-1.114, -0.056] | -26.7 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 11.650 | 14.700 | +3.050 | [+2.000, +4.250] | +26.2 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.390 | -0.086 | [-0.156, -0.015] | -18.0 % | **CHANGED** |
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
| fight:collections_agent@t2 | dealt_per_turn | 16.811 | 16.905 | +0.095 | [-2.239, +2.440] | +0.6 % | noise |
| fight:collections_agent@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | hp_lost | 10.700 | 11.900 | +1.200 | [-1.650, +4.000] | +11.2 % | noise |
| fight:collections_agent@t2 | intake | 9.650 | 10.850 | +1.200 | [-1.453, +3.952] | +12.4 % | noise |
| fight:collections_agent@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | resistance_absorbed | 1.900 | 2.150 | +0.250 | [-0.300, +0.800] | +13.2 % | noise |
| fight:collections_agent@t2 | taken_per_turn | 2.863 | 3.241 | +0.378 | [-0.545, +1.380] | +13.2 % | noise |
| fight:collections_agent@t2 | turns | 4.200 | 4.050 | -0.150 | [-0.900, +0.500] | -3.6 % | noise |
| fight:collections_agent@t2 | turns_both_share | 0.439 | 0.478 | +0.039 | [-0.094, +0.179] | +8.8 % | noise |
| fight:collections_agent@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t3 | dealt_per_turn | 16.922 | 16.649 | -0.273 | [-2.265, +1.664] | -1.6 % | noise |
| fight:collections_agent@t3 | died | 0.000 | 0.050 | +0.050 | [+0.000, +0.150] | - | noise |
| fight:collections_agent@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | hp_lost | 18.850 | 32.050 | +13.200 | [+8.097, +18.150] | +70.0 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 16.150 | 29.050 | +12.900 | [+8.150, +17.850] | +79.9 % | **CHANGED** |
| fight:collections_agent@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | resistance_absorbed | 3.450 | 3.700 | +0.250 | [-0.500, +1.000] | +7.2 % | noise |
| fight:collections_agent@t3 | taken_per_turn | 3.067 | 5.093 | +2.026 | [+1.225, +2.902] | +66.0 % | **CHANGED** |
| fight:collections_agent@t3 | turns | 6.300 | 6.450 | +0.150 | [-0.550, +0.900] | +2.4 % | noise |
| fight:collections_agent@t3 | turns_both_share | 0.459 | 0.443 | -0.015 | [-0.103, +0.080] | -3.4 % | noise |
| fight:collections_agent@t3 | won | 1.000 | 0.950 | -0.050 | [-0.150, +0.000] | -5.0 % | noise |
| fight:collections_agent@t4 | dealt_per_turn | 16.698 | 16.657 | -0.041 | [-1.625, +1.554] | -0.2 % | noise |
| fight:collections_agent@t4 | died | 0.050 | 0.550 | +0.500 | [+0.300, +0.700] | +1000.0 % | **CHANGED** |
| fight:collections_agent@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | hp_lost | 43.150 | 53.900 | +10.750 | [+5.550, +15.600] | +24.9 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 48.650 | +12.850 | [+7.297, +18.250] | +35.9 % | **CHANGED** |
| fight:collections_agent@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | resistance_absorbed | 5.450 | 4.350 | -1.100 | [-1.950, -0.250] | -20.2 % | **CHANGED** |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 7.048 | +2.673 | [+1.683, +3.675] | +61.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 10.000 | 8.250 | -1.750 | [-2.650, -0.750] | -17.5 % | **CHANGED** |
| fight:collections_agent@t4 | turns_both_share | 0.415 | 0.409 | -0.006 | [-0.069, +0.062] | -1.5 % | noise |
| fight:collections_agent@t4 | won | 0.950 | 0.450 | -0.500 | [-0.700, -0.300] | -52.6 % | **CHANGED** |
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
| fight:compliance_officer@t2 | dealt_per_turn | 15.855 | 16.932 | +1.077 | [-1.057, +3.289] | +6.8 % | noise |
| fight:compliance_officer@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | hp_lost | 9.200 | 10.450 | +1.250 | [-1.103, +3.800] | +13.6 % | noise |
| fight:compliance_officer@t2 | intake | 7.850 | 9.100 | +1.250 | [-1.500, +4.050] | +15.9 % | noise |
| fight:compliance_officer@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | resistance_absorbed | 4.400 | 4.500 | +0.100 | [-1.000, +1.200] | +2.3 % | noise |
| fight:compliance_officer@t2 | taken_per_turn | 1.873 | 2.250 | +0.378 | [-0.326, +1.113] | +20.2 % | noise |
| fight:compliance_officer@t2 | turns | 5.450 | 5.050 | -0.400 | [-1.200, +0.400] | -7.3 % | noise |
| fight:compliance_officer@t2 | turns_both_share | 0.323 | 0.342 | +0.020 | [-0.063, +0.103] | +6.1 % | noise |
| fight:compliance_officer@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t3 | dealt_per_turn | 15.041 | 14.853 | -0.188 | [-1.561, +1.170] | -1.3 % | noise |
| fight:compliance_officer@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 26.850 | +7.650 | [+1.200, +13.900] | +39.8 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 23.550 | +7.950 | [+1.750, +14.202] | +51.0 % | **CHANGED** |
| fight:compliance_officer@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | resistance_absorbed | 8.600 | 8.700 | +0.100 | [-1.200, +1.400] | +1.2 % | noise |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 3.244 | +0.967 | [+0.124, +1.792] | +42.5 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 8.850 | 8.850 | +0.000 | [-0.850, +0.850] | +0.0 % | noise |
| fight:compliance_officer@t3 | turns_both_share | 0.353 | 0.343 | -0.010 | [-0.078, +0.058] | -2.9 % | noise |
| fight:compliance_officer@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t4 | dealt_per_turn | 15.738 | 14.265 | -1.473 | [-3.162, +0.273] | -9.4 % | noise |
| fight:compliance_officer@t4 | died | 0.050 | 0.800 | +0.750 | [+0.550, +0.900] | +1500.0 % | **CHANGED** |
| fight:compliance_officer@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 54.550 | +14.750 | [+8.350, +20.350] | +37.1 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 32.300 | 50.050 | +17.750 | [+11.300, +24.200] | +55.0 % | **CHANGED** |
| fight:compliance_officer@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | resistance_absorbed | 12.000 | 10.800 | -1.200 | [-3.400, +0.900] | -10.0 % | noise |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 5.623 | +2.480 | [+1.250, +3.795] | +78.9 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 13.300 | 11.800 | -1.500 | [-3.200, +0.152] | -11.3 % | noise |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.293 | -0.063 | [-0.132, -0.001] | -17.7 % | **CHANGED** |
| fight:compliance_officer@t4 | won | 0.950 | 0.200 | -0.750 | [-0.900, -0.550] | -78.9 % | **CHANGED** |

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
| B fight:billing_daemon@t2 | 20 | 0.70 | 4.20 | 0 | 0.0 | 5.2 | 2.6 | 0 | 0.50 |
| B fight:billing_daemon@t3 | 20 | 0.00 | 9.05 | 0 | 0.0 | 12.4 | 5.4 | 0 | 0.41 |
| B fight:billing_daemon@t4 | 20 | 0.00 | 14.70 | 0 | 0.0 | 18.7 | 9.2 | 0 | 0.39 |
| B fight:collections_agent@t1 | 20 | 0.60 | 2.80 | 0 | 0.0 | 5.5 | 1.2 | 0 | 0.34 |
| B fight:collections_agent@t2 | 20 | 0.60 | 4.05 | 0 | 0.0 | 10.8 | 2.1 | 0 | 0.44 |
| B fight:collections_agent@t3 | 20 | 0.05 | 6.53 | 0 | 0.0 | 29.1 | 3.7 | 0 | 0.45 |
| B fight:collections_agent@t4 | 20 | 0.00 | 9.78 | 0 | 0.0 | 48.6 | 4.3 | 0 | 0.41 |
| B fight:compliance_officer@t1 | 20 | 0.75 | 2.95 | 0 | 0.0 | 4.2 | 2.8 | 0 | 0.37 |
| B fight:compliance_officer@t2 | 20 | 0.45 | 5.05 | 0 | 0.0 | 9.1 | 4.5 | 0 | 0.34 |
| B fight:compliance_officer@t3 | 20 | 0.00 | 8.85 | 0 | 0.0 | 23.6 | 8.7 | 0 | 0.33 |
| B fight:compliance_officer@t4 | 20 | 0.00 | 15.00 | 0 | 0.0 | 50.0 | 10.8 | 0 | 0.28 |

