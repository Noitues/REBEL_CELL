<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__mission_director; status ok; tokens in 8581 cache-write 0 cache-read 32585 out 20770; cost $0.116. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, P1 sizes and "no Perfect"):** kept the sizes, since P1 sums to 30, but fixed the labeling. Every layout table now has explicit tick ranges and a Perfect? column from the R11 default maps. P1 is Shim 5 / Defrag 4 / Overflow 5 / Flare 4 / Null 6 / Shim 6. The 4-tick Flare and the 6-tick Shim and Null have no Perfect, and the biggest slice (Null 6) is deliberately the safe harbor.
- **Issue 2 (BLOCKER, T3 HP and sustain):** rebuilt the HP table. P3 sustain is subtracted from the P3 budget once and never added back. T3 is now 158 (band 132–162); the full arithmetic is in §4.
- **Issue 3 (MAJOR, turns per phase):** each phase now has a per-tier turn count of 3.0–3.6. The P3 two-needle factor is stated as an explicit assumption, 1.5 effective needles rather than 2.0, and flagged in Q1. Gate hits are shrunk to 4 and called a bonus that is not budgeted.
- **Issue 4 (MAJOR, Countdown on phase change and enrage):** a phase change resets the Countdown to 0, cancels any pending Overflow and removes the gates. Enrage is authored at turn 11 (§5). The expected T3 fight is about 10.4 turns, so enrage touches only slow runs.
- **Issue 5 (MAJOR, random Flare):** every Flare is now `SlicePick.UNDER_POINTER`, the slice under your own pointer. It is deterministic and the preview shows it.
- **Issue 6 (MAJOR, Relay role, intake, "trap"):** the Relay is a pure bodyguard with no attack. It docks on the slice under the Director's needle at turn start; the oldest Relay is removed past the cap of 2. The intake math uses only the Director's own slices. The reason steering beats killing is now shown (§2 P2).
- **Issue 7 (MAJOR, `cleanse_on_enter` OWN):** set to NONE and dropped the Virus justification. Statuses the player puts on the Director's slices now persist through every transition (R6).
- **Issue 8 (MAJOR, Countdown hook):** the Countdown is an N15 gate effect (`on_cross` adds to a counter). Fallback: an N6 listener counting nudges to the Director's wheel, and without N15 or N6, resistance 2 plus a fixed extra Overflow slice (§8).
- **Issue 9 (NIT, counter jump):** the Countdown counts +1 per gate crossed, caps at 3 and the surplus is lost. A 2-gate spin from 2 triggers once.
- **Issue 10 (NIT, intake factor):** intake is given at T1 (×1.0) and T3 (×1.69).
- **Triage "P1 Shim no Perfect vs 6-tick Null":** covered by issue 1.
- **Triage "T3 HP 150 exceeds band":** the v1 150 was inside the band, but the sustain arithmetic was wrong. Fixed with issue 2. The critic's suggested HP of 147 was also internally muddled, so I recomputed from the budget.
- **Own correction (v1 resistance error):** v1 set resistance to 1 and claimed it left Flip usable. Under GDD 2.5 any resistance above 0 blocks Flip entirely and absorbs ±1 nudges. Resistance is now 0 in all phases; the gates, not resistance, are the constraint. This is not a designer-ruling conflict.
- **Critic Q "enrage later":** adopted, turn 11 authored.
- **Critic Q "gate hits and parking":** gate damage is parked like any other loss (R3).
- **Critic Q "Relay attack":** pure bodyguards, no attack.

---

# mission_director: direct design

## 1. Identity & the one question

**Class:** Mini-boss (3 phases), Orbital Commons. It guards the final Rack at T1–T3 and teaches rim gates and fixed-satellite replacement. It appears in the L5–6 pressure layers at T3 and as a teaching mini-boss at T1–T2. T4 values exist only for sim symmetry.

