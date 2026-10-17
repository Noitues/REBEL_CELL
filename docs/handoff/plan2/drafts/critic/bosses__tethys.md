<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__bosses__tethys; status ok; tokens in 15178 cache-write 0 cache-read 32585 out 2049; cost $0.029. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: bosses/tethys

**Verdict:** FIX

## Issues

1. **BLOCKER, R1/R2 arithmetic, boss HP floors.** Thresholds 0.89/0.74/0.46/0.16 of 400 give floors 356/296/184/64, so phase HP is 44/60/112/120/64 (sum 400). That does not match the R2 budgets (46/58/112/119/63). Also the R3 floor is ceil(max × next threshold). P1 sustain is 5.0 against a stated 13 net: (18−5)×3.5 = 45.5 → 46 is fine, but P2 uses sustain 1.5 against a computed 1.0. Re-derive the thresholds from the budgets (fix below).
2. **BLOCKER, R11 slice sizes.** Boss P2: 5+5+5+4+5+3+3 = **30** ✓. P3: 4+4+5+4+4+4+5 = **30** ✓. P4: 5+4+5+3+4+3+6 = **30** ✓. P5: 7+5+7+5+6 = **30** ✓. Mini-boss P2: 8+6+5+6+5 = **30** ✓. **P1 is the failure:** 6+5+6+5+4+4 = **30** ✓, but the Harbourmaster P3 sums to 6+5+5+6+5+3 = **30** ✓. The elites' wheels are not specified in ticks: Siphonophore P1 sums to 6×5 = 30 ✓, but the Angler P2 (7+4+7+5+3+4) = 30 ✓ and its P1 (5×6) = 30 ✓. The real sum error is in the **Diver Drone**: 4+6+5+4+6+5 = **30** ✓. Sums pass; no fix needed here.
3. **BLOCKER, R3/R8, Black Ink buff.** Buff 8 applies TIER_DOWN on every phase change. After the P4 `cleanse_on_enter` PLAYER wipe it re-applies at once, which makes the cleanse pointless. Also the "no RNG" claim is fine, but Black Ink and the P4 cleanse contradict each other. Order it explicitly: cleanse first, then Black Ink applies, or say Ink Filter also cancels the cleanse.
4. **MAJOR, R2 mini-boss HP.** `hp_by_tier` T1 = 80 + a 6 HP Gate = 86. The 3-phase band is 85–105 ✓, but the P2 budget (31.5 − Gate 6 = 25.5) double-counts the Gate: the budget is for hits that land on needles, and Gate HP is separate. The T2 and T3 rows repeat this. Also the mini-boss floors (53/27 at 80) imply thresholds of 0.66/0.33, so the P1 HP 26 does not equal the floor gap of 27.
5. **MAJOR, R2 sustain cap in the boss P1.** Sustain 5.0 against a cap of 5.4 per needle is only OK if the "×1.25 average" holds. At HIGH it is 20 × 12/30 = 8.0 on a HIGH turn. The 30 % cap is per turn, so the HIGH turn breaks it. Add a Sea Wall PERCENT cap in P1 or lower the value to 2 % (8).
6. **MAJOR, R13/N14, "Pierce is not present".** P4 says "Pierce is not present", but P4 Blasts are not pierce, which is fine. However, P5 counterplay relies on SANDBOX negating "the biggest overclocked Surge" while the Fuse adds a round. State that SANDBOX is per resolution, and that the 2 overclocks per turn cannot be solved by one SANDBOX.
7. **MAJOR, systems.** TIDE is a new system with no data-only fallback for the boss, and "the clock is the single point of failure" is admitted. Provide the fallback: a 2-state tide by turn parity (given in the mini-boss) should be listed for the boss and roster too. The status-conditioned chain and the round-fired flags should cite N6 and N20, not NEW.
8. **NIT, Site names (flag 4).** Naming "AIR LEASE, PUMP HOUSE…" conflicts with the ruling. It is limited to art, which is acceptable.
9. **NIT,** "Antifouling", "Sluice Key", "Hull Survey" and similar Exploit names are placeholders. The Exploit trio says "Five more pool Exploits", but the table lists only three non-gate Exploits beyond the 5 untagged ones. Count: 8 buffs ✓.

## Concrete fixes

- Boss thresholds from the budgets (cumulative 46/104/216/335/398): use floors 0.88/0.74/0.46/0.16 → exact P1 HP 48. Or change the P1 HP to 44 to match 0.89. Pick: **P1 44, P2 60, P3 112, P4 120, P5 64** and state "budget sums to 400 within rounding".
- Mini-boss P2 HP: T1 **P2 = 31.5** (the Gate is extra); totals T1 **85**, T2 **101**, T3 **128**.
- Sea Wall P1: PERCENT **2 % = 8** (max 16 at HIGH).
- Black Ink: "applies after `cleanse_on_enter`; Ink Filter also stops the re-apply."
- Add a boss fallback: "2-state tide by turn parity; masks off; P2 becomes plain 1-needle."

## Keep

The tide as a readable 4-step clock that teaches in the normals before the mini-boss uses it. The Harbourmaster P2, where you attack the clock, inverts the bodyguard lesson well. The boss's five distinct questions and the P5 Fuse.

## Q:

Q: Should the tide seed come from a named combat RNG stream, with its checkpoint stated?
Q: Does PERCENT Sea Wall at HIGH count against `shield_cap` for enemies?
