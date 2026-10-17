<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__last_mile_enforcer; status ok; tokens in 7793 cache-write 0 cache-read 32585 out 16029; cost $0.091. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, P2 layout, Perfect at needle 0, centres undefined):**
  - P2 is rebuilt as Shim 4 · Overflow 6 · Cite 3 · Null 4 · Overflow 5 · Shim 4 · Shim 4 = 30.
  - Every table now gives tick ranges and the sub-tick map, with slice 0 starting at tick 0.
  - Needle 0 reads a WEAK/GOOD Shim, not a Perfect Overflow.
  - Needle 12 reads the last tick of the 3-tick Cite (GOOD).
  - There is no "boundary" claim any more.
- **Issue 2 (BLOCKER, WEAK share and damage frequency):**
  - A 4-tick slice is W G G W, so 2 of its 4 ticks are WEAK. The false "most ticks" claim is gone.
  - Damaging slices cover 19 of 30 ticks in P1, so frequency is by tick share, not "4 of 6 turns".
  - Expected raw damage per resolve is recomputed from the sub-tick maps.
- **Issue 3 (BLOCKER, HP arithmetic):**
  - HP is recomputed from the R2 formula, and every cell is shown in §4: 61 / 74 / 94 / 120.
  - P2 gets a ×1.15 allowance for its second needle. It is not the full ×2, because Null, Cite and WEAK ticks absorb part of the second landing.
  - The threshold is derived from the two phase budgets (0.48), not assumed to be 0.50.
  - All values sit inside the elite bands.
- **Issue 4 (MAJOR, listener cap per resolve vs per turn):**
  - The listener is now once per turn, BLOCK 2 FLAT scaled by the tier factor.
  - It is checked against the 30 % cap at every tier and is the only sustain source in P2.
  - P1 has no sustain: the Defrag and Sandbox slices are gone.
- **Issue 5 (MAJOR, latch contradiction, invented field):**
  - "Latch" is deleted everywhere.
  - The P1 → P2 pointer change uses the existing PointerBehavior enum: ORBIT → MULTIPLY.
  - The P2 question is "which needle takes the Overflow?".
