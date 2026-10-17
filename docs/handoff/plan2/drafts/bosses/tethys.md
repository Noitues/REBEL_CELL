<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01J5ExrMJuh8Bpj1cDjmAiwa, custom_id corp__tethys; status ok; tokens in 10248 cache-write 0 cache-read 32007 out 51966; cost $0.273. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Tethys Deep: corporation content draft

All numbers are placeholders pending the balance sim. Working names are placeholders. The reference player is `reference_dpt_by_tier` = [9, 11, 14, 18] over 3.5 turns per phase (R2). Enemy flat amounts are written at their T1 base and scale by [1.0, 1.3, 1.69, 2.2]. The boss is T4-only, so its values are shown at T4.

---

## 1. Corporation identity summary

**What they sell.** The waterline and the air.
- The **BREATHE PLAN** keeps a ward dry; a lapse means the pumps are switched off.
- Cold storage (ATLANTIS) holds the city's backups.
- Air leases and fresh water by the litre.

Their villainy is quiet: they never attack, they lower the water.

**House rule: TIDE.** A visible four-step clock: LOW, RISING, HIGH, FALLING. It advances one step per turn.
- **Start step.** Seeded at fight start from the checkpointed combat RNG stream. The HUD shows the current and next step, so preview equals result.
- **HIGH.** Tethys SHIELD slices give ×2.
- **LOW.** Tethys shield drains by 3 (flat, ×tier factor) at turn start.
- **Per-slice and per-hub hooks (new).** An enemy slice may carry `tide_mask` (the steps where it is live; dead reads as NULL) and `tide_mult` (value multiplier at a step). A hub or phase may set `tide_rate` (steps per turn) and `tide_hold` (freeze while a satellite lives).

**How it plays on the wheel.**
- The tide turns every enemy fight into a 4-turn rhythm, which is about one phase (3–4 turns). The player learns three things:
  - HIGH is the turn to set up, SANDBOX or stall.
  - LOW is the turn to burst.
  - Some slices only exist on some steps, so the player steers the needle off the live ones.
- The same clock is the HQ's BALLAST TIDE: it floods and drains the drops between decks. The HQ netrun's route design is out of scope here (D10, G12).

**Tone.** Spa-soft and clinical, lowercase, countdowns. Phase lines are service advisories ("your tide table has changed. breathe easy."). Phase transitions lower the water rather than spike it.

**Exploit trio.**

| Gate type | Flavour | What it counters (boss) |
|---|---|---|
| INTEL | Tide Tables | Deep Fog (hidden forecast and phases) |
| BREACH | Pump Override | Vent Pressure (the Vent Cap breach) |
| VIRUS | Open Air (frees the air leases) | Breathe Plan |

Five more pool Exploits exist (section 3), so a Grid draws 5 of 8.

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
1. **SANDBOX name clash.** The art says "SANDBOX slices give double shield". Under R13, SANDBOX now means "negate a whole attack" and today's SANDBOX type is displayed as SHIELD. TIDE therefore keys on the *shield effect* (display SHIELD), never on the new SANDBOX. Data-wise it keys on `SliceType.SANDBOX` / GAIN_SHIELD.
2. **Boss rule on enemy wheels.** "Overclocks one of its own slices every turn" burns out into CORRUPTED. R9 retires CORRUPTED's damage, and Q3 (CORRUPTED on enemy wheels) is unruled. The design assumes a scorched slice has no penalty for the boss, so the overclock is a pure buff. The player counters by denying or cleansing it. See Q1.
3. **TIDE is new** and has no N#. It needs a GDD line, a HUD chip (the boss wheel's tide gauge already has art direction) and a determinism test.
4. **Site-type names** (AIR LEASE, PUMP HOUSE, BUOY RELAY, COLD VAULT, TAP HOUSE, DOCK LOCK) conflict with the ruling "a Site is its type". Keep them as building/district art types only; the Site card reads Normal Fight, Elite Fight and so on.
5. **Lightless red vs HARM and abyss blue vs Halcyon violet (ΔE 27).** This is art-side. Keep red as material only. In-game, tide state must always have a second cue (the numbered step and the waterline), never colour alone.
6. **The flooded ward on the unified City Grid** is the art doc's open question. This draft assumes a flooded district of the one city.
7. **Octopus ink moves from boss P2 to P3.** The art says "phase 2: the hub inks black". Here ink is P3, the arms phase, and coral grows on the rim in P2. This matches idea 4 in the art notes.

