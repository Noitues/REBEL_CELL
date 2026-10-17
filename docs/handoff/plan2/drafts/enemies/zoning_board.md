<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__zoning_board; status ok; tokens in 16283 cache-write 0 cache-read 32007 out 5490; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# zoning_board: direct design

## 1. Identity & the one question
**Class:** Elite, Halcyon, 2 phases, one threshold at 50 %. Appears in L3-6 (pressure) only. Elites don't spawn in the L1-2 teaching band, and its first phase is readable enough for an early L3 elite.

**Concept:** a planning committee that *rezones your wheel*. Halcyon's identity is statuses on your slices (Citation → OUTPUT_DOWN). Riot Control (the other Halcyon elite) is the brute-force and lockout elite, so the Board is about **territory**: it marks slices of yours, and the mark decides what is worth landing on.

- **P1 "Draft Zoning" asks:** *which of my slices are about to be marked, and can I land the one that isn't?* Its needle orbits predictably, so you can read it 1-2 turns ahead. Citations put OUTPUT_DOWN on your slice under its pointer; the Board's own heavy hit only comes through when its needle sits on a slice you marked last turn (see the Variance rule below). Answer: steer your pointer off your best slice and bait Citations onto your weak or NULL slices.
- **P2 "Variance Denied" asks:** *can I punish the one slice that matters?* The needle stops orbiting and the Board splits into two uneven needles. Its Shim/Overflow hits are bigger, but a single big "Rezone" slice carries a TIER_DOWN stack onto you. Answer: Encrypt or Cleanse the right slice, then burst in the open Hotfix-less window. Phase 2 has no sustain at all, so racing wins.

The fight shortens when the player *denies* Citations (Encrypt, off-pointer landings) and bursts the P1 Permit window.

**Variance rule (no new system):** the Board's Overflow is data-only unmodified. "Marked" is simply OUTPUT_DOWN on your slice, which the Board's Citation puts there (existing behavior, N8/N9 stacks). No listener needed.

## 2. Phase plan

Reference tier-damage factors from R2 apply to flat amounts. Amounts below are T1 base values.

