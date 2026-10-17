<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__account_manager; status ok; tokens in 9049 cache-write 32585 cache-read 0 out 14250; cost $0.121. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **#1 (BLOCKER, budget overrun at T2/T3):** reconciled. HP is now 56 / 68 / 88 (the band floors); v1 had 58 / 72 / 92. The phase split moves from 55 % to 60 %. §4 shows raw budget, HP, guard allowance and turns per phase, and states the remaining overrun (+1.5 HP at T2, +0.5 at T3 against the 66.5 / 87.5 sums). The critic's 90 at T3 is not used: 88 is the band floor and keeps P2 inside 4 turns. T2 68 is as the critic suggested.
- **#2 (BLOCKER, Late Fee rounding):** one rounding rule, round half up per instance: 2 / 2.6 / 3.38 becomes 2 / 3 / 3. Sustain is 22 % / 27 % / 21 %. The worst-case column is added (2 triggers = 4 / 6 / 6, which is 44 % / 55 % / 43 %). The 30 % cap is checked at the expected rate (§3). The critic's "7 at T3" assumed summing before rounding, which the interpreter does not do.
- **#3 (BLOCKER, Retainer hits vs budget):** guards now count. P1 turns are computed as (P1 boss HP + half a Retainer chewed) / (dpt − sustain). Retainer HP drops to 6 / 8 / 10 so that allowance is small. P1 is predicted at 3.6–3.9 turns, not 3.7 flat.
- **#4 (T4 row):** T4 is "n/a, no spawn". The validator must allow n/a for 2–3-phase mini-bosses. The copied value is removed.
- **#5 (corruption vs the free nudge):** Late Fee fires only when RAM > 0 is actually paid. A free nudge costs 0 × 2 = 0 and never triggers it. Corrupted-slice nudges that cost RAM do trigger it. This is an assumption on Q1.
- **#6 (parking claim):** the false "forces ≥ 2 turns" is removed. The skill-1.0 cell now reads "2–4 turns; parking only caps each resolve".
- **#7:** kept. The 6–8 turn class line, the predicted 7.4–7.6 and the irrelevant enrage all hold. The phase turns are re-shown in §4.
- **#8 (N6 payload):** N6 needs a `ram_paid` field in the ON_NUDGE context and `tier` in ON_PERFECT. This is added to §8, and the data-only fallback is reworded.
- **#9:** Retainer removal is tagged as a `wheel_override` side effect (N3 `clear_satellites`), not REPLACE.
- **#10:** wording fixed. The shield slice (type SANDBOX, 5) is removed from the wheel.
- **Triage rows (3):** all three BLOCKERs are covered by #1–#3.

---

# account_manager: direct design

## 1. Identity & the one question

- **Class:** mini-boss, 2 phases, 6–8 turns at the reference player. It guards the final Server Rack of a Solace netrun at T1–T3.
- **Layers:** Solace's first mini-boss, so it teaches the RAM economy. At T1 it is the taught end of layers 1–2. At T3 it is a layer 5–6 pressure fight.
- **Concept change from CONTENT_DESIGN_V2 §3:** I keep guards, then a counter on Perfects, and cut two things.
  - The resistance 1 goes: it absorbs a ±1 nudge entirely, so the RAM question could never arise.
  - The extra needle and the MIGRATE phase go. One needle in both phases keeps a first mini-boss readable.
- **P1 Retainer asks:** "Is steering this tick worth paying RAM?" Two danger slices carry guards, and every paid nudge feeds the boss BLOCK.
  - Shortest answer: use the free nudge and card movement (Spin, Flip, Freeze), which Late Fee ignores, to put the needle on Null or an unguarded Shim, then hit the unguarded slice.
- **P2 Collections asks:** "Is this Perfect worth 4 damage?" Perfects are taxed.
  - Shortest answer: land Good everywhere, except on a Perfect whose hook pays for the Clawback.
- The phases spend different resources: P1 spends RAM, P2 spends precision.

## 2. Phase plan

Slice sizes sum to 30, with centres from cumulative boundaries (R11). Amounts are FLAT, multiplied by the tier damage factor [1.0, 1.3, 1.69] (R2). Each instance is rounded half up. Values are shown at T1 / T2 / T3.

