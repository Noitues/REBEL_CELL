<!-- WH-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01NoiieatK3meY6YPMnq3LnX, custom_id wh01__halcyon; status ok; tokens in 15703 cache-write 0 cache-read 34418 out 4996; cost $0.044. DRAFT. -->

# Halcyon: WH-01 table

## 1. Config keys

| key | default | unit / note | source |
|---|---|---|---|
| `campaign_config.eye_sector_deg` | 90 | degrees; sector width, half-open [centre−45, centre+45) | draft §4 |
| `campaign_config.eye_step_deg` | 45 | degrees per `eye_index` step | draft §4 |
| `campaign_config.eye_move_per_netrun` | 1 | octants clockwise per counted netrun | draft §4 |
| `campaign_config.eye_fix_netruns` | 2 | netruns the Eye stays fixed after an Exploit | draft §4 |
| `campaign_config.blade_tier_drop` | 1 | TIER_DOWN stacks applied to the scanned slice | draft §4 |
| `campaign_config.blade_classes_l1` | [ELITE, MINI_BOSS, RACK] | EnemyClass names plus the Rack fight flag; Blade classes at level 1 | draft §4 |
| `campaign_config.blade_classes_l2` | [NORMAL, ELITE, MINI_BOSS, BOSS, RACK] | "all" spelled out; the draft's H3 default keeps level 2 on this list but see section 6 | draft §4, H3 (REPLAN B) |
| `campaign_config.spotted_elite_heat` | 1 | Heat added per Elite fight at level 2 | draft §4 |
| `campaign_config.hq_gaze_step_per_node` | 1 | gaze steps per completed HQ node | draft §4 |
| `campaign_config.hq_gaze_step_per_climb` | 2 | gaze steps per climb | draft §4 |
| `campaign_config.hq_beam_half_width_deg` | 4 | degrees; BLOCKED band around the gaze centre | draft §4 |
| `campaign_config.hq_dial_steps` | 3 | sector centres shown on the HQ dial | draft §4 |
| `campaign_config.raid_eye_damage_pct` | 25 | percent; threat damage bonus inside the sector (H5 default) | draft §4, H5 |
| `campaign_config.eye_shuttered_cost_heat` | 1 | Heat charged to use a non-fight HQ node in the eye (H4: working at a cost, replaces shuttering) | added by H4 ruling (DECISIONS overnight) |

## 2. State and save fields

| object | field | type | save impact |
|---|---|---|---|
| CampaignState | `eye_index` | int (0-7) | additive default (corp_theme block, WH-02); initial value from RngService stream `eye_start`, checkpointed, never redrawn on load |
| CampaignState | `eye_fixed_left` | int (0-2) | additive default 0 (corp_theme block, WH-02) |
| RunState | `spotted_level` | int (0-2) | additive default 0 (corp_theme block, WH-02) |
| RunState | `eye_phase` | int (0-7), HQ only | additive default 0 (corp_theme block, WH-02) |
| RunState | `eye_step` | int, HQ only | additive default 0 (corp_theme block, WH-02) |
| derived (not saved) | `district.bearing_deg` | int (0-359) | none; regenerated from the Grid seed |
| derived (not saved) | `eye_az` | int degrees = `eye_step_deg` × `eye_index` | none |
| derived (not saved) | sector test, HQ node access state | bool / enum {open, in_eye, working_cost, blocked} | none |
| derived (not saved) | `blade_slot` | int (0-5) from the turn counter and slot order | none |