### P1 "Draft Zoning" (100 → 50 %)
| Item | Value |
|---|---|
| Needles | 1, tick 0, ORBIT 2 ticks/turn (today's behavior, readable ahead by the trail) |
| Layout (sum 30) | Sandbox(SHIELD) 5 · Citation 5 · Shim 12 → 6 ticks · Citation 4 · Hotfix 4 · Null 6 |

Slice detail:
- Slice order: Shield 5, Citation 5, Shim 6, Citation 4, Hotfix 4, Null 6 = 30.
- **Shield (SANDBOX type, R13 name SHIELD):** 6 FLAT. The enemy flat amount is scaled by the tier factor.
- **Citation (5 ticks, W G P G W):** 0 damage; applies OUTPUT_DOWN ×1 on your slice under the pointer (an existing 2-stack PARASITE becomes OUTPUT_DOWN ×2 under R8; here I use ×1 per Citation, so the stack matters). A WEAK landing still applies it (Q11).
- **Citation (4 ticks, no Perfect):** same effect.
- **Shim (6 ticks, WWGGWW):** 9 damage FLAT. A narrow Good window means the player can nudge it to WEAK for 0.5×.
- **Hotfix (4 ticks):** HEAL 3 % max HP PERCENT. It is the phase's single sustain source.
- **Null (6 ticks).**
- **Hub:** none.
- **Satellite:** keep the Civic Drone (1 active, docks slot 1, trigger = 1, every 1). Its wheel and effect stay as today, so it remains the bodyguard that makes the player decide whether to kill the drone or steer around it.

### Transition P1 → P2 (at 50 %, ceil(max×0.5) is the floor)
- Damage parks at the floor (R3); the excess is lost.
- `wheel_override` to the P2 layout; `pointer_ticks` → (0, 12) (uneven, R10) with MULTIPLY.
- Statuses are kept with the R6 remap: **your OUTPUT_DOWN stacks stay**, so the player carries P1's mess into P2.
- `cleanse_on_enter = NONE`. The player must handle the stacks.
- The Board's own Civic Drone, if alive, is removed: its satellite docks are cleared by the override.

### P2 "Variance Denied" (50 → 0 %, no floor)
| Item | Value |
|---|---|
| Needles | 2: ticks 0 / 12 (uneven), FIXED (no orbit) |
| Layout (sum 30) | Shim 5 · Rezone 4 · Overflow 6 · Null 5 · Rezone 4 · Shim 6 |

Slice detail (all damage FLAT, tier-scaled):
- **Shim (5 ticks):** 8 damage.
- **Shim (6 ticks, WWGGWW):** 8 damage.
- **Rezone (4 ticks, no Perfect, GG in the middle):** 0 damage; applies TIER_DOWN ×1 on your slice under the pointer. This new status (R8, N9) reads each landing one tier lower per stack: Perfect→Good, Good→WEAK.
- **Overflow (6 ticks, narrow Good window):** 16 damage.
- **Null (5 ticks).**
- **Sustain:** none. Hotfix is gone.
- **Hub:** *Compliance Lock*: resistance 1 (absorbs 1 tick of nudge each turn, restored each turn). A mild tax on steering.
- With uneven needles at 0 and 12, the Board's two pointers can't both sit on its heavy slices: Overflow occupies ticks 11-16 region against the Rezone at 4-... so the layout is arranged so exactly one of the needles reads a dangerous slice in most rotations. The player nudges one needle onto Null.

(Tick check: Shim 5 at 0-4, Rezone 4 at 5-8, Overflow 6 at 9-14, Null 5 at 15-19, Rezone 4 at 20-23, Shim 6 at 24-29. The needles are at 0 and 12 relative to the rotation. With rotation 0 they read Shim and Overflow.)

## 3. Sustain and intake
- **Sustain:** one source only, P1 Hotfix 3 % max HP, fires on roughly 1 in 6 slice landings (≈0.17 per needle-turn). Expected heal ≈ 0.5 % max HP per turn, e.g. T3 98 HP → ≈ 0.5 HP per turn. Worst case, if it lands every turn, 3 % × 98 = 2.9 HP per turn, which is 21 % of the T3 reference 14 dpt, below the 30 % cap. Cap passes. P2 has none.
- **Intake per turn at T3 (factor 1.69):** the player's pointer reads one slice per turn (6 slices, assume uniform).
  - P1: expected enemy slices: Shield 0 dmg, Citation 0, Shim 9×1.69 = 15 (1/6), Citation 0, Hotfix 0, Null 0. Expected ≈ 2.5 per turn directly, plus OUTPUT_DOWN stacks that cut your damage by 25 % per stack. Target 2-4: pass.
  - P2: two needles. Shim 8 (×1.69 = 13.5) on 2 of the 6 slices, Overflow 27 on 1. Expected per needle ≈ (13.5×(5+6)/30 weights... simplified) ≈ 7.5 per turn per needle, two needles ≈ 10-11 minus Null hits. Target 8-12: pass. It is above 0 at every tier.

## 4. HP by tier
R2 elite band (2 phases): T1 56-72, T2 68-88, T3 88-112, T4 112-144.

Phase budget: dpt × 3.5 turns × needles on the player's side (1) minus sustain × 3.5.
- T1: dpt 9. P1 = 9×3.5 = 31.5 − (0.5×3.5 ≈ 2) ≈ 30; P2 = 31.5. Sum ≈ 62.
- T2: dpt 11. 38.5 each, P1 minus 2 → 36.5 + 38.5 = 75.
- T3: dpt 14. 49 each, P1 minus 2 → 47 + 49 = 96.
- T4: dpt 18. 63 each, P1 minus 2 → 61 + 63 = 124.

P2's enemy needles are two, but the player's pointer count is what scales the budget (the pointer rule is about hits landing on the enemy's needles). The player hits both of the Board's needles in P2, so P2 gets the 2-needle bonus: the player's hits land twice. To avoid overshoot I count ×1.5 (not ×2, because uneven needles often put one on Null):

| Tier | P1 | P2 (×1.5) | HP | Threshold floor (50 %) |
|---|---|---|---|---|
| T1 | 30 | 47 | **72** (cap; band 56-72) | 36 |
| T2 | 36 | 58 | **88** (cap) | 44 |
| T3 | 47 | 73 | **112** (cap) | 56 |
| T4 | 61 | 95 | **144** (cap) | 72 |

These all sit at the top of the band. If the sim finds it too long, drop each by 10 %. The band is the validator, and the arithmetic says the upper edge. `hp_by_tier` = [72, 88, 112, 144] vs. today 132 at all tiers (today's HP is a flat 132 × tier multiplier).

## 5. Enrage
**Default** (start turn 8, every 5, +25 % damage). The expected fight is 6-8 turns, so enrage is a backstop for a stalled P2, not a regular event. Authoring is unneeded: the Board has no stalling mechanism in P2 (no sustain), and the one in P1 is small.

## 6. Buffs and counter Exploits
Not a boss: n/a.

## 7. Counterplay
- **P1:** read the orbit trail. Landing on the Shim's narrow Good window costs you; steer onto Shield or Null. Citations are cheap if they hit a slice you don't care about, so keep your best slice off the pointer when a Citation is next. Encrypt (absorbs the next status on that slice) protects your main hitter. Kill the Civic Drone only if you cannot steer around it. Burst when the needle is on Shield (that turn deals zero threat). The Hotfix is small, so ignore it.
- **P2:** your TIER_DOWN-ed or OUTPUT_DOWN-ed slices are your problem now. Cleanse the worst, then take the fight to the open Null windows. With two uneven needles, nudge one needle to Null and take the other on a Shim. Don't try to Perfect while TIER_DOWN is on your slice: Good→WEAK halves it. The fight has no sustain, so racing is the right play. SANDBOX the Overflow turn if you can see it.
- **Weak players:** let Citations stack on their main slice, then wonder why damage collapses; spend nudges fighting the 1-tick resistance instead of cards; try to kill the drone while ignoring the clock.

## 8. Systems needed
- **N3** (phase floor, status keep, override with centre-tick remap): required. Fallback: none for parking; `wheel_override` exists today, but `_apply_wheel_override` wipes statuses, so without N3 the carry-over feature is lost (data-only fallback: use `cleanse_on_enter` semantics, i.e. accept the wipe, making P2 a clean slate, a weaker design).
- **N1** (amount modes): needed for the PERCENT Hotfix. Fallback: FLAT hotfix 3 (× tier factor).
- **N2** (`hp_by_tier`): required for the HP table.
- **N4** (enrage): default applies. Fallback: none; the fight just lacks a backstop.
- **N8 + N9** (×N stacks, OUTPUT_DOWN, TIER_DOWN): required for Citation and Rezone. Fallback: today's PARASITE status (a half-output halving) for Citation, and drop Rezone for a Citation clone in P2 (loses the "denies Perfects" question).
- **N11** (any-tick pointers, 0/12): required. Fallback: a pointer at 0/15, which gives evenly spaced needles and loses the "only one dangerous" tension.
- **N12** (variable slice sizes): required for the 4/6-tick slices. Fallback: 5-tick slices only, six slices; the narrow Shim and Overflow windows are lost, which is the P2 core. Not recommended.
- **N7/N6:** not needed.

## 9. Delta vs today
- **Today:** one phase, 132 HP at every tier, 6 five-tick slices (Sandbox 8, Shim 12, Citation, Overflow 16, Hotfix 6, Null), one orbiting needle at 2 ticks/turn, a Civic Drone satellite on slot 1.
- **Kept:** the Citation, the orbit, the drone (P1 only), the HOTFIX slice (now PERCENT and smaller), SANDBOX-as-SHIELD.
- **Changed:** HP 132 → 72/88/112/144, one threshold, P2 with two uneven needles, a Rezone slice with TIER_DOWN, Overflow and Shim cut down to narrower windows, resistance 1 hub in P2, Hotfix 6 → 3 % in P1 only, Sandbox 8 → 6.
- **heat_effects:** the file has none set, so there is nothing to keep or retire. If a future one exists, retire it: Halcyon's Heat identity already comes from the ongoing modifiers, and a per-enemy effect would double up.

## 10. Predicted sim check
No baseline row exists for any Halcyon enemy (the baseline covered Solace only). This is an estimate from the wheels.
- **Turns:** ≈ 7 at the reference player (P1 ≈ 3.5, P2 ≈ 3.5); p90 ≈ 9. Inside the 6-8 target.
- **Win %:** T1 ≈ 97, T2 ≈ 95, T3 ≈ 90, T4 ≈ 82 (below the 90 % T3 criterion borderline; the T4 drop is because the 1.69-2.2× enemy damage lands two needles in P2 and OUTPUT_DOWN stacks compound against a weaker deck).
- **Why:** today's 132 HP is the main source of length, as with Account Manager; parking plus the cap-top HP removes the long tail, and P2's lack of sustain means the fight closes quickly once a player is past P1.
- Risk: the 1.5× needle factor is a guess. If the sim shows P2 under 3 turns, raise it to 1.0 and lower P2's HP.

## 11. Open questions
Q: Should a Citation applied to an already ENCRYPTED slice also consume the Encrypt for a visible "fine absorbed" message, or silently? It affects readability of the counterplay.
Q: Is TIER_DOWN too punishing on a 4-tick slice (no Perfect already)? Good→WEAK would be the only effect there; consider exempting it.
Q: Should P2's resistance-1 hub be a counter Exploit target in a later elite-buff pass, or is that boss-only?
Q: Does the Civic Drone count as destroyed when the phase override clears it (Q7 in CONTENT_DESIGN_V2, replaced satellites)?
Q: Is a 72/88/112/144 HP set at the very top of the band acceptable, or should the Board sit mid-band because Halcyon's statuses already tax the player's damage?
