<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__city_manager; status ok; tokens in 16524 cache-write 0 cache-read 32007 out 5800; cost $0.049. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# city_manager: direct design

## 1. Identity & the one question

**Class:** Mini-boss, 3 phases, guards the final Rack at T1-T3. Corporation: Halcyon Civic. It appears at layer 7 of Halcyon netruns, so it is a pressure fight. Its status-stack and lock vocabulary should already have been taught by Citation normals (Patrol Unit, Parking Warden) in L1-2.

**Concept change.** I keep the three-phase shape from §3 (Ordinance / Curfew / Martial Law) but change two things:
- Curfew's nudge-lock no longer depends on "its needle starts on Curfew". That is a conditional the player can't read ahead of time. Instead, the lock is a slice on its wheel, so the player sees it coming and can steer around it.
- Hotfix heal stays only in P3 and is the single sustain source.

**Theme:** a bureaucrat who regulates you. P1 fines you (stacks), P2 restricts your actions (locks), P3 declares an emergency (two needles, pressure on both sides).

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Ordinance | "Where will you stand when the fines land?" Citations stack OUTPUT_DOWN on whichever of your slices sits under its needle. | Spread or dodge the stacks; Encrypt your best slice; burst while it is mostly blocking. |
| P2 Curfew | "What can you do when your wheel is locked?" Its Curfew slice locks your own-wheel nudges next turn. | Steer its needle off Curfew (cards still work), or plan the turn so the lock lands on a turn you don't need nudges. |
| P3 Martial Law | "Which of your two readers is the dangerous one?" Two uneven needles, heavier Citations, a Hotfix window. | Land the safe slice on the needle at 0 and let the other eat Null; kill during the Hotfix gap. |

## 2. Phase plan

Thresholds: 0.66 / 0.33 (R2 3-phase band). Each phase is about 33 % of HP. Parking (R3) applies at both thresholds. Statuses survive all transitions (R6). `cleanse_on_enter = NONE` everywhere: the stacks you have accumulated are the pressure in the next phase.

### P1 Ordinance (100 → 66 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Resistance | 2, passive (restores each turn). Absorbs 2 nudge ticks. |
| Hub rule | None |
| Statuses | OUTPUT_DOWN ×1 per Citation landing, stacking to ×3 on a slice (N8, N9) |
| Listeners | None |

| Slice | Ticks | Effect |
|---|---|---|
| Citation | 6 | 0 damage. OUTPUT_DOWN ×1 on your slice under the pointer. |
| Shim | 5 | 8 damage, FLAT |
| Defrag (BLOCK) | 5 | 10, FLAT |
| Citation | 6 | As above |
| Overflow | 4 | 14 damage, FLAT (size 4: no Perfect, so it never hits for a bonus) |
| Null | 4 | None |
| **Sum** | **30** | |

Sizes 6+5+5+6+4+4 = 30. Citation is 6-tick (WEAK-heavy edges), so about 33 % of landings are WEAK. A WEAK Citation still applies the status (Q11 default). Two of six slices are Citations, so a random respin lands one with ~40 % probability.

### P2 Curfew (66 → 33 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0. Pointer behavior: ORBIT 2 ticks per turn, with a trail shown (readable ahead). |
| Resistance | 2 |
| Hub rule | None |
| Statuses | OUTPUT_DOWN stacks persist from P1 |
| Listeners | None |

| Slice | Ticks | Effect |
|---|---|---|
| Curfew | 4 | Applies `nudge_locked` on your wheel for your next turn (N7). Cards still work; the free nudge is also refused. 0 damage. |
| Citation | 5 | OUTPUT_DOWN ×1 on the slice under the pointer |
| Shim | 5 | 9 damage |
| Defrag (BLOCK) | 6 | 12, FLAT |
| Curfew | 4 | As above |
| Overflow | 3 | 16 damage; size 3 so a Perfect is possible (a Perfect gives the normal 1.0×) |
| Null | 3 | None |
| **Sum** | **30** | |

Sizes 4+5+5+6+4+3+3 = 30. The orbit makes its landing predictable: the player sees the position two turns ahead and can plan to leave Curfew unlanded by nudging its wheel (but resistance 2 absorbs the first 2 ticks, so a paid nudge is needed; spin and Flip cards are blocked by resistance, so the dodge is a real RAM cost). Mind this, since the lock itself blocks nudges the turn after.

### P3 Martial Law (33 → 0 %)

| Field | Value |
|---|---|
| Needles | 2, ticks 0 / 13 (uneven, MULTIPLY, N11) |
| Resistance | 1 |
| Hub rule | Hotfix (the only sustain): "On the turn the Hotfix slice resolves, heal 3 % max HP, PERCENT" |
| Statuses | OUTPUT_DOWN stacks persist and keep growing |
| Listeners | None |

