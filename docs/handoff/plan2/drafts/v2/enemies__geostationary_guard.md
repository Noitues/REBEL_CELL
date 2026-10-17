<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__geostationary_guard; status ok; tokens in 7706 cache-write 0 cache-read 32585 out 9265; cost $0.057. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (P1 spans cover only 28 ticks) and triage BLOCKER 1:** re-derived from cumulative sizes, and the v1 layout was already complete. Spans run from −2 to 27 inclusive, which is 30 ticks. Ticks 28 and 29 are −2 and −1 mod 30, so they belong to the Shield. The slices are Shield 5 + Shim 5 + Flare 5 + Overflow 4 + Shim 5 + Null 6 = 30, with no overlap and no gap. The fix is presentation: §2 now shows start tick, end tick (wrapped into 0..29) and a tick-by-tick coverage check.
- **Issue 2 (P2 spans) and triage BLOCKER 2:** the same check. Start ticks are −2, 3, 8, 12, 16, 20, 24 and sizes are 5/5/4/4/4/4/4 = 30. The last slice ends at 27, and the −2..27 window is 30 ticks. The wrapped slice (ticks 28..2) is shown explicitly.
- **Issue 3 (intake derivation):** the multipliers are now derived from the R11 sub-tick maps. A 5-tick slice averages (0.5 + 1 + 1 + 1 + 0.5)/5 = 0.8; a 4-tick slice averages (0.5 + 1 + 1 + 0.5)/4 = 0.75. P2 Overflow is split into its 5-tick and 4-tick parts. This corrects the v1 P2 figure from 6.2 to 6.1.
- **Issue 4 (budget and drone):** each phase now has its own arithmetic line, and the drone's cost is budgeted. Authored HP is unchanged at 60 / 72 / 96 / 120.
- **Issue 5 (invented "phase clears satellites" field):** removed. A `wheel_override` replaces the slot, so a drone docked to a replaced slot is expected to go with it (verify in N3 / N13). The fallback is `max_active` = 0 for the drone in P2. The broken N12 fallback layout is replaced with a real six-slice one.
- **Issue 6 (overclock quantification):** the R9 burn chain (1.5× once, then CORRUPTED, which doubles RAM) is now stated in §2, with the window quantified. The Perfect 16 claim is limited to the 5-tick Overflow.
- **Issue 7 (resistance wording):** corrected. Resistance 3 absorbs the first 3 ticks, so a single-tick nudge is fully wasted. Moving the wheel takes a Spin of 4 or more, or several nudges.
- **Issue 8 (file cite and N13 fallback):** the "today" numbers are cited to `content/enemies/geostationary_guard.tres`. The "mobile today" fallback is dropped because it conflicts with R12.
- **Critic Q "does the drone count toward the budget":** yes, see §4.
- **Critic Q "Flare burn timing":** the burn happens when the slice triggers, not on entry (GDD 2.9). The v1 questions are updated.
- **Kept, because the critic marked them strong:** the P1 resistance lock that vanishes in P2, the readable 3-tick orbit trail, the HP-in-band result at every tier, and the `heat_effects` decision.

# geostationary_guard: direct design

## 1. Identity & the one question
- **Class:** Elite (2 phases, one threshold at 50 %). It appears from L3 upward in Orbital's pool and is rare at L1-2. It is a pressure fight at L5-6, not a teaching fight.
- **Fantasy:** a satellite that holds station until it is forced down. In P1 it can't be shoved. In P2 it breaks station and overclocks you.
- **P1 "On Station":** *You can't steer it, so what do you pay to steer around it?*
  - Its wheel is locked by resistance 3.
  - A bodyguard drone sits on its Overflow slice.
  - The shortening answer: shape your own landing, and save Spin and Flip cards for P2 instead of burning them on resistance.
- **P2 "Re-entry":** *Cash in the overclock before it burns you.*
  - Resistance is gone and the needle orbits 3 ticks per turn, so its wheel can be steered.
  - Two Flare slices overclock your slices.
  - The shortening answer: trigger overclocked slices on a good landing before they burn, and Flip or Spin its Overflow off your needle.
