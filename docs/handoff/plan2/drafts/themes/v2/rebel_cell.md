<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__rebel_cell; status ok; tokens in 16419 cache-write 0 cache-read 34418 out 6364; cost $0.052. v2: designer answers 2026-10-19 applied. -->

# REBEL_CELL: THREE LINES, ONE CLOCK (v2)

## 0. What changed from v1

- **R1 (three operatives)** confirms v1 rule 1.1.1: exactly 3 operatives, one per lane. Nothing changes except one new coupling: the backup roster is now consumed by R2.
- **R2 (replacement, else abandon)** replaces v1 rules 11-12 (DARK lane, run continues). Death in the route phase now has two outcomes:
  - **A replacement exists:** it enters the lane at that lane's last cleared node (a fresh arrival; see rule 11).
  - **No replacement exists:** the whole run is abandoned. This applies the Q24.1 rule that death means the netrun is abandoned.
  - The DARK lane status is removed for the route phase. `switch_state` DARK survives only for the finale, where an operative can still fall.
  - Rule 17 (fail when all lanes are lost) collapses into "abandoned when there is no replacement."
- **R3 (no lead limit)** deletes v1 rule 6 (lead limit), the "AHEAD OF CLOCK" refusal, `hq_lead_limit`, and the `test_lead_limit_*` test.
  - The clock survives as a derived `step` (lowest living unARMED lane layer) that drives `seq` and the scenery.
  - A new coupling replaces the limit; see rule 6.
- **R4 (default lane effects)** keeps v1's three lane effects unchanged, so no change. It resolves the v1 Q-DESIGNER on lane effects.
- **R5 (regroup heal scales with ICE)** replaces the flat `throw_heal_pct`. The heal is now computed from the current ICE level and shown exactly in the THROW preview.
- **Code (REBEL_CELL not built yet):** no existing code changes. The roster-replacement action and the ICE-scaled heal are new work.

## 1. Rules

### Street netruns (light form)

1. A street Site carries `lane_tag` in {ROOF, STREET, SEWER}, assigned at Grid generation from the `grid` stream. It biases node-type weights only (`hq_lane_node_weights`, scaled by `street_lane_tilt_pct`). ROOF leans toward elites, SEWER toward events, STREET is neutral.
2. Capturing the final Rack of a street netrun adds its `lane_tag` to `lanes_scouted` (a set; no duplicates).
3. In the HQ run, a scouted lane gives its operative +`lane_scout_ram` starting RAM in that lane's first fight, and reveals that lane's end-room enemy on the plan view before launch.

### HQ netrun (full form)

**Setup**

4. The HQ launch requires exactly `hq_lanes_required` (3) operatives, one per lane, any class in any lane. Operatives beyond 3 on the roster are the **backup roster**. They do not enter the run; they wait in reserve.
5. Each lane has its own graph of `hq_lane_layers` (7) layers with 2-3 nodes each. The last layer is an elite-strength end room holding the lane's switch. Graphs are built at launch from the `map` stream and checkpointed. Each operative keeps its own HP, RAM, deck, Firmware and Daemons. Cycles are one shared pool.

**Route phase: one clock, no limit**

6. The player may take any lane's next node at any time, with one node resolving at a time (other lanes wait). Lanes are no longer coupled by position. They are still coupled by:
   1. **The shared Cycles pool.** Spending in one lane's shop reduces what the others can buy.
   2. **The single resolving slot.** One fight at a time, so the player must sequence their attention.
   3. **The shared backup roster.** A replacement used in one lane is gone for the others (rule 11).
   4. **THROW gating.** Nothing happens until every lane is ARMED, so the slowest lane sets the pace.
   5. **The derived clock `step`** (the lowest layer among unARMED lanes), which drives `seq` and the scenery only. It never refuses an action and gives no bonus.
7. `sync_state` is IN_STEP when all unARMED lanes are on the same layer, otherwise OUT_OF_STEP. It is information only.
8. A rest node heals that operative `hq_rest_heal_pct` of max HP. Shops and events spend the shared Cycles pool. Events are tagged to a lane.
9. A lane's end-room win sets its switch to ARMED, and the operative parks at the switch (inactive, safe, cannot take damage).

