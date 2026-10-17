<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__customs_scanner; status ok; tokens in 6628 cache-write 0 cache-read 32585 out 10365; cost $0.062. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, layout arithmetic):** the "centred on 2 / 7 / 11…" sentence is deleted. The layout is now given as explicit start/end ticks, in the critic's order: Scan 5 (0-4), Priority 3 (5-7), Null 4 (8-11), Seizure 4 (12-15), Bulwark 6 (16-21), Scan 5 (22-26), Null 3 (27-29). Sizes re-added: 5+3+4+4+6+5+3 = 30. I enumerated all 30 rotations to get exact read frequencies, replacing the wrong "ticks 9-12 = Null, 13-16 = Seizure" claim. One correction to the critic: tick 11 is the Null slice's W edge, not a G edge, because a 4-tick slice maps W G G W.
- **Issue 2 (BLOCKER, HP arithmetic):** the budget is now dpt × 3.5 × a stated needle factor of 1.1, minus per-turn sustain × 1.0/1.3/1.69/2.2 × 3.5, with every step shown. The unexplained "2.4" is gone. `hp_by_tier` = [30, 36, 46, 58], with the T3 floor clamped to the band. Where a full ×2 for two needles conflicts with the R2 normal band, the band wins (it is validated). This is flagged in Q1.
- **Issue 3 (MAJOR, sustain):** stated explicitly. Bulwark is read 0.3 times per turn (derived), so sustain is 1.8 × tier factor per turn. That is 20 % of the reference dpt at T1 and 22 % at T4.
- **Issue 4 (MAJOR, weak question):** the question is reframed. Seizure is exposed on 8 of 30 rotations, and a 1-tick nudge clears most of them, so the choice is not luck. The question is now "can I spend the free nudge to move the hazard needle, without putting the other needle onto Priority or Seizure?" I verified the geometry by enumeration.
- **Issue 5 (MAJOR, INFECT):** Priority is `SliceType.INFECT` carrying a `DRAIN_RAM 2` extra effect and no status. It deals 0 damage. This is labeled as such.
- **Issue 6 (MAJOR, intake):** Seizure OVERFLOW 14→10 and Scan SHIM 9→5, both applied. Unsteered intake is about 4.7 per turn, and about 3 for a reference player who uses the free nudge. The unsupported "99 %" win rate is replaced by estimates marked as unmeasured.
- **Issue 7 (NIT):** "Kill in 3 turns" no longer depends on Perfects. The garbled "needle count applies only…" sentence is rewritten.
- **Critic Q "two needles for L1-2?":** kept as Q2, because a designer ruling is needed.
- **Critic Q "published needle factor":** adopted as the constant 1.1 and raised as Q1.

# customs_scanner: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. **Corporation:** Meridian.
- **Layers:** L1-2 teaching. It is the first enemy that teaches "the sub-tick map matters on a hostile wheel."
- **The one question:** *"Where do I spend the free nudge so the hazard lands on a W edge or a harmless slice, without feeding the other needle?"*
  - The scanner has 2 needles at uneven ticks 0 and 11 (R10).
  - Seizure is a 4-tick slice with no Perfect (W G G W), and Priority is a 3-tick slice.
  - Seizure is read on 8 of 30 rotations, and there is always a nearby rotation where it is not.
  - The scanner never reads Seizure and Priority together (see §2).
- **Shortening answer:**
  - Nudge or spin the wheel so Seizure and Bulwark are off both needles.
  - Then the scanner only deals chip damage, and the player's hits land unblocked.
  - Ignoring it costs about 10 HP more per fight.

## 2. Phase plan (single phase, no threshold)

| Field | Value |
|---|---|
| Phase | 1 of 1, no parked floor (last phase) |
| Needles | 2, at ticks 0 and 11 (uneven; gap 11, N11) |
| Hub | none, so no Hub Breach target |
| Statuses / parasites | none |
| Listeners | none |

**Layout** (cumulative boundaries, sizes sum to 30):