- **Distinct from siblings:** it has no rim gates and no satellite replacement (Mission Director). Its signature is a resistance lock that switches off at the threshold. Both phases use one needle.

## 2. Phase plan
**Tick convention:** a slice starts at −2 plus the cumulative size of the slices before it, and ends at start + size − 1. Ticks are shown mod 30 in brackets. Flat enemy amounts are T1 base values multiplied by `enemy_damage_by_tier` (R2).

**P1 On Station (100 → 50 %)**

| Slice | Size | Span (mod 30) | Effect |
|---|---|---|---|
| Shield | 5 | −2..2 (28..29, 0..2) | 6 FLAT shield, capped at 15 (`shield_cap`) |
| Shim | 5 | 3..7 | 10 FLAT damage |
| Flare | 5 | 8..12 | OVERCLOCK on 1 random non-NULL slice of yours |
| Overflow | 4 | 13..16 | 16 FLAT damage. W G G W, no Perfect. Orbital Drone docked. |
| Shim | 5 | 17..21 | 10 FLAT damage |
| Null | 6 | 22..27 | nothing |

Size check: 5 + 5 + 5 + 4 + 5 + 6 = 30. Coverage check: 3..7, 8..12, 13..16, 17..21, 22..27, 28..2 = 5 + 5 + 4 + 5 + 6 + 5 = 30 distinct ticks.

| Item | Design |
|---|---|
| Needle | 1 at tick 0, orbit 0 |
| Hub | Station Hold: resistance 3, restored each player turn. Hub Breach cards disable it for one turn. A Spin of 4 or more, or several nudges, are needed to move the wheel at all. |
| Satellite | Orbital Drone (existing `orbital_drone.tres`), fixed on the Overflow slice (R12), `max_active` 1, respawns every 2 turns |
| Statuses | OVERCLOCKED on you from Flare |
| Listeners | none |

**Transition at 50 %**
- Damage parks at ceil(max × 0.5) (R3) and the excess is lost. The preview shows "PARKED −N".
- **Wheel:** `wheel_override` to the P2 layout. Hub resistance 3 → 0. Orbit 0 → 3.
- **Drone:** it is docked to a replaced slot, so it is expected to go with the override (verify in N3 / N13). If it doesn't, `max_active` becomes 0 and it stops respawning.
- **Statuses:** all kept on both sides (R6). Your P1 overclocks follow the centre-tick remap and become P2 resources. `cleanse_on_enter` = NONE, deliberately.
- **Phase line:** one line of text. The new layout is revealed on entry.

**P2 Re-entry (50 → 0 %)**

| Slice | Size | Span (mod 30) | Effect |
|---|---|---|---|
| Overflow | 5 | −2..2 (28..29, 0..2) | 16 FLAT. Has a Perfect at tick 0. |
| Flare | 5 | 3..7 | OVERCLOCK on 1 random non-NULL slice of yours |
| Shim | 4 | 8..11 | 12 FLAT, no Perfect |
| Null | 4 | 12..15 | nothing |
| Flare | 4 | 16..19 | OVERCLOCK as above |
| Overflow | 4 | 20..23 | 16 FLAT, no Perfect |
| Shim | 4 | 24..27 | 12 FLAT, no Perfect |

Size check: 5 + 5 + 4 + 4 + 4 + 4 + 4 = 30. Coverage check: 5 + 5 + 4 + 4 + 4 + 4 + 4 = 30 distinct ticks, ending at 27 = −3 mod 30.

| Item | Design |
|---|---|
| Needle | 1 at tick 0, orbit 3 per turn (trail shown) |
| Hub | none. Resistance 0, so Flip, Spin and Respin all work. |
| Enemy shield | none |

**Overclock and burn (both phases, R9):**
- A Flare overclocks one of your slices.
- The next time that slice triggers it deals 1.5× output (a 10-damage Shim reads 15). It then becomes CORRUPTED.
- CORRUPTED costs 2× RAM for any card or nudge that acts there.
- The burn happens when the slice triggers, not on entry.
- P1 Flare covers 5/30 of its ticks, so about 0.17 Flares per turn. P2 covers 9/30, so about 0.3 per turn, roughly double.

