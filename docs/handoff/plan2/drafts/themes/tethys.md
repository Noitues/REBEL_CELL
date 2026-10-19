<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01Rzb4HxT5fiSKoNiHzd4i91, custom_id theme__tethys; status ok; tokens in 10626 cache-write 0 cache-read 33457 out 13425; cost $0.081. DRAFT: designer picks. -->

# Tethys Deep: THE WATER LEVEL

Working names for the art session: **Head** (LOW / RISING / HIGH / FALLING), **Level** (UPPER / LOWER), **wet** (a node below the water line), **Pump Room** (the street sluice), **Submerged** (a raid node under at HIGH). The HQ rules in §1 extend the Dam Run draft (§1–3) and change it in two places, each marked FIX.

## 1. Rules: street, HQ, raid

### Street netrun (LIGHT form: Head, Level and one sluice; no closing, no Pressure)

1. A Tethys street netrun has a **Head** with 4 steps: LOW, RISING, HIGH, FALLING. It starts at `config: campaign_config.tethys_street_start_head_by_tier` (T1 LOW, T2 LOW, T3 RISING, T4 HIGH).
2. The Head advances one step (cycling FALLING → LOW) after every `tethys_street_nodes_per_tick` = 2 completed nodes. Fights, events, shops and Racks all count. Nothing else moves it except rule 7.
3. Every map node has a **Level**, UPPER or LOWER, fixed at map generation and shown on the map.
   - Elite Router and Server Rack are always LOWER.
   - Router is LOWER with chance `tethys_street_router_lower_pct` = 35, drawn once at generation from the existing map RNG stream.
   - Terminal and Mainframe are always UPPER.
4. Every node has a **floor**, which is where it sits in the building.
   - UPPER nodes sit on floors 1 and up.
   - LOWER Routers sit on B1 (floor −1).
   - LOWER Elites and Racks sit on B2 (floor −2).
5. The **water line** per Head step is LOW −2.0, RISING −1.0, HIGH 0.0, FALLING −1.0. It is measured in floors, where 0 is the ground slab.
   - A node is **wet** when its floor is below the water line.
   - So at LOW nothing is wet. At RISING and FALLING only B2 nodes (Elites, Racks) are wet. At HIGH every LOWER node is wet. UPPER nodes are never wet in the street.
6. The Head when the player **enters** a node is set by what they have completed. A wet node's enemies get +`tethys_wet_resistance` = 1 resistance on top of their class value (N21). The penalty applies only at tier ≥ `tethys_flood_min_tier` = 2. At T1 the Head is shown but nothing is penalized.
7. **Dry salvage:** a LOWER node entered at LOW (not wet) pays +`tethys_dry_salvage_pct` = 25 % Cycles (Rack: Schematics) on its reward. This is the carrot, so the player has a reason to want LOW.
8. **Pump Room:** each street netrun has exactly one Terminal in layers 3–5 that is a sluice. It is an event with two options.
   - **HOLD:** the Head does not advance at the next tick.
   - **SKIP:** the Head advances one step now.
   - The Pump Room counts as a completed node. Taking neither option is allowed.
   - The result of each option is exact in the option text.

### HQ netrun (FULL form: the Dam Run, 11 layers)

1. **Head** as in street rule 1, starting at LOW. It advances every 2 completed nodes.
2. **Levels:** Act I (the Dry Side) and Act III (the Piers) are UPPER. Act IV (the Deep Stair) is LOWER. The Lock is UPPER. The `dam_bay`, `lock`, `pier_end`, `ring`, `inner`, `station`, `deck` and `core` slot classes are as in the Dam Run draft.
3. **Per-Head effect** (the draft table, with one FIX):

| Head | UPPER | LOWER |
|---|---|---|
| LOW | open | Dry: the player has 0 free nudges on turn 1 |
| RISING | open | open |
| HIGH | Awash: enemies +1 resistance | **Flooded: closed** |
| FALLING | open | open; Surge |

   - **FIX (Surge):** Surge means each enemy wheel's start-of-turn respin on turn 1 uses the `combat` stream at the existing checkpoint, with the needle shown as "?" on the preview. The draft's per-node hash is dropped, because RNG goes through RngService streams only.
