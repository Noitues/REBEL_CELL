<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__cargo_hauler; status ok; tokens in 6547 cache-write 0 cache-read 32585 out 3944; cost $0.030. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, budget soak):** the +3/+4/+5 top-ups are deleted. HP is now exactly the R2 budget: 9/11/14/18 × 3.5 × 1 needle − 0 sustain = 31.5 / 38.5 / 49 / 63, rounded to **31 / 38 / 49 / 63**. Defense slices are not sustain, so no exception is claimed. I also checked each value against the class band (T1 28-36, T2 34-44, T3 44-56, T4 56-70).
- **Issue 2 (BLOCKER, resistance growth rider):** removed. Shim is a plain 8 damage, FLAT. Resistance is only the existing fixed passive 2, restored each player turn. No N# is added. The growth idea is moved to Q1 as an optional NEW system.
- **Issue 3 (MAJOR, Crush wording):** now reads "4 ticks: W G G W, so 50% of landings are WEAK (7), 50% Good (14), no Perfect."
- **Issue 4 (MAJOR, intake arithmetic):** redone with one method: Σ(tick share × damage × landing multiplier), WEAK = 0.5×. The result is about 3.1 per turn at T1 before block, scaled by the tier damage factor (1.3 / 1.69 / 2.2) for T2-T4.
- **Issue 5 (MAJOR, T4 turn ceiling):** the resistance growth that threatened the ceiling is gone. T4 is predicted at 3.8 turns, and the prediction is labeled hand-estimated (no Meridian baseline row).
- **Issue 6 (MAJOR, N2 fallback):** replaced with "author the four values in temporary per-tier `.tres` variants until `hp_by_tier` lands". The N1 fallback is stated as a real, working path.
- **Issue 7 (NIT):** the "Defrag 2 → 2" noise is dropped. The 14 Overflow is kept, but I answered the swinginess concern: Crush is 7 damage on half its landings and sits on only 4/30 ticks. Q2 stays open about 12.
- **Issue 8 (NIT, Hub Breach):** deleted. Only Ghost's strip and its first-nudge-ignores-resistance are cited. Weight is a passive trait, which Hub Breach does not affect.
- **Critic's "Keep" items:** kept the pay-or-park question, the 1-tick-nudge trap, the uneven N12 layout and Sandbox's narrow window.

