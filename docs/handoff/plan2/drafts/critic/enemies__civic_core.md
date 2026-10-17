<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__civic_core; status ok; tokens in 8517 cache-write 0 cache-read 32585 out 8874; cost $0.056. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/civic_core

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 / template §3, sustain cap 30 %.** The heal is a PERCENT of max HP, but the cap is checked only at 340. At 380, 1.5 % is 5.7 per turn (32 %). At 420 it is 6.3 (35 %) and at 460 it is 6.9 (38 %). Every `hp_bands` entry above 340 breaks the cap.
2. **MAJOR, R1 / R2, 3–4 turns per phase.** The thresholds are fixed percents, so the higher bands stretch the phases. At 460, P4 is 179 HP, or 5.0 turns at 36 dpt. P5 is 92 HP, or 5.1 turns. P1 is 69 / (18 − 6.9), or 6.2 turns. Section 4 lists the HP but never checks it against 3–4 turns. The draft raises this only in the last Q.
3. **MAJOR, Warrant Ledger.** `Warrant hits = total TIER_DOWN stacks` has no cap. With 6 slices at 2 stacks that is 12 hits of 7, or 84 damage per Warrant. That one-shots a 45–60 HP operative. Base Warrant is also unbounded at 6 hits (42).
4. **MAJOR, Sunset Clause is ambiguous.** The P5 table says orbit 5, but the buff says "orbit is 5 not 3", so the base orbit is unclear. The enrage cadence "every 2 turns in P5" gives no start turn and no step size. R4 says enrage is additive from a start turn.
5. **MAJOR, P4 hinges on SANDBOX (N14).** In today's data only the Rigger wheel carries a Sandbox slice, and Ghost has Detour. The other classes have no answer, so "which needle do you SANDBOX" is not a question for them. "A Baton is the cheapest SANDBOX in the game" is also wrong. SANDBOX is free in cost terms and negates one whole resolution, so you would always spend it on the 15-damage Crackdown, not the 13 total of a Baton.
6. **NIT, P2 Ban.** At 4 HP per extra card, a 10+ damage card is always worth the tax, so the choice is dominated. The intake figure of 8.4 also counts the Ban for a player who is "one card over", but a reference player at two cards pays 0 (intake about 4.0).
7. **NIT, P5 vs P3.** P5 repeats P3's Warrant plus orbit, only with a different speed and no Null. The new question is thin.
8. **NIT, §3.** "Heal turns per phase stay under 4" misreads the criterion, which is at most 1 heal turn per phase. A hub heal fires every turn, so state the criterion as the 30 % cap instead.
9. **NIT, §8.** N6 needs a cards-this-turn count condition, which is a small extension to the listener; say so. N5 and N12 fallbacks are unstated or inconsistent: the N12 fallback of 6 × 5-tick slices cannot hold P4's 8 slices. The N8 fallback (PARASITE as OUTPUT_DOWN ×2) changes the status the design is built on.

Tick sums check (30 in every phase), and the floors 289 / 245 / 201 / 68 check. The budget sum of 330 is correct.

## Concrete fixes

- **#1:** Set the heal to P1 0.8 %, P2 and P3 1.1 %, and add a cap row for the 460 band.

  | Band | P1 heal / turn | P2–P3 heal / turn |
  |---|---|---|
  | 340 | 2.7 (15 %) | 3.7 (21 %) |
  | 460 | 3.7 (20 %) | 5.1 (28 %) |

  At 340 the phases then run about 3.3 / 3.1 / 3.1 turns, still inside 3–4. Update §3 and the P1–P3 hub rows.
- **#2:** Compress the bands to 340 / 360 / 380 / 400. This matches Genome Core's 300–400 spread and gives P4 ≈ 3.7 / 4.0 turns at the top. Add a line: "p90 of turns per phase is checked at 340 and 400 (N19)."
- **#3:** Add "Warrant `hits` capped at 6" to the Warrant row. Warrant Ledger then reads "cap raised to 8". The worst case is 8 × 7 = 56, which still hurts but does not one-shot. Add: "Warrant hits are previewed on the pointer chip."
- **#4:** The P5 table says orbit 3 (base). Sunset Clause makes it orbit 5. Sunset Clause enrage reads: "In P5, enrage steps +25 % every 2 turns from P5's first turn, additive on top of the default steps."
- **#5:** Rewrite the P4 defense line: "SANDBOX if you carry it (Rigger, Detour Ghost); otherwise steer. Without SANDBOX, one needle is steered to Null and the other is eaten. Add one Notice at 3 ticks as the safe slice." Delete the "cheapest SANDBOX in the game" claim.
- **#6:** Make the Ban 3 FLAT, which is 6.6 → 7 per card beyond the 2nd, so a 5-card dump costs 21. Intake for P2 then needs a reference-player figure: 6.4 with 0 over, plus 7 per extra card.

## Keep

- The thresholds and floors are exact. The 51 / 44 / 44 / 133 / 68 split sums to 340.
- Marks that persist through R6 and are cashed in at P3 and P5 are the fight's identity. Cleanse is a defense card and a damage card.
- The uneven needles at 0 and 13 (R10) and the 3-tick G P G Dispersal slice are good uses of the new geometry.
- The enrage timing fits the phases: step 1 lands on P4 and step 2 on P5.

## Q:

Q: Should the boss HP band scale phase thresholds (as the draft asks), or should the top band be capped near 400 so the 3–4 turn target holds?
Q: Is a Cleanse that removes all TIER_DOWN stacks on a slice intended, given that it makes Cleanse a top card in P3?
Q: Is the sim's skill-1.0 win target of 35 % fresh right for a first-contact HQ boss, or should the fight be closer to the 25 % baseline?
