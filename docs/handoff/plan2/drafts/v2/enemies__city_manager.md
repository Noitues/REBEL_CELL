<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__city_manager; status ok; tokens in 9072 cache-write 0 cache-read 32585 out 23700; cost $0.131. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Critic 1 (BLOCKER, sustain subtracted twice, even HP split):** Kept the shared sustain, but it is now subtracted once, from P3 only, at every tier.
  - Hotfix expected rate: one 4-tick slice, two needles that can never share it (13 apart), so 8 of 30 rotations = 0.267 resolves/turn. v1's "0.57" was wrong and is removed.
  - Heal is weighted by its WEAK edges (size 4 → 0.75).
  - Authored HP: T1 90, T2 111, T3 141 (§4). Per-phase spans are shown and match each phase's budget.
- **Critic 2 (BLOCKER, T1/T2 ignore sustain, T3 includes it):** One formula for all three tiers: budget = Σ(dpt × 3.5) − P3 expected heal × 3.5. All three tiers are now computed the same way.
  - The critic's suggested 87 / 108 came from a ~2.2 HP/turn heal that rested on the wrong 0.57 rate. With the corrected rate (heal ≈ 0.45 / 0.55 / 0.71 per turn at T1 / T2 / T3) the numbers are 90 / 111 / 141. This is an arithmetic correction, not a dispute of the fix.
- **Critic 3 (BLOCKER, needle-pair geometry false):** I enumerated all 30 rotations of the P3 layout, and the "~3 of 30" claim is gone.
  - Truth: 16/30 (53 %) put a Null or Hotfix under a needle. 14/30 (47 %) put no safe slice under either.
  - Only 8/30 put two actually damaging reads on you.
  - I kept the uneven 0 / 13 needles (R10 makes them the main tool), but reordered the layout so safe slices sit 13 ticks away from each other's partners (Hotfix at 0–3, Null at 9–12).
  - The critic's own reorder would have put Overflow under needle 13 whenever Citation sat under 0, so I did not adopt it.
  - Counterplay is rewritten as "pick the pair" (§7).
- **Critic 4 (MAJOR, status text and R6 remap):**
  - The remap sentence is removed. Statuses live on the player's wheel, whose layout never changes, and the enemy wheel carries none. `cleanse_on_enter = NONE`.
  - Citation is now stated as a per-landing application: ×1 in P1/P2, ×2 in P3, with `max_stacks = 3` per slice.
  - Both P3 needles resolve against your single pointer, so two Citations stack on the same slice, capped at ×3.
- **Critic 5 (MAJOR, resistance wording):** Flip and Respin are blocked while resistance > 0. Spin loses its first R ticks. The paid-nudge cost to move the enemy wheel is computed.
  - P2 is rebuilt around "the lock arrives next turn, so spend nudges now" rather than "dodge the Curfew".
  - Dodging is possible but expensive, and the draft says so.
- **Critic 6 (MAJOR, intake maths):** Rebuilt.
  - Enemy landings use the tier weights (WEAK = 0.5×; size 4 → 0.75, size 5 → 0.8, size 6 → 0.667).
  - Enemy BLOCK does not count as intake.
  - The "Perfect is possible on size 3" aside is deleted.
  - P3 sums two needles by linearity.
  - Damage values are retuned to 7/12, 8/14 and 6/12 (Shim/Overflow) so the unsteered total is ~40 HP at T1.
- **Critic 7 (MAJOR, P1 Defrag is attrition and self-contradictory):** P1 Defrag is removed. P1's question is now "which of your slices takes the fine". P2 keeps one 8-FLAT Defrag, because with the orbit trail "which turn do you spend your burst" is a real timing question.
- **Critic 8 (NIT, `is_elite`):** Decided in the data (§9): drop `is_elite`, keep `is_mini_boss`. Q4 is removed.
- **Critic 9 (NIT, unsupported "5 damage per turn"):** Removed. Enrage now quotes computed numbers.
- **Critic Qs:** OUTPUT_DOWN is additive (−25 % per stack), capped at ×3 per slice, and clears at combat end (GDD 2.9 "until cleansed or combat ends"). The P1 Defrag is removed.
- **Triage rows:** all three are covered by the items above.
- **Kept, because the critic marked it strong:** the visible Curfew slice, the stacks → lock → two-needles escalation, and the single sustain source in the final phase.
- **Ruling conflict:** none. The R1–R13 rules and the designer rulings are followed.

