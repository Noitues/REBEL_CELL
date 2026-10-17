<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__recall_unit; status ok; tokens in 18743 cache-write 0 cache-read 32007 out 4703; cost $0.045. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# recall_unit: direct design

## 1. Identity & the one question
- **Class:** Elite, Solace, 2 phases, one threshold at 50 %. It appears at L3-6 of T1-T3 netruns (the final stretch before the Rack), never L1-2. Its pointer already teaches "track a moving needle", so it sits just above the teaching tier.
- **Theme:** a recall is a notice, then a pursuit. Phase 1 is the Notice, a slow orbiting needle you can plan against. Phase 2 is the Retrieval, where the unit stops orbiting and *locks on* to your most dangerous slice.
- **P1 Notice asks:** "Can you read a moving needle and kill it while it is predictable?" The orbit is deterministic (+2 ticks per turn) and shown by a trail. A player who plans two turns ahead lands hits when the needle sits on Null or on the weak edge of an attack. A player who ignores the orbit gets hit by the Overflow.
- **P2 Retrieval asks:** "Can you survive a needle that follows you, and pay for the Perfects you have been relying on?" Orbit stops. In its place, a **Recall Tag** listener (N6) hits you every time you land a **Perfect**. The tag is a pre-announced cost shown in the preview. Safe play (Good landings) is slower. Greedy play is faster and costs HP.
- **Shorter fight:** in P1, a nudge that parks the needle on Null or an unguarded slice before the orbit carries it away. In P2, a Good landing on the high-damage slice. Skip Perfect unless the Tag is worth paying.
- **Distinct from siblings:** Claims Adjuster is a straight burst elite. Account Manager runs on RAM economy and fixed bodyguards. The Recall Unit is about *tracking* (orbit) and a *Perfect tax*. The Account Manager's Clawback also taxes Perfects, so mine differs: the Tag is small, flat, always shown, and the unit also loses its defence in P2.

## 2. Phase plan

### P1 "Notice" (100 → 50 % HP)
| Field | Value |
|---|---|
| Needles | 1 at tick 0, **ORBIT +2 ticks/turn** (trail shows the next 2 positions) |
| Resistance | passive 1 (kept; restores each turn) |
| Hub rule | none |
| Statuses/parasites | none |
| Listeners | none |

Layout (ticks, sum 30), clockwise from tick 0:

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Notice (SHIM) | 5 | 9 dmg FLAT |
| 2 | Notice (SHIM) | 5 | 9 dmg FLAT |
| 3 | Recall Plating (DEFRAG → BLOCK) | 5 | 8 BLOCK FLAT |
| 4 | Retrieval (OVERFLOW) | 4 | 15 dmg FLAT (W G G W: no Perfect, so it can never be a "Perfect it" slice and a nudge on the edge does little) |
| 5 | Quarantine (SANDBOX → SHIELD) | 5 | 5 SHIELD FLAT |
| 6 | Null | 6 | none (W W G G W W, a wide safe landing) |

Sum: 5+5+5+4+5+6 = 30.

The orbit moves 2 ticks per turn, so the needle crosses a slice in about 2.5 turns. A Retrieval slice is only 4 ticks wide, so it is quick to pass. The Null slice is the biggest, so the needle spends the most time on it.

### Transition P1 → P2 (at ≤ 50 % HP)
- Damage parks at ceil(0.5 × max) (R3). The excess is lost, and the phase changes at the end of that resolve.
- `wheel_override`: new layout. `pointer_orbit_per_turn` goes to 0.
- Statuses survive with the centre-tick remap (R6). `cleanse_on_enter` = NONE: whatever you stacked on it stays.
- Resistance is reduced from 1 to 0 as part of the override (it "stops hiding").
- The phase line plays and the new layout is revealed.

