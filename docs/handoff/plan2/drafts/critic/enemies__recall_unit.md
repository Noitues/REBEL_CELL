<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__recall_unit; status ok; tokens in 6157 cache-write 0 cache-read 32585 out 1925; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/recall_unit

**Verdict:** FIX

## Issues

1. **BLOCKER, R2/R3 and §4 arithmetic:** the phase budget is applied to both phases, but the draft sets `hp_by_tier` equal to the total and never splits it at the 0.5 floor. T3 is 98 and the floor is 49, which is fine. The real error is §3: it mixes the tier factor in unclearly ("T3-T4 are tempered by ×1.69 and ×2.2"). Multiplying by 2.2 makes T4 intake larger, not "tempered", and no per-tier intake is shown. Intake is never shown to stay survivable at T4: P2 is ~6 × 2.2 = 13 plus Tag 4 × 2.2 = 9 per turn, which is 22 per turn against about 60 HP.
2. **BLOCKER, §2 P1 layout/R10:** P1 intake of "5.0 per turn" is computed as (5·9 + 5·9 + 4·15)/30, which equals 5.0 only if the pointer is uniform. The needle orbits +2 per turn, so it is not random. The "average over the orbit" claim is unsupported, and "A reference player steers ≈ 3" is asserted without any derivation.
3. **MAJOR, §2 P2 Lock-On:** it contradicts the transition table ("FIXED, no orbit") and the listed Needles field ("re-aims"). It is a NEW hub rule that moves the needle every turn after the start-of-turn respin. That conflicts with the GDD turn flow (every wheel respins randomly, so a deterministic re-aim after the respin is not a pointer behavior in R10/N11). The data-only fallback (keep orbit, drop one Null) contradicts the "orbit stops" identity of the phase.
4. **MAJOR, §2 P2 Recall Tag:** it uses ON_PERFECT, a trigger that exists, but the draft says it "resolves before the end-turn pass" and, in the Q list, may fire on nudge cards. Preview = result is not specified when a Perfect is staged and then undone. The draft also says it hits "your own wheel's landing", but Perfect is only known at resolve; it is a listener on a resolved landing, not a "pre-announced" cost.
5. **MAJOR, §1 distinctness:** the Tag is nearly the Account Manager's Clawback (hit on every Perfect), and the rulings emphasize per-enemy directness. "Small, flat, always shown" is a thin difference. P2 also has no defense and a single question ("pay or not"), and the cost is dominated: 4 flat is cheap against ×4 Perfects, so Perfect is always right.
6. **MAJOR, §3 sustain and §7:** claims "SHIELD absorbs the Tag", but the Tag is listener damage with no stated pierce/absorb rule. The "sustain 0 %" line also ignores P1 BLOCK/SHIELD, which are defenses rather than heal; this is fine, but the phase-budget formula subtracts sustain, so the draft should say so explicitly.
7. **NIT, §1:** the elite is placed at L3-6 and "never L1-2", but the class brief says elites feed layers 3-6, so this is fine. §9 says "heat_effects: the current file shows none" without a quote. §10 baseline T2 11.2 turns is not in the supplied baseline (only T3 20.2 and T4 36 are).
8. **NIT, spelling/ids:** "defence" should be "defense" (US spelling).

## Concrete fixes

- **Issue 1:** add a per-tier intake table: T1 3 / 3.4+Tag, T2 3.9 / 7.8, T3 5.1 / 10.1, T4 6.6 / 13.2, with P2 as 6 × factor and the Tag as 4 × factor. Add "T4 intake reaches ~22 per turn; cap P2 Recall Order at 8 FLAT and Final Notice at 13 FLAT" so T4 is survivable.
- **Issue 2:** state "orbit 2 ticks/turn over 30 ticks gives a 15-turn cycle, so over a 3-4 turn phase the needle covers only 6-8 ticks, about one slice". Intake therefore depends on the start tick: P1 starts on Notice (tick 0), so turns 1-3 hit Notice 9, 9, 9. Replace "≈5.0 average" with that deterministic schedule.
- **Issue 3:** drop Lock-On. Use P2 `pointer_behavior = ORBIT, +3 ticks/turn` (data only, N11-free) with a layout that gives Null 6 ticks. Rewrite the transition line "orbit stops" to "orbit speeds from +2 to +3".
- **Issue 4:** write "Recall Tag: ON_PERFECT, deals 4 FLAT × tier factor to you at resolve, staged in the preview, undone with the action."
- **Issue 5:** make the Tag scale with the landing (2 per Perfect, +2 if the Perfect slice is Final Notice), so a low-damage Perfect is a poor trade.

## Keep

- The two-phase notice/retrieval story and the 64/78/98/126 HP table in-band.
- The wide Null slice as a readable safe landing, and the Retrieval slice sizes (4 and 6) that sum to 30 in both layouts.
- Retiring heat_effects with a stated reason.

## Q:
- Should the Tag read the tier factor at all, since it is flat enemy damage under R2?
- Does the orbit speed-up in P2 replace Lock-On cleanly in the preview?
