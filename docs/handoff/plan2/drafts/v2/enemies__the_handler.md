<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__the_handler; status ok; tokens in 9629 cache-write 0 cache-read 32585 out 17962; cost $0.103. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **#1 (BLOCKER, HP above the budget sum):** Fixed by redoing the arithmetic. The R2 budget at 3.5 turns per phase with a proportional 2-needle P3 sums to 120 / 147 / 187, which is above the 3-phase band. I authored HP at 3.0 reference turns per phase, the R1 floor. That budget sums to 103 / 126 / 160, inside the band. The "scale by 0.87" claim is gone. The deviation from R2's 3.5 is stated in §4 and raised as Q1. The critic's Option A (90 / 110 / 138 split 30 / 30 / 30) was **not** taken: it leaves P3 at 30 HP against 18 effective dpt, which is about 1.7 turns, and breaks R1 worse.
- **#2 (BLOCKER, P1/P2 under 3 turns):** P1 and P2 are now 28 / 34 / 43 HP (T1 / T2 / T3), which is 3.1 reference turns each. P3 is 49 / 60 / 76 HP, 3.0 turns including its sustain. Thresholds are now 0.733 / 0.466 (were 0.735 / 0.47), so the integer floors give exactly these splits. The reference meets the 3-turn floor with no slack; §4 says so plainly. The bot ceiling and what the guarantee does and does not cover are in §10.
- **#3 (sustain label):** Kept as the single source, relabeled "enemy defense, counted as sustain conservatively". The share is 18–19 % of the reference damage per turn.
- **#3b (RNG):** Every random-slice rider (Dose, Mark) now names the `fight` stream, drawn at the checkpoint. The preview shows odds (GDD 2.10).
- **#4 (NEW tags):** Echo's output-read amount is tagged NEW: listener output-read rider (N6 extension). Shadow's resistance bypass and coupling are tagged NEW: coupled-wheel nudge response (N6 extension). Each has a fallback.
- **#5 (P3 cleanse):** `cleanse_on_enter = NONE`. P2's CORRUPTED and TIER_DOWN now carry into P3's two-needle phase, so P2 sets up a question that P3 inherits. The Cleanse and Encrypt cards are in the counterplay.
- **#6 (enrage):** Default (start 10) kept. §5 now states the intended effect.
- **#7 (T3 win rate and the 19-turn claim):** I lowered Directive and Override damage (12 / 14 / 14) and P3 Order to 7. T3 win is now about 88 %, still just under the 90 % criterion. The first knob is P3 Order 7 → 6. The "19 turns" line is reworded as arithmetic only, not a baseline measurement.
- **#8 (needle table):** Re-derived tick by tick for needles at 0 and 11. The counts match v1 (8 / 9 / 5 / 5 / 1 / 2 = 30). Both needles stay inside a slice interior for the damage classes.
- **#9 (Mirror Script overlap):** §1 now says how it differs. The normals copy slices, while the Handler couples wheel motion and punishes landing quality.
- **Kept, because strong:** the three questions, the uneven needle at tick 11 with the pair table, Echo against Perfects, and Spin/Flip as decouplers.

# the_handler: direct design

## 1. Identity & the one question
**Class:** mini-boss, 3 phases, fresh-fight target about 9 turns (band 6–12). It is the REBEL_CELL corporation's guard of the final Server Rack at T1–T3, so it is always a layer-7 pressure fight. The first T1 meeting also teaches coupled wheels and the Perfect trade.

**Theme:** the Handler mirrors your hands (P1), your precision (P2), then burns the file (P3).

**Difference from the normals:** Mirror Script and Echo Process copy slices. The Handler never copies a slice. It couples its wheel to your nudges and punishes how precisely you land.

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Shadow | Your free nudge moves both wheels. Which shared rotation is good for you and bad for it? | Find a shared rotation that costs no RAM. Decouple with Spin/Flip or a direct nudge on its wheel. |
| P2 Override | Is a Perfect worth its Echo, and what do you do on a turn you cannot nudge? | Choose Perfect or Good per slice. Plan the locked turns with cards. |
| P3 Burn Notice | Two uneven needles, and you carry P2's marks: which needle gets the danger, and can you afford the RAM to steer? | Read the needle-pair table, steer with RAM, and strike when both needles sit on damageable slices. |

**Changes vs the section 3 concept:**
- Echo scales with the landed slice (60 %) instead of a flat 50 %.
- Coupling is pinned down as a nudge listener.
- TIER_DOWN (Mark) replaces the Citation parasite, because Citation is Halcyon's identity.
- The turn-8 enrage is dropped for the default.

## 2. Phase plan
Thresholds are 0.733 / 0.466 at every tier. Flat amounts are T1 base values and are scaled by the R2 damage factor (×1.3 at T2, ×1.69 at T3). Every "random slice" rider uses RNG stream `fight`, drawn at the checkpoint. The preview shows odds.

