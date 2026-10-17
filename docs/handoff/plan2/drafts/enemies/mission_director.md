<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__mission_director; status ok; tokens in 16518 cache-write 0 cache-read 32007 out 5245; cost $0.046. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# mission_director: direct design

## 1. Identity & the one question

**Class:** Mini-boss (3 phases), Orbital Commons. It guards the final Rack at T1–T3. At T1–T2 it teaches rim gates and satellite replacement. At T3 it is a full routing puzzle. No T4 values are needed, but a T4 column is given for sim symmetry.

**Concept change:** I keep the Countdown / Deploy / Abort Window arc from section 3. I change two things:
- **Pointer positioning is the fight.** P1 puts both needles on one wheel and P3 uses uneven needles, so the pointer geometry carries the questions. The old concept leaned on gates alone.
- **A Flare is a real threat.** The old Deploy phase launched satellites and overclocked you at the same time. Now the satellites are the threat and the Flare is a single slice. That keeps P2 readable.

**Phase questions:**

| Phase | Question | Answer that shortens the fight |
|---|---|---|
| P1 Countdown | "How do you move without tripping the gates?" Nudges and spins that carry a gate past its needle advance a countdown, and at 3 the Director adds an Overflow. | Plan one route per turn. Use Flip and Snap, which don't traverse. |
| P2 Deploy | "Which guard do you steer around and which do you kill?" Fixed satellites replace each other, so hitting one only helps you if it unblocks a lane. | Land on unguarded slices. Spending damage on guards is a trap. |
| P3 Abort Window | "Which of two uneven needles do you feed, and can you afford a big spin?" Crossing a gate hurts it, so the P1 constraint now pays you. | Do a deliberate big spin across both gates, then a Perfect on the safe needle. |

## 2. Phase plan

**Thresholds:** 0.66 and 0.33 (R1: 3 phases, 3–4 turns each). Floors are ceil(max HP × next threshold).

### P1 Countdown (100 → 66 %)

| Item | Value |
|---|---|
| Needles | 1, tick 0 (FIXED) |
| Resistance | passive 1, restored each turn |
| Hub rule | none |
| Gates | 2 rim gates on the Director's wheel at ticks 7 and 22 (N15) |
| Listener | When a nudge or spin of the Director's wheel carries a gate past its needle, Countdown +1 per gate crossed. The respin never counts. At 3, the next resolve adds one extra OVERFLOW resolution at 8, then Countdown resets. |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Shim | 6 | 8 damage, pointer, FLAT |
| Defrag | 4 | BLOCK 6, FLAT, × tier damage factor |
| Overflow | 5 | 12 damage |
| Solar Flare | 5 | OVERCLOCKED on 1 random non-NULL slice of yours (weak flavour) |
| Null | 6 | nothing |
| Shim | 4 | 8 damage (4-tick: no Perfect on this one) |

- The Shim and Overflow are readable and modest.
- Only the Director's own wheel carries the gates. The Countdown counts traversals of the Director's wheel, because that is where your nudges and spins move its needle across.
- Your wheel is untouched.

**Transition P1 → P2:**
- Parks at floor 66 %.
- `wheel_override`.
- Statuses are kept and remapped (R6).
- Gates are removed.
- Countdown resets.
- `cleanse_on_enter` is NONE.

### P2 Deploy (66 → 33 %)

| Item | Value |
|---|---|
| Needles | 1, tick 0 |
| Hub rule | **Launch Window:** at the start of each turn, a fixed Relay satellite docks on one of the Director's slices, REPLACE on occupied (N13). It rotates over the Director's slices in order, which is readable ahead. Max 2 on the wheel. |
| Satellites | Relay: 6 HP, 2-slice mini-wheel (Shim 4, Null), fixed, can't be nudged |
| Listener | none |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Overflow | 5 | 14 damage |
| Flare | 4 | OVERCLOCKED on 1 chosen-by-pointer slice of yours (SlicePick UNDER_POINTER) |
| Shim | 6 | 8 damage |
| Defrag | 5 | BLOCK 8 |
| Null | 4 | nothing |
| Shim | 6 | 8 damage |

- Relays act as bodyguards. A hit that lands on a docked slice hits the Relay instead (GDD 2.7).
- Replacing a Relay is not a kill. Daemons and rewards are unaffected (Q).
- The Flare uses the pointer-slice pick. It is telegraphed in the preview.
- OVERCLOCKED gives 1.5× once and then CORRUPTED, which now costs double RAM (R9). That is a real tax but not damage.

