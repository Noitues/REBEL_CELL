<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__loyalty_test; status ok; tokens in 4868 cache-write 0 cache-read 32585 out 1945; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/loyalty_test

**Verdict:** FIX

## Issues

1. **BLOCKER, R1/R11 + §1 core premise: the central question is dominated.** Draft admits "Good is 1.0×, the same as Perfect." Report punishes Perfect, so the player never gains by taking Perfect except for class hooks. A one-tick nudge to Good costs RAM or the free nudge, so the "question" is mostly "spend a nudge or eat 4." Also the draft claims "Perfect still pays" but gives the player no Perfect-only reward. Needs a real tension.
2. **BLOCKER, §2: layout geometry is wrong and self-contradictory.** Text says "Defrag 12.5→ use 13... see below" (leftover scratch). Audit 0-5 as a 6-slice starting at tick 0 means centre 2.5 and it wraps nothing; cumulative boundaries are 0-5, 6-9, 10-14, 15-19, 20-23, 24-29, which sums to 30, but the "Audit 3, Null 8" centres are wrong. Also the needle at tick 0 reads WEAK on a 6-tick slice (W W G G W W: tick 0 = W), fine, but the 4-tick Null (6-9) centre is 7.5 and the 4-tick Overflow centre is 21.5; the table lists Null as 4 and 6 ticks, so the slice order in the table (Shim 6, Null 4, Defrag 5, Shim 5, Overflow 4, Null 6) is OK, but the prose is garbled. Clean it.
3. **MAJOR, R2: HP budget ignores sustain and the "needles the player's hits land on."** Fine for no sustain, but T1 32 and T2 39 are given as "Current 54 is above bands": correct. T4 63 is inside 56-70. OK. However, the reference arithmetic is fine; the draft's "Both Audit slices can resolve" sentence is irrelevant (one needle).
4. **MAJOR, §3 intake arithmetic is wrong.** Audit tick share: 6+5 = 11/30 = 36.7 %, ×9 = 3.3. Overflow 4/30 = 13.3 %, ×14 = 1.9. Sum 5.2: correct. But the Report adds "about 1.6 per turn" from a 40 % Perfect rate, which is 0.4 × 4 = 1.6 only if one pointer; fine. The T3 "×1.69 ≈ 11" applies to the sum, but then §10 says "11-14 per turn at T3-T4" without T4 (×2.2 → ~15). Inconsistent. Also, the 3-4 turn fight at T1 gives 20-25 damage against 50-60 HP operatives: a 90-97 % win estimate is plausible, but this is not shown.
5. **MAJOR, N6 / R3 rule: Report is "deal 4 to the player" from a listener.** Is it hit-type damage subject to BLOCK and SANDBOX? Draft says SANDBOX negates it "as one resolution," then asks that as a Q. It must be decided.
6. **NIT, §9:** "Solar Flare... stray" and "Hotfix 6" are claims about the current file I cannot verify; treat as unverified. "Heat_effects: none" is likewise unverified.
7. **NIT:** The fallback for N6 is "none"; a data-only fallback is a plain damage wheel, so state that plainly rather than as failure.

## Concrete fixes

- **Fix 1:** give Perfect a payoff the player must weigh. Add to the Audit slices: "WEAK landing on Audit is still a full 9 (no 0.5× applied)? No." Instead: make Report trigger on Perfect AND make Loyalty Test's own BLOCK slice (Clearance) scale: **Clearance = BLOCK 8 FLAT, plus 6 BLOCK per Perfect you landed last turn**? That needs new state. Data-only choice: make Report cost 4 FLAT but have Overflow (Verdict) deal +50 % when you landed no Perfect this turn is also new. Simplest: put the Perfect-capable slices on the player's side as the lure, and give the enemy Audit a **Perfect-only vulnerability** via the player's own hooks (Breaker double resolve). State in §1: "The question is hook value vs 4 tax; classes without a strong hook never take Perfect." Accept and say so.
- **Fix 2 layout text:**
  Audit 0-5 (6, W W G G W W) · Null 6-9 (4) · Defrag 10-14 (5, centre 12) · Audit 15-19 (5, centre 17) · Overflow 20-23 (4, W G G W) · Null 24-29 (6). Sum 6+4+5+5+4+6 = 30.
- **Fix 4:** intake: T1 ≈ 6.8, T2 ≈ 8.8, T3 ≈ 11.5, T4 ≈ 15 per turn unsteered.
- **Fix 5:** "Report is a normal non-pierce hit: BLOCK and SHIELD absorb it, SANDBOX negates it as its own one-hit resolution."

## Keep

Report as a clean, readable listener with a preview chip; no sustain; HP values inside bands; Overflow with no Perfect as a readable design detail; honest sim estimate flagged as no-baseline.

## Q:

1. Should Perfect-landing give any enemy-side Report reward (e.g., the enemy gains BLOCK) so the choice is not strictly one-sided?
2. Is a one-tick nudge cost (free once, 1 RAM after) enough friction for the Perfect/Good choice to matter?