### P1 Shadow (100 → 73.3 %; 28 HP at T1)
| Field | Value |
|---|---|
| Needles | 1, at tick 0, FIXED |
| Hub | Resistance 0. Listener **Shadow**: your own-wheel nudge actions of k ticks (not SPIN / FLIP / RESPIN / SNAP) trigger a NUDGE of its wheel by the same signed k. It ignores resistance, is staged with the action and undoes with it. **NEW: coupled-wheel nudge response (N6 extension).** |
| Statuses | CORRUPTED from Dose (R9: acting at a corrupted slice costs 2× RAM) |

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Order | 7 (W W G P G W W) | SHIM 6 | FLAT |
| 2 | Dose | 4 (W G G W) | CORRUPTED on 1 random non-NULL slice of yours | FLAT, 1 slice |
| 3 | Order | 5 | SHIM 6 | FLAT |
| 4 | Directive | 6 (W W G G W W) | OVERFLOW 12 | FLAT |
| 5 | Null | 5 | none | n/a |
| 6 | Dose | 3 (G P G) | as slice 2 | FLAT, 1 slice |

Sizes: 7+4+5+6+5+3 = 30.

### P2 Override (73.3 → 46.6 %; 28 HP at T1)
| Field | Value |
|---|---|
| Needles | 1, at tick 0, FIXED |
| Hub | Resistance 1. **Override lock** (N7): your own-wheel nudge actions are refused on phase-turns 2, 4, 6… Turn 1 is free. An overlay shows the reason at turn start. Cards still work, including nudge cards. |
| Listener | **Echo** (ON_PERFECT, yours): you take 60 % of the landed slice's output (after tier, before hooks, minimum 1, 0 if the output is 0) as one hit. BLOCK and SHIELD absorb it, SANDBOX negates it. Preview chip "ECHO −N". **NEW: listener output-read rider (N6 extension).** |
| Statuses | TIER_DOWN from Mark: a marked slice cannot read Perfect, so it dodges Echo and also loses the Perfect hook. CORRUPTED from Dose. |

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Order | 6 | SHIM 6 | FLAT |
| 2 | Override | 5 (W G P G W) | OVERFLOW 14 | FLAT |
| 3 | Mark | 4 (W G G W) | TIER_DOWN on 1 random non-NULL slice of yours | FLAT, 1 slice |
| 4 | Order | 5 | SHIM 6 | FLAT |
| 5 | Dose | 3 | as P1 | FLAT, 1 slice |
| 6 | Null | 7 | none | n/a |

Sizes: 6+5+4+5+3+7 = 30.

**P1 → P2:**
- Damage parks at the floor (T1: ceil(105 × 0.733) = 77).
- Statuses are kept and remapped by centre tick (R6).
- The wheel is overridden, Shadow is removed and the Override hub is installed.
- `cleanse_on_enter = NONE`.
- Phase line: "The Handler stops echoing and starts overriding."

### P3 Burn Notice (46.6 → 0 %; 49 HP at T1)
| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 11 (R10, MULTIPLY, uneven: only one can be Perfect) |
| Hub | Resistance 0. No listeners and no lock: the mirror is gone. |
| Statuses | CORRUPTED (Dose) and TIER_DOWN (Mark), carried from P2 and added to by two needles |

| # | Slice | Ticks (wheel frame) | Effect | Mode |
|---|---|---|---|---|
| 1 | Order | 5 (0–4) | SHIM 7 | FLAT |
| 2 | Redact | 3 (5–7, G P G) | BLOCK 8 | FLAT |
| 3 | Directive | 6 (8–13) | OVERFLOW 14 | FLAT |
| 4 | Null | 4 (14–17) | none | n/a |
| 5 | Dose | 4 (18–21) | CORRUPTED on 1 random non-NULL slice of yours | FLAT, 1 slice |
| 6 | Order | 4 (22–25) | SHIM 7 | FLAT |
| 7 | Mark | 4 (26–29) | TIER_DOWN on 1 random non-NULL slice of yours | FLAT, 1 slice |

Sizes: 5+3+6+4+4+4+4 = 30. This needs the lifted slice cap (N12).

**Needle-pair table.** The needles sit 11 ticks apart. Classes: Order and Directive are damage, Redact and Null are safe, Dose and Mark are status.

| Pair reads | Rotations |
|---|---|
| Damage + damage | 8 (ticks 0 1 2 11 12 13 22 23) |
| Damage + status | 9 |
| Damage + safe | 5 |
| Status + safe | 5 |
| Status + status | 1 |
| Safe + safe | 2 |

The total is 30. The player's job is to leave the 8 double-damage rotations.

