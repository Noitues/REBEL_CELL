# Balance comparison: camp_deathheat5

- A: `camp_base.json` (overrides: none)
- B: `camp_deathheat5.json` (overrides: config.death_heat_base=5)
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 1 of 80 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | raids_from_heat_actions | 1.950 | 2.500 | +0.550 | [+0.200, +0.950] | +28.2 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 23.200 | +1.250 | [-5.100, +7.352] | +5.7 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 93.900 | +2.200 | [-6.300, +10.703] | +2.4 % | noise |
| campaign@ice0 | minutes | 745.530 | 786.720 | +41.190 | [-119.268, +197.618] | +5.5 % | noise |
| campaign@ice0 | raids | 6.000 | 6.000 | +0.000 | [-0.750, +0.750] | +0.0 % | noise |
| campaign@ice0 | recruits | 21.400 | 22.600 | +1.200 | [-4.800, +7.200] | +5.6 % | noise |
| campaign@ice0 | runs | 47.700 | 50.450 | +2.750 | [-7.100, +13.150] | +5.8 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1346.750 | +70.450 | [-168.923, +324.953] | +5.5 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 138.050 | +3.650 | [-45.358, +56.255] | +2.7 % | noise |
| campaign@ice0 | turns | 1236.100 | 1318.450 | +82.350 | [-198.425, +358.317] | +6.7 % | noise |
| campaign@ice0 | won | 0.200 | 0.200 | +0.000 | [-0.200, +0.200] | +0.0 % | noise |

