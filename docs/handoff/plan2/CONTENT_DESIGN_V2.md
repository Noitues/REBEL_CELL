# CONTENT_DESIGN_V2: rules and specs from the 2026-10-16 content rulings

**Status:** for the designer's review before any build. Nothing here is built.

**Source of truth:** DECISIONS "2026-10-16 — Designer rulings: content design (CONTENT_CONCEPTS §6.2) and G1–G16".
It supersedes `CONTENT_CONCEPTS.md` and `G_REEVAL.md` wherever they differ; CONTENT_CONCEPTS is used here only for
inventory and diagnosis facts.

**Inputs:**
- `docs/GDD.md` v0.9;
- `content/` (57 enemies, 5 corporations);
- `docs/balance/BASELINE_e2e13918.md`;
- `scripts/core/` (combat_resolver, effect_interpreter, wheel_math, netrun_session);
- `scripts/data/`.

Drafted by a read-only Plan agent 2026-10-16; saved by the orchestrator.

**Conventions:**
- Every number names its file. **(new)** marks a field that doesn't exist yet.
- All numbers are placeholders until the balance sim runs.
- Names are placeholders: no effort on names until a few enemy passes have happened.
- Size: S = content or a few lines; M = a new field or handler + tests; L = a new mechanic + UI.
- The core stays deterministic: no new randomness outside checkpointed RNG streams, and the preview equals the
  result.

**Baseline facts** (`BASELINE_e2e13918`):
- **Boss:** a fresh boss fight takes 38 turns and the player wins 25 %. Inside campaigns, a T4 boss takes 41–50 turns
  and the player wins 4–8 %.
- **Campaign length:** 605 min, against the GDD 11.8 target of ~395.
- **Long fights:**
  - Account Manager: 20.7 turns at T3; 20 % win at T4.
  - Recall Unit: 20.2 turns at T3, 36 at T4.
  - Triage Unit: 3.9 heal turns at T4.
- **Too lethal / too weak:**
  - Care Swarm: 0 % win at T4; 43 HP lost at T3.
  - Dosage Dispenser: 0.05 damage per turn.
- **Code facts:**
  - 75 % of the Genome Core's 1,475 HP is the tier factor.
  - Hub HEAL ignores `output_scale`.
  - `_apply_wheel_override` wipes statuses.
- **Damage-scale mismatch:** GDD 11.6 says 1.2^(t−1), the config has 1.3 and the schema default is 1.6. One table
  replaces all three (R2).

## 1. Design rules
**R1. Phases are the unit of fight length.**

| Class | Phases | Turns per phase | Target fight |
|---|---|---|---|
| Normal | 1 | 3–4 | 3–4 |
| Elite | 2 | 3–4 | 6–8 |
| Mini-boss | 2–3 | 3–4 | 6–12 |
| HQ boss | 4–5 | 3–4 | 12–20 |

