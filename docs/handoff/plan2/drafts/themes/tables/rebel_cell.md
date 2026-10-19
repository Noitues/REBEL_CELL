<!-- WH-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01NoiieatK3meY6YPMnq3LnX, custom_id wh01__rebel_cell; status ok; tokens in 16890 cache-write 0 cache-read 34418 out 5956; cost $0.050. DRAFT. -->

# REBEL_CELL: WH-01 table

## 1. Config keys

| key | default | unit / note | source |
|---|---|---|---|
| `campaign_config.hq_lanes_required` | 3 | operatives, one per lane; THEMES_SHEET R1 default | draft §4 |
| `campaign_config.hq_lane_layers` | 7 | layers per lane graph, 2-3 nodes each | draft §4; REPLAN G (R2) |
| `campaign_config.hq_lead_limit` | 2 | layers a lane may lead the lowest living lane | draft §4; REPLAN G (R1) |
| `campaign_config.hq_rest_heal_pct` | 30 | percent of the operative's max HP, per Rest node | draft §4 |
| `campaign_config.hq_throw_heal_pct` | 20 | percent of max HP at THROW; config-only | draft §4; THEMES_SHEET R5 |
| `campaign_config.lane_scout_ram` | 2 | extra starting RAM in a scouted lane's first fight | draft §4 |
| `campaign_config.hq_seq_steps` | [3, 5] | step thresholds for seq 1 and seq 2 (seq 3 on THROW) | draft §4 |
| `campaign_config.hq_lane_node_weights` | ROOF {elite 30, event 15, shop 10}; STREET {20, 25, 15}; SEWER {15, 40, 15} | percent weights; the rest of each lane's weight goes to Router, Rest and the other node types as the existing generator allocates | draft §4 |
| `campaign_config.street_lane_tilt_pct` | 50 | percent of the HQ tilt away from neutral STREET weights | draft §4 |
| `campaign_config.hq_lane_effects` | ROOF {enemy_resistance_delta: -2, floor 0}; STREET {first_phase_hub_heal: off}; SEWER {operative_ram_bonus: 2} | start-of-fight modifiers on `dispatch_core`, one per ARMED lane | draft §4; THEMES_SHEET R4 |
| `raid_config.rebel_first_wave` | 3 | first-wave threat count for REBEL_CELL raids | draft §4 |
| `campaign_config.hq_lane_ids` | [ROOF, STREET, SEWER] | fixed lane order, also the finale resolve order (Q34); a definition of the lane set | added by the Q34 ruling (resolve order) |

## 2. State and save fields

| object | field | type | save impact |
|---|---|---|---|
| `SiteState` | `lane_tag` | StringName, default `&"STREET"` | additive default (corp_theme block, WH-02) |
| `CampaignState` | `lanes_scouted` | Array[StringName], default [] | additive default (corp_theme block, WH-02) |
| `RunState` | `hq_strike` | HqStrikeState or null (null outside HQ runs) | additive default (corp_theme block, WH-02) |
| `HqStrikeState` | `lanes` | Array[3] of {lane_id: StringName, operative_id: StringName, layer: int, node_id: StringName, status: int (ALIVE, ARMED, DARK)} | additive default (corp_theme block, WH-02) |
| `HqStrikeState` | `graphs` | Array[3] of map graphs, built once at launch from the `map` stream and checkpointed | additive default (corp_theme block, WH-02) |
| `HqStrikeState` | `phase` | int enum (ROUTE, THROWN, FINALE) | additive default (corp_theme block, WH-02) |
| `HqStrikeState` | `focus_lane` | int, finale only | additive default (corp_theme block, WH-02) |
| raid state | `raid_arrival_step` | int; derived, saved so the preview survives reload | additive default (corp_theme block, WH-02) |
| raid state | `threat.start_delay` | int steps; the existing threat field, set at raid build | none (existing field) |
| derived (not saved) | `step` | int, the lowest layer among living lanes that are not parked or ARMED | none |
| derived (not saved) | `sync_state` | enum IN_STEP / OUT_OF_STEP | none |
| derived (not saved) | `seq` | int 0..3 from `step` and `phase` | none |
| derived (not saved) | `switch_state[3]` | NOT_ARMED / ARMED / THROWN / DARK, from lane status and phase | none |