### P1: Retainer (100 % → 60 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (ticks) | Shim 10 (5, ticks 0–4) · **Overflow 16 (4, 5–8, guarded)** · Defrag 6 (5, 9–13) · **Dose (4, 14–17, guarded)** · Shim 10 (5, 18–22) · Null (7, 23–29) = 30 |
| Sub-tick maps | 5-tick: W G P G W · 4-tick Overflow / Dose: W G G W (no Perfect) · Null 7: W W G P G W W |
| Amounts (FLAT) | Shim 10 / 13 / 17 · Overflow 16 / 21 / 27 · Defrag (BLOCK) 6 / 8 / 10 · Dose: CORRUPTED on 1 random non-NULL player slice (R9: it then costs 2× RAM) |
| Satellites | 2 Retainers, fixed (R12), docked on Overflow and Dose. Each has a 2-slice mini-wheel (Shim 3 / Defrag 3 FLAT, so Shim 3 / 4 / 5), HP **6 / 8 / 10**. A player pointer attack on a guarded slice hits its Retainer first (GDD 2.7). A Retainer resolves after its host. |
| Hub rule | None |
| Listener (N6) | **Late Fee:** `ON_NUDGE` with `ram_paid > 0` → the boss gains BLOCK 2 FLAT (2 / 3 / 3). At most 2 triggers per turn. The free nudge (0 RAM) and card NUDGE effects never trigger it. |
| Statuses | CORRUPTED via Dose only |
| Intake target | Unsteered about 5.9 per turn at T1 (Shims 3.3, Overflow 2.1, Retainer Shim about 0.4 from the two hosts). Reference player about 3–4 at T1, scaled ×1.3 / ×1.69. |

- The listener reads staged actions and undoes with them. The preview shows "Late Fee +2 BLOCK".
- Retainers are optional targets. A hit on one is a hit the boss does not take, and the budget in §4 accounts for that.

### Transition P1 → P2 (at 60 %)

- **Parking:** damage parks at ceil(max HP × 0.60). The excess is lost, including a Perfect double-resolve in the same resolve.
- **Guards:** the Retainers are cleared by a `wheel_override` side effect (N3 `clear_satellites`). They count as removed, not destroyed. Late Fee ends.
- **Wheel:** `wheel_override` to the P2 layout.
- **Statuses:** kept with the centre-tick remap (R6); `cleanse_on_enter = NONE`. P1 corruption carries into P2, where the Perfect tax makes the RAM cost matter more.
- **Phase line:** "Account in arrears. Collections has been notified."

### P2: Collections (60 % → 0 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (ticks) | Shim 10 (5, 0–4) · Dose (5, 5–9) · Overflow 16 (4, 10–13) · Defrag 8 (4, 14–17) · Shim 10 (6, 18–23) · Null (6, 24–29) = 30 |
| Sub-tick maps | 5-tick: W G P G W · 4-tick Overflow / Defrag: W G G W · 6-tick Shim / Null: W W G G W W (no Perfect) |
| Amounts (FLAT) | Shim 10 / 13 / 17 · Overflow 16 / 21 / 27 · Defrag 8 / 10 / 14 · Dose: CORRUPTED on 1 random non-NULL player slice |
| Hub rule | None |
| Listener (N6) | **Clawback:** `ON_PERFECT` on a player slice → 4 FLAT (4 / 5 / 7) damage to the player. It is a normal hit (BLOCK, SHIELD and SANDBOX apply). It fires once per Perfect. |
| Statuses | CORRUPTED as the RAM tax. A long P2 can leave 2–3 corrupted slices. |
| Intake target | Slices unsteered about 5.8 at T1 (Shims 1.7 + 2.0, Overflow 2.1) plus Clawback about 2 at a 50 % Perfect rate. Reference player about 4–7 per turn at T1. |

- Perfect output equals Good (1.0×, GDD 2.4), so Perfects only buy hooks, and Clawback prices exactly that.

## 3. Sustain and intake

- **Sustain:** one source, Late Fee BLOCK in P1 only, and none in P2. BLOCK expires at the boss's next turn start, so each point soaks one point of that resolve.

