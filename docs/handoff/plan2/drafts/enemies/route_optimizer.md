<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__route_optimizer; status ok; tokens in 15659 cache-write 0 cache-read 32007 out 3140; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# route_optimizer: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, no enrage. **Corporation:** Meridian.
- **Layers:** L1-2 teaching (first Meridian enemy that shows "two needles read your wheel"), and a L5-6 pressure filler at T3-T4.
- **The one question:** *"Which of my two slices is under each needle, and can I make both read something harmless, or make my hit land on both?"* The Route Optimizer has two needles 15 ticks apart, so its one attack hits twice. The fight is about the **pointer rule (GDD 2.7)**: your own hits land once per needle, so every Shim you land hits twice.
- **Shortening answer:** line your best slice up at both needles. The wheel is 3-fold symmetric by design: the same attack (Shim) sits at opposite positions, so one nudge puts two Shims under the needles and doubles your damage. Anyone who finds the "both needles on Shim" alignment ends the fight in 3 turns. Anyone who ignores it takes a 14 Overflow and a Shim at once.

## 2. Phase plan (single phase, no threshold)

| Field | Value |
|---|---|
| Phase | 1 "Route Plan" (100 % → 0 %, no floor) |
| Needles | 2, ticks **0 and 15** (even, FIXED; no Multiply/Orbit). Pointer ticks stay on multiples of 5 so the data-only layout works |
| Hub rule | none |
| Statuses/parasites/listeners | none |

