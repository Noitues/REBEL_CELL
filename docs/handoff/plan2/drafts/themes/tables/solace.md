<!-- WH-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01NoiieatK3meY6YPMnq3LnX, custom_id wh01__solace; status ok; tokens in 16215 cache-write 34418 cache-read 0 out 5630; cost $0.087. DRAFT. -->

# Solace: WH-01 table

## 1. Config keys

| key | default | unit / note | source |
|---|---|---|---|
| `campaign_config.bloom_start_gap_milli_by_tier` | [4000, 3500, 3000, 2500] | thousandths of a layer, T1..T4 | draft §4 |
| `campaign_config.bloom_hq_start_gap_milli` | 3000 | thousandths of a layer | draft §4 |
| `campaign_config.bloom_pace_node_milli_by_tier` | [500, 600, 650, 700] | front advance per node entered, T1..T4 | draft §4 |
| `campaign_config.bloom_hq_pace_node_milli` | 700 | front advance per HQ node entered | draft §4 |
| `campaign_config.bloom_pace_turn_milli` | 100 | front advance per combat turn, applied at fight end | draft §4 |
| `campaign_config.bloom_pace_cross_milli` | 500 | extra front advance for an HQ ACROSS move | draft §4 |
| `campaign_config.bloom_dose_push_milli` | 1000 | front pushed back per dose | draft §4 |
| `campaign_config.bloom_dose_price` | 15 | Cycles per dose (Mainframe, Terminal option) | draft §4 |
| `campaign_config.bloom_max_gap_milli` | 5000 | gap clamp after a dose | draft §4 |
| `campaign_config.bloom_free_doses_t1` | 1 | doses granted at T1 netrun start | draft §4; S5 default (keep) |
| `campaign_config.bloom_close_gap_milli` | 2000 | CLOSE band ceiling (gap ≤) | draft §4 |
| `campaign_config.bloom_catch_gap_milli` | 1000 | CATCHING band ceiling (gap ≤) | draft §4 |
| `campaign_config.bloom_virus_pace_pct` | 75 | percent multiplier on node and turn pace with the Virus key; floor division, minimum 1 | draft §4 |
| `campaign_config.raid_infection_start_bp_by_band` | [0, 500, 1000, 1500, 2000] | basis points; COOL, NOTICED, FLAGGED, HUNTED, PURGE | draft §4 |
| `campaign_config.raid_infection_bp_base` | 50 | basis points per step | draft §4 |
| `campaign_config.raid_infection_bp_per_threat` | 100 | basis points per living threat per step | draft §4 |
| `campaign_config.raid_infection_lost_bp` | 10000 | CITY LOST threshold (equals the full scale; was a literal in the draft) | added by the "numbers only from config" test rule |
| `campaign_config.bloom_exempt_boss_turn_cost` | true | mini-boss and boss fights add no turn pace; node entry still applies | added by S3 default (REPLAN §B) |
| `campaign_config.bloom_heat_affects_street` | false | Heat never changes street pace | added by S2 default |

## 2. State and save fields

| object | field | type | save impact |
|---|---|---|---|
| `BloomState` (new sub-object of `scripts/state/run_state.gd`) | `front_milli` | int | additive default (corp_theme block, WH-02) |
| `BloomState` | `layer_milli` | int | additive default (corp_theme block, WH-02) |
| `BloomState` | `doses_taken` | int | additive default (corp_theme block, WH-02) |
| `BloomState` | `caught` | bool | additive default (corp_theme block, WH-02) |
| `BloomState` | `enabled` | bool (false when absent, non-Solace, or the pace table gives 0) | additive default (corp_theme block, WH-02); an old save loads disabled and DORMANT |
| `BloomState` | `doses_held` | int (free doses and bought doses not yet used) | additive default (corp_theme block, WH-02) |
| existing raid state object under `scripts/state/` | `infection_bp` | int 0..10000 | additive default 0 (corp_theme block, WH-02); resets per raid |
| derived (not saved) | `bloom_gap_milli` | int = layer_milli − front_milli | none |
| derived (not saved) | `bloom_state` | enum DORMANT / CREEPING / CLOSE / CATCHING / CAUGHT from gap bands | none |
| derived (not saved) | `bloom_room_infected` | bool per node, layer ≤ floor(front_milli / 1000); skipped branches included | none |
| derived (not saved) | `raid_infection_pct` | int = infection_bp / 100 | none |
| derived (not saved) | `raid_infection_rate_bp` | int = base + per_threat × living threats | none |
| derived (not saved) | `raid.steps_to_lost` | int, −1 if never | none |

