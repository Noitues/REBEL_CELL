<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__account_manager; status ok; tokens in 18999 cache-write 32007 cache-read 0 out 15178; cost $0.135. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# account_manager: direct design

## 1. Identity & the one question

- **Class:** mini-boss, 2 phases, 6–8 turns at the reference player. It guards the final Server Rack of a Solace netrun at T1–T3.
- **Layers:** it is Solace's first mini-boss, so it teaches the RAM economy. It sits at the end of layers 1–2 (the T1 Site, taught), and as a layer 5–6 pressure fight at T3.
- **Concept change:** I keep the concept (guards, then a counter on Perfects) but cut two things.
  - The old resistance 1 goes. A resistance of 1 absorbs a ±1 nudge entirely, so the free nudge does nothing and the RAM question never exists.
  - The old second needle and the pointer MIGRATE phase go. One needle in both phases keeps this fight readable as the player's first mini-boss.
- **P1 Retainer asks:** "Is steering this tick worth paying for?" Two guarded danger slices and a boss that banks BLOCK from every paid nudge.
  - Shortest answer: spend the free nudge and card-nudges, which the listener ignores, to put the needle on Null or an unguarded Shim, then attack the unguarded slice.
- **P2 Collections asks:** "Is this Perfect worth 4 damage?" Perfects are taxed, so the player decides which turns buy a Perfect hook and which settle for Good.
  - Shortest answer: Good everywhere, except a Perfect whose hook returns more than the 4 damage it costs.
- The two questions are different resources: P1 spends RAM on the enemy's wheel, P2 spends precision on your own.

## 2. Phase plan

Slice sizes sum to 30. Centres follow the cumulative boundaries (R11). Amounts are FLAT and multiplied by the enemy tier damage factor [1.0, 1.3, 1.69, 2.2] (R2); the shown values are T1.

