<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__permit_office; status ok; tokens in 15769 cache-write 0 cache-read 32007 out 3147; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# permit_office: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. Halcyon. Appears in both L1-2 (teaching) and L5-6 (pressure) at T1-T3.
- **Working concept:** "Backlog". The office is a queue clerk: it stamps a **PENDING** counter on your wheel with Citations, then **cashes the whole queue** with one big slice that is bigger the more of your slices carry the stamp.
- **The one question:** *"How many of your slices are stamped when the Processing slice reaches my pointer?"* The answer that shortens the fight is clearing or dodging stamps (Cleanse, Encrypt, steering its needle away from Citation) and **killing it before the third turn**, when the backlog peaks.
- **Distinct from siblings:** Parking Warden / Patrol Unit are plain damage; Surveillance Mast is a sensor; the Permit Office is the only normal that punishes your *stamp count* instead of your landing.
- **Current wheel problem:** SANDBOX 5 twice, SHIM 8 twice, a Citation and a Null, plus a drone every other turn. That is a vague shield-and-chip wheel. Its HP of 46 is inside the T2 band but is its only tuned value.

## 2. Phase plan
**Single phase, no threshold.** No floor (R3 not used), no transition, no cleanse.

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses | OUTPUT_DOWN ×1 per Citation (R8, N8/N9). Fallback: PARASITE status (halves, existing). |
| Listeners | none |
| Satellites | **dropped** (the civic drone spawn is removed so the wheel stays readable) |

**Layout (sizes sum to 30):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Citation | 5 | Pointer target; OUTPUT_DOWN ×1 on 1 random non-NULL slice of yours (SlicePick RANDOM_NON_NULL), no damage |
| 2 | Filing (SHIM) | 4 | 4 damage FLAT (×tier factor), no Perfect tick |
| 3 | Processing | 7 | Damage 3 FLAT × (1 + number of your slices carrying OUTPUT_DOWN), separate hits (`hits_per_target_status`, N20), max 4 hits |
| 4 | Stamp Pad (BLOCK) | 5 | BLOCK 6 FLAT |
| 5 | Citation | 5 | as slot 1 |
| 6 | Null | 4 | nothing |

Sum: 5+4+7+5+5+4 = 30.

Why these sizes: Processing is the 7-tick slice (W W G P G W W), so it is the easiest to land on. That is deliberate: the threat is *readable and hard to avoid by landing alone*, and the answer is your stamp count, not the offset. The 4-tick Filing cannot be Perfect-boosted and is the cheap chip.

**Needle path:** the pointer starts at a random tick each turn (start-of-turn respin), so the fight is not scripted; the player reads the intent and chooses a nudge.

## 3. Sustain and intake
- **Sustain:** none. The only defensive slice is the Stamp Pad (BLOCK 6, temporary), which absorbs a hit rather than healing. Sustain = 0, well under the 30 % cap (0.3 × reference 11 = 3.3 per turn at T2).
- **Intake per turn** (reference player, random landing; slice weights by tick: Cit 10/30, Filing 4, Proc 7, Pad 5, Null 4; T2 factor ×1.3):

| Stamps on you | Processing damage (T2) |
|---|---|
| 0 | 3 × 1.3 ≈ 4 |
| 1 | ≈ 8 |
| 2 | ≈ 12 |
| 3 | ≈ 16 (cap of 4 hits ≈ 16) |

- Expected per turn at turn 1 with 0 stamps: Filing 4/30 × 5 + Proc 7/30 × 4 ≈ 0.7 + 0.9 ≈ **1.6** (Citation is 0 damage). By turn 3 with ~2 stamps: 0.7 + 7/30 × 12 ≈ **3.5**. Average ≈ **2.5 per turn**, above 0. Lethal only if ignored; the swing is what makes it a question.
- Note: this intake is low on purpose for a normal. The stamp build-up is the threat.

## 4. HP by tier
R2 normal band, 1 phase: budget = reference dpt × 3.5 turns − sustain (0).

| Tier | dpt | Budget | Band | Chosen HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28–36 | **32** |
| T2 | 11 | 38.5 | 34–44 | **38** |
| T3 | 14 | 49 | 44–56 | **48** |
| T4 | 18 | 63 | 56–70 | **62** |

(Today 46 flat; ×tier multiplier ran 64–128 at T3 in the band survey.) Because it has one needle, the pointer rule does not scale the HP.

## 5. Enrage
None (normal, R4). The 3-4 turn target is enforced by the stamp ramp: Processing gets worse each turn you ignore it.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** on turn 1, read where the pointer is. If it sits on Citation, spend the free nudge to push to Null or Stamp Pad. Use Cleanse or Encrypt on a stamped slice before Processing arrives. Burst: with HP 38 at T2, two good turns win it; a fast kill never sees a 3-stamp Processing.
- **Weak player:** ignores stamps because Citation "does no damage", accepts two or three Citations, and is then hit by a 4-hit Processing for 16. They also feed the Stamp Pad turns by attacking into BLOCK 6 with small hits.
- **Teaching value (L1-2):** the first fight with a visible stack-counting threat, and a gentle intro to Cleanse and Encrypt.

## 8. Systems needed
- **N8** (×N stacks) and **N9** (OUTPUT_DOWN): for stamps. **Fallback:** existing PARASITE status, 1 per slice (halves output). Processing counts PARASITE slices instead. Fully data-only except the count.
- **N20** (`hits`, `hits_per_target_status`): for Processing. **Fallback:** fixed 3 hits of 3 damage with no scaling; this loses the question, so not recommended.
- **N12** (slice sizes 4 / 5 / 7): **fallback** is the 5-tick layout with Filing and Processing as normal slices; the sizes are a tuning tool and the design survives without them.
- **N1** (flat × tier factor), **N2** (`hp_by_tier`).

## 9. Delta vs today
- **Removed:** SANDBOX 5 ×2 and the civic drone spawn (`spawns`), because satellites plus shields obscured the question.
- **Added:** Processing (stamp-count hits), Filing, Stamp Pad.
- **Kept:** Citation (now with OUTPUT_DOWN, ×1), Null, `cycle_reward = 15`, id, corporation.
- **HP:** 46 flat → `hp_by_tier` [32, 38, 48, 62].
- **heat_effects:** none present today; none added.

## 10. Predicted sim check
No baseline row exists (Solace only), so this is estimated from the wheel.
- **Turns:** about 3.5 mean at the reference player (T1 ~3.0, T4 ~3.8), p90 ≤ 5.
- **Win %:** T1 ≥ 97 %, T2 ≥ 96 %, T3 ≈ 92 %, T4 ≈ 88 %, because the intake is low early and the risk is a stamp snowball for a player who ignores it.
- **Threat per turn:** ≈ 2.5 > 0, passes.
- **Sustain turns:** 0 heal turns, passes.
- At T4 the risk is only Processing at 4 hits; watch the sim for the 4-hit cap being reached too often.

## 11. Q:
- Q: Should Processing count only stamped slices, or also CORRUPTED ones (so Solace and Halcyon interact)?
- Q: Is a hit cap of 4 right, or should it be 3 so a fully stamped wheel stays survivable at T1?
- Q: Should Citation target a random slice or the slice under the pointer (more readable, less variance)?
- Q: Is dropping the civic drone acceptable, or should it return as one fixed Clerk satellite on the Stamp Pad (N13)?
- Q: Does Cleanse need a guaranteed supply at L1-2 for this fight to teach rather than punish?
