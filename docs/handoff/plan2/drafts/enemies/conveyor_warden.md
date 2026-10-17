<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__conveyor_warden; status ok; tokens in 16147 cache-write 0 cache-read 32007 out 3435; cost $0.037. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# conveyor_warden: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, Meridian. It appears in L1-2 as a teaching enemy for **moving pointers**, and in L5-6 at T3-T4 as a pressure enemy, where the Priority slice becomes a real RAM tax.
- **The one question:** *"Where will its needle be, and can you make it arrive somewhere harmless?"* Its pointer orbits 3 ticks per turn, so the landing is readable one turn ahead. The orbit is a conveyor belt, and the wheel's layout is built so that exactly one slice sits in a danger window each turn.
- **Answer that shortens the fight:** Sort the belt. Nudge or spin its wheel so the needle lands on the 6-tick Null/Defrag gap or the weak edge of Shim. Then spend the turns it can't hurt you on burst. A player who ignores the orbit eats an Overflow 16 at about T2.
- **Distinct from siblings:**
  - Customs Scanner: it reads or reveals.
  - Cargo Hauler: HP-heavy.
  - Drone Dispatcher: satellites.
  - Route Optimizer: respin or lock.
  - Tariff Collector: economy.
  - The Warden is the only plain "orbit" normal. Its Weight and respin tricks belong to others.

## 2. Phase plan (single phase, no thresholds, no floor)

**Needles:** 1, starting at tick 0 and orbiting +3 ticks per turn (`pointer_orbit_per_turn = 3`). The start-of-turn respin still randomizes the wheel. The orbit then moves the pointer, which makes next turn's landing predictable from the current preview, because the player sees the trail (GDD 2.11).

**Layout (sum 30, N12 sizes):**

| Order | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 0 | Shim | 6 | 8 damage (WEAK edge ticks 0, 1, 4, 5) | FLAT |
| 1 | Overflow "Heavy Load" | 4 | 14 damage; no Perfect tick (W G G W) | FLAT |
| 2 | Priority | 5 | 3 damage + drain 2 RAM | FLAT |
| 3 | Defrag | 6 | 6 BLOCK | FLAT |
| 4 | Shim | 5 | 8 damage | FLAT |
| 5 | Null | 4 | nothing | n/a |

- The Overflow is only 4 ticks, so it has no Perfect, and the player can never hit it dead-centre to amplify it. Its GOOD ticks are just 2 of 4.
- The Priority is now an actual attack (3 damage) with a RAM drain, so it is both a tax and a hit. Today it is a damage-less INFECT carrying a drain.
- **Hub rule:** none.
- **Statuses, parasites, listeners:** none. This is a pure geometry question.

**Orbit arithmetic:** 3 ticks per turn means the needle crosses a 5-tick slice in under 2 turns. It spends about 1.8 turns on a slice, so the landing is "sticky": the same slice often resolves twice in a row. Players can plan around that, since the next turn's slice is visible.

## 3. Sustain and intake
- **Sustain:** a single source, the Defrag 6 BLOCK (FLAT, times the tier damage factor). It is block, not heal. At the reference player (T1, 9 per turn), 6 BLOCK on 6 of 30 ticks (20 % of landings) gives an expected 1.2 per turn, about 13 % of reference damage, under the 30 % cap. Even at its worst (a guaranteed Defrag every turn) it absorbs 6 of 9, which is why the player should dodge it by steering.
- **Intake per turn (T1 reference player, no steering):** the weight is the tick share of each slice, with a WEAK landing at 0.5×.
  - Shim 6 and Shim 5: 11/30 × about 8 × 0.9 ≈ 2.6
  - Overflow: 4/30 × 14 × 0.75 ≈ 1.4
  - Priority: 5/30 × 3 ≈ 0.5, plus 0.33 RAM per turn
  - Total ≈ **4.5 damage per turn** unsteered. With good steering it falls toward 1–2, and it never reaches 0. The Null window lasts only 4 ticks, so the player can't hold it for more than one turn at a time.
- Over a 3.5-turn fight that is about 16 HP at T1 and about 26 at T3 (×1.69). This is an easy teaching fight, not a lethal one. It is far above Dosage Dispenser's 0.05.

## 4. HP by tier (R2 Normal band, 1 phase)
Budget: `reference_dpt_by_tier` × 3.5 turns, minus sustain × 3.5.

