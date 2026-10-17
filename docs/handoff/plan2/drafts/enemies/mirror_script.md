<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__mirror_script; status ok; tokens in 16277 cache-write 0 cache-read 32007 out 2771; cost $0.033. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# mirror_script: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, rebel_cell. Appears in L1-2 as the teaching enemy for "your own wheel is a mirror": its needles read two slices at once, one safe and one dangerous, and you choose which.
- **The one question:** *"Two needles sit on tick 0 and tick 15. Which of them will you let land on the big hit?"* The wheel is a symmetric pair: every offensive slice has a defensive twin 15 ticks away. A 15-tick nudge or spin sends both needles to the twins. It's a puzzle in which the answer is to steer the pair of needles together.
- **Which answer shortens the fight:** forcing both needles onto the Null/Block axis and bursting while it is blanked. Turning a 3-turn fight into a 4-turn fight means you let the Overflow land.
- **Distinct from siblings:** Echo Process, Handler Proxy and Loyalty Test are not covered here. This one is the pure geometry enemy: no listeners, no statuses beyond one, no sustain.

## 2. Phase plan (1 phase, no thresholds)

| Field | Value |
|---|---|
| Phase | single (no floor, no threshold; R3 does not apply) |
| Needles | 2: ticks 0 and 15, FIXED (today's pair; R10 not needed) |
| Hub rule | none |
| Statuses | one: Citation → OUTPUT_DOWN ×1 (R8) replaces PARASITE |
| Listeners | none |

**Layout (sums to 30; size_ticks needs N12):** the opposite-needle design needs every slice's twin 15 ticks away, so the wheel is two matching halves of 15: 

| # | Slice | Ticks | Effect | Twin (+15) |
|---|---|---|---|---|
| 0 | Shim | 5 | 9 damage FLAT | slot 3 Block |
| 1 | Citation | 5 | OUTPUT_DOWN ×1 on 1 random non-NULL slice of yours (no damage) | slot 4 Null |
| 2 | Overflow | 5 | 16 damage FLAT | slot 5 Block |
| 3 | Block | 5 | BLOCK 6 FLAT | slot 0 Shim |
| 4 | Null | 5 | nothing | slot 1 Citation |
| 5 | Block | 5 | BLOCK 6 FLAT | slot 2 Overflow |

That is the same six 5-tick slices as today with the Solar Flare swapped for a second Block and the order rearranged so twins pair up (Shim/Block, Citation/Null, Overflow/Block). Because needles are 15 apart, any rest position reads one of three pairs: Shim+Block, Citation+Null, Overflow+Block. Only one needle is ever dangerous, so the question is "which pair": Overflow+Block is the only pair that hurts (16), Shim+Block is the mild one (9), and Citation+Null is the quiet one.

Sizes stay at 5 so the whole fight works with today's geometry: **no N12 needed**.

## 3. Sustain and intake
- **Sustain:** none (no heal, no regen). Block 6 is defense only and is wiped at turn start. Cap 30 % of 11 dpt = 3.3 per turn; actual 0.
- **Intake per turn at the reference player:** the three pairs are equally likely over a random respin; the player can steer. Expected unsteered:
  - Shim+Block: 9 × tier factor
  - Citation+Null: 0 damage, OUTPUT_DOWN ×1
  - Overflow+Block: 16
  - Unsteered mean ≈ (9 + 0 + 16) / 3 ≈ 8.3 at T1. With a reference player who steers away from Overflow half the time ≈ 5 per turn. Always above 0 (a Citation turn still costs 25 % output on one slice). Over a 3.5-turn fight ≈ 17 HP lost at T1, scaled ×1.0 / 1.3 / 1.69 / 2.2 for T1-T4.

## 4. HP by tier (R2)
Budget = reference_dpt[t] × 3.5 turns × needles hit. The player's hit lands on both enemy needles (pointer rule, 2 needles), but Block absorbs: expect ~65 % of nominal to go through on the Block-needle turns, so I use 1.0 effective needle plus a small bonus rather than 2×.

| Tier | dpt | Budget (×3.5) | hp_by_tier (band) |
|---|---|---|---|
| T1 | 9 | 31.5 | **34** (28-36) |
| T2 | 11 | 38.5 | **40** (34-44) |
| T3 | 14 | 49 | **50** (44-56) |
| T4 | 18 | 63 | **64** (56-70) |

Today's 50 is inside the T3 band; this gives it a real curve instead of a flat value.

## 5. Enrage
None (normal; R4).

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** reads the pair on turn start. If Overflow+Block, spend the free nudge or a spin to rotate to Citation+Null (a 10-tick shift moves both), then spends cards on bursts into the Block needle's turn only if the Block needle is facing a WEAK edge. On a Null+Citation turn, burst. Kills in 3 turns.
- **Weak player:** nudges 1 tick, wasting the free nudge (each slice is 5 wide so one tick rarely changes slice), and eats the Overflow. Also ignores Citation, then plays a Perfect-dependent card into an OUTPUT_DOWN slice.

## 8. Systems needed
- N8 (×N stacks) is wanted only for the Citation display; **fallback:** today's PARASITE (halves output) works unchanged as data. 
- N9 (OUTPUT_DOWN): same fallback.
- N1 amount modes: not needed, all FLAT.
- All other content: data-only. No new dependency is hard.

## 9. Delta vs today
- **Kept:** id, corporation, needles 0/15, Shim 9, Overflow 16, Defrag 6, Citation, Null, cycle_reward 15.
- **Changed:** Solar Flare removed (its OVERCLOCK-into-CORRUPTED chain becomes RAM-doubling under R9 and is too punishing for a normal); a second Defrag (BLOCK 6) added; layout reordered so each slice's twin sits 15 ticks away; hp 50 → hp_by_tier [34, 40, 50, 64]; Citation PARASITE → OUTPUT_DOWN ×1 when N9 lands.
- **heat_effects:** none exist; none added.

## 10. Predicted sim check (estimate; no baseline row, derived from the wheel)
- **Expected turns:** about 3.4 at the reference player at every tier (HP tracks dpt). Skill 1.0 about 2.6.
- **Win %:** T1 ≈ 99 %, T2 ≈ 98 %, T3 ≈ 95 %, T4 ≈ 90 %. Intake of ~5 per turn × 3.5 turns × 2.2 = ~38 HP at T4, survivable for a 45-60 HP operative but meaningful.
- No sustain, so the heal-turn criterion passes.

## 11. Q:
- Q: Is a 50/50 pair-of-needles read (only Overflow+Block is dangerous) enough of a question for L1-2, or should L1 drop Overflow to 12?
- Q: Should the second Defrag be BLOCK at all, or a SHIELD so a Perfect burst has to chew through something?
- Q: Does a WEAK landing on Citation still apply OUTPUT_DOWN (Q11 proposes yes)? If not, the pair's quiet turn is truly free.
- Q: Do we want to keep Solar Flare for L5-6 pressure only, as an optional variant slot?
