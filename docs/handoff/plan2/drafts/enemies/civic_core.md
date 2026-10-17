<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__civic_core; status ok; tokens in 17500 cache-write 0 cache-read 32007 out 26125; cost $0.151. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# civic_core: direct design

*Working title for the fight: "state of emergency". The designer-facing name is THE PANOPTICON; the id stays `civic_core`.*

## 1. Identity & the one question

- **Class and corporation:** HQ boss (Central Server), Halcyon Civic. T4 only, so it appears only in the final HQ netrun, as an L6-pressure fight. It never teaches.
- **Concept:** a city government that declares a new emergency every time it is pressed. Each phase is a different decree that taxes a different habit of yours. The marks it stamps on your wheel in P1 persist (R6) and are cashed in later, so a sloppy early game is paid for in P3 and P5.
- **Signature status:** TIER_DOWN (R8, anti-Firmware). Each stack makes a landing on that slice read one tier lower. One stack costs the Perfect hook. Two stacks make every landing WEAK. Stacks cap at 2 per slice.

**The question each phase asks:**

| Phase | Name | Question | What shortens the fight |
|---|---|---|---|
| P1 | Watch Order | Where do you land? | Burst the 51 HP before marks spread; Cleanse or ENCRYPT the marked slices. |
| P2 | Assembly Ban | How few cards can you win with? | Play two strong cards, not five weak ones. |
| P3 | Warrants | How clean is your wheel? | A low mark count, because Warrant hits scale with it. Read the 3-tick orbit trail. |
| P4 | Martial Law | Which of two needles do you SANDBOX? | Burst while there is no heal. SANDBOX the Crackdown needle, steer the other off Crackdown. |
| P5 | Final Verdict | Is there a safe slice? (There isn't.) | Plan the 5-tick orbit two turns ahead. Take a WEAK edge, and have burst saved. |

## 2. Phase plan

**Common to every phase:**
- Authored damage is FLAT and is multiplied by the T4 damage factor 2.2 (R2). Both the authored value and the T4 value are shown.
- Sub-tick maps follow R11. A size-5 slice is W G P G W (average quality 0.8). A size-4 slice is W G G W, with no Perfect (0.75). A size-3 slice is G P G (1.0).
- Statuses are kept across every transition (R6). Each moves to the slice covering its old centre tick. `cleanse_on_enter` is NONE everywhere.
- Floors follow R3, at max HP 340 (band ≤ 1.00). The preview shows "PARKED −N". The last phase has no floor.

**Slice working names** (new files `content/slices/hal_*.tres`):

| Slice | Type | Effect | T4 value |
|---|---|---|---|
| Notice | INFECT | 0 damage. APPLY_STATUS TIER_DOWN ×1 on your slice under the pointer (UNDER_POINTER) | n/a |
| Fine | SHIM | 4 FLAT | 9 |
| Dispersal | OVERFLOW | 8 FLAT | 18 |
| Warrant | SHIM | 3 FLAT per hit. Hits = number of your slices carrying TIER_DOWN, min 1 (`hits_per_target_status`, N20) | 7 per hit |
| Crackdown | OVERFLOW | 7 FLAT | 15 |
| Baton | SHIM | 3 FLAT, `hits` = 2 | 13 total |
| Verdict | OVERFLOW | 9 FLAT | 20 |
| Null | NULL | nothing | n/a |

### P1 Watch Order (100 → 85 %, floor 289)

| Item | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (sum 30) | Notice 6 · Fine 5 · Notice 4 · Null 7 · Fine 4 · Notice 4 |
| Hub | Emergency Powers: HEAL 1 % max HP per turn (PERCENT) |
| Statuses | TIER_DOWN from Notice. No listeners. |

- **Why it works:** only 9 of the 30 ticks hurt. The real cost is the 14 Notice ticks, which stamp a mark about every other turn. The 4-tick Notices have no Perfect, but the mark is applied at any quality.
- **Target:** a clean opener that teaches that marks follow your landings.

### P2 Assembly Ban (85 → 72 %, floor 245)

| Item | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (sum 30) | Notice 5 · Fine 6 · Dispersal 3 · Null 6 · Notice 4 · Fine 3 · Null 3 |
| Hub | HEAL 1.5 % per turn |
| Listener (N6) | ON_CARD_PLAYED: each card you play beyond the 2nd in a turn deals 2 FLAT (4.4, rounded to 4) to you |

- **Transition:** `wheel_override` and `hub_override` only. P1's marks carry over.
- **Wheel:** Dispersal (a 3-tick G P G) is the first big hit. Unlike a 5-tick slice it can't be pushed to a WEAK edge by one nudge, so you either steer it off the needle or SANDBOX it.
- **The Ban:** the damage is staged with the card and undoes with it, and card hover shows "BAN +4". A 5-card dump costs 12.

### P3 Warrants (72 → 59 %, floor 201)

| Item | Value |
|---|---|
| Needles | 1, ORBIT 3 ticks per turn. The trail shows next turn's reading, so you plan two turns ahead. |
| Layout (sum 30) | Warrant 6 · Notice 4 · Dispersal 3 · Null 5 · Warrant 5 · Fine 4 · Null 3 |
| Hub | HEAL 1.5 % per turn |
| Listeners | None. The Ban ends here. |

- **Transition:** `wheel_override`, pointer behavior ORBIT, `hub_override` to drop the Ban.
- **Payoff:** this cashes in your P1/P2 marks. With 3 marked slices a Warrant is 3 hits of 7. Cleanse is now a damage card.

### P4 Martial Law (59 → 20 %, floor 68)

| Item | Value |
|---|---|
| Needles | 2: ticks 0 and 13 (MULTIPLY, uneven per R10) |
| Layout (sum 30) | Crackdown 4 · Baton 3 · Notice 3 · Crackdown 4 · Null 4 · Baton 4 · Crackdown 4 · Null 4 |
| Hub | Emergency Powers stops healing. No block anywhere. |
| Listeners | None |

- **Transition:** `wheel_override`, MULTIPLY (0, 13), `hub_override` with the heal removed. Plan: marks stay, and the boss gets no sustain from here on.
- **Defense:** SANDBOX (R13) negates every hit of one resolution. A Baton is a double hit, so it is the cheapest SANDBOX in the game. Crackdown is a single big hit, which is the real target.
- **Needle spacing:** 13 ticks apart means one nudge rarely fixes both needles. You choose which one reads Null or a WEAK edge.

### P5 Final Verdict (20 → 0 %, no floor)

| Item | Value |
|---|---|
| Needles | 1, ORBIT 5 ticks per turn (back from 2 needles) |
| Layout (sum 30) | Verdict 3 · Warrant 6 · Notice 5 · Crackdown 4 · Fine 4 · Baton 4 · Notice 4 |
| Hub | None |
| Listeners | None |

- **No Null slice:** every landing does something.
- **Transition:** `wheel_override`, pointer ORBIT, `hub_override` cleared.
- **Question:** which slice do you take, not whether to take one. Your accumulated marks make the Warrant the dangerous one.

## 3. Sustain and intake

**Sustain: one source, the Emergency Powers hub heal (PERCENT, N1).** Reference damage is 18 per turn; the R2 cap is 30 %, which is 5.4.

| Phase | Heal | Per turn at 340 max HP | Share of 18 |
|---|---|---|---|
| P1 | 1 % | 3.4 | 19 % |
| P2 | 1.5 % | 5.1 | 28 % |
| P3 | 1.5 % | 5.1 | 28 % |
| P4 | none | 0 | 0 % |
| P5 | none | 0 | 0 % |

Heal turns per phase stay under 4, since there is no extra sustain from block or shield.

**Intake per turn** at the reference player, before enrage and before SANDBOX or steering. It is an expected value over the boss's slice ticks at average sub-tick quality.

| Phase | Calculation | Intake (T4) |
|---|---|---|
| P1 | Fine 9 ticks: 0.30 × 9 × 0.85 | ≈ 2.3 plus ≈ 0.5 marks per turn |
| P2 | Fine 2.2 + Dispersal 1.8 + Ban 4.4 (one card over) | ≈ 8.4 |
| P3 | Warrant 11 ticks, 3 marks: 0.367 × 21 × 0.8 ≈ 5.9; Dispersal 1.8; Fine 1.0 | ≈ 8.7 |
| P4 | Per needle 4.6 (Crackdown) + 2.6 (Baton) = 7.2; two needles | ≈ 14.4 before enrage |
| P5 | Verdict 2.0 + Warrant 3.2 + Fine 0.9 + Crackdown 1.5 + Baton 1.5 | ≈ 9.1 before enrage |

Intake is above 0 in every phase. The 2.3 of P1 is low but needs the mark stamps to bite.

## 4. HP by tier (hp_bands, R2)

**Budget arithmetic.** HP per phase = (18 × needles the player's hits land on − sustain per turn) × 3.5.

| Phase | Needles | Sustain | Budget |
|---|---|---|---|
| P1 | 1 | 3.4 | (18 − 3.4) × 3.5 = 51 |
| P2 | 1 | 5.1 | (18 − 5.1) × 3.5 = 45 |
| P3 | 1 | 5.1 | (18 − 5.1) × 3.5 = 45 |
| P4 | 2 | 0 | 36 × 3.5 = 126 |
| P5 | 1 | 0 | 18 × 3.5 = 63 |
| **Sum** | | | **330** |

The slack of 10 goes into P5. At 340 the parked HP per phase is 51 / 44 / 44 / 133 / 68. P4 runs about 3.7 turns and P5 about 3.8, both inside the 3–4 target.

**hp_bands** (zone ceiling of the ICE boss-strength multiplier → max HP):

| Ceiling | HP | P1–P5 HP at fixed thresholds 0.85 / 0.72 / 0.59 / 0.20 |
|---|---|---|
| ≤ 1.00 | 340 | 51 / 44 / 44 / 133 / 68 |
| ≤ 1.15 | 380 | 57 / 49 / 49 / 148 / 76 |
| ≤ 1.30 | 420 | 63 / 55 / 55 / 164 / 84 |
| > 1.30 | 460 | 69 / 60 / 60 / 179 / 92 |

Today's 360 sits between the first two bands. The R2 hub-heal fix means no tier factor is applied to PERCENT amounts. No T1–T3 entries: it is T4 only.

## 5. Enrage

**Default (R4):** start turn 10, every 5 turns, +25 % additive, damage only. I keep it for these reasons:
- A reference player reaches P4 around turn 10.5, so step 1 lands exactly at the burst phase (14.4 → 18 per turn).
- P5 starts around turn 14, so step 2 (×1.5, turn 15) hits the finish. Intake rises 9 → 14.
- Heal stays unaffected by enrage, so it cannot be the stall tool.

**Authored add-on:** the Sunset Clause buff (section 6) changes the enrage cadence inside P5 only. With it, steps come every 2 turns instead of 5.

## 6. Buffs and counter Exploits

A Grid draws 5 of these 8 (`exploits_per_grid`), and `min_exploits_for_breach = 3` still holds.

| Buff (strong) | Effect | Counter Exploit turns off | Signature? |
|---|---|---|---|
| **Emergency Powers** | The P1–P3 hub heal (1 / 1.5 / 1.5 %) | All boss heal (today's Breach, "Emergency Override") | **Yes** |
| **Sunset Clause** | P5: enrage steps every 2 turns, and the P5 orbit is 5 not 3 | Back to default enrage and orbit 3 | **Yes** |
| Closed Session | Phases and next layouts hidden | Reveals them (today's Intel) | no |
| Warrant Ledger | Warrant hits = total TIER_DOWN stacks, not marked slices | Back to marked-slices count (flavored as the Virus "Open Data Leak") | no |
| Watchlist | Notice applies ×2 stacks | ×1 | no |
| Tight Ban | The Ban threshold is 1 card, not 2 | Back to 2 | no |
| Rapid Response | Crackdown 9 FLAT (20 at T4), Dispersal 10 (22) | Base values | no |
| Sealed Docket | Boss wheel has resistance 2 (absorbs nudges; blocks Flip and Respin) | The resistance | no |

**Why these two are signatures:**
- Emergency Powers defines the early game: with it off, P1–P3 shrink by about 12 HP each in net.
- Sunset Clause defines the late game: it is the only buff that changes the clock, not the numbers.

## 7. Counterplay

**Per phase, a good player:**
- **P1:** lands on Null, a Notice's WEAK edge or a Fine's WEAK edge, spreads landings across slices, and keeps ENCRYPTED or Cleanse ready for two marks. The aim is to burst 51 HP in 3 turns and enter P2 with zero or one mark.
- **P2:** plays two high-value cards and passes. A free nudge is not a card, so it is exempt. SANDBOX the Dispersal turn.
- **P3:** Cleanse is the best damage-prevention card. Read the orbit trail: it is a pure deterministic plan. Spend a nudge to push a Warrant needle onto its WEAK edge.
- **P4:** SANDBOX one needle, steer the other. A double-hit Baton is the cheapest SANDBOX target. Finish 133 HP before step 2 at turn 15. There is no heal, so burst pays.
- **P5:** there is no safe slice, so compare WEAK edges. Keep marks low, because Warrant is the only slice you can shrink. Use saved burst for the last 68 HP.

**A weak player:**
- dumps their hand in P2 and pays 12 per turn;
- ignores P1 marks and meets P3 with 5 marked slices, where each Warrant is 5 hits of 7;
- spends SANDBOX on a Baton or on the wrong needle in P4;
- reaches P5 after step 2 with no burst, and at ×1.5 intake loses.

## 8. Systems needed

| N# | Use | Data-only fallback |
|---|---|---|
| N1 | PERCENT heal, FLAT damage × tier factor | none; the hub heal needs it |
| N2 | `hp_bands`, damage table | none |
| N3 | Five phases, parking, status keep and remap | none |
| N4 | Enrage default | none |
| N5 | 8 buffs, Exploit counters, `exploits_per_grid` | none |
| N6 | P2 Ban: ON_CARD_PLAYED with a cards-this-turn threshold (a count condition on the listener) | replace with a Ban slice in the wheel; lose the card-count question |
| N8 | ×N TIER_DOWN stacks (cap 2) | PARASITE as a 2-stack OUTPUT_DOWN approximation |
| N9 | TIER_DOWN status rules | none; the signature status needs it |
| N11 | Needles at 0 and 13 | use 0 and 15 |
| N12 | Variable slice sizes, 7–8 slices per wheel | 6 × 5-tick slices; P2 and P3 lose Dispersal and the narrow 3/4 slices |
| N14 | SANDBOX negates a whole resolution | none; P4 hinges on it |
| N19 | Turns-per-phase metric | none |
| N20 | `hits`, `hits_per_target_status` | Warrant becomes a flat 3 hits |

Not used: N7, N10, N13, N15.

## 9. Delta vs today

**Replaced:**
- 360 HP flat → `hp_bands` 340 / 380 / 420 / 460.
- Two phases at 0.66 / 0.33 → five phases at 0.85 / 0.72 / 0.59 / 0.20.
- Hub FLAT heal 4 + block 4 per turn → PERCENT heal 1 / 1.5 / 1.5 % in P1–P3 only.
- Citation (PARASITE) → Notice (TIER_DOWN).
- 6-slice 5-tick wheel → the uneven wheels above.
- Today's Breach (remove one pointer) → "Emergency Override" turns off the heal.

**Kept:**
- The id `civic_core`, the hub id `emergency_powers`, `is_boss = true`, `cycle_reward = 0`.
- A SHIM / OVERFLOW core; `civic_drone` stays as a resource for other fights, no longer used here.
- The 3-pointer and orbit-2 phases are retired, replaced by the 2-needle P4 and the orbit P3 / P5.

**heat_effects:** the boss has no `heat_effects` field today. Keep none; ICE scales it through the band.

## 10. Predicted sim check

No baseline row exists for this boss, so this is an estimate from the wheel.

| Check | Estimate |
|---|---|
| Turns at the reference 18 dpt | ≈ 17.5 (5 phases × 3.5) |
| Turns at bot-best (~25 dpt) | ≈ 12–13 |
| Win % at skill 1.0, fresh | ≈ 35 % |
| Win % at the reference skill, fresh | ≈ 20 % |
| Win % inside a campaign (ICE 0, after attrition) | ≈ 10–15 % |
| Tester pace (3–5 dpt) | no win: enrage runs away |

The reason: P4 at turn ~10.5 is the first enraged phase, and it needs SANDBOX on the right needle. Against the baseline (fresh 25 %, campaign 4–8 %), this sits slightly above it, which fits the stated direction of a puzzle rather than a stall. Today's boss runs about 38 turns fresh.

## 11. Open questions

Q: Should Breach ("Emergency Override") now turn off the boss heal instead of removing a pointer? I chose this because removing a needle halves the damage you deal (a pointer rule) and doubles P4's length.
Q: Does a 0-cost or free card count toward the P2 Ban threshold, and does a replayed card count twice?
Q: Does Cleanse remove all TIER_DOWN stacks on a slice or one? The design assumes all, which makes it a strong P3 card.
Q: Should the phase thresholds scale with the HP band, or stay percent as authored? At the 460 band, P4 is ≈ 179 HP and lasts 5 turns.
Q: In P3 and P5 does the orbit apply after the start-of-turn respin, so the trail is only a one-turn lookahead? The "plan two turns ahead" wording assumes it is.
