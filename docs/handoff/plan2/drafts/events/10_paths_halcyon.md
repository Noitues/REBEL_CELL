<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__10_paths_halcyon; status ok; tokens in 6417 cache-write 0 cache-read 32007 out 1983; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_hal_lien_notice: Lien on the Overpass

**Mechanic:** PATHS, corporation halcyon, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Pay down a municipal lien to keep a layer's options open, or work the debt off by closing a route and opening a shortcut that someone else already paid for.

## TerminalEventData fields
- **id:** `ev_hal_lien_notice`
- **title:** Lien on the Overpass
- **speaker:** CORPO (`RC.Voice.CORPO`)
- **text:** "NOTICE OF MUNICIPAL LIEN. The pedestrian overpass ahead was financed by a bond that this district has failed to service. Until the balance is settled, access is restricted to 'verified creditors.' Two corridors are flagged for foreclosure; one is flagged for 'accelerated redevelopment.' Please select a remedy. Interest accrues while you read this."
- **corporation_id:** `halcyon`
- **min_tier:** 2
- **dispatch_clue:** false
- **foreshadows:** (empty)
- **weight:** 0.8

## Choices

### 1. Settle the lien
- **label:** "Settle the balance (-40 Cycles)"
- **result_text:** "The ledger clears. A clerk-bot stamps your forwarding address as 'creditor in good standing.' Nobody here has ever been thanked this fast."
- **cycle_cost:** 40
- **hp_cost:** 0
- **effects:** none
- **reward:** none
- **(new) map_edits:** on the next layer, `reveal_node_type` on all nodes (duration: permanent for this netrun). Reveals every node's type on the next layer, and no route is closed.

### 2. Default on the bond
- **label:** "Let it default (-1 Heat)"
- **result_text:** "The lien transfers to a collections shell and the overpass shuts. A maintenance stairwell opens in the foreclosure sweep, since nobody remembered to seal it. Leaner. Quieter."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount -1
- **reward:** none
- **(new) map_edits:**
  1. `close_link`: the link from this node to the layer's highest-tier option (the Elite Router if one exists, otherwise the Mainframe).
  2. `add_link`: from this node to a random node two layers ahead, picked from the `events` RNG stream at a checkpoint. This skips a layer.

### 3. Redevelop it
- **label:** "Let 'accelerated redevelopment' proceed (+35 Cycles, +2 Heat)"
- **result_text:** "The city pays you a demolition stipend and a Router on the lower deck is bulldozed into something worse. 'Progress,' says the notice. You pocket the stipend."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:**
  - `GAIN_CYCLES`, target CAMPAIGN, amount 35
  - `MODIFY_HEAT`, target CAMPAIGN, amount 2
- **reward:** none
- **(new) map_edits:** `convert_node`: one Router on the next layer (first by node index; deterministic) becomes an Elite Router. The edit takes effect at once.

### 4. Pick the lock
- **label:** "Slip the barrier (-6 HP)"
- **result_text:** "The turnstile bites your wrist before it opens. You're through, and the lien system logs a trespass instead of a payment."
- **cycle_cost:** 0
- **hp_cost:** 6
- **effects:** none
- **reward:** none
- **(new) map_edits:** none. The choice leaves every route as it was and reveals nothing.

## Design notes
**Why it's interesting:** Each option is a different answer to "what do I want from the map?" Settling buys information, defaulting trades a risky fight for a faster, quieter route, redeveloping makes the map harder for money, and the lock pick buys nothing and costs HP. The fourth option is the baseline that tests whether the three edits are worth their prices.

**Economy (placeholders against GDD 11):** 40 Cycles is about one Mainframe purchase, which makes information expensive. The shortcut is worth skipping a layer of about 15 HP of attrition and one fight's rewards. The Elite conversion at +35 Cycles pays for itself only if the run has the HP and build to win it, and Elites already drop better loot.

**Determinism:** The only randomness is the target node of the skip link in choice 2, drawn from the `events` stream at a checkpoint. The choice preview shows the destination before commit, and undo restores it. Choices 1 and 3 pick targets by node index.

**Interactions:**
- Closing a link must never strand the player. N16 validation should refuse an edit that leaves the node with no outgoing path, and the label should then be greyed out with a reason.
- The conversion in choice 3 raises Heat gain, since Elite Routers give +1 Heat.
- It works with Scrubber and Clean Signal, because Heat reduction in choice 2 is minor but synergizes.

**Text keys needed:** `map_edit.reveal_layer`, `map_edit.closed_link`, `map_edit.skip_link`, `map_edit.convert_elite`, and a refusal key `map_edit.blocked_no_path`. The Corpo voice uses legal notice formatting in the result text.

## Q:
Q: Should closing the link target the highest-tier option deterministically, or should the player see all links and choose which one to foreclose?
Q: Does the skip link in choice 2 bypass a Server Rack at layer 4, or must it never skip a layer holding a Rack?
