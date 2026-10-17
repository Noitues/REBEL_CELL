<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__claims_adjuster; status ok; tokens in 9078 cache-write 0 cache-read 32585 out 19591; cost $0.110. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **1 (BLOCKER, HP arithmetic):** Rebuilt §4 so the HP *is* the phase-budget sum rather than a hand-picked number above it. With sustain recomputed (issue 2), `hp_by_tier` = [58, 71, 91, 116]. All four values sit inside the elite band. The "parking waste" justification is deleted, because parked damage is lost and needs no extra HP. The threshold floor is stated on the real HP (29 / 36 / 46 / 58). The P1/P2 net budgets differ by at most about 1.4 HP, so 0.50 stays the split.
- **2 (BLOCKER, sustain):** Recomputed against the final HP, with Defrag cut to 4 % in P1 and 3 % in P2 as the critic proposed. The read frequency now comes from the actual tick layouts (1/3 of turns in both phases). The sustain is deducted by the same formula the HP is built from, so the two cannot disagree. Every figure is at most 9 % of the reference damage per turn, well under the 30 % cap.
- **3 (MAJOR, pairing):** Dropped the "i and i+3" claim. P1 is re-laid with sizes 5, 5, 3, 7, 5, 5 and the needle pairs are enumerated tick by tick for all 30 rotations. Overflow is always paired with Null, and the pairing now holds.
- **4 (MAJOR, transition):** Stated one behavior: needle 2 uses MIGRATE, 15 → 11. Added the PARKED preview and the rule that the floor ignores needle count. Later player hits in the same resolve are lost. The new layout and needle are visible before the next player turn.
- **5 (MAJOR, Dose / TIER_DOWN):**
  - Stated the R9 rule explicitly: acting at a CORRUPTED slice costs 2× RAM.
  - The Denial fallback is now today's PARASITE status, which halves output, instead of a plain Shim. The question survives, and it is data-only.
  - Q1 is answered: TIER_DOWN stays, and OUTPUT_DOWN is the softer swap.
- **6 (MAJOR, amount modes):** Clarified that FLAT damage is multiplied by the tier factor and PERCENT block is never rescaled (R2). Removed the Audit FLAT block. The only block left is PERCENT Defrag.
- **7 (MAJOR, Fine Print):** Deleted the "costs you nothing extra" filler. The Perfect bonus is now a slice rider (`perfect_multiplier` ×1.5, N20) on P2's Overflow, not a hub or listener. This answers the critic's Q2: the Perfect-denial question needs no N6. Hub: none.
- **8 (MAJOR, systems):**
  - N11 fallback corrected: today's code still enforces multiples of 5, so 0 / 10 works as a fallback until N11 lands.
  - The N12 fallback is stated honestly. The 1-tick denial still works on 5-tick slices, but the narrow Perfect window and the 7th slot are lost.
  - N20 is added to the systems list.
- **9 (NIT):** Removed the unsourced "15 HP, turn 1" claim. Enrage timing is corrected to turn 8 and turn 13.
- **10 (NIT):** §10 now separates the reference player from the bot's best play. At the reference player's 9 damage per turn, a 58 HP fight lasts about 6.5 turns, not 4.5.
- **Audit listener: dropped, which departs from the critic's "keep" note.** It gave the enemy a second BLOCK source, which breaks "at most one sustain source". Dropping it also removes the N6 dependency entirely.
- **Critic Q1 (P1 even or uneven):** kept even (0 / 15) so the pairs are learnable, and P2 is uneven. The worst opening turn is a single Shim + Shim pair of 16 raw, with no chained spike.

---

# claims_adjuster: direct design

## 1. Identity & the one question

**Class:** Elite, Solace, 2 phases, one threshold at 0.50 of max HP. It appears in L3-6 (about one elite per layer) and as a Rack elite. It is pressure content, not teaching.

**Concept:** an adjuster auditing a claim with two needles. P1 is the assessment. P2 is the denial.

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Assessment | Its two needles always read opposite ticks (0 / 15). Which pair is up this turn, and can you steer the pair away from Shim + Shim, or toward Defrag + Dose, where nothing hits you? | Spend the free nudge on the **enemy** wheel to move the pair, then burst on the turn the Defrag is not up. |
| P2 Denial | The needles are now uneven (0 / 11) and its Overflow hits ×1.5 on a Perfect. Can you knock that Perfect down to Good with a 1-tick nudge? | Deny the Perfect, avoid the Denial slice, and burst while a needle is on Null or the Defrag pair. |

## 2. Phase plan

