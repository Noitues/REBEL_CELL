<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__halcyon; status ok; tokens in 15655 cache-write 0 cache-read 34418 out 7249; cost $0.055. v2: designer answers 2026-10-19 applied. -->

# Halcyon: the Eye (v2)

## 0. What changed from v1

- **H1 (keep all HQ extras):** Alert and Lockdown, Annex rooms, Stall and Cut the Power move from "out of this theme" into the HQ full form (rules 16-20).
  - The v1 draft only names them and the HQ draft is not in front of me. I define each in its simplest form, behind config, and raise the calls as Q-DESIGNER.
  - `eye_step` now counts gaze steps (completed nodes, climbs, Stalls), not only completed nodes.
  - The reachability guarantee (rule 15) now assumes Stall is the escape valve.
- **H2 (the Eye moves every campaign turn):** the trigger changes from "after each netrun ends" to "each campaign turn".
  - A campaign turn is one ended netrun, whether won, died or abandoned. This is the same behavior as v1 rule 3, but the term is now the ruling's.
  - The fix countdown (`eye_fixed_left`) also ticks per campaign turn.
  - The v1 Q about failed netruns is closed.
- **H3 (level 2 puts the Blade on every normal fight):** rule 8 now says so explicitly.
  - Level 1 stays Elite, Rack and mini-boss only.
  - Level 2 is every fight.
  - The Elite +1 Heat stays.
- **H4 (non-fight HQ nodes in the eye are shuttered):** confirmed, rule 13. Annex rooms are non-fight nodes and are shuttered too.
- **H5 (threats in the sector hit harder):** confirmed as the raid hook, rule 21 (+25 % placeholder). The v1 reverse option is dropped.
- **Code:** Halcyon is not built, so nothing needs reworking. Build from this draft.

## 1. Rules

**Shared**

1. **Bearing.** Every district has an integer `bearing_deg` (0-359) from the Eye marker (the HQ marker), computed once at Grid generation. Sites take their district's bearing.
2. **Sector.** The sector is 90°, centred on `45° × eye_index`, half-open [c−45°, c+45°). A district is **Spotted** if its bearing is inside.
3. **Moving.** Each campaign turn ends with `eye_index = (eye_index + 1) mod 8` if `eye_fixed_left == 0`. A campaign turn is one ended netrun (win, death or abandon). Fixes and moves are suppressed during a netrun; they resolve when it ends.
4. **Fixing.** An Exploit taken in a netrun sets `eye_index` to the octant nearest that Site's bearing and `eye_fixed_left = 2`. This happens after that turn's own tick. A second Exploit re-aims and resets to 2; it never stacks.
5. **Counting.** Each campaign turn with `eye_fixed_left > 0` decrements it by 1 and the Eye does not move. At 0 it moves again from where it stands.
6. **Launch snapshot.** `spotted_level` is stored at launch and never changes mid-run:
   - not Spotted: 0;
   - Spotted, Eye moving: 1;
   - Spotted, Eye FIXED: 2.

**Street (light form)**

7. **The Blade.**
   - At the start of each player turn the scan line marks slice `(turn − 1) mod n`, over non-empty slices in slot order (size 0 skipped).
   - That slice reads one tier lower for the resolve (TIER_DOWN ×1).
   - ENCRYPTED absorbs the Blade and is consumed.
   - The mark is never random.
8. **Where it applies.**
   - Level 1: Elite, Rack and mini-boss fights.
   - Level 2: every fight, normals included.
9. **Heat.** At level 2, each Elite fight adds +1 Heat.
10. Street rooms carry no per-room marks.

**HQ (full form)**

11. **Gaze phase.** `eye_phase = eye_index` at launch.
12. **Gaze step.** `eye_step` counts gaze steps:
    - +1 per completed node;
    - +2 per climb;
    - +1 per Stall (rule 18).

    Gaze centre = `45° × (phase + step)`, with the rule 2 sector.
13. **IN THE EYE.**
    - A fight node is SPOTTED. The Blade applies at `spotted_level` (raised by Lockdown, rule 17).
    - A non-fight node (Terminal, Mainframe, rest, cache, Annex) is SHUTTERED and can't be entered.
14. **The beam.** A node within ±4° of the centre is BLOCKED, whatever its kind.
15. **Reachability.** The graph is rebuilt from stream `hq_graph` until every layer has at least one open (not blocked, not shuttered) node for the launch phase. This holds on the climb-free path and under each climb offset, at the normal beam width. Lockdown or bad luck can still close a layer; Stall is the answer, and at most 7 Stalls always open a node.
16. **Alert.**
    - `hq_alert` starts at `spotted_level`.
    - +1 per fight node completed IN THE EYE, +1 per Stall, +2 per Cut the Power.
    - It never decreases.
