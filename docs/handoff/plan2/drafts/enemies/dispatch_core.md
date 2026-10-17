<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__dispatch_core; status ok; tokens in 19550 cache-write 0 cache-read 32007 out 7336; cost $0.059. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# dispatch_core: direct design

## 1. Identity & the one question

**Class:** HQ boss (Central Server), T4 only. **Corporation:** REBEL_CELL (final corporation; unlocked by clearing the other corporations at ICE 10). **Layer:** pressure only (the end of the final netrun).

**Concept: DISPATCH is the handler that planned you.** The Genome Core is a disease, the Handler mini-boss mirrors your wheel, and DISPATCH *forecasts* you. It has already read your wheel and acts on it. The boss fight is a reading test: it models the player and punishes habits.

The mini-boss (The Handler) mirrors you reactively with Shadow, Override and Echo. DISPATCH is distinct because it acts on **what you did last turn** (a Forecast) instead of mirroring in real time. It also pulls the mirror theme to the Cell's own tools: REBEL_CELL's final boss uses afflictions from all four corporations, one per phase, each phase ending with a twist that the previous phase's answer is now wrong.

**Phase questions (each new, none is attrition):**

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Briefing | "Can you act without a pattern?" It forecasts the slice you landed last turn and punishes repeating it. | Land a different slice each turn; the repeat tax never fires |
| P2 Audit | "What do you spend?" Corp afflictions (Citation stacks, Priority RAM drain) tax RAM and output. Spend budget decisions. | Spend RAM into Perfects early, keep stacks low with Cleanse |
| P3 Surveillance | "Where do you look?" 2 uneven needles, one safe, one lethal; Flares overclock. Read the geometry. | Put the lethal needle on Null or a WEAK edge; burst on the safe needle |
| P4 Handoff | "Can you win with what you have left?" Satellites (echo drones) guard slices; replacements keep arriving. | Ignore guards you can't kill cheaply; steer around them |
| P5 Root | "Can you finish before it finishes you?" 3 needles, no defense, every hit corrupts. | Pure race; keep corruption off your key slices |

The phase budget is about 3.5 turns each. Intended total is about 17 turns (see §3, §10).

## 2. Phase plan

