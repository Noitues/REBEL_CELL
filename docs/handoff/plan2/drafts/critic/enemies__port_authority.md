<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__port_authority; status ok; tokens in 5116 cache-write 0 cache-read 32585 out 1626; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/port_authority

**Verdict:** FIX

## Issues

1. **MAJOR, R2 phase budget / §4:** the sustain deduction is skipped. §3 puts Hold at about 1.0 per turn, "folded in as a ~3 HP margin", but §4 says "with no sustain" and the HP is unchanged. R2 subtracts sustain × 3.5, so each phase is 31.5 − 3.5 = 28 HP in P1. P2 has no Hold, so it stays at 31.5. The total of 59.5 is under the T1 band floor of 56–72? No, it sits inside it, but the arithmetic is internally inconsistent.
2. **MAJOR, §3 arithmetic:** "20 % of ticks × 6 × 0.8 ≈ 1.0" is wrong. Hold is 6 of 30 ticks, so 6/30 = 20 %, and 0.2 × 6 × 0.8 = 0.96. That is fine. But "11 % of 9" is 1.0/9 ≈ 11 %, also fine. The real problem is that the 6 BLOCK is FLAT, while the budget treats it as damage absorbed at one needle. Block only counts if the player hits that slice, so the number is correct but unsourced. The intake table is also unshown: P1 expected raw damage per turn is (6 + 6 + 10) × 0.85/30 × 5 ≈ 3.1 at T1, not 2.8. Show the working.
3. **MAJOR, R1 phase length:** the P1 floor is ceil(0.5 × 63) = 32, which gives 31 HP of budget over 3.5 turns at 9 dpt. With an in-band player this is correct, but at T4 the draft states no turns-per-phase check. Add a turn check with enrage at turn 8 against the 7-turn expected fight.
4. **MAJOR, R8 / §1 P2:** TIER_DOWN ×N on the player's slice does not fit how the draft handles statuses. §2 does not state a stack cap, and §7 says "×2 turns a Perfect into WEAK", which matches R8 only if the stacks are capped. The draft has no cap, so the status can grow without limit by turn 8 and is the main reason for the enrage.
5. **MAJOR, R3 / §2 transition:** the draft does not state that the P1 HP floor also applies to pierce or self-damage. It only says "per R3". Minor, but the Priority RAM drain bypasses nothing, so this is fine. Skip.
6. **NIT, §1:** the pitch says "taxes the quality of your landings", but N8 and N9 are only a fallback via PARASITE. The fallback changes the question from "keep Perfects" to a flat halving.
7. **NIT, Q4:** "Ruling 11" is not a ruling in the supplied text. Rewrite as Q11 in CONTENT_DESIGN_V2 §7.
8. **NIT, §9:** the heat_effects statement ("current file has none") is unverified, and the stated reason cites R2, which does not say that.

## Concrete fixes

- **Issue 1:** replace the §4 note with: "P1 budget = 9 × 3.5 − 1.0 × 3.5 = 28; P2 = 31.5; total 59.5 → `hp_by_tier` [60, 74, 94, 122] (T2: 11 × 3.5 − 1.2 × 3.5 = 34.3 + 38.5 = 72.8; T3: 49 − 5.0 + 49 ≈ 93; T4: 63 − 6.4 + 63 ≈ 120), all in band. Threshold 0.47 for P1 so that P1 = 28 of 60."
- **Issue 4:** add a rule: "TIER_DOWN stacks cap at ×2 (a landing drops at most two tiers). Demurrage on a slice already at ×2 deals 2 damage only."
- **Issue 3:** add to §10: "turns per phase ≈ 3.5 ± 0.5; the first enrage step (turn 8) arrives only if P2 starts after turn 4."
- **Issue 8:** replace the reason with: "no heat_effects are authored; Heat modifiers come from the Grid thresholds (GDD 4.3)."

## Keep

- The question flip: P1 taxes steering, and P2 frees steering but taxes tier.
- The 6- and 4-tick slices with honest no-Perfect maps (sizes sum to 30 in both phases).
- A single needle, which keeps the budget clean, plus the honest N8/N9/N12 fallbacks.

## Q:
Q: Should Hold's block count as sustain for the 30 % cap, or only heals?
Q: Is a TIER_DOWN cap of ×2 the right ceiling at T4?
