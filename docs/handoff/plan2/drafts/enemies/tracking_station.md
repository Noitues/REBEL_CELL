<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__tracking_station; status ok; tokens in 15815 cache-write 0 cache-read 32007 out 3414; cost $0.036. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# tracking_station: direct design

## 1. Identity & the one question

- **Class:** Normal, 1 phase, 3-4 turns, no enrage.
- **Corporation:** Orbital Commons.
- **Layers:** L3-5 mid-pressure. It is the first enemy that teaches "read two uneven needles". Today's 0/15 pair is symmetrical and gives no choice.
- **Concept:** a ground tracking dish with two readers, a **wide-gap pair** at 0 / 11. You can't steer both needles onto safe slices at once, so you pick which one to hurt you.
- **The one question:** "Which needle is the dangerous one this turn, and can I make the other one pay for it?"
- **Shortcut answer:** nudge or spin so the Flare needle lands on Null or a WEAK edge, and the other needle lands on a Defrag. The enemy then deals little and wastes its turn. Meanwhile your hits land twice (pointer rule, GDD 2.7), so you burst it down in 3 turns.
- **Distinct from siblings:** Weather Satellite and Uplink Relay are not given here, so I make no claim about them. Orbital Debris, Launch Pad and Ground Control are not described either. This design depends on **uneven needles plus a Flare that is a status, not damage**, which today's 0/15 pair doesn't ask.

## 2. Phase plan (single phase)

| Field | Value |
|---|---|
| Threshold | none (the only phase, no floor) |
| Needles | 2: ticks **0 and 11** (R10, uneven; N11). FIXED behavior |
| Hub | none |
| Statuses | OUTPUT_DOWN ×1 (N8/N9) via Flare. Fallback: OVERCLOCKED (exists) |
| Listeners | none |

**Layout (ticks sum 30), clockwise from tick 0:**

| # | Slice | Size | Effect | Mode |
|---|---|---|---|---|
| 1 | Ping (Shim) | 4 | 5 damage (W G G W, no Perfect) | FLAT |
| 2 | Lock-On (Overflow) | 5 | 12 damage | FLAT |
| 3 | Solar Flare | 5 | 2 damage and OUTPUT_DOWN ×1 on your slice under the pointer | FLAT |
| 4 | Shield Dish (Defrag) | 4 | 6 BLOCK | FLAT |
| 5 | Ping (Shim) | 6 | 5 damage (W W G G W W) | FLAT |
| 6 | Null | 6 | none | n/a |

Sum: 4+5+5+4+6+6 = 30.