**Transition P2 → P3:**
- Parks at floor 33 %.
- `wheel_override` and `pointer_ticks` = (0, 11).
- Satellites are cleared. Statuses are kept and remapped.
- The Director's own CORRUPTED, if any, is cleansed (`cleanse_on_enter` = OWN). Reason: it lets the player's Virus Exploit mean something in P1–P2 without making P3 a free ride.

### P3 Abort Window (33 → 0 %)

| Item | Value |
|---|---|
| Needles | 2, ticks 0 and 11 (uneven, R10) |
| Orbit | the wheel orbits 3 ticks per turn (telegraphed trail) |
| Resistance | passive 1 |
| Gates | the same 2 rim gates at ticks 7 and 22 |
| Gate rule | **Abort Window:** each gate a player nudge or spin carries past a Director needle deals 6 damage to the Director, once per gate per turn (FLAT). This is the P1 rule inverted. |
| Hub rule | **Hotfix** heals 3 % max HP per turn (PERCENT) — the only sustain |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Overflow | 4 | 16 damage (no Perfect) |
| Shim | 5 | 8 damage |
| Flare | 4 | OVERCLOCKED, under pointer |
| Defrag | 5 | BLOCK 8 |
| Shim | 6 | 8 damage |
| Null | 6 | nothing |

- With 2 needles 11 ticks apart, one needle usually sits on a real threat and the other on a weaker slice.
- At 4–5 ticks the Overflow and Flare windows are narrow. The player nudges one of the two needles onto Null, not both.

## 3. Sustain and intake

**Sustain:** one source, the P3 Hotfix at 3 % max HP per turn.
- T3 (HP 130): 3 % ≈ 4 per turn.
- Cap is 30 % of reference damage: 0.3 × 14 = 4.2 per turn.
- 4 ≤ 4.2, so it passes. P1 and P2 have no sustain beyond Defrag block, which is not healing.

**Intake per turn** at the reference player, at tier damage factor 1.0 (multiply by tier):

| Phase | Intake / turn |
|---|---|
| P1 | 4–6 (one needle on Shim or Overflow about half the time, plus the occasional Countdown Overflow) |
| P2 | 6–9 (Overflow 14 plus Relay Shim 4; Flare adds CORRUPTED RAM tax) |
| P3 | 9–13 (two needles; one often on a threat) |

Every phase is above 0.

## 4. HP by tier

R2 mini-boss (3 phases) bands:
- T1 95–105
- T2 104–128
- T3 132–162

Phase-budget method: `reference_dpt_by_tier` × 3.5 turns × needles landing, minus sustain.

| Tier | dpt | Per-phase base | P1+P2+P3 | Sustain | Chosen HP |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 94.5 | 0 | **96** |
| T2 | 11 | 38.5 | 115.5 | 0 | **115** |
| T3 | 14 | 49 | 147 | 4 × 3.5 = 14 (P3 only) | **150** (band top) |
| T4 | 18 | 63 | 189 | 4 × 3.5 = 14 | n/a; for sim only, 190 |

Arithmetic at T3, per phase:
- Thresholds are 0.66 and 0.33, so shares are 34 %, 33 % and 33 %.
- P1: 150 × 0.34 = 51, roughly 3.6 turns at 14 per turn.
- P2: 150 × 0.33 = 49.5, roughly 3.5 turns.
- P3: 49.5 HP + 14 healed = 63.5 to remove, roughly 4.5 turns at 14 per turn. Abort Window gate hits (6 each) and the second needle on the Director shorten it. The player's hit lands on both needles under the pointer rule, so the expected P3 time is about 3.5.
- Total: ≈ 10.5 turns, inside 6–12.

Today's 150 sits at the top of the T3 band and far above T1 (96) and T2 (115). Authoring `hp_by_tier` = [96, 115, 150, 190] fixes that.

## 5. Enrage

**Default:** start turn 10, every 5 turns, +25 % damage (additive).
- Expected fight is ~10 turns, so enrage only bites a slow fight.
- A fast player finishes at turn ~8 and never sees it.
- A weak player who stalls in P1 gets pushed in P3.

## 6. Buffs and counter Exploits

Not applicable (mini-boss).

## 7. Counterplay

