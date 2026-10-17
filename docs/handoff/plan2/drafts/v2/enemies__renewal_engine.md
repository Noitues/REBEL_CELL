<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__renewal_engine; status ok; tokens in 11074 cache-write 0 cache-read 32585 out 28932; cost $0.159. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, phase HP and turns misaligned, P4 over 4 turns at >1.30):**
  - I re-derived per-phase HP for every band (§4). P4 can't hold more than about 104 HP at 26 net damage per turn without passing 4 turns. A 4-phase boss therefore tops out near 315 HP, so the top three bands use 5 phases.
  - I added a 5th phase, P5 Code Blue II, for the ≥330 bands. `hp_bands` rows now carry a phase list and thresholds: 4 phases at 300, 5 phases at 330 / 360 / 400.
  - I kept the V2 bands (300 / 330 / 360 / 400). The critic's fix of "a 5th phase with 3 needles" was not adopted: a third needle would change player damage and intake across the whole phase. P5 instead removes the Null breathers, so its question is genuinely new.
  - The 300 band's thresholds are now 0.82 / 0.66 / 0.33, which gives clean 54 / 48 / 99 / 99.
  - Every band lists HP, floors and turns per phase, all within 3-4 (P4 at 330 is 2.9, flagged).
  - I added a sustain-cap fix: the heal % now varies by band so the absolute heal stays 3 then 5 (v1's 1.5 % would be 6 at 400 HP, over the cap).
- **Issue 2 (BLOCKER, Second Opinion counter, fallback violates R7):**
  - The primary counter is kept as inert needle 2 (`inert_pointers`, still NEW). It takes your hits and resolves nothing for the boss, so fight length is preserved.
  - The critic's fallback ("set needle-2 slices to NULL") doesn't work: both needles read the same wheel. I replaced it with an honest data-only fallback. With the counter, the boss has one needle and loads an alternate HP row sized for one needle, so it ends up easier and shorter, never longer (§4, §8).
- **Issue 3 (MAJOR, Code Blue changed the ruling):**
  - Reverted to the ruling: every boss hit that reaches you and isn't SANDBOXed corrupts one of your slices.
  - It is capped at 2 per turn, which equals the needle count, so it also stops the 5-slice spread (§2 P4). It is a listener on N6 ON_HIT_DEALT. The fallback with slice riders gives the same result with 2 needles.
- **Issue 4 (MAJOR, RNG on the Immunization rider):** now names the combat RNG stream (the one today's Dose uses), a checkpointed random event, with the preview showing the odds (§2 P1).
- **Issue 5 (MAJOR, Barrier 8 `tick_quality`):** N12 row added to §8 for the authored override.
- **Issue 6 (MAJOR, Sterile Field `cleanse_on_enter`):**
  - Relabeled to OWN, meaning statuses on the boss's own slices (those the player applied).
  - I rejected the critic's BOTH: it would also strip your CORRUPTED slices, which is a gift to the player, not a strong buff.
  - The player-side cleanse remains available as authoring option PLAYER, unused here.
- **Issue 7 (MAJOR, Metabolism as a weak buff):**
  - Dropped from the buff list and kept as the base hub rule (heal off cannot be a buff).
  - The pool is now 7 buffs / 7 Exploits.
  - Triage Reserve raised from 3 % to 5 % (V2 value). Chart Hidden is marked as an info buff.
  - Signatures: Second Opinion, Compliance Lock, Antibodies, Sterile Field.
- **Issue 8 (NIT, win %):** the §10 win rates now show their reasoning against the baseline and are labeled hypotheses.
- **Issue 9 (NIT, enrage timing):** timings are recomputed per band from the phase turns in §4 (the "P4 starts at about turn 10.5" claim was only valid for a 3.5-turn P3).
- **Own correction (arithmetic):** v1's "full fight ≈ 55 HP net" was wrong. Its own factors give 3.5·1.5 + 3.5·3.5 + 3.5·7 + 4·9 ≈ 78. I lowered the net targets so the 4-phase fight costs about 60 HP (§3).

# renewal_engine: direct design

(Auto-Renew, the Genome Core fight of CONTENT_DESIGN_V2 §2; the id stays.)

## 1. Identity & the one question

- **Class:** HQ boss, Solace Central Server, T4 only. It is the fight after the final Rack, so there is no L1-2 or L5-6 placement.
- **Concept:** a doctor treating a progressing disease, and the disease is you. Your CORRUPTED slices are its damage multiplier and your RAM tax.
- **Target fight:** 14.8 turns (300 band, 4 phases), up to 18.9 (400 band, 5 phases). Both are inside 12-20.

| Phase | Question | Answer that shortens it |
|---|---|---|
| P1 Screening | Do I spend the free nudge to deny corruption, or accept it and burst? | Steer its needle to Null or a WEAK Immunization edge, then burst. Barrier turns are wasted. |
| P2 Treatment | Can I deny the Medicine Perfect and keep my CORRUPTED count low? | A 1-tick nudge turns ×4 into ×1. SANDBOX the landed Medicine or a big IV. Cleanse before the IVs scale. |
| P3 Intensive Care | Which of two uneven needles reads the dangerous slice? | Choose the landing so a Perfect Medicine always sits beside an IV. Your hits land twice, so race. |
| P4 Code Blue | How do I stop the corruption spiral when nothing can be blocked? | Land on an already-corrupted slice (sacrificial), SANDBOX the Adrenaline, finish before enrage step 2. |
| P5 Code Blue II (≥330 bands only) | Can I afford a turn with no breather? | Every turn both needles fire; the only free turn is the one you SANDBOX or cleanse. |

## 2. Phase plan

**Common to all phases:**
- Flat enemy amounts are base values × 2.2 at T4 (R2). Rounded T4 values are in parentheses.
- Heal is PERCENT of the boss's own max HP, never rescaled.
- Floors are `ceil(max HP × threshold)` and the excess is lost (R3). Per-band thresholds are in §4.
- Statuses survive phase changes (R6). `cleanse_on_enter` = NONE, except under the Sterile Field buff (OWN).
- Layouts are listed clockwise from tick 0 at rotation 0. Quality maps follow R11.

### P1 Screening

| Field | Value |
|---|---|
| Needles | 1, at tick 0 |
| Hub | Metabolism: heal PERCENT, absolute ≈ 3 per turn (1 % at 300, 0.75 % at 400) |
| Layout | Barrier 6 · Immun 4 · Immun 4 · Barrier 6 · Immun 4 · Null 6 (= 30) |
| Barrier | BLOCK 6 FLAT (13). Map W W G G W W, never Perfect |
| Immunization | SHIM 5 FLAT (11); map W G G W, avg ×0.75. Rider: CORRUPTED FLAT 1 on a random non-NULL slice of yours. It is drawn from the combat RNG stream (the same one today's Dose uses) as a checkpointed random event, so a reload cannot reroll. The preview shows the odds (1/n over your uncorrupted non-NULL slices). |
| Statuses and listeners | None |

### P2 Treatment

| Field | Value |
|---|---|
| Needles | 1, at tick 0 |
| Hub | Metabolism: absolute ≈ 5 per turn (1.5 % at 300) |
| Layout | Barrier 8 · IV 4 · Medicine 3 · Null 4 · IV 4 · Immun 4 · Medicine 3 (= 30) |
| Barrier | BLOCK 8 FLAT (18), authored `tick_quality` W W G G G G W W (no Perfect; size 8 is not in R11) |
| IV | SHIM 2 FLAT (4) per hit, `hits_per_target_status` = your CORRUPTED slices (min 1), separate hits. Map W G G W |
| Medicine | OVERFLOW 5 FLAT (11); Perfect ×4 (44). Map G P G (1 tick of 3) |
| Immunization | As P1, kept as a bridge |

- Separate IV hits matter: BLOCK 18 eats about 4 hits, and SANDBOX negates all of them.

### P3 Intensive Care

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 14 |
| Hub | Metabolism (≈ 5 per turn) |
| Layout | Barrier 5 · IV 4 · Med 3 · IV 4 · Immun 4 · Med 3 · IV 4 · Null 3 (= 30) |
| Barrier | BLOCK 6 FLAT (13) |
| Other slices | As P2 |

**Why 14 works (checked against the layout).**
- Slice ranges are Barrier 0-4, IV 5-8, Med 9-11 (centre 10), IV 12-15, Immun 16-19, Med 20-22 (centre 21), IV 23-26, Null 27-29.
- The Medicine centres are 11 apart and the needles 14 apart, so they are never both Perfect.
- Needle A on tick 10 puts needle B on tick 24 (IV). Needle B on tick 21 puts A on tick 7 (IV).
- A Perfect Medicine therefore always arrives with an IV, never with a second Perfect or a free Null. This is the uneven-needle tool of R10.

### P4 Code Blue

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 14 |
| Hub | Metabolism (≈ 5 per turn) + **Code Blue** |
| Layout | IV 4 · Adren 3 · IV 4 · Null 4 · Adren 3 · IV 4 · Adren 3 · Null 5 (= 30) |
| Defense | None |
| IV | As P2 |
| Adrenaline | OVERFLOW 5 FLAT (11), Perfect ×4 (44), **pierce** |

- **Code Blue (hub rule, listener, N6 ON_HIT_DEALT):** every boss hit that reaches you and is not SANDBOXed corrupts one of your slices. BLOCK and SHIELD don't stop it.
  - **Cap: 2 per turn**, equal to the needle count.
  - Needle 1's hits corrupt the slice under your pointer. Needle 2's hits corrupt the next clockwise non-NULL, uncorrupted slice. Both are deterministic, with no RNG and a normal preview.
  - A hit onto an already-corrupted slice is not retargeted (that is the sacrificial slice).
  - Adrenaline centres are at 5, 16 and 23, so needles 14 apart are never both Perfect.
  - When needle A is in ticks 11-14, B is in 25-28 and both are on Null. That is about a 13 % breather turn, which is fine.

### P5 Code Blue II (330 / 360 / 400 bands only)

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 14 (unchanged) |
| Hub | Metabolism + Code Blue (unchanged) |
| Layout | IV 4 · Adren 3 · IV 4 · IV 4 · Adren 3 · IV 4 · Adren 3 · IV 5 (= 30) |

- Ranges: IV 0-3, Adren 4-6 (centre 5), IV 7-10, IV 11-14, Adren 15-17 (centre 16), IV 18-21, Adren 22-24 (centre 23), IV 25-29.
- Both Null slices become IV, so there are no breather turns.
- Pairing at offset 14: A on Adren 5 puts B on tick 19 (IV). A on 16 puts B on tick 0 (IV). A on 23 puts B on tick 7 (IV). The reverse also lands on IV, so there is never a double Adrenaline Perfect.

### Transitions
- Each transition parks damage at the floor and ends the resolve. The new layout loads (`wheel_override` + `hub_override`) and takes effect at the next start-of-turn respin. Statuses stay (R6 remap).
- A phase line plays. The new layout is revealed on entry only under Chart Hidden.
- P1 → P2: heal up, Barrier fewer and bigger, IV and Medicine arrive.
- P2 → P3: MULTIPLY to ticks 0 / 14.
- P3 → P4: all defense dropped, Code Blue on.
- P4 → P5: Null slices become IV.

## 3. Sustain and intake

**Sustain: one source, the hub heal.** The cap is 30 % of reference damage per turn.

| Phase | Reference dmg/turn | Cap | Heal | OK? |
|---|---|---|---|---|
| P1 | 18 | 5.4 | 3 | yes |
| P2 | 18 | 5.4 | 5 | yes |
| P3-P5 | ≈ 31 (2 needles × 18 × 0.85) | 9.3 | 5 | yes |

- The heal % is authored per band so the absolute value stays at 3 then 5. At 400 HP a flat 1.5 % would be 6 and break the cap.
- Heal uses nearest rounding: 4.5 → 5 at 300, 5.04 → 5 at 360.
- **Triage Reserve** (buff, shield 5 % max HP, 15 at 300) is ≈ 4.3 per turn on top. Metabolism + Triage Reserve ≈ 9 in P2, over the cap, by design: it is an uncountered-buff cost, and the HP budget assumes it is off.

**Intake per turn at the reference player.**
- **Assumed corrupted count:** 2 in P2, 3 in P3, 4 in P4, 5 in P5.
- **Raw intake:** unsteered, unblocked, T4 values.
- **Net target:** after block, steer and SANDBOX (a mid-to-good player).

| Phase | Raw per turn | Net target |
|---|---|---|
| P1 | 3.3 | 1.5 |
| P2 | 7.3 | 2.5 |
| P3 | ≈ 19 | 5.5 |
| P4 | ≈ 24 | 6.5 |
| P5 | ≈ 31 (Adren 7.3 + IV 8.4 per needle) | 7 |

**Fight cost (net HP).**
- **300 band:** 3.6·1.5 + 3.7·2.5 + 3.7·5.5 + 3.8·6.5 ≈ 5.4 + 9.3 + 20.4 + 24.7 ≈ 60. That is about one full operative bar, so a good player ends low and a weak one dies in P3-P4.
- **360 band:** ≈ 5.4 + 8.8 + 20.9 + 19.5 + 21.7 ≈ 76, deliberately worse at high ICE (see Q).
- Intake is above 0 in every phase.

## 4. HP by tier

T4 only. `hp_bands` rows carry total HP, the phase count, thresholds and the heal %.

**Phase-budget arithmetic** at T4, with reference 18 dmg/turn and 3.5 turns per phase.
- **Net dpt per phase:**
  - P1: 18 − 3 = 15.
  - P2: 18 − 5 = 13.
  - P3 (2 needles, 8/30 ticks on Barrier or Null ≈ ×1.75): 31.5 − 5 = 26.5.
  - P4 / P5 (9/30 Null, ≈ ×1.7): 30.6 − 5 ≈ 26.
- **Why a 4-phase boss caps near 315 HP:**
  - At 4.0 turns each, P4 holds about 104 HP.
  - P1 + P2 + P3 + P4 at 4 turns ≈ 60 + 52 + 106 + 104 = 322.
  - A 5-phase boss needs at least 3 turns per phase, ≈ 45 + 39 + 80 + 78 + 78 = 320.
  - So 300 fits 4 phases and 330 and above fit 5.

| ICE zone ceiling | HP | Phases | Thresholds | Floors | HP per phase | Turns per phase | Total |
|---|---|---|---|---|---|---|---|
| ≤ 1.00 | 300 | 4 | 0.82 / 0.66 / 0.33 | 246 / 198 / 99 | 54 / 48 / 99 / 99 | 3.6 / 3.7 / 3.7 / 3.8 | 14.8 |
| ≤ 1.15 | 330 | 5 | 0.86 / 0.73 / 0.47 / 0.24 | 284 / 241 / 156 / 80 | 46 / 43 / 85 / 76 / 80 | 3.1 / 3.3 / 3.2 / 2.9 / 3.1 | 15.6 |
| ≤ 1.30 | 360 | 5 | 0.85 / 0.72 / 0.44 / 0.22 | 306 / 260 / 159 / 80 | 54 / 46 / 101 / 79 / 80 | 3.6 / 3.5 / 3.8 / 3.0 / 3.1 | 17.0 |
| > 1.30 | 400 | 5 | 0.85 / 0.72 / 0.46 / 0.23 | 340 / 288 / 184 / 92 | 60 / 52 / 104 / 92 / 92 | 4.0 / 4.0 / 3.9 / 3.5 / 3.5 | 18.9 |

- **Sums re-added:**
  - 300: 54 + 48 + 99 + 99 = 300.
  - 330: 46 + 43 + 85 + 76 + 80 = 330.
  - 360: 54 + 46 + 101 + 79 + 80 = 360.
  - 400: 60 + 52 + 104 + 92 + 92 = 400.
- P4 at 330 is 2.9 turns, rounded to "about 3". It is the only phase under 3 and is accepted.
- **Data-only alternate row (Second Opinion countered, one needle in P3-P5):**
  - One-needle phases are sized (18 − 5) × 3.5 ≈ 45 each.
  - The 300 row becomes 54 / 48 / 46 / 46 = 194 with thresholds 0.72 / 0.47 / 0.24.
  - The 330 / 360 / 400 rows scale the same way.

## 5. Enrage

**Default** (start turn 10, every 5, +25 % damage per step, additive; damage only).
- **300 band:** P3 ends at turn ≈ 11.0 and P4 runs turns 11-14.8, so step 1 (×1.25) lands right at the end of P3 and P4 plays under it.
  - Step 2 (turn 15) is reached only by a slow player.
- **360 band:** P5 starts at turn ≈ 13.9, so step 2 (×1.5) at turn 15 hits the climax.
- No authored trigger: Code Blue's spreading corruption is already a built-in clock, and a second clock would stack punishment.

## 6. Buffs and counter Exploits

A route draws 5 of the 7-Exploit Solace pool, so about 71 % of buffs are counterable per run.
- Today's Intel / Breach / Virus are the first three of the pool. Four new `ExploitData` are needed (one per new buff). Each Exploit has its own building (D5).
- `min_exploits_for_breach = 3` stays.
- Metabolism is no longer a buff; it is the base hub rule.

| Buff | Effect | Counter Exploit turns off | Notes |
|---|---|---|---|
| **Second Opinion** (signature) | Needle 2 acts in P3-P5 | Needle 2 becomes **inert**: it resolves nothing for the boss but still takes your hits | Today's Breach, remapped |
| **Compliance Lock** (signature) | Hub resistance 2: a 1-tick nudge is fully absorbed; Flip and Respin blocked | Resistance 0 | P2 Medicine denial costs 3 RAM |
| **Antibodies** (signature) | Immunization corrupts FLAT 2 | Back to 1 | Today's Virus, remapped |
| **Sterile Field** (signature) | `cleanse_on_enter` = OWN: strips statuses on the boss's own slices at each phase change (your OUTPUT_DOWN etc.) | Statuses stick | OWN, not BOTH, because BOTH would also cleanse your CORRUPTED |
| Booster | IV minimum 2 hits | Minimum 1 | |
| Triage Reserve | SHIELD = 5 % max HP at each phase start | No shield | |
| Chart Hidden (info) | Phases and next layouts hidden | Reveals them | Today's Intel; mild by design |

- **Second Opinion counter:** the inert needle keeps both your damage and the HP budget intact, so the counter shortens the boss's threat, not your fight. Without the new field the fallback is the alternate one-needle HP row in §4, never a longer fight (R7).
- **Virus remap:** with R9, CORRUPTED no longer deals damage, so "boss starts corrupted" retires and Virus counters Antibodies.

## 7. Counterplay

**P1**
- Good: use the free nudge to move its needle onto Null or an Immunization WEAK edge, then burst. Keep your CORRUPTED count at 0-1 (Cleanse, Encrypt).
- Weak: feeds it Barrier turns (each ≈ 0.7 of a reference turn) and lets corruption stack for free.

**P2**
- Good: deny the Medicine Perfect (a 1-tick nudge turns ×4 into ×1). SANDBOX the landed Medicine, SHIELD the IV chip. Corrupted slices cost 2× RAM, so cleansing is also economy.
- Weak: leaves 3+ corrupted slices into IV, so IV turns hit 3+ times and cost double RAM.

**P3**
- Good: choose which needle reads which slice. The 14-tick offset ties a Perfect Medicine to an IV, so SANDBOX that turn. Flip works if Compliance Lock is off. Race, because your hits land twice.
- Weak: nudges one needle only and eats a Perfect ×4 plus an IV.

**P4**
- Good: place the pointer on an already-corrupted slice so needle 1's corruption is wasted. SANDBOX the Adrenaline (pierce ignores BLOCK and SHIELD). Cleanse during Null turns. Finish before step 2.
- Weak: plays defense that does not exist, takes 2 new corruptions every turn (IV ×5 hits, RAM ×2 on everything), and dies in the enrage step.

**P5 (≥330 bands)**
- Good: SANDBOX the Adrenaline turn and spend a card turn on Cleanse; the sacrificial slice still holds the line.
- Weak: expects a Null breather that no longer exists.

## 8. Systems needed

| System | Needed for | Data-only fallback |
|---|---|---|
| N1 amount modes | PERCENT heal, FLAT × tier | None |
| N2 tier tables / `hp_bands` (+ per-band phase list, thresholds, heal %, alternate one-needle row) | Band HP | Ship the 300 band as a 4-phase row only |
| N3 phases, parking, status keep, `cleanse_on_enter` | Core to the fight | None |
| N4 enrage | Default enrage | None |
| N5 buffs and Exploits | §6 | Ship phases without buffs (drops the route-subset layer) |
| N6 listener (ON_HIT_DEALT) | Code Blue | Slice riders (corrupt on resolved IV / Adrenaline); same result with 2 needles |
| N9 corruption as RAM ×2 | The fight's economy | Without it the fight is just IV damage |
| N11 any-tick pointers | Needles at 0 / 14 | P3-P5 at 0 / 15, which loses the Perfect-pairing puzzle |
| N12 variable sizes + sub-tick map + `tick_quality` override | Narrow Medicine Perfect; Barrier 8 override (W W G G G G W W) | Not recommended |
| N14 defense trio | SANDBOX negates the whole resolution | Today's DETOUR cancels only one SHIM or OVERFLOW |
| N20 slice riders (`hits_per_target_status`, `perfect_multiplier`, `pierce`) | IV, Medicine, Adrenaline | IV as 3 fixed small hits; Medicine and Adrenaline as plain OVERFLOW (no ×4) |
| NEW: `inert_pointers` (phase-data field) | Second Opinion counter | Alternate one-needle HP row (§4) |
| N19 sim metrics | Turns per phase, parked damage | Not blocking |

## 9. Delta vs today

- **HP:** 360 flat (1,475 with tier factor) → `hp_bands` 300 / 330 / 360 / 400.
- **Phases:** today 2 (66 % Multiply, 33 % Orbit + 2 collections drones + `wheel_emergency`) → 4 to 5 `BossPhaseData` entries.
- **Retired:** Orbit, collections-drone spawns, the 10-flat hub heal (percent now).
- **Kept:** `id`, `corporation_id`, `is_boss`, `cycle_reward = 100`, Dose's random-non-NULL pattern (Immunization).
- **New slice files:** `gc_barrier_5/6/8`, `gc_immunization`, `gc_iv`, `gc_medicine`, `gc_adrenaline`.
- **Exploits:** Intel → Chart Hidden counter, Breach → Second Opinion counter, Virus → Antibodies counter, plus 4 new.
- **`heat_effects`:** none on today's file; none added.

## 10. Predicted sim check

There is no measured row for this boss, so these are estimates reasoned from the old boss row (fresh 25 % at 38 turns, campaign 4-8 % at 41-50 turns).

| Case | Mean turns | Win % | Why |
|---|---|---|---|
| Fresh, ICE 0 | 14-16 | 30-40 | The fight is under half the old length and enrage is barely reached. Parking caps burst skips, so the bot's 16-35 dpt can't skip a phase. Hypothesis, not data. |
| Campaign (HP attrition) | 15-18 | 12-20 | Net intake ≈ 60 HP of a 45-60 bar, so any carried deficit decides it. Above the 4-8 % baseline because the fight is shorter, below fresh because of the deficit. |
| Weak player (3-5 dpt) | 25+ | ≈ 0 | Enrage steps 10 and 15. |
| 400 band, fresh | 18-19 | 15-25 | Net cost ≈ 76 HP. |

Pass criteria:
- 3-4 turns per phase (N19), with P4 at 330 allowed down to 2.9.
- Intake above 0 in every phase.
- At most 1 heal turn per phase.
- Sustain inside the cap without Triage Reserve.

## 11. Open questions

- Q: Is a net intake of about 60 HP (one full bar) at the 300 band, and about 76 at the 360 band, the intended lethality, or should the Q12 win-rate target lower it?
- Q: Code Blue sends needle 2's corruption to the next clockwise uncorrupted slice. Is that the right second target, or should both go under the pointer (max 1 per turn)?
- Q: Do we accept `inert_pointers` as a small N11 extension, or ship only the one-needle alternate HP row (a weaker counter, no new field)?
- Q: Should a phase count that varies by band (4 versus 5) be authored per `hp_bands` row, or should every band use 5 phases and the 300 band merge its P4 and P5?
- Q: Is Chart Hidden (an info-only buff) acceptable as one of the 7, or should it be replaced by a mechanical buff?
