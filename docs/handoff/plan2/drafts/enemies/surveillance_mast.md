<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__surveillance_mast; status ok; tokens in 15930 cache-write 0 cache-read 32007 out 3854; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# surveillance_mast: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. **Corporation:** Halcyon. **Layers:** L3-4 mid-run teaching of "read the future, not the present". It is the Halcyon fight that teaches orbit prediction, so L1-2 shows the Parking Warden and Patrol Unit first, and L5-6 shows it as a pressure check with its tier HP.
- **The one question:** *"Where will the read head be when I end turn?"* The orbit is deterministic (+2 ticks per turn, per `pointer_orbit_per_turn`). The Mast does not hide anything. It is hard to pin because its pointer moves after the start-of-turn respin and the trail shows where it ends. The player must plan around the post-orbit landing, not the position shown at turn start.
- **Which answer shortens the fight:** nudge or spin so the orbiting needle lands on a Null or a DETOUR-only stretch, then hit the Mast on the turn its two Detours are not under the player's reading. The Detours negate whole attacks (R13 SANDBOX), so the shortest fight comes from bursting on the turns when the Detour slices are *not* at the Mast's pointer. Its pointer does not decide its defense; its DETOUR sits as a slice that fires only when the needle reads it. Staying out of the Detour is what the player controls.

