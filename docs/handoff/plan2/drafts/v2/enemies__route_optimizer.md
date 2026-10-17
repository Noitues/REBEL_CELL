<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__route_optimizer; status ok; tokens in 6074 cache-write 0 cache-read 32585 out 12316; cost $0.071. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, HP budget):**
  - The 32/40/50/64 row is deleted and 34/42/54/68 is gone.
  - §4 now shows the full 2-needle budget: 9 × 3.5 × 2 = 63 at T1, then 77 / 98 / 126.
  - HP is set to the R2 band tops, **36 / 44 / 56 / 70**, and the shortfall is stated: the cap is deliberate, and it shortens the fight (see §10 and Q1).
  - The "Null and Defrag slices offset it" argument is removed.
- **Issue 2 (BLOCKER, layout and symmetry):**
  - The "3-fold symmetric" claim is deleted.
  - The pair table is recomputed over all 30 respin rotations for the new uneven layout (needles 0 and 13).
  - Enemy needle position is random per respin, and the intake estimate now says so. The player steers only by nudging the enemy wheel: the free nudge moves it 1 tick, and each extra nudge costs 1 RAM.
  - The intake math includes the WEAK halving, which v1 ignored.
- **Issue 3 (MAJOR, question):** §1 is rewritten per the critic's text. The "line your best slice at both needles" idea is gone, because the player's wheel has one pointer and each hit simply lands once per enemy needle.
- **Issue 4 (MAJOR, R10/R11):**
  - Needles are now at ticks 0 and 13 (uneven).
  - The slices are 6 / 4 / 5 / 5 / 5 / 5 (sum 30).
  - 13 is chosen so the two needles can never both read a Perfect tick: Perfect centres sit at 12, 17, 22 and 27, none 13 apart.
  - The "multiples of 5" remark is deleted.
