<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__geostationary_guard; status ok; tokens in 6039 cache-write 0 cache-read 32585 out 1831; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/geostationary_guard

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 P1 layout, tick arithmetic.** The sizes are 5+5+5+4+5+6 = 30, so the sum is fine. The spans do not fit, though. Starting at −2, Shield covers −2..2, Shim 3..7, Flare 8..12, Overflow 13..16, Shim 17..21 and Null 22..27. Ticks 28 and 29 (= −2, −1) are covered twice and the Shield overlaps them. The spans end at 27, which is 28 ticks, not 30. The listed span widths also don't match the sizes: the 6-tick Null spans 22..27, so Shim 17..21 is 5 and the rest is right. The spans are mislabeled or the layout is really 28 ticks. The sum check is dishonest.

2. **BLOCKER, §2 P2 layout.** The sizes are 5+5+4+4+4+4+4 = 30. The spans run −2..2, 3..7, 8..11, 12..15, 16..19, 20..23, 24..27, which is again only 28 ticks. The needle at tick 0 sits on slice 0, but the final slice 24..27 should wrap to 29. Re-derive the spans from cumulative sizes starting at −2 (the last slice ends at 27 = 30−3).

3. **MAJOR, R11 / §2 Overflow.** "A 4-tick slice (W G G W) has no Perfect; it is full output on 2 of 4 ticks." This is correct, but the intake math then uses 0.75 and 0.8 tier multipliers with no derivation. P2 Overflow mixes a 5-tick slice (one Perfect) with a 4-tick one. Intake is not shown per tick.

4. **MAJOR, R2 / §4 budget.** The P1 budget uses 28 and the P2 budget uses 32. The author then picks 30/30 and says drone interception "offsets" it. The drone is an extra needle target, so a reference player spends hits on it, which makes P1 harder, not easier. T3 is 48/48 against budgets of 43/49. Both phases need an explicit arithmetic line. The P1 drone's HP is not budgeted.

5. **MAJOR, R6 / R12 / §8 "NEW: phase clears satellites".** `wheel_override` already handles slot content. Check first whether `satellite_spawn_data` and the override cover removal. The invented field also contradicts the fallback, which is itself broken: "Shim dropped into Shim 5" is not a layout.

6. **MAJOR, R8 / R9 §2 Statuses.** P1 and P2 Flares apply OVERCLOCK at random on both phases. The draft never says the burn goes to CORRUPTED as double RAM, apart from one line in §7. The threat to "eat" is the Overflow Perfect that cannot happen on a 4-tick slice. Counterplay claims "a 16-damage Overflow Perfect" on the 5-tick one only, which is fine, but the 1.5× overclock window is unquantified.

7. **NIT, §2 P1 hub.** Resistance 3 is restored each turn. "3-RAM-or-nothing" is wrong: resistance absorbs ticks, so one nudge of 1 tick is fully absorbed and costs RAM for nothing.

8. **NIT, §9.** The draft says today's Sandbox is 8 and the Shim 14 without citing the file. The N13 fallback ("mobile today") conflicts with R12.

## Concrete fixes

- **P1 layout:** use cumulative boundaries from −2, so slice i spans start..start+size−1 and the last slice wraps: Shield −2..2 · Shim 3..7 · Flare 8..12 · Overflow 13..16 · Shim 17..21 · Null 22..27 **plus two ticks 28..29.** The simplest fix is to make Null 8 ticks (22..29) and drop another slice to 4. Corrected sizes: Shield 5 · Shim 5 · Flare 5 · Overflow 4 · Shim 5 · Null 6 = 30 with spans that wrap by listing the start tick of each slice (−2, 3, 8, 13, 17, 22) and the Null ending at 27 + wrap. State the convention once and show the sum.
- **P2 layout:** list start ticks (−2, 3, 8, 12, 16, 20, 24), sizes 5/5/4/4/4/4/4, and state that the last slice's end wraps to tick −3.
- **§4:** replace the 30/30 rationale with: "P1 28 + drone (5 HP ≈ 1.5 hits) = 30; P2 32 is parked at 30 because the threshold is shared."
- **§8:** replace the NEW field with: "check `satellite_spawn_data` for a clear-on-phase flag; if missing, fallback is the drone persists and `max_active` = 0 in P2."

## Keep

The resistance lock in P1 that vanishes in P2 is a clear question flip. The 3-tick orbit trail makes P2 readable. HP is inside the band at every tier. The heat_effects decision is justified.

## Q:
Q: Does the P1 drone count toward the phase HP budget?
Q: Should the Flare burn go to CORRUPTED immediately on P2 entry, or only when the slice triggers?
