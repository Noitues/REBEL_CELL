<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__commons_array; status ok; tokens in 7258 cache-write 0 cache-read 32585 out 1980; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/commons_array

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 vs §4 (thresholds contradict).** §2 builds on 0.80/0.60/0.40/0.20 and says "each phase is a 20 % slice." §4 then replaces them with 0.88/0.74/0.46/0.22. The phase tables, intake and enrage timing were never redone for the new split. Worse, 0.88/0.74/0.46/0.22 gives shares of 12/14/28/24/22 %. At 330 HP that is 40/46/92/79/73 (sum 330, ok), but P5 is 73 HP with two needles at 18 DPT, about 2 turns, and P1 is 40 HP, about 2.7 turns. Both fall below the 3-4 turn rule.
2. **BLOCKER, §4 (HP band invented).** The spec band is ≤1.00 → 300, ≤1.15 → 330, ≤1.30 → 360, >1.30 → 400. The draft uses 330/360/400/440, one step too high, and says "ICE ≤ 1.00 → 300" in §2 but 330 in §4. The R2 budget (sum ≈ 445) is also not reconciled with any band. The draft never states that the budget is about 1.4× the band, nor does it fix the shortfall.
3. **BLOCKER, R3/R4 (turns per phase).** At 330 HP the draft's own arithmetic yields about 2 turns per phase in P3-P5. It admits this ("shorter than 3-4") and does not fix it. The fight total of 14-17 turns is also unsupported.
4. **MAJOR, §3 (sustain cap).** The 1.5 % heal is only declared in prose. The §2 tables still say 2 %. Under the new 330 HP, 1.5 % = 4.95, so the cap is nearly breached anyway (5.4). P1 at 1 % is fine.
5. **MAJOR, §2 P2 / R12.** "A Perfect on the guarded slice costs a Relay" and "Relays re-dock after being destroyed" conflict with the fixed-satellite and REPLACE rules. A 2-slice satellite with 15 ticks per slice is also not stated as summing to 30. The P2 layout does sum to 7+5+4+7+4+3 = 30, but it has only 6 slices where the table lists "Relay-Defrag" as a slice type that does not exist. This also repeats the Mission Director's satellite theme the brief says to avoid.
6. **MAJOR, repeats banned patterns.** Flare overclocking is the normals' Solar Flare theme. The brief excludes it, yet P3 is built on it.
7. **MAJOR, arithmetic.** P1: 6+4+6+6+4+4 = 30, ok. P3: 5+4+5+4+4+5+3 = 30, ok. P4: 4+6+3+4+6+4+3 = 30, ok. P5: 5+5+4+5+5+3+3 = 30, ok. P3 says "MULTIPLY from P2" but P2 has one needle. The P3 and P4 needles are 14 and 11 apart, and the text claims B "trails A by 11" while both orbit, so uneven spacing never changes.
8. **MAJOR, R9.** The P3 Burnout listener deals damage when a slice burns out. R9 moves damage onto the Parasite ring. Also "CORRUPTED ... doubles RAM" appears correct elsewhere.
9. **MAJOR, §6.** Only 8 buffs, of which Burnout Link, Chart Hidden and Debris Field are weak. "Orbital keeps Intel, Breach, Virus as gate Exploits" contradicts the "any 3 of the drawn subset" open question.
10. **NIT.** §11 asks the same things as the issues above. The enrage claim "first step lands at the start of P4" is unsupported.

## Concrete fixes

- **Band and thresholds:** use the spec band (300 at ICE ≤1.00). Use equal-turn thresholds 0.84/0.66/0.38/0.16, giving HP 48/54/84/73/41. Alternatively, accept that the 445 budget exceeds the band, set P3-P5 to 1 needle in P3, and add a single 3.5-turn pacing check. Recompute: at 300 HP and 18 DPT (×2 on two needles), P1 = 48 (2.7 turns, so raise P1 to 20 %).
- **Cleaner split, 300 HP:** thresholds 0.80/0.62/0.40/0.18. Phases = 60/54/66/66/54. Turns at DPT 18 (sustain subtracted) ≈ 3.8/3.5/2.1/2.1/1.5. Rewrite P3-P5 to one needle each, or move the second needle to P4 only.
- **Sustain:** hub heal 1 % in P1, 1.5 % in P2-P4 (4.5 HP). Update the tables to match.
- **Satellites:** remove "re-dock" and "costs a Relay". Say a fixed Relay is destroyed only by hits on it, and no replacement.
- **Burnout:** replace it with a Debris parasite that triggers on a corrupted slice, or drop it.
- **P3:** replace Flares with a Parasite-ring question.

## Keep

- The Orbit Schedule clock and readable trail concept, with the Station Keeping signature heal tied to a counter Exploit.
- The uneven needle question in P4 and the racing end phase.
- Honest fallback table and slice sums that mostly check out.

## Q:

Q: Which is binding, the spec band (300 base) or the draft's 330?
Q: Should P5 be one needle so it stays at 3 turns?
Q: Drop Flare overclocking from this boss?
