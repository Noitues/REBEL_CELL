<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01VyfaEioaVujaomJg4hxWKS, custom_id v2__enemies__commons_array; status ok; tokens in 9216 cache-write 0 cache-read 32585 out 40383; cost $0.214. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Critic 1 (BLOCKER, thresholds contradict, P1/P5 under 3 turns):** One threshold set now: **0.82 / 0.68 / 0.52 / 0.19**. The 20 % steps and 0.88/0.74/0.46/0.22 are gone. Phase HP is 54 / 42 / 48 / 99 / 57 at 300 HP, each derived from the R2 budget. Phase tables, intake and enrage timing were rebuilt on it. P1 is about 3.6 turns and P5 about 3.2.
- **Critic 2 (BLOCKER, band invented):** The spec band is used as written, 300 / 330 / 360 / 400 (≤1.00 / ≤1.15 / ≤1.30 / >1.30). The R2 budget is re-derived to sum to about 300. The v1 budget of 445 came from two needles in P3-P5 and 3.5 turns on all five phases. It is fixed by giving the second needle only to P4 and P4 gets 3.07 turns. HP is shown for all four bands.
- **Critic 3 (BLOCKER, ~2 turns per phase):** Needle count is now 1 / 1 / 1 / 2 / 1, so the budget fits 300 HP. Turns per phase are 3.6 / 3.6 / 3.7 / 3.1 / 3.2, total about 17.
  - Pointer lists are authored per phase (the same field Genome Core uses), so P5 can drop back to one needle.
  - This follows the critic's alternative ("move the second needle to P4 only"). Critic's Q "P5 one needle?": yes.
- **Critic 4 (MAJOR, sustain):** Hub heal is 1 % in P1, **1.25 %** in P2-P4 and none in P5. It is applied in every table. At 300 HP the heal is 3.0 / 3.75 per turn (≤ 21 % of 18). At the 400 band it is 5.0 (27.8 %), so the 30 % cap holds in every band.
- **Critic 5 (MAJOR, satellites / R12):**
  - Removed "re-dock", "costs a Relay" and the non-existent "Relay-Defrag" slice type.
  - A Relay is destroyed only by damage dealt to it. Nothing replaces it, and R12 REPLACE is not used.
  - The mini-wheel is stated as 15 + 15 = 30 ticks.
  - Guards stay only in P2, as a steering question. The brief bans the Mission Director's gates and replacement, not fixed guards.
- **Critic 6 (MAJOR, Flare overclock reused):** All Flare / OVERCLOCK content is removed. P3 is now a Parasite-ring question (Debris).
- **Critic 7 (MAJOR, arithmetic):** All five layouts were re-added and are shown with tick spans.
  - "MULTIPLY from P2" was wrong. Needles are now 1/1/1/2/1 with MULTIPLY at P3→P4.
  - Orbit needles with a fixed 11-tick gap never change spacing, so P4 needles are FIXED. ORBIT lives in P1 and P5.
- **Critic 8 (MAJOR, Burnout vs R9):** The Burnout listener and CORRUPTED are dropped. Damage lives on the Parasite ring. No listeners remain, so N6 is no longer needed.
- **Critic 9 (MAJOR, buffs weak / Exploit contradiction):**
  - Eight buffs. Three weak ones (Burnout Link, Second Reader, Debris Field as v1 wrote them) were replaced by Phase Shield, Burn Profile and Ground Link. Debris Field was rewritten stronger.
  - Intel, Breach and Virus are mapped onto three of the eight counters. A route draws 5 and any 3 open the breach (R7, `min_exploits_for_breach` = 3).
- **Critic 10 (NIT):** The enrage timeline is now computed from cumulative turns. The v1 "repeat before all slices fire" trigger is dropped, because it fires on turn 1 on a 7-slice wheel. It is listed as Q. This also removes the v1 mapping of that trigger to N20.
- **Critic keep list:** Kept the clock concept with a readable trail, the Station Keeping signature heal tied to a counter, the uneven-needle P4 question, the racing last phase and the honest fallback table.
- **Ruling conflicts:** None. R2 band, R3 parking, R6 keep, R7 subset and R12 fixed satellites are all followed.

# commons_array: direct design

Working name: "Station Keeping".

## 1. Identity & the one question

