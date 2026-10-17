<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__12_paths_aurelian; status ok; tokens in 3588 cache-write 0 cache-read 32585 out 1496; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/12_paths_aurelian

**Verdict:** FIX

## Issues

1. **BLOCKER, ids / systems:** Choice 2 uses `geostationary_guard`, an Orbital enemy, as an Aurelian event fight. It exists in the inventory, so the id is valid. But the draft admits it is a placeholder and then asks in Q2 whether that is acceptable. The template asks for ids from the given list, and Aurelian has no enemies yet. A cross-corporation borrow is a content-integrity problem, not a rules one. Fix: either tag the fight as "enemy chosen from the existing pool, corporation-agnostic" or move the elite to a data-only slot.

2. **BLOCKER, systems / R1 and R4:** `combat_overrides: enrage start turn 8 (the elite default)` overrides nothing. Elite enrage is already 8 by default (R4), so the override is a no-op and misrepresents the stake. It also cites "6 to 8 turns" as the fight length without any HP-phase arithmetic. Fix: drop the override, or make it a real change (see fixes).

3. **MAJOR, N16 / stake:** Choice 2's `map_edits` fire "on win only", but there is no stake or reward for the elite beyond the edits. Choice 2 also carries a built-in penalty (`cut_layer_option`) that the player cannot see in the label. An elite fight for a shortcut plus a self-cut is likely dominated by Choice 4. Choice 1 reveals a layer and opens a link for 20 Cycles, which is strictly cheaper and risk-free.

4. **MAJOR, design quality / dominance:** Choice 3 pays +35 Cycles net, while Choice 1 costs 20. The Heat of +2 is trivial next to those amounts, so Choice 3 beats Choice 4 on any run that does not need the targeted node. Choice 3's closure also targets a "Terminal if one exists", so the cost is unknown at decision time.

5. **MAJOR, determinism / preview:** `close_link` "leaving at least one path" and `cut_layer_option` have no validator specified for Server Rack reachability (the draft's own Q1). This must be answered in the draft, not left open: the safe answer is that the validator refuses edits that disconnect the final Rack.

6. **NIT, template:** `effects: none` on Choice 1, and Choice 4 omits the fields. The text keys list is incomplete, since choice 4 has a result string. The text runs 5 sentences, which is fine.

7. **NIT, spelling:** US spelling is fine ("honor", "favorite"). The speaker "STREET_MERC" matches the Voice enum.

## Concrete fixes

- **Fix 1/2:** Replace the fight line with: `starts_combat: enemy geostationary_guard (placeholder until the Aurelian elite exists; swap is data-only), stake: on win map_edits apply plus reward 25 Cycles`. Remove the enrage override.
- **Fix 3:** Make the cut visible in the label: "Step into the sand (-6 HP, elite fight; win: shortcut, but the house takes a node)". Replace the cut with a mild one: `cut_layer_option` removes the highest-id *Router* only if two or more Routers remain on the layer. Add reward: 25 Cycles on win.
- **Fix 4:** Raise Choice 3's cost: `MODIFY_HEAT +4` and cut the next layer's highest-id Terminal or Mainframe, stated in the label: "Sell the slot (+35 Cycles, +4 Heat, a lane closes)".
- **Fix 5:** Add to Design notes: "The N16 validator refuses any `close_link` or `cut_layer_option` that would leave the final Rack unreachable. If refused, the choice falls back to its Cycles/Heat effects only."

## Keep

- The deterministic, id-order target selection, with the exact nodes shown in the preview.
- Three different PATHS verbs (reveal/open, add/cut, close/cut) across the choices.
- The Choice 3 premise (the airtime sale narrows the map) is a good, thematic price.

## Q:

- Q: Should map-edit previews list the exact node ids, or only the edit kinds, to preserve some uncertainty about a closure?
- Q: Is the fight's 6 HP up-front cost necessary, given the elite already costs HP in combat?
