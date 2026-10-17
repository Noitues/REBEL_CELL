<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__patrol_unit; status ok; tokens in 15589 cache-write 0 cache-read 32007 out 3159; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# patrol_unit: direct design

## 1. Identity & the one question
- **Class:** Normal, Halcyon, 1 phase, 3-4 turns, no enrage.
- **Layers:** L3-6 pressure body. It is Halcyon's "brute that turtles": the first fight where a player sees a big hit with a stated tell.
- **The one question:** *"Which of its two readings is on your pointer, and can you steer it before it lands?"* Its wheel has one fat Overflow (Raid Baton), and that Overflow is the only slice that matters. Everything else is chip damage or a wall.
- **Faster answer:** Burst while the Sandbox slice is under the needle and shield is down. Nudge the needle off the Baton onto Null or Defrag. Both lines shorten the fight: the first by killing it, the second by removing its only threat.
- **Distinct from siblings:** no statuses (Citations belong to the Warden/Permit Office), no heal (Mast, Meter), no resistance (Transit Controller). It is the only normal with one dominant tell slice plus a lingering shield.

## 2. Phase plan

Single phase, no threshold, no floor (R3 applies only with a next threshold; there is none).

| | Phase 1: Patrol |
|---|---|
| Needles | 1, at tick 0 (fixed, FIXED behavior) |
| Hub | none |
| Statuses / parasites / listeners | none |

**Layout (sizes sum to 30), uneven by design (R11):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Shim 8 (Baton Tap) | 4 | 8 damage, W G G W (no Perfect) | FLAT × tier factor |
| 2 | Defrag (Riot Shield) | 6 | BLOCK 8 | FLAT × tier factor |
| 3 | Shim 8 | 4 | 8 damage | FLAT |
| 4 | Overflow (Raid Baton) | 3 | 18 damage, G P G | FLAT |
| 5 | Sandbox (Hardlight) | 5 | SHIELD 6 | FLAT |
| 6 | Null | 8 | nothing | n/a |

Sum: 4+6+4+3+5+8 = 30.

Why these shapes:
- **Overflow is only 3 ticks.** Only 3 of 30 ticks hit it, so a random respin puts the needle on it 10% of the time. The threat is rare but readable and always steerable by a 1-tick nudge.
- **The Shim slices have 4 ticks (no Perfect).** Chip damage cannot be "perfected" for extra effect, and they read as bland.
- **Null is the big 8-tick wedge.** About 27% of turns the Patrol does nothing, so the free nudge pays off.

Slice intents are visible at turn start (GDD 2.2), so the tell is always shown.

No transition (single phase).

## 3. Sustain and intake
- **Sustain:** one source, SHIELD 6 from Hardlight (lingers, cap 15). No heal.
  - Shield lands on 5/30 ticks. Expected ≈ 6 × 5/30 = 1.0 per turn raw, about 11% of the 9 DPT reference at T1. Under the 30% cap (2.7 at T1, 5.4 at T4).
  - Defrag BLOCK 8 expires each turn. Expected ≈ 8 × 6/30 = 1.6 per turn. Counting it as sustain too gives 2.6 per turn at T1, which is 29% of 9. Just inside the cap at T1; it falls to ≈ 14% at T4 as the player's damage rises faster than the flat values (R2 scales them by 1.0/1.3/1.69/2.2 against DPT 9/11/14/18, so the ratio stays around 29% at T1 and about 32% at T4, with block treated as full sustain). Block is only up for the turn it lands, so the hit-after-block mostly matters to a player who plays slow. I count it as sustain-lite.
- **Intake per turn (T1, vs the reference player, who does not steer):**
  - Shim 8: 8 × 8/30 = 2.1
  - Overflow 18: 18 × 3/30 = 1.8
  - Total ≈ 3.9 per turn at T1 (Tier ×1.3 → 5.1, ×1.69 → 6.6, ×2.2 → 8.6).
  - Above 0, and well above the Dosage Dispenser's 0.05. Every 10th turn-start reading is a 18-dmg Baton, and a player who always dodges takes ≈ 2 per turn.

