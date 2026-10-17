<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__commons_array; status ok; tokens in 17502 cache-write 0 cache-read 32007 out 5777; cost $0.050. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# commons_array: direct design

Working name: "Station Keeping". Per the brief it does not repeat the Mission Director's rim gates and satellite replacement, the Station Commander / Geostationary Guard elite patterns, or the normals' Solar Flare chip damage. Its identity is the sky as a clock: an Orbit Schedule the player can read and exploit.

## 1. Identity & the one question

- **Class:** HQ boss (Launch Control, final Site). Orbital corporation, T4 only. It appears only in the final fight of the campaign, so there are no L1-2 teaching appearances. Pressure comes from the Exploit draw, not from layers.
- **Concept:** a constellation that owns the sky and rents it back. It *keeps station*: everything on its wheel is on a schedule. The fight teaches that its "orbit" is deterministic, so the player plans around where its needles and satellites will be, not where they are.
- **Hub identity:** Station Keeping, the boss's hub. The existing description is "repairs 3, shields 3". Under R2 and R5 this becomes a PERCENT heal and a flat shield, and it is *the one sustain source*.
- **Phase questions** (each is a new question, none is attrition):

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Uplink | Which slice do I let its orbiting needle read? (one needle, orbit 2/turn, readable ahead) | Plan two turns ahead; land the dangerous slices on Null |
| P2 Constellation | Can I hit through the guards? (2 fixed Relay satellites guard its two big slices) | Steer attacks onto unguarded slices; do not trade damage with guards |
| P3 Solar Storm | How do I pay for my own Perfects? (Flares OVERCLOCK, then CORRUPT, my slices, and corruption doubles RAM) | Cleanse/Encrypt before the burnout, or fire overclocked slices before they burn |
| P4 Deorbit Burn | Which of two uneven needles is the safe one? (needles 0 / 11) | Park the dangerous needle on Null/Shield; spend hits on the other |
| P5 Kessler | Can I finish before the sky falls? (no defense, a Debris parasite ring, a repeat trigger) | Burst; the boss shares no sustain here |

- **Threshold parking (R3)** applies at every threshold, so a burst cannot skip a phase.

## 2. Phase plan

The HP shares come from the §4 budget: 5 phases, T4 at 18 DPT (the boss band, ICE ≤ 1.00 → 300; see §4). Thresholds: **0.80 / 0.60 / 0.40 / 0.20**, so each phase is a 20 % slice. Slice sizes sum to 30 in every layout. All amounts are placeholders. Flat enemy amounts are scaled by `enemy_damage_by_tier[3]` = 2.2; the figures below are **pre-scale** base values (post-scale in brackets where it matters).

### P1 Uplink (100 → 80 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, **ORBIT** 2 ticks/turn (trail visible, so planning is possible two turns ahead) |
| Layout (ticks, sum 30) | Shim 6 · Flare 4 · Defrag 6 · Shim 6 · Null 4 · Overflow 4 |
| Shim | 4 damage [≈9] |
| Flare (INFECT) | 2 damage + OVERCLOCKED on 1 random non-NULL slice of yours |
| Defrag | BLOCK 10 % max HP PERCENT |
| Overflow (4 ticks, no Perfect) | 8 damage [≈18], so it can only be hit at Good |
| Hub | Station Keeping: heal 1 % max HP per turn (PERCENT) |
| Statuses | OVERCLOCKED on yours (1.5× once, then CORRUPTED, R9) |
| Listeners | none |

Intent: teaching. The orbit makes the question "when does it arrive at Overflow", and the player can see that three turns ahead.

### P2 Constellation (80 → 60 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0, **FIXED** (orbit stops so the guards matter) |
| Layout | Overflow 7 · Shim 5 · Relay-Defrag 4 · Overflow 7 · Flare 4 · Null 3 |
| Satellites | 2 fixed **Relay** satellites (N13) on the two Overflows. 2-slice mini-wheel (15 ticks each): Shim 3 / Defrag. Pointer attacks aimed there hit the satellite (bodyguard). |
| Overflow | 10 damage [≈22], 7 ticks, Perfect reads at the centre |
| Relay-Defrag | BLOCK 8 % max HP PERCENT |
| Hub | Station Keeping heal 2 % |
| Rule | A replaced satellite is "destroyed"? No: relays are **fixed** (R12), and a Perfect on the guarded slice costs a Relay |

Intent: a different question from P1. Guards give the boss a safe window; the player must steer to the Shim 5 / Null or accept hitting the Relay.

### P3 Solar Storm (60 → 40 %)

