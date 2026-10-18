# Balance comparison: boss_enrage14

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_enrage14.json` (overrides: config.enrage_start_turn_by_class=[0,8,10,14])
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 21.084 | +1.123 | [-5.237, +7.315] | +5.6 % | noise |
| boss@ice0 | died | 0.895 | 0.842 | -0.053 | [-0.211, +0.105] | -5.9 % | noise |
| boss@ice0 | enrage_step | 2.842 | 2.526 | -0.316 | [-1.842, +1.263] | -11.1 % | noise |
| boss@ice0 | hp_lost | 54.316 | 52.842 | -1.474 | [-10.326, +8.000] | -2.7 % | noise |
| boss@ice0 | intake | 55.684 | 56.316 | +0.632 | [-12.421, +13.684] | +1.1 % | noise |
| boss@ice0 | parked | 6.684 | 7.632 | +0.947 | [-8.000, +9.845] | +14.2 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 26.789 | +1.947 | [-7.845, +11.632] | +7.8 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 5.951 | -0.154 | [-3.097, +3.043] | -2.5 % | noise |
| boss@ice0 | turns | 20.895 | 21.684 | +0.789 | [-7.947, +9.105] | +3.8 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.258 | +0.014 | [-0.040, +0.068] | +5.9 % | noise |
| boss@ice0 | won | 0.053 | 0.105 | +0.053 | [-0.105, +0.211] | +100.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 17.73 | 46 | 7.6 | 56.3 | 26.8 | 10 | 0.24 |

