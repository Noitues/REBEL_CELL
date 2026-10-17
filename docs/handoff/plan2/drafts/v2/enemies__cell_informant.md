<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__cell_informant; status ok; tokens in 6086 cache-write 0 cache-read 32585 out 3788; cost $0.028. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, random Citation target):** changed. Citation now applies OUTPUT_DOWN ×1 to **your slice under your pointer** (`SlicePick.UNDER_POINTER`), so the preview equals the result and no RNG stream is needed. v1 Q3 is deleted.
- **Issue 2 (BLOCKER, intake arithmetic):** changed. Overflow is now 12 FLAT (12 / 16 / 20 / 26 by tier), giving about 4.0 at T1 (see below). The intake lines are rewritten so Shim is correctly listed as a damage source. The 4.0 total sits at the top edge of the 2-4 band; this is deliberate, and prepared play drops it to about 2.4.
- **Issue 3 (orbit claim):** changed. The false "Overflow right after Detour or Priority" claim is removed. The respin randomizes the start each turn, and the trail shows only the landing after that turn's 3-tick orbit. The question is reworded to "plan within the turn".
- **Issue 4 (layout rationale):** changed. The layout is reordered with a stated rationale. The Overflow is now flanked by Null and Citation, not Detour, and the single Perfect slice is the Null, not a threat.
- **Issue 5 (naming, RAM scaling):** changed. The slice is called SANDBOX everywhere, and the RAM drain is stated as not tier-scaled.
- **Issue 6 (unsupported win rates):** changed. T4 is lowered to about 85 %, and all rates are marked as estimates pending the step-0 sweep.
- **Issue 7 (orbit is existing):** changed. §8 now states that `pointer_orbit_per_turn` / ORBIT already exists.
- **Issue 8 (rounding rule):** changed. The rule is stated: flat × tier factor, rounded to nearest, with .5 rounding up.
- **Critic Qs:** the 7-slice busyness question is kept as a Q. The 2-per-turn orbit question is kept as a Q.
- **Kept, because the critic marked them strong:** HP by tier [32, 39, 50, 63], a single phase with no enrage and no sustain, and the data-only fallbacks.

