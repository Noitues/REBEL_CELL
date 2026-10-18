# Balance comparison: boss_hp035

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_hp035.json` (overrides: renewal_engine.hp*=0.35)
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 1 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | turns_phase_1 | 16.211 | 9.842 | -6.368 | [-10.474, -2.211] | -39.3 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 17.733 | -2.227 | [-7.804, +3.196] | -11.2 % | noise |
| boss@ice0 | died | 0.895 | 0.789 | -0.105 | [-0.316, +0.053] | -11.8 % | noise |
| boss@ice0 | enrage_step | 2.842 | 2.158 | -0.684 | [-2.105, +0.842] | -24.1 % | noise |
| boss@ice0 | hp_lost | 54.316 | 52.263 | -2.053 | [-10.368, +6.842] | -3.8 % | noise |
| boss@ice0 | intake | 55.684 | 55.421 | -0.263 | [-11.424, +11.424] | -0.5 % | noise |
| boss@ice0 | parked | 6.684 | 9.789 | +3.105 | [-5.161, +10.947] | +46.5 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 22.895 | -1.947 | [-11.895, +8.263] | -7.8 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.178 | +0.074 | [-2.877, +3.256] | +1.2 % | noise |
| boss@ice0 | turns | 20.895 | 17.474 | -3.421 | [-11.368, +3.947] | -16.4 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.259 | +0.016 | [-0.042, +0.073] | +6.4 % | noise |
| boss@ice0 | won | 0.053 | 0.158 | +0.105 | [-0.053, +0.263] | +200.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.05 | 10.25 | 26 | 9.8 | 55.4 | 22.9 | 11 | 0.26 |

