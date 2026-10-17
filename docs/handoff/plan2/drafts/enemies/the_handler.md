<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__the_handler; status ok; tokens in 16889 cache-write 0 cache-read 32007 out 39638; cost $0.218. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# the_handler: direct design

## 1. Identity & the one question
**Class:** mini-boss, 3 phases, fresh-fight target 9 turns (band 6–12). It guards the final Server Rack of every REBEL_CELL netrun at T1–T3, so it is always a layer-7 pressure fight. The first T1 meeting is also where the player learns coupled wheels and the Perfect trade.

**Theme:** the Handler mirrors your hands, then your precision, then drops the mirror.
- **Mirrors your motion** (P1).
- **Mirrors your precision** (P2).
- **Burns the file** and attacks with two needles (P3).

This stays distinct from the Mirror Script / Echo Process normals, which I assume copy slices. The Handler never copies a slice. It reacts to how you move and how precisely you land.

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Shadow | Your free nudge moves both wheels. Which shared rotation is good for you and bad for it? | Find a shared rotation that costs no RAM. Decouple with a Spin or Flip card, or a direct nudge on its wheel. |
| P2 Override | Is a Perfect worth its Echo, and what do you do on a turn you cannot nudge? | Choose Perfect or Good per slice. Plan the locked turns with cards. |
| P3 Burn Notice | Two uneven needles: which one gets the danger, and can you afford the RAM to steer? | Read the needle-pair table, spend RAM on the one rotation that matters, and strike when both needles sit on damageable slices. |

**Concept change:** I refined the section-3 concept in four ways.
- **Echo scales:** it hits for 60% of the landed slice's output instead of a flat 50%.
- **Coupling is an explicit rule:** it is mechanically pinned down as a nudge listener.
- **TIER_DOWN replaces the Citation parasite:** Citation is Halcyon's mini-boss identity. TIER_DOWN fits "it knows how you fight".
- **Cleanse added:** a PLAYER cleanse on entering P3.

## 2. Phase plan
HP shares are shown at T1 (HP 105). Thresholds are 0.735 / 0.47 at every tier. Flat amounts below are T1 base values, scaled by the R2 damage factor (×1.3 at T2, ×1.69 at T3).

### P1 Shadow (100 → 73.5 %, 27 HP at T1)
| Field | Value |
|---|---|
| Needles | 1, at tick 0, FIXED |
| Hub | Resistance 0. Listener **Shadow**: ON_NUDGE on your own wheel by k ticks (nudge actions and NUDGE effects, not SPIN / FLIP / RESPIN / SNAP) → NUDGE its wheel by the same signed k. It ignores resistance and is staged with the action, so undo is clean. |
| Statuses | CORRUPTED from Dose (your RAM cost ×2 on that slice, so nudging with a corrupted slice under the pointer costs double) |

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Order | 7 (W W G P G W W) | SHIM 6 | FLAT |
| 2 | Dose | 4 (W G G W) | INFECT: CORRUPTED on 1 random non-NULL slice of yours | FLAT 1 slice |
| 3 | Order | 5 | SHIM 6 | FLAT |
| 4 | Directive | 6 (W W G G W W) | OVERFLOW 14 | FLAT |
| 5 | Null | 5 | none | n/a |
| 6 | Dose | 3 (G P G) | as slice 2 | FLAT 1 slice |

Sizes sum to 30 (7+4+5+6+5+3).

