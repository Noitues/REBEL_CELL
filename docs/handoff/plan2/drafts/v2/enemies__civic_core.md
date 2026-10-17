<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__civic_core; status ok; tokens in 10516 cache-write 0 cache-read 32585 out 20016; cost $0.114. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **#1 (BLOCKER, sustain cap above 340 HP):** the hub heal is now P1 0.8 %, P2 and P3 1.1 % (PERCENT). The cap is shown at the lowest and highest bands. At 340 it is 15 % / 21 % of reference damage; at 370 it is 16 % / 23 %. The cap holds in every band, and section 3 has the full table.
- **#2 (MAJOR, 3–4 turns per phase):** bands compressed to 340 / 350 / 360 / 370 instead of 340–460. I did not adopt the critic's 400 top band, because my arithmetic gives P4 = 156 / 36 = 4.3 turns and P5 = 4.4 turns there. At 370, P4 is 4.0 and P5 is 4.1. Section 4 now has a turns-per-phase check for every band, with the p90 check at 340 and 370 (N19). Thresholds stay fixed percents (answers my own v1 question).
- **#3 (MAJOR, Warrant hit count):** the base Warrant is capped at 6 hits. Warrant Ledger counts total stacks and raises the cap to 8, so the worst case is 8 × 7 = 56. Hit count is previewed on the pointer chip.
- **#4 (MAJOR, Sunset Clause ambiguous):** the base P5 orbit is 3 ticks per turn. Sunset Clause makes it 5. Its enrage add-on is now fully specified: +25 % at P5 turns 2, 4, 6…, additive with the default steps.
- **#5 (MAJOR, P4 and SANDBOX):** deleted the "cheapest SANDBOX" claim. P4 is now steering-first. SANDBOX is an optional shortcut for classes that carry it (Ghost's Detour slice becomes SANDBOX under R13), and everyone else steers one needle to Null / the 3-tick Notice and absorbs the other with BLOCK or SHIELD. Under R13 the Rigger's Sandbox slice is SHIELD, not SANDBOX, so I did not repeat the critic's "Rigger" example.
- **#6 (NIT, Ban):** Ban = 3 FLAT (6.6 → 7) per card beyond the 2nd. P2 intake is split into a 2-card figure (≈ 3.8) and +7 per extra card, replacing the v1 "8.4" that assumed one card over.
- **#7 (NIT, P5 vs P3):** kept the layouts. P3's orbit is now 2 ticks per turn with two Nulls (a slow, plannable clean line). P5 is orbit 3 with no Null, so the P5 question is "take the cheapest", not "find the clean line". The Notice slices still stamp marks, so "no safe slice" means no slice that is free of cost.
- **#8 (NIT, heal-turn criterion):** replaced "heal turns under 4" with the 30 % cap. The hub heal fires every turn, so the 1-heal-turn criterion does not apply.
- **#9 (NIT, §8):** stated the N6 count-condition extension. Rewrote the N12, N8 and N5 fallbacks: N12 falls back to 6 × 5-tick wheels in all phases, and N8 to a single-stack TIER_DOWN (the status stays, depth is lost).
- **Arithmetic re-check (my own fix):** recomputed all intake figures with exact sub-tick weights (size 3 = 1.0, 4 = 0.75, 5 = 0.8, 6 = 0.667). This moved several v1 numbers (P1 2.3 → 2.1; P3 8.7 → 4.4 / 6.2 / 7.9 by mark count; P5 9.1 → 7.5), and the enrage section was updated to match. Tick sums re-added: all five layouts are 30.
- **Orbit lookahead:** v1's "plan two turns ahead" was wrong because the wheel respins each turn. The trail shows where the pointer sits next turn, so lookahead is exact only if you Freeze. Wording fixed, and this replaces v1's orbit Q.
- **Kept, because the critic marked them strong:** thresholds and floors, persistent marks cashed in at P3 and P5, uneven needles at 0 and 13, the 3-tick Dispersal, and the enrage timing.
- **No designer ruling conflicts.**

---

# civic_core: direct design

*Working title for the fight: "state of emergency". The designer-facing name is THE PANOPTICON; the id stays `civic_core`.*

