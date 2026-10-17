<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__patrol_unit; status ok; tokens in 6046 cache-write 0 cache-read 32585 out 6027; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (sustain counted inconsistently):** Sustain is now only SHIELD 6 (Hardlight). BLOCK is defense, not sustain: it expires the same turn and is not in the R2 phase-budget formula. The cap check is shown at all four tiers (about 9-10 %, under 30 %). The contradictory "falls to 14 % / about 32 %" text is gone.
- **Issue 2 (Mode column inconsistent):** Every damage, BLOCK and SHIELD row now reads "FLAT × tier factor". Intake is also recomputed with the tier-weighted landing output rather than raw damage.
- **Issue 3 (tell rarely relevant):** The layout is now seven slices: Shim 4 · Defrag 5 · Shim 4 · Overflow 4 · Shield 5 · Null 4 · Shim 4 = 30. Overflow covers 4/30 ticks (13 %) and Null 13 %. Idle-or-wall slices (Defrag, Shield, Null) fall from 63 % to 47 % of ticks, and Shim covers 40 %. The question is now a three-way read (threat, wall or chip), not "dodge a 10 % event". The critic's raw intake was 5.6, but I use the tier-weighted figure, 4.2 at T1.
- **Issue 4 (SANDBOX name clash):** The slice is renamed Hardlight (SHIELD 6) everywhere, including the fallback. In v1 the "burst while the Sandbox slice is under the needle" line mixed the old type name with the R13 meaning. The answer is rewritten around the same-turn simultaneous resolution.
- **Issue 5 (HP above budget):** HP is now stated as "rounded up to the band", with the unrounded budget shown. HP is 30 / 36 / 45 / 58, down from 32 / 38 / 48 / 60 because shield sustain is lower once tier-weighted.
- **Issue 6 (N11 unused, N14 "cosmetic"):** N11 is dropped. N14 is kept as required, because the renamed slice has to read as SHIELD.
- **Issue 7 (unsourced "54 HP ≈ 6 turns"):** Removed. Section 10 is flagged as a hand estimate, since there is no Halcyon baseline.
- **Critic Q1 (Perfect on the 4-tick Overflow):** Kept without a Perfect. A 4-tick slice has none by R11, and a WEAK edge landing deals half, so steering has a visible payoff.
- **Critic Q2 (is 13 % Null enough):** Kept at 4 ticks. See Q2.
- **Kept, because strong:** the single needle at tick 0, the one big readable Overflow, the cheap 1-2 tick nudge dodge, and the explicit 5-tick fallback.

# patrol_unit: direct design

## 1. Identity & the one question
- **Class:** Normal, Halcyon, 1 phase, 3-4 turns, no enrage.
- **Layers:** L3-6 pressure body, with a plain-reading L2 appearance at T1. It is Halcyon's brute that turtles, and it is the first fight with one big hit and a shown tell.
- **The one question:** *"What is on my pointer: the Baton, the wall or the chip, and do I pay a nudge to change it?"* Its needle sits on a threat (Baton 13 %), a wall (Defrag or Hardlight 33 %), chip (Shim 40 %) or nothing (Null 13 %).
- **Faster answer:** Steer the needle off Hardlight, because its SHIELD 6 resolves the same turn and eats your hit. A 1-2 tick nudge onto Shim or Null also dodges a Baton. The fight shortens either by killing it faster or by removing its only real threat.
- **Distinct from siblings:** no statuses (Citations belong to the Warden and Permit Office), no heal (Mast, Meter), no resistance (Transit Controller). It is the only normal with one dominant tell slice plus a lingering shield.

## 2. Phase plan
One phase, no threshold and no HP floor (R3 applies only when a next threshold exists).

| | Phase 1: Patrol |
|---|---|
| Needles | 1, at tick 0 (FIXED) |
| Hub | none |
| Statuses / parasites / listeners | none |

**Layout (R11, sizes sum to 30), starting at tick 0:**

| # | Slice | Ticks (range) | Effect | Mode |
|---|---|---|---|---|
| 1 | Shim (Baton Tap) | 4 (0-3) | 8 damage; W G G W, no Perfect | FLAT × tier factor |
| 2 | Defrag (Riot Shield) | 5 (4-8) | BLOCK 8 | FLAT × tier factor |
| 3 | Shim (Baton Tap) | 4 (9-12) | 8 damage | FLAT × tier factor |
| 4 | Overflow (Raid Baton) | 4 (13-16) | 18 damage; W G G W, no Perfect | FLAT × tier factor |
| 5 | Shield (Hardlight) | 5 (17-21) | SHIELD 6 (lingers, cap 15) | FLAT × tier factor |
| 6 | Null | 4 (22-25) | nothing | n/a |
| 7 | Shim (Baton Tap) | 4 (26-29) | 8 damage | FLAT × tier factor |

Sum: 4+5+4+4+5+4+4 = 30.

Why these shapes:
- **Overflow is 4 ticks with no Perfect.** A WEAK landing on its edge (2 of 4 ticks) deals 9 instead of 18. Steering by 1 tick toward the edge halves the blow, and 2-3 ticks removes it.
- **Shims share a size and a gap.** Three 4-tick Shims separated by walls make chip the most common reading, so the Baton is a spike against a steady baseline, not a lone event.
- **Hardlight stays a standard 5-tick slice** and is the one place a player can get a Perfect-reading wall. The resolution phase gives defense first, so the shield counts the same turn you hit.

The intent is visible at turn start (GDD 2.2). No transition.

