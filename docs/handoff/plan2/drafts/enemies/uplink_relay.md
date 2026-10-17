<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__uplink_relay; status ok; tokens in 15836 cache-write 0 cache-read 32007 out 3286; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# uplink_relay: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, no enrage. Orbital Commons. Appears in L1-2 as the teaching enemy for the **Solar Flare = OVERCLOCK trap**, and again in L5-6 at higher tiers as pressure.
- **Hub:** none.
- **The one question: "Do you cash in the overclocked slice or cleanse it?"** The Relay's Flare overclocks your slice, which is a gift (1.5× once) followed by a curse (it becomes CORRUPTED, so cards and nudges there cost 2× RAM, R9). The player either lands on the flared slice and spends the 1.5× before it burns out, or runs from it.
- **Shortens the fight:** Flare your best offensive slice, then land it. A player who does so deals about 1.5× on that turn. A player who ignores flares ends up with CORRUPTED slices and a tighter RAM budget.
- **Distinct from siblings:** Uplink Relay is the "gift then tax" enemy. Its question concerns the player's own wheel state and has no dependence on guards, orbit gates or shields. (Weather Satellite and Debris Guard get different questions; I don't use satellites, gates or parasites here.)

## 2. Phase plan
**Single phase, 100 % to 0 %, no thresholds, no floor.**

| Field | Value |
|---|---|
| Needles | 1, at tick 0, **orbit +1 per turn** (kept from today; the player can read it 2 turns ahead) |
| Layout (sum 30) | Flare 6 · Shim 5 · Flare 4 · Overflow 4 · Shim 5 · Null 6 |

Slice effects (all damage/block are FLAT × tier damage factor, R2):
- **Flare (6 and 4 ticks):** 0 damage. APPLY_STATUS OVERCLOCKED to 1 random non-NULL slice of yours (`slice_pick = RANDOM_NON_NULL`; today it is a random pick, so it stays deterministic through the combat RNG stream). The 6-tick Flare is easy to land on; the 4-tick Flare has no Perfect (W G G W).
- **Shim (5 ticks):** 7 damage (today 9; lowered, see §3).
- **Overflow (4 ticks):** 12 damage. 4 ticks means no Perfect for the player to deny; the question is how many ticks of Good it gets.
- **Null (6 ticks):** nothing. WEAK edges of Null are all the rest of the wheel's safe spots.

Why these sizes: the Flare is the "bad" slice but also the easy one to read, so it gets the big 6-tick body. Overflow is small, so a one-tick nudge from the orbiting needle moves it onto Null or Shim.

**Hub rule:** none. **Statuses used:** OVERCLOCKED → CORRUPTED (existing). **Listeners:** none. **Transition:** none.

## 3. Sustain and intake
- **Sustain:** none. 0 of the 30 % cap (≈ 0.3 × 9 = 2.7 dmg/turn at T1).
- **Intake at the reference player.** The needle orbits 1 tick per turn, and the player's own free nudge plus cards can move it. Treat the landing as roughly uniform over the wheel for a player who does not steer, with 6 ticks per Flare/Null and 4-5 per other slice:
  - Shim 10/30 × 7 = 2.3
  - Overflow 4/30 × 12 = 1.6
  - **Expected unsteered ≈ 3.9 per turn at T1** (above 0, as required), × tier factor 1.3 / 1.69 / 2.2 for T2-T4 = 5.1 / 6.6 / 8.6.
- Flare turns cost no HP, but they cost RAM later (CORRUPTED). That is the real intake: on 10/30 of turns, one slice of yours becomes a 2× RAM tax within two uses.
- A steering player reduces intake to near zero by parking on Null (6 ticks) and Flare.

## 4. HP by tier
Class: normal, 1 phase. Budget = `reference_dpt_by_tier` × 3.5 turns, minus sustain (0). The Relay's wheel gives the player no defence to chew through, but 6 + 6 ticks of Null / Flare give it low threat, so it sits at the **lower-mid** of the band.

