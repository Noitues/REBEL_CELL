<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__cell_informant; status ok; tokens in 4505 cache-write 0 cache-read 32585 out 1732; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/cell_informant

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 / §3 / R10 / determinism:** The Citation applies a status to a "random non-NULL slice". That is randomness inside the resolve. Today's SlicePick.RANDOM_NON_NULL exists, but it needs a named RNG stream with a checkpoint, and the draft names none. It also contradicts its own Q3. Use UNDER_POINTER (the slice under the player's pointer) so the preview equals the result.
2. **BLOCKER, §3 arithmetic:** The weights are wrong. Shim is 4 + 5 = 9 ticks, so 9/30 × 8 = 2.4, which is right. Overflow is 4/30 × 16 = 2.13, also right. Total ≈ 4.5 before the tier factor, but the draft calls it "T1 ≈ 4.5". That is above the stated 2-4 L1-2 teaching band, and it says "slightly above" without fixing it. Also, "Shim, Priority, Citation, Detour and Null cost HP 0 directly" lists Shim, which does damage. Rewrite the intake line.
3. **MAJOR, §2 vs §1 (orbit and quality):** The claim that "from any start, the needle reaches Overflow right after Detour or Priority" is false for a 3-tick orbit over 4-tick slices. The needle can skip slices, and the start tick is random after the respin. Also, a start-of-turn respin makes the needle position random each turn, so the orbit trail only shows the landing after that turn's orbit. The "schedule across turns" premise is weak. Reword it as "this turn's landing is visible, so plan this turn".
4. **MAJOR, §2 layout:** Citation (5), Null (4) and Shim (5) give two slices with a Perfect, and the draft's own point is that Perfect matters little. The Citation sitting at the only Perfect slot makes its landing the "good" one. The layout has no ordering rationale. The Overflow in particular sits next to Detour with no adjacency logic.
5. **MAJOR, §4 R2:** The T4 budget is stated as 63, within the 56-70 band. OK. But "Detour is renamed SANDBOX" in the effect column while the same slice is listed as "Detour". Use one name. Also "drain 2 RAM (FLAT)" gets the tier factor, which is not meaningful for RAM; state that it is not scaled.
6. **MAJOR, §10:** The win-rate claims are unsupported. T4 at 90 % when Overflow is 35 (that is, ~58 % of a 60-HP operative) is optimistic. The baseline for a comparable normal is not cited.
7. **NIT, §8:** N11 "not required" is fine. N12 fallback is stated. The orbit "N-less" use should be marked as existing (`pointer_orbit_per_turn` / ORBIT exists).
8. **NIT:** The tier factor is applied to flat damage, but the draft's Shim numbers (8/10/14/18) use rounding that is inconsistent with 8 × 1.69 = 13.5 → 14 and 8 × 2.2 = 17.6 → 18. OK, but state the rounding rule.

## Concrete fixes

- **Fix 1:** Slice 5 row: "Citation | 5 | OUTPUT_DOWN ×1 on **your slice under the pointer** (SlicePick.UNDER_POINTER); fallback PARASITE". Delete Q3.
- **Fix 2:** Replace the intake bullets: "Shim 8 × 9/30 = 2.4; Overflow 16 × 4/30 = 2.1; total 4.5 at T1. To land in the 2-4 teaching band, set Overflow to 12 FLAT (1.6) and total ≈ 4.0 → 4.0 at T1 (Overflow 12 / 16 / 20 / 26 by tier). Prepared play (SANDBOX on the Overflow turn) ≈ 2.4."
- **Fix 3:** Replace the "Orbit order matters" bullet: "The respin randomizes the start each turn; the trail shows the landing after the 3-tick orbit. The player plans within the turn, so nudges and cards react to a visible result."
- **Fix 5:** Name it SANDBOX everywhere. Add "RAM drain is not tier-scaled."
- **Fix 6:** T4 win ≈ 85 %, and mark all win rates as unknown pending the step-0 sweep.

## Keep

- HP by tier [32, 39, 50, 63] follows the phase budget correctly.
- A single phase, no enrage and no sustain are clean for a teaching normal.
- Data-only fallbacks are stated for N1, N2, N12 and N8/N9, and the slice sizes sum to 30.

## Q:

- Q: Should the Informant's orbit be reduced to 2 per turn at L1-2 so the visible landing is easier to read?
- Q: Is a 7-slice wheel too busy for the first REBEL_CELL enemy?
