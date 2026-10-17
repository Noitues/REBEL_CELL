<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__weather_satellite; status ok; tokens in 16164 cache-write 0 cache-read 32007 out 3541; cost $0.037. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# weather_satellite: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns. No enrage, no `heat_effects` review needed (see §9).
- **Corporation:** Orbital Commons. Appears from **L3 to L6**, as the first Orbital enemy that makes the player read an *orbiting* needle. It is the pressure version of "the pointer moves; plan for where it lands."
- **Hook:** it sells you the forecast. Its needle orbits 4 ticks per turn, so the *next* turn's slice is readable ahead of time. A storm slice (Solar Flare) is coming around the rim, and a Perfect read on it is the danger.
- **The one question:** *"Where will the needle be at resolve, and can I make that a slice I like?"*
  - **Shortens the fight:** read the orbit, nudge or spin so the needle lands on Hotfix's WEAK edge or Null, and pile damage into the turn when the Hotfix is out of reach.
  - **Lengthens it:** ignoring the orbit and eating Flares and Overflows while it repairs.
- The preview shows the landing slice after orbit, so the question is a planning one and not a guess.

## 2. Phase plan (single phase, no threshold, no floor)

| Field | Value |
|---|---|
| Phase | 1 of 1: "Forecast" |
| Needles | 1, tick 0 (FIXED pointer), `pointer_orbit_per_turn` = 4 (kept) |
| Hub rule | none |
| Statuses used | OVERCLOCKED (Flare, kept). It burns into CORRUPTED, which is now the R9 RAM tax. |
| Listeners | none |

**Layout (R11 uneven sizes, sum 30):**

| # | Slice | Ticks | Effect (flat × tier damage factor, R2) | Sub-tick map |
|---|---|---|---|---|
| 1 | Shim | 5 | 8 damage, FLAT | W G P G W |
| 2 | Solar Flare | 4 | OVERCLOCK 1 random non-NULL slice of yours (no damage) | W G G W (no Perfect, so its landing is never "perfect") |
| 3 | Hotfix | 4 | Heal 4% max HP, PERCENT | W G G W (no Perfect, so a Perfect never doubles it) |
| 4 | Overflow | 3 | 14 damage, FLAT | G P G (the narrow danger window) |
| 5 | Detour (SANDBOX) | 3 | Negates one attack | G P G |
| 6 | Null | 11 | nothing | large, safe stretch |

Total: 5+4+4+3+3+11 = 30. ✔

- **Why uneven:** Overflow and Detour are narrow, so one 1-tick nudge turns a Perfect landing into a Good one. Null at 11 ticks is the "drift toward safety" zone, and the orbit passes through it for about 2.75 turns.
- **Orbit path:** 4 ticks per turn, 30-tick wheel, so the needle visits a new slice roughly every turn. Flare and Hotfix are 4-tick slices, so the needle can *skip* one in a single hop, which is the readable puzzle.
- **Rotation check:** the wheel respins at the start of each turn (GDD 2.2), then the orbit applies. The preview shows the post-orbit result, so preview = result.
- **Flare moved to a no-Perfect slice** so Overclocked-then-Corrupted is a steady, controllable tax and not a spike on a Perfect.

## 3. Sustain and intake
- **Sustain (one source):** Hotfix, 4% of max HP, only when the needle reads that 4-tick slice.
  - At T3 (HP 50): 2 HP per read; the hit rate is about 1 turn in 6.
  - **Per-turn expectation:** 2 × (4/30) ≈ **0.27 HP per turn**; even if a player fails to steer away at all, a read is ≤ 2 HP.
  - **Cap check:** 30% of reference DPT at T3 (14) = 4.2 per turn. We are at **~2% of reference damage**, far under. The previous version healed a flat 6 × tier factor.
- **Intake per turn** (reference player, no steering, T3 factor 1.69):
  - Shim 8 × 1.69 = 13.5 × (5/30) = 2.25
  - Overflow 14 × 1.69 = 23.7 × (3/30) = 2.37
  - Flare: no damage; a Corrupted slice later costs RAM, not HP.
  - Expected **≈ 4.6 HP per turn unsteered**, with the walk through Null bringing it to ≈ **2.3 once steered**. Above 0 ✔. Over a 3.5-turn fight, ≈ 8-16 HP at T3 against 60 HP, comfortably survivable, with Flares as the lasting cost.

