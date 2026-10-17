<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__mirror_script; status ok; tokens in 5796 cache-write 0 cache-read 32585 out 10823; cost $0.063. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, geometry):** I rebuilt the pair logic from the real geometry.
  - Needles at 0 and 15 sit on slots i and i+3, so the pairs are fixed: A = slots 0+3, B = 1+4, C = 2+5.
  - A 5-tick spin moves to an adjacent pair (A→B→C→A); it never reaches a "twin".
  - I deleted "a 15-tick or 10-tick shift sends both needles to the twins" and "force both needles onto Null/Block".
  - I added a real Null+Block pair (C), so "blank one needle" exists.
  - Nudges are ±1 tick, so the free nudge changes the pair only from a WEAK edge, and the draft now says so. The critic's "5-tick nudge" is also wrong.
  - Both needles always read the same offset, so they share a precision tier.
- **Issue 2 (BLOCKER, Block and intake math):**
  - Enemy Block is the enemy's own defense. It absorbs part of the player's hits and is not intake.
  - It is now counted as the single sustain source and checked against the 30 % cap (§3).
  - Intake is derived from pair probabilities and a stated steering assumption, not "half the time".
- **Issue 3 (MAJOR, HP budget):**
  - HP is now derived from R2: dpt × 3.5 × 2 needles, minus the Block absorbed. Needles hit the body regardless of the slice read, so the critic's "effective 1.0 needle" is rejected.
  - The result exceeds the 1-needle normal band. R2 itself says more needles get proportionally more HP, so I flag a validator exception (Q1).
  - Today's T3 value: 50 changes to 72.
- **Issue 4 (MAJOR, filler and mirror theme):**
  - The "not covered here" filler is removed.
  - The mirror theme is the symmetric wheel itself.
  - Copying the player's wheel (GDD 8.5) stays with the Mirror elites (Q4).
- **Issue 5 (MAJOR, dependencies):**
  - OUTPUT_DOWN ×1 needs N9, and N8 only by build order. No ×N display is needed.
  - The fallback delta is named: PARASITE is −50 % against −25 %, so Citation is applied once and its odds are noted.
- **Issue 6 (MAJOR, sim check):** turns are derived from net damage per turn, and slice numbers are shown scaled by the tier factors.
- **Issue 7 (NIT, "Q11"):** removed; the answer is stated (yes, WEAK still applies it).
- **Issue 8 (NIT, layers and Overflow):** Overflow drops 16 → 14 and Shim 9 → 8, and WEAK-edge reading halves both needles. This keeps L1–2 gentle, and L5–6 pressure comes from the tier scaling.
- **Citation target (no critic issue):** the target changes from random non-NULL to the slice under your pointer. This is deterministic, so the preview equals the result.
- **Kept:** no sustain beyond Block, no listeners, nonzero intake, and Solar Flare cut.

# mirror_script: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, rebel_cell. It teaches in L1–2 and applies pressure in L5–6 through tier scaling.
- **The one question:** *"Both needles always read the same slice offset, 15 ticks apart. Do you sit on the pair that hurts you, the pair that blocks your damage, or the pair that gives you a clean burst?"*
- **Answer that shortens the fight:** steer to pair B (Shim + Citation), which has no Block. It costs about 8 damage, but your hits land twice at full value. Pair C (Null + Block) costs 0 but absorbs part of your burst.
- **Mirror theme:** the wheel is symmetric, but the pairs are different, so reading one needle never tells you the other.

## 2. Phase plan (1 phase, no thresholds; R3 does not apply)

| Field | Value |
|---|---|
| Needles | 2, FIXED at ticks 0 and 15 |
| Hub rule | none |
| Statuses | Citation → OUTPUT_DOWN ×1 (R8) on your slice under your pointer |
| Listeners | none |

**Layout (six 5-tick slices = 30; no N12):**

| Slot | Ticks | Slice | Effect (FLAT × tier damage factor) | Pair |
|---|---|---|---|---|
| 0 | 5 | Overflow | 14 damage | A |
| 1 | 5 | Shim | 8 damage | B |
| 2 | 5 | Null | nothing | C |
| 3 | 5 | Block | BLOCK 6 | A |
| 4 | 5 | Citation | OUTPUT_DOWN ×1 on your slice under your pointer (no damage) | B |
| 5 | 5 | Block | BLOCK 6 | C |

Sizes: 6 × 5 = 30 ✓.

- **Pairs:**
  - A = Overflow + Block
  - B = Shim + Citation
  - C = Null + Block
  - A random respin gives each pair 1/3.
- **Same offset:** both needles read the same offset, hence the same tier. A WEAK edge landing halves everything on both (Overflow 7, Block 3). A 2-tick nudge off Perfect therefore cuts the damage and the Block together.
- **Moving between pairs:**
  - Rotation by 5 moves A→B→C→A, so a 5-tick spin in either direction reaches any other pair.
  - The free ±1 nudge changes the pair only from an edge (offset ±2, nudged outward).

**Scaled numbers (×1.0 / 1.3 / 1.69 / 2.2):**

| Value | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Overflow 14 | 14 | 18 | 24 | 31 |
| Shim 8 | 8 | 10 | 14 | 18 |
| Block 6 | 6 | 8 | 10 | 13 |

