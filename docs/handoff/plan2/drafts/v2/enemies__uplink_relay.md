<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__uplink_relay; status ok; tokens in 6334 cache-write 0 cache-read 32585 out 6504; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 / triage BLOCKER (effect text vs intake math):** The tick breakdown is now stated once and used in both places: Flare 6+4 = 10, Shim 5+5 = 10, Overflow 4, Null 6, total 30. The wrong "6 ticks per Flare/Null" line is gone. Intake now includes the WEAK 0.5× edges, which v1 left out (Shim 0.8× and Overflow 0.75× average output), so the T1 figure moves from 3.9 to 3.3.
- **Issue 2 / triage BLOCKER (random Flare pick):** The Flare is now deterministic and steerable. It overclocks the player slice **opposite** the slice under the player's pointer at resolve. Your own landing decides what gets flared, and the preview shows it. Landing so the opposite slice is NULL makes the Flare harmless. This needs NEW: `SlicePick.OPPOSITE_POINTER` (size S). The "Defrag at 1.5× wasted" weak-player line was rewritten around the real OVERCLOCKED rule (1.5× on the next trigger, then CORRUPTED).
- **Issue 3 (intake assumption):** The unsteered/uniform-landing assumption is stated outright, and the Flare and Null ticks cost 0 HP.
- **Issue 4 (HP justification):** HP is now justified only by the R2 budget (dpt × 3.5 × 1 needle). The "low threat, lower-mid" reasoning is dropped.
- **Issue 5 (fallbacks):** Rewritten. N1 and N2 fall back to a per-tier enemy `output_scale` and a manual HP override. N9 falls back to the current CORRUPTED rule and the design is marked provisional. N12 falls back to six 5-tick slices.
- **Issue 6 (invented slice ids):** The `shim_7` / `overflow_12` file names are dropped. Slice resources are named "to be confirmed against `content/slices`". The wheel still has no defense slot, and this is intended.
- **Issue 7 (nudge claim):** Rewritten. A 4-tick Overflow has no Perfect, and a 1-tick nudge only changes the tier. It takes 2 ticks to leave the slice from its edge.
- **Issue 8 (sibling name):** "Debris Guard" is corrected to `orbital_debris`.
- **Critic Qs:** The Flare is now chosen via landing, not random. The "3.9 enough threat" question is answered by raising Shim to 8 and Overflow to 13, and by listing it in Q.
- **Kept:** the one question (cash in or avoid), single phase, no sustain, no enrage, the HP bands, and the orbit.

# uplink_relay: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, no enrage. Orbital. It appears in L1-2 as the teaching enemy for the **Solar Flare = OVERCLOCK trap**, and in L5-6 at T3-T4 as pressure.
- **Hub:** none.
- **The one question: "Do you cash in the flared slice, or steer the flare somewhere harmless?"**
  - A Flare overclocks your slice: 1.5× on its next trigger, then it becomes CORRUPTED (2× RAM for cards and nudges there, R9).
  - Because the Flare hits the slice **opposite** your landing, your pointer choice picks the victim. A Flare on a NULL slice does nothing. A Flare on your best slice is a one-shot 1.5× that costs RAM afterwards.
- **What shortens the fight:** landing the flared slice for the 1.5× on a big hit, then cleansing or accepting the tax.
- **Distinct from siblings:** it is about your own wheel state. It uses no guards (`weather_satellite`), no gates and no parasites.

## 2. Phase plan
**Single phase, 100 % → 0 %, no thresholds, no floor.**

| Field | Value |
|---|---|
| Needles | 1, at tick 0, **orbit +1 per turn** (kept from today) |
| Layout (sum 30) | Flare 6 · Shim 5 · Flare 4 · Overflow 4 · Shim 5 · Null 6 |

Tick check: 6+5+4+4+5+6 = 30. By type: Flare 10, Shim 10, Overflow 4, Null 6.

| Slice | Ticks | Quality map | Effect (FLAT × tier damage factor) |
|---|---|---|---|
| Flare | 6 | W W G G W W (no Perfect) | 0 damage. OVERCLOCKED on your slice opposite the one under your pointer. |
| Flare | 4 | W G G W | Same. |
| Shim | 5 (×2) | W G P G W | 8 damage |
| Overflow | 4 | W G G W | 13 damage, no Perfect to deny |
| Null | 6 | W W G G W W | Nothing |

- **Flare targeting:** `slice_pick = OPPOSITE_POINTER` (NEW). It resolves in the status pass, after your actions, so the preview shows the exact flared slice before End Turn. If the opposite slice is NULL, nothing happens. It applies at any landing tier.
- **Why the sizes:** the Flare is the identity slice, so it gets the big 6-tick body and the small 4-tick one. Overflow is a 4-tick slice with no Perfect, so denying it means leaving it by 2 ticks from the edge (a 1-tick nudge only changes its tier).
- **Hub:** none. **Listeners:** none. **Transition:** none.
- **Statuses:** OVERCLOCKED → CORRUPTED (existing, R9 cost).