| Slice | Ticks | Effect |
|---|---|---|
| Citation | 5 | OUTPUT_DOWN ×2 on your slice |
| Shim | 4 | 10 damage |
| Hotfix | 4 | Heal 3 % max HP, PERCENT. No other defense in this phase. |
| Overflow | 4 | 18 damage |
| Citation | 5 | As above |
| Shim | 4 | 10 damage |
| Null | 4 | None |
| **Sum** | **30** | |

Sizes 5+4+4+4+5+4+4 = 30. The offset 13 means that when one needle sits on a Citation, the other tends to sit on a Shim or Null, because the gap spans roughly three slices. Layout order is built so that for any rotation, both needles land on dangerous slices only at ~3 of 30 rotations, i.e. rarely.

**Transitions:**
- **P1→P2:** `wheel_override`, pointer ORBIT. Phase line: "Curfew in effect." The player's OUTPUT_DOWN stacks are kept (remapped by the centre-tick rule on enemy wheel changes only). Damage parks at 66 %.
- **P2→P3:** `wheel_override` plus MULTIPLY (0, 13). Phase line: "Emergency session: martial law declared." Damage parks at 33 %.

## 3. Sustain and intake

**Sustain:** a single source, the P3 Hotfix: 3 % max HP per resolve. At T3 (HP 130, see §4) that is 3.9, say 4 per resolve. Hotfix is one of seven slices, with 2 needles, so it resolves on average about 0.57 times per turn. That gives ~2.2 HP per turn against a reference of 14 damage per turn at T3, which is 16 %. Under the 30 % cap. Worst case, both needles on Hotfix (rare): 7.8 HP, 56 % of one turn, and it can't repeat since the layout has one Hotfix slice, so only one needle can read it at a time. At most 1 Hotfix per turn: 3.9 = 28 % of 14. OK.

**Intake per turn** at the reference player (no SANDBOX, some BLOCK), T1 values:
- **P1:** two Citations (no damage). Shim 8, Overflow 14, other slices nothing. Expected damage per resolve: (8 + 14) / 6 slice-weighted by ticks (5 and 4 of 30) = 8×0.167 + 14×0.133 = 1.33 + 1.87 = **~3.2 per turn**, before the status effect (which is the real cost: −25 % per stack on your damage).
- **P2:** 9×0.167 + 16×0.1 = 1.5 + 1.6 = **~3.1 per turn**, plus the lock.
- **P3:** two needles, 10×(4/30)×2 + 18×(4/30) = 2.67 + 2.4 = **~5.1 per turn**.

All above 0. Total over a 10-turn fight is ~35-40 HP lost at T1 before block. Enrage raises this at turn 10.

## 4. HP by tier

Using the R2 formula `reference_dpt_by_tier × 3.5 × needles − sustain × 3.5`, with player needles = 1:

| Tier | Per-phase | 3 phases (budget) | Band | Authored |
|---|---|---|---|---|
| T1 | 9 × 3.5 = 31.5 | 94.5 | 85-105 | **95** |
| T2 | 11 × 3.5 = 38.5 | 115.5 | 104-128 | **116** |
| T3 | 14 × 3.5 = 49 | 147 | 132-162 | **145** (minus P3 sustain ~2.2 × 3.5 = 7.7, so authored 147 − 8 = **139**; I author 140) |
| T4 | n/a | n/a | n/a | not used (mini-boss does not appear at T4) |

Per-phase HP at T3 (140): P1 floor = ceil(140 × 0.66) = 93 → P1 spans 47 HP. P2 floor = ceil(140 × 0.33) = 47 → P2 spans 46 HP. P3 spans 47 HP, at 14 per turn = 3.4 turns plus Hotfix delay. About 3.5 turns each, matching the target.

Today's HP is 150 at T3-equivalent (the tier factor applies), well above these bands, which is the main number change.

## 5. Enrage

Mini-boss default: start 10, every 5, +25 % damage, additive (×1.25 at 10, ×1.5 at 15). I keep the default. Expected fight length is 3 phases × 3.5 = 10.5 turns, so enrage lands at the end of P3. That is deliberate: it punishes stalling in the Hotfix phase, which is where stalling happens. A weak player who reaches turn 10 meets ×1.25 on a P3 with 5 damage per turn, which is tight but survivable. It raises damage only, not the Citation stacks (the status amount is a buff and tier-independent).

## 6. Buffs and counter Exploits

Not applicable (mini-boss).

## 7. Counterplay