| # | Slice | Size | Ticks | Map | Effect |
|---|---|---|---|---|---|
| 1 | Scan | 5 | 0-4 | W G P G W | SHIM 5 FLAT (×enemy damage factor 1.0 / 1.3 / 1.69 / 2.2) |
| 2 | Priority | 3 | 5-7 | G P G | INFECT slice, no status; extra_effects DRAIN_RAM 2 (RAM is not tier-scaled). 0 damage |
| 3 | Null | 4 | 8-11 | W G G W | nothing |
| 4 | Seizure | 4 | 12-15 | W G G W (no Perfect) | OVERFLOW 10 FLAT |
| 5 | Bulwark | 6 | 16-21 | W W G G W W | BLOCK 6 FLAT |
| 6 | Scan | 5 | 22-26 | W G P G W | SHIM 5 FLAT |
| 7 | Null | 3 | 27-29 | G P G | nothing |

Sum: 5+3+4+4+6+5+3 = 30.

**Exact read table.** Needle A reads tick r and needle B reads tick (r+11) mod 30, for wheel rotation r = 0…29.

| Rotations | A reads | B reads |
|---|---|---|
| r = 0 | Scan (W edge) | Null (W edge, tick 11) |
| r = 1-4 | Scan | Seizure |
| r = 5-7 | Priority | Bulwark |
| r = 8-10 | Null | Bulwark |
| r = 11 | Null | Scan |
| r = 12-15 | Seizure | Scan |
| r = 16-18 | Bulwark | Null |
| r = 19-21 | Bulwark | Scan |
| r = 22-23 | Scan | Scan |
| r = 24-26 | Scan | Priority |
| r = 27-29 | Null | Null |

**Frequencies per turn** (uniform start-of-turn respin):

| Slice | Rotations | Per-turn read rate |
|---|---|---|
| Seizure | 8 (r 1-4, 12-15) | 0.27 |
| Scan | 20 slice-reads | 0.67 |
| Priority | 6 | 0.20 |
| Bulwark | 9 | 0.30 |

Seizure and Priority are never read together, and Seizure is never read by both needles.

**Nudge hazards:**
- At r = 0, needle B is on tick 11 (Null, W edge). A +1 rotation puts it on Seizure's W edge (tick 12, 5 damage at ×0.5), and +2 puts it on a G tick (full 10).
- At r = 12-15, a −1 to −4 nudge pulls needle A off Seizure but may place B on Scan or A on Null.

No transition: single phase.

## 3. Sustain and intake
- **Sustain (one source: Bulwark BLOCK 6 FLAT):**
  - Bulwark is read 0.30 times per turn (table above), so expected block is 0.30 × 6 = 1.8 per turn at T1.
  - Bulwark reads W W G G W W, so the true average is lower (about ×0.67); 1.8 is the upper bound.
  - Block is enemy-owned and R2-scaled by the tier factor: 1.8 / 2.3 / 3.0 / 4.0 per turn at T1-T4.
  - Against the reference dpt [9, 11, 14, 18]: **20 % / 21 % / 22 % / 22 %**, under the 30 % cap.
  - A single read blocks 6 against 9 dpt (67 %). It is rare and steerable.
- **Intake per turn, T1, unsteered** (tier-weighted: Scan W/G/P/G/W averages ×0.8, Seizure W G G W averages ×0.75):
  - Scan: 0.67 reads × 5 × 0.8 = 2.7
  - Seizure: 0.27 reads × 10 × 0.75 = 2.0
  - Total **≈ 4.7 per turn**, plus 0.4 RAM drained per turn (0.20 × 2).
- **Intake with the reference player** using the free nudge to clear Seizure: **≈ 3 per turn**, about 10 per 3.5-turn fight against a 45-60 HP operative. Above 0, and the teaching cost is visible but not punishing.

## 4. HP by tier (R2 normal band, 1 phase)
Budget = `reference_dpt[t]` × 3.5 × needle factor − (sustain per turn × tier factor × 3.5).

**Needle factor = 1.1.** A full ×2 for two needles (the pointer rule) would give 63 HP at T1, against a 28-36 band that is validated. I take 1.1 as a stated constant for two-needle normals; see Q1.