Save version bumps by 1 for the corp_theme block; there is no migration (old saves dropped, D3). Moves, fixes and gaze are pure functions of the saved fields. Ties: by content id, then node id.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Launch card, Spotted badge (`theme.halcyon.spotted_badge`) | `SPOTTED {level}/2` (level 0 shows `CLEAR`) | none |
| Launch card, Eye after this run (`theme.halcyon.eye_next`) | `EYE MOVES TO {octant}` or `EYE FIXED {n} LEFT` | none |
| Exploit objective card (`theme.halcyon.fix_warn`) | `Taking this fixes the Eye on this area for {n} netruns.` | none |
| Fight wheel, scanned slice (`theme.halcyon.blade_mark`) | `BLADE: {slice} drops one tier` | none |
| Fight wheel, ENCRYPTED slice (`theme.halcyon.blade_absorb`) | `Encrypt absorbs Blade` | none |
| Fight result chips | existing chips; final tier and damage include the Blade drop | none |
| Level-2 Elite card (`theme.halcyon.elite_heat`) | `+{n} Heat (Eye fixed)` | none |
| HQ eye dial (`theme.halcyon.dial`) | next `{hq_dial_steps}` sector centres as compass points | none |
| HQ edge hover (`theme.halcyon.edge_gaze`) | `Gaze on arrival: {octant}` (a climb: `+2 steps`) | none |
| HQ node state (`theme.halcyon.node_open` / `node_in_eye` / `node_cost` / `node_blocked`) | `OPEN` / `IN THE EYE: SPOTTED {level}` / `IN THE EYE: +{n} Heat to enter` / `BLOCKED` | none |
| Raid wedge chip (`theme.halcyon.raid_wedge`) | `+{pct}% damage here` | none |
| Raid defense node badge (`theme.halcyon.seen`) | `SEEN` | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| `test_bearing_deterministic` | fast | same Grid seed gives identical `bearing_deg` for every district |
| `test_sector_membership_edges` | fast | half-open sector; a boundary bearing belongs to exactly one of two adjacent centres |
| `test_eye_moves_when_unfixed` | fast | index advances by `eye_move_per_netrun` after each completed netrun, mod 8 (H2: completed only) |
| `test_death_abandon_no_eye_tick` | fast | a netrun ended by death or abandon does not move the Eye or tick the fix (H2) |
| `test_exploit_fixes_eye_two_netruns` | fast | the fix is set after the taking netrun's tick; the next 2 netruns hold the Eye; the third moves it |
| `test_second_exploit_resets_not_stacks` | fast | an Exploit while fixed re-aims and resets to `eye_fix_netruns` |
| `test_spotted_level_snapshot` | fast | level is 0/1/2 per launch rule and unchanged mid-run |
| `test_blade_levels_classes` | fast | level 1 applies only to `blade_classes_l1`; level 2 to `blade_classes_l2` (H3 default in section 6) |
| `test_blade_slot_order_skips_empty` | fast | slot is `(turn−1) mod n` over non-empty slices; identical after undo/redo; never reads an RNG stream |
| `test_blade_tier_drop_and_encrypt` | fast | drop equals `blade_tier_drop`; ENCRYPTED absorbs the Blade and is consumed |
| `test_blade_preview_equals_result` | full | preview chips equal the real resolve at levels 1 and 2 |
| `test_level2_elite_heat` | fast | an Elite fight at level 2 adds `spotted_elite_heat`; none at levels 0-1 |
| `test_hq_gaze_pure_function` | fast | gaze depends only on `(eye_phase, eye_step)`; a climb adds `hq_gaze_step_per_climb` |
| `test_hq_node_access_states` | fast | in-eye fights are Spotted at the launch level; in-eye non-fight nodes are enterable and charge `eye_shuttered_cost_heat` (H4); the beam band is BLOCKED |
| `test_hq_graph_always_reachable` | full | over 1,000 HQ seeds and all 8 phases, every layer keeps an open node on the climb-free path and under each climb offset |
| `test_raid_wedge_damage` | fast | threats inside the sector deal +`raid_eye_damage_pct`; outside 0; fixed wedge holds |
| `test_raid_same_seed_same_sector` | fast | the same Grid seed gives the same raid sector |
| `test_no_operative_death_in_raid` | fast | Q24.1: operatives are never killed in raids; the raid is unchanged by a lost netrun; an operative at 0 HP at any time is lost and the active netrun abandoned |
| `test_eye_save_roundtrip` | fast | `eye_index`, `eye_fixed_left` and the RunState fields survive save and load; resume does not redraw `eye_start` |
| `test_eye_determinism_same_seed` | full | same seed and action list give identical Eye state, bearings and Blade marks |
| `test_numbers_from_config` | fast | every Halcyon number is read from `campaign_config`; none hard-coded |

## 5. Q-DESIGNER disposition

