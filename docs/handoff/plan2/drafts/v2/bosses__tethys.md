<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__bosses__tethys; status ok; tokens in 17106 cache-write 0 cache-read 32585 out 33689; cost $0.189. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Critic 1 (BLOCKER, boss phase HP vs thresholds; P2 sustain 1.5 vs 1.0).**
  - I re-derived every phase from `(18 × needles − sustain) × 3.5` with the sustains recomputed (P1 4.0, P2 1.0, P3 4.0, P4 2.0, P5 0). The budgets are 49 / 60 / 112 / 119 / 63, which sum to 403.
  - The thresholds are now 0.88 / 0.73 / 0.45 / 0.16, with floors of ceil(400 × t) = 352 / 292 / 180 / 64.
  - Phase HP is therefore 48 / 60 / 112 / 116 / 64, which sums to 400. Each phase is within 3 HP of its budget, and the table shows both columns.
  - P2 sustain is 1.0 everywhere, not 1.5. The gross value of 5/30 × 12 × 0.5 was already 1.0.
- **Critic 2 / triage row "all slices sum to 30" (labelled BLOCKER, but it reports no error).** Kept, because I re-added every layout and all of them sum to 30. The sums are now shown in the layout cells (for example "5+5+5+4+5+3+3 = 30"). No fix was needed.
- **Critic 3 (BLOCKER, Black Ink vs the P4 `cleanse_on_enter`).**
  - Transition order is now explicit: park → status remap (R6) → `cleanse_on_enter` → Black Ink.
  - The cleanse wipes the accumulated stacks. Black Ink then leaves exactly one residual TIER_DOWN stack, which is the buff's price.
  - Ink Filter removes the re-apply.
  - The "no RNG" line is clarified. The target is the player slice under pointer 1 and its clockwise neighbor at the moment of the phase change, which is deterministic. The respin that follows is the existing checkpointed event.
- **Critic 4 (MAJOR, mini-boss Gate double-count; floors vs P1 HP).**
  - The Gate's HP is now on top of the phase budget, as the critic ruled. P2 is therefore the full 31.5 at T1.
  - **Where I deviate from the critic's totals.** Re-adding gives T1 85 (26.25 + 31.5 + 28), T2 104 and T3 132, not the critic's T2 101 and T3 128. The critic's T2 and T3 totals do not follow from the formula: 31.7 + 38.5 + 34 = 104.2 and 40.3 + 49 + 43 = 132.3. T1 85 matches.
  - Thresholds are re-derived to 0.70 / 0.34 so the floor gaps match the budgets. At T1 the phases hold 25 / 31 / 29 against budgets of 26 / 31.5 / 28.
  - The Gate Jet intake is corrected to 0.4, because half the Gate's mini-wheel is Seal.
  - Mini-boss P3 `tide_set` is added, so the double-speed tide is always LOW / HIGH. Without it a RISING seed produced RISING / FALLING and the P3 design broke.
- **Critic 5 (MAJOR, P1 sustain cap on HIGH turns).** The Sea Wall is now PERCENT 2 % = 8 (16 at HIGH).
  - Sustain is 4.0 averaged over a tide cycle, against a cap of 5.4.
  - The HIGH-turn peak of 6.4 is stated openly as the designed "don't burst" turn.
  - A stored enemy shield cap of 4 % max HP (16) is added, as a placeholder (Q2).
- **Critic 6 (MAJOR, SANDBOX in P4/P5).**
  - SANDBOX is per resolution (per needle read).
  - P4 chain slices count as extra hits of the same resolution, so one SANDBOX negates a whole chain on that needle.
  - In P5 a single SANDBOX buys one turn of about 3.5, so steering is still required.