### P2 "Retrieval" (50 → 0 %)
| Field | Value |
|---|---|
| Needles | 1 at tick 0, **FIXED** (no orbit). It re-aims instead: see the Lock rule below. |
| Resistance | 0 |
| Hub rule | **Lock-On:** at the start of each turn after the respin, if the needle reads a slice that is not Null, no change. If it reads Null, it is nudged +2 ticks toward the next attack slice (deterministic, telegraphed on the preview). It still only moves once per turn. |
| Statuses | none |
| Listeners (N6) | **Recall Tag:** ON_PERFECT (player landing on your own wheel): deal 4 FLAT damage to you. Preview shows "TAG −4". Also resolves before the end-turn pass, so it is plain damage with no randomness. |

Layout (sum 30):

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Recall Order (SHIM) | 5 | 9 FLAT |
| 2 | Recall Order (SHIM) | 5 | 9 FLAT |
| 3 | Recall Order (SHIM) | 4 | 9 FLAT (no Perfect) |
| 4 | Final Notice (OVERFLOW) | 5 | 15 FLAT |
| 5 | Null | 5 | none |
| 6 | Null | 6 | none |

Sum: 5+5+4+5+5+6 = 30. There is no block and no shield in P2: the unit trades its defence for the Tag.

Lock-On is an alternative to the old orbit and is cheap: it only nudges the needle on Null. A data-only version is described in section 8.

## 3. Sustain and intake
- **Sustain: none.** The Recall Unit has no heal. Its defence is BLOCK 8 and SHIELD 5 in P1 only. This stays under the 30 % cap (0 % of 11 dpt).
- **Reference player:** `reference_dpt_by_tier` = [9, 11, 14, 18].
- **Intake at reference play** (enemy damage × tier factor [1.0, 1.3, 1.69, 2.2]; 6 slices, average over the orbit):
  - P1: slices that attack (SHIM 9, SHIM 9, OVERFLOW 15) cover 14 of 30 ticks, weighted ≈ (5·9 + 5·9 + 4·15)/30 = 5.0 expected damage per turn at T1. A reference player who steers 1 nudge per turn gets ≈ 3.
  - P2: attacks cover 19 of 30 ticks, weighted (5·9 + 5·9 + 4·9 + 5·15)/30 = 6.7 per turn. Lock-On pushes off Null so assume ≈ 6. Plus the Tag, 4 per Perfect (about 1 Perfect per turn at the reference play, so +4 if the player chooses it).
  - **Target intake:** P1 2-4 per turn, P2 5-8 per turn (+ Tag). Well above 0. Against the baseline 0.97 per turn taken, this is about 4× more threat. T3-T4 are tempered by the tier factors: ×1.69 and ×2.2 on every flat amount.

## 4. HP by tier
R2 band: Elite (2 phases) T1 56-72, T2 68-88, T3 88-112, T4 112-144. Budget per phase = `reference_dpt` × 3.5 turns × 1 needle − sustain (0). Both phases are single-needle, so both budgets are equal.

| Tier | dpt | Per-phase budget | Total | In band | `hp_by_tier` |
|---|---|---|---|---|---|
| T1 | 9 | 9 × 3.5 = 31.5 | 63 | 56-72 ✓ | **64** |
| T2 | 11 | 38.5 | 77 | 68-88 ✓ | **78** |
| T3 | 14 | 49 | 98 | 88-112 ✓ | **98** |
| T4 | 18 | 63 | 126 | 112-144 ✓ | **126** |

- Threshold 0.5. P1 and P2 are each ≈ half of the above.
- Today's HP of 106 is replaced by the tier table (so T1 falls from 106 to 64).
- The orbit makes P1 fairly slow to hit cleanly, so P1 effectively runs ~4 turns. The tier set it up so that a typical player (below reference) needs 5 to 6.

## 5. Enrage
**Elite default** (start turn 8, then every 5, +25 % damage per step, additive). It is a safety net only. At 6-8 turns the expected fight ends before or on the first step. The Tag is a flat amount and is also raised by the step.

## 6. Buffs and counter Exploits
Not a boss. Not applicable.