# cell_informant: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage. **Corporation:** REBEL_CELL. **Layers:** L1-2 teaching; the first enemy a player meets whose needle moves after the respin.
- **Concept:** a snitch that tails your last move. Its reader orbits 3 ticks per turn (today's trait, kept, existing ORBIT behavior). After the start-of-turn respin, the trail shows **where its needle will land this turn**. The one question: **"The landing is visible now, so can you steer the dangerous slice (Overflow) onto a guarded turn, or off it?"**
- **Shortens the fight:** a player who reads the trail, nudges the Overflow landing to WEAK or to Null, SANDBOXes or BLOCKs when it can't be moved, and bursts when it lands on Null or SANDBOX. A player who ignores the trail eats the Overflow and a Citation.
- Siblings (Dead Drop, Echo Process, Mirror Script, Handler Proxy, Loyalty Test) are unchanged. The Informant owns **orbit-as-visible-landing** and a small status tax. No listener, no lock.

## 2. Phase plan

**Phase 1 "Tail" (100 → 0 %, no floor, the only phase)**

| Item | Value |
|---|---|
| Needle | 1 pointer at tick 0, `pointer_orbit_per_turn = 3`, trail shown. |
| Hub rule | none |
| Listeners | none |
| Statuses | OUTPUT_DOWN ×1 via Citation (N8/N9). Fallback: today's PARASITE. |

Layout: 7 slices, clockwise from tick 0.

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Shim | 5 | 8 damage (FLAT, × tier factor) |
| 2 | Priority | 4 | drain 2 RAM (FLAT, not tier-scaled) |
| 3 | SANDBOX | 4 | negates one of your attacks this turn |
| 4 | Null | 4 | nothing (the only 4-tick slice without a threat neighbor on both sides) |
| 5 | Overflow | 4 | 12 damage (FLAT, × tier factor) |
| 6 | Citation | 5 | OUTPUT_DOWN ×1 on your slice under your pointer (UNDER_POINTER) |
| 7 | Shim | 4 | 8 damage |

5+4+4+4+4+5+4 = 30.

- **Ordering rationale:** the Overflow sits between Null and Citation. A 1-tick nudge toward Null is a real option, while the other side costs a Citation. The cheap threats (Priority, SANDBOX) cluster so a weak landing there is harmless.
- 4-tick slices read W G G W (no Perfect). The 5-tick Shim and Citation keep a Perfect. A Perfect landing on Citation is the player's chance to see the status-tax slice at full strength, which is not a reward, so nudging off it is correct.
- The respin makes the start random each turn. The trail shows the landing after the 3-tick orbit. The player reacts within the turn with nudges and cards.
- **Transition:** none (single phase).

## 3. Sustain and intake
- **Sustain:** none (0, inside the 30 % cap of 2.7 per turn at T1).
- **Intake per turn at T1** (unprepared, weighted by ticks of 30):
  - Shim: 8 × 9/30 = 2.4
  - Overflow: 12 × 4/30 = 1.6
  - Total ≈ **4.0** HP per turn. Priority costs 2 RAM (4/30 weight), Citation a status (5/30), and SANDBOX and Null nothing. These carry no HP.
  - It is above 0, at the top of the L1-2 band of 2-4.
  - Prepared play (SANDBOX or BLOCK on the Overflow turn, nudge off Shim) ≈ 2.4.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget = `reference_dpt` × 3.5, single needle.

| Tier | dpt | Budget | Sustain | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 0 | **32** |
| T2 | 11 | 38.5 | 0 | **39** |
| T3 | 14 | 49 | 0 | **50** |
| T4 | 18 | 63 | 0 | **63** |

`hp_by_tier` = [32, 39, 50, 63]. Flat damage × [1.0, 1.3, 1.69, 2.2], rounded to nearest (.5 up): Shim 8 / 10 / 14 / 18; Overflow 12 / 16 / 20 / 26. A T4 Overflow of 26 is under half a 60-HP operative, so it is a hard lesson and not a one-shot.

## 5. Enrage
None. The class default is off for normals (R4), and the fight is 3-4 turns.

## 6. Buffs and counter Exploits
Not applicable: not a boss.

## 7. Counterplay
- **Good player:** after the respin, reads the trail. If it lands on Overflow, nudges it toward Null (a 1-tick nudge may suffice, since 4-tick slices run W G G W) or plays BLOCK or SANDBOX. If it lands on Citation, nudges off or lands their pointer on a slice they can afford to weaken. Bursts on Null and SANDBOX-adjacent turns. The fight ends in 3 turns.
- **Weak player:** ignores the trail, spends burst into the SANDBOX landing, and takes the Overflow at full value. A stacking Citation slows their finishing burst, and the fight reaches 5-6 turns.
- **Nudge tool:** nudging the Informant's wheel by 1-2 ticks is a within-turn fix, paid with the free nudge or RAM.

## 8. Systems needed
- **Orbit:** exists (`pointer_orbit_per_turn`, ORBIT). Data-only.
- **N1** (FLAT × tier factor): needed. Fallback: current `output_scale` scaling, data-only.
- **N2** (`hp_by_tier`): needed. Fallback: `hp` 50 with the flat multiplier.
- **N12** (variable slice sizes): needed for the 4/5 mix. Fallback: six 5-tick slices (drop the second Shim); it loses the rare-Perfect feel.
- **N8/N9** (OUTPUT_DOWN ×N): fallback is PARASITE (halve output), data-only.
- **N11:** not required (the needle starts at tick 0).
- No N6, N7 or N10.

## 9. Delta vs today
- **Kept:** the orbit of 3, Shim, Priority, Overflow, Citation, Null, and the REBEL_CELL identity.
- **Changed:**
  - 6 slices become 7, with 4-tick slices.
  - The Shim 10 slice becomes Shim 8 ×2.
  - Overflow 16 becomes 12 (flat) to meet the intake band.
  - Detour is renamed SANDBOX (R13).
  - Citation's status becomes OUTPUT_DOWN ×1 and targets the slice under your pointer (it was random).
  - `hp` 46 becomes `hp_by_tier` [32, 39, 50, 63].
- **heat_effects:** none exist on a normal; none added.

## 10. Predicted sim check
No baseline row exists for this enemy. All numbers are estimates pending the step-0 sweep.
- **Turns:** about 3.3 at T1-T2, 3.5 at T3-T4. p90 ≤ 5.
- **Win %:** T1 ≈ 97 %, T2 ≈ 95 %, T3 ≈ 91 %, T4 ≈ 85 %.
- **Why:** low HP, one needle, no sustain and a visible landing keep fights short. T4 is lower because the 26 Overflow plus a 18 Shim punish an unread turn. Threat per turn is above 0 at every tier.

## 11. Q:
- Q: Should the orbit be 2 per turn at L1-2 so the visible landing is easier to read?
- Q: Is a 7-slice wheel too busy for the first REBEL_CELL enemy?
- Q: Does a W G G W 4-tick slice make nudging too binary (a 1-tick nudge only moves between WEAK and GOOD)?
- Q: Is Priority (RAM drain 2) enough pressure alone, or should it become a RAM tax tied to CORRUPTED once N9 lands?
