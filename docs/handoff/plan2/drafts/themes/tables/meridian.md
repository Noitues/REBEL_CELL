<!-- WH-01 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01NoiieatK3meY6YPMnq3LnX, custom_id wh01__meridian; status ok; tokens in 11782 cache-write 0 cache-read 34418 out 4416; cost $0.037. DRAFT. -->

# Meridian: WH-01 table

## 1. Config keys

| key | default | unit / note | source |
|---|---|---|---|
| `campaign_config.meridian.weight_firmware` | 1 | Load points per equipped Firmware | draft rule 1 |
| `campaign_config.meridian.weight_daemon` | 2 | Load points per Daemon | draft rule 1 |
| `campaign_config.meridian.weight_asset` | 2 | Load points per unbanked Armory asset | draft rule 1 |
| `campaign_config.meridian.capacity_base` | 5 | Capacity at Rank 0 | draft rule 2 |
| `campaign_config.meridian.capacity_per_rank` | 1 | Capacity per Rank | draft rule 2 |
| `campaign_config.meridian.capacity_tier_bonus` | [2, 1, 1, 0] | Capacity added by target tier T1..T4; the draft says "+2 at T1, tapering to 0 at T4", and the middle values are the simplest taper | draft section 4; middle values chosen (see section 6) |
| `campaign_config.meridian.over_resistance_cap` | 3 | Max player-wheel resistance from Over | draft rule 3; REPLAN G |
| `campaign_config.meridian.jettison_refund_pct` | 50 | Percent of the item's Cycles value refunded | draft rule 5; M1; REPLAN G |
| `campaign_config.meridian.station_capacity_penalty` | 2 | Capacity lost per Weigh Station passed | draft rule 6 |
| `campaign_config.meridian.weigh_station_layers` | [4, 7, 10] | HQ route layers holding a Weigh Station | draft rule 6; REPLAN 2.25 |
| `campaign_config.meridian.hub_load_divisor` | 3 | Boss hub resistance = floor(Load / divisor) | draft rule 8 |
| `campaign_config.meridian.raid_node_capacity` | 2 | Assets a defense node fires at full speed | draft rule 9 |
| `campaign_config.meridian.raid_overcap_delay_steps` | 1 | Steps each asset beyond capacity fires late | draft rule 9 ("one step later"); added to give the delay a config home |
| `campaign_config.meridian.jettison_value_firmware` | 30 | Cycles value used for the refund, per Firmware | added by simplest-option rule (the draft gives no item Cycles values) |
| `campaign_config.meridian.jettison_value_daemon` | 60 | Cycles value for a Daemon | added by simplest-option rule |
| `campaign_config.meridian.jettison_value_asset` | 40 | Cycles value for an unbanked asset | added by simplest-option rule |

## 2. State and save fields

| object | field | type | save impact |
|---|---|---|---|
| derived (not saved) | `load` | int, Σ item weights from the Firmware, Daemon and unbanked-asset lists | none |
| derived (not saved) | `capacity` | int, capacity_base + capacity_per_rank × Rank + capacity_tier_bonus[tier] − station penalty × stations passed + capacity_bonus | none |
| derived (not saved) | `over` | int, max(0, load − capacity) | none |
| derived (not saved) | `asset_overcap_count` | int per raid node, max(0, assets − raid_node_capacity); ties for which asset is late: by asset content id, then node id | none |
| derived (not saved) | `hub_resistance_from_load` | int, load / hub_load_divisor (integer division) | none |
| RunState | `capacity_bonus` | int, default 0; each Weigh Station passed subtracts the penalty (stored as a negative) | additive default (corp_theme block, WH-02) |
| RunState | `weigh_stations_passed` | PackedInt32Array of layers; the `weigh_station_state` {pending, passed} is read from it | additive default (corp_theme block, WH-02) |
| CombatantState | `start_resistance_from_load` | int, set at combat start to min(over, over_resistance_cap); reuses the WheelState resistance field on the player wheel (Q16/Q31 lifecycle) | none (combat state already saves resistance) |
| WheelState | `resistance` | int, reused on the player wheel | none |

No RNG is used anywhere in this theme.

## 3. Preview lines

| surface | exact text pattern | "?" parts |
|---|---|---|
| HUD Load chip | `theme.meridian.load_chip`: "LOAD {load}/{capacity}", amber when over > 0 | none |
| Load chip tooltip | `theme.meridian.load_tip`: "Over by {over}. Your wheel gets +{min(over, cap)} resistance each turn." (when over is 0: `theme.meridian.load_ok` "Within capacity.") | none |
| Player wheel at turn start | `theme.meridian.over_mark`: "+{n}" grease-pen mark (reuses the N21 mark) | none |
| Jettison button | `theme.meridian.jettison_btn`: "JETTISON {item}: +{cycles} Cycles, LOAD {load} to {load_after}" | none |
| Weigh Station node card | `theme.meridian.station_card`: "WEIGH STATION: capacity {capacity} to {capacity_after}" | none |
| Boss hub chip (HQ) | `theme.meridian.hub_resist`: "CUSTOMS SEAL +{n} (LOAD {load} / {divisor})" | none |
| Raid asset marker | `theme.meridian.raid_late`: "FIRES LATE: step +{delay}" | none |
| Raid node card | `theme.meridian.raid_cap`: "ASSETS {count}/{raid_node_capacity}" | none |

## 4. Tests