**Death and replacement (Q24.1, R2)**

10. An operative at 0 HP from any cause is lost for good, killed by the existing Q24.1 rule. Heat for the death follows GDD 4.2.
11. **Replacement.** If the backup roster is non-empty at that moment, the first operative in roster order (the earliest recruited, a fixed order) replaces the dead one:
    1. It enters the lane at the **last node that lane cleared**, or at the lane's layer-1 entry if it cleared none. The replacement starts at that node's exit, so the next node it can take is the one the dead operative was fighting. That node's fight is rebuilt fresh, with no carried damage.
    2. It arrives at **full HP**, with its own deck, Firmware and Daemons, and starting RAM as at a normal combat start.
    3. It keeps the lane's `lane_tag` benefits (the scout RAM applies again in its first fight).
    4. The lane's already-ARMED state is impossible, since a parked operative cannot die in the route phase.
    5. The replacement is removed from the backup roster. A dead operative's loss is permanent as usual.
12. **No replacement.** If the backup roster is empty when an operative dies, the run is abandoned: all surviving operatives return to HQ unharmed, with the **unbanked gains of the run lost**, and the HQ netrun stays launchable. This follows the Q24.1 reading that a death abandons the netrun.
13. An operative can never be lost while parked at an armed switch. The only death risks are route fights, events and the finale.
14. Abandoning the run by choice (GDD 4.5) kills every operative on it, as today, and does not consume the backup roster.

**THROW and the finale (Q34)**

15. When all three lanes are ARMED, THROW enables. It is a single deterministic action that checkpoints the save.
16. On THROW:
    1. each operative heals `regroup_heal_pct(ICE)` of max HP (rule 17);
    2. `seq` goes to 3 and `pulse` fires;
    3. each lane applies its `lane_effect` to the `dispatch_core` combat as a start modifier (R4: ROOF resistance −2 (min 0); STREET first-phase hub heal off; SEWER each operative +2 RAM at fight start);
    4. the finale combat is created.
17. **Regroup heal (R5).** With `i` = the current ICE level:
    - `i ≤ regroup_full_until_ice` (0): 100 %.
    - `i ≥ regroup_floor_ice` (5): `regroup_floor_pct` (20 %).
    - In between: linear, `pct = 100 − (100 − floor) × i / floor_ice`, rounded to the nearest whole percent. The floor is also the value above ICE 7, since 20 % is the floor for everything at or above ICE 5.
    - The heal never exceeds max HP and never revives a dead operative.
18. **Finale.** Survivors form the operative set. Within a turn the player moves focus freely between operative wheels. SEND IT resolves the focused wheel, then the rest in fixed order ROOF, STREET, SEWER, skipping fallen operatives. Operatives share no HP. The boss's phases, buffs and enrage belong to the DISPATCH boss pass.
19. A fallen operative in the finale is lost and its wheel leaves the focus set. The finale's replacements are not allowed: the backup roster does not enter once THROWN. If all operatives fall, the run fails and the HQ stays launchable.
20. Win = campaign win per GDD 1.3.

### Raid (one hook)