| Tier | dpt × 3.5 × 1.1 | Sustain (1.8 × factor × 3.5) | Budget | Band | `hp_by_tier` |
|---|---|---|---|---|---|
| T1 | 34.7 | 6.3 | 28.4 | 28-36 | **30** |
| T2 | 42.4 | 8.2 | 34.2 | 34-44 | **36** |
| T3 | 53.9 | 10.7 | 43.2 (clamp 44) | 44-56 | **46** |
| T4 | 69.3 | 13.9 | 55.4 (clamp 56) | 56-70 | **58** |

Each value is the arithmetic result (or the band floor, where the result falls below it) plus about 2 HP for a turn where the player's slice is not a damage landing. Today's 50 HP is replaced.

## 5. Enrage
None. Normals have it off (R4), and a 3-4 turn fight does not need it.

## 6. Buffs and counter Exploits
Not applicable (normals only).

## 7. Counterplay
- **Good player:**
  - Read the preview at the start of the turn, then use the free nudge to move Seizure and Bulwark off both needles.
  - Check the other needle before committing the nudge. Rotating A off Seizure can put B on Bulwark or Priority.
  - Land the player's own damage when Bulwark is off the needles.
  - Cleanse is not needed, since there are no statuses.
  - Takes ≈ 3 per turn and finishes in 3-4 turns.
- **Weak player:**
  - Only manages their own wheel, takes a Seizure 10 (up to ×2.2 at T4) once or twice, and loses RAM to Priority.
  - Still wins, but with about 10 more damage taken. That is the teaching moment.
- **Over-correction:** nudging by 1 from r = 0 hands B a Seizure W tick. Nudges can create a hazard as well as remove one.

## 8. Systems needed
- **N12** (variable slice sizes, sub-tick map) for the 3-, 4- and 6-tick slices.
  - **Fallback:** six 5-tick slices (Scan, Priority, Null, Seizure, Bulwark, Scan) with needles 0 and 15, the existing legal evenly-spaced rule. The no-Perfect teach is lost.
- **N11** (pointers on any tick) for needles 0 and 11. **Fallback:** 0 / 10 or 0 / 15.
- **N1** (flat amounts × tier damage factor). **Fallback:** today's `output_scale`.
- **N2** (`hp_by_tier`). **Fallback:** one HP value with a multiplier.
- Everything else exists: SHIM, OVERFLOW, DEFRAG (BLOCK), INFECT with an extra DRAIN_RAM effect. No N6, N8, N10.

## 9. Delta vs today
- **Today:** one needle, six 5-tick slices (Shim 9, Priority, Defrag 6, Overflow 14, Shim 9, Null), 50 HP.
- **Changes:**
  - A second needle at tick 11.
  - Seven slices of 3-6 ticks, and the Overflow slice becomes the no-Perfect Seizure.
  - Shim 9→5 and Overflow 14→10, since two needles carry the total. Priority drain 3→2.
  - `hp_by_tier` [30, 36, 46, 58] replaces the single HP.
- **Kept:** the Priority RAM-drain identity, one Defrag-style sustain source, `cycle_reward` 15, id and description.
- **heat_effects:** none authored today, none added.

## 10. Predicted sim check
There is no Meridian baseline row (the baseline covered Solace only), so these are wheel-derived estimates.
- **Turns:** about 3.3 at T1, 3.5 at T2-T3, 3.8 at T4. HP is set at about 3.5 reference-damage turns, and Bulwark adds a fraction of a turn.
- **Win %:** about 98 % at T1, 97 % at T2, 94 % at T3, 90 % at T4. Intake is about 10-16 per fight against 45-60 HP, rising with the tier factor.
- **Why:** HP falls from 50 to 30 at T1, which cuts about 1.5 turns, and the second needle roughly doubles intake. Total damage taken is therefore similar to today but is now steerable.

Q: Should two-needle normals use a published needle factor of 1.1 in the R2 budget, or does the pointer rule's full ×2 warrant a band exception (T1 63 HP)?
Q: Is a two-needle normal appropriate for L1-2 teaching, or should the second needle wait for L5-6?
Q: Should Seizure be flagged in the intent UI as "cannot be Perfected" so players learn the sub-tick map?
Q: Is a 2 RAM drain per Priority hit meaningful, given RAM is banked to 12?
Q: Should the 0 / 11 needle gap be a Meridian-wide pattern or reserved for this scanner?