17. **Lockdown.** At `hq_alert ≥ 4`, Lockdown is on for the rest of the run:
    - beam half-width doubles (4° to 8°);
    - the Blade level on HQ fights is +1, capped at 2.
18. **Stall.** An action at the current node, once per layer. It advances `eye_step` by 1, completes no node, and adds Alert (rule 16). It lets the Eye pass.
19. **Annex rooms.** Optional side nodes branching off a layer. Each is a non-fight node holding a rest, a cache or the Power Room. They follow the shuttered rule (13).
20. **Cut the Power.** The Power Room's one-time action, once per run. The Eye sleeps for 2 gaze steps: no sector, no beam, and no Blade at the HQ. Alert +2. The eye dial shows "asleep".

**Raid (one hook)**

21. **Wedge.**
    - The raid map draws the sector.
    - Corporate threats on a node inside it deal +25 % damage (per-node `RAID_STRENGTH_PCT`).
    - Defense nodes inside are SEEN.
    - If the Eye is FIXED, the wedge holds the fixed area.

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `eye_index` | int 0-7 | CampaignState | Drawn once from stream `eye_start`, checkpointed. |
| `eye_fixed_left` | int 0-2 | CampaignState | |
| `spotted_level` | int 0-2 | RunState | Snapshot at launch. |
| `eye_phase` | int 0-7 | RunState (HQ) | |
| `eye_step` | int | RunState (HQ) | Counts steps, including Stalls. |
| `hq_alert` | int | RunState (HQ) | Starts at `spotted_level`. |
| `hq_asleep_left` | int 0-2 | RunState (HQ) | Cut the Power. |
| `power_cut_used`, `stalled_this_layer` | bool | RunState (HQ) | |

- **Derived, not saved:** `bearing_deg`, `eye_az`, sector tests, node states, `lockdown` (alert ≥ 4) and `blade_slot`.
- **Determinism:** the only draw is `eye_start`. The HQ graph reads `hq_graph`.
- **Save impact:** additive fields only, save version +1, no migration (old saves are dropped).

## 3. Preview

- **Grid and launch card.**
  - The Spotted level shows as pips.
  - The card states what the Eye does after this campaign turn ("moves to octant N" or "FIXED n left").
  - On an Exploit Site: "Taking this fixes the Eye here for 2 turns."
  - A launch card notes that a failed run still moves the Eye.
- **Fight.** The scanned slice is outlined, and the result chips already include the tier drop. A slice with ENCRYPTED shows "absorbs Blade".
- **HQ.**
  - The dial shows the next 3 sector centres.
  - Each node shows open, IN THE EYE (SPOTTED), SHUTTERED or BLOCKED.
  - Hovering an edge shows the gaze at arrival.
  - Stall previews the new gaze and Alert.
  - Cut the Power previews "asleep 2 steps".
  - Alert and the Lockdown threshold are shown as a bar.
- **Raid.** The wedge and SEEN badges show during setup, with the projected outcome including +25 %.
- **No "?" anywhere.** `eye_start` resolves before any preview.

## 4. Numbers

| Value | Placeholder | Key |
|---|---|---|
| Sector | 90° | `config: campaign_config.eye_sector_deg` |
| Octant step | 45° | `config: campaign_config.eye_step_deg` |
| Moves per campaign turn | 1 | `config: campaign_config.eye_move_per_turn` |
| Fix duration (campaign turns) | 2 | `config: campaign_config.eye_fix_turns` |
| Blade tier drop | 1 | `config: campaign_config.blade_tier_drop` |
| Level 1 Blade classes | ELITE, MINI_BOSS, Rack | `config: campaign_config.blade_classes_l1` |
| Level 2 Blade classes | all fights | `config: campaign_config.blade_classes_l2` |
| Level 2 Elite Heat | +1 | `config: campaign_config.spotted_elite_heat` |
| Gaze step per node / climb / Stall | 1 / 2 / 1 | `config: campaign_config.hq_gaze_step_per_node`, `…_per_climb`, `…_per_stall` |
| Beam half-width | 4° | `config: campaign_config.hq_beam_half_width_deg` |
| Dial look-ahead | 3 | `config: campaign_config.hq_dial_steps` |
| Alert gain (eye fight / Stall / Power cut) | 1 / 1 / 2 | `config: campaign_config.hq_alert_gain_eye_fight`, `…_stall`, `…_power_cut` |
| Lockdown threshold | 4 | `config: campaign_config.hq_lockdown_alert` |
| Lockdown beam multiplier / Blade bonus | ×2 / +1 | `config: campaign_config.hq_lockdown_beam_mult`, `…_blade_bonus` |
| Power cut asleep steps | 2 | `config: campaign_config.hq_power_cut_steps` |
| Raid damage inside the sector | +25 % | `config: campaign_config.raid_eye_damage_pct` |