---

## 2. Mini-boss: THE HARBOURMASTER (working name)

**File:** `content/enemies/harbourmaster.tres` (guards the final Rack of every Tethys netrun at T1–T3).

**Identity and the one question.** It owns the tide. P1 asks: when does the wall stand? P2 asks: how do you take the tide away from it? P3 asks: how do you play a double-speed tide?

**Phase plan.** Single needle at tick 0 throughout; thresholds 0.66 / 0.33. Amounts are T1 base values.

| | P1 Slack Water (100 → 66 %) | P2 Sluice Lock (66 → 33 %) | P3 Ebb Run (33 → 0 %) |
|---|---|---|---|
| Needle | 1 (tick 0) | 1 (tick 0) | 1 (tick 0) |
| Layout (ticks, sum 30) | Breakwater 7 · Harpoon 5 · Breakwater 7 · Harpoon 5 · Gaff 6 | Breakwater 8 *(Sluice Gate docked)* · Harpoon 6 · Gaff 5 · Null 6 · Harpoon 5 | Flood 6 · Breakwater 5 · Harpoon 5 · Flood 6 · Breakwater 5 · Gaff 3 |
| Breakwater (SHIELD, FLAT) | 4 | 4 | 4 |
| Harpoon (SHIM) | 5 | 5 | 5 |
| Gaff (SHIM) | 4 | 4 | 4 |
| Flood (OVERFLOW) | n/a | n/a | 5; `tide_mult` ×2 at HIGH; dead (NULL) at LOW |
| Satellite | none | **Sluice Gate** docked on Breakwater (fixed). HP 6, mini-wheel 2 × 15 ticks: Seal (SHIELD 3 to host) / Jet (SHIM 3) | none |
| Tide rule | normal, 1 step/turn | **tide frozen at HIGH while a Sluice Gate lives.** A new Gate re-docks every 3rd turn if the slot is empty. | `tide_rate` = 2: LOW, HIGH, LOW, HIGH. Visible a full turn ahead. |
| Hub | Tide (house) | Tide | Tide |

**Sustain and intake (T1).**
- **P1:** Breakwater lands on 14/30 of the wheel. Shield 4 × average tide multiplier 1.25 × 0.47 ≈ 2.3. The LOW drain claws back about 0.8, so net sustain ≈ 1.5 per turn (≤ 30 % of 9 = 2.7 ✓). Intake: Harpoon (10/30 × 5) + Gaff (6/30 × 4) = 1.7 + 0.8 ≈ 2.5 (target 2–4 ✓).
- **P2:** sustain 0 (the Gate is the buffer; with the tide frozen HIGH the wall is ×2 but only matters if you strike the Breakwater, where the Gate absorbs the hit). Intake: Harpoon 11/30 × 5 = 1.8, Gaff 5/30 × 4 = 0.7, Gate Jet 8/30 × 3 = 0.8, total ≈ 3.3.
- **P3:** sustain about 1. Flood hits 12/30 × 5 = 2 at LOW-dead... precisely, at HIGH ×2: 12/30 × 10 = 4. Plus Harpoon 0.8 and Gaff 0.4. Intake ≈ 3 on LOW turns and ≈ 5 on HIGH turns (target 3–6 ✓).

**HP by tier (R2 budget: ref × 3.5 per phase, minus sustain × 3.5, minus satellite HP).**
- **T1** (ref 9, 31.5 per phase):
  - P1: (9 − 1.5) × 3.5 = 26.
  - P2: 31.5 − Gate 6 = 25.5.
  - P3: (9 − 1) × 3.5 = 28.
  - Total **80** boss HP (floors at 0.66 / 0.33 → 53 / 27), plus a 6 HP Gate. The pool of 86 sits on the 3-phase band floor (85–105).
- **T2** (ref 11, 38.5; flat amounts ×1.3): P1 (11 − 1.95) × 3.5 = 31.7; P2 38.5 − 8 = 30.5; P3 (11 − 1.3) × 3.5 = 34 → **96** (Gate 8; pool 104 ✓).
- **T3** (ref 14, 49; ×1.69): P1 (14 − 2.5) × 3.5 = 40; P2 49 − 10 = 39; P3 (14 − 1.7) × 3.5 = 43 → **122** (Gate 10; pool 132 ✓).
- `hp_by_tier` = [80, 96, 122, n/a].

