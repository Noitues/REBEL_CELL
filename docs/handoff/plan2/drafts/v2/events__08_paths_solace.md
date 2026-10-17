<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__08_paths_solace; status ok; tokens in 4914 cache-write 0 cache-read 32585 out 3008; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, inconsistent fields):** kept, because the critic's point is correct. Every choice now lists the full field set (label, result_text, cycle_cost, hp_cost, effects, reward, starts_combat, next_combat_overrides, map_edits, event_wheel), with "none" where empty. `dispatch_clue` and `foreshadows` are now typed values (`false`, `""`).
- **Issue 2 (BLOCKER, Terminal vs Rest, near-dominance):** choice 3 now uses `convert_node` to turn a next-layer node into a Rest. The Rest (D4) heals or swaps Firmware locations. Cost is 30 Cycles. The Terminal claim and the "Rest-type payoff" mismatch are deleted. Because the Rest heals, it competes with choice 1's HP cost instead of being a weak event.
- **Issue 3 (MAJOR, determinism timing):** the `events` stream now rolls the closed node once, when the Terminal opens. The result is checkpointed and shown on the card as "CLOSES: {name}" before any choice. The determinism note says so.
- **Issue 4 (MAJOR, choice 1 too strong, layer skip):** replaced the layer skip with `add_link` from the current node to one named next-layer node, plus `close_node` on a different named node in that layer. There is no layer skip, so no Rack bypass and no unsupported Elite-guarantee claim. Both edits show on open as "LINK: A→C, CLOSES: B". Old Q1 is resolved and removed.
- **Issue 5 (MAJOR, arithmetic and unsourced income):** the Heat line is now "+2 Heat is about a fifth of a MINOR step (every 10)". The unsourced Cycles-per-combat figure is marked placeholder.
- **Issue 6 (MAJOR, named targets / UI field):** targets are now named by the event on open, not chosen by the player. This removes the unspecified picker UI. Choice 3's target is also named. The "Collections lift" and "Ward 9" lines stay as fiction only.
- **Issue 7 (NIT):** the choice 2 label no longer says "+0 Cycles"; it shows its real cost. The `dispatch_clue` and `foreshadows` fields are typed.
- **Issue 8 (NIT, choice 2 dominance):** `reveal_type` is restricted to the next layer only, with `cycle_cost` 10.
- **Critic Q's:** the committed-path question is handled by a validator rule: the close target is rolled only among nodes that aren't on the player's current selected route, and never the last option on a layer. The Rest-before-it-exists question is answered by the Fallback note below.
- **Rulings check:** no conflict. D4 Rest and N16 are used as ruled.

---

# ev_solace_wellness_hold: Wellness Hold

**Mechanic:** PATHS (N16 map_edits), corporation solace, min_tier 2, weight 0.8, dispatch_clue false, foreshadows ""
**One-line decision:** Spring a sedated subscriber to open one named route and shut another, pay to turn a node into a Rest, buy a look at the next layer, or walk on.

## TerminalEventData fields
- id: `ev_solace_wellness_hold`
- title: Wellness Hold
- speaker: STREET_MERC
- text: "The Terminal sits in a corridor of frosted doors, each stenciled WELLNESS HOLD, VOLUNTARY. Behind the glass of door 6 a man in a Solace gown presses his dead implant to the pane, mouthing a number: his arrears. The door log says he agreed to the stay. The signature is a thumbprint taken while he was sedated. The card on the Terminal reads: LINK {A}→{C}, CLOSES {B}. He knows which corridors Collections will weld shut the moment this door opens."
- corporation_id: `solace`
- min_tier: 2
- dispatch_clue: false
- foreshadows: ""
- weight: 0.8

## Choices

### 1. Spring him
- label: Spring him (-8 HP, +2 Heat)
- result_text: "The lock gives. He hands you a route sheet, shaking. A shutter drops down the hall, welded from the other side."
- cycle_cost: 0
- hp_cost: 8
- effects: MODIFY_HEAT, CAMPAIGN, amount 2
- reward: none
- (new) starts_combat: none
- (new) combat_overrides / next_combat_overrides: none
- (new) map_edits:
  - `add_link`: current node → named next-layer node C (never a Rack, never B).
  - `close_node`: named next-layer node B, rolled by the `events` stream at open time, excluding nodes on the selected route and never the layer's last option.
- (new) event_wheel: none

### 2. Sell the complaint
- label: Sell the complaint (-10 Cycles)
- result_text: "You file it as a formal Grievance Packet. The Terminal pays in a readout of the next layer. The man is moved to Ward 9. The door closes."
- cycle_cost: 10
- hp_cost: 0
- effects: none
- reward: none
- (new) starts_combat: none
- (new) combat_overrides / next_combat_overrides: none
- (new) map_edits: `reveal_type` on every node in the next layer only.
- (new) event_wheel: none

### 3. Pay the arrears
- label: Pay the arrears (-30 Cycles)
- result_text: "Thirty Cycles clears his balance and his implant lights. He walks you to a maintenance hatch. Behind it, a bunk and a med-cart nobody logged."
- cycle_cost: 30
- hp_cost: 0
- effects: none
- reward: none
- (new) starts_combat: none
- (new) combat_overrides / next_combat_overrides: none
- (new) map_edits: `convert_node`: named next-layer non-Rack node D becomes a Rest (heal, or swap Firmware locations), plus `add_link` from the current node to D if absent. D is shown on open.
- (new) event_wheel: none

### 4. Leave him
- label: Walk on
- result_text: "You don't look at door 6. The glass fogs, then clears."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- (new) starts_combat: none
- (new) combat_overrides / next_combat_overrides: none
- (new) map_edits: none
- (new) event_wheel: none

## Design notes
- **Why it's interesting:** each choice spends a different resource on a different change to the map. Spring him costs HP and Heat for one shortcut plus one lost option. Sell the complaint is cheap information, worth little if the layer is already readable. Pay the arrears is the priciest choice and buys a heal or Firmware swap on the route, so it competes with Spring him's HP cost: a hurt player pays Cycles, a rich one saves HP. Walk on keeps everything. If the card shows B is a node you wanted, option 1 loses value; if C is an Elite you want to dodge, it gains.
- **Economy (placeholders, pending sim):** 30 Cycles is roughly one shop item; early-run income per combat is a placeholder. 8 HP is about 13% of a Breaker's 60. +2 Heat is about a fifth of a MINOR step (every 10).
- **Interactions:** no layer is skipped, so Rack gating and Elite frequency are untouched. Scrubber and Cold Exit are unaffected. The validator refuses a close that would leave a layer with no option.
- **Determinism:** the `events` stream rolls the closed node once, when the Terminal opens. The result is checkpointed and shown on the card as "CLOSES: {name}" before any choice, so Rewind can't reroll it and the preview equals the result. Nodes C and D are chosen by fixed rule (lowest id that meets the conditions), with no extra rolls.
- **Fallback without N16:** none for map edits. A data-only fallback would be choice 3 as a heal effect for 30 Cycles, and choice 1 as hp_cost 8 plus MODIFY_HEAT with no route change. Rest depends on the D4 node existing; until then, choice 3 uses the heal fallback.
- **Text keys:** `ev_solace_wellness_hold.*` (title, text, 4 labels, 4 results), plus preview strings "LINK: {A}→{C}", "CLOSES: {B}", "TYPES REVEALED", "BECOMES REST: {D}".

## Q:
- Q: Should the player be allowed to see all of A, B, C and D before the first click, or only the edits relevant to the hovered choice?
- Q: Should a closed node stay on the map as a greyed "WELDED" node, or be removed?
