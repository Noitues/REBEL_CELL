<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__tethys; status ok; tokens in 15671 cache-write 0 cache-read 34418 out 5700; cost $0.048. v2: designer answers 2026-10-19 applied. -->

# Tethys Deep: THE WATER LEVEL (v2)

## 0. What changed from v1

- **T1 (start Head by tier):** the street default stands: `tethys_street_start_head_by_tier` = LOW, LOW, RISING, HIGH. Q-DESIGNER 1 is closed. Nothing changes in the rules.
- **T2 (raid continues from the last netrun's Head):** v1 rule "raid Head starts LOW" is replaced.
  - The raid's start Head is the Head the last netrun ended on.
  - This adds one saved campaign field (`last_netrun_end_head`). It also breaks v1's "no raid fields saved" claim.
  - The raid bands are now offset by the start step.
- **T3 (Submerged mutes turrets only):** v1 rule 3's "threats deal 50 % damage" is deleted. This removes `tethys_submerged_threat_damage_pct`, its test assertion and its preview line.
- **T4 (no Dry salvage bonus):** v1 street rule 7 is deleted. This removes `tethys_dry_salvage_pct`, `test_dry_salvage_reward` and the "DRY +25 %" header. The wet penalty is the only street carrot or stick, so LOW is wanted only to avoid the penalty.
- **T5 ("wait for the tide" costs Heat):** v1 HQ rule 6 gains a Heat cost on every Wait. Cost: `tethys_wait_heat` = 2. The validator still guarantees no Wait is needed on layers 1–7, so Wait is a real cost only on layers 8+. The v1 HQ rule that Wait "is always offered" stays.
- **T6 (Divert is permanent for the run):** v1 HQ rule 4 is confirmed: a Drained node is never closed for the rest of the run. Q-DESIGNER 6 is closed.
- **Code to change:** Tethys is not built, so only the v1 draft changes. `last_netrun_end_head` is new. The Dry salvage and Submerged damage code is dropped.

## 1. Rules

### Street netrun (light form)

1. The Head has 4 steps: LOW, RISING, HIGH, FALLING. It starts at `tethys_street_start_head_by_tier` (T1 LOW, T2 LOW, T3 RISING, T4 HIGH).
2. The Head advances one step (FALLING → LOW) after every `tethys_street_nodes_per_tick` = 2 completed nodes. Fights, events, shops and Racks all count. Only rule 7 and the Pump Room otherwise move it.
3. Each node has a Level, fixed at map generation and shown on the map.
   - Elite Router and Server Rack are LOWER.
   - Router is LOWER with chance `tethys_street_router_lower_pct`, drawn once from the map stream.
   - Terminal and Mainframe are UPPER.
4. Floors: UPPER ≥ 1; a LOWER Router is at B1 (−1); a LOWER Elite or Rack is at B2 (−2).
5. The water line is LOW −2.0, RISING −1.0, HIGH 0.0, FALLING −1.0. A node is **wet** when its floor is below the water line. At LOW nothing is wet. At RISING and FALLING only B2 nodes are wet. At HIGH every LOWER node is wet. UPPER nodes are never wet.
6. A wet node's enemies get +`tethys_wet_resistance` resistance (N21), only at tier ≥ `tethys_flood_min_tier`. At T1 the Head shows but nothing is penalized.
7. **Pump Room:** each street netrun has one Terminal in layers 3–5 that is a sluice, an event with two options.
   - HOLD: the Head does not advance at the next tick.
   - SKIP: the Head advances one step now.
   - Taking neither is allowed. The Pump Room counts as a completed node.
8. When a street netrun ends (win, abandon or death), the campaign stores the Head at that moment as `last_netrun_end_head`. This is the Head used in raid rule 1.

### HQ netrun (full form: the Dam Run, 11 layers)

1. The Head starts LOW and advances every `tethys_hq_nodes_per_tick` = 2 completed nodes.
2. Levels: Act I (Dry Side) and Act III (Piers) are UPPER. Act IV (Deep Stair) is LOWER. The Lock is UPPER.
3. Per-Head effect:

| Head | UPPER | LOWER |
|---|---|---|
| LOW | open | Dry: 0 free nudges on turn 1 |
| RISING | open | open |
| HIGH | Awash: enemies +1 resistance | Flooded: closed |
| FALLING | open | open; Surge |

   - **Surge:** each enemy wheel's turn-1 start respin uses the `combat` stream at its existing checkpoint. The needle previews as "?".
4. **Sluice nodes:** layer 2 has two and layer 6 has one. The player gets one action, or two with a Sluice key.
   - **Hold:** freeze the Head for one tick.
   - **Skip:** advance the Head one step.
   - **Divert:** mark one LOWER node on the next layer **Drained**. A Drained node is never closed for the rest of the run (T6). Drained marks persist across layers.
5. **Lock Cycle:** the DOCK LOCK on layer 3 is a mini-fight against the Lockkeeper with a `tethys_lock_turns` = 4 turn clock.
   - Win in time: the player picks LOW or RISING as the Head at layer 4.
   - Win late: the Head is HIGH on entering layer 4.
6. **Wait for the tide:** if every reachable node is closed, the player must Wait. A Wait advances the Head one step and adds `tethys_wait_heat` Heat (T5). It never counts toward the node tick. The validator guarantees no Wait is needed on layers 1–7.
7. **Pressure Stair:** on layers 8–11, Pressure = layer − 8. Max RAM is reduced by floor(Pressure / `tethys_pressure_per_ram`), so 12 / 12 / 11 / 11 on layers 8–11. A Decompression node (layers 9 and 10) resets Pressure to 0 at the cost of `tethys_decompression_ticks` Head steps.
8. A one-use HOLD pickup freezes the Head for one tick.

### Raid (one hook: SUBMERGED at HIGH)

1. The raid Head starts at `last_netrun_end_head` (T2). If the campaign has no stored value, it starts at LOW. The Head steps every `tethys_raid_steps_per_head` = 6 raid steps over the 30-step clock. Step s reads Head (start + floor(s / 6)) mod 4, so the bands are LOW, RISING, HIGH, FALLING, then the cycle repeats. A start at HIGH puts HIGH at steps 0–5.
2. Raid Levels by node type (`tethys_raid_level_by_node_type`):
   - UPPER: Home Server, Relay, Firewall Relay, Safehouse.
   - LOWER: Compiler Rack, Vault Terminal, Proxy Relay.
3. While the Head is HIGH, each LOWER node is **Submerged**: its turret assets and built-in turrets cannot fire. Nothing else changes (T3): threat damage, ICE Locks, Decoys and integrity are as normal. UPPER nodes are never affected.
4. Operatives are never killed in raids (Q24.1). Submerged affects nodes only.

## 2. State and save fields

| Field | Type | Where |
|---|---|---|
| `tethys.head_step` | int 0–3 | `TethysRunState` on the run state |
| `tethys.nodes_since_tick` | int | same |
| `tethys.hold_ticks` | int | same |
| `tethys.pressure` | int (HQ) | same |
| `tethys.drained_node_ids` | Array[int] (HQ) | same |
| `node.level` | int 0 UPPER, 1 LOWER | map node |
| `node.floor` | int | map node |
| `node.is_sluice` | bool | map node |
| `campaign.tethys_last_netrun_end_head` | int 0–3, default 0 | campaign state (new, T2) |

- **Determinism:** the Head is a pure function of the start step, the completed-node count and the actions (Hold, Skip, Wait, Divert). The only random draws are the Router Level (map stream at generation) and the Surge respin (`combat` stream, checkpointed).
- **Raid:** the Head bands and Submerged ranges are pure functions of the step, the start Head and the node type. They are not saved beyond the campaign field.
- **Save impact:** all fields are additive with defaults. They ride the N8 version bump. Old saves are dropped (D3).

## 3. Preview

- **Map:**
  - A tide gauge shows the current Head and the next three steps.
  - Each node shows its Level glyph and floor.
  - Each node shows its arrival Head and a "wet" or "closed" badge. This is exact, assuming no Hold, Skip or Wait.
  - Hovering a Pump Room or HQ sluice option ghosts the changed Head track, and the result equals the preview.
  - The Wait button shows "+2 Heat".
- **Fight header:** "WET +1 res" on wet nodes at T2+.
- **HQ Surge:** the turn-1 needle shows as a ghosted "?" with the respin direction (Q19).
- **Raid setup:**
  - A 30-step Head bar starts at the stored Head, with the four bands marked.
  - The start Head is labeled "from last netrun".
  - Each LOWER node shows its Submerged step ranges, with turret icons silenced in those windows.
  - The projected outcome (HOLDS / DOWN / TAKEN) includes Submerged.
- Everything else is exact. "?" appears only on the Surge respin.

## 4. Numbers

| Value | Placeholder | Config key |
|---|---|---|
| Street nodes per tick | 2 | `campaign_config.tethys_street_nodes_per_tick` |
| Street start Head by tier | LOW, LOW, RISING, HIGH | `campaign_config.tethys_street_start_head_by_tier` |
| Water line per Head | −2.0, −1.0, 0.0, −1.0 | `campaign_config.tethys_street_water_line_by_head` |
| LOWER Router chance | 35 % | `campaign_config.tethys_street_router_lower_pct` |
| Floors: Router / Elite / Rack | −1 / −2 / −2 | `campaign_config.tethys_street_floor_by_node_type` |
| Wet resistance | +1 | `campaign_config.tethys_wet_resistance` |
| Flood penalty min tier | 2 | `campaign_config.tethys_flood_min_tier` |
| HQ nodes per tick | 2 | `campaign_config.tethys_hq_nodes_per_tick` |
| HQ Awash resistance | +1 | `campaign_config.tethys_awash_resistance` |
| HQ Dry free nudges | 0 | `campaign_config.tethys_hq_dry_free_nudges` |
| Lock clock | 4 turns | `campaign_config.tethys_lock_turns` |
| Wait Heat | 2 | `campaign_config.tethys_wait_heat` |
| Pressure per RAM point | 2 | `campaign_config.tethys_pressure_per_ram` |
| Decompression cost | 2 Head steps | `campaign_config.tethys_decompression_ticks` |
| Raid steps per Head | 6 | `campaign_config.tethys_raid_steps_per_head` |
| Raid Level by node type | see §1 | `campaign_config.tethys_raid_level_by_node_type` |

## 5. Tests to write

| Test | Tier | Asserts |
|---|---|---|
| `test_head_cycle_pure_function` | fast | The same start, completions and actions give the same Head; FALLING → LOW. |
| `test_street_start_head_by_tier` | fast | The start Head is LOW, LOW, RISING, HIGH for T1–T4. |
| `test_street_wet_by_floor` | fast | A node is wet iff its floor < the water line, at each Head. |
| `test_street_level_assignment_deterministic` | fast | The same seed gives the same Levels; Elites and Racks are always LOWER. |
| `test_pump_room_hold_skip` | fast | Hold freezes one tick, Skip advances one step, each equal to its preview. |
| `test_wet_resistance_gated_by_tier` | fast | +1 at T2+, none at T1. |
| `test_no_dry_salvage` | fast | A LOWER node entered at LOW pays the base reward. |
| `test_arrival_head_preview_equals_actual` | full | The previewed arrival Head equals the real one on a scripted path. |
| `test_hq_lower_closed_at_high` | fast | LOWER HQ nodes are closed at HIGH. |
| `test_divert_permanent` | fast | A Drained node stays open at HIGH on every later layer. |
| `test_wait_costs_heat_and_skips_tick` | fast | Wait adds 2 Heat, advances the Head, and does not change `nodes_since_tick`. |
| `test_hq_wait_guarantee` | full | The validator finds no map needing a Wait on layers 1–7. |
| `test_lock_clock_sets_head` | full | A win within 4 turns lets the player pick the Head; a late win sets HIGH. |
| `test_pressure_ram_cap` | fast | Max RAM is 12/12/11/11 on layers 8–11. |
| `test_surge_uses_combat_stream` | full | The Surge respin comes from the `combat` stream and rewind restores it. |
| `test_raid_start_head_from_last_netrun` | fast | The raid Head at step 0 equals the stored end Head; with none stored it is LOW. |
| `test_raid_head_bands_offset` | fast | Steps 0–29 read (start + floor(s/6)) mod 4 for every start. |
| `test_raid_submerged_turrets_only` | fast | At HIGH only LOWER nodes' turrets are silenced; threat damage, ICE Locks, Decoys and UPPER nodes are unchanged. |
| `test_raid_preview_equals_playout` | full | The setup projection equals the resolved raid. |
| `test_tethys_save_roundtrip` | fast | The run-state fields, node Levels and `tethys_last_netrun_end_head` survive save and load. |

## 6. Build slices

1. **S:** config keys and the pure Head function (`TethysRunState`). No dependencies.
2. **M:** `node.level` and `node.floor` at map generation, the wet rule and the T2+ resistance (needs N21 and slice 1).
3. **M:** the tide gauge and the map badges for the street, with the arrival-Head preview (slice 2).
4. **S:** the Pump Room event with Hold and Skip (slice 1; N17 optional, EventChoice fallback).
5. **S:** the raid Head bands, the stored end Head and the Submerged turret mute (slice 1).
6. **M:** the raid setup Head bar and Submerged preview (slice 5).
7. **L:** the HQ Dam Run: Levels per act, closing, Dry and Awash, sluice puzzles, Divert, Wait with Heat (N16, slices 1–3).
8. **M:** the Lock Cycle mini-fight and Pressure Stair (N3, N4, slice 7).
9. **S:** Surge on the `combat` stream and the "?" preview (slice 7).

The art-pass owns the 3D look: caustics, water surface, drowned nodes and dimmed turrets.

## 7. Q-DESIGNER

Q-DESIGNER: Should the Head a netrun ends on be stored when the operative dies or abandons, or only on a win? (Store it on every end, since a failed netrun is still a campaign turn.)
Q-DESIGNER: Should Wait for the tide cost a flat 2 Heat or scale with layer? (Flat 2.)
Q-DESIGNER: Should a stored end Head expire after one raid? (No; it is overwritten by the next netrun's end.)
Q-DESIGNER: Should Divert cost something, such as one Sluice action, since it is now permanent? (It uses the sluice action it already spends, with no extra cost.)