## 3. Sustain and intake
- **Sustain:** none (0 of the 30 % cap, which is about 2.7 per turn at T1).
- **Intake at the reference player.** Assumption: the unsteered needle is a uniform landing, and WEAK edges give 0.5× output (Shim averages 0.8×, Overflow 0.75×).
  - Shim: 10/30 × 8 × 0.8 = 2.13
  - Overflow: 4/30 × 13 × 0.75 = 1.30
  - **T1 ≈ 3.4 per turn** (above 0), and × 1.3 / 1.69 / 2.2 gives **4.4 / 5.7 / 7.5** for T2-T4.
- 16 of 30 ticks (Flare 10 + Null 6) deal no damage. A steering player lands on those and takes near 0.
- The real tax is RAM: a flare on a slice you then land means 2× RAM on it afterwards.

## 4. HP by tier
Budget = `reference_dpt_by_tier` × 3.5 turns × 1 needle − 0 sustain.

| Tier | dpt | Budget | Band | **HP** |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28-36 | **32** |
| T2 | 11 | 38.5 | 34-44 | **38** |
| T3 | 14 | 49 | 44-56 | **48** |
| T4 | 18 | 63 | 56-70 | **62** |

Today's 46 HP × tier is far above the band at T2-T4.

## 5. Enrage
None (normals, R4). A 3-4 turn fight needs no stall guard.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:**
  - Reads the Flare's target in the preview and nudges the landing so the opposite slice is NULL, or a slice they want to cash in.
  - If a strong slice is flared, they land it next turn for 1.5×, then Cleanse it or accept 2× RAM.
  - They steer off Overflow, using 2 ticks of nudge to leave its edge.
  - The fight ends in 3 turns.
- **Weak player:** ignores the preview, so the flare hits their best slice and it fires on a bad landing (a WEAK edge). It burns into CORRUPTED, nudges there cost double, and they run low on RAM by turn 4. They also sit on Overflow.

## 8. Systems needed
- **NEW: slice_pick OPPOSITE_POINTER** (size S): the deterministic Flare target. Fallback: `UNDER_POINTER`, which overclocks the slice that just fired. The Flare is then a plain tax and the steering question degrades.
- **N1 / N2** (amounts, `hp_by_tier`, tier damage table): Fallback: a per-tier enemy `output_scale` with a manual HP override per tier until N2 lands.
- **N9** (CORRUPTED as a RAM cost): Fallback: keep the current CORRUPTED rule and mark the design provisional. This is harsher, because self-damage punishes the flare.
- **N12** (`size_ticks`): Fallback: six 5-tick slices. The Shim/Overflow question remains, and the size contrast is lost.
- Pointer orbit is existing.

## 9. Delta vs today
- **Kept:** id, corporation, description, the Flare concept, the orbiting pointer, `cycle_reward` 15.
- **Changed:**
  - Flare is now two slices (6 and 4 ticks) and is deterministic (opposite the pointer) instead of a random pick.
  - Defrag is removed, since a 3-4 turn fight needs no absorb slot.
  - Shim → 8, Overflow → 13.
  - HP 46 → 32 / 38 / 48 / 62.
  - Uneven slice sizes.
- **Slice resources:** reuse existing Shim / Overflow / Flare where numbers match. Otherwise author new ones, with names to be confirmed against `content/slices`.
- **`heat_effects`:** none present today, none added.

## 10. Predicted sim check
There is no baseline row for Orbital (the baseline covered Solace only), so this is an estimate.
- **Expected turns:** about 3.5 at every tier by construction (p90 about 5).
- **Win rate:** T1 ≥ 98 %, T2 ≥ 97 %, T3 ≥ 94 %, T4 ≈ 90 %.
- **Why:** total intake over 3.5 turns is about 12 / 15 / 20 / 26 HP at T1-T4 for an unsteered player. The Flare costs no HP, and the risk is RAM erosion.
- Today's 46 × tier HP (about 101 at T4) takes 6+ turns at the reference player.

## 11. Open questions
Q: Should the Flare skip a slice that is already ENCRYPTED, or absorb into it? ENCRYPTED absorbs a status, which makes pre-encrypting the cheap L1-2 answer.
Q: With N9, should the preview show the flared slice's "next trigger = 1.5×, then CORRUPTED" countdown?
Q: Is about 3.4 raw intake at T1 enough threat for a teaching enemy, or should Shim go to 9?
Q: Should the orbit be 1 tick or 2 per turn, given 4-tick slices make 1 tick a real step?
Q: If the opposite slice is NULL and the Flare is wasted, should the Relay instead pick the next non-NULL clockwise, so Flares never whiff?
