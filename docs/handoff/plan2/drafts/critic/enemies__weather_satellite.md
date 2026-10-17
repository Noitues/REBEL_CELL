<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__weather_satellite; status ok; tokens in 4989 cache-write 0 cache-read 32585 out 1815; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/weather_satellite

**Verdict:** FIX

## Issues

1. **BLOCKER, R8/R9, §2 Flare "OVERCLOCK 1 random non-NULL slice" and §3.** The Flare's only damage is the R9 RAM tax, and §3 says "Flare: no damage". The tax appears only after an OVERCLOCK burns out, which needs the player to trigger that slice, so the design can't say whether intake is above zero from it. Also, "random non-NULL slice" is RANDOM_NON_NULL, a random pick outside a named RNG stream or checkpoint. Preview = result needs this to be a deterministic or checkpointed pick.
2. **MAJOR, §3 arithmetic.** The T3 factor is 1.69, so Shim 13.5 × 5/30 = 2.25 (OK) and Overflow 23.7 × 3/30 = 2.37 (OK). That sum is 4.6, not "≈ 2.3 once steered". Null at 11 ticks gives roughly 37% for 0 damage, but the steering claim has no arithmetic. Sustain is also wrong: 4% of 48 = 1.9 HP, and 1.9 × 4/30 = 0.26 (OK), but "hit rate about 1 turn in 6" conflicts with 4/30 (about 1 in 7.5).
3. **MAJOR, §4 vs R2 and today.** The budget table uses tier DPT but no needle count beyond 1, fine. "Today: 44 flat" and "T1 drops 12" claim 44 at T1; the "Today at T3" band is 64-128, so the 44 comparison is unverified. Also T2 38 and T4 62 are inside the bands, but T1 = 32 (budget 30.5) was rounded up without saying so. Minor, but state it.
4. **MAJOR, §2 sub-tick maps vs R11.** Size 4 is W G G W (OK). Size 3 is G P G (OK). Size 5 is W G P G W (OK). But Hotfix and Flare are "no Perfect so a Perfect never doubles it". Hotfix has no Perfect rider anywhere, so that justification is empty. "Shim 5" gets a Perfect, so Overflow's 3-tick window is not the "narrow danger window" the text claims: P is 1 of 3 ticks, which is the same chance as P in 5 ticks per tick (about 1 in 3 vs 1 in 5). It is wider per slice, not narrower.
5. **MAJOR, §1/§2 orbit claim.** "Visits a new slice roughly every turn" and "passes through Null for about 2.75 turns" (11/4). But the wheel respins each turn (GDD 2.2), which makes the orbit forecast meaningless if the needle's start tick is random. Reconcile how the orbit reads "ahead of time" with the per-turn random respin.
6. **NIT, §8.** "Pure data-only version: PERCENT-less Hotfix" overlaps the N1 fallback. §9 says Detour "keeps the same type", but R13 renames it SANDBOX; the table calls it "Detour (SANDBOX)". Use one name. Also "Shim 9 → 8" is unsourced.
7. **NIT, §1.** "No `heat_effects` review needed" but §9 asserts none authored; confirm against the file.

## Concrete fixes

- **Issue 1:** Flare: "Apply OVERCLOCKED to the slice 2 ahead of your pointer (deterministic, the one the orbit reaches next turn)" or declare `SlicePick` CHOSEN-by-enemy as deterministic. Add intake: "Flare also deals 4 FLAT (×factor) damage", giving T3 4 × 1.69 × 4/30 = +0.9 per turn, so intake unsteered ≈ 5.5.
- **Issue 2:** replace the steering line with: "Steered (needle on Null 37% of reads, Detour/Hotfix skipped): ≈ 4.6 × 0.63 ≈ 2.9." Hit rate: "4/30, about 1 turn in 7.5."
- **Issue 4:** Overflow: "3 ticks, G P G: a Perfect is 1 in 3 of its landings, so it is a wide danger window; make Overflow 4 ticks W G G W (no Perfect) and give Null 10." Total: 5+4+4+4+3+10 = 30.
- **Issue 5:** add: "The orbit applies after the start-of-turn respin; the preview shows both, and the 'forecast' is the next-turn post-orbit tick only from a Freeze or Anchor, so state the orbit trail as the displayed next step."

## Keep

- One clear question (read the orbit and steer) with a flat, readable slice set.
- Sustain is tiny, so the fight length comes from damage and not attrition.
- Intake is above zero and the HP arithmetic sits inside the R2 bands.
- Data-only fallbacks are stated for every N dependency.

## Q:
Q: Does the start-of-turn respin make an orbit "forecast" possible at all, or must the orbit act before the respin?
Q: Should Flare be a damage slice (so intake is real) or a pure RAM tax?
Q: Is the 4% Hotfix worth keeping as the single sustain source?