**Why the two phases ask different questions:** P1 is defensive, because the needle is stuck, you can't afford to move it, and the drone guards the Overflow. P2 is a race. It is more dangerous but now movable and exploitable.

## 3. Sustain and intake
**Sustain:** one source, the P1 Shield. P2 has none. It resolves on 5 of 30 ticks at 6 FLAT × factor, so average sustain per turn = 5/30 × 6 × factor:

| Tier | Factor | Sustain per turn | Share of reference dpt |
|---|---|---|---|
| T1 | 1.0 | 1.0 | 11 % of 9 |
| T2 | 1.3 | 1.3 | 12 % of 11 |
| T3 | 1.69 | 1.7 | 12 % of 14 |
| T4 | 2.2 | 2.2 | 12 % of 18 |

This is well under the 30 % cap.

**Intake per turn** with the needle landing uniformly and no steering (T1 base). Per-tick output averages 0.8 on a 5-tick slice and 0.75 on a 4-tick slice (R11 maps, with WEAK at 0.5×):

| Phase | Calculation | Intake | Target |
|---|---|---|---|
| P1 | Shim 10/30 × 10 × 0.8 = 2.67; Overflow 4/30 × 16 × 0.75 = 1.60 | **≈ 4.3** | 3-5 |
| P2 | Shim 8/30 × 12 × 0.75 = 2.40; Overflow 5/30 × 16 × 0.8 = 2.13 plus 4/30 × 16 × 0.75 = 1.60 | **≈ 6.1** | 5-8 |

Both are above 0. Flare adds a RAM tax on top of this.

## 4. HP by tier
Phase budget (R2) = `reference_dpt` × 3.5 − sustain × 3.5, with 1 needle.

**Drone cost in P1:** the drone intercepts landings on the Overflow slice, 4/30 of ticks (13 %). A reference player avoids about half of those, so the lost damage is about 0.065 × dpt × 3.5 per phase (2 / 2.5 / 3.2 / 4 for T1-T4). That is added to the P1 budget. P2 has no drone.

| Tier | dpt | P1 budget | P2 budget | Total | Authored `hp_by_tier` | R2 elite band |
|---|---|---|---|---|---|---|
| T1 | 9 | (9 − 1.0) × 3.5 = 28, + drone 2 = 30 | 9 × 3.5 = 31.5 | 61.5 | **60** (30 / 30) | 56-72 |
| T2 | 11 | (11 − 1.3) × 3.5 = 34, + 2.5 = 36.5 | 38.5 | 75 | **72** (36 / 36) | 68-88 |
| T3 | 14 | (14 − 1.7) × 3.5 = 43, + 3.2 = 46 | 49 | 95 | **96** (48 / 48) | 88-112 |
| T4 | 18 | (18 − 2.2) × 3.5 = 55, + 4 = 59 | 63 | 122 | **120** (60 / 60) | 112-144 |

- The threshold sits at 0.5. Parking at 50 % means P1 is exactly half. P2 runs 1.5 to 3 HP under its budget, which the Flare pressure absorbs.
- This replaces today's 145 (`content/enemies/geostationary_guard.tres`), about 1.5× the T3 band.

## 5. Enrage
**Default for elites:** start turn 8, every 5 turns, +25 % damage, additive.
- The expected fight is about 7 turns, so enrage only catches stalling players.
- It raises damage only, not heal or defense.

## 6. Buffs and counter Exploits
Not applicable (elite).

## 7. Counterplay
**P1 (good player)**
- Reads its needle and doesn't spend nudges on it. Resistance 3 absorbs a 1-tick nudge entirely, so the RAM is wasted.
- If the needle sits on the Overflow, takes the hit through the drone or SANDBOXes it. Otherwise ignores the drone and hits the host elsewhere.
- Keeps overclocked slices unburnt to carry into P2.
- Dumps burst before the 50 % park line. Overkill is lost, so the damage plan stops at the threshold and keeps leftover cards for P2.

