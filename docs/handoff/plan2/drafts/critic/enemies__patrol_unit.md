<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__patrol_unit; status ok; tokens in 4608 cache-write 0 cache-read 32585 out 1704; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/patrol_unit

**Verdict:** FIX

## Issues

1. **MAJOR, Section 3 / R2 (arithmetic, sustain).** Sustain is counted inconsistently. Section 4 uses shield only (1.0), but Section 3 admits block pushes sustain to 2.6 (29 %) at T1 and "about 32 % at T4", which breaks the 30 % cap by its own math. It also says the ratio "falls to ≈14 %" and then "about 32 %". The draft contradicts itself.
2. **MAJOR, Section 3 (expected intake).** The draft's own wheel gives 8×8/30 = 2.13 for the Shim slices. But slices 1 and 3 are 4 ticks each, so Shim covers 8 ticks. That part is right. It then says Overflow is "every 10th turn-start", which is right at 3/30. Yet "Shim 8" intake is raw. Raw damage ignores BLOCK and SHIELD, which is acceptable. The tier scaling is wrong: "Tier ×1.3 → 5.1" scales the T1 total by the T2 factor, but intake at a tier should be 3.9 × [1.0, 1.3, 1.69, 2.2] = 3.9 / 5.1 / 6.6 / 8.6. That matches, so the arithmetic holds. The real defect is that Section 9 changes the base damage numbers without the flat×tier note on Shim/Overflow in the table (the Mode column says "FLAT" on rows 3 to 4 but "FLAT × tier factor" only on rows 1 to 2). Make the column consistent.
3. **MAJOR, Section 2 (a design flaw in the one question).** The sustain/defense slices (Defrag 6, Sandbox 5, Null 8, total 19 of 30 ticks) make the enemy do nothing 63 % of the time. Combined with a 3-tick Overflow, the "tell" is rarely relevant. The question reads as "dodge a 10 % event", which is weak for an L3-6 pressure body.
4. **MAJOR, Section 1 vs Section 2 (self-contradiction).** Section 1 says "Burst while the Sandbox slice is under the needle and shield is down". Under the player's burst, SHIELD 6 only banks if the player does nothing about it, and the Sandbox slice is a self-shield (SHIELD, not Sandbox). The draft mixes the old type name SANDBOX with the R13 names. Under R13, SANDBOX means a whole-attack negate. The slice must be named SHIELD (Hardlight).
5. **NIT, Section 4.** The HP choice sits above the budget at every tier (32 vs 28, 38 vs 34, 48 vs 43, 60 vs 55). The justification ("Null turns cost the enemy nothing") is not a sustain argument. The values stay in the bands; say "rounded up" instead.
6. **NIT, Section 8.** N11 is listed but unused. N14 is called cosmetic, yet Sandbox is renamed.
7. **NIT, Section 10.** The "54 HP was about 6 turns" claim is unsourced.

## Concrete fixes

- **Issue 1:** Replace the sustain paragraph with: "Sustain: one source, SHIELD 6 (Hardlight), expected 1.0/turn = 11 % of 9 DPT at T1. BLOCK is defense, not sustain (it expires the same turn and is not in the R2 phase budget formula), so it is excluded from the 30 % check. Shield stays at about 11-12 % at every tier."
- **Issue 2:** Mode column rows 1-5: "FLAT × tier factor" on every damage, BLOCK and SHIELD row.
- **Issue 3:** Change layout to give the tell more presence: Shim 4 · Defrag 5 · Shim 4 · Overflow 4 (W G G W, 18) · Shield 5 · Null 4 · Shim 4. That sums to 4+5+4+4+5+4+4 = 30. Overflow is then 4 of 30 ticks at 13 % and Null is 13 %. Raw intake: Shim 12×8/30 = 3.2 (using three Shims), Overflow 18×4/30 = 2.4, total 5.6 at T1.
- **Issue 4:** Rename the slice "Hardlight (SHIELD 6)" in the table and Sections 1, 7. Rename "Sandbox slice" in the Section 8 fallback to "Shield slice".

## Keep

The single-needle identity with one big readable Overflow is clean, and the HP table stays inside the R2 normal bands. The Counterplay section names a concrete, cheap dodge (nudge 1-2 ticks). The fallback to 5-tick slices is explicit.

## Q:

Q: Should the 4-tick Overflow lack a Perfect so no landing reads as a bonus for the player's steering?
Q: Is 13 % Null enough to make the free nudge worth spending on offense?
