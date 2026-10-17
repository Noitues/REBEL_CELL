<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__renewal_engine; status ok; tokens in 9377 cache-write 0 cache-read 32585 out 1853; cost $0.022. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/renewal_engine
**Verdict:** FIX

## Issues
1. **BLOCKER, R1/R2 phase count and arithmetic, §2 and §4.** The draft uses 4 phases, but its own text says "3 `BossPhaseData` entries (P2, P3, P4 on top of the P1 base)", which is fine. The phase HP is wrong, though. Floors at 0.82 / 0.67 / 0.35 of 300 give P1 = 54, P2 = 45, P3 = 96, P4 = 105, which sums to 300. At 320 / 345 / 370 the band tables only rescale turns. The draft never re-derives the per-phase HP, so the floors stay percent-based while the turns column silently inflates. The "3.9 / 3.5 / 3.9 / 4.3" row breaks the 3-4 turn rule (P4 reaches 4.9 at >1.30). The tapered bands still violate R1 in the top two zones.
2. **BLOCKER, Second Opinion counter, §6.** The counter introduces `inert_pointers` and justifies it with "your attacks hit every pointer". That rule is in GDD 2.7 only for the *target's* pointers, so it holds. But the draft is tagged NEW and called an "extension of N11", though N11 only covers pointer placement. Both are acceptable only if the fallback is stated honestly. The fallback "fight lengthens" fails R7 (a counter must not punish the player). Needs a real data-only fallback.
3. **MAJOR, Code Blue rule, §2 P4.** The ruling says "every hit against you corrupts." The draft changes it to once per boss slice and lets it fire through BLOCK. It also says "Landing on an already-corrupted slice is a no-op". The corruption is therefore not tied to damage taken, which contradicts the ruling's intent without designer sign-off. Q2 asks this, but the draft ships it as the design.
4. **MAJOR, amount modes, §2 P1.** The Immunization rider is "CORRUPTED FLAT 1, RANDOM_NON_NULL". Randomness is "shown as odds". It must name its RNG stream and be a checkpointed random event. P4's UNDER_POINTER riders are deterministic, which is good.
5. **MAJOR, Barrier 8, §2.** The draft writes the quality map as "W W G G G G W W", which has no Perfect. R11 lets a slot override via `tick_quality`, so this is legal, but it also needs `tick_quality` tagged under N12 in §8, where it is missing.
6. **MAJOR, Sterile Field, §6.** "strips your statuses" conflicts with R6, where `cleanse_on_enter` BOTH/OWN/PLAYER is a boss-authored option. The V2 text says it cleanses the boss's own statuses. The draft flips it to the player's. OWN means the boss's own, so this is mislabeled.
7. **MAJOR, Metabolism listed as a buff.** R7 says buffs are strong. The draft admits it is "Base mechanic, not strong" and 4 of 8 buffs are weak, so the "signature" count is low.
8. **NIT, §10.** The campaign win rate of 15-25 % is unsupported against the baseline of 4-8 %. No sim reference is given for the 30-40 %.
9. **NIT, Enrage.** The turn-10 estimate (P4 starts about turn 10.5) is only correct if P3 takes exactly 3.5 turns.

## Concrete fixes
- **Issue 1:** Keep the V2 bands (300 / 330 / 360 / 400) and cut P4 by raising the P3 and P4 floors: ≤1.15 → 330 with floors 0.82 / 0.67 / 0.37 (P1 59, P2 50, P3 99, P4 122). P4 at 122 HP / 26 net ≈ 4.7 turns still exceeds 4. Better: put the HP on a 5-phase split above 345, with a 5th "Code Blue II" phase that has the same layout but 3 needles. Add a table of per-phase HP per band.
- **Issue 2:** Fallback: "Breach sets the needle-2 slices to NULL via `wheel_override`, so only one needle attacks while both still take hits." This needs no new field.
- **Issue 3:** Revert to "every enemy hit that reaches you (not SANDBOXed) corrupts one slice" with a per-turn cap of 2 slices. This stays in the ruling and fixes the 5-slice spread.
- **Issue 4:** Add "events RNG stream, checkpointed; the preview shows the odds".
- **Issue 5:** §8 gets the row: N12 `tick_quality` override for Barrier 8.
- **Issue 6:** Change to `cleanse_on_enter` = BOTH under Sterile Field, with "strips all statuses on both sides at each phase change".

## Keep
- The ramp P1 to P4, with a clear question per phase.
- The 14-tick offset analysis (a Perfect Medicine always pairs with an IV).
- Keeping sustain at one source, with the 5.4 cap arithmetic.

## Q:
- Q: Should P4 split into a 5th phase to meet the 3-4 turn rule at higher bands?
- Q: Is Code Blue per-hit with a cap of 2 per turn acceptable?
- Q: Does Metabolism stay a buff or become base-only?