- **Class:** HQ boss (Launch Control, final Site). Orbital corporation, T4 only. It appears once, in the campaign's final fight, so there are no L1-2 teaching appearances. Pressure comes from which Exploits the player collected, not from layers.
- **Concept:** a constellation that owns the sky and rents it back. The sky is a clock. The boss's wheel is a schedule the player can read, and later the schedule falls apart. It avoids the Mission Director's gates and replacement, the elites' orbit patterns and the normals' Solar Flare chip damage.
- **Hub:** Station Keeping, the single sustain source, a PERCENT heal. The old "shield 3" is removed.
- **Orbit rule:** an ORBIT needle replaces its wheel's start-of-turn respin, so the trail is true across turns (see Q1).

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Uplink | When does the orbiting needle reach the Overflow? | Read the trail 2 turns ahead; park the Overflow on Null, hit the boss on Shim and Null turns |
| P2 Constellation | The slices that hurt me are the guarded ones. Can I steer off them and still hit the boss? | Nudge away from guarded Overflows; do not trade damage with Relays |
| P3 Debris Belt | Where on my ring do I let Debris sit? | Read with your pointer off Debris; Cleanse the Shade first; burst between latches |
| P4 Deorbit Burn | Which of two uneven needles is the safe one? | Park one needle on Null/Shim; accept the other's hit; carry Debris cleanly |
| P5 Kessler | Can I finish before the sky falls? | Burst; defense is pierced, the boss does not heal |

Threshold parking (R3) applies at all four thresholds, so a burst cannot skip a phase.

## 2. Phase plan

300 HP (band ≤ 1.00). Thresholds **0.82 / 0.68 / 0.52 / 0.19**. Floors: 246 / 204 / 156 / 57. Phase HP: 54 / 42 / 48 / 99 / 57 = 300. Amounts are authored pre-scale, with T4 post-scale (×2.2) in brackets. Damage uses `enemy_damage_by_tier[3]`; percent amounts are not scaled again. Sub-tick map: odd sizes have a Perfect (R11); sizes 2, 4 and 6 have none.

### P1 Uplink (100 → 82 %)

| Field | Value |
|---|---|
| Needles | 1 at tick 0, **ORBIT 2 ticks/turn**, trail shows 3 turns |
| Layout (spans) | Shim 5 (0-4) · Overflow 5 (5-9) · Defrag 6 (10-15) · Shim 4 (16-19) · Null 6 (20-25) · Shim 4 (26-29) = **30** |
| Shim | 4 [≈9] damage |
| Overflow | 8 [≈18] damage |
| Defrag | BLOCK 4 % max HP, PERCENT (12) |
| Hub | Station Keeping: heal 1 % max HP, PERCENT |
| Statuses / listeners | none |

### P2 Constellation (82 → 68 %)

| Field | Value |
|---|---|
| Needles | 1 at tick 0, **FIXED** (wheel respins normally) |
| Layout (spans) | Overflow 5 (0-4) · Shim 5 (5-9) · Defrag 4 (10-13) · Overflow 5 (14-18) · Shim 6 (19-24) · Null 5 (25-29) = **30** |
| Overflow | 10 [≈22] damage |
| Shim | 4 [≈9] damage |
| Defrag | BLOCK 4 % max HP, PERCENT (12) |
| Satellites (N13) | 2 fixed Relays on the two Overflows. 14 HP each. Mini-wheel 15 + 15 = 30 ticks: Shim 2 [≈4] / BLOCK 4 [≈9] flat. A Relay acts only when its host slice is read. |
| Guard rule | Your attack aimed at a guarded slice hits the Relay first. Relays die only to damage; nothing re-docks or replaces them. |
| Hub | Station Keeping: heal 1.25 % |

The guarded slices are exactly the dangerous ones. Steering away from Overflow aims your hits at the boss.

### P3 Debris Belt (68 → 52 %)

| Field | Value |
|---|---|
| Needles | 1 at tick 0, FIXED. Relays are removed on entry (their host slices vanish). |
| Layout (spans) | Latch-A 4 (0-3) · Shim 5 (4-8) · Overflow 5 (9-13) · Defrag 4 (14-17) · Latch-B 4 (18-21) · Shim 5 (22-26) · Null 3 (27-29) = **30** |
| Latch-A | 2 [≈4] damage + latches a **Debris-Drain** (N10) |
| Latch-B | 2 [≈4] damage + latches a **Debris-Shade** (N10) |
| Shim / Overflow | 4 [≈9] / 10 [≈22] damage |
| Defrag | BLOCK 4 % max HP, PERCENT |
| Hub | Station Keeping: heal 1.25 % |

