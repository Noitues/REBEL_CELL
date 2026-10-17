<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__conveyor_warden; status ok; tokens in 6774 cache-write 0 cache-read 32585 out 7266; cost $0.046. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, Perfect status and 0.9×):**
  - Section 2 now states the maps: 6-tick Shim and Defrag are W W G G W W (no Perfect), the 4-tick Overflow and Null are W G G W (no Perfect), and only the 5-tick Priority and 5-tick Shim read W G P G W.
  - The unexplained 0.9× is removed. Intake now uses the average output per slice from the tick maps (6-tick 0.667, 4-tick 0.75, 5-tick 0.8).
- **Issue 2 (BLOCKER, tier scaling):**
  - Intake is recomputed from the sub-tick maps and scaled by [1.0, 1.3, 1.69, 2.2] for every tier.
  - Sustain is recomputed per tier, not reused from T1.
  - The v1 sum "2.6 + 1.4 + 0.5" ignored the Shim quality weights. The corrected T1 total is 3.9, not 4.5.
  - The tier intake and the fight totals are now consistent with the factors.
- **Issue 3 (BLOCKER, sustain arithmetic):**
  - Sustain is now per-turn block times 3.5 turns. At T1 it is 1.2 × 3.5 = 4.2 (the Defrag's 6 BLOCK times its 6/30 landing share, taken as an upper bound with no quality discount). T2 is 5.5, T3 is 7.1 and T4 is 9.2.
  - The R2 budget results (27.3 / 33.0 / 41.9 / 53.8) fall at or just below the band floors, so I clamp HP to the floors: [28, 34, 44, 56].
  - This replaces v1's [30, 38, 48, 62]. Those values exceeded the budget, and the critic's "keep HP" note conflicts with its own corrected arithmetic. I follow the arithmetic.
- **Issue 4 (MAJOR, orbit and R10):**
  - The stale multiple-of-5 fallback is removed.
  - The orbit is no longer called "existing". It is tagged N11 plus NEW: normal-class pointer orbit.
  - The fallback is a fixed pointer.
- **Issue 5 (MAJOR, sticky and predictable claims):**
  - Dropped both claims.
  - The orbit applies after the start-of-turn respin, so only the current landing is shown.
  - The question is now "Which slice does the needle reach after this turn's steering?"
  - The dwell times are corrected: 2 turns on a 6-tick slice, 1.33 on a 4-tick, 1.67 on a 5-tick.
  - Dwell times only matter when the respin is skipped (Freeze), which is now stated openly.
- **Issue 6 (MAJOR, Priority fallback):**
  - The N20 misuse is removed.
  - The fallback is a SHIM-type slice with an extra DRAIN_RAM effect (data-only).
  - I do not repeat the unverified "today it is a damage-less INFECT" claim. It is flagged "verify against the .tres".
- **Issue 7 (NIT, Null window):** the contradiction is removed. A 4-tick Null can be held only one turn per steering, and the counterplay text now says exactly that.
- **Issue 8 (NIT, unsourced deltas):**
  - The current-.tres values are marked "per v1 reading, verify".
  - The Heavy Load threat is stated as 14 at T1 and 18 / 24 / 31 at T2–T4, not "16 at T2".
- **Critic Q on Priority drain scaling:** decided, it stays flat at 2. R2 scales heal, block, shield and hits, and RAM is a player resource.

# conveyor_warden: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, Meridian.
  - L1-2: it teaches "the needle is not where the wheel starts".
  - L5-6 at T3-T4: it is a pressure enemy, because Priority's RAM drain hurts a RAM-starved player.
- **The one question:** *"Which slice does its needle reach after this turn's steering?"* The conveyor needle is offset 3 ticks after the respin. The player sees the current landing and has a free nudge or a card to change it.
- **Answer that shortens the fight:** sort the belt. Move its wheel so the needle lands on Null or a WEAK edge instead of Heavy Load, then burst on the turns that can't hurt you. A player who ignores the preview eats Heavy Load (14 at T1) on 13 % of landings.
- **Distinct from siblings:**
  - Customs Scanner: reads or reveals.
  - Cargo Hauler: HP-heavy.
  - Drone Dispatcher: satellites.
  - Route Optimizer: respin or lock.
  - Tariff Collector: economy.
  - The Warden is the only plain "orbit" normal. It has no Weight and no respin tricks.

## 2. Phase plan (single phase, no thresholds, no floor)
**Needle:** 1, with `pointer_orbit_per_turn = 3`. The start-of-turn respin runs first, then the orbit shifts the needle by 3, so the player always sees the real landing. The orbit only adds forward predictability when the wheel is not respun (e.g. the player Freezes it); then the needle keeps moving 3 per turn and the next landing is readable.

**Layout (6 + 4 + 5 + 6 + 5 + 4 = 30):**

| Order | Slice | Ticks | Sub-tick map | Effect (mode) |
|---|---|---|---|---|
| 0 | Shim | 6 | W W G G W W (no Perfect) | 8 damage (FLAT) |
| 1 | Overflow "Heavy Load" | 4 | W G G W (no Perfect) | 14 damage (FLAT) |
| 2 | Priority | 5 | W G P G W | 3 damage + drain 2 RAM (FLAT) |
| 3 | Defrag | 6 | W W G G W W (no Perfect) | 6 BLOCK (FLAT) |
| 4 | Shim | 5 | W G P G W | 8 damage (FLAT) |
| 5 | Null | 4 | W G G W | nothing |

- Only the two 5-tick slices, Priority and the second Shim, have a Perfect tick. The player's hooks matter only if the needle lands there.
- Priority becomes a real attack with a RAM tax (per v1's reading of today's slice; verify). Its drain is flat 2 at every tier.
- **Hub rule, statuses, parasites, listeners:** none. This is a pure geometry question.

## 3. Sustain and intake
- **Sustain:** a single source, Defrag 6 BLOCK (FLAT × tier factor). It is block, not heal.
  - The upper bound per turn is 6/30 × 6 × factor (no quality discount).
  - That gives 1.2 / 1.56 / 2.03 / 2.64 per turn at T1–T4, or 13 / 14 / 14.5 / 14.7 % of the reference dpt (9 / 11 / 14 / 18).
  - All are under the 30 % cap.
  - Worst case (a guaranteed Defrag every turn) absorbs 6 × factor against the reference 9 × 1.0 at T1. A player who lets that happen is not steering.
- **Intake per turn (unsteered, expected, T1):** each slice's tick share × amount × average output of its map (6-tick 0.667, 4-tick 0.75, 5-tick 0.8).
  - Shim 6: 6/30 × 8 × 0.667 = 1.07
  - Shim 5: 5/30 × 8 × 0.8 = 1.07
  - Heavy Load: 4/30 × 14 × 0.75 = 1.40
  - Priority: 5/30 × 3 × 0.8 = 0.40 (plus 0.33 RAM per turn)
  - Total ≈ **3.9 damage per turn** at T1.
  - With factors: **3.9 / 5.1 / 6.7 / 8.7** at T1–T4.
  - Over a 3.6-turn fight that is about 14 HP at T1 and about 24 at T3.
- **Steering:**
  - Null is only 4 ticks, so it is a one-turn dodge, not a hold.
  - Best steering keeps intake near 1–2 per turn at T1.
  - It never reaches 0, because every other slice but Defrag hurts. The intake is above 0, unlike Dosage Dispenser's 0.05.

## 4. HP by tier (R2 Normal band, 1 phase)
Budget: `reference_dpt_by_tier` × 3.5 − sustain × 3.5.

| Tier | dpt | Gross (×3.5) | Sustain/turn | Sustain × 3.5 | Budget | Band | HP |
|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 1.20 | 4.2 | 27.3 | 28–36 | 28 |
| T2 | 11 | 38.5 | 1.56 | 5.5 | 33.0 | 34–44 | 34 |
| T3 | 14 | 49.0 | 2.03 | 7.1 | 41.9 | 44–56 | 44 |
| T4 | 18 | 63.0 | 2.64 | 9.2 | 53.8 | 56–70 | 56 |

- `hp_by_tier` = [28, 34, 44, 56]. The budget falls just under each band floor, so HP is clamped to the floor.
- Reference fight length is HP / (dpt − sustain): 28/7.8 = 3.6, 34/9.44 = 3.6, 44/11.97 = 3.7, 56/15.36 = 3.65 turns.
- **Flat amounts × [1.0, 1.3, 1.69, 2.2]** (rounded):
  - Heavy Load is 14 / 18 / 24 / 31.
  - Shim is 8 / 10 / 14 / 18.
  - Block is 6 / 8 / 10 / 13.
- The RAM drain stays flat 2.

## 5. Enrage
**None** (the normal default is off). The fight lasts 3–4 turns and its only sustain is a small block.

## 6. Buffs and counter Exploits
Not applicable (normals only).

## 7. Counterplay
- **Good player:**
  - Reads the landing at turn start. If the needle sits on Heavy Load, spend the free nudge (1 tick) to push it to a W edge, or 2 ticks to reach Shim's neighbor. A 4-tick Heavy Load has only G G in the middle, so even a 1-tick nudge cuts it in half.
  - Burst on the turn the needle sits on Null or a WEAK edge, and hit a Perfect only if the hook is worth it (only the two 5-tick slices have one).
  - Spend the nudge or card on the Defrag turn, so the player damage is not wasted into 6 × factor BLOCK. Avoid Priority when RAM is short.
  - Freeze its wheel only if the next landing (after +3) is harmless. The Freeze removes the respin, so the needle moves exactly 3 and the next landing is known.
- **Weak player:**
  - Ignores the preview, eats Heavy Load and the Shims, and pours damage into the Defrag, stretching the fight to 5–6 turns.
  - Freezes without checking where +3 lands.
  - Spends RAM on extra nudges and then eats the Priority drain.

## 8. Systems needed
| Need | System | Fallback |
|---|---|---|
| Variable sizes (4, 5, 6) and sub-tick maps | N12 | Six 5-tick slices (the 6th is Null). The Overflow then has a Perfect, which is weaker as a teaching tool. Acceptable. |
| Flat amounts × tier factor, `hp_by_tier` | N1, N2 | Hand-set HP now and today's scale. |
| Orbit on a normal, pointer on any tick | N11 + NEW: normal-class pointer orbit (GDD 2.11 lists Orbit as a boss pointer behavior) | A fixed pointer. The layout still moves through the start-of-turn respin only. The design survives; the "conveyor" flavor is lost. |
| Priority as damage + RAM drain | existing SHIM-type slice with an extra DRAIN_RAM effect | None needed (data-only). |

## 9. Delta vs today
Per v1's reading of the current .tres (verify before building).
- **Kept:** the id, the orbit of 3, the slice set (Shim, Shim, Overflow, Defrag, Priority, Null) and `cycle_reward = 15`.
- **Changed:**
  - HP 54 → [28, 34, 44, 56].
  - Slice sizes become uneven (6/4/5/6/5/4).
  - Overflow drops from 16 to 14 at the base tier.
  - The second Shim drops from 10 to 8.
  - Priority gains 3 damage.
  - The two Shims are no longer adjacent.
- **`heat_effects`:** none today and none added.

## 10. Predicted sim check
No baseline row exists (the baseline covers Solace only), so these are wheel-based estimates.
- **Turns:** about 3.6 at the reference player, p90 ≤ 5.
- **Win %:** T1 about 99 %, T2 about 98 %, T3 about 94 %, T4 about 91 %. There is no enrage and no heal, and the worst-case intake is under 30 HP.
- **Why:** HP matches the net budget, and the only sustain is a small block that steering dodges. Today's 54 HP would take about 6 turns, so this fight is shorter and its question clearer.

## 11. Open questions
Q: Is a normal-class orbit worth N11 plus a new normal-class pointer behavior, given it only matters when the respin is skipped (Freeze)? Or should the Warden be a fixed-pointer enemy that teaches uneven slice sizes instead?
Q: Is a 4-tick Overflow with no Perfect legible enough, or should the intent plate show a "no Perfect" marker?
Q: Should the sub-tick map be shown on the enemy's intent plate in L1-2 as well as on the loadout screen?