- **Issue 5b (MAJOR, "Sandbox 8 slice" removal):** removed. The current .tres is not in the brief, so no delta claim is made about it.
- **Issue 6 (MAJOR, escort respawn, N# tagging, mixed raw/post-block intake):**
  - The respawn is dropped. The escort is fixed once (N13) and removed by the override.
  - `max_active` is dropped.
  - Intake is stated as raw and as after-play, separately.
  - Every system is tagged with an N# or a fallback.
- **Issue 7 (MAJOR, heat_effects hedge):** now a flat decision: **retire**, with the reason.
- **Issue 8 (NIT):** kept, because the Flip and Cleanse notes were correct.
- **Critic Q "Does the escort survive the override?":** no. It is removed without counting as a kill.
- **Critic Q "cap per turn or per resolve?":** per turn.
- **Orbit readability:** v1 claimed it was readable two turns ahead. That conflicts with the start-of-turn respin (GDD 2.2). v2 states it as a known +2 drift applied at resolve, shown in the preview and trail.
- **Conflict with rulings:** none.

# last_mile_enforcer: direct design

## 1. Identity & the one question

**Class:** Elite, Meridian, 2 phases, one threshold at 48 % HP. It appears at L3-6 as pressure and as an L5-6 gate. It is not a teaching enemy; Port Authority holds the Meridian elite teaching slot.

**Distinct from the rest of Meridian:**
- Conveyor Warden and Weight enemies own spin resistance.
- Port Authority and the Customs Seal own shields.
- Drone Dispatcher owns spawning.
- The Enforcer is the **delivery** enemy: a drifting needle, a bodyguard escort, then a pair of uneven needles with a double-Overflow trap. It has no resistance and no heal.

| Phase | Question | What shortens the fight |
|---|---|---|
| P1 Route (100 → 48 %) | "The needle drifts +2 ticks before it resolves. Where does it really land, and can you nudge it onto Null or a WEAK edge?" | Dodge cheaply, then burst on Null and Defrag-free turns. Overkill past the park is lost, so land exact bursts. |
| P2 Signature Required (48 → 0 %) | "Two needles 12 ticks apart: which one takes the Overflow, and is a Perfect worth +2 enemy block?" | Steer so at most one needle reads an Overflow. Never leave both on Overflow. |

## 2. Phase plan

**Convention:** slice k covers ticks [start, start+size−1]. A needle on tick t reads sub-tick t−start of the R11 map. Wheel rotation shifts which ticks the needles read, so every position below is relative to the wheel.

### P1 Route (100 → 48 %, parked at the floor)

| Item | Value |
|---|---|
| Needles | 1 at tick 0, ORBIT: +2 ticks applied at resolve. The trail and preview show the shifted landing. |
| Escort | Courier Drone (existing `courier_drone.tres`) docked on slice 1. Fixed (N13), no respawn. |
| Hub / statuses / listeners | none |

| # | Slice | Ticks (start–end) | Size | Sub-tick map | Effect |
|---|---|---|---|---|---|
| 0 | Shim | 0–4 | 5 | W G P G W | 8 damage FLAT |
| 1 | Shim (escort) | 5–8 | 4 | W G G W | 8 damage FLAT. Player hits aimed at this slice hit the drone. |
| 2 | Null | 9–13 | 5 | none | none |
| 3 | Overflow | 14–17 | 4 | W G G W | 14 damage FLAT (no Perfect; 2 of 4 ticks are WEAK) |
| 4 | Shim | 18–23 | 6 | W W G G W W | 6 damage FLAT |
| 5 | Null | 24–29 | 6 | none | none |

Sizes: 5+4+5+4+6+6 = 30.

**Damage share:** damaging slices cover 19 of 30 ticks (5+4+4+6).

**Expected raw damage per resolve (sub-tick quality, WEAK = 0.5×):**
- Slice 0: 4+8+8+8+4 = 32.
- Slice 1: 4+8+8+4 = 24.
- Overflow: 7+14+14+7 = 42.
- Slice 4: 3+3+6+6+3+3 = 24.
- Total 122 / 30 ≈ 4.1 per resolve.

### Transition P1 → P2 (parks at 48 %)
- Excess damage is lost (R3). The phase changes at the end of that resolve.
- `wheel_override` with the P2 layout; the pointer behavior changes ORBIT → MULTIPLY (needles at 0 and 12).
- The escort is removed by the override. It is not destroyed, so there are no kill rewards. (Q7 is still open.)
- Player statuses are kept (R6). `cleanse_on_enter = NONE`.
- Phase line: "SIGNATURE REQUIRED."

### P2 Signature Required (48 → 0 %, no floor)

| Item | Value |
|---|---|
| Needles | 2 at ticks 0 and 12 (uneven, R10), FIXED. No orbit, no escort. |
| Status | Cite applies OUTPUT_DOWN ×1 to your slice under that needle, max ×2 (N8/N9). |
| Listener (N6) | **Proof of Delivery:** the first time each turn you land a Perfect (ON_PERFECT), it gains BLOCK 2 FLAT (× tier factor) at its next defensive pass. It expires at its next turn start. The preview shows "+BLOCK 2" when the Perfect is staged, and undo removes it. |

| # | Slice | Ticks | Size | Sub-tick map | Effect |
|---|---|---|---|---|---|
| 0 | Shim | 0–3 | 4 | W G G W | 6 damage FLAT |
| 1 | Overflow | 4–9 | 6 | W W G G W W | 12 damage FLAT |
| 2 | Cite (INFECT) | 10–12 | 3 | G P G | 4 damage FLAT + OUTPUT_DOWN ×1 |
| 3 | Null | 13–16 | 4 | none | none |
| 4 | Overflow | 17–21 | 5 | W G P G W | 12 damage FLAT |
| 5 | Shim | 22–25 | 4 | W G G W | 6 damage FLAT |
| 6 | Shim | 26–29 | 4 | W G G W | 5 damage FLAT |

Sizes: 4+6+3+4+5+4+4 = 30.

**The pair rule:**
- Needle B reads tick t+12 when needle A reads tick t.
- Both needles sit on an Overflow when t is 5–9 (5 of 30 rotations). That is the trap.
- Needle B on Null needs t = 1–4. Needle A on Null needs t = 13–16.
- A 1–2 tick nudge usually breaks a double-Overflow.

**Expected raw damage per needle:**
- Per slice: 18, 48, 12, 0, 48, 18, 15 = 159, so 159 / 30 ≈ 5.3 per needle.
- Two needles: 10.6 raw per resolve.

## 3. Sustain and intake

**Sustain:**
- P1: none.
- P2: only the Proof of Delivery block, once per turn, 2 × tier factor.
- It is the only source, and it fires only if you land a Perfect.

| Tier | Factor | Listener block per turn | 30 % of reference DPT | Under cap |
|---|---|---|---|---|
| T1 | 1.0 | 2.0 | 2.7 | yes |
| T2 | 1.3 | 2.6 | 3.3 | yes |
| T3 | 1.69 | 3.4 | 4.2 | yes |
| T4 | 2.2 | 4.4 | 5.4 | yes |

**Intake per turn** (raw means before player defense, and it is scaled by the tier factor):

| Phase | Raw per resolve | T3 raw (×1.69) | After reference play | Above 0? |
|---|---|---|---|---|
| P1 | 4.1 | ≈ 6.9 | 3–5 (one nudge off the Overflow) | yes |
| P2 | 10.6 | ≈ 17.9 | 8–11 (break the double-Overflow, SHIELD or SANDBOX the second hit) | yes |

## 4. HP by tier (R2, elite, 2 phases)

**Formula:**
- P1 budget = DPT × 3.5.
- P2 budget = DPT × 3.5 × 1.15 (second needle) − sustain × 3.5.
- Why 1.15: the pointer rule gives P2 more landings, but Null, Cite and WEAK ticks absorb part of the second landing.

| Tier | DPT | P1 | P2 base ×1.15 | P2 sustain ×3.5 | P2 net | HP total | Band |
|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 36.2 | 7.0 | 29.2 | **61** | 56–72 |
| T2 | 11 | 38.5 | 44.3 | 9.1 | 35.2 | **74** | 68–88 |
| T3 | 14 | 49.0 | 56.4 | 11.8 | 44.5 | **94** | 88–112 |
| T4 | 18 | 63.0 | 72.5 | 15.4 | 57.1 | **120** | 112–144 |

**Threshold:**
- 0.48 is the P2 share (29.2 / 60.7 = 0.481, and T3 gives 0.476).
- The floor is ceil(HP × 0.48).

| Tier | Floor | P1 damage | P2 damage |
|---|---|---|---|
| T1 | 30 | 31 | 30 |
| T2 | 36 | 38 | 36 |
| T3 | 46 | 48 | 46 |
| T4 | 58 | 62 | 58 |

Each phase lands within one HP of its budget, apart from rounding.

## 5. Enrage

**Default:** start turn 8, every 5 turns, +25 % additive (Q2 is pending on additive vs compounding).
- The fight targets 6–8 turns, so enrage only punishes a stall.
- No authored enrage is needed. The drift and pair rules need no extra clock.

## 6. Buffs and counter Exploits
Elite: none.

## 7. Counterplay

**P1, good play:**
- Read the preview's drifted landing and spend the free nudge on the enemy wheel to put the needle on a Null (9–13, 24–29) or a WEAK edge of the Overflow.
- Burst on Null turns.
- Attack the escort only when slice 1 sits at your pointer anyway.
- Do not overkill past the floor.

**P1, weak play:**
- Forgets the +2 drift and nudges the wrong way, eating the 14-damage Overflow (≈ 24 at T3).
- Spends damage on the escort, which has no respawn but still soaks that slice's hits.

**P2, good play:**
- Check the pair rule each turn: if t is 5–9, nudge 1–3 ticks to put one needle on Null or Cite.
- Hold SANDBOX or a spin for a bad respin.
- Cleanse OUTPUT_DOWN ×2 off your best slice.
- Take Good over Perfect unless your Perfect hook (a Breaker double resolve) is worth the +2 block.

**P2, weak play:**
- Ignores the pair rule and takes two Overflows (≈ 40 at T3).
- Lets OUTPUT_DOWN ×2 sit on the main damage slice.
- Chases Perfects for no hook, feeding the block.
- At Heat ≥ 50 the global +1 resistance absorbs a 1-tick nudge, so the nudge needs 2 ticks (1 RAM extra).

## 8. Systems needed

| N# | Use | Fallback |
|---|---|---|
| N1, N2 | FLAT amounts × tier factor; `hp_by_tier` | none for N2 (data field) |
| N3 | Threshold park at 0.48 | the phase still triggers; test without the floor |
| N4, N19 | Enrage; per-phase metrics | n/a |
| N6 | Proof of Delivery listener | drop it; P2 loses its Perfect tax |
| N8, N9 | OUTPUT_DOWN ×N via Cite | today's PARASITE as OUTPUT_DOWN ×2, no stacking |
| N11 | Needles at 0 / 12 | use 0 / 15 |
| N12 | Slice sizes 3–6 | 5-tick, 6-slice wheels (below) |
| N13 | Fixed escort, removed by the override | escort docked and left alone |

ORBIT and MULTIPLY already exist.

**Data-only fallback:**
- P1: Shim 8 / Shim 8 (escort) / Null / Overflow 14 / Shim 6 / Null.
- P2: needles 0 and 15, Shim / Overflow / Cite / Null / Overflow / Shim.
- No listener, and PARASITE used for Cite.
- The narrow Overflow becomes a normal 5-tick slice with a Perfect, so it keeps the drift question but loses the double-Overflow trap.

## 9. Delta vs today

- **Kept:** the corporation, the single ORBIT 2 needle, the Courier Drone escort, and the Shim and Overflow identity.
- **Changed:**
  - HP 132 → 61 / 74 / 94 / 120. At T3 that is −29 % against the 112 band ceiling.
  - One flat wheel becomes two designed wheels.
  - A second phase with a second needle, an uneven pair, Cite with OUTPUT_DOWN and the Proof of Delivery listener are new.
  - Slice sizes vary.
- **heat_effects: retire.**
  - Heat already acts through the global modifiers: elites more frequent at 25, +1 enemy resistance at 50.
  - A bespoke per-enemy effect would add hidden state and break the phase budget.

## 10. Predicted sim check

There is no Meridian row in the baseline (it covers Solace only), so this is an estimate. The nearest comparison is the Solace elite Recall Unit at 20.2 turns at T3.
- **Turns:** P1 ≈ 3.4 and P2 ≈ 3.4, total ≈ 6.8 at T3 (94 / 14). p90 ≈ 9.
- **Win %:** T1 97, T2 95, T3 91, T4 84. Two Overflows at T4 are 2.2× damage on a 12 base, which punishes missed pair-breaking.
- **Why:** 132 HP / 14 DPT ≈ 9.4 turns overran the 6–8 target. 94 HP lands on about 7.

## 11. Open questions

Q: ORBIT is read as a +2 drift applied at resolve, because the start-of-turn respin randomizes the wheel. Is that the intended meaning of "readable ahead"?
Q: Should the +2 BLOCK Proof of Delivery tax (once per turn) be larger, or does it stay a small tax that only matters to Perfect-hook builds?
Q: Does OUTPUT_DOWN ×2 on the player's best slice feel too close to the Halcyon mini-boss's Citation stacking? Should Meridian use TIER_DOWN instead?
Q: Should the P2 needle gap (12) stay fixed, or narrow per tier (for example 9 at T4)?
Q: Does the escort, removed by the override, count as destroyed for Daemons and rewards (Q7 in the design questions)?