**Changes from the section 3 concept:**
- Pointer geometry carries the questions: a deterministic Relay launch under the needle in P2, and uneven needles in P3.
- Relays are pure bodyguards. The old Deploy phase launched attacking satellites and Flares together, which was unreadable.
- Countdown and gate crossings are counted on player actions only. The Director's own orbit never counts.

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Countdown | "How do you move its needle without tripping the gates?" Each gate carried past its needle by a nudge or spin adds +1 Countdown; at 3 it adds an Overflow. | Plan one route per turn. Flip and Snap don't traverse. Burst the plain Shim and Overflow windows. |
| P2 Deploy | "Which slice do you leave?" A Relay docks under its needle each turn, and your hit on a guarded needle hits the Relay. | Spend the free nudge to leave the guarded slice. Don't spend damage on guards. |
| P3 Abort Window | "Which of the two uneven needles do you feed, and can you afford a big spin?" Gates now pay you. | Find the rotation with one needle on Null and one on Defrag, and cross gates with a deliberate spin. |

## 2. Phase plan

**Thresholds:** 0.69 and 0.38 of max HP. Floors are ceil(max HP × next threshold), per R3. They are derived from the phase budgets in §4; the 3 phases are 31%/31%/38% of HP.

### P1 Countdown (100 → 69 %)

| Item | Value |
|---|---|
| Needles | 1, tick 0 (FIXED) |
| Resistance | 0 |
| Hub rule | none |
| Gates (N15) | 2 rim gates on the Director's wheel at ticks 7 and 22; they rotate with the wheel |
| Listener / counter | A nudge or spin of the Director's wheel that carries a gate past its needle: Countdown +1 per gate crossed. Respin, Flip, Snap and the start-of-turn respin never count. The counter caps at 3 and the surplus is lost. At 3, the next resolve adds one extra OVERFLOW hit (12 FLAT × tier damage factor) in the offensive pass at the needle's slice, then Countdown resets to 0. The preview shows the pending hit and the lit gates. |

**Layout (5+4+5+4+6+6 = 30):**

| Slice | Ticks | Range | Perfect? | Effect |
|---|---|---|---|---|
| Shim | 5 | 0–4 | yes | 8 damage, FLAT × tier factor |
| Defrag | 4 | 5–8 | no | BLOCK 6, FLAT × tier factor |
| Overflow | 5 | 9–13 | yes | 12 damage, FLAT |
| Flare | 4 | 14–17 | no | OVERCLOCKED on the slice under your pointer |
| Null | 6 | 18–23 | no | nothing (the safe harbor) |
| Shim | 6 | 24–29 | no | 8 damage (map W W G G W W) |

Gates at ticks 7 and 22 sit on the Defrag and the Null.

**Transition P1 → P2:**
- Damage parks at the floor (R3).
- `wheel_override` swaps the layout.
- Gates are removed.
- Countdown resets and any pending Overflow is cancelled.
- Statuses stay, remapped by centre tick (R6). `cleanse_on_enter` = NONE.

### P2 Deploy (69 → 38 %)

| Item | Value |
|---|---|
| Needles | 1, tick 0 |
| Resistance | 0 |
| Hub rule | **Launch Window:** at the start of each turn, after the respin, a fixed Relay docks on the slice under the Director's needle (N13, `on_occupied` = REPLACE). Max 2 Relays on the wheel; a third launch first removes the oldest. |
| Relay | 6 HP, fixed, no attack. Mini-wheel: Defrag 3 / Null (block for itself only). It can't be nudged, spun or respun. |
| Listeners | none |

**Layout (5+4+6+5+4+6 = 30):**

| Slice | Ticks | Range | Perfect? | Effect |
|---|---|---|---|---|
| Overflow | 5 | 0–4 | yes | 14 damage, FLAT × factor |
| Flare | 4 | 5–8 | no | OVERCLOCKED on the slice under your pointer |
| Shim | 6 | 9–14 | no | 8 damage |
| Defrag | 5 | 15–19 | yes | BLOCK 8, FLAT × factor |
| Null | 4 | 20–23 | no | nothing |
| Shim | 6 | 24–29 | no | 8 damage |

