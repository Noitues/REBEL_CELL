<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__weather_satellite; status ok; tokens in 6595 cache-write 0 cache-read 32585 out 7732; cost $0.049. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Triage row (BLOCKER: Flare damage undefined, randomness uncheckpointed, preview impossible)** -> The Flare no longer picks a random slice. It uses `SlicePick.UNDER_POINTER`: it OVERCLOCKS the slice under your pointer on that resolve, and is a no-op if that slice is NULL. The pick is deterministic and the preview shows it. The Flare also gets a real damage component (4 FLAT), so intake no longer depends on the delayed R9 RAM tax.
- **Critic 1 (BLOCKER)** -> Same fix as the triage row. The Flare is now an INFECT-style slice (4 damage plus OVERCLOCKED). §3 adds the Flare's intake.
- **Critic 2 (MAJOR, §3 arithmetic)** -> Intake is recomputed with tier output multipliers. The Hotfix hit rate is corrected to 4/30, about 1 turn in 7.5. The vague "≈ 2.3 steered" is replaced by a labeled estimate with its working.
- **Critic 3 (MAJOR, HP vs today)** -> Sustain is recomputed per tier, giving T1 = 31, and the rounding is stated. "Today 44" is flagged as quoted from v1 and unverified against the file. The "T1 drops 12" claim is removed.
- **Critic 4 (MAJOR, R11 maps)** -> The false "Perfect never doubles Hotfix" justification is removed. Overflow becomes 4 ticks (W G G W, no Perfect) and Null becomes 10. The 3-tick G P G window is kept only for Detour. Total: 5+4+4+4+3+10 = 30.
- **Critic 5 (MAJOR, orbit vs respin)** -> The "forecast next turn" claim is withdrawn, because the start-of-turn respin makes it false. The orbit is applied after the respin and shown in the preview. It is a true multi-turn forecast only when the wheel is Frozen (the player skips its respin), and a Q asks whether the order should change.
- **Critic 6 (NIT)** -> One name, SANDBOX, is used throughout. The duplicate fallback paragraph is merged into §8. "Shim 9 → 8" is marked "confirm vs file".
- **Critic 7 (NIT)** -> `heat_effects` is marked "confirm against the .tres" in §9.

# weather_satellite: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage.
- **Corporation:** Orbital Commons. Layers **L3-L6**, as the pressure version of "read where the needle lands and steer it".
- **Hook:** a weather satellite whose needle orbits 4 ticks per turn. A storm (the Solar Flare) damages you and primes one of your slices to burn out into a RAM tax.
- **The one question:** *"After the orbit, which slice does the needle read, and can I move it off the Overflow or the Flare?"*
  - **Shortens the fight:** steer the needle onto Null or a WEAK edge, and burst on turns when it reads Null or Hotfix. That is cheaper than burst on a SANDBOX turn.
  - **Lengthens the fight:** ignoring the preview, eating Overflows and Flares while the Hotfix trickles back.
- **Orbit and respin:** every wheel respins at turn start (GDD 2.2). The orbit is applied after that respin, so the preview already shows the post-orbit landing. A Freeze card on this wheel skips its respin, so the orbit becomes a real two-turn forecast (the displayed next step). The respin sets a checkpoint, so nothing here is hidden randomness.

## 2. Phase plan (single phase, no threshold, no floor)

| Field | Value |
|---|---|
| Phase | 1 of 1: "Forecast" |
| Needles | 1, start tick 0, `pointer_orbit_per_turn` = 4 (kept) |
| Hub rule | none |
| Statuses used | OVERCLOCKED (via Flare), which burns into CORRUPTED (R9: 2× RAM on that slice) |
| Listeners | none |

**Layout (R11, sum 30):**

| # | Slice | Ticks | Effect (FLAT amounts × tier damage factor, R2) | Sub-tick map |
|---|---|---|---|---|
| 1 | Shim | 5 | 8 damage, FLAT | W G P G W |
| 2 | Solar Flare | 4 | 4 damage, FLAT, plus OVERCLOCKED on the slice under your pointer (NULL: no status) | W G G W |
| 3 | Hotfix | 4 | Heal 4% of max HP, PERCENT | W G G W |
| 4 | Overflow | 4 | 14 damage, FLAT | W G G W |
| 5 | Sandbox | 3 | Negates one attack (R13) | G P G |
| 6 | Null | 10 | nothing | the safe stretch |

Total: 5+4+4+4+3+10 = 30 ✔

- **Why these sizes:** the big hit (Overflow) has no Perfect, so its danger is a gradient. Its WEAK edges (2 of its 4 ticks) read at 0.5×, so a 1-tick nudge from the middle to the edge halves it. Null at 10 ticks (one third of the wheel) is the destination to steer to.
- **Flare priming:** the pick is under your pointer, so it is deterministic and previewed. An OVERCLOCKED slice gives 1.5× on its next trigger, then becomes CORRUPTED. A sharp player can cash that 1.5× first and Cleanse or Encrypt before the burnout.

