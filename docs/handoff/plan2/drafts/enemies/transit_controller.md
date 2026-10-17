<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__transit_controller; status ok; tokens in 15375 cache-write 0 cache-read 32007 out 4036; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# transit_controller: direct design

## 1. Identity & the one question

- **Class:** Normal, 1 phase, 3-4 turns, no enrage.
- **Corporation:** Halcyon Civic (transit signal control).
- **Layers:** L1-2 teaching. It is the first enemy that makes the player read two needles that move. It can still appear at L5-6 at T3-T4, where the numbers carry the pressure.
- **Working concept:** "Signal Timing." Two needles run on a loop and each turn's reading is predictable one turn ahead. Its wheel is built so the needles never read a pair of strong slices together.
- **The one question:** "The needles move 1 tick per turn and I can read where they will be. Which slice do I want under each, and can I steer so that its big hit lands on a WEAK edge or on Null?"
- **What shortens the fight:** the Overflow is a 3-tick slice, so a 1-tick nudge turns a Perfect or Good landing into WEAK. The Defrag is a 7-tick slice with a Perfect in the middle. The player nudges onto it to soak it into a wasted 0.5x block, or steers away from it to keep it from blocking. One free nudge per turn decides who wins the turn.
- **Distinct from siblings:**
  - Parking Warden, Permit Office and Utility Meter are single-pointer status or economy enemies, and Patrol Unit is a flat brawler.
  - This is the only normal whose question is needle timing (orbit plus an uneven pair).

## 2. Phase plan

Single phase, no thresholds, no floor (R3 is moot for a 1-phase normal).