21. A REBEL_CELL raid always has 3 first-wave threats with start delays so all three reach the target on the same step: delay = (longest of the three path lengths) − (the threat's own path length). Raids never kill operatives (Q24.1). Everything else is unchanged.

### Campaign escalation

22. None.

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `lane_tag` | StringName | `SiteState` | `grid` stream; default `&"STREET"` |
| `lanes_scouted` | Array[StringName] | `CampaignState` | default [] |
| `hq_strike` | `HqStrikeState` | `RunState` | null outside HQ runs |
| `lanes` | Array[3] of `{lane_id, operative_id, layer, node_id, status}` | in `hq_strike` | status in ALIVE, ARMED (DARK is finale-only) |
| `graphs` | Array[3] | in `hq_strike` | built at launch from `map`, checkpointed |
| `backup_queue` | Array[operative_id] | in `hq_strike` | snapshot of the backup roster in fixed recruit order, consumed by replacements |
| `replacements_used` | int | in `hq_strike` | for the log and the preview |
| `phase` | enum ROUTE, THROWN, FINALE | in `hq_strike` | |
| `focus_lane` | int | in `hq_strike` | finale only |
| `regroup_heal_pct` | int | in `hq_strike` | computed at THROW from ICE, saved for the preview |
| `raid_arrival_step` | int | raid state | derived but saved so the preview survives reload |

- **Derived, never saved:** `step`, `sync_state`, `seq`.
- **RNG:** graphs use the `map` stream (checkpointed); `lane_tag` uses `grid`. Replacement uses no randomness (a fixed order), and rebuilding the node's fight uses the ordinary combat stream at a checkpoint.
- **Save impact:** additive fields with defaults: one version bump, trivial migration (old saves are dropped anyway per D3).

## 3. Preview

- **Plan view (DISPATCH view):** three lane graphs with node types, a step ruler, and per lane the layer, HP and RAM gauges and status. It also shows the **backup roster count** ("RESERVE n"). Scouted lanes show their end-room enemy.
- **Death preview:** an at-risk operative's lane shows exactly what happens at 0 HP. It reads "REPLACED by <operative> at <node>" if the reserve is non-empty, otherwise "RUN ABANDONED". Both are exact, since the roster order is fixed.
- **THROW preview:** the survivors, each HP after the heal (using the exact regroup percent for the current ICE), and the lane effects that will apply. All exact; no "?".
- **Fight outcomes** in the route follow the normal combat preview. A random respin shows "?" per Q19.
- **Raid:** each threat's arrival step and start delay, exact.

## 4. Numbers (placeholders)

| Value | Placeholder | config |
|---|---|---|
| Operatives required | 3 | `campaign_config.hq_lanes_required` |
| Layers per lane | 7 | `campaign_config.hq_lane_layers` |
| Rest heal | 30 % | `campaign_config.hq_rest_heal_pct` |
| Regroup heal at full-heal ICE | 100 % | `campaign_config.hq_regroup_full_pct` |
| ICE at or below which the heal is full | 0 | `campaign_config.hq_regroup_full_until_ice` |
| ICE at which the floor is reached | 5 | `campaign_config.hq_regroup_floor_ice` |
| Regroup heal floor | 20 % | `campaign_config.hq_regroup_floor_pct` |
| Replacement HP | 100 % | `campaign_config.hq_replacement_hp_pct` |
| Scout RAM | 2 | `campaign_config.lane_scout_ram` |
| `seq` 1 at step ≥ | 3 | `campaign_config.hq_seq_steps` |
| `seq` 2 at step ≥ | 5 | `campaign_config.hq_seq_steps` |
| Lane node weights (elite / event / shop) | ROOF 30/15/10, STREET 20/25/15, SEWER 15/40/15 | `campaign_config.hq_lane_node_weights` |
| Street tilt | 50 % of the HQ tilt | `campaign_config.street_lane_tilt_pct` |
| Lane effects on `dispatch_core` | ROOF: resistance −2; STREET: phase-1 hub heal off; SEWER: +2 RAM each | `campaign_config.hq_lane_effects` |
| First-wave threat count | 3 | `raid_config.rebel_first_wave` |

Worked values for the heal: ICE 0 = 100 %, ICE 1 = 84 %, ICE 2 = 68 %, ICE 3 = 52 %, ICE 4 = 36 %, ICE 5 and above = 20 %.

## 5. Tests to write

| Test | Tier | Asserts |
|---|---|---|
| `test_lane_tag_biases_node_weights` | fast | the tag changes weights only; same seed, same graph |
| `test_lanes_scouted_set_on_rack_capture` | fast | the tag is added once |
| `test_hq_launch_requires_three_operatives` | fast | fewer is refused with a reason; extras become the backup queue in recruit order |
| `test_lane_graphs_checkpointed_deterministic` | fast | same seed, same graphs; reload does not reroll |
| `test_no_lead_limit_any_lane_any_order` | fast | a lane may run 7 layers ahead of the others; nothing is refused |
| `test_step_and_sync_state_derived` | fast | derived values for a table of lane layers; ARMED lanes excluded |
| `test_end_room_win_arms_and_parks` | fast | ARMED, and the parked operative is untargetable |
| `test_death_replaced_from_backup` | fast | the first reserve enters at the last cleared node at full HP, the fight is rebuilt, and the roster shrinks by 1 |
| `test_replacement_at_layer_one_when_none_cleared` | fast | the entry-node case |
| `test_death_without_backup_abandons_run` | fast | the run ends, survivors return unharmed, unbanked gains are lost, and the HQ stays launchable |
| `test_replacement_order_across_lanes` | fast | two deaths use the queue in order and then abandon at the third |
| `test_replacement_deterministic_no_rng` | fast | no RNG draw beyond the combat checkpoint; identical results on reload |
| `test_regroup_heal_scales_with_ice` | fast | the table ICE 0 to 8: 100, 84, 68, 52, 36, 20, 20, 20, 20; never above max HP; never revives |
| `test_throw_requires_all_armed` | fast | THROW is disabled until the last lane is ARMED |
| `test_throw_applies_lane_effects` | fast | one effect per lane |
| `test_throw_checkpoint_roundtrip` | full | save at THROW, reload, and the same finale state |
| `test_no_replacement_in_finale` | full | the backup roster stays closed once THROWN |
| `test_finale_focus_order_skips_fallen` | full | Q34 order |
| `test_abandon_by_choice_kills_all_keeps_roster` | fast | GDD 4.5 on three operatives; the backup roster is untouched |
| `test_raid_converging_arrival` | fast | three threats share one arrival step; delay arithmetic |
| `test_raid_never_kills_operatives` | fast | Q24.1 |
| `test_preview_death_outcome_exact` | fast | the preview text matches the real outcome in both branches |
| `test_hq_save_load_roundtrip` | full | `hq_strike` survives a mid-route reload, including the backup queue |

## 6. Build slices

1. **Light form: `lane_tag` and `lanes_scouted`** (S). No dependencies. Data fields, grid generation, node-weight tilt.
2. **Config block and heal function** (S). The `regroup_heal_pct(ICE)` pure function plus its tests (slice 1 optional).
3. **`HqStrikeState` and save fields** (M). Depends on 1. Includes `backup_queue` and the save bump.
4. **NEW: multi-operative netrun session** (L). Depends on 3. Three operative states, input routed to the lane of the action, the clock derivation, parking. The fallback is one operative walking all three lanes in sequence; it keeps the replacement and heal rules, but loses simultaneity.
5. **Death, replacement and abandon** (M). Depends on 4. Replacement entry at the last cleared node, the rebuilt fight, the abandon branch.
6. **THROW action and lane effects** (M). Depends on 4 and the boss pass hook for start modifiers.
7. **Plan view UI** (M). Depends on 4. The art-pass owns the 3D look. Includes gauges, the reserve count, and the death and THROW previews.
8. **Raid converging arrival** (S). Independent; it uses the existing threat start-delay field.
9. **Finale (Q34)** (L). Covered by the DISPATCH boss pass (N3, N5, N6). Depends on 6.

## 7. Q-DESIGNER

Q-DESIGNER: When a replacement enters and the dead operative's lane was mid-fight, should the fight restart fresh (my default) or resume with the enemy's damage kept?
Q-DESIGNER: Should the backup roster also supply replacements for operatives that fall in the finale (my default: no, since the roster closes at THROW), or may a reserve step in?
Q-DESIGNER: Should the run-abandon case (no reserve) lose the run's unbanked gains (my default, as in Q24.1), or keep Cycles already earned?
Q-DESIGNER: Should the heal floor stay 20 % at every ICE of 5 and above (my default), or keep declining past ICE 7?
Q-DESIGNER: Should the backup roster be shown to the player on the launch screen as an explicit "reserve" choice (my default: all roster extras, in recruit order), or may the player pick the order?