**P2 → P3:**
- Damage parks at the floor (T1: ceil(105 × 0.466) = 49).
- Statuses remap.
- The wheel is overridden with MULTIPLY (0, 11).
- `cleanse_on_enter = NONE`.
- Your P2 corruption and marks carry into the two-needle phase.
- Phase line: "The Handler burns the notice."

## 3. Sustain and intake
**Sustain:** one source, the P3 Redact BLOCK. It is enemy defense counted conservatively as sustain, and there is no heal.
- Two needles read Redact with probability 3/30 each, so the expected absorption is 2 × 0.1 × 8 = **1.6 per turn at T1**.
- That is 18 % of the reference 9 dpt, under the 30 % cap.
- At T2 it is 2.1 (19 % of 11). At T3 it is 2.7 (19 % of 14).

**Intake per turn** (T1 base, pre-block, uniform landings, tier-averaged; "ref" removes about 40 % through steering and selective Perfects):

| Phase | Raw | At reference | Target |
|---|---|---|---|
| P1 | 3.4 | 2.0 | 2–3 |
| P2 | 3.5 slices + Echo | 4.3 | 4–6 |
| P3 | 7.2 (3.6 per needle) | 5.0 | 5–7 |

All values are above 0. The total is about 35 HP at T1 over a reference fight, before cards. T2 is ×1.3 and T3 ×1.69.

## 4. HP by tier
R2 phase budget = `reference_dpt` × turns × needles landed − sustain × turns. P3 counts 2 needles.

| Tier | Budget at R2's 3.5 turns | Band (3 phases) | Budget at 3.0 turns (P1 / P2 / P3) | Sum | Authored HP (P1 / P2 / P3) |
|---|---|---|---|---|---|
| T1 (dpt 9) | 31.5 + 31.5 + (63 − 5.6) = 120 | 85–105 | 27 / 27 / (54 − 4.8 = 49.2) | 103.2 | **105** (28 / 28 / 49) |
| T2 (dpt 11) | 38.5 + 38.5 + (77 − 7.3) = 147 | 104–128 | 33 / 33 / (66 − 6.3 = 59.7) | 125.7 | **128** (34 / 34 / 60) |
| T3 (dpt 14) | 49 + 49 + (98 − 9.5) = 187 | 132–162 | 42 / 42 / (84 − 8.1 = 75.9) | 159.9 | **162** (43 / 43 / 76) |
| T4 | n/a, no mini-boss at T4 | | | | n/a |

**Deviation:** at R2's 3.5 turns per phase, a 2-needle P3 sums above the 3-phase band, which assumes about one needle per phase. I held the band and shortened the reference turns per phase to 3.0 to 3.1, the R1 floor.

**Floors:**

| Tier | Floor P1 → P2 | Floor P2 → P3 |
|---|---|---|
| T1 | 77 | 49 |
| T2 | 94 | 60 |
| T3 | 119 | 76 |

**Reference turns per phase:**
- T1: 28/9 = 3.1, 28/9 = 3.1, 49/16.4 = 3.0.
- T2: 34/11 = 3.1, 34/11 = 3.1, 60/19.9 = 3.0.
- T3: 43/14 = 3.1, 43/14 = 3.1, 76/25.3 = 3.0.

The total is about 9.2 turns at every tier. Phases run longer for slower players.

## 5. Enrage
**Default** (start 10, every 5, +25 % additive).
- The reference ends around turn 9.2, so the clock matters only to slower players, whose first step lands in P3.
- It stops a stalled P3 from becoming attrition, while the reference win stays clear of it.
- The turn-8 concept was dropped: it would tax the reference player and stack with Echo.

## 6. Buffs and counter Exploits
n/a. Mini-bosses carry no boss buffs. Exploits (Intel, Breach, Virus) do not change this fight.

## 7. Counterplay
- **P1:**
  - **Good player:** reads the preview chip, which shows its needle after the coupled nudge. They pick a rotation that keeps the Handler on Null or a Dose edge. They can decouple with a Spin or Flip card (neither triggers Shadow), or nudge the Handler's wheel directly (resistance 0) at 1 RAM per tick. They keep CORRUPTED slices off the pointer so nudges stay cheap.
  - **Weak player:** nudges for a Perfect without noticing the Handler's needle moved onto Directive, then pays 2× RAM on a corrupted slice to fix it.
- **P2:**
  - **Good player:** takes Good over Perfect on big slices (Echo is 60 % of the output) and Perfect on small slices or when the hook pays. They hold a Spin or nudge card for locked turns, and SANDBOX or BLOCK soaks the Echo or an Override Perfect. They also manage which slices stay corrupted, because P3 inherits them.
  - **Weak player:** chases Perfects every turn and takes Echo each time, tries to nudge on locked turns and is refused, and ignores marks.