**How the guards work:**
- The Relay launches under the needle, so every turn the needle starts on a guarded slice. Your Pointer attack aimed there hits the Relay (GDD 2.7), not the Director.
- Leaving costs the free nudge; killing the Relay costs a whole hit (6 HP absorbed). The nudge is cheaper, and the slice you move to is one the Director really reads. That is the tension.
- A Relay replaced by a later launch is not killed (Q3). It is simply removed.
- OVERCLOCKED gives 1.5× once on that slice's next trigger, then CORRUPTED (2× RAM, R9). It is a gift if you can land it as a Perfect, then Cleanse it.

**Transition P2 → P3:**
- Parks at the floor.
- `wheel_override` and `pointer_ticks` = (0, 11).
- Relays are removed.
- Statuses stay and are remapped. Anything you planted on the Director's slices persists. `cleanse_on_enter` = NONE.

### P3 Abort Window (38 → 0 %)

| Item | Value |
|---|---|
| Needles | 2 at ticks 0 and 11 (uneven, R10) |
| Orbit | both needles orbit 3 ticks per turn, with a telegraphed trail. The Director's own orbit never counts toward gates. |
| Resistance | 0 |
| Gates (N15) | the same 2 gates at ticks 7 and 22 |
| Gate rule | **Abort Window:** each gate a player nudge or spin carries past a Director needle deals 4 damage to the Director, once per gate per turn (max 8 per turn). The damage is parked like any loss (R3). This inverts the P1 rule. |
| Hub rule | **Hotfix:** heal 2.5 % of max HP per turn, PERCENT (N1). It is breachable by Hub Breach cards. |

**Layout (4+5+4+5+6+6 = 30):**

| Slice | Ticks | Range | Perfect? | Effect |
|---|---|---|---|---|
| Overflow | 4 | 0–3 | no | 16 damage |
| Shim | 5 | 4–8 | yes | 8 damage |
| Flare | 4 | 9–12 | no | OVERCLOCKED on the slice under your pointer |
| Defrag | 5 | 13–17 | yes | BLOCK 8 |
| Shim | 6 | 18–23 | no | 8 damage |
| Null | 6 | 24–29 | no | nothing |

- With needles at (r, r+11), the zero-intake rotation is needle A on Defrag (13–17) with B on Null (24–28).
- A needle on Null puts the other on Shim (5–8) or Flare (9–10). A needle on Defrag with the other on Shim 18–23 costs 8 damage.
- This is a solvable puzzle that orbit shifts every turn.

## 3. Sustain and intake

**Sustain:** one source, the P3 Hotfix at 2.5 % max HP per turn.

| Tier | Max HP | Heal | 30 % of reference dpt | OK? |
|---|---|---|---|---|
| T1 | 102 | 2.55 | 0.3 × 9 = 2.7 | yes |
| T2 | 124 | 3.1 | 0.3 × 11 = 3.3 | yes |
| T3 | 158 | 3.95 | 0.3 × 14 = 4.2 | yes |

P1 and P2 have no healing. Block is not healing.

**Intake per turn** (raw, before steering; the reference player steers away from about 45 % of it):

| Phase | T1 (×1.0) | T3 (×1.69) | Derivation (T1 numbers) |
|---|---|---|---|
| P1 | ≈ 3.7 | ≈ 6.3 | (5×0.8×8 + 6×0.667×8 + 5×0.8×12) / 30 |
| P2 | ≈ 4.0 | ≈ 6.8 | (5×0.8×14 + 2×6×0.667×8) / 30 |
| P3 | ≈ 7.5 | ≈ 12.6 | 2 needles × (4×0.75×16 + 5×0.8×8 + 6×0.667×8) / 30 |