## 1. Identity & the one question

- **Class and corporation:** HQ boss (Central Server), Halcyon Civic. T4 only, so it appears only in the final HQ netrun, as an L6-pressure fight. It never teaches.
- **Concept:** a city government that declares a new emergency every time it is pressed. Each phase is a different decree that taxes a different habit of yours. The marks it stamps on your wheel in P1 persist (R6) and are cashed in later, so a sloppy early game is paid for in P3 and P5.
- **Signature status:** TIER_DOWN (R8, anti-Firmware). Each stack makes a landing on that slice read one tier lower. One stack costs the Perfect hook. Two stacks make every landing WEAK. Stacks cap at 2 per slice.

| Phase | Name | Question | What shortens the fight |
|---|---|---|---|
| P1 | Watch Order | Where do you land? | Burst the ~51 HP before marks spread; Cleanse or ENCRYPT marked slices. |
| P2 | Assembly Ban | How few cards can you win with? | Play two strong cards, not five weak ones. |
| P3 | Warrants | How clean is your wheel? | A low mark count, because Warrant hits scale with it. Read the pointer trail. |
| P4 | Martial Law | Which of two needles do you steer or SANDBOX? | Burst while there is no heal. Steer one needle off Crackdown and absorb or SANDBOX the other. |
| P5 | Final Verdict | Which landing is cheapest? (No Null.) | Plan the orbit. Take a WEAK edge or a Notice, and have burst saved. |

## 2. Phase plan

**Common to every phase:**
- Authored damage is FLAT, multiplied by the T4 damage factor 2.2 (R2). Both the authored value and the T4 value are shown.
- Sub-tick maps follow R11. Size 3 = G P G (1.0 average output). Size 4 = W G G W, no Perfect (0.75). Size 5 = W G P G W (0.8). Size 6 = W W G G W W (0.667).
- Statuses are kept across every transition (R6). Each moves to the slice covering its old centre tick. `cleanse_on_enter` is NONE everywhere.
- Floors follow R3, at the 340 band. The preview shows "PARKED −N". The last phase has no floor.

**Slice working names** (new files `content/slices/hal_*.tres`):

| Slice | Type | Effect | T4 value |
|---|---|---|---|
| Notice | INFECT | 0 damage. APPLY_STATUS TIER_DOWN ×1 on your slice under the pointer (UNDER_POINTER), applied at any landing quality | n/a |
| Fine | SHIM | 4 FLAT | 8.8 (9) |
| Dispersal | OVERFLOW | 8 FLAT | 17.6 (18) |
| Warrant | SHIM | 3 FLAT per hit. Hits = your slices carrying TIER_DOWN, min 1, **cap 6** (`hits_per_target_status`, N20). Hit count shown on the pointer chip | 6.6 (7) per hit |
| Crackdown | OVERFLOW | 7 FLAT | 15.4 (15) |
| Baton | SHIM | 3 FLAT, `hits` = 2 | 13.2 (13) total |
| Verdict | OVERFLOW | 9 FLAT | 19.8 (20) |
| Null | NULL | nothing | n/a |

### P1 Watch Order (100 → 85 %, floor 289)

| Item | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (sum 30) | Notice 6 · Fine 5 · Notice 4 · Null 7 · Fine 4 · Notice 4 = 30 |
| Hub | Emergency Powers: HEAL 0.8 % max HP per turn (PERCENT) |
| Statuses | TIER_DOWN from Notice. No listeners. |

- **Why it works:** only 9 of the 30 ticks hurt. The real cost is the 14 Notice ticks, which stamp a mark about every other turn (0.47 per turn). The 4-tick Notices have no Perfect, but the mark applies at any quality.
- **Target:** a clean opener that teaches that marks follow your landings.

### P2 Assembly Ban (85 → 72 %, floor 245)

| Item | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Layout (sum 30) | Notice 5 · Fine 6 · Dispersal 3 · Null 6 · Notice 4 · Fine 3 · Null 3 = 30 |
| Hub | HEAL 1.1 % per turn |
| Listener (N6) | ON_CARD_PLAYED: each card you play beyond the 2nd in a turn deals **3 FLAT (6.6 → 7)** to you |

