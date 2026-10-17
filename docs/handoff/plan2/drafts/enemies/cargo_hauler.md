<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__cargo_hauler; status ok; tokens in 16179 cache-write 0 cache-read 32007 out 3290; cost $0.036. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# cargo_hauler: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, Meridian. It is the WEIGHT teacher (spin resistance), and it is the only normal whose question is "pay to move it, or don't move it".
- **Layers:** L1-2 teaching (at T1 resistance 2, one needle, readable) and L5-6 pressure (same wheel, T3-T4 numbers, Heat +1 resistance stacks on top).
- **The one question:** "Its wheel resists, so which landing can you afford to leave alone?" Resistance 2 absorbs the first 2 ticks of nudge, so a 1-tick nudge is wasted RAM. The Hauler is built so a 1-2 tick fix never works, while a 3+ tick spin card or a Flip-free plan does.
- **Answer that shortens the fight:** a Spin card (the first 2 ticks are absorbed, the rest move the wheel) steers the needle onto the Null slice or a WEAK edge, and you then burst the open turns. Wasting free nudges on it lengthens the fight.
- Distinct from Conveyor Warden (orbit), Customs Scanner and Tariff Collector (RAM drain / tolls), and Route Optimizer and Drone Dispatcher (plans and satellites): the Hauler is pure mass, with no listener, ring or satellite.

## 2. Phase plan (single phase)

| Field | Value |
|---|---|
| Phase | 1 of 1, no threshold, no floor (R3 not used) |
| Needles | 1, fixed at tick 0 (FIXED) |
| Hub | Weight: passive resistance 2, refreshed each player turn (existing `passive_resistance`) |
| Statuses / parasites / listeners | none |

**Layout (7 slices, sizes sum to 30, N12):**

| # | Slice | Size | Effect |
|---|---|---|---|
| 1 | Crush (Overflow) | 4 | 14 damage, FLAT. A 4-tick slice has no Perfect, so it hits as G/G or W (only ever Good or WEAK). |
| 2 | Brace (Defrag) | 5 | BLOCK 8, FLAT |
| 3 | Shim | 5 | 8 damage, FLAT, plus +1 resistance on trigger (kept from shim_8_weight) |
| 4 | Null | 6 | nothing (W W G G W W: the safe parking slice) |
| 5 | Brace | 4 | BLOCK 8, FLAT |
| 6 | Sandbox (Detour) | 3 | SANDBOX: negates one attack. Perfect only at the centre tick. |
| 7 | Shim | 3 | 8 damage, FLAT |

Total: 4+5+5+6+4+3+3 = 30.

**Design logic:**
- One big 14 hit makes the threat real. The two Shims are the small hits.
- Weight's growth (+1 resistance when Shim 8 triggers) punishes lazy play: if it lands the Shim, resistance 3 makes next turn's nudges even worse. It is capped at 4 (a new `max_resistance` is not needed: cap it in data by using Cleanse-on-turn, or accept the growth at 3-4 turn lengths).
- Brace and Sandbox give the Hauler its defensive texture: they eat a bad opening turn but cost it the turn's damage.
- No transition: a single phase.

## 3. Sustain and intake
- **Sustain:** none. It has no heal. Its defense is BLOCK and one SANDBOX, which are not sustain. The cap of 30 % of reference damage (≈2.7 at T1, 5.4 at T4) is not approached.
- **Intake per turn** (reference player, one needle, uniformly random landing, T1 damage factor 1.0 and T3 1.69):
  - Damage slices: Crush 4/30 at ~14, Shim 5/30 at 8, Shim 3/30 at 8. Expected raw = (4×14 + 5×8 + 3×8)/30 = 120/30 = 4.0 per turn at T1. WEAK landings cut some by half, about −10 %, so ≈3.6.
  - Player block or sandbox lowers this. A sensible player takes about **2.5-3.5 per turn at T1**, 4.2-5.9 at T3 and 5.5-7.7 at T4 (×1.3 / 1.69 / 2.2). This is above 0 and well above a Dosage-Dispenser-style failure.
  - Over 3.5 turns at T1 that is ~10 HP, a clear but not punishing cost.

