<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__13_paths_tethys; status ok; tokens in 6418 cache-write 0 cache-read 32007 out 1927; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_tet_hatch_fault: Hatch Fault

**Mechanic:** PATHS, corporation tethys, min_tier 2, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** A pressure-lock malfunction has opened a flooded service duct. Do you hold it open for a shortcut, force it shut behind you, or rewire it to a destination you can't see?

## TerminalEventData fields
- id: `ev_tet_hatch_fault`
- title: Hatch Fault
- speaker: STREET_MERC (1)
- text: "The bulkhead hatch is cycling by itself: open, seal, open, a hydraulic cough every four seconds. Condensation runs down the Terminal's screen. A maintenance light reads EQUALIZING, and nothing has equalized in an hour. Behind the hatch is a duct nobody drew on the map. Water pushes at the seal and the lock can't decide. Whatever you tell it, it will do for the rest of this dive."
- corporation_id: `tethys`
- min_tier: 2
- dispatch_clue: false
- foreshadows: `&""`
- weight: 1.0

## Choices

**1. Pin the hatch open (shortcut)**
- label: "Pin it open (+1 link, +4 Heat)"
- result_text: "The lock groans and holds. A wet, cold passage to the next layer, and every pressure sensor on the hull just logged the breach."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount 4
- reward: none
- map_edits (new): ADD_LINK from this node to a node two layers ahead (the lowest-index node not already linked). Permanent for this run.
- next_combat_overrides (new): none

**2. Force it sealed (safe lane)**
- label: "Force it shut behind you (-8 HP, -2 Heat)"
- result_text: "You lean on the wheel until the seal bites. Your shoulder pays for it. The duct stays drowned, and the hull's logs read as a clean seal."
- cycle_cost: 0
- hp_cost: 8
- effects: MODIFY_HEAT, target CAMPAIGN, amount -2
- reward: none
- map_edits (new): CUT_OPTION on the next layer: remove the Elite Router node with the highest index in that layer. If the layer has no Elite, reveal one random node's type (events RNG stream, checkpointed) instead.

**3. Rewire the lock (gamble on a destination)**
- label: "Rewire the lock (30 Cycles)"
- result_text: "You bridge the pressure sensor to the wrong relay. The hatch swings onto a duct that wasn't on any chart. Something in the dark is already moving toward the open door."
- cycle_cost: 30
- hp_cost: 0
- effects: none
- reward: Rare Firmware (working description: a sealed-slice chip, "Pressure Seal", gives a slice permanent ENCRYPTED and +1 output), granted only once the combat is won.
- map_edits (new): TURN_NODE: convert the next layer's lowest-index Router into an Elite Router; the duct reveals its type.
- starts_combat (new): none. Stake: the converted node is now an Elite fight (enemy `port_authority` is not used; it is `last_mile_enforcer`, a pursuit unit in the pressure ducts).
- combat_overrides (new): none

**4. Walk on**
- label: "Leave the hatch cycling"
- result_text: "You step over the coaming and let the lock argue with itself. Behind you the hatch coughs open again."
- cycle_cost: 0, hp_cost: 0, effects: none, map_edits (new): none

## Event wheel
Not used.

## Design notes
- **Three different edits, three different asks.** Choice 1 adds a link (a shortcut that skips a layer and its Cycles and Terminal chances) for Heat. Choice 2 cuts an option (a safer map) for HP. Choice 3 turns a node (a deliberate fight) for Cycles and a Firmware reward. None dominates. Choice 1 skips a fight and a shop layer, so its cost is lost income. Choice 2 costs about 13% of a 60 HP operative. Choice 3 is the only edit that increases risk on purpose.
- **Economy (GDD 11 placeholders):** +4 Heat is roughly a third of one Elite Router's Heat plus complications. -2 Heat is a modest sink, comparable to Billing Loop's "Kill the loop" at -1. 30 Cycles is about one Mainframe purchase, so choice 3 competes with the shop.
- **Determinism:** edits apply immediately at event resolution and are saved in run state. Only the fallback in choice 2 uses a named RNG stream. The map preview shows the new link or Elite before commit.
- **Interactions:** adding a link doesn't break the 7-layer rule for Rack layers 4 and 7. Under the full-graph display (D7) the new edge draws highlighted. An Elite conversion adds +1 Heat on clear per the Elite Router rule.
- **Text keys:** `evt.tet_hatch_fault.title`, `.text`, `.c1`–`.c4` labels and results, `map.edit.new_link`, `map.edit.node_converted`.

## Q:
- Q: Should ADD_LINK be allowed to skip over a Rack layer (4 or 7), or must it be capped to avoid bypassing the Rack?
- Q: Should the converted Elite be shown as a changed node before the player commits, or should the cost of the gamble include the surprise?