- **Transition:** `wheel_override` and `hub_override` only. P1's marks carry over.
- **Wheel:** Dispersal (3-tick G P G) is the first big hit. Unlike a 5-tick slice it can't be pushed to a WEAK edge by one nudge, so you steer it off the needle or SANDBOX it.
- **The Ban:** the damage is staged with the card and undoes with it. Card hover shows "BAN +7". It is a normal hit (BLOCK and SHIELD apply, no pierce). It is not an end-of-turn resolution, so SANDBOX does not negate it. A 5-card dump costs 21.
- **Why 3 FLAT:** at 7 per card the third card must be worth more than 7 HP of damage or defense, so the choice stays real.

### P3 Warrants (72 → 59 %, floor 201)

| Item | Value |
|---|---|
| Needles | 1, ORBIT **2** ticks per turn. The trail shows where it sits next turn. |
| Layout (sum 30) | Warrant 6 · Notice 4 · Dispersal 3 · Null 5 · Warrant 5 · Fine 4 · Null 3 = 30 |
| Hub | HEAL 1.1 % per turn |
| Listeners | None. The Ban ends here. |

- **Transition:** `wheel_override`, pointer behavior ORBIT, `hub_override` to drop the Ban.
- **Lookahead:** the wheel still respins at turn start, so the trail gives a certain two-turn plan only if you Freeze the wheel (skip its respin). Otherwise it is a one-turn read.
- **Payoff:** this cashes in your P1/P2 marks. With 3 marked slices a Warrant is 3 hits of 7. Cleanse is now a damage-prevention card.

### P4 Martial Law (59 → 20 %, floor 68)

| Item | Value |
|---|---|
| Needles | 2: ticks 0 and 13 (MULTIPLY, uneven per R10) |
| Layout (sum 30) | Crackdown 4 · Baton 3 · Notice 3 · Crackdown 4 · Null 4 · Baton 4 · Crackdown 4 · Null 4 = 30 |
| Hub | Emergency Powers stops healing. No block anywhere. |
| Listeners | None |

