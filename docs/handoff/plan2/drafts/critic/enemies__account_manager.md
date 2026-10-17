<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__account_manager; status ok; tokens in 7315 cache-write 0 cache-read 32585 out 1850; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/account_manager

**Verdict:** FIX

## Issues

1. **BLOCKER, R1/R2 (budget arithmetic).** §4 sums P1 + P2 to 56 / 66.5 / 87.5 and then picks HP 58 / 72 / 92, but the P1/P2 columns are written as if they were budgets (26+32=58 ✓, 32+40=72 ✓, 41+51=92 ✓). Check the floors: ceil(58×0.55)=32, so P1 = 26 ✓. ceil(72×0.55)=40 ✓. ceil(92×0.55)=51 ✓. The real problem is that P2 gets 32 / 40 / 51 against a budget of 31.5 / 38.5 / 49, and P1 gets 26 / 32 / 41 against 24.5 / 28 / 38.5. The 72 at T2 overshoots by 5.5 and the 92 at T3 by 4.5. That is a 2-HP "rounding up" at T1 but about 6 % at T2/T3, and the draft never reconciles it.
2. **BLOCKER, R2 (Late Fee scaling).** FLAT 2 × tier factor gives 2 / 2.6 / 3.4. The draft says 2 / 3 / 3 and then "2.6×2 → 5 at T2". Rounding is inconsistent, and the T3 figure should be 3.4 (3 or 4). The sustain percentage is computed from the wrong values, so the 30 % cap check is unreliable. The worst case of 2 triggers = 7 at T3 is not shown.
3. **BLOCKER, R1 (phase count vs the P1 mechanic).** P1 turns depend on Retainers (8–13 HP) that the plan says players should ignore. The budget excludes any hits that land on a Retainer, yet the draft expects wasted hits. Either the guard HP counts toward the budget or the P1 numbers are optimistic.
4. **MAJOR, R2/R5 (T4 row).** "92 (copy of T3 so the validator passes)" invents a hack. The spec's table marks mini-bosses n/a at T4. Say "unused; validator must allow n/a for mini-bosses" instead of a copied value.
5. **MAJOR, R9 (corruption in P1).** Dose corrupts a random slice. The draft says "free nudge on a CORRUPTED slice" is a question, but the P1 "spend the free nudge" answer then collides with corruption. The listener also never says whether the free nudge is exempt from Late Fee when it costs 2× RAM.
6. **MAJOR, R3 (parking claims).** The skill-1.0 line "parking floor forces ≥ 2 turns" is false. Parking only stops crossing within a resolve, so P1 and P2 can each be one turn, and the fight can finish in 2 turns. That gives 2–3 turns at skill 1.0, not 3–5.
7. **MAJOR, §1 (concept vs rule).** The draft says "6–8 turns" in the class line but predicts 7.3 and 7.6, and the enrage-from-turn-10 default is irrelevant at that pace. Fine, but the draft claims P1 and P2 are 3–4 turns each; 3.7 + 3.6 ✓.
8. **MAJOR, N#.** Late Fee's "paid nudge" distinction (extra nudge vs card nudge) needs a context flag in the N6 trigger payload; this is not listed. The N6 fallback is described as "hub block 2 per turn", which is a hub sustain with no paid-nudge condition.
9. **NIT, R12.** "Retainers removed at transition" is a new rule, not REPLACE. Tag it as a `wheel_override` side effect (N3).
10. **NIT, Spelling/phrasing.** "Sandbox 5 → removed" is ambiguous. State "the SANDBOX slice is removed".

## Concrete fixes

- **#1:** use T2 HP 68 (P1 28 → floor 40, P2 40) and T3 HP 90, and add a line: "Phase HP equals the budget plus guard allowance of 0 / 2 / 3."
  Table row T2: `68 | 38 | 30 | 38` and T3: `90 | 50 | 40 | 50`.
- **#2:** Late Fee values: T1 2, T2 3, T3 3 (state rounding rule: round half up). Sustain: 22 % / 27 % / 21 % stands. Add a worst-case column: 4 / 6 / 7.
- **#3:** "Retainer HP is excluded from the budget; a hit on a Retainer is a wasted hit, so P1 is expected at 4.0 turns, not 3.7."
- **#4:** T4 cell: `n/a (mini-boss does not spawn at T4)`.
- **#6:** replace the skill-1.0 cell with "2–4 turns; parking only caps each resolve."

## Keep

The P1 RAM-steering question and the P2 "is this Perfect worth 4" question are distinct and well matched to the Solace RAM theme. The sustain accounting, the heat_effects retirement and the data-only fallbacks are strong.

## Q:

Q: Does a Retainer's HP count toward the phase budget?
Q: Is Late Fee exempt on a CORRUPTED-slice nudge that costs 2×?
Q: Should the T4 validator allow n/a for mini-bosses?