| Field | Value |
|---|---|
| Needles | 2, ticks 0 / 14 (uneven, R10), **MULTIPLY** from P2 |
| Layout | Flare 5 · Shim 4 · Overflow 5 · Flare 4 · Defrag 4 · Overflow 5 · Null 3 |
| Flare | 3 dmg [≈7] + OVERCLOCKED on 2 of your slices (Antibody-like pair) |
| Hub | Station Keeping heal 2 % |
| Transition | Cleanse: **NONE**. Statuses survive (R6). Your overclocked slices carry over on purpose |
| Listener (N6) | **Burnout**: when one of your OVERCLOCKED slices becomes CORRUPTED on its trigger, the boss deals 4 [≈9] to you |

Intent: the RAM tax question. Corrupted slices double your RAM, so you must decide whether to spend or cleanse.

### P4 Deorbit Burn (40 → 20 %)

| Field | Value |
|---|---|
| Needles | 2, ticks 0 / 11, **ORBIT** 3 ticks/turn, kept uneven because both move together |
| Layout | Shim 4 · Overflow 6 · Flare 3 · Null 4 · Overflow 6 · Shim 4 · Flare 3 |
| Overflow | 12 [≈26] |
| Defense | none: no BLOCK slices |
| Hub | Station Keeping: heal 2 %, **shield 0** |
| Rule | Fully aware: needle B trails needle A by 11 ticks. If A is on a Perfect Overflow, B sits near the Shim 4 |

Intent: which needle is the safe one. Both orbit, so the arrangement drifts: the player solves a moving puzzle.

### P5 Kessler (20 → 0 %)

| Field | Value |
|---|---|
| Needles | 2, ticks 0 / 11 (continuing) |
| Layout | Debris-Shim 5 · Overflow 5 · Flare 4 · Debris-Shim 5 · Overflow 5 · Flare 3 · Null 3 |
| Parasite ring (N10) | 2 **Debris** segments of 4 ticks on your wheel: when the pointer reads one, it deals 3 [≈7] and reduces your damage to the boss by 50 % for that resolution |
| Hub | Station Keeping **broken** (no heal) |
| Rule | **Repeat trigger**: if any boss slice would fire twice before every slice has fired, the second fire deals +50 % |

Intent: racing. No sustain, a ring of anti-slices, and the enrage step is likely here.

**Transitions (all):** each parks damage at the threshold (R3) and carries statuses (R6). P2 → P3 uses MULTIPLY; P3 → P4 uses `wheel_override` plus ORBIT; P4 → P5 changes the hub.

## 3. Sustain and intake

- **One source:** the Station Keeping hub. 1 % in P1, 2 % in P2-P4, nothing in P5. The 2 % = 6 HP/turn at 300 HP. Cap check: 30 % of 18 = 5.4/turn. 6 > 5.4, slightly over. **Fix:** set the hub heal to **1.5 %** (4.5 HP) in P2-P4.
- No shield and no other heal. The old "shield 3" is **removed**: P2 and P3 carry only BLOCK on slices.
- **Intake per turn** at the reference player (pointer lands on the average slice, one needle ≈ 40 % chance of a damaging slice, one in two Perfects steered away):

| Phase | Intake/turn |
|---|---|
| P1 | 3-5 |
| P2 | 6-9 |
| P3 | 9-14 (two needles + Burnout) |
| P4 | 12-18 |
| P5 | 14-20 before enrage |

All above 0, and it ramps.

## 4. HP by tier / hp_bands

T4 only. Phase arithmetic at `reference_dpt_by_tier[3]` = 18, 3.5 turns per phase, and the phase's needles (P3-P5 have two, so hits land twice):

| Phase | Budget | HP |
|---|---|---|
| P1 | (18 − 3) × 3.5 | ≈ 52 |
| P2 | (18 − 4.5) × 3.5 | ≈ 47 |
| P3 | (36 − 4.5) × 3.5 | ≈ 110 |
| P4 | (36 − 4.5) × 3.5 | ≈ 110 |
| P5 | 36 × 3.5 | ≈ 126 (no heal) |

Sum ≈ **445**. That is high for the band, so the player's hits on two needles (R2 pointer rule) are doubled only in P3-P5. I choose to **cap at hp_bands** and shift thresholds by what each band produces:

| ICE zone ceiling | HP |
|---|---|
| ≤ 1.00 | 330 |
| ≤ 1.15 | 360 |
| ≤ 1.30 | 400 |
| > 1.30 | 440 |

At 330: P1 20 % = 66, P2 66, P3 66, P4 66, P5 66. These are equal 20 % shares (66 vs budget 52/47/110/110/126), so P1-P2 take 4 turns and P3-P5 take about 2 turns under a double-needle player. That is shorter than 3-4, so I **reshape thresholds**: **0.88 / 0.74 / 0.46 / 0.22**, which gives HP 40 / 46 / 92 / 79 / 73, hitting budget well enough. Use these thresholds, not 20 % steps.

## 5. Enrage