---

# city_manager: direct design

## 1. Identity & the one question

**Class:** mini-boss, 3 phases. It guards the final Rack of Halcyon netruns at T1–T3, so it appears at layer 7 as a pressure fight. Its vocabulary (Citation fines, stacks) is taught by Citation normals in L1–2 (Parking Warden, Patrol Unit).

**Concept change vs CONTENT_DESIGN_V2 §3.** I keep the shape Ordinance → Curfew → Martial Law, with two changes:
- Curfew's lock is a slice on its wheel (readable, steerable) rather than "when its needle starts on Curfew".
- Hotfix heal exists only in P3 and is the single sustain source.

**Theme:** a bureaucrat who regulates you. P1 fines you (stacks), P2 restricts your actions (locks), P3 declares an emergency (two needles).

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Ordinance | "Which of your slices takes the fine?" A Citation puts OUTPUT_DOWN on the slice under your pointer: the one you just fired. | Present a slice you can afford to tax, spread fines across your slices, Encrypt your best slice. Hit hard on its Null and Shim turns. |
| P2 Curfew | "What do you do on a turn you can't nudge?" A Curfew landing locks your own-wheel nudges next turn. The orbit trail shows it coming. | Spend your nudges on the turn before the lock, carry a spin card for the locked turn, and time your burst around its Defrag. |
| P3 Martial Law | "Which pair of slices do you let it read?" Two uneven needles (0 / 13), Citations ×2, one Hotfix window. | Nudge your wheel so a Null or the Hotfix sits under one needle, and burst on the turns it is not healing. |

## 2. Phase plan

Thresholds 0.66 / 0.33. Parking (R3) at both. `cleanse_on_enter = NONE` everywhere: your accumulated stacks are the next phase's pressure. The enemy wheel never carries statuses, and your wheel's layout never changes, so R6 has nothing to remap.

**Status rule (R8/N9):** OUTPUT_DOWN = −25 % output per stack, additive, `max_stacks = 3` per slice (−75 %), lasting until cleansed or combat end. ENCRYPTED absorbs one application.

**Landing weights (R11, applies to enemy slices too):** size 4 = 0.75 average output, size 5 = 0.8, size 6 = 0.667 (WEAK = 0.5×). Damage values below are base T1 FLAT values × the tier damage factor [1.0, 1.3, 1.69].

### P1 Ordinance (100 → 66 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED. Wheel respins at turn start as normal. |
| Resistance | 2 (passive, restores each player turn) |
| Hub rule | None |
| Statuses / listeners | OUTPUT_DOWN ×1 per Citation landing. No listeners. |

| Slice | Ticks | Range | Effect |
|---|---|---|---|
| Citation | 6 | 0–5 | 0 damage. OUTPUT_DOWN ×1 on your slice under the pointer (still applies on a WEAK landing). |
| Shim | 5 | 6–10 | 7 damage, FLAT |
| Citation | 6 | 11–16 | as above |
| Overflow | 4 | 17–20 | 12 damage, FLAT |
| Null | 4 | 21–24 | nothing |
| Shim | 5 | 25–29 | 7 damage, FLAT |
| **Sum** | **30** | | 6+5+6+4+4+5 = 30 |

There is no enemy block and no heal here. Citation is 12/30 = 40 % of landings and Null 13 %, so the phase is about reading the intent and choosing what you present.

### P2 Curfew (66 → 33 %)

| Field | Value |
|---|---|
| Needles | 1, ORBIT +2 ticks per turn, trail shown for the coming turns. |
| Resistance | 2 |
| Hub rule | None |
| Statuses / listeners | P1 stacks persist. Citation ×1. Curfew applies `nudge_locked` (N7). No listeners. |

