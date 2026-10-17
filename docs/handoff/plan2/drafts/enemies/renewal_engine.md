<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__renewal_engine; status ok; tokens in 18978 cache-write 0 cache-read 32007 out 25617; cost $0.150. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# renewal_engine: direct design

(Auto-Renew, the Genome Core fight of CONTENT_DESIGN_V2 §2; the id stays.)

## 1. Identity & the one question

- **Class:** HQ boss, Solace Central Server, T4 only. It is the fight after the final Rack, so there is no L1-2 or L5-6 placement.
- **Concept:** a doctor treating a progressing disease, and the disease is you. Your CORRUPTED slices are its damage multiplier and your RAM tax.
- **Target fight:** 4 phases × 3.5-4 turns ≈ 14-16 turns at the reference player (limit 12-20).

| Phase | Question | Answer that shortens it |
|---|---|---|
| P1 Screening | Do I spend the free nudge to deny corruption, or accept it and burst? | Steer its needle to Null or a WEAK Immunization edge, then burst. Barrier turns are wasted turns. |
| P2 Treatment | Can I deny the Medicine Perfect and keep my CORRUPTED count low? | A 1-tick nudge turns ×4 into ×1. SANDBOX the landed Medicine or a big IV. Cleanse before the IVs scale. |
| P3 Intensive Care | Which of two uneven needles do I let read the dangerous slice? | Choose the landing so a Perfect Medicine always sits beside an IV. Your hits land twice, so race. |
| P4 Code Blue | How do I stop the corruption spiral when nothing can be blocked? | Land your pointer on an already-corrupted slice (sacrificial). SANDBOX the Adrenaline. Finish before the turn-15 enrage step. |

## 2. Phase plan

**Common to all phases:**
- All flat enemy amounts below are base values, multiplied by the tier factor 2.2 at T4 (R2). Rounded T4 values are in parentheses.
- Heal is PERCENT of the boss's own max HP and never scaled again.
- Phase floors at T4/300 HP: 246 / 201 / 105 (R3). Damage parks there and the excess is lost.
- Statuses stay across phases (R6). `cleanse_on_enter` = NONE, except under the Sterile Field buff (OWN).
- Layouts are listed clockwise from tick 0 at rotation 0.
- Quality maps follow R11. Size 8 is not in the R11 table, so Barrier 8 uses an authored `tick_quality` of W W G G G G W W.

### P1 Screening (100 → 82 %, 54 HP at T4/300)

| Field | Value |
|---|---|
| Needles | 1, at tick 0 |
| Hub | Metabolism: heal 1 % max HP per turn |
| Layout | Barrier 6 · Immun 4 · Immun 4 · Barrier 6 · Immun 4 · Null 6 (= 30) |
| Barrier | BLOCK 6 FLAT (13). Map W W G G W W, so never Perfect |
| Immunization | SHIM 5 FLAT (11); map W G G W, so avg ×0.75. Rider: CORRUPTED FLAT 1, RANDOM_NON_NULL (existing Dose pattern, RNG shown as odds) |
| Statuses and listeners | None |

### P2 Treatment (82 → 67 %, 45 HP)

| Field | Value |
|---|---|
| Needles | 1, at tick 0 |
| Hub | Metabolism: heal 1.5 % (2 % in the V2 draft is over the cap, see §3) |
| Layout | Barrier 8 · IV 4 · Medicine 3 · Null 4 · IV 4 · Immun 4 · Medicine 3 (= 30) |
| Barrier | BLOCK 8 FLAT (18). Fewer and bigger |
| IV | SHIM 2 FLAT (4) per hit, with `hits_per_target_status` = your CORRUPTED slices (min 1), separate hits. Map W G G W |
| Medicine | OVERFLOW 5 FLAT (11); Perfect ×4 (44). Map G P G, so the Perfect is 1 tick of 3 |
| Immunization | As P1, kept as a bridge |

- Separate IV hits matter: BLOCK 18 eats about 4 hits, and SANDBOX negates all of them.