Needle positions are ticks. Slice sizes sum to 30. All "FLAT" amounts are authored at T1 base and multiplied by `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2] (R2). This boss is T4 only, so the T4 value is shown as ×2.2, with the base in parentheses. PERCENT amounts read the boss's max HP.

**Boss HP (T4, band, see §4):** 360 at ICE ≤1.15 base (hp_bands below). Phase thresholds are at 0.80 / 0.60 / 0.40 / 0.20 (5 phases).

I use equal phase shares: each phase ~20 % of max HP. This is a deliberate choice: with 5 phases and ~3.5 turns each, equal shares keep every phase at 3–4 turns for the reference player. Phase budget arithmetic is in §4.

### New slice definitions used (data under `content/slices/dc_*.tres`)

| Slice | Type | Effect |
|---|---|---|
| Forecast Strike | OVERFLOW | 8 damage (T4: 18). **×2 if the slice under my pointer matches the slice your pointer landed on last turn** (rider `repeat_multiplier`, read from last turn's recorded landing; deterministic, preview-visible) |
| Order | SHIM | 6 (T4: 13) damage |
| Directive | DEFRAG (BLOCK) | PERCENT 5 % max HP |
| Citation | INFECT | OUTPUT_DOWN ×1 on your slice under the pointer (the existing Halcyon slice, migrated by N9) |
| Priority | INFECT | Drain 3 RAM (existing Meridian slice) |
| Flare | INFECT | OVERCLOCK on a random non-NULL slice of yours (existing Orbital slice) |
| Dose | INFECT | CORRUPTED on a random non-NULL slice of yours (existing Solace slice; now a RAM-×2 tax, R9) |
| Hotfix | HOTFIX | PERCENT 1.5 % max HP |
| Null | NULL | none |
| Audit Strike | OVERFLOW | 10 (T4: 22) damage; `hits_per_target_status`: +1 hit per OUTPUT_DOWN stack on your landing slice, max 3 hits |
| Overwrite | OVERFLOW | 12 (T4: 26) damage, **pierce** |

### P1: Briefing (100 → 80 %), 1 needle

| Item | Value |
|---|---|
| Needle | 1, tick 0 (fixed) |
| Layout (ticks) | Forecast Strike 5 · Directive 5 · Order 4 · Null 6 · Forecast Strike 4 · Dose 6 |
| Hub rule | **Root Access (Archive):** PERCENT 1 % max HP heal per turn (this is the sustain; see §3) |
| Statuses | CORRUPTED via Dose |
| Listener | **Forecast:** ON_RESOLVE records your landing slice id; used next turn |

- The Forecast Strike appears twice, so it comes up often. It doubles if you repeat last turn's slice. Directive is BLOCK 5 % (18 HP at T4 base 360).
- Intake at the reference player: the Strike is 18 at T4, doubled to 36 on a repeat. Mean intake target 2–4 damage per turn if you avoid repeats, as with the Genome Core's P1.
- Layout geometry: the Strike windows (5 and 4 ticks) are not equal, so sub-tick landings matter (R11): the 4-tick one has no Perfect (W G G W) but its Good is the same output.

### P2: Audit (80 → 60 %), 1 needle

| Item | Value |
|---|---|
| Needle | 1, tick 0 |
| Layout | Citation 5 · Order 4 · Priority 5 · Directive 4 · Audit Strike 6 · Dose 3 · Null 3 |
| Hub rule | Archive heal continues at 1 % |
| Statuses | OUTPUT_DOWN stacks (up to ×3) and CORRUPTED |
| Listener | **Late Fee:** ON_RAM_SPENT (N6): when you spend RAM on a nudge, the boss gains BLOCK 1 % of max HP per RAM (cap 3 RAM per turn) |

- The Audit Strike rewards leaving stacks on your landing slice: 1 hit base, up to 3 hits (22 each at T4). Total up to 66 damage per turn if stacked to ×2 and landed.
- Late Fee punishes brute-force nudging. The answer is to save RAM for cards and Perfect hooks, and use the free nudge.
- Transition P1 → P2 (parks at 80 %): `wheel_override`; statuses survive and remap by centre tick (R6). Dose-corrupted slices stay and become a RAM tax into P2. `cleanse_on_enter` = NONE.

### P3: Surveillance (60 → 40 %), 2 needles

| Item | Value |
|---|---|
| Needles | 2 uneven: ticks 0 and 11 (R10) |
| Layout | Overwrite 3 · Flare 5 · Order 4 · Citation 5 · Null 3 · Forecast Strike 5 · Directive 5 |
| Hub rule | Archive 1 % heal. Mirror Eye: **the boss's second needle copies your pointer's slice type when yours landed Perfect** is retired (too much, see Q) |
| Listener | **Echo:** ON_PERFECT (N6): replay 25 % of your landed slice damage at you (a smaller Echo than The Handler's 50 %, to keep it distinct) |

- Two needles at 11 apart means exactly one is usually on a bad slice. Overwrite is a 3-tick slice (G P G, so a narrow window, Perfect is the only dangerous Perfect for me too). Intake without steering: Overwrite 26 pierce, Flare overclock.
- Geometry decides the phase. The player nudges so that one needle lands on Null (3 ticks, G P G, wide-ish) and the other on Directive.
- Transition P2 → P3: `wheel_override` + MULTIPLY (0, 11); `cleanse_on_enter` = PLAYER (cleans one stack tier: OUTPUT_DOWN ×1 each, so P2 stacks do not spill). I chose a partial reset because P2's stack game would otherwise make P3 unwinnable. If N8 is not available, use NONE.

### P4: Handoff (40 → 20 %), 2 needles

| Item | Value |
|---|---|
| Needles | 2, ticks 0 and 15 (even), **ORBIT 2 ticks per turn** (telegraphed trail) |
| Layout | Order 5 · Echo Drone dock slot 5 · Forecast Strike 5 · Directive 4 · Audit Strike 5 · Null 6 |
| Satellites | Echo Drone (existing `echo_drone.tres`): launches one per turn onto a slice; `on_occupied = REPLACE` (R12, N13); max 2 |
| Hub rule | Archive heal 1 % |
| Listener | Forecast continues |

- Drones are fixed bodyguards (R12). Orbit moves the needles so you have to plan two turns ahead, as the Meridian mini-boss does for orbit; here the question is guards.
- Transition P3 → P4 (parks at 40 %): `wheel_override`, pointer_behavior ORBIT; statuses survive.

### P5: Root (20 → 0 %), 3 needles, last phase (no floor)

| Item | Value |
|---|---|
| Needles | 3: ticks 0 / 10 / 20 |
| Layout | Overwrite 4 · Dose 4 · Overwrite 4 · Priority 4 · Forecast Strike 5 · Overwrite 4 · Null 5 |
| Hub rule | **Root Access (Final):** the heal is gone; **Code Red:** every enemy hit that reaches you (not SANDBOXed) applies CORRUPTED to one of your slices (same rule the Genome Core uses; rule N6 hook `ON_HIT_DEALT`) |
| Defense | none |

- Race phase. No Directive. Enrage steps (turn 15) land in this phase.
- Transition P4 → P5: `wheel_override` + MULTIPLY (0, 10, 20), `hub_override`.

## 3. Sustain and intake

**Sustain (one source):** the Archive heal 1 % of max HP per turn in P1–P4 = 3.6 HP/turn at 360 HP; none in P5. The Hotfix slice is dropped from the layouts to keep one source. Cap check: 30 % of reference damage per turn = 0.3 × 18 = 5.4. 3.6 < 5.4. ✔

**Intake per turn at the reference player (T4):**

| Phase | Target |
|---|---|
| P1 | 2–4 |
| P2 | 5–8 |
| P3 | 8–12 (with steering) |
| P4 | 10–14 |
| P5 | 14+ before enrage |

All above 0. (The Dosage Dispenser fault is avoided: even P1 has 2–4.)

## 4. HP by tier (hp_bands)

The boss is T4 only; HP is by ICE boss-strength zone ceiling (R2).

| ICE zone ≤ | HP |
|---|---|
| 1.00 | 300 |
| 1.15 | 330 |
| 1.30 | 360 |
| >1.30 | 400 |

**Budget arithmetic (reference 18 dpt, 3.5 turns/phase), base 300:**

Net per turn = 18 − sustain, where sustain is 1 % × 300 = 3 in P1–P4 and 0 in P5.

- P1–P4: 15 × 3.5 = 52.5 each.
- P5: 18 × 3.5 = 63; but two enemy needles in P3–P5 give the player extra hits through the pointer rule, and the player's wheel matters, so P3–P5 get a bonus. I use thresholds that give each phase ~20 % (60 HP at 300).

Check at 300: 60 HP per phase vs a budget of 52.5 (P1–P4) and 63 (P5). The slightly high P1–P4 figure (+7) costs about half a turn each, giving ~4 turns per phase, the top of the 3–4 band. To pull it back, thresholds are **0.82 / 0.64 / 0.44 / 0.22**:

| Phase | Share | HP at 300 | Budget | Turns |
|---|---|---|---|---|
| P1 | 18 % | 54 | 52.5 | 3.6 |
| P2 | 18 % | 54 | 52.5 | 3.6 |
| P3 | 20 % | 60 | 52.5 + 2-needle bonus ≈ 70 | 3 |
| P4 | 22 % | 66 | 52.5 + bonus ≈ 70 | 3.3 |
| P5 | 22 % | 66 | 63 | 3.7 |

Total ≈ 17.2 turns. Inside 12–20. ✔ (Thresholds 0.82 / 0.64 / 0.44 / 0.22 replace the 0.80 grid above.)

## 5. Enrage

**Default** (boss: start turn 10, every 5, +25 % damage, additive per Q2): the expected path puts the P4 → P5 transition at about turn 13–14, so the first step (turn 10) lands in P3–P4 and the second (turn 15) lands in P5. That is the right shape: the race phase gets squeezed. No authored override. A distinct authored trigger is **not** needed here since the Forecast Strike repeat tax already creates a "don't stall" pressure.

## 6. Buffs and counter Exploits

A route draws 5 of the corporation's Exploit pool (R7). REBEL_CELL's pool is 8 (the legacy Intel, Breach, Virus mapped in, plus five new).

| Buff (strong) | Effect | Counter Exploit turns off | Notes |
|---|---|---|---|
| **Forecast** (signature) | Forecast Strike doubles on a repeated landing; with the buff on, a repeat on *any* boss slice type doubles that slice too | Off: only Forecast Strike doubles... no: off = no repeat tax at all | Defines the phase-1 question |
| Archive | The 1 % per-turn heal | No boss heal | The Core's "Metabolism" analogue |
| Second Needle | The extra needle from P3 on | One fewer needle (today's Breach) | Legacy Breach |
| Chart Hidden | Phases and layouts hidden | Reveals them (today's Intel) | Legacy Intel |
| Quorum (signature) | Takes only 50 % damage on a slice read at the boss's **first** needle while another needle exists | Full damage | Makes needles matter for *you* |
| Compliance Lock | Resistance 2 | No resistance | |
| Afflictions Pool | Citation, Priority, Flare and Dose each add one extra effect (stack +1, drain +1, etc.) | Base effects | Corp-mix flavor |
| Cell Patch | Boss starts each phase with SHIELD 5 % max HP | None | Legacy Virus (replaced) |

**Signature buffs:** Forecast (the hook the whole boss stands on) and Quorum (nudges the player to consider which needle is "primary", a puzzle with uneven needles).

`min_exploits_for_breach = 3` stays.

## 7. Counterplay

- **P1:** don't land the same slice twice in a row. Rotate; use the free nudge to break a repeat. Heavy hitters waiting on the same slice every turn is the greedy line, and it costs 36 per turn.
- **P2:** don't burn RAM on extra nudges (Late Fee). Keep stacks on a slice you don't need; Cleanse before the Audit Strike. Weak players stack OUTPUT_DOWN on their best slice and take 3 hits.
- **P3:** make one needle safe. The second needle is the dangerous one at the 11-tick offset: nudge so Overwrite sits where the pointer lands WEAK, or on Null. Weak players ignore the geometry and eat a pierce hit.
- **P4:** don't kill every drone; steer around them (replacement is free). Plan two turns ahead because of orbit.
- **P5:** race. Keep CORRUPTED off the slices you rely on, and SANDBOX the Overwrite. A weak player stalls, hits the turn-15 step and loses.

## 8. Systems needed

| N# | Used for | Fallback |
|---|---|---|
| N1 | PERCENT block and heal | FLAT amounts at 18 HP (loses scaling) |
| N2 | hp_bands, damage table | none (required) |
| N3 | Phase parking, status keep, `cleanse_on_enter` | none (required) |
| N4 | Enrage | none (required) |
| N5 | Buffs and Exploits | Legacy 3 Exploits only; fewer counters |
| N6 | Listeners (ON_RESOLVE record, ON_RAM_SPENT, ON_PERFECT, ON_HIT_DEALT) | Drop Late Fee and Echo; Forecast needs ON_RESOLVE or a per-turn recorded landing **NEW: last-landing record** (a CombatantState field, saved) |
| N8, N9 | OUTPUT_DOWN stacks; CORRUPTED as RAM ×2 | Use today's PARASITE halving and corruption damage |
| N11 | Needles at 11 and 0 | Use 15 / 10-multiples |
| N12 | Variable slice sizes (3–6) | 5-tick slices: loses the narrow windows (Overwrite 3 ticks) |
| N13 | Fixed satellites and REPLACE | Today's docking |
| N20 | `pierce`, `hits_per_target_status` riders | Drop Audit multi-hit |
| NEW: repeat_multiplier | `repeat_multiplier` slice rider reading the last-landing record | Replace Forecast with a flat Strike (loses P1's question) |

**The Forecast hook is the one new thing that has no N# fit.** It is a small variant of N6 plus a stored landing id; data-only is not possible.

## 9. Delta vs today

- **Kept:** id, display name, corporation, Root Access hub name, the Dose, Citation, Priority and Solar Flare slices, the echo_drone satellite, and the phase lines (reused as transition text).
- **Changed:** HP 460 → hp_bands 300–400. Today it has 2 phases (0.66 / 0.33) with a constant repair-and-shield hub (4 + 4 per turn) that makes the fight attrition; now 5 phases, Archive heal 1 %, no shield.
- **Removed:** the always-on shield 4 (the Hub's second effect) and the repair 4. Shield returns only under the Cell Patch buff.
- **`heat_effects`:** none on the file today; none added.
- Today's wheel (Shim 14, Dose, Defrag 12, Overflow 24, Priority, Null) is replaced phase by phase.

## 10. Predicted sim check

No baseline row exists; this is an estimate from the wheel arithmetic.

- **Turns:** ~17 fresh at the reference player (12–20 target); p90 ≈ 20. A skilled bot (16–35 dpt) would finish in ~11–13, so the low end of the target requires the enrage steps and the Forecast tax to bite for strong players.
- **Win %:** unknown for T4 campaigns where baseline T4 bosses win 4–8 % (campaign) and 25 % (fresh); I expect 25–35 % fresh and 10–15 % campaign, since the intake of 2–14 per turn is lower than the Genome Core's. The sim must confirm.
- **Why:** it is a boss, so pass criteria differ from normals; the 12–20 turn target holds if phases take 3–4 turns.

## 11. Open questions

Q: Is the Forecast landing record (this turn vs the previous turn) acceptable as new state, or should DISPATCH read the *current* staged landing at preview time (a pure function of the board, no history)?

Q: P3's partial `cleanse_on_enter` (PLAYER) hides a status-stack puzzle from the phase before; is a total NONE (stacks carry into Surveillance) better?

Q: Does Quorum (50 % damage on the first needle) conflict with the pointer rule (GDD 2.7), where a hit lands on each pointer?

Q: Are the five phases right, or should P4 (drones) be dropped in favour of 4 phases at ~4 turns each?

Q: Does the Echo (25 % replay on your Perfect) overlap too much with The Handler's Echo listener (50 %)?
