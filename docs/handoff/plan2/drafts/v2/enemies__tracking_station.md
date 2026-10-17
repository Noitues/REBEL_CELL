<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__tracking_station; status ok; tokens in 6457 cache-write 0 cache-read 32585 out 12301; cost $0.071. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, geometry):** I re-derived the layout tick by tick and found the v1 claim "no rotation where both needles are harmless" was false. With v1's order (Dish 14-17, Null 24-29), rotations 14-17 read Dish + Null, a fully harmless pair. I reordered the layout so the Null (6) and Dish (4) sit adjacent, and §2 now shows the per-tick table and the min-damage proof. The stray "6.5→" fragment is gone. The "Ping WEAK edge" claim is replaced by the exact tick list.
- **Issue 2 (BLOCKER, Flare target):** Flare's effect is now exact. It applies in the statuses pass to the player's slice under the player's own pointer, after that slice has resolved. It is not tied to which enemy needle read it, and it applies once per Flare read.
- **Issue 3 (BLOCKER, intake):** Recomputed with WEAK at 0.5× (v1 forgot the halving: 120 became 91). Base unsteered intake is 6.07 per turn, scaled by 1.0 / 1.3 / 1.69 / 2.2. The free-nudge minimum is computed over all 30 rotations. §10 is redone from these numbers.
- **Issue 4 (MAJOR, sustain):** Now stated as "0 %, no heal source".
- **Issue 5 (MAJOR, HP budget):** The pseudo-derivation is dropped. The R2 normal band applies with no needle multiplier. I chose the upper part of the band because the two needles let the player's pointer attack land twice. HP is now 34 / 42 / 54 / 68, and Q1 asks the designer to confirm.
- **Issue 6 (MAJOR, fallback):** OVERCLOCKED is removed. The fallback is the existing PARASITE status, which is a 2-stack OUTPUT_DOWN (−50 %), harsher than one stack.
- **Issue 7 (NIT, layers and filler):** Layers are now L1-2 teaching, and the siblings paragraph is cut.
- **Critic Q (TIER_DOWN):** Kept OUTPUT_DOWN, because it is a plain number the player can read. TIER_DOWN stays as an alternative in Q3.
- **Critic Q (Lock-On cut):** Not applied. At T3 the reference-player intake is about 8 per turn over about 3.8 turns, which clears the 90 % target. The Lock-On 12 → 10 cut is kept as a T4 sim-gated option.

# tracking_station: direct design

## 1. Identity & the one question

- **Class:** Normal, 1 phase, 3-4 turns, no enrage.
- **Corporation:** Orbital Commons.
- **Layers:** L1-2 teaching. It is the first enemy that makes the player read two uneven needles. Higher campaign tiers raise its numbers only.
- **Concept:** a ground tracking dish with two readers set 11 ticks apart (0 / 11), so you cannot park both needles on harmless slices.
- **The one question:** "Which needle do I let hurt me this turn, and do I take the damage or the Flare?"
- **Shortcut answer:** use the free nudge to move the pair onto a Ping weak edge plus Null or Dish, away from the Flare. Your own hits land on both needles (pointer rule, GDD 2.7), so the fight ends in about 3-4 turns.

## 2. Phase plan (single phase)

| Field | Value |
|---|---|
| Threshold | none (single phase, no floor) |
| Needles | 2 at ticks **0 and 11** (R10, N11), FIXED |
| Hub | none |
| Statuses | OUTPUT_DOWN ×1 (N8/N9) from Flare |
| Listeners | none |

**Layout, clockwise from tick 0 (sizes sum 30):**

| # | Slice | Ticks | Size | Effect | Mode |
|---|---|---|---|---|---|
| 1 | Ping (Shim) A | 0-3 | 4 | 5 damage; map W G G W (no Perfect) | FLAT |
| 2 | Lock-On (Overflow) | 4-8 | 5 | 12 damage; W G P G W | FLAT |
| 3 | Solar Flare | 9-13 | 5 | 2 damage, then OUTPUT_DOWN ×1 (−25 % output) on the player's slice under the player's own pointer, applied in the statuses pass after that slice resolves; W G P G W | FLAT |
| 4 | Ping (Shim) B | 14-19 | 6 | 5 damage; W W G G W W | FLAT |
| 5 | Null | 20-25 | 6 | none | n/a |
| 6 | Shield Dish (Defrag) | 26-29 | 4 | 6 BLOCK; W G G W | FLAT |

Sum: 4+5+5+6+6+4 = 30. WEAK landings output 0.5×, and the Flare applies its status on any landing (Q4).

**Geometry proof.** At rotation r, needle A reads tick r and needle B reads tick (r+11) mod 30. Base damage per tick at T1 (Ping G 5 / W 2.5, Lock-On 12 / W 6, Flare 2 / W 1 plus status, Dish and Null 0):

| Ticks | 0-3 | 4-8 | 9-13 | 14-19 | 20-29 |
|---|---|---|---|---|---|
| Damage | 2.5, 5, 5, 2.5 | 6, 12, 12, 12, 6 | 1, 2, 2, 2, 1 (S) | 2.5, 2.5, 5, 5, 2.5, 2.5 | 0 |