4. **Sluice nodes:** Layer 2 has two sluice puzzle nodes, and layer 6 has one.
   - The player gets one action, or two with a Sluice key.
   - **Hold:** freeze the Head for one tick.
   - **Skip:** advance the Head one step now.
   - **Divert:** mark one LOWER node on the next layer **Drained**, meaning it is never closed for the rest of the run.
5. **Lock Cycle:** the DOCK LOCK on layer 3 is a mini-fight against the Lockkeeper, with a `tethys_lock_turns` = 4 turn clock.
   - Win within the clock: the player picks LOW or RISING as the Head at layer 4.
   - Win after the clock: the Head is HIGH on entering layer 4. Awash applies to the UPPER pier nodes, and any LOWER pier node is closed.
6. **FIX (no soft-lock):** if every node reachable from the current position is closed, the player must **Wait for the tide**. This advances the Head one step with no node completed, so it never counts toward rule 1. It is always offered, and the validator guarantees a Wait is never needed on layers 1–7.
7. **Pressure Stair:** on layers 8–11 the player carries Pressure = layer − 8. Max RAM is reduced by floor(Pressure / `tethys_pressure_per_ram` = 2).
   - **FIX:** the draft's "10 at layer 11" is wrong. With a base of 12, layer 10 gives 11 and layer 11 gives 11.
   - A Decompression node (layers 9 and 10) resets Pressure to 0 at the cost of 2 Head steps.
8. A one-use pickup, **HOLD**, freezes the Head for one tick. It can come from a Terminal at an Exploit building.

### Raid (ONE hook: SUBMERGED at HIGH)

1. Raids on a Tethys campaign use the same Head, driven by the 30-step raid clock. The Head steps every `tethys_raid_steps_per_head` = 6 raid steps and starts LOW. The bands are LOW 0–5, RISING 6–11, HIGH 12–17, FALLING 18–23 and LOW 24–29.
2. Network nodes have a Level by type (`tethys_raid_level_by_node_type`):
   - UPPER: Home Server, Relay, Firewall Relay, Safehouse.
   - LOWER: Compiler Rack, Vault Terminal, Proxy Relay.
3. While the Head is HIGH, every LOWER node is **Submerged**. On a Submerged node:
   - turret assets and built-in turrets cannot fire;
   - threats on it deal `tethys_submerged_threat_damage_pct` = 50 % damage;
   - ICE Locks, Decoys and node integrity are unchanged.
   - UPPER nodes are never affected. The Firewall Relay always fires.
4. The effect is symmetric and deterministic. It applies to threats on the node equally. Nothing else in the raid changes with the Head.
5. **Death rule:** operatives are never killed in raids (Q24.1). Submerged affects nodes only.

## 2. State and save fields

| Field | Type | Where |
|---|---|---|
| `tethys.head_step` | int 0–3 (LOW, RISING, HIGH, FALLING) | new `TethysRunState` on the run state (scripts/state/) |
| `tethys.nodes_since_tick` | int | same |
| `tethys.hold_ticks` | int (ticks still to freeze) | same |
| `tethys.pressure` | int (HQ only) | same |
| `tethys.drained_node_ids` | Array[int] (HQ only) | same |
| `node.level` | int 0 UPPER, 1 LOWER | per map node in the map graph state |
| `node.floor` | int (−2..n) | per map node |
| `node.is_sluice` | bool | per map node (street: the Pump Room; HQ: the three sluice puzzle nodes) |

