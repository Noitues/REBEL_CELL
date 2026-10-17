<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__conveyor_warden; status ok; tokens in 4886 cache-write 0 cache-read 32585 out 1965; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/conveyor_warden
**Verdict:** FIX

## Issues
1. **BLOCKER, section 2 / R11 arithmetic.** The layout is 6+4+5+6+5+4 = 30, so the sum is fine. But the Shim 6 note says "WEAK edge ticks 0, 1, 4, 5". Under R11 a 6-tick slice maps W W G G W W, so the WEAK ticks are 0, 1, 4, 5 and the GOOD ticks are 2, 3. That matches the draft, but a 6-tick slice has no Perfect, and the draft never says so. Intake also treats the Shim at 0.9 × 8, which is unexplained.
2. **BLOCKER, section 3 / R2 intake.** The scaling is inconsistent. The draft says the flat amounts scale by the tier factor, then reports T3 intake as 26 (×1.69). It also keeps the Defrag at 6 BLOCK in the T1 sustain math. The sustain caps are computed once at T1 and then reused for T2–T4 HP as −5, −6 and −8. The intake sum is also off: 2.6 + 1.4 + 0.5 ≈ 4.5 holds only if the Defrag and Null slices are ignored. That is acceptable, but the Shim 11/30 share is correct only if the Shims are 6 + 5.
3. **BLOCKER, section 4 / phase budget.** Sustain is "13 %" of reference damage, which is a ratio of expected block to damage, but the budget subtracts it as a flat HP amount (−4 at T1). The R2 budget subtracts sustain per turn × turns: 1.2 × 3.5 ≈ 4. That matches at T1. T2 uses −5, which is right only if block scales ×1.3 (1.56 × 3.5 ≈ 5.5). T3 gives 2.0 × 3.5 = 7, not 6. T4 gives 2.64 × 3.5 ≈ 9, not 8. The HPs of 48 and 62 are still in band, but the stated arithmetic is wrong.
4. **MAJOR, section 8 / R10 and the orbit fallback.** The draft says the orbit of 3 needs N11, then offers "orbit of 5 (a multiple of 5)" as the data fallback. R10 removed the multiple-of-5 rule, so this is stale. The orbit is also described as an "existing `pointer_orbit_per_turn`", but the GDD lists Orbit only as an experimental boss pointer phase (2.11). Using it on a normal is new. Tag it N11/NEW, not "existing".
5. **MAJOR, section 2 / sticky-orbit claim.** "Crosses a 5-tick slice in under 2 turns, about 1.8 turns" is wrong for the layout. At 3 ticks per turn, the 6-tick slices take 2 turns and the 4-tick ones 1.33. Also, "the trail makes next turn's landing predictable" conflicts with the start-of-turn respin, which re-randomizes the wheel before the orbit moves.
6. **MAJOR, section 8 / existing content.** The Priority slice already drains RAM, and the draft claims "Today it is a damage-less INFECT". The fallback "N20 hits/damage on an INFECT slice" is a misuse: N20 riders are `hits`, `pierce` and so on, with no damage rider. The correct fallback is a SHIM slice with an extra DRAIN_RAM effect.
7. **NIT, section 3.** The "Null window 4 ticks cannot be held" claim contradicts the counterplay text, which says to hold the wheel on Null or Defrag.
8. **NIT, section 9.** "Shim reduced 10 → 8" and "Overflow 16 → 14" are asserted without sources. The Overflow-at-T2 threat claim ("16 at about T2") conflicts with the 14, 18, 24, 31 scaling.

## Concrete fixes
- Issue 1: add "6-tick Shim and Defrag: W W G G W W, no Perfect. The only Perfect landing is the 5-tick Shim (W G P G W)." Remove "0.9×".
- Issue 3, replace the sustain column: T1 −4 → HP 30; T2 (1.2×1.3×3.5 = 5.5) → 38 ok; T3 (7.1) → 48 ok; T4 (9.2) → 62 (round down: 54 gross band floor 56 is fine). The stated HP values are kept.
- Issue 4: "Orbit 3 per turn needs N11 (pointers on any tick) and the boss-only Orbit behavior (GDD 2.11) enabled on normals: NEW: normal-class pointer orbit. Fallback: a fixed pointer, with the layout rotating through the start-of-turn respin only."
- Issue 5: "Orbit applies after the respin: needle position = respin tick + 3 × turn offset, so only the current turn's landing is shown. The next turn's landing is not predictable." Change the question to "Which slice does the needle reach after this turn's steering?"
- Issue 6: fallback "SHIM slice with extra DRAIN_RAM (data-only)".

## Keep
- The tick-size layout (sum 30) with a no-Perfect Overflow is a clear teaching tool for R11.
- Sustain as the single source, block only, with a nonzero intake.
- Plain-orbit identity, distinct from its siblings.

## Q:
1. Is the orbit applied after the start-of-turn respin, and is the trail drawn for it?
2. Should the Perfect-less 6-tick Shim be the main damage slice, or should the 5-tick Shim be larger?
3. Should the Priority drain scale by tier, given that RAM is a player resource?