- The two harmless zones, Null (20-25) and Dish (26-29), are contiguous (20-29). Needles 11 apart cannot both sit in a 10-tick run. If A is in 20-29, B reads ticks 1-10 (Ping, Lock-On or Flare). If B is in 20-29, A reads ticks 9-18 (Flare or Ping).
- The full per-rotation sum of both needles is 182 over 30 rotations (mean 6.07). Rotation 6 (Lock-On Perfect + Ping B G) costs 17. Rotation 14 (Ping W + Null) costs 2.5 with no status.
- No rotation costs 0. The cheapest clean pairs (no Flare) are r14, r15, r18 and r22, at 2.5 each. Cheaper pairs (1-2 damage) exist but read the Flare, so they trade damage for the status. That is the question.

## 3. Sustain and intake

**Sustain:** none. The Dish is BLOCK only, a defense and not a heal. That is 0 % of reference damage, well under the 30 % cap.

**Intake per turn** (base 6.07 unsteered, times the enemy damage factor; the Flare status is a separate cost):

| Tier | Factor | Unsteered | Best with free nudge (mean over r±1 min = 3.77 base) |
|---|---|---|---|
| T1 | 1.0 | 6.1 | 3.8 |
| T2 | 1.3 | 7.9 | 4.9 |
| T3 | 1.69 | 10.3 | 6.4 |
| T4 | 2.2 | 13.4 | 8.3 |

The reference player lands between the two columns (about 4.9 / 6.4 / 8.3 / 10.8). The floor is above 0: the minimum over any three adjacent rotations is at least 1 base, and it comes with the Flare status. The Dish's 6 BLOCK is not counted, so real intake is a little lower.

## 4. HP by tier

R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. A 1-phase normal's band applies as written, with no needle multiplier. I take the upper part of the band because the player's pointer attack lands on both enemy needles.

| Tier | `hp_by_tier` | Band | Turns at reference dpt (9 / 11 / 14 / 18) |
|---|---|---|---|
| T1 | 34 | 28-36 | 3.8 |
| T2 | 42 | 34-44 | 3.8 |
| T3 | 54 | 44-56 | 3.9 |
| T4 | 68 | 56-70 | 3.8 |

## 5. Enrage

None (normal class, R4). It has no sustain and the fight is short, so there is nothing to stall.

## 6. Buffs and counter Exploits

Not applicable (normal class).

## 7. Counterplay

- **Good player:** read both needles on turn 1. Spend the free nudge to reach a clean cheap pair (r14, r15, r18 or r22), keeping the Flare off or on a slice you don't care about. If the Flare cannot be avoided, put a Cleanse or ENCRYPT on the slice at your pointer; ENCRYPTED absorbs the status. Use a card that makes both of your hits land and finish in 3-4 turns.
- **Weak player:** fixes only the Lock-On needle and lets the Flare tag the slice at their pointer, so that slice is at −25 % output on its next landing. Or burns RAM on extra nudges for a Perfect and drops into a high-damage rotation (r5-r7, r24-r26).

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Variable slice sizes 4 / 5 / 6 | N12 | Six 5-tick slices (today's wheel). Loses the 4-tick no-Perfect Ping and the geometry proof above |
| Needles at 0 / 11 | N11 | Today's 0 / 15. Loses the core of the design |
| `hp_by_tier`, damage table | N2 | Keep a single `hp` of 54 |
| OUTPUT_DOWN ×1 | N8 / N9 | The PARASITE status (data-only, exists today) is a 2-stack OUTPUT_DOWN, harsher at −50 %. Drop the Flare damage to compensate |
| Flat × tier damage factor | N1 | Keep flat numbers unscaled |

## 9. Delta vs today

- **Kept:** id, two needles, the Flare, `cycle_reward` 15.
- **Changed:**
  - Needles 0 / 15 → 0 / 11.
  - Layout from today's six 5-tick slices to the six uneven slices above.
  - Overflow 16 → Lock-On 12.
  - Shim 8 → Ping 5.
  - Flare gains 2 damage and OUTPUT_DOWN, and one Defrag becomes the Dish.
  - HP 48 → [34, 42, 54, 68].
- **Heat effects:** none exist and none are added.

## 10. Predicted sim check

No baseline row exists, so this is estimated from the wheel.

- **Expected turns:** about 3.4 at T1-T2, 3.6 at T3, 3.8 at T4.
- **Win %:** T1 ~99 %, T2 ~98 %, T3 ~94 %, T4 ~88 %.
- **Why:** at T3 the reference intake is about 8 per turn over 3.6 turns, roughly 29 HP, which a 55-60 HP operative absorbs. At T4 it is about 10.8 × 3.8 ≈ 41 HP, so the 90 % target is borderline. If the sim shows T4 under 90 %, cut Lock-On to 10 (T4 only).

## 11. Open questions

Q: Does the player's hit really land once per enemy needle, so two needles means two hits? If it does, should HP drop to mid-band, or keep the upper band to hold 3-4 turns?
Q: Is an 11-tick needle gap readable on the HUD (the N11 risk), or should it be at least 12?
Q: Should the Flare use TIER_DOWN ("tracking loses precision") instead of OUTPUT_DOWN ×1?
Q: May the Flare apply its status on a WEAK landing (Q11 proposal: yes)?
Q: If T4 sim win is under 90 %, cut Lock-On to 10 at T4 only, or lower T4 HP?
