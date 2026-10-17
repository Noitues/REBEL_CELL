<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__12_paths_aurelian; status ok; tokens in 6419 cache-write 0 cache-read 32007 out 2137; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_aur_verdict_broadcast: Live Verdict Feed
**Mechanic:** PATHS, corporation aurelian, min_tier 2, weight 1.0, dispatch_clue false, foreshadows none
**One-line decision:** Spend Cycles or HP so the live arena broadcast reveals or opens a route, or sell the same airtime for a safe cut that closes a lane the crowd is watching.

## TerminalEventData fields
- id: `ev_aur_verdict_broadcast`
- title: Live Verdict Feed
- speaker: STREET_MERC (the operative commenting over the feed)
- text: "The Terminal is locked onto an Aurelian arena broadcast: BREAD. CIRCUS. TERMS APPLY. A caption crawl lists today's VERDICTS, and each one is a route in this netrun. The Lanista's announcer reads the odds like a weather report. Patrons are betting on which lanes the clients survive, and the house will pay out on whatever you make interesting. Your cut-in window is about ten seconds."
- corporation_id: `aurelian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 1.0

## Choices

**1. Bet on the Lanista's card (reveal and open)**
- label: "Read the odds, back the favorite (-20 Cycles)"
- result_text: "The crawl names the favorite lane and the sealed lane behind it. You bet against the house's own tell. Doors you couldn't see are suddenly marked."
- cycle_cost: 20
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits (all on the current netrun map, next two layers ahead of the player):
  - `reveal_type`: every node on the next layer.
  - `open_link`: one locked cross-link, chosen deterministically as the first by node id order.
- (new) starts_combat: none
- (new) next_combat_overrides: none

**2. Enter the arena feed (fight for the crowd)**
- label: "Step into the sand (impromptu fight, -6 HP)"
- result_text: "You hijack the feed and the crowd roars. A client-class enforcer is dropped in to give the patrons a show. Win, and the Lanista has to honor the terms: a shortcut opens."
- cycle_cost: 0
- hp_cost: 6
- effects: none
- reward: none
- (new) starts_combat: enemy `geostationary_guard` (elite, per its corporation-agnostic stats; no override of its ids). Stake: on win, `map_edits` apply. On loss, normal death rules.
- (new) combat_overrides: enemy `enrage` start turn 8 (the elite default), duration this fight only. The crowd wants a finish.
- (new) map_edits (on win only):
  - `add_link`: from the current node straight to the layer-after-next node with the lowest id.
  - `cut_layer_option`: remove one node from the next layer, chosen as the highest-id Router. This is the "house takes its cut".
- Note: `geostationary_guard` is Orbital, so placeholder; swap to the Aurelian elite once one exists.

**3. Sell the airtime (safe cut, closes a lane)**
- label: "Sell the cut-in slot to a Patron (+35 Cycles, +2 Heat)"
- result_text: "A Patron's agent buys your ten seconds for a sponsor spot. They also ask that you stay out of the main lane so the feed has a clean picture. You take the money."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 35; MODIFY_HEAT, target CAMPAIGN, amount 2
- reward: none
- (new) map_edits: `close_link` (the first outgoing link from the current node, by id order, leaving at least one path), then `cut_layer_option` on the next layer's highest-id Terminal if one exists.

**4. Mute it**
- label: "Mute the feed and move on"
- result_text: "The crawl keeps scrolling without you. Somewhere a patron groans."
- No costs, no effects.

## Event wheel
Not used.

## Design notes
- **Tension:** Choice 1 is information plus a quiet shortcut and costs a flat 20 Cycles (about one shop item's worth of a typical early-run balance). Choice 2 can pay out the most (a shortcut that skips a node) but is a real elite fight for 6 HP up front, and it also cuts one of your own options. Choice 3 is the greedy safe option, and its payment is a narrower map and Heat. Choice 4 keeps the run untouched.
- **Why none dominates:** Reveal helps you plan around Elites and Racks, but a good route already exists in many runs. The fight is worth it only when your build kills an elite in 6 to 8 turns. The sale is best on a run starving for Cycles and is worst when your next layer holds a Mainframe or Terminal you wanted.
- **Determinism:** All map edits pick targets by node id order with no RNG. The preview can list the exact nodes and links changed before commit. Choice 2's edits fire only after the combat result.
- **Corporation fit:** The patron, client, Lanista and VERDICT framing is carried by the text, and the "house cut" removing a node mirrors Aurelian terms-apply flavor.
- **Dependencies:** N16 (`map_edits`, `starts_combat`, `combat_overrides`) is required for choices 1 to 3. Data-only fallback: choice 3 keeps its Cycles and Heat effects without the map edits, and choice 1 becomes a plain Cycles-for-nothing trade, so keep N16 as a build prerequisite.
- **Text keys:** `ev_aur_verdict_broadcast.title`, `.text`, `.c1` to `.c4` labels and results, `map_edit.reveal_next_layer`, `map_edit.house_cut`.

## Q:
- Q: Should `cut_layer_option` ever be allowed to remove the only remaining path to a Server Rack, or must the edit validator refuse it?
- Q: Should an Aurelian elite replace `geostationary_guard` in choice 2 before the content pass, or is a borrowed enemy acceptable for a draft?
