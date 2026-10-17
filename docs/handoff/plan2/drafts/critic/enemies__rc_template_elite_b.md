<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__rc_template_elite_b; status ok; tokens in 5279 cache-write 0 cache-read 32585 out 1883; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/rc_template_elite_b

**Verdict:** FIX

## Issues

1. **BLOCKER, R2/R3 arithmetic (§4).** Sustain is subtracted from the P1 budget, but BLOCK is not sustain; the draft itself says "Sustain: none". Treating Guard as sustain is inconsistent. The table also doesn't add up. P1 at T1 is 31.5 − 9.5 = 22, and P1 + P2 = 53.5, which the draft rounds to 54. The "HP set" values (60/72/96/120) are then justified by "slightly above budget", which hides that P1 and P2 shares don't match the 0.50 threshold. P1 budget (22) against P2 (31.5) implies a threshold near 0.41, not 0.50. At T3, 39.5 / 88.5 ≈ 0.45.

2. **BLOCKER, R11 (P2 layout).** The sizes are 5+4+3+5+4+4+5 = 30, which sums correctly. But the "cumulative boundaries: 5, 9, 12, 17, 21, 25, 30" are right while the slice list has a Null of 4 sitting between Lunge and the second Jab. Check the P1 layout: 6+4+6+4+5+5 = 30, which is OK. The real P2 problem is that the Riposte "Perfect-quality tick" rider requires a 5-tick slice, and the "burst window at the Detour/Null edge" is not derivable from these positions. Needles at 0 and 9 sit on tick 0 (Riposte, centre 2 or 3) and tick 9 (the Jab/Detour edge). That is unexplained and unreadable.

3. **MAJOR, R2 (intake, §3).** P1 intake math is wrong. (6+6+12)/6 = 4 is the average over equal slices, but the slices have unequal sizes: tick-weighted damage is (6×4 + 12×5 + 6×4)/30 = 3.6 raw. Then ×1.69 ≈ 6.1, not 6.8. The "intake target 3–5" in P1 contradicts the T3 figure of 6.8. P2 "12–14 at T3" is inconsistent with the stated target of 6–9.

4. **MAJOR, R4/R1 (turns per phase).** The two phases give about 6–7.5 turns in total, but the draft never shows 3–4 turns per phase. At T4, 53.5 HP in P1 ≈ 3 turns and 63 HP in P2 ≈ 3.5 turns, which would work only if the HP split follows the budget (see 1).

5. **MAJOR, N6 listeners.** The Echo "skipped if the player's own result is SANDBOXed" is wrong: SANDBOX is the player's defense, so it should negate the Echo hit as an enemy attack, not the trigger. Also, "once per resolve" vs "once per Perfect" is left open, but the number of fires determines intake.

6. **MAJOR, design quality.** Riposte's "+6 if it lands on a Perfect-quality tick" contradicts §1 ("Perfects are now free in P2"). The Perfect tax persists and the flip is not clean. The Detour is described as "a block on one attack" while the draft says it negates a whole attack.

7. **NIT.** The resistance 1 → 0 change breaks nothing, but the transition mutates it with no hook named. Corporation id given as `rebel_cell`; there is no ruling on this. Echo reuses the mini-boss Handler's Echo idea, so it is not distinct from the sibling.

## Concrete fixes

- **Fix 1 (HP):** Drop the sustain line (set it to 0). Then P1 and P2 budgets at 3.5 turns are T1 31.5/31.5, T2 38.5/38.5, T3 49/49, T4 63/63, which is a 0.50 threshold. Set `hp_by_tier` = [60, 72, 96, 126], with T1 floor 30, T2 36, T3 48, T4 63. The T4 total of 126 is in band (112–144).
- **Fix 3 (intake):** Replace §3 with tick-weighted figures. P1 raw is 3.6 per turn, plus the Echo, and about 6.1 at T3. P2 is about 6.5 raw per needle-turn, so about 11 at T3. Set the targets to 3–5 (T1) and 6–9 (T1, P2).
- **Fix 5 (Echo):** "ON_PERFECT: once per Perfect needle, 4 FLAT (×tier factor), blockable by BLOCK/SHIELD and negated by SANDBOX."
- **Fix 6 (Riposte):** Make Riposte SHIM 12 with no Perfect rider. The flip is then clean: P1 punishes Perfects, P2 doesn't.
- **Fix 2:** Add a sentence naming which slice each needle reads at rest (e.g. tick 0 = Riposte centre-ish, tick 9 = Jab/Detour edge) so the "hot needle" claim is checkable.

## Keep

- The flip in P1 (Perfects punished) → P2 (listener removed, second needle) is a real question change.
- The uneven (0, 9) needles and the 4-tick Jab with no Perfect use R10/R11 well.
- The data-only fallbacks are stated per system.

## Q:

Q: Should the corporation id be set to `rebel_cell` here, or left to the sibling pass?
Q: Does the Echo hit stack with the enrage step at T4?
