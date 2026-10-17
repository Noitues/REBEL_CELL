<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__billing_daemon; status ok; tokens in 4524 cache-write 0 cache-read 32585 out 1644; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/billing_daemon

**Verdict:** FIX

## Issues

1. **MAJOR, R2 / §3 sustain arithmetic.** The draft contradicts itself. It states Late Fee as "BLOCK 3 FLAT" in §2, then silently changes it to 2 in §3. Also, "3 × 1.0 = 3 vs 2.7 cap" is computed against a 9-DPT reference as if block were healing. Late Fee is a BLOCK, not heal, so the 30 % cap is arguably moot, but the number must be consistent. The T2-T4 figures (2.6, 3.4, 4.4) use the tier damage factor [1.3, 1.69, 2.2] only approximately (2×1.3 = 2.6, 2×1.69 = 3.38, 2×2.2 = 4.4, so these are fine). §2 is the error.

2. **MAJOR, §4 HP arithmetic.** The budget "gross − half of sustain" is invented. R2 says subtract the full sustain per turn × 3.5. Recomputed with full sustain: T1 31.5 − 7 = 24.5, which is below the T1 band floor of 28. T2: 38.5 − 9.1 = 29.4, below 34. T3: 49 − 11.9 = 37.1, below 44. T4: 63 − 15.4 = 47.6, below 56. The HP values only fit the band because the sustain was halved. Either Late Fee does not count as sustain (justify it) or the budget must be redone.

3. **MAJOR, R1 / §1 intake claim.** "Today's 1.22 HP per turn" is compared with a predicted 2.5 HP per turn, but the unsteered mean (5.2) is just asserted. The 30-tick wheel with a 4-tick Overdue and 6-tick Defrag gives landing probabilities of 5/30, 4/30, 6/30 and so on, not 1/6 each. Recompute: damage = (7×5 + 12×4 + 7×5 + 5×5)/30 = 143/30 ≈ 4.8, RAM = (5 + 8 + 5 + 15)/30 = 1.1. These are small errors, but the "uniform 1/6" shortcut is wrong.

4. **MAJOR, §10 prediction.** "T3 3.8 turns, T4 4.0 turns, with ~95 % win" is unsupported. At T4 intake of ~6/turn over 4 turns costs about 24 HP against a 45-60 HP operative. The 95 % claim needs a stated reason. Also the pass criteria require ≥ 90 % at T3 and a p90 of target + 2, which is not addressed.

5. **NIT, §2 listener design.** Late Fee gives block only when the player pays for a nudge, so it is dominated by simply not nudging. That is the intent, but the penalty is too tiny (BLOCK 2) to be a real question. Note that block expires at the start of the Daemon's turn, so it only matters if the player's hits resolve after it. Clarify.

6. **NIT, N6.** Listeners must stay undo-clean; the draft does not say that Late Fee un-applies when the nudge is undone.

## Concrete fixes

- **Fix 1:** In §2, change the listener to "gains BLOCK 2 FLAT (× tier damage factor), once per turn".
- **Fix 2:** Count Late Fee at full worst-case sustain, or declare it non-sustain because it is temporary block that expires before the next player phase. Preferred: the latter, and the budget becomes plain reference DPT × 3.5, so T1 31.5, T2 38.5, T3 49, T4 63, giving hp_by_tier = [31, 38, 49, 63] (T4 is above the 56-70 band's floor and inside it). Write: "Late Fee is block, not heal; it does not reduce the budget."
- **Fix 3:** Replace the uniform averages in §3 with the weighted figures: 4.8 HP and 1.1 RAM unsteered; roughly 2.4 HP after steering.
- **Fix 4:** In §10, state the per-turn HP cost at T4 (~24 over 4 turns at ~6) and either lower T4 damage or give win ≥ 90 % with a reason.
- **Fix 5:** Add "the listener is staged with the nudge and undone with it" to §2.

## Keep

- The one question (what your RAM is worth) is clear and distinct from the other Solace normals.
- The 4-tick Overdue with no Perfect is a good use of R11.
- The data-only fallbacks in §8 are honest and useful.

## Q:

Q: Does block from Late Fee count against the 30 % sustain cap, given it expires before the player's next phase?
Q: Is draining 3 RAM on Statement acceptable at L1-2 when starting RAM is 6?