- **P3:**
  - **Good player:** uses the pair table. The free nudge moves both needles together, so they steer to damage + safe or status-only rotations. They spend a Cleanse or Encrypt on the carried CORRUPTED, since a 2× RAM tax on a steering turn is the biggest cost. Kill-turns are those where both needles sit on damageable slices and Redact is not read.
  - **Weak player:** drifts into the 27 % double-damage rotations, burns RAM on repeated nudges and lets inherited CORRUPTED double the bill.

## 8. Systems needed
| Dependency | Why | Data-only fallback |
|---|---|---|
| N1 amount modes | FLAT × tier factor | Fixed amounts per tier |
| N2 tier tables | `hp_by_tier`, `enemy_damage_by_tier` | Three `.tres` files |
| N3 phases and parking | floors, status remap, `cleanse_on_enter` | Existing boss phases without parking |
| N4 enrage | class default | None; the Handler is slower without it |
| N6 enemy listeners | Echo on ON_PERFECT | Flat Echo 5 × factor |
| **NEW:** N6 extension, output-read rider | Echo = 60 % of the landed output | Flat Echo |
| **NEW:** N6 extension, coupled-wheel nudge response | Shadow, ignoring resistance | Resistance 2 in P1; no coupling |
| N7 nudge lock | P2 Override | None; drop the lock and keep Echo |
| N9 status rules | TIER_DOWN, CORRUPTED as a RAM debuff | Mark becomes the Citation PARASITE slice; Dose as today |
| N11 pointers on any tick | P3 needle at tick 11 | Needle at 10 |
| N12 slice sizes | all three layouts | 6 × 5-tick slices; the sub-tick puzzle is lost |
| N14 defense trio names | BLOCK on Redact | DEFRAG |
| N19 sim metrics | turns per phase, Echo fires, parked damage | None |

N8 (×N stacks) is not needed: Mark and Dose apply at ×1.

## 9. Delta vs today
**Today:** 170 HP, six 5-tick slices (Shim 12, Dose, Overflow 16, Citation, Sandbox 8, Null), resistance 2 for the whole fight, phases at 50 % (MULTIPLY 0/15) and 25 % (ORBIT 3).

**Changes:**
- HP 170 → 105 / 128 / 162.
- Thresholds 0.5 / 0.25 → 0.733 / 0.466, with three authored layouts.
- Resistance 2 permanent → 0 / 1 / 0.
- ORBIT is gone. MULTIPLY (0, 11) replaces (0, 15).
- Citation and Sandbox 8 are dropped. TIER_DOWN Mark, Redact BLOCK, Order and the Shadow and Echo listeners are new.

**Kept:** id `the_handler`, `is_elite` and `is_mini_boss` flags, `cycle_reward = 60`, Dose, Overflow, Shim and Null as templates.

**heat_effects:** none authored today; none added.

**New files:** `content/slices/hd_*.tres` and three phase resources.

## 10. Predicted sim check
No baseline row exists, so this is a hand estimate.

| Tier | Turns (reference) | Win % (step-0 skill) | Why |
|---|---|---|---|
| T1 | about 9.2 | about 97 % | about 35 HP intake over 9 turns against 45–60 HP plus card block |
| T2 | about 9.2 | about 93 % | ×1.3 damage |
| T3 | about 9.1 | about 88 % | ×1.69 damage; the 2-needle P3 and inherited Dose RAM tax bite |

- **T3 and the pass criteria:** T3 sits just under the 90 % criterion. The first knob is P3 Order 7 → 6, then Directive 14 → 12.
- **Bot ceiling:** a skill-1.0 bot at 16–35 dpt ends each phase in about 1.5–2 turns, so it finishes in about 5 turns. That is below the 6-turn class floor. Parking guarantees only one resolve per phase. R1's 3-turn floor is not enforced for burst play, and I would raise P3 HP rather than weaken the phases (Q1).
- **For scale:** today's 170 HP at 9 dpt is about 19 turns by division alone, ignoring its resistance 2 and extra pointers. That is arithmetic, not a measurement, but it points the same way as the Account Manager and Recall Unit baselines (20+ turns).

## 11. Open questions
Q: Should the 3-phase band be raised (about 120 / 147 / 187) so each phase runs the full 3.5 reference turns with a 2-needle P3? Today it fits only at 3.0 turns per phase.
Q: Echo as 60 % of the landed output needs the N6 output-read rider. Is that acceptable, or flat 5 × factor (data-only, never punishes a big Perfect)?
Q: Should Shadow also fire on SPIN effects? I excluded them so Spin and Flip cards stay the clean decouplers.
Q: With `cleanse_on_enter = NONE`, P3 inherits P2's marks and corruption. Is that right, or does a Cleanse card make that too soft?
Q: The Virus Exploit puts CORRUPTED on enemy slices, which does nothing now that it is a RAM debuff. Should a mini-boss ignore it, or should Virus get a different mini-boss effect?
