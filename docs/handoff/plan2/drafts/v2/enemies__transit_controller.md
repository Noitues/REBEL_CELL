<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__transit_controller; status ok; tokens in 7671 cache-write 0 cache-read 32585 out 8414; cost $0.053. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **#1 / triage BLOCKER 1 (Defrag value):** one value everywhere, **Defrag = 5 BLOCK FLAT**. The §2 table, §3 and §9 all say 5. The "read the row as 5" sentence is deleted. Today's value is 6, so the delta is 6 → 5.
- **#2 / triage BLOCKER 2 (centre ticks):** §2 now lists cumulative-midpoint centres and the sub-tick map for every slice.
  - Centres: Shim 2, Defrag 8, Shim 13.5 (no centre tick), Overflow 17, Shim 21, Null 26.5.
  - Re-check of v1's tier labels: the Overflow's 3-tick window is G P G, so **both Good and Perfect output 1.0×** and it has no WEAK tick. v1's "a 1-tick nudge turns the Overflow into WEAK" was wrong. A nudge only helps when it carries the needle *off* the slice.
- **#3 / triage BLOCKER 3 (sustain):** BLOCK is recomputed from the sub-tick output map (expected output 5/30 of the Defrag's ticks, not 0.23 × 0.83) and multiplied by the tier factor. It is shown at all four tiers and compared with 30 % of the reference dpt, including T4 (18 → cap 5.4).
- **#4 (HP budget):** sustain is now subtracted per R2.
  - The budget lands below the band floor at every tier, so `hp_by_tier` is the band floor (28/34/44/56). The band wins and this is stated. Resulting fight lengths are shown.
- **#5 (intake):** recomputed from the sub-tick map. The nudge effect is stated explicitly: one free nudge per turn, shared with the player's own wheel.
- **#6 (respin vs orbit):** the fabricated turn-by-turn tick table is removed. Reads are relative: the needles are always 12 ticks apart on a wheel that respins every turn, and the orbit +1 is shown by the trail. A pair-coupling table replaces the old table.
- **#7 (counterplay):** rewritten. The enemy wheel can be nudged (free nudge once per turn, then 1 RAM). A nudge on the enemy wheel moves *both* needles. The contradictory "burst on turns 2-3" line is removed.
- **#8 (nits):** the sibling claims are cut down to what is defensible. The answerable Qs are removed.
- **#9 (T4 win %):** Shim 6 → 5 and Overflow 14 → 12 lower intake. HP sits at the band floor. The predicted T3/T4 win rates are now ≥ 90 %.

# transit_controller: direct design

## 1. Identity & the one question