**Enrage.** Mini-boss default: turn 10, every 5, +25 % damage. Expected fight is 10.5 turns, so only the first step is reachable, and only if the player stalls in P2.

**Counterplay per phase.**
- **P1:** hit on LOW and RISING turns (the wall is small, and the LOW drain clears stored shield); on HIGH turns spend the free nudge to put the needle on Gaff or Harpoon, or SANDBOX nothing and set up cards.
- **P2:** the tide is stuck at HIGH, so it is useless to burst. Steer the needle (nudge, Spin, Freeze) onto the guarded Breakwater. The pointer rule sends your hit to the Gate, and killing it releases the tide next turn. You then have 2 turns before the re-dock. Plan the kill so the burst turns land on FALLING and LOW. The Gate's Seal also shields the host, so killing it early is also anti-sustain.
- **P3:** HIGH turns are the Flood turns. Spend them on defense and setup (SANDBOX the Flood, SHIELD, Cleanse, draw). LOW turns are free damage (Flood dead, shield drained). The question is a rhythm, not attrition.

**Systems.**
- N1, N2, N3, N4.
- N13 (fixed satellite + `on_occupied` REPLACE).
- **NEW: TIDE clock** (with `tide_rate`, `tide_hold`, `tide_mult`). No data-only fallback for the clock. Cheapest fallback: a 2-state tide by turn parity read inside the shield handler, which loses the seed and the RISING/FALLING steps.
- Gate re-dock timer: `ON_TURN_START` spawn effect (data-only if the existing satellite spawn can be hub-triggered; otherwise a small N13 add-on).

**Delta/notes.** Compared with the old mini-bosses: Solace's has guards then a counter, Halcyon's has status stacks, Meridian's has parasites, Orbital's has gates, REBEL_CELL's mirrors you. This one is the only mini-boss that moves a global clock, and P2 asks you to attack the *clock*. Note that "hit the satellite on purpose" inverts the usual bodyguard lesson; the Sluice Gate preview should say "TIDE FROZEN" on the HUD chip.

---

## 3. Boss / Central Server: THE BLACK SMOKER

**Files:**
- `content/enemies/black_smoker.tres` (new boss id; Hub: THE VENT CAP)
- new slices `content/slices/bs_*.tres` (sea_wall, harpoon, vent_spit, thermal_jet, lamprey_launch, ink_burst, vent_blast, smoke_surge, exhale)

**Identity and the one question.** A vent that heats the water it sits in. Every turn it overclocks one of its own slices, and the tide decides how much that matters. The fight is a progression of five questions:
- P1: read the tide.
- P2: which half of the wheel is alive?
- P3: how do you keep your Perfects under ink?
- P4: how do you stop the powder keg from chaining?
- P5: can you walk the fire order?

**Boss rule (Vent Pressure, hub).** At the end of each turn, after resolve, the Vent Cap overclocks the first non-NULL, not-yet-OVERCLOCKED slice clockwise from the one that just resolved at needle 1. The target is marked on the wheel one turn ahead (deterministic, visible). OVERCLOCKED slices stay until they trigger (×1.5 once, then burn). Statuses survive phase changes (R6), so the powder keg carries over. The Pump Override Exploit turns this off.

### Phase table (T4 values; base in parentheses)