## 3. Sustain and intake
- **Sustain:** one source, Hardlight SHIELD 6. BLOCK is defense, not sustain: it expires the same turn and is not in the R2 budget formula, so it is excluded from the cap.
  - Tier-weighted expectation (Perfect and Good full, WEAK ½: 3 full ticks + 2 half ticks = 4 effective of 30): 6 × 4/30 = 0.8 per turn at T1. Scaled by the tier factor: 0.8 / 1.04 / 1.35 / 1.76.
  - Against reference DPT 9 / 11 / 14 / 18: 8.9 % / 9.5 % / 9.6 % / 9.8 %. Under the 30 % cap (2.7 / 3.3 / 4.2 / 5.4) at every tier.
- **Intake per turn (T1, reference player who does not steer, tier-weighted landings):**
  - Shim: 12 ticks, 6 full and 6 WEAK → 8 × (6 + 3)/30 = 2.4
  - Overflow: 4 ticks, 2 full and 2 WEAK → 18 × (2 + 1)/30 = 1.8
  - Total 4.2 per turn at T1. Scaled by the damage table [1.0, 1.3, 1.69, 2.2]: 4.2 / 5.5 / 7.1 / 9.2.
  - Raw, if every landing is Good, it is 5.6 at T1. Above 0 at every tier. A player who always dodges the Baton takes about 2.4 at T1.

## 4. HP by tier (R2 normal band, 1 phase, 1 needle)
Budget = ref_dpt × 3.5 − sustain × 3.5.

| Tier | Ref DPT | Sustain/turn | Calc | Budget | HP | Band |
|---|---|---|---|---|---|---|
| T1 | 9 | 0.80 | 31.5 − 2.8 | 28.7 | **30** | 28-36 |
| T2 | 11 | 1.04 | 38.5 − 3.6 | 34.9 | **36** | 34-44 |
| T3 | 14 | 1.35 | 49.0 − 4.7 | 44.3 | **45** | 44-56 |
| T4 | 18 | 1.76 | 63.0 − 6.2 | 56.8 | **58** | 56-70 |

Each HP is the budget rounded up to a whole number inside the band, with no padding argument. Today's 54 HP is only reachable at T3 in the new scheme.

## 5. Enrage
None (normal class, R4). The shield cap of 15 and one 3-4 turn phase prevent a stall.

## 6. Buffs and counter Exploits
n/a (not a boss).

## 7. Counterplay
- **Good player:** reads the intent at turn start.
  - Baton on the needle: spend the free nudge 1-3 ticks toward Shim, Defrag or Null (edge ticks cut it to 9), or SANDBOX it.
  - Hardlight on the needle: nudge off it, because the shield resolves the same turn, and commit the burst on a Shim or Null reading.
  - Otherwise: attack. The fight ends in 3-4 turns.
- **Weak player:** spends the free nudge on offense and eats the 18 (scaled by tier). Attacks into Hardlight turns and feels the fight drag. Misses that a 1-tick nudge turns the Baton into a 9.

## 8. Systems needed
- **N12** (variable slice sizes, 7 slices, lifts the 6-slice cap). **Data-only fallback:** six 5-tick slices: Shim, Defrag, Shim, Overflow, Shield, Null. This drops the third Shim, the 4-tick Perfect-less Baton and the uneven intake, but keeps the identity.
- **N1** (flat × tier damage factor), **N2** (`hp_by_tier`).
- **N14** (BLOCK / SHIELD naming, so the Hardlight slice reads as SHIELD).
- No statuses, parasites or listeners. N11 is not needed (needle stays at 0).

## 9. Delta vs today
- **Kept:** one needle at 0; the Shim / Defrag / Overflow / shield / Null identity; id, corporation, cycle_reward.
- **Changed:**
  - Shim 10 → 8, Overflow 16 → 18, Defrag 8 stays, shield 5 → 6 (now named SHIELD, not Sandbox).
  - Shim count 2 → 3; layout 6 slices → 7 with variable sizes; Overflow and Null each 4 ticks.
  - hp 54 → `hp_by_tier` [30, 36, 45, 58].
- **heat_effects:** none present, none added.

## 10. Predicted sim check
No Halcyon baseline row exists, so this is a hand estimate against Solace normals.
- **Turns:** about 3.3-3.8 at T1-T3, about 4.0 at T4 (one needle, shield about 0.8-1.8 per turn).
- **Win %:** T1 ≈ 97 %, T2 ≈ 95 %, T3 ≈ 92 %, T4 ≈ 86 %. Intake 4.2 / 5.5 / 7.1 / 9.2 per turn over about 4 turns is 17-37 raw, before block and shield. T4 is the tightest and is where the pass criterion (≥ 90 % at T3) needs checking.
- **Why:** the old 54 HP was a T3-sized pool at every tier. The new HP puts the kill at about 3.5 turns for the reference player, and a nudge-steered Baton keeps intake under the operative's pool.

## 11. Q:
Q: Is a 4-tick Overflow with no Perfect too punishing for an L2 teaching appearance, or should L1-2 use the 5-tick fallback?
Q: Is 13 % Null (4 ticks) enough dead turns to make spending the free nudge on offense a real choice, or does it need 5-6 ticks?
Q: At T4 the tier-weighted intake is 9.2 per turn (86 % win estimate); should Shim drop to 7 to hold the 90 % criterion?
Q: Should BLOCK count toward the 30 % sustain cap in the lint, or only heal and lingering SHIELD?
