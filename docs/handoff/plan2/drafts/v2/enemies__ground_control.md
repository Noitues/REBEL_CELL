<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__ground_control; status ok; tokens in 6530 cache-write 0 cache-read 32585 out 4578; cost $0.033. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, layout and tick 0):** the layout now has an explicit origin. Slice 1 starts at tick 0, and tick 0 is the left edge of Slice 1 (the Shim). Boundaries are stated as cumulative sums, and the *centre tick* of each slice (R11: d = 0 → PERFECT) is stated as an integer. All sizes are chosen so every centre is a whole tick: 5, 3, 5 and 7 are odd and 4, 6 are even. For even sizes I give the pair of GOOD ticks and no Perfect. The needle now starts at tick 0, which is Slice 1's first sub-tick. The Null sits to its left, so a −1 nudge reads Null, which is a teaching beat. The v1 "boundaries at 0,5,10,13,18,22,30" line was also wrong (it listed 7 numbers for 6 slices with sizes that didn't match); it is replaced.
- **Issue 2 (BLOCKER, Defrag and the defense cap):** the "Defrag 8" ambiguity is fixed. The table now has a separate Size column (ticks) and a separate Amount column. Defense per turn is recomputed from the new layout, and the draft states that the 30 % cap applies to heal only. Block and shield are listed as defense and not compared to the cap.
- **Issue 3 (BLOCKER, intake math):** intake is recomputed per slice from its sub-tick map (R11), with one rule: WEAK reads 0.5×, GOOD and PERFECT read 1.0×. The irrelevant WEAK/GOOD map on the Null is removed. The result is one clean table.
- **Issue 4 (MAJOR, T4 win rate):** HP at T4 is 56 (band 56–70, bottom edge), the Overflow drops from 16 to 14, and the predicted T4 win is ≥ 90 %. The sim check is rewritten with the new intake.
- **Issue 5 (MAJOR, drift too small to be a puzzle):** kept the idea of orbit but redesigned the question. The drift is 2 ticks per turn but the start-of-turn respin randomizes the needle, so the drift only matters *within the turn it is previewed*. I changed the core question: the orbit applies at end of turn *before* resolve, so the needle that resolves is the settled position plus 2 (a 2-tick shift is bigger than the free nudge's 1). The player must nudge to where the needle will be *after* the drift. This makes the drift larger than the free nudge, so the preview and the resolved landing differ by design (preview shows the post-drift landing, so preview equals result). The "lap" claim is deleted.
- **Issue 6 (MAJOR, Freeze rule):** ruled in the draft: Freeze skips the respin; the orbit still applies. Q3 is closed (no longer asked).
- **Issue 7 (NIT):** N19 named for the turns metric. The N12 fallback is stated honestly with what it loses.
- **Critic's "Concrete fix" on 4/5/3/6/4/8:** **adopted** (4+5+3+6+4+8 = 30), with a reorder so the Overflow is not adjacent to the first Shim in a way that breaks the origin. Kept the rest.
- **Kept, because strong:** one needle, one dangerous narrow slice, a wide Null, zero sustain, positive intake at every tier, HP bands with arithmetic, an honest data-only fallback.

# ground_control: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3–4 turns, no enrage (R1, R4). Orbital Commons.
- **Layers:** L1–2 teaching (T1–T2 Routers) and L5–6 as a common pressure fight (T3–T4). The design is the same at every tier; only base numbers change (R2).
- **Concept:** a ground station tracking a satellite. Its needle **drifts 2 ticks at the end of each turn, before resolve** (`pointer_orbit_per_turn = 2`). The preview shows the post-drift landing, so what you see is what resolves.
- **The one question:** *"The drift moves its needle 2 ticks, more than your free nudge of 1. Where will it end up, and can you steer the one narrow Overflow off it?"*
- **What shortens the fight:** after the respin, read the post-drift landing, then spend the free nudge (plus a RAM nudge if needed) so the drifted needle reads the Null or a Shim you want to take, and strike the turns it is not on the Sandbox.
- **Distinct from siblings:** Weather Satellite and Orbital Debris lean on flares and orbit speed. This enemy teaches **reading a drift one step ahead with one needle and one dangerous slice**: no status, no parasite, no listener.

## 2. Phase plan
Single phase, no threshold, no HP floor (R3: the last phase has none). **No phase entries** on the `.tres`.

| Field | Value |
|---|---|
| Needles | 1, starts at tick 0 of the layout (the left edge of Slice 1), `ORBIT` 2 ticks per turn, applied before resolve |
| Hub rule | none |
| Statuses, parasites, listeners | none |

**Wheel layout (R11).** The layout starts at tick 0 in listed order; boundaries are cumulative.

| # | Slice | Ticks | Span | Centre / Perfect tick | Sub-tick map | Effect | Mode |
|---|---|---|---|---|---|---|---|
| 1 | Shim | 4 | 0–3 | none (even) | W G G W | Damage 10 | FLAT |
| 2 | Defrag → BLOCK | 5 | 4–8 | 6 | W G P G W | Block 8 | FLAT |
| 3 | Overflow | 3 | 9–11 | 10 | G P G | Damage 14 | FLAT |
| 4 | Shim | 6 | 12–17 | none (even) | W W G G W W | Damage 10 | FLAT |
| 5 | Sandbox → SHIELD | 4 | 18–21 | none (even) | W G G W | Shield 5 | FLAT |
| 6 | Null | 8 | 22–29 | none (even) | n/a | nothing | n/a |

4 + 5 + 3 + 6 + 4 + 8 = **30**. Boundaries: 0, 4, 9, 12, 18, 22, 30.

Notes on the design:
- Damage, block and shield amounts are FLAT × the tier damage factor (R2).
- The Overflow is 3 ticks (G P G), so it has **no WEAK landing**. Every read is full output, so it is a real spike to steer away from.
- The Null is 8 ticks wide: the safe harbour. Tick 0 sits next to it (tick 29 is Null), so a −1 nudge from the start reads Null.
- The Sandbox (4 ticks, no Perfect) is a small shield that never gates a kill.
- The Defrag is 5 ticks and 8 block; the "8" is the amount, not a size.

**Transition:** none (single phase).

## 3. Sustain and intake
- **Sustain:** none. Heal turns per fight: 0 (≤ 1 allowed). The 30 % cap (applies to heal) is not engaged.
- **Defense per turn (not sustain):** Defrag 5/30 × 8 + Sandbox 4/30 × 5 = 1.33 + 0.67 = **2.0 per turn** (before the tier factor; block and shield).
- **Intake per turn** at a random landing, one needle. WEAK reads 0.5×, GOOD and PERFECT 1.0×, so the full-output share of each slice is: Shim 4 → (2 + 2×0.5)/4 = 0.75; Shim 6 → (2 + 2 + 2×0.5)/6... Specifically W W G G W W has 2 G and 4 W: (2 + 4×0.5)/6 = 0.667; Overflow 1.0.
  - Shim (4 ticks): 4/30 × 10 × 0.75 = 1.00
  - Shim (6 ticks): 6/30 × 10 × 0.667 = 1.33
  - Overflow: 3/30 × 14 × 1.0 = 1.40
  - Base total = **3.73 per turn** (base factor).
  - × tier factor: **T1 3.7 · T2 4.9 · T3 6.3 · T4 8.2** (factors 1.0 / 1.3 / 1.69 / 2.2).
- Intake is > 0 at every tier. Over a 3.5-turn fight at T3 that is about 22 HP unsteered, near 0 when the needle is steered onto the Null.

## 4. HP by tier
Budget (R2): `reference_dpt_by_tier` × 3.5 turns × 1 needle, minus sustain (0).

| Tier | Ref dpt | Budget | Band (R2 normal) | **hp_by_tier** |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28–36 | **32** |
| T2 | 11 | 38.5 | 34–44 | **38** |
| T3 | 14 | 49 | 44–56 | **48** |
| T4 | 18 | 63 | 56–70 | **56** |

T4 is set at the band floor (56, not the 63 budget) because intake is 8.2 per turn and the class has no sustain; a shorter fight keeps the win rate at target. Today's flat 52 is replaced.

## 5. Enrage
**Off** (normal default, R4). The fight is 3–4 turns and the drift keeps the Overflow coming.

## 6. Buffs and counter Exploits
Not applicable (normals have none).

## 7. Counterplay
- **Good player:** after the respin, reads the post-drift landing in the preview, then nudges (free, plus one RAM nudge if needed) so the drifted needle reads the Null on the turn the Overflow would otherwise land, and strikes on turns the needle is not on the Sandbox. Kills in 3 turns taking about 0–8 damage.
- **Strong burst:** kills before the Sandbox matters; the 5-shield is too small to gate a kill.
- **Weak player:** nudges to where the needle *is*, not where it will be, so the drift carries it onto the Overflow (14 × factor, 24 at T3, with no WEAK discount). Also wastes a big hit into the Defrag's 8 block.
- **Freeze:** skips the enemy's start-of-turn respin; **the orbit still applies**. This is a teaching beat ("Freeze isn't a pause on drift").

## 8. Systems needed
| N# | Use | Fallback |
|---|---|---|
| N1 | Flat amounts × tier damage factor (slice scaling only, no hub) | Today's `output_scale` already scales slices; no loss |
| N2 | `hp_by_tier` | Single `hp = 48` with `enemy_scale` |
| N12 | `size_ticks` for the 4/3/6/4/8 slices and sub-tick maps | **Data-only fallback:** six 5-tick slices (today's wheel). Loses the Overflow with no WEAK, the wide Null and the even-size maps; acceptable at T1–T2 only |
| N19 | Turns-per-fight metric for the sim check | Read mean turns from the existing fight output |
| N14 | BLOCK / SHIELD display names | display strings only |

Orbit already exists (`pointer_orbit_per_turn`). N11 is not needed (the needle starts on tick 0).

## 9. Delta vs today
- **Kept:** id, corporation, `pointer_orbit_per_turn = 2`, the five slice types, `cycle_reward = 15`, one needle at tick 0, no hub rule.
- **Changed:** `hp` 52 → `hp_by_tier` [32, 38, 48, 56]; Overflow 16 → 14; slice order separated (Shim / Defrag / Overflow / Shim / Sandbox / Null); `size_ticks` 4/5/3/6/4/8 (needs N12).
- **Heat effects:** none authored today, none added.

## 10. Predicted sim check
No baseline row (the baseline is Solace-only), so this is an estimate from the wheel.
- **Turns:** 3.4 mean at the step-0 skill, p90 ≈ 5; about 2.8–3.0 at skill 1.0.
- **Win %:** T1 ≥ 98, T2 ≥ 97, T3 ≈ 95, T4 ≈ 90.
- **Why:** one needle and no sustain mean the fight length is HP ÷ damage. T3 intake is 6.3 per turn, about 22 HP over the fight, and T4 is 8.2 per turn against 56 HP, shorter than the 60 of v1 and with a lighter Overflow, so T4 now sits at the 90 % target and not below.

## 11. Q:
- Q: Is a 3-tick Overflow with no WEAK landing too punishing for T1 teaching? If so, widen it to 4 (G G, no Perfect) and take 1 tick from the Null.
- Q: Should the preview show only the post-drift landing, or also a faint ghost of the pre-drift tick?
- Q: Should the 5-shield get a PERCENT variant later, or stay FLAT on a normal?