- **Transition:** `wheel_override`, MULTIPLY (0, 13), `hub_override` with the heal removed. Marks stay, and the boss has no sustain from here on.
- **Defense (steering first):**
  - Without SANDBOX, steer one needle to Null or the 3-tick Notice and absorb the other with BLOCK or SHIELD.
  - A class that carries SANDBOX (e.g. Ghost's Detour slice) can negate the whole resolution of one needle. That is a shortcut, not a requirement.
- **Needle spacing:** 13 ticks apart means one nudge rarely fixes both needles. You choose which one reads Null or a WEAK edge.
- **Safe slices:** two Nulls (4 each) and one 3-tick Notice (0 damage, one mark).

### P5 Final Verdict (20 → 0 %, no floor)

| Item | Value |
|---|---|
| Needles | 1, ORBIT **3** ticks per turn (back from 2 needles) |
| Layout (sum 30) | Verdict 3 · Warrant 6 · Notice 5 · Crackdown 4 · Fine 4 · Baton 4 · Notice 4 = 30 |
| Hub | None |
| Listeners | None |

- **No Null slice:** every landing does something. The two Notices (9 ticks) deal no damage but stamp a mark, which feeds the Warrant.
- **Transition:** `wheel_override`, pointer ORBIT, `hub_override` cleared.
- **Question:** which cost do you take: a mark, a WEAK edge, or Fine. Your accumulated marks make the Warrant the dangerous slice.

## 3. Sustain and intake

**Sustain: one source, the Emergency Powers hub heal (PERCENT, N1).** Reference damage is 18 per turn; the R2 cap is 30 %, which is 5.4. The hub heal fires every turn, so the cap is the criterion, not a heal-turn count.

| Phase | Heal | At 340 max HP | Share of 18 | At 370 max HP | Share of 18 |
|---|---|---|---|---|---|
| P1 | 0.8 % | 2.72 | 15 % | 2.96 | 16 % |
| P2 | 1.1 % | 3.74 | 21 % | 4.07 | 23 % |
| P3 | 1.1 % | 3.74 | 21 % | 4.07 | 23 % |
| P4 | none | 0 | 0 % | 0 | 0 % |
| P5 | none | 0 | 0 % | 0 | 0 % |

The cap holds in all four bands. PERCENT heal grows with the band, so the highest band (370) is the binding case, and it passes at 23 %.

**Intake per turn** at the reference player, before enrage, steering, SANDBOX and defense. It is the expected value over the boss's ticks at sub-tick weights.

| Phase | Calculation | Intake (T4) |
|---|---|---|
| P1 | Fine 5 (0.8) + Fine 4 (0.75): 1.17 + 0.88 | ≈ 2.1, plus ≈ 0.5 marks per turn |
| P2 | Fine 6 (0.667) + Fine 3 (1.0): 1.17 + 0.88; Dispersal 1.76 | ≈ 3.8 at 2 cards, **+7 per card beyond 2** (≈ 10.8 at 3 cards) |
| P3 | Per marked slice, Warrant gives 1.76; Dispersal 1.76; Fine 0.88 | 4.4 (0 marks, min 1 hit) · 6.2 (2 marks) · 7.9 (3 marks) · 13.2 (6 marks) |
| P4 | Per needle: Crackdown 3 × 4-tick = 4.62; Baton 1.32 + 1.32 = 2.64; ≈ 7.26 per needle, two needles | ≈ 14.5 |
| P5 | Verdict 1.98 + Warrant (2 marks) 1.76 + Crackdown 1.54 + Fine 0.88 + Baton 1.32 | ≈ 7.5 (2 marks), 8.4 (3 marks) |

Intake is above 0 in every phase. P1's 2.1 is low on purpose and only bites through the marks.

## 4. HP by tier (hp_bands, R2)

**Budget arithmetic** at the 340 band: HP per phase = (18 × needles the player's hits land on − sustain per turn) × 3.5.

| Phase | Needles | Sustain | Budget |
|---|---|---|---|
| P1 | 1 | 2.72 | (18 − 2.72) × 3.5 = 53.5 |
| P2 | 1 | 3.74 | (18 − 3.74) × 3.5 = 49.9 |
| P3 | 1 | 3.74 | (18 − 3.74) × 3.5 = 49.9 |
| P4 | 2 | 0 | 36 × 3.5 = 126 |
| P5 | 1 | 0 | 18 × 3.5 = 63 |
| **Sum** | | | **342** (band 340, slack −2) |

Fixed thresholds 0.85 / 0.72 / 0.59 / 0.20. Phase HP and turns at reference damage (turns = phase HP ÷ net damage per turn):

| Ceiling (ICE strength) | Max HP | P1 / P2 / P3 / P4 / P5 HP | Turns P1 / P2 / P3 / P4 / P5 |
|---|---|---|---|
| ≤ 1.00 | 340 | 51 / 44.2 / 44.2 / 132.6 / 68 | 3.3 / 3.1 / 3.1 / 3.7 / 3.8 |
| ≤ 1.15 | 350 | 52.5 / 45.5 / 45.5 / 136.5 / 70 | 3.5 / 3.2 / 3.2 / 3.8 / 3.9 |
| ≤ 1.30 | 360 | 54 / 46.8 / 46.8 / 140.4 / 72 | 3.6 / 3.3 / 3.3 / 3.9 / 4.0 |
| > 1.30 | 370 | 55.5 / 48.1 / 48.1 / 144.3 / 74 | 3.7 / 3.5 / 3.5 / 4.0 / 4.1 |

- **Floors at 340:** ceil(340 × 0.85) = 289, 245, 201, 68.
- **Why 370 is the top:** every phase stays at or very near 4 turns. A 400 top band would push P4 to 4.3 and P5 to 4.4.
- **Check:** p90 of turns per phase is checked at 340 and 370 (N19). Higher ICE zones still get harder, because BOSS_STRENGTH_PCT also raises boss damage.
- No T1–T3 entries: this boss is T4 only. PERCENT heal reads max HP and is never scaled again (R2).

## 5. Enrage

**Default (R4):** start turn 10, every 5 turns, +25 % additive, damage only. Kept:
- The reference player reaches P4 around turn 10 (3.3 + 3.1 + 3.1 = 9.5 turns), so step 1 lands at the burst phase (14.5 → 18.1 per turn).
- P5 starts around turn 13. Step 2 (×1.5, turn 15) hits the finish: 7.5 → 11.3 per turn.
- Heal is unaffected by enrage, so it cannot be a stall tool.

**Authored add-on (Sunset Clause only, §6):** in P5, +25 % additive at P5 turns 2, 4, 6…, on top of the default steps. With Sunset Clause, a P5 starting at turn 13 reaches ×1.5 at turn 14, ×1.75 at turn 15 and ×2.0 at turn 16 (≈ 7.5 → 15 per turn).

## 6. Buffs and counter Exploits

A Grid draws 5 of these 8 (`exploits_per_grid`), and `min_exploits_for_breach = 3` still holds.

| Buff (strong) | Effect | Counter Exploit turns off | Signature? |
|---|---|---|---|
| **Emergency Powers** | The P1–P3 hub heal (0.8 / 1.1 / 1.1 %) | All boss heal (today's Breach, "Emergency Override") | **Yes** |
| **Sunset Clause** | P5: pointer orbit 3 → 5, plus extra enrage steps (+25 % every 2 turns from P5 turn 2, additive) | Default P5: orbit 3, no extra steps | **Yes** |
| Closed Session | Phases and next layouts hidden | Reveals them (today's Intel) | no |
| Warrant Ledger | Warrant hits = total TIER_DOWN stacks, **cap raised to 8** (worst case 8 × 7 = 56) | Back to marked-slice count, cap 6 (flavored as the Virus "Open Data Leak") | no |
| Watchlist | Notice applies ×2 stacks | ×1 | no |
| Tight Ban | The Ban threshold is 1 card, not 2 | Back to 2 | no |
| Rapid Response | Crackdown 9 FLAT (19.8 at T4), Dispersal 10 (22) | Base values | no |
| Sealed Docket | Boss wheel has resistance 2 (absorbs nudges; blocks Flip and Respin) | The resistance | no |

**Why these two are signatures:**
- Emergency Powers defines the early game. With it off, P1–P3 heal about 9 + 11.6 + 11.6 ≈ 32 HP less in total, about 1.8 turns shorter.
- Sunset Clause defines the late game. It is the only buff that changes the clock (enrage and pointer speed), not the numbers.

## 7. Counterplay

**Per phase, a good player:**
- **P1:** lands on Null or a WEAK edge, spreads landings across slices, and keeps ENCRYPTED or Cleanse ready for two marks. The aim is to burst ~51 HP in 3 turns and enter P2 with zero or one mark.
- **P2:** plays two high-value cards and passes. A free nudge is not a card, so it is exempt. SANDBOX the Dispersal turn if you carry it.
- **P3:** Cleanse is the best damage-prevention card. Read the pointer trail, and Freeze if you want a certain two-turn plan. Spend a nudge to push a Warrant needle onto its WEAK edge.
- **P4:** steer one needle onto Null or the 3-tick Notice and absorb the other with BLOCK or SHIELD. If you carry SANDBOX, spend it on the Crackdown needle. Finish ~133 HP before step 2 at turn 15. There is no heal, so burst pays.
- **P5:** compare costs: a Notice mark, a WEAK edge, or Fine. Keep marks low, because the Warrant is the slice you can shrink. Use saved burst for the last ~68 HP.

**A weak player:**
- dumps their hand in P2 (a 5-card dump costs 21);
- ignores P1 marks and meets P3 with 5–6 marked slices, where each Warrant is 5–6 hits of 7;
- tries to dodge both P4 needles at once and eats both;
- reaches P5 after step 2 with no burst, and at ×1.5 intake loses.

## 8. Systems needed

| N# | Use | Data-only fallback |
|---|---|---|
| N1 | PERCENT heal; FLAT damage × tier factor | none; the hub heal needs it |
| N2 | `hp_bands`, damage table | flat 355 HP (loses ICE banding) |
| N3 | Five phases, parking, status keep and remap | none |
| N4 | Enrage default | none |
| N5 | 8 buffs, Exploit counters, `exploits_per_grid` | map today's Intel / Breach / Virus gates to Closed Session / Emergency Powers / Warrant Ledger; the other five buffs are dropped |
| N6 | P2 Ban: ON_CARD_PLAYED needs a small extension, a cards-this-turn count condition | a Ban slice on the wheel; loses the card-count question |
| N8 | ×N TIER_DOWN stacks (cap 2) | single-stack TIER_DOWN (cap 1): the status stays, the "two stacks = all WEAK" depth is lost, and Warrant Ledger loses its point |
| N9 | TIER_DOWN status rules | none; the signature status needs it |
| N11 | Needles at 0 and 13 | use 0 and 15 |
| N12 | Variable slice sizes, 7–8 slices per wheel | rewrite every phase to 6 × 5-tick slices (P4's 8 slices become 6; the 3- and 4-tick narrow windows are lost) |
| N14 | SANDBOX negates a whole resolution | optional in P4 (steering-first); no fallback needed |
| N19 | Turns-per-phase metric | none |
| N20 | `hits`, `hits_per_target_status` (capped) | Warrant becomes a flat 3 hits |

Not used: N7, N10, N13, N15.

## 9. Delta vs today

**Replaced:**
- 360 HP flat → `hp_bands` 340 / 350 / 360 / 370.
- Two phases at 0.66 / 0.33 → five phases at 0.85 / 0.72 / 0.59 / 0.20.
- Hub FLAT heal 4 + block 4 per turn → PERCENT heal 0.8 / 1.1 / 1.1 % in P1–P3 only.
- Citation (PARASITE) → Notice (TIER_DOWN).
- 6-slice 5-tick wheel → the uneven wheels above.
- Today's Breach (remove one pointer) → "Emergency Override" turns off the heal. Reason: removing a needle halves your damage under the pointer rule and doubles P4's length.

**Kept:**
- The id `civic_core`, the hub id `emergency_powers`, `is_boss = true`, `cycle_reward = 0`.
- A SHIM / OVERFLOW core. `civic_drone` stays as a resource for other fights and is no longer used here.
- The 3-pointer and orbit-2 phases are retired, replaced by the 2-needle P4 and the orbit P3 / P5.

**heat_effects:** the boss has no `heat_effects` field today. Keep none; ICE scales it through the band.

## 10. Predicted sim check

No baseline row exists for this boss, so this is an estimate from the wheel.

| Check | Estimate |
|---|---|
| Turns at the reference 18 dpt | ≈ 17 (3.3 + 3.1 + 3.1 + 3.7 + 3.8) |
| Turns at bot-best (~25 dpt) | ≈ 13–14 |
| Win % at skill 1.0, fresh | ≈ 30 % |
| Win % at the reference skill, fresh | ≈ 18 % |
| Win % inside a campaign (ICE 0, after attrition) | ≈ 10–12 % |
| Tester pace (3–5 dpt) | no win: enrage runs away |

The reason: P4 starts about turn 10, the first enraged phase, and it needs steering of both needles (about 14.5 gross, 18.1 enraged). Against the baseline (fresh 25 %, campaign 4–8 %), this sits slightly above it, consistent with the stated direction of a puzzle rather than a stall. Today's boss runs about 38 turns fresh; this one should land at 13–17.

## 11. Open questions

Q: Should phase thresholds stay fixed percents with a compressed 340–370 band (as drafted), or should HP vary more by ICE zone with per-band thresholds so every phase stays at 3–4 turns?
Q: Does Cleanse remove all TIER_DOWN stacks on a slice, or one? The design assumes all, which makes Cleanse a top card in P3.
Q: Does a 0-cost card count toward the P2 Ban threshold, and does a replayed card count twice? Is the Ban hit blockable (drafted: yes) rather than unblockable?
Q: Is the orbit trail useful enough given the start-of-turn respin, or should P3 and P5 pointers orbit before the respin so the reading is predictable?
Q: Is a ≈ 30 % skill-1.0 fresh win rate right for a first-contact HQ boss, or should it be closer to the 25 % baseline?
