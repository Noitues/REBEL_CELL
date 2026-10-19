<!-- WH-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01NoiieatK3meY6YPMnq3LnX, custom_id wh01__orbital; status ok; tokens in 12138 cache-write 0 cache-read 34418 out 4218; cost $0.037. DRAFT. -->

# Orbital: WH-01 table

## 1. Config keys

| key | default | unit / note | source |
|---|---|---|---|
| `campaign_config.street_dark_nodes` | 1 | dark fight nodes per street netrun, placed in layers 3-6 | draft §4; REPLAN 2.22 |
| `campaign_config.street_dark_every` | 3 | DARK turn cadence in street dark fights (turns 1, 4, 7, ...) | draft §4 |
| `campaign_config.hq_dark_pattern` | [0, 1] | `layer mod 4` residues that are dark at the HQ | draft §4 |
| `campaign_config.hq_dark_every` | 2 | DARK turn cadence in HQ dark fights (turns 1, 3, 5, ...) | draft §4 |
| `campaign_config.uplink_lit_layers` | 2 | layers lit after an Uplink Dish clear | draft §4 |
| `campaign_config.hq_uplink_count` | 3 | Uplink Dish nodes per HQ run | draft §4; REPLAN 2.21 |
| `campaign_config.raid_dark_radius` | 1 | hops from the entry Site's node that form the Dead Zone | draft §4 |
| `campaign_config.dark_layer_min` | 3 | first layer eligible for the street dark node | added by REPLAN 2.22 (draft's "layers 3-6" made a key) |
| `campaign_config.dark_layer_max` | 6 | last layer eligible for the street dark node | added by REPLAN 2.22 |
| `campaign_config.dark_pattern_modulus` | 4 | the `mod` in the HQ dark pattern | added by REPLAN 2.22 (so the pattern holds no literal) |
| `campaign_config.dark_turn_first` | 1 | the first DARK turn index in a dark fight | added by REPLAN 2.22 (turns 1, 4, 7) |

## 2. State and save fields

| object | field | type | save impact |
|---|---|---|---|
| NetrunState | `dark_nodes` | Array[StringName] (node ids, sorted by id) | additive default [] (corp_theme block, WH-02) |
| NetrunState | `lit_until_layer` | int (HQ only) | additive default 0 (corp_theme block, WH-02) |
| RaidState | `dark_nodes` | Array[StringName] (sorted by node id) | additive default [] (corp_theme block, WH-02); recomputable from the entry Site and graph |
| CombatState | `nudge_locks` | existing N7 field, source `blackout` | none beyond N7 |
| derived (not saved) | `dark_turn(turn_index, every)` | bool, pure function of `turn_index`, `dark_turn_first` and the cadence | none |
| derived (not saved) | `layer_signal(layer, lit_until_layer)` | enum LIT / DARK | none |
| derived (not saved) | `raid_dark(node)` | bool, BFS from the entry node to `raid_dark_radius` hops | none |
| derived (not saved) | `dark_turn_list` | Array[int], the DARK turns shown on the turn track | none |

The dark node pick uses the existing netrun map stream (no new RNG). Ties break by content id, then node id.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| Map, dark node | `theme.orbital.node_dark`: "NO SIGNAL: free nudge locked on DARK turns" | none |
| Map, HQ dark layer tint | `theme.orbital.layer_dark`: "DARK LAYER: DARK turns {every_n}" | none |
| Map, lit layer | `theme.orbital.layer_lit`: "LIT: uplink restored through layer {n}" | none |
| Turn track | `theme.orbital.turn_dark`: "DARK" mark on turns {list} | none |
| Locked nudge button | `theme.orbital.nudge_locked`: "BLACKOUT: free nudge locked this turn" | none |
| Uplink Dish node | `theme.orbital.dish`: "UPLINK DISH: clear to light the next {n} layers" | none |
| Dark Mainframe | `theme.orbital.shop_closed`: "SHOP CLOSED: no signal" | none |
| Raid setup, dark node | `theme.orbital.raid_dark`: "DEAD ZONE: assets can't be placed or moved here" | none |
| Raid placement refusal | `theme.orbital.raid_refuse`: "DEAD ZONE: {node} is dark" | none |

Nothing is random, so no "?" appears anywhere.

## 4. Tests

| name | tier | assert |
|---|---|---|
| `test_dark_turn_locks_nudge` | fast | In a street dark fight the free nudge on turn 1 is refused with reason `blackout`, cards still work, and turn 2 allows it. |
| `test_street_dark_cadence` | fast | Turns 1, 4, 7 are DARK and turns 2, 3, 5, 6 are not, with `street_dark_every` read from config. |
| `test_hq_dark_cadence` | fast | HQ dark fights are DARK on turns 1, 3, 5, and a lit layer has none. |
| `test_street_dark_node_placement` | fast | Exactly `street_dark_nodes` fight node falls in layers `dark_layer_min`..`dark_layer_max`, and it is flagged before entry. |
| `test_hq_dark_layers` | fast | Layers with `layer mod 4` in {0, 1} are DARK. |
| `test_dark_schedule_matches_preview` | fast | The turn track's DARK list equals the locks actually applied (preview equals result). |
| `test_uplink_dish_lights_next_two_layers` | fast | After a dish clear, `lit_until_layer` is set and the next `uplink_lit_layers` layers produce no locks. |
| `test_uplink_count` | fast | An HQ run has `hq_uplink_count` Uplink Dish nodes, and each is a dark fight. |
| `test_dark_mainframe_closed` | fast | A Mainframe on a dark layer refuses the shop with its reason, and one on a lit layer opens. |
| `test_only_free_nudge_locked` | fast | On a DARK turn nudge cards, paid nudges and other card effects still work (O1 default). |
| `test_sandbox_never_ignored` | fast | No Orbital theme effect bypasses SANDBOX (O2). |
| `test_raid_dark_nodes_refuse_placement` | fast | Placing or moving an asset on a dark node is refused, and the projection is unchanged. |
| `test_raid_dead_zone_radius` | fast | The dark set equals the entry node plus nodes within `raid_dark_radius` hops, and it is a pure function of the entry Site and graph. |
| `test_raid_own_nodes_only` | fast | The Dead Zone affects only player nodes, never neutral cleared Sites (O3). |
| `test_raid_builtin_defenses_work` | fast | Built-in defenses on dark nodes fire normally. |
| `test_raid_no_operative_death` | fast | No operative is killed in a raid (Q24.1). |
| `test_zero_hp_operative_lost` | fast | An operative at 0 HP in a dark fight is lost, the netrun is abandoned and the raid is unchanged (Q24.1). |
| `test_blackout_turn_lifecycle` | fast | The lock is removed at end of turn and reapplied on the next DARK turn start (Q31). |
| `test_dark_flags_deterministic` | full | The same seed gives the same dark nodes, before and after save and reload. |
| `test_dark_sweep_numbers_from_config` | full | A sweep with altered config values changes the cadence and radius, and no literal in code matches a theme number. |

## 5. Q-DESIGNER disposition

| # | draft line (first 6 words, verbatim) | DEFAULT or DROPPED | text |
|---|---|---|---|
| 1 | Q-DESIGNER: Do you want the blackout | DEFAULT | Blackout (A) is the theme: overnight default and REPLAN §B, over the draft's recommendation B. |
| 2 | Q-DESIGNER: May a theme lock the | DEFAULT | O1: only the free own-wheel nudge on DARK turns is locked, with no lock beyond it (REPLAN §G; DECISIONS overnight defaults). |
| 3 | Q-DESIGNER: Should Orbital strikes be allowed | DEFAULT | O2: never ignore SANDBOX (overnight default; Q39). It is also moot because the strike option B is retired. |
| 4 | Q-DESIGNER: In raids, should the theme | DEFAULT | O3: own nodes only (overnight default; REPLAN §B). |
| 5 | Q-DESIGNER: Is the HQ allowed to | DEFAULT | O4: the full form is at the HQ, and street runs get one flagged dark fight (overnight default). |
| 6 | Q-DESIGNER: Do you want a Debris-style | DROPPED | Concerns option C, which is retired (REPLAN retire list). O5 is also answered: no permanent run cost. |

## 6. Reconciliation notes

- The draft's ranked recommendation (B first) is overruled: the designer's stated leaning plus the overnight default pick A, with relays (Uplink Dishes) as the escape.
- Options B, C and D are retired. Their section 8 text is advice only and builds nothing.
- Draft rule 4 says DARK turns are "1, 3, 5, ... (one turn in two)". REPLAN 2.22 says "every second turn". These agree, and `hq_dark_every` = 2 starts at `dark_turn_first`.
- Added keys: `dark_layer_min`, `dark_layer_max`, `dark_pattern_modulus` and `dark_turn_first`, so the draft's literals (layers 3-6, mod 4, turn 1) live in config. The first two are the simplest option behind config.
- The draft's risk line cites "Q26 spirit". Escape = Uplink Dishes, which also light 2 layers.
- The draft's N7 fallback (−1 RAM income on DARK turns) is DROPPED as a build target. N7 exists in rc.gd (`LOCK_NUDGE`), so no fallback is needed.
- Draft rule 2 locks the "own-wheel nudge". It is the free nudge only (O1 default), so paid nudges and nudge cards still work.
- Q31 binds the lock lifecycle: locks are removed at end of turn, and a DARK turn reapplies its lock at turn start.
- The "dark" Mainframe is closed, so no shop opens. It consumes no stream and uses the layer signal only.
- Raid: the Dead Zone hits the player's own nodes only (O3). Neutral cleared Sites are not locked. Operatives are never killed in raids (Q24.1).
- A cleared Uplink Dish sets `lit_until_layer` = dish layer + `uplink_lit_layers`. Dishes on an already lit layer still count as dark fights, and the later value wins (simplest option; no stacking).
- The map-generation pick of the street dark node uses the existing netrun map stream. Ties break by content id, then node id.
- The HQ tint and dish art need the art answers listed in the draft §6 (`dark`, `signal`, `lit_until_layer`, `raid_dark`, `dark_turn`). There is no art-pass plan for this corp.
- `RaidState.dark_nodes` is saved as an additive cache but is always recomputable. A mismatch on load is resolved by recomputing.
- DROPPED KEY `campaign_config.dark_fallback_ram_penalty`: it was only the retired N7 fallback and was never a named config key in the draft, so no lint match is needed.
- Feeds W2 slices: 2.21 WH-40 + NA-33 (Uplink Dish nodes, `hq_uplink_count`), 2.22 WH-41 (street and HQ rules), 2.23 WH-42 (raid Dead Zone), 2.24 NA-32 (HQ scene tint).