## 3. Sustain and intake
- **Sustain (one source):** Hotfix heals 4% of max HP only when the needle reads its 4 ticks, a rate of 4/30, about 1 turn in 7.5.
  - At T3 (HP 48): 1.9 HP per read, so 1.9 × 4/30 ≈ **0.26 HP per turn**.
  - Cap check: 30% of reference DPT at T3 (14) = 4.2 per turn. We are at about 6% of that cap.
- **Intake per turn** (reference player, T3 factor 1.69; expected value over random reads, tier output Shim 0.8, others 0.75):
  - Shim: 8 × 1.69 = 13.5 × 5/30 × 0.8 = 1.80
  - Flare: 4 × 1.69 = 6.8 × 4/30 × 0.75 = 0.68
  - Overflow: 14 × 1.69 = 23.7 × 4/30 × 0.75 = 2.37
  - Total ≈ **4.85 HP per turn unsteered**. Above 0 ✔ (Null, Hotfix and Sandbox read 0).
  - **Steered estimate:** a free nudge each turn moves Overflow reads to its WEAK edge (0.5×) or onto Null. That saves about 1.2-1.5, giving ≈ **3.3-3.6**. Over a 3.5-turn fight that is about 12-17 HP at T3, on top of the Flare's lingering RAM tax.

## 4. HP by tier (R2 normal band, 1 phase)
Budget = `reference_dpt_by_tier[t]` × 3.5 × 1 needle, minus sustain per turn (4% of own HP × 4/30) × 3.5.

| Tier | DPT × 3.5 | Sustain term | Budget | Band (R2) | **hp_by_tier** |
|---|---|---|---|---|---|
| T1 | 31.5 | 0.6 | 30.9 | 28-36 | **31** |
| T2 | 38.5 | 0.7 | 37.8 | 34-44 | **38** |
| T3 | 49 | 0.9 | 48.1 | 44-56 | **48** |
| T4 | 63 | 1.2 | 61.8 | 56-70 | **62** |

All four values are rounded to the nearest integer of the budget. Today's `hp` is quoted in v1 as 44 and must be confirmed against the file.

## 5. Enrage
**None** (the normal default is off). A 3-4 turn fight with 10 ticks of Null and a 4%-HP Hotfix cannot stall.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads the post-orbit preview at turn start.
  - Uses the free nudge to move the Overflow landing to a WEAK edge or onto Null.
  - Saves big cards for turns when the needle reads Null or Hotfix, and holds them on Sandbox turns.
  - Cashes the Flare's 1.5× OVERCLOCKED on one trigger, then Cleanses or Encrypts the slice before it burns out.
  - With a Freeze, plans two turns ahead.
- **Weak player:**
  - Fires the biggest card into Sandbox.
  - Leaves the Flare-primed slice alone, so it burns into CORRUPTED and doubles RAM costs on later turns.
  - Never nudges, so it takes the full Overflow.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| `hp_by_tier`, `enemy_damage_by_tier` | N2 | Flat `hp` and today's multiplier |
| PERCENT Hotfix heal | N1 | FLAT 3 × tier factor |
| `size_ticks` and `tick_quality` (4-tick W G G W slices) | N12 | Six 5-tick slices. This loses the narrow Sandbox window and Null at 10. |
| CORRUPTED as a 2× RAM cost | N9 | Today's self-damage rule |
| SANDBOX naming and whole-attack negate | N14 | Today's DETOUR |

Existing and kept: the orbiting pointer and `SlicePick.UNDER_POINTER`. **Data-only version:** six 5-tick slices, a FLAT Hotfix, and today's names and corruption.

## 9. Delta vs today
- **Kept:** the six slice types, the 4-tick orbit and `cycle_reward` 15.
- **Changed:**
  - Sizes become uneven (Null 10, Overflow 4, Flare 4, Hotfix 4, Sandbox 3).
  - The Flare picks the slice under your pointer instead of a random one, and now also deals 4 damage.
  - The Hotfix becomes a 4% PERCENT heal.
  - HP is 31 / 38 / 48 / 62.
  - Shim is 8 (confirm against the file); Overflow is 14.
- **`heat_effects`:** none authored per v1 (confirm against the `.tres`); none added, to keep a clean identity.
- **Distinct from siblings:** its identity is the steered, orbiting read of one needle plus a primed slice, not burst, swarm or drain.

## 10. Predicted sim check
No baseline row exists (the baseline covers Solace only).
- **Turns:** T1 3.0, T2 3.3, T3 3.6, T4 3.8; p90 ≤ 5.
- **Win %:** T1 ≥ 97%, T2 ≥ 96%, T3 ≈ 92%, T4 ≈ 85-90%.
- **Why:** intake of about 5 per turn (3-4 steered), sustain of about 0.26 per turn and HP at 3.5 reference turns make the fight length depend on damage, not attrition. It is nothing like the Care Swarm's lethality or the Triage Unit's heal turns.

Q: Should the orbit act before the start-of-turn respin, which would make the forecast real but change the enemy turn order?
Q: Is the Flare priming the slice under your pointer too forgiving, since it hands the player a 1.5× trigger before the burnout?
Q: Is a 4% Hotfix too small to read as an identity, or should it be 6% on a 3-tick slice?
