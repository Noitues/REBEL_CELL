<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__city_manager; status ok; tokens in 7311 cache-write 0 cache-read 32585 out 1851; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/city_manager

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 phase budget / HP arithmetic.** §4 T3: the budget is 147, but the draft subtracts the P3 sustain a second time ("147 − 8 = 139", authored 140). Per-phase 49 × 3 = 147 already used 14 × 3.5. Sustain is only in P3: 2.2 × 3.5 ≈ 8, so subtracting it once is fine. But the P1 floor "ceil(140 × 0.66) = 93" gives P1 = 47, P2 = 46, P3 = 47, and the HP is split evenly while P3 alone carries the sustain. The draft also treats the Hotfix as 0.57 resolves per turn, which conflicts with "at most 1 Hotfix per turn: 3.9 = 28 %" being the quoted worst case.
2. **BLOCKER, R1/R3 thresholds vs the draft's own concept.** The 0.66 / 0.33 floors are fine, but T1/T2 authored HP (95 / 116) ignore P3 sustain (should be about 87 / 108 at T1 and T2 respectively), while T3 subtracts it. This is inconsistent.
3. **BLOCKER, R10/R11 pointer claim wrong.** P3 says "Layout order is built so… both needles land on dangerous slices only at ~3 of 30 rotations." With needles 13 ticks apart and slices of 4-5 ticks, the pair spans roughly 2.7 slices. Dangerous slices (Citation, Shim, Overflow) are 5 of 7. Both needles are dangerous at about 60 % of rotations. The "safe/dangerous" counterplay is false.
4. **MAJOR, R8/R9 statuses.** The wheel text calls the effect "Citation", but ×2 in P3 is a 2-stack application and the cap of ×3 is not stated for P3. Also "remapped by the centre-tick rule on enemy wheel changes only" misreads R6. The remap applies to the status-bearing wheel whose layout changes. The player's wheel layout does not change, so there is nothing to remap. Reword.
5. **MAJOR, §2 P2 orbit and the nudge dodge.** The text says "spin and Flip cards are blocked by resistance". Under GDD 2.5 spin is only partly absorbed (first R ticks). Only Flip and Respin are blocked. Also the lock stops the paid nudge the turn after, which undermines "steer off Curfew".
6. **MAJOR, intake maths.** P1 intake "(8+14)/6 slice-weighted" is muddled: 8 × 5/30 + 14 × 4/30 = 3.2 is right only if damage is 100 % landed. Defrag is the enemy's own block and does not reduce the player's damage taken. The Overflow in size 4 has no Perfect, but P2's Overflow "size 3 so a Perfect is possible" is a pointless note, since no Perfect bonus exists on enemy slices. P3 gives 2 needles but the sum treats Overflow once, so ~5.1 is understated (should be about 5.3 with 2 needles at 4/30 each: 2×(10×8/30)... recheck needed).
7. **MAJOR, R1 phase length.** At T1 intake is about 3 per turn against 60 HP and the player deals 9 per turn, so the 95 HP fight is 10.5 turns without enrage. P1 blocking (Defrag 10 FLAT) is a plain attrition phase with no question. The draft says "burst while it is mostly blocking", which contradicts itself.
8. **NIT, §9 `is_elite`.** The draft only asks Q4. Fix it in the data: drop `is_elite` and say so.
9. **NIT, enrage text.** "Stacks are a buff and tier-independent" is fine, but "5 damage per turn" is unsupported.

## Concrete fixes

- Fix 1/2: authored HP = budget − (P3 sustain × 3.5): T1 **87** (94.5 − 8), T2 **108** (115.5 − 8), T3 **139**. P3 floor at 0.33.
- Fix 3: set the P3 needles at 0 / 15 (even), or rewrite counterplay as "one needle is often on a bad slice; Null sits 15 apart from Overflow." Layout reorder: Citation 5, Shim 4, Null 4, Overflow 4, Citation 5, Hotfix 4, Shim 4. Needle 13 then reads Overflow when 0 reads Citation.
- Fix 4: "On P1→P2 and P2→P3, statuses on the player's wheel stay untouched (player layout unchanged); the enemy wheel carries no statuses."
- Fix 5: "Flip and Respin are blocked by resistance 2; spin loses its first 2 ticks."
- Fix 7: P1 Defrag → Null-adjacent at 8 FLAT with the question "land Citation on a stacked slice".

## Keep

- Lock as a visible slice, not a conditional.
- The escalation of stacks into lock into two needles.
- Single sustain source in the final phase, within the 30 % cap.

## Q:

Q: Is OUTPUT_DOWN capped at ×3 per slice for the player's whole run, or per fight?
Q: Should the P1 Defrag be removed so P1 has a clearer question?