**Layout (6 slices × 5 ticks = 30, today's geometry, reordered so the needles at 0 and 15 sit on slices 0 and 3):**

| Slot | Centre tick | Size | Slice | Effect (FLAT, × tier damage factor per R2) |
|---|---|---|---|---|
| 0 | 0 | 5 | Shim 8 | 8 damage |
| 1 | 5 | 5 | Null | nothing |
| 2 | 10 | 5 | Overflow 14 | 14 damage |
| 3 | 15 | 5 | Shim 8 | 8 damage |
| 4 | 20 | 5 | Defrag 5 | BLOCK 5 FLAT |
| 5 | 25 | 5 | Shim 8 | 8 damage |

Reasoning: needles at 0 and 15 sit 3 slices apart, so the pair always reads slot *i* and slot *i+3*. The pairs, rotating by slice:
- (0,3) Shim + Shim = 16 damage
- (1,4) Null + Defrag = harmless, gain 5 BLOCK
- (2,5) Overflow + Shim = **22 damage** (the danger pair)
- (3,0) Shim + Shim = 16
- (4,1) Defrag + Null = 5 BLOCK
- (5,2) Shim + Overflow = 22

So the six alignments give: two safe/idle, two at 16, two at 22. The enemy wheel respins randomly each turn, so this is a known distribution the preview shows. The 22 pair is the threat; the Null/Defrag pair is the opening. The player's nudges move *their* wheel, but a 1-tick nudge of an **enemy** wheel (Jam/Strip/Freeze/Spin cards) shifts a Perfect/Good/WEAK reading: pushing a needle to the WEAK edge halves that hit.

Change vs today: Overflow and its Shim neighbour were adjacent at slots 2-3, which put a 22 pair at needle spacing 15 only for part of the rotation. The new order makes the pair table clean (2 × 22, 2 × 16, 2 × idle) and every alignment readable.

## 3. Sustain and intake
- **Sustain:** none (no heal, no hub). Only BLOCK 5 on the Defrag, which the player's own damage pays for. Block is not heal; at T1 it absorbs 5 of about 31 per-turn hits, well under the 30 % cap (30 % × 9 = 2.7 heal/turn is the cap, and heal is 0).
- **Intake per turn (reference player, first-pass estimate, no baseline row):** expected damage per resolve at T1, averaged over six alignments: (0 + 0 + 16 + 16 + 22 + 22)/6 ≈ **12.7 raw**, with the two Defrag/Null pairs at 0. The reference player steers away from the 22 pair with the free nudge about half the time: ≈ **8-10 per turn** at T1 (×1.3 / ×1.69 / ×2.2 at T2-T4 per `enemy_damage_by_tier`). Clearly above 0. Over 3.5 turns, about 30 damage at T1 against a 60 HP operative, which is a real but safe cost.

## 4. HP by tier (R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70)
Budget = `reference_dpt_by_tier[t]` × 3.5 × needles my hits land on (my hit lands on each of the enemy's needles, so ×2 when aligned, but the reference player aligns only half the time, so I use an effective ×1.5 here), minus sustain (0).
- T1: 9 × 3.5 = 31.5 → **HP 32** (ignoring the pointer bonus; the needle bonus is added back below)
- T2: 11 × 3.5 = 38.5 → **HP 40**
- T3: 14 × 3.5 = 49 → **HP 50**
- T4: 18 × 3.5 = 63 → **HP 64**

The pointer rule gives a 2-needle phase proportionally more HP (R2 note). R2's bands already assume 1 needle; for 2 needles the value would be 1.5×, taking T1 to 47, far beyond the band. **Choice:** stay at the top of the band rather than scale it, because the reference damage is measured on a typical wheel where the needle count is part of what the player faces and the band says "28-36"; the extra needle is offset by the layout, whose Null and Defrag slices make about a third of the alignments non-damaging for the player's attack to dodge (they still hit the enemy normally). So: **T1 34, T2 42, T3 54, T4 68** (upper band edges, giving the 2-needle bonus without leaving the band). Current 48 HP is above T1's band.

## 5. Enrage
None (normal class, R4). A 3-4 turn fight has no stall problem.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** read the six-pair table in the preview, use the free nudge to move the needles off the Overflow (22) pair onto the Defrag/Null pair, then put their strongest slice at both needles (the pair is 15 ticks apart, so an Overflow-Shim-style player wheel with a 3-fold repeat gets a double hit). Finish in 3 turns.
- **Weak player:** nudges toward a Perfect on the first needle without looking at the second, and lands the 22 pair. Wastes nudges chasing a Perfect on a Null. Takes about 4 turns and 35-40 damage at T1.

## 8. Systems needed
- N2 (`hp_by_tier`, `enemy_damage_by_tier`) for the numbers. **Fallback:** the single `hp` field set to the T1 value (34) with the global damage scale; no new mechanic is needed.
- N1 (amount modes): Defrag is FLAT, which is today's default; nothing new.
- Everything else (two pointers at 0 and 15, six 5-tick slices) is existing data.

## 9. Delta vs today
- **HP:** 48 → 34 / 42 / 54 / 68 by tier (`hp_by_tier`).
- **Layout:** slot order Shim, Shim, Overflow, Defrag, Shim, Null → Shim, Null, Overflow, Shim, Defrag, Shim. The same slices are kept, nothing new is authored.
- **Kept:** pointer ticks (0, 15), `cycle_reward` 15, id, description.
- **heat_effects:** none exist; none added.

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only); estimate from the wheel. Expect mean ~3.4 turns at the reference skill, p90 ≤ 5. Win rates: T1 ≈ 98 %, T2 ≈ 96 %, T3 ≈ 92 %, T4 ≈ 88 %. The T4 figure falls a little below the 90 % target only because the 22 × 2.2 ≈ 48 pair is lethal to a 45-50 HP operative if it lands twice in a row, so a T4 retune may pull the Overflow to 12.

## 11. Q:
- Q: Should a 2-needle normal get HP above the 1-needle band (the pointer rule) or stay inside it as proposed?
- Q: Should the Overflow keep a 14 base at T4, where the pair hits for about 48, or should a normal's biggest hit be capped?
- Q: Is a Meridian L1-2 teacher with two needles too hard for a first fight; should Customs Scanner own that role instead?