Default for a boss: start turn 10, every 5 turns, +25 % damage (additive). With an expected 15-18 turn fight, the first step lands at the start of P4, the second inside P5. I keep the default. The designer's mention of a "slice repeats before all slices have fired" is used as P5's authored mechanic (above), not as a second enrage.

## 6. Buffs and counter Exploits

A route draws 5 of 8 (`exploits_per_grid` = 5). Orbital keeps Intel, Breach and Virus as the three gate Exploits; the five new ones are drawn.

| Buff (strong) | Effect | Counter Exploit |
|---|---|---|
| **Station Keeping** (signature) | The hub heal each turn, P1-P4 | Heal off |
| **Orbit Schedule** (signature) | The boss's ORBIT: its needles move 2-3 ticks/turn | Needles stop (FIXED) |
| Relay Mesh | Relays are immune to Pierce and Perfects, and re-dock after being destroyed | Relays die normally |
| Flare Reserve | Flares overclock 2 slices, not 1 | Back to 1 |
| Second Reader | 2nd needle in P3-P5 | One needle |
| Debris Field | Parasite ring in P5 has 3 segments | 1 segment |
| Burnout Link | The Burnout listener | Off |
| Chart Hidden | Phases and layouts hidden | Reveals (Intel) |

**Signature pair:** Station Keeping (the heal is the one sustain) and Orbit Schedule (the premise of the fight). A route without either counter is the hard route.

## 7. Counterplay

- **Good player:**
  - P1: read the trail and land the Overflow on a Null at Good.
  - P2: steer to the unguarded Shim and ignore the guards. Spend the free nudge, not RAM.
  - P3: Cleanse or Encrypt overclocked slices before their burnout, and fire them first; accept Perfects only where the RAM allows.
  - P4: use the 11-tick gap to park one needle on Null and take the other's hit. Block, do not Sandbox, the smaller hits.
  - P5: all-in burst; SANDBOX the Debris resolve.
- **Weak player:**
  - Trades damage with the Relays in P2.
  - Lets Flares stack and pays doubled RAM for the whole of P3-P4.
  - Ignores the orbit and takes both Overflows in P4.
  - Reaches enrage step 2 in P5.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Percent heal and block | N1 | Flat values scaled by tier (approximate) |
| hp_bands, tier tables | N2 | Single HP 330 |
| Phase parking, status keep | N3 | none: central |
| Enrage | N4 | none |
| Buffs and Exploits | N5 | Use the 3 existing Exploits only |
| Listener (Burnout) | N6 | Drop the listener; keep Flares |
| Statuses, CORRUPTED RAM cost | N8, N9 | Existing statuses |
| Parasite ring (P5) | N10 | Replace with 2 extra Flare slices (loses P5's hook) |
| Uneven needles | N11 | Even needles |
| Variable slice sizes | N12 | Use 5-tick slices (loses the 4-tick no-Perfect Overflow) |
| Fixed satellites | N13 | Existing docking |
| Slice riders (repeat) | N20 | Drop |

## 9. Delta vs today

- **Kept:** id, Station Keeping hub, Solar Flare, Orbital theme, Overflow, the existing orbital_drone satellite lines.
- **Changed:** 420 → 330 HP at the band minimum; 3 phases → 5; the heal and shield become one PERCENT heal; the old 3-pointer MULTIPLY end state is replaced by 2 uneven needles; the Crit wheel is gone.
- **New:** slices with sizes and tick maps, a Relay variant, Burnout listener, Debris parasites, enrage, 8 buffs.
- **heat_effects:** none authored, none kept.

## 10. Predicted sim check

No baseline row; estimated from the wheel. A fresh fight at skill ≈ the reference: 14-17 turns (P1 3-4, P2 3-4, P3-P5 about 3 each), p90 ≈ 19. Win rate is not tuned for the campaign condition.

| Tier | Expected |
|---|---|
| T1-T3 | n/a (T4 only) |
| T4 ICE 0, fresh | ≈ 35-45 % win, because the boss now has 20 % less HP than today's 420 but real damage in P3-P5 |
| T4 in campaign | ≈ 15-25 %; the baseline of 4-8 % is dominated by HP, which is now much lower |

Worst-case hard route (no counters drawn): ≈ 20 % fresh.

## 11. Open questions

Q: Is the 330 / 360 / 400 / 440 band right, given the phase budgets sum to ≈ 445 at 18 DPT? Should P3-P5 be shorter instead?
Q: Does the "repeat before all fire" trigger in P5 need N20, or can the sim treat it as an authored Enrage variant?
Q: Do Relays count as destroyed when a later satellite replaces them (R12 Q7)?
Q: Should the Orbit Schedule buff be the one the designer wants guaranteed in every Grid draw?
Q: Is a Debris parasite on the player's ring (N10) acceptable at launch, or should P5 wait for the ring?