- The save version bumps by 1 with a trivial migration (additive defaults; old saves are dropped per D3).
- RNG: lane graphs use the `map` stream, `lane_tag` uses the `grid` stream, nothing else is random.
- Ties are broken by content id, then node id.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Plan view, lane header (`theme.rebel_cell.lane_header`) | `{LANE}: layer {n}/7, HP {hp}/{max}, RAM {ram}, {status}` | none |
| Plan view, step ruler (`theme.rebel_cell.step_ruler`) | `STEP {step}, {IN STEP / OUT OF STEP}` | none |
| Plan view, node (`theme.rebel_cell.node_type`) | `{node type}` per node | none (fight outcomes follow the normal combat preview) |
| Plan view, scouted lane (`theme.rebel_cell.end_room_scouted`) | `END ROOM: {enemy name}` | none |
| Plan view, unscouted lane (`theme.rebel_cell.end_room_unscouted`) | `END ROOM: ?` | the enemy is unknown until the lane is scouted |
| Hover on a refused node (`theme.rebel_cell.ahead_of_clock`) | `AHEAD OF CLOCK: advance {lane}` | none |
| Route fight outcome (`theme.rebel_cell.route_fight`) | the normal combat preview | "?" until fought, as in the normal combat |
| Launch refusal (`theme.rebel_cell.need_three`) | `NEED {n} OPERATIVES: {have} assigned` | none |
| Lane scout bonus (`theme.rebel_cell.scout_ram`) | `{LANE} SCOUTED: +{n} RAM in first fight` | none |
| Lane dark (`theme.rebel_cell.lane_dark`) | `{LANE} DARK: operative lost` | none |
| THROW preview (`theme.rebel_cell.throw_preview`) | `THROW: {n} operatives, HP after heal {hp list}; effects: {list}; lost with DARK lanes: {list}` | none |
| THROW disabled (`theme.rebel_cell.throw_wait`) | `WAITING: {lane} not armed` | none |
| Finale (`theme.rebel_cell.finale_focus`) | `FOCUS {LANE}: resolves {tier/damage}; next {LANE}...` | "?" only where the Q34 preview shows a random respin per Q19 |
| Raid threat (`theme.rebel_cell.raid_arrival`) | `THREAT {n}: arrives step {s}, starts after {d} steps` | none |
| Abandon confirm (`theme.rebel_cell.abandon_all`) | `ABANDON: all {n} operatives lost` | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| `test_lane_tag_biases_node_weights` | fast | the tag changes weights only; the same seed gives the same graph; STREET is neutral and the street tilt is `street_lane_tilt_pct` of the HQ tilt |
| `test_lanes_scouted_set_on_rack_capture` | fast | the tag is added once, never duplicated |
| `test_scout_ram_and_reveal` | fast | a scouted lane gives `lane_scout_ram` in its first fight only; the end-room enemy is revealed, with no state change |
| `test_hq_launch_requires_three_operatives` | fast | fewer than `hq_lanes_required` is refused with a reason |
| `test_lane_graphs_checkpointed_deterministic` | fast | same seed gives the same three graphs; reload does not reroll; 7 layers of 2-3 nodes |
| `test_lead_limit_refuses_third_layer_ahead` | fast | the refusal text `AHEAD OF CLOCK: advance <lane>`; a parked, ARMED or DARK lane is excluded from the minimum |
| `test_sync_state_in_vs_out_of_step` | fast | derived values for a table of lane layers; no penalty in either state |
| `test_shared_cycles_pool` | fast | shop and event spend comes from one pool; HP, RAM, deck and Firmware stay per operative |
| `test_rest_heals_config_pct` | fast | Rest heals `hq_rest_heal_pct` of that operative's max HP, clamped to max |
| `test_end_room_win_arms_switch` | fast | the status becomes ARMED and the operative is parked |
| `test_operative_death_darkens_lane_run_continues` | fast | Q24.1: 0 HP at any time makes the lane DARK, the operative lost and Heat per GDD 4.2; the other lanes keep playing; the DARK lane is not in the step minimum |
| `test_all_lanes_dark_fails_run_keeps_hq_open` | fast | the run fails; the HQ netrun stays launchable; the raid is unchanged |
| `test_throw_requires_all_living_armed` | fast | THROW is disabled until the last living lane is ARMED |
| `test_throw_heals_and_applies_lane_effects` | fast | heal is `hq_throw_heal_pct`, one effect per ARMED lane, none for DARK, values only from `hq_lane_effects` |
| `test_throw_preview_equals_result` | fast | the THROW preview HP and effect list equal the created finale state |
| `test_throw_checkpoint_roundtrip` | full | save at THROW, reload, and the same finale state results |
| `test_finale_focus_order_skips_dead` | full | Q34 order ROOF, STREET, SEWER; killed operatives are skipped and leave the focus set; focus returns to the first living wheel |
| `test_finale_preview_equals_result` | full | the focused wheel's preview equals the resolved result |
| `test_finale_carry_over` | fast | HP, deck, Firmware and Daemons carry; RAM resets to the normal combat start; statuses and the lead limit do not carry |
| `test_abandon_kills_all_operatives` | fast | GDD 4.5 applied to every operative on the run |
| `test_raid_converging_arrival` | fast | three threats share one arrival step; delay = longest path minus own path |
| `test_raid_never_kills_operatives` | fast | Q24.1: no operative is lost in a raid |
| `test_seq_mapping_from_step` | fast | seq 0 below step 3, 1 from 3, 2 from 5, 3 on THROW |
| `test_hq_save_load_roundtrip` | full | `hq_strike` survives a mid-route reload |
| `test_hq_determinism_same_seed` | full | same seed and same inputs give identical route, THROW and finale state hashes |
| `test_numbers_only_from_config` | fast | no theme number is a literal in code; every value above is read from config |
| `test_theme_strings_in_textdb` | fast | every `theme.rebel_cell.*` key exists in TextDb in US English |

