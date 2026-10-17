<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__zoning_board; status ok; tokens in 8778 cache-write 0 cache-read 32585 out 16530; cost $0.095. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, P2 budget ×1.5 invented, table inconsistent):** The ×1.5 factor is deleted. The pointer rule makes a 2-needle P2 cost ×2, which puts an elite at 93/113/145/187 against a band of 56-72 / 68-88 / 88-112 / 112-144. R2's band validator wins, so P2 is now a **single-needle** phase and its budget is derived at ×1 in §4. The critic's "needle 2 mostly on Null" fix is rejected: a player's hit lands on every enemy pointer regardless of which slice the pointer reads, so a Null-parked needle does not reduce the hits that land on the Board. The 2-needle variant is kept as Q1.
- **Issue 2 (BLOCKER, "Shim 12 → 6 ticks", no-Perfect Shim, "Overflow 11-16"):** The leftover edit is removed. The 6-tick Shim is stated as W W G G W W with no Perfect, and the "narrow Good window / nudge to WEAK" talk is dropped. The Overflow position is now stated only by the tick check (14-19). All sizes are re-added to 30 in §2.
- **Issue 3 (BLOCKER, both needles on damaging slices at rotation 0):** This is moot with one needle in P2. The P2 layout also follows the critic's order (Shim 5 · Rezone 4 · Null 5 · Overflow 6 · Rezone 4 · Shim 6). The "exactly one needle is dangerous" claim is deleted.
- **Hub resistance 1 in P2 (critic Q1, issue 3):** Removed. P2 already taxes steering through TIER_DOWN, so there is no hub rule in either phase.
- **Issue 4 (MAJOR, drone contradiction):** The Civic Drone is kept. It is fixed on slot 1 in both phases (R12) and is not cleared by the override. It soaks at most one hit on 1 turn in 6, which §4 absorbs into its tolerance. Q3 still asks whether a replaced drone counts as destroyed.
- **Issue 5 (MAJOR, Hotfix odds):** Corrected to 4/30 = 0.133 per turn, times the 0.75 average tier multiplier. The expected heal is derived in §3 (≈0.3 HP per turn at T3).
- **Issue 6 (MAJOR, intake hand-waved, ≈21 at the critic's numbers):** Intake is now shown by slice probability × tier multiplier × flat amount × tier factor. P1 ≈ 3.2 and P2 ≈ 5.4 per turn at T3. Overflow is lowered 16 → 12 and Shim 8 → 6. Citation gets 3 chip damage so the P1 intake is above 0 and in range.
- **Issue 7 (MAJOR, T4 82 % with no fix; Variance rule paragraph):** The "Variance rule" paragraph is deleted. The T4 prediction is re-derived at about 90 %, and §10 gives a lever (Overflow 12 → 10) if the sim disagrees.
- **Issue 8 (NIT, heat_effects):** Rewritten as a plain decision, retire, with no claim about the file.
- **Issue 9 (NIT, "no elites in L1-2"):** Replaced with the GDD 4.2 guarantee (about 1 elite per layer in layers 3-6).
- **Kept, because the critic marked them strong:** the territory concept, with P1 Citation stacks carrying into P2 via R6; the no-sustain P2 as a racing phase; and the honest per-system fallback list. The 0/12 needle asymmetry is not kept (see issue 1).

# zoning_board: direct design

## 1. Identity & the one question
**Class:** Elite, Halcyon, 2 phases, one threshold at 50 %. Elites appear about once per layer in layers 3-6 (GDD 4.2), so this is pressure content. P1 is readable enough for an early L3 elite.

**Concept:** a planning committee that *zones your wheel*. Riot Control is Halcyon's brute-force and lockout elite. The Board is about territory: it marks slices of yours, and the marks decide which of your slices is worth landing on.

- **P1 "Draft Zoning" asks:** *which of my slices is about to be marked, and can I keep my best slice off the pointer?* Its needle orbits 2 ticks per turn, so you can read it 1-2 turns ahead. Citations put OUTPUT_DOWN on your slice under your pointer. Answer: bait Citations onto weak or NULL slices, Encrypt your main hitter, and burst when the needle sits on Shield or Null.
- **P2 "Variance Denied" asks:** *which of my slices can afford to be down-tiered, and can I finish before the Overflow comes round?* Rezone puts TIER_DOWN on your slice (Perfect → Good → WEAK), on top of the P1 marks you carried over. Answer: Cleanse the worst slice, land your remaining Good slice on the pointer, and race. P2 has no sustain.

The fight shortens when the player denies Citation stacks in P1 (off-pointer landings, Encrypt) and so enters P2 with a clean wheel.

## 2. Phase plan
Flat amounts are T1 base values and are multiplied by the tier damage factor [1.0, 1.3, 1.69, 2.2] (R2). Percent amounts read the Board's own max HP.

### P1 "Draft Zoning" (100 → 50 %, floor = ceil(max × 0.5))
| Item | Value |
|---|---|
| Needles | 1, tick 0, ORBIT 2 ticks/turn (trail shows the next 2 turns) |
| Layout | Shield 5 · Citation 5 · Shim 6 · Citation 4 · Hotfix 4 · Null 6 = **30** |
| Hub | none |
| Satellite | Civic Drone, fixed on slot 1 (the 5-tick Citation), as today |
| Statuses | OUTPUT_DOWN ×1 per Citation on your slice under the pointer (stacks; N8/N9) |
| Listeners | none |

Slice detail:
- **Shield (5 ticks, W G P G W):** SHIELD, FLAT 6.
- **Citation (5 ticks, W G P G W):** 3 damage FLAT, plus OUTPUT_DOWN ×1 (−25 % output per stack). It applies even on a WEAK landing.
- **Shim (6 ticks, W W G G W W, no Perfect):** 9 damage FLAT.
- **Citation (4 ticks, W G G W):** same as the 5-tick Citation.
- **Hotfix (4 ticks, W G G W):** HEAL PERCENT 3 % of max HP.
- **Null (6 ticks).**

### Transition P1 → P2 (at the 50 % floor)
- Damage parks at the floor and the excess is lost (R3). The floor is 31 / 38 / 49 / 63 at T1-T4.
- `wheel_override` swaps the layout. The needle goes to FIXED at tick 0.
- Statuses are kept and remapped by centre tick (R6). Your OUTPUT_DOWN stacks come with you, which is the carried "territory".
- `cleanse_on_enter = NONE`.
- The Civic Drone stays docked on slot 1, which is now a Rezone. It is fixed (R12) and not replaced.
- The Hotfix slice is gone.

### P2 "Variance Denied" (50 → 0 %, no floor)
| Item | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout | Shim 5 · Rezone 4 · Null 5 · Overflow 6 · Rezone 4 · Shim 6 = **30** |
| Hub | none |
| Statuses | TIER_DOWN ×1 per Rezone, capped at 2 stacks (Perfect → Good → WEAK) |
| Listeners | none |

Slice detail (tick ranges: Shim 0-4, Rezone 5-8, Null 9-13, Overflow 14-19, Rezone 20-23, Shim 24-29):
- **Shim (5 ticks, W G P G W):** 6 damage FLAT.
- **Rezone (4 ticks, W G G W):** 0 damage, TIER_DOWN ×1 on your slice under the pointer. Because Rezone has no amount, a WEAK landing on it costs the Board nothing. You avoid it only by steering to another slice.
- **Null (5 ticks).**
- **Overflow (6 ticks, W W G G W W):** 12 damage FLAT.
- **Rezone (4 ticks):** same as above.
- **Shim (6 ticks, W W G G W W):** 6 damage FLAT.

## 3. Sustain and intake
**Sustain:** one source, the P1 Hotfix (3 % max HP, PERCENT). P2 has none.
- **Landing odds:** 4 ticks of 30 = 0.133 per turn. The average tier multiplier is 0.75 (W G G W).
- **Heal per landing at T3:** 3 % × 98 = 2.9 HP. Expected per turn: 0.133 × 0.75 × 2.9 ≈ 0.3 HP.
- **Cap:** 30 % of T3 reference damage (14) = 4.2 per turn. The worst case of 2.9 per turn passes. At T1: 3 % × 62 = 1.9 against 0.3 × 9 = 2.7, which also passes.

**Intake per turn** (landing odds × tier multiplier × flat × factor). Tier multipliers: 5-tick slice 0.8, 4-tick 0.75, 6-tick 0.667.
- **P1 at T3 (factor 1.69):**
  - Shim: 0.2 × 0.667 × 9 × 1.69 = 2.0
  - Citation chip: (0.167 × 0.8 + 0.133 × 0.75) × 3 × 1.69 = 1.2
  - Total ≈ **3.2** (target 2-4)
- **P2 at T3:**
  - Shim 5: 0.167 × 0.8 × 6 × 1.69 = 1.35
  - Shim 6: 0.2 × 0.667 × 6 × 1.69 = 1.35
  - Overflow: 0.2 × 0.667 × 12 × 1.69 = 2.7
  - Total ≈ **5.4** (target 5-8)
- **By tier:** the ×factor scaling gives P1 1.9 / 2.5 / 3.2 / 4.2 and P2 3.2 / 4.2 / 5.4 / 7.0 at T1-T4. Both are above 0 at every tier. Marks reduce your damage and so lengthen the fight on top of this.

## 4. HP by tier
R2 elite band: T1 56-72, T2 68-88, T3 88-112, T4 112-144. Both phases are single-needle, so the player's hits land once (×1). Budget = reference dpt × 3.5 turns minus sustain × 3.5.

| Tier | dpt | P1 (dpt×3.5 − ~1 sustain) | P2 (dpt×3.5) | Sum | `hp_by_tier` | Floor (50 %) |
|---|---|---|---|---|---|---|
| T1 | 9 | 30.5 | 31.5 | 62 | **62** | 31 |
| T2 | 11 | 37.5 | 38.5 | 76 | **76** | 38 |
| T3 | 14 | 48 | 49 | 97 | **98** | 49 |
| T4 | 18 | 62 | 63 | 125 | **126** | 63 |

- All four values sit inside the band.
- The ~1 HP of sustain is the expected 0.3 per turn over 3.5 turns.
- The drone soaks at most one hit on about 1 turn in 6, which sits inside the rounding.
- Today the Board has a flat 132 at every tier.

## 5. Enrage
Default: start turn 8, every 5 turns, +25 % damage. The expected fight is 6-8 turns, so enrage is a backstop against a stalled P2, not a regular event. No authored trigger is needed because P2 has no sustain.

## 6. Buffs and counter Exploits
Not a boss: n/a.

## 7. Counterplay
- **P1:**
  - Read the orbit trail two turns out. Put your best slice off the pointer when a Citation is next, and put Null or a weak slice on it.
  - Encrypt absorbs one status on your main hitter.
  - Burst when the needle sits on Shield or Null, since that turn has no threat.
  - Kill the drone only if it blocks your hits. Ignore the Hotfix; it is small.
- **P2:**
  - Cleanse the worst-marked slice, or land through the Null window.
  - TIER_DOWN removes your Perfects, so plan Good landings.
  - Use SANDBOX on the Overflow turn (the 6-tick slice, ticks 14-19, is visible ahead).
  - Race, because there is no sustain.
- **Weak players:**
  - Let Citations stack on their main slice and wonder why damage collapses.
  - Chase Perfects under TIER_DOWN.
  - Spend nudges on the Board's wheel when nudging their own would do.

## 8. Systems needed
- **N3:** parking and the status keep with the centre-tick remap.
  - Fallback: `wheel_override` exists but wipes statuses today, so P2 would start clean. That is a weaker design but playable.
- **N1:** the PERCENT Hotfix. Fallback: FLAT 3 × tier factor.
- **N2:** `hp_by_tier`. Required.
- **N4:** enrage default. Fallback: none; the fight just lacks a backstop.
- **N8 + N9:** OUTPUT_DOWN and TIER_DOWN.
  - Fallback: today's PARASITE status for the Citation, and a Citation clone in place of Rezone. This loses the "denies Perfects" question.
- **N12:** 4- and 6-tick slices.
  - Fallback: six 5-tick slices. This loses the no-Perfect Shim and Overflow windows. Not recommended.
- **N13:** a fixed satellite. The drone needs it.
- **N19:** the turns-per-phase sim metric.
- **Not needed:** N11 (a single needle at tick 0 or orbiting), N6, N7, N10.

## 9. Delta vs today
- **Kept:**
  - the Citation, the orbit and the Civic Drone;
  - the Hotfix slice (now PERCENT 3 % and P1 only);
  - SANDBOX-as-SHIELD, at 6 instead of 8.
- **Changed:**
  - HP 132 → 62 / 76 / 98 / 126;
  - one threshold at 50 %;
  - a new P2 with Rezone and TIER_DOWN;
  - Shim 12 → 9 (P1) and 6 (P2);
  - Overflow 16 → 12;
  - Citation gains 3 chip damage;
  - slice sizes vary (4 / 5 / 6).
- **heat_effects:** retire. The Heat 50 modifier (all enemies +1 resistance) already covers Halcyon's pressure, and an elite-specific effect would stack on top of it.

## 10. Predicted sim check
No Halcyon row exists in the baseline (Solace only), so these are estimates. The nearest comparison is Recall Unit at 20.2 turns at T3, which this replaces with phases.
- **Turns:** ≈ 7 at the reference player (3.5 per phase), p90 ≈ 9, inside the 6-8 target.
- **Win %:**

| Tier | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Win % | ≈ 98 | ≈ 96 | ≈ 93 | ≈ 90 |

- **Why:**
  - The tail is cut by parking, band HP and no P2 sustain.
  - Total expected intake at T3 is 3.2 × 3.5 + 5.4 × 3.5 ≈ 30 HP before defenses. That is manageable.
  - At T4 it is about 39 HP.
  - OUTPUT_DOWN stacks lengthen the fight for a weak player.
- **Lever:** if T4 is below 90 %, drop Overflow 12 → 10.

## 11. Open questions
Q: Should P2 get the second needle (0 / 12) anyway as an elite exception to the R2 band? A ×2 P2 sums to 93 / 113 / 145 / 187 at T1-T4.
Q: Do enemy needle landings scale enemy output by tier (WEAK = 0.5×)? §3 assumes yes.
Q: Does the Civic Drone count as destroyed if a later satellite replaces it (V2 Q7)?
Q: Is the 3 chip damage on Citation acceptable, or should intake come from the Shim only?
Q: Is the 2-stack cap on TIER_DOWN right, or should Rezone stack to a floor of WEAK only?