**Parasite ring.** A 4-tick segment is latched on your ring at the tick under your pointer when the Latch resolves. It rotates with your wheel. Max 2; a third latch replaces the oldest.
- **Debris-Drain:** when your pointer reads it, deals 3 [≈7] damage to you.
- **Debris-Shade:** when your pointer reads it, your damage to the boss is ×0.5 for that resolution.
- A Cleanse card removes one segment.

### P4 Deorbit Burn (52 → 19 %)

| Field | Value |
|---|---|
| Needles | 2 at ticks **0 / 11**, FIXED. Entered by MULTIPLY (0, 11). |
| Layout (spans) | Overflow 5 (0-4, centre 2) · Shim 3 (5-7) · Null 3 (8-10) · Shim 6 (11-16) · Overflow 5 (17-21, centre 19) · Shim 3 (22-24) · Null 3 (25-27) · Shim 2 (28-29) = **30** |
| Overflow | 8 [≈18] damage, **perfect_multiplier ×2** (N20): Perfect = 35 |
| Shim | 4 [≈9] damage |
| Defense | none: no BLOCK slices, no Latch |
| Hub | Station Keeping: heal 1.25 % |
| Debris | Carried over from P3 (cleanse_on_enter NONE). New latches stop. |

Overflow Perfect ticks sit 17 apart (2 and 19). The needle gap is 11, so both needles can never be Perfect on Overflows at once. The worst pair is Perfect plus Weak: 35 + 9.

### P5 Kessler (19 → 0 %)

| Field | Value |
|---|---|
| Needles | 1 at tick 0, **ORBIT 3 ticks/turn**, trail visible. The second needle burns up: the pointer list is authored as (0). |
| Layout (spans) | Overflow 5 (0-4) · Shim 4 (5-8) · Overflow 5 (9-13) · Shim 3 (14-16) · Overflow 5 (17-21) · Null 3 (22-24) · Shim 5 (25-29) = **30** |
| Overflow | 12 [≈26] damage, **pierce** (N20): ignores BLOCK and SHIELD, not SANDBOX |
| Shim | 4 [≈9] damage |
| Hub | Station Keeping **broken**: no heal |
| Debris | Carried over, if any remains |

### Transitions

Every phase change parks damage at the floor (R3), keeps statuses and Debris (R6, `cleanse_on_enter` NONE everywhere), plays a phase line and reveals the new layout.
- **P1→P2:** `wheel_override`; ORBIT becomes FIXED; heal 1 % → 1.25 %.
- **P2→P3:** `wheel_override`; Relays removed.
- **P3→P4:** `wheel_override` + MULTIPLY (0, 11); defense and Latch slices removed. Debris you left in P3 is your P4 problem.
- **P4→P5:** `wheel_override`; pointer list (0), ORBIT 3; `hub_override` (heal off).

## 3. Sustain and intake

**Sustain.** One source: the Station Keeping hub heal. Block slices are defense, not sustain.

| Phase | Heal | Per turn at 300 HP | Share of 18 DPT |
|---|---|---|---|
| P1 | 1 % | 3.0 | 17 % |
| P2-P4 | 1.25 % | 3.75 | 21 % |
| P5 | 0 | 0 | 0 % |

At the 400 band the 1.25 % is 5.0, or 27.8 % of 18, still under the 30 % cap. The Phase Shield buff (§6) is front-loaded and only exceeds the cap on routes without its counter. That is its cost, not a base-fight rule.

**Intake per turn** at the reference player. Unsteered is the average over a random landing, pre-enrage, before block. The reference player steers away from about 40 % of the danger.

| Phase | Unsteered | At reference | Note |
|---|---|---|---|
| P1 | 5.3 | 3-5 | |
| P2 | 8.2 (+ Relay Shim 2) | 5-8 | |
| P3 | 6.2 | 6-9 | includes about 1 from Debris |
| P4 | 18.8 (two needles) | 10-13 | |
| P5 | 13.5 | 9-13 | pierce; before enrage |

All above 0, and it ramps, with enrage steps (×1.25 from turn 10, ×1.5 from turn 15) on top.

## 4. HP by tier

T4 only. T1-T3: n/a.

