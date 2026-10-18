# Balance comparison: boss_hp050

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_hp050.json` (overrides: renewal_engine.hp*=0.5)
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 18.830 | -1.131 | [-6.906, +4.513] | -5.7 % | noise |
| boss@ice0 | died | 0.895 | 0.842 | -0.053 | [-0.211, +0.105] | -5.9 % | noise |
| boss@ice0 | enrage_step | 2.842 | 2.263 | -0.579 | [-2.000, +0.895] | -20.4 % | noise |
| boss@ice0 | hp_lost | 54.316 | 51.895 | -2.421 | [-11.845, +7.055] | -4.5 % | noise |
| boss@ice0 | intake | 55.684 | 55.474 | -0.211 | [-12.053, +11.792] | -0.4 % | noise |
| boss@ice0 | parked | 6.684 | 10.632 | +3.947 | [-5.632, +13.263] | +59.1 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 20.684 | -4.158 | [-13.374, +5.161] | -16.7 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.143 | +0.038 | [-2.903, +3.223] | +0.6 % | noise |
| boss@ice0 | turns | 20.895 | 18.211 | -2.684 | [-10.632, +4.687] | -12.8 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.245 | +0.001 | [-0.054, +0.054] | +0.3 % | noise |
| boss@ice0 | won | 0.053 | 0.158 | +0.105 | [-0.053, +0.263] | +200.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 12.12 | 24 | 10.6 | 55.5 | 20.7 | 9 | 0.23 |