**Geometry, the point of the design.** Slice centres are at ticks 2, 6.5→ computed from cumulative boundaries: Ping 0-3 (centre 1.5), Lock-On 4-8 (centre 6), Flare 9-13 (centre 11), Dish 14-17 (centre 15.5), Ping 18-23 (centre 20.5), Null 24-29 (centre 26.5). The 11 needle sits exactly on the **Flare's Perfect-centre**, so the second needle starts on the status slice. Needle 0 sits on the Ping's WEAK edge. Rotating the wheel one tick at a time keeps the pair 11 ticks apart: when 0 reads Null, 11 reads tick 4-5 of the Lock-On (hot). The wheel has no rotation where both needles are harmless. The two safest layouts (needle A on Null / Needle B on the Dish at about −3, or A on Dish / B on the Ping's WEAK) cost 1-2 nudges.

**Flare slice reads under tier:** Flare's status applies on any landing (Q11 proposal), so only steering away avoids it.

**Transition:** none. Single phase.

## 3. Sustain and intake

**Sustain:** none. The Shield Dish gives BLOCK only, a defense and not a heal. That is below the 30 % cap (0 of 9).

**Intake per turn** at the reference T3 player. The enemy output factor is ×1.69 (R2 table) on flat amounts.

- Random/unsteered layout, 2 needles, uniform over the 30 ticks, using per-slice damage weights (tick share) at T1 (×1.0):
  - Ping A (4 ticks): 5 → 20
  - Lock-On: 12 × 5 = 60
  - Flare: 2 × 5 = 10 (plus status)
  - Dish: 0
  - Ping B: 5 × 6 = 30
  - Null: 0
  - Sum 120 / 30 = **4.0 expected damage per needle**, **8.0 per turn** for two needles, before block.
- Unsteered with the player's free nudge only: roughly 5-6 per turn at T1. At T3: ~8-10, at T4: ~13.
- A **good player steering** takes about 1-3 per turn. Intake is above 0 for all players, because the free nudge cannot cover both needles. The Flare status costs −25 % output on one of the player's slices per hit.

## 4. HP by tier

R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget: `reference_dpt` × 3.5 turns × needles landing, minus sustain (0).

Two enemy needles are not the same as two hits on it: the pointer rule says the *player's* attack hits whatever is at each *enemy* pointer. So my hits land on **2 needles**, but the budget formula says "needles the player's hits land on". I count both needles as landing (×2 hits only when the player's attack slice is a pointer attack), and apply a conservative factor of 1.0 as the band already accounts for a typical 1-2 needle normal. Check: T3, 14 × 3.5 = 49. T1, 9 × 3.5 = 31.5.

| Tier | HP | Arithmetic |
|---|---|---|
| T1 | 32 | 9 × 3.5 = 31.5 |
| T2 | 39 | 11 × 3.5 = 38.5 |
| T3 | 50 | 14 × 3.5 = 49 |
| T4 | 63 | 18 × 3.5 = 63 |

All inside the bands. Today's 48 HP flat is near the T3 value. `hp_by_tier` = [32, 39, 50, 63].

## 5. Enrage

None (normal class, R4). Stall risk is low: the fight is 3-4 turns and the enemy has no heal.

## 6. Buffs and counter Exploits

Not applicable (normal class).

## 7. Counterplay

- **Good player:** on turn 1 read the two needles. Spend the free nudge to put the Flare needle onto a WEAK landing or Null. Use a Defrag or SANDBOX if the Lock-On is unavoidable. Keep a slice cleansed or ENCRYPTED, because ENCRYPTED absorbs the Flare. Burst with a card that makes both of your hits land, since the pointer rule doubles them.
- **Weak player:** fixes only the Lock-On needle and ignores the Flare, so a slice of theirs sits at −25 % output for the rest of the fight. Or spends RAM on extra nudges to get a Perfect and drops into a worse needle position.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Variable slice sizes (4, 5, 6) | N12 | Data-only fallback: all 5-tick slices with 6 slices (today); lose the narrow Ping |
| Needle at tick 11 | N11 | None; this is the core of the design. Without it, use 0 / 15 (today) |
| `hp_by_tier`, damage table | N2 | Keep `hp` = 50 |
| OUTPUT_DOWN ×1 | N8/N9 | OVERCLOCKED on your slice. It burns into CORRUPTED, which is harsher. Or the PARASITE status (a 2-stack OUTPUT_DOWN today) |
| Flat × tier damage factor | N1 | Keep flat numbers unscaled |

## 9. Delta vs today

- **Kept:** id, the two-needle identity, the Flare, Overflow 16 turned into a smaller Lock-On, cycle_reward 15.
- **Changed:** needles 0/15 → 0/11; layout from 6×5 (Shim 8, Shim 8, Defrag 6, Overflow 16, Flare, Null) to 6 uneven slices; Overflow 16 → 12; Shim 8 → 5; Flare gains 2 damage and a status; HP 48 → tier table.
- **Heat effects:** none exist in the file, and none are added.

## 10. Predicted sim check

No baseline row exists; this is estimated from the wheel.

- Expected turns: ~3.2 at T1-T2, ~3.6 at T3, ~3.8 at T4.
- Win %: T1 ~99 %, T2 ~98 %, T3 ~94 %, T4 ~88 %.
- Why: the intake at T4 is about 13 per turn unsteered, times 3.8 turns, ≈ 49 HP against a 60-65 HP operative before steering, which cuts it by roughly half. T4 is on the edge of the 90 % target and may need slightly lower Lock-On damage.

## 11. Open questions

Q: Is 11 apart (0 / 11) too hard to read on the HUD? Close needles are the N11 readability risk, so should the gap be at least 12?
Q: Should the Flare status be OUTPUT_DOWN ×1, or should it be TIER_DOWN, which fits "tracking loses precision" better thematically?
Q: Does the player's hit really land on both enemy needles? The budget uses ×1 as a conservative factor, so do we confirm which?
Q: May Flare apply on a WEAK landing, as Q11 proposes?
Q: Should T4 Lock-On drop to 10, if the sim shows under 90 % win?