| Slice | Ticks | Range | Effect |
|---|---|---|---|
| Curfew | 3 | 0–2 | 0 damage. Your own-wheel nudges (free and paid) are refused next turn. Cards, spin and Freeze still work. |
| Citation | 5 | 3–7 | OUTPUT_DOWN ×1 on your slice under the pointer |
| Shim | 5 | 8–12 | 8 damage, FLAT |
| Defrag (BLOCK) | 5 | 13–17 | 8, FLAT. It absorbs your damage in the same resolve. |
| Curfew | 3 | 18–20 | as above |
| Overflow | 4 | 21–24 | 14 damage, FLAT |
| Null | 5 | 25–29 | nothing |
| **Sum** | **30** | | 3+5+5+5+3+4+5 = 30 |

**The orbit combo:** the needle drifts 2 ticks per turn, so across a phase it reads 2–3 neighbouring slices in order. The second Curfew sits directly before Overflow. You are locked on the turn the big hit arrives, and your start-of-turn respin is random, so only cards can fix your landing. You see this two turns ahead and spend nudges while you still have them.

**Moving its wheel (the dodge):** resistance 2 absorbs the first 2 ticks per turn. Shifting its wheel by 1 tick costs 3 nudges (1 free + 2 RAM). Shifting by 2 costs 1 free + 3 RAM. Flip and Respin are blocked. A spin card works but loses its first 2 ticks. The dodge is possible but expensive, which is intended.

### P3 Martial Law (33 → 0 %)

| Field | Value |
|---|---|
| Needles | 2, ticks 0 / 13 (uneven, MULTIPLY, N11), FIXED |
| Resistance | 1 |
| Hub rule | **Hotfix** (the only sustain): the Hotfix slice heals 2.5 % max HP, PERCENT, on resolve. No other defense in this phase. |
| Statuses / listeners | OUTPUT_DOWN ×2 per Citation landing, capped at ×3 per slice. No listeners. |

| Slice | Ticks | Range | Effect |
|---|---|---|---|
| Hotfix | 4 | 0–3 | Heal 2.5 % max HP (PERCENT, never re-scaled by tier) |
| Citation | 5 | 4–8 | OUTPUT_DOWN ×2 on your slice |
| Null | 4 | 9–12 | nothing |
| Shim | 4 | 13–16 | 6 damage, FLAT |
| Overflow | 4 | 17–20 | 12 damage, FLAT |
| Citation | 5 | 21–25 | OUTPUT_DOWN ×2 |
| Shim | 4 | 26–29 | 6 damage, FLAT |
| **Sum** | **30** | | 4+5+4+4+4+5+4 = 30 |

**All 30 rotations (needle A at t, needle B at t+13):**

| Rotation t | Reads | Count |
|---|---|---|
| 0–3 | Hotfix + Shim | 4 |
| 4–7 | Citation + Overflow | 4 |
| 8, 21–25 | Citation + Citation (both land on your one pointer slice: ×2+×2, capped ×3) | 6 |
| 9–12 | Null + Citation | 4 |
| 13–16 | Shim + Shim | 4 |
| 17–20 | Overflow + Hotfix | 4 |
| 26–29 | Shim + Null | 4 |

- A safe slice (Null or Hotfix) is under one needle on 16/30 rotations (53 %).
- Neither needle is safe on 14/30 (47 %), but double damage happens on only 8/30: Shim+Shim and Citation+Overflow.
- Both Citations stack onto the same slice of yours, so the damage is concentrated rather than spread.

**Transitions**
- **P1→P2:** `wheel_override`; pointer behavior FIXED → ORBIT. Line: "Curfew in effect." Damage parks at 66 %.
- **P2→P3:** `wheel_override`; MULTIPLY (0, 13); hub_override (Hotfix); resistance 2 → 1. Line: "Emergency session." Damage parks at 33 %. No cleanse in either transition.

## 3. Sustain and intake

**Sustain: one source, the P3 Hotfix.**
- One 4-tick slice. The needles are 13 apart, so both can never read it. At most 1 resolve per turn.
- Heal per resolve = 2.5 % of max HP:

| Tier | Max HP | Heal | Per-turn damage | Heal as share of damage |
|---|---|---|---|---|
| T1 | 90 | 2.25 | 9 | 25 % |
| T2 | 111 | 2.8 | 11 | 25 % |
| T3 | 141 | 3.5 | 14 | 25 % |

  Worst case ≤ 25 %, under the 30 % cap.
