<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01QpYFZqBxUvn2JMgwTbAhtu, custom_id theme__halcyon; status ok; tokens in 24613 cache-write 0 cache-read 33457 out 10979; cost $0.083. DRAFT: designer picks. -->

# Halcyon: the Eye (THE PANOPTICON)

Working name for the rules: **THE EYE**. It is one Eye with one state: `eye_index`, an octant of the compass around the Eye marker on the City Grid. Everything below is derived from that one value and from whether the Eye is FIXED.

## 1. Rules: street, HQ, raid

**Shared rules (all forms)**

1. **Bearing.** Every district has an integer `bearing_deg` (0-359) from the Eye marker (the corporation's HQ marker on the Grid), computed once at Grid generation.
   - Sites take their district's bearing, so the hatch on the map matches the Sites.
   - Testable: the same Grid seed gives identical bearings.
2. **Sector.** The Eye covers a 90° sector centred on `45° × eye_index`: [centre − 45°, centre + 45°).
   - A district is **Spotted** if its `bearing_deg` is inside the sector.
3. **Moving.** After each netrun ends (win, death or abandoned), if `eye_fixed_left == 0`, `eye_index` advances by `eye_move_per_netrun` (+1, clockwise) modulo 8.
4. **Fixing.** When a netrun ends with an Exploit taken:
   - `eye_index` becomes the octant nearest the Exploit Site's bearing.
   - `eye_fixed_left` is set to 2, after that netrun's own tick (rule 5).
   - A second Exploit taken while fixed re-aims the Eye and resets `eye_fixed_left` to 2. It never stacks.
5. **Counting.** After each ended netrun with `eye_fixed_left > 0`, it drops by 1 and the Eye does not move.
   - At 0 the Eye is released and moves again from where it stands.
   - Because the tick runs before the fix is set, the **next two netruns** are the fixed ones.
6. **Launch snapshot.** At launch the run stores `spotted_level`. It never changes mid-run.
   - Site not Spotted: level 0.
   - Site Spotted, Eye moving: level 1.
   - Site Spotted, Eye FIXED (`eye_fixed_left > 0`): level 2.

**Street (light form)**

7. **The Blade.** A Spotted fight has a Blade rider.
   - At the start of each player turn the scan line marks one slice of your wheel, `(turn − 1) mod n`, over your non-empty slices (size 0 is skipped) in slot order.
   - That slice reads one precision tier lower for that turn's resolve (TIER_DOWN ×1: Perfect to Good, Good to WEAK).
   - An ENCRYPTED slice absorbs the Blade, and the Encrypt is consumed.
   - The mark is never random.
8. **Where the Blade applies.**
   - Level 1: Elite, Rack and mini-boss fights only.
   - Level 2: every fight.
9. **Heat.** At level 2, each Elite fight adds +1 Heat on top of its normal Heat.
10. **Signal.** Street rooms carry no per-room marks (territory-level only).

**HQ (full form)**

11. **Gaze phase.** The HQ run's gaze starts at `phase = eye_index` at launch. It is the same Eye and not a new draw.
12. **Gaze step.** `step` = nodes completed in this run.
    - Gaze centre = `45° × (phase + step)`, the same sector rule as rule 2.
    - A climb counts as 2 steps.
13. **IN THE EYE.** A node whose azimuth lies in the sector is IN THE EYE.
    - **Fight node:** entered as SPOTTED. The Blade applies at the run's `spotted_level`: 1, or 2 if the Eye was FIXED at launch.
    - **Non-fight node** (Terminal, Mainframe, rest, cache): SHUTTERED. It can't be entered.
14. **The beam.** A node within ±4° of the centre is BLOCKED, whatever its kind.
15. **Reachability guarantee.** The graph is rebuilt from stream `hq_graph` until every layer keeps at least one open (neither blocked nor shuttered) node for the launch `phase`, on the climb-free path and with each possible climb offset. Pure and exact.

**Raid (one hook)**

16. **Wedge.** On the raid map (the Grid in raid mode) the same sector is drawn at launch of the raid.
    - Corporate threats standing on a node inside the sector deal +25 % damage (`RAID_STRENGTH_PCT` applied per node).
    - Defense nodes in the sector are marked SEEN.
    - If the Eye is FIXED, the sector holds on the fixed area.

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `eye_index` | int 0-7 | CampaignState (`scripts/state/`) | Initial value drawn once at campaign start from RngService stream `eye_start`, checkpointed. Never redrawn. |
| `eye_fixed_left` | int 0-2 | CampaignState | |
| `district.bearing_deg` | int | Grid data, derived at generation, regenerated on load | Not saved. |
| `spotted_level` | int 0-2 | RunState | Snapshot at launch. |
| `eye_phase` | int 0-7 | RunState (HQ only) | = `eye_index` at launch. |
| `eye_step` | int | RunState (HQ only) | |
| `blade_slot` | int, derived | CombatantState | Computed from the turn counter; not saved. |

- **Derived, never stored:** `eye_az` (= 45° × index), the sector test, node access states and the Blade slot.
- **Save impact:** CampaignState gains two fields and RunState three, all additive with defaults. Bump the save version by 1. There is no migration, because old saves are dropped (D3).
- **Determinism:** the only random draw is `eye_start`. Moves, fixes and gaze are pure functions of the saved fields.

## 3. Preview

- **Grid and launch card.** For each Site the card shows:
  - the Spotted level badge (0 / 1 / 2 pips);
  - what the Eye does after this netrun (moves to octant N, or "FIXED n left");
  - on an Exploit objective: "Taking this fixes the Eye on this area for 2 netruns."
- **No "?" in these rules.** The one random draw, `eye_start`, resolves before any preview.
- **Fight.** The scanned slice is outlined on the wheel before End Turn. The preview chips (final tier and damage) already include the Blade's tier drop. A slice with ENCRYPTED shows "absorbs Blade".
- **HQ.**
  - The eye dial shows the next 3 sector centres.
  - Hovering an edge shows the gaze at arrival (+1 step, or +2 for a climb).
  - Each node shows its state: open, IN THE EYE (SPOTTED), SHUTTERED or BLOCKED. A climb node shows its arrival state.
- **Raid.** The wedge and SEEN badges show during setup, with the projected outcome including the +25 %.

## 4. Numbers

All of these are placeholders.

| Value | Placeholder | Key |
|---|---|---|
| Sector width | 90° | `config: campaign_config.eye_sector_deg` |
| Octant step | 45° | `config: campaign_config.eye_step_deg` |
| Moves per ended netrun | 1 | `config: campaign_config.eye_move_per_netrun` |
| Fix duration (netruns) | 2 | `config: campaign_config.eye_fix_netruns` |
| Blade tier drop | 1 | `config: campaign_config.blade_tier_drop` |
| Level 1 Blade classes | ELITE, MINI_BOSS, Rack | `config: campaign_config.blade_classes_l1` |
| Level 2 Blade classes | all | `config: campaign_config.blade_classes_l2` |
| Level 2 Elite Heat | +1 | `config: campaign_config.spotted_elite_heat` |
| HQ steps per completed node | 1 | `config: campaign_config.hq_gaze_step_per_node` |
| HQ steps per climb | 2 | `config: campaign_config.hq_gaze_step_per_climb` |
| Beam half-width | 4° | `config: campaign_config.hq_beam_half_width_deg` |
| HQ dial look-ahead | 3 | `config: campaign_config.hq_dial_steps` |
| Raid damage inside the sector | +25 % | `config: campaign_config.raid_eye_damage_pct` |

## 5. Tests to write

| Test | Tier | Asserts |
|---|---|---|
| `test_bearing_deterministic` | fast | Same seed gives identical `bearing_deg` for every district. |
| `test_sector_membership_edges` | fast | The sector is half-open, so exactly one of two adjacent centres claims a boundary bearing. |
| `test_eye_moves_when_unfixed` | fast | The index advances by 1 per ended netrun (win, death, abandon alike), modulo 8. |
| `test_exploit_fixes_eye_two_netruns` | fast | The fix is set after the taking netrun's tick. The next 2 netruns hold the Eye. The third moves it. |
| `test_second_exploit_resets_not_stacks` | fast | Taking an Exploit while fixed re-aims and resets to 2. |
| `test_spotted_level_snapshot` | fast | The level is 0 / 1 / 2 per rule 6 and does not change mid-run. |
| `test_blade_slot_order_skips_empty` | fast | The scanned slot cycles in slot order and skips size-0 slots. It is identical after undo and redo. |
| `test_blade_tier_drop_and_encrypt` | fast | The tier drops by 1. ENCRYPTED absorbs the Blade and is consumed. |
| `test_blade_preview_equals_result` | full | The preview chips equal the real resolve on a Spotted fight at levels 1 and 2. |
| `test_hq_gaze_pure_function` | fast | The gaze depends only on `(phase, step)`. A climb adds 2. |
| `test_hq_node_access_states` | fast | IN THE EYE fight nodes are SPOTTED, non-fight nodes are SHUTTERED and the beam band is BLOCKED. |
| `test_hq_graph_always_reachable` | full | For all 8 phases over many seeds, every layer has an open node on the climb-free path and under each climb offset. |
| `test_raid_wedge_damage` | fast | Threats inside the sector deal +25 % and threats outside deal 0 %. Fixed wedge holds. |
| `test_eye_save_roundtrip` | fast | `eye_index`, `eye_fixed_left` and the RunState fields survive save and load. Resuming does not redraw `eye_start`. |

## 6. Art answers

Numbered as in the art plan's "Questions for the build session".

1. **Spotted territory** is a district (with its Sites), not a room.
   - It is set when the district's bearing is in the sector, and cleared when the Eye moves out of it.
   - A netrun snapshots its level at launch.
2. **Difficulty levels:** two, stepped. Pip bar of 2 slots: level 1 = one pip, level 2 (FIXED) = two.
3. **Eye movement:**
   - It moves once per ended netrun, anchored at the corporation's HQ marker.
   - It is a 90° wedge from that marker.
   - It steps 45° (18-frame clip).
   - The art's disc fallback is not needed.
4. **Fix:**
   - The area is the sector centred on the Exploit Site's bearing, rounded to 45°.
   - Every netrun that ends counts (win, death or abandon).
   - On expiry the Eye resumes moving from where it stands.
   - A second Exploit re-aims and resets to 2 pips. It never stacks.
5. **Street marks:** territory-level only. Street rooms wear no red rings.
6. **Raid hook:** the Grid in raid mode shows the wedge.
   - Threats on nodes inside it deal +25 %. Nodes inside carry SEEN badges, and the chip text is "+25 % damage here".
   - It uses FIXED: when the Eye is fixed, the wedge snaps to the fixed area and shows 2 pips at the marker.
7. **HQ shape:** slot-driven, 13 layers and about 30 nodes per the HQ draft. Tier sizing is the art session's call.
   - **In:** shuttered, the 3-step eye dial, climbs.
   - **Out of this theme (pending Q-DESIGNER):** the Alert band, eye-asleep (Cut the Power), Annex nodes, Warden lockdown, the 6-step dial.
8. **Rule words:**
   - SPOTTED: an IN THE EYE fight node.
   - SHUTTERED: a non-fight node in the eye.
   - BLOCKED: the beam band, ±4°.
   - The ROOM BLOCKED look is the solid red frame.
9. **HQ and FIXED:** the HQ has no separate FIXED visual. It starts at `phase = eye_index`, which is the fixed octant if the Eye is fixed. If it was fixed at launch, in-eye fights show 2 pips on their chip.
10. **Per-frame fields:** see the state table below.
11. **Pure function:** yes. The Eye position is a pure function of `(eye_index, eye_fixed_left)`, and the HQ gaze of `(eye_phase, eye_step)`.
12. **Palette:** confirmed. Amber rim on hardware only, white-teal for light, red only for consequence marks.
13. **Grid and raid value and style rules:** the build session has none. They are the art session's, and the wedge and hatch alpha caps in the art plan stand. The HQ idle orbit is also the art session's.
14. **Street netruns** use the same orbit and decision rig and the same occlusion rule (ruling 2026-10-18, applied to every netrun).

**State names**

| Art plan name | Status | Final name and values |
|---|---|---|
| `eye_state` (away / scan / spotted / fixed) | Renamed | `eye_state` ∈ {`away`, `spotted`, `fixed`}. `scan` is retired: its look becomes the level-1 `spotted` look. |
| `eye_az` | Confirmed | Derived: 45 × `eye_index`, in degrees. |
| `fixed_left` | Renamed | `eye_fixed_left`, 0-2. |
| `spotted` (bool) | Replaced | `spotted_level`, 0-2. A bool is level > 0. |
| `difficulty_pips` | Confirmed | = `spotted_level`. |
| `phase`, `step` | Renamed | `eye_phase`, `eye_step`. |
| per-node `state` | Renamed, partial | open / in_eye / shuttered / blocked / walked / current / ahead / past. |
| `alert`, `starting_alert` | Not in this theme | Pending Q-DESIGNER; do not draw. |
| `blade_slot`, `blade_progress` | Confirmed | `blade_slot` 0-5 (the slice), progress art-only. |
| `climb_progress` | Confirmed | Unchanged. |
| `beam_node` | Confirmed | Node id or none. |

## 7. Reuse and dependencies

| Piece | Source | Fallback |
|---|---|---|
| TIER_DOWN and the status rules | N8 / N9 | Apply the Blade as a resolver-side tier modifier (no status). This is data-only. |
| Empty-arc handling | N12 | Skip-empty only matters once zero sizes exist. |
| Enrage | N4 | Not used by the Eye. |
| Rider and override plumbing for Spotted fights | N16 `next_combat_overrides` | Bake the Blade flag into the run's fight setup. |
| Per-node raid damage mod | `RAID_STRENGTH_PCT` | New per-node scope. |
| Map edits and node state | `map_graph` | |
| Data-driven rewards | N18 | Not needed. |

- **NEW code:**
  - the Eye state and its pure functions (sector test, step, fix);
  - bearings at Grid generation;
  - HQ node-access states (shuttered / blocked) and the reachability check on `map_graph`;
  - the Blade rider hook in the resolver;
  - the raid sector scope.
- **Not used:** the Parasite ring, rim gates and resistance.
- **Introduction order:** street level 1 (Elite and Rack only), then level 2 and the FIXED Exploit rule, then the raid wedge, then the HQ full form.

## 8. Q-DESIGNER

Q-DESIGNER: Do the HQ draft's extras (Alert and Lockdown, Annex rooms, Stall, Cut the Power) stay in the HQ run, or should the HQ keep only the gaze, the Spotted fights and the beam?
Q-DESIGNER: Should a netrun that ends in death or abandonment move the Eye and tick the fix, or only completed netruns?
Q-DESIGNER: Is level 2 (FIXED) allowed to put the Blade on every normal fight, or should it stay Elite and Rack plus +1 Heat?
Q-DESIGNER: Should non-fight HQ nodes be shuttered inside the eye, or keep working and cost something instead?
Q-DESIGNER: Should the raid hook be a damage bonus for threats inside the sector, or the reverse (assets inside it are blinded and lose range)?