| name | tier | assert |
|---|---|---|
| `test_load_sums_item_weights` | fast | Firmware, Daemon and asset counts give the expected Load from the config weights |
| `test_capacity_formula_uses_rank_tier_and_station` | fast | capacity = base + per_rank × Rank + tier_bonus[t] + capacity_bonus |
| `test_over_capacity_sets_resistance_capped` | fast | Over 5 gives player resistance 3; Over 2 gives 2; Over 0 gives 0 |
| `test_player_resistance_refreshes_and_zeroes` | fast | The Q31 lifecycle: 0 at end of turn, regained at start of turn, the "+N" mark appears |
| `test_jettison_refund_and_load_drop` | fast | The refund equals value × jettison_refund_pct / 100 and Load drops by the item weight; the refund shown equals the refund applied |
| `test_jettison_only_at_mainframe_terminal_station` | fast | Jettison is refused elsewhere, with a reason |
| `test_load_is_derived_not_saved` | fast | The save has no `load`, and the value is recomputed on load |
| `test_weigh_station_penalty_persists_in_save` | full | Save and reload keeps `capacity_bonus` and the passed stations |
| `test_weigh_station_layers_l4_l7_l10` | fast | The HQ graph places a station at each configured layer; the preview shows the capacity after |
| `test_boss_hub_resistance_load_div_3` | fast | Load 8 gives the hub resistance floor(8/3) = 2, and it stays inside the boss class range (Q16) |
| `test_raid_overcap_fires_one_step_late` | full | A third asset on a node fires one step later; the projection equals the played result |
| `test_raid_overcap_tie_order` | fast | The late asset is chosen by content id, then node id |
| `test_meridian_deterministic_same_seed` | full | The same seed gives identical Load, resistance and raid projections |
| `test_meridian_preview_equals_result` | full | The chip, Jettison, station and raid-late previews match the applied values |
| `test_q24_1_zero_hp_abandons_netrun` | fast | An operative at 0 HP at any time is lost, the netrun is abandoned and the raid is unchanged; no raid code path kills an operative |
| `test_meridian_numbers_from_config` | fast | A lint finds no literal weight, capacity, cap, refund, penalty, divisor or raid values outside `campaign_config` |

## 5. Q-DESIGNER disposition

| # | draft line (first 6 words, verbatim) | DEFAULT or DROPPED | text |
|---|---|---|---|
| 1 | Q-DESIGNER: Which option do you want, | DROPPED | Already answered: Meridian = A PAYLOAD (DECISIONS overnight defaults; REPLAN section B). The merge idea (A plus D) is retired with the other options. |
| 2 | Q-DESIGNER: Should the theme be allowed | DEFAULT | M1 reward-leaning (THEMES_SHEET, DECISIONS overnight, REPLAN G): Jettison refund 50%, Over resistance capped at 3. The theme may cost some power but never punishes hard. |
| 3 | Q-DESIGNER: For option C, is a | DROPPED | Option C is retired; no slice builds from it. |
| 4 | Q-DESIGNER: For option B, should a | DROPPED | Option B is retired (M3 concerns only B). |
| 5 | Q-DESIGNER: For option D, may the | DROPPED | Option D is retired (M4 concerns only D). |

## 6. Reconciliation notes

- Only Option A is carried. Options B, C and D and their rules are retired (REPLAN retire list).
- The draft's first three of its rules were kept as written. Rule 4 now cites Q16/Q31 and N21 for the lifecycle and mark.
- M1 reward-leaning (overnight default and REPLAN G) fixes the refund at 50% and the Over cap at 3, as the draft already had.
- Added keys: `weigh_station_layers`, `raid_overcap_delay_steps` and the three `jettison_value_*` keys. The draft names a refund of 50% of an item's "Cycles value" but gives no values; the simplest option was chosen behind config. These values are placeholders for BAL-08.
- `capacity_tier_bonus` is written as an array indexed by target tier; the draft's "[t]" form is kept. Middle values [2, 1, 1, 0] are a guess at the taper, since the draft states only T1 = +2 and T4 = 0.
- Conflict on the HQ capacity penalty: the draft says each station "lowers Capacity by 2 for the rest of the run"; REPLAN agrees. It is stored as `capacity_bonus` (negative), which is saved; Load stays derived.
- Conflict on save impact: the draft says a "minor save-version bump"; the WH-02 plan puts new fields in an additive corp_theme block with defaults. The ruling wins: additive default, no version bump.
- The draft's `RunState.load` is described as "derived, not stored"; kept as derived (not saved).
- Hub resistance: the draft's Load ÷ 3 is kept (integer division). It must stay inside the boss class range of Q16 (5-6 for a boss); the REPLAN 2.25 note says "reads the combined formula", so the hub's authored base plus the Load term is clamped by the existing resistance caps. If no cap exists, none is added here (simplest option).
- Weigh Station Jettison (draft rule 7) reuses the same Jettison rule and the same keys; no separate key.
- A "NEW" dependency: player-side resistance wiring if WheelState's field is enemy-only. N21 supplies the lifecycle; this is data-only if the field is shared.
- The draft's Art answers (section 6) and its Reuse section are not table content. The state names `load`, `capacity`, `over`, `weigh_station_state`, `jettison_available`, `player_resistance` and `asset_overcap_count` are kept in section 2 where they have state.
- Q24.1 is added as a test only; the theme creates no new death. The draft is silent on it.
- Raid: the late firing uses the existing exact projection (draft); no new RNG, and the ordering is content id then node id.
- No dependency on N10, rim gates or enrage for the street or raid forms. The HQ graph (WH-50) depends on N10 per REPLAN 2.25.
- Language: all player-facing strings are US English and stored as TextDb keys `theme.meridian.*`.
- Feeds W2 slice rows: 2.25 (WH-50 + NA-33: station layers, hub resistance), 2.26 (WH-51: Load, capacity, Over resistance, Jettison, stations, hub), 2.27 (WH-52: raid node capacity and late fire), 2.28 (NA-32: HQ scene, the visual state names).