## 4. HP by tier (R2 normal band; 1 phase)
Budget = reference_dpt × 3.5 turns × 1 needle, minus sustain × 3.5.

| Tier | Ref DPT | Sustain/turn (shield only) | Calc | HP |
|---|---|---|---|---|
| T1 | 9 | 1.0 | 9×3.5 − 3.5 = 28 | **32** (band 28-36) |
| T2 | 11 | 1.3 | 38.5 − 4.6 = 34 | **38** (band 34-44) |
| T3 | 14 | 1.7 | 49 − 6 = 43 | **48** (band 44-56) |
| T4 | 18 | 2.2 | 63 − 7.7 = 55 | **60** (band 56-70) |

I pick slightly above budget because Null turns (27%) cost the enemy nothing but also give the player a free turn, and 3-4 turns is the target. Current 54 HP sits in the T3 band but the old tier multiplier made T4 far bigger.

## 5. Enrage
None (normal class, R4). The fight is 3-4 turns; the Shield cap of 15 prevents a stall.

## 6. Buffs and counter Exploits
n/a (not a boss).

## 7. Counterplay
- **Good player:** reads the intent at turn start. If the Baton (Overflow) is on the needle, nudge 1-2 ticks to Null or Defrag, or SANDBOX it. If Hardlight is on the needle, burst before it banks, or keep damage low that turn. Otherwise let Shim chip and spend resources attacking. Fight ends 3-4 turns.
- **Weak player:** spends the free nudge on offense and eats the 18. Over-attacks into shield turns and feels the fight drag to 5-6 turns. Never realises the Overflow window is only 3 ticks and can be dodged with one nudge.

## 8. Systems needed
- **N11** (pointers on any tick; needle stays at 0 here, so not required).
- **N12** (variable slice sizes) for 3-, 4-, 6-, 8-tick slices. **Fallback (data-only):** 5-tick slices, six slices: Shim, Defrag, Shim, Overflow, Sandbox, Null. This loses the "only 3 ticks" window and the Perfect-less Shims, but keeps the identity.
- **N1** (flat × tier damage factor) for scaling.
- **N2** (hp_by_tier).
- **N14** (BLOCK/SHIELD naming). Cosmetic.
- No statuses, parasites, listeners.

## 9. Delta vs today
- **Kept:** one needle at 0; the Shim/Defrag/Overflow/Sandbox/Null identity; id, corporation, cycle_reward.
- **Changed:**
  - Shim 10 → 8, Overflow 16 → 18, Defrag 8 stays, Sandbox 5 → 6.
  - Shim count 2 → 2 (one on each side of the Defrag).
  - Variable sizes: Overflow shrinks to 3 ticks, Null grows to 8.
  - hp 54 → hp_by_tier [32, 38, 48, 60].
- **heat_effects:** none present, none added.

## 10. Predicted sim check
No baseline row for Halcyon; this is a hand estimate.
- **Turns:** 3.2-4.0 at T1-T3 (sustain ~1/turn, 1 needle). Slightly longer at T4 (≈4.0).
- **Win %:** T1 ≈ 97%, T2 ≈ 96%, T3 ≈ 93%, T4 ≈ 90%. Intake of 4-9 per turn over 4 turns is 16-34 damage, well below a 45-60 HP operative's pool for one fight.
- **Why:** the old 54 HP was about 6 turns at the reference DPT. Cutting to 32-60 and making the threat a dodgeable 3-tick window puts it in the 3-4 turn target.

## 11. Q:
Q: Is a 3-tick Overflow (no steering margin except one nudge) too punishing for L1-2, or should the teaching version use a 4-tick Overflow with no Perfect?
Q: Should Defrag count as "sustain" under the 30 % cap, since it expires every turn?
Q: Should the Null slice be 8 ticks (27 % dead turns) or split into two 4-tick Nulls so a Shim always sits next to it?
Q: Should T1 use the fallback 5-tick layout so it teaches nudging before uneven slices appear?
