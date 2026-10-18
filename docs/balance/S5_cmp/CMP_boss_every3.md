# Balance comparison: boss_every3

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_every3.json` (overrides: config.enrage_every_n_turns_by_class=[0,5,5,3])
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 20.226 | +0.266 | [-5.792, +6.226] | +1.3 % | noise |
| boss@ice0 | died | 0.895 | 0.895 | +0.000 | [-0.158, +0.158] | +0.0 % | noise |
| boss@ice0 | enrage_step | 2.842 | 4.474 | +1.632 | [-0.476, +3.947] | +57.4 % | noise |
| boss@ice0 | hp_lost | 54.316 | 54.316 | +0.000 | [-8.842, +8.842] | +0.0 % | noise |
| boss@ice0 | intake | 55.684 | 55.000 | -0.684 | [-11.213, +10.158] | -1.2 % | noise |
| boss@ice0 | parked | 6.684 | 6.684 | +0.000 | [-8.950, +8.950] | +0.0 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 24.579 | -0.263 | [-10.263, +10.000] | -1.1 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.158 | +0.054 | [-2.861, +3.213] | +0.9 % | noise |
| boss@ice0 | turns | 20.895 | 20.526 | -0.368 | [-9.108, +8.158] | -1.8 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.247 | +0.004 | [-0.056, +0.063] | +1.5 % | noise |
| boss@ice0 | won | 0.053 | 0.053 | +0.000 | [-0.105, +0.105] | +0.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.0 | 24.6 | 18 | 0.24 |

