# Balance comparison: cal_policy_heur1

- A: `cal_builtin_s100.json` (overrides: none)
- B: `cal_heur1_s100.json` (overrides: none)
- mode fight; A 720 records, B 720 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 332 of 792 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:account_manager@t1 | dealt_per_turn | 18.992 | 21.230 | +2.238 | [+0.489, +3.884] | +11.8 % | **CHANGED** |
| fight:account_manager@t1 | hp_end | 40.650 | 48.700 | +8.050 | [+3.250, +13.002] | +19.8 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost | 19.350 | 11.300 | -8.050 | [-13.050, -3.250] | -41.6 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost_frac | 0.322 | 0.188 | -0.134 | [-0.216, -0.054] | -41.6 % | **CHANGED** |
| fight:account_manager@t1 | intake | 15.150 | 6.650 | -8.500 | [-12.903, -4.148] | -56.1 % | **CHANGED** |
| fight:account_manager@t1 | perfect_rate | 0.814 | 0.906 | +0.091 | [+0.035, +0.150] | +11.2 % | **CHANGED** |
| fight:account_manager@t1 | ram_left_per_turn | 7.820 | 5.046 | -2.774 | [-3.698, -1.836] | -35.5 % | **CHANGED** |
| fight:account_manager@t1 | resistance_absorbed | 9.300 | 12.750 | +3.450 | [+1.200, +5.557] | +37.1 % | **CHANGED** |
| fight:account_manager@t1 | taken | 19.350 | 11.300 | -8.050 | [-13.100, -3.200] | -41.6 % | **CHANGED** |
| fight:account_manager@t1 | taken_per_turn | 2.500 | 1.581 | -0.919 | [-1.694, -0.195] | -36.8 % | **CHANGED** |
| fight:account_manager@t1 | turns | 8.150 | 7.250 | -0.900 | [-1.600, -0.200] | -11.0 % | **CHANGED** |
| fight:account_manager@t1 | turns_both_share | 0.311 | 0.452 | +0.141 | [+0.041, +0.242] | +45.2 % | **CHANGED** |
| fight:account_manager@t2 | dealt_per_turn | 19.410 | 24.416 | +5.006 | [+3.403, +6.515] | +25.8 % | **CHANGED** |
| fight:account_manager@t2 | enrage_step | 1.250 | 0.750 | -0.500 | [-0.800, -0.250] | -40.0 % | **CHANGED** |
| fight:account_manager@t2 | hp_end | 22.150 | 37.400 | +15.250 | [+9.450, +21.300] | +68.8 % | **CHANGED** |
| fight:account_manager@t2 | hp_lost | 37.850 | 22.600 | -15.250 | [-21.250, -9.148] | -40.3 % | **CHANGED** |
| fight:account_manager@t2 | hp_lost_frac | 0.631 | 0.377 | -0.254 | [-0.355, -0.150] | -40.3 % | **CHANGED** |
| fight:account_manager@t2 | intake | 27.200 | 12.550 | -14.650 | [-20.300, -9.048] | -53.9 % | **CHANGED** |
| fight:account_manager@t2 | perfect_rate | 0.832 | 0.941 | +0.108 | [+0.065, +0.153] | +13.0 % | **CHANGED** |
| fight:account_manager@t2 | ram_left_per_turn | 8.255 | 4.678 | -3.577 | [-4.355, -2.699] | -43.3 % | **CHANGED** |
| fight:account_manager@t2 | resistance_absorbed | 14.850 | 18.600 | +3.750 | [+1.042, +6.450] | +25.3 % | **CHANGED** |
| fight:account_manager@t2 | taken | 37.850 | 22.600 | -15.250 | [-21.303, -9.447] | -40.3 % | **CHANGED** |
| fight:account_manager@t2 | taken_per_turn | 2.971 | 2.272 | -0.699 | [-1.179, -0.218] | -23.5 % | **CHANGED** |
| fight:account_manager@t2 | turns | 12.850 | 9.900 | -2.950 | [-3.950, -1.900] | -23.0 % | **CHANGED** |
| fight:account_manager@t2 | turns_both_share | 0.292 | 0.519 | +0.227 | [+0.153, +0.296] | +77.7 % | **CHANGED** |
| fight:account_manager@t3 | dealt | 320.850 | 384.000 | +63.150 | [+49.147, +76.650] | +19.7 % | **CHANGED** |
| fight:account_manager@t3 | dealt_per_turn | 16.271 | 24.458 | +8.187 | [+6.919, +9.505] | +50.3 % | **CHANGED** |
| fight:account_manager@t3 | died | 1.000 | 0.100 | -0.900 | [-1.000, -0.800] | -90.0 % | **CHANGED** |
| fight:account_manager@t3 | enrage_step | 2.650 | 1.800 | -0.850 | [-1.200, -0.500] | -32.1 % | **CHANGED** |
| fight:account_manager@t3 | hp_end | 0.000 | 19.800 | +19.800 | [+15.347, +24.350] | - | **CHANGED** |
| fight:account_manager@t3 | hp_lost | 60.000 | 40.200 | -19.800 | [-24.750, -15.400] | -33.0 % | **CHANGED** |
| fight:account_manager@t3 | hp_lost_frac | 1.000 | 0.670 | -0.330 | [-0.408, -0.256] | -33.0 % | **CHANGED** |
| fight:account_manager@t3 | intake | 43.700 | 20.700 | -23.000 | [-27.450, -18.797] | -52.6 % | **CHANGED** |
| fight:account_manager@t3 | perfect_rate | 0.792 | 0.947 | +0.154 | [+0.116, +0.194] | +19.5 % | **CHANGED** |
| fight:account_manager@t3 | ram_left_per_turn | 9.042 | 5.507 | -3.535 | [-4.246, -2.852] | -39.1 % | **CHANGED** |
| fight:account_manager@t3 | resistance_absorbed | 23.250 | 27.300 | +4.050 | [+0.450, +7.650] | +17.4 % | **CHANGED** |
| fight:account_manager@t3 | taken | 60.000 | 40.200 | -19.800 | [-24.450, -15.398] | -33.0 % | **CHANGED** |
| fight:account_manager@t3 | taken_per_turn | 3.079 | 2.538 | -0.541 | [-0.919, -0.188] | -17.6 % | **CHANGED** |
| fight:account_manager@t3 | turns | 20.200 | 15.850 | -4.350 | [-5.750, -2.900] | -21.5 % | **CHANGED** |
| fight:account_manager@t3 | turns_both_share | 0.233 | 0.490 | +0.257 | [+0.201, +0.316] | +110.5 % | **CHANGED** |
| fight:account_manager@t3 | won | 0.000 | 0.900 | +0.900 | [+0.800, +1.000] | - | **CHANGED** |
| fight:account_manager@t4 | dealt | 305.300 | 582.650 | +277.350 | [+237.447, +318.655] | +90.8 % | **CHANGED** |
| fight:account_manager@t4 | dealt_per_turn | 15.009 | 22.497 | +7.488 | [+5.954, +9.083] | +49.9 % | **CHANGED** |
| fight:account_manager@t4 | died | 1.000 | 0.450 | -0.550 | [-0.750, -0.350] | -55.0 % | **CHANGED** |
| fight:account_manager@t4 | enrage_step | 2.650 | 3.850 | +1.200 | [+0.750, +1.650] | +45.3 % | **CHANGED** |
| fight:account_manager@t4 | hp_end | 0.000 | 5.150 | +5.150 | [+2.397, +8.150] | - | **CHANGED** |
| fight:account_manager@t4 | hp_lost | 60.000 | 54.850 | -5.150 | [-8.353, -2.400] | -8.6 % | **CHANGED** |
| fight:account_manager@t4 | hp_lost_frac | 1.000 | 0.914 | -0.086 | [-0.140, -0.039] | -8.6 % | **CHANGED** |
| fight:account_manager@t4 | intake | 41.400 | 20.950 | -20.450 | [-25.300, -15.450] | -49.4 % | **CHANGED** |
| fight:account_manager@t4 | parked | 1.800 | 11.150 | +9.350 | [+7.150, +11.400] | +519.4 % | **CHANGED** |
| fight:account_manager@t4 | perfect_rate | 0.795 | 0.916 | +0.121 | [+0.086, +0.156] | +15.2 % | **CHANGED** |
| fight:account_manager@t4 | ram_left_per_turn | 9.093 | 5.603 | -3.490 | [-4.325, -2.733] | -38.4 % | **CHANGED** |
| fight:account_manager@t4 | resistance_absorbed | 19.950 | 50.100 | +30.150 | [+25.800, +34.500] | +151.1 % | **CHANGED** |
| fight:account_manager@t4 | taken | 60.000 | 54.850 | -5.150 | [-8.200, -2.547] | -8.6 % | **CHANGED** |
| fight:account_manager@t4 | taken_per_turn | 3.178 | 2.137 | -1.041 | [-1.424, -0.679] | -32.7 % | **CHANGED** |
| fight:account_manager@t4 | turns | 20.250 | 26.150 | +5.900 | [+3.650, +8.102] | +29.1 % | **CHANGED** |
| fight:account_manager@t4 | turns_both_share | 0.203 | 0.504 | +0.302 | [+0.247, +0.353] | +149.0 % | **CHANGED** |
| fight:account_manager@t4 | won | 0.000 | 0.550 | +0.550 | [+0.350, +0.750] | - | **CHANGED** |
| fight:billing_daemon@t1 | hp_end | 56.400 | 58.000 | +1.600 | [+0.100, +3.150] | +2.8 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_lost | 3.600 | 2.000 | -1.600 | [-3.100, -0.150] | -44.4 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_lost_frac | 0.060 | 0.033 | -0.027 | [-0.052, -0.001] | -44.4 % | **CHANGED** |
| fight:billing_daemon@t1 | ram_left_per_turn | 4.366 | 2.841 | -1.524 | [-2.358, -0.650] | -34.9 % | **CHANGED** |
| fight:billing_daemon@t1 | taken | 3.600 | 2.000 | -1.600 | [-3.153, -0.050] | -44.4 % | **CHANGED** |
| fight:billing_daemon@t1 | turns_both_share | 0.529 | 0.683 | +0.154 | [+0.004, +0.304] | +29.1 % | **CHANGED** |
| fight:billing_daemon@t2 | combat_hash | 2027441879.000 | 2774490671.800 | +747048792.800 | [+142746165.795, +1346971494.682] | +36.8 % | **CHANGED** |
| fight:billing_daemon@t2 | dealt_per_turn | 16.000 | 19.540 | +3.540 | [+1.619, +5.469] | +22.1 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_end | 52.150 | 56.850 | +4.700 | [+2.300, +7.203] | +9.0 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_lost | 7.850 | 3.150 | -4.700 | [-7.300, -2.350] | -59.9 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_lost_frac | 0.131 | 0.052 | -0.078 | [-0.120, -0.038] | -59.9 % | **CHANGED** |
| fight:billing_daemon@t2 | intake | 6.950 | 2.400 | -4.550 | [-7.100, -2.300] | -65.5 % | **CHANGED** |
| fight:billing_daemon@t2 | perfect_rate | 0.847 | 0.975 | +0.128 | [+0.068, +0.189] | +15.1 % | **CHANGED** |
| fight:billing_daemon@t2 | ram_left_per_turn | 5.839 | 3.171 | -2.668 | [-3.544, -1.767] | -45.7 % | **CHANGED** |
| fight:billing_daemon@t2 | resistance_absorbed | 2.200 | 2.850 | +0.650 | [+0.250, +1.100] | +29.5 % | **CHANGED** |
| fight:billing_daemon@t2 | taken | 7.850 | 3.150 | -4.700 | [-7.400, -2.350] | -59.9 % | **CHANGED** |
| fight:billing_daemon@t2 | taken_per_turn | 1.830 | 0.879 | -0.951 | [-1.610, -0.325] | -51.9 % | **CHANGED** |
| fight:billing_daemon@t2 | turns | 4.500 | 3.500 | -1.000 | [-1.500, -0.500] | -22.2 % | **CHANGED** |
| fight:billing_daemon@t2 | turns_both_share | 0.426 | 0.671 | +0.245 | [+0.108, +0.380] | +57.5 % | **CHANGED** |
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 20.405 | +3.891 | [+2.140, +5.614] | +23.6 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_end | 48.450 | 53.300 | +4.850 | [+1.450, +8.250] | +10.0 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_lost | 11.550 | 6.700 | -4.850 | [-8.153, -1.650] | -42.0 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_lost_frac | 0.193 | 0.112 | -0.081 | [-0.139, -0.023] | -42.0 % | **CHANGED** |
| fight:billing_daemon@t3 | intake | 8.700 | 4.000 | -4.700 | [-7.700, -1.600] | -54.0 % | **CHANGED** |
| fight:billing_daemon@t3 | perfect_rate | 0.884 | 0.966 | +0.082 | [+0.030, +0.136] | +9.2 % | **CHANGED** |
| fight:billing_daemon@t3 | ram_left_per_turn | 5.345 | 3.477 | -1.868 | [-2.756, -0.996] | -34.9 % | **CHANGED** |
| fight:billing_daemon@t3 | taken | 11.550 | 6.700 | -4.850 | [-8.400, -1.600] | -42.0 % | **CHANGED** |
| fight:billing_daemon@t3 | turns | 6.750 | 5.450 | -1.300 | [-1.850, -0.750] | -19.3 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 19.518 | +4.200 | [+2.497, +5.862] | +27.4 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_end | 34.800 | 45.850 | +11.050 | [+4.950, +17.250] | +31.8 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_lost | 25.200 | 14.150 | -11.050 | [-17.353, -4.998] | -43.8 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_lost_frac | 0.420 | 0.236 | -0.184 | [-0.291, -0.084] | -43.8 % | **CHANGED** |
| fight:billing_daemon@t4 | intake | 19.800 | 8.000 | -11.800 | [-17.650, -6.348] | -59.6 % | **CHANGED** |
| fight:billing_daemon@t4 | perfect_rate | 0.867 | 0.948 | +0.081 | [+0.040, +0.122] | +9.3 % | **CHANGED** |
| fight:billing_daemon@t4 | ram_left_per_turn | 7.341 | 3.592 | -3.748 | [-4.618, -2.831] | -51.1 % | **CHANGED** |
| fight:billing_daemon@t4 | taken | 25.200 | 14.150 | -11.050 | [-17.303, -5.000] | -43.8 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 11.650 | 9.100 | -2.550 | [-3.500, -1.550] | -21.9 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.623 | +0.147 | [+0.057, +0.234] | +30.8 % | **CHANGED** |
| fight:care_swarm@t1 | dealt_per_turn | 10.886 | 15.000 | +4.114 | [+0.750, +7.250] | +37.8 % | **CHANGED** |
| fight:care_swarm@t1 | ram_left_per_turn | 5.719 | 3.216 | -2.502 | [-3.661, -1.338] | -43.8 % | **CHANGED** |
| fight:care_swarm@t1 | resistance_absorbed | 1.400 | 0.750 | -0.650 | [-1.100, -0.200] | -46.4 % | **CHANGED** |
| fight:care_swarm@t1 | taken_per_turn | 4.865 | 6.050 | +1.185 | [+0.105, +2.236] | +24.4 % | **CHANGED** |
| fight:care_swarm@t1 | turns | 3.050 | 1.900 | -1.150 | [-1.800, -0.550] | -37.7 % | **CHANGED** |
| fight:care_swarm@t2 | dealt_per_turn | 10.968 | 14.799 | +3.831 | [+1.682, +6.017] | +34.9 % | **CHANGED** |
| fight:care_swarm@t2 | ram_left_per_turn | 6.272 | 3.716 | -2.556 | [-3.621, -1.495] | -40.7 % | **CHANGED** |
| fight:care_swarm@t2 | taken | 22.900 | 19.650 | -3.250 | [-6.600, -0.150] | -14.2 % | **CHANGED** |
| fight:care_swarm@t2 | turns | 4.150 | 2.950 | -1.200 | [-1.850, -0.550] | -28.9 % | **CHANGED** |
| fight:care_swarm@t3 | dealt_per_turn | 10.205 | 14.620 | +4.415 | [+2.330, +6.408] | +43.3 % | **CHANGED** |
| fight:care_swarm@t3 | hp_end | 14.000 | 23.950 | +9.950 | [+4.700, +14.950] | +71.1 % | **CHANGED** |
| fight:care_swarm@t3 | hp_lost | 46.000 | 36.050 | -9.950 | [-14.900, -4.600] | -21.6 % | **CHANGED** |
| fight:care_swarm@t3 | hp_lost_frac | 0.767 | 0.601 | -0.166 | [-0.251, -0.084] | -21.6 % | **CHANGED** |
| fight:care_swarm@t3 | intake | 44.950 | 35.000 | -9.950 | [-14.800, -5.000] | -22.1 % | **CHANGED** |
| fight:care_swarm@t3 | ram_left_per_turn | 7.303 | 4.662 | -2.641 | [-3.726, -1.523] | -36.2 % | **CHANGED** |
| fight:care_swarm@t3 | taken | 46.000 | 36.050 | -9.950 | [-15.050, -5.050] | -21.6 % | **CHANGED** |
| fight:care_swarm@t3 | turns | 7.100 | 4.850 | -2.250 | [-3.350, -1.150] | -31.7 % | **CHANGED** |
| fight:care_swarm@t4 | combat_hash | 1882330650.250 | 2489646231.050 | +607315580.800 | [+9233049.548, +1183469719.160] | +32.3 % | **CHANGED** |
| fight:care_swarm@t4 | dealt | 56.700 | 88.050 | +31.350 | [+22.950, +39.403] | +55.3 % | **CHANGED** |
| fight:care_swarm@t4 | dealt_per_turn | 9.313 | 14.661 | +5.348 | [+3.324, +7.521] | +57.4 % | **CHANGED** |
| fight:care_swarm@t4 | perfect_rate | 0.845 | 0.950 | +0.105 | [+0.045, +0.171] | +12.5 % | **CHANGED** |
| fight:care_swarm@t4 | ram_left_per_turn | 7.740 | 5.074 | -2.667 | [-3.623, -1.713] | -34.5 % | **CHANGED** |
| fight:care_swarm@t4 | resistance_absorbed | 2.600 | 3.600 | +1.000 | [+0.300, +1.700] | +38.5 % | **CHANGED** |
| fight:care_swarm@t4 | turns_both_share | 0.328 | 0.502 | +0.174 | [+0.077, +0.269] | +53.1 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_end | 40.900 | 49.150 | +8.250 | [+3.397, +12.850] | +20.2 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost | 19.100 | 10.850 | -8.250 | [-13.150, -3.298] | -43.2 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost_frac | 0.318 | 0.181 | -0.137 | [-0.220, -0.061] | -43.2 % | **CHANGED** |
| fight:claims_adjuster@t1 | intake | 17.900 | 10.400 | -7.500 | [-12.300, -2.800] | -41.9 % | **CHANGED** |
| fight:claims_adjuster@t1 | ram_left_per_turn | 5.487 | 3.220 | -2.267 | [-3.249, -1.245] | -41.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | resistance_absorbed | 3.900 | 5.400 | +1.500 | [+0.150, +2.850] | +38.5 % | **CHANGED** |
| fight:claims_adjuster@t1 | taken | 19.100 | 10.850 | -8.250 | [-12.850, -3.448] | -43.2 % | **CHANGED** |
| fight:claims_adjuster@t1 | taken_per_turn | 6.366 | 4.108 | -2.258 | [-3.927, -0.598] | -35.5 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns | 3.200 | 2.700 | -0.500 | [-0.900, -0.100] | -15.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns_both_share | 0.320 | 0.571 | +0.251 | [+0.120, +0.381] | +78.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | dealt_per_turn | 35.969 | 43.109 | +7.140 | [+2.899, +11.385] | +19.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_end | 26.300 | 41.750 | +15.450 | [+8.700, +21.550] | +58.7 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost | 33.700 | 18.250 | -15.450 | [-22.003, -9.198] | -45.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost_frac | 0.562 | 0.304 | -0.257 | [-0.363, -0.149] | -45.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | intake | 30.700 | 16.000 | -14.700 | [-21.153, -8.143] | -47.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | ram_left_per_turn | 6.562 | 3.856 | -2.706 | [-3.699, -1.700] | -41.2 % | **CHANGED** |
| fight:claims_adjuster@t2 | taken | 33.700 | 18.250 | -15.450 | [-21.653, -9.198] | -45.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | taken_per_turn | 6.578 | 4.523 | -2.055 | [-3.402, -0.615] | -31.2 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns | 5.200 | 4.300 | -0.900 | [-1.350, -0.450] | -17.3 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns_both_share | 0.372 | 0.507 | +0.135 | [+0.029, +0.245] | +36.2 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt | 262.350 | 287.000 | +24.650 | [+10.500, +41.702] | +9.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt_per_turn | 33.029 | 40.084 | +7.055 | [+3.909, +10.274] | +21.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | died | 0.650 | 0.050 | -0.600 | [-0.800, -0.400] | -92.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | hp_end | 4.200 | 28.350 | +24.150 | [+18.547, +30.003] | +575.0 % | **CHANGED** |
| fight:claims_adjuster@t3 | hp_lost | 55.800 | 31.650 | -24.150 | [-30.103, -18.100] | -43.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | hp_lost_frac | 0.930 | 0.528 | -0.403 | [-0.500, -0.302] | -43.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | intake | 50.400 | 24.750 | -25.650 | [-31.553, -19.100] | -50.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | perfect_rate | 0.898 | 0.955 | +0.057 | [+0.013, +0.102] | +6.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | ram_left_per_turn | 7.664 | 3.530 | -4.134 | [-4.961, -3.204] | -53.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | resistance_absorbed | 8.550 | 15.600 | +7.050 | [+4.800, +9.150] | +82.5 % | **CHANGED** |
| fight:claims_adjuster@t3 | taken | 55.800 | 31.650 | -24.150 | [-30.102, -18.000] | -43.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | taken_per_turn | 7.232 | 4.489 | -2.743 | [-3.908, -1.530] | -37.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns_both_share | 0.273 | 0.607 | +0.334 | [+0.248, +0.419] | +122.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | won | 0.350 | 0.950 | +0.600 | [+0.400, +0.800] | +171.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt | 240.150 | 440.700 | +200.550 | [+167.093, +230.415] | +83.5 % | **CHANGED** |
| fight:claims_adjuster@t4 | died | 1.000 | 0.250 | -0.750 | [-0.900, -0.600] | -75.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | enrage_step | 0.600 | 1.500 | +0.900 | [+0.600, +1.200] | +150.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | hp_end | 0.000 | 11.050 | +11.050 | [+6.300, +16.052] | - | **CHANGED** |
| fight:claims_adjuster@t4 | hp_lost | 60.000 | 48.950 | -11.050 | [-16.300, -6.297] | -18.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | hp_lost_frac | 1.000 | 0.816 | -0.184 | [-0.273, -0.105] | -18.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | intake | 55.500 | 35.300 | -20.200 | [-25.853, -14.848] | -36.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | perfect_rate | 0.877 | 0.940 | +0.062 | [+0.009, +0.114] | +7.1 % | **CHANGED** |
| fight:claims_adjuster@t4 | ram_left_per_turn | 7.476 | 3.682 | -3.794 | [-4.670, -2.818] | -50.8 % | **CHANGED** |
| fight:claims_adjuster@t4 | resistance_absorbed | 8.850 | 26.100 | +17.250 | [+13.950, +20.550] | +194.9 % | **CHANGED** |
| fight:claims_adjuster@t4 | taken | 60.000 | 48.950 | -11.050 | [-16.152, -6.200] | -18.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | taken_per_turn | 9.357 | 4.194 | -5.163 | [-7.080, -3.417] | -55.2 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns | 7.700 | 12.300 | +4.600 | [+3.200, +6.002] | +59.7 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns_both_share | 0.231 | 0.601 | +0.370 | [+0.301, +0.440] | +160.3 % | **CHANGED** |
| fight:claims_adjuster@t4 | won | 0.000 | 0.750 | +0.750 | [+0.600, +0.900] | - | **CHANGED** |
| fight:collections_agent@t1 | combat_hash | 2348250131.200 | 1698206180.050 | -650043951.150 | [-1215172559.045, -49479161.990] | -27.7 % | **CHANGED** |
| fight:collections_agent@t1 | dealt_per_turn | 15.332 | 18.333 | +3.001 | [+1.001, +4.835] | +19.6 % | **CHANGED** |
| fight:collections_agent@t1 | ram_left_per_turn | 5.700 | 3.525 | -2.175 | [-3.242, -1.051] | -38.2 % | **CHANGED** |
| fight:collections_agent@t1 | turns | 2.800 | 2.300 | -0.500 | [-0.850, -0.150] | -17.9 % | **CHANGED** |
| fight:collections_agent@t2 | combat_hash | 1614174098.100 | 2264861346.500 | +650687248.400 | [+235508130.437, +1099522913.255] | +40.3 % | **CHANGED** |
| fight:collections_agent@t2 | dealt_per_turn | 16.811 | 19.837 | +3.026 | [+0.947, +5.100] | +18.0 % | **CHANGED** |
| fight:collections_agent@t2 | ram_left_per_turn | 6.441 | 3.491 | -2.950 | [-3.976, -1.881] | -45.8 % | **CHANGED** |
| fight:collections_agent@t2 | turns | 4.200 | 3.350 | -0.850 | [-1.500, -0.250] | -20.2 % | **CHANGED** |
| fight:collections_agent@t2 | turns_both_share | 0.439 | 0.593 | +0.154 | [+0.023, +0.297] | +35.2 % | **CHANGED** |
| fight:collections_agent@t3 | dealt_per_turn | 16.922 | 21.213 | +4.291 | [+2.390, +6.099] | +25.4 % | **CHANGED** |
| fight:collections_agent@t3 | hp_end | 41.150 | 44.750 | +3.600 | [+0.850, +6.450] | +8.7 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost | 18.850 | 15.250 | -3.600 | [-6.400, -0.850] | -19.1 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost_frac | 0.314 | 0.254 | -0.060 | [-0.104, -0.014] | -19.1 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 16.150 | 11.350 | -4.800 | [-7.850, -1.900] | -29.7 % | **CHANGED** |
| fight:collections_agent@t3 | ram_left_per_turn | 6.897 | 3.763 | -3.134 | [-4.089, -2.068] | -45.4 % | **CHANGED** |
| fight:collections_agent@t3 | taken | 18.850 | 15.250 | -3.600 | [-6.350, -0.950] | -19.1 % | **CHANGED** |
| fight:collections_agent@t3 | turns | 6.300 | 4.950 | -1.350 | [-1.900, -0.750] | -21.4 % | **CHANGED** |
| fight:collections_agent@t3 | turns_both_share | 0.459 | 0.662 | +0.203 | [+0.099, +0.306] | +44.3 % | **CHANGED** |
| fight:collections_agent@t4 | dealt_per_turn | 16.698 | 20.776 | +4.078 | [+2.751, +5.366] | +24.4 % | **CHANGED** |
| fight:collections_agent@t4 | hp_end | 16.850 | 28.700 | +11.850 | [+7.250, +16.650] | +70.3 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost | 43.150 | 31.300 | -11.850 | [-16.553, -7.398] | -27.5 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost_frac | 0.719 | 0.522 | -0.198 | [-0.276, -0.123] | -27.5 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 23.650 | -12.150 | [-17.200, -7.750] | -33.9 % | **CHANGED** |
| fight:collections_agent@t4 | ram_left_per_turn | 7.800 | 4.365 | -3.435 | [-4.311, -2.561] | -44.0 % | **CHANGED** |
| fight:collections_agent@t4 | taken | 43.150 | 31.300 | -11.850 | [-16.503, -7.450] | -27.5 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 10.000 | 8.000 | -2.000 | [-2.600, -1.400] | -20.0 % | **CHANGED** |
| fight:collections_agent@t4 | turns_both_share | 0.415 | 0.541 | +0.125 | [+0.056, +0.193] | +30.2 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_end | 55.200 | 57.450 | +2.250 | [+0.600, +3.900] | +4.1 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_lost | 4.800 | 2.550 | -2.250 | [-3.950, -0.550] | -46.9 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_lost_frac | 0.080 | 0.043 | -0.037 | [-0.065, -0.009] | -46.9 % | **CHANGED** |
| fight:compliance_officer@t1 | intake | 4.200 | 1.950 | -2.250 | [-3.850, -0.650] | -53.6 % | **CHANGED** |
| fight:compliance_officer@t1 | ram_left_per_turn | 5.187 | 2.737 | -2.450 | [-3.283, -1.646] | -47.2 % | **CHANGED** |
| fight:compliance_officer@t1 | resistance_absorbed | 2.800 | 4.300 | +1.500 | [+0.700, +2.300] | +53.6 % | **CHANGED** |
| fight:compliance_officer@t1 | taken | 4.800 | 2.550 | -2.250 | [-4.000, -0.500] | -46.9 % | **CHANGED** |
| fight:compliance_officer@t1 | taken_per_turn | 1.820 | 0.987 | -0.833 | [-1.542, -0.115] | -45.8 % | **CHANGED** |
| fight:compliance_officer@t1 | turns_both_share | 0.371 | 0.646 | +0.275 | [+0.142, +0.400] | +74.2 % | **CHANGED** |
| fight:compliance_officer@t2 | dealt_per_turn | 15.855 | 20.601 | +4.745 | [+2.521, +6.936] | +29.9 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_end | 50.800 | 55.350 | +4.550 | [+2.250, +6.700] | +9.0 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_lost | 9.200 | 4.650 | -4.550 | [-6.750, -2.150] | -49.5 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_lost_frac | 0.153 | 0.077 | -0.076 | [-0.113, -0.037] | -49.5 % | **CHANGED** |
| fight:compliance_officer@t2 | intake | 7.850 | 3.150 | -4.700 | [-6.903, -2.400] | -59.9 % | **CHANGED** |
| fight:compliance_officer@t2 | perfect_rate | 0.889 | 0.952 | +0.063 | [+0.009, +0.116] | +7.1 % | **CHANGED** |
| fight:compliance_officer@t2 | ram_left_per_turn | 6.705 | 3.317 | -3.388 | [-4.187, -2.553] | -50.5 % | **CHANGED** |
| fight:compliance_officer@t2 | resistance_absorbed | 4.400 | 6.500 | +2.100 | [+0.900, +3.400] | +47.7 % | **CHANGED** |
| fight:compliance_officer@t2 | taken | 9.200 | 4.650 | -4.550 | [-6.600, -2.250] | -49.5 % | **CHANGED** |
| fight:compliance_officer@t2 | taken_per_turn | 1.873 | 1.234 | -0.639 | [-1.241, -0.017] | -34.1 % | **CHANGED** |
| fight:compliance_officer@t2 | turns | 5.450 | 4.100 | -1.350 | [-2.050, -0.700] | -24.8 % | **CHANGED** |
| fight:compliance_officer@t2 | turns_both_share | 0.323 | 0.642 | +0.319 | [+0.214, +0.418] | +98.8 % | **CHANGED** |
| fight:compliance_officer@t3 | combat_hash | 1556676763.600 | 2285189764.100 | +728513000.500 | [+110185695.367, +1348238250.972] | +46.8 % | **CHANGED** |
| fight:compliance_officer@t3 | dealt_per_turn | 15.041 | 20.117 | +5.075 | [+3.460, +6.745] | +33.7 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_end | 40.800 | 52.500 | +11.700 | [+7.400, +16.100] | +28.7 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 7.500 | -11.700 | [-15.900, -7.350] | -60.9 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost_frac | 0.320 | 0.125 | -0.195 | [-0.271, -0.122] | -60.9 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 3.900 | -11.700 | [-15.800, -7.395] | -75.0 % | **CHANGED** |
| fight:compliance_officer@t3 | ram_left_per_turn | 7.166 | 3.751 | -3.415 | [-4.223, -2.563] | -47.7 % | **CHANGED** |
| fight:compliance_officer@t3 | taken | 19.200 | 7.500 | -11.700 | [-16.100, -7.500] | -60.9 % | **CHANGED** |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 1.179 | -1.098 | [-1.697, -0.517] | -48.2 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 8.850 | 6.550 | -2.300 | [-3.100, -1.500] | -26.0 % | **CHANGED** |
| fight:compliance_officer@t3 | turns_both_share | 0.353 | 0.599 | +0.246 | [+0.148, +0.348] | +69.7 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt_per_turn | 15.738 | 19.736 | +3.998 | [+2.708, +5.206] | +25.4 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_end | 20.200 | 41.850 | +21.650 | [+15.497, +27.450] | +107.2 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 18.150 | -21.650 | [-27.400, -15.300] | -54.4 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost_frac | 0.663 | 0.302 | -0.361 | [-0.461, -0.262] | -54.4 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 32.300 | 10.500 | -21.800 | [-27.703, -15.750] | -67.5 % | **CHANGED** |
| fight:compliance_officer@t4 | perfect_rate | 0.888 | 0.947 | +0.059 | [+0.025, +0.093] | +6.6 % | **CHANGED** |
| fight:compliance_officer@t4 | ram_left_per_turn | 7.871 | 2.756 | -5.115 | [-5.733, -4.413] | -65.0 % | **CHANGED** |
| fight:compliance_officer@t4 | resistance_absorbed | 12.000 | 16.000 | +4.000 | [+2.200, +5.700] | +33.3 % | **CHANGED** |
| fight:compliance_officer@t4 | taken | 39.800 | 18.150 | -21.650 | [-27.453, -15.600] | -54.4 % | **CHANGED** |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 1.758 | -1.385 | [-2.015, -0.774] | -44.1 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 13.300 | 10.550 | -2.750 | [-3.700, -1.800] | -20.7 % | **CHANGED** |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.623 | +0.267 | [+0.189, +0.345] | +74.9 % | **CHANGED** |
| fight:dosage_dispenser@t1 | dealt_per_turn | 16.468 | 18.050 | +1.583 | [+0.001, +3.166] | +9.6 % | **CHANGED** |
| fight:dosage_dispenser@t1 | ram_left_per_turn | 5.245 | 4.367 | -0.879 | [-1.804, -0.034] | -16.8 % | **CHANGED** |
| fight:dosage_dispenser@t2 | combat_hash | 2577982977.150 | 1902733627.500 | -675249349.650 | [-1312843984.555, -56617481.833] | -26.2 % | **CHANGED** |
| fight:dosage_dispenser@t2 | dealt_per_turn | 17.840 | 19.669 | +1.829 | [+0.355, +3.353] | +10.3 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns | 3.600 | 3.150 | -0.450 | [-0.850, -0.100] | -12.5 % | **CHANGED** |
| fight:dosage_dispenser@t3 | combat_hash | 2094462071.050 | 2838644462.900 | +744182391.850 | [+167836206.665, +1308156206.920] | +35.5 % | **CHANGED** |
| fight:dosage_dispenser@t3 | dealt_per_turn | 17.935 | 21.178 | +3.244 | [+1.396, +4.957] | +18.1 % | **CHANGED** |
| fight:dosage_dispenser@t3 | ram_left_per_turn | 7.222 | 5.038 | -2.183 | [-3.100, -1.259] | -30.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns | 5.700 | 4.650 | -1.050 | [-1.600, -0.550] | -18.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | dealt_per_turn | 19.386 | 22.985 | +3.598 | [+2.056, +5.042] | +18.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | perfect_rate | 0.897 | 0.965 | +0.068 | [+0.029, +0.108] | +7.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | ram_left_per_turn | 7.707 | 5.563 | -2.143 | [-2.991, -1.311] | -27.8 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns | 8.300 | 6.850 | -1.450 | [-2.100, -0.900] | -17.5 % | **CHANGED** |
| fight:recall_unit@t1 | dealt_per_turn | 17.702 | 21.037 | +3.335 | [+1.507, +5.183] | +18.8 % | **CHANGED** |
| fight:recall_unit@t1 | enrage_step | 0.150 | 0.000 | -0.150 | [-0.300, -0.050] | -100.0 % | **CHANGED** |
| fight:recall_unit@t1 | hp_end | 42.300 | 51.450 | +9.150 | [+5.100, +13.050] | +21.6 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost | 17.700 | 8.550 | -9.150 | [-13.103, -4.998] | -51.7 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost_frac | 0.295 | 0.143 | -0.152 | [-0.220, -0.087] | -51.7 % | **CHANGED** |
| fight:recall_unit@t1 | intake | 15.600 | 5.850 | -9.750 | [-13.753, -5.548] | -62.5 % | **CHANGED** |
| fight:recall_unit@t1 | perfect_rate | 0.914 | 0.976 | +0.061 | [+0.026, +0.097] | +6.7 % | **CHANGED** |
| fight:recall_unit@t1 | ram_left_per_turn | 7.208 | 3.511 | -3.697 | [-4.424, -2.962] | -51.3 % | **CHANGED** |
| fight:recall_unit@t1 | resistance_absorbed | 5.400 | 9.900 | +4.500 | [+2.400, +6.750] | +83.3 % | **CHANGED** |
| fight:recall_unit@t1 | taken | 17.700 | 8.550 | -9.150 | [-13.300, -4.850] | -51.7 % | **CHANGED** |
| fight:recall_unit@t1 | taken_per_turn | 2.957 | 1.741 | -1.216 | [-1.995, -0.468] | -41.1 % | **CHANGED** |
| fight:recall_unit@t1 | turns | 6.200 | 5.200 | -1.000 | [-1.550, -0.450] | -16.1 % | **CHANGED** |
| fight:recall_unit@t1 | turns_both_share | 0.216 | 0.472 | +0.256 | [+0.133, +0.368] | +118.7 % | **CHANGED** |
| fight:recall_unit@t2 | combat_hash | 2662215628.800 | 2041491675.650 | -620723953.150 | [-1205874842.270, -28866567.460] | -23.3 % | **CHANGED** |
| fight:recall_unit@t2 | dealt_per_turn | 15.864 | 20.195 | +4.331 | [+3.020, +5.684] | +27.3 % | **CHANGED** |
| fight:recall_unit@t2 | enrage_step | 1.100 | 0.850 | -0.250 | [-0.450, -0.100] | -22.7 % | **CHANGED** |
| fight:recall_unit@t2 | hp_end | 23.650 | 43.550 | +19.900 | [+13.650, +26.402] | +84.1 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost | 36.350 | 16.450 | -19.900 | [-26.700, -13.447] | -54.7 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost_frac | 0.606 | 0.274 | -0.332 | [-0.436, -0.222] | -54.7 % | **CHANGED** |
| fight:recall_unit@t2 | intake | 30.500 | 10.300 | -20.200 | [-27.153, -13.298] | -66.2 % | **CHANGED** |
| fight:recall_unit@t2 | perfect_rate | 0.904 | 0.959 | +0.055 | [+0.019, +0.090] | +6.1 % | **CHANGED** |
| fight:recall_unit@t2 | ram_left_per_turn | 8.293 | 3.824 | -4.469 | [-5.120, -3.757] | -53.9 % | **CHANGED** |
| fight:recall_unit@t2 | resistance_absorbed | 10.500 | 16.050 | +5.550 | [+3.150, +7.950] | +52.9 % | **CHANGED** |
| fight:recall_unit@t2 | taken | 36.350 | 16.450 | -19.900 | [-26.400, -13.150] | -54.7 % | **CHANGED** |
| fight:recall_unit@t2 | taken_per_turn | 3.508 | 1.966 | -1.542 | [-2.302, -0.802] | -43.9 % | **CHANGED** |
| fight:recall_unit@t2 | turns | 10.750 | 8.600 | -2.150 | [-2.800, -1.500] | -20.0 % | **CHANGED** |
| fight:recall_unit@t2 | turns_both_share | 0.234 | 0.498 | +0.264 | [+0.177, +0.347] | +113.0 % | **CHANGED** |
| fight:recall_unit@t3 | dealt | 221.550 | 271.000 | +49.450 | [+31.450, +68.252] | +22.3 % | **CHANGED** |
| fight:recall_unit@t3 | dealt_per_turn | 14.155 | 18.674 | +4.518 | [+3.118, +6.000] | +31.9 % | **CHANGED** |
| fight:recall_unit@t3 | died | 0.750 | 0.000 | -0.750 | [-0.900, -0.600] | -100.0 % | **CHANGED** |
| fight:recall_unit@t3 | hp_end | 2.250 | 34.200 | +31.950 | [+28.500, +35.500] | +1420.0 % | **CHANGED** |
| fight:recall_unit@t3 | hp_lost | 57.750 | 25.800 | -31.950 | [-35.400, -28.297] | -55.3 % | **CHANGED** |
| fight:recall_unit@t3 | hp_lost_frac | 0.963 | 0.430 | -0.533 | [-0.591, -0.472] | -55.3 % | **CHANGED** |
| fight:recall_unit@t3 | intake | 49.800 | 13.350 | -36.450 | [-41.302, -31.600] | -73.2 % | **CHANGED** |
| fight:recall_unit@t3 | perfect_rate | 0.830 | 0.938 | +0.108 | [+0.055, +0.160] | +13.0 % | **CHANGED** |
| fight:recall_unit@t3 | ram_left_per_turn | 8.856 | 3.895 | -4.961 | [-5.690, -4.175] | -56.0 % | **CHANGED** |
| fight:recall_unit@t3 | resistance_absorbed | 17.100 | 28.750 | +11.650 | [+8.400, +15.300] | +68.1 % | **CHANGED** |
| fight:recall_unit@t3 | taken | 57.750 | 25.800 | -31.950 | [-35.550, -28.350] | -55.3 % | **CHANGED** |
| fight:recall_unit@t3 | taken_per_turn | 3.933 | 1.798 | -2.135 | [-2.815, -1.518] | -54.3 % | **CHANGED** |
| fight:recall_unit@t3 | turns_both_share | 0.219 | 0.554 | +0.335 | [+0.277, +0.393] | +152.9 % | **CHANGED** |
| fight:recall_unit@t3 | won | 0.250 | 1.000 | +0.750 | [+0.600, +0.900] | +300.0 % | **CHANGED** |
| fight:recall_unit@t4 | dealt | 215.100 | 423.550 | +208.450 | [+168.098, +250.002] | +96.9 % | **CHANGED** |
| fight:recall_unit@t4 | dealt_per_turn | 13.893 | 17.341 | +3.448 | [+2.117, +4.829] | +24.8 % | **CHANGED** |
| fight:recall_unit@t4 | died | 1.000 | 0.050 | -0.950 | [-1.000, -0.850] | -95.0 % | **CHANGED** |
| fight:recall_unit@t4 | enrage_step | 2.300 | 3.850 | +1.550 | [+0.950, +2.150] | +67.4 % | **CHANGED** |
| fight:recall_unit@t4 | hp_end | 0.000 | 21.000 | +21.000 | [+16.550, +25.502] | - | **CHANGED** |
| fight:recall_unit@t4 | hp_lost | 60.000 | 39.000 | -21.000 | [-25.450, -16.547] | -35.0 % | **CHANGED** |
| fight:recall_unit@t4 | hp_lost_frac | 1.000 | 0.650 | -0.350 | [-0.426, -0.280] | -35.0 % | **CHANGED** |
| fight:recall_unit@t4 | intake | 51.900 | 16.350 | -35.550 | [-40.850, -29.898] | -68.5 % | **CHANGED** |
| fight:recall_unit@t4 | perfect_rate | 0.785 | 0.905 | +0.120 | [+0.069, +0.169] | +15.2 % | **CHANGED** |
| fight:recall_unit@t4 | ram_left_per_turn | 8.711 | 5.213 | -3.498 | [-4.112, -2.893] | -40.2 % | **CHANGED** |
| fight:recall_unit@t4 | resistance_absorbed | 17.850 | 48.650 | +30.800 | [+24.950, +37.002] | +172.5 % | **CHANGED** |
| fight:recall_unit@t4 | taken | 60.000 | 39.000 | -21.000 | [-25.203, -16.650] | -35.0 % | **CHANGED** |
| fight:recall_unit@t4 | taken_per_turn | 5.106 | 1.675 | -3.431 | [-4.959, -2.128] | -67.2 % | **CHANGED** |
| fight:recall_unit@t4 | turns | 16.000 | 24.700 | +8.700 | [+5.850, +11.500] | +54.4 % | **CHANGED** |
| fight:recall_unit@t4 | turns_both_share | 0.208 | 0.536 | +0.328 | [+0.264, +0.393] | +157.8 % | **CHANGED** |
| fight:recall_unit@t4 | won | 0.000 | 0.950 | +0.950 | [+0.850, +1.000] | - | **CHANGED** |
| fight:triage_unit@t1 | intake | 0.450 | 0.000 | -0.450 | [-0.900, -0.150] | -100.0 % | **CHANGED** |
| fight:triage_unit@t1 | ram_left_per_turn | 4.996 | 3.759 | -1.238 | [-2.246, -0.267] | -24.8 % | **CHANGED** |
| fight:triage_unit@t1 | turns | 2.800 | 2.450 | -0.350 | [-0.700, -0.050] | -12.5 % | **CHANGED** |
| fight:triage_unit@t2 | ram_left_per_turn | 5.419 | 3.862 | -1.557 | [-2.773, -0.301] | -28.7 % | **CHANGED** |
| fight:triage_unit@t3 | dealt_per_turn | 16.372 | 21.026 | +4.654 | [+2.570, +6.658] | +28.4 % | **CHANGED** |
| fight:triage_unit@t3 | hp_end | 53.900 | 56.400 | +2.500 | [+0.600, +4.400] | +4.6 % | **CHANGED** |
| fight:triage_unit@t3 | hp_lost | 6.100 | 3.600 | -2.500 | [-4.453, -0.600] | -41.0 % | **CHANGED** |
| fight:triage_unit@t3 | hp_lost_frac | 0.102 | 0.060 | -0.042 | [-0.075, -0.010] | -41.0 % | **CHANGED** |
| fight:triage_unit@t3 | intake | 2.500 | 0.750 | -1.750 | [-3.250, -0.250] | -70.0 % | **CHANGED** |
| fight:triage_unit@t3 | perfect_rate | 0.825 | 0.981 | +0.155 | [+0.105, +0.204] | +18.8 % | **CHANGED** |
| fight:triage_unit@t3 | ram_left_per_turn | 6.856 | 4.383 | -2.473 | [-3.581, -1.320] | -36.1 % | **CHANGED** |
| fight:triage_unit@t3 | taken | 6.100 | 3.600 | -2.500 | [-4.400, -0.550] | -41.0 % | **CHANGED** |
| fight:triage_unit@t3 | turns | 7.450 | 5.700 | -1.750 | [-2.600, -0.950] | -23.5 % | **CHANGED** |
| fight:triage_unit@t4 | dealt_per_turn | 14.656 | 20.108 | +5.452 | [+3.727, +7.164] | +37.2 % | **CHANGED** |
| fight:triage_unit@t4 | hp_end | 47.800 | 50.600 | +2.800 | [+0.350, +5.350] | +5.9 % | **CHANGED** |
| fight:triage_unit@t4 | hp_lost | 12.200 | 9.400 | -2.800 | [-5.253, -0.300] | -23.0 % | **CHANGED** |
| fight:triage_unit@t4 | hp_lost_frac | 0.203 | 0.157 | -0.047 | [-0.088, -0.007] | -23.0 % | **CHANGED** |
| fight:triage_unit@t4 | perfect_rate | 0.819 | 0.952 | +0.133 | [+0.089, +0.180] | +16.2 % | **CHANGED** |
| fight:triage_unit@t4 | ram_left_per_turn | 7.784 | 4.566 | -3.217 | [-4.198, -2.198] | -41.3 % | **CHANGED** |
| fight:triage_unit@t4 | taken | 12.200 | 9.400 | -2.800 | [-5.300, -0.400] | -23.0 % | **CHANGED** |
| fight:triage_unit@t4 | turns | 13.300 | 9.350 | -3.950 | [-5.150, -2.650] | -29.7 % | **CHANGED** |
| fight:triage_unit@t4 | turns_both_share | 0.403 | 0.576 | +0.173 | [+0.090, +0.253] | +43.0 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:account_manager@t1 | dealt_per_turn | 18.992 | 21.230 | +2.238 | [+0.489, +3.884] | +11.8 % | **CHANGED** |
| fight:account_manager@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:account_manager@t1 | enrage_step | 0.200 | 0.050 | -0.150 | [-0.300, +0.000] | -75.0 % | noise |
| fight:account_manager@t1 | hp_lost | 19.350 | 11.300 | -8.050 | [-13.050, -3.250] | -41.6 % | **CHANGED** |
| fight:account_manager@t1 | intake | 15.150 | 6.650 | -8.500 | [-12.903, -4.148] | -56.1 % | **CHANGED** |
| fight:account_manager@t1 | parked | 20.650 | 16.350 | -4.300 | [-10.153, +2.100] | -20.8 % | noise |
| fight:account_manager@t1 | resistance_absorbed | 9.300 | 12.750 | +3.450 | [+1.200, +5.557] | +37.1 % | **CHANGED** |
| fight:account_manager@t1 | taken_per_turn | 2.500 | 1.581 | -0.919 | [-1.694, -0.195] | -36.8 % | **CHANGED** |
| fight:account_manager@t1 | turns | 8.150 | 7.250 | -0.900 | [-1.600, -0.200] | -11.0 % | **CHANGED** |
| fight:account_manager@t1 | turns_both_share | 0.311 | 0.452 | +0.141 | [+0.041, +0.242] | +45.2 % | **CHANGED** |
| fight:account_manager@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t2 | dealt_per_turn | 19.410 | 24.416 | +5.006 | [+3.403, +6.515] | +25.8 % | **CHANGED** |
| fight:account_manager@t2 | died | 0.100 | 0.000 | -0.100 | [-0.200, +0.000] | -100.0 % | noise |
| fight:account_manager@t2 | enrage_step | 1.250 | 0.750 | -0.500 | [-0.800, -0.250] | -40.0 % | **CHANGED** |
| fight:account_manager@t2 | hp_lost | 37.850 | 22.600 | -15.250 | [-21.250, -9.148] | -40.3 % | **CHANGED** |
| fight:account_manager@t2 | intake | 27.200 | 12.550 | -14.650 | [-20.300, -9.048] | -53.9 % | **CHANGED** |
| fight:account_manager@t2 | parked | 16.100 | 18.250 | +2.150 | [-5.205, +9.700] | +13.4 % | noise |
| fight:account_manager@t2 | resistance_absorbed | 14.850 | 18.600 | +3.750 | [+1.042, +6.450] | +25.3 % | **CHANGED** |
| fight:account_manager@t2 | taken_per_turn | 2.971 | 2.272 | -0.699 | [-1.179, -0.218] | -23.5 % | **CHANGED** |
| fight:account_manager@t2 | turns | 12.850 | 9.900 | -2.950 | [-3.950, -1.900] | -23.0 % | **CHANGED** |
| fight:account_manager@t2 | turns_both_share | 0.292 | 0.519 | +0.227 | [+0.153, +0.296] | +77.7 % | **CHANGED** |
| fight:account_manager@t2 | won | 0.900 | 1.000 | +0.100 | [+0.000, +0.200] | +11.1 % | noise |
| fight:account_manager@t3 | dealt_per_turn | 16.271 | 24.458 | +8.187 | [+6.919, +9.505] | +50.3 % | **CHANGED** |
| fight:account_manager@t3 | died | 1.000 | 0.100 | -0.900 | [-1.000, -0.800] | -90.0 % | **CHANGED** |
| fight:account_manager@t3 | enrage_step | 2.650 | 1.800 | -0.850 | [-1.200, -0.500] | -32.1 % | **CHANGED** |
| fight:account_manager@t3 | hp_lost | 60.000 | 40.200 | -19.800 | [-24.750, -15.400] | -33.0 % | **CHANGED** |
| fight:account_manager@t3 | intake | 43.700 | 20.700 | -23.000 | [-27.450, -18.797] | -52.6 % | **CHANGED** |
| fight:account_manager@t3 | parked | 16.400 | 14.800 | -1.600 | [-7.650, +3.750] | -9.8 % | noise |
| fight:account_manager@t3 | resistance_absorbed | 23.250 | 27.300 | +4.050 | [+0.450, +7.650] | +17.4 % | **CHANGED** |
| fight:account_manager@t3 | taken_per_turn | 3.079 | 2.538 | -0.541 | [-0.919, -0.188] | -17.6 % | **CHANGED** |
| fight:account_manager@t3 | turns | 20.200 | 15.850 | -4.350 | [-5.750, -2.900] | -21.5 % | **CHANGED** |
| fight:account_manager@t3 | turns_both_share | 0.233 | 0.490 | +0.257 | [+0.201, +0.316] | +110.5 % | **CHANGED** |
| fight:account_manager@t3 | won | 0.000 | 0.900 | +0.900 | [+0.800, +1.000] | - | **CHANGED** |
| fight:account_manager@t4 | dealt_per_turn | 15.009 | 22.497 | +7.488 | [+5.954, +9.083] | +49.9 % | **CHANGED** |
| fight:account_manager@t4 | died | 1.000 | 0.450 | -0.550 | [-0.750, -0.350] | -55.0 % | **CHANGED** |
| fight:account_manager@t4 | enrage_step | 2.650 | 3.850 | +1.200 | [+0.750, +1.650] | +45.3 % | **CHANGED** |
| fight:account_manager@t4 | hp_lost | 60.000 | 54.850 | -5.150 | [-8.353, -2.400] | -8.6 % | **CHANGED** |
| fight:account_manager@t4 | intake | 41.400 | 20.950 | -20.450 | [-25.300, -15.450] | -49.4 % | **CHANGED** |
| fight:account_manager@t4 | parked | 1.800 | 11.150 | +9.350 | [+7.150, +11.400] | +519.4 % | **CHANGED** |
| fight:account_manager@t4 | resistance_absorbed | 19.950 | 50.100 | +30.150 | [+25.800, +34.500] | +151.1 % | **CHANGED** |
| fight:account_manager@t4 | taken_per_turn | 3.178 | 2.137 | -1.041 | [-1.424, -0.679] | -32.7 % | **CHANGED** |
| fight:account_manager@t4 | turns | 20.250 | 26.150 | +5.900 | [+3.650, +8.102] | +29.1 % | **CHANGED** |
| fight:account_manager@t4 | turns_both_share | 0.203 | 0.504 | +0.302 | [+0.247, +0.353] | +149.0 % | **CHANGED** |
| fight:account_manager@t4 | won | 0.000 | 0.550 | +0.550 | [+0.350, +0.750] | - | **CHANGED** |
| fight:billing_daemon@t1 | dealt_per_turn | 17.150 | 18.550 | +1.400 | [-0.525, +3.325] | +8.2 % | noise |
| fight:billing_daemon@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | hp_lost | 3.600 | 2.000 | -1.600 | [-3.100, -0.150] | -44.4 % | **CHANGED** |
| fight:billing_daemon@t1 | intake | 3.150 | 1.700 | -1.450 | [-2.950, +0.000] | -46.0 % | noise |
| fight:billing_daemon@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | resistance_absorbed | 1.750 | 2.000 | +0.250 | [-0.100, +0.600] | +14.3 % | noise |
| fight:billing_daemon@t1 | taken_per_turn | 1.433 | 0.900 | -0.533 | [-1.200, +0.133] | -37.2 % | noise |
| fight:billing_daemon@t1 | turns | 2.600 | 2.350 | -0.250 | [-0.550, +0.050] | -9.6 % | noise |
| fight:billing_daemon@t1 | turns_both_share | 0.529 | 0.683 | +0.154 | [+0.004, +0.304] | +29.1 % | **CHANGED** |
| fight:billing_daemon@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t2 | dealt_per_turn | 16.000 | 19.540 | +3.540 | [+1.619, +5.469] | +22.1 % | **CHANGED** |
| fight:billing_daemon@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | hp_lost | 7.850 | 3.150 | -4.700 | [-7.300, -2.350] | -59.9 % | **CHANGED** |
| fight:billing_daemon@t2 | intake | 6.950 | 2.400 | -4.550 | [-7.100, -2.300] | -65.5 % | **CHANGED** |
| fight:billing_daemon@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | resistance_absorbed | 2.200 | 2.850 | +0.650 | [+0.250, +1.100] | +29.5 % | **CHANGED** |
| fight:billing_daemon@t2 | taken_per_turn | 1.830 | 0.879 | -0.951 | [-1.610, -0.325] | -51.9 % | **CHANGED** |
| fight:billing_daemon@t2 | turns | 4.500 | 3.500 | -1.000 | [-1.500, -0.500] | -22.2 % | **CHANGED** |
| fight:billing_daemon@t2 | turns_both_share | 0.426 | 0.671 | +0.245 | [+0.108, +0.380] | +57.5 % | **CHANGED** |
| fight:billing_daemon@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 20.405 | +3.891 | [+2.140, +5.614] | +23.6 % | **CHANGED** |
| fight:billing_daemon@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | hp_lost | 11.550 | 6.700 | -4.850 | [-8.153, -1.650] | -42.0 % | **CHANGED** |
| fight:billing_daemon@t3 | intake | 8.700 | 4.000 | -4.700 | [-7.700, -1.600] | -54.0 % | **CHANGED** |
| fight:billing_daemon@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 4.050 | -0.500 | [-1.150, +0.100] | -11.0 % | noise |
| fight:billing_daemon@t3 | taken_per_turn | 1.795 | 1.320 | -0.476 | [-1.120, +0.104] | -26.5 % | noise |
| fight:billing_daemon@t3 | turns | 6.750 | 5.450 | -1.300 | [-1.850, -0.750] | -19.3 % | **CHANGED** |
| fight:billing_daemon@t3 | turns_both_share | 0.546 | 0.630 | +0.084 | [-0.024, +0.192] | +15.4 % | noise |
| fight:billing_daemon@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 19.518 | +4.200 | [+2.497, +5.862] | +27.4 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | hp_lost | 25.200 | 14.150 | -11.050 | [-17.353, -4.998] | -43.8 % | **CHANGED** |
| fight:billing_daemon@t4 | intake | 19.800 | 8.000 | -11.800 | [-17.650, -6.348] | -59.6 % | **CHANGED** |
| fight:billing_daemon@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | resistance_absorbed | 7.200 | 7.100 | -0.100 | [-0.950, +0.750] | -1.4 % | noise |
| fight:billing_daemon@t4 | taken_per_turn | 2.166 | 1.634 | -0.532 | [-1.068, +0.030] | -24.6 % | noise |
| fight:billing_daemon@t4 | turns | 11.650 | 9.100 | -2.550 | [-3.500, -1.550] | -21.9 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.623 | +0.147 | [+0.057, +0.234] | +30.8 % | **CHANGED** |
| fight:billing_daemon@t4 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t1 | dealt_per_turn | 10.886 | 15.000 | +4.114 | [+0.750, +7.250] | +37.8 % | **CHANGED** |
| fight:care_swarm@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | hp_lost | 12.500 | 11.000 | -1.500 | [-3.400, +0.500] | -12.0 % | noise |
| fight:care_swarm@t1 | intake | 12.500 | 11.000 | -1.500 | [-3.403, +0.500] | -12.0 % | noise |
| fight:care_swarm@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | resistance_absorbed | 1.400 | 0.750 | -0.650 | [-1.100, -0.200] | -46.4 % | **CHANGED** |
| fight:care_swarm@t1 | taken_per_turn | 4.865 | 6.050 | +1.185 | [+0.105, +2.236] | +24.4 % | **CHANGED** |
| fight:care_swarm@t1 | turns | 3.050 | 1.900 | -1.150 | [-1.800, -0.550] | -37.7 % | **CHANGED** |
| fight:care_swarm@t1 | turns_both_share | 0.364 | 0.350 | -0.014 | [-0.169, +0.135] | -4.0 % | noise |
| fight:care_swarm@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t2 | dealt_per_turn | 10.968 | 14.799 | +3.831 | [+1.682, +6.017] | +34.9 % | **CHANGED** |
| fight:care_swarm@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | hp_lost | 22.900 | 19.650 | -3.250 | [-6.350, +0.100] | -14.2 % | noise |
| fight:care_swarm@t2 | intake | 22.750 | 19.650 | -3.100 | [-6.453, +0.350] | -13.6 % | noise |
| fight:care_swarm@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | resistance_absorbed | 1.950 | 1.500 | -0.450 | [-1.100, +0.200] | -23.1 % | noise |
| fight:care_swarm@t2 | taken_per_turn | 6.007 | 7.024 | +1.017 | [-0.156, +2.251] | +16.9 % | noise |
| fight:care_swarm@t2 | turns | 4.150 | 2.950 | -1.200 | [-1.850, -0.550] | -28.9 % | **CHANGED** |
| fight:care_swarm@t2 | turns_both_share | 0.353 | 0.391 | +0.038 | [-0.108, +0.184] | +10.7 % | noise |
| fight:care_swarm@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t3 | dealt_per_turn | 10.205 | 14.620 | +4.415 | [+2.330, +6.408] | +43.3 % | **CHANGED** |
| fight:care_swarm@t3 | died | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:care_swarm@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t3 | hp_lost | 46.000 | 36.050 | -9.950 | [-14.900, -4.600] | -21.6 % | **CHANGED** |
| fight:care_swarm@t3 | intake | 44.950 | 35.000 | -9.950 | [-14.800, -5.000] | -22.1 % | **CHANGED** |
| fight:care_swarm@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t3 | resistance_absorbed | 3.400 | 2.650 | -0.750 | [-1.450, +0.000] | -22.1 % | noise |
| fight:care_swarm@t3 | taken_per_turn | 7.030 | 8.051 | +1.021 | [-0.275, +2.296] | +14.5 % | noise |
| fight:care_swarm@t3 | turns | 7.100 | 4.850 | -2.250 | [-3.350, -1.150] | -31.7 % | **CHANGED** |
| fight:care_swarm@t3 | turns_both_share | 0.395 | 0.441 | +0.046 | [-0.052, +0.142] | +11.5 % | noise |
| fight:care_swarm@t3 | won | 0.950 | 1.000 | +0.050 | [+0.000, +0.150] | +5.3 % | noise |
| fight:care_swarm@t4 | dealt_per_turn | 9.313 | 14.661 | +5.348 | [+3.324, +7.521] | +57.4 % | **CHANGED** |
| fight:care_swarm@t4 | died | 1.000 | 0.900 | -0.100 | [-0.200, +0.000] | -10.0 % | noise |
| fight:care_swarm@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t4 | hp_lost | 60.000 | 59.450 | -0.550 | [-1.250, +0.000] | -0.9 % | noise |
| fight:care_swarm@t4 | intake | 58.050 | 57.950 | -0.100 | [-1.250, +1.100] | -0.2 % | noise |
| fight:care_swarm@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t4 | resistance_absorbed | 2.600 | 3.600 | +1.000 | [+0.300, +1.700] | +38.5 % | **CHANGED** |
| fight:care_swarm@t4 | taken_per_turn | 10.081 | 9.962 | -0.119 | [-1.539, +1.370] | -1.2 % | noise |
| fight:care_swarm@t4 | turns | 6.400 | 6.400 | +0.000 | [-0.800, +0.850] | +0.0 % | noise |
| fight:care_swarm@t4 | turns_both_share | 0.328 | 0.502 | +0.174 | [+0.077, +0.269] | +53.1 % | **CHANGED** |
| fight:care_swarm@t4 | won | 0.000 | 0.100 | +0.100 | [+0.000, +0.200] | - | noise |
| fight:claims_adjuster@t1 | dealt_per_turn | 38.172 | 43.398 | +5.226 | [-0.188, +10.738] | +13.7 % | noise |
| fight:claims_adjuster@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | hp_lost | 19.100 | 10.850 | -8.250 | [-13.150, -3.298] | -43.2 % | **CHANGED** |
| fight:claims_adjuster@t1 | intake | 17.900 | 10.400 | -7.500 | [-12.300, -2.800] | -41.9 % | **CHANGED** |
| fight:claims_adjuster@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | resistance_absorbed | 3.900 | 5.400 | +1.500 | [+0.150, +2.850] | +38.5 % | **CHANGED** |
| fight:claims_adjuster@t1 | taken_per_turn | 6.366 | 4.108 | -2.258 | [-3.927, -0.598] | -35.5 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns | 3.200 | 2.700 | -0.500 | [-0.900, -0.100] | -15.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns_both_share | 0.320 | 0.571 | +0.251 | [+0.120, +0.381] | +78.4 % | **CHANGED** |
| fight:claims_adjuster@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:claims_adjuster@t2 | dealt_per_turn | 35.969 | 43.109 | +7.140 | [+2.899, +11.385] | +19.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | died | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:claims_adjuster@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t2 | hp_lost | 33.700 | 18.250 | -15.450 | [-22.003, -9.198] | -45.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | intake | 30.700 | 16.000 | -14.700 | [-21.153, -8.143] | -47.9 % | **CHANGED** |
| fight:claims_adjuster@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t2 | resistance_absorbed | 6.750 | 7.650 | +0.900 | [-0.750, +2.550] | +13.3 % | noise |
| fight:claims_adjuster@t2 | taken_per_turn | 6.578 | 4.523 | -2.055 | [-3.402, -0.615] | -31.2 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns | 5.200 | 4.300 | -0.900 | [-1.350, -0.450] | -17.3 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns_both_share | 0.372 | 0.507 | +0.135 | [+0.029, +0.245] | +36.2 % | **CHANGED** |
| fight:claims_adjuster@t2 | won | 0.950 | 1.000 | +0.050 | [+0.000, +0.150] | +5.3 % | noise |
| fight:claims_adjuster@t3 | dealt_per_turn | 33.029 | 40.084 | +7.055 | [+3.909, +10.274] | +21.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | died | 0.650 | 0.050 | -0.600 | [-0.800, -0.400] | -92.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | enrage_step | 0.650 | 0.450 | -0.200 | [-0.450, +0.050] | -30.8 % | noise |
| fight:claims_adjuster@t3 | hp_lost | 55.800 | 31.650 | -24.150 | [-30.103, -18.100] | -43.3 % | **CHANGED** |
| fight:claims_adjuster@t3 | intake | 50.400 | 24.750 | -25.650 | [-31.553, -19.100] | -50.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t3 | resistance_absorbed | 8.550 | 15.600 | +7.050 | [+4.800, +9.150] | +82.5 % | **CHANGED** |
| fight:claims_adjuster@t3 | taken_per_turn | 7.232 | 4.489 | -2.743 | [-3.908, -1.530] | -37.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns | 8.150 | 7.350 | -0.800 | [-1.600, +0.000] | -9.8 % | noise |
| fight:claims_adjuster@t3 | turns_both_share | 0.273 | 0.607 | +0.334 | [+0.248, +0.419] | +122.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | won | 0.350 | 0.950 | +0.600 | [+0.400, +0.800] | +171.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt_per_turn | 33.521 | 36.828 | +3.306 | [-0.945, +7.376] | +9.9 % | noise |
| fight:claims_adjuster@t4 | died | 1.000 | 0.250 | -0.750 | [-0.900, -0.600] | -75.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | enrage_step | 0.600 | 1.500 | +0.900 | [+0.600, +1.200] | +150.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | hp_lost | 60.000 | 48.950 | -11.050 | [-16.300, -6.297] | -18.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | intake | 55.500 | 35.300 | -20.200 | [-25.853, -14.848] | -36.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t4 | resistance_absorbed | 8.850 | 26.100 | +17.250 | [+13.950, +20.550] | +194.9 % | **CHANGED** |
| fight:claims_adjuster@t4 | taken_per_turn | 9.357 | 4.194 | -5.163 | [-7.080, -3.417] | -55.2 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns | 7.700 | 12.300 | +4.600 | [+3.200, +6.002] | +59.7 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns_both_share | 0.231 | 0.601 | +0.370 | [+0.301, +0.440] | +160.3 % | **CHANGED** |
| fight:claims_adjuster@t4 | won | 0.000 | 0.750 | +0.750 | [+0.600, +0.900] | - | **CHANGED** |
| fight:collections_agent@t1 | dealt_per_turn | 15.332 | 18.333 | +3.001 | [+1.001, +4.835] | +19.6 % | **CHANGED** |
| fight:collections_agent@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | hp_lost | 5.850 | 4.700 | -1.150 | [-3.150, +1.050] | -19.7 % | noise |
| fight:collections_agent@t1 | intake | 5.550 | 4.550 | -1.000 | [-3.050, +1.052] | -18.0 % | noise |
| fight:collections_agent@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | resistance_absorbed | 1.200 | 1.400 | +0.200 | [-0.200, +0.600] | +16.7 % | noise |
| fight:collections_agent@t1 | taken_per_turn | 2.167 | 2.150 | -0.017 | [-0.933, +0.950] | -0.8 % | noise |
| fight:collections_agent@t1 | turns | 2.800 | 2.300 | -0.500 | [-0.850, -0.150] | -17.9 % | **CHANGED** |
| fight:collections_agent@t1 | turns_both_share | 0.367 | 0.512 | +0.146 | [-0.050, +0.325] | +39.8 % | noise |
| fight:collections_agent@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t2 | dealt_per_turn | 16.811 | 19.837 | +3.026 | [+0.947, +5.100] | +18.0 % | **CHANGED** |
| fight:collections_agent@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | hp_lost | 10.700 | 9.250 | -1.450 | [-4.050, +1.202] | -13.6 % | noise |
| fight:collections_agent@t2 | intake | 9.650 | 8.050 | -1.600 | [-4.050, +0.900] | -16.6 % | noise |
| fight:collections_agent@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | resistance_absorbed | 1.900 | 2.150 | +0.250 | [-0.200, +0.700] | +13.2 % | noise |
| fight:collections_agent@t2 | taken_per_turn | 2.863 | 2.824 | -0.039 | [-0.898, +0.845] | -1.4 % | noise |
| fight:collections_agent@t2 | turns | 4.200 | 3.350 | -0.850 | [-1.500, -0.250] | -20.2 % | **CHANGED** |
| fight:collections_agent@t2 | turns_both_share | 0.439 | 0.593 | +0.154 | [+0.023, +0.297] | +35.2 % | **CHANGED** |
| fight:collections_agent@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t3 | dealt_per_turn | 16.922 | 21.213 | +4.291 | [+2.390, +6.099] | +25.4 % | **CHANGED** |
| fight:collections_agent@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | hp_lost | 18.850 | 15.250 | -3.600 | [-6.400, -0.850] | -19.1 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 16.150 | 11.350 | -4.800 | [-7.850, -1.900] | -29.7 % | **CHANGED** |
| fight:collections_agent@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | resistance_absorbed | 3.450 | 3.600 | +0.150 | [-0.400, +0.750] | +4.3 % | noise |
| fight:collections_agent@t3 | taken_per_turn | 3.067 | 3.135 | +0.068 | [-0.418, +0.540] | +2.2 % | noise |
| fight:collections_agent@t3 | turns | 6.300 | 4.950 | -1.350 | [-1.900, -0.750] | -21.4 % | **CHANGED** |
| fight:collections_agent@t3 | turns_both_share | 0.459 | 0.662 | +0.203 | [+0.099, +0.306] | +44.3 % | **CHANGED** |
| fight:collections_agent@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t4 | dealt_per_turn | 16.698 | 20.776 | +4.078 | [+2.751, +5.366] | +24.4 % | **CHANGED** |
| fight:collections_agent@t4 | died | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:collections_agent@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | hp_lost | 43.150 | 31.300 | -11.850 | [-16.553, -7.398] | -27.5 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 23.650 | -12.150 | [-17.200, -7.750] | -33.9 % | **CHANGED** |
| fight:collections_agent@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | resistance_absorbed | 5.450 | 5.350 | -0.100 | [-0.950, +0.750] | -1.8 % | noise |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 3.955 | -0.420 | [-0.969, +0.148] | -9.6 % | noise |
| fight:collections_agent@t4 | turns | 10.000 | 8.000 | -2.000 | [-2.600, -1.400] | -20.0 % | **CHANGED** |
| fight:collections_agent@t4 | turns_both_share | 0.415 | 0.541 | +0.125 | [+0.056, +0.193] | +30.2 % | **CHANGED** |
| fight:collections_agent@t4 | won | 0.950 | 1.000 | +0.050 | [+0.000, +0.150] | +5.3 % | noise |
| fight:compliance_officer@t1 | dealt_per_turn | 17.919 | 19.794 | +1.875 | [-0.416, +4.166] | +10.5 % | noise |
| fight:compliance_officer@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | hp_lost | 4.800 | 2.550 | -2.250 | [-3.950, -0.550] | -46.9 % | **CHANGED** |
| fight:compliance_officer@t1 | intake | 4.200 | 1.950 | -2.250 | [-3.850, -0.650] | -53.6 % | **CHANGED** |
| fight:compliance_officer@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | resistance_absorbed | 2.800 | 4.300 | +1.500 | [+0.700, +2.300] | +53.6 % | **CHANGED** |
| fight:compliance_officer@t1 | taken_per_turn | 1.820 | 0.987 | -0.833 | [-1.542, -0.115] | -45.8 % | **CHANGED** |
| fight:compliance_officer@t1 | turns | 2.950 | 2.650 | -0.300 | [-0.600, +0.000] | -10.2 % | noise |
| fight:compliance_officer@t1 | turns_both_share | 0.371 | 0.646 | +0.275 | [+0.142, +0.400] | +74.2 % | **CHANGED** |
| fight:compliance_officer@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t2 | dealt_per_turn | 15.855 | 20.601 | +4.745 | [+2.521, +6.936] | +29.9 % | **CHANGED** |
| fight:compliance_officer@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | hp_lost | 9.200 | 4.650 | -4.550 | [-6.750, -2.150] | -49.5 % | **CHANGED** |
| fight:compliance_officer@t2 | intake | 7.850 | 3.150 | -4.700 | [-6.903, -2.400] | -59.9 % | **CHANGED** |
| fight:compliance_officer@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | resistance_absorbed | 4.400 | 6.500 | +2.100 | [+0.900, +3.400] | +47.7 % | **CHANGED** |
| fight:compliance_officer@t2 | taken_per_turn | 1.873 | 1.234 | -0.639 | [-1.241, -0.017] | -34.1 % | **CHANGED** |
| fight:compliance_officer@t2 | turns | 5.450 | 4.100 | -1.350 | [-2.050, -0.700] | -24.8 % | **CHANGED** |
| fight:compliance_officer@t2 | turns_both_share | 0.323 | 0.642 | +0.319 | [+0.214, +0.418] | +98.8 % | **CHANGED** |
| fight:compliance_officer@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t3 | dealt_per_turn | 15.041 | 20.117 | +5.075 | [+3.460, +6.745] | +33.7 % | **CHANGED** |
| fight:compliance_officer@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 7.500 | -11.700 | [-15.900, -7.350] | -60.9 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 3.900 | -11.700 | [-15.800, -7.395] | -75.0 % | **CHANGED** |
| fight:compliance_officer@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | resistance_absorbed | 8.600 | 9.400 | +0.800 | [-0.700, +2.300] | +9.3 % | noise |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 1.179 | -1.098 | [-1.697, -0.517] | -48.2 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 8.850 | 6.550 | -2.300 | [-3.100, -1.500] | -26.0 % | **CHANGED** |
| fight:compliance_officer@t3 | turns_both_share | 0.353 | 0.599 | +0.246 | [+0.148, +0.348] | +69.7 % | **CHANGED** |
| fight:compliance_officer@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t4 | dealt_per_turn | 15.738 | 19.736 | +3.998 | [+2.708, +5.206] | +25.4 % | **CHANGED** |
| fight:compliance_officer@t4 | died | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:compliance_officer@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 18.150 | -21.650 | [-27.400, -15.300] | -54.4 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 32.300 | 10.500 | -21.800 | [-27.703, -15.750] | -67.5 % | **CHANGED** |
| fight:compliance_officer@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | resistance_absorbed | 12.000 | 16.000 | +4.000 | [+2.200, +5.700] | +33.3 % | **CHANGED** |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 1.758 | -1.385 | [-2.015, -0.774] | -44.1 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 13.300 | 10.550 | -2.750 | [-3.700, -1.800] | -20.7 % | **CHANGED** |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.623 | +0.267 | [+0.189, +0.345] | +74.9 % | **CHANGED** |
| fight:compliance_officer@t4 | won | 0.950 | 1.000 | +0.050 | [+0.000, +0.150] | +5.3 % | noise |
| fight:dosage_dispenser@t1 | dealt_per_turn | 16.468 | 18.050 | +1.583 | [+0.001, +3.166] | +9.6 % | **CHANGED** |
| fight:dosage_dispenser@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | hp_lost | 0.150 | 0.000 | -0.150 | [-0.450, +0.000] | -100.0 % | noise |
| fight:dosage_dispenser@t1 | intake | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | resistance_absorbed | 0.850 | 0.700 | -0.150 | [-0.600, +0.300] | -17.6 % | noise |
| fight:dosage_dispenser@t1 | taken_per_turn | 0.050 | 0.000 | -0.050 | [-0.150, +0.000] | -100.0 % | noise |
| fight:dosage_dispenser@t1 | turns | 2.450 | 2.150 | -0.300 | [-0.550, +0.000] | -12.2 % | noise |
| fight:dosage_dispenser@t1 | turns_both_share | 0.267 | 0.250 | -0.017 | [-0.171, +0.138] | -6.2 % | noise |
| fight:dosage_dispenser@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t2 | dealt_per_turn | 17.840 | 19.669 | +1.829 | [+0.355, +3.353] | +10.3 % | **CHANGED** |
| fight:dosage_dispenser@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | hp_lost | 1.550 | 1.250 | -0.300 | [-1.250, +0.700] | -19.4 % | noise |
| fight:dosage_dispenser@t2 | intake | 0.200 | 0.200 | +0.000 | [-0.400, +0.400] | +0.0 % | noise |
| fight:dosage_dispenser@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | resistance_absorbed | 1.300 | 1.250 | -0.050 | [-0.600, +0.500] | -3.8 % | noise |
| fight:dosage_dispenser@t2 | taken_per_turn | 0.424 | 0.364 | -0.060 | [-0.339, +0.201] | -14.2 % | noise |
| fight:dosage_dispenser@t2 | turns | 3.600 | 3.150 | -0.450 | [-0.850, -0.100] | -12.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns_both_share | 0.276 | 0.296 | +0.020 | [-0.113, +0.150] | +7.3 % | noise |
| fight:dosage_dispenser@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t3 | dealt_per_turn | 17.935 | 21.178 | +3.244 | [+1.396, +4.957] | +18.1 % | **CHANGED** |
| fight:dosage_dispenser@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | hp_lost | 3.650 | 3.650 | +0.000 | [-1.650, +1.600] | +0.0 % | noise |
| fight:dosage_dispenser@t3 | intake | 0.500 | 0.500 | +0.000 | [-0.750, +0.750] | +0.0 % | noise |
| fight:dosage_dispenser@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | resistance_absorbed | 2.100 | 1.950 | -0.150 | [-0.900, +0.600] | -7.1 % | noise |
| fight:dosage_dispenser@t3 | taken_per_turn | 0.639 | 0.742 | +0.103 | [-0.193, +0.395] | +16.0 % | noise |
| fight:dosage_dispenser@t3 | turns | 5.700 | 4.650 | -1.050 | [-1.600, -0.550] | -18.4 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns_both_share | 0.282 | 0.351 | +0.069 | [-0.039, +0.181] | +24.6 % | noise |
| fight:dosage_dispenser@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t4 | dealt_per_turn | 19.386 | 22.985 | +3.598 | [+2.056, +5.042] | +18.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | hp_lost | 7.800 | 6.850 | -0.950 | [-2.803, +0.900] | -12.2 % | noise |
| fight:dosage_dispenser@t4 | intake | 1.050 | 0.700 | -0.350 | [-1.400, +0.700] | -33.3 % | noise |
| fight:dosage_dispenser@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | resistance_absorbed | 3.650 | 3.000 | -0.650 | [-1.400, +0.100] | -17.8 % | noise |
| fight:dosage_dispenser@t4 | taken_per_turn | 0.981 | 0.998 | +0.017 | [-0.233, +0.272] | +1.7 % | noise |
| fight:dosage_dispenser@t4 | turns | 8.300 | 6.850 | -1.450 | [-2.100, -0.900] | -17.5 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns_both_share | 0.354 | 0.372 | +0.018 | [-0.058, +0.093] | +5.1 % | noise |
| fight:dosage_dispenser@t4 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t1 | dealt_per_turn | 17.702 | 21.037 | +3.335 | [+1.507, +5.183] | +18.8 % | **CHANGED** |
| fight:recall_unit@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t1 | enrage_step | 0.150 | 0.000 | -0.150 | [-0.300, -0.050] | -100.0 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost | 17.700 | 8.550 | -9.150 | [-13.103, -4.998] | -51.7 % | **CHANGED** |
| fight:recall_unit@t1 | intake | 15.600 | 5.850 | -9.750 | [-13.753, -5.548] | -62.5 % | **CHANGED** |
| fight:recall_unit@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t1 | resistance_absorbed | 5.400 | 9.900 | +4.500 | [+2.400, +6.750] | +83.3 % | **CHANGED** |
| fight:recall_unit@t1 | taken_per_turn | 2.957 | 1.741 | -1.216 | [-1.995, -0.468] | -41.1 % | **CHANGED** |
| fight:recall_unit@t1 | turns | 6.200 | 5.200 | -1.000 | [-1.550, -0.450] | -16.1 % | **CHANGED** |
| fight:recall_unit@t1 | turns_both_share | 0.216 | 0.472 | +0.256 | [+0.133, +0.368] | +118.7 % | **CHANGED** |
| fight:recall_unit@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t2 | dealt_per_turn | 15.864 | 20.195 | +4.331 | [+3.020, +5.684] | +27.3 % | **CHANGED** |
| fight:recall_unit@t2 | died | 0.100 | 0.000 | -0.100 | [-0.200, +0.000] | -100.0 % | noise |
| fight:recall_unit@t2 | enrage_step | 1.100 | 0.850 | -0.250 | [-0.450, -0.100] | -22.7 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost | 36.350 | 16.450 | -19.900 | [-26.700, -13.447] | -54.7 % | **CHANGED** |
| fight:recall_unit@t2 | intake | 30.500 | 10.300 | -20.200 | [-27.153, -13.298] | -66.2 % | **CHANGED** |
| fight:recall_unit@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t2 | resistance_absorbed | 10.500 | 16.050 | +5.550 | [+3.150, +7.950] | +52.9 % | **CHANGED** |
| fight:recall_unit@t2 | taken_per_turn | 3.508 | 1.966 | -1.542 | [-2.302, -0.802] | -43.9 % | **CHANGED** |
| fight:recall_unit@t2 | turns | 10.750 | 8.600 | -2.150 | [-2.800, -1.500] | -20.0 % | **CHANGED** |
| fight:recall_unit@t2 | turns_both_share | 0.234 | 0.498 | +0.264 | [+0.177, +0.347] | +113.0 % | **CHANGED** |
| fight:recall_unit@t2 | won | 0.900 | 1.000 | +0.100 | [+0.000, +0.200] | +11.1 % | noise |
| fight:recall_unit@t3 | dealt_per_turn | 14.155 | 18.674 | +4.518 | [+3.118, +6.000] | +31.9 % | **CHANGED** |
| fight:recall_unit@t3 | died | 0.750 | 0.000 | -0.750 | [-0.900, -0.600] | -100.0 % | **CHANGED** |
| fight:recall_unit@t3 | enrage_step | 2.300 | 1.900 | -0.400 | [-0.800, +0.000] | -17.4 % | noise |
| fight:recall_unit@t3 | hp_lost | 57.750 | 25.800 | -31.950 | [-35.400, -28.297] | -55.3 % | **CHANGED** |
| fight:recall_unit@t3 | intake | 49.800 | 13.350 | -36.450 | [-41.302, -31.600] | -73.2 % | **CHANGED** |
| fight:recall_unit@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t3 | resistance_absorbed | 17.100 | 28.750 | +11.650 | [+8.400, +15.300] | +68.1 % | **CHANGED** |
| fight:recall_unit@t3 | taken_per_turn | 3.933 | 1.798 | -2.135 | [-2.815, -1.518] | -54.3 % | **CHANGED** |
| fight:recall_unit@t3 | turns | 16.650 | 14.750 | -1.900 | [-4.000, +0.300] | -11.4 % | noise |
| fight:recall_unit@t3 | turns_both_share | 0.219 | 0.554 | +0.335 | [+0.277, +0.393] | +152.9 % | **CHANGED** |
| fight:recall_unit@t3 | won | 0.250 | 1.000 | +0.750 | [+0.600, +0.900] | +300.0 % | **CHANGED** |
| fight:recall_unit@t4 | dealt_per_turn | 13.893 | 17.341 | +3.448 | [+2.117, +4.829] | +24.8 % | **CHANGED** |
| fight:recall_unit@t4 | died | 1.000 | 0.050 | -0.950 | [-1.000, -0.850] | -95.0 % | **CHANGED** |
| fight:recall_unit@t4 | enrage_step | 2.300 | 3.850 | +1.550 | [+0.950, +2.150] | +67.4 % | **CHANGED** |
| fight:recall_unit@t4 | hp_lost | 60.000 | 39.000 | -21.000 | [-25.450, -16.547] | -35.0 % | **CHANGED** |
| fight:recall_unit@t4 | intake | 51.900 | 16.350 | -35.550 | [-40.850, -29.898] | -68.5 % | **CHANGED** |
| fight:recall_unit@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t4 | resistance_absorbed | 17.850 | 48.650 | +30.800 | [+24.950, +37.002] | +172.5 % | **CHANGED** |
| fight:recall_unit@t4 | taken_per_turn | 5.106 | 1.675 | -3.431 | [-4.959, -2.128] | -67.2 % | **CHANGED** |
| fight:recall_unit@t4 | turns | 16.000 | 24.700 | +8.700 | [+5.850, +11.500] | +54.4 % | **CHANGED** |
| fight:recall_unit@t4 | turns_both_share | 0.208 | 0.536 | +0.328 | [+0.264, +0.393] | +157.8 % | **CHANGED** |
| fight:recall_unit@t4 | won | 0.000 | 0.950 | +0.950 | [+0.850, +1.000] | - | **CHANGED** |
| fight:triage_unit@t1 | dealt_per_turn | 17.137 | 19.125 | +1.988 | [-0.075, +4.088] | +11.6 % | noise |
| fight:triage_unit@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | hp_lost | 0.900 | 0.300 | -0.600 | [-1.200, +0.000] | -66.7 % | noise |
| fight:triage_unit@t1 | intake | 0.450 | 0.000 | -0.450 | [-0.900, -0.150] | -100.0 % | **CHANGED** |
| fight:triage_unit@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | resistance_absorbed | 1.500 | 1.600 | +0.100 | [-0.300, +0.450] | +6.7 % | noise |
| fight:triage_unit@t1 | taken_per_turn | 0.400 | 0.150 | -0.250 | [-0.550, +0.025] | -62.5 % | noise |
| fight:triage_unit@t1 | turns | 2.800 | 2.450 | -0.350 | [-0.700, -0.050] | -12.5 % | **CHANGED** |
| fight:triage_unit@t1 | turns_both_share | 0.447 | 0.492 | +0.044 | [-0.088, +0.173] | +9.9 % | noise |
| fight:triage_unit@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t2 | dealt_per_turn | 19.320 | 21.000 | +1.680 | [-0.540, +3.900] | +8.7 % | noise |
| fight:triage_unit@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | hp_lost | 2.500 | 1.550 | -0.950 | [-2.300, +0.350] | -38.0 % | noise |
| fight:triage_unit@t2 | intake | 1.000 | 0.800 | -0.200 | [-1.200, +0.800] | -20.0 % | noise |
| fight:triage_unit@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | resistance_absorbed | 2.150 | 2.500 | +0.350 | [-0.050, +0.800] | +16.3 % | noise |
| fight:triage_unit@t2 | taken_per_turn | 0.610 | 0.475 | -0.135 | [-0.469, +0.196] | -22.2 % | noise |
| fight:triage_unit@t2 | turns | 4.000 | 3.550 | -0.450 | [-0.950, +0.050] | -11.3 % | noise |
| fight:triage_unit@t2 | turns_both_share | 0.473 | 0.588 | +0.115 | [-0.033, +0.266] | +24.3 % | noise |
| fight:triage_unit@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t3 | dealt_per_turn | 16.372 | 21.026 | +4.654 | [+2.570, +6.658] | +28.4 % | **CHANGED** |
| fight:triage_unit@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | hp_lost | 6.100 | 3.600 | -2.500 | [-4.453, -0.600] | -41.0 % | **CHANGED** |
| fight:triage_unit@t3 | intake | 2.500 | 0.750 | -1.750 | [-3.250, -0.250] | -70.0 % | **CHANGED** |
| fight:triage_unit@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | resistance_absorbed | 4.200 | 3.850 | -0.350 | [-1.250, +0.550] | -8.3 % | noise |
| fight:triage_unit@t3 | taken_per_turn | 0.831 | 0.691 | -0.139 | [-0.427, +0.161] | -16.8 % | noise |
| fight:triage_unit@t3 | turns | 7.450 | 5.700 | -1.750 | [-2.600, -0.950] | -23.5 % | **CHANGED** |
| fight:triage_unit@t3 | turns_both_share | 0.449 | 0.552 | +0.103 | [-0.020, +0.229] | +22.8 % | noise |
| fight:triage_unit@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t4 | dealt_per_turn | 14.656 | 20.108 | +5.452 | [+3.727, +7.164] | +37.2 % | **CHANGED** |
| fight:triage_unit@t4 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | hp_lost | 12.200 | 9.400 | -2.800 | [-5.253, -0.300] | -23.0 % | **CHANGED** |
| fight:triage_unit@t4 | intake | 3.800 | 3.100 | -0.700 | [-2.900, +1.700] | -18.4 % | noise |
| fight:triage_unit@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | resistance_absorbed | 7.050 | 6.550 | -0.500 | [-1.700, +0.650] | -7.1 % | noise |
| fight:triage_unit@t4 | taken_per_turn | 0.962 | 1.047 | +0.086 | [-0.175, +0.368] | +8.9 % | noise |
| fight:triage_unit@t4 | turns | 13.300 | 9.350 | -3.950 | [-5.150, -2.650] | -29.7 % | **CHANGED** |
| fight:triage_unit@t4 | turns_both_share | 0.403 | 0.576 | +0.173 | [+0.090, +0.253] | +43.0 % | **CHANGED** |
| fight:triage_unit@t4 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A fight:account_manager@t1 | 20 | 0.18 | 2.72 | 0 | 20.6 | 15.2 | 9.3 | 1 | 0.31 |
| A fight:account_manager@t2 | 20 | 0.21 | 4.31 | 0 | 16.1 | 27.2 | 14.8 | 3 | 0.28 |
| A fight:account_manager@t3 | 20 | 0.09 | 9.91 | 0 | 16.4 | 43.7 | 23.2 | 4 | 0.23 |
| A fight:account_manager@t4 | 20 | 0.00 | 19.91 | 0 | 1.8 | 41.4 | 19.9 | 4 | 0.21 |
| A fight:billing_daemon@t1 | 20 | 0.50 | 2.60 | 0 | 0.0 | 3.1 | 1.8 | 0 | 0.50 |
| A fight:billing_daemon@t2 | 20 | 0.55 | 4.50 | 0 | 0.0 | 7.0 | 2.2 | 0 | 0.40 |
| A fight:billing_daemon@t3 | 20 | 0.00 | 6.75 | 0 | 0.0 | 8.7 | 4.5 | 0 | 0.53 |
| A fight:billing_daemon@t4 | 20 | 0.00 | 11.65 | 0 | 0.0 | 19.8 | 7.2 | 0 | 0.46 |
| A fight:care_swarm@t1 | 20 | 0.45 | 3.05 | 1 | 0.0 | 12.5 | 1.4 | 0 | 0.38 |
| A fight:care_swarm@t2 | 20 | 0.55 | 4.15 | 2 | 0.0 | 22.8 | 1.9 | 0 | 0.37 |
| A fight:care_swarm@t3 | 20 | 0.16 | 6.84 | 4 | 0.0 | 45.0 | 3.4 | 0 | 0.38 |
| A fight:care_swarm@t4 | 20 | - | - | 5 | 0.0 | 58.0 | 2.6 | 0 | 0.34 |
| A fight:claims_adjuster@t1 | 20 | 0.65 | 3.20 | 0 | 0.0 | 17.9 | 3.9 | 0 | 0.33 |
| A fight:claims_adjuster@t2 | 20 | 0.26 | 5.16 | 0 | 0.0 | 30.7 | 6.8 | 0 | 0.38 |
| A fight:claims_adjuster@t3 | 20 | 0.00 | 8.29 | 0 | 0.0 | 50.4 | 8.6 | 1 | 0.28 |
| A fight:claims_adjuster@t4 | 20 | - | - | 0 | 0.0 | 55.5 | 8.8 | 1 | 0.27 |
| A fight:collections_agent@t1 | 20 | 0.60 | 2.80 | 0 | 0.0 | 5.5 | 1.2 | 0 | 0.34 |
| A fight:collections_agent@t2 | 20 | 0.65 | 4.20 | 0 | 0.0 | 9.7 | 1.9 | 0 | 0.39 |
| A fight:collections_agent@t3 | 20 | 0.10 | 6.30 | 0 | 0.0 | 16.1 | 3.5 | 0 | 0.44 |
| A fight:collections_agent@t4 | 20 | 0.00 | 9.84 | 0 | 0.0 | 35.8 | 5.5 | 0 | 0.41 |
| A fight:compliance_officer@t1 | 20 | 0.75 | 2.95 | 0 | 0.0 | 4.2 | 2.8 | 0 | 0.37 |
| A fight:compliance_officer@t2 | 20 | 0.30 | 5.45 | 0 | 0.0 | 7.8 | 4.4 | 0 | 0.33 |
| A fight:compliance_officer@t3 | 20 | 0.00 | 8.85 | 0 | 0.0 | 15.6 | 8.6 | 0 | 0.36 |
| A fight:compliance_officer@t4 | 20 | 0.00 | 13.53 | 0 | 0.0 | 32.3 | 12.0 | 0 | 0.35 |
| A fight:dosage_dispenser@t1 | 20 | 0.35 | 2.45 | 0 | 0.0 | 0.0 | 0.8 | 0 | 0.27 |
| A fight:dosage_dispenser@t2 | 20 | 0.80 | 3.60 | 0 | 0.0 | 0.2 | 1.3 | 0 | 0.26 |
| A fight:dosage_dispenser@t3 | 20 | 0.20 | 5.70 | 0 | 0.0 | 0.5 | 2.1 | 0 | 0.30 |
| A fight:dosage_dispenser@t4 | 20 | 0.00 | 8.30 | 0 | 0.0 | 1.1 | 3.6 | 0 | 0.36 |
| A fight:recall_unit@t1 | 20 | 0.05 | 6.20 | 0 | 0.0 | 15.6 | 5.4 | 1 | 0.22 |
| A fight:recall_unit@t2 | 20 | 0.00 | 10.78 | 0 | 0.0 | 30.5 | 10.5 | 2 | 0.23 |
| A fight:recall_unit@t3 | 20 | 0.00 | 18.20 | 0 | 0.0 | 49.8 | 17.1 | 5 | 0.22 |
| A fight:recall_unit@t4 | 20 | - | - | 0 | 0.0 | 51.9 | 17.9 | 5 | 0.24 |
| A fight:triage_unit@t1 | 20 | 0.60 | 2.80 | 2 | 0.0 | 0.5 | 1.5 | 0 | 0.43 |
| A fight:triage_unit@t2 | 20 | 0.75 | 4.00 | 3 | 0.0 | 1.0 | 2.1 | 0 | 0.42 |
| A fight:triage_unit@t3 | 20 | 0.00 | 7.45 | 5 | 0.0 | 2.5 | 4.2 | 0 | 0.42 |
| A fight:triage_unit@t4 | 20 | 0.00 | 13.30 | 8 | 0.0 | 3.8 | 7.0 | 0 | 0.39 |
| B fight:account_manager@t1 | 20 | 0.27 | 2.42 | 0 | 16.4 | 6.7 | 12.8 | 1 | 0.44 |
| B fight:account_manager@t2 | 20 | 0.08 | 3.30 | 0 | 18.2 | 12.6 | 18.6 | 1 | 0.52 |
| B fight:account_manager@t3 | 20 | 0.38 | 5.34 | 0 | 14.8 | 20.7 | 27.3 | 3 | 0.49 |
| B fight:account_manager@t4 | 20 | 0.16 | 9.80 | 0 | 11.2 | 20.9 | 50.1 | 6 | 0.50 |
| B fight:billing_daemon@t1 | 20 | 0.35 | 2.35 | 0 | 0.0 | 1.7 | 2.0 | 0 | 0.68 |
| B fight:billing_daemon@t2 | 20 | 1.00 | 3.50 | 0 | 0.0 | 2.4 | 2.9 | 0 | 0.67 |
| B fight:billing_daemon@t3 | 20 | 0.15 | 5.45 | 0 | 0.0 | 4.0 | 4.0 | 0 | 0.64 |
| B fight:billing_daemon@t4 | 20 | 0.00 | 9.10 | 0 | 0.0 | 8.0 | 7.1 | 0 | 0.62 |
| B fight:care_swarm@t1 | 20 | 0.15 | 1.90 | 1 | 0.0 | 11.0 | 0.8 | 0 | 0.37 |
| B fight:care_swarm@t2 | 20 | 0.55 | 2.95 | 2 | 0.0 | 19.6 | 1.5 | 0 | 0.39 |
| B fight:care_swarm@t3 | 20 | 0.55 | 4.85 | 2 | 0.0 | 35.0 | 2.6 | 0 | 0.45 |
| B fight:care_swarm@t4 | 20 | 0.00 | 6.50 | 3 | 0.0 | 58.0 | 3.6 | 0 | 0.48 |
| B fight:claims_adjuster@t1 | 20 | 0.65 | 2.70 | 0 | 0.0 | 10.4 | 5.4 | 0 | 0.57 |
| B fight:claims_adjuster@t2 | 20 | 0.60 | 4.30 | 0 | 0.0 | 16.0 | 7.7 | 0 | 0.51 |
| B fight:claims_adjuster@t3 | 20 | 0.00 | 7.37 | 0 | 0.0 | 24.8 | 15.6 | 1 | 0.61 |
| B fight:claims_adjuster@t4 | 20 | 0.00 | 13.07 | 0 | 0.0 | 35.3 | 26.1 | 3 | 0.60 |
| B fight:collections_agent@t1 | 20 | 0.20 | 2.30 | 0 | 0.0 | 4.5 | 1.4 | 0 | 0.50 |
| B fight:collections_agent@t2 | 20 | 0.90 | 3.35 | 0 | 0.0 | 8.1 | 2.1 | 0 | 0.57 |
| B fight:collections_agent@t3 | 20 | 0.35 | 4.95 | 0 | 0.0 | 11.3 | 3.6 | 0 | 0.65 |
| B fight:collections_agent@t4 | 20 | 0.00 | 8.00 | 0 | 0.0 | 23.6 | 5.3 | 0 | 0.54 |
| B fight:compliance_officer@t1 | 20 | 0.60 | 2.65 | 0 | 0.0 | 1.9 | 4.3 | 0 | 0.64 |
| B fight:compliance_officer@t2 | 20 | 0.75 | 4.10 | 0 | 0.0 | 3.1 | 6.5 | 0 | 0.65 |
| B fight:compliance_officer@t3 | 20 | 0.00 | 6.55 | 0 | 0.0 | 3.9 | 9.4 | 0 | 0.60 |
| B fight:compliance_officer@t4 | 20 | 0.00 | 10.55 | 0 | 0.0 | 10.5 | 16.0 | 0 | 0.63 |
| B fight:dosage_dispenser@t1 | 20 | 0.15 | 2.15 | 0 | 0.0 | 0.0 | 0.7 | 0 | 0.26 |
| B fight:dosage_dispenser@t2 | 20 | 0.95 | 3.15 | 0 | 0.0 | 0.2 | 1.2 | 0 | 0.29 |
| B fight:dosage_dispenser@t3 | 20 | 0.40 | 4.65 | 0 | 0.0 | 0.5 | 1.9 | 0 | 0.35 |
| B fight:dosage_dispenser@t4 | 20 | 0.00 | 6.85 | 0 | 0.0 | 0.7 | 3.0 | 0 | 0.37 |
| B fight:recall_unit@t1 | 20 | 0.25 | 5.20 | 0 | 0.0 | 5.8 | 9.9 | 0 | 0.49 |
| B fight:recall_unit@t2 | 20 | 0.00 | 8.60 | 0 | 0.0 | 10.3 | 16.1 | 1 | 0.49 |
| B fight:recall_unit@t3 | 20 | 0.00 | 14.75 | 0 | 0.0 | 13.3 | 28.8 | 3 | 0.55 |
| B fight:recall_unit@t4 | 20 | 0.00 | 25.37 | 0 | 0.0 | 16.4 | 48.6 | 5 | 0.54 |
| B fight:triage_unit@t1 | 20 | 0.45 | 2.45 | 2 | 0.0 | 0.0 | 1.6 | 0 | 0.49 |
| B fight:triage_unit@t2 | 20 | 0.95 | 3.55 | 2 | 0.0 | 0.8 | 2.5 | 0 | 0.56 |
| B fight:triage_unit@t3 | 20 | 0.15 | 5.70 | 5 | 0.0 | 0.8 | 3.9 | 0 | 0.56 |
| B fight:triage_unit@t4 | 20 | 0.00 | 9.35 | 8 | 0.0 | 3.1 | 6.5 | 0 | 0.58 |

