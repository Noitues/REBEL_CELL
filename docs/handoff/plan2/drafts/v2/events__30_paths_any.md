<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__30_paths_any; status ok; tokens in 4925 cache-write 0 cache-read 32585 out 2734; cost $0.022. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, determinism):** the RNG draw is gone. The `debt_due` enemy is fixed: the lowest-id normal enemy in the corporation's pool at the player's tier. It is named in the choice tooltip and on the node badge. No RNG, so preview = result and nothing can be peeked or rerolled.
- **Issue 2 (Borrow dominated by Walk on):** Borrow now pays out. It adds a layer-skipping link plus +10 Cycles from the shortcut cache. The debt is a fixed +1 normal enemy, capped at 3–4 turns (one phase). Saving a layer and paying one enemy nets even on HP and time, and the +10 Cycles breaks the tie.
- **Issue 3 (TURN_NODE):** removed. Pay is now ADD_LINK plus REVEAL_TYPE only. It stays a priced "safe and informed" option and no longer deletes a fight. This also answers Q2 of the critic: conversion is not offered as a priced option.
- **Issue 4 (Burn):** Burn now closes the Elite Router in the next layer, which is visible and named in the tooltip. If no Elite Router is there, nothing is cut and the choice is greyed out with a reason. Heat is now −2. The result_text matches the mechanic.
- **Issue 5 (safety guards):** guards are now constraints of `map_edits`: never remove or target a Rack, skip the candidate if it is the last Mainframe in layers 3–5, and never leave a layer empty or disconnect the final Rack.
- **Issue 6 (override spec):** the debt triggers on the first combat entered via the added link, expires at run end, and voids if the link is never taken. It adds +1 enemy and a 3–4 turn cap.
- **Issue 7 (nits):** Walk on has explicit fields, the "Cheap it isn't" line was replaced, the weak fallback was rewritten, and the text-keys line was dropped.
- **Kept, because strong:** the three currencies plus a neutral baseline, the deterministic tie-breaks, and the kiosk text.

# ev_toll_ledger_debt: The Toll Ledger

**Mechanic:** PATHS, corporation any, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Take a shortcut on credit, pay for a clean revealed lane, or burn the ledger and shut a dangerous lane for good.

## TerminalEventData fields
- id: `ev_toll_ledger_debt`
- title: The Toll Ledger
- speaker: STREET_MERC
- text: "A gutted payphone kiosk sits between two server stacks, its screen scrolling a ledger of names. Every name is a runner who bought a shortcut on credit and never closed the account. The last line blinks: YOUR LINE OF CREDIT IS APPROVED. Somebody built a toll road through this net and still collects on it. Everything here has a price, and the bill always comes late."
- corporation_id: &"" (any)
- min_tier: 1
- dispatch_clue: false
- foreshadows: &""
- weight: 0.8

## Choices

### 1. Borrow the shortcut
- label: Borrow the shortcut (+10 Cycles, owe one fight)
- result_text: "The map redraws itself. A lane you couldn't see is open, stamped with a due date, and the kiosk spits out a few Cycles as a sweetener. It logs your handle."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target SELF, amount 10
- reward: none
- (new) map_edits:
  - ADD_LINK: from the current node to the node two layers ahead with the fewest inbound links (ties: lowest id), skipping one layer.
  - REVEAL_TYPE: that target node.
  - Constraints: never target a Rack; never leave a layer empty.
- (new) next_combat_overrides:
  - `debt_due`: trigger = the first combat entered via the added link; expires at run end; voids if the link is never taken.
  - Effect: +1 enemy, the lowest-id normal enemy in the corporation's pool at the player's tier (named in the tooltip and on the node badge). No RNG.
  - Stake: fight length stays 3–4 turns per phase (one extra body, no extra phase). It costs about the HP of the fight you skipped.

### 2. Pay for a clean lane
- label: Pay 40 Cycles (clean lane, type revealed)
- result_text: "You feed the kiosk. The ledger scrubs your name and the toll road swings open with no strings and a clear label."
- cycle_cost: 40
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits:
  - ADD_LINK: same link as choice 1.
  - REVEAL_TYPE: the target node.
  - No TURN_NODE.
- (new) next_combat_overrides: none

### 3. Burn the ledger
- label: Burn the ledger (-2 Heat, close the next Elite lane)
- result_text: "You overload the kiosk and the names turn to static. The debt is wiped, and the Elite Router waiting in the next layer loses its feed and goes dark."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount -2
- reward: none
- (new) map_edits:
  - CLOSE_NODE: the Elite Router in the next layer (lowest id if several). If none exists, no cut: the choice is greyed out ("no Elite lane ahead").
  - Constraints: never a Rack; skip it if it is the last Mainframe in layers 3–5; never leave a layer empty or disconnect the final Rack.

### 4. Walk on
- label: Walk on
- result_text: "You leave the kiosk to its names. It will keep asking."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: none

## Design notes
- **Decision shape:** later cost (Borrow), Cycles now (Pay), or a lane removed (Burn), with Walk on as the baseline. Everything is visible before commit: the link target, the debt enemy and the cut node are named in tooltips.
- **Numbers (placeholders vs GDD 11):** a run earns about 100–150 Cycles by layer 4, so 40 is a real cost that competes with Mainframe purchases. Borrow skips about one fight (~2 min, 8–12 HP) and owes about one extra normal enemy of equal cost, plus +10 Cycles. It is slightly positive for a strong deck on a time budget, and a risk for a low-HP operative. Burn removes an Elite fight (+1 Heat and a harder fight avoided) and gives −2 Heat, but also forfeits that Elite's loot, so it suits low-HP runs, not greedy ones.
- **Determinism:** links, cuts and the debt enemy are all fixed by tie-break rules. No RNG draw is involved.
- **Interactions:** a skipped layer reduces Elite Heat. Scrubber and Cold Exit are unaffected. Debt voiding when the link goes unused means Borrow is free if ignored, but then the +10 Cycles is the only gain.
- **Dependencies:** N16 (`map_edits` ADD_LINK / REVEAL_TYPE / CLOSE_NODE with constraints; run-level `next_combat_overrides`). Data-only fallback: choice 1 becomes +10 Cycles and +1 Heat, choice 2 a plain 40-Cycle cost for a Heat -1, and choice 3 a -2 Heat for a Cycle cost. All lose the actual path change.

## Q:
- Q: Should an unpaid, taken debt carry into the next netrun as a Grid-level debt, or stay within the run?
- Q: Can the `debt_due` enemy be an Elite at T3+, or always a normal?