- **Issue 5 (MAJOR, sustain and intake):**
  - The "block is paid by the player" line is removed. Block is shown as the only defensive source, at about 1.7 per turn.
  - T1 intake is about 8 and T4 about 17.
  - The Overflow is capped at a base of 11 (under the critic's cap of 12) from the start. The T4 worst case is stated in §3 as design, not as a sim note.
- **Issue 6 (NIT):** N11 and N12 are tagged, with a data-only fallback.
- **Issue 7 (NIT):** §9 now ties today's 48 HP to the missing needle bonus and the missing band.
- **Triage rows (both BLOCKERs):** covered by the issue 1 and 2 changes above.
- **Kept:** the pair-table presentation, zero sustain, and no heat_effects.
- **Ruling check:** no designer ruling conflicts with these fixes. R2's band is binding and I stayed inside it; the sim may raise it.

# route_optimizer: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, no enrage. **Corporation:** Meridian.
- **Layers:** L1-2 teaching (the first enemy that shows "two needles read the same wheel"), and a T3-T4 pressure filler in L5-6.
- **The one question:** *"Two needles read my enemy's wheel at once, and one pair reads 18 damage. Can I nudge it so the pair lands on Null + Defrag or on WEAK edges?"*
- **Shortening answer:** kill it before the big pair rolls. Burst, and spend the free nudge on the enemy wheel only when the roll is bad. The needles are 13 ticks apart, so they can never both be Perfect. A 1-tick nudge usually turns the worst pair into a WEAK read.

## 2. Phase plan (single phase, no threshold)

| Field | Value |
|---|---|
| Phase | 1 "Route Plan" (100 % → 0 %, no floor) |
| Needles | 2 at ticks **0 and 13** (uneven, FIXED; R10) |
| Hub rule | none |
| Statuses / parasites / listeners | none |

**Layout (sizes sum 6+4+5+5+5+5 = 30; tick ranges from wheel tick 0):**

| Slot | Ticks | Size | Sub-tick map (R11) | Slice | Effect (FLAT, × tier damage factor) |
|---|---|---|---|---|---|
| A | 0-5 | 6 | W W G G W W | Shim | 7 damage |
| B | 6-9 | 4 | W G G W | Null | nothing |
| C | 10-14 | 5 | W G P G W | Overflow | 11 damage |
| D | 15-19 | 5 | W G P G W | Shim | 7 damage |
| E | 20-24 | 5 | W G P G W | Defrag | BLOCK 5 FLAT |
| F | 25-29 | 5 | W G P G W | Shim | 7 damage |

For an enemy slice, WEAK halves the output and Good and Perfect are 1.0×. 14 of the 30 ticks are WEAK, so the average multiplier is about 0.77.

**Pair table over all 30 respin rotations** (needle 1 at tick r, needle 2 at r+13; raw base damage before WEAK):
- **18 (A+C or C+F): 8 rotations** (r = 0, 1, 12, 13, 14, 27, 28, 29). This is the danger pair.
- **14 (A+D or D+F): 9 rotations** (r = 2-5, 15-19).
- **11 (Overflow + Defrag): 2 rotations** (r = 10, 11).
- **7, with Null or Defrag as the other needle: 6 rotations** (r = 6, 20-22, 25, 26).
- **0 damage: 5 rotations** (r = 7-9, 23, 24), all Null + Defrag.

The mean is 334/30 ≈ 11.1 raw. Applying the 0.77 WEAK average gives about 8.6 unsteered.

**Steering.** A 1-tick nudge of the enemy wheel gives each rotation r the best of r−1, r, r+1. That cuts the raw mean from 11.1 to about 8.8, or about 6.8 after WEAK. Steering costs the player's free nudge, so the reference player does it about half the time.

## 3. Sustain and intake
- **Sustain:** no heal and no hub. The only defense is BLOCK 5 on E, which sits under a needle on 10 of 30 rotations (never both needles). That is about 1.7 expected block per turn, roughly 19 % of the T1 reference damage (9), under the 30 % cap. It is deducted conservatively in §10.
- **Intake per turn at the reference player:**
  - T1 ≈ 8 (the blend of 8.6 unsteered and 6.8 steered).
  - T2 ≈ 10 (×1.3).
  - T3 ≈ 14 (×1.69).
  - T4 ≈ 17 (×2.2).
- This is clearly above 0.
- **Worst single resolve at T4:** 18 × 2.2 ≈ 40, only on a rotation with both needles on good ticks of the big pair (8 of 30 rotations before steering). One 1-tick nudge turns most of these into a WEAK read, so the worst case is real but answerable.

## 4. HP by tier (R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70)
Phase budget = `reference_dpt_by_tier` × 3.5 × needles hit. Both enemy needles take each of the player's pointer attacks (GDD 2.7), so the factor is 2. Sustain deduction is about 1.7 per turn at T1, which is small.

| Tier | Full budget | Band top | **HP set** |
|---|---|---|---|
| T1 | 9 × 3.5 × 2 = 63 | 36 | **36** |
| T2 | 11 × 3.5 × 2 = 77 | 44 | **44** |
| T3 | 14 × 3.5 × 2 = 98 | 56 | **56** |
| T4 | 18 × 3.5 × 2 = 126 | 70 | **70** |

- **Decision:** HP is capped at the band top, because the band is binding (R2 validation). The 2-needle bonus is therefore not fully applied.
- **Consequence:** at reference damage the fight is shorter than 3-4 turns (§10). The sim decides whether to raise the band for 2-needle normals.

## 5. Enrage
None (normal class, R4).

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** read the preview and, on a bad roll, spend the free nudge on the enemy wheel to move the pair onto a Null + Defrag or WEAK read. Otherwise spend it on their own Perfect. Burst the 36-70 HP down fast, since every turn risks an 18 pair.
- **Weak player:** chases a Perfect on their own wheel and ignores the enemy needles, taking the 18 pair at full strength. Or they spend extra RAM nudges steering and never build damage. They finish in 4-5 turns and take 30-40 damage at T1.

## 8. Systems needed
- **N2** (`hp_by_tier`, `enemy_damage_by_tier`).
- **N11** (needle at tick 13).
- **N12** (slice sizes 6 and 4 and the sub-tick map).
- **Data-only fallback:**
  - Keep six 5-tick slices in the same order and put the needles at 0 and 15.
  - The pairs become 14 / 0 / 18 / 14 / 0 / 18 by slice rotation, a mean of about 9 raw.
  - The "never both Perfect" property is lost, since 0 and 15 are both centres, and the question gets less interesting.
  - The single `hp` field is set to 36 with the global damage scale.
- N1 is not needed (BLOCK is FLAT, today's behavior).

## 9. Delta vs today
- **HP:** 48 → 36 / 44 / 56 / 70 by tier. Today's 48 exceeds the T1 band and ignores the 2-needle phase budget.
- **Layout:** today Shim 8, Shim 8, Overflow 14, Defrag 5, Shim 8, Null in 6 × 5 ticks, needles 0 and 15 → the new 6-4-5-5-5-5 layout above with needles 0 and 13.
- **Amounts:** Shim 8 → 7 and Overflow 14 → 11 (capped under 12), so the pair stays inside the intake targets.
- **Kept:** id, description and `cycle_reward` 15.
- **heat_effects:** none exist; none added.

## 10. Predicted sim check
There is no baseline row for Meridian; this is estimated from the wheel.

- **Expected mean turns at the reference skill:** about 2.4 at T1 (36 HP against 18 damage per turn from two needles, minus about 1.7 block). That is below the 3-4 target, a known cost of staying inside the band.
- **At tester skill (3.2-5.0 per turn):** about 3.5-6 turns.
- **Win rates:** T1 ≈ 98 %, T2 ≈ 97 %, T3 ≈ 93 %, T4 ≈ 88 %.
- **Why T4 is lower:** intake of about 17 per turn with a worst resolve of about 40 is lethal to a weak player. The fight is short, so cumulative damage stays moderate.
- **If the sim confirms the short fight:** raise the band for 2-needle normals rather than lowering the Overflow.

## 11. Q:
- Q: Should the normal band allow extra HP for 2-needle enemies (R2 says "proportionally more"), so the fight actually lasts 3-4 turns at the reference player?
- Q: Is a worst-case resolve of about 40 at T4 acceptable for a normal, or should the Overflow base drop to 9?
- Q: Is a two-needle Meridian L1-2 teacher too hard for a first fight; should Customs Scanner own that role?