Flat enemy amounts are authored at T1 and multiplied by `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2] (R2). PERCENT amounts are never rescaled.

### P1 "Assessment" (100 → 50 % HP)

| Field | Value |
|---|---|
| Needles | 2 at ticks 0 and 15 (even, as today) |
| Hub | none |
| Statuses | Dose: CORRUPTED on 1 random non-NULL player slice (R9: acting there costs 2× RAM) |
| Listeners | none |

**Layout** (slice start ticks are wheel-relative; the wheel starts at the needle's tick 0):

| Slice | Ticks | Range | Effect |
|---|---|---|---|
| Shim A | 5 | 0-4 | FLAT 8 damage |
| Defrag | 5 | 5-9 | BLOCK, PERCENT 4 % max HP |
| Overflow | 3 | 10-12 | FLAT 14 damage (G P G) |
| Shim B | 7 | 13-19 | FLAT 8 damage (W W G P G W W) |
| Dose | 5 | 20-24 | 0 damage, CORRUPTED on 1 slice |
| Null | 5 | 25-29 | none |

Ticks: 5 + 5 + 3 + 7 + 5 + 5 = 30.

**Pairs.** With the first needle at tick r, the second sits at r+15. Over the 30 rotations, r and r+15 give the same pair, so 15 distinct cases are each counted twice:

| First needle ticks | Second needle ticks | Pair | Cases of 15 | Raw damage at T1 |
|---|---|---|---|---|
| 0-4 | 15-19 | Shim A + Shim B | 5 | 16 |
| 5-9 | 20-24 | Defrag + Dose | 5 | 0 (block 4 %) |
| 10-12 | 25-27 | **Overflow + Null** | 3 | 14 |
| 13-14 | 28-29 | Shim B + Null | 2 | 8 |

- Mean raw damage per turn is (5×16 + 3×14 + 2×8) / 15 = 9.2 at T1.
- Overflow is always paired with Null, so only one big hit can land per turn.
- Dose is read on 1/3 of turns. Defrag is read on 1/3 of turns, always together with Dose.

### Transition (at 50 %)

- **Parking (R3):** the floor is ceil(0.5 × max HP) = 29 / 36 / 46 / 58. Excess damage on the crossing hit is lost, and so are later player hits in the same resolve (a Breaker double-hit overkills for nothing). The floor does not depend on needle count. The preview shows "PARKED −N".
- **Wheel:** `wheel_override` swaps in the P2 layout.
- **Needles:** needle 2 uses MIGRATE, 15 → 11. The new layout and needle positions are on screen for the whole next player phase (the start-of-turn respin only rotates them).
- **Statuses (R6):** they stay on both wheels, remapped by centre tick. `cleanse_on_enter = NONE`: your CORRUPTED slices carry into the denial and keep taxing your RAM.
- **Phase line:** "Claim reviewed. Denied."

### P2 "Denial" (50 → 0 %)

| Field | Value |
|---|---|
| Needles | 2 at ticks 0 and 11 (uneven, R10) |
| Hub | none |
| Statuses | Dose: CORRUPTED on 1 slice. Denial: TIER_DOWN ×1 on your slice under the pointer (R8: Perfect → Good → WEAK). |
| Listeners | none |

**Layout (7 slots, N12):**

| Slice | Ticks | Range | Effect |
|---|---|---|---|
| Overflow A | 3 | 0-2 | FLAT 18 damage, `perfect_multiplier` 1.5 (Perfect at tick 1 = 27) |
| Shim | 4 | 3-6 | FLAT 8 damage (W G G W, no Perfect) |
| Denial | 5 | 7-11 | FLAT 6 damage + TIER_DOWN ×1 |
| Null | 5 | 12-16 | none |
| Dose | 5 | 17-21 | CORRUPTED on 1 slice |
| Overflow B | 3 | 22-24 | FLAT 18 damage, `perfect_multiplier` 1.5 (Perfect at tick 23) |
| Defrag | 5 | 25-29 | BLOCK, PERCENT 3 % max HP |

Ticks: 3 + 4 + 5 + 5 + 5 + 3 + 5 = 30.

**Pairs.** The second needle is at r+11. Both Overflows are never read in the same turn: A needs the pair (r, r+11) = (A, B), but r in 0-2 gives r+11 in 11-13, and B needs r in 22-24 or r+11 in 22-24, which gives the other needle at 3-5 or 11-13. Checked over all 30 rotations:

- Raw damage totals 340 across the 30 rotations, a mean of 11.3 per turn at T1.
- The worst pairs are Overflow B + Shim (26 raw, rotations 22-24) and Overflow A + Denial (24).
- A Perfect on either Overflow happens on 4 of 30 rotations (needle on tick 1 or 23). That adds about 9 × 4/30 = 1.2, for a mean of 12.5 per turn at T1.
- Defrag is read on 10/30 rotations. Dose is read on 9-10/30.

**Why the Perfect matters.** The 3-tick Overflow reads G P G, so a Perfect needs the exact centre tick, and a 1-tick nudge on the enemy wheel turns ×1.5 into ×1.0 and saves 9 per tier-factor. Perfect is the dangerous tier for the enemy, so Good is the safe landing. The Denial slice then taxes the player's own Perfects, which is the tension.

## 3. Sustain and intake

**Sustain:** exactly one source, the PERCENT Defrag BLOCK. Block resolves before offense in the same resolve (GDD 2.2), so it absorbs that turn's player hit. There is no heal and no second block source.

Expected sustain per turn is the Defrag share × the read rate (1/3 in both phases), using the final HP:

| Tier | HP | P1: 4 % per read | P1 per turn | P2: 3 % per read | P2 per turn | Cap (30 % of dpt) |
|---|---|---|---|---|---|---|
| T1 | 58 | 2.3 | 0.77 | 1.7 | 0.58 | 2.7 |
| T2 | 71 | 2.8 | 0.95 | 2.1 | 0.71 | 3.3 |
| T3 | 91 | 3.6 | 1.21 | 2.7 | 0.91 | 4.2 |
| T4 | 116 | 4.6 | 1.55 | 3.5 | 1.16 | 5.4 |

The worst case is 1.55 against 5.4 at T4, about 29 % of the cap and 9 % of reference dpt.

**Intake per turn at the reference player** (assumption: the reference player's free nudge and one defense card remove about 70 % of the raw expected damage; placeholder pending the sim):

| Tier | P1 raw (9.2 × factor) | P1 intake (×0.30) | P2 raw (12.5 × factor) | P2 intake (×0.30) |
|---|---|---|---|---|
| T1 | 9.2 | 2.8 | 12.5 | 3.8 |
| T2 | 12.0 | 3.6 | 16.3 | 4.9 |
| T3 | 15.5 | 4.7 | 21.1 | 6.3 |
| T4 | 20.2 | 6.1 | 27.5 | 8.3 |

Intake is above 0 in every phase and tier. That fixes the baseline's roughly 2 damage taken per turn at T3.

## 4. HP by tier

Phase budget (R2): `reference_dpt_by_tier` × 3.5 turns, minus sustain per turn × 3.5. The player has one pointer on the enemy, so the needles factor is 1. Sustain is a fraction of max HP H (P1 1.33 % per turn, P2 1.00 % per turn), so:

- P1 net = 3.5·dpt − 0.0467·H
- P2 net = 3.5·dpt − 0.0350·H
- H = sum, which gives H ≈ 6.47 × dpt.

| Tier | dpt | Gross per phase | P1 net | P2 net | Sum | `hp_by_tier` | Elite band | Floor (0.50) | P1 HP / P2 HP |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 28.8 | 29.5 | 58.3 | **58** | 56-72 | 29 | 29 / 29 |
| T2 | 11 | 38.5 | 35.2 | 36.0 | 71.2 | **71** | 68-88 | 36 | 35 / 36 |
| T3 | 14 | 49.0 | 44.8 | 45.8 | 90.6 | **91** | 88-112 | 46 | 45 / 46 |
| T4 | 18 | 63.0 | 57.6 | 58.9 | 116.5 | **116** | 112-144 | 58 | 58 / 58 |

- The P1 and P2 nets differ by at most 1.4 HP, so a 0.50 threshold is the right split.
- Today at T3 the HP is 112, so this is a cut of about 19 % there.

## 5. Enrage

**Default: start turn 8, every 5 turns, +25 % damage, additive.** The fight targets 6-8 turns, so the first step lands on its edge (turn 8) and the second on turn 13 (×1.25, then ×1.5). It raises damage only. No authored trigger is needed: the 0.50 floor already stops stalling at the threshold, and the fight is short.

## 6. Buffs and counter Exploits

Not a boss. Not applicable.

## 7. Counterplay

**P1**
- A good player reads the pair: Shim + Shim is up on 1/3 of turns, Defrag + Dose on 1/3 and Overflow + Null on 1/5. They use the free nudge or a spin card on the enemy wheel to move away from Shim + Shim and burst when Defrag is not paired in.
- They spend a card on Cleanse or Encrypt if Dose has landed, because P2 compounds the RAM tax.
- They arrive at the floor with one large hit instead of overkilling, since excess damage is lost.
- A weak player ignores the pairs and takes 16 raw on a bad turn. They then pay doubled RAM on a corrupted slice and overkill the phase.

**P2**
- The player deals with the Overflow Perfect by nudging the enemy wheel one tick. That turns ×1.5 into ×1.0 and saves 9 × tier factor per nudge.
- The 0 / 11 needles mean fixing one often exposes the other, so the player chooses which one stays dangerous.
- They avoid landing their own pointer where a needle is on Denial, or they accept a Good over a Perfect.
- They burst while a needle is on Null, and finish before the second enrage step on turn 13.
- A weak player nudges their own wheel to chase a Perfect, lands on Denial, gets TIER_DOWN and then eats the enemy Perfect.

## 8. Systems needed

| # | Use | Data-only fallback |
|---|---|---|
| N1 | PERCENT block; FLAT damage × tier factor | Flat block amounts. Skip PERCENT. |
| N2 | `hp_by_tier` | Set per-tier `hp` by hand. |
| N3 | Threshold, parking, status keep | None. Without parking the threshold has no effect. |
| N4 | Enrage default | Skip for a first sim. |
| N8 / N9 | TIER_DOWN, CORRUPTED = RAM ×2 | Denial applies today's PARASITE status (halves output). Dose keeps today's CORRUPTED behavior. |
| N11 | Needle at tick 11 (R10) | 0 / 10 works today (multiples of 5). The pair table must be recomputed. |
| N12 | Variable slice sizes, 7 slots | All 5-tick, 6 slots. Overflow reads W G P G W, so the 1-tick denial still works but the narrow Perfect window and the 7th slot are lost. |
| N20 | `perfect_multiplier` rider | Drop it. P2 loses its Perfect-denial hook and keeps the uneven needles and Denial. |

## 9. Delta vs today

| Item | Today | New |
|---|---|---|
| HP | 112 flat | [58, 71, 91, 116] |
| Phases | 1 | 2, threshold 0.50 |
| Needles | 2 at 0 / 15 | P1 at 0 / 15, P2 at 0 / 11 (MIGRATE) |
| Slices | 6 uniform 5-tick | 6 slots in P1, 7 in P2, variable sizes |
| Overflow | 16 | 14 in P1, 18 in P2 with Perfect ×1.5 |
| Defrag | 8 flat | PERCENT: 4 % in P1, 3 % in P2 |
| Dose | CORRUPTED with self-damage | CORRUPTED = 2× RAM |
| New | none | Denial (TIER_DOWN), enrage |

**Kept:** the Shim / Overflow / Defrag / Dose / Null slice set, two needles, `cycle_reward = 35` and `is_elite`.

**heat_effects: retire.** Pressure now comes from phases, intake and enrage. The campaign Heat modifiers that already apply (elite frequency at 25, +1 resistance at 50) stay. An extra elite-level Heat hook would stack with enrage and stretch the fight past 8 turns.

## 10. Predicted sim check

At the reference player (step-0 skill), the fight is about 7 turns by construction (H ≈ 6.47 × dpt), plus a little for parked overkill. Against the bot's best play (baseline column), phases still force at least 2 turns.

| Tier | Turns at reference | Turns at bot's best | Win % | Why | Baseline row |
|---|---|---|---|---|---|
| T1 | 6.5-7.5 | 2.5-3.5 | ~97 | Low HP, gentle P1 pairs | 3.1 turns, 100 % |
| T2 | 6.5-7.5 | 3-4 | ~96 | Same shape, HP 71 | 5.2 turns, 100 % |
| T3 | 6.5-7.5 | 4-5 | ~92 | HP 91 vs 112, but intake is real (about 38 HP per fight) | 8.8 turns, 100 % |
| T4 | 6.5-8 | 5-6 | ~85 | HP 116 vs 112, intake 6-8 per turn, enrage near turn 8 | 14.9 turns, 85 % |

- Turns fall sharply at T3 and T4 and rise at T1, where phases force at least 3 turns each at reference damage.
- Threat per turn is above 0 at every tier. Heat turns per phase are 0, because there is no heal.

## 11. Q:

Q: At T3 the reference player takes about 38 HP per fight at the 30 % intake placeholder. Is that too lethal for an elite that carries HP into the next fight (compare Care Swarm's 43 HP at T3)?
Q: Is TIER_DOWN ×1 too punishing in a phase that also doubles RAM on corrupted slices, or should Denial use OUTPUT_DOWN ×1 (−25 %)?
Q: Should the 0 / 11 needle be telegraphed before the threshold (a ghost needle once the preview shows the floor reachable), or is showing it on phase entry enough?
Q: Is 0.50 right, or should the threshold sit slightly lower so P2 (the harder phase, 12.5 raw versus 9.2) has more HP?
Q: If N20 slips, is P2 still a good question with only the uneven needles and Denial?
