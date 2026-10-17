<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__orbital_debris; status ok; tokens in 15352 cache-write 0 cache-read 32007 out 3075; cost $0.034. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# orbital_debris: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage. **Corporation:** Orbital. Appears in L1-2 as a teaching enemy for **spin resistance** (the first Orbital enemy that makes manipulation cost something) and in L5-6 as a pressure enemy whose Debris Cloud eats a nudge or a card every turn.
- **The one question:** "Do I pay to move a heavy wheel, or do I plan around where it already sits?" Resistance 2 absorbs the first 2 ticks of every nudge or spin. A free nudge ±1 does nothing against it, which today makes the wheel nearly immovable and the fight a coin flip.
- **Fast answer:** read the wheel at the turn-start respin and move it only when one paid action (a 3-tick spin, or Flip/Respin with the hub down) lands the needle on the Null or the Sandbox slice. A player who burns RAM trying to turn it loses tempo.
- **Distinct from siblings:** Ground Control, Launch Pad, Tracking Station, Uplink Relay and Weather Satellite are not rebuilt here. Debris is the only normal whose identity is resistance plus a wide slab slice.

## 2. Phase plan (single phase, no threshold, no floor)

| Item | Design |
|---|---|
| Needles | 1, fixed at tick 0 (FIXED) |
| Hub rule | Passive resistance 2, refreshed each player turn (as today) |
| Statuses / parasites / listeners | None. Data only. |

**Layout (sizes sum to 30, N12; 6 slices):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Slab (SHIM) | 7 | 9 damage, WEAK-heavy edges (W W G P G W W) | FLAT |
| 2 | Plating (BLOCK) | 5 | 8 block | FLAT |
| 3 | Fragment (SHIM) | 4 | 6 damage; no Perfect (W G G W) | FLAT |
| 4 | Plating (BLOCK) | 5 | 8 block | FLAT |
| 5 | Containment (SANDBOX) | 4 | negates one whole attack of yours (R13), no Perfect | n/a |
| 6 | Null | 5 | nothing | n/a |

Total 7+5+4+5+4+5 = 30.

- **Why the sizes:** the big 7-tick Slab is the dangerous slice and also a big landing target, so the player can drag the needle onto an edge (WEAK = 0.5×, 4.5 damage) with a 2-3 tick shift. The 4-tick Fragment has no Perfect, so the Debris never gets full output from it.
- **Transition:** none. One phase, so nothing is parked or cleansed.

## 3. Sustain and intake
- **Sustain:** none (no heal). The Plating block is defense, not sustain; it expires on its own turn and reaches only about 8 of the reference 11 damage when it lands.
- **Intake at the reference player** (flat damage × tier factor, T1 baseline; random landing, 1 needle):
  - Slab: probability 7/30 of being read. Expected (Perfect 1/30 → 9, Good 2/30 → 9, Weak 4/30 → 4.5): (1×9 + 2×9 ... computed per tick: 7 ticks → 5 full-power-ish ticks ×9 + 2 weak... ) Simplified: 3 non-weak×9... In detail with W W G P G W W: 3 ticks at 9 and 4 at 4.5 = 45 per 30 ticks = 1.5 per turn.
  - Fragment: W G G W → 2×6 + 2×3 = 18 → 0.6 per turn.
  - **Raw expected intake ≈ 2.1 per turn at T1** (about 2.7 / 3.5 / 4.6 at T2-T4 with the damage table 1.3 / 1.69 / 2.2). This is above 0 but gentle, as a teaching normal should be; a player who steers onto Slab takes 9-10 per turn, which is the threat that makes resistance matter.
  - The old wheel (two 10-damage Shims in six slices) gave about 3.3 per turn at T1; the new one is milder on average, with a sharper tail.

## 4. HP by tier (R2 normal band)
Budget = reference_dpt × 3.5 turns × needles on the enemy (1) minus sustain (0). The Debris's resistance taxes the player's manipulation but not hits, and its Plating blocks about 8 on 2 of 6 slices, so I trim the budget slightly: about 1 in 3 turns the player's damage meets a block.

| Tier | dpt | 3.5 × dpt | Chosen HP | Band |
|---|---|---|---|---|
| T1 | 9 | 31.5 | **34** | 28-36 |
| T2 | 11 | 38.5 | **40** | 34-44 |
| T3 | 14 | 49 | **50** | 44-56 |
| T4 | 18 | 63 | **62** | 56-70 |

`hp_by_tier` = [34, 40, 50, 62]. Today 62 HP is the T3 value. It is above band at T3 (56 max) and equals T4, so it is cut at T1-T3.

## 5. Enrage
None (normal class default is off, R4). A 3-4 turn fight does not need it; the damage tail on Slab already punishes stalling.

## 6. Buffs and counter Exploits
Not applicable (normal enemy).

## 7. Counterplay
- **Good player:** reads the turn-start landing. If the needle sits on Null or Containment, they do nothing. If it sits on Slab, they pay for a 3-tick spin (2 absorbed, 1 moves; so a 4-tick spin is needed for 2 ticks of movement) or play a Spin card, or just SHIELD/BLOCK the 9 and keep attacking. They use Strip/Ghost resistance-ignoring effects if available (the Ghost core ignores resistance on the first nudge, which makes Ghost the ideal answer).
- **Burst answer:** a Breaker's double-resolve ends it in 3 turns without ever touching the wheel.
- **Weak player:** spends free nudges ±1 that are fully absorbed (preview shows 0 movement), then pays RAM for nothing; or attacks into Plating blocks without noticing that 2 of 6 slices block.

## 8. Systems needed
- **N12** (variable slice sizes, sub-tick map): required for 7/5/4-tick slices. **Fallback (data-only):** use six 5-tick slices in the same order with Fragment and Containment as normal slices. It works but loses the "no Perfect on Fragment" detail and the wide-edge Slab; the design remains valid.
- **N2** (`hp_by_tier`, `enemy_damage_by_tier`): required for the HP numbers. Fallback: author hp = 50 as a single value.
- **N1** is not needed (all amounts FLAT). Nothing else.

## 9. Delta vs today
- **Kept:** passive_resistance 2, pointer at tick 0, Shim/Defrag/Sandbox/Null set, cycle_reward 15, description.
- **Changed:** HP 62 → [34, 40, 50, 62]; Shim 10 ×2 → Slab 9 (7 ticks) and Fragment 6 (4 ticks); Defrag 8 stays but now two 5-tick slices; slices become sized; Sandbox 5 becomes the R13 SANDBOX (negate one attack) rather than a shield of 5.
- **New slice files:** `debris_slab`, `debris_fragment` (rather than the shared shim_10).
- **heat_effects:** none exist on this file; none added.

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only), so this is estimated from the wheel.
- **Turns:** about 3-4 at the step-0 reference player on every tier (HP tracks the budget). The ordinary player sees ~1/3 of turns blocked, so 3.5-4.
- **Win rate:** about 97 % at T1-T2, 93 % at T3, 90 % at T4. Intake of about 2-5 per turn over 4 turns is low against 45-60 HP operatives.
- **Why:** low expected intake, no sustain, HP at the band midpoint; the only risk is a tail of consecutive Slab landings, with a sharp 9-20 damage loss at T4.

## 11. Q:
- Q: Should resistance show a preview line "your nudge moves 0" so the wheel's heaviness is legible to a first-time player?
- Q: Should Containment (SANDBOX) read its negation on the enemy side too, or is a player-facing "negates one attack" only?
- Q: Do I want Slab at 9 or keep the old 10 for continuity?