**Budget at 300 HP**, using `reference_dpt_by_tier[3]` = 18, 3.5 turns per phase, with sustain from §3. Three corrections apply:
- P2 guard factor 0.85 (the reference player lands on guards 15 % of the time).
- P3 Shade drag 0.93.
- P4 and P5 get 3.0-3.1 turns.

| Phase | Effective damage per turn | Turns | HP |
|---|---|---|---|
| P1 | 18 − 3.0 = 15.0 | 3.6 | 54 (budget 52.5) |
| P2 | 18 × 0.85 − 3.75 = 11.55 | 3.64 | 42 |
| P3 | 18 × 0.93 − 3.75 = 12.99 | 3.7 | 48 |
| P4 | 2 × 18 − 3.75 = 32.25 | 3.07 | 99 |
| P5 | 18 (no heal) | 3.17 | 57 |

Sum = 54 + 42 + 48 + 99 + 57 = **300**. Cumulative turns: 3.6 → 7.2 → 10.9 → 14.0 → 17.2. Boss block slices add up to about 0.3 turn if the player does not steer off them. All phases land at 3-4 turns.

**hp_bands.** Same thresholds in every band. The per-phase list below is P1 / P2 / P3 / P4 / P5.

| ICE zone ceiling | HP | Phase HP | Floors (0.82 / 0.68 / 0.52 / 0.19) |
|---|---|---|---|
| ≤ 1.00 | 300 | 54 / 42 / 48 / 99 / 57 | 246 / 204 / 156 / 57 |
| ≤ 1.15 | 330 | 59 / 46 / 53 / 109 / 63 | 271 / 225 / 172 / 63 |
| ≤ 1.30 | 360 | 64 / 51 / 57 / 119 / 69 | 296 / 245 / 188 / 69 |
| > 1.30 | 400 | 72 / 56 / 64 / 132 / 76 | 328 / 272 / 208 / 76 |

Sums check: 330 and 360 and 400 as in the table. At the 400 band P1 is about 4.8 turns, because `reference_dpt` is per tier, not per ICE (see Q2).

## 5. Enrage

**Default boss enrage:** start turn 10, every 5 turns, +25 % additive (×1.25, ×1.5). It raises damage only, including Debris-Drain.

On the expected 17-turn path, step 1 lands in the last turn of P3 and applies through P4 and P5. Step 2 (turn 15) lands in the first turns of P5, which is the last phase and the racing one. The default is kept because the fight has no stall mechanic of its own. The "repeat before all slices fire" trigger is dropped (see Q3).

## 6. Buffs and counter Exploits

Eight buffs. A Grid draws 5 counters (`exploits_per_grid`), so at least three buffs are always on. Any 3 drawn Exploits open the breach (R7). Intel, Breach and Virus are three of the eight counters.

| Buff | Effect | Counter Exploit turns off |
|---|---|---|
| **Station Keeping** (signature) | The per-turn hub heal in P1-P4 | All boss heal (legacy **Breach**) |
| **Orbit Schedule** (signature) | Afterimage: an ORBIT needle also reads last turn's tick at ×0.5 output (NEW: afterimage read). Applies in P1 and P5. | Single read (legacy **Virus**) |
| Relay Mesh | Relays have 28 HP (not 14) and their BLOCK slice blocks the host too | Relays 14 HP, no host block |
| Phase Shield | At each phase start the boss gains SHIELD = 3 % max HP (PERCENT, 9) | No shield |
| Debris Field | Debris max 3 segments; Drain deals 5 [≈11] instead of 3 [≈7] | 2 segments, 3 [≈7] |
| Burn Profile | P4 Overflow Perfect ×3 (not ×2); P5 Shim also pierces | Back to ×2; P5 Shim not piercing |
| Ground Link | Boss wheel resistance 2, restored each turn: blocks Flip and Respin, absorbs nudges | No resistance |
| Dark Orbit | Trails and next-phase layouts are hidden | Reveals both (legacy **Intel**) |

**Signature pair:** Station Keeping (the one sustain) and Orbit Schedule (the clock itself). A route that counters neither is the hard route.

## 7. Counterplay

**Good player**
- **P1:** read the trail, land the Overflow on Null at Good. Hit the boss on the Shim and Null turns. Spend the free nudge, not RAM.
- **P2:** steer your own pointer so the boss needle reads an unguarded slice. Ignore the Relays unless a Perfect hit kills one for free.
- **P3:** do not chase Perfects through Debris. Park your pointer off the Shade segment; spend one Cleanse on Shade before P4. Burst on Null/Defrag landings.
- **P4:** use the 11-tick gap: park one needle on Null or a short Shim. SANDBOX the one Perfect Overflow if it lands. Hit both needles' worth of damage.
- **P5:** all-in. SANDBOX the Overflow turn (pierce skips block and shield). Read the 3-tick trail.