| Tier | dpt | Gross | Sustain (13 %) | HP | Band |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | −4 | 30 | 28–36 |
| T2 | 11 | 38.5 | −5 | 38 | 34–44 |
| T3 | 14 | 49 | −6 | 48 | 44–56 |
| T4 | 18 | 63 | −8 | 62 | 56–70 |

`hp_by_tier` = [30, 38, 48, 62]. Today's 54 sits near T3 and needs no multiplier.

**Damage per tier (R2):** the table is ×[1.0, 1.3, 1.69, 2.2] on the flat amounts. Overflow reads 14, 18, 24, 31. This is intentional: block and drain scale as flat enemy amounts too.

## 5. Enrage
**None (class default for normals is off).** The fight is 3–4 turns, so a clock is unnecessary.

## 6. Buffs and counter Exploits
Not applicable (normals only).

## 7. Counterplay
- **Good player:**
  - Reads the trail and the next-turn slice. If the needle is about to enter Overflow, they spend the free nudge (1 tick) to push the landing to its WEAK edge or into Null. The 4-tick Overflow has no Perfect, so a nudge of 1–2 ticks is enough.
  - Nudges the Warden's wheel to hold it on Null or Defrag only when cheap, then bursts when it lands on Shim's WEAK edge.
  - Doesn't waste damage into the Defrag 6; instead cards its steering on the turn the Defrag arrives. Avoids the Priority when RAM is short.
  - Lines up a burst on turn 2 using the sticky needle, killing it in 3 turns.
- **Weak player:**
  - Ignores the orbit and stays in the same position.
  - Nudges the Warden's wheel without checking the next turn, so the needle moves into the Overflow anyway.
  - Spends RAM on a nudge, then eats the Priority drain.
  - Pours damage into the BLOCK, which stretches the fight to 5–6 turns.

## 8. Systems needed
| Need | System | Fallback |
|---|---|---|
| Variable sizes (4, 5, 6) | N12 | Use 5-tick slices (6 × 5) and a 6th Null. The Overflow then has a Perfect, which is weaker as a design. Acceptable. |
| Flat amounts × tier factor, `hp_by_tier` | N1, N2 | Hand-set HP now, and use today's scale. |
| Priority as damage + RAM drain | existing (the effect already exists, add a damage rider) | N20 `hits`/damage on an INFECT slice, or swap it to a SHIM-type slice with an extra DRAIN_RAM effect. This is data-only. |
| Orbit | existing `pointer_orbit_per_turn` (GDD 2.11) | None needed. |
| R10 (pointer on any tick) | N11 | The orbit of 3 already breaks multiples of 5, so it needs N11 for a valid pointer position. Data fallback: use an orbit of 5 (a multiple of 5). |

## 9. Delta vs today
- **Kept:** the id, the orbit of 3, the Shim, Defrag, Overflow, Priority, Null composition, and `cycle_reward = 15`.
- **Changed:**
  - HP 54 → [30, 38, 48, 62].
  - Slice sizes become uneven (6/4/5/6/5/4), with the Overflow at 14 and no Perfect.
  - Priority gains 3 damage.
  - The second Shim is reduced from 10 to 8.
  - Overflow drops from 16 to 14.
  - Two Shims no longer sit adjacent: the order is interleaved.
- **`heat_effects`:** none today, and none added.

## 10. Predicted sim check
No baseline row exists (the baseline covered Solace only). This is an estimate from the wheel.
- **Turns:** 3.5 on average at the reference player, with p90 ≤ 5.
- **Win %:** T1 about 99 %, T2 about 98 %, T3 about 94 %, T4 about 90 %. Intake is under 30 HP in the worst case, and there's no enrage or heal.
- **Why:** HP is sized for 3.5 turns, and its single sustain is block that a steering player dodges. Today's 54 HP at T1 would take about 6 turns, so the fight is shorter and the question is clearer.

## 11. Open questions
Q: Should the sticky orbit (about 1.8 turns per slice) be shown as a trail of the next 2 turns, or only the next turn, for L1-2 teaching?
Q: Is a 4-tick Overflow with no Perfect legible enough, or should it show a "no Perfect" marker on the intent plate?
Q: Should the Priority RAM drain scale by the tier factor (2, 3, 3, 4) or stay flat at 2, since RAM is a player resource?