| Item | Value |
|---|---|
| Needles | 2: ticks 0 and 12 (uneven, R10) |
| Pointer behavior | ORBIT, +1 tick per turn on both (kept from today; a trail previews next turn's ticks) |
| Hub rule | none |
| Statuses / parasites / listeners | none |
| Heal | none |

**Layout (sum 30)**, in clockwise order from tick 0. Slice centers are at the cumulative midpoint of each slice. Tick 0 is the pointer's start; the first slice is centered at 2 (its first tick is 0).

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Shim | 5 | 6 damage | FLAT |
| 2 | Defrag | 7 | 8 BLOCK | FLAT |
| 3 | Shim | 4 | 6 damage (no Perfect) | FLAT |
| 4 | Overflow | 3 | 14 damage (G P G) | FLAT |
| 5 | Shim | 5 | 6 damage | FLAT |
| 6 | Null | 6 | none | n/a |

Sum: 5+7+4+3+5+6 = 30.

- **Slice boundaries (ticks):**
  - Shim 0-4
  - Defrag 5-11
  - Shim 12-15
  - Overflow 16-18
  - Shim 19-23
  - Null 24-29
- **Start positions:** needle A on tick 0 reads Shim 1's edge (WEAK, distance 2 from centre tick 2). Needle B on tick 12 reads Shim 3's edge (WEAK).
- **Orbit:** both needles move +1 per turn.
  - Turn 2: A on 1 (Good) and B on 13 (Good).
  - Turn 3: A on 2 (Perfect) and B on 14 (Good).
  - Turn 4: A on 3 (Good) and B on 15 (WEAK).

  Both slices stay in range for the whole fight, so damage ramps toward the middle turns.
- **Why the reads are interesting:** the Overflow is far from both needles on turns 1-3 (ticks 16-18 versus B at 12-14), so it is a threat that arrives late. B reaches tick 16 on turn 5, which most fights never see. Wheel starts are re-randomised each turn (GDD 2.2), so the orbit offsets stack on top of a random respin. A "preview ahead" matters only because the player sees the trail.

**Transition:** none.

## 3. Sustain and intake

- **Sustain:** one source, the Defrag slice's BLOCK. It is not heal, so there is 0 heal per turn. The player-facing cost of the BLOCK is capped at the reference damage (T3 reference 14 dpt):
  - Defrag 8 BLOCK × T3 tier factor 1.69 = 13.5, so ~13 prevented at most.
  - It reads only when a needle lands on the 7-tick Defrag, roughly 7/30 = 23 % per needle.
  - Expected reading: 2 needles × 0.23 × 13 ≈ 6.0 BLOCK per turn.
  - That is ~43 % of T3 reference dpt before the player's counterplay, which is over the 30 % cap.
- **Fix:** cut Defrag to 5 FLAT. Then 2 × 0.23 × 5 × 1.69 ≈ 3.9 per turn, or 28 % of 14. That fits the cap.
- **Chosen:** Defrag 5 BLOCK. Table amount above is revised to 5 (the table in §2 applies this change; read the Defrag row as 5 BLOCK).
- **Intake** at the reference player (damage the enemy deals per turn, T1 values, before block and nudges):
  - The player's average landing cannot be known exactly, so use the geometric expectation. Each needle reads a Shim with probability (5+4+5)/30 = 0.47 and an Overflow with 0.10.
  - Per needle per turn: Shim 0.47 × 6 × ~0.83 (mix of WEAK/Good/Perfect tiers) ≈ 2.3, plus Overflow 0.10 × 14 × 0.83 ≈ 1.2. Total ≈ 3.5.
  - Two needles: ~7 per turn at T1 before player steering.
  - A reference player with one free nudge removes about a third by steering one needle off damage: **~4.5 intake per turn at T1**, above 0.
  - At T3 this is ×1.69, about 7.6.

## 4. HP by tier

R2 budget: `reference_dpt_by_tier` [9, 11, 14, 18] × 3.5 turns × needles the player hits land on. The player hits one enemy wheel with one pointer, so ×1. No sustain subtracted beyond the BLOCK (BLOCK absorbs only the player's turn damage, accounted in intake rather than HP).

| Tier | Budget (dpt × 3.5) | `hp_by_tier` | Band (R2) |
|---|---|---|---|
| T1 | 9 × 3.5 = 31.5 | 32 | 28-36 |
| T2 | 11 × 3.5 = 38.5 | 39 | 34-44 |
| T3 | 14 × 3.5 = 49 | 49 | 44-56 |
| T4 | 18 × 3.5 = 63 | 63 | 56-70 |

Today's 50 HP is flat across tiers. Under the enemy damage table [1.0, 1.3, 1.69, 2.2], threat scales too, so a 4-turn T4 fight stays fair.

## 5. Enrage

None (Normal class default is off). A 3-4 turn fight never reaches turn 8.

## 6. Buffs and counter Exploits

Not applicable (not a boss).

## 7. Counterplay

- **Good player:**
  - Reads the orbit trail on turn 1, nudges the needle that would land on the Overflow edge into WEAK or onto Null (one tick is enough on a 3-tick slice).
  - Keeps the free nudge for the BLOCK: it is cheap to nudge a needle off the Defrag, because block only costs the player damage if it lands.
  - Burst-spends cards on turns 2-3, while the needles still sit on the weak left-hand Shims and Null.
  - Wins in 3-4 turns.
- **Weak player:**
  - Ignores the second needle and only checks the Overflow.
  - Wastes damage on turns where a needle sits on the Defrag, because the player damage is absorbed.
  - Spends the free nudge on a WEAK Shim instead of the block, and stretches the fight to 5+ turns, taking the Overflow on turn 5.

## 8. Systems needed

| N# | Need | Fallback |
|---|---|---|
| N11 pointers on any tick | Needles at 0 / 12 (uneven) | Keep 0 / 15 (even); loses some of the "which needle" tension |
| N12 variable slice sizes | 7/4/3/6-tick slices | Use six 5-tick slices; the Overflow loses its narrow window |
| N2 `hp_by_tier`, `enemy_damage_by_tier` | HP by tier, flat amounts × tier factor | Single `hp`, current scale |
| N1 amount modes | FLAT amounts are scaled by tier factor | Current behaviour |

The fully data-only fallback is six 5-tick slices, pointers 0 / 15, HP single value: it works today, with a weaker question.

## 9. Delta vs today

- **Changed:**
  - Needles 0 / 15 → 0 / 12.
  - Layout from six 5-tick slices to 5/7/4/3/5/6.
  - Shim 8 → 6 and Defrag 6 → 5 (flat amounts × tier factor, and shim_6 and defrag_5 need new slice files; Overflow stays 14).
  - HP 50 → 32 / 39 / 49 / 63.
- **Kept:** orbit 1 per turn, the two-needle theme, Overflow 14, the Null slice, `cycle_reward` 15, the Halcyon corporation entry.
- **Per-turn damage:** the old wheel read two Shims 8 as the common case; the new wheel lowers Shim and raises variance with the narrow Overflow.
- **heat_effects:** none exist on this enemy; none are added.

## 10. Predicted sim check

No baseline row exists (the sweep covered Solace only). This is an estimate from the wheel.

| Tier | Mean turns | Win % | Reason |
|---|---|---|---|
| T1 | ~3.5 | ~97 % | 32 HP against 9 dpt; ~4.5 intake per turn over 3-4 turns is ~16 damage |
| T2 | ~3.6 | ~96 % | HP and damage both scale (×1.3) |
| T3 | ~3.8 | ~92 % | Intake ~7.6 per turn; ~30 over the fight |
| T4 | ~4.0 | ~88 % | Intake ~10 per turn; the narrow Overflow is the main risk |

Expect p90 turns ≈ 5. The T4 win rate is likely under the 90 % target, so lower T4 Shim or HP if the sim confirms.

## 11. Open questions

Q: Should the orbit step (+1 per turn) be preserved as a trail on the HUD, or does N11 need the trail redrawn when two needles sit 12 ticks apart?
Q: Is 3-tick Overflow (G P G) too punishing at T4 (14 × 2.2 = 31 on a Perfect), or should the amount drop to 12?
Q: Should the Defrag be a 7-tick slice (soft-block, wide) or a 4-tick slice (hard-to-hit)? I chose 7 so the block is easy to dodge-or-feed.
Q: Does the player's free nudge apply to the enemy wheel at the same cost, so the BLOCK dodge costs 0 RAM on turn 1?
Q: Would an authored `tick_quality` on the 7-tick Defrag (W W W P W W W) make the block's Perfect more readable?