### P2 Override (73.5 → 47 %, 28 HP at T1)
| Field | Value |
|---|---|
| Needles | 1, at tick 0. The pointer stays FIXED. |
| Hub | Resistance 1. **Override lock** (N7): your own-wheel nudge actions are refused on phase-turns 2, 4, 6… (turn 1 is free). It is shown at turn start as an overlay with the reason. Cards still work, including nudge cards. |
| Listener | **Echo** (ON_PERFECT, yours): you take 60 % of the landed slice's output (after tier, before hooks, minimum 1, 0 if the output is 0) as one hit. BLOCK and SHIELD absorb it; SANDBOX negates it. Preview chip "ECHO −N". |
| Statuses | TIER_DOWN from Mark (a tier-down is not a Perfect, so a marked slice dodges Echo and also loses the hook). CORRUPTED from Dose. |

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Order | 6 | SHIM 6 | FLAT |
| 2 | Override | 5 (W G P G W) | OVERFLOW 15 | FLAT |
| 3 | Mark | 4 (W G G W) | TIER_DOWN on 1 random non-NULL slice of yours | FLAT 1 slice |
| 4 | Order | 5 | SHIM 6 | FLAT |
| 5 | Dose | 3 | as P1 | FLAT 1 slice |
| 6 | Null | 7 | none | n/a |

Sizes sum to 30 (6+5+4+5+3+7).

**P1 → P2:** damage parks at the floor (ceil(105 × 0.735) = 78). Statuses are kept and remapped by centre tick (R6). The wheel is overridden, Shadow is removed, and the Override hub is installed. `cleanse_on_enter = NONE`, so your CORRUPTED slices from P1 carry into P2's RAM puzzle.

**Phase line:** "The Handler stops echoing and starts overriding."

### P3 Burn Notice (47 → 0 %, 50 HP at T1)
| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 11 (R10, MULTIPLY, uneven, so only one can be Perfect) |
| Hub | Resistance 0. No listeners and no lock: the mirror is gone and this is a pure solve. |
| Statuses | CORRUPTED (Dose) and TIER_DOWN (Mark), both landing from two needles |

| # | Slice | Ticks (wheel frame) | Effect | Mode |
|---|---|---|---|---|
| 1 | Order | 5 (0–4) | SHIM 8 | FLAT |
| 2 | Redact | 3 (5–7, G P G) | BLOCK 8 | FLAT |
| 3 | Directive | 6 (8–13) | OVERFLOW 16 | FLAT |
| 4 | Null | 4 (14–17) | none | n/a |
| 5 | Dose | 4 (18–21) | CORRUPTED on 1 random non-NULL slice of yours | FLAT 1 slice |
| 6 | Order | 4 (22–25) | SHIM 8 | FLAT |
| 7 | Mark | 4 (26–29) | TIER_DOWN on 1 random non-NULL slice of yours | FLAT 1 slice |

Sizes sum to 30 (5+3+6+4+4+4+4). This needs the lifted 6-slice cap (N12).

**Needle-pair table.** The two needles sit 11 ticks apart. Over the 30 rotations:

| Pair reads | Rotations |
|---|---|
| Damage + damage | 8 (27 %) |
| Damage + status | 9 |
| Damage + safe (Null or Redact) | 5 |
| Status + safe | 5 |
| Status + status | 1 |
| Safe + safe | 2 |

The player's job is to leave the 8 double-damage rotations and reach a safe or status-only one.

**P2 → P3:** damage parks at the floor (ceil(105 × 0.47) = 50). Statuses remap (R6). Wheel and hub are overridden, with MULTIPLY to (0, 11). `cleanse_on_enter = PLAYER`: the Handler burns your marks, so P3's RAM and tier question starts from a clean wheel and only its own two needles build it back up.

**Phase line:** "The Handler burns the notice."

## 3. Sustain and intake
**Sustain:** exactly one source, the Redact BLOCK in P3 (none in P1 or P2). No heal.
- Probability a needle reads Redact is 3/30 = 0.1, and two needles give 0.2 expected hits of BLOCK 8, so the expected absorption is **1.6/turn at T1**.
- That is 18 % of the reference 9 dpt, under the 30 % cap. At T2 it is 2.1 (19 % of 11) and at T3 it is 2.7 (19 % of 14).

