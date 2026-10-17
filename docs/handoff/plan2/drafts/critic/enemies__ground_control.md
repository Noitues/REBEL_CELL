<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__ground_control; status ok; tokens in 4863 cache-write 0 cache-read 32585 out 1751; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/ground_control

**Verdict:** FIX

## Issues

1. **BLOCKER, §2/§3 arithmetic and layout.** The "boundaries at 0, 5, 10, 13, 18, 22, 30" line is wrong. Cumulative sizes are 0, 5, 10, 13, 18, 22, 30, so the first slice spans ticks 0–5 and is not centred on tick 0. The needle at tick 0 sits on the boundary between Null (last) and Shim (first). Authored centres are 2.5, 7.5, 11.5, 15.5, 20, 26, which are fractional for the odd sizes. State where the layout starts and where tick 0 lands, or the "needle at tick 0" claim is unverifiable.
2. **BLOCKER, §2 vs §3 slice effects.** The table lists "Defrag 8" (8 ticks of block?) but §3 says "Defrag (5/30)" and "about 8 block". Defrag is 5 ticks and Sandbox is 4. The "~30 % of random starts" figure is also wrong: (5+4)/30 = 30 % is correct, but it gives 0.17×8 + 0.13×5 ≈ 2.0 per turn, not 2.4. Also, the defense cap is compared against 30 % of reference damage, a cap that applies to sustain/heal only, so the comparison is misplaced.
3. **BLOCKER, §3 intake math.** The Shim line mixes arithmetic: 10/30 × 10 × 1.69 = 5.6 is correct for two Shims at full output, but the WEAK discount is wrong. Shim is 5 ticks (W G P G W), so the factor is (3 + 2×0.5)/5 = 0.8, giving 4.5. That is fine, but the Overflow is 3/30 × 16 × 1.69 = 2.7 and the total is then 7.2. Check T1: (4.5+2.7)/1.69 = 4.3, which is fine. Yet the draft says Overflow "has no WEAK" while the Shims are discounted, so the total is consistent. The error is the Null: 8 ticks with "W W G G G G W W" is irrelevant for Null and misleading.
4. **MAJOR, R2 amount mode.** "FLAT (× tier damage factor)" is fine, but the HP budget leaves T4 at 60 in a 56–70 band while predicting 88 % win, under the 90 % target. A failing prediction at T4 is not acceptable. Lower the T4 intake or HP.
5. **MAJOR, R10/orbit claim.** "crosses the Overflow roughly once per 15-turn lap" is correct (30/2), but a 3–4 turn fight never completes a lap. The needle moves only 6–8 ticks per fight, so it reads about two adjacent slices, not "orbit prediction". The question is weak: the needle starts on a random tick after the respin, and the player can nudge, so the drift (2 ticks) is smaller than a free nudge (1) plus a cheap one.
6. **MAJOR, template.** §1 says "no status, no listener", yet §7 invents a Freeze beat that conflicts with Q3. Freeze skipping the respin while orbit still moves is unresolved, so the counterplay depends on an undefined rule.
7. **NIT.** Today's slices are listed as "kept", but the change to 6 slices of varying size relies on N12, and the fallback loses both the identity points. Name N19 for the turns metric.

## Concrete fixes

- Layout (fix start and centres): list "Needle at tick 0 reads the first slice's centre by starting layout at tick −2.5"; simplest is to put Shim (5) first and give it centre tick 0 by offsetting the layout by 2.5 and rounding sizes: use 6 slices as 4/5/3/6/4/8 = 30 (Shim 4, Defrag 5, Overflow 3, Shim 6, Sandbox 4, Null 8) so the Overflow centre and tick 0 are stated.
- §3 defense: replace with "Defense per turn ≈ 2.0 (Defrag 5/30 × 8 + Sandbox 4/30 × 5). No sustain, so the 30 % cap is not engaged."
- T4: set hp_by_tier T4 = 56 and Overflow 14 to reach about 90 % win.
- §1 question: "Can you steer the one 3-tick Overflow off the needle using this turn's nudge, given the drift moves it 2 ticks at end of turn?"
- Freeze: "Freeze skips the enemy's respin; orbit still applies."

## Keep

- One needle, one dangerous narrow slice, and a wide Null is a clean, readable teaching question.
- Zero sustain and positive intake at every tier.
- HP bands per tier inside R2, with arithmetic shown.
- Honest data-only fallback stated.

## Q:
- Q: Is a drift of 2 meaningful when a free nudge moves 1 and a fight lasts only 3–4 turns?
- Q: Does Freeze stop ORBIT?
- Q: Should the Overflow have a WEAK edge at T1?
