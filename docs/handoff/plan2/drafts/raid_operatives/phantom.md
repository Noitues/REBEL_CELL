<!-- RD-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01EGVQBTvvXmgoWzSJEGcPEp, custom_id rd01__phantom; status ok; tokens in 12368 cache-write 0 cache-read 34418 out 7731; cost $0.054. DRAFT. -->

# Phantom: raid operative design

## 1. Raid role

**Phantom is a Ghost alternative. Its raid role is "stalls the hardest hitter, then shrugs off one hit." The role is driven by data already in `phantom.tres` (`ON_RAID_START` → FREEZE) plus the unified draft's reconciliation line "Phantom SANDBOX negates a whole exposed hit." It adds no mechanic and no RNG.** The Ghost's "threats entering node delayed" bonus and its R2 free decrypt do not carry over: this class dodges instead of slipping resistance.

The Hub Core passive and the netrun Perfect hook have no raid analogue, so they are not used.

A Phantom has a raid role only while stationed on a Safehouse. Stationing is set between runs, never in a raid, so there is no re-setup. Without a stationed Phantom the cell gets nothing from this class.

Rules:
1. **Raid-start freeze (the station bonus).**
   - When the raid is built, each stationed Phantom picks one first-wave threat: the one with the highest scaled damage, ties broken by lowest threat index.
   - Two Phantoms pick different threats, in descending damage order.
   - That threat's movement clock (or `arrival_step`, for a LANDER) starts `freeze_steps` later.
   - `freeze_steps` = base freeze amount × the class's rank station multiplier, rounded half up.
   - The freeze is a plain delay, not an ICE Lock, so FLYING threats are not exempt (same as frozen edges in R3).
   - A frozen threat deals no damage while it waits, because it is not yet on a claimed node.
   - It still counts against the step cap.
2. **One-hit dodge (the SANDBOX analogue).** The stationed node negates the first threat hit it would take in the raid: a whole single hit by one threat in one step. The negated hit deals no integrity damage and creates no 50 % spill. It is used once per raid and does not refresh.
3. **R1 EXPOSED.**
   - The negate is evaluated after the exposure multiplier.
   - It is full value on the exposed node: the ×1.5 never reaches integrity and nothing spills.
   - A player who knows a Phantom node is exposed can leave it uncovered by assets and lean on the dodge, but only for one hit.
4. **R2 encrypted routes.** The freeze target is chosen from stats, which are always visible, so encryption never hides it. The class gives no decrypts.
5. **R3 vehicles.**
   - The freeze works on every vehicle type.
   - The dodge works against any hit, including a HEAVY's.
   - LANDER drops onto a node the dodge covers are a natural use: the unified draft lists the Phantom SANDBOX as a LANDER counter.
6. **R4 second wave and ULTIMATUM.**
   - The class has no ultimatum interaction and is never part of the Schematics sink.
   - The freeze applies to the first wave only. The dodge is spent on whichever hit comes first, from either wave.

Simplest choice where the sources are silent: the rank multiplier scales the freeze steps only, and the dodge count stays flat. Both are behind config.

## 2. Numbers

| key | default | unit / note |
|---|---|---|
| config: content/classes/phantom.tres station_bonus FREEZE `amount` | 1 | steps; base freeze, read from the existing `ON_RAID_START` effect |
| config: campaign_config.raid_station_multiplier_rank0 | 1.0 | multiplier; no-rank value (the class file holds the other ranks) |
| config: content/classes/phantom.tres rank_rewards[1].station_bonus_multiplier | 1.25 | multiplier (existing) |
| config: content/classes/phantom.tres rank_rewards[2].station_bonus_multiplier | 1.5 | multiplier (existing) |
| config: content/classes/phantom.tres rank_rewards[3].station_bonus_multiplier | 2.0 | multiplier (existing) |
| config: campaign_config.raid_phantom_freeze_rounding | half_up | rounding rule for the freeze steps; yields 1 / 1 / 2 / 2 across the four ranks |
| config: campaign_config.raid_phantom_freeze_targets | 1 | threats frozen per stationed Phantom |
| config: campaign_config.raid_phantom_freeze_wave | 1 | wave index the freeze applies to |
| config: campaign_config.raid_phantom_freeze_ignores_vehicle_hold | 1 | flag (1 = FLYING is not exempt) |
| config: campaign_config.raid_phantom_dodge_hits | 1 | whole hits negated per stationed Phantom per raid |
| config: campaign_config.raid_phantom_dodge_spill | 0 | percent of spill from a negated hit |
| config: campaign_config.exposed_damage_mult | 1.5 | existing R1 key; the dodge is evaluated after it |
| config: campaign_config.raid_step_cap | 30 | steps; existing |

## 3. Preview lines

All values are exact: stats are visible and the freeze target is a deterministic rule, so nothing in this class is random. R2's hatched interval on a node's outcome is not a Phantom effect; the freeze and dodge are applied inside each combination of that sweep.