**Weak player**
- Trades damage with the Relays in P2.
- Lets Debris-Shade sit through P3, then carries it into P4 where damage doubles on Perfect Overflow.
- Uses BLOCK against P5's pierce.
- Reaches enrage step 2 in P5 with the boss at full threshold.
- Spreads nudges evenly instead of spending the free one early.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| PERCENT heal / block / shield | N1 | Flat values × tier factor (approximate) |
| `hp_bands`, tier tables | N2 | Single HP 300 |
| Phases, parking, keep statuses | N3 | none |
| Enrage | N4 | none |
| Buffs and Exploits | N5 | Use only legacy Intel / Breach / Virus (3 buffs) |
| Parasite ring (Debris in P3, carried into P4/P5) | N10 | Latch applies the existing PARASITE status (halves the slice) to the slice under your pointer. Loses Drain damage and Shade. |
| Uneven needles (0 / 11) | N11 | Even needles (0 / 15). Loses the "only one Perfect" geometry. |
| Variable slice sizes | N12 | 5-tick slices only. Loses the sub-tick design: not recommended. |
| Fixed satellites | N13 | Existing docking |
| Riders `perfect_multiplier`, `pierce` | N20 | Plain Overflow |
| Afterimage read (Orbit Schedule) | NEW: afterimage pointer read | Drop that buff (7 buffs) |
| Defense names | N14 | SHIELD (the boss's Phase Shield) uses the existing SANDBOX rule |
| Sim metrics | N19 | none |

No listeners (N6) are needed.

## 9. Delta vs today

- **Kept:** id (`commons_array`), the Orbital theme, the Station Keeping hub name and its repair (now PERCENT heal), Overflow, and the placeholder display name.
- **Changed:**
  - HP moves from the shared boss template to `hp_bands` 300 / 330 / 360 / 400.
  - The shared phase template is replaced by 5 direct phases (the old 3-pointer MULTIPLY end state is replaced by 2 uneven needles in P4 and one orbit needle in P5).
  - The shield on the hub is removed; the heal is a single PERCENT source.
- **New:**
  - Slice size maps.
  - Relay satellites.
  - Debris Parasite ring.
  - Eight buffs.
  - Enrage.
- **heat_effects:** retired. Heat already scales the boss through ICE and bands, so authoring more here would double-count.

## 10. Predicted sim check

No baseline row for this boss. Compared with the boss baseline (fresh 38 turns, 25 % win; campaign 41-50 turns, 4-8 % win), the new fight is far shorter, so the HP wall disappears while per-turn damage is higher.

| Condition | Turns | Win |
|---|---|---|
| T4 ICE 0, fresh, typical draw (3 buffs on) | 16-19, p90 ≈ 21 | ≈ 35-45 % |
| T4 in campaign (after the route) | same | ≈ 15-25 % (baseline 4-8 % was HP-dominated) |
| Best route (heal, Phase Shield, Ground Link all countered) | 13-14 | ≈ 50 % |
| Hard route (no heal / shield counters) | 21-24 | ≈ 15-20 % |

Rationale: 17.2 expected turns on 300 HP against 38 today. Intake of 3-13 per turn is mostly steerable. The two hard spikes are P4's two needles and P5's pierce with enrage.

## 11. Open questions

Q: Does an ORBIT needle suppress the boss wheel's start-of-turn respin? The "readable ahead" claim (P1, P5) needs it; otherwise the trail is only valid within a turn.
Q: `reference_dpt` is per tier, not per ICE, so at the 400 band P1 runs about 4.8 turns. Should `hp_bands` above 1.00 also scale `reference_dpt`, or accept longer phases?
Q: Do you want the "a slice repeats before all slices have fired" trigger back as an authored P5 enrage? I dropped it because it fires on turn 1 on this layout.
Q: Does the Phase Shield (PERCENT, 3 % max HP) need its own cap (R2 Q9), or does it stay uncapped as a buff?
Q: Is the Exploit mapping right (Breach → Station Keeping, Virus → Orbit Schedule, Intel → Dark Orbit), with any 3 of the 5 drawn opening the breach?