## 4. HP by tier (R2 normal band; one phase)
Budget: `reference_dpt_by_tier[t]` × 3.5 turns × 1 needle, minus sustain × 3.5 (≈ 0.27 × 3.5 ≈ 1).

| Tier | Reference DPT | DPT × 3.5 | − sustain ≈ 1 | Band (R2) | **hp_by_tier** |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 30.5 | 28-36 | **32** |
| T2 | 11 | 38.5 | 37.5 | 34-44 | **38** |
| T3 | 14 | 49 | 48 | 44-56 | **48** |
| T4 | 18 | 63 | 62 | 56-70 | **62** |

Today: 44 flat, scaled by the tier multiplier. The new T3 value of 48 is close to today's, while T1 drops 12 HP and T4 rises.

## 5. Enrage
**None** (normal class default: off). The fight is 3-4 turns, and the 11-tick Null plus the small Hotfix rule out a stall.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads the post-orbit preview on turn start and moves the needle with the free nudge off Overflow or Flare, onto Null or Shim's WEAK edge.
  - Spends nudges to turn the narrow Overflow's Perfect into a Good (the damage is the same, but this keeps it off the Flare's spot).
  - Bursts on turns when the needle is on Null or Detour (Detour negates one attack, so save the big one for a different turn).
  - Cleanses or Encrypts a slice if a Flare lands, since an Overclocked slice burns into a RAM tax.
- **Weak player:**
  - Fires into Detour, wasting the biggest card.
  - Ignores the Flare, so the Overclock burns into CORRUPTED (2× RAM) and the later turns choke.
  - Treats the orbit as random and never plans two turns ahead.

## 8. Systems needed
| Need | N# | Fallback |
|---|---|---|
| `hp_by_tier`, `enemy_damage_by_tier` | N2 | Use the flat `hp` and today's multiplier. |
| PERCENT heal on Hotfix | N1 | Keep FLAT heal 3 × the tier factor (small). |
| Variable slice sizes, `tick_quality` for the no-Perfect 4-tick slices | N12 | Use 5-tick slices (6 × 5): the same layout without the narrow windows. Loses the "nudge denies the Perfect" question. |
| CORRUPTED as a RAM cost | N9 | Today's corrupted self-damage. |
| Uneven pointer | none (single needle) | n/a |

**Pure data-only version:** the six 5-tick slices as today, with a PERCENT-less Hotfix. It works, but the design is blunter.

## 9. Delta vs today
- **Kept:** the 6-slice shape, the 4-tick orbit, the Flare, Hotfix, Detour and Null, `cycle_reward` 15.
- **Changed:**
  - Slice sizes become uneven (Null grows to 11).
  - Hotfix becomes a 4% PERCENT heal (today a flat 6, roughly 10-15% of HP at low tiers).
  - Detour keeps the same type but follows the R13 SANDBOX rule.
  - Shim 9 → 8 and Overflow 14 stay in the same ballpark, now scaled by the damage table.
  - HP 44 → 32 / 38 / 48 / 62 by tier.
- **`heat_effects`:** none authored in the file; none added, since a normal should keep a clean teaching identity.
- **Distinct from siblings:** its identity is the *orbit-read*, not Launch Pad (assumed burst), Debris (assumed swarm) or Uplink Relay (assumed drain).

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only); this is my estimate from the wheel.
- **Expected turns:** T1 3.0, T2 3.3, T3 3.6, T4 3.8; p90 ≤ 5.
- **Win %:** T1 ≥ 97%, T2 ≥ 96%, T3 ≈ 92%, T4 ≈ 85-90% (borderline against the ≥ 90% criterion at T4; T4 is not a strict criterion for normals).
- **Why:** intake is low (2-5 HP per turn), sustain is about 0.3 per turn, and HP is set to roughly 3.5 reference turns, so the fight length is set by damage and not by attrition.
- Compared with the Solace baseline: nothing like the Care Swarm's lethality or the Triage Unit's heal turns.

Q: Should the orbit be a reference-player-visible trail (the future slices lit for 2 turns) so the "plan ahead" question is a read and not a calculation?
Q: Is a flat 4% Hotfix too negligible to count as a "sustain" identity, or should it be 6% with a Perfect-less 3-tick slice?
Q: Does a Flare landing on an already-CORRUPTED slice do nothing, or upgrade it to a stronger debuff (R9 leaves it unspecified)?