- **Critic 7 (MAJOR, TIDE fallback; conditional chain and Fuse cite N6/N20).**
  - Every TIDE consumer now has a fallback: a 2-state parity tide, with `tide_mask` / `tide_mult` cut where needed. This is listed for the boss and the whole roster in §5.
  - The chain rider is now N20 (`chain_next_if_status`) with N6. The Fuse is now N6 with N3 counters. Neither is NEW.
  - Only the clock and its fields remain NEW (no N# fits).
- **Critic 8 (NIT, Site names).** Kept, because the flag already confines them to art types.
- **Critic 9 (NIT, "five more pool Exploits").** The five non-gate Exploits are named in §1: Sluice Key, Hull Survey, Antifouling, Depth Recalibration and Ink Filter. A Grid still draws 5 of 8.
- **Critic Q1 (tide seed stream).** Decided, not left open. The start step is drawn once at `create_combat` from the named `combat` stream and stored in CombatState. It is saved with checkpoints, so rewind cannot reroll it.
- **Critic Q2 (enemy shield cap).** Decided as a placeholder: 4 % max HP for stored enemy shields. It remains as a designer question (Q2).
- **Own re-check of the roster.**
  - Diver Drone Torpedo raised to 6 so the stated threat of 1.6 is true.
  - Kelp Crawler Lash raised to 4, so threat is 1.6, and its HP is re-derived.
  - Pressure Sentinel HP dropped to the band floor. Resistance is a cost to the player, not a reason for more HP.
  - Pump Warden, Buoy Tender and Lamprey are re-derived to the band floors, because budget minus sustain lands below the floor.
  - Angler HP is recomputed (59 / 72 / 91 / 117).
  - Siphonophore P2 layout is now given in ticks.
- **Breathe Plan buff reduced.** Shield 3 % → 2 %, so its off-budget sustain is stated (about 3.3 per turn) and the Exploit's job is clear.

---

# Tethys Deep: corporation content draft (v2)

All numbers are placeholders pending the balance sim. Working names are placeholders. The reference player is `reference_dpt_by_tier` = [9, 11, 14, 18] over 3.5 turns per phase (R2). Enemy flat amounts are written at their T1 base and scale by [1.0, 1.3, 1.69, 2.2]. The boss is T4-only, so its values are shown at T4. A satellite's HP is on top of the host's phase budget.

---

## 1. Corporation identity summary

**What they sell.** The waterline and the air.
- The **BREATHE PLAN** keeps a ward dry. A lapse means the pumps are switched off.
- Cold storage (ATLANTIS) holds the city's backups.
- Air leases and fresh water are sold by the liter.

Their villainy is quiet: they never attack, they lower the water.

**House rule: TIDE.** A visible four-step clock: LOW, RISING, HIGH, FALLING. It advances one step per turn.
- **Start step.** Drawn once at `create_combat` from the named `combat` RNG stream and stored in CombatState. It is saved with checkpoints, so rewind cannot reroll it and preview equals result. The HUD shows the current and next step, as a number and a waterline mark, never color alone.
- **HIGH.** Tethys shield effects give ×2.
- **LOW.** Tethys stored shield drains by 3 (flat, × tier factor) at turn start. The drain removes only stored shield.
- **Enemy shield cap.** Stored enemy shield is capped at 4 % of max HP for PERCENT shields. For flat shields the cap is 2 × the largest flat shield on the wheel. Both are placeholders (Q2).
- **Per-slice and per-hub fields (new).**
  - `tide_mask`: the steps where the slice is live. A dead slice reads NULL.
  - `tide_mult`: a value multiplier at a step.
  - `tide_rate`: steps per turn.
  - `tide_hold`: freeze at a step while a satellite lives.
  - `tide_set`: force the step on phase entry.

**How it plays on the wheel.**
- The tide turns every enemy fight into a 4-turn rhythm, about one phase. The player learns three things:
  - HIGH is the turn to set up, SANDBOX or stall.
  - LOW is the turn to burst.
  - Some slices exist only on some steps, so the player steers the needle off the live ones.
- The same clock is the HQ's BALLAST TIDE: it floods and drains the drops between decks. The HQ route design is out of scope (D10, G12).

**Tone.** Spa-soft and clinical, lowercase, countdowns. Phase lines are service advisories ("your tide table has changed. breathe easy."). Phase transitions lower the water rather than spike it.

**Exploit trio and pool.** A Grid draws 5 of 8 (R7, `exploits_per_grid` = 5).

| Gate type | Flavor | What it counters (boss) |
|---|---|---|
| INTEL | Tide Tables | Deep Fog (hidden forecast and phases) |
| BREACH | Pump Override | Vent Pressure |
| VIRUS | Open Air (frees the air leases) | Breathe Plan |
| none | Sluice Key | Tide Lock |
| none | Hull Survey | Pressure Hull |
| none | Antifouling | Lamprey Swarm |
| none | Depth Recalibration | Crush Depth |
| none | Ink Filter | Black Ink |

**Raids: HIGH TIDES** (for the raid pass; not designed here).
- Threats are amphibious pods (fast, fragile) and flood barges (slow, high integrity damage).
- Raid steps carry a tide: threats gain +1 edge move at HIGH, and flooded links read as "closed".
- The after-action report is a FLOOD ADVISORY. The campaign-loss stamp is SUBMERGED.

**Story-path hooks.** One hidden path is picked at campaign start; beats unlock in Exploit order.
- **The Breathe Plan:** the lapse notices.
- **Ward Nine Floods:** the night the pumps went off.
- **Cold Storage:** whose memories sit in the pods.
- **The Cable Cut:** the sea cables as the arcology's leash.
- **Sunken Ghost:** foreshadows DISPATCH (a concierge that answers before it is asked).
- **Salvage Rights:** foreshadows the next corporation.

**Game-side flags (where the art identity needs a change).**
1. **SANDBOX name clash.** The art says "SANDBOX slices give double shield". Under R13, SANDBOX is now "negate a whole attack" and today's SANDBOX type is displayed as SHIELD. TIDE therefore keys on the *shield effect* (display SHIELD, data `SliceType.SANDBOX` / GAIN_SHIELD), never on the new SANDBOX.
2. **Boss rule on enemy wheels.** "Overclocks one of its own slices every turn" burns out into CORRUPTED. R9 retires CORRUPTED's damage, and V2 Q3 (CORRUPTED on enemy wheels) is unruled. The design assumes a burnt enemy slice has no penalty, so the overclock is a pure buff. The player counters by denying or cleansing it (Q1).
3. **TIDE is new** and has no N#. It needs a GDD line, a HUD chip (the boss wheel's tide gauge already has art direction) and a determinism test.
4. **Site-type names** (AIR LEASE, PUMP HOUSE, BUOY RELAY, COLD VAULT, TAP HOUSE, DOCK LOCK) conflict with the ruling "a Site is its type". Keep them as building and district art types only. The Site card reads Normal Fight, Elite Fight and so on.
5. **Lightless red vs HARM, and abyss blue vs Halcyon violet (ΔE 27).** This is art-side. Red stays material only.
6. **The flooded ward on the unified City Grid** is the art doc's open question. This draft assumes a flooded district of the one city.
7. **Octopus ink moves from boss P2 to P3.** The art says "phase 2: the hub inks black". Here ink is P3, the arms phase, and coral grows on the rim in P2.

---

## 2. Mini-boss: THE HARBORMASTER (working name)

**File:** `content/enemies/harbourmaster.tres` (id kept; guards the final Rack of every Tethys netrun at T1–T3).

**Identity and the one question.** It owns the tide.
- P1 asks: when does the wall stand?
- P2 asks: how do you take the tide away from it?
- P3 asks: how do you play a double-speed tide?

**Phase plan.** One needle at tick 0 throughout. Thresholds 0.70 / 0.34. Amounts are T1 base values.

| | P1 Slack Water (100 → 70 %) | P2 Sluice Lock (70 → 34 %) | P3 Ebb Run (34 → 0 %) |
|---|---|---|---|
| Needle | 1 (tick 0) | 1 (tick 0) | 1 (tick 0) |
| Layout (ticks, sum 30) | Breakwater 7 · Harpoon 5 · Breakwater 7 · Harpoon 5 · Gaff 6 (7+5+7+5+6 = 30) | Breakwater 8 *(Sluice Gate docked)* · Harpoon 6 · Gaff 5 · Null 6 · Harpoon 5 (8+6+5+6+5 = 30) | Flood 6 · Breakwater 5 · Harpoon 5 · Flood 6 · Breakwater 5 · Gaff 3 (6+5+5+6+5+3 = 30) |
| Breakwater (SHIELD, FLAT) | 4 | 4 | 4 |
| Harpoon (SHIM) | 5 | 5 | 5 |
| Gaff (SHIM) | 4 | 4 | 4 |
| Flood (OVERFLOW, FLAT) | n/a | n/a | 5; `tide_mult` ×2 at HIGH; dead (NULL) at LOW |
| Satellite | none | **Sluice Gate** docked on Breakwater (fixed). HP 6, mini-wheel 2 × 15 ticks: Seal (SHIELD 3 to host) / Jet (SHIM 3) | none |
| Tide rule | normal, 1 step per turn | **`tide_hold` = HIGH while a Sluice Gate lives.** A new Gate re-docks at turn start every 3rd turn if the slot is empty. | `tide_rate` = 2 and **`tide_set` = LOW on entry**: LOW, HIGH, LOW, HIGH. Visible a full turn ahead. |
| Hub | Tide (house) | Tide | Tide |

**Sustain and intake (T1).**
- **P1.** Breakwater covers 14 of 30 ticks. Gross shield is 14/30 × 4 × 1.25 = 2.3, and the LOW drain claws back about 0.8, so net sustain is about 1.5. That is within the cap of 30 % × 9 = 2.7. Intake: Harpoon 10/30 × 5 = 1.7 plus Gaff 6/30 × 4 = 0.8, so about 2.5.
- **P2.**
  - Sustain is 0 (the Gate is the buffer). With the tide held at HIGH the wall is ×2, but only matters if you strike it, and the Gate absorbs that hit.
  - Intake: Harpoon 11/30 × 5 = 1.8, Gaff 5/30 × 4 = 0.7, Gate Jet 8/30 × ½ × 3 = 0.4. Total about 2.9.
- **P3.**
  - Sustain: Breakwater covers 10 ticks. Average gross is 10/30 × 4 × 1.5 = 2.0, and the LOW drain on alternate turns leaves about 1.0 net.
  - Intake on a HIGH turn: Flood 12/30 × 10 = 4.0, Harpoon 5/30 × 5 = 0.8, Gaff 3/30 × 4 = 0.4, so about 5.2. On a LOW turn Flood is dead, so about 1.2. The average is about 3.2.

**HP by tier (R2: (ref − sustain) × 3.5 per phase).**

| Tier | P1 budget | P2 budget (Gate extra) | P3 budget | Total | Band (3-phase) |
|---|---|---|---|---|---|
| T1 (ref 9) | (9 − 1.5) × 3.5 = 26.25 | 31.5 | (9 − 1) × 3.5 = 28 | **85** | 85–105 ✓ |
| T2 (ref 11, ×1.3) | (11 − 1.95) × 3.5 = 31.7 | 38.5 | (11 − 1.3) × 3.5 = 34 | **104** | 104–128 ✓ |
| T3 (ref 14, ×1.69) | (14 − 2.5) × 3.5 = 40.3 | 49 | (14 − 1.7) × 3.5 = 43 | **132** | 132–162 ✓ |

- Totals are rounded to the nearest HP. Each total sits on its band floor, because the cheap sustain pulls it down.
- **Floors at 0.70 / 0.34** (ceil of max × next threshold):

| Tier | Floors | Phase HP | Budgets |
|---|---|---|---|
| T1 | 60 / 29 | 25 / 31 / 29 | 26 / 31.5 / 28 |
| T2 | 73 / 36 | 31 / 37 / 36 | 32 / 38.5 / 34 |
| T3 | 93 / 45 | 39 / 48 / 45 | 40 / 49 / 43 |

- **Gate HP (extra):** 6 / 8 / 10 (6 × 1.3 = 7.8, 6 × 1.69 = 10.1). It is optional to kill, but the tide stays frozen while it lives, so a real fight is about 10 turns.
- `hp_by_tier` = [85, 104, 132, n/a].

**Enrage.** Mini-boss default: turn 10, every 5, +25 % damage. The expected fight is about 10 turns, so only the first step is reachable, and only if the player stalls in P2.

**Counterplay per phase.**
- **P1:** hit on LOW and RISING turns. The wall is small, and the LOW drain clears stored shield. On HIGH turns, spend the free nudge to put the needle on Gaff or Harpoon, or set up cards.
- **P2:** the tide is stuck at HIGH, so bursting is pointless. Steer the needle (nudge, Spin, Freeze) onto the guarded Breakwater. The pointer rule sends your hit to the Gate, and killing it releases the tide next turn. You then have 2 turns before the re-dock. Plan the kill so the burst turns fall on FALLING and LOW. The Gate's Seal also shields the host, so killing it early is anti-sustain.
- **P3:** HIGH turns are the Flood turns. Spend them on defense and setup (SANDBOX the Flood, SHIELD, Cleanse, draw). LOW turns are free damage (Flood dead, shield drained). It is a rhythm, not attrition.

**Systems.**
- N1, N2, N3, N4.
- N13 (fixed satellite plus `on_occupied` REPLACE).
- **NEW: TIDE clock** (`tide_rate`, `tide_hold`, `tide_set`, `tide_mult`). Fallback: a 2-state tide by turn parity (LOW on even turns, HIGH on odd) read in the shield handler. It loses the seed, RISING / FALLING, `tide_set` and the P3 pacing, but P1–P3 still work: P3 becomes plain LOW / HIGH alternation, which is what it already is.
- Gate re-dock: an `ON_TURN_START` spawn from the hub (data-only if the existing satellite spawn can be hub-triggered; otherwise a small N13 add-on).

**Delta/notes.**
- Solace's mini-boss has guards then a counter, Halcyon's has status stacks, Meridian's has parasites, Orbital's has gates and REBEL_CELL's mirrors you. This is the only one that moves a global clock, and P2 asks you to attack the clock.
- "Hit the satellite on purpose" inverts the bodyguard lesson. The Gate preview should say "TIDE FROZEN" on the HUD chip.

---

## 3. Boss / Central Server: THE BLACK SMOKER

**Files:**
- `content/enemies/black_smoker.tres` (new boss id; Hub: THE VENT CAP).
- New slices `content/slices/bs_*.tres`: sea_wall, harpoon, vent_spit, thermal_jet, lamprey_launch, ink_burst, vent_blast, smoke_surge, exhale.

**Identity and the one question.** A vent that heats the water it sits in. Every turn it overclocks one of its own slices, and the tide decides how much that matters. It has five questions, one per phase:
- P1: read the tide.
- P2: which half of the wheel is alive?
- P3: how do you keep your Perfects under ink?
- P4: how do you stop the powder keg from chaining?
- P5: can you walk the fire order?

**Boss rule (Vent Pressure, hub).**
- At the end of each turn, after resolve, the Vent Cap overclocks the first non-NULL, not-yet-OVERCLOCKED slice clockwise from the one that just resolved at needle 1.
- The target is marked on the wheel one turn ahead (deterministic, visible).
- An OVERCLOCKED slice stays until it triggers (×1.5 once, then it burns out).
- Statuses survive phase changes (R6), so the powder keg carries over.
- The Pump Override Exploit turns this off.

**Transition order (every phase change).** Park at the floor (R3) → status remap (R6) → `cleanse_on_enter` → buff on-enter effects (Black Ink) → phase line and layout reveal.

### Phase table (T4 values; base in parentheses)

| | P1 Cold Vent | P2 Thermocline | P3 Plume | P4 Eruption | P5 Black Smoke |
|---|---|---|---|---|---|
| Threshold (floor = ceil(400 × t)) | 100 → 88 % (352) | 88 → 73 % (292) | 73 → 45 % (180) | 45 → 16 % (64) | 16 → 0 % (no floor) |
| Phase HP at 400 | 48 | 60 | 112 | 116 | 64 |
| R2 budget | 49 | 60 | 112 | 119 | 63 |
| Needles | 1 (tick 0) | 1 (tick 0) | 2: ticks 0 / 11 (uneven) | 2: ticks 0 / 13 | 1 (tick 0) |
| Layout (ticks, sum 30) | Sea Wall 6 · Harpoon 5 · Sea Wall 6 · Harpoon 5 · Vent Spit 4 · Null 4 (30) | Jet [WARM] 5 · Sea Wall [COLD] 5 · Harpoon [COLD] 5 · Lamprey Launch [WARM] 4 · Jet [WARM] 5 · Harpoon [COLD] 3 · Null 3 (30) | Ink Burst 4 · Sea Wall 4 · Jet 5 · Harpoon 4 · Lamprey Launch 4 · Ink Burst 4 · Jet 5 (30) | Vent Blast 5 · Harpoon 4 · Vent Blast 5 · Null 3 · Harpoon 4 · Sea Wall 3 · Vent Blast 6 (30) | Smoke Surge 7 · Exhale 5 · Smoke Surge 7 · Exhale 5 · Smoke Surge 6 (30) |
| Sea Wall (SHIELD, PERCENT of boss max HP) | 2 % = 8; HIGH ×2 = 16 | 3 % = 12 | 3 % = 12 | 2 % = 8 | none |
| Harpoon (SHIM, FLAT) | 3 (7) | 3 (7) | 3 (7) | 3 (7) | none |
| Vent Spit (SHIM, FLAT) | 4 (9) | none | none | none | none |
| Thermal Jet (OVERFLOW, FLAT) | none | 5 (11) | 5 (11) | none | none |
| Lamprey Launch | none | LATCH_PARASITE: Lamprey segment (4 ticks) on your wheel, max 2 | same | none | none |
| Ink Burst (INFECT) | none | none | TIER_DOWN ×1 on your slice under pointer 1 (stacks to ×2) | none | none |
| Vent Blast (OVERFLOW, FLAT) | none | none | none | 4 (9) | none |
| Smoke Surge (OVERFLOW, FLAT) | none | none | none | none | 8 (18) |
| Exhale | none | none | none | none | no effect; counts as fired for the Fuse |
| Hub rule | Vent Cap + Tide | Vent Cap + Tide; `tide_mask` splits the wheel | Vent Cap + Tide | Vent Cap + **Chain Eruption**: if a resolved slice is OVERCLOCKED, the next clockwise OVERCLOCKED slice also resolves (as extra hits of the same resolution) | Vent Cap overclocks **2** slices per turn + **Fuse**: a slice that fires again before all 5 have fired this round adds +25 % damage until the round completes |
| `cleanse_on_enter` | NONE | NONE | NONE | **PLAYER**: your Ink and TIER_DOWN stacks are wiped | NONE |
| Phase line | "your tide table has changed." | "the water is warm here." | "visibility is reduced." | "pressure is rising." | "breathe easy." |

**Tide-mask detail (P2).**
- WARM slices (Jet, Lamprey Launch) are live at RISING and HIGH only.
- COLD slices (Sea Wall, Harpoons) are live at LOW and FALLING only.
- A dead slice reads NULL, shown gray with its live steps on the label.
- Warm turns therefore bring 14 live ticks of Jets and Lamprey. Cold turns bring 13 live ticks of wall and Harpoons.

**P5 Fuse detail.** A round resets on phase entry. With one needle a round takes 5 resolves, longer than the phase, so the Fuse is almost always pending and the tracker shows which slices have fired. Landing on an unfired slice is free, and Exhale is always safe.

**Sustain and intake (T4).** Sustain is shield landing probability × value × average tide factor (1.25, from 1 / 1 / 2 / 1). The cap is 30 % of reference damage per needle (5.4).

| Phase | Sustain per turn | Cap | Intake before enrage |
|---|---|---|---|
| P1 | 12/30 × 8 × 1.25 = **4.0**. The HIGH-turn peak is 6.4, the designed "don't burst now" turn; the 4-turn average is under the cap. | 5.4 ✓ (average) | Harpoon 10/30 × 7 = 2.3, Vent Spit 4/30 × 9 = 1.2: **3.5**, rising to 4–5 with the overclock ratchet |
| P2 | 5/30 × 12 × 0.5 (live half the turns, multiplier 1 at LOW and FALLING) = **1.0** | ✓ | Warm: Jets 10/30 × 11 = 3.7 plus Lamprey reads ≈ 0.9 = ~4.6. Cold: Harpoons 8/30 × 7 = 1.9. |
| P3 | 2 × 4/30 × 12 × 1.25 = **4.0** | 10.8 for 2 needles ✓ | Jets 2 × 10/30 × 11 = 7.3, Harpoons 2 × 4/30 × 7 = 1.9, parasite reads ≈ 1.5: **~10.7** |
| P4 | 2 × 3/30 × 8 × 1.25 = **2.0** | ✓ | Blasts 2 × 16/30 × 9 = 9.6, Harpoons 2 × 8/30 × 7 = 3.7: **13.3** before chain and overclock |
| P5 | **0** | ✓ | Surges 20/30 × 18 = 12.0 base. With 2 overclocks per turn and Fuse steps it reaches 16–24. |

**HP by tier band (R2).** Phase budget = (18 × needles − sustain) × 3.5.

| Phase | Arithmetic | Budget | Phase HP at 400 (from the floors) |
|---|---|---|---|
| P1 | (18 − 4.0) × 3.5 | 49 | 48 |
| P2 | (18 − 1.0) × 3.5 | 59.5 → 60 | 60 |
| P3 | (36 − 4.0) × 3.5 | 112 | 112 |
| P4 | (36 − 2.0) × 3.5 | 119 | 116 |
| P5 | 18 × 3.5 | 63 | 64 |
| **Sum** | | **403** | **400** |

- The thresholds are chosen so every phase is within 3 HP of its budget. That is under 0.2 turn at the reference player, so no phase leaves the 3–4 turn window.
- **`hp_bands`** (ICE boss-strength zone ceiling → HP): ≤ 1.00 → **400**; ≤ 1.15 → **440**; ≤ 1.30 → **480**; > 1.30 → **530**.
- The threshold fractions are fixed, so phase HP scales proportionally with the band. Flat sustain does not scale, so phases run longer at high bands (Q3).
- **Fight length.** 5 phases × 3.5 ≈ 17.5 turns at the 400 band (class target 12–20 ✓). At 530 a phase takes about 4.6 turns and the fight about 23.

**Enrage.** Boss default: turn 10, every 5, +25 % damage, additive (R4).
- Expected path: turn 10 lands late in P3 (P3 runs about turns 7–10.5). Turn 15 lands in P5 (P5 starts about turn 14), giving ×1.5.
- The P5 Fuse is a boss-authored trigger and adds to the enrage steps rather than multiplying, so P5 is the high-water mark.

### Buffs and counter-Exploits (a Grid draws 5 of 8; ★ = signature)

| # | Buff (strong) | Effect | Counter Exploit | Gate |
|---|---|---|---|---|
| 1 ★ | **Vent Pressure** | The Vent Cap overclocks one slice per turn (2 in P5) | Pump Override | BREACH |
| 2 ★ | **Breathe Plan** | Each phase starts with SHIELD 2 % max HP (8); heals 1 % max HP (4) at turn start on HIGH | Open Air | VIRUS |
| 3 ★ | **Tide Lock** | The tide skips LOW (RISING, HIGH, FALLING loop), so there is no drain turn and fewer burst windows | Sluice Key | none |
| 4 | **Deep Fog** | The next tide step and the next layout stay hidden (the current turn's preview is exact) | Tide Tables | INTEL |
| 5 | **Pressure Hull** | Spin resistance by tide: LOW 0, RISING/FALLING 1, HIGH 3 (blocks Flip and Respin above 0) | Hull Survey | none |
| 6 | **Lamprey Swarm** | One Lamprey latches on your wheel at every phase start (max 2) | Antifouling | none |
| 7 | **Crush Depth** | At HIGH the boss's damage slices deal ×1.5 | Depth Recalibration | none |
| 8 | **Black Ink** | On every phase change, **after** `cleanse_on_enter`, applies TIER_DOWN ×1 to your slice under pointer 1 and its clockwise neighbor | Ink Filter | none |

**Notes on buffs.**
- **Off-budget by design (R7).**
  - Breathe Plan adds about 3.3 sustain per turn (8 per phase ÷ 3.5 = 2.3, plus 4 on one turn in four = 1.0), about 18 % of reference damage. Its HP is not in the budget, so it adds about 0.6 turn per phase.
  - Open Air is the answer. The sim should test the best and worst 5-buff draws.
- A route that draws only Tide Lock, Pressure Hull and Crush Depth makes HIGH hostile, so the strongest answer is a SANDBOX economy, not speed.
- **Black Ink and the P4 cleanse.**
  - The cleanse wipes the stacks accumulated in P1–P3.
  - Black Ink then leaves one residual stack on the pointer slice and its neighbor. That is the buff's price, and Ink Filter removes it. The cleanse is not cancelled.
  - Targets are the slices at pointer 1 when the phase changes, which is deterministic. The respin that follows is the existing checkpointed event.
- `min_exploits_for_breach = 3` stays.

### Counterplay per phase
- **P1:** hit on LOW and use the free nudge to put the needle on Null. Each overclock marker is a clock. A player who lets the overclock land on Sea Wall or Null wastes the boss's ratchet.
- **P2:** read the tide mask. On WARM turns put the needle on a dead cold slice or on Null (nudge, Spin). On COLD turns burst. Lampreys latch on warm turns, so steer your own wheel so they sit off your pointer, or Cleanse one (the cost is a card, the reward is no TIER_DOWN).
- **P3:** two needles hit you twice and hit the boss twice. The uneven gap lets you choose which needle reads the dangerous slice. Ink makes your Perfects Good, so land Good-and-safe rather than chase a Perfect. Spending a card to Cleanse mid-phase pays off only for Perfect-hook classes.
- **P4:** the player is the fuse. Overclock markers accumulate on Blasts, and a single OVERCLOCKED Blast chains into the next. Break the chain in one of three ways:
  - Cleanse an overclocked Blast (needs CLEANSE with WheelTarget ANY).
  - Nudge a needle so the overclocked slice is read on a Harpoon or Null, which burns it harmlessly.
  - SANDBOX the resolution. Chain slices are extra hits of the same resolution, so one SANDBOX negates the whole chain on that needle. With two needles the other needle is a separate resolution.
- **P5:** walk the Fuse. Use the free nudge to put the needle on an unfired slice (landing on Exhale is free). SANDBOX is per resolution, so one SANDBOX covers one turn of about 3.5. It cannot neutralize 2 overclocks per turn across the phase, so steering still decides. Finish before the turn-15 step.

### Systems
- N1, N2, N3, N4, N5, N19.
- N6: the Fuse round tracker (an ON_RESOLVE counter) and the chain condition. Fallback: P5 is a plain single-needle phase with enrage only.
- N20: new slice rider `chain_next_if_status` (the P4 chain). Fallback: RETRIGGER of the neighbor via `ON_SLICE_TRIGGER` if it supports an `if_status` condition. Otherwise P4 is plain 2-needle Blasts, which is weaker.
- N8 / N9: TIER_DOWN stacks, CORRUPTED as a RAM cost.
- N10: Parasite ring (Lamprey segments). Fallback: Lamprey Launch applies the PARASITE status (2-stack OUTPUT_DOWN).
- N11 (uneven needles), N12 (variable slice sizes; every layout uses 3–7 ticks), N13, N14.
- **NEW: TIDE clock** plus `tide_mask`, `tide_mult` and `tide_set`.
  - Fallback: a 2-state parity tide (LOW on even turns, HIGH on odd) in the shield handler, and masks cut.
  - Under that fallback P2 becomes a plain one-needle phase (WARM = HIGH, COLD = LOW can be kept if only the mask field survives).
  - Tide Lock, Deep Fog and Pressure Hull are cut or reduced to a fixed value.

### Delta/notes
- **Compared to the Genome Core.** It ramps defense away (heal → block → corruption). The Black Smoker never heals and keeps one question per phase on the tide clock. The Genome Core punishes your state (corruption count). The Smoker punishes your timing (tide) and your needle choice (chain, Fuse).
- **Octopus art.** Coral on the rim in P2, arms curling round the threat ring and ink in P3, vent mouths lighting for the P4 overclock glow.
- **Cleanse on enemy wheels** is assumed (CLEANSE with WheelTarget ANY). If not, P4 loses its direct cleanse answer; steering and SANDBOX remain.

---

## 4. Enemy roster sketch

Teaching order: the first three normals teach TIDE in L1–2 (shield, gated attack, satellite). The next two add statuses and tide-linked resistance in L2–4. The Lamprey brings the parasite ring in L3–5. Both elites run L3–6. The Harbormaster then uses TIDE hard.

### Normals (1 phase, 3–4 turns)

HP bands: T1 28–36, T2 34–44, T3 44–56, T4 56–70. Normal budget is ref × 3.5 = 31.5 / 38.5 / 49 / 63. Where budget minus sustain lands under the band floor, the floor wins (R2 validation).

| Working name | Layer role | The one question | Wheel sketch (ticks sum 30; one needle) | HP T1/T2/T3/T4 | N# needed |
|---|---|---|---|---|---|
| **Pump Warden** | Teach (L1–2) | Hit when the water is low: the wall doubles at HIGH and drains at LOW | Seawall (SHIELD 2) 8 · Spanner (SHIM 3) 7 · Seawall 8 · Spanner 7 (30) | 28 / 34 / 44 / 56 | N1, N2, TIDE |
| **Diver Drone** | Teach (L1–2) | Is the Torpedo live this turn? Read the tide and keep the needle off it | Torpedo (OVERFLOW 6; live RISING/HIGH, dead otherwise) 4 · Dart (SHIM 2) 6 · Null 5 · Torpedo 4 · Dart 6 · Bubble Screen (BLOCK 3) 5 (30) | 30 / 36 / 46 / 59 | N1, N2, TIDE (`tide_mask`) |
| **Buoy Tender** | Teach (L2) | Dig through the bodyguard or steer round it? It also teaches that a satellite is fixed | Cannon (OVERFLOW 4, **Marker Buoy** docked) 6 · Net (BLOCK 3) 6 · Harpoon (SHIM 3) 6 · Net 6 · Null 6 (30). Buoy: HP 3/4/5/7; mini-wheel Flash SHIM 1 / Float SHIELD 2 to host | 28 / 34 / 44 / 56 (host; the Buoy is on top) | N13, TIDE (Float ×2 at HIGH) |
| **Kelp Crawler** | Pressure (L2–3) | Rotate off the stacked slice or Cleanse now? Statuses cost output, not actions | Entangle (INFECT: OUTPUT_DOWN ×1 on your slice under the pointer; ×2 at HIGH) 6 · Lash (SHIM 4) 6 · Entangle 6 · Null 6 · Lash 6 (30) | 30 / 37 / 46 / 60 | N8, N9, TIDE (`tide_mult`); fallback: today's PARASITE status (2-stack OUTPUT_DOWN) |
| **Pressure Sentinel** | Pressure (L3–4) | Nudge it at LOW, when it moves freely, because at HIGH it is locked | Crush (OVERFLOW 5) 6 · Plate (BLOCK 4) 6 · Crush 6 · Plate 6 · Null 6 (30). Resistance by tide: LOW 0, RISING/FALLING 1, HIGH 3 | 28 / 34 / 44 / 56 | N2, TIDE (tide-linked resistance on the hub); fallback: fixed resistance 2 |
| **Lamprey** | Pressure (L3–5) | Kill it before it latches, or pay a Cleanse to remove the parasite after? | Latch (LATCH_PARASITE: Lamprey segment, 3 ticks; read: 2 damage + TIER_DOWN ×1) 5 · Bite (SHIM 2) 5 · Slither (SANDBOX: negates one whole attack) 5 · Latch 5 · Bite 5 · Null 5 (30) | 28 / 34 / 44 / 56 | N10, N8, N9, N14; fallback: Latch applies the PARASITE status |

**HP arithmetic** (T1; ×1.3 / ×1.69 / ×2.2 for sustain on later tiers).
- **Pump Warden:** sustain 16/30 × 2 × 1.25 = 1.3 per turn at T1. T1 budget (9 − 1.3) × 3.5 = 27, so the floor of 28 wins. T2 (11 − 1.7) × 3.5 = 32 → 34. T3 (14 − 2.2) × 3.5 = 41 → 44. T4 (18 − 2.9) × 3.5 = 53 → 56.
- **Diver Drone:** sustain is the Bubble Screen, 5/30 × 3 = 0.5. T1 (9 − 0.5) × 3.5 = 29.75 → 30. T2 (11 − 0.65) × 3.5 = 36. T3 (14 − 0.85) × 3.5 = 46. T4 (18 − 1.1) × 3.5 = 59.
- **Buoy Tender:** sustain Net 12/30 × 3 = 1.2 plus Float 6/30 × ½ × 2 × 1.25 = 0.25, total 1.45. T1 (9 − 1.45) × 3.5 = 26.4 → 28. T2 31.8 → 34. T3 40.4 → 44. T4 51.8 → 56. All at the floor; the satellite HP is extra.
- **Kelp Crawler:** no sustain. Its OUTPUT_DOWN stacks cut the player's damage by about 5 %, so HP is 95 % of budget: 30 / 37 / 46 / 60.
- **Pressure Sentinel:** sustain Plate 12/30 × 4 = 1.6, so T1 (9 − 1.6) × 3.5 = 26 → floor 28. Tide-linked resistance is a cost to the player's nudges and is not compensated with HP.
- **Lamprey:** sustain is the Slither's negation (about 0.5 equivalent), so T1 about 30 → clamp. The floor 28 is used because the latch outlives the Lamprey.

**Intake per turn at T1 (every normal > 0).**

| Enemy | Intake |
|---|---|
| Pump Warden | Spanner 14/30 × 3 = 1.4 |
| Diver Drone | Torpedo 8/30 × 6 × ½ live = 0.8 + Dart 12/30 × 2 = 0.8, so 1.6 |
| Buoy Tender | Cannon 6/30 × 4 + Harpoon 6/30 × 3 = 1.4 + Flash 0.1 |
| Kelp Crawler | Lash 12/30 × 4 = 1.6 + the OUTPUT_DOWN tax |
| Pressure Sentinel | Crush 12/30 × 5 = 2.0 |
| Lamprey | Bite 10/30 × 2 = 0.7 + parasite reads |

### Elites (2 phases, 6–8 turns)

Single-needle by design. Bands: T1 56–72, T2 68–88, T3 88–112, T4 112–144.

| Working name | Layer role | The one question (P1 → P2) | Wheel sketch (ticks sum 30) | HP T1/T2/T3/T4 | N# |
|---|---|---|---|---|---|
| **Siphonophore** | Pressure (L3–6) | P1: which end of the chain do you cut? → P2: the chain breaks and replaces itself, so steer around, don't kill | P1 (100 → 55 %): Sting (SHIM 3) 6 · Zooid-host 6 · Zooid-host 6 · Zooid-host 6 · Null 6 (30). 3 chained **Zooid** satellites (HP 4/5/7/9; mini-wheel 2 × 15: Shield 2 to the next zooid / Stinger SHIM 2). Killing the middle one cuts the chain. P2 (55 → 0 %): Sting (OVERFLOW 5) 6 · Zooid-host 6 · Sting 6 · Jab (SHIM 3) 6 · Null 6 (30). The chain is gone. Each turn a new Zooid launches onto a slice and **replaces** any satellite there. | 58 / 70 / 89 / 114 | N13 (REPLACE), N3, TIDE (Zooid shield ×2 at HIGH) |
| **Angler** | Pressure (L3–6) | P1: plan two turns ahead, because the lantern needle sweeps and can't be held → P2: its jaws open only when the tide is not HIGH, so pick your rhythm | P1 (100 → 50 %): needle **ORBIT** +5 ticks per turn (trail shows future positions). Bite (OVERFLOW 5) 5 · Snap (SHIM 3) 5 · Lure (INFECT: TIER_DOWN ×1 on your slice) 5 · Snap 5 · Gill (SHIELD 3) 5 · Null 5 (30). P2 (50 → 0 %): orbit stops. Bite 7 · Gill 4 · Bite 7 · Snap 5 · Lure 3 · Null 4 (30). **Bite dead at HIGH** (`tide_mask`), Gill ×2 at HIGH. | 59 / 72 / 91 / 117 | N3, N9, TIDE (`tide_mask`); ORBIT exists |

**Elite arithmetic** (HP = (ref − sustain) × 3.5 per phase, summed).
- **Siphonophore:**
  - Sustain 1.5 at T1 from the zooid shields (not scaled for the elite's P2, where there is none).
  - T1: P1 (9 − 1.5) × 3.5 = 26 plus P2 31.5 = 58. The floor is ceil(58 × 0.55) = 32, so P1 holds 26 ✓.
  - T2: 31.7 + 38.5 = 70. T3: 40 + 49 = 89. T4: sustain 3.3, (18 − 3.3) × 3.5 = 51.5, plus 63 = 114.
  - P1 intake about 1.2 (Sting 0.6 plus zooid stingers 0.6). P2 about 2.8 (Sting 2.0, Jab 0.6, new zooid 0.2).
- **Angler:**
  - P1 sustain: Gill 5/30 × 3 × 1.25 = 0.63. P2: 4/30 × 3 × 1.25 = 0.5.
  - T1: 29.3 + 29.75 = 59. T2 (sustain 0.82 / 0.65): 35.6 + 36.2 = 72. T3 (1.06 / 0.85): 45.3 + 46 = 91. T4 (1.39 / 1.1): 58.1 + 59.1 = 117.
  - Intake: P1 Bite 5/30 × 5 + Snap 10/30 × 3 = 1.8. P2 Bite 14/30 × 7 × ¾ live + Snap 0.5 = 3.0.
- Both use the elite default enrage (turn 8, every 5, +25 %). Both retire their `heat_effects`; the phase is the pressure now.

---

## 5. Systems needed

| # | System | Used by |
|---|---|---|
| N1 | Amount modes (FLAT / PERCENT) | all (shields as PERCENT on the boss) |
| N2 | Tier base-value tables, `hp_by_tier`, `hp_bands` | all |
| N3 | Phases on every class, parking, status keep, `cleanse_on_enter` | mini-boss, boss, elites |
| N4 | Enrage | mini-boss, boss, elites |
| N5 | Boss buffs and Exploits | boss |
| N6 | Enemy listeners / round counters | boss P5 Fuse, P4 chain condition |
| N8, N9 | ×N stacks; OUTPUT_DOWN, TIER_DOWN, CORRUPTED as a RAM cost | Kelp Crawler, Lamprey, Angler, boss |
| N10 | Parasite ring | Lamprey, boss P2–P3 |
| N11 | Pointers on any tick | boss P3 / P4 |
| N12 | Variable slice sizes (3–8 ticks) | every layout here |
| N13 | Fixed satellites + replacement | Buoy Tender, mini-boss P2, Siphonophore |
| N14 | Defense trio (SANDBOX negates a whole resolution) | Lamprey, boss P4–P5 counterplay |
| N19 | Sim metrics (turns per phase, tide step, enrage step) | verification |
| N20 | Slice rider `chain_next_if_status` | boss P4 |
| **NEW** | **TIDE clock** (seeded step, advance, HUD chip, `tide_rate`, `tide_hold`, `tide_set`) | everything |
| **NEW** | **Tide-conditioned fields** (`tide_mask`, `tide_mult`, tide-linked resistance) | Diver, Sentinel, boss P2, Angler |

**Fallbacks (a corporation-level summary).**
- **TIDE clock.** A 2-state parity tide (LOW on even turns, HIGH on odd) read in the shield handler. It loses the seed, RISING / FALLING, `tide_set` and the HUD step number.
- **Tide-conditioned fields.** Cut them if the clock is reduced to parity. The effect:
  - Pump Warden and Buoy Tender still work (shield ×2 at HIGH and drain at LOW).
  - Diver Drone's Torpedo is live on HIGH only.
  - Sentinel gets a fixed resistance of 2.
  - Angler and boss P2 become one-needle plain phases.
- **N10.** Falls back to the PARASITE status.
- **N6 / N20.** Fall back as described in §3.

**Build order.**
1. Foundation: N1 → N2 → N3 → N4 → N19, with N11, N13, N14 in parallel.
2. **TIDE clock** right after N3. It is cheap and unblocks every normal. The first three normals (Pump Warden, Diver Drone, Buoy Tender) are data-only once the clock exists.
3. N12 starts early (the longest).
4. N8 → N9 → Kelp Crawler, Sentinel, Lamprey fallback (PARASITE status).
5. Harbormaster (needs the clock, N13, N3, N4).
6. N5, N10 → full Lamprey, Siphonophore, Angler.
7. Boss: N6 / N20 chain and Fuse last.

If the clock is cut entirely, nothing here survives, so the clock is the corporation's single point of failure. The parity fallback is the floor, not the plan.

---

## 6. Open questions
Q: Enemy CORRUPTED (V2 Q3): the boss assumes a burnt-out enemy slice has no penalty, so Vent Pressure is a pure buff. Should a burnt-out enemy slice instead read at −25 % (OUTPUT_DOWN ×1) for one turn, as a small reward for letting the overclock land?
Q: Enemy shield cap: this draft uses 4 % max HP for stored PERCENT shields (16 at 400) and 2 × the largest flat shield for flat ones. Is that the right shape, or should it be one cap like the player's `shield_cap` = 15?
Q: Is the high-ICE boss length acceptable (about 23 turns at the 530 band), or should the top band cut P1–P2 HP and keep P3–P5 HP so the extra length is spent on the late phases?
Q: Should the player ever read the tide as a tool (a Firmware or Daemon that nudges the tide one step or shows the next two)? As written the tide is information only.
Q: Should Tide Lock (buff 3) skip LOW in the HQ's BALLAST TIDE too, so one Exploit is felt on the map and in the fight? That depends on the unified-city ruling (flooded district of one model); if Tethys is a separate map, the HQ and raid use of the clock needs a new ruling.