| | P1 Cold Vent | P2 Thermocline | P3 Plume | P4 Eruption | P5 Black Smoke |
|---|---|---|---|---|---|
| Threshold (HP floor at 400) | 100 → 89 % (356) | 89 → 74 % (296) | 74 → 46 % (184) | 46 → 16 % (64) | 16 → 0 % (no floor) |
| Needles | 1 (tick 0) | 1 (tick 0) | 2: ticks 0 / 11 (uneven) | 2: ticks 0 / 13 | 1 (tick 0) |
| Layout (ticks, sum 30) | Sea Wall 6 · Harpoon 5 · Sea Wall 6 · Harpoon 5 · Vent Spit 4 · Null 4 | Jet [WARM] 5 · Sea Wall [COLD] 5 · Harpoon [COLD] 5 · Lamprey Launch [WARM] 4 · Jet [WARM] 5 · Harpoon [COLD] 3 · Null 3 | Ink Burst 4 · Sea Wall 4 · Jet 5 · Harpoon 4 · Lamprey Launch 4 · Ink Burst 4 · Jet 5 | Vent Blast 5 · Harpoon 4 · Vent Blast 5 · Null 3 · Harpoon 4 · Sea Wall 3 · Vent Blast 6 | Smoke Surge 7 · Exhale 5 · Smoke Surge 7 · Exhale 5 · Smoke Surge 6 |
| Sea Wall (SHIELD, PERCENT of boss max HP) | 2.5 % = 10; HIGH ×2 | 3 % = 12 | 3 % = 12 | 2 % = 8 | none |
| Harpoon (SHIM, FLAT) | 3 (7) | 3 (7) | 3 (7) | 3 (7) | none |
| Vent Spit (SHIM, FLAT) | 4 (9) | none | none | none | none |
| Thermal Jet (OVERFLOW, FLAT) | none | 5 (11) | 5 (11) | none | none |
| Lamprey Launch | none | LATCH_PARASITE: Lamprey segment (4 ticks) on your wheel, max 2 | same | none | none |
| Ink Burst (INFECT) | none | none | TIER_DOWN ×1 on the slice under your pointer (stacks to ×2) | none | none |
| Vent Blast (OVERFLOW, FLAT) | none | none | none | 4 (9) | none |
| Smoke Surge (OVERFLOW, FLAT) | none | none | none | none | 8 (18) |
| Hub rule | Vent Cap + Tide | Vent Cap + Tide; **`tide_mask`** splits the wheel | Vent Cap + Tide; **ink** on entry | Vent Cap + **Chain Eruption**: if a resolved slice is OVERCLOCKED, the next clockwise OVERCLOCKED slice also resolves | Vent Cap overclocks **2** slices/turn + **Fuse**: a slice that fires again before all 5 have fired this round adds +25 % damage until the round completes |
| `cleanse_on_enter` | NONE | NONE | NONE | **PLAYER** (the plume clears: your ink and TIER_DOWN stacks wiped) | NONE |
| Phase line | "your tide table has changed." | "the water is warm here." | "visibility is reduced." | "pressure is rising." | "breathe easy." |

**Tide-mask detail (P2).** WARM slices (Jet, Lamprey Launch) are live at RISING and HIGH only; COLD slices (Sea Wall, Harpoons) are live at LOW and FALLING only. A dead slice reads NULL, shown greyed with its live steps on the label. So warm turns bring Jets (14 live ticks) and cold turns bring wall and harpoons (13 live ticks).

**Sustain and intake (T4).** Each step is shown as shield landing probability × value × tide factor.

| Phase | Sustain (per turn) | 30 % cap (5.4 per needle) | Intake before enrage |
|---|---|---|---|
| P1 | Sea Wall 12/30 × 10 × 1.25 = 5.0 | ✓ | Harpoon 10/30 × 7 = 2.3, Vent Spit 4/30 × 9 = 1.2: 3.5 (target 3–6; 4–5 with a ratcheting overclock) |
| P2 | Sea Wall live half the time: 5/30 × 12 × 0.5 ≈ 1.0 (rounded 1.5 with HIGH carry) | ✓ | Warm: Jets 10/30 × 11 = 3.7 + Lamprey reads ≈ 0.9: ~4.6. Cold: Harpoons 8/30 × 7 = 1.9. Peak target 4–8 ✓ |
| P3 | Sea Wall 2 needles: 2 × 4/30 × 12 × 1.25 = 4.0 | ✓ (2 needles → cap 10.8) | Jets 2 × 10/30 × 11 = 7.3, Harpoons 2 × 4/30 × 7 = 1.9, parasite reads ≈ 1.5: ~10.7 (target 9–12 ✓) |
| P4 | Sea Wall 2 × 3/30 × 8 × 1.25 = 2.0 | ✓ | Blasts 2 × 16/30 × 9 = 9.6, Harpoons 2 × 8/30 × 7 = 3.7: 13.3 before chain and overclock (target 12–16, rising with the ratchet) |
| P5 | 0 | ✓ | Surges 20/30 × 18 = 12.0 base; with 2 overclocks per turn and Fuse steps it reaches 16–24, so SANDBOX on the right turn is the answer |

