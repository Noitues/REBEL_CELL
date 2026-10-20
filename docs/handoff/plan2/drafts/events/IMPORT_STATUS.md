# Events drafts: import status (W3 slice 3.17, replan)

Base: w1-close @ 92b8de03. Schema checked: `scripts/data/terminal_event_data.gd`, `event_choice_data.gd`,
`effect_data.gd`, `scripts/data/rc.gd` (EffectType, EffectTarget, Voice, Status).
Existing events: 124 files in `content/events/`, matched by filename, `id = &"..."` and `title = "..."`.

## Result

- Drafts: 30. Each draft defines exactly one TerminalEventData.
- Already in `content/events/` (by id or title): 0 of 30.
- Authored as .tres: 0 of 30.
- Skipped: 30 of 30. Every draft needs at least one mechanic the schema does not have.

## Missing mechanics (not in the schema, so no event authored)

Checked with grep on `scripts/data/`, `content/`, `tools/`: none of these exist as event-choice fields.
- `next_combat_overrides` (and `combat_overrides`, `next_raid_overrides`): per-combat or per-raid modifiers.
  The only runtime `combat_overrides` is a RunState dictionary (`shop_stock_delta`, `max_ram`), not an EventChoiceData field.
- `map_edits` (N16): close_link, add_link, convert_node, reveal_node_type, remove_node.
- `starts_combat` (events that open a fight, including ambush fights): no such choice field. Ambush is an option, never a node kind.
- `event_wheel` (EventWheelData, N17): the Thruster Dial and other event wheels.
- Conditional rewards ("granted on a win", "on a WEAK read") and `reward` as a random pool.

## Table

| # | Draft | Event id | Title | Corp | Status | Reason |
|---|---|---|---|---|---|---|
| 01 | 01_future_solace | ev_sol_courtesy_waiver | Courtesy Waiver | solace | skip | next_combat_overrides (3 choices) |
| 02 | 02_future_meridian | ev_mer_dock_broadcast | Dock Floor Broadcast | meridian | skip | next_combat_overrides (3 choices) |
| 03 | 03_future_halcyon | ev_hal_stuck_crosswalk | Stuck Crosswalk | halcyon | skip | next_combat_overrides, map_edits |
| 04 | 04_future_orbital | ev_orb_cold_witness | The Witness on the Rim | orbital | skip | next_combat_overrides, map_edits |
| 05 | 05_future_rebel_cell | ev_rc_standing_contract | Standing Contract | rebel_cell | skip | next_combat_overrides (3 choices) |
| 06 | 06_future_aurelian | ev_aur_service_lift | Service Lift | aurelian | skip | aurelian not a schema corp; also overrides, map_edits |
| 07 | 07_future_tethys | ev_tet_pressure_rumor | Pressure Rumor | tethys | skip | tethys not a schema corp; also overrides |
| 08 | 08_paths_solace | ev_solace_wellness_hold | Wellness Hold | solace | skip | map_edits |
| 09 | 09_paths_meridian | ev_mer_wrong_address | Wrong Address | meridian | skip | map_edits, starts_combat |
| 10 | 10_paths_halcyon | ev_hal_lien_notice | Lien on the Overpass | halcyon | skip | map_edits (3 of 4 choices) |
| 11 | 11_paths_orbital | ev_orb_pad_favor | A Favor on Pad Nine | orbital | skip | map_edits, next_combat_overrides |
| 12 | 12_paths_aurelian | ev_aur_verdict_broadcast | Live Verdict Feed | aurelian | skip | aurelian corp; map_edits, starts_combat |
| 13 | 13_paths_tethys | ev_tet_hatch_fault | Hatch Fault | tethys | skip | tethys corp; map_edits |
| 14 | 14_ambush_solace | ev_witness_statement | Witness Statement | solace | skip | starts_combat, combat_overrides, map_edits |
| 15 | 15_ambush_meridian | ev_mer_exclusive_carrier | Exclusive Carrier Clause | meridian | skip | starts_combat, next_combat_overrides, map_edits |
| 16 | 16_ambush_halcyon | ev_hal_maintenance_tunnel | Service Tunnel Shortcut | halcyon | skip | starts_combat, map_edits, next_combat_overrides, conditional reward |
| 17 | 17_ambush_orbital | ev_orb_rumor_flare | Rumor of a Dead Bird | orbital | skip | starts_combat (2 choices), conditional Daemon/Firmware reward; choices 3-4 alone would change the design |
| 18 | 18_ambush_rebel_cell | ev_rc_holding_cell_tip | The Prisoner in the Trunk | rebel_cell | skip | starts_combat, combat_overrides |
| 19 | 19_ambush_tethys | ev_tet_pressure_courier | Pressure Courier | tethys | skip | tethys corp; starts_combat |
| 20 | 20_wheel_solace | ev_sol_payment_plan | Payment Plan Roulette | solace | skip | event_wheel, starts_combat |
| 21 | 21_wheel_meridian | ev_mer_favor_slot | Favor Slot | meridian | skip | event_wheel, starts_combat, map_edits |
| 22 | 22_wheel_halcyon | ev_hal_public_address | Emergency Broadcast Lottery | halcyon | skip | event_wheel, map_edits |
| 23 | 23_wheel_orbital | ev_orb_stuck_thruster | Stuck Thruster | orbital | skip | event_wheel (Thruster Dial), extra-nudge HP costs |
| 24 | 24_wheel_rebel_cell | ev_rc_witness_stand | The Witness Stand | rebel_cell | skip | event_wheel, next_combat_overrides, map_edits |
| 25 | 25_wheel_aurelian | ev_aur_lanista_contract | The Lanista's Contract | aurelian | skip | aurelian corp; event_wheel, starts_combat |
| 26 | 26_wheel_any | ev_service_hatch | Service Hatch | any | skip | event_wheel, map_edits, starts_combat |
| 27 | 27_raidwin_any | ev_rw_second_hand_rumor | Second-Hand Rumor | any | skip | next_raid_overrides, map_edits |
| 28 | 28_raidwin_rebel_cell | ev_rc_held_courier | The Man in the Van | rebel_cell | skip | starts_combat, next_combat_overrides, map_edits, raid rewards |
| 29 | 29_hqview_any | ev_hq_dead_letter_crate | Unmarked Crate at the Loading Door | any | skip | event_wheel, starts_combat, next_combat_overrides |
| 30 | 30_paths_any | ev_toll_ledger_debt | The Toll Ledger | any | skip | map_edits, next_combat_overrides |

## Other checks

- Aurelian and Tethys: neither is a schema corporation (`content/corporations/` has solace, meridian, halcyon, orbital, rebel_cell). Their events are skipped, not authored (drafts 06, 07, 12, 13, 19, 25).
- Strings: existing events use plain `text` / `title` / `label` strings, not TextDb keys. `tools/export_text.gd` does not export events, so no `strings.csv` re-export was needed.
- Black Market: no draft mentions it, so no maybe-unknown event was added.
- Ambush: all ambush drafts (14-19) need a fight from an event choice, which the schema does not support.

## Q: for the designer

- Q: Author the supported choices only (for example 17 choices 3-4, or the non-override choice of 01, 02, 05)? That changes the drafted design, so it needs a ruling. Not done.
- Q: Add an event-choice field for a combat start, the next-combat modifiers, map edits and an event wheel? Each is a schema change (rule 8), so it needs a DECISIONS.md entry. Not done.
