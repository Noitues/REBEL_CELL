<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__30_paths_any; status ok; tokens in 6337 cache-write 0 cache-read 32007 out 2044; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_toll_ledger_debt: The Toll Ledger

**Mechanic:** PATHS, corporation any, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Take a shortcut on credit and owe the route a debt later, pay for a clean lane now, or burn the ledger and lose a lane forever.

## TerminalEventData fields
- id: `ev_toll_ledger_debt`
- title: The Toll Ledger
- speaker: STREET_MERC
- text: "A gutted payphone kiosk sits between two server stacks, its screen scrolling a ledger of names. Every name is a runner who bought a shortcut on credit and never closed the account. The kiosk's last line is blinking: YOUR LINE OF CREDIT IS APPROVED. Somebody built a toll road through this net and still collects on it. Everything here has a price, and the bill is always sent late."
- corporation_id: &"" (any)
- min_tier: 1
- dispatch_clue: false
- foreshadows: &""
- weight: 0.8

## Choices

### 1. "Borrow the shortcut"
- label: Borrow the shortcut (no cost now, owe later)
- result_text: "The map redraws itself. A lane you couldn't see is suddenly open, stamped with a due date. The kiosk logs your handle."
- cycle_cost: 0
- hp_cost: 0
- effects: none now
- reward: none
- (new) map_edits:
  - ADD_LINK: from the current node to a node in layer +2 (the node with the fewest inbound links, ties by lowest id), skipping one layer.
  - REVEAL_TYPE: the target node's type.
- (new) next_combat_overrides (duration: the next 1 combat that begins after the target node is entered, or run end):
  - `debt_due`: the first Router or Elite Router fight after taking the link adds one extra normal enemy from the corporation's pool (impromptu add, fixed by the `events` RNG stream at a checkpoint).
  - Stake: the shortcut saves one layer of fights, but you pay with a heavier fight later.

### 2. "Pay for a clean lane"
- label: Pay 40 Cycles for the clean lane
- result_text: "You feed the kiosk. The ledger scrubs your name, and the toll road swings open with no strings. Cheap it isn't."
- cycle_cost: 40
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits:
  - ADD_LINK: same link as choice 1.
  - REVEAL_TYPE: the target node's type.
  - TURN_NODE: if the target is a Router, change it to a Terminal (an event is a reprieve).
- (new) next_combat_overrides: none

### 3. "Burn the ledger"
- label: Burn the ledger (-1 Heat, cut a lane)
- result_text: "You overload the kiosk and the names turn to static. The debt is wiped, but so is the road: a layer ahead loses an option when the ledger's host node goes dark."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount -1
- reward: none
- (new) map_edits:
  - CLOSE_NODE: in the next layer, remove one non-Rack node that is not the only node in its layer (lowest inbound count, ties by lowest id). Never the only route to the final Rack.

### 4. "Walk on"
- label: Walk on
- result_text: "You leave the kiosk to its names. It will keep asking."
- (new) map_edits: none

## Design notes
- **Decision shape:** each of the three options trades a different currency: later danger (borrow), Cycles now (pay), or route flexibility (burn). Walking on is the neutral baseline.
- **Numbers (placeholders vs GDD 11):** a typical run earns about 100–150 Cycles by layer 4, so 40 is a real but affordable cost. The skipped layer saves roughly one fight (about 2 minutes, about 8–12 HP). The extra enemy at normal strength costs about the same HP, so borrowing is a time-for-HP trade: it nets out neutral when the build is strong and punishing when the operative is already low. Burning gives -1 Heat, minor next to the lost option.
- **Why no dominant option:** paying is strictly safer, but it competes with Mainframe purchases. Borrowing is best for a strong deck on a time budget. Burning only shines if the operative wants to dodge an Elite lane. The player sees the reveal before choosing only in the pay option, which is intentional information value.
- **Determinism:** the link target and node removal are chosen by fixed tie-break rules, not random. The added enemy is picked from the `events` RNG stream at a checkpoint (before the choice is committed), so the preview equals the result.
- **Interactions:** the Scrubber and Cold Exit Daemons are unaffected. A skipped layer reduces total Heat from Elite Routers. Cutting a node never removes the guaranteed Mainframe in layers 3–5: the engine should skip the candidate if it is the last one.
- **Dependencies:** N16 (`map_edits` ADD_LINK, REVEAL_TYPE, TURN_NODE, CLOSE_NODE; run-level `next_combat_overrides`). Data-only fallback: choice 2 as "+reveal type" only via a Cycles/Heat effect, choice 3 as a plain -1 Heat, and choice 1 as a flat +1 Heat; this loses the actual path change.
- **Text keys:** `ev_toll_ledger_debt.title`, `.text`, `.c1`–`.c4` labels and results. Debt tag `debt_due` for the map node badge.

## Q:
- Q: Should an unpaid borrow also carry into the next netrun (a Grid-level debt), or stay within the run?
- Q: Can the added `debt_due` enemy be an Elite at T3+, or always a normal?