## 5. Tests to write

| Test | Tier | Asserts |
|---|---|---|
| `test_bearing_deterministic` | fast | The same seed gives the same bearings. |
| `test_sector_membership_edges` | fast | The half-open sector: a boundary bearing belongs to exactly one octant. |
| `test_eye_moves_each_campaign_turn` | fast | The index advances by 1 per ended netrun (win, death, abandon), mod 8. |
| `test_exploit_fixes_two_turns` | fast | The fix is set after that turn's tick. The next 2 turns hold the Eye and the third moves it. |
| `test_second_exploit_resets` | fast | Re-aims and resets to 2; it never stacks. |
| `test_spotted_level_snapshot` | fast | The level is 0 / 1 / 2 per rule 6 and constant mid-run. |
| `test_blade_normal_fights_level2` | fast | Level 2 applies the Blade to normal fights, level 1 doesn't, and level 0 never does. |
| `test_blade_slot_and_encrypt` | fast | The scanned slot skips empty slots and is the same after undo. ENCRYPTED absorbs and is consumed. |
| `test_blade_preview_equals_result` | full | The chips equal the resolve at levels 1 and 2. |
| `test_hq_gaze_pure` | fast | The gaze is a function of (phase, step). A climb adds 2, a Stall adds 1. |
| `test_hq_node_states` | fast | A fight node in the eye is SPOTTED, a non-fight node (including Annex) is SHUTTERED, and the beam band is BLOCKED. |
| `test_hq_alert_lockdown` | fast | Alert starts at `spotted_level` and gains per rule 16. At 4, the beam doubles and the Blade level is +1, capped at 2. |
| `test_stall_once_per_layer` | fast | A second Stall is refused. Stall advances the step and adds Alert. |
| `test_cut_the_power` | fast | The Eye sleeps for 2 steps (no sector, no Blade), the action is once per run, and Alert is +2. |
| `test_hq_graph_reachable` | full | For all 8 phases there is an open node per layer at the normal beam, and at most 7 Stalls open one. |
| `test_raid_wedge_damage` | fast | Threats inside the sector deal +25 % and threats outside deal 0 %. A fixed wedge holds. |
| `test_eye_save_roundtrip` | fast | All new fields survive save and load, and `eye_start` is not redrawn. |

## 6. Build slices

1. **Eye state and pure functions** (sector, move, fix, campaign turn hook, `eye_start`): M, no dependencies.
2. **Grid bearings, spotted badge and launch card, Grid pips:** M, depends on 1. The art pass owns the 3D hatch and wedge look.
3. **Blade rider** (levels 1 and 2, normal fights, Heat): M, depends on 1. It uses N9 TIER_DOWN. Fallback: a resolver-side tier modifier.
4. **Raid wedge** (per-node `RAID_STRENGTH_PCT`, SEEN badges): S-M, depends on 1.
5. **HQ gaze, node states, beam, shuttered, dial and reachability check:** L, depends on 1 and 3. N16 `map_edits` can carry node states.
6. **Alert and Lockdown:** S, depends on 5.
7. **Stall and Annex rooms:** M, depends on 5.
8. **Cut the Power:** S, depends on 7 (the Power Room is an Annex room).

Introduction order: street level 1, then level 2 with FIXED, then the raid wedge, then the HQ.

## 7. Q-DESIGNER

Q-DESIGNER: Do other actions that pass time on the Grid (a raid, a patrol) also count as campaign turns that move the Eye? (No: only ended netruns.)
Q-DESIGNER: Is Lockdown (beam ×2, Blade +1) the right shape for Alert, or should it summon a Warden fight? (Beam and Blade only.)
Q-DESIGNER: Should Stall cost something besides Alert and a step, such as Heat? (No.)
Q-DESIGNER: Should Annex rooms be exempt from SHUTTERED, since they are optional? (No, they follow H4.)
Q-DESIGNER: Should Cut the Power be once per run, or a Daemon or Exploit-linked reward? (Once per run, in the Power Room.)
Q-DESIGNER: Should a FIXED Eye give a stronger raid bonus than a moving one? (No, the same +25 %.)