- Averages: 0.8 for a 5-tick slice, 0.667 for a 6-tick, and 0.75 for a 4-tick.
- Every phase is above 0 even for a perfect steerer in P1 and P2. P3 has a zero-intake rotation, but orbit moves the needles each turn.
- Countdown Overflows add ≈ 12 per trigger in P1.

## 4. HP by tier

**Method:** per phase, budget = `reference_dpt_by_tier` × 3.5 × needles landing − sustain × 3.5.
- P1 and P2: 1 needle.
- P3: 2 needles, with an effective factor of 1.5. The Director's own Defrag block and a needle on a block slice absorb about a quarter of the doubled hit (Q1).
- Gate damage is a bonus and is not budgeted.

| Tier | dpt | P1 | P2 | P3 | Sum | Band | Chosen |
|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 31.5 | 3.5×(13.5−2.55) = 38.3 | 101.3 | 95–105 | **102** |
| T2 | 11 | 38.5 | 38.5 | 3.5×(16.5−3.1) = 46.9 | 123.9 | 104–128 | **124** |
| T3 | 14 | 49 | 49 | 3.5×(21−3.95) = 59.7 | 157.7 | 132–162 | **158** |
| T4 (sim only) | 18 | 63 | 63 | 3.5×(27−5.1) = 76.7 | 202.7 | n/a | 203 |

**Floors** at thresholds 0.69 / 0.38:

| Tier | P1 removes | P2 removes | P3 holds |
|---|---|---|---|
| T1 (102) | 102 − 71 = 31 | 71 − 39 = 32 | 39 |
| T2 (124) | 124 − 86 = 38 | 86 − 48 = 38 | 48 |
| T3 (158) | 158 − 110 = 48 | 110 − 61 = 49 | 61 |

**Turns per phase** (hits at the reference dpt):

| Tier | P1 | P2 | P3 |
|---|---|---|---|
| T1 | 31/9 = 3.4 | 32/9 = 3.6 | 39/(13.5−2.55) = 3.6 |
| T2 | 38/11 = 3.5 | 38/11 = 3.5 | 48/(16.5−3.1) = 3.6 |
| T3 | 48/14 = 3.4 | 49/14 = 3.5 | 61/(21−3.95) = 3.6 |

All are in 3–4. Total is about 10.5 turns at the reference player, inside 6–12. A skill-1.0 player or one who uses the gates finishes around 6–8.

`hp_by_tier` = [102, 124, 158, 203]. Today's flat 150 is replaced.

## 5. Enrage

**Authored:** start turn 11, every 5 turns, +25 % damage (additive, R4).
- The default start (10) would fire in the middle of nearly every on-budget T3 fight (≈ 10.5 turns), so it would be a tax, not a stall-breaker.
- At 11, enrage touches only fights that run past budget (a stalled P1 with Countdown Overflows, for example).
- Enrage raises damage only, not Hotfix or block.

## 6. Buffs and counter Exploits

Not applicable (mini-boss).

## 7. Counterplay

**P1:**
- Read the gates and move the needle the short way, or land on Null with the free nudge.
- Use Flip and Snap, which don't traverse.
- Burst the Shim and Overflow windows.
- Overkill past the 69 % floor is lost, so don't over-burst.
- Deliberately take one Countdown +1 if the route needs it. Resetting at 3 costs you one 12-damage hit.

**P2:**
- Spend the free nudge to leave the guarded slice.
- Choose between Null or Defrag and an unguarded Perfect on a Shim or Overflow slice.
- Cleanse the Flare's CORRUPTED, or land the 1.5× slice as a Perfect first.
- Plant statuses on slices you expect to read. They survive into P3.

**P3:**
- Find the zero-intake rotation (A on Defrag 13–17, B on Null 24–28) and hold it against the orbit.
- Cross both gates with one spin for 8 damage when the route allows it. It is a bonus.
- SANDBOX the Overflow turn.
- Finish before turn 11.

