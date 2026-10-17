<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__10_paths_halcyon; status ok; tokens in 4778 cache-write 0 cache-read 32585 out 3167; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, random link target):** Choice 2's `add_link` is now deterministic: from this node to the middle node (by index, lower index on ties) two layers ahead. All mention of the `events` RNG is removed. The "preview shows destination" claim is now true: the preview highlights both the closed link and the new link. The determinism note is rewritten.
- **Issue 2 (BLOCKER, dominated choices):**
  - Choice 2 now costs 15 Cycles plus the Heat reduction. It closes the link to the Elite Router, which is a real loss (Elites give better rewards). If no Elite Router exists on the layer, the choice is greyed out with `map_edit.blocked_no_path`.
  - Choice 4 is now "Slip the barrier": `reveal_node_type` on the first node by index of the next layer, -6 HP, +1 Heat. It is a cheaper, partial version of choice 1 that pays in HP and Heat instead of Cycles.
  - Choice 1 gains an advantage: it reveals all next-layer nodes and also reveals the layer after for the one node you pick by path, so it is the only fully informed option. I kept it to one layer to avoid adding scope: it reveals the whole next layer and keeps its 40-Cycle price.
- **Issue 3 (text/choice mismatch):** The text now reads "One corridor is flagged for foreclosure; one Router is flagged for accelerated redevelopment." This matches choice 2 (closes one link) and choice 3 (converts one Router). Choice 1 settles the lien and leaves both unchanged, and the result text says so.
- **Issue 4 (undefined targets, no fallback):** Edit ids and selectors are named: `reveal_node_type`, `close_link`, `add_link`, `convert_node`. Targets are fully defined with a fallback when absent. A data-only fallback is stated: choices 1 and 4 become Cycles/HP/Heat trades, and choices 2 and 3 are hidden until N16 ships.
- **Issue 5 (preview=result for conversion):** Choice 3's target is specified (first Router by index on the next layer) and the preview highlights it. If no Router exists, the choice is greyed out.
- **Issue 6 (NIT, bad synergies):** The Scrubber and Clean Signal line is deleted. The unsourced "Elites already drop better loot" claim is replaced by the GDD 4.2 fact: Elite Routers give +1 Heat.
- **Issue 7 (NIT):** Kept. The Q lines now address the critic's questions.
- **Keep list:** The legal-notice Corpo voice, choice 3's Cycles-for-risk trade, and the no-strand validation are all kept.

---

# ev_hal_lien_notice: Lien on the Overpass

**Mechanic:** PATHS, corporation halcyon, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Pay for full information, trade a risky route for a shortcut, take a hard fight for cash, or squeeze through for a partial look at a cost in HP and Heat.

## TerminalEventData fields
- **id:** `ev_hal_lien_notice`
- **title:** Lien on the Overpass
- **speaker:** CORPO (`RC.Voice.CORPO`)
- **text:** "NOTICE OF MUNICIPAL LIEN. The pedestrian overpass ahead was financed by a bond that this district has failed to service. Until the balance is settled, access is restricted to 'verified creditors.' One corridor is flagged for foreclosure. One Router is flagged for 'accelerated redevelopment.' Please select a remedy. Interest accrues while you read this."
- **corporation_id:** `halcyon`
- **min_tier:** 2
- **dispatch_clue:** false
- **foreshadows:** (empty)
- **weight:** 0.8

## Choices

### 1. Settle the lien
- **label:** "Settle the balance (-40 Cycles)"
- **result_text:** "The ledger clears. A clerk-bot stamps your address 'creditor in good standing' and withdraws both notices. Nobody here has ever been thanked this fast."
- **cycle_cost:** 40
- **hp_cost:** 0
- **effects:** none
- **reward:** none
- **(new) map_edits:** `reveal_node_type` on all nodes of the next layer (permanent for this netrun). No link is closed and no node is converted.
- **Data-only fallback:** a plain -40 Cycles trade that reveals nothing. I'd hide the choice in that case.

