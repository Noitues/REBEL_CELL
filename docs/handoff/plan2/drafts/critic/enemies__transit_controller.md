<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__transit_controller; status ok; tokens in 5482 cache-write 0 cache-read 32585 out 2242; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/transit_controller

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 vs §3 (internal contradiction):** The §2 table says Defrag 8 BLOCK. §3 says "read the Defrag row as 5 BLOCK". The table is the spec, so it must be edited. §9 says Defrag 6 → 5, so the draft states three different values.
2. **BLOCKER, §2 geometry (center ticks and tiers):** Centers are wrong. Centers are cumulative midpoints: Shim1 0-4 → 2, Defrag 5-11 → 8, Shim3 12-15 → 13.5, Overflow 16-18 → 17, Shim5 19-23 → 21, Null 24-29 → 26.5.
   - Needle B at tick 12 on Shim3 (4 ticks, W G G W) is the edge (WEAK), which is right. Turn 2 (tick 13) is GOOD and turn 3 (tick 14) is GOOD, which are right too. Turn 4 (tick 15) is WEAK, which is right.
   - Turn 3: A on tick 2 = PERFECT, B on tick 14 = GOOD, which is right.
   - However, A on tick 0 is "distance 2 from centre 2", which is right, but the "(no Perfect)" label on a 4-tick Shim is fine.
   - Tick 26.5 for Null is irrelevant. This item is a nit-level check, but the "Overflow 3 ticks G P G" is right (center 17).
3. **BLOCKER, §3 (sustain cap):**
   - BLOCK is not a heal. The 30 % cap applies to sustain, but the draft treats BLOCK as sustain and computes it wrongly. 7/30 = 23 % is the chance per needle. Using 5 BLOCK at T3 (×1.69) gives 2 × 0.23 × 8.45 ≈ 3.9, which is correct, but then "5 × 1.69" ignores that the expected tier factor on BLOCK is ~0.83.
   - More seriously, the 30 % cap is on reference dpt per turn *at the tier*. The draft must show it at T4 (18 dpt → 5.4 cap). The T4 value is 2 × 0.23 × 5 × 2.2 ≈ 5.1, which is a pass but tight. Show it.
4. **MAJOR, §4 (budget arithmetic):** The budget ignores sustain. R2 says to subtract sustain × turns: T3 49 − 3.9 × 3.5 ≈ 35. The draft says "no sustain subtracted", which contradicts R2. Either subtract it or state the HP is raised to cover it. The HP values then sit near the band floor or below (T1 32 − 2.7 ≈ 29, T3 ≈ 35, below the 44-56 band). Re-fit.
5. **MAJOR, §3 (intake arithmetic):** Shim hit probability (5+4+5)/30 = 0.47 is right, but Shim 6 at T1 × 0.83 per needle ≈ 2.3 gives 0.47 × 6 × 0.83 = 2.34, fine. Overflow is 0.10 × 14 × 0.83 = 1.16, fine. The "~4.5 after nudge" is hand-waved, because the free nudge also serves the player's own wheel.
6. **MAJOR, §2 (rule/system conflict):**
   - "Start positions: needle on tick 0" conflicts with GDD 2.2 (wheels respin at turn start). The draft admits the respin but then bases the orbit turn table on fixed ticks. The turn-by-turn reads in §2 are fiction.
   - "B reaches tick 16 on turn 5" is likewise unsupported.
   - Needles are pointers; the wheel is what respins. Rewrite the table as relative readings.
7. **MAJOR, §7 (counterplay):** "Nudge the needle off the Defrag... block only costs the player damage if it lands." The player cannot nudge enemy needles unless they nudge the enemy wheel (allowed, 1 RAM after the free nudge). Also "Burst on turns 2-3 while needles sit on weak Shims" contradicts §2 turn 3 (A Perfect).
8. **NIT, §1:** "Parking Warden... single-pointer" claims are unverified. The §11 questions are mostly answerable (the free nudge exists), not open.
9. **NIT, §10:** T4 win ~88 % is below the 90 % pass criterion at T3 and T4. Fix the numbers rather than defer.

## Concrete fixes

- **§2 table row 2:** `| 2 | Defrag | 7 | 5 BLOCK | FLAT |`, and delete the "read as 5" sentence in §3 and the 8 in §2.
- **§3 sustain:**
  - "BLOCK is the one sustain source: per turn = 2 needles × 0.23 × 5 × tier factor × 0.83 ≈ 1.9 × factor. T1 1.9 (21 % of 9), T3 3.2 (23 % of 14), T4 4.2 (23 % of 18). Under the 30 % cap."
- **§4 HP:** budget = dpt × 3.5 − sustain × 3.5.

| Tier | Budget | hp_by_tier |
|---|---|---|
| T1 | 31.5 − 6.7 = 24.8 | 28 (band floor; note it) |
| T2 | 38.5 − 8.7 = 29.8 | 34 |
| T3 | 49 − 11.2 = 37.8 | 44 |
| T4 | 63 − 14.7 = 48.3 | 56 |

  Each value is the band floor. Say so, and note the floor accounts for BLOCK.
- **§2:** replace the orbit table with "tick offsets relative to the turn's random landing; trail shows next turn."
- **§7:** replace the nudge instruction with "spend the free nudge on your own wheel to move out of the Defrag read; nudging the enemy wheel costs 1 RAM after the free one."

## Keep

- The uneven needles (0/12) with a 3-tick Overflow are a clear, single question.
- The sizes sum to 30 and the boundaries are listed correctly.
- A full data-only fallback is stated.
- The Null slice and Overflow 14 are kept.

## Q:

- Q: Is the orbit trail enough for the player to plan, given the per-turn respin?
- Q: Should the Defrag use an authored `tick_quality`, or is the default map fine?
