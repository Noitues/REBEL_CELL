<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__surveillance_mast; status ok; tokens in 6801 cache-write 0 cache-read 32585 out 4136; cost $0.031. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (HP arithmetic):** Deleted the invented 0.85 factor and the clamp sentence. HP is now the plain R2 formula, dpt × 3.5 × 1 needle, minus 0 sustain, rounded into band: 32 / 38 / 48 / 60.
- **Issue 2 (intake):** Redid the math. It names the R2 damage table [1.0, 1.3, 1.69, 2.2], not "×1.3". The needle is steerable, so I show both the unsteered lottery baseline and the steered case. The Citation tax is quantified as −50% on one of 5 non-NULL slices, about 10% of the player's total output per landing. The slice mean multipliers are stated explicitly.
- **Issue 3 (layers and orbit timing):** Layers are now "L2-4 teaching, L5-6 pressure at tier HP". The wording now says the orbit moves the needle +2 at end of turn after the turn-start respin, which matches GDD 2.2. N11 is still not needed.
- **Issue 4 (design quality):** The question is now a per-turn tempo problem across the whole fight. The trail shows the slice identity (answering critic Q1 as a design requirement, listed under systems). The two Detours are asymmetric (narrow 4, wide 6), and the Citation lands on the player's own pointer slice, so every turn has two things to steer: the Detour and the Citation. The fight is no longer a single timing check.
- **Issue 5 (Citation targeting and RNG):** Citation is APPLY_STATUS OUTPUT_DOWN ×2 on the slice under the player's pointer (UNDER_POINTER). No RNG is used, and the preview equals the result. This answers v1's Q1, so it is dropped from the open questions.
- **Issue 6 (NIT):** The 4-tick Overflow has no Perfect. Halving applies only to its W edges, and the wording is fixed.
- **Issue 7 (NIT):** Kept the display-name note: enum DETOUR, shown as SANDBOX.
- **Issue 8 (NIT):** "Today's 44" is flagged as the figure from the brief and unverified in the file. It is not relied on.
- **Critic Q2 (WEAK Detour):** Kept as full negate, since a Detour is a binary guard. Moved into the open questions.
- **Triage rows:** none.

# surveillance_mast: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. **Corporation:** Halcyon. **Layers:** L2-4 teaching of "read the future, not the present"; L5-6 pressure at tier HP. L1 shows the Parking Warden and Patrol Unit first.
- **The one question:** *"Where will the read head be when I end turn?"* After the turn-start respin, the orbit moves the needle +2 ticks at end of turn (`pointer_orbit_per_turn`). The trail shows the end tick and the slice it will read. The player plans around that landing, not the dial at turn start.
- **Which answer shortens the fight:** two things must be steered every turn. (a) Keep the Mast's needle off its own Citation and Overflow, or onto Null. (b) Burst on a turn when the Mast's needle ends off both Detours. A Detour (display name SANDBOX, enum DETOUR) negates a whole attack, so a burst into a Detour is wasted. The player steers the Mast's wheel to open the burst turn while keeping their own pointer off the Citation. A player who handles both finishes in 3 turns. One who handles only one needs 4-5.

## 2. Phase plan
Single phase, no threshold, no floor (R3 applies to multi-phase only).

| Field | Value |
|---|---|
| Needles | 1, tick 0, ORBIT +2 per turn (kept). The trail shows the end tick and slice. |
| Hub rule | none |
| Statuses | Citation: OUTPUT_DOWN ×2 on the slice under the player's pointer (R8; replaces PARASITE) |
| Listeners | none |

**Layout (sum 30), slot order Detour4 · Shim5 · Null6 · Overflow4 · Citation5 · Detour6:**

| Order | Slice | Ticks | Sub-tick map | Effect |
|---|---|---|---|---|
| 1 | Detour (SANDBOX) | 4 | W G G W | Negates one whole attack against the Mast this turn. |
| 2 | Shim | 5 | W G P G W | 9 damage, FLAT × tier factor. |
| 3 | Null | 6 | W W G G W W | Nothing. A wide safe stretch. |
| 4 | Overflow | 4 | W G G W | 14 damage, FLAT × tier factor. No Perfect; W edges ×0.5. |
| 5 | Citation | 5 | W G P G W | 0 damage; APPLY_STATUS OUTPUT_DOWN ×2 on the slice under the player's pointer. |
| 6 | Detour (SANDBOX) | 6 | W W G G W W | As slice 1. |

Sum: 4+5+6+4+5+6 = 30. The Detours are uneven (4 and 6), so which one is read matters for how far the player must steer.

**Transition:** none.

## 3. Sustain and intake
- **Sustain:** none. Cap would be 30% × 9 = 2.7 per turn; the Mast uses 0, so there are no heal turns.
- **Defensive uptime:** the Detours cover 10 of 30 ticks, so about 33% of unsteered landings. A steering player can usually avoid this.
- **Intake per turn, unsteered baseline at T1** (landing probability × damage × mean tier multiplier; W G P G W averages 0.8, W G G W averages 0.75):
  - Shim: 5/30 × 9 × 0.8 = 1.2
  - Overflow: 4/30 × 14 × 0.75 = 1.4
  - **Direct total ≈ 2.6 per turn at T1.** The Citation, Null and Detours do no direct damage.
