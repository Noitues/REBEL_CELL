<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__overclocker; status ok; tokens in 12367 cache-write 0 cache-read 34418 out 3044; cost $0.031. DRAFT. -->

# Overclocker: raid operative design

## 1. Raid role

The Overclocker is a Rigger alternative. Its netrun kit (banked RAM instead of free nudges, 55 HP, max RAM 12) has no raid analogue. The only raid-relevant data in the `.tres` is the station bonus: trigger 12 (`ON_RAID_START`), effect type 14 (`MODIFY_HEAT`), target 0, amount 5. The input shows no sign, so the draft reads the amount as +5 and the raid effect is a Heat change at raid start. The sign is not confirmed by the excerpt (Q-DESIGNER 1).

**Role: "Surge Station."** Stationed on a Safehouse, the operative adds the Heat change at the moment the raid starts, scaled by the rank multiplier (1.25 / 1.5 / 2.0 at ranks 1 / 2 / 3).

- It touches **R4** only: the Heat shift changes the band the raid is built in, so it must be applied before band-gated rules (R2 encryption, R3 vehicle availability, wave 2, ultimatum) are resolved.
- It does not touch R1 (exposure) or R2 (decrypt sources: Ghost and Intel only).
- It has no playout effect. It is not a turret, volley or absorb source.
- **Simplest behind config:** the station Heat change is applied once, at `ON_RAID_START`, only if the operative is stationed on a Safehouse and not DOWN or TAKEN. Setup shows the resulting band before the player commits anything. It cannot cross a threshold, because that would queue a new raid. If it would cross one (or reach 100), the Heat change is clamped to the largest legal value, which may be 0.
- **Cascade rule:** the shift never queues a raid, so a raid queued this way has no wave 2 (the unified no-cascade rule extends to it).
- **Defenses stay shared:** the operative adds no per-operative copy of anything.
- **Hub Core passive:** the input gives no raid reading for the Overclocker Hub, so it has no raid effect.
- **If the designer prefers no Heat effect,** set `config: campaign_config.raid_overclocker_station_heat` to 0; the class then has no raid role.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| `config: campaign_config.raid_overclocker_station_heat` | 5 | Heat points at raid start, taken from the class file `te_station` amount; sign per Q-DESIGNER 1 |
| `config: campaign_config.raid_overclocker_rank_mult` | [1.0, 1.25, 1.5, 2.0] | multiplier by rank 0-3, from `station_bonus_multiplier` (rank 0 = 1.0) |
| `config: campaign_config.raid_overclocker_clamp_below_threshold` | 1 | boolean: clamp the shift so it never crosses a Heat threshold or reaches 100 |
| `config: campaign_config.raid_overclocker_apply_step` | 0 | raid step at which the shift applies (0 = before band rules are built) |
| `config: campaign_config.raid_overclocker_requires_safehouse` | 1 | boolean: only applies while stationed on a Safehouse |
| `config: campaign_config.raid_overclocker_stack_with_other_stations` | 0 | boolean: 0 = only the highest single station Heat effect applies |
| `config: campaign_config.raid_step_cap` | 30 | steps (existing) |
| `config: campaign_config.ultimatum_heat_by_band` | {4, 6} | existing unified key; the Overclocker shift is checked against it for threshold legality |

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Setup header chip | `Surge Station: Heat {delta} at raid start -> band {band}` (TextDb `raid.overclocker.chip`) | none |
| Setup header chip, clamped | `Surge Station: Heat {delta} (limited to stay under {threshold})` (`raid.overclocker.chip_clamped`) | none |
| Setup header chip, no effect | `Surge Station: no effect (needs a Safehouse)` (`raid.overclocker.chip_off`) | none |
| Band tooltip | `Raid band is {band} after Surge Station` (`raid.overclocker.band`) | none |
| Ultimatum sheet | `Heat now {heat}; paying Heat would reach {heat_after}` (`raid.overclocker.ultimatum`) | none |

Nothing in this role is random.

## 4. Tests

| name | tier | assert |
|---|---|---|
| surge_applies_at_raid_start | fast | Stationed on a Safehouse with a fixed Heat, the shift is applied once before band rules are built |
| surge_rank_scaling | fast | The shift at ranks 0-3 equals the base times `raid_overclocker_rank_mult`, rounded |
| surge_clamp_threshold | fast | A shift that would cross a threshold or reach 100 is clamped to the largest legal value; no raid is queued |
| surge_no_safehouse_no_effect | fast | An operative not on a Safehouse, or on a DOWN or TAKEN node, gives no shift |
| surge_band_feeds_r2_r3_r4 | fast | The band after the shift selects encryption, vehicle availability, wave 2 and ultimatum |
| surge_no_cascade | fast | A raid queued by Heat from this effect has no wave 2 |
| surge_single_station | fast | With several stations, only one Heat effect applies when `stack_with_other_stations` = 0 |
| surge_applies_once | fast | A raid applies the shift once; the playout never reapplies it |
| determinism_same_seed | fast | The same seed, graph, placements and stationing give an identical raid and result |
| preview_equals_result | fast | The band and Heat shown in setup equal those used in the built raid |
| preview_interval_contains_result | full | With encrypted threats, the outcome lies in the interval; the shift is identical in best and worst cases |
| q24_1_zero_hp_operative_lost | fast | An operative at 0 HP is lost and the active netrun abandoned; the raid itself is unchanged |
| q24_1_no_raid_kills | fast | No raid step reduces an operative's HP; stationing is never harmful |
| q42_sink_once | fast | The ultimatum Schematics payment happens at most once per raid, whatever the stationing |
| q42_shared_defenses | fast | The class adds no per-operative defense; every operative defends the same network |
| q42_no_resetup | fast | After Start raid, setup cannot reopen; the shift cannot be re-triggered |
| numbers_from_config | fast | Changing each key in section 2 changes behavior; no literal in the rules code |
| sweep_heat_sink_effect | full | Over a sweep, the shift moves raid band frequency and ultimatum payments within the sink target (5-8 % of income) |

## 5. Binding rule check

- **Q24.1:** The role never damages or kills an operative. The only operative-affecting rule stays "0 HP at any time means the operative is lost and the netrun is abandoned"; the raid is unchanged. Tested in `q24_1_zero_hp_operative_lost` and `q24_1_no_raid_kills`.
- **Q42 sink once:** The Overclocker adds no Schematics cost or payment. It only moves the band, and the unified ultimatum is still paid at most once per raid (`q42_sink_once`).
- **Q42 shared defenses / no re-setup:** The class adds no asset, copy or per-operative defense. The shift resolves once at raid start, before setup commits, and setup cannot reopen after Start raid (`q42_shared_defenses`, `q42_no_resetup`).

## 6. Q-DESIGNER lines

Q-DESIGNER: Is the station bonus amount 5 a Heat increase or a Heat reduction at raid start (the excerpt shows no sign)? | DEFAULT: a reduction of 5 Heat before bands are built, scaled by rank, clamped so it cannot cross a threshold downward in a way that cancels the raid
Q-DESIGNER: Should the shift apply before the band (changing wave 2, encryption and ultimatum) or after band selection (a cosmetic Heat change only)? | DEFAULT: after the raid's band is chosen but before the ultimatum price is shown, so the band is stable and only the Heat-option legality and the end-of-raid Heat change
Q-DESIGNER: Should the Overclocker have any playout role (for example a one-time RAM-style burst), or stay a setup-only Heat station? | DEFAULT: setup-only; no playout effect
Q-DESIGNER: Does the shift stack with other classes' station Heat effects? | DEFAULT: no; only the largest single station effect applies
