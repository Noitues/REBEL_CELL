<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__riot_control; status ok; tokens in 15840 cache-write 0 cache-read 32007 out 3773; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# riot_control: direct design

## 1. Identity & the one question
- **Class:** Elite (2 phases, one threshold at 0.50), Halcyon. It appears from L3 onward as a pressure fight. It is not a teaching enemy: it asks for nudge economy and for reading two needles.
- **Concept:** a riot line with a visible formation. P1 is a shield wall, so you decide where your hits go. P2 is the wall breaking into a charge, so you decide what to protect.
- **P1 "Shield Wall":** two needles 15 ticks apart. One reads the Wall (Barrier slices, heavy block), the other reads the Baton (damage). *Question: which of the two needles do you steer onto the weak edge, and which do you leave alone?* Each of your hits lands on both needles' targets (pointer rule). Block parks on the Wall needle and does not apply to the Baton needle's hit. In practice, spend the free nudge to move the Wall needle onto Null. That shortens the phase.
- **P2 "Kettle":** the wall drops (no block). Needles move to uneven positions (0 / 11). Citations stack OUTPUT_DOWN on you. *Question: your slices are being degraded, so which slice do you protect, and do you spread the stacks or stack them on a slice you don't need?* Cleanse or Encrypt shortens the phase, and so does burst while the stacks are still low.
- **Distinct from Zoning Board** (an elite, not designed here, so I assume a map or terrain theme) and from the Halcyon mini-boss (City Manager: stacks to ×3, nudge lockout). Riot Control uses stacks only in P2, with a pierce-free baton. It has no lockout. Its identity is block versus needle choice.

## 2. Phase plan

**Threshold:** P1 → P2 at 0.50 (floor = ceil(max HP × 0.5)). Damage parks at the floor (R3).

### P1 Shield Wall (100 → 50 %)
| Item | Value |
|---|---|
| Needles | 2 at ticks 0 / 15 (even; passive_resistance 1 kept as the Hub) |
| Layout (sum 30) | Barrier 6 · Baton 4 · Barrier 6 · Baton 4 · Citation-lite none · Null 5 · Shove 5 |
| Barrier (BLOCK, FLAT) | 10 × tier factor |
| Baton (SHIM, FLAT) | 6 × tier factor, single hit |
| Shove (OVERFLOW) | 10 × tier factor |
| Null | nothing |
| Hub | Resistance 1 (restores each turn). This is today's value, a light tax on the free nudge. |
| Statuses / listeners | none |

### P2 Kettle (50 → 0 %)
| Item | Value |
|---|---|
| Needles | 2 at ticks 0 / 11 (uneven, R10) |
| Layout (sum 30) | Citation 5 · Baton 4 · Shove 6 · Citation 5 · Baton 4 · Null 6 |
| Citation (INFECT) | OUTPUT_DOWN ×1 on a random non-NULL slice of yours (the existing slice_pick). This is today's PARASITE status becoming a 2-stack OUTPUT_DOWN (R8). I author it as OUTPUT_DOWN ×1 for P2 so two Citations in a turn make ×2. |
| Baton | 7 × tier factor |
| Shove | 14 × tier factor |
| Hub | Resistance 1 (kept). No block anywhere. |
| Listener (N6) | **Riot Response:** ON_PERFECT on your own wheel, the enemy gains BLOCK 6 (FLAT) on its next resolve. It punishes Perfect-fishing and gives P2 a counter to burst. |

**Transition:** `wheel_override` plus `MULTIPLY`-style needle move (11 is a pointer re-seat, not a new pointer). Statuses on your wheel survive (R6). Enemy block is cleared. `cleanse_on_enter` = NONE. The phase line is "Hold the line." The new layout is revealed on entry.

## 3. Sustain and intake
- **Sustain:** none. Block is defense, not heal. The Barrier is the single defensive source, and it exists only in P1.
- **Block budget:** Barrier on one needle per turn at 10 FLAT × factor. At T3 (1.69) that is 17. Against reference 14 dpt, one Barrier needle absorbing a hit costs about 17/14 ≈ one hit of lost damage per turn, which is ≤ 30 % of reference damage once you steer the second needle away. I accept that: the Barrier is "sustain" that a good player removes with one nudge.
- **Intake per turn, reference player, T1 factor 1.0:**
  - P1: two needles over six slices, expected hit per needle ≈ (Baton 4/30 × 6 + Shove 5/30 × 10) ≈ 0.8 + 1.7 = 2.5. Two needles ≈ 5 per turn before your block. **Target 3–6. OK.**
  - P2: Baton 8/30 × 7 + Shove 6/30 × 14 ≈ 1.9 + 2.8 = 4.7 per needle, ≈ 9.4 for two. Citations add the degrade (roughly −25 % per stack to your output over time). **Target 8–12. OK, above 0.**