- **Class:** Normal, 1 phase, 3-4 turns, no enrage.
- **Corporation:** Halcyon Civic (transit signal control).
- **Layers:** L1-2 teaching of "two needles on one wheel". It may appear at L5-6 at T3-T4, where the tier numbers carry the pressure.
- **Working concept:** "Linked signals." Two needles sit 12 ticks apart on one wheel, so they are *coupled*: wherever one reads, the other reads the slice 12 ticks away.
- **The one question:** "After the respin, which slice is under each needle, and is my one free nudge better spent shifting *both* needles on its wheel, or on my own wheel?"
- **What shortens the fight:**
  - Spend the nudge to take the Overflow off its edge (or off the wheel's strong slices) so that only a Null or WEAK read remains.
  - Bring burst while a needle sits on the Defrag's WEAK ticks, so the block is small.
- **Distinct from siblings:** it is the only Halcyon normal whose question is two coupled needles on an uneven pair. It has no statuses and no heal.

## 2. Phase plan

Single phase, no threshold, no floor (R3 moot).

| Item | Value |
|---|---|
| Needles | 2 at ticks 0 and 12 on the wheel (uneven, R10) |
| Pointer behavior | ORBIT +1 per turn, as today. The trail shows the tick each needle resolves on, so preview = result |
| Hub rule / statuses / parasites / listeners | none |
| Heal | none |

**Layout (sum 30), clockwise from tick 0:**

| # | Slice | Ticks | Range | Centre | Sub-tick map | Effect | Mode |
|---|---|---|---|---|---|---|---|
| 1 | Shim | 5 | 0-4 | 2 | W G P G W | 5 damage | FLAT |
| 2 | Defrag | 7 | 5-11 | 8 | W W G P G W W | 5 BLOCK | FLAT |
| 3 | Shim | 4 | 12-15 | 13.5 | W G G W | 5 damage | FLAT |
| 4 | Overflow | 3 | 16-18 | 17 | G P G | 12 damage | FLAT |
| 5 | Shim | 5 | 19-23 | 21 | W G P G W | 5 damage | FLAT |
| 6 | Null | 6 | 24-29 | 26.5 | W W G G W W | none | n/a |

Sum: 5+7+4+3+5+6 = 30.

**Reading the wheel.** The wheel respins at turn start, so the needles' positions are random each turn. What is fixed is the coupling. Let A be the tick under the first needle; B is at A+12.
- **Overflow under B** (A in 4-6): A reads Shim 1's edge (4, WEAK) or the Defrag (5-6). The Overflow never pairs with a strong Shim.
- **Overflow under A** (A in 16-18): B reads Null (28, 29) or Shim 1's WEAK tick 0.
- **A on Defrag centre (8):** B is at 20, Shim 5 Good.
- **A on Null (24-29):** B is at 6-11, on the Defrag.

The orbit adds a known +1, shown by the trail. The player always sees the exact resolve ticks, then chooses a nudge.

**Transition:** none.

## 3. Sustain and intake

**Sustain: one source, the Defrag BLOCK. There is no heal.**
- Expected Defrag output per needle per turn: sub-tick outputs (0.5, 0.5, 1, 1, 1, 0.5, 0.5) sum to 5.0 over 30 ticks, so 5.0/30 = 0.167 per needle.
- Two needles × 0.167 × 5 BLOCK = 1.67 base, × tier factor [1.0, 1.3, 1.69, 2.2]:

| Tier | BLOCK/turn | Reference dpt | Share | Cap (30 %) |
|---|---|---|---|---|
| T1 | 1.67 | 9 | 18.5 % | 2.7 |
| T2 | 2.17 | 11 | 19.7 % | 3.3 |
| T3 | 2.82 | 14 | 20.1 % | 4.2 |
| T4 | 3.67 | 18 | 20.4 % | 5.4 |

Passes at every tier, including T4 (3.67 < 5.4).

**Intake** (damage to the player per turn, T1 base):
- Per needle: Shim 5 with outputs (4 + 3 + 4)/30 = 11/30 of ticks at full value → 11/30 × 5 = 1.83. Overflow 3/30 × 12 = 1.20. Total 3.03.
- Two needles: **6.1 per turn before any nudge**.
- The free nudge is shared with the player's own wheel. An enemy-wheel nudge shifts both needles together and removes about a quarter of the expected damage when used well. So **~4.6 per turn at T1**, above 0.
- ×1.3 / ×1.69 / ×2.2 gives ≈ 6.0 / 7.8 / 10.1 at T2 / T3 / T4.

*Assumption:* enemy BLOCK stays up during the player phase, as it does for today's Defrag enemies.

## 4. HP by tier

Budget (R2) = reference dpt × 3.5 − sustain × 3.5. One player pointer on this wheel, so ×1.

| Tier | dpt × 3.5 | − sustain × 3.5 | Budget | Band | `hp_by_tier` | Turns = HP/(dpt − sustain) |
|---|---|---|---|---|---|---|
| T1 | 31.5 | 5.8 | 25.7 | 28-36 | **28** | 28/7.33 = 3.8 |
| T2 | 38.5 | 7.6 | 30.9 | 34-44 | **34** | 34/8.83 = 3.9 |
| T3 | 49.0 | 9.9 | 39.1 | 44-56 | **44** | 44/11.18 = 3.9 |
| T4 | 63.0 | 12.8 | 50.2 | 56-70 | **56** | 56/14.33 = 3.9 |

The budget falls below the band at every tier, so the band floor binds. The floor already leaves room for the BLOCK. Today's flat 50 HP is replaced.

## 5. Enrage

None. Normal class default is off, and a 3-4 turn fight never gets there.

## 6. Buffs and counter Exploits

Not applicable (not a boss).

## 7. Counterplay

- **Good player:**
  - After the respin, reads both needles and the trail.
  - If a needle sits on the Overflow's edge (16 or 18), spends the free nudge on the enemy wheel to push both needles one tick. The Overflow read drops to a WEAK Shim edge, from 12 to ~2.5. It checks that the second needle doesn't move onto a worse slice, using the coupling table.
  - If no Overflow is in play, spends the free nudge on its own wheel as normal.
  - Bursts on turns when a needle reads the Defrag's WEAK edge, so the block is half value.
  - Finishes in 3-4 turns.
- **Weak player:**
  - Watches one needle only and misses the second needle's coupled read.
  - Nudges an Overflow read at tick 17 by one tick. That still lands on the slice, so the full 12 stays.
  - Pays 1 RAM per extra enemy-wheel nudge and runs short.
  - Plays damage into a Defrag Perfect and sees the block eat it, stretching the fight to 5+ turns.

## 8. Systems needed

| N# | Need | Fallback |
|---|---|---|
| N11 pointers on any tick | Needles 0 / 12 (uneven) | Keep 0 / 15; the Overflow/Defrag coupling table changes but still works |
| N12 variable slice sizes | 5/7/4/3/5/6 layout with sub-tick maps | Six 5-tick slices; the narrow Overflow window is lost |
| N2 `hp_by_tier`, `enemy_damage_by_tier` | HP and flat amounts by tier | Single `hp`, today's scale |
| N1 amount modes | FLAT × tier factor | Current behavior |

Data-only fallback: six 5-tick slices, needles 0 / 15, single HP. It works today with a weaker question. The new slice files are `shim_5`, `defrag_5` and `overflow_12`.

## 9. Delta vs today

- **Changed:**
  - Needles 0 / 15 → 0 / 12.
  - Layout from six 5-tick slices → 5/7/4/3/5/6.
  - Shim 8 → 5, Defrag 6 → 5, Overflow 14 → 12.
  - HP 50 flat → 28 / 34 / 44 / 56.
- **Kept:** orbit +1, the two-needle theme, the Null slice, `cycle_reward` 15, the Halcyon entry.
- **heat_effects:** none exist on this enemy and none are added.

## 10. Predicted sim check

No baseline row exists (the sweep covered Solace only), so these are estimates from the wheel.

| Tier | Mean turns | Win % | Reason |
|---|---|---|---|
| T1 | ~3.8 | ~98 % | 28 HP; intake 4.6 × 3.8 ≈ 17 damage |
| T2 | ~3.9 | ~97 % | Intake ≈ 6.0 per turn, ~23 total |
| T3 | ~3.9 | ~93 % | Intake ≈ 7.8 per turn, ~30 total |
| T4 | ~3.9 | ~91 % | Intake ≈ 10.1 per turn, ~39 total; the Overflow is the main risk |

Expected p90 turns ≈ 5.

## 11. Open questions

Q: The wheel respins each turn, so the orbit +1 is only a small known shift. Keep it, or drop ORBIT and use two fixed needles at 0 / 12?
Q: Should the 7-tick Defrag author a `tick_quality` such as W W W P W W W so the block's Perfect is rarer?
Q: Is the Overflow's 12 at T4 (12 × 2.2 = 26) too punishing, or should it use a PERCENT amount?
