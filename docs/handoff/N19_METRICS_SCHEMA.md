# N19 sim metrics schema

Collector: `tools/balance/sim_metrics.gd` (`SimMetrics`, observational: reads result events and one state number, no RNG, no state writes).
Hooked in `balance_probe.gd` (`observe`), emitted by `balance_runner.gd` (`run_fight`, `run_boss`), aggregated in
`tools/balance/phase_metrics.py` and rendered by `balance.py` (report and `compare`). Records without `metrics` (pre-N19 files) load with no metrics and are skipped.

## Result record fields (`rec.metrics`, fight and boss modes)
| field | unit | source |
|---|---|---|
| `phases[]` | list | one entry per phase that had at least one turn; `[]` for a zero-turn fight |
| `phases[].turns` | turns | End Turn calls; the phase-change turn counts in the outgoing phase (`boss_phase` event moves later events on) |
| `phases[].parked` | HP | sum of `parked` on `damage` / `corrupted` / `parasite` events whose target is not the player (R3 floor excess); last phase is 0 |
| `phases[].parked_by_path` | HP | `{hit, self, parasite, pierce}`; sums to `parked`. `self` = `corrupted` events or attacker == target; `pierce` = `damage.pierce`; `parasite` stays 0 until an event is emitted for it |
| `phases[].intake` | HP | `damage.hp_damage` with target == player (unblocked, after block and shield); a `sandboxed` hit counts 0 (charges: N14) |
| `phases[].heal_turns` | turns | turns containing a `heal` event with amount > 0 on a non-player (checked at the End Turn) |
| `phases[].resistance_absorbed` | ticks | `spin.absorbed` plus one per `nudge_absorbed`, enemy targets |
| `phases[].incomplete` | bool | true on the last phase when the fight was not won (death, stuck) |
| `enrage_step` | step | highest `enrage_step` seen on any enemy (N4 state); 0 when none (an enrage-free normal also reads 0) |
| `listener_fires` | map id -> count, or `null` | counts `listener_fire` events; `null` while N6 is absent (`listeners_supported` false) |
| `turn_manipulation` | turns | `{own, enemy, both, none}`: per turn, whether the player's own actions moved their wheel, the enemy's, both or neither (nudge/spin/flip events from player actions) |

Flat scalars added to `rec.scalars` (so `compare` shows them): `parked`, `intake`, `resistance_absorbed`, `enrage_step`, `turns_both_share`.

## Aggregates and pass criteria (`phase_metrics.aggregate`)
- `turns_mean`, `turns_p90`: over fight turns (sum of phase turns); p90 is nearest-rank (`sorted[ceil(0.9 n) - 1]`).
- `win_rate`: mean of `scalars.won`.
- `phase_turns_mean`, `in_target`: over complete (not `incomplete`) phases; in target = 3 to 4 turns inclusive. Empty list gives `None`, no division.
- `heal_turns_per_phase_max`, `heal_over_limit`: limit 1 heal turn per phase.
- `parked_mean`, `intake_mean`, `resistance_absorbed_mean`: per fight sums, averaged.
- `turns_with_both_share`: `both / (own + enemy + both + none)`; the designer wants one or the other, not both.
- Boss warnings only (never failures): win rate outside 50 % +/- 15 points at `boss@ice0`; any phase over 4 turns.
