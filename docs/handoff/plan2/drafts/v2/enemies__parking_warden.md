<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__parking_warden; status ok; tokens in 6888 cache-write 0 cache-read 32585 out 4133; cost $0.031. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, fallback layout unspecified; stamp delivery unclear):** The fallback is now fully specified as six 5-tick slices (Shim 6, Citation, Defrag 6, Overflow 10, Shim 6, Null; 6 × 5 = 30). Every Citation in the main layout is now UNDER_POINTER, so the delivery rule is the same on all slices. The Perfect on the 3-tick Citation is addressed: it only means the pointer is dead-centre. The stamp lands on every landing, so it adds no precision.
- **Issue 2 (BLOCKER, 3.5 figure underived; T4 labeling):** I dropped the 3.5 figure and now show the derivation. The weighted intake is 3.3 at T1. The tier scaling is applied once, to flat amounts only: 3.3 × 1.3 / 1.69 / 2.2 = 4.3 / 5.6 / 7.3.
- **Issue 3 (MAJOR, HP budget contradiction):** Sustain is 0 and BLOCK is not sustain. HP is now 32 / 38 / 48 / 62, with no block credit and no "round up to the band" step.
- **Issue 4 (MAJOR, hub leftover):** The hub row is now "none". The "ticket counter" mention is deleted from §1.
- **Issue 5 (MAJOR, N8 and fallback):** N9 is required. N8 is needed only if stacks above 1 are used, and the Warden only applies ×1. The fallback is specified (see Issue 1).
- **Issue 6 (MAJOR, unavoidable random stamp):** Slice 2 is now UNDER_POINTER, so the random stamp is gone. Every Citation is readable and steerable, and Cleanse is no longer required. The cost of an unanswered ×1 is quantified in §3.
- **Issues 7 and 8 (NITs):** The turn loss is stated as about 14 HP at the 3.5-turn mark. The kill-in-3 line is kept (32 / 3 ≈ 10.7).
- **Designer rulings:** None conflict. R8 applies status on a WEAK landing by default, and I keep that.

# parking_warden: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, no enrage. Halcyon. It is the **L1-2 Citation teacher** (first Halcyon fight, T1 Sites). At L5-6 it is a T2-T3 filler with the same shape.
- **The one question:** "Which of your slices can you afford to have cut by a Citation, and can you steer the stamp onto a slice you don't need?"
- Its Citation applies OUTPUT_DOWN ×1 (−25 %), not the old half-output PARASITE. A single stack is survivable, and every Citation stamps the slice under your pointer, so you can see it coming.
- **Answer that shortens the fight:** nudge its pointer to a Citation's WEAK edge or to Null, and burst while its only defense is off the pointer. Nudge your own wheel so a slice you don't need sits under your pointer when a Citation lands.
- **Answer that lengthens it:** letting the stamp land on your Overflow or Shim and then trading at reduced output.
- This is the pure single-stack Citation teacher. Other Halcyon normals should not own Citation-first design.

## 2. Phase plan (one phase, no threshold, no floor)

| Item | Value |
|---|---|
| Needles | 1, fixed at tick 0 |
| Hub rule | none (pure wheel; L1-2 baseline) |
| Statuses used | OUTPUT_DOWN ×1 (R8), via Citation |
| Parasites | none |
| Listeners | none |

**Layout (sizes sum to 30). Damage and block are FLAT, × the tier damage factor (R2):**

| # | Slice | Ticks | Effect | Quality map |
|---|---|---|---|---|
| 1 | Shim 6 | 5 | 6 damage to pointer target | W G P G W |
| 2 | Citation | 4 | 3 damage + OUTPUT_DOWN ×1 on your slice under your pointer (UNDER_POINTER) | W G G W |
| 3 | Defrag 6 | 5 | BLOCK 6 FLAT | W G P G W |
| 4 | Overflow 10 | 4 | 10 damage | W G G W (no Perfect) |
| 5 | Shim 6 | 5 | 6 damage | W G P G W |
| 6 | Citation | 3 | 3 damage + OUTPUT_DOWN ×1 on your slice under your pointer | G P G |
| 7 | Null | 4 | nothing | W G G W |

Sum: 5+4+5+4+5+3+4 = **30**.

- Both Citations use the same rule, so there is one thing to learn. They differ in size: the 4-tick one has WEAK edges, and the 3-tick one is all GOOD/PERFECT, so it is harder to nudge off.
- The Perfect on slice 6 only means the pointer is dead-centre. The stamp applies on any landing, so it adds no precision.
- Overflow is 4 ticks with no Perfect, so a 1-tick nudge can halve it (WEAK = 5 damage).
- BLOCK 6 is the only defense. There is no heal.

## 3. Sustain and intake
- **Sustain:** 0. BLOCK is not sustain in R2 terms. The 30 % cap is trivially met.
- **Intake per turn at the reference player (T1, factor 1.0).** The start tick is uniform. Raw chance by tick share:
  - Shim 6 ×2 (10 ticks): 10/30 × 6 = 2.0
  - Citation 3 ×2 (7 ticks): 7/30 × 3 = 0.7
  - Overflow 10 (4 ticks): 4/30 × 10 = 1.33
  - Defrag, Null: 0
  - Raw total ≈ 4.0.