(Open point in the current data: "Detour" today cancels the next incoming SHIM/OVERFLOW. Under R13 it becomes SANDBOX: negates one whole attack, every hit of one resolution. I keep it as the Mast's signature defense.)

## 2. Phase plan
Single phase, no threshold, no floor (R3 applies only to multi-phase).

| Field | Value |
|---|---|
| Needles | 1, tick 0, ORBIT +2 per turn (kept). The trail shows the end-of-turn position. |
| Hub rule | none |
| Statuses | Citation applies PARASITE (today). Under R8 that becomes OUTPUT_DOWN ×2 on a random non-NULL slice of yours. |
| Listeners | none (N6 avoided) |

**Layout (sum 30), 6 slices, uneven sizes (N12):**

| Order | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Detour (SANDBOX) | 4 | Negates one whole attack against it this turn. W G G W: no Perfect on its own face. |
| 2 | Shim 9 | 5 | 9 damage FLAT × tier factor. |
| 3 | Null | 6 | Nothing. Wide, W W G G W W. |
| 4 | Overflow 14 | 4 | 14 damage FLAT × tier factor. No Perfect (4-tick). Weak edges halve it. |
| 5 | Citation | 5 | 0 damage; OUTPUT_DOWN ×2 on a random non-NULL slice of yours (RANDOM_NON_NULL, the `rng` stream already used). |
| 6 | Detour (SANDBOX) | 6 | As above. Wide so the 2nd guard is easy to land on, a fair trade for the player. |

Sum: 4+5+6+4+5+6 = 30. Order differs from today (Detour, Shim, Detour, Overflow, Citation, Null) so the two Detours are no longer evenly spaced, and Null is wide, giving a readable safe stretch. Slot order: Detour4 · Shim5 · Null6 · Overflow4 · Citation5 · Detour6.

**Orbit reading:** the needle starts at a random tick (respin), then orbits 2 ticks. The Overflow window is 4 ticks wide, so the needle's end tick falls on it with probability about 4/30 per turn. The player sees this on the trail and can nudge it off or onto it.

**Transition:** none (single phase).

## 3. Sustain and intake
- **Sustain:** none. The Detours are defense, not healing. Zero heal turns. (Cap would be 30 % × 9 = 2.7 per turn; we use 0.)
- **Defensive uptime:** a Detour is read when the end-of-turn needle lies in ticks of the two Detour slices, 10 of 30 ticks, so about 33 % of landings. SANDBOX negates all hits of one resolution, so a 2-hit player burst is wasted when it lands on a Detour. The Mast never reads a Detour twice in a turn (1 needle).
- **Intake per turn (reference player, tier-1 damage, expected):**
  - Shim 9: 5/30 landing × 9 × weak/good mix (0.5 on WEAK edges: 2 of 5 ticks) = 0.167 × 9 × 0.8 ≈ 1.2.
  - Overflow 14: 4/30 × 14 × (G P... 4-tick has 2 Good, 2 Weak, so avg 0.75) ≈ 1.4.
  - Citation and Null, Detours: 0 direct damage, but Citation costs the player about 25 %-50 % output on one slice (a real tax, ~1.5-2 effective).
  - **Total ≈ 2.6 damage per turn plus a status tax** at T1 (≈ 3.4 at T2, 4.4 at T3, 5.7 at T4 by the ×1.3 table). Above 0, the Dosage Dispenser failure avoided. It is low but the Mast is a tempo check, not a damage race.
- Predicted: 3.5 turns × 2.6 ≈ 9 HP per fight at T1.

## 4. HP by tier
R2 phase budget: `reference_dpt` × 3.5 turns, minus sustain (0), and the Detour uptime discount: the reference player's hits are negated on about 33 % of turns unless they steer, and the reference player steers about half the time, so effective uptime loss ≈ 15 %.

| Tier | dpt | Raw (×3.5) | ×0.85 | Band | **hp_by_tier** |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 26.8 | 28-36 | **30** |
| T2 | 11 | 38.5 | 32.7 | 34-44 | **36** |
| T3 | 14 | 49 | 41.7 | 44-56 | **46** |
| T4 | 18 | 63 | 53.6 | 56-70 | **58** |

I clamp to the band floor where the discounted number falls under it, because the band is the validated range. Today's 44 sits at T2.5; T3 becomes 46, near today's.

One needle, so no pointer-rule multiplier.

## 5. Enrage
None (normal class, R4 default off). A 3-4 turn fight has no stalling risk; the Detour is not a heal.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:** reads the orbit trail at the start of turn, then spends the free nudge (and a card spin if needed) to place the Mast's end-of-turn needle on Null (6 wide) or on the Citation's WEAK edge. Then it plays its big hits on a turn where the needle ends off both Detours. A good player also lands the Mast's Overflow on a WEAK edge (halved) rather than letting it read at the centre. It keeps one Cleanse or Encrypt for the Citation.
- **Weak player:** attacks without checking the Detour, loses a whole 2-hit burst to SANDBOX, and burns turns. It also lets Citation stack OUTPUT_DOWN on its best slice and then wonders why its Perfect hits shrink.
- Fight shape: turn 1 read and steer, turn 2 burst, turn 3 finish, turn 4 only if a Detour ate a burst.

## 8. Systems needed
- **N1** (FLAT amounts × tier factor): data-only fallback exists; today's `output_scale` path covers it.
- **N2** (`hp_by_tier`): fallback is the current single `hp` plus the tier multiplier.
- **N8 / N9** (OUTPUT_DOWN ×2 replacing PARASITE): fallback is today's PARASITE status, which halves the slice, an equivalent feel.
- **N12** (variable slice sizes, 4/5/6): hard dependency for this layout. Fallback: six 5-tick slices in the order Detour · Shim · Null · Overflow · Citation · Detour, which loses the wide-Null and no-Perfect-Overflow shaping but keeps the question.
- **N14** (SANDBOX negates a whole resolution): fallback is today's DETOUR (cancels the next SHIM/OVERFLOW), which is nearly the same for a 1-hit player.
- **N11:** not needed (needle still starts on tick 0 by respin).

## 9. Delta vs today
- **Kept:** id, corporation, 1 needle, ORBIT 2 per turn, Detour / Shim 9 / Overflow 14 / Citation / Null slice set, cycle_reward 15.
- **Changed:** HP becomes `hp_by_tier` (30 / 36 / 46 / 58) instead of a flat 44 times a multiplier; the layout moves from six 5-tick slices to 4/5/6/4/5/6; the two Detours are no longer evenly spaced (one narrow, one wide); Null is widened to 6; Overflow narrowed to 4 (no Perfect); Citation's PARASITE becomes OUTPUT_DOWN ×2.
- **Description update:** "Its needle drifts two ticks a turn. Read the trail, not the dial."
- **heat_effects:** none exist on this file; none added.

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only), so this is an estimate from the wheel.
- **Turns:** about 3.5 at the step-0 skill (range 3-4); p90 ≈ 5. A Detour eating one burst adds a turn.
- **Win rate:** T1 about 97 %, T2 about 96 %, T3 about 92 %, T4 about 88 %. Intake is low (2.6 to 5.7 per turn over about 3.5 turns), so losses come only from stacked Citations on a weak deck at T4.
- **Why:** the threat is tempo, not damage. Compared with the Solace normals the baseline flagged (Dosage Dispenser at 0.05 damage per turn), this one has intake above 0 and a real choice per turn.

## 11. Open questions
Q: Should the Citation's OUTPUT_DOWN ×2 hit the slice under the *player's* pointer instead of a random one, so the player can steer around it deterministically (better previews, less variance)?
Q: Does a Detour (SANDBOX) read at WEAK tier still negate the attack, or should a WEAK landing only negate half (consistent with R8's tier idea)?
Q: Is a 4-tick Overflow with no Perfect too harsh for a "big hit" slice, or should the Mast's Overflow be a 5-tick so the Perfect-denial question belongs to the Genome Core alone?
Q: Should the orbit step scale (2, 3 at T3+) as a base value, or stay fixed since buffs and mechanics are tier-independent?
