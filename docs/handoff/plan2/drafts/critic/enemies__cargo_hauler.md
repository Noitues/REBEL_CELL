<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__cargo_hauler; status ok; tokens in 4741 cache-write 0 cache-read 32585 out 1961; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/cargo_hauler

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 phase budget / §4 arithmetic.** The budget "9 × 3.5 = 31.5, +3" adds soak on top of the budget. R2 subtracts sustain from the budget and never adds block. The band (T1 28-36) is fine, but the +3/+4/+5 top-ups are invented and unlabeled. T4 66 is also near the band's top while the stated turn target is 4.0. Defense slices are not sustain. Either HP lands at the budget (31/38/49/63) or the draft states an R2 exception.
2. **BLOCKER, §2 vs §1, the question vs "no ring or listener".** Resistance 2 is a hub passive that already exists. But the Shim "+1 resistance on trigger" is a new on-trigger resistance rider. It is not in the GDD and has no N#. The draft kept it "from shim_8_weight", but the growth is unbounded, and the draft hand-waves the cap ("Cleanse-on-turn, or accept"). Cleanse does not touch resistance.
3. **MAJOR, R11 / §2 Crush text.** "A 4-tick slice has no Perfect, so it hits as G/G or W." The R11 map is W G G W (two Goods, two WEAK). Likewise, the "Null 6" parenthetical (W W G G W W) is correct, but "Sandbox 3: Perfect only at the centre tick" is fine. Only the Crush wording is wrong.
4. **MAJOR, §3 intake arithmetic.** (4×14 + 5×8 + 3×8)/30 = (56 + 40 + 24)/30 = 4.0, which checks. But the "WEAK cuts about −10 %" claim is unshown. A 4-tick slice is 50 % WEAK, so Crush alone loses about 25 %, and the 5-tick Shim loses 40 %. The real figure is nearer 3.0 raw. Also, "2.5-3.5 per turn at T1" after block contradicts the 4.0 raw figure only loosely. T3/T4 values are ×1.69/×2.2 of the same figure. State one method.
5. **MAJOR, R1 / §10 target turns.** T4 predicted 4.0 and "resistance growth could push T4 over 4". That risks breaking the 3-4 turn ceiling. The prediction is not tied to a sim row (no Meridian baseline).
6. **MAJOR, §8 fallbacks.** The N2 fallback ("single hp 52 plus global scale") violates R2 (tier sets base values, no multiplier for HP). Also N1 "without N1 old output_scale applies" is acceptable, but is flagged only as "acceptable".
7. **NIT, §9.** "Defrag count goes 2 → 2" is noise. The Overflow 14 added to a weak L1-2 teacher: Q2 itself admits it is swingy.
8. **NIT, §7.** Weak-player text claims Strip and Hub Breach turn Weight off. Hub Breach disables only a Hub-sourced resistance, and this one is a "passive trait", so Hub Breach does nothing here. Ghost's strip works.

## Concrete fixes

- **HP table (#1):** T1 **31**, T2 **38**, T3 **49**, T4 **63**, i.e. 9/11/14/18 × 3.5 × 1 needle, sustain 0. Delete the "+3/+4/+5" soak column. If the designer wants extra for BLOCK, state it as an explicit exception.
- **Growth rider (#2):** replace the Shim 3 effect with a plain "Shim, 8 damage FLAT". Resistance stays at the fixed passive 2 (restores each turn). If growth is wanted: NEW: `MODIFY_RESISTANCE` rider on trigger (EffectType MODIFY_RESISTANCE already exists), capped at 3 through a data field `max_resistance` (NEW). Fallback: no growth.
- **Crush (#3):** "4 ticks: W G G W, so 50 % of landings are WEAK (7 damage), 50 % Good (14). No Perfect."
- **Intake (#4):** raw expected = Σ(size × damage × tier-factor) / 30, with WEAK 0.5×: Crush (2×14 + 2×7)/30 = 1.4, Shim5 (3×8 + 2×4)/30 = 1.07 (W G P G W gives 1 W, wait: 2 W, 3 G/P), Shim3 (2×8 + 4)/30 = 0.67. Total ≈ 3.1 per turn at T1 before block, ×1.3/1.69/2.2 above. Rewrite the §3 ranges from this.
- **Fallback N2 (#6):** "Fallback: author the four values in a temporary per-tier `.tres` variant until hp_by_tier lands."
- **Hub Breach (#8):** delete "Hub Breach"; keep "Ghost strip / first nudge ignores".

## Keep
- A single clear question (pay or park) with a genuine 1-tick-nudge trap; the Null/Brace "leave it alone" answer.
- Uneven slice layout that sums to 30 and uses N12 purposefully; Sandbox's narrow window.
- Honest arithmetic on raw intake (4.0, which checks) and a no-listener, no-enrage normal.

## Q:
- Q: Is Weight growth wanted at all, given there is no resistance cap field?
- Q: Should Crush drop to 12 for L1-2 teaching, or be gated to L5-6 only?
- Q: Is the elite-sized 72 HP history deliberate lore to preserve, or just a legacy number?
