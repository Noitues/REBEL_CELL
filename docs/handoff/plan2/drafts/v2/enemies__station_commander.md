<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__station_commander; status ok; tokens in 7953 cache-write 0 cache-read 32585 out 5270; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, HP table / double-needle factor):** Dropped the invented ×1.5 factor and the "clip to band top" step. R2 prices a phase as `reference_dpt × 3.5 × needles the player's hits land on`. Needles on the enemy's wheel don't change how many of the player's hits land, so the P1 budget does not scale with them. Both phases hold equal HP because the floor is 50 %, and each half is checked against dpt × 3.5. HP is now 64 / 78 / 100 / 128. Each total sits inside the band, and the floors are 32 / 39 / 50 / 64.
- **Issue 2 (BLOCKER, Shim 12 vs 8):** The layout label is fixed. Shim is 8 FLAT in the layout, the table and §9. The old 12 appears only as the "today" value.
- **Issue 3 (BLOCKER, Perfect rules / tick quality):** Tick quality is now stated per slice from the R11 map. 4-tick slices (W G G W) have no Perfect, 5-tick slices have one, and 6-tick slices (W W G G W W) also have no Perfect. The 6-tick Defrag and Detonate are Perfect-less too; the v1 claim of a Perfect "at the centre" of a 6-tick slice was wrong. Intake is recomputed with the WEAK 0.5× weights (see §3).
- **Issue 4 (MAJOR, overclock decay):** Stated that unfired OVERCLOCKED slices still burn out into CORRUPTED when they trigger (the 2× RAM tax of R9). **Decision:** Detonate consumes the OVERCLOCKED stacks it counts (the 1.5× is lost), so firing your overclocked slices first is the answer. This also settles v1's Q2.
- **Issue 5 (MAJOR, P2 intake arithmetic):** Redone per read-probability, with tick quality (§3).
- **Issue 6 (MAJOR, Flare Feed runaway):** Stated that Flare Feed guarantees at least one OVERCLOCKED slice at each resolve. The floor is k ≥ 1, so cleansing never reaches zero hits. "Cleanse" becomes "trim k", and Encrypt on a slice absorbs the Feed (Encrypt is the explicit counter). Flare Feed also skips ENCRYPTED slices, which settles v1's Q3.
- **Issue 7 (MAJOR, RNG stream):** Both random picks (Solar Flare in P1, Flare Feed in P2) use the named `combat` RNG stream, drawn at the start-of-turn respin checkpoint. No draws happen after the player's actions.
- **Issue 8 (NIT, heat_effects):** Not verified against the file. Retire anyway, and flag it for the content agent to confirm the field is empty. If any rider exists, it is dropped.
- **Issue 9 (NIT, Qs):** Q4 and Q5 are resolved in the draft (see §4 and §2). Replaced with open questions about the Flare Feed floor and T4 tuning.

---

# station_commander: direct design

## 1. Identity & the one question
- **Class:** Elite, Orbital Commons. Two phases, one threshold. Appears in L5-6 (pressure); never a teaching enemy. A T1 Site draws it only in the late layers.
- **Theme:** A station commander runs a drill, then orders a lockdown.
- **Distinct from:** the Geostationary Guard, and the Mission Director (rim gates and satellite replacement). The Commander uses uneven needles plus Flare overclock bait, with no gates and no satellites.
- **P1 question: "Which of my slices do I let it read?"** Two uneven needles (0 / 11): one lands on a dangerous slice, one on a safe one. Flares overclock your slice, so a Perfect on a Flared slice is both a gift and a trap. Answer: steer the dangerous needle to Null, Defrag or a WEAK edge, and spend your Flared slices for 1.5×.
- **P2 question: "Can I spend an overclock before it is taken from me?"** Detonate hits once per OVERCLOCKED slice you carry, then consumes them. Answer: fire your overclocked slices first (1.5× for you), then burst. This shortens the fight.

## 2. Phase plan
**Threshold:** 0.50. The HP floor is ceil(max × 0.5) while P1 is active (R3); the excess is lost. P2 has no floor. Values are T1 base, before the tier damage factor (R2).