# cargo_hauler: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, Meridian. It is the WEIGHT teacher (spin resistance).
- **Layers:** L1-2 teaching (T1 numbers, one needle, readable) and L5-6 pressure (the same wheel at T3-T4 numbers; Heat's +1 resistance at 50 stacks on top).
- **The one question:** "Its wheel resists, so which landing can you afford to leave alone, and which is worth a real spin?" Resistance 2 absorbs the first 2 ticks of nudge, so a 1-tick nudge is wasted RAM. The wheel is built so a 1-2 tick fix never works. A 3+ tick spin card does.
- **Answer that shortens the fight:** if the needle sits on Brace or Null, leave the wheel alone and attack. If it sits on Crush, a Spin of 4+ (2 absorbed, 2 moved) walks the needle off it. Burn no free nudges on it. Wasting nudges and attacking into Brace/Sandbox turns lengthens the fight.
- It differs from Conveyor Warden (orbit), Customs Scanner and Tariff Collector (RAM drain) and Route Optimizer and Drone Dispatcher (plans, satellites). The Hauler is pure mass: no listener, ring or satellite.

## 2. Phase plan (single phase)

| Field | Value |
|---|---|
| Phase | 1 of 1, no threshold, no floor (R3 not used) |
| Needles | 1, FIXED at tick 0 |
| Hub | Weight: passive resistance 2, refreshed each player turn (existing `passive_resistance`; not a Hub-sourced resistance, so Hub Breach doesn't touch it) |
| Statuses / parasites / listeners | none |

**Layout (7 slices, N12):**

| # | Slice | Size | Effect |
|---|---|---|---|
| 1 | Crush (Overflow) | 4 | 14 damage, FLAT. Map W G G W: no Perfect; 50% of landings WEAK (7), 50% Good (14). |
| 2 | Brace (Defrag) | 5 | BLOCK 8, FLAT |
| 3 | Shim | 5 | 8 damage, FLAT |
| 4 | Null | 6 | nothing (W W G G W W: the safe parking slice) |
| 5 | Brace (Defrag) | 4 | BLOCK 8, FLAT |
| 6 | Sandbox (Detour) | 3 | SANDBOX: negates one attack. Perfect only at the centre tick (G P G). |
| 7 | Shim | 3 | 8 damage, FLAT |

Sizes: 4+5+5+6+4+3+3 = **30**.

**Design logic:**
- One big 14 hit makes the threat real; the two Shims are small hits.
- Brace and Sandbox are its defensive texture: they cost the Hauler the turn's damage and blunt the player's burst on those turns.
- No growth, no transition: Weight is a flat 2 all fight, so the lesson stays clean.

## 3. Sustain and intake
- **Sustain:** none. BLOCK and SANDBOX are not sustain. The 30% cap (≈2.7 at T1, 5.4 at T4) is not approached.
- **Intake per turn** (uniform random landing; Σ tick share × damage × landing multiplier, WEAK = 0.5×):
  - Crush (4 ticks: 2 Good, 2 WEAK): (2×14 + 2×7)/30 = 1.40
  - Shim 5 (W G P G W: 3 full, 2 WEAK): (3×8 + 2×4)/30 = 1.07
  - Shim 3 (G P G: all full): 3×8/30 = 0.80
  - Total ≈ **3.3 per turn at T1 before block** (the critic's 3.1 used a WEAK split on the 3-tick slice that R11 doesn't give).
  - Tier scaling (R2 damage table 1.3 / 1.69 / 2.2): about 4.3 at T2, 5.6 at T3, 7.3 at T4.
  - Player block or SANDBOX reduces this to roughly 2.5-3.3 at T1, 4.2-5.6 at T3 and 5.5-7.3 at T4.
- This is above 0. At T1, 3.5 turns costs about 10 HP: noticeable, not punishing.

## 4. HP by tier (R2 Normal band)
Budget = `reference_dpt_by_tier` × `target_turns_per_phase` (3.5) × 1 needle − sustain (0). No soak top-up, because defense is not sustain.

| Tier | Arithmetic | Band | HP |
|---|---|---|---|
| T1 | 9 × 3.5 = 31.5 | 28-36 | **31** |
| T2 | 11 × 3.5 = 38.5 | 34-44 | **38** |
| T3 | 14 × 3.5 = 49 | 44-56 | **49** |
| T4 | 18 × 3.5 = 63 | 56-70 | **63** |

Today's 72 HP is an elite-sized outlier, so T1 drops by more than half.

## 5. Enrage
None (normal class, R4). The 3-4 turn HP budget bounds a stalling player.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** on turn 1 read the landing. On Crush, play a Spin of 4+ rather than two nudges. On Null or Brace, leave the wheel and spend the turn on damage. Ghost's Perfect-hook strip and its first-nudge-ignores-resistance remove Weight's tax. Cards that attack the Brace turns' block (pierce) pay off.
- **Weak player:** spends the free nudge and RAM on 1-tick nudges that Weight fully absorbs, then eats Crush. Or attacks into Brace/Sandbox turns and wastes damage, stretching the fight past 4 turns.

## 8. Systems needed
- **N12** (variable slice sizes): needed for the 3/4/6-tick slices. **Fallback:** 6 slices of 5 ticks (Crush, Brace, Shim, Null, Sandbox, Shim); the question stays, and only the narrow Sandbox window and the Crush WEAK split are lost.
- **N1** (amount modes): flat amounts × the tier damage factor. **Fallback:** the old `output_scale` path works unchanged.
- **N2** (`hp_by_tier`): needed for the table. **Fallback:** author the four values in temporary per-tier `.tres` variants until `hp_by_tier` lands.
- **N14** (defense trio names, SANDBOX rule): display and rule only, no data change.
- N3 is not needed (single phase).

## 9. Delta vs today
- **Kept:** the id, the Weight passive (resistance 2), the Sandbox and Null slices, one pointer at tick 0 and `cycle_reward = 15`.
- **Changed:** HP 72 → 31/38/49/63 via `hp_by_tier`. Six equal slices become seven uneven ones (N12). Overflow 14 is added as the one real threat, because today's wheel only has Shim 10. The old Shim-with-resistance-growth slice becomes a plain Shim 8.
- **heat_effects:** none today and none added. Heat's global +1 resistance at 50 already stacks on the Hauler.

## 10. Predicted sim check
Hand-estimated; there is no Meridian baseline row.

| Tier | Turns | Win % | Why |
|---|---|---|---|
| T1 | 3.2 | ≥97% | 31 HP in about 3 turns, intake ≈3 |
| T2 | 3.4 | ~96% | |
| T3 | 3.6 | ~93% | intake ≈5 per turn, still affordable |
| T4 | 3.8 | ~90% | intake ≈7 per turn; Brace/Sandbox turns are the main stretch risk |

Today's 72 HP at the same reference damage would run about 8 turns, so this roughly halves it. Fixed resistance 2 removes the growth risk from v1.

## 11. Q:
- Q: Is a growth mechanic wanted at all? If so it needs NEW: an on-trigger `MODIFY_RESISTANCE` rider plus a `max_resistance` field (cap 3); the default here is no growth.
- Q: Should Crush drop from 14 to 12 for L1-2 teaching, or be reserved for T3-T4 numbers only?
- Q: Does Sandbox on a 3-tick slice read clearly enough, or should it sit on a 5-tick slice?
- Q: Is the 72-HP elite history deliberate lore to keep (for example a later "Heavy Hauler" elite), or just a legacy number?
