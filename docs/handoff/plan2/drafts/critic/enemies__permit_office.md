<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__permit_office; status ok; tokens in 4590 cache-write 0 cache-read 32585 out 1777; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/permit_office

**Verdict:** FIX

## Issues

1. **BLOCKER, R8/determinism, §2 Citation:** "1 random non-NULL slice of yours (RANDOM_NON_NULL)". A random pick is not allowed outside a named RNG stream, and the preview must equal the result. SlicePick has no deterministic option beyond UNDER_POINTER and CHOSEN. Q3 even asks whether to use the slice under the pointer, but the draft never decides.
2. **MAJOR, §3 arithmetic:** the intake table is wrong. Processing is 3 × (1 + stamps) × 1.3, so 0 stamps gives 3.9, 1 gives 7.8, 2 gives 11.7, 3 gives 15.6. The text says "max 4 hits", so 3 stamps already reaches the cap, but the 0-stamp row shows only one hit. The expected value is also wrong: Filing 4 × 1.3 = 5.2, so 4/30 × 5.2 ≈ 0.7, but the draft adds "0.7 + 0.9" and calls that 1.6. Processing at 0 stamps is 7/30 × 3.9 ≈ 0.9, so that part is fine, but the factor applied at T1 and T3 is never stated, and the BLOCK pad subtracts nothing. The "≈ 2.5 per turn" average is hand-waved.
3. **MAJOR, §3 sustain cap:** "0.3 × reference 11" is fine, but BLOCK 6 is not an amount-mode PERCENT or FLAT × tier factor entry in the table. §2 says Filing is "FLAT (×tier factor)" while the Stamp Pad's BLOCK 6 is not marked. It still has to be shown as a flat amount, scaled by the tier damage factor.
4. **MAJOR, R2 HP vs. its own rule:** HP 32/38/48/62 is in band, but "reference dpt × 3.5 × needles" is applied with the budget of 31.5 and the draft chose 32, which is slightly above budget. Acceptable, but "T2 budget 38.5, chose 38" is fine, while T3 48 vs. 49 and T4 62 vs. 63 are fine too. Only T1 exceeds by 0.5, a nit.
5. **MAJOR, §2 layout and R11 vs. 3-4 turns:** with a single needle and 4 of 6 slices harmless (Citation ×2, Pad, Null = 19/30 ticks), many fights see no Processing at all, so the "peaks at turn 3" claim is not reliable. Intake of about 2.5 is too low for L5-6 pressure, and the same enemy serves both layers with no difference.
6. **MAJOR, dominated choice:** since stamps only matter when Processing lands, and Processing has 7/30 odds, the player can ignore stamps and just burst. The "one question" is weak at T1-T2 (the kill takes 3 turns anyway).
7. **NIT, §2:** Processing says "7 ticks W W G P G W W", but Filing, 4 ticks, "no Perfect" is correct. Fine.
8. **NIT, §9:** invented ids are avoided, but "civic drone spawn (`spawns`)" and the 8 SHIM values are not checked here.
9. **NIT, US spelling:** fine.

## Concrete fixes

- Citation (slots 1 and 5): replace with "applies OUTPUT_DOWN ×1 to the slice under your own pointer (SlicePick UNDER_POINTER); no random pick". Alternatively use a deterministic fixed order: the clockwise next non-NULL, unstamped slice from the one under your pointer.
- Intake table (T2, ×1.3): 0 stamps 1 hit = 3.9; 1 stamp 2 hits = 7.8; 2 stamps 3 hits = 11.7; 3+ stamps 4 hits (cap) = 15.6. Add the T1/T3/T4 factors (1.0/1.69/2.2) and state that the expected value is about 2.5 at T2 only.
- Stamp Pad row: "BLOCK 6 FLAT (×tier factor)".
- Raise the pressure: make Processing 3 damage per hit at 5 hits cap, or add L5-6 variance by having Citation stamp 2 slices at T3-T4 (FLAT count ×1 at T1-T2).
- Make Processing stronger on a Perfect (perfect_multiplier is N20) so landing also matters; this removes the "ignore stamps and burst" dominance.

## Keep

- The "count your stamps" hook is a clear single question, unlike sibling normals.
- The sizes sum to 30 (5+4+7+5+5+4) and the 7-tick Processing slice fits R11.
- Honest data-only fallbacks for N8/N9, N12, and N20.

## Q:

- Q: Should Processing's cap scale with tier instead of being fixed?
- Q: Should L1-2 and L5-6 versions differ (two layouts), or just the tier HP?
- Q: Does Encrypt, which absorbs a status, make the first Citation harmless, so that Cleanse supply matters?