## 5. Q-DESIGNER disposition

| # | draft line (first 6 words, verbatim) | DEFAULT or DROPPED | text |
|---|---|---|---|
| 1 | Q-DESIGNER: Should the HQ run require | DEFAULT | Exactly three operatives behind `hq_lanes_required`. THEMES_SHEET R1 default; REPLAN section B. |
| 2 | Q-DESIGNER: When one operative dies in | DEFAULT | The other lanes continue and the dead lane is DARK. THEMES_SHEET R2 default; REPLAN G Q24.1 and R4. The Q24.1 netrun abandonment applies per lane, not to the whole run. |
| 3 | Q-DESIGNER: Should the lead limit be | DEFAULT | 2 layers (`hq_lead_limit`). THEMES_SHEET R3; REPLAN G (R1). |
| 4 | Q-DESIGNER: Should lane effects on `dispatch_core` | DEFAULT | The three proposed starts (`hq_lane_effects`). THEMES_SHEET R4 default; REPLAN section B. |
| 5 | Q-DESIGNER: Should an operative's route HP | DEFAULT | Route HP carries with a 20 percent heal (`hq_throw_heal_pct`). THEMES_SHEET R5 default; REPLAN G. |

## 6. Reconciliation notes

- The draft says "Q34 decided". Both agree. The resolve order is ROOF, STREET, SEWER, and the added key `campaign_config.hq_lane_ids` records it.
- Q24.1 ("the active netrun is abandoned") against the draft's "run continues for the remaining lanes". Choice: REPLAN section B ("dead lane is DARK") wins. A lane's netrun ends for that operative, and the HQ run continues on the other lanes.
- Q24.1 and raids: the draft's raid rule 20 matches. Raids never kill operatives; RD-03 pins it.
- Draft §5 says "Heat for the death follows GDD 4.2". Kept as written; the 10 + tier Heat is a GDD value, not a new key.
- The draft's `lane_effects` list ROOF "enemy resistance −2 (min 0)". Q16 gives every fight resistance, so the effect is meaningful. Kept as the draft says, floored at 0.
- The STREET effect "first-phase hub heal off" matches the Genome Core-style hub rules in R2. It depends on the boss pass defining a first-phase hub heal on `dispatch_core`. If the boss has none, the effect is a no-op (the simplest option, noted for WH-33).
- The draft says the save version bumps by 1. This table keeps it additive defaults inside the WH-02 corp_theme block; any real bump follows WH-02's migration, and old saves are dropped per D3.
- The draft §6 state-name table renames `lane_pos` to `lane_layer[3]` and `lane_node[3]`. These are the same data as `HqStrikeState.lanes[].layer` and `.node_id`, so no extra save field is added.
- The art-plan names `countered_room`, `stall_tokens`, `relay_events[]`, the Exploit flags and `dark_lane[3]` (merged into DARK) are not state here.
- DROPPED KEY `campaign_config.hq_seq_steps` as two separate keys: the draft lists two rows under one key name, so this table holds one array `[3, 5]` under that name.
- DROPPED KEY `campaign_config.lanes_required`: the draft's §1 prose key is replaced by the config path `campaign_config.hq_lanes_required` in §4.
- DROPPED KEY `campaign_config.hq_lane_node_weights` as three per-lane keys: kept as one table-valued key.
- The earlier HQ draft's relay, Counter, STALL, Hack puzzle, per-Exploit lane effects and parked-support passives stay retired, as the draft says. No config keys exist for them.
- THROW heal order: heal first, then lane effects, then the finale is created. This follows draft rule 14 and is tested as one action.
- The lead limit excludes parked, ARMED and DARK lanes from the minimum, per draft rules 6, 7 and 11.
- If one living lane is ARMED and the others are not, `step` is computed only over the unARMED living lanes. The draft is silent when all remaining lanes are ARMED; there THROW enables and `seq` shows 3 on THROW.
- Focus controls for the finale: click a wheel or keys 1-3 (REPLAN G). They are UI only and need no config key.
- Raid delay rule: start delay = the longest of the three path lengths minus the threat's own path length. This uses the existing threat start-delay field, so no new raid key is needed.
- The mini-boss and raid hook (WH-31): the draft has no mini-boss content, only the end-room enemy reveal for scouted lanes. This table feeds the reveal and raid hook only.
- The Sync Strike boss's phases, buffs and enrage are out of this table; they belong to WH-32 and WH-33.
- Lead-limit refusal text and all player-facing strings are TextDb keys under `theme.rebel_cell.*` in US English.
- Slice rows fed: 2.16 (WH-30), 2.17 (WH-31), 2.18 (WH-32), 2.19 (WH-33), 2.20 (NA-33 and NA-32, display of `seq`, `pulse`, `switch_state`, `sync_state`).
- N-system dependencies: N3, N4, N5, N6, N18, N20 (boss pass) and the new multi-operative netrun session; the fallback of one operative walking three lanes in sequence loses simultaneity but keeps the lead limit.
