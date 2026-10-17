<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__route_optimizer; status ok; tokens in 4588 cache-write 0 cache-read 32585 out 1636; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/route_optimizer

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 / §4 HP budget.** The draft's own arithmetic yields 32/40/50/64 for a single-needle reference, and it admits 2 needles imply ×1.5 (47 at T1). It then picks "upper band edges" with no phase-budget math behind them. The "Null/Defrag alignments offset it" argument is hand-waving, because those alignments do not affect the player's damage to the enemy. HP is also inconsistent: 32/40/50/64 is listed, then 34/42/54/68 is chosen. Under R2 the 2-needle bonus is intended ("proportionally more HP"), and the draft itself says so.

2. **BLOCKER, §2 layout vs the pair table.** The layout is Shim 8, Null, Overflow 14, Shim 8, Defrag, Shim 8. The pairs are (0,3) Shim+Shim = 16, (1,4) Null+Defrag, (2,5) Overflow+Shim = 22, (3,0) = 16, (4,1), (5,2) = 22. That arithmetic holds, but the "3-fold symmetric" claim in §1 is false: the layout has no 3-fold symmetry. Also, the 12.7 expected raw damage equals 76/6, which is correct, but "8-10 per turn" at T1 assumes steering that §1 contradicts (an enemy needle position is random per respin).

3. **MAJOR, §1 "shortening answer."** The "both needles on Shim" idea confuses the two wheels. The player's hits land once per enemy needle, so enemy needle spacing is irrelevant to what the player's wheel reads. The player's own wheel has one pointer. "Line your best slice up at both needles" is not a mechanic. The question and its shortening answer are therefore ill-defined.

4. **MAJOR, R10 / §2.** "Pointer ticks stay on multiples of 5 so the data-only layout works" misreads R10: pointers may sit on any tick, and uneven needles are the main tool. The design uses 0/15, so it is not an offender by itself, but it also passes up R10 and R11. Every slice is 5 ticks, so there is no "only one can be Perfect" question and no new design question. The enemy is the baseline layout, reshuffled.

5. **MAJOR, §3 sustain/intake.** Block 5 is described as "paid by the player's damage," which is nonsense. Sustain is zero, which is fine, but the T4 intake is not shown. The §10 admission that 22 × 2.2 ≈ 48 per turn is lethal is a design smell, not a sim note.

6. **NIT, §8.** N11 (pointers on any tick) is not tagged, and the 4-tick Null/Defrag slices were not used.

7. **NIT, §9.** The "today" HP of 48 is above the T1 band. This is fine, but the cause of the problem (the pointer count) is not tied to it.

## Concrete fixes

- **HP (replace §4):** for 2 needles, with an aligned-hit share of 1.5: T1 9×3.5×1.5 = 47 → the band tops out at 36, so cut the needle count or accept a deliberately higher HP. Decision: keep both needles, set **T1 36 / T2 44 / T3 56 / T4 70** (the band tops) and state "2-needle bonus capped at the band ceiling; the sim decides whether to raise the band." Delete the 32/40/50/64 row.
- **Question (replace §1):** *"Two needles read your wheel at once, and one pair reads 22 damage. Can you nudge so the pair lands on Null+Defrag or on WEAK edges?"* Shortening answer: kill it before the 22 pair rolls, via burst and the free nudge. Delete the "3-fold symmetric" and "both needles" text.
- **Needles (R10/R11):** use ticks 0 and 13 (uneven). Layout: Shim 8 (6) · Null (4) · Overflow 14 (5) · Shim 8 (5) · Defrag 5 (5) · Shim 8 (5) = 30. Tag N11 and N12, with the fallback of keeping 5-tick slices and 0/15.
- **Intake:** state T1 expected intake ≈ 8 and T4 ≈ 8×2.2 ≈ 17, then cap the T4 Overflow at 12 up front.

## Keep
- The pair-table presentation is clear and honest about the 22 threat.
- Zero sustain and a clean no-heal identity.
- Trimming the heat_effects question to "none."

## Q:
- Q: Is the 2-needle HP bonus meant to break the band ceiling?
- Q: Should Route Optimizer be a normal at all, with two needles, at L1-2?
