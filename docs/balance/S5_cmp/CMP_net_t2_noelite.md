# Balance comparison: net_t2_noelite

- A: `net_t2_base.json` (overrides: none)
- B: `net_t2_noelite.json` (overrides: config.map_elites_per_layer=0)
- mode netrun; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 11 of 24 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| netrun@t2 | completed | 0.000 | 0.400 | +0.400 | [+0.250, +0.600] | - | **CHANGED** |
| netrun@t2 | died | 1.000 | 0.600 | -0.400 | [-0.550, -0.200] | -40.0 % | **CHANGED** |
| netrun@t2 | fight_hp_lost.elite.t2 | 27.711 | 20.625 | -7.086 | [-12.731, -1.507] | -25.6 % | **CHANGED** |
| netrun@t2 | fight_hp_lost.mini_boss.t2 | 8.400 | 24.846 | +16.446 | [+9.245, +23.585] | +195.8 % | **CHANGED** |
| netrun@t2 | fight_turns.mini_boss.t2 | 5.400 | 12.000 | +6.600 | [+4.169, +9.108] | +122.2 % | **CHANGED** |
| netrun@t2 | fight_win.mini_boss.t2 | 0.000 | 0.615 | +0.615 | [+0.385, +0.846] | - | **CHANGED** |
| netrun@t2 | heals_available | 2.300 | 3.300 | +1.000 | [+0.650, +1.300] | +43.5 % | **CHANGED** |
| netrun@t2 | hp_frac_arrival.t2.l5 | 0.265 | 0.682 | +0.417 | [+0.268, +0.553] | +157.6 % | **CHANGED** |
| netrun@t2 | hp_frac_arrival.t2.l6 | 0.217 | 0.647 | +0.431 | [+0.285, +0.572] | +198.8 % | **CHANGED** |
| netrun@t2 | hp_frac_arrival.t2.l7 | 0.140 | 0.556 | +0.416 | [+0.279, +0.560] | +297.5 % | **CHANGED** |
| netrun@t2 | layers | 5.000 | 5.950 | +0.950 | [+0.200, +1.700] | +19.0 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| netrun@t2 | died | 1.000 | 0.600 | -0.400 | [-0.550, -0.200] | -40.0 % | **CHANGED** |
| netrun@t2 | hp_end_frac | 0.294 | 0.322 | +0.028 | [-0.087, +0.148] | +9.4 % | noise |
| netrun@t2 | layers | 5.000 | 5.950 | +0.950 | [+0.200, +1.700] | +19.0 % | **CHANGED** |

