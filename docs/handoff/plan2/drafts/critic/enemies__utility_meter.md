<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__utility_meter; status ok; tokens in 5514 cache-write 0 cache-read 32585 out 2149; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/utility_meter

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 structure.** The section contains two layouts. The first is a BLOCK layout followed by a "Decision... see below" that contradicts itself, then a "Fix" layout. Only one layout may stand. The first table's ticks sum to 6+4+5+5+4+6 = 30, but it carries the abandoned design.
2. **BLOCKER, R2/R3 arithmetic, §4.** The sustain is subtracted as 0.83 × 3.5 = 2.9. The raw budgets are 31.5 / 38.5 / 49 / 63. Subtracting 2.9 gives 28.6 / 35.6 / 46.1 / 60.1, but the table lists 30 / 38 / 48 / 60. T1, T2 and T3 do not follow the stated formula. The sustain is also not tier-scaled, although the text says "×tier". The figure is also wrong at its source: 5 % of 48 HP is 2.4, not 2.5, and rounding up to 3 HP breaks "percent amounts read max HP". T3 and T4 are in band (44-56 / 56-70). T1 (30) and T2 (38) are in band.
3. **MAJOR, intake §3.** Expected intake is computed with the resistance-1 tax and random landings, but the Surcharge bonus is stated as "~3" while the cap is +6 and the shield only reaches 6 after one Reserve landing. A single needle with a 6-tick Reserve (20 %) makes the average bonus much lower than 3. The Surcharge's tier factor on the bonus is unclear (the bonus is a derived value, so it should not be scaled again). T3 intake "4.6" uses ×1.69 on 2.7, which gives 4.56. That is acceptable, but T4 ×2.2 is never shown.
4. **MAJOR, R13/§2 mechanics.** Enemy SHIELD is a persistent buffer. It is capped at the player's `shield_cap` of 15, while open question 9 (enemy percent shields get their own cap) is unresolved. The draft also says "Reserve... FLAT × tier factor" for shield, which gives 6 × 1.3 = 7.8 at T2. The rider "max +6" is not tier-aware.
5. **MAJOR, N# tagging, §8.** `damage_per_owner_shield` is not an existing N20 rider (hits, hits_per_target_status, perfect_multiplier, pierce). It must be tagged "NEW: owner-shield damage rider", with N20 as the closest home. "SHIELD / N14" claims a fallback to the SANDBOX slice type, but the enum SANDBOX is the shield, so N14 is naming only. The N12 fallback contradicts itself ("Playable, weaker").
6. **MAJOR, design quality.** The "one question" is thin. The shield the Surcharge reads is capped at +6 and the Surcharge covers 4 of 30 ticks (13 %), so the bonus is rarely live. The Meter's real question reduces to "hit it". The Rebate is a sustain source, and the shield is a second defensive layer.
7. **NIT, §7.** "Hits Reserve with a burst" is garbled, because a Reserve landing is a slice, not a target. "SANDBOX" is described as a card, but the player's SANDBOX slice is a wheel slice. The weak-player lines are unclear.
8. **NIT, §10.** The wins quoted ("~98 %") are a guess with no reference. "R-question 9" is a wrong citation.

## Concrete fixes

- **§2:** delete the first layout and the "Decision / Fix" prose. Keep one table:

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Reserve (SANDBOX type) | 6 | +6 shield, FLAT × tier factor |
| 2 | Surcharge (SHIM) | 4 | 4 FLAT + 50 % of own shield, rider max +6, not rescaled |
| 3 | Rebate (HOTFIX) | 5 | heal 5 % max HP, PERCENT, no rounding up |
| 4 | Null | 5 | nothing |
| 5 | Reserve | 4 | +6 shield |
| 6 | Peak Rate (OVERFLOW) | 6 | 9 FLAT |

- **§4:** the sustain per turn is 5/30 × 5 % × HP × 3.5 turns. Show it per tier: T1 30 HP gives 0.25 per turn, so the budget is 31.5 − 0.9 = 30.6 → **30**. T2: 38.5 − 1.1 = 37.4 → **37**. T3: 49 − 1.4 = 47.6 → **48**. T4: 63 − 1.8 = 61.2 → **61**. Set `hp_by_tier` = [30, 37, 48, 61].
- **§3:** replace the sustain text with: the Rebate heals 5 % of max HP (1.5 / 1.9 / 2.4 / 3.1 HP), expected 0.17 × that per turn. At T3 that is 0.4 HP, and the cap of 30 % × 14 = 4.2 is met. Give intake for T1-T4 as 2.7 × [1, 1.3, 1.69, 2.2] = 2.7 / 3.5 / 4.6 / 5.9, using a bonus of ~2.
- **§8:** relabel the rider as "NEW: owner-shield damage rider (N20 family); fallback: Surcharge is plain SHIM 8". Change the N12 fallback to "all slices 5 ticks; the Surcharge gains a Perfect".

## Keep

- Intake is above zero and the sustain is a single bounded source. This fixes the old double-Hotfix flaw, and the "Delta vs today" section lists the changes clearly.
- The idea of a self-fed damage number is a good teaching hook.

## Q:

Q: Does the shield rider read the Meter's shield at resolve (after the defensive pass), so a Reserve landing never feeds a same-turn Surcharge with a single needle?
Q: Is a 13 % chance of landing a +6 bonus enough to ask a question, or should the Surcharge be larger or the Reserve adjacent to it?