**Good player:**
- **P1:** identify the Citation slice, steer your wheel (own nudges are free the first time) so the Citation lands on a low-value or already-stacked slice. Put Encrypt on the best slice (it absorbs one status). Cleanse before P2. Burst in turns where the needle sits on Defrag only if you pierce; otherwise hit when it lands on Citation or Null (no block).
- **P2:** read the orbit trail and plan two turns ahead. A locked nudge turn is fine if you spent your RAM on cards. Keep a spin card in hand for the turn after a Curfew lands. Land Perfect on your Overflow before the lock.
- **P3:** use the uneven pair. Nudge your wheel so the slice at needle 0 is your high-value slice and needle 13 reads a Null or a Shim. Hit the turn after Hotfix resolves, because Hotfix is the only slice it will not use for damage.

**Weak player:**
- Ignores stacks, so by P3 three of their slices are ×3 stacked (−75 % output) and the fight stalls into enrage.
- Wastes the free nudge in P2 on a turn that Curfew then locks.
- Treats both P3 needles as one and takes Overflow plus Shim on the same resolve.

## 8. Systems needed

| N# | Use | Data-only fallback |
|---|---|---|
| N3 | Parking, phases at 0.66 / 0.33 | None: core to the design |
| N8 | ×N OUTPUT_DOWN stacks | Fallback: replace stacks with the existing PARASITE status (a 2-stack-equivalent halving), losing the escalation. Weak. |
| N9 | OUTPUT_DOWN status rule | Fallback: PARASITE (existing) |
| N7 | `nudge_locked` from the Curfew slice | None. Fallback: swap Curfew for a Citation. P2 then asks the same question as P1. |
| N11 | Needles at 0 / 13 (uneven) | Fallback: 0 / 15 (even) as today. Loses the "one safe, one dangerous" read. |
| N12 | Slice sizes 3-6 | Fallback: 5-tick slices (6 slices fits; P2/P3 need 7, so cut one Null) |
| N4 | Enrage | Fallback: none needed to ship; default is data in `campaign_config` |
| N1 | PERCENT Hotfix | Fallback: FLAT 4 × tier factor (works, slightly less clean) |
| N2 | `hp_by_tier` | Fallback: hand-set HP per tier in code, which R2 forbids long-term |

## 9. Delta vs today

- **HP:** 150 (flat) → 95 / 116 / 140 by tier.
- **Phases:** today 2 phases at 0.5 / 0.25 (MULTIPLY then ORBIT). New: 3 phases at 0.66 / 0.33. The player-facing pointer story is reordered: ORBIT moves to P2, MULTIPLY to P3, and P3's second needle moves from 15 to 13.
- **Wheel:** today one wheel, six 5-tick slices (Shim 10, Defrag 8, Overflow 15, Citation, Hotfix 6, Null), resistance 2, with Hotfix present in every phase. New: three distinct layouts. Hotfix leaves P1-P2 (so sustain is one source and only in P3). Citation is doubled in P1, since it is the thing to learn.
- **Kept:** Citation slice, passive resistance 2 in P1-P2 (1 in P3), `is_mini_boss`, `is_elite` flag (R1 says elites have exactly 2 phases; I would drop `is_elite` for this enemy), `cycle_reward = 60`.
- **New:** Curfew slice, uneven needles, OUTPUT_DOWN ×N (replacing PARASITE), enrage default.
- **heat_effects:** none in the current file. Decision: none to add. Heat's modifiers already apply (+1 resistance at Heat 50) and stacking it onto a phase-designed fight muddies the numbers.

## 10. Predicted sim check

No baseline row exists for Halcyon; this is estimated from the wheel and the R2 budget, not measured.

| Tier | Expected turns | Win % | Why |
|---|---|---|---|
| T1 | 9-11 | ~92 % | 95 HP at 9 per turn ≈ 10.5; intake ~3-5 per turn is well under a 60 HP operative |
| T2 | 10-11 | ~90 % | Same shape; intake up by ×1.3 |
| T3 | 10-12 | ~85 % | 140 HP at 14 per turn = 10; stacks and enrage start to bite. Under the 90 % T3 pass criterion, so expect one tuning round (likely trim Overflow 18 → 15 in P3). |
| T4 | n/a | n/a | not used |

Compared with Account Manager (20.7 turns at T3, 20 % win at T4) the intent is roughly half the length. The main risk is that stacks slow the reference player more than the budget accounts for. If so, cap OUTPUT_DOWN at ×2.

## 11. Open questions

Q: Does OUTPUT_DOWN ×3 (−75 %) stack additively or multiplicatively? I assumed additive (−25 % per stack), with a floor of −75 %.
Q: Does the Curfew lock also refuse the free nudge, or only paid ones? I chose both (the free nudge is refused too); a softer lock would make it a tax rather than a puzzle.
Q: Should P3 remain on 1 resistance, or should Flip and Respin be unblocked (0)? I kept 1 to preserve nudge costs; 0 would make Flip an easy answer to the uneven needles.
Q: Is dropping `is_elite` from a mini-boss acceptable for the reward and route code that currently reads it?
Q: Should Curfew's lock extend to cards in a later tier, or is the "cards always work" line a hard rule for the corporation?
