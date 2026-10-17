<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__09_paths_meridian; status ok; tokens in 6417 cache-write 0 cache-read 32007 out 1943; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_mer_wrong_address: Wrong Address

**Mechanic:** PATHS, corporation meridian, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Sign for a mis-routed freight pod to force a different path on the map, or refuse it and keep the route you planned.

## TerminalEventData fields
- id: `ev_mer_wrong_address`
- title: Wrong Address
- speaker: NARRATOR (0)
- text: "A sealed freight pod sits in the Terminal's receiving slot, its label flashing DELIVERY ATTEMPT 3 OF 3. The address is a node two layers ahead, one that doesn't exist on your map. A courier drone hovers over it and refuses to leave until someone signs. Meridian never forgets a parcel. It only reroutes the blame."
- corporation_id: `meridian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Sign for it
- label: "Sign for it (open a hidden route)"
- result_text: "The drone chirps, DELIVERED, and peels off. The pod's manifest bleeds a route into your map, a lane Meridian pretends isn't there."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / +2
- reward: none
- (new) map_edits:
  - ADD_LINK: from the current node to a non-adjacent node 2 layers ahead (the first Mainframe, or Elite Router if none), skipping 1 layer
  - REVEAL_TYPE: that target node's type
- (new) next_combat_overrides: none

### 2. Redirect it
- label: "Redirect the pod (fight the recipient, 15 Cycles of Loot)"
- result_text: "You re-label it to an angry address. The recipient's enforcer arrives to collect, and the pod's contents are yours if you beat him."
- cycle_cost: 0, hp_cost: 0
- effects: none
- reward: Common Firmware (working description: "Tracked Parcel": +1 Cycle per Router cleared)
- (new) starts_combat: `tariff_collector`
  - overrides: enemy HP ×1.0, +1 pointer for the fight (uneven, ticks 0 / 11)
  - stake: lose the fight and the pod is seized, so no reward and 4 HP lost.
- (new) map_edits: CLOSE_LINK: the shortcut to a Mainframe in the next layer (the route the enforcer was guarding)

### 3. Open it
- label: "Cut it open (−6 HP, 40 Cycles, a layer thins)"
- result_text: "Packing foam, a cracked ledger, and a damaged anti-theft charge that bites your hand. The cargo is cash. The blast scorches a node off the board."
- cycle_cost: 0
- hp_cost: 6
- effects: GAIN_CYCLES / CAMPAIGN / +40
- reward: none
- (new) map_edits:
  - REMOVE_OPTION: from the next layer that has 3 or more nodes, remove 1 node (the first non-Router; fall back to the last node in list order). It is never the final Rack.

### 4. Refuse
- label: "Refuse delivery"
- result_text: "The drone logs a Return to Sender and leaves. The route stays the way it was."
- cycle_cost: 0, hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: none

## Design notes
- **Four different prices on the same pod.** Sign gives access, Redirect gives a fight for loot, Open gives money while taking away an option, Refuse keeps the status quo. None dominates:
  - **Sign** (+2 Heat) trades Heat for a shortcut that skips one layer. That saves roughly 2 minutes of a ~15-minute run, and revealing the target node's type makes the skip a planned one.
  - **Redirect** is a Normal-strength fight at a single pointer-modified `tariff_collector`. Expected loss is about 8–12 HP, per the T2 intake target. Reward is a low-value Firmware that pays back slowly. Closing the Mainframe link hurts the player who planned to shop, so it gets weighed against Sign's lane to the same node.
  - **Open** is 40 Cycles and −6 HP (about 10 % of a Breaker's 60 HP). A typical run earns ~100–140 Cycles, so 40 is a big share. Cutting a node reduces choice rather than damage; the player must read the map first, because the "remove the first non-Router" rule is deterministic and previewable.
  - **Refuse** is the safe line and costs nothing.
- **Determinism:** no randomness. Every map_edit picks its target by a stated, fixed rule, so the choice preview can name the node. The `tariff_collector` uses the normal combat seeding, and its pointer override is data.
- **Interactions:** Sign and Redirect conflict on the same Mainframe link (one opens, one closes), so a player who takes one cannot take the other from the same Terminal. Open's removed node can't be the final Rack. Scrubber and Proxy Relay lower the cost of the +2 Heat.
- **Text keys:** `ev_mer_wrong_address.title/text`, one label/result key per choice, and a map tooltip, "Hidden lane: a delivery nobody signed for."

## Q:
Q: When Open cuts a node, should the preview name the node (clear) or only say "a node in layer N" (more tension)?
Q: Should Sign's added link be one-way, so the shortcut can't be used to retreat?