**P1 (weak player)**
- Pours Spin and Flip cards into the resistance and stalls.
- Kills the drone first, and it respawns every 2 turns.
- Lets Flare overclock the wheel's best slice and loses it to corruption.

**P2 (good player)**
- Flips or spins the Overflow off the needle. This is cheap now that resistance is 0.
- Reads the 3-tick orbit trail one turn ahead.
- Triggers an overclocked Overflow or Shim for the 1.5× burst before the slice burns.
- Uses ENCRYPTED or Cleanse on the Flare target.

**P2 (weak player)**
- Lets overclocked slices burn into CORRUPTED, which doubles RAM there (R9).
- Never repositions, and eats the 16-damage Overflow Perfect on the 5-tick slice.

## 8. Systems needed
| # | Use | Fallback without it |
|---|---|---|
| N1 | Flat amounts × tier factor | Author the numbers per tier by hand |
| N2 | `hp_by_tier` | A flat HP value |
| N3 | One threshold, parked damage, `_apply_wheel_override` keeps statuses | No park or status keep: statuses are wiped and the Flare carry-over is lost. Not recommended. |
| N4 | Default enrage | Default HP only |
| N9 | OVERCLOCKED → CORRUPTED as a RAM tax | Today's CORRUPTED self-damage |
| N12 | Layout sizes 4 / 5 / 6 | **Data-only fallback:** six 5-tick slices. P1 is unchanged except Overflow is 5 ticks with a Perfect. P2 is Overflow · Flare · Shim · Null · Flare · Overflow, with one Shim dropped. Intake rises slightly because every Overflow now has a Perfect tick. |
| N13 | Fixed drone (R12) | None needed: docking on the slice already holds under R12 |
| N14 | SHIELD rename | Name only, no rule change |
| Drone removal | Drone leaves at the override | `max_active` = 0 in P2, so it stops respawning |

## 9. Delta vs today
- **HP:** 145 → 60 / 72 / 96 / 120 by tier, with 2 phases and a 50 % park.
- **Wheel:** a single static 6×5 wheel → two layouts with different slice sizes.
- **Orbit:** orbit 3 for the whole fight → P1 orbit 0, P2 orbit 3.
- **Resistance:** none → resistance 3 hub in P1 only.
- **Amounts:** Shim 14 → 10 (P1) / 12 (P2). Overflow stays 16. Sandbox 8 → Shield 6 FLAT × tier. (All "today" values per `content/enemies/geostationary_guard.tres`.)
- **Flare:** 1 slice → 1 in P1, 2 in P2 (9 of 30 ticks).
- **Drone:** kept as the P1 bodyguard, made fixed.
- **`heat_effects`:** the current `.tres` has none, and none are added. The two phases carry the difficulty on their own.

## 10. Predicted sim check
There is no baseline row for Orbital, so this is estimated from the wheel.
- **Turns:** about 6.5-7.5 at the step-0 skill, p90 at 9. Each phase is 3-4 turns.

| Tier | Win % | Why |
|---|---|---|
| T1 | ≈ 98 % | Intake ≈ 4-6 |
| T2 | ≈ 96 % | |
| T3 | ≈ 92 % | |
| T4 | ≈ 85 % | Flares, burnt slices and RAM tax compound |

- **Today:** 145 HP at T3 implies roughly 2 turns of extra attrition. The new fight is shorter and sharper.

## 11. Open questions
Q: Does orbit move the needle before or after the preview and resolve? I assume the preview shows the post-orbit landing (the trail), so preview equals result.
Q: Does the drone leave with `wheel_override`, or does it need an explicit clear? If not, the fallback is `max_active` = 0.
Q: Is the Shield cap of 15 right for an enemy (R2 open question 9), or should the enemy's flat shield be uncapped?
Q: Does a Flare landing on a WEAK tier still apply its status (R2 open question 11)? I assume yes.
Q: Should P2's second Flare slice stay at 4 ticks, or be reduced if the sim shows overclock cascades?