- Every phase asks a new question; none is attrition.
- Elites gain phases (this replaces M7's +25 % HP).
- Every enemy is designed directly; the shared boss template goes away.
- `EnemyData.validate` allows one phase entry on elites and none on normals.

**R2. Tier sets base values only.**
- **Starting HP and starting damage** come from the tier.
- **Flat enemy amounts** (heal, block, shield, hits) × the enemy's tier damage factor. This fixes the hub HEAL.
- **Percent amounts** read the enemy's own max HP and are never scaled again.
- **Buffs and debuffs** (×1.25, −25 %, ×0.5) don't depend on tier.
- **Damage table:** `campaign_config.tres` `enemy_damage_by_tier` **(new)** = [1.0, 1.3, 1.69, 2.2] (today's
  1.3^(t−1) made explicit).
- **HP by band, not a multiplier:**
  - Enemies author `EnemyData.hp_by_tier` **(new)**, 4 entries.
  - Bosses author `hp_bands` **(new)**: {ICE boss-strength zone ceiling, HP}, i.e. "if the multiplier is in this
    zone, HP is X".
  - Validation checks each value against the class band.
- **Phase budget:** `reference_dpt_by_tier[t]` × `target_turns_per_phase` × (needles the player's hits land on),
  minus the phase's sustain per turn × `target_turns_per_phase`.
  - `reference_dpt_by_tier` **(new)** = [9, 11, 14, 18].
  - `target_turns_per_phase` **(new)** = 3.5.
  - The reference player is calibrated in §4 step 0: between testers (3.2–5.0 per turn) and the bot's best play
    (16–35).

| Class (phases) | T1 | T2 | T3 | T4 | Today at T3 |
|---|---|---|---|---|---|
| Normal (1) | 28–36 | 34–44 | 44–56 | 56–70 | 64–128 |
| Elite (2) | 56–72 | 68–88 | 88–112 | 112–144 | 271–287 |
| Mini-boss (2) | 56–72 | 68–88 | 88–112 | n/a | 384 |
| Mini-boss (3) | 85–105 | 104–128 | 132–162 | n/a | 384 |
| Boss (4–5) | n/a | n/a | n/a | sum of phase budgets (~300 Genome Core) | 1,475 |

A phase with more enemy needles gets proportionally more HP, because of the pointer rule (GDD 2.7).

**R3. Damage parks at phase thresholds.**
- While a phase is active, the HP floor is ceil(max HP × the next threshold) (a CombatantState field **(new)**).
- A hit that would cross the floor leaves HP at the floor; the excess is lost. This applies on every loss path:
  `deal_hit`, self-damage, parasites, pierce.
- The phase changes at the end of that resolve; later hits in the same resolve are also lost.
- The last phase has no floor.
- The preview shows "PARKED −N".

**R4. Health triggers phases; turns trigger enrage.**
- `EnrageData` **(new)**: start_turn, every_n_turns, damage_pct_step. It raises damage only, not heal or defense.
- Class defaults in `campaign_config.tres` `enrage_defaults` **(new)**:

| Class | Start | Every | Step |
|---|---|---|---|
| Boss | 10 | 5 | 25 % |
| Mini-boss | 10 | 5 | 25 % |
| Elite | 8 | 5 | 25 % |
| Normal | off | n/a | n/a |

- Steps are additive (×1.25, ×1.5, …); see question 2.
- A boss may author its own trigger, e.g. "a slice repeats before all slices have fired".

**R5. Amount modes.**
- `amount_mode` **(new)**, FLAT or PERCENT, on heal, block, shield and corruption (`EffectData`, `SliceData`). It is
  a mode on the existing effects, not a new status.
- PERCENT means a share of the owner's max HP (heal, block, shield), or a share of the target's non-NULL slices
  (corruption; rounded, minimum 1).

**R6. Statuses survive phase changes.**
- `_apply_wheel_override` keeps statuses. When the layout changes, each status moves to the new slice that covers the
  old slice's centre tick; stacks on the same slice merge.
- `BossPhaseData.cleanse_on_enter` **(new)**: NONE / OWN / PLAYER / BOTH. Usually it is a buff with a counter
  Exploit.

**R7. Boss buffs and Exploits.**
- `EnemyData.buffs` **(new `BossBuffData`)**, each countered by `ExploitData.disables_buff` **(new)**. An Exploit is
  just the name that turns a buff off.
- A Grid draws a subset of the corporation's Exploit pool (`exploits_per_grid` **(new)** = 5), so not every buff is
  counterable every run.
- Buffs are strong. `min_exploits_for_breach = 3` stays.

**R8. Statuses vs the Parasite ring.**
- **Statuses are anti-Firmware.** They change how a slice performs, never what it does:
  - OUTPUT_DOWN: −25 % output per stack;
  - TIER_DOWN: each landing reads one tier lower per stack (Perfect → Good → WEAK);
  - OVERCLOCKED, ENCRYPTED and CORRUPTED (R9).
- **×N stacks.** Today's PARASITE status becomes a 2-stack OUTPUT_DOWN.
- **Parasites are anti-slices on the Parasite ring:** anything a slice can do, against you. They can damage you,
  reduce your damage to the boss, apply or remove statuses, and drain RAM.
- New status types are allowed once these rules are approved.

**R9. Corruption is a RAM debuff.**
- A card or nudge acting where the acting pointer reads a CORRUPTED slice costs `corrupted_ram_cost_multiplier`
  **(new)** = 2× RAM.
- CORRUPTED deals no damage any more; damage moves to the Parasite ring.
- `corrupted_self_damage`, `corrupted_damage_per_major` and `corrupted_ram_drain` retire.
- OVERCLOCKED still burns out into CORRUPTED.

**R10. Pointers may sit on any tick** (GDD 2.1 amendment). Uneven needles are the main tool for "only one can be
Perfect".

**R11. Slice sizes vary, even sizes included.**
- Each slot gets `size_ticks` **(new)**; a wheel's sizes sum to 30.
- **Sub-tick quality** by distance d from the slice centre: d = 0 → PERFECT; d ≤ 1 → GOOD; otherwise WEAK.

| Size | Default map |
|---|---|
| 2 | G G |
| 3 | G P G |
| 4 | W G G W (no Perfect) |
| 5 | W G P G W (today's slice) |
| 6 | W W G G W W |
| 7 | W W G P G W W |

- A slot may author an override map, `tick_quality` **(new)**.
- A Firmware (placeholder "Calibrated") raises every sub-tick one tier: a 4-tick slice reads G P P G.
- The loadout screen shows each slice's map.

**R12. Satellites are fixed.**
- A satellite is fixed to its slice; its wheel can't be nudged, spun, respun or changed.
- Exceptions: one operative class, plus `can_move_satellites` **(new)** on some Firmware and Daemons.
- Docking on an occupied slice replaces the satellite there (`on_occupied = REPLACE` **(new)**). This amends
  GDD 2.7.

**R13. The player defense trio.**

| Name | Today's type | Rule |
|---|---|---|
| BLOCK | DEFRAG | Temporary; expires at the start of your next turn |
| SHIELD | SANDBOX | Lingers; capped by `shield_cap` = 15 |
| SANDBOX | DETOUR (evade) | Negates one whole attack: every hit of one resolution |

- Pierce ignores BLOCK and SHIELD, not SANDBOX or bodyguards.
- The enum ints are kept for saves; only the display names and the SANDBOX rule change.

## 2. Genome Core: full spec (a doctor treating a progressing disease, and the disease is you)
**Concept:** a mild start that ramps: more heal, then a second needle, then no defense and every hit corrupts. Your
corrupted slices are both its damage multiplier and your RAM tax.

**Files:**
- `content/enemies/renewal_engine.tres` (the id stays);
- new slices `content/slices/gc_*.tres` (barrier, immunization, iv, medicine, adrenaline).

**HP bands (T4)** by ICE zone: ≤ 1.00 → 300 · ≤ 1.15 → 330 · ≤ 1.30 → 360 · > 1.30 → 400.

**Thresholds:** 0.82 / 0.68 / 0.33, from the R2 budget at 18 damage per turn (≈ 3.5 turns per phase):
- P1 (18 − 3) × 3.5 ≈ 52 HP;
- P2 (18 − 6) × 3.5 ≈ 42 HP;
- P3 and P4 (2 × 18 − 6) × 3.5 ≈ 105 HP each.

**Enrage:** the defaults (turn 10, turn 15, …). The expected path puts P3 in the first step and P4 in the second.

**New slice riders** (N20): `hits`, `hits_per_target_status` (IV), `perfect_multiplier` (Medicine), `pierce`
(Adrenaline). **New trigger:** ON_HIT_DEALT (N6).

| | P1 Screening (100 → 82 %) | P2 Treatment (82 → 68 %) | P3 Intensive Care (68 → 33 %) | P4 Code Blue (33 → 0 %) |
|---|---|---|---|---|
| Needles | 1 | 1 | 2: ticks 0 / 14 (uneven) | 2 |
| Heal (hub, PERCENT) | 1 % max HP per turn | 2 % | 2 % | 2 % |
| Layout (ticks, sum 30) | Barrier 6 · Immun 4 · Immun 4 · Barrier 6 · Immun 4 · Null 6 | Barrier 8 · IV 4 · Medicine 3 · Null 4 · IV 4 · Immun 4 · Medicine 3 | Barrier 5 · IV 4 · Med 3 · IV 4 · Immun 4 · Med 3 · IV 4 · Null 3 | IV 4 · Adren 3 · IV 4 · Null 4 · Adren 3 · IV 4 · Adren 3 · Null 5 |
| Barrier (BLOCK) | 12 | 20 (fewer, bigger) | 14 | none |
| Immunization | 5 damage + CORRUPTED on 1 random non-NULL slice of yours | as P1 | as P1 | none |
| IV | n/a | 2 damage × your CORRUPTED slices (min 1), separate hits | as P2 | as P2 |
| Medicine / Adrenaline | n/a | Medicine 10, ×4 on a Perfect | Medicine 10, ×4 on a Perfect | Adrenaline 10, ×4 on a Perfect, **pierce** |
| Hub rule | Metabolism | Metabolism | Metabolism | Metabolism + **Code Blue:** every enemy hit that reaches you (not SANDBOXed) corrupts one of your slices |
| Intake target (damage per turn) | 2–4 | 5–8 | 8–12 | 12+ before enrage |

**Transitions:** each one parks damage (R3), keeps statuses with the remap (R6), plays a phase line and reveals the
new layout (on entry only, under Chart Hidden).
- P1 → P2: `wheel_override` + `hub_override` (heal 2 %).
- P2 → P3: `wheel_override` + MULTIPLY (0, 14).
- P3 → P4: `wheel_override` + `hub_override` (Code Blue).

**Buffs and their Exploits** (a route draws a subset):

| Buff (strong) | Effect | Counter Exploit turns off |
|---|---|---|
| Metabolism | The per-phase hub heal | All boss heal |
| Second Opinion | The 2nd needle in P3–P4 | The 2nd needle (today's Breach) |
| Sterile Field | Cleanses its own statuses on each phase change | Statuses stick across phases |
| Compliance Lock | Resistance 2 (absorbs nudges; blocks Flip and Respin) | The resistance |
| Antibodies | Immunization corrupts 2 slices | Back to 1 |
| Booster | IV minimum 2 hits | Minimum 1 |
| Triage Reserve | Starts each phase with SHIELD = 5 % max HP | No shield |
| Chart Hidden | Phases and next layouts hidden | Reveals them (today's Intel) |

**Your counterplay:**
- **P1:** steer its needle to Null or an Immunization's WEAK edge; avoid feeding it Barrier turns. Keep your
  CORRUPTED count low (Cleanse, Encrypt), because P2 multiplies it. Burst through; P1 is short.
- **P2:** deny the Medicine Perfect: a 1-tick nudge turns ×4 into ×1 (Compliance Lock makes that cost real RAM).
  SANDBOX the landed Medicine or a big IV; SHIELD the IV chip damage. Corrupted slices double your RAM, so cleansing
  is both defense and economy.
- **P3:** two needles mean your hits land twice: race. Uneven needles let you choose which one reads the dangerous
  slice. Flip works if Compliance Lock is off.
- **P4:** no boss defense. Every hit corrupts you; IVs grow; pierce leaves SANDBOX and steering as your only defense.
  Finish before the turn-15 step.

**Fallback without N12** (variable slice sizes): P1 and P2 on 5-tick slices; defer P3 / P4. Not recommended:
Medicine's narrow window is the core question.

## 3. Mini-boss concepts (one per corporation)
These guard the final Rack of every netrun at T1–T3.
- **HP (R2 band):** 2 phases → T1 63 / T2 77 / T3 98; 3 phases → 95 / 116 / 147, minus sustain.
- **Thresholds:** 0.5 for 2 phases; 0.66 / 0.33 for 3.
- **Enrage:** the mini-boss default.

| Corporation · file | Phases | Hook | Phase plan | Counterplay | Needs |
|---|---|---|---|---|---|
| **Solace** · `account_manager.tres` | 2 | RAM economy: fixed bodyguards, then a counter on your Perfects | **P1 Retainer:** 2 fixed Retainer satellites on Overflow and Dose (Fortress: attacks at a guarded slice hit the guard). Late Fee listener: +2 BLOCK per paid nudge. **P2 Collections:** the guards drop; Clawback listener hits 4 on every player Perfect; Dose corrupts (doubles your RAM). | P1: steer to an unguarded slice or Null; use the free nudge and cards. P2: Good over Perfect unless your Perfect hook pays for the Clawback. | N1, N3, N6, N9, N13 |
| **Halcyon** · `city_manager.tres` | 3 | ×N status stacks and nudge lockout | **P1 Ordinance:** Citation puts OUTPUT_DOWN ×1 on your slice under the pointer, stacking to ×3. **P2 Curfew:** when its needle starts on Curfew, its wheel is nudge-locked (cards still work). **P3 Martial Law:** a 2nd needle (0 / 13); Citations ×2; Hotfix heals 3 %. | Rotate your landing to spread or dodge stacks; Cleanse; Encrypt absorbs one. P2: carry a spin or Flip card. P3: kill the Hotfix window. | N1, N3, N7, N8, N9, N11 |
| **Meridian** · `logistics_director.tres` | 3 | Parasite ring and respin lock | **P1 Intake:** Weight (resistance 3, restored each turn); orbit 2 per turn (readable ahead). **P2 Packages:** every other turn it latches a 4-tick Package parasite on your wheel (max 2): when read, drain 2 RAM and −50 % to your damage. **P3 Overtime:** respin lock on both wheels; Weight 1. | P1: plan two turns ahead. P2: land off the Packages; Cleanse removes one. P3: a pure deterministic plan, so solve it. | N3, N7, N10 |
| **Orbital** · `mission_director.tres` | 3 | Rim gates and satellite replacement | **P1 Countdown:** 2 rim gates; a nudge or spin that carries a gate past its needle advances a countdown (the respin never counts); at 3, its next resolve adds an Overflow. **P2 Deploy:** each turn it launches a fixed satellite onto a slice, replacing any satellite there; Flares overclock your slice. **P3 Abort Window:** crossing a gate deals 6 to it; orbit 3. | P1: route around the gates (Flip and Snap don't traverse). P2: steer around guards rather than killing them. P3: big precise spins pay. | N13, N15 |
| **REBEL_CELL** · `the_handler.tres` | 3 | It mirrors you | **P1 Shadow:** your nudges on your own wheel move its wheel the same way. **P2 Override:** your own-wheel nudges are locked every other turn; an Echo listener replays your landed slice at you at 50 % on each Perfect. **P3 Burn Notice:** 2 uneven needles (0 / 11), Citation + Dose; enrage authored at turn 8. | P1: find the shared good rotation (Jam / Strip / Freeze move only its wheel). P2: plan with cards; weigh Perfects against Echo. P3: one needle dangerous, one safe. | N6, N7, N9, N11 |

## 4. Enemy direct-design pass plan
**Inventory** (normals 1 phase / elites 2 / mini-boss / boss / satellites):

| Corporation | Normals | Elites | Mini-boss | Boss |
|---|---|---|---|---|
| Solace | billing_daemon, care_swarm, collections_agent, compliance_officer, dosage_dispenser, triage_unit | claims_adjuster, recall_unit | account_manager | renewal_engine |
| Meridian | cargo_hauler (72 HP: elite-sized), conveyor_warden, customs_scanner, drone_dispatcher, route_optimizer, tariff_collector | last_mile_enforcer, port_authority | logistics_director | the_manifest |
| Halcyon | parking_warden, patrol_unit, permit_office, surveillance_mast, transit_controller, utility_meter | riot_control, zoning_board | city_manager | civic_core (THE PANOPTICON) |
| Orbital | ground_control, launch_pad, orbital_debris, tracking_station, uplink_relay, weather_satellite | geostationary_guard, station_commander | mission_director | commons_array |
| REBEL_CELL | cell_informant, dead_drop, echo_process, handler_proxy, loyalty_test, mirror_script | rc_template_elite, rc_template_elite_b | the_handler | dispatch_core (Sync Strike pass) |

**Questions per normal** (1 phase, 3–4 turns):
1. What one question does it ask, and which answer shortens the fight?
2. Is its intake per turn at the reference player above 0? (The Dosage Dispenser fails this.)
3. Sustain: at most one source, at most 30 % of the reference damage per turn. (The Triage Unit fails this.)
4. HP inside the band, per tier.
5. Which systems does it need? Prefer data-only.
6. Which layer: L1–2 teaching, or L5–6 pressure?

**Elites** (2 phases, 6–8 turns), all of the above plus:
- How does the question flip at the threshold?
- Which phase is the burst window?
- Its strong move, and what threshold parking protects.
- Keep or retire its `heat_effects`?
- Enrage default or authored?

**Order (worst first):**
- **Step 0, calibrate:** skill sweeps (`balance.py run fight --enemy all --tiers 1 --skill 0.5…0.9`) set
  `reference_dpt_by_tier`. Per-corporation sweeps (`--corp`) are needed too; only Solace is in the baseline.
1. Triage Unit
2. Account Manager
3. Recall Unit
4. Claims Adjuster
5. Care Swarm
6. Compliance Officer
7. Dosage Dispenser
8. The rest of Solace
9. The other corporations by sweep rank: the high-HP elites first (Station Commander 154, Geostationary Guard 145,
   Port Authority 144, Riot Control 142, Last-Mile Enforcer and Zoning Board 132), Cargo Hauler early.

**Verification:**
- Work on branch `balance` (its path guard limits it to data) with `--set` / `--variant`, then commit the `.tres`.
- `balance.py run fight --enemy <id> --tiers 1,2,3,4 --seeds 1000:1019`, then
  `compare … --name <id>_vN` → `docs/balance/CMP_*.md`.
- **Pass criteria (proposal)**, at the step-0 skill and at skill 1.0:
  - mean turns inside the class target, p90 at most target + 2;
  - win ≥ 95 % at T1–T2 and ≥ 90 % at T3;
  - threat per turn > 0;
  - at most 1 heal turn per phase;
  - 3–4 turns per phase (needs N19).
- **After each batch:** campaign ICE 0 / 5, minutes against ~395. Boss: `--source campaign|fresh`, 12–20 turns, and
  `--policy heuristic --lookahead 2` for "is it a puzzle".

**Lane (designer: Batch API where it fits):**
- **Drafting:** one Message Batches request per enemy (and per corporation for the mini-bosses), with the R1–R13
  rules, that enemy's data, its sim numbers and the findings → a design draft. Sonnet for design quality.
- **Choosing:** the orchestrator picks from the drafts; nothing auto-applies.
- **Content edits and sim runs:** a local agent on branch `balance`.

## 5. New systems implied
| # | System | What | Code area | Size | Depends on |
|---|---|---|---|---|---|
| N1 | Amount modes | FLAT / PERCENT; flat enemy amounts × the tier damage factor | `effect_data`, `slice_data`; `effect_interpreter._scaled`, heal / gain_*; `combat_resolver._resolve_pointer` | S–M | none |
| N2 | Tier base-value tables | `hp_by_tier`, boss `hp_bands`, `enemy_damage_by_tier`, `reference_dpt_by_tier`, a band validator | `enemy_data`, `campaign_config_data` + `.tres`; `netrun_session.enemy_scale()` / `enemy_output_scale()`; `combat_resolver.create_combat`; a lint test | M | none |
| N3 | Phases on every class, threshold parking, status keep, cleanse on enter | HP floor on every loss path; the centre-tick status remap; `cleanse_on_enter`; the PARKED preview | `enemy_data.validate`, `boss_phase_data`; `combat_resolver._check_boss_phases`, `_apply_wheel_override`; `effect_interpreter.deal_hit`; CombatantState | M | none |
| N4 | Enrage | `EnrageData` + class defaults; a HUD countdown chip | new `enrage_data.gd`; `combat_resolver.start_turn`; HUD | S | none |
| N5 | Boss buffs and Exploits | `BossBuffData`; `disables_buff`; the Grid draws a subset | new data file; `exploit_data`, `site_data`; `campaign_rules` (Grid build); breach overrides; HQ Exploit list UI | M–L | N3 |
| N6 | Enemy listeners | Reactions to the player's ON_NUDGE / ON_CARD_PLAYED / ON_PERFECT; ON_RAM_SPENT, ON_HIT_DEALT. Inside the action, no random input, undo-clean. | `rc.gd`, `enemy_data` / `hub_core_data`; `combat_resolver._apply_nudge` / `_apply_card` / `_resolve_pointer`; preview | M | none |
| N7 | Block nudge / respin | `nudge_locked` / `respin_locked` (source, turns); LOCK_* effects; refusals with reasons; an overlay | `rc.gd`, `wheel_state`, `combat_resolver.validate_action` / `start_turn`; `ui/wheel` | S–M | N6 (optional) |
| N8 | ×N stacks | Slot statuses become {status: stacks}; save version 2 → 3 with migration; a ×N badge | `wheel_state` (13 call sites), `effect_interpreter.apply_status` / `cleanse`; `save_service`; UI | M–L | none |
| N9 | Status rules + corruption as a RAM cost | OUTPUT_DOWN, TIER_DOWN; PARASITE status → OUTPUT_DOWN ×2; CORRUPTED = RAM ×2; self-damage retired; RAM forecast; Codex / tutorial text | `rc.gd`, `combat_resolver` cost paths, `_corrupted_trigger`, `parasite_handler`, `campaign_config_data`; `ram_bar.gd` | M | N8 |
| N10 | Parasite ring | Enemy-owned partial outer ring of segments on your wheel (rotates with it); anti-slice effects when read; LATCH_PARASITE; Cleanse removes a segment; preview; rim art | new `parasite_segment_data.gd`; `wheel_state`; `combat_resolver._collect_resolutions`; `effect_interpreter`; `ring_mods.gd`, `wheel_face.gd` | L | N1, N9; reads best after the inner-ring redesign |
| N11 | Pointers on any tick | GDD 2.1 amendment; uneven layouts; HUD readability for close needles | `combat_resolver` (`EXTRA_POINTER_OFFSETS`); `ui/wheel` | S | none |
| N12 | Variable slice sizes + sub-tick map | `size_ticks`, `tick_quality`; Firmware tick step. WheelMath on cumulative boundaries (slice_at, offset, tier, mirror, snap, Mirror / Shunt). Lift the 6-slice cap. Wedges; the sub-tick map on `loadout_view.gd`. | `wheel_slot_data`, `wheel_data`, `firmware_data`; `wheel_math.gd`; `wheel_state`; `snap_to_center`; `wheel_wedge.gd`; `loadout_view.gd`; the shop overwrite | L | none (needed before the Genome Core) |
| N13 | Fixed satellites + replacement | Refuse moves unless `can_move_satellites`; Undock scoped to it; `on_occupied = REPLACE` | `satellite_spawn_data`, `combat_resolver._spawn_satellite` / `validate_action`; `undock_handler`; class / Firmware / Daemon data | S–M | none |
| N14 | Defense trio | BLOCK / SHIELD / SANDBOX names; SANDBOX negates a whole resolution; pierce doesn't bypass it | `effect_interpreter.gain_evade` / `deal_hit`; `combat_resolver._slice_action`; glyphs, Codex, strings | S–M | none |
| N15 | Rim gates (G7, earlier) | Gate ticks + effects; traversal detection in nudges and spins (never the respin); the preview lights crossed gates | `wheel_data` (gates), `wheel_math`, `effect_interpreter.nudge` / `spin`; `ui/wheel` | M | none |
| N16 | Events that alter future fights / paths; impromptu fights | A run-level `next_combat_overrides`; `EventChoiceData.starts_combat` / `combat_overrides` / `map_edits` | `event_choice_data`; `netrun_session`, `map_graph`; RunState | M | N2 |
| N17 | Event wheel | `EventWheelData` (outcome slices, nudge budget, extra-nudge cost); a page reusing the wheel kit; `events` RNG at a checkpoint | new data file; `netrun_session`; `wheel_kit.gd` | M | N12 (optional) |
| N18 | Data-driven rewards list | `RewardTableData` rows (kind, pool, count, chance, conditions: node type / elite / Rack / tier / layer) replace the hard-coded offers in `_finish_combat` (~432–446); a `slice_flash` row kind for Racks | new `reward_table_data.gd` + `content/config/reward_table.tres`; `netrun_session._finish_combat`, `_offer`; RewardList UI | M | flash waits for the slice-upgrade pass |
| N19 | Sim metrics | Turns per phase for every class, parked damage, enrage step reached, intake per phase, listener fires | `tools/balance/balance_runner.gd`, `balance.py` | S | N3, N4 |
| N20 | Slice riders | `hits`, `hits_per_target_status`, `perfect_multiplier`, `pierce` | `slice_data`; `combat_resolver._resolve_pointer` / `_slice_action` | S–M | N9 |

**Build order:**
1. **Foundation:** N1 → N2 → N3 → N4 → N19, with N11, N13, N14 in parallel.
2. **Expressiveness:** N8 → N9 → N20; N6 → N7; N12 (the longest; start early).
3. **Bosses:** N5 → Genome Core → the Solace / Halcyon / REBEL_CELL mini-bosses → N15 + the Orbital mini-boss → N10 +
   the Meridian mini-boss.
4. **Run layer:** N18, N16, N17.

**Challenges:**
- N8 changes the save format.
- N12 touches every wheel-geometry caller and the UI.
- N6 must keep preview = result: listeners react to staged actions and undo with them.
- N10's readability depends on the inner-ring redesign.

**Lanes:** the N-systems touch `scripts/core` (rule-bearing): fix-rules agents, with an OPUS-BECAUSE where
determinism or preview = result is at stake. Content and balance: the Batch API for drafts, local agents on `balance`
for edits and sims.

## 6. Separate passes to schedule (not designed here)
| Pass | Scope as ruled | When |
|---|---|---|
| Raid design | R1 EXPOSED spotlight, R2 encrypted routes, R3 vehicle types, R4 Heat-scaled 2nd wave with an ultimatum (= the Schematics sink); all four in one pass | After the foundation wave |
| DISPATCH Sync Strike | A small fight per operative, then the final fight. Open: do the minis dictate effects in the final? A rotating focus across 3 player wheels before End Turn? | After the route / HQ redesign; needs N3–N7 |
| Events | Add more events first (consolidate and prune later); events in the HQ / raid view; a raid-win reward screen | Batch API drafting, one request per event; N16 / N17 enable decision events |
| Slice upgrades | Levels I, II, III, IV…; Rack "flash" (upgrade or swap; stronger Rack rewards) as an N18 row | After N18 and N12 |
| Card upgrades | A separate pass | — |
| Station bonuses | A unique bonus per class; alternates feel similar | `content/classes/*.tres` |
| Shop wheel | 100 / 80 / 100; a Daemon nudge or a paid nudge (Daemon makes the first free) | Per-slice price list (new) |
| Rim gates | Mechanic design (moved earlier) | Before the Orbital mini-boss |
| Inner ring redesign (G1) | Readability from afar; what it does and how to work it | Before N10's UI |
| Remove Site names | Sites are typed (Event, Normal / Elite / Mini-Boss / Boss Fight…); only the corporation, HQ building and boss keep names | Small |
| HQ netruns per corporation (G12) | Every HQ netrun unique, with unique mechanics | After the route / HQ redesign art |
| THE PANOPTICON rename | Display name only (id `civic_core` stays) | Queued |

## 7. Open questions for the designer
1. **Reference player:** tune the HP bands to the bot's best play, to testers, or to the midpoint
   `reference_dpt_by_tier` = [9, 11, 14, 18]?
2. **Enrage:** additive (×1.25, ×1.5) or compounding? Are the class defaults right (elite 8, mini-boss 10, normal
   off)?
3. **CORRUPTED on enemy wheels** (Virus): what does it do now that it's a RAM debuff? Does the free nudge cost 1 RAM
   on a corrupted slice?
4. **Defense trio:** confirm the mapping (DEFRAG → BLOCK, SANDBOX → SHIELD, DETOUR → SANDBOX), and that pierce
   doesn't bypass SANDBOX.
5. **Exploits:** do Intel / Breach / Virus stay as fixed gate types, or does any 3 of the drawn subset open the
   breach? How many does a Grid draw (5)?
6. **Satellites:** which operative class moves them? Does the Undock card stay?
7. Does a replaced satellite count as destroyed (Daemons, rewards)?
8. **Corruption amount modes:** FLAT = N slices, PERCENT = a share of slices?
9. Do enemy percent shields get their own cap?
10. Does the Parasite ring rotate with your wheel (proposed), or stay fixed in the pointer's frame?
11. Do statuses still apply on a WEAK landing (proposed: yes, unless a slice authors a minimum tier)?
12. **Boss win-rate target** at ICE 0 in the sim? Baseline: 25 % fresh, 8 % in campaigns.
