# Balance comparison: cal_skill_100_060

- A: `cal_builtin_s100.json` (overrides: none)
- B: `cal_builtin_s060.json` (overrides: none)
- mode fight; A 720 records, B 720 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 385 of 792 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:account_manager@t1 | dealt | 150.000 | 142.750 | -7.250 | [-13.550, -2.300] | -4.8 % | **CHANGED** |
| fight:account_manager@t1 | dealt_per_turn | 18.992 | 13.954 | -5.039 | [-6.933, -3.173] | -26.5 % | **CHANGED** |
| fight:account_manager@t1 | died | 0.000 | 0.450 | +0.450 | [+0.300, +0.650] | - | **CHANGED** |
| fight:account_manager@t1 | enrage_step | 0.200 | 0.800 | +0.600 | [+0.350, +0.850] | +300.0 % | **CHANGED** |
| fight:account_manager@t1 | hp_end | 40.650 | 16.400 | -24.250 | [-32.602, -16.048] | -59.7 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost | 19.350 | 43.600 | +24.250 | [+15.697, +32.650] | +125.3 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost_frac | 0.322 | 0.727 | +0.404 | [+0.272, +0.543] | +125.3 % | **CHANGED** |
| fight:account_manager@t1 | intake | 15.150 | 36.450 | +21.300 | [+13.850, +28.500] | +140.6 % | **CHANGED** |
| fight:account_manager@t1 | parked | 20.650 | 14.400 | -6.250 | [-11.400, -1.050] | -30.3 % | **CHANGED** |
| fight:account_manager@t1 | perfect_rate | 0.814 | 0.618 | -0.196 | [-0.269, -0.123] | -24.0 % | **CHANGED** |
| fight:account_manager@t1 | ram_left_per_turn | 7.820 | 8.699 | +0.879 | [+0.172, +1.593] | +11.2 % | **CHANGED** |
| fight:account_manager@t1 | taken | 19.350 | 43.600 | +24.250 | [+15.898, +32.650] | +125.3 % | **CHANGED** |
| fight:account_manager@t1 | taken_per_turn | 2.500 | 3.910 | +1.410 | [+0.487, +2.288] | +56.4 % | **CHANGED** |
| fight:account_manager@t1 | turns | 8.150 | 10.850 | +2.700 | [+1.700, +3.700] | +33.1 % | **CHANGED** |
| fight:account_manager@t1 | won | 1.000 | 0.550 | -0.450 | [-0.650, -0.250] | -45.0 % | **CHANGED** |
| fight:account_manager@t2 | dealt | 240.000 | 175.600 | -64.400 | [-76.900, -50.947] | -26.8 % | **CHANGED** |
| fight:account_manager@t2 | dealt_per_turn | 19.410 | 13.037 | -6.372 | [-8.072, -4.609] | -32.8 % | **CHANGED** |
| fight:account_manager@t2 | died | 0.100 | 0.900 | +0.800 | [+0.650, +0.950] | +800.0 % | **CHANGED** |
| fight:account_manager@t2 | hp_end | 22.150 | 1.300 | -20.850 | [-25.850, -15.450] | -94.1 % | **CHANGED** |
| fight:account_manager@t2 | hp_lost | 37.850 | 58.700 | +20.850 | [+15.697, +26.300] | +55.1 % | **CHANGED** |
| fight:account_manager@t2 | hp_lost_frac | 0.631 | 0.978 | +0.348 | [+0.253, +0.437] | +55.1 % | **CHANGED** |
| fight:account_manager@t2 | intake | 27.200 | 46.800 | +19.600 | [+13.747, +25.150] | +72.1 % | **CHANGED** |
| fight:account_manager@t2 | perfect_rate | 0.832 | 0.602 | -0.230 | [-0.283, -0.176] | -27.6 % | **CHANGED** |
| fight:account_manager@t2 | taken | 37.850 | 58.700 | +20.850 | [+15.500, +25.650] | +55.1 % | **CHANGED** |
| fight:account_manager@t2 | taken_per_turn | 2.971 | 4.406 | +1.435 | [+0.950, +1.907] | +48.3 % | **CHANGED** |
| fight:account_manager@t2 | won | 0.900 | 0.100 | -0.800 | [-0.950, -0.650] | -88.9 % | **CHANGED** |
| fight:account_manager@t3 | dealt | 320.850 | 164.050 | -156.800 | [-184.705, -129.097] | -48.9 % | **CHANGED** |
| fight:account_manager@t3 | dealt_per_turn | 16.271 | 10.530 | -5.741 | [-7.200, -4.326] | -35.3 % | **CHANGED** |
| fight:account_manager@t3 | enrage_step | 2.650 | 1.750 | -0.900 | [-1.350, -0.450] | -34.0 % | **CHANGED** |
| fight:account_manager@t3 | parked | 16.400 | 2.200 | -14.200 | [-19.750, -9.450] | -86.6 % | **CHANGED** |
| fight:account_manager@t3 | perfect_rate | 0.792 | 0.563 | -0.229 | [-0.286, -0.172] | -28.9 % | **CHANGED** |
| fight:account_manager@t3 | resistance_absorbed | 23.250 | 15.200 | -8.050 | [-11.950, -4.350] | -34.6 % | **CHANGED** |
| fight:account_manager@t3 | taken_per_turn | 3.079 | 4.222 | +1.143 | [+0.575, +1.762] | +37.1 % | **CHANGED** |
| fight:account_manager@t3 | turns | 20.200 | 15.600 | -4.600 | [-6.750, -2.500] | -22.8 % | **CHANGED** |
| fight:account_manager@t4 | dealt | 305.300 | 139.550 | -165.750 | [-205.002, -122.500] | -54.3 % | **CHANGED** |
| fight:account_manager@t4 | dealt_per_turn | 15.009 | 10.642 | -4.367 | [-6.048, -2.682] | -29.1 % | **CHANGED** |
| fight:account_manager@t4 | enrage_step | 2.650 | 1.300 | -1.350 | [-1.900, -0.750] | -50.9 % | **CHANGED** |
| fight:account_manager@t4 | intake | 41.400 | 49.500 | +8.100 | [+3.500, +12.500] | +19.6 % | **CHANGED** |
| fight:account_manager@t4 | parked | 1.800 | 0.000 | -1.800 | [-3.150, -0.700] | -100.0 % | **CHANGED** |
| fight:account_manager@t4 | perfect_rate | 0.795 | 0.556 | -0.239 | [-0.301, -0.178] | -30.1 % | **CHANGED** |
| fight:account_manager@t4 | resistance_absorbed | 19.950 | 13.300 | -6.650 | [-10.550, -2.700] | -33.3 % | **CHANGED** |
| fight:account_manager@t4 | taken_per_turn | 3.178 | 5.620 | +2.443 | [+1.357, +3.650] | +76.9 % | **CHANGED** |
| fight:account_manager@t4 | turns | 20.250 | 13.300 | -6.950 | [-9.600, -4.250] | -34.3 % | **CHANGED** |
| fight:billing_daemon@t1 | dealt_per_turn | 17.150 | 14.125 | -3.025 | [-5.350, -0.700] | -17.6 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_end | 56.400 | 51.150 | -5.250 | [-7.800, -2.700] | -9.3 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_lost | 3.600 | 8.850 | +5.250 | [+2.700, +7.700] | +145.8 % | **CHANGED** |
| fight:billing_daemon@t1 | hp_lost_frac | 0.060 | 0.148 | +0.087 | [+0.046, +0.128] | +145.8 % | **CHANGED** |
| fight:billing_daemon@t1 | intake | 3.150 | 8.550 | +5.400 | [+3.050, +7.850] | +171.4 % | **CHANGED** |
| fight:billing_daemon@t1 | perfect_rate | 0.858 | 0.676 | -0.183 | [-0.283, -0.079] | -21.3 % | **CHANGED** |
| fight:billing_daemon@t1 | ram_left_per_turn | 4.366 | 5.716 | +1.350 | [+0.217, +2.424] | +30.9 % | **CHANGED** |
| fight:billing_daemon@t1 | taken | 3.600 | 8.850 | +5.250 | [+2.800, +7.800] | +145.8 % | **CHANGED** |
| fight:billing_daemon@t1 | taken_per_turn | 1.433 | 2.667 | +1.234 | [+0.413, +2.064] | +86.1 % | **CHANGED** |
| fight:billing_daemon@t1 | turns | 2.600 | 3.450 | +0.850 | [+0.300, +1.450] | +32.7 % | **CHANGED** |
| fight:billing_daemon@t2 | dealt_per_turn | 16.000 | 12.919 | -3.081 | [-5.062, -1.008] | -19.3 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_end | 52.150 | 45.650 | -6.500 | [-10.300, -2.750] | -12.5 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_lost | 7.850 | 14.350 | +6.500 | [+2.900, +10.250] | +82.8 % | **CHANGED** |
| fight:billing_daemon@t2 | hp_lost_frac | 0.131 | 0.239 | +0.108 | [+0.047, +0.173] | +82.8 % | **CHANGED** |
| fight:billing_daemon@t2 | intake | 6.950 | 14.050 | +7.100 | [+3.250, +10.750] | +102.2 % | **CHANGED** |
| fight:billing_daemon@t2 | perfect_rate | 0.847 | 0.721 | -0.126 | [-0.213, -0.041] | -14.9 % | **CHANGED** |
| fight:billing_daemon@t2 | ram_left_per_turn | 5.839 | 7.171 | +1.332 | [+0.287, +2.376] | +22.8 % | **CHANGED** |
| fight:billing_daemon@t2 | taken | 7.850 | 14.350 | +6.500 | [+2.500, +10.302] | +82.8 % | **CHANGED** |
| fight:billing_daemon@t2 | taken_per_turn | 1.830 | 2.579 | +0.749 | [+0.015, +1.435] | +40.9 % | **CHANGED** |
| fight:billing_daemon@t2 | turns | 4.500 | 5.700 | +1.200 | [+0.350, +2.150] | +26.7 % | **CHANGED** |
| fight:billing_daemon@t3 | combat_hash | 2440960232.800 | 1683331544.800 | -757628688.000 | [-1282258881.237, -209109427.410] | -31.0 % | **CHANGED** |
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 11.200 | -5.313 | [-6.696, -3.964] | -32.2 % | **CHANGED** |
| fight:billing_daemon@t3 | died | 0.000 | 0.150 | +0.150 | [+0.050, +0.300] | - | **CHANGED** |
| fight:billing_daemon@t3 | hp_end | 48.450 | 26.350 | -22.100 | [-28.252, -15.748] | -45.6 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_lost | 11.550 | 33.650 | +22.100 | [+15.900, +28.250] | +191.3 % | **CHANGED** |
| fight:billing_daemon@t3 | hp_lost_frac | 0.193 | 0.561 | +0.368 | [+0.259, +0.473] | +191.3 % | **CHANGED** |
| fight:billing_daemon@t3 | intake | 8.700 | 31.250 | +22.550 | [+16.297, +28.750] | +259.2 % | **CHANGED** |
| fight:billing_daemon@t3 | perfect_rate | 0.884 | 0.668 | -0.217 | [-0.285, -0.148] | -24.5 % | **CHANGED** |
| fight:billing_daemon@t3 | ram_left_per_turn | 5.345 | 7.706 | +2.361 | [+1.441, +3.302] | +44.2 % | **CHANGED** |
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 5.550 | +1.000 | [+0.150, +1.850] | +22.0 % | **CHANGED** |
| fight:billing_daemon@t3 | taken | 11.550 | 33.650 | +22.100 | [+15.897, +28.402] | +191.3 % | **CHANGED** |
| fight:billing_daemon@t3 | taken_per_turn | 1.795 | 3.328 | +1.533 | [+0.840, +2.207] | +85.4 % | **CHANGED** |
| fight:billing_daemon@t3 | turns | 6.750 | 9.900 | +3.150 | [+2.350, +3.950] | +46.7 % | **CHANGED** |
| fight:billing_daemon@t3 | turns_both_share | 0.546 | 0.422 | -0.124 | [-0.226, -0.030] | -22.7 % | **CHANGED** |
| fight:billing_daemon@t3 | won | 1.000 | 0.850 | -0.150 | [-0.300, -0.050] | -15.0 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt | 172.000 | 138.650 | -33.350 | [-44.650, -22.648] | -19.4 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 11.519 | -3.800 | [-5.377, -2.132] | -24.8 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.000 | 0.700 | +0.700 | [+0.550, +0.850] | - | **CHANGED** |
| fight:billing_daemon@t4 | hp_end | 34.800 | 5.350 | -29.450 | [-35.750, -23.095] | -84.6 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_lost | 25.200 | 54.650 | +29.450 | [+23.148, +35.500] | +116.9 % | **CHANGED** |
| fight:billing_daemon@t4 | hp_lost_frac | 0.420 | 0.911 | +0.491 | [+0.388, +0.593] | +116.9 % | **CHANGED** |
| fight:billing_daemon@t4 | intake | 19.800 | 51.200 | +31.400 | [+24.897, +37.050] | +158.6 % | **CHANGED** |
| fight:billing_daemon@t4 | perfect_rate | 0.867 | 0.638 | -0.229 | [-0.290, -0.166] | -26.4 % | **CHANGED** |
| fight:billing_daemon@t4 | ram_left_per_turn | 7.341 | 8.622 | +1.281 | [+0.506, +2.062] | +17.4 % | **CHANGED** |
| fight:billing_daemon@t4 | taken | 25.200 | 54.650 | +29.450 | [+23.100, +35.800] | +116.9 % | **CHANGED** |
| fight:billing_daemon@t4 | taken_per_turn | 2.166 | 4.687 | +2.521 | [+1.866, +3.253] | +116.4 % | **CHANGED** |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.383 | -0.093 | [-0.172, -0.017] | -19.5 % | **CHANGED** |
| fight:billing_daemon@t4 | won | 1.000 | 0.300 | -0.700 | [-0.850, -0.550] | -70.0 % | **CHANGED** |
| fight:care_swarm@t1 | hp_end | 47.500 | 42.700 | -4.800 | [-8.400, -1.500] | -10.1 % | **CHANGED** |
| fight:care_swarm@t1 | hp_lost | 12.500 | 17.300 | +4.800 | [+1.500, +8.702] | +38.4 % | **CHANGED** |
| fight:care_swarm@t1 | hp_lost_frac | 0.208 | 0.288 | +0.080 | [+0.026, +0.138] | +38.4 % | **CHANGED** |
| fight:care_swarm@t1 | intake | 12.500 | 17.300 | +4.800 | [+1.450, +8.450] | +38.4 % | **CHANGED** |
| fight:care_swarm@t1 | perfect_rate | 0.868 | 0.639 | -0.228 | [-0.336, -0.120] | -26.3 % | **CHANGED** |
| fight:care_swarm@t1 | taken | 12.500 | 17.300 | +4.800 | [+1.400, +8.600] | +38.4 % | **CHANGED** |
| fight:care_swarm@t2 | dealt_per_turn | 10.968 | 7.917 | -3.051 | [-5.120, -0.835] | -27.8 % | **CHANGED** |
| fight:care_swarm@t2 | died | 0.000 | 0.250 | +0.250 | [+0.100, +0.400] | - | **CHANGED** |
| fight:care_swarm@t2 | heal_total | 1.500 | 4.800 | +3.300 | [+1.250, +5.350] | +220.0 % | **CHANGED** |
| fight:care_swarm@t2 | heal_turns | 0.400 | 1.100 | +0.700 | [+0.250, +1.150] | +175.0 % | **CHANGED** |
| fight:care_swarm@t2 | hp_end | 37.100 | 22.700 | -14.400 | [-20.453, -8.850] | -38.8 % | **CHANGED** |
| fight:care_swarm@t2 | hp_lost | 22.900 | 37.300 | +14.400 | [+8.700, +20.800] | +62.9 % | **CHANGED** |
| fight:care_swarm@t2 | hp_lost_frac | 0.382 | 0.622 | +0.240 | [+0.148, +0.336] | +62.9 % | **CHANGED** |
| fight:care_swarm@t2 | intake | 22.750 | 36.850 | +14.100 | [+8.397, +19.750] | +62.0 % | **CHANGED** |
| fight:care_swarm@t2 | perfect_rate | 0.881 | 0.580 | -0.301 | [-0.397, -0.212] | -34.1 % | **CHANGED** |
| fight:care_swarm@t2 | ram_left_per_turn | 6.272 | 7.787 | +1.515 | [+0.374, +2.646] | +24.2 % | **CHANGED** |
| fight:care_swarm@t2 | taken | 22.900 | 37.300 | +14.400 | [+8.450, +20.250] | +62.9 % | **CHANGED** |
| fight:care_swarm@t2 | turns | 4.150 | 6.250 | +2.100 | [+0.950, +3.350] | +50.6 % | **CHANGED** |
| fight:care_swarm@t2 | won | 1.000 | 0.750 | -0.250 | [-0.400, -0.100] | -25.0 % | **CHANGED** |
| fight:care_swarm@t3 | dealt | 64.650 | 53.350 | -11.300 | [-18.100, -5.050] | -17.5 % | **CHANGED** |
| fight:care_swarm@t3 | dealt_per_turn | 10.205 | 7.572 | -2.633 | [-4.476, -0.865] | -25.8 % | **CHANGED** |
| fight:care_swarm@t3 | died | 0.050 | 0.600 | +0.550 | [+0.350, +0.750] | +1100.0 % | **CHANGED** |
| fight:care_swarm@t3 | hp_end | 14.000 | 6.600 | -7.400 | [-12.500, -2.048] | -52.9 % | **CHANGED** |
| fight:care_swarm@t3 | hp_lost | 46.000 | 53.400 | +7.400 | [+2.000, +12.602] | +16.1 % | **CHANGED** |
| fight:care_swarm@t3 | hp_lost_frac | 0.767 | 0.890 | +0.123 | [+0.032, +0.211] | +16.1 % | **CHANGED** |
| fight:care_swarm@t3 | intake | 44.950 | 52.650 | +7.700 | [+2.647, +12.950] | +17.1 % | **CHANGED** |
| fight:care_swarm@t3 | perfect_rate | 0.879 | 0.579 | -0.301 | [-0.398, -0.198] | -34.2 % | **CHANGED** |
| fight:care_swarm@t3 | ram_left_per_turn | 7.303 | 8.701 | +1.398 | [+0.339, +2.443] | +19.1 % | **CHANGED** |
| fight:care_swarm@t3 | taken | 46.000 | 53.400 | +7.400 | [+2.100, +12.400] | +16.1 % | **CHANGED** |
| fight:care_swarm@t3 | turns_both_share | 0.395 | 0.246 | -0.149 | [-0.244, -0.055] | -37.7 % | **CHANGED** |
| fight:care_swarm@t3 | won | 0.950 | 0.400 | -0.550 | [-0.750, -0.350] | -57.9 % | **CHANGED** |
| fight:care_swarm@t4 | dealt | 56.700 | 46.200 | -10.500 | [-21.305, -1.047] | -18.5 % | **CHANGED** |
| fight:care_swarm@t4 | perfect_rate | 0.845 | 0.587 | -0.258 | [-0.342, -0.171] | -30.5 % | **CHANGED** |
| fight:claims_adjuster@t1 | dealt_per_turn | 38.172 | 28.395 | -9.776 | [-15.479, -4.123] | -25.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_end | 40.900 | 30.950 | -9.950 | [-15.450, -4.550] | -24.3 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost | 19.100 | 29.050 | +9.950 | [+4.650, +15.700] | +52.1 % | **CHANGED** |
| fight:claims_adjuster@t1 | hp_lost_frac | 0.318 | 0.484 | +0.166 | [+0.072, +0.252] | +52.1 % | **CHANGED** |
| fight:claims_adjuster@t1 | intake | 17.900 | 26.800 | +8.900 | [+3.648, +14.200] | +49.7 % | **CHANGED** |
| fight:claims_adjuster@t1 | perfect_rate | 0.945 | 0.662 | -0.283 | [-0.368, -0.193] | -30.0 % | **CHANGED** |
| fight:claims_adjuster@t1 | ram_left_per_turn | 5.487 | 7.107 | +1.619 | [+0.374, +2.873] | +29.5 % | **CHANGED** |
| fight:claims_adjuster@t1 | taken | 19.100 | 29.050 | +9.950 | [+4.700, +15.250] | +52.1 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns | 3.200 | 4.500 | +1.300 | [+0.600, +2.000] | +40.6 % | **CHANGED** |
| fight:claims_adjuster@t2 | dealt | 179.000 | 160.300 | -18.700 | [-29.450, -8.200] | -10.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | dealt_per_turn | 35.969 | 24.977 | -10.992 | [-15.074, -6.772] | -30.6 % | **CHANGED** |
| fight:claims_adjuster@t2 | died | 0.050 | 0.500 | +0.450 | [+0.250, +0.650] | +900.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | enrage_step | 0.000 | 0.300 | +0.300 | [+0.150, +0.500] | - | **CHANGED** |
| fight:claims_adjuster@t2 | hp_end | 26.300 | 11.350 | -14.950 | [-22.455, -7.498] | -56.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost | 33.700 | 48.650 | +14.950 | [+7.147, +21.952] | +44.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost_frac | 0.562 | 0.811 | +0.249 | [+0.123, +0.367] | +44.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | intake | 30.700 | 43.100 | +12.400 | [+4.397, +20.102] | +40.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | perfect_rate | 0.941 | 0.626 | -0.315 | [-0.387, -0.240] | -33.5 % | **CHANGED** |
| fight:claims_adjuster@t2 | ram_left_per_turn | 6.562 | 8.092 | +1.530 | [+0.525, +2.576] | +23.3 % | **CHANGED** |
| fight:claims_adjuster@t2 | taken | 33.700 | 48.650 | +14.950 | [+7.600, +22.250] | +44.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns | 5.200 | 6.800 | +1.600 | [+0.950, +2.300] | +30.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | won | 0.950 | 0.500 | -0.450 | [-0.650, -0.250] | -47.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt | 262.350 | 167.900 | -94.450 | [-125.102, -61.743] | -36.0 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt_per_turn | 33.029 | 26.787 | -6.243 | [-9.914, -2.663] | -18.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | died | 0.650 | 0.900 | +0.250 | [+0.050, +0.450] | +38.5 % | **CHANGED** |
| fight:claims_adjuster@t3 | enrage_step | 0.650 | 0.300 | -0.350 | [-0.600, -0.050] | -53.8 % | **CHANGED** |
| fight:claims_adjuster@t3 | perfect_rate | 0.898 | 0.639 | -0.260 | [-0.333, -0.189] | -28.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | taken_per_turn | 7.232 | 10.455 | +3.223 | [+1.808, +4.795] | +44.6 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns | 8.150 | 6.300 | -1.850 | [-2.903, -0.750] | -22.7 % | **CHANGED** |
| fight:claims_adjuster@t3 | won | 0.350 | 0.100 | -0.250 | [-0.450, -0.050] | -71.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt | 240.150 | 141.150 | -99.000 | [-137.700, -57.892] | -41.2 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt_per_turn | 33.521 | 25.920 | -7.601 | [-12.561, -2.829] | -22.7 % | **CHANGED** |
| fight:claims_adjuster@t4 | perfect_rate | 0.877 | 0.608 | -0.269 | [-0.339, -0.200] | -30.7 % | **CHANGED** |
| fight:claims_adjuster@t4 | taken_per_turn | 9.357 | 13.007 | +3.650 | [+1.119, +5.952] | +39.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns | 7.700 | 5.550 | -2.150 | [-3.500, -0.648] | -27.9 % | **CHANGED** |
| fight:collections_agent@t1 | combat_hash | 2348250131.200 | 1651821745.100 | -696428386.100 | [-1343655076.250, -38892496.278] | -29.7 % | **CHANGED** |
| fight:collections_agent@t1 | dealt_per_turn | 15.332 | 11.818 | -3.514 | [-5.514, -1.480] | -22.9 % | **CHANGED** |
| fight:collections_agent@t1 | hp_end | 54.150 | 49.800 | -4.350 | [-7.250, -1.400] | -8.0 % | **CHANGED** |
| fight:collections_agent@t1 | hp_lost | 5.850 | 10.200 | +4.350 | [+1.550, +7.102] | +74.4 % | **CHANGED** |
| fight:collections_agent@t1 | hp_lost_frac | 0.097 | 0.170 | +0.073 | [+0.025, +0.118] | +74.4 % | **CHANGED** |
| fight:collections_agent@t1 | intake | 5.550 | 9.900 | +4.350 | [+1.600, +7.100] | +78.4 % | **CHANGED** |
| fight:collections_agent@t1 | perfect_rate | 0.875 | 0.656 | -0.219 | [-0.327, -0.108] | -25.1 % | **CHANGED** |
| fight:collections_agent@t1 | ram_left_per_turn | 5.700 | 7.104 | +1.404 | [+0.325, +2.429] | +24.6 % | **CHANGED** |
| fight:collections_agent@t1 | taken | 5.850 | 10.200 | +4.350 | [+1.450, +7.200] | +74.4 % | **CHANGED** |
| fight:collections_agent@t1 | turns | 2.800 | 3.750 | +0.950 | [+0.447, +1.450] | +33.9 % | **CHANGED** |
| fight:collections_agent@t2 | dealt_per_turn | 16.811 | 12.975 | -3.836 | [-6.010, -1.577] | -22.8 % | **CHANGED** |
| fight:collections_agent@t2 | hp_end | 49.300 | 40.400 | -8.900 | [-13.500, -4.648] | -18.1 % | **CHANGED** |
| fight:collections_agent@t2 | hp_lost | 10.700 | 19.600 | +8.900 | [+4.250, +13.350] | +83.2 % | **CHANGED** |
| fight:collections_agent@t2 | hp_lost_frac | 0.178 | 0.327 | +0.148 | [+0.074, +0.226] | +83.2 % | **CHANGED** |
| fight:collections_agent@t2 | intake | 9.650 | 17.950 | +8.300 | [+4.500, +12.450] | +86.0 % | **CHANGED** |
| fight:collections_agent@t2 | perfect_rate | 0.882 | 0.686 | -0.196 | [-0.277, -0.110] | -22.2 % | **CHANGED** |
| fight:collections_agent@t2 | ram_left_per_turn | 6.441 | 7.737 | +1.296 | [+0.345, +2.255] | +20.1 % | **CHANGED** |
| fight:collections_agent@t2 | taken | 10.700 | 19.600 | +8.900 | [+4.500, +13.450] | +83.2 % | **CHANGED** |
| fight:collections_agent@t2 | turns | 4.200 | 5.400 | +1.200 | [+0.350, +1.950] | +28.6 % | **CHANGED** |
| fight:collections_agent@t2 | turns_both_share | 0.439 | 0.272 | -0.167 | [-0.293, -0.041] | -38.1 % | **CHANGED** |
| fight:collections_agent@t3 | dealt | 102.000 | 96.300 | -5.700 | [-10.153, -1.850] | -5.6 % | **CHANGED** |
| fight:collections_agent@t3 | dealt_per_turn | 16.922 | 12.422 | -4.500 | [-6.325, -2.657] | -26.6 % | **CHANGED** |
| fight:collections_agent@t3 | died | 0.000 | 0.350 | +0.350 | [+0.200, +0.550] | - | **CHANGED** |
| fight:collections_agent@t3 | hp_end | 41.150 | 18.900 | -22.250 | [-28.700, -15.148] | -54.1 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost | 18.850 | 41.100 | +22.250 | [+15.650, +28.703] | +118.0 % | **CHANGED** |
| fight:collections_agent@t3 | hp_lost_frac | 0.314 | 0.685 | +0.371 | [+0.250, +0.486] | +118.0 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 16.150 | 36.750 | +20.600 | [+14.300, +26.700] | +127.6 % | **CHANGED** |
| fight:collections_agent@t3 | perfect_rate | 0.881 | 0.622 | -0.259 | [-0.324, -0.187] | -29.4 % | **CHANGED** |
| fight:collections_agent@t3 | ram_left_per_turn | 6.897 | 8.473 | +1.577 | [+0.778, +2.412] | +22.9 % | **CHANGED** |
| fight:collections_agent@t3 | taken | 18.850 | 41.100 | +22.250 | [+15.250, +29.150] | +118.0 % | **CHANGED** |
| fight:collections_agent@t3 | taken_per_turn | 3.067 | 4.938 | +1.871 | [+1.110, +2.613] | +61.0 % | **CHANGED** |
| fight:collections_agent@t3 | turns | 6.300 | 8.150 | +1.850 | [+1.100, +2.600] | +29.4 % | **CHANGED** |
| fight:collections_agent@t3 | turns_both_share | 0.459 | 0.302 | -0.157 | [-0.240, -0.071] | -34.2 % | **CHANGED** |
| fight:collections_agent@t3 | won | 1.000 | 0.650 | -0.350 | [-0.550, -0.200] | -35.0 % | **CHANGED** |
| fight:collections_agent@t4 | dealt | 163.600 | 115.150 | -48.450 | [-64.005, -33.750] | -29.6 % | **CHANGED** |
| fight:collections_agent@t4 | dealt_per_turn | 16.698 | 12.533 | -4.165 | [-5.701, -2.639] | -24.9 % | **CHANGED** |
| fight:collections_agent@t4 | died | 0.050 | 0.750 | +0.700 | [+0.500, +0.850] | +1400.0 % | **CHANGED** |
| fight:collections_agent@t4 | hp_end | 16.850 | 2.100 | -14.750 | [-18.950, -10.600] | -87.5 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost | 43.150 | 57.900 | +14.750 | [+10.550, +18.600] | +34.2 % | **CHANGED** |
| fight:collections_agent@t4 | hp_lost_frac | 0.719 | 0.965 | +0.246 | [+0.176, +0.311] | +34.2 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 52.350 | +16.550 | [+12.100, +20.800] | +46.2 % | **CHANGED** |
| fight:collections_agent@t4 | perfect_rate | 0.910 | 0.662 | -0.248 | [-0.311, -0.188] | -27.2 % | **CHANGED** |
| fight:collections_agent@t4 | taken | 43.150 | 57.900 | +14.750 | [+10.800, +18.900] | +34.2 % | **CHANGED** |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 7.136 | +2.761 | [+1.696, +3.916] | +63.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns_both_share | 0.415 | 0.330 | -0.086 | [-0.154, -0.020] | -20.6 % | **CHANGED** |
| fight:collections_agent@t4 | won | 0.950 | 0.250 | -0.700 | [-0.850, -0.500] | -73.7 % | **CHANGED** |
| fight:compliance_officer@t1 | dealt_per_turn | 17.919 | 13.554 | -4.365 | [-6.924, -1.805] | -24.4 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_end | 55.200 | 49.400 | -5.800 | [-8.400, -3.150] | -10.5 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_lost | 4.800 | 10.600 | +5.800 | [+3.247, +8.400] | +120.8 % | **CHANGED** |
| fight:compliance_officer@t1 | hp_lost_frac | 0.080 | 0.177 | +0.097 | [+0.053, +0.141] | +120.8 % | **CHANGED** |
| fight:compliance_officer@t1 | intake | 4.200 | 10.150 | +5.950 | [+3.400, +8.600] | +141.7 % | **CHANGED** |
| fight:compliance_officer@t1 | perfect_rate | 0.917 | 0.720 | -0.197 | [-0.281, -0.111] | -21.5 % | **CHANGED** |
| fight:compliance_officer@t1 | ram_left_per_turn | 5.187 | 6.989 | +1.802 | [+0.763, +2.761] | +34.7 % | **CHANGED** |
| fight:compliance_officer@t1 | taken | 4.800 | 10.600 | +5.800 | [+3.200, +8.350] | +120.8 % | **CHANGED** |
| fight:compliance_officer@t1 | turns | 2.950 | 4.300 | +1.350 | [+0.700, +2.000] | +45.8 % | **CHANGED** |
| fight:compliance_officer@t2 | dealt_per_turn | 15.855 | 12.842 | -3.013 | [-4.929, -1.163] | -19.0 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_end | 50.800 | 40.450 | -10.350 | [-14.650, -6.250] | -20.4 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_lost | 9.200 | 19.550 | +10.350 | [+6.300, +14.700] | +112.5 % | **CHANGED** |
| fight:compliance_officer@t2 | hp_lost_frac | 0.153 | 0.326 | +0.173 | [+0.098, +0.242] | +112.5 % | **CHANGED** |
| fight:compliance_officer@t2 | intake | 7.850 | 17.900 | +10.050 | [+6.000, +14.300] | +128.0 % | **CHANGED** |
| fight:compliance_officer@t2 | perfect_rate | 0.889 | 0.738 | -0.152 | [-0.222, -0.082] | -17.1 % | **CHANGED** |
| fight:compliance_officer@t2 | ram_left_per_turn | 6.705 | 8.141 | +1.436 | [+0.597, +2.243] | +21.4 % | **CHANGED** |
| fight:compliance_officer@t2 | taken | 9.200 | 19.550 | +10.350 | [+6.150, +14.850] | +112.5 % | **CHANGED** |
| fight:compliance_officer@t2 | taken_per_turn | 1.873 | 2.932 | +1.059 | [+0.378, +1.755] | +56.6 % | **CHANGED** |
| fight:compliance_officer@t2 | turns | 5.450 | 6.550 | +1.100 | [+0.250, +1.900] | +20.2 % | **CHANGED** |
| fight:compliance_officer@t3 | combat_hash | 1556676763.600 | 2295709065.450 | +739032301.850 | [+130036685.993, +1345337976.517] | +47.5 % | **CHANGED** |
| fight:compliance_officer@t3 | dealt | 128.000 | 124.200 | -3.800 | [-7.003, -1.050] | -3.0 % | **CHANGED** |
| fight:compliance_officer@t3 | dealt_per_turn | 15.041 | 11.985 | -3.057 | [-4.507, -1.598] | -20.3 % | **CHANGED** |
| fight:compliance_officer@t3 | died | 0.000 | 0.400 | +0.400 | [+0.200, +0.600] | - | **CHANGED** |
| fight:compliance_officer@t3 | hp_end | 40.800 | 15.700 | -25.100 | [-32.455, -17.200] | -61.5 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 44.300 | +25.100 | [+17.300, +32.550] | +130.7 % | **CHANGED** |
| fight:compliance_officer@t3 | hp_lost_frac | 0.320 | 0.738 | +0.418 | [+0.291, +0.538] | +130.7 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 40.100 | +24.500 | [+17.150, +31.952] | +157.1 % | **CHANGED** |
| fight:compliance_officer@t3 | perfect_rate | 0.908 | 0.687 | -0.221 | [-0.282, -0.159] | -24.3 % | **CHANGED** |
| fight:compliance_officer@t3 | ram_left_per_turn | 7.166 | 8.581 | +1.415 | [+0.706, +2.130] | +19.7 % | **CHANGED** |
| fight:compliance_officer@t3 | taken | 19.200 | 44.300 | +25.100 | [+17.297, +32.300] | +130.7 % | **CHANGED** |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 4.179 | +1.902 | [+1.068, +2.722] | +83.5 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 8.850 | 10.850 | +2.000 | [+0.900, +3.050] | +22.6 % | **CHANGED** |
| fight:compliance_officer@t3 | won | 1.000 | 0.600 | -0.400 | [-0.600, -0.250] | -40.0 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt | 203.750 | 134.400 | -69.350 | [-87.453, -52.597] | -34.0 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt_per_turn | 15.738 | 11.430 | -4.308 | [-5.656, -2.928] | -27.4 % | **CHANGED** |
| fight:compliance_officer@t4 | died | 0.050 | 0.850 | +0.800 | [+0.650, +0.950] | +1600.0 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_end | 20.200 | 0.700 | -19.500 | [-24.100, -14.850] | -96.5 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 59.300 | +19.500 | [+15.000, +24.200] | +49.0 % | **CHANGED** |
| fight:compliance_officer@t4 | hp_lost_frac | 0.663 | 0.988 | +0.325 | [+0.249, +0.400] | +49.0 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 32.300 | 55.200 | +22.900 | [+17.750, +28.100] | +70.9 % | **CHANGED** |
| fight:compliance_officer@t4 | perfect_rate | 0.888 | 0.651 | -0.238 | [-0.286, -0.186] | -26.8 % | **CHANGED** |
| fight:compliance_officer@t4 | ram_left_per_turn | 7.871 | 8.874 | +1.003 | [+0.462, +1.563] | +12.7 % | **CHANGED** |
| fight:compliance_officer@t4 | taken | 39.800 | 59.300 | +19.500 | [+15.000, +24.002] | +49.0 % | **CHANGED** |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 5.438 | +2.295 | [+1.557, +3.015] | +73.0 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 13.300 | 11.750 | -1.550 | [-2.950, -0.100] | -11.7 % | **CHANGED** |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.294 | -0.062 | [-0.122, -0.003] | -17.5 % | **CHANGED** |
| fight:compliance_officer@t4 | won | 0.950 | 0.150 | -0.800 | [-0.950, -0.650] | -84.2 % | **CHANGED** |
| fight:dosage_dispenser@t1 | dealt_per_turn | 16.468 | 12.889 | -3.579 | [-5.479, -1.363] | -21.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | hp_end | 59.850 | 57.900 | -1.950 | [-3.608, -0.600] | -3.3 % | **CHANGED** |
| fight:dosage_dispenser@t1 | hp_lost | 0.150 | 2.100 | +1.950 | [+0.600, +3.750] | +1300.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | hp_lost_frac | 0.003 | 0.035 | +0.032 | [+0.010, +0.062] | +1300.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | intake | 0.000 | 1.350 | +1.350 | [+0.450, +2.550] | - | **CHANGED** |
| fight:dosage_dispenser@t1 | perfect_rate | 0.871 | 0.615 | -0.256 | [-0.371, -0.138] | -29.4 % | **CHANGED** |
| fight:dosage_dispenser@t1 | ram_left_per_turn | 5.245 | 6.792 | +1.547 | [+0.639, +2.417] | +29.5 % | **CHANGED** |
| fight:dosage_dispenser@t1 | taken | 0.150 | 2.100 | +1.950 | [+0.600, +3.600] | +1300.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | taken_per_turn | 0.050 | 0.505 | +0.455 | [+0.173, +0.772] | +910.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | turns | 2.450 | 3.350 | +0.900 | [+0.400, +1.400] | +36.7 % | **CHANGED** |
| fight:dosage_dispenser@t2 | dealt_per_turn | 17.840 | 13.993 | -3.848 | [-5.721, -1.974] | -21.6 % | **CHANGED** |
| fight:dosage_dispenser@t2 | hp_end | 58.450 | 55.100 | -3.350 | [-5.850, -1.200] | -5.7 % | **CHANGED** |
| fight:dosage_dispenser@t2 | hp_lost | 1.550 | 4.900 | +3.350 | [+1.150, +5.750] | +216.1 % | **CHANGED** |
| fight:dosage_dispenser@t2 | hp_lost_frac | 0.026 | 0.082 | +0.056 | [+0.020, +0.095] | +216.1 % | **CHANGED** |
| fight:dosage_dispenser@t2 | intake | 0.200 | 2.800 | +2.600 | [+1.000, +4.400] | +1300.0 % | **CHANGED** |
| fight:dosage_dispenser@t2 | perfect_rate | 0.866 | 0.663 | -0.203 | [-0.281, -0.125] | -23.5 % | **CHANGED** |
| fight:dosage_dispenser@t2 | ram_left_per_turn | 5.786 | 7.423 | +1.638 | [+0.681, +2.643] | +28.3 % | **CHANGED** |
| fight:dosage_dispenser@t2 | taken | 1.550 | 4.900 | +3.350 | [+1.300, +5.900] | +216.1 % | **CHANGED** |
| fight:dosage_dispenser@t2 | taken_per_turn | 0.424 | 0.997 | +0.573 | [+0.153, +1.012] | +135.1 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns | 3.600 | 4.700 | +1.100 | [+0.500, +1.700] | +30.6 % | **CHANGED** |
| fight:dosage_dispenser@t3 | dealt_per_turn | 17.935 | 13.823 | -4.112 | [-6.023, -2.307] | -22.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | hp_end | 56.350 | 48.400 | -7.950 | [-12.700, -3.850] | -14.1 % | **CHANGED** |
| fight:dosage_dispenser@t3 | hp_lost | 3.650 | 11.600 | +7.950 | [+4.050, +12.700] | +217.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | hp_lost_frac | 0.061 | 0.193 | +0.133 | [+0.068, +0.213] | +217.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | intake | 0.500 | 5.750 | +5.250 | [+2.250, +8.750] | +1050.0 % | **CHANGED** |
| fight:dosage_dispenser@t3 | perfect_rate | 0.891 | 0.658 | -0.234 | [-0.304, -0.164] | -26.2 % | **CHANGED** |
| fight:dosage_dispenser@t3 | ram_left_per_turn | 7.222 | 8.591 | +1.370 | [+0.762, +2.019] | +19.0 % | **CHANGED** |
| fight:dosage_dispenser@t3 | taken | 3.650 | 11.600 | +7.950 | [+4.000, +12.650] | +217.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | taken_per_turn | 0.639 | 1.567 | +0.928 | [+0.394, +1.477] | +145.3 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns | 5.700 | 7.400 | +1.700 | [+0.950, +2.502] | +29.8 % | **CHANGED** |
| fight:dosage_dispenser@t4 | dealt_per_turn | 19.386 | 14.665 | -4.721 | [-6.604, -2.757] | -24.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | hp_end | 52.200 | 36.750 | -15.450 | [-21.400, -9.800] | -29.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | hp_lost | 7.800 | 23.250 | +15.450 | [+9.997, +21.500] | +198.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | hp_lost_frac | 0.130 | 0.388 | +0.258 | [+0.165, +0.356] | +198.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | intake | 1.050 | 11.100 | +10.050 | [+5.450, +15.050] | +957.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | perfect_rate | 0.897 | 0.654 | -0.244 | [-0.310, -0.173] | -27.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | ram_left_per_turn | 7.707 | 8.914 | +1.207 | [+0.588, +1.850] | +15.7 % | **CHANGED** |
| fight:dosage_dispenser@t4 | taken | 7.800 | 23.250 | +15.450 | [+9.850, +21.702] | +198.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | taken_per_turn | 0.981 | 2.107 | +1.125 | [+0.632, +1.698] | +114.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns | 8.300 | 11.000 | +2.700 | [+1.550, +3.850] | +32.5 % | **CHANGED** |
| fight:recall_unit@t1 | dealt_per_turn | 17.702 | 12.178 | -5.524 | [-7.387, -3.664] | -31.2 % | **CHANGED** |
| fight:recall_unit@t1 | enrage_step | 0.150 | 0.900 | +0.750 | [+0.450, +1.050] | +500.0 % | **CHANGED** |
| fight:recall_unit@t1 | hp_end | 42.300 | 29.900 | -12.400 | [-18.850, -5.998] | -29.3 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost | 17.700 | 30.100 | +12.400 | [+5.997, +18.902] | +70.1 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost_frac | 0.295 | 0.502 | +0.207 | [+0.103, +0.314] | +70.1 % | **CHANGED** |
| fight:recall_unit@t1 | intake | 15.600 | 28.000 | +12.400 | [+6.100, +18.850] | +79.5 % | **CHANGED** |
| fight:recall_unit@t1 | perfect_rate | 0.914 | 0.727 | -0.187 | [-0.252, -0.124] | -20.4 % | **CHANGED** |
| fight:recall_unit@t1 | ram_left_per_turn | 7.208 | 8.850 | +1.641 | [+1.081, +2.204] | +22.8 % | **CHANGED** |
| fight:recall_unit@t1 | resistance_absorbed | 5.400 | 9.350 | +3.950 | [+1.800, +5.950] | +73.1 % | **CHANGED** |
| fight:recall_unit@t1 | taken | 17.700 | 30.100 | +12.400 | [+6.000, +19.202] | +70.1 % | **CHANGED** |
| fight:recall_unit@t1 | turns | 6.200 | 9.550 | +3.350 | [+2.200, +4.500] | +54.0 % | **CHANGED** |
| fight:recall_unit@t2 | dealt | 168.200 | 142.650 | -25.550 | [-38.300, -14.350] | -15.2 % | **CHANGED** |
| fight:recall_unit@t2 | dealt_per_turn | 15.864 | 10.902 | -4.962 | [-6.184, -3.728] | -31.3 % | **CHANGED** |
| fight:recall_unit@t2 | died | 0.100 | 0.650 | +0.550 | [+0.350, +0.750] | +550.0 % | **CHANGED** |
| fight:recall_unit@t2 | enrage_step | 1.100 | 1.600 | +0.500 | [+0.250, +0.750] | +45.5 % | **CHANGED** |
| fight:recall_unit@t2 | hp_end | 23.650 | 4.800 | -18.850 | [-25.303, -12.750] | -79.7 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost | 36.350 | 55.200 | +18.850 | [+12.500, +24.800] | +51.9 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost_frac | 0.606 | 0.920 | +0.314 | [+0.213, +0.413] | +51.9 % | **CHANGED** |
| fight:recall_unit@t2 | intake | 30.500 | 49.900 | +19.400 | [+12.750, +26.250] | +63.6 % | **CHANGED** |
| fight:recall_unit@t2 | perfect_rate | 0.904 | 0.652 | -0.252 | [-0.303, -0.199] | -27.9 % | **CHANGED** |
| fight:recall_unit@t2 | ram_left_per_turn | 8.293 | 9.101 | +0.809 | [+0.442, +1.178] | +9.8 % | **CHANGED** |
| fight:recall_unit@t2 | resistance_absorbed | 10.500 | 14.650 | +4.150 | [+1.550, +6.850] | +39.5 % | **CHANGED** |
| fight:recall_unit@t2 | taken | 36.350 | 55.200 | +18.850 | [+12.647, +25.000] | +51.9 % | **CHANGED** |
| fight:recall_unit@t2 | turns | 10.750 | 13.350 | +2.600 | [+1.700, +3.500] | +24.2 % | **CHANGED** |
| fight:recall_unit@t2 | won | 0.900 | 0.350 | -0.550 | [-0.750, -0.350] | -61.1 % | **CHANGED** |
| fight:recall_unit@t3 | dealt | 221.550 | 133.400 | -88.150 | [-118.400, -58.000] | -39.8 % | **CHANGED** |
| fight:recall_unit@t3 | dealt_per_turn | 14.155 | 10.412 | -3.743 | [-5.666, -2.036] | -26.4 % | **CHANGED** |
| fight:recall_unit@t3 | died | 0.750 | 1.000 | +0.250 | [+0.100, +0.400] | +33.3 % | **CHANGED** |
| fight:recall_unit@t3 | enrage_step | 2.300 | 1.500 | -0.800 | [-1.250, -0.350] | -34.8 % | **CHANGED** |
| fight:recall_unit@t3 | hp_end | 2.250 | 0.000 | -2.250 | [-4.150, -0.750] | -100.0 % | **CHANGED** |
| fight:recall_unit@t3 | hp_lost | 57.750 | 60.000 | +2.250 | [+0.700, +4.200] | +3.9 % | **CHANGED** |
| fight:recall_unit@t3 | hp_lost_frac | 0.963 | 1.000 | +0.037 | [+0.012, +0.069] | +3.9 % | **CHANGED** |
| fight:recall_unit@t3 | intake | 49.800 | 56.100 | +6.300 | [+2.900, +9.800] | +12.7 % | **CHANGED** |
| fight:recall_unit@t3 | perfect_rate | 0.830 | 0.610 | -0.220 | [-0.301, -0.139] | -26.5 % | **CHANGED** |
| fight:recall_unit@t3 | ram_left_per_turn | 8.856 | 9.366 | +0.510 | [+0.043, +0.996] | +5.8 % | **CHANGED** |
| fight:recall_unit@t3 | resistance_absorbed | 17.100 | 12.900 | -4.200 | [-7.800, -0.400] | -24.6 % | **CHANGED** |
| fight:recall_unit@t3 | taken | 57.750 | 60.000 | +2.250 | [+0.700, +4.100] | +3.9 % | **CHANGED** |
| fight:recall_unit@t3 | taken_per_turn | 3.933 | 5.392 | +1.459 | [+0.504, +2.448] | +37.1 % | **CHANGED** |
| fight:recall_unit@t3 | turns | 16.650 | 12.450 | -4.200 | [-6.650, -1.800] | -25.2 % | **CHANGED** |
| fight:recall_unit@t3 | won | 0.250 | 0.000 | -0.250 | [-0.400, -0.100] | -100.0 % | **CHANGED** |
| fight:recall_unit@t4 | dealt | 215.100 | 94.300 | -120.800 | [-161.257, -79.288] | -56.2 % | **CHANGED** |
| fight:recall_unit@t4 | dealt_per_turn | 13.893 | 9.301 | -4.592 | [-6.525, -2.567] | -33.1 % | **CHANGED** |
| fight:recall_unit@t4 | enrage_step | 2.300 | 1.050 | -1.250 | [-1.800, -0.700] | -54.3 % | **CHANGED** |
| fight:recall_unit@t4 | intake | 51.900 | 57.600 | +5.700 | [+2.850, +8.850] | +11.0 % | **CHANGED** |
| fight:recall_unit@t4 | perfect_rate | 0.785 | 0.588 | -0.197 | [-0.278, -0.118] | -25.1 % | **CHANGED** |
| fight:recall_unit@t4 | ram_left_per_turn | 8.711 | 9.184 | +0.473 | [+0.008, +0.942] | +5.4 % | **CHANGED** |
| fight:recall_unit@t4 | resistance_absorbed | 17.850 | 9.550 | -8.300 | [-13.400, -3.100] | -46.5 % | **CHANGED** |
| fight:recall_unit@t4 | turns | 16.000 | 10.300 | -5.700 | [-8.603, -2.750] | -35.6 % | **CHANGED** |
| fight:triage_unit@t1 | dealt_per_turn | 17.137 | 12.912 | -4.226 | [-6.457, -1.964] | -24.7 % | **CHANGED** |
| fight:triage_unit@t1 | heal_turns | 0.750 | 1.300 | +0.550 | [+0.150, +0.950] | +73.3 % | **CHANGED** |
| fight:triage_unit@t1 | perfect_rate | 0.898 | 0.688 | -0.210 | [-0.302, -0.117] | -23.4 % | **CHANGED** |
| fight:triage_unit@t1 | ram_left_per_turn | 4.996 | 7.098 | +2.102 | [+1.000, +3.171] | +42.1 % | **CHANGED** |
| fight:triage_unit@t1 | turns | 2.800 | 3.950 | +1.150 | [+0.600, +1.750] | +41.1 % | **CHANGED** |
| fight:triage_unit@t1 | turns_both_share | 0.447 | 0.302 | -0.146 | [-0.267, -0.023] | -32.6 % | **CHANGED** |
| fight:triage_unit@t2 | dealt | 72.000 | 74.000 | +2.000 | [+1.000, +3.150] | +2.8 % | **CHANGED** |
| fight:triage_unit@t2 | dealt_per_turn | 19.320 | 12.868 | -6.452 | [-8.633, -4.205] | -33.4 % | **CHANGED** |
| fight:triage_unit@t2 | heal_total | 4.600 | 9.050 | +4.450 | [+1.200, +7.650] | +96.7 % | **CHANGED** |
| fight:triage_unit@t2 | heal_turns | 1.050 | 1.750 | +0.700 | [+0.150, +1.300] | +66.7 % | **CHANGED** |
| fight:triage_unit@t2 | hp_lost | 2.500 | 5.100 | +2.600 | [+0.047, +5.750] | +104.0 % | **CHANGED** |
| fight:triage_unit@t2 | hp_lost_frac | 0.042 | 0.085 | +0.043 | [+0.000, +0.098] | +104.0 % | **CHANGED** |
| fight:triage_unit@t2 | perfect_rate | 0.926 | 0.679 | -0.247 | [-0.329, -0.161] | -26.7 % | **CHANGED** |
| fight:triage_unit@t2 | ram_left_per_turn | 5.419 | 7.889 | +2.471 | [+1.349, +3.662] | +45.6 % | **CHANGED** |
| fight:triage_unit@t2 | resistance_absorbed | 2.150 | 2.950 | +0.800 | [+0.200, +1.450] | +37.2 % | **CHANGED** |
| fight:triage_unit@t2 | taken | 2.500 | 5.100 | +2.600 | [+0.100, +5.800] | +104.0 % | **CHANGED** |
| fight:triage_unit@t2 | turns | 4.000 | 6.350 | +2.350 | [+1.500, +3.200] | +58.7 % | **CHANGED** |
| fight:triage_unit@t2 | turns_both_share | 0.473 | 0.352 | -0.120 | [-0.243, -0.001] | -25.4 % | **CHANGED** |
| fight:triage_unit@t3 | dealt | 115.000 | 120.600 | +5.600 | [+3.400, +7.950] | +4.9 % | **CHANGED** |
| fight:triage_unit@t3 | dealt_per_turn | 16.372 | 12.346 | -4.026 | [-5.860, -2.196] | -24.6 % | **CHANGED** |
| fight:triage_unit@t3 | heal_total | 11.250 | 21.800 | +10.550 | [+5.147, +16.000] | +93.8 % | **CHANGED** |
| fight:triage_unit@t3 | heal_turns | 2.200 | 3.300 | +1.100 | [+0.300, +1.900] | +50.0 % | **CHANGED** |
| fight:triage_unit@t3 | hp_end | 53.900 | 48.650 | -5.250 | [-9.652, -0.950] | -9.7 % | **CHANGED** |
| fight:triage_unit@t3 | hp_lost | 6.100 | 11.350 | +5.250 | [+1.050, +9.850] | +86.1 % | **CHANGED** |
| fight:triage_unit@t3 | hp_lost_frac | 0.102 | 0.189 | +0.088 | [+0.017, +0.164] | +86.1 % | **CHANGED** |
| fight:triage_unit@t3 | intake | 2.500 | 6.850 | +4.350 | [+0.850, +8.050] | +174.0 % | **CHANGED** |
| fight:triage_unit@t3 | perfect_rate | 0.825 | 0.653 | -0.172 | [-0.248, -0.100] | -20.8 % | **CHANGED** |
| fight:triage_unit@t3 | ram_left_per_turn | 6.856 | 8.842 | +1.986 | [+0.993, +2.983] | +29.0 % | **CHANGED** |
| fight:triage_unit@t3 | taken | 6.100 | 11.350 | +5.250 | [+1.247, +9.602] | +86.1 % | **CHANGED** |
| fight:triage_unit@t3 | turns | 7.450 | 10.600 | +3.150 | [+1.750, +4.550] | +42.3 % | **CHANGED** |
| fight:triage_unit@t3 | turns_both_share | 0.449 | 0.310 | -0.139 | [-0.236, -0.039] | -30.9 % | **CHANGED** |
| fight:triage_unit@t4 | dealt | 184.350 | 199.050 | +14.700 | [+10.850, +19.050] | +8.0 % | **CHANGED** |
| fight:triage_unit@t4 | dealt_per_turn | 14.656 | 10.294 | -4.362 | [-5.861, -2.789] | -29.8 % | **CHANGED** |
| fight:triage_unit@t4 | heal_total | 27.850 | 54.050 | +26.200 | [+16.750, +34.703] | +94.1 % | **CHANGED** |
| fight:triage_unit@t4 | heal_turns | 3.850 | 6.400 | +2.550 | [+1.550, +3.550] | +66.2 % | **CHANGED** |
| fight:triage_unit@t4 | hp_end | 47.800 | 30.550 | -17.250 | [-22.800, -11.550] | -36.1 % | **CHANGED** |
| fight:triage_unit@t4 | hp_lost | 12.200 | 29.450 | +17.250 | [+11.797, +22.900] | +141.4 % | **CHANGED** |
| fight:triage_unit@t4 | hp_lost_frac | 0.203 | 0.491 | +0.287 | [+0.197, +0.382] | +141.4 % | **CHANGED** |
| fight:triage_unit@t4 | intake | 3.800 | 16.700 | +12.900 | [+7.700, +18.605] | +339.5 % | **CHANGED** |
| fight:triage_unit@t4 | perfect_rate | 0.819 | 0.584 | -0.235 | [-0.290, -0.178] | -28.7 % | **CHANGED** |
| fight:triage_unit@t4 | ram_left_per_turn | 7.784 | 9.361 | +1.577 | [+0.793, +2.374] | +20.3 % | **CHANGED** |
| fight:triage_unit@t4 | resistance_absorbed | 7.050 | 9.700 | +2.650 | [+1.500, +3.800] | +37.6 % | **CHANGED** |
| fight:triage_unit@t4 | taken | 12.200 | 29.450 | +17.250 | [+11.800, +23.152] | +141.4 % | **CHANGED** |
| fight:triage_unit@t4 | taken_per_turn | 0.962 | 1.472 | +0.511 | [+0.214, +0.815] | +53.1 % | **CHANGED** |
| fight:triage_unit@t4 | turns | 13.300 | 20.400 | +7.100 | [+4.950, +9.250] | +53.4 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| fight:account_manager@t1 | dealt_per_turn | 18.992 | 13.954 | -5.039 | [-6.933, -3.173] | -26.5 % | **CHANGED** |
| fight:account_manager@t1 | died | 0.000 | 0.450 | +0.450 | [+0.300, +0.650] | - | **CHANGED** |
| fight:account_manager@t1 | enrage_step | 0.200 | 0.800 | +0.600 | [+0.350, +0.850] | +300.0 % | **CHANGED** |
| fight:account_manager@t1 | hp_lost | 19.350 | 43.600 | +24.250 | [+15.697, +32.650] | +125.3 % | **CHANGED** |
| fight:account_manager@t1 | intake | 15.150 | 36.450 | +21.300 | [+13.850, +28.500] | +140.6 % | **CHANGED** |
| fight:account_manager@t1 | parked | 20.650 | 14.400 | -6.250 | [-11.400, -1.050] | -30.3 % | **CHANGED** |
| fight:account_manager@t1 | resistance_absorbed | 9.300 | 10.000 | +0.700 | [-1.350, +2.802] | +7.5 % | noise |
| fight:account_manager@t1 | taken_per_turn | 2.500 | 3.910 | +1.410 | [+0.487, +2.288] | +56.4 % | **CHANGED** |
| fight:account_manager@t1 | turns | 8.150 | 10.850 | +2.700 | [+1.700, +3.700] | +33.1 % | **CHANGED** |
| fight:account_manager@t1 | turns_both_share | 0.311 | 0.255 | -0.056 | [-0.140, +0.028] | -18.1 % | noise |
| fight:account_manager@t1 | won | 1.000 | 0.550 | -0.450 | [-0.650, -0.250] | -45.0 % | **CHANGED** |
| fight:account_manager@t2 | dealt_per_turn | 19.410 | 13.037 | -6.372 | [-8.072, -4.609] | -32.8 % | **CHANGED** |
| fight:account_manager@t2 | died | 0.100 | 0.900 | +0.800 | [+0.650, +0.950] | +800.0 % | **CHANGED** |
| fight:account_manager@t2 | enrage_step | 1.250 | 1.400 | +0.150 | [-0.150, +0.450] | +12.0 % | noise |
| fight:account_manager@t2 | hp_lost | 37.850 | 58.700 | +20.850 | [+15.697, +26.300] | +55.1 % | **CHANGED** |
| fight:account_manager@t2 | intake | 27.200 | 46.800 | +19.600 | [+13.747, +25.150] | +72.1 % | **CHANGED** |
| fight:account_manager@t2 | parked | 16.100 | 9.900 | -6.200 | [-13.300, +0.652] | -38.5 % | noise |
| fight:account_manager@t2 | resistance_absorbed | 14.850 | 13.900 | -0.950 | [-4.050, +2.250] | -6.4 % | noise |
| fight:account_manager@t2 | taken_per_turn | 2.971 | 4.406 | +1.435 | [+0.950, +1.907] | +48.3 % | **CHANGED** |
| fight:account_manager@t2 | turns | 12.850 | 13.700 | +0.850 | [-0.450, +2.150] | +6.6 % | noise |
| fight:account_manager@t2 | turns_both_share | 0.292 | 0.260 | -0.032 | [-0.103, +0.036] | -11.0 % | noise |
| fight:account_manager@t2 | won | 0.900 | 0.100 | -0.800 | [-0.950, -0.650] | -88.9 % | **CHANGED** |
| fight:account_manager@t3 | dealt_per_turn | 16.271 | 10.530 | -5.741 | [-7.200, -4.326] | -35.3 % | **CHANGED** |
| fight:account_manager@t3 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t3 | enrage_step | 2.650 | 1.750 | -0.900 | [-1.350, -0.450] | -34.0 % | **CHANGED** |
| fight:account_manager@t3 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t3 | intake | 43.700 | 45.250 | +1.550 | [-2.100, +4.803] | +3.5 % | noise |
| fight:account_manager@t3 | parked | 16.400 | 2.200 | -14.200 | [-19.750, -9.450] | -86.6 % | **CHANGED** |
| fight:account_manager@t3 | resistance_absorbed | 23.250 | 15.200 | -8.050 | [-11.950, -4.350] | -34.6 % | **CHANGED** |
| fight:account_manager@t3 | taken_per_turn | 3.079 | 4.222 | +1.143 | [+0.575, +1.762] | +37.1 % | **CHANGED** |
| fight:account_manager@t3 | turns | 20.200 | 15.600 | -4.600 | [-6.750, -2.500] | -22.8 % | **CHANGED** |
| fight:account_manager@t3 | turns_both_share | 0.233 | 0.209 | -0.023 | [-0.067, +0.021] | -10.1 % | noise |
| fight:account_manager@t3 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:account_manager@t4 | dealt_per_turn | 15.009 | 10.642 | -4.367 | [-6.048, -2.682] | -29.1 % | **CHANGED** |
| fight:account_manager@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t4 | enrage_step | 2.650 | 1.300 | -1.350 | [-1.900, -0.750] | -50.9 % | **CHANGED** |
| fight:account_manager@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:account_manager@t4 | intake | 41.400 | 49.500 | +8.100 | [+3.500, +12.500] | +19.6 % | **CHANGED** |
| fight:account_manager@t4 | parked | 1.800 | 0.000 | -1.800 | [-3.150, -0.700] | -100.0 % | **CHANGED** |
| fight:account_manager@t4 | resistance_absorbed | 19.950 | 13.300 | -6.650 | [-10.550, -2.700] | -33.3 % | **CHANGED** |
| fight:account_manager@t4 | taken_per_turn | 3.178 | 5.620 | +2.443 | [+1.357, +3.650] | +76.9 % | **CHANGED** |
| fight:account_manager@t4 | turns | 20.250 | 13.300 | -6.950 | [-9.600, -4.250] | -34.3 % | **CHANGED** |
| fight:account_manager@t4 | turns_both_share | 0.203 | 0.230 | +0.027 | [-0.027, +0.080] | +13.4 % | noise |
| fight:account_manager@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | dealt_per_turn | 17.150 | 14.125 | -3.025 | [-5.350, -0.700] | -17.6 % | **CHANGED** |
| fight:billing_daemon@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | hp_lost | 3.600 | 8.850 | +5.250 | [+2.700, +7.700] | +145.8 % | **CHANGED** |
| fight:billing_daemon@t1 | intake | 3.150 | 8.550 | +5.400 | [+3.050, +7.850] | +171.4 % | **CHANGED** |
| fight:billing_daemon@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t1 | resistance_absorbed | 1.750 | 2.000 | +0.250 | [-0.200, +0.700] | +14.3 % | noise |
| fight:billing_daemon@t1 | taken_per_turn | 1.433 | 2.667 | +1.234 | [+0.413, +2.064] | +86.1 % | **CHANGED** |
| fight:billing_daemon@t1 | turns | 2.600 | 3.450 | +0.850 | [+0.300, +1.450] | +32.7 % | **CHANGED** |
| fight:billing_daemon@t1 | turns_both_share | 0.529 | 0.448 | -0.082 | [-0.226, +0.071] | -15.4 % | noise |
| fight:billing_daemon@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t2 | dealt_per_turn | 16.000 | 12.919 | -3.081 | [-5.062, -1.008] | -19.3 % | **CHANGED** |
| fight:billing_daemon@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | hp_lost | 7.850 | 14.350 | +6.500 | [+2.900, +10.250] | +82.8 % | **CHANGED** |
| fight:billing_daemon@t2 | intake | 6.950 | 14.050 | +7.100 | [+3.250, +10.750] | +102.2 % | **CHANGED** |
| fight:billing_daemon@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t2 | resistance_absorbed | 2.200 | 2.700 | +0.500 | [-0.150, +1.200] | +22.7 % | noise |
| fight:billing_daemon@t2 | taken_per_turn | 1.830 | 2.579 | +0.749 | [+0.015, +1.435] | +40.9 % | **CHANGED** |
| fight:billing_daemon@t2 | turns | 4.500 | 5.700 | +1.200 | [+0.350, +2.150] | +26.7 % | **CHANGED** |
| fight:billing_daemon@t2 | turns_both_share | 0.426 | 0.356 | -0.070 | [-0.172, +0.027] | -16.3 % | noise |
| fight:billing_daemon@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:billing_daemon@t3 | dealt_per_turn | 16.514 | 11.200 | -5.313 | [-6.696, -3.964] | -32.2 % | **CHANGED** |
| fight:billing_daemon@t3 | died | 0.000 | 0.150 | +0.150 | [+0.050, +0.300] | - | **CHANGED** |
| fight:billing_daemon@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | hp_lost | 11.550 | 33.650 | +22.100 | [+15.900, +28.250] | +191.3 % | **CHANGED** |
| fight:billing_daemon@t3 | intake | 8.700 | 31.250 | +22.550 | [+16.297, +28.750] | +259.2 % | **CHANGED** |
| fight:billing_daemon@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t3 | resistance_absorbed | 4.550 | 5.550 | +1.000 | [+0.150, +1.850] | +22.0 % | **CHANGED** |
| fight:billing_daemon@t3 | taken_per_turn | 1.795 | 3.328 | +1.533 | [+0.840, +2.207] | +85.4 % | **CHANGED** |
| fight:billing_daemon@t3 | turns | 6.750 | 9.900 | +3.150 | [+2.350, +3.950] | +46.7 % | **CHANGED** |
| fight:billing_daemon@t3 | turns_both_share | 0.546 | 0.422 | -0.124 | [-0.226, -0.030] | -22.7 % | **CHANGED** |
| fight:billing_daemon@t3 | won | 1.000 | 0.850 | -0.150 | [-0.300, -0.050] | -15.0 % | **CHANGED** |
| fight:billing_daemon@t4 | dealt_per_turn | 15.319 | 11.519 | -3.800 | [-5.377, -2.132] | -24.8 % | **CHANGED** |
| fight:billing_daemon@t4 | died | 0.000 | 0.700 | +0.700 | [+0.550, +0.850] | - | **CHANGED** |
| fight:billing_daemon@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | hp_lost | 25.200 | 54.650 | +29.450 | [+23.148, +35.500] | +116.9 % | **CHANGED** |
| fight:billing_daemon@t4 | intake | 19.800 | 51.200 | +31.400 | [+24.897, +37.050] | +158.6 % | **CHANGED** |
| fight:billing_daemon@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:billing_daemon@t4 | resistance_absorbed | 7.200 | 6.600 | -0.600 | [-1.650, +0.450] | -8.3 % | noise |
| fight:billing_daemon@t4 | taken_per_turn | 2.166 | 4.687 | +2.521 | [+1.866, +3.253] | +116.4 % | **CHANGED** |
| fight:billing_daemon@t4 | turns | 11.650 | 12.500 | +0.850 | [-0.450, +2.200] | +7.3 % | noise |
| fight:billing_daemon@t4 | turns_both_share | 0.476 | 0.383 | -0.093 | [-0.172, -0.017] | -19.5 % | **CHANGED** |
| fight:billing_daemon@t4 | won | 1.000 | 0.300 | -0.700 | [-0.850, -0.550] | -70.0 % | **CHANGED** |
| fight:care_swarm@t1 | dealt_per_turn | 10.886 | 8.998 | -1.887 | [-5.097, +1.551] | -17.3 % | noise |
| fight:care_swarm@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | hp_lost | 12.500 | 17.300 | +4.800 | [+1.500, +8.702] | +38.4 % | **CHANGED** |
| fight:care_swarm@t1 | intake | 12.500 | 17.300 | +4.800 | [+1.450, +8.450] | +38.4 % | **CHANGED** |
| fight:care_swarm@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t1 | resistance_absorbed | 1.400 | 1.400 | +0.000 | [-0.550, +0.550] | +0.0 % | noise |
| fight:care_swarm@t1 | taken_per_turn | 4.865 | 4.815 | -0.050 | [-1.013, +0.924] | -1.0 % | noise |
| fight:care_swarm@t1 | turns | 3.050 | 3.900 | +0.850 | [-0.150, +1.900] | +27.9 % | noise |
| fight:care_swarm@t1 | turns_both_share | 0.364 | 0.245 | -0.119 | [-0.262, +0.028] | -32.7 % | noise |
| fight:care_swarm@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t2 | dealt_per_turn | 10.968 | 7.917 | -3.051 | [-5.120, -0.835] | -27.8 % | **CHANGED** |
| fight:care_swarm@t2 | died | 0.000 | 0.250 | +0.250 | [+0.100, +0.400] | - | **CHANGED** |
| fight:care_swarm@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | hp_lost | 22.900 | 37.300 | +14.400 | [+8.700, +20.800] | +62.9 % | **CHANGED** |
| fight:care_swarm@t2 | intake | 22.750 | 36.850 | +14.100 | [+8.397, +19.750] | +62.0 % | **CHANGED** |
| fight:care_swarm@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t2 | resistance_absorbed | 1.950 | 2.300 | +0.350 | [-0.400, +1.050] | +17.9 % | noise |
| fight:care_swarm@t2 | taken_per_turn | 6.007 | 6.286 | +0.279 | [-0.731, +1.255] | +4.6 % | noise |
| fight:care_swarm@t2 | turns | 4.150 | 6.250 | +2.100 | [+0.950, +3.350] | +50.6 % | **CHANGED** |
| fight:care_swarm@t2 | turns_both_share | 0.353 | 0.292 | -0.061 | [-0.183, +0.065] | -17.3 % | noise |
| fight:care_swarm@t2 | won | 1.000 | 0.750 | -0.250 | [-0.400, -0.100] | -25.0 % | **CHANGED** |
| fight:care_swarm@t3 | dealt_per_turn | 10.205 | 7.572 | -2.633 | [-4.476, -0.865] | -25.8 % | **CHANGED** |
| fight:care_swarm@t3 | died | 0.050 | 0.600 | +0.550 | [+0.350, +0.750] | +1100.0 % | **CHANGED** |
| fight:care_swarm@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t3 | hp_lost | 46.000 | 53.400 | +7.400 | [+2.000, +12.602] | +16.1 % | **CHANGED** |
| fight:care_swarm@t3 | intake | 44.950 | 52.650 | +7.700 | [+2.647, +12.950] | +17.1 % | **CHANGED** |
| fight:care_swarm@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t3 | resistance_absorbed | 3.400 | 2.850 | -0.550 | [-1.350, +0.200] | -16.2 % | noise |
| fight:care_swarm@t3 | taken_per_turn | 7.030 | 7.357 | +0.328 | [-0.796, +1.457] | +4.7 % | noise |
| fight:care_swarm@t3 | turns | 7.100 | 7.800 | +0.700 | [-0.550, +1.950] | +9.9 % | noise |
| fight:care_swarm@t3 | turns_both_share | 0.395 | 0.246 | -0.149 | [-0.244, -0.055] | -37.7 % | **CHANGED** |
| fight:care_swarm@t3 | won | 0.950 | 0.400 | -0.550 | [-0.750, -0.350] | -57.9 % | **CHANGED** |
| fight:care_swarm@t4 | dealt_per_turn | 9.313 | 8.188 | -1.125 | [-3.198, +0.948] | -12.1 % | noise |
| fight:care_swarm@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:care_swarm@t4 | intake | 58.050 | 59.100 | +1.050 | [+0.000, +2.100] | +1.8 % | noise |
| fight:care_swarm@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:care_swarm@t4 | resistance_absorbed | 2.600 | 2.000 | -0.600 | [-1.250, +0.050] | -23.1 % | noise |
| fight:care_swarm@t4 | taken_per_turn | 10.081 | 10.797 | +0.716 | [-0.638, +2.129] | +7.1 % | noise |
| fight:care_swarm@t4 | turns | 6.400 | 5.900 | -0.500 | [-1.350, +0.300] | -7.8 % | noise |
| fight:care_swarm@t4 | turns_both_share | 0.328 | 0.264 | -0.064 | [-0.158, +0.031] | -19.5 % | noise |
| fight:care_swarm@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | dealt_per_turn | 38.172 | 28.395 | -9.776 | [-15.479, -4.123] | -25.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | enrage_step | 0.000 | 0.050 | +0.050 | [+0.000, +0.150] | - | noise |
| fight:claims_adjuster@t1 | hp_lost | 19.100 | 29.050 | +9.950 | [+4.650, +15.700] | +52.1 % | **CHANGED** |
| fight:claims_adjuster@t1 | intake | 17.900 | 26.800 | +8.900 | [+3.648, +14.200] | +49.7 % | **CHANGED** |
| fight:claims_adjuster@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t1 | resistance_absorbed | 3.900 | 4.800 | +0.900 | [-0.800, +2.400] | +23.1 % | noise |
| fight:claims_adjuster@t1 | taken_per_turn | 6.366 | 6.680 | +0.314 | [-1.207, +1.788] | +4.9 % | noise |
| fight:claims_adjuster@t1 | turns | 3.200 | 4.500 | +1.300 | [+0.600, +2.000] | +40.6 % | **CHANGED** |
| fight:claims_adjuster@t1 | turns_both_share | 0.320 | 0.311 | -0.009 | [-0.128, +0.112] | -2.8 % | noise |
| fight:claims_adjuster@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:claims_adjuster@t2 | dealt_per_turn | 35.969 | 24.977 | -10.992 | [-15.074, -6.772] | -30.6 % | **CHANGED** |
| fight:claims_adjuster@t2 | died | 0.050 | 0.500 | +0.450 | [+0.250, +0.650] | +900.0 % | **CHANGED** |
| fight:claims_adjuster@t2 | enrage_step | 0.000 | 0.300 | +0.300 | [+0.150, +0.500] | - | **CHANGED** |
| fight:claims_adjuster@t2 | hp_lost | 33.700 | 48.650 | +14.950 | [+7.147, +21.952] | +44.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | intake | 30.700 | 43.100 | +12.400 | [+4.397, +20.102] | +40.4 % | **CHANGED** |
| fight:claims_adjuster@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t2 | resistance_absorbed | 6.750 | 7.850 | +1.100 | [-1.050, +3.250] | +16.3 % | noise |
| fight:claims_adjuster@t2 | taken_per_turn | 6.578 | 7.344 | +0.767 | [-0.567, +2.078] | +11.7 % | noise |
| fight:claims_adjuster@t2 | turns | 5.200 | 6.800 | +1.600 | [+0.950, +2.300] | +30.8 % | **CHANGED** |
| fight:claims_adjuster@t2 | turns_both_share | 0.372 | 0.335 | -0.037 | [-0.147, +0.071] | -10.1 % | noise |
| fight:claims_adjuster@t2 | won | 0.950 | 0.500 | -0.450 | [-0.650, -0.250] | -47.4 % | **CHANGED** |
| fight:claims_adjuster@t3 | dealt_per_turn | 33.029 | 26.787 | -6.243 | [-9.914, -2.663] | -18.9 % | **CHANGED** |
| fight:claims_adjuster@t3 | died | 0.650 | 0.900 | +0.250 | [+0.050, +0.450] | +38.5 % | **CHANGED** |
| fight:claims_adjuster@t3 | enrage_step | 0.650 | 0.300 | -0.350 | [-0.600, -0.050] | -53.8 % | **CHANGED** |
| fight:claims_adjuster@t3 | hp_lost | 55.800 | 58.000 | +2.200 | [-1.203, +5.552] | +3.9 % | noise |
| fight:claims_adjuster@t3 | intake | 50.400 | 53.350 | +2.950 | [-1.700, +7.650] | +5.9 % | noise |
| fight:claims_adjuster@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t3 | resistance_absorbed | 8.550 | 7.100 | -1.450 | [-4.150, +1.350] | -17.0 % | noise |
| fight:claims_adjuster@t3 | taken_per_turn | 7.232 | 10.455 | +3.223 | [+1.808, +4.795] | +44.6 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns | 8.150 | 6.300 | -1.850 | [-2.903, -0.750] | -22.7 % | **CHANGED** |
| fight:claims_adjuster@t3 | turns_both_share | 0.273 | 0.280 | +0.007 | [-0.080, +0.102] | +2.6 % | noise |
| fight:claims_adjuster@t3 | won | 0.350 | 0.100 | -0.250 | [-0.450, -0.050] | -71.4 % | **CHANGED** |
| fight:claims_adjuster@t4 | dealt_per_turn | 33.521 | 25.920 | -7.601 | [-12.561, -2.829] | -22.7 % | **CHANGED** |
| fight:claims_adjuster@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:claims_adjuster@t4 | enrage_step | 0.600 | 0.300 | -0.300 | [-0.550, +0.000] | -50.0 % | noise |
| fight:claims_adjuster@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:claims_adjuster@t4 | intake | 55.500 | 56.700 | +1.200 | [-0.900, +3.450] | +2.2 % | noise |
| fight:claims_adjuster@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:claims_adjuster@t4 | resistance_absorbed | 8.850 | 6.350 | -2.500 | [-5.600, +0.650] | -28.2 % | noise |
| fight:claims_adjuster@t4 | taken_per_turn | 9.357 | 13.007 | +3.650 | [+1.119, +5.952] | +39.0 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns | 7.700 | 5.550 | -2.150 | [-3.500, -0.648] | -27.9 % | **CHANGED** |
| fight:claims_adjuster@t4 | turns_both_share | 0.231 | 0.234 | +0.003 | [-0.082, +0.087] | +1.5 % | noise |
| fight:claims_adjuster@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | dealt_per_turn | 15.332 | 11.818 | -3.514 | [-5.514, -1.480] | -22.9 % | **CHANGED** |
| fight:collections_agent@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | hp_lost | 5.850 | 10.200 | +4.350 | [+1.550, +7.102] | +74.4 % | **CHANGED** |
| fight:collections_agent@t1 | intake | 5.550 | 9.900 | +4.350 | [+1.600, +7.100] | +78.4 % | **CHANGED** |
| fight:collections_agent@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t1 | resistance_absorbed | 1.200 | 1.650 | +0.450 | [-0.050, +1.000] | +37.5 % | noise |
| fight:collections_agent@t1 | taken_per_turn | 2.167 | 2.650 | +0.483 | [-0.336, +1.299] | +22.3 % | noise |
| fight:collections_agent@t1 | turns | 2.800 | 3.750 | +0.950 | [+0.447, +1.450] | +33.9 % | **CHANGED** |
| fight:collections_agent@t1 | turns_both_share | 0.367 | 0.264 | -0.103 | [-0.255, +0.041] | -28.0 % | noise |
| fight:collections_agent@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t2 | dealt_per_turn | 16.811 | 12.975 | -3.836 | [-6.010, -1.577] | -22.8 % | **CHANGED** |
| fight:collections_agent@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | hp_lost | 10.700 | 19.600 | +8.900 | [+4.250, +13.350] | +83.2 % | **CHANGED** |
| fight:collections_agent@t2 | intake | 9.650 | 17.950 | +8.300 | [+4.500, +12.450] | +86.0 % | **CHANGED** |
| fight:collections_agent@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t2 | resistance_absorbed | 1.900 | 2.500 | +0.600 | [-0.050, +1.250] | +31.6 % | noise |
| fight:collections_agent@t2 | taken_per_turn | 2.863 | 3.574 | +0.711 | [-0.156, +1.567] | +24.8 % | noise |
| fight:collections_agent@t2 | turns | 4.200 | 5.400 | +1.200 | [+0.350, +1.950] | +28.6 % | **CHANGED** |
| fight:collections_agent@t2 | turns_both_share | 0.439 | 0.272 | -0.167 | [-0.293, -0.041] | -38.1 % | **CHANGED** |
| fight:collections_agent@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:collections_agent@t3 | dealt_per_turn | 16.922 | 12.422 | -4.500 | [-6.325, -2.657] | -26.6 % | **CHANGED** |
| fight:collections_agent@t3 | died | 0.000 | 0.350 | +0.350 | [+0.200, +0.550] | - | **CHANGED** |
| fight:collections_agent@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | hp_lost | 18.850 | 41.100 | +22.250 | [+15.650, +28.703] | +118.0 % | **CHANGED** |
| fight:collections_agent@t3 | intake | 16.150 | 36.750 | +20.600 | [+14.300, +26.700] | +127.6 % | **CHANGED** |
| fight:collections_agent@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t3 | resistance_absorbed | 3.450 | 3.900 | +0.450 | [-0.200, +1.150] | +13.0 % | noise |
| fight:collections_agent@t3 | taken_per_turn | 3.067 | 4.938 | +1.871 | [+1.110, +2.613] | +61.0 % | **CHANGED** |
| fight:collections_agent@t3 | turns | 6.300 | 8.150 | +1.850 | [+1.100, +2.600] | +29.4 % | **CHANGED** |
| fight:collections_agent@t3 | turns_both_share | 0.459 | 0.302 | -0.157 | [-0.240, -0.071] | -34.2 % | **CHANGED** |
| fight:collections_agent@t3 | won | 1.000 | 0.650 | -0.350 | [-0.550, -0.200] | -35.0 % | **CHANGED** |
| fight:collections_agent@t4 | dealt_per_turn | 16.698 | 12.533 | -4.165 | [-5.701, -2.639] | -24.9 % | **CHANGED** |
| fight:collections_agent@t4 | died | 0.050 | 0.750 | +0.700 | [+0.500, +0.850] | +1400.0 % | **CHANGED** |
| fight:collections_agent@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | hp_lost | 43.150 | 57.900 | +14.750 | [+10.550, +18.600] | +34.2 % | **CHANGED** |
| fight:collections_agent@t4 | intake | 35.800 | 52.350 | +16.550 | [+12.100, +20.800] | +46.2 % | **CHANGED** |
| fight:collections_agent@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:collections_agent@t4 | resistance_absorbed | 5.450 | 4.500 | -0.950 | [-1.850, +0.000] | -17.4 % | noise |
| fight:collections_agent@t4 | taken_per_turn | 4.375 | 7.136 | +2.761 | [+1.696, +3.916] | +63.1 % | **CHANGED** |
| fight:collections_agent@t4 | turns | 10.000 | 9.100 | -0.900 | [-2.100, +0.250] | -9.0 % | noise |
| fight:collections_agent@t4 | turns_both_share | 0.415 | 0.330 | -0.086 | [-0.154, -0.020] | -20.6 % | **CHANGED** |
| fight:collections_agent@t4 | won | 0.950 | 0.250 | -0.700 | [-0.850, -0.500] | -73.7 % | **CHANGED** |
| fight:compliance_officer@t1 | dealt_per_turn | 17.919 | 13.554 | -4.365 | [-6.924, -1.805] | -24.4 % | **CHANGED** |
| fight:compliance_officer@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | hp_lost | 4.800 | 10.600 | +5.800 | [+3.247, +8.400] | +120.8 % | **CHANGED** |
| fight:compliance_officer@t1 | intake | 4.200 | 10.150 | +5.950 | [+3.400, +8.600] | +141.7 % | **CHANGED** |
| fight:compliance_officer@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t1 | resistance_absorbed | 2.800 | 3.800 | +1.000 | [-0.050, +2.152] | +35.7 % | noise |
| fight:compliance_officer@t1 | taken_per_turn | 1.820 | 2.545 | +0.725 | [-0.004, +1.454] | +39.8 % | noise |
| fight:compliance_officer@t1 | turns | 2.950 | 4.300 | +1.350 | [+0.700, +2.000] | +45.8 % | **CHANGED** |
| fight:compliance_officer@t1 | turns_both_share | 0.371 | 0.348 | -0.023 | [-0.135, +0.090] | -6.1 % | noise |
| fight:compliance_officer@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t2 | dealt_per_turn | 15.855 | 12.842 | -3.013 | [-4.929, -1.163] | -19.0 % | **CHANGED** |
| fight:compliance_officer@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | hp_lost | 9.200 | 19.550 | +10.350 | [+6.300, +14.700] | +112.5 % | **CHANGED** |
| fight:compliance_officer@t2 | intake | 7.850 | 17.900 | +10.050 | [+6.000, +14.300] | +128.0 % | **CHANGED** |
| fight:compliance_officer@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t2 | resistance_absorbed | 4.400 | 4.800 | +0.400 | [-0.850, +1.650] | +9.1 % | noise |
| fight:compliance_officer@t2 | taken_per_turn | 1.873 | 2.932 | +1.059 | [+0.378, +1.755] | +56.6 % | **CHANGED** |
| fight:compliance_officer@t2 | turns | 5.450 | 6.550 | +1.100 | [+0.250, +1.900] | +20.2 % | **CHANGED** |
| fight:compliance_officer@t2 | turns_both_share | 0.323 | 0.282 | -0.041 | [-0.118, +0.034] | -12.7 % | noise |
| fight:compliance_officer@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:compliance_officer@t3 | dealt_per_turn | 15.041 | 11.985 | -3.057 | [-4.507, -1.598] | -20.3 % | **CHANGED** |
| fight:compliance_officer@t3 | died | 0.000 | 0.400 | +0.400 | [+0.200, +0.600] | - | **CHANGED** |
| fight:compliance_officer@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | hp_lost | 19.200 | 44.300 | +25.100 | [+17.300, +32.550] | +130.7 % | **CHANGED** |
| fight:compliance_officer@t3 | intake | 15.600 | 40.100 | +24.500 | [+17.150, +31.952] | +157.1 % | **CHANGED** |
| fight:compliance_officer@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t3 | resistance_absorbed | 8.600 | 9.050 | +0.450 | [-1.350, +2.200] | +5.2 % | noise |
| fight:compliance_officer@t3 | taken_per_turn | 2.277 | 4.179 | +1.902 | [+1.068, +2.722] | +83.5 % | **CHANGED** |
| fight:compliance_officer@t3 | turns | 8.850 | 10.850 | +2.000 | [+0.900, +3.050] | +22.6 % | **CHANGED** |
| fight:compliance_officer@t3 | turns_both_share | 0.353 | 0.327 | -0.025 | [-0.100, +0.049] | -7.2 % | noise |
| fight:compliance_officer@t3 | won | 1.000 | 0.600 | -0.400 | [-0.600, -0.250] | -40.0 % | **CHANGED** |
| fight:compliance_officer@t4 | dealt_per_turn | 15.738 | 11.430 | -4.308 | [-5.656, -2.928] | -27.4 % | **CHANGED** |
| fight:compliance_officer@t4 | died | 0.050 | 0.850 | +0.800 | [+0.650, +0.950] | +1600.0 % | **CHANGED** |
| fight:compliance_officer@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | hp_lost | 39.800 | 59.300 | +19.500 | [+15.000, +24.200] | +49.0 % | **CHANGED** |
| fight:compliance_officer@t4 | intake | 32.300 | 55.200 | +22.900 | [+17.750, +28.100] | +70.9 % | **CHANGED** |
| fight:compliance_officer@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:compliance_officer@t4 | resistance_absorbed | 12.000 | 10.200 | -1.800 | [-3.850, +0.100] | -15.0 % | noise |
| fight:compliance_officer@t4 | taken_per_turn | 3.143 | 5.438 | +2.295 | [+1.557, +3.015] | +73.0 % | **CHANGED** |
| fight:compliance_officer@t4 | turns | 13.300 | 11.750 | -1.550 | [-2.950, -0.100] | -11.7 % | **CHANGED** |
| fight:compliance_officer@t4 | turns_both_share | 0.356 | 0.294 | -0.062 | [-0.122, -0.003] | -17.5 % | **CHANGED** |
| fight:compliance_officer@t4 | won | 0.950 | 0.150 | -0.800 | [-0.950, -0.650] | -84.2 % | **CHANGED** |
| fight:dosage_dispenser@t1 | dealt_per_turn | 16.468 | 12.889 | -3.579 | [-5.479, -1.363] | -21.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | hp_lost | 0.150 | 2.100 | +1.950 | [+0.600, +3.750] | +1300.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | intake | 0.000 | 1.350 | +1.350 | [+0.450, +2.550] | - | **CHANGED** |
| fight:dosage_dispenser@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t1 | resistance_absorbed | 0.850 | 1.050 | +0.200 | [-0.250, +0.600] | +23.5 % | noise |
| fight:dosage_dispenser@t1 | taken_per_turn | 0.050 | 0.505 | +0.455 | [+0.173, +0.772] | +910.0 % | **CHANGED** |
| fight:dosage_dispenser@t1 | turns | 2.450 | 3.350 | +0.900 | [+0.400, +1.400] | +36.7 % | **CHANGED** |
| fight:dosage_dispenser@t1 | turns_both_share | 0.267 | 0.218 | -0.048 | [-0.186, +0.089] | -18.1 % | noise |
| fight:dosage_dispenser@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t2 | dealt_per_turn | 17.840 | 13.993 | -3.848 | [-5.721, -1.974] | -21.6 % | **CHANGED** |
| fight:dosage_dispenser@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | hp_lost | 1.550 | 4.900 | +3.350 | [+1.150, +5.750] | +216.1 % | **CHANGED** |
| fight:dosage_dispenser@t2 | intake | 0.200 | 2.800 | +2.600 | [+1.000, +4.400] | +1300.0 % | **CHANGED** |
| fight:dosage_dispenser@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t2 | resistance_absorbed | 1.300 | 1.750 | +0.450 | [-0.100, +1.050] | +34.6 % | noise |
| fight:dosage_dispenser@t2 | taken_per_turn | 0.424 | 0.997 | +0.573 | [+0.153, +1.012] | +135.1 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns | 3.600 | 4.700 | +1.100 | [+0.500, +1.700] | +30.6 % | **CHANGED** |
| fight:dosage_dispenser@t2 | turns_both_share | 0.276 | 0.293 | +0.017 | [-0.106, +0.136] | +6.2 % | noise |
| fight:dosage_dispenser@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t3 | dealt_per_turn | 17.935 | 13.823 | -4.112 | [-6.023, -2.307] | -22.9 % | **CHANGED** |
| fight:dosage_dispenser@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | hp_lost | 3.650 | 11.600 | +7.950 | [+4.050, +12.700] | +217.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | intake | 0.500 | 5.750 | +5.250 | [+2.250, +8.750] | +1050.0 % | **CHANGED** |
| fight:dosage_dispenser@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t3 | resistance_absorbed | 2.100 | 2.550 | +0.450 | [-0.200, +1.100] | +21.4 % | noise |
| fight:dosage_dispenser@t3 | taken_per_turn | 0.639 | 1.567 | +0.928 | [+0.394, +1.477] | +145.3 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns | 5.700 | 7.400 | +1.700 | [+0.950, +2.502] | +29.8 % | **CHANGED** |
| fight:dosage_dispenser@t3 | turns_both_share | 0.282 | 0.255 | -0.027 | [-0.121, +0.064] | -9.5 % | noise |
| fight:dosage_dispenser@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:dosage_dispenser@t4 | dealt_per_turn | 19.386 | 14.665 | -4.721 | [-6.604, -2.757] | -24.4 % | **CHANGED** |
| fight:dosage_dispenser@t4 | died | 0.000 | 0.050 | +0.050 | [+0.000, +0.150] | - | noise |
| fight:dosage_dispenser@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | hp_lost | 7.800 | 23.250 | +15.450 | [+9.997, +21.500] | +198.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | intake | 1.050 | 11.100 | +10.050 | [+5.450, +15.050] | +957.1 % | **CHANGED** |
| fight:dosage_dispenser@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:dosage_dispenser@t4 | resistance_absorbed | 3.650 | 4.500 | +0.850 | [-0.050, +1.700] | +23.3 % | noise |
| fight:dosage_dispenser@t4 | taken_per_turn | 0.981 | 2.107 | +1.125 | [+0.632, +1.698] | +114.6 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns | 8.300 | 11.000 | +2.700 | [+1.550, +3.850] | +32.5 % | **CHANGED** |
| fight:dosage_dispenser@t4 | turns_both_share | 0.354 | 0.276 | -0.078 | [-0.161, +0.007] | -22.1 % | noise |
| fight:dosage_dispenser@t4 | won | 1.000 | 0.950 | -0.050 | [-0.150, +0.000] | -5.0 % | noise |
| fight:recall_unit@t1 | dealt_per_turn | 17.702 | 12.178 | -5.524 | [-7.387, -3.664] | -31.2 % | **CHANGED** |
| fight:recall_unit@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t1 | enrage_step | 0.150 | 0.900 | +0.750 | [+0.450, +1.050] | +500.0 % | **CHANGED** |
| fight:recall_unit@t1 | hp_lost | 17.700 | 30.100 | +12.400 | [+5.997, +18.902] | +70.1 % | **CHANGED** |
| fight:recall_unit@t1 | intake | 15.600 | 28.000 | +12.400 | [+6.100, +18.850] | +79.5 % | **CHANGED** |
| fight:recall_unit@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t1 | resistance_absorbed | 5.400 | 9.350 | +3.950 | [+1.800, +5.950] | +73.1 % | **CHANGED** |
| fight:recall_unit@t1 | taken_per_turn | 2.957 | 3.183 | +0.226 | [-0.604, +1.018] | +7.6 % | noise |
| fight:recall_unit@t1 | turns | 6.200 | 9.550 | +3.350 | [+2.200, +4.500] | +54.0 % | **CHANGED** |
| fight:recall_unit@t1 | turns_both_share | 0.216 | 0.232 | +0.016 | [-0.042, +0.077] | +7.4 % | noise |
| fight:recall_unit@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t2 | dealt_per_turn | 15.864 | 10.902 | -4.962 | [-6.184, -3.728] | -31.3 % | **CHANGED** |
| fight:recall_unit@t2 | died | 0.100 | 0.650 | +0.550 | [+0.350, +0.750] | +550.0 % | **CHANGED** |
| fight:recall_unit@t2 | enrage_step | 1.100 | 1.600 | +0.500 | [+0.250, +0.750] | +45.5 % | **CHANGED** |
| fight:recall_unit@t2 | hp_lost | 36.350 | 55.200 | +18.850 | [+12.500, +24.800] | +51.9 % | **CHANGED** |
| fight:recall_unit@t2 | intake | 30.500 | 49.900 | +19.400 | [+12.750, +26.250] | +63.6 % | **CHANGED** |
| fight:recall_unit@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t2 | resistance_absorbed | 10.500 | 14.650 | +4.150 | [+1.550, +6.850] | +39.5 % | **CHANGED** |
| fight:recall_unit@t2 | taken_per_turn | 3.508 | 4.220 | +0.712 | [-0.007, +1.411] | +20.3 % | noise |
| fight:recall_unit@t2 | turns | 10.750 | 13.350 | +2.600 | [+1.700, +3.500] | +24.2 % | **CHANGED** |
| fight:recall_unit@t2 | turns_both_share | 0.234 | 0.263 | +0.029 | [-0.028, +0.090] | +12.4 % | noise |
| fight:recall_unit@t2 | won | 0.900 | 0.350 | -0.550 | [-0.750, -0.350] | -61.1 % | **CHANGED** |
| fight:recall_unit@t3 | dealt_per_turn | 14.155 | 10.412 | -3.743 | [-5.666, -2.036] | -26.4 % | **CHANGED** |
| fight:recall_unit@t3 | died | 0.750 | 1.000 | +0.250 | [+0.100, +0.400] | +33.3 % | **CHANGED** |
| fight:recall_unit@t3 | enrage_step | 2.300 | 1.500 | -0.800 | [-1.250, -0.350] | -34.8 % | **CHANGED** |
| fight:recall_unit@t3 | hp_lost | 57.750 | 60.000 | +2.250 | [+0.700, +4.200] | +3.9 % | **CHANGED** |
| fight:recall_unit@t3 | intake | 49.800 | 56.100 | +6.300 | [+2.900, +9.800] | +12.7 % | **CHANGED** |
| fight:recall_unit@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t3 | resistance_absorbed | 17.100 | 12.900 | -4.200 | [-7.800, -0.400] | -24.6 % | **CHANGED** |
| fight:recall_unit@t3 | taken_per_turn | 3.933 | 5.392 | +1.459 | [+0.504, +2.448] | +37.1 % | **CHANGED** |
| fight:recall_unit@t3 | turns | 16.650 | 12.450 | -4.200 | [-6.650, -1.800] | -25.2 % | **CHANGED** |
| fight:recall_unit@t3 | turns_both_share | 0.219 | 0.250 | +0.031 | [-0.033, +0.095] | +13.9 % | noise |
| fight:recall_unit@t3 | won | 0.250 | 0.000 | -0.250 | [-0.400, -0.100] | -100.0 % | **CHANGED** |
| fight:recall_unit@t4 | dealt_per_turn | 13.893 | 9.301 | -4.592 | [-6.525, -2.567] | -33.1 % | **CHANGED** |
| fight:recall_unit@t4 | died | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t4 | enrage_step | 2.300 | 1.050 | -1.250 | [-1.800, -0.700] | -54.3 % | **CHANGED** |
| fight:recall_unit@t4 | hp_lost | 60.000 | 60.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:recall_unit@t4 | intake | 51.900 | 57.600 | +5.700 | [+2.850, +8.850] | +11.0 % | **CHANGED** |
| fight:recall_unit@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:recall_unit@t4 | resistance_absorbed | 17.850 | 9.550 | -8.300 | [-13.400, -3.100] | -46.5 % | **CHANGED** |
| fight:recall_unit@t4 | taken_per_turn | 5.106 | 7.156 | +2.050 | [-0.063, +3.984] | +40.1 % | noise |
| fight:recall_unit@t4 | turns | 16.000 | 10.300 | -5.700 | [-8.603, -2.750] | -35.6 % | **CHANGED** |
| fight:recall_unit@t4 | turns_both_share | 0.208 | 0.162 | -0.046 | [-0.113, +0.022] | -22.3 % | noise |
| fight:recall_unit@t4 | won | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | dealt_per_turn | 17.137 | 12.912 | -4.226 | [-6.457, -1.964] | -24.7 % | **CHANGED** |
| fight:triage_unit@t1 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | hp_lost | 0.900 | 1.500 | +0.600 | [-0.450, +1.650] | +66.7 % | noise |
| fight:triage_unit@t1 | intake | 0.450 | 1.350 | +0.900 | [+0.000, +1.950] | +200.0 % | noise |
| fight:triage_unit@t1 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t1 | resistance_absorbed | 1.500 | 1.600 | +0.100 | [-0.300, +0.500] | +6.7 % | noise |
| fight:triage_unit@t1 | taken_per_turn | 0.400 | 0.417 | +0.017 | [-0.350, +0.385] | +4.4 % | noise |
| fight:triage_unit@t1 | turns | 2.800 | 3.950 | +1.150 | [+0.600, +1.750] | +41.1 % | **CHANGED** |
| fight:triage_unit@t1 | turns_both_share | 0.447 | 0.302 | -0.146 | [-0.267, -0.023] | -32.6 % | **CHANGED** |
| fight:triage_unit@t1 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t2 | dealt_per_turn | 19.320 | 12.868 | -6.452 | [-8.633, -4.205] | -33.4 % | **CHANGED** |
| fight:triage_unit@t2 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | hp_lost | 2.500 | 5.100 | +2.600 | [+0.047, +5.750] | +104.0 % | **CHANGED** |
| fight:triage_unit@t2 | intake | 1.000 | 3.450 | +2.450 | [+0.000, +5.400] | +245.0 % | noise |
| fight:triage_unit@t2 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t2 | resistance_absorbed | 2.150 | 2.950 | +0.800 | [+0.200, +1.450] | +37.2 % | **CHANGED** |
| fight:triage_unit@t2 | taken_per_turn | 0.610 | 0.769 | +0.159 | [-0.236, +0.596] | +26.0 % | noise |
| fight:triage_unit@t2 | turns | 4.000 | 6.350 | +2.350 | [+1.500, +3.200] | +58.7 % | **CHANGED** |
| fight:triage_unit@t2 | turns_both_share | 0.473 | 0.352 | -0.120 | [-0.243, -0.001] | -25.4 % | **CHANGED** |
| fight:triage_unit@t2 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t3 | dealt_per_turn | 16.372 | 12.346 | -4.026 | [-5.860, -2.196] | -24.6 % | **CHANGED** |
| fight:triage_unit@t3 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | hp_lost | 6.100 | 11.350 | +5.250 | [+1.050, +9.850] | +86.1 % | **CHANGED** |
| fight:triage_unit@t3 | intake | 2.500 | 6.850 | +4.350 | [+0.850, +8.050] | +174.0 % | **CHANGED** |
| fight:triage_unit@t3 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t3 | resistance_absorbed | 4.200 | 4.350 | +0.150 | [-0.800, +1.100] | +3.6 % | noise |
| fight:triage_unit@t3 | taken_per_turn | 0.831 | 0.999 | +0.168 | [-0.176, +0.535] | +20.3 % | noise |
| fight:triage_unit@t3 | turns | 7.450 | 10.600 | +3.150 | [+1.750, +4.550] | +42.3 % | **CHANGED** |
| fight:triage_unit@t3 | turns_both_share | 0.449 | 0.310 | -0.139 | [-0.236, -0.039] | -30.9 % | **CHANGED** |
| fight:triage_unit@t3 | won | 1.000 | 1.000 | +0.000 | [+0.000, +0.000] | +0.0 % | noise |
| fight:triage_unit@t4 | dealt_per_turn | 14.656 | 10.294 | -4.362 | [-5.861, -2.789] | -29.8 % | **CHANGED** |
| fight:triage_unit@t4 | died | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | enrage_step | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | hp_lost | 12.200 | 29.450 | +17.250 | [+11.797, +22.900] | +141.4 % | **CHANGED** |
| fight:triage_unit@t4 | intake | 3.800 | 16.700 | +12.900 | [+7.700, +18.605] | +339.5 % | **CHANGED** |
| fight:triage_unit@t4 | parked | 0.000 | 0.000 | +0.000 | [+0.000, +0.000] | - | noise |
| fight:triage_unit@t4 | resistance_absorbed | 7.050 | 9.700 | +2.650 | [+1.500, +3.800] | +37.6 % | **CHANGED** |
| fight:triage_unit@t4 | taken_per_turn | 0.962 | 1.472 | +0.511 | [+0.214, +0.815] | +53.1 % | **CHANGED** |
| fight:triage_unit@t4 | turns | 13.300 | 20.400 | +7.100 | [+4.950, +9.250] | +53.4 % | **CHANGED** |
| fight:triage_unit@t4 | turns_both_share | 0.403 | 0.349 | -0.053 | [-0.128, +0.021] | -13.3 % | noise |
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
| B fight:account_manager@t1 | 20 | 0.24 | 3.94 | 0 | 14.4 | 36.5 | 10.0 | 2 | 0.24 |
| B fight:account_manager@t2 | 20 | 0.12 | 8.16 | 0 | 9.9 | 46.8 | 13.9 | 2 | 0.25 |
| B fight:account_manager@t3 | 20 | 0.12 | 14.75 | 0 | 2.2 | 45.2 | 15.2 | 3 | 0.21 |
| B fight:account_manager@t4 | 20 | - | - | 0 | 0.0 | 49.5 | 13.3 | 3 | 0.22 |
| B fight:billing_daemon@t1 | 20 | 0.55 | 3.45 | 0 | 0.0 | 8.6 | 2.0 | 0 | 0.42 |
| B fight:billing_daemon@t2 | 20 | 0.35 | 5.70 | 0 | 0.0 | 14.1 | 2.7 | 0 | 0.37 |
| B fight:billing_daemon@t3 | 20 | 0.00 | 9.53 | 0 | 0.0 | 31.2 | 5.5 | 0 | 0.42 |
| B fight:billing_daemon@t4 | 20 | 0.00 | 13.83 | 0 | 0.0 | 51.2 | 6.6 | 0 | 0.38 |
| B fight:care_swarm@t1 | 20 | 0.50 | 3.90 | 3 | 0.0 | 17.3 | 1.4 | 0 | 0.22 |
| B fight:care_swarm@t2 | 20 | 0.33 | 4.73 | 3 | 0.0 | 36.9 | 2.3 | 0 | 0.25 |
| B fight:care_swarm@t3 | 20 | 0.00 | 7.50 | 5 | 0.0 | 52.6 | 2.9 | 0 | 0.24 |
| B fight:care_swarm@t4 | 20 | - | - | 3 | 0.0 | 59.1 | 2.0 | 0 | 0.27 |
| B fight:claims_adjuster@t1 | 20 | 0.55 | 4.50 | 0 | 0.0 | 26.8 | 4.8 | 1 | 0.30 |
| B fight:claims_adjuster@t2 | 20 | 0.00 | 6.10 | 0 | 0.0 | 43.1 | 7.8 | 1 | 0.32 |
| B fight:claims_adjuster@t3 | 20 | 0.00 | 10.50 | 0 | 0.0 | 53.4 | 7.1 | 2 | 0.29 |
| B fight:claims_adjuster@t4 | 20 | - | - | 0 | 0.0 | 56.7 | 6.3 | 2 | 0.26 |
| B fight:collections_agent@t1 | 20 | 0.65 | 3.75 | 0 | 0.0 | 9.9 | 1.6 | 0 | 0.28 |
| B fight:collections_agent@t2 | 20 | 0.40 | 5.40 | 0 | 0.0 | 17.9 | 2.5 | 0 | 0.26 |
| B fight:collections_agent@t3 | 20 | 0.00 | 7.77 | 0 | 0.0 | 36.8 | 3.9 | 0 | 0.29 |
| B fight:collections_agent@t4 | 20 | 0.00 | 11.20 | 0 | 0.0 | 52.4 | 4.5 | 0 | 0.34 |
| B fight:compliance_officer@t1 | 20 | 0.50 | 4.30 | 0 | 0.0 | 10.2 | 3.8 | 0 | 0.34 |
| B fight:compliance_officer@t2 | 20 | 0.05 | 6.55 | 0 | 0.0 | 17.9 | 4.8 | 0 | 0.28 |
| B fight:compliance_officer@t3 | 20 | 0.00 | 10.92 | 0 | 0.0 | 40.1 | 9.1 | 0 | 0.32 |
| B fight:compliance_officer@t4 | 20 | 0.00 | 15.33 | 0 | 0.0 | 55.2 | 10.2 | 0 | 0.31 |
| B fight:dosage_dispenser@t1 | 20 | 0.55 | 3.35 | 0 | 0.0 | 1.4 | 1.1 | 0 | 0.21 |
| B fight:dosage_dispenser@t2 | 20 | 0.60 | 4.70 | 0 | 0.0 | 2.8 | 1.8 | 0 | 0.29 |
| B fight:dosage_dispenser@t3 | 20 | 0.00 | 7.40 | 0 | 0.0 | 5.8 | 2.5 | 0 | 0.24 |
| B fight:dosage_dispenser@t4 | 20 | 0.00 | 11.05 | 0 | 0.0 | 11.1 | 4.5 | 0 | 0.26 |
| B fight:recall_unit@t1 | 20 | 0.00 | 9.55 | 0 | 0.0 | 28.0 | 9.3 | 2 | 0.23 |
| B fight:recall_unit@t2 | 20 | 0.00 | 12.57 | 0 | 0.0 | 49.9 | 14.7 | 3 | 0.26 |
| B fight:recall_unit@t3 | 20 | - | - | 0 | 0.0 | 56.1 | 12.9 | 3 | 0.27 |
| B fight:recall_unit@t4 | 20 | - | - | 0 | 0.0 | 57.6 | 9.6 | 3 | 0.17 |
| B fight:triage_unit@t1 | 20 | 0.55 | 3.95 | 3 | 0.0 | 1.4 | 1.6 | 0 | 0.28 |
| B fight:triage_unit@t2 | 20 | 0.20 | 6.35 | 5 | 0.0 | 3.5 | 3.0 | 0 | 0.33 |
| B fight:triage_unit@t3 | 20 | 0.00 | 10.60 | 7 | 0.0 | 6.8 | 4.3 | 0 | 0.29 |
| B fight:triage_unit@t4 | 20 | 0.00 | 20.40 | 11 | 0.0 | 16.7 | 9.7 | 0 | 0.33 |