### P3 Intensive Care (67 → 35 %, 96 HP)

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 14 |
| Hub | Metabolism 1.5 % |
| Layout | Barrier 5 · IV 4 · Med 3 · IV 4 · Immun 4 · Med 3 · IV 4 · Null 3 (= 30) |
| Barrier | BLOCK 6 FLAT (13) |
| Other slices | As P2 |

**Why 14 is the right offset (checked against the layout).**
- Medicine centres sit at ticks 10 and 21, 11 apart. The needles are 14 apart, so both can never be Perfect on Medicine together.
- Whenever one needle is on a Perfect Medicine, the other lands on an IV (G or W).
- Result: a Perfect Medicine always comes with an IV, never with a second Perfect or a free Null. This is the uneven-needle tool of R10.

### P4 Code Blue (35 → 0 %, 105 HP, no floor)

| Field | Value |
|---|---|
| Needles | 2, at ticks 0 and 14 |
| Hub | Metabolism 1.5 % |
| Layout | IV 4 · Adren 3 · IV 4 · Null 4 · Adren 3 · IV 4 · Adren 3 · Null 5 (= 30) |
| Defense | None |
| IV (CB) | As P2, plus a rider: CORRUPTED FLAT 1, UNDER_POINTER |
| Adrenaline | OVERFLOW 5 FLAT (11), Perfect ×4 (44), **pierce**. Rider: CORRUPTED FLAT 1, UNDER_POINTER |

- **Code Blue** is authored as slice riders, not a hub listener: once per resolved boss slice (not per hit), on the slice your pointer read.
  - It corrupts even if BLOCK absorbed the damage.
  - Only SANDBOX (negating the whole resolution) stops it.
  - Landing on an already-corrupted slice is a no-op, so a sacrificial slice limits spread.
- **Idle turns:** Adrenaline centres are at 5, 16 and 23, so the needles are never both Perfect. Whenever needle A is in ticks 11-14, needle B is in 25-28, so both sit on Null. That is a 13 % breather turn, which is fine.

### Transitions
Each transition parks damage at the floor and ends the resolve. The new layout loads (`wheel_override` + `hub_override`) and takes effect at the next start-of-turn respin. Statuses stay (R6 remap). The phase line plays, and the new layout is revealed on entry only under Chart Hidden.
- P1 → P2: heal 1 % → 1.5 %.
- P2 → P3: MULTIPLY to ticks 0 / 14.
- P3 → P4: all defense dropped, Code Blue riders on.

## 3. Sustain and intake

**Sustain: one source, the hub heal. Cap = 30 % of reference damage per turn.**

| Phase | Reference dmg/turn | Cap | Heal at 300 | OK? |
|---|---|---|---|---|
| P1 | 18 | 5.4 | 1 % = 3 | yes |
| P2 | 18 | 5.4 | 1.5 % = 4.5 → 5 | yes |
| P3, P4 | ≈ 31 (2 needles × 18 × 0.85 for dead needles) | 9.3 | 5 | yes |

- **V2 draft error:** P2 at 2 % = 6 exceeds the 5.4 cap. P2 is the only single-needle phase with the larger heal. 1.5 % fixes it.
- It also matches the ruling "heal as in phase 2" for P3 and P4.
- **Triage Reserve** (the buff) adds a once-per-phase shield of 3 % max HP (9, ≈ 2.6 per turn). Metabolism + Triage Reserve together is about 7.6 per turn in P2, over the cap. That is accepted: it is an uncountered-buff cost, and the HP budget below is without it.

**Intake per turn at the reference player.** Raw means unsteered and unblocked; T4 values.
- Assumed corrupted count: 2 in P2, 3 in P3, 4 in P4.
- The expected multiplier per landing is as follows:

| Slice | Average output multiplier |
|---|---|
| Medicine / Adrenaline (3-tick, G P G) | (4+1+1)/3 = 2.0 |
| 4-tick slices | 0.75 |