| surface | exact text pattern | "?" parts |
|---|---|---|
| Safehouse station tooltip (setup) | `raid.phantom.station`: "Phantom: freezes {threat} for {steps} steps at raid start; {node} dodges the first hit." | none |
| Threat chip, frozen (setup) | `raid.phantom.frozen_chip`: "FROZEN {steps}" | none |
| Node tooltip, dodge ready (setup) | `raid.phantom.dodge_ready`: "DODGE ready: negates the first hit ({hit} damage)." | none |
| Node tooltip, dodge on an exposed node | `raid.phantom.dodge_exposed`: "EXPOSED ×{mult}: the dodge negates the first hit in full." | none |
| Playout log, freeze | `raid.phantom.log_freeze`: "{threat} held at {entry} ({steps} steps left)." | none |
| Playout log, dodge | `raid.phantom.log_dodge`: "{node} dodged {threat}'s hit ({hit} damage)." | none |
| Post-raid summary line | `raid.phantom.summary`: "Phantom: froze {threat} for {steps} steps; dodged {count} hit(s), {saved} integrity saved." | none |
| Station tooltip, nothing to freeze | `raid.phantom.no_target`: "Phantom: no incoming threat to freeze." | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| freeze_target_is_highest_damage | fast | The frozen threat is the first-wave threat with the highest scaled damage; ties go to the lowest threat index |
| freeze_two_phantoms_distinct | fast | Two stationed Phantoms freeze two different threats in descending damage order |
| freeze_steps_from_rank | fast | `freeze_steps` equals the base freeze amount × the rank multiplier, rounded half up, for every rank; the numbers come from the class file and config |
| freeze_delays_movement_and_arrival | fast | A frozen ground, flying or heavy threat starts moving `freeze_steps` later; a LANDER's `arrival_step` is pushed back by the same amount |
| freeze_ignores_vehicle_hold | fast | A frozen FLYING threat is held (the flag is on); with the flag off the same threat is not held |
| freeze_first_wave_only | fast | Second-wave threats never receive the freeze |
| freeze_no_damage_while_held | fast | A frozen threat deals no integrity damage before its clock starts |
| dodge_negates_first_hit_whole | fast | The first hit on the stationed node deals zero integrity damage and produces no spill |
| dodge_once_per_raid | fast | The dodge is spent on the first hit and the second hit lands normally |
| dodge_after_exposure | fast | On an exposed Phantom node the first hit is negated in full, not reduced to the pre-multiplier amount |
| dodge_unstationed_absent | fast | With no stationed Phantom there is no freeze and no dodge |
| dodge_per_phantom_own_node | fast | Each stationed Phantom's dodge covers only its own node |
| phantom_encrypted_threat_preview_exact_target | fast | With all threats encrypted, the freeze target still matches the visible-stats rule |
| determinism_same_seed | fast | The same graph, placements, band and seed produce an identical playout log, including freeze and dodge events |
| preview_equals_result_decrypted | fast | With every threat decrypted, the setup preview equals the playout for every node (freeze and dodge included) |
| preview_inside_interval_encrypted | fast | With encrypted threats, the playout lies inside the R2 interval and the freeze and dodge are applied in every enumerated combination |
| q24_1_operative_zero_hp_lost_netrun_abandoned | fast | An operative at 0 HP in the active netrun is lost and the netrun abandoned; the raid itself is unchanged |
| q24_1_raid_never_kills | fast | No raid step changes an operative's HP; a stationed Phantom on a DOWN or TAKEN node returns to reserves unharmed |
| q42_sink_once_per_raid | fast | The ultimatum is paid at most once per raid, with a Phantom stationed or not; the class adds no payment |
| q42_shared_defenses_no_resetup | fast | A stationed Phantom changes no asset or placement; there is no setup action after Start raid |
| config_only_numbers | fast | Every number comes from config or the class file; no literal in the raid code path |
| sweep_phantom_value | full | Across tiers and Heat bands, raids with a Phantom stationed show a measurable but bounded difference in nodes held vs. without; report win-rate delta |

## 5. Binding rule check

- **Q24.1:** The raid never touches operative HP. A stationed Phantom's node going DOWN or TAKEN returns it to reserves unharmed. An operative at 0 HP in a netrun is lost and the netrun abandoned, and the raid is unchanged. Tests `q24_1_*` cover both directions.
- **Q42 Schematics sink:** The class adds no cost, payment or refund and does not interact with the ultimatum. The sink stays once per raid and is fully owned by R4.
- **Q42 shared defenses / no re-setup:** The freeze and dodge come from the Phantom's station slot, fixed between runs, and change no asset or placement. They are stationing effects, not per-operative defense copies. No action is available after Start raid.

## 6. Q-DESIGNER lines

Q-DESIGNER: Should the Phantom's freeze scale with rank, or stay flat? | DEFAULT: scale with the existing rank station multiplier, giving 1 / 1 / 2 / 2 steps across the four ranks
Q-DESIGNER: Should the freeze target a specific threat type rather than the highest damage? | DEFAULT: highest scaled damage in the first wave, ties by lowest threat index
Q-DESIGNER: Should the dodge also scale with rank? | DEFAULT: no; flat at one hit per raid, scaling only the freeze