**HP by tier band (R2).** Phase HP = (ref 18 × needles − sustain) × 3.5:

| Phase | Arithmetic | HP |
|---|---|---|
| P1 | (18 − 5) × 3.5 | 46 |
| P2 | (18 − 1.5) × 3.5 | 58 |
| P3 | (36 − 4) × 3.5 | 112 |
| P4 | (36 − 2) × 3.5 | 119 |
| P5 | 18 × 3.5 | 63 |
| **Sum** | | **398 ≈ 400** |

- **`hp_bands`** (ICE boss-strength zone ceiling → HP): ≤ 1.00 → **400**; ≤ 1.15 → **440**; ≤ 1.30 → **480**; > 1.30 → **530**.
- **Thresholds** (fractions fixed; the floor scales with the band): 0.89 / 0.74 / 0.46 / 0.16. At 400 the phases hold 44 / 60 / 112 / 120 / 64 HP.
- **Fight length.** 5 phases × 3.5 ≈ 17.5 turns (class target 12–20 ✓). At the 530 band a phase reaches about 4.6 turns and the fight ~23, so the enrage steps do the work at high ICE. See Q3.

**Enrage.** Boss default (turn 10, every 5, +25 % damage, additive). Expected path: turn 10 lands late P3, turn 15 at the start of P5 (×1.5). The P5 Fuse is a boss-authored trigger that stacks with it, so P5 is the high-water mark. Enrage and Fuse add together, not multiply.

### Buffs and counter-Exploits (a Grid draws 5 of 8; ★ = signature; gate = fixed gate type)