No RngService stream is used. Integer thousandths throughout. Ties by content id then node id. If N8 bumps the save version, fold these fields into that bump; otherwise no bump.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Route chip, non-fight node (`theme.solace.chip_gap`) | `FRONT -{gap}` | none |
| Route chip, HQ ACROSS (`theme.solace.chip_cross`) | `FRONT -{gap} (ACROSS +{cross})` | none |
| Route chip, fight node (`theme.solace.chip_fight`) | `FRONT -{gap} → ?` | turn cost after the fight |
| Fight chip tooltip (`theme.solace.tip_turn`) | `-0.1 per turn` (exempt fights: `NO TURN COST`) | none |
| Caught warning (`theme.solace.warn_caught`) | `CAUGHT` | none |
| Dose option (`theme.solace.dose_option`) | `ANTIVIRAL {price} CYCLES: FRONT -{gap} → -{gap_after}` | none |
| Ward rest (`theme.solace.rest_dose`) | `WARD REST: HEAL + FRONT -{gap} → -{gap_after}` | none |
| Fight result (`theme.solace.result`) | `FRONT -{a} → -{b}` | none |
| TIDE gauge state label (`theme.solace.state_<name>`) | `CREEPING` / `CLOSE` / `CATCHING` / `CAUGHT` | none |
| HQ Intel ladder (`theme.solace.intel_gap`) | `FRONT -{gap}` on every candidate move (without Intel, only within the read horizon) | none |
| Raid setup, population (`theme.solace.raid_pop`) | `POPULATION INFECTED {nn}%` | none |
| Raid setup, outcome (`theme.solace.raid_outcome`) | `CITY LOST at step {n}` or `holds at {nn}%` | none |
| Raid rate chip (`theme.solace.raid_rate`) | `+{n}%/step` | none |
| Raid end text (`theme.solace.city_lost`) | `THE CITY IS INFECTED. ONLY SOLACE HAS THE CURE.` | none |

Fight-end turns are the only unknown, and they show as "?" in the route chip. All other values are exact.

## 4. Tests

| name | tier | assert |
|---|---|---|
| `test_bloom_gap_after_node_entry` | fast | Gap changes by layer step ×1000 − pace_node (tier table) |
| `test_bloom_combat_turns_advance_front_at_fight_end` | fast | Front is frozen during a fight; it advances turns × pace_turn at the end |
| `test_bloom_exempt_boss_fights_no_turn_cost` | fast | Mini-boss and boss fights add 0 turn pace while the exempt key is true; normal, elite and Rack fights do add it |
| `test_bloom_caught_at_gap_zero` | fast | Gap ≤ 0 after node entry or fight end latches `caught` |
| `test_bloom_caught_is_operative_lost_q24_1` | fast | CAUGHT loses the operative with everything unbanked, abandons the netrun, leaves the raid unchanged, applies 10 + tier Heat |
| `test_bloom_never_catches_mid_fight` | fast | No CAUGHT between a fight's first and last turn |
| `test_bloom_state_bands` | fast | The state is exact at each boundary (close_gap, catch_gap, 0, DORMANT before the first node) |
| `test_bloom_dose_push_and_clamp` | fast | A dose pushes `dose_push` and the gap is clamped to `max_gap` |
| `test_bloom_t1_free_dose_and_wide_gap` | fast | T1 starts with the config gap and `free_doses_t1` doses |
| `test_bloom_hq_shared_front_both_towers` | fast | One front value; rung r is infected on both towers at the same moment, including skipped branches |
| `test_bloom_hq_across_cost_preview_equals_result` | fast | The ACROSS chip equals the real front change |
| `test_bloom_ward_rest_calls_dose_push` | fast | HQ REST applies `dose_push` once, with the same clamp |
| `test_bloom_intel_reveals_whole_ladder` | fast | Intel shows the exact gap for every candidate move; the preview equals the result |
| `test_bloom_virus_scales_pace` | fast | The multiplier is applied once per advance, rounded down, minimum 1 |
| `test_bloom_breach_has_no_effect` | fast | The Breach key changes no Bloom number |
| `test_bloom_crown_frozen_boss_fight` | fast | The caught check runs on crown entry; no front change during the Genome Core fight |
| `test_bloom_heat_does_not_change_street_pace` | fast | Pace is identical across Heat bands |
| `test_bloom_deterministic_same_seed` | fast | The same seed and the same action list give an identical front and `BloomState` hash |
| `test_bloom_disabled_on_other_corporations` | fast | `enabled` is false for non-Solace corporations |
| `test_bloom_save_roundtrip_midnetrun` | full | A mid-netrun save and load gives an identical `BloomState`; an old save loads disabled; a mid-fight quit and resume keeps the front frozen |
| `test_raid_infection_rises_per_step_and_threat` | fast | The per-step rise equals base + per_threat × living threats; a threat on a node counts like one in transit |
| `test_raid_infection_never_decreases` | fast | Monotonic across 30 steps, including after threats die |
| `test_raid_infection_start_by_band` | fast | A new raid starts at the Heat band's value |
| `test_raid_city_lost_ends_campaign` | full | 10000 bp ends the raid CITY LOST and the campaign as lost through the BREACHED path with the Solace text |
| `test_raid_infection_preview_equals_result` | fast | The setup projection (end % and loss step) equals the played-out result |
| `test_raid_infection_resets_per_raid` | fast | Infection does not carry to the next raid |
| `test_operatives_never_killed_in_raid_infection` | fast | CITY LOST and every infection step change no operative state |
| `test_raid_thirty_steps_holds` | fast | A raid that runs 30 steps below the threshold ends CELL HOLDS |
| `test_bloom_no_magic_numbers` | fast | Bloom and raid-infection code read only the config keys above |
| `test_bloom_no_retired_keys` | fast | The lint rejects debt and tower_pressure keys and the retired toll keys |

