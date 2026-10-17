<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__claims_adjuster; status ok; tokens in 7129 cache-write 0 cache-read 32585 out 2099; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/claims_adjuster

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 / §4 HP arithmetic.** The P1 net comes to 24, 31, 41 and 55, and the P2 net to 28, 35, 45.5 and 59.5. The table totals 52, 66, 87 and 115, which are below the elite band at every tier (56-72, 68-88, 88-112, 112-144). The draft then picks [60, 76, 96, 124] and explains the gap as "parking waste", which isn't a valid reason. Parked damage is lost, so it doesn't call for extra HP. The draft also never says where the threshold falls on the actual HP. The P2 budget is also wrong because 0.5 splits HP evenly, but the phase nets are unequal.

2. **BLOCKER, R2 sustain math.** The draft computes the P1 Defrag at 6 % of 112 max HP. But T3 HP is now 96, so a hit is 5.8, not 6.7. The draft also assumes the Defrag is read "1 turn in 3". With two needles on pairs, the Defrag is read about 2 of 6 slices, or roughly 1/3 of needle-reads per turn, so the 2.2 per turn figure is inconsistent. Sustain is reported at 2.2 and 1.0 per turn, yet it is deducted as if the player gets all of it. Recompute against the final HP.

3. **MAJOR, R10 / pointers.** P1 pairs claim "slices i and i+3". That only holds for equal 5-tick slices. With sizes 5, 6, 3, 5, 5, 6 the slice centres are at 2.5, 8, 12.5, 16.5, 21.5 and 27. Needles at 0 and 15 do NOT pair the slices as listed. The pair table (Overflow + Null always together) is unverified and likely false. Check by tick: tick 0 lands on the Null/Shim boundary, and tick 15 lands on slice 4 (ticks 14-16, centre 15 is Overflow's neighbour). The readability argument rests on this.

4. **MAJOR, R3 / transition.** "MULTIPLY / MIGRATE style" is vague. A pointer shift from 15 to 11 needs one stated behavior. Parking is also missing the preview ("PARKED −N") and the interaction with the second needle.

5. **MAJOR, R9 / R8.** The draft is internally inconsistent about Dose. Dose is listed as "0 damage" with a CORRUPTED rider and "RAM x2", which is correct. But the P2 counterplay says "double RAM costs on corrupted slices" without stating that it is a debuff on the player's own slice, and TIER_DOWN ×1 stacks on a "slice under the pointer" using the N8 stacks system. The data-only fallback replaces Denial with Shim 10, which loses the phase's one question.

6. **MAJOR, R2 amount modes.** Enemy PERCENT block is 6 % and 4 % of max HP, but §3 discusses "block does not scale with tier", which conflicts with the draft saying flat amounts × tier factor. The Audit listener's "BLOCK 3 FLAT" is the only flat block.

7. **MAJOR, §2 hub rule.** "Fine Print" is called a Hub rule but is actually an N6 listener (ON_HIT_DEALT). It also says "each of your Perfects costs you nothing extra", which is meaningless filler.

8. **MAJOR, Systems.** N9 and N8 are batched, and N11 is described as having a fallback of 0/10, but "today's tick-multiple rule" is gone per R10. The N12 fallback says P2 can use 5-tick slices, yet Overflow 3-tick Perfect windows are the core of the phase. 7 slots: GDD says 6 slices, with the cap lift stated in N12.

9. **NIT, §1.** "Dies on turn 1 at 15 HP" is cited as playtest evidence without source. P2 enrage claims "finish before turn 13" while the class start is 8.

10. **NIT, §10.** T1 baseline turns of 3.1 and the claim that phases "force at least 3 turns" conflicts with a 60 HP elite taking 4.5+ at 9 dpt (60/9 = 6.7).

## Concrete fixes

- **HP:** set P1 and P2 budgets to equal halves. With sustain deducted at the corrected figure, use `hp_by_tier` = [60, 76, 96, 124] and state it as band lower-mid, with the phase split 0.50 (30 / 38 / 48 / 62). Delete the "parking waste" justification.
- **Sustain:** replace with "P1 Defrag 6 % × 96 = 5.8 per read, about 0.33 reads per needle-turn, 2 needles, about 3.8 per turn"? That breaks the 4.2 cap. Change P1 Defrag to **4 %** (3.8 at T3, about 2.5 per turn) and P2 to 3 %.
- **Pairing:** drop the "i and i+3" claim. Recompute with the real tick positions, or set P1 sizes to 5, 5, 5, 5, 5, 5 except one pair (e.g. Overflow 3 + Null 7) so that the pairing is checkable.
- **Transition:** state "Orbit: needle 2 migrates 15 → 11, telegraphed one turn ahead (GDD 2.11)".
- **Fine Print:** rename "listener", tag N6 ON_HIT_DEALT, and delete "costs you nothing extra".

## Keep

The 3-tick Overflow with a Perfect window and the one-nudge denial answer is a real question. The uneven 0 / 11 needles give an actual dilemma. The Audit tax is small and undo-clean. Retiring heat_effects is justified.

## Q:

Q: Should P1 be made to genuinely differ from today (needles even) or should it also be uneven so the 15-HP opening problem is solved by geometry?
Q: Can the same Perfect-denial question be asked with no N6 listener (a bigger Perfect damage multiplier on the slice)?