**Weak player:**
- Nudges across gates in P1 for no reason, feeding the Countdown Overflow.
- Swings at a guarded needle and wastes the hit on a 6 HP Relay.
- Ignores the Flare and lets CORRUPTED double RAM costs.
- Parks both P3 needles on threats.

## 8. Systems needed

| N# | Used for | Fallback |
|---|---|---|
| N3 | Phase floors, status remap, parking | none; core |
| N1 | PERCENT Hotfix; FLAT × tier damage factor | Hotfix as flat 4 |
| N2 | `hp_by_tier` | per-tier `.tres` overrides |
| N4 | Authored enrage | none; use the default |
| N11 | Uneven needles (0 / 11) | use 0 / 15 (today's Multiply) |
| N12 | 4- and 6-tick slices | all 5-tick; loses the narrow Overflow windows |
| N13 | Fixed Relays, REPLACE | ordinary movable satellites; weaker |
| N15 | Rim gates, traversal detection, `on_cross` counter field | N6 fallback below; **no gate fallback** for the P3 gate payoff, so P3 degrades to a plain 2-needle fight |
| N6 | fallback only | Countdown as an ON_NUDGE listener counting nudges to the Director's wheel (3 nudges adds the Overflow) |
| N9 | CORRUPTED as a RAM cost | old CORRUPTED self-damage (worse) |
| N19 | turns per phase metrics | n/a |

Without N15 or N6: replace P1 with resistance 2 and a fixed extra Overflow slice.

## 9. Delta vs today

**Kept:** id, corporation, `is_mini_boss`, `cycle_reward` 60, the slice set (Shim, Defrag, Overflow, Flare, Null), and the "Abort window" and "Go for launch" phase lines.

**Changed:**
- Thresholds from 0.5 / 0.25 to 0.69 / 0.38.
- P1 now has its own phase with gates and the Countdown. Today's P1 is a plain 1-needle phase with resistance 2.
- Today's phase 0 Multiply to (0, 15) becomes the P3 uneven (0 / 11).
- Today's phase 1 Orbit 3 is kept, but only in P3.
- Resistance drops from 2 to 0 in every phase (resistance blocks Flip and Respin and absorbs nudges).
- HP from a flat 150 (384 at T3 today) to [102, 124, 158, 203].
- New: variable-size layouts, the Relay and Launch Window, rim gates and the Hotfix hub.

**`heat_effects`:** retire any. The phases and enrage carry the pressure.

## 10. Predicted sim check

No baseline row exists (the baseline covers Solace only), so these are estimates from the wheel arithmetic.

| Tier | Turns | Win % | Why |
|---|---|---|---|
| T1 | 9–11 | 93–96 | 102 HP, intake 4–7 raw, steering halves most of it |
| T2 | 9–11 | 91–94 | Flare tax and Relay steering cost nudges |
| T3 | 10–12 | 86–91 | P3 intake ≈ 12.6 raw; enrage at 11 touches the slow third of runs |
| T4 | 12–14 | ≈ 70 | sim only |

The main risk is P3. If the effective needle factor is below 1.5 the phase runs past 4 turns, and an unread gate rule in P1 pushes the fight past turn 11.

## 11. Open questions

Q: Is the P3 effective needle factor of 1.5 (not 2.0) acceptable for the R2 budget, or should the Director's Defrag block be removed in P3 so the full 2× applies?
Q: When your Pointer attack is absorbed by a Relay, is the excess damage lost (assumed) or does it carry through to the Director?
Q: Does a replaced or removed Relay count as destroyed for Daemons like Botnet Seed and for rewards? Assumed no.
Q: Is turn 11 the right authored enrage start for a 6–12 turn mini-boss, or should all mini-bosses stay on the class default (10)?
Q: Should a Flip that carries a gate across the needle ever count as a crossing? Assumed no, because Flip mirrors rather than rotates.