**P1:**
- A good player reads the gates and routes the Director's wheel the short way.
- They use the free nudge toward Null, and cards that don't traverse (Flip, Snap).
- They burst the Shim and Overflow windows, which are plain.
- Floor parking means overkill damage is lost, so there is no reason to burst past 66 %.

**P2:**
- They steer onto unguarded slices.
- They use Perfect hits on a slice with no Relay.
- They spend a spare nudge to move a Relay off the lane.
- They don't attack a Relay unless it blocks a Perfect.
- They Cleanse a CORRUPTED slice before the RAM tax compounds.

**P3:**
- They find the one big spin that crosses both gates for 12 damage.
- They put the 0 needle on Null and take the 11 needle's Shim.
- They SANDBOX the Overflow turn.
- They kill it before the enrage step.

**Weak player mistakes:**
- Nudging over gates in P1 for no reason, feeding the Countdown Overflow.
- Killing Relays in P2 (the replacement rule wastes it).
- Ignoring the Flare, so CORRUPTED stacks and every nudge costs 2 RAM.
- Walking both P3 needles onto threats.

## 8. Systems needed

| N# | Used for | Fallback |
|---|---|---|
| N3 | Phase floors, status remap, `cleanse_on_enter` | none; core |
| N1 | PERCENT Hotfix, FLAT × tier damage factor | Hotfix as flat 4 |
| N2 | `hp_by_tier` | per-tier `.tres` overrides |
| N4 | Enrage | none; use default |
| N11 | Uneven needles (0 / 11) | use 0 / 15 (today's multiplier) |
| N12 | 4- and 6-tick slices | all 5-tick; loses the narrow Overflow window |
| N13 | Fixed Relays and REPLACE | Relays as normal satellites; weaker |
| N15 | Rim gates | **no fallback**; gates are the signature. Without them P1 and P3 become a plain heal-and-hit fight. |
| N6 | none (listener-style Countdown could be a gate rule) | n/a |
| N9 | CORRUPTED as a RAM cost | old CORRUPTED self-damage (less good) |
| N19 | turns-per-phase metrics | n/a |

The gate rules are a gate feature (N15), not N6 listeners, so N6 is not required.

## 9. Delta vs today

**Kept:**
- id, corporation and `is_mini_boss`.
- Slice set (Shim, Defrag, Overflow, Flare, Null).
- `cycle_reward` of 60.
- The "Abort window" and "Go for launch" phase lines, reused.

**Changed:**
- Thresholds from 0.5 / 0.25 to 0.66 / 0.33.
- P1 (needles 0) is new; today it has resistance 2.
- Today's phase 0 is a Multiply to (0, 15). That becomes the P3 pointer concept, now uneven (0 / 11).
- Today's phase 1 is an Orbit of 3 ticks per turn. That is kept only in P3.
- Resistance 2 drops to 1 (Flip and Respin were blocked entirely, which hid the Countdown route).
- HP 150 → [96, 115, 150, 190].
- Wheel layout rebuilt with variable sizes.
- New Relay satellite, rim gates and the Hotfix hub.

**`heat_effects`:** retire any. Phases and enrage carry the pressure.

## 10. Predicted sim check

No baseline row exists (baseline covered Solace only), so this is estimated from the wheel and not measured.

| Tier | Turns | Win % | Why |
|---|---|---|---|
| T1 | 7–9 | 90–95 | 96 HP, intake 5–8 per turn |
| T2 | 8–10 | 90–93 | Relay and Flare tax grow |
| T3 | 10–12 | 85–90 | P3 Hotfix 4 per turn; enrage may touch a slow run |
| T4 | 12–14 | 70 | sim only |

The risk is T3: if the gate rule goes unread, P1 adds Overflows and the fight can pass turn 10.

## 11. Open questions

Q: Does the Countdown's extra Overflow at 3 stack with the Director's normal pointer resolve, or replace it? I assumed it adds a separate hit.
Q: Should a gate crossed by the Director's own orbit in P3 count, or only player crossings? I assumed only player nudges and spins.
Q: Do replaced Relays count as destroyed for Daemons like Botnet Seed? Assumed no.
Q: Is `cleanse_on_enter` = OWN on P3 right, or should P3 keep the Director's statuses so a Virus Exploit stays live?
Q: Are rim gates one set per wheel, or may the Director's gates also appear on the player's wheel in later tiers?