| Phase | Raw per needle | Needles | Raw per turn | Net target (after block, steer, SANDBOX) |
|---|---|---|---|---|
| P1 | 3.3 | 1 | 3.3 | 1-2 |
| P2 | 4.4 (Med) + 1.8 (IV) + 1.1 (Immun) = 7.3 | 1 | 7.3 | 3-4 |
| P3 | ≈ 9.5 | 2 | ≈ 19 | 6-8 |
| P4 | 7.3 (Adren) + 4.8 (IV) ≈ 12 | 2 | ≈ 24 | 8-10 before enrage |

- **Fix to the V2 draft:** its "12+ before enrage" for P4 only makes sense as raw. Taken as net it is about 50 HP over 4 turns, and the whole fight would cost about 110 HP against a 45-60 HP operative.
- With the net targets above, a full fight costs about 55 HP (≈ 3.5·1.5 + 3.5·3.5 + 3.5·7 + 4·9). That is roughly one full HP bar: a good player ends low, a weak player dies in P3-P4. This is deliberate for the final boss.
- Intake is above 0 in every phase.

## 4. HP by tier

T4 only. Per-tier values below are `hp_bands` (ICE boss-strength zone ceiling → HP).

**Phase-budget arithmetic** at T4, with reference 18 dmg/turn and 3.5 turns per phase:

| Phase | Needle factor | Calculation | Budget | Authored |
|---|---|---|---|---|
| P1 | 1 | (18 − 3) × 3.5 | 52.5 | 54 |
| P2 | 1 | (18 − 5) × 3.5 | 45.5 | 45 |
| P3 | 1.75 | (31.5 − 5) × 3.5 | 93 | 96 |
| P4 | 1.7 | (30.6 − 5) × 3.5 | 90 | 105 |

- **Needle factor:** two needles are not ×2 for the player. In P3 8/30 of ticks read Barrier or Null (≈ 1.75×), and in P4 9/30 read Null (≈ 1.7×).
- **P4 on purpose:** 105 HP at 26 net damage per turn is about 4.0 turns (the climax, top of the 3-4 range).
- **Sum:** budgets total about 281 HP, authored total 300.

| ICE zone ceiling | HP | Phase turns (P1/P2/P3/P4) | Total turns |
|---|---|---|---|
| ≤ 1.00 | 300 | 3.6 / 3.3 / 3.6 / 4.0 | ≈ 14.5 |
| ≤ 1.15 | 320 | 3.9 / 3.5 / 3.9 / 4.3 | ≈ 15.5 |
| ≤ 1.30 | 345 | 4.1 / 3.8 / 4.2 / 4.6 | ≈ 16.7 |
| > 1.30 | 370 | 4.4 / 4.1 / 4.4 / 4.9 | ≈ 17.8 |

- The V2 bands (330 / 360 / 400) push P4 to about 5.4 turns and the total to about 19, past the 3-4 turn-per-phase rule, so I tapered them.
- Floors are percent-based (0.82 / 0.67 / 0.35). The V2 draft's 0.68 / 0.33 gives P4 99 HP, which is fine, but 0.35 gives a cleaner P3/P4 split.

## 5. Enrage

**Default** (start turn 10, every 5 turns, +25 % damage per step, additive).
- Expected path: P4 begins around turn 10.5, so P4 runs under step 1 (×1.25).
- Step 2 (×1.5) lands at turn 15 and punishes a slow P4, which is the Code Blue clock.
- **Correction to the V2 text** ("P3 in the first step, P4 in the second"): P3 runs turns 7-10.5, mostly before step 1.
- It raises damage only, not heal or defense.
- No authored trigger: Code Blue's spreading corruption is already a built-in clock, and a second authored clock would stack punishment.

## 6. Buffs and counter Exploits

A route draws 5 of the corporation's Exploit pool, so about 60 % of buffs are counterable per run (8 buffs, 5 Exploits).
- Today's three Exploits (Intel / Breach / Virus) become part of an 8-Exploit pool; Solace needs 5 new `ExploitData`.
- `min_exploits_for_breach = 3` stays.