- No raid fields are saved. Raid Head, Submerged ranges and the preview are pure functions of step number and node type.
- **Determinism:** the Head is a pure function of start step, completed-node count and the actions taken (Hold, Skip, Wait, Divert). It never changes mid-fight, so combat rewind is unaffected. The only random draws are the Router Level (map stream, at generation) and the HQ Surge respin (combat stream, already checkpointed).
- **Save impact:** all fields are additive with defaults. They ride the N8 version bump (2 → 3 migration) if N8 lands first. Otherwise they cost +1 version. Old saves are dropped (D3), so no migration is needed beyond defaults.

## 3. Preview

- **Map (street and HQ):**
  - A tide gauge shows the current Head and the next three steps.
  - Each node shows its Level glyph and floor.
  - Each node shows the Head at which you would enter it. This is exact, because layer n is entered after n−1 completions, assuming no Hold, Skip or Wait.
  - Each node shows a "wet" or "closed" badge for that arrival Head.
  - Hovering a Pump Room option or HQ sluice ghosts the changed Head track, and the result equals the preview.
- **Street fight header:** "WET +1 res" or "DRY +25 %" on LOWER nodes.
- **HQ Surge:** the first-turn needle shows as a ghosted "?" with the respin direction (Q19).
- **Raid setup:** a 30-step Head bar with the four bands marked. Each LOWER node shows "SUBMERGED steps 12–17" and silenced turret icons in that window. The projected outcome (HOLDS / DOWN / TAKEN) already includes Submerged.
- **Nothing is hidden or random** in the Head, the Levels or the raid band, so none of it shows "?" except the Surge respin and the unsolved HQ Wait state.

## 4. Numbers

| Value | Placeholder | Config key |
|---|---|---|
| Street nodes per tick | 2 | `campaign_config.tethys_street_nodes_per_tick` |
| Street start Head by tier | LOW, LOW, RISING, HIGH | `tethys_street_start_head_by_tier` |
| Street water line per Head | −2.0, −1.0, 0.0, −1.0 | `tethys_street_water_line_by_head` |
| LOWER Router chance | 35 % | `tethys_street_router_lower_pct` |
| Floors: Router / Elite / Rack | −1 / −2 / −2 | `tethys_street_floor_by_node_type` |
| Wet resistance | +1 | `tethys_wet_resistance` |
| Flood penalty min tier | 2 | `tethys_flood_min_tier` |
| Dry salvage | +25 % | `tethys_dry_salvage_pct` |
| HQ nodes per tick | 2 | `tethys_hq_nodes_per_tick` |
| HQ Awash resistance | +1 | `tethys_awash_resistance` |
| HQ Dry free nudges | 0 on turn 1 | `tethys_hq_dry_free_nudges` |
| Lock clock | 4 turns | `tethys_lock_turns` |
| Pressure per RAM point | 2 | `tethys_pressure_per_ram` |
| Decompression cost | 2 Head steps | `tethys_decompression_ticks` |
| Raid steps per Head | 6 | `tethys_raid_steps_per_head` |
| Raid node Level by type | see §1 | `tethys_raid_level_by_node_type` |
| Submerged threat damage | 50 % | `tethys_submerged_threat_damage_pct` |

## 5. Tests to write

| Test | Tier | Asserts |
|---|---|---|
| `test_head_cycle_pure_function` | fast | Same start, completions and actions give the same Head; cycles FALLING → LOW. |
| `test_street_wet_by_floor` | fast | At each Head, a node is wet iff its floor < the water line (the table in §1). |
| `test_street_level_assignment_deterministic` | fast | The same seed gives the same Levels. Elites and Racks are always LOWER. |
| `test_pump_room_hold_skip` | fast | Hold freezes one tick, Skip advances one step, and each matches the preview. |
| `test_arrival_head_preview_equals_actual` | full | The previewed arrival Head per layer equals the Head on entry for a scripted path. |
| `test_wet_resistance_gated_by_tier` | fast | +1 resistance on a wet node at T2+, none at T1. |
| `test_dry_salvage_reward` | fast | A LOWER node entered at LOW pays +25 %. |
| `test_hq_lower_closed_at_high` | fast | LOWER HQ nodes are closed at HIGH. |
| `test_hq_wait_guarantee` | full | The validator finds no map where Wait is needed on layers 1–7. Layers 8+ always offer Wait. |
| `test_lock_clock_sets_head` | full | A win within 4 turns lets the player pick the Head. A win after the clock sets HIGH. |
| `test_pressure_ram_cap` | fast | Layers 8–11 give max RAM 12/12/11/11. |
| `test_surge_uses_combat_stream` | full | The Surge respin comes from the `combat` stream, and rewind restores it. |
| `test_raid_head_bands` | fast | The raid Head bands match steps 0–29. |
| `test_raid_submerged_lower_only` | fast | At HIGH only LOWER nodes silence turrets and halve threat damage. UPPER nodes, ICE Locks and Decoys are unaffected. |
| `test_raid_preview_equals_playout` | full | The setup projection equals the resolved raid with Submerged. |
| `test_tethys_save_roundtrip` | fast | Run-state fields and node Levels survive save and load. |