| Tier | Late Fee per trigger (rounded) | Expected, 1 paid nudge per turn | Reference dpt | Share | Worst case (2 triggers) | Share |
|---|---|---|---|---|---|---|
| T1 | 2 | 2 | 9 | 22 % | 4 | 44 % |
| T2 | 3 (2.6) | 3 | 11 | 27 % | 6 | 55 % |
| T3 | 3 (3.38) | 3 | 14 | 21 % | 6 | 43 % |

- The 30 % cap is met at the expected rate. The worst case costs the player 2 RAM and the block lasts one resolve.
- **Retainers:** not sustain. They are optional, steerable around, and 6–10 HP.
- **Intake above 0:** P1 about 3–4 per turn at T1 (about 5 at T2, 6 at T3). P2 about 4–7 at T1 (about 7–9 at T2, 8–12 at T3).

## 4. HP by tier

Phase turns are computed as (phase boss HP + guard allowance) / (dpt − sustain). The guard allowance is half a Retainer's HP and applies to P1 only. Raw budget = (dpt − sustain) × 3.5 for P1 and dpt × 3.5 for P2. The mini-boss (2 phases) band is T1 56–72, T2 68–88, T3 88–112.

| Tier | Raw budget P1 + P2 | **HP** | Floor (0.60) | P1 HP | Guard allowance | P1 turns | P2 HP | P2 turns | Total turns |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 24.5 + 31.5 = 56 | **56** | 34 | 22 | 3 | (22+3)/7 = 3.57 | 34 | 34/9 = 3.78 | 7.35 |
| T2 | 28 + 38.5 = 66.5 | **68** | 41 | 27 | 4 | (27+4)/8 = 3.88 | 41 | 41/11 = 3.73 | 7.61 |
| T3 | 38.5 + 49 = 87.5 | **88** | 53 | 35 | 5 | (35+5)/11 = 3.64 | 53 | 53/14 = 3.79 | 7.43 |
| T4 | n/a: the mini-boss does not spawn at T4 (the validator must allow n/a here) | | | | | | | | |

- Floors are ceil(56×0.6)=34, ceil(68×0.6)=41 and ceil(88×0.6)=53. Dividing HP at the floor leaves P1 = 22 / 27 / 35.
- Reconciliation: HP sits at the band floor, so the sums run +0 / +1.5 / +0.5 over the raw budget. P2 is above its raw budget by 8 % / 6 % / 8 %, and P1 plus its allowance by 2 % / 11 % / 6 %. All phases stay within 3–4 turns.
- This replaces today's 150 HP × tier multiplier (384 at T3).

## 5. Enrage

- **Mini-boss default:** start turn 10, every 5 turns, +25 % damage, additive. It covers Shim, Overflow, Retainer attacks and Clawback, but not Late Fee block or heal.
- Predicted fights end around turn 7.5, so enrage only punishes stalling. The likely stall is a player who burns RAM in P1 or chases Perfects in P2.
- No authoring needed. Clawback already makes late turns more dangerous.

## 6. Buffs and counter Exploits

Not applicable (bosses only). The Solace Exploits (Intel, Breach, Virus) do not affect this fight.

## 7. Counterplay

- **P1, good player:**
  - Reads the guarded Overflow and Dose slices.
  - Spends the free nudge and card movement (Spin, Flip, Freeze) to put the needle on Null or an unguarded Shim.
  - Pays RAM only for a turn-ending threat (Overflow at the needle, a Dose on a Perfect hook) and accepts +2 BLOCK.
  - Ignores the Retainers and hits the unguarded Shim.
- **P1, weak player:** pays for every nudge and feeds Late Fee, attacks the guarded slice and wastes hits on a Retainer, or lets Dose corrupt a slice per turn and enters P2 with 2 corrupted slices.
- **P2, good player:**
  - Plays for Good, not Perfect: a 1-tick nudge on their own wheel turns a Perfect into a Good.
  - Takes the Perfect only when its hook is worth the 4 (a Breaker double-resolve pays; a weak hook does not).
  - Cleanses CORRUPTED early, because corruption doubles the cost of the very nudges used to avoid the Perfect.
  - Bursts on a Null needle: free damage with no Clawback, no intake.
  - Uses the Defrag turn: with the needle on Defrag nothing hits them.
- **P2, weak player:** chases a Perfect every turn and loses about 4 per turn, ignores corruption so the RAM tax compounds, or burns RAM steering and has none left to cleanse.