- **Citation tax:** OUTPUT_DOWN ×2 is −50% on one of the player's 5 non-NULL slices, about 10% of total output per landing. Landing probability is 5/30, so the expected tax is small (about 1.7% of output per turn), but a hit on the player's best slice is felt. The player can steer to avoid it.
- **Scaled by the R2 damage table [1.0, 1.3, 1.69, 2.2]:** T1 2.6, T2 3.4, T3 4.4, T4 5.7. Above 0 at every tier. Expected loss per fight at T1 is about 3.5 × 2.6 ≈ 9 HP. The Mast is a tempo check, not a damage race.

## 4. HP by tier
R2 phase budget: `reference_dpt_by_tier` × 3.5 turns × 1 needle − (sustain 0 × 3.5).

| Tier | dpt | Budget | **hp_by_tier** | Band |
|---|---|---|---|---|
| T1 | 9 | 31.5 | **32** | 28–36 |
| T2 | 11 | 38.5 | **38** | 34–44 |
| T3 | 14 | 49 | **48** | 44–56 |
| T4 | 18 | 63 | **60** | 56–70 |

All values are inside the class band. One needle, so no pointer-rule multiplier.

## 5. Enrage
None (normal class, R4 default off). A 3-4 turn fight has no stalling risk, and the Detour is not a heal.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:** reads the trail at the start of turn, which shows the end tick and the slice. It spends the free nudge, plus a card spin if needed, to do two jobs. It moves the Mast's end needle onto Null (6 wide) or a W edge, and it keeps its own best slice off its own pointer when the Citation could land. It bursts on a turn when the Mast's needle ends off both Detours, and keeps one Cleanse or Encrypt for a stuck OUTPUT_DOWN.
- **Weak player:** attacks without checking the Detour and loses a whole 2-hit burst to SANDBOX. It lets Citation stack OUTPUT_DOWN on its best slice and then wonders why its Perfects shrink.
- **Fight shape:** turn 1 read and steer, turn 2 burst, turn 3 finish, turn 4 only if a Detour ate a burst.

## 8. Systems needed
- **N1** (FLAT amounts × tier factor): data-only fallback is today's `output_scale` path.
- **N2** (`hp_by_tier`): fallback is the single `hp` with a tier multiplier.
- **N8 / N9** (OUTPUT_DOWN ×2 replacing PARASITE): fallback is today's PARASITE status, which halves the slice, an equivalent feel.
- **N12** (variable slice sizes, 4/5/6): hard dependency for this layout. Fallback: six 5-tick slices in the order Detour · Shim · Null · Overflow · Citation · Detour. It loses the wide Null and the no-Perfect Overflow but keeps the question.
- **N14** (SANDBOX negates a whole resolution): fallback is today's DETOUR, nearly the same for a 1-hit player.
- **Trail slice identity:** the wheel UI already shows the orbit trail; showing the slice name at the end tick is a UI addition (NEW: trail slice label, small). Fallback: the player reads the slice from the wheel at the trail end.
- **N11:** not needed. Orbit already exists (GDD 2.11).

## 9. Delta vs today
- **Kept:** id, corporation, 1 needle, ORBIT 2 per turn, the Detour / Shim 9 / Overflow 14 / Citation / Null slice set, cycle_reward 15.
- **Changed:** HP becomes `hp_by_tier` (32 / 38 / 48 / 60), replacing today's single `hp` (the brief says 44; not re-verified in the file). The layout moves from six 5-tick slices to 4/5/6/4/5/6. The Detours are uneven, Null is widened to 6 and the Overflow narrowed to 4 with no Perfect. Citation's PARASITE becomes OUTPUT_DOWN ×2 on the player's pointer slice.
- **Description update:** "Its needle drifts two ticks a turn. Read the trail, not the dial."
- **heat_effects:** none exist on this file; none added.

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only), so this is an estimate from the wheel.
- **Turns:** about 3.5 at the step-0 skill (range 3-4); p90 ≈ 5. A Detour eating a burst adds a turn.
- **Win rate:** T1 about 97%, T2 96%, T3 92%, T4 88%. Intake is low (2.6 to 5.7 per turn over about 3.5 turns), so losses come only from repeated Citation stacking on a weak deck at T4.
- **Why:** the threat is tempo, not damage. Unlike the Dosage Dispenser (0.05 damage per turn in the baseline), intake is above 0 and every turn has a steering choice.

## 11. Open questions
Q: Should a Detour read at WEAK tier still negate the whole attack (proposed, since it is a binary guard), or only half, in line with R8's tier idea?
Q: Is a 4-tick Overflow with no Perfect too harsh for a big-hit slice, or should it be 5 ticks so Perfect denial stays a Genome Core question?
Q: Should the orbit step scale (2, then 3 at T3+) as a base value, or stay fixed since mechanics are tier-independent?
Q: Is steering two things at once (Detour and Citation) too much for an L2 teaching fight, or should the Citation arrive only from L3?