- Rotation chance: 8/30 = 0.267 resolves per turn. WEAK edges reduce the heal (size-4 weight 0.75).
- **Expected heal:** 0.267 × 0.75 × heal per resolve:

| Tier | Expected heal per turn |
|---|---|
| T1 | 0.45 |
| T2 | 0.55 |
| T3 | 0.71 |

  That is about 5 % of reference damage at every tier.

**Intake per turn** (T1 values, unsteered random landing, before your BLOCK):

| Phase | Shim contribution | Overflow contribution | Total |
|---|---|---|---|
| P1 | 7 × 0.8 × 10/30 = 1.87 | 12 × 0.75 × 4/30 = 1.2 | **3.1** |
| P2 (Defrag and Curfew are not damage) | 8 × 0.8 × 10/30 = 2.13 | 14 × 0.75 × 4/30 = 1.4 | **3.5** |
| P3, per needle | 6 × 0.75 × 8/30 = 1.2 | 12 × 0.75 × 4/30 = 1.2 | 2.4; **4.8** for 2 needles |

- The real cost is on top of that: stacks (up to −75 % on a slice) and the lock.
- Unsteered, 3.5 turns per phase costs ≈ (3.1 + 3.5 + 4.8) × 3.5 ≈ 40 HP at T1. A steering player with BLOCK takes about 25–30. At T2/T3 multiply by 1.3 / 1.69.

## 4. HP by tier

Budget per phase = `reference_dpt_by_tier` × 3.5. P3 minus expected heal × 3.5. One formula, one subtraction.

| Tier | P1 | P2 | P3 (minus heal × 3.5) | Total budget | Band | Authored |
|---|---|---|---|---|---|---|
| T1 (dpt 9) | 31.5 | 31.5 | 31.5 − 0.45 × 3.5 = 29.9 | 92.9 | 85–105 | **90** |
| T2 (dpt 11) | 38.5 | 38.5 | 38.5 − 0.55 × 3.5 = 36.6 | 113.6 | 104–128 | **111** |
| T3 (dpt 14) | 49 | 49 | 49 − 0.71 × 3.5 = 46.5 | 144.5 | 132–162 | **141** |
| T4 | not used | | | | | |

**Parked spans** (floor = ceil(max × next threshold)):
- **T1, 90:** floors 60 and 30 → spans 30 / 30 / 30.
- **T2, 111:** floors 74 and 37 → spans 37 / 37 / 37.
- **T3, 141:** floors 94 and 47 → spans 47 / 47 / 47.
- Authored HP is 2–3 % under budget so the fight leans fast. P3's span matches its sustain-reduced budget (30 vs 29.9, 37 vs 36.6, 47 vs 46.5).

At 3.5 turns per phase that is about 10.5 turns, inside the 6–12 target.

## 5. Enrage

Mini-boss default: start turn 10, every 5, +25 % damage, additive (×1.25, then ×1.5). I keep it.
- The expected fight is ~10.5 turns, so the first step lands at the end of P3, exactly when stalling around Hotfix would otherwise be rewarded.
- At T1 it takes P3 intake from 4.8 to 6.0 per turn. Stack amounts and the lock are not scaled (buffs are tier-independent).

## 6. Buffs and counter Exploits

Not applicable (mini-boss).

## 7. Counterplay

**Good player**
- **P1:** read the Citation intent each turn. You choose which slice goes under your pointer and takes the fine. Give it a slice you rarely use, or one already at ×2 rather than a fresh Overflow. Encrypt your best slice (absorbs one fine). Spread fines across your three Shims. Cleanse before the P2 floor. Hit hard on Null/Shim turns. There is no block to time.
- **P2:** read the orbit trail. Before the lock, put your setup nudges into the turn you can still nudge. On the locked turn, rely on a spin or Freeze card. Fire your burst when the trail shows Defrag is not coming, and expect the second Curfew to precede the Overflow.
- **P3:** one nudge moves both needles, so you choose a pair. Aim for Null+Citation, Shim+Null, or Hotfix+Shim, and avoid Shim+Shim and Citation+Overflow. If both Citations will land, put a slice you already stacked or don't need under your pointer, because the second fine wastes against the ×3 cap. Burst on turns the Hotfix pair is not up.