### P1 "Drill" (100 → 50 %)
| Item | Value |
|---|---|
| Needles | 2: ticks 0 / 11 (uneven, R10), fixed |
| Resistance | 1, passive, restores each turn |
| Layout | Shim (5) · Defrag (6) · Overflow (4) · Solar Flare (5) · Shim (4) · Null (6) = 30 |
| Shim | 8 damage FLAT |
| Defrag (BLOCK) | 10 FLAT × tier factor |
| Overflow | 14 damage FLAT |
| Solar Flare | OVERCLOCKED on 1 random non-NULL slice of yours (existing INFECT slice, data only) |
| Null | nothing |
| Tick quality (R11) | Shim 5: W G P G W · Defrag 6: W W G G W W · Overflow 4: W G G W · Flare 5: W G P G W · Shim 4: W G G W · Null 6 |
| Hub / listeners | none |

The needle at 11 sits in the middle of the Overflow window. In the sizes above, Shim (5) occupies ticks 28–2, Defrag 3–8, Overflow 9–12 and Flare 13–17. Needle 0 reads Shim and needle 11 reads Overflow in the opening position. Rotating by 3 ticks swaps the two reads.

### Transition P1 → P2 "Lockdown order"
- Parks damage at the floor (R3). Statuses survive with the centre-tick remap (R6). `cleanse_on_enter` = NONE: OVERCLOCKED slices carried from P1 are P2's fuel.
- `wheel_override` + `hub_override`. Needles collapse to a single needle at tick 0, so the question moves from steering two needles to spending overclocks.

### P2 "Lockdown" (50 → 0 %)
| Item | Value |
|---|---|
| Needles | 1 at tick 0, fixed |
| Resistance | 1 |
| Layout | Detonate (6) · Shim (4) · Defrag (5) · Detonate (6) · Overflow (4) · Null (5) = 30 |
| Detonate (N20 rider) | 4 damage × your OVERCLOCKED slices (min 1), separate hits; **consumes the counted OVERCLOCKED stacks** |
| Shim | 8 FLAT |
| Defrag (BLOCK) | 8 FLAT × tier factor |
| Overflow | 16 FLAT |
| Tick quality | Detonate 6: W W G G W W · Shim 4 and Overflow 4: W G G W · Defrag 5: W G P G W. Only Defrag can be Perfect. |
| Hub "Flare Feed" | At its turn start, OVERCLOCK 1 random non-NULL, non-ENCRYPTED slice of yours (ON_TURN_START APPLY_STATUS) |
| Listeners | none |

- **Floor:** Flare Feed guarantees k ≥ 1 at every resolve, unless every slice is ENCRYPTED. Encrypt is the counter.
- **Decay:** an OVERCLOCKED slice that triggers burns out into CORRUPTED (R9, 2× RAM). Detonate removes the status first, so the burn never happens.
- **RNG:** both random picks use the named `combat` stream, drawn at the start-of-turn checkpoint, so the preview equals the result.

## 3. Sustain and intake
- **Sustain: none.** Its Defrag is BLOCK, not healing. 0 heal turns.
- **Intake per turn** (a landing is WEAK 0.5× when it reads a WEAK sub-tick; tick-share weights per the R11 maps; the figures are before BLOCK):
  - **Shim 5-tick:** reads W 2/5, G 2/5, P 1/5 → ×(0.5×0.4 + 0.6) = 0.8 → 8 × 0.8 = 6.4 per hit. **Shim 4-tick:** W 2/4 → ×0.75 → 6.0.
  - **P1 per needle:** Shim (5): 5/30 × 6.4 = 1.07; Shim (4): 4/30 × 6.0 = 0.80; Overflow (4): 4/30 × 14 × 0.75 = 1.40. Sum ≈ 3.27 per needle, ≈ 6.5 for two. With one steered to Null or Defrag, ≈ 3.3–4. Target 3–6 ✓.
  - **P2 (single needle):** Shim (4): 0.80. Overflow (4): 4/30 × 16 × 0.75 = 1.60. Detonate (12/30 = 0.4 of reads): damage 4k × quality (W W G G W W: 4/6 WEAK → ×0.67) = 2.7k per read → 0.4 × 2.7k ≈ 1.07k. k = 1 → 3.5 per turn. k = 3 → 5.6. k = 5 → 7.7. Target 4–8 ✓ (all > 0).
- Enrage is not included above.