**Transition:** none. There is a single phase, so nothing is parked or cleansed.

## 3. Sustain and intake
- **Sustain: one source, Block.**
  - It absorbs your damage at 2/3 of unsteered turns (pairs A and C).
  - Expected absorbed per turn: 6 × 2/3 × factor = 4.0 / 5.2 / 6.8 / 8.8.
  - Cap: 30 % of the reference damage on 2 needles: 0.3 × 18 = 5.4 / 0.3 × 22 = 6.6 / 0.3 × 28 = 8.4 / 0.3 × 36 = 10.8.
  - Actual share: 22 % / 24 % / 24 % / 24 % ✓.
- **Intake at the reference player:**
  - Unsteered: (14 + 8 + 0) / 3 = 7.3 at T1.
  - Steering assumption: with cards or nudges, the reference player dodges A on 60 % of A's turns, split evenly to B and C.
  - Probabilities: A 0.133, B 0.433, C 0.433.
  - Mean: 0.133 × 14 + 0.433 × 8 = 1.9 + 3.5 = **5.3 per turn at T1**.
  - Scaled: 5.3 / 6.9 / 9.0 / 11.7 per turn at T1–T4. This is above 0, and pair B's Citation also costs 25 % on one slice.
- **HP lost over about 3.4 turns:** 18 / 23 / 30 / 40.

## 4. HP by tier (R2, 2 needles)
Formula: dpt × 3.5 turns × 2 needles, minus the expected Block absorbed over 3.5 turns.

| Tier | dpt | Gross (×3.5×2) | Block absorbed (×3.5) | hp_by_tier |
|---|---|---|---|---|
| T1 | 9 | 63 | 14 | **48** |
| T2 | 11 | 77 | 18 | **58** |
| T3 | 14 | 98 | 24 | **72** |
| T4 | 18 | 126 | 31 | **92** |

- Net damage per turn is gross/3.5 minus the absorbed amount. For example, T1 is 18 − 4.0 = 14, and 48 / 14 = 3.4 turns ✓. T4 is 36 − 8.8 = 27.2, and 92 / 27.2 = 3.4 ✓.
- These values are above the 1-needle normal band (28–36 … 56–70). R2 explicitly gives more needles proportionally more HP, so I ask for a validator allowance (Q1).

## 5. Enrage
None (normal; R4).

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads the pair at turn start.
  - On A, spends a 5-tick spin or a card to leave the pair, or uses the free nudge when sitting on a WEAK edge. Taking the WEAK edge halves the Overflow anyway.
  - Prefers B for the burst (no Block, 8 intake). Takes C to be safe, and accepts the Block absorbing about 6 of the damage.
  - Kills in 3 turns.
- **Weak player:**
  - Spends the free nudge on a Perfect landing; one tick does not change the slice and does not change the pair, so it changes nothing.
  - Sits on A and eats the Overflow.
  - Ignores Citation and plays a Perfect-hook card into an OUTPUT_DOWN slice.
  - Bursts into C's Block and finishes in 5 turns.

## 8. Systems needed
- **N9** (OUTPUT_DOWN) for Citation. By build order it follows N8, but only one stack is used, so no ×N badge is needed.
  - **Fallback:** today's PARASITE as data. It is −50 %, harsher than OUTPUT_DOWN ×1 (−25 %), so Citation applies it only on pair B.
- N1: not needed, all FLAT.
- **N2:** the hp_by_tier field, plus a validator band that scales with needles (Q1).
- Everything else uses existing data and systems.

## 9. Delta vs today
- **Kept:**
  - id, corporation, needles 0/15, the Citation slice and a Null slice
  - the single phase
  - cycle_reward 15
- **Changed:**
  - Solar Flare is removed (OVERCLOCK → CORRUPTED chains become RAM-doubling under R9, too punishing for a normal).
  - The layout is rearranged into three fixed pairs, and a second Block slice is added.
  - Overflow 16 → 14 and Shim 9 → 8.
  - hp becomes hp_by_tier [48, 58, 72, 92].
  - Citation PARASITE → OUTPUT_DOWN ×1 on the slice under your pointer.
- **heat_effects:** none exist; none added.

## 10. Predicted sim check (estimate; no baseline row)
- **Expected turns:** about 3.4 at the reference player at every tier (net damage per turn tracks HP, see §4). About 2.7 at skill 1.0.
- **Win %:** T1 ≈ 99 %, T2 ≈ 97 %, T3 ≈ 94 %, T4 ≈ 85 %.
  - Why: intake is 11.7 per turn at T4 (about 40 HP over the fight), against 18 reference damage per turn.
  - T4 does not need the ≥ 90 % criterion.
- The heal-turn criterion passes (no heal).

## 11. Q:
- Q: Is a validator band scaled by needle count (2 needles ≈ 1.5–2× the 1-needle band) acceptable, or should this enemy drop to 1 needle and take the band?
- Q: Is Block 6 as the single sustain enough defense, or should pair C's Block be a SHIELD (lingering, cap 15) so a burst has to chew through it?
- Q: Is Overflow 14 at T1 acceptable for L1–2 teaching, or should L1 drop it to 10?
- Q: Should this normal ever copy the player's wheel (GDD 8.5), or is that reserved for the Mirror elites?
