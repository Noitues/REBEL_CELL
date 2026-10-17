<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__orbital_debris; status ok; tokens in 6183 cache-write 0 cache-read 32585 out 7165; cost $0.045. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **1 (old-wheel figure, tier factor):** Fixed. The old-wheel intake is now shown as 2×(3×10 + 2×5)/30 = 2.7, not 3.3. §3 states that flat amounts are authored at T1 and multiplied by `enemy_damage_by_tier` (R2).
- **2 (scratch work in §3):** Removed. The Slab line is now 3×9 + 4×4.5 = 45/30 = 1.5. Fragment is re-added after the resize (see 5).
- **3 (resistance arithmetic, Flip/Respin):**
  - §1 and §7 now state the real price. Resistance is a passive trait, not a Hub, so Hub Breach does not touch it.
  - Resistance 2 absorbs the first 2 ticks of manipulation each turn. The free nudge ±1 does nothing, and a Spin card of N ticks moves the wheel N−2.
  - Flip and Respin are blocked outright (GDD 2.5), so they are no longer offered as answers.
  - The "fast answer" is rewritten around a Spin card, Ghost, or not touching the wheel.
- **4 (budget not honest):**
  - Block is now netted explicitly. Expected absorbed block is computed per tier (Plating is scaled by the tier factor, and WEAK edges halve it).
  - Effective damage per turn (dpt) is 7.7 / 9.3 / 11.8 / 15.1 at T1-T4.
  - The raw budget falls below the band floor, so HP sits at the floor: `hp_by_tier` = [28, 34, 44, 56], matching the critic's numbers.
  - Expected fight length is about 3.7 turns.
- **5 (Containment too strong, intake too low):**
  - Containment is resized to 3 ticks (G P G).
  - Fragment is resized to 5 ticks (W G P G W) and regains a Perfect tick.
  - Layout is Slab 7, Plating 5, Fragment 5, Plating 5, Containment 3, Null 5 = 30.
  - Intake rises to 2.3 at T1.
  - The critic's "Fragment 6" is not used because it would break the sum to 30.
  - Containment is kept, because the designer rulings require the SANDBOX tier, but it covers only 3/30 ticks (10 %).
- **6 (nits):**
  - The Meridian WEIGHT overlap is acknowledged. The differentiator is the wide Slab, not resistance alone.
  - "Strip" is dropped from §7.
  - The slice is named BLOCK throughout (the old Defrag is mentioned once in §9).
- **7 (N14 tag):** Added to §8, with the fallback of a 5-shield as today.
- **Critic's Q on resistance 1 at T1:** Decided in the draft. Resistance stays 2 at every tier; it is left as an open Q below.

# orbital_debris: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage. **Corporation:** Orbital.
- **Layers:**
  - L1-2 as a teaching enemy for "some wheels resist you".
  - L5-6 as a pressure enemy: a wide Slab that hits hard if you ignore it, and a cloud that makes free nudges worthless.
- **The one question:** "Is it worth paying to move a heavy wheel, or do I plan around where it already sits?"
- **Resistance rule:** a passive trait of 2 (not a Hub, so Hub Breach does not affect it) absorbs the first 2 ticks of your manipulation each turn.
  - The free nudge ±1 is fully absorbed.
  - A Spin card of N ticks moves the wheel N−2.
  - Flip and Respin on this wheel are blocked outright (GDD 2.5).
- **Fast answer:**
  - Read the turn-start landing. If it sits on Null, Plating or Containment, spend nothing and attack.
  - If it sits on Slab, either pay for a Spin card that drags the needle to a WEAK edge or off the slab, or block the 9 and race.
  - Ghost (first nudge ignores resistance) is the natural counter.
- **Weak answer:** spending free nudges and RAM on a wheel that does not move.
- **Distinct from siblings:** the identity is resistance plus a wide slab whose edges can be dragged. Meridian's WEIGHT is a similar trait, but there it comes with different slices.

## 2. Phase plan (single phase, no threshold, no floor)

| Item | Design |
|---|---|
| Needles | 1, fixed at tick 0 (FIXED) |
| Resistance | Passive trait 2, restored each player turn (as today) |
| Hub rule | None beyond today's passive |
| Statuses / parasites / listeners | None. Data only. |

**Layout (N12, six slices, sizes sum to 30):**

| # | Slice | Ticks | Effect (T1 base, FLAT) | Tick map |
|---|---|---|---|---|
| 1 | Slab (SHIM) | 7 | 9 damage | W W G P G W W |
| 2 | Plating (BLOCK) | 5 | 5 block | W G P G W |
| 3 | Fragment (SHIM) | 5 | 6 damage | W G P G W |
| 4 | Plating (BLOCK) | 5 | 5 block | W G P G W |
| 5 | Containment (SANDBOX) | 3 | Negates one whole attack of yours (R13) | G P G |
| 6 | Null | 5 | Nothing | n/a |

Sum: 7 + 5 + 5 + 5 + 3 + 5 = 30.

- **Why the sizes:** Slab is large (23 % of the wheel) and its edges are WEAK, so dragging the needle two or three ticks off center halves it. Containment is small so the evade is a rare surprise (1 in 10 landings), not a reliable shield.
- **Transition:** none. One phase, so nothing is parked or cleansed.

