<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__claims_adjuster; status ok; tokens in 18675 cache-write 0 cache-read 32007 out 5669; cost $0.050. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# claims_adjuster: direct design

## 1. Identity & the one question

**Class:** Elite, 2 phases, one threshold at 0.50 of max HP. Solace. It appears in L3-6 (about one elite per layer) and as a Rack elite. It is pressure content, not teaching.

**Concept:** an insurance adjuster who audits a claim. It has two needles reading two claims at once. **Phase 1 is an assessment** and **phase 2 is a denial**.

| Phase | Question | The answer that shortens the fight |
|---|---|---|
| P1 Assessment | "Two needles read your wheel and mine at once. Which of its two needles is the dangerous one, and can you make both read Null or Defrag?" | Spin or nudge the enemy wheel so both needles land off the Overflow. Hit while it is blocking little. |
| P2 Denial | "Its needles are now uneven and it gets a Perfect bonus. Can you deny its Perfect with a 1-tick nudge, or do you eat a double-damage claim?" | Spend the free nudge to knock the Perfect Overflow to Good. Burst while its needle is on the Null. |

The playtests show testers dying to this enemy on turn 1 at 15 HP, and one-shot at 30 → 14 → dead. The cause is two evenly spaced needles reading 10, 16 and 10 with no warning. Today's version never teaches a read. The redesign makes the threat readable and answerable. The first turn of P1 is gentle, and the Overflow window is deliberately narrow.

## 2. Phase plan

Flat enemy amounts below are authored at T1 and multiplied by the tier damage factor (R2, N1).

### P1 "Assessment" (100 → 50 % HP)

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 15 (even, as today). The player can read it and the answers are symmetric. |
| Hub | none |
| Statuses | Dose applies CORRUPTED (RAM x2, R9) to 1 random non-NULL slice |
| Listeners | none |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Shim 8 | 5 | FLAT 8 damage |
| Defrag | 6 | BLOCK, PERCENT 6 % max HP |
| Overflow 14 | 3 | FLAT 14 damage. 3 ticks (G P G), so Perfect is only the center tick. |
| Shim 8 | 5 | FLAT 8 damage |
| Dose | 5 | 0 damage, CORRUPTED on 1 slice |
| Null | 6 | none |

The ticks sum to 5+6+3+5+5+6 = 30.

**Why this layout:** an evenly spaced pair of needles over 6 slices reads slices *i* and *i*+3. Order is Shim, Defrag, Overflow, Shim, Dose, Null (indices 0-5), so the pairings are:

- Shim + Shim
- Defrag + Dose
- Overflow + Null

So the Overflow always arrives with a Null, and the worst claim is Overflow + Null (14 on one needle only). The pair Shim + Shim (16 total) is the largest sum and is visible. This is the P1 question: the player learns the pairs.

**Intake:** the pairs average about (16 + 0 + 14) / 3 ≈ 10 damage per turn with no player defense. At the reference player's usual block and nudge, the target is 2-4 per turn (see §3).

### Transition (at 50 %)

- Damage parks (R3). The floor is ceil(max HP × 0.5).
- `wheel_override` swaps in the P2 layout.
- Pointers use MULTIPLY / MIGRATE style: needle 2 moves from tick 15 to tick 11 (uneven, R10).
- Statuses stay on the player's slices (R6) and on the enemy's, remapped by centre tick.
- `cleanse_on_enter = NONE`. Your CORRUPTED slices stay, which is the point: they feed P2's RAM tax.
- Phase line plays: "Claim reviewed. Denied."

### P2 "Denial" (50 → 0 %)

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 11 (uneven). The gap is 11 ticks, so the pair is never symmetric and "only one can be Perfect" (R10). |
| Hub | **Fine Print:** each of your Perfects costs you nothing extra, but when the enemy needle lands PERFECT on a damage slice, that hit repeats once at 50 % (an ON_HIT_DEALT listener, N6). It rewards denying its Perfect. |
| Statuses | Dose applies CORRUPTED to 1 slice. Denial applies TIER_DOWN (R8) to your slice. |
| Listeners | One N6 listener (below). |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Overflow 18 | 3 | FLAT 18 damage |
| Shim 8 | 4 | FLAT 8 damage. No Perfect (W G G W). |
| Denial | 5 | 6 damage + TIER_DOWN x1 on your slice under the pointer |
| Null | 5 | none |
| Dose | 5 | CORRUPTED on 1 slice |
| Overflow 18 | 3 | FLAT 18 damage |
| Defrag | 5 | BLOCK, PERCENT 4 % max HP |

The ticks sum to 3+4+5+5+5+3+5 = 30. There are 7 slots (the 6-slot cap is lifted by N12).