**Intake per turn** (T1 base, pre-block, expected over uniform landings with tier-averaged factors; "ref" assumes the reference player's steering removes about 35 % and picks Perfects selectively):

| Phase | Raw | At reference | Target |
|---|---|---|---|
| P1 | 3.7 (Order 1.8 + Directive 1.9) | 2.2 | 2–3 |
| P2 | 3.6 slices + Echo | 4.5 (2.3 slices + about 0.4 Perfect-echoes/turn × 5.4) | 4–6 |
| P3 | 8.0 (4.0 per needle) | 5.6 | 5–7 |

All values are above 0. At T1 this totals about 37 HP over a reference fight (2.2×3.05 + 4.5×3.05 + 5.6×3.05) before cards. T2 is ×1.3 and T3 ×1.69.

## 4. HP by tier
R2 budget = `reference_dpt` × 3.5 × (needles landing) − sustain × 3.5. P3 uses 2 needles, since every player hit lands twice.

| Tier | P1 | P2 | P3 (2 needles, minus sustain) | Unconstrained sum | Band | Authored HP |
|---|---|---|---|---|---|---|
| T1 (dpt 9) | 31.5 | 31.5 | 63 − 5.6 = 57.4 | 120.4 | 85–105 | **105** (27 / 28 / 50) |
| T2 (dpt 11) | 38.5 | 38.5 | 77 − 7.3 = 69.7 | 146.7 | 104–128 | **128** (33 / 34 / 61) |
| T3 (dpt 14) | 49 | 49 | 98 − 9.5 = 88.5 | 186.5 | 132–162 | **162** (42 / 43 / 77) |
| T4 | n/a | | | | | n/a (no mini-boss at T4) |

**Deviation, stated plainly:** the 3-phase band assumes about one needle per phase. Applying the proportional pointer rule to P3 would put the totals 15–25 % above the band. I hold the band at its ceiling and scale every phase by about 0.87. The result is that each phase takes about 3.05 turns at the reference, instead of 3.5. Floors (T1 / T2 / T3): 78 / 50, 95 / 61, 120 / 77.

## 5. Enrage
**Default** (start 10, every 5, +25 % additive). The reference fight ends around turn 9.2, so the clock fires just after a reference win. Slower players meet the first step in P3, which stops a stalled P3 from snowballing. I dropped the concept's turn 8 because it would tax the reference player and stack with Echo.

## 6. Buffs and counter Exploits
n/a. Mini-bosses carry no boss buffs. Exploits (Intel, Breach, Virus) don't change this fight, since the pointer-removing Breach text is boss-only.

## 7. Counterplay
- **P1:**
  - **Good player:** reads the preview chip on each hover. It shows where its needle will land after the coupled nudge. They pick a rotation that keeps the Handler on Null or a Dose edge. Alternatively they decouple with a Spin or Flip card (neither triggers Shadow), or nudge the Handler's wheel directly (it has 0 resistance here) to undo the coupling at 1 RAM per tick. They keep CORRUPTED slices off the pointer so nudges stay cheap.
  - **Weak player:** nudges their own wheel for a Perfect without noticing the Handler's needle moved onto Directive, then burns RAM fixing it. Corrupted slices make the fix cost 2× RAM.
- **P2:**
  - **Good player:** takes Good over Perfect on big slices (the Echo is 60 % of the output), and Perfects on small slices or when the hook pays. On locked turns they hold a nudge or spin card instead of a nudge. SANDBOX or BLOCK soaks the Echo or a Directive Perfect.
  - **Weak player:** chases Perfects every turn and takes Echo each time, tries to nudge on locked turns and gets refused, and ignores TIER_DOWN marks.
- **P3:**
  - **Good player:** uses the needle-pair table. The free nudge (plus RAM) moves both needles together, so they steer to a safe+damage or status-only rotation and save a Cleanse for CORRUPTED. Kill-turns are the ones where both needles sit on damageable slices and Redact is not under either.
  - **Weak player:** drifts into the 27 % double-damage rotations, spends RAM on repeated nudges, and lets CORRUPTED double the cost.

## 8. Systems needed
| Dependency | Why | Data-only fallback |
|---|---|---|
| N1 amount modes | FLAT × tier factor | Fixed amounts per tier |
| N2 tier tables | `hp_by_tier`, `enemy_damage_by_tier` | Author three `.tres` files |
| N3 phases and parking | floors, status remap, `cleanse_on_enter` | Existing boss phases without parking |
| N4 enrage | class default | None; the Handler is slower without it |
| N6 enemy listeners | ON_NUDGE coupling (P1) and ON_PERFECT Echo (P2). **NEW rider:** an amount derived from the triggering slice's output. | Flat Echo 5 ×factor; P1 coupling has no data-only form (replace with resistance 2) |
| N7 nudge lock | P2 Override | None; drop the lock and keep Echo |
| N9 status rules | TIER_DOWN, CORRUPTED as a RAM debuff | Mark becomes the Citation PARASITE slice; Dose as today |
| N11 pointers on any tick | P3 needle at tick 11 | Needle at 10 |
| N12 slice sizes | all three layouts | 6 × 5-tick slices; the sub-tick quality puzzle is lost |
| N14 defense trio names | BLOCK on Redact | Use DEFRAG |
| N19 sim metrics | turns per phase, Echo fires, parked damage | None |

N8 (×N stacks) is optional: Mark is applied at ×1 here.

## 9. Delta vs today
**Today:** 170 HP, six 5-tick slices (Shim 12, Dose, Overflow 16, Citation, Sandbox 8, Null), resistance 2 for the whole fight, phases at 50 % (MULTIPLY to 0/15) and 25 % (ORBIT 3).

**Changes:**
- HP 170 → 105 / 128 / 162 (T1 / T2 / T3).
- Thresholds 0.5 / 0.25 → 0.735 / 0.47, with three authored wheel layouts.
- Resistance 2 permanent → 0 / 1 / 0 per phase.
- ORBIT is gone. MULTIPLY (0, 11) replaces (0, 15).
- Citation and Sandbox 8 are dropped. TIER_DOWN Mark, Redact BLOCK and Order are new.

**Kept:** id `the_handler`, `is_elite` and `is_mini_boss` flags, `cycle_reward = 60`, Dose, Overflow, Shim and Null as templates.

**heat_effects:** none authored today; none added.

**New files:** `content/slices/hd_*.tres` and three phase resources.

## 10. Predicted sim check
No baseline row exists, so this is a hand estimate.

| Tier | Turns (reference) | Win % (step-0 skill) | Why |
|---|---|---|---|
| T1 | about 9.2 | about 96 % | intake of about 37 over about 9 turns vs 45–60 HP and card block |
| T2 | about 9.3 | about 91 % | ×1.3 damage |
| T3 | about 9.4 | about 84 % | ×1.69 damage; the 2-needle P3 and Dose RAM tax bite |

- **Risks:** T2 and T3 may miss the 95 % / 90 % pass criteria. The tuning knob is Directive 14–16 down toward 12 and P3 Order 8 down to 7.
- **Bot ceiling:** a skill-1.0 bot (16–35 dpt) could finish in about 5.5 turns, below the 6-turn floor. Parking guarantees at least 3 resolves, and I would raise P3 HP rather than weaken the phases.
- **For scale:** today's 170 HP at T1 should run about 19 turns at the reference, in line with the long-fight baseline rows (Account Manager 20.7 turns at T3).

## 11. Open questions
Q: Raise the 3-phase band to fit a 2-needle P3? Right now phases are about 3.05 turns instead of 3.5.
Q: Should Echo scale with the landed slice (60 %, needs a context-read rider on N6) or be flat 5? The flat version is data-only but never punishes a big Perfect.
Q: Does Shadow also fire on SPIN effects? I excluded them so Spin cards are the clean decoupler.
Q: Is the PLAYER cleanse on entering P3 right, or should P3 inherit your accumulated statuses?
Q: The Virus Exploit puts CORRUPTED on the boss's slices. Does a mini-boss ignore that, given CORRUPTED is now a RAM debuff on enemy wheels and does nothing here?
