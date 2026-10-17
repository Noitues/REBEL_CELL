<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__permit_office; status ok; tokens in 6141 cache-write 0 cache-read 32585 out 3845; cost $0.029. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, random pick):** Citation no longer picks a random slice. It stamps the slice under your own pointer (SlicePick UNDER_POINTER), which is deterministic and visible in the preview. Q3 is closed. The RANDOM_NON_NULL pick is removed everywhere in the draft.
- **Issue 2 (MAJOR, intake arithmetic):** recomputed with Processing = 3 × (1 + stamps) × tier factor, hit cap 4 at T1-T2 and 5 at T3-T4. Factors 1.0 / 1.3 / 1.69 / 2.2 are stated, and the table and the expected value are shown below. BLOCK is also subtracted.
- **Issue 3 (MAJOR, BLOCK marking):** Stamp Pad is now "BLOCK 6 FLAT (× tier factor)".
- **Issue 4 (HP above budget at T1):** T1 changed from 32 to 31, which is inside the 28–36 band and under the 31.5 budget. T2, T3 and T4 are unchanged (38 / 48 / 62).
- **Issue 5 (pressure, one version for both layers):** the tier-scaled hit cap (4 → 5) and a Perfect bonus raise pressure. Citation is cut to 4 ticks, so harmless ticks fall from 19/30 to 17/30 (Pad 5 + Null 4 + Citation 4 + Citation 4). Whether L1-2 and L5-6 should differ is deferred to Q.
- **Issue 6 (dominated "ignore stamps and burst"):** Processing now has a `perfect_multiplier` of ×2 (N20), so landing precision matters, and stamps stay a real cost. Stamping the slice under *your* pointer also creates a self-reinforcing loop: a stamped slice under your pointer is the one you are about to land on.
- **Issue 7, 8, 9 (nits):** kept, because they are correct. The `spawns` removal is still stated and listed as unverified against the .tres in §9.
- **Critic Q's:** hit cap now scales with tier (answered). Encrypt: it absorbs the first Citation on that slice, so it is a real counter, not an auto-win (see §7).
- **Ruling conflict:** none.

# permit_office: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. Halcyon. L1-2 (teaching) and L5-6 (pressure) at T1-T3.
- **Working concept:** "Backlog". The office stamps a **PENDING** mark (OUTPUT_DOWN ×1) on the slice under your pointer with Citations, then cashes the queue with a big Processing slice that hits once per stamped slice.
- **The one question:** *"How many of your slices are stamped when Processing reaches my pointer, and is the stamped slice the one I need?"* Shortening answers: Cleanse or Encrypt before Processing, steering its needle off Citation, landing a Perfect of your own on Processing's turn to deny it, or killing it by turn 3-4.
- **Distinct from siblings:** Parking Warden and Patrol Unit are plain damage; Surveillance Mast is a sensor. This is the only normal that punishes stamp count.

## 2. Phase plan
**Single phase, no threshold.** No floor, no transition, no cleanse.

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses | OUTPUT_DOWN ×1 per Citation (R8; N8/N9). Fallback: PARASITE status (halves, existing). |
| Listeners | none |
| Satellites | dropped (civic drone spawn removed) |

**Layout (sizes sum to 30):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Citation | 4 | OUTPUT_DOWN ×1 on the slice under **your** pointer (UNDER_POINTER), no damage. No Perfect tick (G G W W layout is not used; 4-tick default W G G W). |
| 2 | Filing (SHIM) | 4 | 4 damage FLAT (× tier factor) |
| 3 | Processing | 7 | 3 damage FLAT (× tier factor) × (1 + your stamped slices), separate hits, cap 4 hits at T1-T2 and 5 at T3-T4 (`hits_per_target_status`, N20). **Perfect: ×2** (`perfect_multiplier`, N20). |
| 4 | Stamp Pad (BLOCK) | 6 | BLOCK 6 FLAT (× tier factor) |
| 5 | Citation | 4 | as slot 1 |
| 6 | Null | 5 | nothing |

Sum: 4 + 4 + 7 + 6 + 4 + 5 = 30.

Processing is the 7-tick slice (W W G P G W W), the easiest to hit. The threat is readable, and your stamp count and your own precision are the answer. Landing a Perfect on Processing is a risk only for the enemy's own reading: its Perfect fires when its needle sits on the center tick, which you can nudge away.

**Needle path:** the start-of-turn respin is random, as in all fights; the player reads the intent and chooses a nudge.

## 3. Sustain and intake
- **Sustain:** none (BLOCK absorbs, it does not heal). Cap would be 0.3 × 11 = 3.3 per turn at T2; sustain is 0.
- **Processing damage, T2 (factor 1.3):**

