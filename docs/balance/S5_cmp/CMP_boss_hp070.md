# Balance comparison: boss_hp070

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_hp070.json` (overrides: renewal_engine.hp*=0.7)
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 19.519 | -0.442 | [-6.423, +5.365] | -2.2 % | noise |
| boss@ice0 | died | 0.895 | 0.895 | +0.000 | [-0.158, +0.158] | +0.0 % | noise |
| boss@ice0 | enrage_step | 2.842 | 2.263 | -0.579 | [-2.000, +0.842] | -20.4 % | noise |
| boss@ice0 | hp_lost | 54.316 | 55.684 | +1.368 | [-6.105, +9.579] | +2.5 % | noise |
| boss@ice0 | intake | 55.684 | 56.368 | +0.684 | [-11.274, +13.318] | +1.2 % | noise |
| boss@ice0 | parked | 6.684 | 6.474 | -0.211 | [-9.263, +7.789] | -3.1 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 22.526 | -2.316 | [-11.789, +7.582] | -9.3 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.244 | +0.139 | [-2.781, +3.312] | +2.3 % | noise |
| boss@ice0 | turns | 20.895 | 18.158 | -2.737 | [-10.632, +4.318] | -13.1 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.252 | +0.008 | [-0.049, +0.064] | +3.4 % | noise |
| boss@ice0 | won | 0.053 | 0.105 | +0.053 | [-0.105, +0.211] | +100.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 14.18 | 32 | 6.5 | 56.4 | 22.5 | 9 | 0.25 |