## 4. HP by tier (R2 elite band: T1 56–72, T2 68–88, T3 88–112, T4 112–144)
With a 0.50 floor, each phase holds half of max HP. Each phase is priced at `ref_dpt × 3.5` (the player's hits land once per player phase regardless of enemy needles). Sustain is 0, so no deduction.

| Tier | ref dpt | Per phase = dpt × 3.5 | Phase HP (rounded) | **HP = 2 phases** | Floor (50 %) | In band? |
|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 32 | **64** | 32 | 56–72 ✓ |
| T2 | 11 | 38.5 | 39 | **78** | 39 | 68–88 ✓ |
| T3 | 14 | 49 | 50 | **100** | 50 | 88–112 ✓ |
| T4 | 18 | 63 | 64 | **128** | 64 | 112–144 ✓ |

- T3 check: floor = ceil(100 × 0.5) = 50. P1 = 50/14 ≈ 3.6 turns, P2 ≈ 3.6 turns, total ≈ 7.1 ✓ (target 6–8).
- Today is 154 HP, above the T3 band.

## 5. Enrage
**Default (start 8, every 5, +25 % additive).** A competent player finishes in 7, so enrage only punishes dithering. The Flare Feed already provides the pressure, so no authored trigger.

## 6. Buffs and counter Exploits
Not a boss. Not applicable.

## 7. Counterplay
- **P1:** use the free nudge to move the needle reading Overflow onto Null, Defrag or a WEAK edge. Take Perfects on Flared slices at 1.5×. Remember that every OVERCLOCKED slice you keep becomes a Detonate hit.
- **P2:** the Detonate count is visible before End Turn. Fire your OVERCLOCKED slices first, or Encrypt a slice so Flare Feed skips it. A 1-tick nudge moves the single needle out of Detonate's 6-tick window. Hold a Spin for a turn when Detonate would read.
- **Weak players:** hoard Flares as free damage and then eat Detonate at k = 4+ (about 16 raw). Or they nudge both P1 needles to the same side and take Overflow twice.

## 8. Systems needed
| N# | Use | Fallback |
|---|---|---|
| N3 | phase transition, parking, status keep | Required. Without status keep, P2's fuel is wiped. |
| N11 | needles 0 / 11 | Existing 0 / 15, same design; weaker asymmetry |
| N12 | slice sizes 4 / 5 / 6 | Six 5-tick slices; loses the Perfect-less Overflow and Detonate windows |
| N20 | `hits_per_target_status` (Detonate) | Flat 10 damage + consume OVERCLOCKED; loses "count your burns" |
| N1 | FLAT amounts × tier factor | Bake tier values into the .tres |
| N2 | `hp_by_tier` | Required for per-tier HP |
| N4 | enrage | Default applies once built |
| N9 | CORRUPTED as RAM cost (OVERCLOCKED burnout stays) | none needed |

## 9. Delta vs today
- **Kept:** Shim, Defrag, Overflow, Solar Flare, Null; the pointer at 0; resistance 1; the Orbital flavor; `cycle_reward = 35`.
- **Changed:**
  - HP 154 → 64 / 78 / 100 / 128.
  - Pointers 0 / 15 (even) → 0 / 11 (uneven) in P1.
  - Variable slice sizes (4 / 5 / 6).
  - Shim 12 → 8 and Overflow 16 → 14 in P1, since two needles at the old values were too lethal.
  - New P2: Detonate, Flare Feed hub, a single needle.
- **`heat_effects`: retire.** The v1 claim that the file has none is unverified, so the content agent should confirm. Any rider found is dropped, because R1 replaces HP-style elite riders with phases.

## 10. Predicted sim check
There is no baseline row for this enemy (the baseline covered Solace only), so these estimates come from the wheel math.
- Expected turns ≈ 6.5–7.5 at the step-0 skill, p90 ≈ 9.
- Win %: T1 ≈ 97 %, T2 ≈ 95 %, T3 ≈ 90 %, T4 ≈ 82 %. T4 is the pressure tier and may sit below 90 %. Detonate at k ≥ 3 is the sensitive lever, and the sim may drop it to 3 per hit.
- Why: no sustain, parking forces both phases, and Detonate is readable, so a skilled player trades a burn for a fast kill.
- Against today (154 HP, no phases, probably 12+ turns): about a 40 % cut.

## 11. Open questions
Q: Should Flare Feed pause when the player already holds 3+ overclocks, to prevent a runaway?
Q: Is T4 win ≈ 82 % acceptable, or should Detonate drop to 3 per hit?
Q: If N20 slips, is the flat-10 Detonate fallback acceptable without the "count your burns" question?
Q: Should Encrypt protect a slice from Flare Feed only, or from Detonate counting as well?
Q: Should P1 → P2 ever cleanse the player (`cleanse_on_enter` = PLAYER) for a gentler pass, even though that removes the fuel?