## 4. HP by tier (R2 Normal band)
Budget = `reference_dpt_by_tier` × 3.5 turns × 1 needle (the player's hits land once), minus sustain (0).

| Tier | Arithmetic | Band | HP |
|---|---|---|---|
| T1 | 9 × 3.5 = 31.5, +Brace/Sandbox soak ≈ 3 | 28-36 | **34** |
| T2 | 11 × 3.5 = 38.5, +3 | 34-44 | **40** |
| T3 | 14 × 3.5 = 49, +4 | 44-56 | **52** |
| T4 | 18 × 3.5 = 63, +5 | 56-70 | **66** |

- The Hauler's current 72 HP is an elite-sized outlier and is cut by about half at T1.
- The small top-up covers the two Brace slices and the Sandbox, which absorb about one hit's worth over the fight.

## 5. Enrage
None (normal class, R4). A stalling player is bounded by the 3-4 turn HP budget, and Weight's resistance growth is the soft pressure.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** on turn 1 read where the needle lands. If it is on Crush, spend a Spin of 4+ (2 absorbed, 2 moved, enough to cross into Brace or Null) rather than 2 nudges. If on a Null or Brace, leave the wheel alone and burst. Strip or Hub Breach cards (Ghost's Perfect hook strips 2 resistance) turn Weight off, and Ghost's first nudge ignores it. Avoid letting a Shim 8 land twice: the resistance climbs.
- **Weak player:** spends the free nudge and 2 RAM on 1-tick nudges that Weight absorbs completely, then eats Crush; or attacks into Brace and Sandbox turns and wastes damage, which stretches the fight past 4 turns.

## 8. Systems needed
- **N12** (variable slice sizes, 3-6 ticks): needed for the 4/3/6-tick slices. **Fallback:** 6 slices of 5 ticks (Crush, Brace, Shim, Null, Brace/Sandbox mix, Shim), which keeps the question and loses only the narrow Sandbox window.
- **N1** (amount modes): the flat amounts get the R2 tier damage factor. Without N1 the old `output_scale` path applies, which is acceptable.
- **N2** (`hp_by_tier`): needed for the table above. **Fallback:** a single `hp` of 52 (T3) plus the global scale.
- **N14** (defense trio naming and the SANDBOX rule): display and rule only, no data change.
- N3 is not needed (single phase).

## 9. Delta vs today
- **Kept:** the id, the Weight passive (resistance 2), the Shim-with-resistance slice, the Sandbox and Null slices, one pointer at tick 0 and `cycle_reward = 15`.
- **Changed:** HP 72 → tiered 34/40/52/66 via `hp_by_tier`. The six equal slices become seven uneven slices (N12). Overflow 14 is added as the one real threat, since today's wheel only has Shim 10. One Shim 10 is cut to Shim 8, and Defrag count goes 2 → 2 with a 4-tick and a 5-tick version.
- **heat_effects:** it has none today and none is added. Heat's global +1 resistance at 50 already stacks onto the Hauler naturally.

## 10. Predicted sim check
(Estimated by hand, no baseline row for Meridian.)

| Tier | Turns | Win % | Why |
|---|---|---|---|
| T1 | 3.2 | ≥97 % | 34 HP in 3-4 turns with ~3 intake |
| T2 | 3.4 | ~96 % | |
| T3 | 3.7 | ~92 % | intake ~5 per turn, still affordable |
| T4 | 4.0 | ~90 % | resistance 3-4 growth risk |

- The current 72 HP at the same reference damage would be about 8 turns, so this is roughly a halving.
- Risk: Weight growth could push T4 over 4 turns if the player never removes resistance.

## 11. Q:
- Q: Should the Shim +1 resistance growth be capped (for example at 4) in data, or left to the 3-4 turn length to cap itself?
- Q: Is a 14-damage Overflow on a 4-tick slice (never Perfect, so a flat 14 or 7) too swingy for L1-2 teaching? Would 12 be safer?
- Q: Does Sandbox on a 3-tick slice read clearly enough, or should Sandbox sit on a 5-tick slice and lose the narrow window?
- Q: Should Cargo Hauler lose its elite-size history entirely, or do we want a "Heavy Hauler" elite variant later?
