<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__station_commander; status ok; tokens in 15832 cache-write 0 cache-read 32007 out 4673; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station_commander: direct design

## 1. Identity & the one question
- **Class:** Elite, Orbital Commons. Two phases, one threshold. Appears in L5-6 pressure (a gate elite for T2+ Sites). A T1 Site can draw it at the late layers only. Not a teaching enemy.
- **Theme:** A station commander runs a drill and then, when you land hits, orders a lockdown. Phase 1 teaches you to read its stations. Phase 2 punishes you for ignoring them.
- **Distinct from the Geostationary Guard (elite) and from the Mission Director (rim gates and satellite replacement):** the Commander's tool is *uneven needles plus Flare overclock bait*. It uses no gates and no satellites.
- **P1 question: "Which of my slices do I let it read?"** Two uneven needles (0 / 11). One needle is dangerous, one is safe. Flares overclock your slice, so a Perfect on a Flared slice is a gift and a trap. Answer: steer the dangerous needle onto Null or a Defrag and land the safe one on a lethal slice of yours.
- **P2 question: "Can I spend a burn I'm about to lose?"** The Flare fuse. Your overclocked slices are 1.5× once and then corrupt. P2 turns its Flare into a Detonate that hits for each overclocked slice of yours, so you must either fire your overclocked slices before it resolves or cleanse them. Answer: cash in overclocks as damage (they are 1.5× for you too), then burst through. Cashing in shortens the fight.

## 2. Phase plan
**Threshold:** 0.50 (HP floor ceil(max × 0.5) while P1 is active, R3). The excess is lost. The last phase has no floor.
**Layouts below are tick sizes summing to 30.** Slice values are at T1 base before the tier damage factor (R2).

### P1 "Drill" (100 → 50 %)
| Item | Value |
|---|---|
| Needles | 2: ticks 0 / 11 (uneven, R10). Fixed. |
| Resistance | 1, passive (kept from today); restores each turn |
| Layout | Shim 12 (5) · Defrag (6) · Overflow 16 (4) · Solar Flare (5) · Shim 8 (4) · Null (6) = 30 |
| Shim | 8 damage, FLAT |
| Defrag (BLOCK) | 10 FLAT × tier factor |
| Overflow | 14 damage, FLAT (a 4-tick slice has no Perfect, so it never lands as the Perfect pay-off; it is a readable 4-tick window) |
| Solar Flare | applies OVERCLOCKED to 1 random non-NULL slice of yours (existing INFECT slice, data only) |
| Null | nothing |
| Hub | none |
| Listeners | none |

The two needles sit 11 ticks apart. With 5/6/4/5/4/6 sizes, the second needle usually lands one slice ahead of the first. The player can see which needle gets Overflow and rotate the wheel (nudge, spin) so that needle reads Null or Defrag.

### Transition P1 → P2 "Lockdown order"
- Parks damage at the floor (R3). Statuses survive with the centre-tick remap (R6). **Not cleansed**, on purpose: any OVERCLOCKED slice you carry out of P1 stays and becomes P2's fuel. `cleanse_on_enter` = NONE.
- Layout and hub change (`wheel_override` + `hub_override`). Needles go to a single needle at tick 0 (MULTIPLY removed). Why: the question moves from "steer two" to "spend your overclocks", so one needle keeps the read simple.

### P2 "Lockdown" (50 → 0 %)
| Item | Value |
|---|---|
| Needles | 1 at tick 0, fixed |
| Resistance | 1 (kept) |
| Layout | Detonate (6) · Shim 8 (4) · Defrag (5) · Detonate (6) · Overflow (4) · Null (5) = 30 |
| Detonate (new slice, N20 rider) | 4 damage × your OVERCLOCKED slices (min 1), separate hits (`hits_per_target_status`); then it cleanses OVERCLOCKED from your wheel |
| Shim | 8 damage, FLAT |
| Defrag (BLOCK) | 8 FLAT × tier factor |
| Overflow | 16 FLAT, 4-tick, no Perfect |
| Solar Flare | none on the wheel. Hub rule below supplies it. |
| Hub rule "Flare Feed" | at its turn start, OVERCLOCK 1 random non-NULL slice of yours (hub, data via ON_TURN_START APPLY_STATUS) |
| Listeners | none |