## 7. Counterplay
- **P1:** read the trail. The Retrieval slice is only 4 ticks wide with no Perfect, so use the free nudge to park the needle on Null (the widest slice) at the right moment. Strike hard on a turn the needle sits on Null or Quarantine. The resistance 1 absorbs one nudge tick, so budget a 2-tick nudge, or use a spin card. Do not spend turns chipping the Plating: its BLOCK is small and expires.
- **P2:** decide per turn whether a Perfect is worth 4 damage. The Tag is flat, so against big hits (reference ×4 on a Perfect) it is cheap, and against small hits it is a poor trade. SHIELD absorbs the Tag if the player holds one. Keep the needle on Null (Lock-On nudges it +2 toward the attack, so a 2-tick counter-nudge holds it).
- **Weak players get wrong:** they chase Perfects in P2 and bleed 4 per turn to the Tag; they ignore the orbit and walk into the Retrieval; they burn nudges on resistance in P1.

## 8. Systems needed
| System | Use | Fallback |
|---|---|---|
| N2 `hp_by_tier`, N1 tier factors | HP table and scaled flat amounts | None; required by R2 |
| N3 phases on elites, threshold parking | the 50 % threshold | required |
| N4 Enrage | default | required |
| N11 | none (needle at tick 0) | n/a |
| N12 `size_ticks` | 4- and 6-tick slices | Use 5-tick slices only: Retrieval then has a Perfect, which weakens the "narrow and never Perfect" idea but still works |
| N6 listener ON_PERFECT | Recall Tag | Fallback: drop the Tag and give P2 a plain hub rule "damage +25 %"; loses the Perfect question |
| N14 | SHIELD/BLOCK names | cosmetic |
| Lock-On hub rule | NEW: `lock_on_nudge` (a hub rule: nudge the needle toward the next attacking slice when it reads Null) | Data-only fallback: P2 keeps `pointer_orbit_per_turn = 2` and the layout removes Null slice #5, leaving one Null; cheaper, loses the "tracks you" feel |

## 9. Delta vs today
- **Kept:** the orbit (P1), the slice set (Shim 9 ×2, Defrag 8, Overflow 15, Sandbox 5, Null), resistance 1, `cycle_reward` 35, the elite flag.
- **Changed:** HP 106 → tier table (64/78/98/126); the orbit stops in P2; a second layout with no defence; the Tag listener; slice sizes vary (4 and 6).
- **New:** one threshold at 0.5, parked damage, Lock-On.
- **heat_effects:** the current file shows none, so there is nothing to keep. Decision: **do not add any**; the Tag and threshold carry the identity, and an elite already gives +1 Heat from its node.

## 10. Predicted sim check
| Tier | Turns (mean) | Win % | Baseline |
|---|---|---|---|
| T1 | 6-7 | ~100 | 6.5, 100 % |
| T2 | 6-8 | ~98 | 11.2, 100 % |
| T3 | 7-9 | ~92 | 20.2, 100 % |
| T4 | 8-10 | ~75 | 36.0, 65 % |

Why: HP is now tuned to the reference damage, not to a tier multiplier, so T2-T4 fights fall from 11/20/36 turns to 6-10. The new threat (≈ 5 per turn against 1.0-1.5 today) lowers the win rate slightly at T3-T4. T1 stays at about 6.5 turns because the HP drop is offset by the orbit and resistance. Check that P2 takes 3-4 turns, using N19.

## 11. Q:
- Q: Should the Recall Tag also trigger on the player's **Perfect nudge-cards** (not only slice landings)?
- Q: Is Lock-On (a new hub rule) worth a field, or should P2 simply keep a slower orbit as the data-only fallback?
- Q: Should the Tag be a flat 4 or a PERCENT share of your max HP (it would then not scale with tier, as R2 intends for percent amounts)?
- Q: Does the P1 resistance of 1 still earn its place now that the orbit is the main tracking question?
- Q: Does the Tag count against the 30 % sustain cap analogue (a "tax cap"), or only at the designer's discretion?
