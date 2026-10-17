<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__collections_agent; status ok; tokens in 4667 cache-write 0 cache-read 32585 out 1736; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/collections_agent

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 vs §1, the question is self-contradictory.** §1 says "the drone sits on the Dose, not on the Overflow" and "hits taken by the drone are wasted". §2 and §7 then say the player "gains nothing" by killing the drone, and that the drone guards the *less* dangerous slice. A guard on the harmless slice is a dominated choice: ignore the drone, always. Phase question: none. (One more ding: the wheel text says the order is Shim, Null, Dose, Defrag, Overflow, Shim, but "Overflow opposite Null" is false. Null is at index 1 and Overflow at index 4, so they are 3 slices = 15 ticks apart. That part is fine, but Null's sibling Shim sits next to Overflow and Defrag precedes it, so a 15-tick spin still works.)
2. **BLOCKER, §3 arithmetic.** The unsteered intake is (6+0+4+0+14+6)/6 = 5.0, correct. But the Defrag is 1/6 × 6 = 1.0 BLOCK per turn, not an expected-sustain figure that counts toward "heal". BLOCK is not sustain, and the drone's Defrag 3 is on a separate wheel and is not boss sustain. The cap check is muddled (the "0.3 × 9 = 2.7" figure compares block with a heal cap). State: sustain = 0 HP heal.
3. **MAJOR, §4 HP budget.** The "+4 drone-dodge allowance" is invented and unexplained. Pure R2: T1 9 × 3.5 = 31.5, T2 38.5, T3 49, T4 63. Subtracting 5.3 block (not sustain) is wrong, and the allowance then cancels it by accident. The HP values still sit inside the bands (32 / 38 / 48 / 62), but the justification must be rewritten.
4. **MAJOR, §2 / R2 scaling.** The listed slice amounts are unmarked as tier-1 base values. State that FLAT amounts × [1.0, 1.3, 1.69, 2.2]. §3 uses a different T4 figure (11.0), which is not 5.0 × 2.2 = 11.0, so OK; but T3 8.5 matches 5.0 × 1.69 = 8.45. Fine. The Q on Dose scaling contradicts R2 (flat enemy amounts always scale); drop that Q.
5. **MAJOR, §2 satellite.** "Resolves after the host", "re-docks once" (§7) contradicts the §Q "never". A "6 HP drone" is not in R2's HP table, and drone HP is a new field with no tag. R12: "fixed" is fine, but N13 says "already effectively true", which is not a tag; N13 is needed for the replacement rule.
6. **MAJOR, §10.** Baseline T3 5.8 and T4 9.9 turns are quoted without a source. Win ≥ 90 % at T4 for an enemy that corrupts is unsupported.
7. **NIT, §7.** A "1-tick nudge to the WEAK edge of Null" is meaningless (Null is harmless at any tick). Better: nudge off the Overflow's Perfect tick onto WEAK (7 dmg).

## Concrete fixes

- **Fix 1:** dock the Collector Drone on **Overflow** (`dock_slot` on the Overflow slice). The question becomes: "Do you pay the drone's HP to open Overflow's guard, or steer the needle away from it?" Because it is on the Overflow, the pointer cannot hit the collector on its biggest slice, so the bodyguard has real value, and killing the drone first (6 HP) is the slow answer. Replace the §1 / §2 / §7 / §9 text accordingly.
- **Fix 2 (§3):** "Sustain: none (no HEAL). Defrag BLOCK 6 is defense (1/6 slices ≈ 1.0/turn); 0 HP of heal, under the 30 % cap."
- **Fix 3 (§4):** budget = dpt × 3.5 with no deductions: T1 31.5 → 32, T2 38.5 → 38, T3 49 → 48, T4 63 → 62. Delete the drone allowance.
- **Fix 4 (§2):** header the table "T1 base; × enemy_damage_by_tier".
- **Fix 5:** resolve the re-dock as "never" in §7 and tag the replacement rule as N13.

## Keep

- Single phase, no enrage, hp_by_tier inside the band.
- One big threat (Overflow 14) with a readable Null / Defrag spread and a card-based answer (the 15-tick spin).
- Dose as a RAM tax under R9 with a clean data-only fallback.

## Q:
- Q: Should drone HP scale by tier through its own hp_by_tier, or fixed?
- Q: Does the Dose's CORRUPTED pick stay random (RNG stream, checkpointed) or become the slice under the pointer for determinism?