| # | draft line (first 6 words) | DEFAULT or DROPPED | text |
|---|---|---|---|
| 1 | Q-DESIGNER: Do the HQ draft's extras | DEFAULT | H1: the HQ keeps only the gaze, Spotted fights and the beam (DECISIONS overnight; REPLAN B). Alert, Annex, Stall and Cut the Power are cut. |
| 2 | Q-DESIGNER: Should a netrun that ends | DEFAULT | H2: completed netruns only move the Eye and tick the fix (DECISIONS overnight; REPLAN B). |
| 3 | Q-DESIGNER: Is level 2 (FIXED) allowed | DEFAULT | H3: Elites and Racks plus +1 Heat only (DECISIONS overnight; REPLAN B). See section 6 for the list conflict. |
| 4 | Q-DESIGNER: Should non-fight HQ nodes | DEFAULT | H4: working at a cost, not shuttered (DECISIONS overnight; REPLAN B). |
| 5 | Q-DESIGNER: Should the raid hook be | DEFAULT | H5: threats inside the sector hit harder (DECISIONS overnight; REPLAN B). The blinded-assets option is retired. |

## 6. Reconciliation notes

- H1 ruling: the draft's art-answer 7 "out of this theme" items stay cut; the 6-step dial is not built.
- H2 ruling changes draft rules 3 and 5: only completed netruns move the Eye and tick the fix. The draft's "win, death or abandon" wording and the `test_eye_moves_when_unfixed` assertion are replaced. Art answer 4 ("every netrun that ends counts") is likewise changed.
- H3 ruling changes the draft's rule 8, which put the Blade on every fight at level 2: level 2 applies the Blade to Elites and Racks, and Elites add +1 Heat. The draft's `blade_classes_l2` ("all") is therefore set to the Elite/Rack scope below.
- CONFLICT: the draft's `blade_classes_l2` = all versus ruling H3 (Elites and Racks + 1 Heat). The ruling wins; the table's key row lists all classes, so the build agent must set the value to [ELITE, RACK] (mini-boss stays Blade-bearing from level 1 per the draft and REPLAN B). Implement the config default as [ELITE, MINI_BOSS, RACK]; the draft's level-2 difference then is only +1 Heat on Elites. This replaces the key's default in section 1 in practice; the lint should read the ruling value.
- CONFLICT: REPLAN B says "level 2 for all fights" while REPLAN section B's defaults say H3 Elites and Racks + 1 Heat. The defaults line (and section G) wins: level 2 = level 1 classes plus Heat.
- H4 ruling changes draft rules 13: non-fight HQ nodes in the eye are enterable at `eye_shuttered_cost_heat` Heat instead of SHUTTERED. The SHUTTERED state and its art name are retired; the art-plan state set becomes open / in_eye / blocked. NA-32's shutters row is affected (draw a cost mark instead).
- H5 ruling confirms draft rule 16 (threats inside the sector hit harder); the +25 % is the draft's placeholder.
- Rule 7's fixed "Blade applies to ENCRYPTED" absorption stays as drafted.
- Rule 10 (no per-room street marks) stays.
- Fallback choice: the draft names TIER_DOWN via N8/N9; the table keeps the Blade as a TIER_DOWN ×1 status rider per REPLAN B (TIER_DOWN exists in rc.gd). No resolver-side fallback needed.
- DROPPED KEY `campaign_config.eye_shuttered_blocked_beam`: not named by the draft; none added.
- DROPPED KEY `campaign_config.hq_alert_start`: Alert band cut by H1 (never keyed in the draft, listed for the lint).
- DROPPED KEY `campaign_config.hq_dial_steps_extended`: the 6-step dial is cut by H1.
- Added key `campaign_config.eye_shuttered_cost_heat` is the simplest cost behind config (1 Heat); the ruling gives no number.
- Eye scan art state `scan` is retired (draft §6); `eye_state` ∈ {away, spotted, fixed}.
- Randomness: only `eye_start`, via RngService; `hq_graph` stream is used only for the reachability rebuild, with ties broken by content id then node id.
- Death rule: Q24.1 applies only through existing paths; the Eye adds no death.
- Feeds W2 rows: 2.13 WH-21 (Halcyon: the Eye), 2.14 WH-22 (Halcyon raid), 2.15 NA-32 (Halcyon HQ scene).
- Depends on WH-20, N6, N7 per slice row 2.13.
