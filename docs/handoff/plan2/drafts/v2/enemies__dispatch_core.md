<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__dispatch_core; status ok; tokens in 11085 cache-write 0 cache-read 32585 out 23136; cost $0.130. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, slice contents):**
  - P4's "Echo Drone dock slot" is removed from the layout. The layout is now Order 5 · Forecast Strike 5 · Directive 4 · Audit Strike 5 · Null 6 · Order 5 = 30. Echo Drones are N13 satellites docked onto slices.
  - The unreadable P3 line is rewritten. Overwrite is a 3-tick G P G slice, so every landing on it deals full output (no WEAK edge).
  - P1 and P4 now state the consequence of 4-tick slices (W G G W): no Perfect, and WEAK edges halve output.
  - I re-added every layout: P1 5+5+4+6+4+6 = 30, P2 5+4+5+4+6+3+3 = 30, P3 3+5+4+5+3+5+5 = 30, P4 = 30, P5 4+4+4+4+5+4+5 = 30.
- **Issue 2 (BLOCKER, thresholds and budget):**
  - There is now one threshold set, **0.88 / 0.76 / 0.52 / 0.40**, used in every caption. It replaces both v1 sets.
  - The v1 sets could not be kept. When I re-derived the budget with R2's rule (HP proportional to the needles your hits land on), the v1 shares did not fit the band.
  - The "bonus ≈ 70" is replaced by explicit multipliers: ×2 for two needles, ×3 for three, with arithmetic in §4.
  - To fit, P4 is now a single orbiting needle, and P5 is a short 3-turn spike.
- **Issue 3 (BLOCKER, enrage timing):**
  - Cumulative phase ends are now 3.4 / 6.9 / 9.9 / 13.3 / 16.3 turns.
  - The turn-10 step lands on P4's first turn, not "P3–P4". The turn-15 step lands inside P5 (13.3 to 16.3).
  - §5 says this explicitly.