**Why:**

- The Overflow slices are 3-tick (G P G), so a Perfect needs the exact centre tick. A single nudge of 1 tick turns a Perfect into a Good. In this phase Perfect is the dangerous tier (Fine Print), so the Good landing is the safe one.
- The Denial slice applies TIER_DOWN. TIER_DOWN makes a player's slice read one tier lower, which strips a player's Perfect and makes the Perfect hook harder to use.

**Listener (N6):** "Audit." When the player plays a card that deals damage while a needle sits on Denial, the enemy gains BLOCK 3 (a small FLAT amount, scaled by tier). It is a minor tax on hitting through the Denial window. It is not a listener on random input and is undo-clean.

## 3. Sustain and intake

**Sustain:** exactly one source, the Defrag BLOCK. P1 is 6 % of max HP and P2 is 4 %, but only when a needle lands on it.

- Reference dpt at T3 is 14, so the cap is 30 % × 14 = 4.2 per turn.
- P1: the Defrag shares a pair with Dose, so one needle reads it roughly 1 turn in 3 (the pairs rotate). At 112 max HP, 6 % = 6.7 per hit, so about 2.2 per turn averaged. At a Perfect it stays the same, since block does not scale with tier.
- P2: 4 % of 112 = 4.5 per hit, with one Defrag slice among 7. The expected value is ≈ 1 per turn.
- Both are under the 4.2 cap. There is no heal in this fight (heal turns stay 0).

**Intake per turn at the reference player** (assumes the reference player uses the free nudge and one defensive card, and takes about 40 % of the raw expected damage):

| Phase | Raw expected | Target intake |
|---|---|---|
| P1 | ~10 / turn | 3-5 per turn |
| P2 | ~14 / turn, with Fine Print | 6-9 per turn |

