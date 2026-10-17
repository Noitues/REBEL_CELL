<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__mission_director; status ok; tokens in 6756 cache-write 0 cache-read 32585 out 1996; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/mission_director

**Verdict:** FIX

## Issues

1. **BLOCKER, R11 / arithmetic, P1 layout.** 6+4+5+5+6+4 = 30, which is fine. But P3 is 4+5+4+5+6+6 = 30 with the Overflow at 4 ticks, fine. P2 is 5+4+6+5+4+6 = 30, fine. The real failure is the sizes in the draft's own notes: P1 calls the Shim at 4 ticks "no Perfect", yet its 6-tick Null is the biggest slice. This is a nit on its own, but it feeds issue 2.
2. **BLOCKER, R2 / HP arithmetic, §4.** The T3 chosen HP is 150, but the 3-phase T3 band is 132–162 and "minus sustain" applies. Only the P3 sustain (14) is subtracted in the table, and it is not subtracted from 147. 147 − 14 = 133. The draft keeps 150 and then adds the 14 heal back in the P3 turn count. That counts the sustain twice in the wrong direction. T1's 96 and T2's 115 are fine.
3. **MAJOR, R1 / turns per phase, §4.** P3 is "about 4.5 turns, then about 3.5" by an unexplained claim that the double-needle hit halves it. The two-needle damage is already in "needles landing". The Abort Window gate hits (6 each) are not budgeted either. Per-phase turns are not shown to land at 3–4.
4. **MAJOR, R3 / R4, §2 P1 and §5.** The P1 floor is 66 %, but the transition parks at the floor with the Countdown Overflow still pending. The draft never says what the Countdown does on a phase change. Enrage starts at turn 10 against an expected 10.5-turn fight, so enrage fires in nearly every T3 run and is not "only a slow fight".
5. **MAJOR, R8 / R9, §2 P2 and P1.** "OVERCLOCKED on 1 random non-NULL slice" is a random target. It needs a named RNG stream or a deterministic pick, and the preview must equal the result. The P1 Flare is random while the P2 Flare uses UNDER_POINTER, an inconsistent rule.
6. **MAJOR, R12 / N13, §2 P2.** The Launch Window docks a satellite on the *Director's* wheel, but GDD 2.7 satellites dock on the host wheel and hit as bodyguards for the Director, so they are defenders. Relay "Shim 4" would also attack the player. The "intake" arithmetic mixes the two roles. Also, "Max 2" with REPLACE means that after turn 2 every turn replaces one, so hitting a guard never matters, and the draft calls it a trap without showing why.
7. **MAJOR, R6, §2 P3.** `cleanse_on_enter` = OWN is justified by a Virus Exploit, but the draft is not a boss and has no buffs or Exploits, and enemy CORRUPTED is a RAM debuff with no meaning on the Director's wheel (open question 3 of V2). The reason given does not hold.
8. **MAJOR, §8 N15 / N4 gap.** The gate-crossing rule is N15, but the Countdown "at 3, next resolve adds an OVERFLOW" is a state counter needing a hook. The draft says N6 is not required and lists no fallback beyond "no fallback".
9. **NIT, §1.** Q1 asks whether the extra Overflow stacks, but it is also unclear whether Countdown +1 per gate crossed can jump from 2 to 4.
10. **NIT, §3.** Intake is stated at factor 1.0, but R2 scales flat damage by tier. Give the T3 figures.

## Concrete fixes

- **Issue 2 (and 3):** T3 phase budget is 14 × 3.5 = 49 per phase, 147 total. P3 sustain is 4 × 3.5 = 14, so a P3 that needs 49 of effective damage holds 49 + 14 = 63 of removed HP. Set T3 HP = 98 + 98... use this: P1 = 49, P2 = 49, P3 = 49 (net) so floors are at 0.66 and 0.33 of **147**. Set `hp_by_tier` = [96, 115, 147] with T4 = 190, and show P3 as "49 net, 14 healed; gate hits of 6 are bonus, not budgeted".
- **Issue 4:** Add "on a phase change Countdown resets to 0 and a pending Overflow is cancelled". Add "Enrage start is authored at 11 for this unit".
- **Issue 5:** Make the P1 Flare "UNDER_POINTER" like P2.
- **Issue 6:** Rewrite the P2 Relay as a bodyguard with no attack: "Relay: 6 HP, mini-wheel Defrag 3 / Null, fixed". Keep the intake at Overflow 14 and Shim 8.
- **Issue 7:** Set `cleanse_on_enter` = NONE and drop the Virus justification.
- **Issue 8:** Fallback: "Countdown as a Director slice with an authored gate rule; without N15 use plain resistance 2".

## Keep

- Uneven needles (0 / 11) in P3 and the gate inversion (P1 punishes crossing, P3 pays for it) are a good arc.
- The P1 → P2 → P3 questions are each distinct.
- The single 3 % Hotfix passes the 30 % cap, and the data-only fallbacks are clear.

## Q:

Q: Should the Relay satellites also attack, or be pure bodyguards?
Q: Should enrage be authored later (turn 11–12) for this mini-boss?
Q: Do gate hits bypass parking (R3) or are they also parked?