## 8. Systems needed

| N# | What | Fallback |
|---|---|---|
| N1 | FLAT amounts × the tier damage factor (Retainer, Late Fee, Clawback), half-up rounding per instance | Hand-authored per-tier values in the `.tres` |
| N2 | `hp_by_tier` (T1–T3 only), band validator that allows n/a at T4 for mini-bosses | Hand-set `hp` per tier |
| N3 | Parking at 0.60, status keep, `clear_satellites` on `wheel_override` | Today's phase + wheel override; no parking, no satellite clearing (Retainers stay) |
| N4 | Enrage defaults | None; keeps today's no-enrage fights |
| N6 | Late Fee (ON_NUDGE with `ram_paid` in the context) and Clawback (ON_PERFECT with `tier`). Reads staged actions, undo-clean. | Data-only: P1 = hub BLOCK 2 FLAT per turn (no paid-nudge condition) and P2 = Dose ×2 with today's CORRUPTED. Both questions are lost. |
| N9 | CORRUPTED as the 2× RAM debuff | Today's CORRUPTED (self-damage); P2 still reads but the RAM question is gone |
| N12 | Slice sizes 4–7 and sub-tick maps | All slices 5 ticks (6 slices). Loses the no-Perfect danger slices and the 7-tick Null. |
| N13 | Fixed satellites | Today's nudgeable satellites; the guard concept weakens |
| N19 | Turns per phase, listener fires | Manual count meanwhile |

## 9. Delta vs today

- **Kept:** the id, the corporation, the Shim 10 / Overflow 16 / Defrag / Dose / Null slice vocabulary, the 2-phase shape, and the Solace retainer-and-collections theme.
- **Changed:**
  - HP 150 → 56 / 68 / 88. Thresholds 0.5 / 0.25 → one at 0.60. The Migrate phase and the "Final notice" beat are dropped; the P2 phase line replaces them.
  - Passive resistance 1 is removed. The two pointers (MULTIPLY / MIGRATE) become one fixed needle per phase.
  - The shield slice (type SANDBOX, shield 5) is removed from the wheel. Defrag is the only boss defense here, because a lingering shield would turn the P1 block question into attrition.
  - New: two Retainer satellites, the Late Fee and Clawback listeners, and sizes 4–7.
- **`heat_effects`: retire.** The Heat-75 Retainer heal of 5 per turn would be a second sustain source (about 55 % of reference damage at T1), against R2's cap of one source and 30 %. Enrage covers the anti-stall role.

## 10. Predicted sim check

| Tier | Baseline | Predicted at the reference player | At skill 1.0 |
|---|---|---|---|
| T1 | 6.7 turns, 100 % | 7.4 turns, ≥ 97 % | 2–4 turns |
| T2 | 11.4 turns, 100 % | 7.6 turns, ≥ 95 % | 2–4 turns |
| T3 | 20.7 turns, 90 % | 7.4 turns, ≥ 92 % | 3–5 turns |
| T4 | 30.9 turns, 20 % | not spawned | n/a |

- **Why:** the baseline length came from attrition on one 150 HP pool. Two phases of 56–88 HP cut the turns. Clawback and RAM-gated steering keep intake above the baseline's 1.75–2.0 per turn.
- **Flag:** the bot at skill 1.0 deals 16–35 per turn and clears 56 HP in about 2–4 turns, below the class target. Parking only caps each resolve and does not force extra turns. The "turns inside class target" criterion should use the step-0 skill.

## 11. Open questions

Q: Does a nudge on a CORRUPTED slice cost 2× RAM when its base cost is 0 (the free nudge stays free)? P2's Good-over-Perfect line depends on it.
Q: Does Late Fee fire on Linked Bus nudges (free, so `ram_paid` = 0)? I propose no.
Q: Is a Retainer removed at the transition "destroyed" for Daemons and rewards? I propose no.
Q: Is the 30 % sustain cap judged at the expected rate (I assumed so) or at the worst case, where Late Fee reaches 43–55 %? If worst case, drop to 1 trigger per turn.
Q: Should the validator allow n/a at T4 for 2–3-phase mini-bosses, or should it carry an explicit "no spawn" flag?
