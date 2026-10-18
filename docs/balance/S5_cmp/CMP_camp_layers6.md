# Balance comparison: camp_layers6

- A: `camp_base.json` (overrides: none)
- B: `camp_layers6.json` (overrides: config.map_layers=6, config.rack_layers=[4,6])
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 19 of 77 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | completed | 24.400 | 30.550 | +6.150 | [+1.500, +10.655] | +25.2 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.boss.t4 | 44.435 | 53.452 | +9.017 | [+0.822, +17.175] | +20.3 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.elite.t2 | 11.525 | 13.364 | +1.839 | [+0.337, +3.412] | +16.0 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.elite.t3 | 11.561 | 14.614 | +3.054 | [+0.172, +5.666] | +26.4 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.enemy.t1 | 3.504 | 4.327 | +0.823 | [+0.353, +1.333] | +23.5 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.enemy.t2 | 3.773 | 4.701 | +0.928 | [+0.377, +1.508] | +24.6 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.enemy.t3 | 4.266 | 5.543 | +1.277 | [+0.020, +2.526] | +29.9 % | **CHANGED** |
| campaign@ice0 | fight_hp_lost.mini_boss.t1 | 11.203 | 13.838 | +2.635 | [+0.581, +4.711] | +23.5 % | **CHANGED** |
| campaign@ice0 | fight_turns.elite.t2 | 4.751 | 5.060 | +0.310 | [+0.005, +0.620] | +6.5 % | **CHANGED** |
| campaign@ice0 | fight_win.elite.t3 | 0.859 | 0.788 | -0.071 | [-0.131, -0.013] | -8.3 % | **CHANGED** |
| campaign@ice0 | heal_hp_per_run | 1.520 | 0.839 | -0.681 | [-1.215, -0.236] | -44.8 % | **CHANGED** |
| campaign@ice0 | heals_available_per_run | 2.024 | 1.711 | -0.313 | [-0.378, -0.246] | -15.4 % | **CHANGED** |
| campaign@ice0 | heals_used_per_run | 0.438 | 0.326 | -0.112 | [-0.193, -0.045] | -25.7 % | **CHANGED** |
| campaign@ice0 | heat_at_breach | 76.211 | 92.263 | +16.053 | [+4.261, +27.737] | +21.1 % | **CHANGED** |
| campaign@ice0 | heat_end | 81.900 | 96.200 | +14.300 | [+2.750, +25.953] | +17.5 % | **CHANGED** |
| campaign@ice0 | hp_frac_arrival.t1.l2 | 0.924 | 0.909 | -0.015 | [-0.027, -0.003] | -1.6 % | **CHANGED** |
| campaign@ice0 | hp_frac_arrival.t1.l3 | 0.862 | 0.838 | -0.024 | [-0.047, -0.002] | -2.8 % | **CHANGED** |
| campaign@ice0 | hp_frac_arrival.t2.l6 | 0.627 | 0.579 | -0.047 | [-0.093, -0.003] | -7.6 % | **CHANGED** |
| campaign@ice0 | layers_per_run | 6.184 | 5.314 | -0.870 | [-1.039, -0.700] | -14.1 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 22.850 | +0.900 | [-4.100, +6.150] | +4.1 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 96.200 | +4.500 | [-2.950, +12.050] | +4.9 % | noise |
| campaign@ice0 | minutes | 745.530 | 852.810 | +107.280 | [-42.971, +255.831] | +14.4 % | noise |
| campaign@ice0 | raids | 6.000 | 6.000 | +0.000 | [-0.750, +0.800] | +0.0 % | noise |
| campaign@ice0 | recruits | 21.400 | 22.450 | +1.050 | [-4.203, +6.252] | +4.9 % | noise |
| campaign@ice0 | runs | 47.700 | 54.850 | +7.150 | [-2.600, +16.900] | +15.0 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1430.850 | +154.550 | [-74.327, +393.635] | +12.1 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 125.950 | -8.450 | [-47.255, +26.352] | -6.3 % | noise |
| campaign@ice0 | turns | 1236.100 | 1304.450 | +68.350 | [-192.523, +316.522] | +5.5 % | noise |
| campaign@ice0 | won | 0.200 | 0.050 | -0.150 | [-0.300, +0.000] | -75.0 % | noise |