| Tier | dpt | Budget (×3.5) | Band | **HP** |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28-36 | **32** |
| T2 | 11 | 38.5 | 34-44 | **38** |
| T3 | 14 | 49 | 44-56 | **48** |
| T4 | 18 | 63 | 56-70 | **62** |

(Today 46 flat × tier factor ≈ 46 / 60 / 78 / 101, far above the band at T2-T4.)

## 5. Enrage
None (normals, R4). A 3-4 turn fight needs no stall guard.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:** reads the orbit two turns ahead. On Flare turns, they note which slice got OVERCLOCKED (the preview shows it) and, if they can, land that slice next turn for 1.5× before it burns into CORRUPTED. They nudge the needle off Overflow onto Null or the Shim WEAK edge, and use Cleanse or Encrypt only if a Flare hit a key slice they cannot play this turn. The fight ends in 3 turns.
- **Weak player:** ignores the flares, so the overclocked slice fires by accident on a bad slot (e.g. their Defrag at 1.5×, wasted) and burns into CORRUPTED, then pays 2× RAM to nudge or play cards there, running dry by turn 4. They also let the needle sit on Overflow.

## 8. Systems needed
- **N1** (amount modes and flat × tier damage factor): needed to scale the Shim and Overflow numbers by tier. **Fallback:** the existing `output_scale` does this today, so the damage numbers work data-only.
- **N2** (`hp_by_tier`): needed for the HP row. **Fallback:** a single `hp` field of 46 (today's); the sim would then need a manual HP override per tier.
- **N9** (CORRUPTED as a RAM cost): without it, CORRUPTED still self-damages and the fight reads as a damage race. Fallback: keep the current CORRUPTED rule; the design still works, but Flare is a harsher trap.
- **N12** (variable slice sizes, `size_ticks`): needed for the 6/5/4 layout. **Fallback:** six 5-tick slices (today's); the big/small Flare contrast is lost, but the question survives.
- Pointer orbit is existing (`pointer_orbit_per_turn`).

## 9. Delta vs today
- **Kept:** id, corporation, description, Flare concept, orbiting pointer, 6 slots (same slice types), cycle_reward 15.
- **Changed:**
  - Flare is now **two** slices (6 and 4 ticks) instead of one, so the identity (the Flare) is more prominent.
  - Defrag 6 is removed. A normal with a 3-4 turn fight does not need to absorb damage, and it softens the question.
  - Shim 9 → 7 and Overflow 14 → 12 (current 9 / 14 at 6 slices gave ≈ 6.4 per turn unscaled).
  - HP 46 → 32 / 38 / 48 / 62.
  - Uneven slice sizes (N12).
- **`heat_effects`:** none present today; none added.
- **New slice file needed:** `shim_7.tres`, `overflow_12.tres` (data only).

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only); this is an estimate from the wheel.
- Reference player at 9 / 11 / 14 / 18 dpt gives about 3.5 turns at every tier by construction.
- **Expected turns:** 3.5 (p90 ≈ 5), T1-T4.
- **Win rate:** T1 ≥ 98 %, T2 ≥ 97 %, T3 ≥ 94 %, T4 ≈ 90 %. Its intake is low (3.9 to 8.6 per turn over 3.5 turns = 14 to 30 HP), and its damage is easy to dodge; the risk is only RAM erosion from CORRUPTED slices on the longer fights.
- Today (46 HP × factor, ≈ 101 at T4) would take 6+ turns at the reference player; the new numbers shorten it to the class target.

## 11. Open questions
Q: Should the Flare pick be random (today) or "the slice under the pointer's opposite side", so that a player can predict and use the flared slice? Deterministic prediction would make the 1.5× cash-in the puzzle.
Q: With N9, should an OVERCLOCKED slice show its burn-out countdown in the preview, so the trade is readable?
Q: Does a flared slice that is Encrypted absorb the Flare (ENCRYPTED absorbs the next status), and is that the intended cheap answer at L1-2?
Q: Should the orbit be 1 tick per turn or 2, given variable slice sizes make 1 tick a meaningful step on 4-tick slices?
Q: Is 7 damage on Shim too low at T1 to register as a threat for the new player, given the 3-turn fight?
