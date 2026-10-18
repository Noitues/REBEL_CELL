# Balance comparison: camp_rookie25

- A: `camp_base.json` (overrides: none)
- B: `camp_rookie25.json` (overrides: config.rookie_cost=25)
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 80 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 21.850 | -0.100 | [-6.550, +6.350] | -0.5 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 92.300 | +0.600 | [-7.750, +8.953] | +0.7 % | noise |
| campaign@ice0 | minutes | 745.530 | 740.520 | -5.010 | [-166.533, +165.267] | -0.7 % | noise |
| campaign@ice0 | raids | 6.000 | 6.050 | +0.050 | [-0.800, +0.850] | +0.8 % | noise |
| campaign@ice0 | recruits | 21.400 | 21.300 | -0.100 | [-6.500, +6.500] | -0.5 % | noise |
| campaign@ice0 | runs | 47.700 | 47.350 | -0.350 | [-11.750, +10.453] | -0.7 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1261.250 | -15.050 | [-292.225, +260.822] | -1.2 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 121.350 | -13.050 | [-54.815, +31.405] | -9.7 % | noise |
| campaign@ice0 | turns | 1236.100 | 1233.550 | -2.550 | [-302.652, +281.702] | -0.2 % | noise |
| campaign@ice0 | won | 0.200 | 0.150 | -0.050 | [-0.250, +0.150] | -25.0 % | noise |