### P1: Retainer (100 % → 55 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (clockwise, ticks) | Shim 10 (5) · **Overflow 16 (4, guarded)** · Defrag 6 (5) · **Dose (4, guarded)** · Shim 10 (5) · Null (7) = 30 |
| Sub-tick maps | 5-tick slices W G P G W; the 4-tick Overflow and Dose slices W G G W (no Perfect); Null 7 W W G P G W W |
| Overflow / Dose | Overflow 16 FLAT. Dose: CORRUPTED on 1 random non-NULL player slice (R9: that slice now costs 2× RAM). |
| Satellites | 2 Retainers, fixed (R12), docked on Overflow and Dose. Each has a 2-slice mini-wheel (15 ticks per slice): Shim 3 / Defrag 3, HP 8 / 10 / 13 (T1 / T2 / T3). A player pointer attack at a guarded slice hits the Retainer, not the boss (GDD 2.7). A Retainer resolves after its host. |
| Hub rule | None |
| Listener (N6) | **Late Fee:** `ON_NUDGE` where the nudge cost RAM (an extra nudge, not the free one and not a card's NUDGE effect) → the boss gains BLOCK 2 FLAT. At most 2 triggers per turn. |
| Statuses / parasites | CORRUPTED via Dose only |
| Intake target (reference player) | 2–4 per turn |

- The listener reads staged actions and undoes with them, so the preview is exact. The preview line reads "Late Fee +2 BLOCK".
- Card nudges and Spin/Flip cards are the clean answer. The player pays RAM only when nothing else moves the needle.

### Transition P1 → P2 (at 55 %)

- **Parking:** damage parks at ceil(max HP × 0.55). The excess is lost, including a Perfect double-resolve landing in the same resolve.
- **Guards:** both Retainers are removed (their HP is not counted as "destroyed"). Late Fee ends.
- **Wheel:** `wheel_override` to the P2 layout.
- **Statuses:** kept, with the centre-tick remap (R6); `cleanse_on_enter = NONE`.
  - Corruption you took in P1 carries into P2, where the RAM tax matters more.
- **Phase line:** "Account in arrears. Collections has been notified."

### P2: Collections (55 % → 0 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (ticks) | Shim 10 (5) · Dose (5) · Overflow 16 (4) · Defrag 8 (4) · Shim 10 (6) · Null (6) = 30 |
| Sub-tick maps | Shim 5: W G P G W. Dose 5: W G P G W. Overflow 4 and Defrag 4: W G G W. Shim 6: W W G G W W (no Perfect). Null 6: W W G G W W. |
| Dose | CORRUPTED on 1 random non-NULL player slice |
| Hub rule | None |
| Listener (N6) | **Clawback:** `ON_PERFECT` on a player slice → 4 FLAT damage to the player (a normal hit: BLOCK, SHIELD and SANDBOX apply). It fires once per Perfect. |
| Statuses | CORRUPTED (the RAM tax). The player's wheel can end up with 2–3 corrupted slices over a long P2. |
| Intake target | 4–7 per turn (about 3 from slices, about 2 from Clawback at a 50 % Perfect rate) |

- The P2 wheel is a shorter, harsher read than P1: 4+4 tick no-Perfect slices, an oversized Null, and every dangerous slice exposed.
- Perfect output is 1.0×, the same as Good (GDD 2.4). Perfects therefore only buy hooks, and Clawback prices exactly that.

## 3. Sustain and intake

- **Sustain:** a single source, Late Fee BLOCK in P1 only. BLOCK expires at the boss's next turn start, so each point soaks one point of the player's hit this resolve.
  - Expected sustain: about 1 paid nudge per turn at the reference player, which is 2 / 3 / 3 per turn (T1 / T2 / T3, FLAT × tier factor, rounded).
  - Against reference damage per turn [9, 11, 14] that is 22 % / 27 % / 21 %, under the 30 % cap.
  - Worst case is 2 triggers = 4 block (2.6 × 2 → 5 at T2), and it requires the player to spend 2 RAM.
- **P2 sustain:** none. The Retainer guards are not counted as sustain: they are optional, steerable around, and 8–13 HP.
- **Intake (above 0 in both phases):**
  - P1: unsteered, the two Shims and the Overflow (unguarded) give about 2.7 + 1.6 ≈ 4.3 at T1. The reference player's partial steering cuts that to about 3 per turn. Retainer Shim 3 adds when its host resolves.
  - P2: about 3 from slices plus about 2 from Clawback ≈ 5 at T1.
  - Both phases scale ×1.3 / ×1.69 with tier.

## 4. HP by tier

- **Phase budget** (R2): `dpt × 3.5 turns × 1 needle − sustain/turn × 3.5`. One enemy needle means no needle multiplier.
- The mini-boss (2 phases) band is T1 56–72, T2 68–88, T3 88–112.

| Tier | P1 budget (dpt − sustain) × 3.5 | P2 budget (dpt × 3.5) | Sum | **HP** | Floor (55 %) | P1 HP | P2 HP |
|---|---|---|---|---|---|---|---|
| T1 | (9 − 2) × 3.5 = 24.5 | 9 × 3.5 = 31.5 | 56 | **58** | 32 | 26 | 32 |
| T2 | (11 − 3) × 3.5 = 28 | 11 × 3.5 = 38.5 | 66.5 | **72** | 40 | 32 | 40 |
| T3 | (14 − 3) × 3.5 = 38.5 | 14 × 3.5 = 49 | 87.5 | **92** | 51 | 41 | 51 |
| T4 | n/a (the mini-boss does not spawn at T4) | | | 92 (copy of T3 so the 4-entry validator passes) | | | |

- I round up 2–4 HP against the band's lower edge. Late Fee block and guard HP both make P1 slightly longer than the table implies.
- Thresholds are 0.55 for every tier. This replaces today's 150 HP and its tier multiplier (384 at T3).
- Expected turns at the reference player: P1 3.7 / 4.0 / 3.7 and P2 3.6 / 3.6 / 3.6, about 7.3 turns, inside 6–12.

## 5. Enrage

- **Mini-boss default:** start 10, every 5, +25 % damage, additive (×1.25, ×1.5). It covers Clawback and Shim/Overflow damage, not Late Fee block.
- At the reference pace the fight ends around turn 7, so enrage only punishes stalling. The likeliest stall is a player who never takes the Good-over-Perfect line and bleeds in P2, or who burns RAM in P1.
- The default needs no authoring. Clawback already makes late turns more dangerous.

## 6. Buffs and counter Exploits

Not applicable (bosses only). This is a mini-boss. Its counter-play comes from the Solace Exploit set indirectly: Breach and Intel behave as today and do not affect it.

## 7. Counterplay

- **P1 good player:**
  - Reads the Retainer-guarded Overflow and Dose slices.
  - Uses the free nudge on the enemy wheel, or a Spin/Freeze/Flip card, to move the needle onto Null or an unguarded Shim.
  - Spends the free nudge on the enemy wheel on the first turn. Pays RAM only for a turn-ending threat (Overflow at the needle, a corrupt-the-Perfect Dose) and accepts +2 BLOCK.
  - Avoids spending the Retainers' HP: ignores them and attacks the unguarded Shim.
  - Finishes P1 before the guards have fired many times.
- **P1 weak player:** pays for every nudge (3 RAM at once feeds Late Fee), lands attacks on the guarded slice and wastes hits on a Retainer, or lets Dose corrupt one slice per turn and enters P2 with 2 corrupted slices.
- **P2 good player:**
  - Plays for Good, not Perfect: a 1-tick own-wheel nudge costs the free nudge and turns a Perfect into a Good.
  - Takes the Perfect only when the hook is worth 4 damage: a Breaker double-resolve Perfect pays, a weak hook does not.
  - Cleanses CORRUPTED slices early, because with the 2× cost the free nudge is the first thing taxed.
  - Uses a SANDBOX slice on the turn Overflow or Dose is at the needle.
  - Bursts a Null window: a Null needle deals damage to the boss with no cost to the player.
- **P2 weak player:** chases Perfect every turn and loses about 4 per turn, ignores the corrupted slices so the RAM tax compounds, or burns RAM steering and has none left to cleanse.

## 8. Systems needed

| N# | What | Fallback |
|---|---|---|
| N1 | FLAT amounts × the tier damage factor (Retainer, Late Fee, Clawback) | Hand-authored per-tier values in the `.tres` |
| N2 | `hp_by_tier` and the band validator | Hand-set `hp` and a per-tier override |
| N3 | Phase parking at 0.55, status keep, `cleanse_on_enter` | Today's phases work for the pointer layout; no parking, so the ≥ 2 phase turns can be skipped |
| N4 | Enrage defaults | None; keeps today's no-enrage fights |
| N6 | Late Fee (ON_NUDGE with RAM cost) and Clawback (ON_PERFECT) listeners | Data-only: P1 Retainer = hub block 2 FLAT per turn, P2 Clawback = none and Dose ×2 CORRUPTED (existing self-damage CORRUPTED). The Perfect/RAM questions are lost. |
| N9 | CORRUPTED as the RAM debuff (2× RAM) | Existing CORRUPTED (self-damage); P2 still reads, but the RAM question is gone |
| N12 | Variable slice sizes (4, 5, 6, 7) and sub-tick maps | All slices 5 ticks: six slices (Shim, Overflow, Defrag, Dose, Shim, Null) at 5 each. Loses the no-Perfect 4-tick danger slices and the Null window. |
| N13 | Fixed satellites (Retainer fixed, removed at the transition) | Satellites exist today; they can be nudged, which weakens the guard concept |
| N14 | BLOCK expiry rule | None; the existing DEFRAG block already works |
| N19 | Sim metrics (turns per phase, listener fires) | Needed to validate; a manual count meanwhile |

## 9. Delta vs today

- **Kept:** the id, the corporation, the Shim 10 / Defrag / Overflow 16 / Dose / Null slice set, the 2-phase shape, the Solace theme (retainer, collections, billing).
- **Changed:**
  - HP 150 → 58 / 72 / 92, thresholds 0.5 / 0.25 → one at 0.55. The old Migrate phase is gone.
  - Passive resistance 1 → none, and the two pointers (MULTIPLY / MIGRATE) are replaced by one fixed needle in each phase.
  - New: two Retainer satellites, Late Fee and Clawback listeners, new wheel sizes (4–7).
  - Sandbox 5 → removed. The player-facing defence is now Defrag only on this wheel; SHIELD would turn the P1 block question into attrition.
  - The existing "Final notice" Migrate beat is dropped; the P2 phase line replaces it.
- **`heat_effects`: retire.** Retainer healing 5 each turn at Heat 75+ would be a second sustain source (about 55 % of reference damage at T1), against R1 and R2 and the 30 % cap. Enrage covers the anti-stall role.

## 10. Predicted sim check

| Tier | Baseline | Predicted at the reference player | At skill 1.0 |
|---|---|---|---|
| T1 | 6.7 turns, 100 % | 7.3 turns, ≥ 97 % | 3–5 turns; the parking floor forces ≥ 2 turns |
| T2 | 11.4 turns, 100 % | 7.6 turns, ≥ 95 % | 3–5 turns |
| T3 | 20.7 turns, 90 % | 7.3 turns, ≥ 92 % | 4–6 turns |
| T4 | 30.9 turns, 20 % | not spawned | n/a |

- **Why:** baseline length was attrition on one 150 HP pool. 58–92 HP in two phases cuts the turns, while Clawback and RAM-gated steering keep intake above the baseline's 1.75–2.0 per turn.
- **Flag:** the bot at skill 1.0 deals 16–35 per turn, 2–3× the reference, so it clears 58 HP in 3–5 turns, below the 6–12 target. The "mean turns inside the class target" criterion should use the step-0 skill, not 1.0 (Q on the reference player, V2 question 1).

## 11. Open questions

Q: Does the free nudge on a CORRUPTED slice cost 1 RAM (2× of 1) or stay free? It decides whether P2's Good-over-Perfect nudge is itself taxed.
Q: Does Late Fee trigger on Linked Bus nudges (a Daemon nudge on the enemy wheel that also moves yours, free)? I propose no, since those are free.
Q: Are the Retainers' removal at the transition "destroyed" for Daemons and rewards? I propose no (removed, not killed).
Q: Is retiring the Heat-75 heal acceptable, or should Heat 75+ instead add a third Late Fee trigger (+2 block) in P1?
Q: Should the mini-boss band lower edge hold for T2 at 72 HP, or is 68 (the exact budget) closer to the intended feel?
