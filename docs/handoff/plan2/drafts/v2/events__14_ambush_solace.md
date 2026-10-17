<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__14_ambush_solace; status ok; tokens in 4823 cache-write 0 cache-read 32585 out 2917; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, stake incoherent):** The stake is now a graded win. Win at ≥ 40% max HP gives the full reward. Win below 40% gives a reduced "clerk taken" reward. Normal defeat follows normal run-death rules with no extra penalty. A fight is never won and lost at once. The v1 Q1 (does a lost stake pay Cycles?) is resolved: a low-HP win pays half Cycles.
- **Issue 2 (BLOCKER, unnamed field and no N#):** The field is named `combat_overrides.stake_min_hp_pct` = 0.40 and marked "NEW: Ambush stake" (no N# fits; N16 covers only `starts_combat` and `combat_overrides`). The fallback is no stake, full reward on any win. The HUD line and the clerk-taken line are text keys tied to this field, not separate systems.
- **Issue 3 (MAJOR, escort tag):** Choice 2 now uses `next_combat_overrides`: the next fight node adds +1 Collections Agent as an extra enemy, 1 combat (N16). The fallback is +6 Heat and no escort.
- **Issue 4 (MAJOR, label mismatch):** The choice 3 label now matches the numbers (see Issue 5). The result text keeps the scuffle.
- **Issue 5 (MAJOR, dominance):** Choice 3 is now cycle_cost 40, hp_cost 8, Heat −2. Choice 1 pays +35 Cycles, a Firmware and −2 Heat, so it out-earns choice 3, and its price is the 40% HP fail line.
- **Issue 6 (NIT, unsupported economy claim):** The "elite-lite" and "1.5×" claims are removed. The notes now state the numbers as placeholders and cite no GDD 11 figure.
- **Issue 7 (NIT, invented chip):** The reward is "one Common Firmware from the existing reward pool". The R11 "Calibrated" reference is removed.
- **Kept, because the critic marked it strong:** Collections Agent, the stake as a fight-quality test, choices 2 and 4 as anchors, and the explicit determinism note.
- **Critic Q on tier-scaled threshold:** not adopted (no added scope); it stays a flat 40%. The clerk-reappears question is dropped as scope creep.

# ev_witness_statement: Witness Statement

**Mechanic:** AMBUSH, corporation solace, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Hold the door for a Solace witness at a real HP risk, sell her to the sweep for cash and a debt, or pay to smuggle her out with no fight.

## TerminalEventData fields
- id: `ev_witness_statement`
- title: Witness Statement
- speaker: STREET_MERC
- text: "A claims clerk sits curled under the Terminal desk, her badge still blinking green. She watched Solace sign off on a recall that bricked a whole block, and she wants it on record before they find her. Her handset pings every ten seconds; a Collections sweep is two corridors out. She says her statement is worth more than anything in this building, if she's still breathing when it uploads."
- corporation_id: `solace`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Guard her upload (fight the sweep)
- label: "Hold the door while she uploads (fight; finish at 40% HP or more to protect her)"
- result_text: "The sweep arrives right on schedule. She types through the whole thing, lips moving, saying names."
- cycle_cost: 0
- hp_cost: 0
- effects: none directly; the fight carries the outcome
- reward: none directly (granted by the fight outcome below)
- starts_combat (new, N16): enemy `collections_agent`
- combat_overrides (new, N16):
  - tier: node tier + 1 (cap 4)
  - stake (NEW: Ambush stake, `stake_min_hp_pct` = 0.40; fallback: no stake, full reward on any win)
  - win at ≥ 40% max HP: +35 Cycles, −2 Heat, one Common Firmware from the existing reward pool
  - win below 40% max HP ("the clerk is taken"): +17 Cycles, no Firmware, no Heat change
  - defeat: normal run-death rules, no extra penalty
  - duration: this combat only
- map_edits (new): none

### 2. Sell her location
- label: "Sell her to the sweep (+45 Cycles, +4 Heat)"
- result_text: "The collectors pay by the head. She doesn't scream. She just looks at you, and the badge goes dark."
- cycle_cost: 0
- hp_cost: 0
- effects:
  - GAIN_CYCLES, CAMPAIGN, amount 45
  - MODIFY_HEAT, CAMPAIGN, amount 4
- reward: none
- starts_combat (new): none
- next_combat_overrides (new, N16): the next fight node adds +1 `collections_agent` as an extra enemy; duration 1 combat. Fallback: Heat +6 instead of +4, no escort.

### 3. Smuggle her out
- label: "Pay for a quiet exit (−40 Cycles, −8 HP, −2 Heat)"
- result_text: "You burn credits on a service hatch and a fake reassignment. She leaves, and the statement leaves with her. A small piece of the sweep still catches you on the way."
- cycle_cost: 40
- hp_cost: 8
- effects:
  - MODIFY_HEAT, CAMPAIGN, amount −2
- reward: none
- starts_combat (new): none
- map_edits (new): none

### 4. Walk on
- label: "Not your problem"
- result_text: "You leave her under the desk. Behind you the handset pings again, then stops."
- effects: none
- starts_combat (new): none

## Design notes
- **Tension:** Choice 1 is the only source of the Firmware, and it earns +35 Cycles against choice 3's −40, but its price is a tier +1 fight with a real 40% HP fail line. Winning ragged still pays +17 and no Heat relief. Choice 3 buys the same Heat direction safely, at a Cycle and HP cost, and gets no Firmware. Choice 2 pays the most Cycles, but +4 Heat and a bonus Collections Agent at the next fight make it a debt. Choice 4 is the zero baseline.
- **Economy (all placeholders pending the sim):** choice 1 nets +35 Cycles, −2 Heat and a Firmware. Choice 3 nets −40 Cycles, −8 HP and −2 Heat, a 75-Cycle swing against choice 1. Choice 2 trades +45 Cycles for +4 Heat and a harder next fight.
- **Why Collections Agent:** it asks the "will you take the toll" question directly, so the clerk being collected fits the stake. At tier +1 it is a normal in the R2 band (T3: 44–56 HP) and a one-phase fight of 3–4 turns, so no phase work is needed.
- **Determinism:** no new randomness. The stake is a plain HP comparison at combat end, and tier and enemy overrides are applied before `create_combat`, so previews equal results. The fight's own RNG streams are unchanged.
- **Dependencies:**
  - N16 for `starts_combat`, `combat_overrides` and `next_combat_overrides`. There is no data-only fallback for the impromptu fight itself; if N16 is missing, drop choice 1 and keep 2–4.
  - NEW: Ambush stake (`stake_min_hp_pct`), with no N#. Fallback: no stake.
- **Interactions:** the −2 Heat stacks with Clean Signal and Scrubber. The Heat from choice 2 can tip a MINOR threshold and its netrun complication.
- **Text keys needed:** `ev_witness_statement.title`, `.text`, `.c1`–`.c4` labels and results, the HUD stake line "WITNESS: finish at 40% HP or more", and the low-HP win line "The clerk is taken."

## Q:
- Q: Should the stake threshold scale with tier (40% at T2, 50% at T4), or stay flat?
- Q: Should the extra Collections Agent in choice 2 count toward the next fight's normal reward, or pay nothing extra?