## 3. Sustain and intake
- **Sustain:** no heal. Plating is mitigation, netted in §4.
  - Expected block absorbed at T1: Plating covers 10 ticks (6 full at 5, 4 weak at 2.5) = 40/30 = 1.33 per turn.
  - Against the reference damage of 9 per turn that is about 15 %, under the 30 % cap (2.7).
- **Intake** at the reference player (one needle, random landing, T1 base):
  - Slab: 3 ticks × 9 + 4 ticks × 4.5 = 45/30 = 1.5.
  - Fragment: 3 ticks × 6 + 2 ticks × 3 = 24/30 = 0.8.
  - Total: **2.3 per turn at T1.**
  - Scaled by `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2]: **2.3 / 3.0 / 3.9 / 5.1** at T1-T4. This is above 0 and gentle, as a teaching normal should be. A landing on Slab untouched costs 9 / 12 / 15 / 20.
  - Old wheel for comparison: 2×(3×10 + 2×5)/30 = 2.7 at T1. The new wheel is milder on average with a sharper tail.

## 4. HP by tier (R2 normal band)
Budget = reference dpt × 3.5 turns × 1 needle, minus sustain. Plating is netted, with its amount scaled by the tier factor (block expected = 1.33 × factor, capped at the player's damage):

| Tier | dpt | Block absorbed per turn | Effective dpt | 3.5 × eff. | Band | Chosen HP | Turns |
|---|---|---|---|---|---|---|---|
| T1 | 9 | 1.33 | 7.7 | 26.8 | 28-36 | **28** | 3.6 |
| T2 | 11 | 1.73 | 9.3 | 32.6 | 34-44 | **34** | 3.7 |
| T3 | 14 | 2.25 | 11.8 | 41.2 | 44-56 | **44** | 3.7 |
| T4 | 18 | 2.93 | 15.1 | 52.8 | 56-70 | **56** | 3.7 |

- The netted budget falls just under the band floor on every tier, so HP sits at the floor.
- `hp_by_tier` = [28, 34, 44, 56]. Today's 62 is above band at T1-T3.

## 5. Enrage
None (normal default is off, R4). A 3-4 turn fight does not need it, and the Slab tail already punishes stalling.

## 6. Buffs and counter Exploits
Not applicable (normal enemy).

## 7. Counterplay
- **Good player:**
  - Reads the turn-start landing.
  - On Null, Plating or Containment, makes no manipulation and attacks. If Plating is landed, they can still fire a big hit or two.
  - On Slab, either pays for a Spin card of 4+ ticks (moves the needle 2+ ticks to an edge), or BLOCKs or SHIELDs the 9 and keeps hitting.
  - A Ghost player's first nudge ignores resistance, so it moves the full tick.
  - A Breaker's double-resolve ends the fight in about 3 turns without touching the wheel.
  - Should not attack into a Containment landing with the turn's one big hit; spread damage across smaller hits.
- **Weak player:**
  - Spends the free nudge and then RAM on ±1 nudges that the first 2 ticks of resistance eat (the preview shows movement 0).
  - Tries Flip or Respin and gets a refusal.
  - Attacks into Plating without noticing 1/3 of turns are blocked.

## 8. Systems needed
- **N12** (variable slice sizes, sub-tick map): needed for the 7/5/3-tick slices.
  - Fallback (data only): six 5-tick slices in the same order. Containment and Slab lose their distinct sizes, but the question survives.
- **N2** (`hp_by_tier`, `enemy_damage_by_tier`): needed for the HP and the tier-scaled damage. Fallback: a single hp = 44 and the current damage multiplier.
- **N14** (SANDBOX negates a whole resolution): needed for Containment. Fallback: a SANDBOX slice giving a 5-shield, as today.
- N1 is not needed (all amounts FLAT). Nothing else.

## 9. Delta vs today
- **Kept:** passive_resistance 2, pointer at tick 0, the SHIM / BLOCK / SANDBOX / Null set, cycle_reward 15, description.
- **Changed:**
  - HP 62 → [28, 34, 44, 56].
  - Two 10-damage Shims on 5-tick slices → Slab 9 (7 ticks) and Fragment 6 (5 ticks).
  - The old Defrag 8 → Plating 5, now on two 5-tick slices.
  - The Sandbox 5-shield → Containment, a 3-tick whole-attack negate.
  - Slices become sized (N12).
- **New slice files:** `debris_slab`, `debris_fragment`, `debris_plating`, `debris_containment` (replacing the shared shim_10).
- **heat_effects:** none exist on this file; none added.

## 10. Predicted sim check
No baseline row exists for Orbital (the baseline covers Solace only), so this is estimated from the wheel.
- **Turns:** about 3.6-3.7 at the reference player on every tier (§4). Skilled players finish in 3.
- **Win rate:** about 97 % at T1, 96 % at T2, 93 % at T3 and 90 % at T4.
- **Why:** total intake over ~4 turns is about 9 / 12 / 16 / 20 against 45-60 HP operatives; there is no sustain, so the only real risk is consecutive Slab landings at T3-T4.

## 11. Q:
- Q: Is resistance a per-turn pool of 2 ticks (as drafted) or per action? The preview must state which.
- Q: Should resistance be 1 at T1 so L1 players see one nudge move the wheel?
- Q: Should the preview show "your nudge moves 0" for absorbed ticks?
- Q: Is Containment a good fit on a teaching normal (10 % of landings), or should it be reserved for Orbital elites?
