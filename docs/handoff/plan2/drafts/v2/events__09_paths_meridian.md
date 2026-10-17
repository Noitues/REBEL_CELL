<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__09_paths_meridian; status ok; tokens in 4903 cache-write 0 cache-read 32585 out 3109; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, Redirect combat):** dropped the +1 uneven pointer. The override is now `enemy damage +25 %, no HP change`, a tier-independent buff (R2). It is tagged N16 (needs N2) with a data-only fallback. The intake arithmetic is rebuilt (see notes) instead of the unsupported "8–12 HP".
- **Issue 2 (BLOCKER, map_edit semantics):** Redirect's CLOSE_LINK now removes one link into the next layer's Mainframe, and only if that Mainframe keeps at least 1 other inbound link and that link's source keeps at least 1 other outbound link. Otherwise no edit. The false "Sign/Redirect conflict" bullet is deleted. Open's removal now has the same connectivity guard.
- **Issue 3 (N# tags and fallback):** all new fields are tagged N16 (needs N2), and a data-only fallback is stated.
- **Issue 4 (fiction/mechanics, layer condition):** the event is offered only on layers 1–5. The text now says "a node two layers ahead your map hasn't drawn yet". ADD_LINK targets the first Mainframe two layers ahead, else the first Router, else no edit. It never targets an Elite.
- **Issue 5 (label/reward mismatch):** the label is now "Redirect the pod (fight the recipient's enforcer)". The reward is the existing common Firmware Patch+. The invented Cycle-income Firmware is gone.
- **Issue 6 (Open dominates):** hp_cost 8, Cycles +30. The removed node is the Mainframe in that layer if one exists, else the first Router, with the connectivity guard.
- **Issue 7 (Sign overstated):** Heat +4. The ADD_LINK is one-way, which answers v1's Q2. The "saves 2 minutes" claim is dropped. A skipped layer's loot is named as the cost.
- **Issue 8 (nit):** speaker is `NARRATOR`. The ad hoc "4 HP lost" stake is replaced by "no reward". Defeat is already death by the normal combat rules.
- **Critic Q on REVEAL_TYPE and Server Racks:** the type is revealed but never the Exploit; this is stated in the notes. The other critic Q (a link bypassing a layer's Mainframe guarantee) is acceptable and noted, since the guarantee is for the generated map and the player opts into the bypass.
- **Kept:** four distinct prices, fixed target rules, the Final-Rack protection, and the "reroutes the blame" voice.

# ev_mer_wrong_address: Wrong Address

**Mechanic:** PATHS, corporation meridian, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows. Offered only on layers 1–5.
**One-line decision:** Sign for a mis-routed freight pod to open a one-way lane that skips a layer (and its loot), fight the recipient's enforcer for Firmware, cut the pod open for cash at the cost of a map option, or refuse.

## TerminalEventData fields
- id: `ev_mer_wrong_address`
- title: Wrong Address
- speaker: NARRATOR
- text: "A sealed freight pod sits in the Terminal's receiving slot, its label flashing DELIVERY ATTEMPT 3 OF 3. It's addressed to a node two layers ahead that your map hasn't drawn yet. A courier drone hovers over it and refuses to leave until someone signs. Meridian never forgets a parcel. It only reroutes the blame."
- corporation_id: `meridian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Sign for it
- label: "Sign for it (+4 Heat, open a one-way lane)"
- result_text: "The drone chirps DELIVERED and peels off. The manifest bleeds a lane into your map, a route Meridian pretends isn't there."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / +4
- reward: none
- (new) map_edits (N16, needs N2):
  - ADD_LINK, one-way, from the current node to the first Mainframe two layers ahead, else the first Router two layers ahead, else no edit.
  - REVEAL_TYPE: that target node. Never a Server Rack's Exploit.
- (new) next_combat_overrides: none

### 2. Redirect it
- label: "Redirect the pod (fight the recipient's enforcer)"
- result_text: "You re-label it to an angry address. The recipient's enforcer arrives to collect, and the pod is yours if you win."
- cycle_cost: 0, hp_cost: 0
- effects: none
- reward: Common Firmware Patch+ (slice output +50 %)
- (new) starts_combat (N16, needs N2): `tariff_collector`
  - combat_overrides: enemy damage +25 %, no HP change, this fight only.
  - stake: lose and there is no reward; defeat follows normal run rules.
- (new) map_edits (N16): CLOSE_LINK, one link into the next layer's Mainframe, only if that Mainframe keeps at least 1 other inbound link and that link's source keeps at least 1 other outbound link. Otherwise no edit.

### 3. Open it
- label: "Cut it open (−8 HP, +30 Cycles, a node is lost)"
- result_text: "Packing foam, a cracked ledger, and an anti-theft charge that bites your hand. The cargo is cash. The blast scorches a node off the board."
- cycle_cost: 0
- hp_cost: 8
- effects: GAIN_CYCLES / CAMPAIGN / +30
- reward: none
- (new) map_edits (N16): REMOVE_OPTION in the next layer that has 3 or more nodes. The target is the Mainframe in that layer if one exists, else the first Router. Never the final Rack. Skipped if removal would disconnect any node from the start or the final Rack.

### 4. Refuse
- label: "Refuse delivery"
- result_text: "The drone logs a Return to Sender and leaves. The route stays as it was."
- cycle_cost: 0, hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: none

## Design notes
- **Four prices on one pod.** None dominates:
  - **Sign** skips one layer, so it also skips that layer's combat loot and any shop there. +4 Heat is about 40 % of a MINOR step, small but real. It rewards a player who is already strong or short on time. The one-way link means no retreat.
  - **Redirect:** `tariff_collector` is a normal enemy (R1, 1 phase) at T2 with an R2 HP band of 34–44. At the reference 11 damage per turn, that is about 3.5 turns to kill. Its +25 % damage is a flat buff that doesn't depend on tier. If its base intake is in the T2 normal band of ~3–5 per turn, the buffed fight costs about 4–6 HP over 3.5 turns. That is the arithmetic placeholder; the sim must confirm it. The reward is a modest common Firmware. The Mainframe link closure only happens when it is safe, so the cost is lost flexibility, never a lockout.
  - **Open** is +30 Cycles for 8 HP (about 13 % of a Breaker's 60) and a thinner layer. A typical run earns ~100–140 Cycles, so 30 is roughly a quarter. Losing a Mainframe option can cost more than 30 Cycles of shopping to a player who relied on it, which is the tension.
  - **Refuse** is the safe line and costs nothing.
- **Determinism:** no randomness. Every map_edit has a fixed target rule and a stated guard, so the choice preview can name the node or say "no edit". `tariff_collector` uses normal combat seeding.
- **Interactions:** the choices are mutually exclusive. Open and Redirect cannot disconnect the graph or remove the final Rack. Scrubber and Proxy Relay offset Sign's Heat. A Sign link may bypass a layer's guaranteed Mainframe; that is accepted because the player chose it.
- **Fallback (no N16):** Sign = +4 Heat with a Cycle reward in place of the lane; Redirect = a plain `tariff_collector` combat with no overrides; Open = +30 Cycles / −8 HP with no map edit. The event stays playable but loses its PATHS identity, so it should be deferred until N16 lands.
- **Text keys:** `ev_mer_wrong_address.title/text`, one label/result key per choice, a map tooltip "Hidden lane: a delivery nobody signed for."

## Q:
Q: When Open cuts a node, should the preview name the node (clear) or say only "a node in layer N" (more tension)?
Q: Should Sign's lane skip the intervening layer's loot entirely, or should the player still collect one reward on the way?
