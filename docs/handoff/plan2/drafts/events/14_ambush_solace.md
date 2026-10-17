<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__14_ambush_solace; status ok; tokens in 6417 cache-write 0 cache-read 32007 out 2162; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_witness_statement: Witness Statement

**Mechanic:** AMBUSH, corporation solace, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Pay to protect a Solace witness who wants to talk, shake her down and fight what comes, or hand her over to the debt-collection sweep and keep your Heat clean.

## TerminalEventData fields
- id: `ev_witness_statement`
- title: Witness Statement
- speaker: STREET_MERC (1)
- text: "A claims clerk sits curled under the Terminal desk, her badge still blinking green. She watched Solace sign off on a recall that bricked a whole block, and she wants it on record before they find her. Her handset pings every ten seconds; a Collections sweep is two corridors out. She says her statement is worth more than anything in this building, if she's still breathing when it uploads."
- corporation_id: `solace`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Guard her upload (fight the sweep)
- label: "Hold the door while she uploads (fight, win her statement)"
- result_text: "The sweep kicks in right on schedule. She types through the whole thing, lips moving, saying names."
- cycle_cost: 0
- hp_cost: 0
- effects: none directly; the fight carries the outcome
- reward: none directly (granted by the fight's stake)
- starts_combat (new): enemy `collections_agent`
- combat_overrides (new):
  - tier: +1 (a tier tweak; the combat uses the node's tier + 1, cap 4)
  - stake: the Witness (the fight is lost if you end it below 40% max HP; the clerk is then taken and you get the loss branch)
  - on_win: +35 Cycles, −2 Heat (the statement goes public), reward: one Common Firmware (a "Calibrated" chip from her desk)
  - on_loss: none beyond normal combat defeat; no extra penalty
  - duration: this combat only
- map_edits (new): none

### 2. Shake her down
- label: "Sell her location to the sweep (+45 Cycles, +4 Heat)"
- result_text: "The collectors pay by the head. She doesn't scream. She just looks at you, and the badge goes dark."
- cycle_cost: 0
- hp_cost: 0
- effects:
  - GAIN_CYCLES, CAMPAIGN, amount 45
  - MODIFY_HEAT, CAMPAIGN, amount 4
- reward: none
- starts_combat (new): none
- next_combat_overrides (new): the next fight node starts with `collections_agent` added as a Router escort (+1 enemy tag), duration 1 combat. The sweep wants a receipt.

### 3. Smuggle her out blind
- label: "Pay for a quiet exit (−30 Cycles, −1 HP-cost scuffle, −3 Heat)"
- result_text: "You burn credits on a service hatch and a fake reassignment. She leaves, and the statement leaves with her. A small piece of the sweep still catches you on the way."
- cycle_cost: 30
- hp_cost: 6
- effects:
  - MODIFY_HEAT, CAMPAIGN, amount −3
- reward: none
- starts_combat (new): none
- map_edits (new): none

### 4. Walk on
- label: "Not your problem"
- result_text: "You leave her under the desk. Behind you the handset pings again, then stops."
- effects: none
- starts_combat (new): none

## Design notes
- **Tension:** Choice 1 is the only way to get the Firmware and the Heat drop, but it is a tier +1 fight against a normal that is mostly a RAM and billing-pressure test, with the 40% HP stake as a real fail line. Choice 3 is the safe version of the same Heat result, at a Cycle cost and a small HP cost. Choice 2 pays the most Cycles, but the follow-up escort and +4 Heat make it a debt, not free money. Choice 4 is the baseline and carries no risk.
- **Economy (GDD 11 placeholders):** a typical T2 Router pays ~20–25 Cycles, so +35 plus a Firmware plus −2 Heat for a fight comparable to an elite-lite is roughly 1.5× a normal reward. Selling her is ~2 Routers of Cycles for +4 Heat, about one Minor threshold step.
- **Why Collections Agent:** it asks the "will you take the toll" question directly, so the stake fits (the clerk is the thing being collected). Tier +1 puts the normal at T3 values, inside the R2 normal band (44–56 HP), so the preview and fight length stay in the 3–4 turn target. It also stays a one-phase fight, so no new phase work is needed.
- **Determinism:** no randomness added. The stake check is a plain HP comparison at combat end; the fight's own RNG streams are unchanged. The tier tweak is applied through `combat_overrides` before `create_combat`, so previews match results.
- **Dependencies:**
  - N16 for `starts_combat`, `combat_overrides` and `next_combat_overrides`. No data-only fallback for the impromptu fight itself.
  - Data-only fallback for the event: drop choice 1 and keep choices 2–4 (all use existing effects). Choice 2's escort can be replaced by +2 Heat.
  - The stake (end-of-fight HP check) is NEW: `combat_overrides.win_condition_min_hp_pct`. A fallback is plain victory with no stake.
- **Interactions:** the −2 Heat on a win stacks with Clean Signal and Scrubber for Heat-focused builds. Selling her out adds Heat that can tip a MINOR threshold and its netrun complication.
- **Text keys needed:** `ev_witness_statement.title`, `.text`, `.c1`–`.c4` labels and results, a stake HUD line "WITNESS: finish above 40% HP", and a loss line "The clerk is taken."

## Q:
- Q: Should a lost stake (below 40% HP at a win) still pay the Cycles, or does it pay nothing?
- Q: Should the +1 tier cap at the run's current tier ceiling, or may an ambush exceed it?
