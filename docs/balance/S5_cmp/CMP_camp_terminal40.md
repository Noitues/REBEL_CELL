# Balance comparison: camp_terminal40

- A: `camp_base.json` (overrides: none)
- B: `camp_terminal40.json` (overrides: config.map_terminal_ratio=0.4)
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 2 of 80 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | heals_available_per_run | 2.024 | 3.070 | +1.046 | [+0.927, +1.161] | +51.7 % | **CHANGED** |
| campaign@ice0 | heals_used_per_run | 0.438 | 0.677 | +0.239 | [+0.154, +0.309] | +54.6 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 23.050 | +1.100 | [-5.300, +7.202] | +5.0 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 92.100 | +0.400 | [-9.003, +9.405] | +0.4 % | noise |
| campaign@ice0 | minutes | 745.530 | 777.750 | +32.220 | [-130.386, +197.263] | +4.3 % | noise |
| campaign@ice0 | raids | 6.000 | 6.150 | +0.150 | [-0.650, +1.000] | +2.5 % | noise |
| campaign@ice0 | recruits | 21.400 | 22.650 | +1.250 | [-5.053, +7.350] | +5.8 % | noise |
| campaign@ice0 | runs | 47.700 | 49.800 | +2.100 | [-8.653, +12.653] | +4.4 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1335.700 | +59.400 | [-212.502, +328.582] | +4.7 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 131.550 | -2.850 | [-45.752, +43.710] | -2.1 % | noise |
| campaign@ice0 | turns | 1236.100 | 1248.450 | +12.350 | [-281.800, +270.267] | +1.0 % | noise |
| campaign@ice0 | won | 0.200 | 0.150 | -0.050 | [-0.250, +0.150] | -25.0 % | noise |