Detonate's two slots are 6 ticks, so a Perfect (centre only) is a single tick out of six and Good covers three. A player who steers it to Null makes it fizzle; a player who has OVERCLOCKED slices at hand sees exactly how many hits will land (preview = result, since the count is deterministic after the turn-start Flare Feed).

**Deterministic note:** the random slice pick for Flare uses the existing `SlicePick.RANDOM_NON_NULL` stream, set at the start-of-turn respin checkpoint.

## 3. Sustain and intake
- **Sustain: none.** The only sustain-like effect is BLOCK on the Commander's own Defrag, which is not healing. Zero heal turns, which satisfies "at most 1 heal turn per phase".
- **Intake per turn at the reference player** (assumes the pointer sits on each slice with equal weight, and a free-nudge steer lowers the worst needle's contribution):
  - P1: two needles, each reads one of 6 slices. Expected damage per needle ≈ (8×5 + 14×4)/30 ≈ 3.2; two needles ≈ 6.4 before BLOCK. After the player's first steer (one needle to Null/Defrag) ≈ 3.5. Target 3–6.
  - P2: single needle. Shim 8×4 + Overflow 16×4 + Detonate (6+6 ticks × ~4 × typical 1.5 overclocks ≈ 6 per ground tick) → 32+64+72 = 168 / 30 ≈ 5.6 per turn on a random read. Heavy rises when the player has 3+ overclocked slices, since Detonate then hits 12+. Target 5–9.
- All intakes are above 0.

## 4. HP by tier (R2 elite band: T1 56–72, T2 68–88, T3 88–112, T4 112–144)
Phase budget = reference_dpt × 3.5 turns × needles hit. The player's hits land on the enemy's wheel, and the Commander has **2 needles in P1 and 1 in P2**, so P1 gets double hit-count weight (per the pointer rule, GDD 2.7). I take the single-needle phase as the base budget and the two-needle phase at ×1.5 (a conservative factor, because only some of the player's hits stack on two needles; the sim calibrates this). Sustain is 0.

| Tier | ref dpt | P2 (1 needle) = dpt × 3.5 | P1 (2 needles) = ×1.5 | Total | Chosen HP (band) |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 47 | 79 | **72** (band top; 79 clipped to the band) |
| T2 | 11 | 38.5 | 58 | 96 | **88** |
| T3 | 14 | 49 | 73.5 | 122 | **110** |
| T4 | 18 | 63 | 94.5 | 157 | **140** |

I clip to the band top, accepting a slightly faster fight (about 6 turns at the reference). Why: the old 154 HP was well above the T3 band (88–112), and that is the principal reason it ran long. Parking at 50 % puts the floor at 36 / 44 / 55 / 70 HP, so P1 is roughly 36 / 44 / 55 / 70 HP of work and P2 the same.
- Arithmetic at T3: floor = ceil(110 × 0.5) = 55. P1 = 55 HP at 14 dpt ≈ 3.9 turns, times the two-needle bonus, which pulls it to ≈ 3 turns. P2 = 55 HP at 14 ≈ 3.9 turns. Total ≈ 7. This matches the 6–8 target.

## 5. Enrage
**Default (start turn 8, every 5, +25 % damage, additive).** Reason: a fight of 6–8 turns finishes before turn 8 for a competent player, so enrage only bites a player who dithers over Flare management. No authored mechanic is needed; the Flare-fuse is already the pressure.

## 6. Buffs and counter Exploits
Not a boss. Not applicable.

## 7. Counterplay
- **P1:** use the free nudge on the needle that reads Overflow, so it lands on Null or Defrag. Both needles reading dangerous slices is the cost of a bad rotation. Keep the number of OVERCLOCKED slices in mind, because P2 will convert each into a hit. A Perfect on a Flared slice is 1.5× damage; take it.
- **P2:** the Detonate count is visible before End Turn. The reference answer: fire your OVERCLOCKED slices now (they are 1.5× for you), or Cleanse/Encrypt before they count. Steer the single needle off Detonate with a 1-tick nudge. Hold a Spin card for the turn Detonate's 6-tick window would read Good.
- **Weak players:** treat Flares as free damage and hoard OVERCLOCKED slices, and then eat a 20+ Detonate. They also nudge both needles toward the same side and take both big hits.

## 8. Systems needed
| N# | Use | Fallback |
|---|---|---|
| N11 | needles 0 / 11 | If missing, use the existing 0 / 15 with the same design. Weaker (less "one dangerous, one safe" asymmetry). |
| N12 | slice sizes 4/5/6 | Fallback: six 5-tick slices. Loses the "no Perfect on Overflow" window, and Detonate loses its wide fizzle. |
| N3 | phase 1→2, parking, status keep | Not data-only; needed. Without status keep, P2's fuel is wiped. |
| N20 | `hits_per_target_status` (Detonate) | Fallback: Detonate = flat 10 damage + cleanse OVERCLOCKED. It loses the "count your burns" question. |
| N9 | OVERCLOCKED stays as is; no new status | none needed |
| N1 | FLAT amounts × tier factor; fixes block scaling | Data-only fallback: bake tier values into the .tres. |
| N4 | enrage | Data-only fallback: none; the default applies once built. |

## 9. Delta vs today
- **Kept:** Shim, Defrag, Overflow, Solar Flare, Null; the 0-based pointer; resistance 1; the Orbital flavor.
- **Changed:**
  - HP 154 → 72 / 88 / 110 / 140 by tier.
  - Pointers 0 / 15 (even) → 0 / 11 (uneven) in P1.
  - Slice sizes become variable (4 / 5 / 6).
  - P2 is new: Detonate, Flare Feed hub, a single needle.
  - Shim 12 → 8; Overflow 16 → 14 (P1). Why: two needles ×12 and ×16 was too lethal with the pointer rule. Percent-of-reference: P1 intake ≈ 6 vs the old ≈ 8–10.
- **`heat_effects`: retire.** The file has none, and R1 says elites gain phases in place of HP-style heat riders. Nothing to port.
- The `cycle_reward = 35` is kept.

## 10. Predicted sim check
No baseline row exists for this enemy (the baseline covered Solace only). Estimates are from the wheel, not from a sim.
- Expected turns ≈ 6.5–7.5 at the step-0 skill, p90 ≈ 9.
- Win %: T1 ≈ 97 %, T2 ≈ 95 %, T3 ≈ 90 %, T4 ≈ 80 %. T4 is the pressure tier and lands below the 90 % target. Prediction is sensitive to Detonate; the sim may need −1 to the Detonate hit damage.
- Why: no sustain, parking keeps P1 from being skipped, and the Detonate threat is readable, so a skilled player trades an overclock burn for a fast kill.
- Compare with the old fight: HP 154 with no phases suggests ~12+ turns and attrition, so this is a roughly 40 % cut in length.

## 11. Open questions
Q: Is losing the "count your overclocks" question acceptable if N20 `hits_per_target_status` slips (the flat-10 fallback)?
Q: Should Detonate also cleanse OVERCLOCKED (so the burn is consumed), or leave it so the player keeps the 1.5× next turn?
Q: Should Flare Feed in P2 skip the player's slices that are ENCRYPTED, giving Encrypt a clear role as the counter?
Q: Is the 1.5× two-needle HP factor right, or should P1 count a full ×2?
Q: Should the P1 → P2 transition ever cleanse the player (`cleanse_on_enter` = PLAYER) for a gentler pass, or does keeping overclocks defeat that?