- **Issue 4 (BLOCKER, cleanse mode):**
  - "Cleans one stack tier" is deleted. `cleanse_on_enter` = **PLAYER** (the R6 enum, a full cleanse of the player's statuses) at P2 → P3 only. All other transitions use NONE.
  - Why: P2's stack-and-RAM question is self-contained. Unlike v1 I say plainly that this also clears CORRUPTED. N8 is not needed for the cleanse itself.
- **Issue 5 (MAJOR, buffs):**
  - The Forecast row remnant is fixed. Off means no repeat tax.
  - Legacy mapping is explicit: Intel → Chart Hidden, Breach → Second Needle, Virus → Cell Patch (3 legacy + 5 new = pool of 8).
  - Quorum is kept but redefined to be pointer-rule compatible: it halves each hit landing at the secondary needles. Its effect on phase length is shown in §4.
  - Second Needle's counter is redefined so that countering it does not remove your own hits.
- **Issue 6 (MAJOR, N# tagging):**
  - `repeat_multiplier` is N20 plus N6 with a saved per-turn field, replacing "NEW: last-landing record".
  - The Forecast record is a saved CombatantState field written at ON_RESOLVE (N6).
  - There is no NEW system left.
- **Issue 7 (MAJOR, Mirror Eye):** the dead rule is deleted.
- **Issue 8 (MAJOR, P1 intake):** intake is now given at the reference player, "5–8 with rotation, ~35 on a repeat", with the arithmetic.
- **Issue 9 (MAJOR, §10):**
  - The bot's best play is computed (8–19 turns across 16–35 dpt) and the fight is acknowledged to sit below target for top play.
  - DISPATCH authors its own `hp_bands` as the sum of phase budgets (400 to 520). They are not the Genome Core's 300 to 400, which could not fit this phase structure. The band is raised for ICE above 1.30.
  - There is no baseline row for this boss; the comparison is against the Boss row (38 turns fresh, 25 % win).
- **Issue 10 (NIT):**
  - Late Fee units are stated (1 % max HP of BLOCK per RAM, cap 3 RAM per turn).
  - The slice is named "Forecast Strike" and the buff "Forecast", with the relationship stated.
- **Triage rows:** all four are covered above (issues 1, 2, 3 and 4). No fix conflicted with a designer ruling.
- **Kept, because the critic marked them strong:**
  - the Forecast concept (a reading test, distinct from the Handler's mirror);
  - the P5 race with Code Red, no defense and three needles;
  - a single sustain source shown against the 5.4 cap.

---

# dispatch_core: direct design (v2)

## 1. Identity & the one question

**Class:** HQ boss (Central Server), T4 only. **Corporation:** REBEL_CELL. **Layers:** pressure only (the end of the final netrun).

**Concept: DISPATCH is the handler that planned you.** The Genome Core is a disease, and the Handler mini-boss mirrors your wheel in real time. DISPATCH has read your last turn and acts on it. Each phase borrows one corporation's affliction, and each ends with a twist that makes the previous answer wrong.

**Forecast rule.** Forecast Strike doubles when the slot your pointer is on this turn is the same slot you resolved last turn.
- The record is a saved field written at ON_RESOLVE (end of turn), so rewind cannot change it.
- The preview shows the doubling exactly.
- This is reading, not mirroring: the Handler reacts to your actions, DISPATCH reacts to your habits.

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Briefing | Can you act without a pattern? | Resolve a different slot each turn; the repeat tax never fires |
| P2 Audit | What do you spend? | Use the free nudge, not paid ones (Late Fee); Cleanse stacks before the Audit Strike |
| P3 Surveillance | Where do you look? | Park the needles on Null / WEAK edges; burst while they are safe |
| P4 Handoff | What will you ignore? | Steer onto unguarded slices; do not clear drones |
| P5 Root | Can you finish before it finishes you? | Pure race; keep corruption off your key slots |

## 2. Phase plan

Thresholds: **0.88 / 0.76 / 0.52 / 0.40**. Parked HP floors at 400 base: 352 / 304 / 208 / 160. Phase HP: 48 / 48 / 96 / 48 / 160 = 400.

FLAT amounts are authored at base and multiplied by `enemy_damage_by_tier` (T4 ×2.2). Only the T4 value is shown, rounded, with the base in parentheses. PERCENT amounts read max HP.

**Slice set** (`content/slices/dc_*.tres`):

| Slice | Type | Effect |
|---|---|---|
| Forecast Strike | OVERFLOW | 18 (8) FLAT; rider `repeat_multiplier` ×2 on a repeat (active only while the Forecast buff is on) |
| Order | SHIM | 13 (6) FLAT |
| Directive | DEFRAG (BLOCK) | PERCENT 5 % max HP |
| Citation | INFECT | OUTPUT_DOWN ×1 on your slice under the pointer |
| Priority | INFECT | Drain 3 RAM |
| Flare | INFECT | OVERCLOCK on a random non-NULL slice of yours |
| Dose | INFECT | CORRUPTED on a random non-NULL slice of yours (RAM ×2, R9) |
| Audit Strike | OVERFLOW | 22 (10) FLAT; `hits_per_target_status`: +1 hit per OUTPUT_DOWN stack on your landing slot, max 3 hits total |
| Overwrite | OVERFLOW | 26 (12) FLAT, **pierce** (P3); P5 variant 13 (6), pierce |
| Null | NULL | none |

**Hub: Archive (P1–P4).** PERCENT heal, 1 % max HP per turn; this is the only sustain. It is gone in P5.

### P1: Briefing (100 → 88 %), 1 needle at tick 0

| Layout | Forecast Strike 5 · Directive 5 · Order 4 · Null 6 · Forecast Strike 4 · Dose 6 = 30 |
|---|---|
| Statuses | CORRUPTED via Dose |
| Listener | **Forecast:** ON_RESOLVE writes your resolved slot id (N6) |

- The 4-tick Strike and Order read W G G W: no Perfect, and the edges halve output. A needle there is WEAK half the time, so Strike-4 is the milder hit.
- Directive blocks 5 % max HP (20 at 400).

### P2: Audit (88 → 76 %), 1 needle at tick 0

| Layout | Citation 5 · Order 4 · Priority 5 · Directive 4 · Audit Strike 6 · Dose 3 · Null 3 = 30 |
|---|---|
| Statuses | OUTPUT_DOWN up to ×3, CORRUPTED |
| Listener | **Late Fee:** ON_RAM_SPENT (N6). Each RAM you spend on a paid nudge gives the boss BLOCK of 1 % max HP, capped at 3 RAM per turn (12 HP max). |

- Late Fee is defense, not sustain. It only exists if you pay, and the budget assumes the free nudge only.
- Audit Strike is 6 ticks (W W G G W W): no Perfect, and WEAK on 4 of 6 ticks. Its multi-hit threat is stacks, not precision.
- **Transition P1 → P2:** `wheel_override`, statuses kept and remapped by centre tick (R6), `cleanse_on_enter` = NONE. Dose-corrupted slots carry into P2's RAM game.

### P3: Surveillance (76 → 52 %), 2 needles, ticks 0 and 11 (uneven, R10)

| Layout | Overwrite 3 · Flare 5 · Order 4 · Citation 5 · Null 3 · Forecast Strike 5 · Directive 5 = 30 |
|---|---|
| Statuses | OVERCLOCK via Flare |
| Listener | **Echo:** ON_PERFECT (N6) replays 25 % of your landed slice damage at you |

- Overwrite is 3 ticks (G P G): no WEAK edge, so any landing deals full 26 pierce. It is narrow (3 ticks of 30).
- With the needles 11 apart, a safe pair exists. Example: needle A on Null centre (tick 18, in 17–19) puts needle B on tick 29, a WEAK edge of Directive. That is the geometry the phase asks you to find.
- **Transition P2 → P3:** `wheel_override` + MULTIPLY (0, 11), `cleanse_on_enter` = PLAYER (full cleanse, including CORRUPTED). It resets P2's stack puzzle so Surveillance starts as its own question.

### P4: Handoff (52 → 40 %), 1 needle, ORBIT 2 ticks per turn (trail shown)

| Layout | Order 5 · Forecast Strike 5 · Directive 4 · Audit Strike 5 · Null 6 · Order 5 = 30 |
|---|---|
| Satellites | Existing `echo_drone.tres` (intent unchanged). The phase opens with 1 drone docked on Forecast Strike. When Directive resolves it launches a drone onto the Audit Strike slot (`on_occupied = REPLACE`, max 2). |
| Statuses | none new |
| Listener | Forecast continues |

- Directive is 4 ticks (no Perfect).
- A satellite on the slice under the needle takes your hit instead of the boss (bodyguard, GDD 2.7). Drones are fixed (R12, N13).
- The danger slices are the guarded ones. Steering onto unguarded Order lets your damage through, and the needle then also deals less damage to you.
- **Transition P3 → P4:** `wheel_override`, pointer_behavior ORBIT, statuses kept, no cleanse.

### P5: Root (40 → 0 %), 3 needles at 0 / 10 / 20, last phase (no floor)

| Layout | Overwrite 4 · Dose 4 · Overwrite 4 · Priority 4 · Forecast Strike 5 · Overwrite 4 · Null 5 = 30 |
|---|---|
| Hub | The Archive heal is gone. **Code Red:** every boss hit that reaches you (not SANDBOXed) applies CORRUPTED to one of your slots (N6 `ON_HIT_DEALT`). |
| Defense | none (no Directive) |

- Overwrite slices here are 13 pierce (the P5 variant).
- Because there is no Directive, every needle takes your full hit.
- **Transition P4 → P5:** `wheel_override` + MULTIPLY (0, 10, 20) + `hub_override`. Statuses are kept, so the corruption you carried becomes your RAM tax in the race.

## 3. Sustain and intake

**Sustain (one source):** Archive, 1 % of max HP per turn. That is 4.0 HP at 400, 4.4 at 440, 4.8 at 480 and 5.2 at 520.
- The cap is 30 % × 18 reference dpt = 5.4, so every band is under it ✔.
- P5 has none.
- Late Fee BLOCK exists only when the player pays RAM, so it is not a sustain source.

**Intake per turn** at the reference player (T4 values; per-needle expected = P(land) × tier factor × damage):

| Phase | Unsteered | Steered | Basis |
|---|---|---|---|
| P1 | ~5.4 | 5–8 band holds | Strike 9 ticks × 0.78 × 17.6 ≈ 4.1, plus Order ≈ 1.3; ~35 on a repeat |
| P2 | ~6 | 6–10 | Audit ≈ 2.9 per hit × ~1.5 hits ≈ 4.4, plus Order 1.3 |
| P3 | ~12 | 6–9 | ~6.2 per needle × 2 |
| P4 | ~10 | 4–7 | Strike 2.3, Audit ≈ 4.4, Order 3.5 |
| P5 | ~19 | 11–15 | ~6.3 per needle × 3 (Overwrite 4.0 + Strike 2.3) before enrage |

All are above 0. The unsteered P5 figure kills the operative in about 3 turns, so steering and SANDBOX are required there.

## 4. HP by tier (hp_bands)

T4 only. DISPATCH authors its own bands as a sum of phase budgets (R2), not the Genome Core's 300 to 400.

| ICE boss-strength zone ceiling | HP |
|---|---|
| ≤ 1.00 | 400 |
| ≤ 1.15 | 440 |
| ≤ 1.30 | 480 |
| > 1.30 | 520 |

**Budget at 400** (reference 18 dpt, 3.5 turns per phase). Net = 18 × (needles landing) − sustain (4.0 in P1–P4):

| Phase | Needles | Net per turn | Target turns | HP | Turns |
|---|---|---|---|---|---|
| P1 | 1 | 14 | 3.5 | 48 | 3.4 |
| P2 | 1 | 14 | 3.5 | 48 | 3.4 |
| P3 | 2 (×2) | 36 − 4 = 32 | 3.0 | 96 | 3.0 |
| P4 | 1 | 14 | 3.5 | 48 | 3.4 |
| P5 | 3 (×3) | 54 | 3.0 | 160 | 3.0 |
| **Total** | | | | **400** | **16.2** |

- The multi-needle phases target 3 turns, not 3.5, because the band cannot hold 3.5 at ×2 and ×3 (P3 alone would be 112).
- Cumulative phase ends: 3.4 / 6.9 / 9.9 / 13.3 / 16.2 turns.
- At 440 / 480 / 520 the phase HPs scale in the same proportions (heal also scales, still under the cap).
- **Quorum on** (see §6): secondary needles count half, so P3 is 96 / (27 − 4) ≈ 4.2 turns and P5 is 160 / 36 ≈ 4.4 turns. The total rises to about 18.4, still inside 12–20.

## 5. Enrage

**Default** (boss: start 10, every 5, +25 % additive).
- The turn-10 step lands on P4's first turn (P3 ends at about 9.9). P4 plays under ×1.25.
- The turn-15 step lands inside P5 (13.3 to 16.2), the phase with 3 needles, so the race is squeezed exactly where it should be.
- No authored enrage is needed: Forecast's repeat tax is already pressure against stalling.

## 6. Buffs and counter Exploits

A route draws 5 of the pool of 8 (R7). Legacy: Intel, Breach and Virus are mapped in. The other five are new.

| Buff (strong) | Effect | Counter Exploit turns off | Origin |
|---|---|---|---|
| **Forecast** (signature) | Enables the `repeat_multiplier` rider: Forecast Strike doubles on a repeated slot | No repeat tax | New |
| Archive | The 1 % per turn Archive heal (P1–P4) | No boss heal | New |
| Second Needle | The boss's extra needles resolve their slices | Extra needles resolve as Null for the boss's output (they still exist for your hits) | Legacy Breach |
| Chart Hidden | Phases and next layouts hidden | Reveals them | Legacy Intel |
| **Quorum** (signature) | Your hits landing at the secondary needles deal 50 % (a per-hit rule, so the pointer rule still gives one hit per needle) | Full damage | New |
| Compliance Lock | Resistance 2 | No resistance | New |
| Afflictions Pool | Citation +1 stack, Priority drain +1, Flare and Dose each hit one extra slot | Base effects | New |
| Cell Patch | Starts each phase with SHIELD 5 % max HP | No shield | Legacy Virus |

**Signatures:**
- **Forecast** is the hook P1 stands on. Without it P1 is a plain, easy phase.
- **Quorum** makes the uneven-needle geometry matter for your damage as well as your defense.

`min_exploits_for_breach = 3` stays.

## 7. Counterplay

- **P1:** do not resolve the same slot twice in a row. Use the free nudge to break a repeat. A weak player loads the same good slot every turn and eats about 35.
- **P2:** use the free nudge only, and Cleanse before the Audit Strike. Late Fee turns paid nudges into boss block. A weak player stacks OUTPUT_DOWN on their best slot and takes 3 hits of 22.
- **P3:** make one needle safe (Null, or a WEAK edge). Burst on the safe pair. Perfects cost you Echo damage, so weigh them. A weak player ignores the geometry and eats a 26 pierce.
- **P4:** do not clear the drones. Steer onto unguarded slices and plan two turns ahead (the orbit trail shows it). A weak player aims at guarded slices and wastes damage.
- **P5:** race. Keep CORRUPTED off your key slots, SANDBOX the Overwrite, and finish before the turn-15 step. A weak player stalls and loses to enrage.

## 8. Systems needed

| N# | Used for | Fallback |
|---|---|---|
| N1 | PERCENT block and heal | FLAT amounts |
| N2 | `hp_bands`, `enemy_damage_by_tier` | none (required) |
| N3 | Parking, status keep, `cleanse_on_enter` PLAYER | none (required) |
| N4 | Enrage | none (required) |
| N5 | Buffs and Exploits | Legacy 3 only |
| N6 | ON_RESOLVE record (a saved landing field), ON_RAM_SPENT, ON_PERFECT, ON_HIT_DEALT | Drop Late Fee and Echo; Forecast needs ON_RESOLVE |
| N8, N9 | OUTPUT_DOWN stacks, CORRUPTED as a RAM cost | Today's PARASITE halving and corruption damage |
| N11 | Needles at 11 and orbit offsets | 15 / 10 multiples |
| N12 | Slice sizes 3 to 6 | 5-tick slices (lose the narrow Overwrite and the no-Perfect slices) |
| N13 | Fixed satellites and REPLACE | Today's docking |
| N20 | `pierce`, `hits_per_target_status`, `repeat_multiplier` | Drop the multi-hit; flat Strike (loses P1's question) |

No NEW system is needed.

## 9. Delta vs today

- **Kept:** id, display name, corporation, the Root Access hub name, the Dose / Citation / Priority / Flare slices, the `echo_drone` satellite, and the phase lines (reused as transition text).
- **Changed:**
  - HP 460 → `hp_bands` 400 to 520.
  - 2 phases (0.66 / 0.33) with a constant repair 4 plus shield 4 hub (attrition) → 5 phases, Archive heal 1 %, and no shield except under Cell Patch.
  - The wheel is replaced phase by phase.
- **Removed:** the always-on shield and the repair 4.
- **`heat_effects`:** none today, none added.

## 10. Predicted sim check

There is no baseline row for this boss. The comparison is against the Boss baseline (fresh 38 turns, 25 % win; campaign T4 41–50 turns, 4–8 %).

- **Turns:** about 16 fresh at the reference player (about 18 with Quorum on), p90 ≈ 20, inside 12–20.
- **Bot's best play (16 to 35 dpt):**
  - at 16 dpt: about 18–19 turns;
  - at 35 dpt: about 8 turns.
  - Top play therefore sits below target. The enrage steps and the Forecast tax apply to the slower runs. For ICE above 1.30, `hp_bands` (520) restores length.
- **Win %:** 30–40 % fresh and 10–15 % in campaign, against 25 % and 4–8 % today.
  - The boss deals less intake than the Genome Core in P1–P2, but P5 is lethal if unsteered.
  - The sim must confirm both.

## 11. Open questions

Q: Are DISPATCH's own `hp_bands` (400 to 520, above the Genome Core's 300 to 400) acceptable, or should P3 and P5 shrink to fit 300–400?
Q: Is P5's unsteered intake (~19 per turn, about 3 turns to kill a 55 HP operative) too lethal for the reference player, or is steering plus SANDBOX enough?
Q: Does `cleanse_on_enter` = PLAYER at P2 → P3, which also clears CORRUPTED, feel right, or should statuses carry (NONE) so P2's debt matters in P3?
Q: Does Quorum (halves hits at secondary needles) lengthen P3 and P5 too much for the 3–4 turns per phase target when drawn?
Q: Does Echo at 25 % in P3 overlap with the Handler's Echo (50 %), or does the shared theme read as intended?
