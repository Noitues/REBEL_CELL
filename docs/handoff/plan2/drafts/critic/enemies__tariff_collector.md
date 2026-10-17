<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__tariff_collector; status ok; tokens in 4810 cache-write 0 cache-read 32585 out 1801; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/tariff_collector

**Verdict:** FIX

## Issues

1. **MAJOR, R2 / §4 phase budget:** the HP rows don't follow the draft's own formula. Gross minus sustain is 31.5−3.5 = 28, 38.5−3.5 = 35, 49−3.5 = 45.5 and 63−3.5 = 59.5. The table lists 32 / 38 / 48 / 62 instead, so only 28 and 35 are in-band and the stated arithmetic is wrong. The sustain column is also wrong: it says "1.0/turn" but then charges a flat 3.5 at every tier.
2. **MAJOR, §3 sustain math:** "Ledger lands on at most 1/6 of rolls... 6 block / 6 = 1 block per turn" is only the expected value. Block is not HP sustain, and the draft does not show it against the 30 % cap in a way that matches the HP deduction. The deduction should be one consistent number (see fixes).
3. **MAJOR, R8/R9 / Late Fee:** "OUTPUT_DOWN ×1 on the slice under *your* pointer" is an INFECT status. The text says "applied on any landing", which is fine, but the RAM drain and the status together on a 4-tick no-Perfect slice make it the second RAM source. The §3 RAM expectation also ignores that CORRUPTED is now a ×2 RAM cost, so the draft contradicts nothing but never uses it. This is a NIT-level missed chance unless N9 is cut.
4. **MAJOR, §8 fallback:** "merge the Toll count to 2" on six 5-tick slices is unclear. The PARASITE fallback is described as harsher (−50 %), but R8 says PARASITE becomes a 2-stack OUTPUT_DOWN, which is the same thing, so the "harsher" fallback is not a different option. It needs a data-only version that works without N8.
5. **MAJOR, §3 intake:** the 0.8 WEAK average is unexplained. A needle that is not steered lands on all 6 slices equally, so the WEAK share is 2/5 for 5-tick slices and 1/2 for 4-tick slices (the 4-tick map has no Perfect). The expected damage uses the wrong mix; also the Surcharge OVERFLOW on a 4-tick slice has no WEAK-only treatment shown. Recompute with a per-slice tier mix. The T4 damage is scaled by 2.2 but the 10 and 6 base values stay unscaled in the table.
6. **NIT, Q4 / §3:** can RAM drain exceed current RAM? The draft leaves it open although it is a required rule for the preview.
7. **NIT, §9:** "Shim 7 / Overflow 12 / drain 3" are claims about today's .tres that cannot be checked; label them "per draft's reading of the current file".
8. **NIT, §10:** win % is "estimated" with no baseline row; fine, but say that no baseline row exists for this enemy.

## Concrete fixes

- **HP table (replace §4):** sustain per turn = 1.0 expected block, taken as 1.0 × 3.5 = 3.5 at all tiers.

| Tier | Ref dpt | Gross (×3.5) | −3.5 sustain | hp_by_tier |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28 | **30** (band 28-36) |
| T2 | 11 | 38.5 | 35 | **36** (34-44) |
| T3 | 14 | 49 | 45.5 | **46** (44-56) |
| T4 | 18 | 63 | 59.5 | **60** (56-70) |

  Each value is rounded up to a whole HP and sits in its band. Today's 53 at T3 therefore drops to 46.
- **§3 intake:** tier mix per slice: Toll (5-tick) 40 % WEAK; Surcharge and Late Fee (4-tick) 50 % WEAK. Expected unsteered damage per turn = (6×0.8 + 6×0.8 + 10×0.75)/6 = 2.85 at T1. T2 ≈ 3.7, T3 ≈ 4.8, T4 ≈ 6.3, after the damage table. State it this way.
- **§8 fallback without N8:** use today's PARASITE status on Late Fee and treat it as a 2-stack OUTPUT_DOWN. Say plainly there is no softer data-only option. Drop the "harsher" claim.
- **Q4 answer:** RAM drain is capped at current RAM and never makes it negative. There is no HP penalty, so the preview stays simple.

## Keep

- The single clear question, "what is your RAM worth?", is distinct inside Meridian.
- The Toll / Surcharge / Late Fee split keeps one cheap choice, one narrow dangerous slice and one status choice.
- The 6/6/4/5/4/6 layout sums to 30 and uses R11 sizes properly, with no hub or enrage.

## Q:

- Q: Should Late Fee cost 2 RAM on top of the status, or is the status alone enough of a toll?
- Q: Does a Toll that lands on a corrupted slice of yours cost 2 RAM for the card but still drain only 1?