**Weak player**
- Fires the same strong slice every turn into Citations, so by P3 it sits at ×3 (−75 %) and the fight stalls into enrage.
- Burns the free nudge on the turn before a Curfew, then lands random on the locked turn.
- Treats P3's two needles as one and takes Shim+Shim or Citation+Overflow repeatedly.

## 8. Systems needed

| N# | Use | Data-only fallback |
|---|---|---|
| N3 | Phases and parking at 0.66 / 0.33 | None, core |
| N8 | ×N OUTPUT_DOWN stacks (cap 3) | Existing PARASITE (halving). Loses escalation; weak. |
| N9 | OUTPUT_DOWN status rule | PARASITE |
| N7 | `nudge_locked` from Curfew | None. A Curfew-for-Citation swap makes P2 repeat P1. |
| N11 | Needles at 0 / 13 | 0 / 15 even: the pair geometry changes, so re-enumerate the layout. |
| N12 | Slice sizes 3–6, sub-tick map | 5-tick slices: 6 slices only, so P2/P3 lose 1 slice each. Not recommended. |
| N4 | Enrage | Default data in `campaign_config` |
| N1 | PERCENT Hotfix | FLAT 3.5 × tier factor (a small drift) |
| N2 | `hp_by_tier` | Hand-set HP in the `.tres` |
| existing | ORBIT (GDD 2.11), resistance, Hotfix slice | none needed |

## 9. Delta vs today

- **HP:** today flat ~150 → 90 / 111 / 141 (T1 / T2 / T3). `hp_by_tier` authored.
- **Phases:** 2 phases at 0.5 / 0.25 (MULTIPLY then ORBIT) → 3 phases at 0.66 / 0.33. ORBIT moves to P2, MULTIPLY to P3, and the P3 offset 15 → 13.
- **Wheel:** one 6×5-tick layout (Shim 10, Defrag 8, Overflow 15, Citation, Hotfix 6, Null) with Hotfix in every phase → three authored layouts. Hotfix only in P3 (PERCENT), Defrag only in P2, and P1 has none.
- **Kept:** the Citation slice, resistance 2 in P1–P2, `is_mini_boss`, `cycle_reward = 60`.
- **Dropped:** `is_elite`. A mini-boss with R1's elite phase count is a validation conflict, so the flag goes. The reward/route code must read `is_mini_boss`; check that on the build pass.
- **New:** Curfew, the uneven needles, OUTPUT_DOWN (PARASITE → OUTPUT_DOWN ×2 per R8), enrage.
- **heat_effects:** none today, none added. The Heat bands (+1 resistance at Heat 50) already modify the fight, and stacking more on a phase-tuned budget would muddy the sim.

## 10. Predicted sim check

No Halcyon baseline exists, so these are estimates from the wheel and the R2 budget.

| Tier | Expected turns | Win % | Why |
|---|---|---|---|
| T1 | 10–11 | ~93 % | 90 HP at 9 dpt ≈ 10 turns plus stack slowdown; unsteered intake ≈ 40 vs a 45–60 HP operative |
| T2 | 10–11 | ~90 % | Same shape, intake ×1.3 |
| T3 | 10–12 | ~86 % | 141 HP at 14 dpt = 10; intake ×1.69 and enrage near the end of P3. Likely one tuning round: P3 Overflow 12 → 10. |
| T4 | n/a | n/a | not used |

Against Account Manager (20.7 turns at T3, 20 % win at T4) this is roughly half the length. The risk is that stacks slow the reference player more than the 3.5-turn budget assumes. If so, cap OUTPUT_DOWN at ×2.

## 11. Open questions

Q: Does an ORBIT wheel skip the start-of-turn respin? P2's readable trail assumes it does. If it respins, the trail is meaningless and P2 needs another readability device.
Q: P3's two Citations land on your one pointer slice and cap at ×3. Is that the intended "concentrated fine", or should the second Citation spill to the next slice?
Q: Does the Curfew lock refuse the free nudge too? I chose yes, since a softer lock turns the puzzle into a tax.
Q: Should resistance stay 1 in P3, or drop to 0 so Flip and Respin work against the uneven pair?
Q: Is OUTPUT_DOWN ×3 (−75 %) too severe for a mini-boss fight against a slice that is the player's only damage source (Breaker's Overflow)?