That is above 0 (it fixes the baseline's 2.2 taken per turn at T3, which reads as far too soft for an elite). The first-turn spike also stays survivable. The worst P1 pair is Shim + Shim = 16 raw. At T1 that is within a 45-60 HP operative's range.

## 4. HP by tier

Phase budget (R2): `reference_dpt` × 3.5 turns × needles the player's hits land on, minus sustain. The player's wheel has 1 pointer to the enemy, so the player-side "needles landing" factor is 1. The enemy's two needles make the enemy phase budget larger by the pointer rule only when the player attacks the enemy's wheel through multiple needles. The player's attack lands once per player pointer, so the factor is 1.

Per phase, HP = dpt × 3.5 − sustain × 3.5.

| Tier | dpt | P1 gross | P1 sustain | P1 net | P2 gross | P2 sustain | P2 net | Total |
|---|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 2.2 × 3.5 = 7.7 | 24 | 31.5 | 1.0 × 3.5 = 3.5 | 28 | 52 |
| T2 | 11 | 38.5 | 7.7 | 31 | 38.5 | 3.5 | 35 | 66 |
| T3 | 14 | 49 | 7.7 | 41 | 49 | 3.5 | 45.5 | 87 |
| T4 | 18 | 63 | 7.7 | 55 | 63 | 3.5 | 59.5 | 115 |

The raw sums fall slightly under the R2 elite band (56-72, 68-88, 88-112, 112-144). The band is a validation range, so I choose the HP at the band's lower-middle:

`hp_by_tier` = **[60, 76, 96, 124]**

- This is inside every band.
- It is a 30 % cut from today's 112, which at T3 sits at the top of the band.
- The extra HP over the raw sum (about 8-9) accounts for parking waste and the Defrag spikes, because parked damage is lost.

**Threshold floor:** 0.50 × max HP = 30 / 38 / 48 / 62.

## 5. Enrage

**The default (start turn 8, every 5 turns, +25 % damage step, additive).** The fight's target is 6-8 turns, so enrage lands exactly at the edge. A stalling player sees the first step on turn 8 and the second on turn 13. No authored trigger is needed. The fight is short, and the phase floor already prevents stalling at the threshold.

## 6. Buffs and counter Exploits

Not a boss. Not applicable.

## 7. Counterplay

**P1**

- A good player reads the pairs (Shim + Shim, Defrag + Dose, Overflow + Null) and uses the free nudge on the **enemy** wheel to move the worst pair away. Spinning the enemy wheel with a card is also strong.
- Cleanse or Encrypt is worth a card if Dose has landed. P2 doubles RAM costs on corrupted slices.
- Save burst for the Defrag-free turns. Do not attack while Shim + Shim is up unless it is the finisher.
- A weak player ignores the pairs, takes 16 on the first turn, and then loses RAM to Dose.

**Threshold:** hit it hard enough to arrive with one big hit, because the excess damage is lost at the floor. A weak player overkills the phase and wastes a card.

**P2**

- Deny the Perfect. One nudge of 1 tick on the enemy Overflow turns Perfect (18 + an echo of 9) into Good (18). That is a saving of 9 damage per nudge.
- Keep your own Perfects. TIER_DOWN taxes them, so route your own landings to avoid the Denial slice.
- The uneven needles (0 / 11) mean a nudge that fixes one often exposes the other. The player chooses which needle stays dangerous.
- Burst while a needle is on Null, and finish before turn 13.
- A weak player nudges to a Perfect on their own wheel, lands on Denial, and gets TIER_DOWN. They then take the Overflow echo.

## 8. Systems needed

| # | Use | Data-only fallback |
|---|---|---|
| N1 | PERCENT BLOCK, tier-scaled FLAT damage | Use flat amounts and skip PERCENT. |
| N2 | `hp_by_tier` | Set `hp` per tier by hand. |
| N3 | Phase threshold, parking, status keep | Required. No fallback: without parking the threshold has no effect. |
| N4 | Enrage default | A late-turn damage rider is not possible without it. Skip it for a first sim. |
| N6 | The Fine Print and Audit listeners | Drop both. P2 loses its Perfect-denial hook but keeps the uneven needles and Overflow. |
| N8 / N9 | TIER_DOWN, CORRUPTED as a RAM cost | Replace the Denial slice with a plain Shim 10. Dose keeps today's behaviour. |
| N11 | Needle at tick 11 | None. A 0 / 11 needle is needed for P2. A 0 / 10 pair would also work and is already allowed by today's tick-multiple rule. |
| N12 | Variable slice sizes (3, 4, 5, 6) | Fall back to 5-tick slices. This loses the narrow Perfect window, which is the core of P2. |

## 9. Delta vs today

| Item | Today | New |
|---|---|---|
| HP | 112 flat | [60, 76, 96, 124] |
| Phases | 1 | 2, threshold 0.5 |
| Needles | 2 at 0 / 15 | P1 at 0 / 15, P2 at 0 / 11 |
| Slices | 6 uniform 5-tick | 6 slots in P1, 7 in P2, variable sizes |
| Overflow | 16 | 14 (P1), 18 (P2) |
| Defrag | 8 flat | 6 % / 4 % PERCENT |
| Dose | CORRUPTED self-damage | CORRUPTED RAM x2 |
| New | none | Fine Print, Audit, TIER_DOWN, enrage |

**Kept:** the Shim, Overflow, Defrag, Dose and Null slice set, two needles, `cycle_reward = 35`, `is_elite`.

**heat_effects decision: retire them.** The elite currently has no distinct heat rider, and its pressure now comes from the phase structure. The Heat modifiers that already apply (elite frequency at 25, +1 resistance at 50) stay in the campaign layer. A `heat_effects` hook on top would stack with the enrage default and stretch the fight past 8 turns.

## 10. Predicted sim check

| Tier | Turns (new) | Win % | Why | Baseline row |
|---|---|---|---|---|
| T1 | 4.5-5.5 | ~97 | Low HP (60) and gentle P1 pairs | 3.1 turns, 100 % |
| T2 | 5.5-6.5 | ~97 | Slightly bigger HP, same structure | 5.2, 100 % |
| T3 | 6.5-7.5 | ~92 | HP 96 vs 112 today. The parked floor adds a turn. P2 Overflow pressure is real. | 8.8, 100 % |
| T4 | 7-8.5 | ~85 | HP 124, enrage at turn 8 adds a step for slow players. | 14.9, 85 % |

- T1 turns rise from 3.1 because phases force at least 3 turns each.
- T3 and T4 fall sharply from 8.8 and 14.9.
- Intake per turn should rise from ~2.2 to 5-8. This is the main change.
- Threat per turn must exceed 0 at every tier.

## 11. Open questions

Q: Is TIER_DOWN on a Denial slice too punishing in a phase that already doubles RAM on corrupted slices? An alternative is OUTPUT_DOWN x1 (−25 %).
Q: Should the Fine Print echo be 50 % of the Perfect hit, or a flat +4? A percentage grows with tier, and R2 says flat amounts scale by the tier factor while percentages do not.
Q: P2's 7 slots need N12 and the 6-slice cap lifted. Should P2 stay at 6 slots to keep a fallback?
Q: Should the first player turn (a 15 HP operative case from playtests) get a guaranteed gentle reading, for example a P1 opening respin that avoids Overflow + Shim?
Q: Does the threshold line "Claim reviewed. Denied." need a one-turn warning telegraph, as the Migrate pointer has in GDD 2.11?
