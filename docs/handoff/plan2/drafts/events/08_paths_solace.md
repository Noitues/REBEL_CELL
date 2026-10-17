<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__08_paths_solace; status ok; tokens in 6417 cache-write 0 cache-read 32007 out 2047; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_solace_wellness_hold: Wellness Hold

**Mechanic:** PATHS (N16 map_edits), corporation solace, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** A bricked subscriber is locked in a "voluntary wellness hold" behind a Solace door. Spring him and the door you open also opens a new route, but a payload-clause alarm shuts another one. Or trade his testimony for a clear view of what lies ahead.

## TerminalEventData fields
- id: `ev_solace_wellness_hold`
- title: Wellness Hold
- speaker: STREET_MERC (1)
- text: "The Terminal sits in a corridor of frosted doors, each one stenciled WELLNESS HOLD, VOLUNTARY. Behind the glass of door 6 a man in a Solace gown is pressing his dead implant against the pane, mouthing a number: his arrears. The door log says he agreed to the stay. The signature is a thumbprint taken while he was sedated. He knows which service corridors Collections uses, and which ones they'll weld shut the moment this door opens."
- corporation_id: `solace`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. "Cut the thumbprint lock and walk him out"
- label: Spring him (-8 HP, +2 Heat)
- result_text: "The lock gives. He hands you a route sheet, shaking: the Collections lift he was wheeled in on. You open it. Down the hall a shutter drops, welded from the other side."
- cycle_cost: 0
- hp_cost: 8 (the door arcs)
- effects: MODIFY_HEAT, CAMPAIGN, amount 2
- reward: none
- (new) starts_combat: none
- (new) next_combat_overrides: none
- (new) map_edits:
  - `add_link`: from the current node's layer to a node one layer further ahead, skipping that layer's option. (The player picks the target from the offered forward nodes.)
  - `close_node`: one random non-Rack node in the next layer (chosen by the `events` RNG stream at event-open time, so the preview names it).

### 2. "Trade his testimony to the Auditor's Office for a map"
- label: Sell the complaint (+0 Cycles, free)
- result_text: "You log his complaint as a formal Grievance Packet. The Terminal pays in the only currency it has: a full node readout for the layers ahead. The man is moved to Ward 9. The door closes."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: `reveal_type` on every node in the next two layers.
- (new) next_combat_overrides: none

### 3. "Pay his arrears and take him as a guide"
- label: Pay the arrears (-45 Cycles)
- result_text: "Forty-five Cycles clears his balance. The implant lights. He doesn't thank you; he walks you to a maintenance hatch, and you walk out of Solace's well-lit route entirely."
- cycle_cost: 45
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: `convert_node`: one chosen non-Rack node in the next layer becomes a Terminal (Event), and `add_link` from the current node to it if absent.

### 4. "Leave him. Hold's voluntary."
- label: Walk on
- result_text: "You don't look at door 6. The glass fogs, then clears."
- No costs, no effects, no map_edits.

## Design notes
- **Why it's interesting:** Each choice trades a different resource for a different kind of route knowledge. Spring-him pays HP and Heat for a shortcut that skips a layer, and the closed node costs you the option you might have wanted; it's flexible but not free. Sell-the-complaint is free and safe but changes nothing about the topology, only your planning. Pay-the-arrears costs real Cycles for a guaranteed Terminal, which is only worth it if you want another event or a Rest-type payoff. None dominates: if the next layers are already readable, option 2 is nearly worthless; if you're low on HP, option 1 is a trap.
- **Economy (GDD 11 placeholders):** Typical early-run Cycles income is ~25–35 per combat, so 45 is about one combat's worth, equal to a modest shop item. 8 HP is ~13% of a Breaker's 60. +2 Heat sits just below one Minor threshold step's worth (+1 per Elite, +10 per Minor tier), so it's a small campaign cost. Skipping a layer saves roughly one combat (~2 minutes) at the cost of its drops.
- **Interactions:** The skipped layer's Elite guarantee is bypassed, which makes it attractive at low Heat and dangerous if you need Firmware. Closing a node can't close the last remaining option on a layer (validator must refuse, falling back to the other node). Scrubber and Cold Exit are unaffected. `reveal_type` pairs well with Cold Exit routing.
- **Determinism:** The closed node is picked from the `events` stream at open time and saved in a checkpoint, so Rewind can't reroll it and the preview shows exactly which node closes.
- **Fallback without N16:** none for the map edits. A data-only version could swap choice 1 for hp_cost 8 plus MODIFY_HEAT with no route change, but that removes the point.
- **Text keys:** `ev_solace_wellness_hold.*` (title, text, 4 labels, 4 results), plus preview strings "LINK ADDED", "NODE CLOSED: {name}", "TYPES REVEALED".

## Q:
- Q: Should `add_link` skipping a layer be allowed to bypass the layer-7 Rack gating, or only up to layer 6?
- Q: Does a closed node refund or remove an already-visible reward preview (e.g. a revealed Elite), or is it silently gone?