| # | Buff (strong) | Effect | Counter Exploit | Gate |
|---|---|---|---|---|
| 1 ★ | **Vent Pressure** | The Vent Cap overclocks one slice per turn (2 in P5) | Pump Override | BREACH |
| 2 ★ | **Breathe Plan** | Each phase starts with SHIELD 3 % max HP; +1 % max HP heal at turn start on HIGH | Open Air | VIRUS |
| 3 ★ | **Tide Lock** | The tide skips LOW (RISING, HIGH, FALLING loop), so no drain turn and fewer burst windows | Sluice Key | none |
| 4 | **Deep Fog** | The next tide step and the next layout stay hidden (the current turn's preview is exact) | Tide Tables | INTEL |
| 5 | **Pressure Hull** | Spin resistance by tide: LOW 0, RISING/FALLING 1, HIGH 3 (blocks Flip and Respin while above 0) | Hull Survey | none |
| 6 | **Lamprey Swarm** | One Lamprey latches on your wheel at every phase start (max 2) | Antifouling | none |
| 7 | **Crush Depth** | At HIGH the boss's damage slices deal ×1.5 | Depth Recalibration | none |
| 8 | **Black Ink** | Every phase change applies TIER_DOWN ×1 to the slice under your pointer and its clockwise neighbour (no RNG) | Ink Filter | none |

**Notes on buffs.**
- A route that draws only Tide Lock, Pressure Hull and Crush Depth makes HIGH hostile, so the strongest answer is a SANDBOX economy, not speed.
- Black Ink stacks with the P3 Ink Burst. The P4 `cleanse_on_enter` PLAYER wipes both, and then Black Ink re-applies one stack on the same transition.
- `min_exploits_for_breach = 3` stays.

### Counterplay per phase
- **P1:** hit on LOW, and keep the free nudge for putting the needle on Null. Each unresolved overclock marker is a clock: the boss rewards a player who lets its overclock land on Sea Wall or Null.
- **P2:** read the tide mask. On WARM turns put the needle on a cold (dead) slice or on Null (nudge, Spin); on COLD turns burst. Lampreys latch on warm turns, so steer your own wheel so they sit off your pointer, or Cleanse one (the cost is a card; the reward is no TIER_DOWN).
- **P3:** two needles hit you twice and hit the boss twice. The uneven gap means you can choose which needle reads the dangerous slice. Ink makes your Perfects Good, so land Good-and-safe rather than chase Perfect. Cleansing mid-phase is worth a card only if a Perfect-hook class.
- **P4:** the player is the fuse. Overclock markers accumulate on Blasts, and a single OVERCLOCKED Blast resolving chains into the next. Break the chain: Cleanse an overclocked Blast (cards can target the enemy wheel), nudge a needle so the overclocked slice is read on a Harpoon or Null (burning it harmlessly), or SANDBOX one chained resolution (SANDBOX negates one whole resolution, and the chain adds another). Pierce is not present, so SANDBOX is always an answer.
- **P5:** walk the Fuse. The round tracker shows which of the five slices have fired. Spend the free nudge to put the needle on an unfired slice (Exhale counts as fired and is harmless, so landing on Exhale is "free"). SANDBOX the biggest overclocked Surge. Finish before turn 15.

### Systems
- N1, N2, N3, N4, N5.
- N6 (conditional listener, for the P4 chain).
- N8/N9 (TIER_DOWN stacks, CORRUPTED RAM).
- N10 (Parasite ring: Lamprey segments).
- N11 (uneven needles), N12 (variable slice sizes; every layout uses 3–7 ticks), N13, N14.
- **NEW: TIDE clock** (see section 2), plus `tide_mask` for the P2 split.
- **NEW: status-conditioned chain** (a slice rider "if this resolved slice is OVERCLOCKED, also resolve the next OVERCLOCKED slice"). Fallback: RETRIGGER of the neighbour slice via `ON_SLICE_TRIGGER`, if it supports an `if_status` condition. Otherwise Chain Eruption drops and P4 becomes plain 2-needle Blasts (weaker).
- **NEW: round-fired flags** (the P5 Fuse). Fallback: P5 is a plain single-needle phase with enrage only.

### Delta/notes
- **Compared to the Genome Core:** it ramps *defence away* (heal → block → corruption), whereas the Black Smoker never has a heal and keeps one question per phase across the same tide clock. The Genome Core punishes your *state* (corruption count); the Smoker punishes your *timing* (tide) and your *needle choice* (chain, Fuse).
- **Octopus art:** coral on the rim in P2, arms curling round the threat ring in P3, ink in P3 entry. The P4 overclock glow reads as the vent mouths lighting.
- **Cleanse on enemy wheels** is assumed to exist (CLEANSE with WheelTarget ANY). If it does not, P4 loses its direct cleanse answer; steering and SANDBOX remain.

---

## 4. Enemy roster sketch

Teaching order: the first three normals teach TIDE in L1–2 (shield, gated attack, satellite). The next two add statuses and tide-linked resistance in L2–3. The Lamprey brings the parasite ring in L3–4. Both elites run L3–6. The Harbourmaster then uses TIDE hard.

### Normals (1 phase, 3–4 turns)

HP bands: T1 28–36, T2 34–44, T3 44–56, T4 56–70.

| Working name | Layer role | The one question | Wheel sketch (ticks sum 30; needle 1 unless noted) | HP T1/T2/T3/T4 | N# needed |
|---|---|---|---|---|---|
| **Pump Warden** | Teach (L1–2) | Hit when the water is low: the wall doubles at HIGH and drains at LOW | Seawall (SHIELD 2) 8 · Spanner (SHIM 3) 7 · Seawall 8 · Spanner 7 | 28 / 34 / 44 / 56 (budget minus sustain lands on the band floor) | N1, N2, TIDE |
| **Diver Drone** | Teach (L1–2) | Is the Torpedo live this turn? Read the tide and keep the needle off it | Torpedo (OVERFLOW 4; live RISING/HIGH, dead otherwise) 4 · Dart (SHIM 2) 6 · Null 5 · Torpedo 4 · Dart 6 · Bubble Screen (BLOCK 3) 5 | 32 / 39 / 49 / 63 | N1, N2, TIDE (`tide_mask`) |
| **Buoy Tender** | Teach (L2) | Dig through the bodyguard or steer round it? It also teaches that a satellite is fixed | Cannon (OVERFLOW 4, **Marker Buoy** docked) 6 · Net (BLOCK 3) 6 · Harpoon (SHIM 3) 6 · Net 6 · Null 6. Buoy (HP 3/4/5/7; mini-wheel Flash SHIM 1 / Float SHIELD 2 to host) | 29 / 35 / 44 / 56 (host; the satellite HP is on top) | N13, TIDE (Float ×2 at HIGH) |
| **Kelp Crawler** | Pressure (L2–3) | Rotate off the stacked slice or Cleanse now? Statuses cost output, not actions | Entangle (INFECT: OUTPUT_DOWN ×1 on the slice under your pointer; ×2 at HIGH) 6 · Lash (SHIM 3) 6 · Entangle 6 · Null 6 · Lash 6 | 30 / 37 / 46 / 58 (its stacks cut your damage by ~10 %) | N8, N9, TIDE (`tide_mult`); fallback: today's PARASITE status (2-stack OUTPUT_DOWN) |
| **Pressure Sentinel** | Pressure (L3–4) | Nudge it at LOW, when it moves freely, because at HIGH it is locked | Crush (OVERFLOW 5) 6 · Plate (BLOCK 4) 6 · Crush 6 · Plate 6 · Null 6. Resistance by tide: LOW 0, RISING/FALLING 1, HIGH 3 | 34 / 42 / 52 / 66 (resistance tax) | N2, TIDE (tide-linked resistance on the hub); fallback: fixed resistance 2 |
| **Lamprey** | Pressure (L3–5) | Kill it before it latches, or pay a Cleanse to remove the parasite after? | Latch (LATCH_PARASITE: Lamprey segment, 3 ticks, read: 2 damage + TIER_DOWN ×1) 5 · Bite (SHIM 2) 5 · Slither (EVADE/SANDBOX: negates one hit) 5 · Latch 5 · Bite 5 · Null 5 | 28 / 34 / 44 / 56 (floor; the latch outlives it) | N10, N8, N9, N14; fallback: Latch applies the PARASITE status |

**Arithmetic notes.** Normal budget is ref × 3.5 = 31.5 / 38.5 / 49 / 63.
- **Pump Warden:** sustain 16/30 × 2 × 1.25 = 1.3 per turn at T1. 31.5 − 4.6 = 27, which is at the floor of 28.
- **Buoy Tender:** HP 31.5 − satellite 3 = 28.5 → 29, and so on up the tiers.
- Every normal has threat per turn > 0: Pump Warden 1.4, Diver Drone (Torpedo 4/30 × 8 live half the time + Dart 6/30 × 2) ≈ 1.6, Kelp Crawler 2.0, Sentinel about 2.5.

### Elites (2 phases, 6–8 turns)

Single-needle by design, so the HP band applies without a needle factor.

Band: T1 56–72, T2 68–88, T3 88–112, T4 112–144.

| Working name | Layer role | The one question (P1 → P2) | Wheel sketch | HP T1/T2/T3/T4 | N# |
|---|---|---|---|---|---|
| **Siphonophore** | Pressure (L3–6) | P1: which end of the chain do you cut? → P2: the chain breaks and replaces itself, so steer around, don't kill | P1 (100 → 55 %): 3 chained **Zooid** satellites on adjacent slices (each HP 4/5/7/9; shield the next on their mini-wheel); host layout Sting (SHIM 3) 6 · Zooid-host 6 · Zooid-host 6 · Zooid-host 6 · Null 6. Killing the middle one cuts the chain (shield sharing stops). P2 (55 → 0 %): chain gone; every turn a new Zooid is launched onto a slice and **replaces** any satellite there; Sting becomes OVERFLOW 5 | 58 / 70 / 89 / 114 | N13 (REPLACE), N3, TIDE (Zooid shield ×2 at HIGH) |
| **Angler** | Pressure (L3–6) | P1: plan two turns ahead, because the lantern needle sweeps and can't be held → P2: its jaws only open when the tide is not HIGH, so choose your rhythm | P1 (100 → 50 %): needle **ORBIT** +5 ticks/turn (trail shows future positions). Layout Bite (OVERFLOW 5) 5 · Snap (SHIM 3) 5 · Lure (INFECT: TIER_DOWN ×1 on your slice) 5 · Snap 5 · Gill (SHIELD 3) 5 · Null 5. P2 (50 → 0 %): orbit stops; Bite 7 · Gill 4 · Bite 7 · Snap 5 · Lure 3 · Null 4; **Bite dead at HIGH** (`tide_mask`), Gill ×2 at HIGH | 58 / 70 / 89 / 114 | N3, N9, TIDE (`tide_mask`); ORBIT exists |

**Elite arithmetic.**
- **Siphonophore:** sustain 1.5 at T1 (the zooid shields). P1 (9 − 1.5) × 3.5 = 26 and P2 = 31.5, for 58. T2: 31.7 + 38.5 = 70. T3: 40 + 49 = 89. T4: 51.5 + 63 = 114.
- **Angler:** sustain 0.5 in P1, 1 in P2. T1: 29.75 + 28 = 58. T2: 36.2 + 34 = 70. T3: 46 + 43 = 89. T4: 59 + 55.3 = 114.
- Both use the elite default enrage (turn 8, every 5, +25 %). Both retire their `heat_effects`; the phase *is* the pressure now.

---

## 5. Systems needed

| # | System | Used by |
|---|---|---|
| N1 | Amount modes (FLAT / PERCENT) | all (shields as PERCENT on the boss) |
| N2 | Tier base-value tables, `hp_by_tier`, `hp_bands` | all |
| N3 | Phases on every class, parking, status keep, `cleanse_on_enter` | mini-boss, boss, elites |
| N4 | Enrage | mini-boss, boss, elites |
| N5 | Boss buffs and Exploits | boss |
| N6 | Enemy listeners / conditional triggers | boss P4 chain (fallback exists) |
| N8, N9 | ×N stacks; OUTPUT_DOWN, TIER_DOWN, CORRUPTED as RAM cost | Kelp Crawler, Lamprey, Angler, boss |
| N10 | Parasite ring | Lamprey, boss P2–P3 |
| N11 | Pointers on any tick | boss P3 / P4 |
| N12 | Variable slice sizes (3–7 ticks) | every layout here |
| N13 | Fixed satellites + replacement | Buoy Tender, mini-boss P2, Siphonophore |
| N14 | Defense trio (SANDBOX negates a whole resolution) | Lamprey, boss P4–P5 counterplay |
| N19 | Sim metrics (turns per phase, tide step, enrage step) | verification |
| **NEW** | **TIDE clock** (seeded step, advance, HUD chip, `tide_rate`, `tide_hold`) | everything |
| **NEW** | **Tide-conditioned fields** (`tide_mask`, `tide_mult`, tide-linked resistance) | Diver, Sentinel, boss P2, Angler |
| **NEW** | Status-conditioned chain rider | boss P4 |
| **NEW** | Round-fired flags (the Fuse) | boss P5 |

**Build order.**
1. Foundation: N1 → N2 → N3 → N4 → N19, with N11, N13, N14 in parallel.
2. **TIDE clock now**, right after N3. It is cheap, unblocks every normal, and the first three normals (Pump Warden, Diver Drone, Buoy Tender) are data-only once the clock exists.
3. N12 starts early (it is the longest).
4. N8 → N9 → Kelp Crawler, Sentinel, Lamprey fallback (PARASITE status).
5. Harbourmaster (needs the clock, N13, N3, N4).
6. N5, N10 → full Lamprey, Siphonophore, Angler.
7. Boss: N6 / chain and Fuse last.

If the clock is cut, nothing in this document survives, so the clock is the corporation's single point of failure.

---

## 6. Open questions
Q: Enemy CORRUPTED (Q3 in V2): the boss design assumes a scorched slice has no penalty, so Vent Pressure is a pure buff. Should a burnt-out enemy slice instead read at −25 % (OUTPUT_DOWN ×1) for one turn, giving the player a short reward for letting the overclock land?
Q: Should the player ever read the tide as a tool (a Firmware or Daemon such as "Dead Reckoning" that nudges the tide one step, or shows the next two steps)? As written the tide is information only for the player.
Q: Is the high-ICE boss length acceptable (≈ 23 turns at the 530 band), or should the top band cut P1–P2 HP and keep P3–P5 HP so extra length is spent on the late phases?
Q: Do Tethys PERCENT shields need their own cap? Sea Wall at HIGH is 20 (P1) / 24 (P3) shield, which is more than the player's cap of 15.
Q: Should Tide Lock (buff 3) skip LOW in the HQ's BALLAST TIDE too, so one Exploit is felt on the map and in the fight, or stay fight-only?
Q: Does the unified-city ruling (flooded district of one model) hold, so the TIDE chip is legible on the map as well? If Tethys is a separate map, the HQ and raid use of the same clock needs a new ruling.
