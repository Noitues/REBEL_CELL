<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__orbital_debris; status ok; tokens in 4523 cache-write 0 cache-read 32585 out 1926; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/orbital_debris

**Verdict:** FIX

## Issues

1. **MAJOR, R2 tier damage / §3 and §9:** The draft states flat damage "× tier factor" but §9 keeps flat 9 and 6 in the .tres. The T2-T4 intake (2.7 / 3.5 / 4.6) mixes in the table. Fine in principle, but the "T1 baseline" claim and the old wheel's "3.3 per turn" are unverified. Using the draft's own formula, the old wheel (two 10-damage Shims on 5-tick slices at 4/5 effective) is ≈ 2×(3×10 + 2×5)/30 = 2.7, not 3.3.

2. **MAJOR, §3 arithmetic:** The Slab line contains visible scratch work ("computed per tick... Simplified..."). The result is wrong anyway: W W G P G W W gives 3 ticks at 9 and 4 at 4.5, so 27 + 18 = 45 per 30 ticks, i.e. 1.5 per turn. That is correct. But Fragment: W G G W gives 2×6 + 2×3 = 18, i.e. 0.6 per turn, also correct. The total is 2.1 only if the Perfect tick gets no bonus. The sum is fine; the scratch text must go.

3. **MAJOR, §7 resistance arithmetic:** "a 3-tick spin (2 absorbed, 1 moves; so a 4-tick spin is needed for 2 ticks)". It is muddled, and it contradicts §1, where a "3-tick spin lands the needle". Also, GDD 2.5 says Flip and Respin are blocked entirely while resistance is above 0, so "Flip/Respin with the hub down" needs a Hub Breach. The fast answer in §1 is therefore not available to most players. State the real price: 1 RAM nudge ×3 for 1 tick, or a card spin.

4. **MAJOR, §4 budget:** The budget is not shown honestly. 3.5 × 9 = 31.5 and HP 34 is above it, yet the draft claims it "trims" the budget for blocks. Plating blocks 8 on 2/6 of slices, ≈ 2.7 per turn, so effective damage is ~6.3 per turn, not 9. Either the HP is too high or the block must be netted explicitly. T3 50 and T4 62 are also above the 49/63 budget, uncorrected. Block is not "sustain", but it does lengthen the fight.

5. **MAJOR, R13 / §9 and §2:** SANDBOX "negates one whole attack of yours" on a 4-tick no-Perfect slice, replacing a 5-shield. This is enemy-side evade, a strong effect against a player with one big hit per turn, and it makes the "Null/Containment = do nothing" advice dominate Slab. With Containment, Plating ×2 and Null, 4 of 6 slices are defensive or idle (≈ 18/30 ticks). Intake of 2.1 is then too low for a teaching normal that should threaten.

6. **NIT, §1:** "Orbital Debris … teaching for spin resistance" overlaps Meridian's WEIGHT. Also "Ghost core ignores resistance on first nudge" is correct but "Strip" is a card not defined here. §9 says "Defrag 8 stays", but §2 labels it BLOCK; use one name consistently.

7. **NIT, §8:** The N13 and N14 tags are missing; SANDBOX semantics require N14. The fallback should say so.

## Concrete fixes

- **§3:** Delete the scratch line. Replace it with: "Slab 3×9 + 4×4.5 = 45/30 = 1.5; Fragment 2×6 + 2×3 = 18/30 = 0.6; total 2.1 at T1 (2.7 / 3.5 / 4.6 at T2-T4). Old wheel: 2×(3×10 + 2×5)/30 = 2.7."
- **§4:** Net the block: "Plating 2/6 × 8 = 2.7 per turn absorbed; effective dpt = dpt − 2.7." Then T1 HP 28 (≈ 6.3 × 3.5 = 22 plus buffer, floored at the band minimum), T2 34, T3 44, T4 56. `hp_by_tier` = [28, 34, 44, 56].
- **§2:** Raise intake by making Containment 3 ticks (G P G) and Null 5, Fragment 6 (W W G G W W) for 6 + ... Resize: Slab 7, Plating 5, Fragment 5, Plating 5, Containment 3, Null 5 = 30. Intake rises to ~2.5 at T1.
- **§7:** "A 1-tick nudge costs 3 RAM-free-tick absorptions: resistance 2 eats 2 ticks, so a 3-tick paid nudge moves 1. Spin cards (N ≥ 3) are the real answer; Flip and Respin need a Hub Breach."
- **§8:** Add "N14 (SANDBOX negate); fallback: 5-shield as today."

## Keep

- A single-question identity: the heavy wheel plus a wide Slab whose edges can be dragged.
- Sizes sum to 30, with a data-only fallback to 5-tick slices.
- No enrage, no heat_effects, no sustain, and Ghost named as the natural counter.

## Q:

- Q: Should Containment be dropped on a normal, given that enemy-side evade already crowds Orbital's slice set?
- Q: Is resistance 2 teachable at L1, or should it be 1 at T1?