## 5. Q-DESIGNER disposition

| # | draft line (first 6 words, verbatim) | DEFAULT or DROPPED | text |
|---|---|---|---|
| 1 | Q-DESIGNER: Should the raid infection carry | DEFAULT | S1 default: reset per raid (THEMES_SHEET; REPLAN §B). |
| 2 | Q-DESIGNER: Does the Heat band also | DEFAULT | S2: Heat affects raids only (DECISIONS overnight defaults; REPLAN §G). The street pace has no Heat input. |
| 3 | Q-DESIGNER: Is a mini-boss or elite | DEFAULT | S3: bosses and mini-bosses are exempt from the turn cost. Elites keep it (DECISIONS overnight defaults; REPLAN §B). |
| 4 | Q-DESIGNER: Do you want the HQ | DROPPED | S4: debts are cut, and their keys are removed (REPLAN retire list). |
| 5 | Q-DESIGNER: Should the T1 free dose | DEFAULT | S5: keep the T1 free dose (DECISIONS overnight defaults). |
| 6 | Q-DESIGNER: Is Virus the right Exploit | DEFAULT | S6: Virus slows the pace, Intel reveals the ladder, Breach has no effect (REPLAN §B). |

## 6. Reconciliation notes

- S3 ruling changed the draft: mini-boss and boss fights add no turn pace (draft rule 3 counted them). Added key `campaign_config.bloom_exempt_boss_turn_cost`. Elites still pay.
- S2 ruling: Heat touches raids only. Added key `campaign_config.bloom_heat_affects_street` (false), a guard for the lint and test.
- S4 ruling: debts and the pink halo pips are cut. Nothing in the draft's key list used them, so no key is dropped, and the lint rejects leftovers.
- Retired HQ tolls (Co-pay, Referral, Audit, Quarantine) are replaced by ACROSS cost (REPLAN retire list).
- The draft's literal 10000 bp threshold became `campaign_config.raid_infection_lost_bp`, which is the simplest way to meet "numbers only from config".
- The draft's state field `bloom.doses_taken` is kept as telemetry. I added `doses_held`, because the free and bought doses need an inventory. The draft was silent, so I took the simplest option. Where the held doses live (BloomState versus the run's items) is a build-time call.
- Draft rule 13 and REPLAN agree that the Genome Core fight is frozen. CAUGHT is checked on crown entry only.
- The draft's §6 art answers (derived `bloom_room_infected`, `raid_infection_rate_pct`) became derived fields. The rate is stored as bp.
- The draft's `raid.steps_to_lost` is kept as a derived, unsaved value.
- Raid view: the draft's art answer 10 (no Grid scar) means no extra raid state is added.
- `tower_pressure` is dropped (draft rule 14); it has no key in the draft.
- Q24.1: CAUGHT uses the existing operative-loss flow. Raids never kill operatives, so CITY LOST touches no operative.
- Conflict: the draft says the preview shows `FRONT -n.n → ?` for fights, while the REPLAN row says "no '?' (nothing is random)". Choice: the turn count of a future fight is unknown, so "?" stays on the fight-end part only (Q19). Every gap after a node entry is exact.
- Conflict: the draft's "Dose price (Cycles)" and the N18 reward row. Choice: the dose is a config-priced shop and event row, with a hard-coded shop slot as fallback.
- Save: fold into the N8 bump if it lands first; otherwise additive via the WH-02 corp_theme block.
- Dependencies from the draft: N2 (tier tables), N5 (Exploit modifiers as `ExploitData` fields), N18 (dose row, with fallback), D4 REST; N16 not needed.
- THEMES_SHEET S1-S6 are all resolved in section 5 with no unresolved conflicts, and REPLAN §G wins on S2-S6.
- Feeds W2 rows: 2.7 WH-11 (street, HQ and Bloom rules), 2.8 WH-12 (raid infection), 2.9 NA-32 (HQ visuals read `front_milli`, `bloom_state`, `bloom_room_infected`).