| Buff | Effect | Counter Exploit turns off | Notes |
|---|---|---|---|
| **Second Opinion** (signature) | Needle 2 acts in P3-P4 | Needle 2 becomes **inert**: it resolves nothing for the boss but still takes your hits | Today's Breach, remapped |
| **Compliance Lock** (signature) | Hub resistance 2 (a 1-tick nudge is fully absorbed; Flip and Respin blocked) | Resistance 0 | Makes the P2 Medicine denial cost 3 RAM |
| **Antibodies** (signature) | Immunization corrupts FLAT 2 | Back to 1 | |
| Metabolism | The hub heal | All boss heal off | Base mechanic, not strong; the counter is its fix |
| Sterile Field | `cleanse_on_enter` = OWN: strips your statuses (OUTPUT_DOWN etc.) on each boss phase change | Statuses stick | |
| Booster | IV minimum 2 hits | Minimum 1 | |
| Triage Reserve | SHIELD = 3 % max HP (9) at each phase start | No shield | |
| Chart Hidden | Phases and next layouts hidden | Reveals them | Today's Intel |

- **Second Opinion fix (V2 error).** The draft counters it by removing the needle, but R2 sizes HP for two needles and your attacks hit every pointer. Removing one halves your damage while the HP stays, so the "counter" would make P3-P4 take about 7 turns each and trigger enrage.
  - **Fix:** the counter makes needle 2 inert, so it loses its attack and keeps taking your hits. This needs a new `inert_pointers` field on the phase data (see §8).
- **Virus (open-source patch):** with R9, CORRUPTED no longer deals damage. Retire its "boss starts corrupted" effect; remap it to counter Antibodies, with no new design.

## 7. Counterplay

**P1**
- Good: use the free nudge to move its needle onto Null or an Immunization WEAK edge, then burst. Keep your CORRUPTED count at 0-1 (Cleanse, Encrypt).
- Weak: feeds it Barrier turns (each is about 0.7 of a reference turn) and lets corruption stack for free.

**P2**
- Good: deny the Medicine Perfect (a 1-tick nudge turns ×4 into ×1). SANDBOX the landed Medicine, SHIELD the IV chip damage. Remember corrupted slices cost 2× RAM, so cleansing is also economy.
- Weak: leaves 3+ corrupted slices into IV, so IV turns hit 3+ times and cost double RAM.

**P3**
- Good: choose which needle reads which slice. The 14-tick offset ties a Perfect Medicine to an IV, so SANDBOX the Medicine turn; Flip works if Compliance Lock is off. Race: your hits land twice.
- Weak: nudges only one needle and eats a Perfect ×4 plus an IV.

**P4**
- Good: use a sacrificial corrupted slice to stop spread, SANDBOX the Adrenaline (pierce ignores BLOCK and SHIELD), and finish before turn 15.
- Weak: plays defense that does not exist here, spreads to all 5 slices (IV ×5 hits, RAM ×2 on everything), and dies in the enrage step.

## 8. Systems needed

| System | Needed for | Data-only fallback |
|---|---|---|
| N1 amount modes | PERCENT heal, FLAT amounts × tier | None |
| N2 tier tables / `hp_bands` | Band HP and the 2.2 factor | None |
| N3 phases, parking, status keep, `cleanse_on_enter` | Core to the fight | None |
| N4 enrage | Default enrage | None |
| N5 buffs and Exploits | §6 | Ship phases without buffs (drops the route-subset layer) |
| N9 corruption as RAM ×2 | The fight's economy | Without it the fight is just IV damage |
| N11 any-tick pointers | Needles at 0 / 14 | P3-P4 at 0 / 15 (evenly spaced): loses the Perfect-pairing puzzle |
| N12 variable slice sizes + sub-tick map | Narrow Medicine Perfect | Not recommended: Medicine's narrow window is the core question |
| N14 defense trio | SANDBOX negates whole resolution | Today's DETOUR cancels only one SHIM/OVERFLOW |
| N20 slice riders (`hits_per_target_status`, `perfect_multiplier`, `pierce`) | IV, Medicine, Adrenaline | IV as fixed 3 small hits; Medicine/Adrenaline as plain OVERFLOW (no ×4) |
| NEW: `inert_pointers` (small extension of N11) | Second Opinion counter | Without it, Breach removes a needle and the fight lengthens |
| N19 sim metrics | Turns per phase, parked damage | Not blocking |