## 4. HP by tier
Class band: Elite, 2 phases. Phase budget = reference_dpt[t] × 3.5 × needles my hits land on (the pointer rule, 2 needles ⇒ my slices land on both only if I hit the enemy wheel; the enemy has 2 needles, so the multiplier applies to *enemy needles my hits land on* = 2) minus sustain × 3.5. I read the R2 table as already folding in a 2-phase total. I use its band midpoint and check the arithmetic:

| Tier | Ref dpt | P1 (3.5 t, block tax) | P2 (3.5 t) | Sum | Band | **HP** |
|---|---|---|---|---|---|---|
| T1 | 9 | 9×3.5 = 31.5 − block tax ~1×3.5 → ~28 | 31.5 | ~60 | 56–72 | **64** |
| T2 | 11 | 38.5 − ~4 → ~34 | 38.5 | ~73 | 68–88 | **78** |
| T3 | 14 | 49 − ~5 → ~44 | 49 | ~93 | 88–112 | **100** |
| T4 | 18 | 63 − ~6 → ~57 | 63 | ~120 | 112–144 | **128** |

The threshold floor is 50 %, so P1 is half of HP. P1 is slightly shorter in HP than budget demands because the block tax is real, so I set HP a little above the sum so the block tax doesn't make P1 take over 4 turns. This is a placeholder pending the sim. This replaces today's 142 flat (an elite at 142 is above the T3 band).

## 5. Enrage
**Default** (start 8, every 5, +25 %). Expected path: P1 about 3.5 turns plus P2 about 3.5 turns means the fight ends around turn 7 and enrage never fires for a reference player. It fires only for a stalling player, which is the point. I don't author a custom one because the two-needle P2 is already the pressure.

## 6. Buffs and counter Exploits
Not applicable (elite).

## 7. Counterplay
- **P1:** one free nudge on the Wall needle toward Null. Burst the Baton needle's side. Don't spend big spin cards into Barrier. The resistance 1 tax makes that first nudge cost you a tick. Plan for it.
- **P2:** SANDBOX the Shove. Keep Perfects for kill windows and not for filler, since Riot Response gives it block. Cleanse or Encrypt one slice. Choose which slice absorbs the stacks (a Null or your weakest).
- **Weak player:** feeds every Perfect into Riot Response, ignores stacks until a key slice is at ×3, and nudges the wrong needle in P1 so Barrier eats the burst.

## 8. Systems needed
- N1 (FLAT amounts × tier factor) and N2 (`hp_by_tier`): needed.
- N3 (phase threshold, parking): needed.
- N4 (enrage defaults): needed.
- N8/N9 (×N stacks, OUTPUT_DOWN): needed for the Citation. **Fallback:** keep the existing PARASITE status, which halves the slice, with no stacking.
- N6 (listener, Riot Response): needed. **Fallback:** drop the listener and add 4 FLAT BLOCK to P2's Null slice, a weaker version of the idea.
- N11 (pointers on any tick): needed for the 0 / 11 needles. **Fallback:** keep 0 / 15 or 0 / 10 in P2, which is data-only.
- N12 (variable slice sizes): needed for the 4 / 5 / 6-tick layout. **Fallback:** 5-tick slices only, six per wheel. Both phases still work but lose the narrow-Baton accuracy window.

## 9. Delta vs today
- **Changes:** HP 142 → 64 / 78 / 100 / 128. A phase is added. The single wheel is split into two designed wheels. P2 loses block. A listener is added.
- **Kept:** two needles, passive_resistance 1, Citation, Shim / Defrag / Overflow values (re-scaled by tier factor FLAT), `cycle_reward` 35.
- **heat_effects:** **retire.** The file shows no `heat_effects` set, so there is nothing to carry. If a Heat hook exists elsewhere, the phase structure replaces it, and mixing Heat-driven stat changes into a fixed phase plan breaks R3 parking readability.

## 10. Predicted sim check
There is no baseline row for Halcyon (the baseline covered Solace only). The estimate comes from wheel arithmetic.
- **Expected turns:** 6–8 (3–4 per phase).
- **Win %:** T1 about 97, T2 about 95, T3 about 90, T4 about 82. T4 is lower because the P2 Shove at ×2.2 is 31 per hit, which is dangerous with stacks on you.
- **Why:** today's 142 HP at two needles against ref 14 takes about 10 turns, which is too long.

## 11. Open questions
Q: Does the P1 Barrier on one needle count as "sustain" for the 30 % cap, or only heals?
Q: Should Riot Response (the P2 listener) fire on ON_NUDGE instead, so a good player has two ways to play around it?
Q: With the Citation's random slice pick, is the OUTPUT_DOWN placement deterministic under a named RNG stream, and does the preview show the target slice?
Q: Is the P2 needle seat 0 / 11 too close to read on the HUD?