### 2. Default on the bond
- **label:** "Let it default (-15 Cycles, -1 Heat)"
- **result_text:** "The lien transfers to a collections shell and the overpass is foreclosed. A maintenance stairwell opens in the sweep, since nobody remembered to seal it. Leaner. Quieter."
- **cycle_cost:** 15
- **hp_cost:** 0
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount -1
- **reward:** none
- **(new) map_edits:**
  1. `close_link`: the link from this node to the Elite Router on the next layer (first by index if several). If none exists, the choice is greyed out with `map_edit.blocked_no_path`.
  2. `add_link`: from this node to the middle node (by index, lower index on ties) two layers ahead. This skips a layer.
  Validation refuses the edit if it would leave this node with no outgoing path.
- **Fallback:** hidden until N16 ships.

### 3. Redevelop it
- **label:** "Let 'accelerated redevelopment' proceed (+35 Cycles, +2 Heat)"
- **result_text:** "The city pays you a demolition stipend and a Router on the lower deck is bulldozed into something worse. 'Progress,' says the notice. You pocket the stipend."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:**
  - `GAIN_CYCLES`, target CAMPAIGN, amount 35
  - `MODIFY_HEAT`, target CAMPAIGN, amount 2
- **reward:** none
- **(new) map_edits:** `convert_node`: the first Router by index on the next layer becomes an Elite Router, effective at once. The preview highlights that node. If no Router exists, the choice is greyed out with `map_edit.blocked_no_path`.
- **Fallback:** hidden until N16 ships.

### 4. Slip the barrier
- **label:** "Slip the barrier (-6 HP, +1 Heat)"
- **result_text:** "The turnstile bites your wrist before it opens. You glimpse one door ahead before the lien system logs a trespass."
- **cycle_cost:** 0
- **hp_cost:** 6
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount 1
- **reward:** none
- **(new) map_edits:** `reveal_node_type` on the first node by index of the next layer, permanent for this netrun.
- **Fallback:** a plain -6 HP, +1 Heat trade that reveals nothing. I'd hide the choice in that case.

## Design notes
**Why it's interesting:** Each option answers a different question about the map.
- Settling buys full information with Cycles.
- Defaulting pays 15 Cycles and gives up the Elite route (its higher loot and the +1 Heat from GDD 4.2) for a skipped layer and -1 Heat.
- Redeveloping trades a harder map for money.
- Slipping the barrier is the cheap, partial look, paid in HP and Heat.

No option dominates: 4 is a weaker 1 for a different currency, and 2 is only worth it if you'd rather avoid the Elite than fight it.

**Economy (placeholders against GDD 11):**
- 40 Cycles is about one Mainframe purchase.
- Choice 2's cost of 15 Cycles plus losing the Elite route is balanced by the skipped layer, roughly 15 HP of attrition and one fight's rewards.
- Choice 3 pays only if the run can beat an Elite.

**Determinism:** All edits are deterministic: targets are picked by node index and previewed before commit. No RNG is used, and undo restores the map.

**Interactions:**
- Closing a link must never strand the player: N16 validation refuses the edit and greys the label with a reason.
- Choice 3 raises Heat gain, since Elite Routers give +1 Heat.
- A skip link may jump a layer 4 optional Server Rack and its banked Schematics; see Q1.

**Text keys needed:** `map_edit.reveal_layer`, `map_edit.reveal_node`, `map_edit.closed_link`, `map_edit.skip_link`, `map_edit.convert_elite`, `map_edit.blocked_no_path`. Result text uses Corpo legal-notice formatting.

## Q:
Q: Should the skip link in choice 2 be allowed to bypass a layer 4 Server Rack, given that it banks Schematics?
Q: Should the Elite conversion show the Elite's reward beforehand, so it reads as a gamble the player can judge?