| Stamped slices | Hits | Damage |
|---|---|---|
| 0 | 1 | 3.9 |
| 1 | 2 | 7.8 |
| 2 | 3 | 11.7 |
| 3+ | 4 (cap) | 15.6 |

 Other factors scale linearly: T1 ×1.0 (3 / 6 / 9 / 12), T3 ×1.69, T4 ×2.2 (cap 5 hits: 3 × 5 × 2.2 = 33 at 4+ stamps).
- **Expected intake at T2, per resolve:** Filing 4/30 × 5.2 = 0.69; Processing 7/30 × damage. Turn 1 (0 stamps): 7/30 × 3.9 = 0.91, total **1.6**. Turn 2 (about 1 stamp, as 8/30 of landings stamp): 7/30 × 7.8 = 1.82, total **2.5**. Turn 3 (about 2 stamps): 7/30 × 11.7 = 2.73, total **3.4**. BLOCK subtraction is small: Pad is 6/30 of the turns and only for defense it grants, so I ignore it. Average over 3 turns ≈ **2.5 per turn** at T2, above 0. It rises with stamps, so a player who lets stamps pile up takes spikes of 11.7-15.6.
- At the Perfect ×2, a single spike is up to 31 at T2 with 3 stamps. That is rare (7/30 for the slice, 1/7 of it Perfect), but it is why stamps matter.

## 4. HP by tier
R2 normal band, 1 phase: budget = reference dpt × 3.5 − sustain (0).

| Tier | dpt | Budget | Band | Chosen HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28–36 | **31** |
| T2 | 11 | 38.5 | 34–44 | **38** |
| T3 | 14 | 49 | 44–56 | **48** |
| T4 | 18 | 63 | 56–70 | **62** |

One needle, so no pointer-rule scaling. Today: 46 flat.

## 5. Enrage
None (normal, R4). The ramp comes from the stamps: Processing gets worse each turn you ignore it.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** on turn 1 read the pointer. If it sits on Citation, spend the free nudge to push to Null or Stamp Pad. Encrypt a slice you will land on: it absorbs the first stamp. Cleanse a stamped slice before Processing arrives. Burst: 38 HP at T2 is two good turns.
- **Weak player:** treats Citation as harmless because it does no damage, lets 2-3 stamps build (the stamps land on the slice they are about to use, so their own output drops 25 % per stamp), then eats a 3-4 hit Processing.
- **Teaching (L1-2):** the first visible stack-counting threat and an intro to Cleanse and Encrypt.

## 8. Systems needed
- **N8 / N9** (×N stacks, OUTPUT_DOWN). Fallback: existing PARASITE status, 1 per slice; Processing counts PARASITE slices. Data-only apart from the count.
- **N20** (`hits_per_target_status`, `perfect_multiplier`). Fallback: fixed 3 hits of 3 damage and no Perfect bonus. This loses the question, so not recommended.
- **N12** (sizes 4 / 6 / 7). Fallback: 5-tick layout with the same slices; the design survives.
- **N1, N2** (flat × tier factor, `hp_by_tier`).

## 9. Delta vs today
- **Removed:** SANDBOX 5 ×2 and the civic drone spawn (`spawns`). Not checked against the current .tres here.
- **Added:** Processing, Filing, Stamp Pad.
- **Kept:** Citation (now OUTPUT_DOWN ×1 on your pointer's slice), Null, `cycle_reward = 15`, id, corporation.
- **HP:** 46 flat → `hp_by_tier` [31, 38, 48, 62].
- **heat_effects:** none today; none added.

## 10. Predicted sim check
No baseline row (Solace only); estimated from the wheel.
- **Turns:** about 3.5 mean (T1 ~3.0, T4 ~3.8), p90 ≤ 5.
- **Win %:** T1 ≥ 97 %, T2 ≥ 96 %, T3 ≈ 92 %, T4 ≈ 88 %. Intake is low early; the risk is a stamp snowball.
- **Threat per turn:** ≈ 2.5 at T2 > 0. **Heal turns:** 0.
- Watch the sim for the 5-hit cap at T4 being reached too often.

## 11. Q:
- Q: Should Processing count CORRUPTED slices as well as stamped ones, so Solace and Halcyon interact?
- Q: Should L1-2 and L5-6 use different layouts, or only the tier HP and hit cap?
- Q: Is a Perfect ×2 on Processing too swingy at T4 (up to 66 with 4+ stamps)?
- Q: Should the civic drone return as one fixed Clerk satellite on the Stamp Pad (N13)?
- Q: Does Cleanse need a guaranteed supply at L1-2 for this fight to teach rather than punish?