**Dropped:** N6 (listeners). Code Blue is authored as slice riders (extra_effects at ON_SLICE_TRIGGER), which also avoids the preview risk of a listener.

## 9. Delta vs today (and vs the V2 §2 draft)

**Delta vs today**
- HP 360 flat → `hp_bands` 300 / 320 / 345 / 370 (a 75 % tier factor was baked into 1,475 HP before).
- Phases: today 2 (66 % Multiply, 33 % Orbit + 2 collections drones + `wheel_emergency`) → 3 `BossPhaseData` entries (P2, P3, P4 on top of the P1 base wheel).
- Retired: Orbit, collections-drone spawns, and the 10-flat hub heal (percent now).
- Kept: `id`, `corporation_id`, `is_boss`, `cycle_reward = 100`, Dose's random-non-NULL corruption pattern (Immunization).
- New slice files: `gc_barrier_6/8`, `gc_immunization`, `gc_iv`, `gc_iv_cb`, `gc_medicine`, `gc_adrenaline`.
- Exploits: Intel → Chart Hidden counter, Breach → Second Opinion counter, Virus → Antibodies counter, plus 5 new.
- `heat_effects`: none on today's file; none added.

**Corrections to the V2 §2 draft**
1. P2 heal 2 % exceeds the single-needle cap (5.4): use 1.5 %.
2. Medicine and Adrenaline base 10 → 22 at T4, so ×4 = 88: unavoidable lethal. Base 5 → 44.
3. Code Blue "per hit that reaches you" would corrupt all 5 slices in one IV turn. Now once per boss slice.
4. The Second Opinion counter lengthened the fight; now an inert needle.
5. The enrage timeline was wrong (P4 is in step 1, not step 2).
6. Size 8 had no quality map (authored override).
7. Bands 330/360/400 over-stretch P4; tapered.
8. Intake "12+" was raw, not net.

## 10. Predicted sim check

No baseline row exists for this boss, so this is estimated from the wheel and the playtest log, not measured. Playtest fights ran 17-54 turns against the current flat-heal boss.

| Case | Mean turns | Win % | Why |
|---|---|---|---|
| Fresh, ICE 0 | 14-16 | 30-40 | Baseline 25 % fresh / 4-8 % in campaigns. Parking removes burst skips, so a bot's 16-35 dpt burst is capped by the floors. |
| Campaign (HP attrition) | 15-18 | 15-25 | Net intake ≈ one HP bar, so the carried HP deficit costs. |
| Weak player (3-5 dpt) | 25+ | ≈ 0 | Enrage steps 10 and 15 kill. |
| `--policy heuristic --lookahead 2` | n/a | n/a | Should do better than random; check "puzzle" here. |

Pass criteria for the sim: 3-4 turns per phase, intake > 0, ≤ 1 heal turn per phase. Sustain stays inside the cap without Triage Reserve.

## 11. Open questions

- Q: Percent heal rounding (1.5 % of 300 = 4.5): round up (proposed), round to nearest, or keep the integer 1 % / 2 %?
- Q: Does a Code Blue rider fire when BLOCK absorbs all the damage? I chose yes (corruption fires even if blocked), making SANDBOX the only counter. Confirm.
- Q: Is a net intake of about 55 HP over the fight (a full operative bar at T4) the intended lethality, or should the boss win-rate target in Q12 force it lower?
- Q: Should Metabolism ship as a "strong" buff at all (heal ≈ 4-5/turn, small)? If it needs more bite, a second heal source breaks the sustain cap.
- Q: Add `inert_pointers` (a field on the phase data) as part of N11, or accept that Breach removes a needle and re-tune the HP for that case?