## 6. Art answers

There is no art-pass plan for Tethys, so these are the assumed state names and values for the art session.

| State | Names / values |
|---|---|
| Head | `LOW`, `RISING`, `HIGH`, `FALLING` (int 0–3) |
| Level | `UPPER`, `LOWER` |
| Street water line, in floors (HQ uses 2.5 ZW on the dam) | LOW −2.0, RISING −1.0, HIGH 0.0, FALLING −1.0 |
| Street floors | UPPER ≥ 1. LOWER Router B1. LOWER Elite and Rack B2. |
| Street sluice node | the Pump Room (a Terminal) |
| HQ sluice nodes | the layer-2 sluice puzzles, the layer-6 sluice puzzle, and the DOCK LOCK (a clock puzzle) |
| HQ closed state | `closed` at HIGH on LOWER nodes, drawn drowned |
| Raid LOWER nodes (flood at HIGH) | Compiler Rack, Vault Terminal, Proxy Relay |
| Raid UPPER nodes (never flood) | Home Server, Relay, Firewall Relay, Safehouse |
| Raid band steps | LOW 0–5, RISING 6–11, HIGH 12–17, FALLING 18–23, LOW 24–29 |

Art cues, which are the art session's call:
- Caustics are strongest at RISING and FALLING.
- The surface sits at the ground slab at HIGH.
- A submerged raid node is drawn under the clear-water look with turret icons dimmed.

## 7. Reuse and dependencies

- **N21** (class resistance and per-turn refresh) carries the +1 wet and Awash resistance. It is data-only on top of N21.
- **N16** (map edits) carries Divert and the closed or Drained flags.
- **N17** (event wheel) is optional for the Pump Room and the HQ sluice puzzles. Data-only fallback: an EventChoice with `head_action` outcomes.
- **N3 and N4:** the Lockkeeper's phases. No new enrage is needed.
- The raid sim reuses the 30-step clock and existing assets.
- **NEW code:**
  - `TethysRunState` and the Head tick.
  - `node.level` and `node.floor` on map nodes.
  - The wet / closed / Wait validator and arrival-Head preview.
  - The tide gauge UI.
  - The raid Submerged modifier.
  - The Pump Room, Hold, Skip and Divert event effects.
  - The Dry salvage reward modifier.
- **Not used:** the Parasite ring, rim gates.

## 8. Q-DESIGNER

Q-DESIGNER: Should a street netrun's start Head follow the tier table (LOW, LOW, RISING, HIGH) or always start LOW?
Q-DESIGNER: Should a raid's Head start LOW every time, or continue from the Head the last netrun ended on?
Q-DESIGNER: Is Submerged both muting turrets and halving threat damage (a trade-off), or only muting turrets?
Q-DESIGNER: Should the Dry salvage carrot (+25 % Cycles at LOW on LOWER nodes) stay, or is the wet penalty enough?
Q-DESIGNER: Should "Wait for the tide" at HQ cost nothing, or cost Heat?
Q-DESIGNER: Is Divert permanent for the run, or does it expire after one layer?