- **Tier weighting.** A WEAK landing halves damage. Shim edges are 2 of 5 ticks WEAK, so Shim 2.0 × 0.8 = 1.6. Overflow edges are 2 of 4 WEAK, so 1.33 × 0.75 = 1.0. Citation: 0.7 (the Citation 3 is all G/P, and the 4-tick Citation's edges are not reduced here, a small overcount). Total **≈ 3.3 per turn at T1**.
- **Tier scaling (flat amounts × the factor, applied once):** T2 4.3 · T3 5.6 · T4 7.3. Over 3.5 turns that is about 12 HP at T1.
- **Cost of an unanswered Citation:** OUTPUT_DOWN ×1 is −25 % of one slice's output. If it sits on a slice that deals about 6 per landing, it costs about 1.5 damage each time that slice resolves, roughly 1-2 damage over the fight. It is a tax, not a wall.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget = `reference_dpt[t]` × 3.5 turns × 1 player needle − sustain (0) × 3.5:

| Tier | dpt | Arithmetic | **hp_by_tier** |
|---|---|---|---|
| T1 | 9 | 9 × 3.5 = 31.5 | **32** |
| T2 | 11 | 11 × 3.5 = 38.5 | **38** |
| T3 | 14 | 14 × 3.5 = 49 | **48** |
| T4 | 18 | 18 × 3.5 = 63 | **62** |

All values are inside the band. This replaces today's flat 48.

## 5. Enrage
**None** (normal class, R4). A 3-4 turn fight needs no clock.

## 6. Buffs and counter Exploits
Not a boss; n/a.

## 7. Counterplay
- **Good player:** reads the pointer at turn start. If it sits on a Citation, they nudge their own wheel so a slice they don't need (Defrag or Null) is under their pointer when the stamp lands. They burst on turns when its needle sits on Defrag or Null. They use the free nudge to push its needle off the 4-tick Overflow, whose WEAK edges make a 1-tick nudge halve it. A Cleanse is a bonus, not a requirement.
- **Weak player:** leaves the stamp on their Overflow or Perfect slice, spends RAM nudging its needle onto Shim 6 instead of Null, and does not use the free nudge. They take about 14-18 damage over a 5-6 turn fight, which is not lethal.
- **Fight-length lever:** every Defrag or Null turn you deny is a free turn for your damage. Killing in 3 turns takes about 11 per turn at T1 (32 / 3 ≈ 10.7).

## 8. Systems needed
- **N1** amount modes (FLAT × tier factor) and **N2** `hp_by_tier` + `enemy_damage_by_tier`.
- **N9** OUTPUT_DOWN as a status. N8 (×N stacks) is needed only if stacks above 1 are ever used. The Warden applies ×1 only.
- **N12** variable slice sizes and sub-tick maps (3-, 4- and 5-tick slices).
- **Data-only fallback (specified):** six 5-tick slices, all W G P G W: Shim 6, Citation, Defrag 6, Overflow 10, Shim 6, Null (6 × 5 = 30). Citation keeps today's PARASITE status (halves the slice) and UNDER_POINTER. This loses the Perfect-less Overflow edge and the 3-tick slice. HP needs N2 or a flat tier multiplier.

## 9. Delta vs today
- **Kept:** id, corporation, the Citation concept, the Shim / Citation / Defrag / Overflow / Null wheel, one needle at tick 0, `cycle_reward` 15.
- **Changed:**
  - Six slices become seven, with variable sizes.
  - Citation changes from "half output until cleansed" to OUTPUT_DOWN ×1 (−25 %), always UNDER_POINTER.
  - Shim 9 → 6 and Overflow 14 → 10, with no Perfect on Overflow.
  - Citation now carries 3 damage, so it has nonzero threat.
  - HP 48 flat → 32 / 38 / 48 / 62.
- **Description text:** "Writes Citations: your slice under the pointer runs at −25 % until you cleanse it."
- **heat_effects:** none exist on the file; none added.

## 10. Predicted sim check
There is no Halcyon baseline row (the sweep covered Solace only), so this is an estimate from the wheel.
- **Turns:** about 3.5 mean at the step-0 skill, p90 ≤ 5. About 3.0 at skill 1.0.
- **Win %:** T1 ≈ 98 %, T2 ≈ 97 %, T3 ≈ 94 %, T4 ≈ 92 %. Intake of 3.3-7.3 per turn over about 3.5 turns is 12-26 HP, well inside a 45-60 HP operative.
- **Why:** the only defense is one 6-BLOCK slice and there is no heal, so the HP-band kill falls in the 3-4 turn window. Citations are a tax, not a wall.

## 11. Q:
- Q: Should the first Halcyon fight force a fixed opening (needle on the 3-tick Citation) as a tutorial beat, or stay on the normal random respin?
- Q: Does OUTPUT_DOWN ×1 on a WEAK landing still apply (R8 default yes)? If not, the 4-tick Citation's WEAK edges are a free dodge.
- Q: With every Citation now UNDER_POINTER, is the 4-tick versus 3-tick difference enough to keep two Citation slices, or should they merge?
