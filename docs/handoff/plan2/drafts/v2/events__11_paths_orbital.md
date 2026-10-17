<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__11_paths_orbital; status ok; tokens in 4816 cache-write 0 cache-read 32585 out 2607; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, N-tags):** every `map_edits` line is now tagged "(N16, needs N2)". Fallbacks are data-only, built from Cycles/Heat/HP, and are listed in the notes.
- **Issue 2 (BLOCKER, enrage override):** `next_combat_overrides` is dropped from the whole event. Choice 2 now pays a real cost, `cycle_cost: 10`, and the result text says so ("She charges for the read"). The fix is applied exactly as the critic proposed.
- **Issue 3 (map_edits vocabulary):** ops are pinned to the N16 list, with `open_link` / `add_link` / `reveal_type` / `cut_option`. `remove_node` and `convert_node` are gone. `cut_option` re-links predecessors to successors and never empties a layer.
- **Issue 4 (determinism / preview):** tie-break rules (lowest node id) are now written in the field itself. The preview shows the exact link or node, and if the target is invalid the choice greys out with its reason.
- **Issue 5 (design quality):**
  - The false "Heat from routers" claim is removed.
  - Choice 1 notes "−2 fights, so fewer Cycles and cards".
  - The shortcut is validated against the layer 3-5 Mainframe guarantee: it may not bypass the only Mainframe layer. This is a rule, not just a warning, so the designer question is no longer open.
  - Choice 4 is no longer dominated, because choice 2 now costs 10 Cycles.
  - Choice 1 keeps +1 Heat. Quick math: it saves two fights' risk and costs Cycles/cards.
- **Issue 6 (economy):** choice 3 is re-priced against the GDD 11 economy: 6 HP for the cut plus 8 Cycles, not 15. HP is ~10% of a 60 HP operative. Cutting an Elite removes an optional threat but also its reward.
- **Issue 7 (text/title):** the title is unified as "A Favor on Pad Nine". The backstory is "she owes you", so the one-line decision no longer says "stranger".
- **Issue 8 (Q2):** the `okafor_debt` flag is tagged NEW: event flags.
- **Kept, because strong:** deterministic selection with an exact-edit preview, four distinct trade-offs, and the Orbital voice.

# ev_orb_pad_favor: A Favor on Pad Nine

**Mechanic:** PATHS, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Cash in a range tech's debt to reshape the map, and pick between speed, sight, safety, or keeping the favor unspent.

## TerminalEventData fields
- id: `ev_orb_pad_favor`
- title: A Favor on Pad Nine
- speaker: STREET_MERC
- text: "A night-shift range tech named Okafor waves you into a blast shelter at the foot of Pad Nine. Her brother's implant got bricked after a launch-delay surcharge, and your Cell paid the reactivation fee last winter. She has not forgotten. The pad's access grid is open on her slate: gates, service tunnels, one flagged crawlway. She can make one edit before the next window closes."
- corporation_id: `orbital`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Open the service tunnel
- label: Open the service tunnel (shortcut)
- result_text: "Okafor taps the slate. A maintenance hatch ahead unlatches. 'Walk it quiet. I never saw you.'"
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount +1 (her edit leaves a trace)
- reward: none
- (N16, needs N2) map_edits: `add_link`, one-way, from the node in layer+1 with the most outgoing links (tie: lowest node id) to the lowest-id non-Elite node in layer+3. Validation: the link may not bypass the only Mainframe layer within layers 3-5. If no valid target exists, the choice greys out with the reason.
- starts_combat: none

### 2. Buy the launch manifest
- label: Buy the launch manifest (scouting, 10 Cycles)
- result_text: "She charges for the read. Pad crews, gantry loads, what's fueled and what's waiting. You see the board before you step on it."
- cycle_cost: 10
- hp_cost: 0
- effects: none
- reward: none
- (N16, needs N2) map_edits: `reveal_type` on all nodes in layers +1 and +2 (this netrun; no layout change). Greys out if all are already revealed.

### 3. Seal the crawlway
- label: Seal the crawlway (cut an Elite, pay 6 HP)
- result_text: "The crawlway is a rat hole of live cable. Okafor shuts the hatch with you still in it. It hurts. Ahead, one Elite route just loses its door, and you strip the cable on the way out."
- cycle_cost: 0
- hp_cost: 6
- effects: GAIN_CYCLES, CAMPAIGN, amount +8 (salvage)
- reward: none
- (N16, needs N2) map_edits: `cut_option` on the nearest Elite Router ahead (tie: lowest node id): its predecessors are linked to its successors. Never empties a layer. If no Elite is ahead, or the cut would empty a layer, the choice greys out with the reason.

### 4. Leave the debt open
- label: Leave the debt open
- result_text: "'Suit yourself.' She pockets the slate. 'The favor stays on the books.'"
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- map_edits: none

## Design notes
- **Trade-offs:**
  - Choice 1 buys tempo: −2 fights, so fewer Cycles and cards, plus +1 Heat. A strong deck takes it.
  - Choice 2 costs 10 Cycles (~a third of a shop item) for information, so a planner can route toward Mainframes or around Elites.
  - Choice 3 spends about 10% of a 60 HP operative to remove one Elite and gain 8 Cycles. It suits a healthy run that wants safety, but it also forgoes that Elite's rewards.
  - Choice 4 keeps everything and is right when resources are tight.
- **Determinism:** all targets come from fixed rules with lowest-id tie-breaks. No RNG. The preview highlights the exact link or node and reads "NEW LINK", "REVEALED" or "SEALED".
- **Interactions:** Scrubber, Cold Exit and Clean Signal are unaffected. The Mainframe-guarantee validation keeps layers 3-5 intact.
- **Text keys:** `ev_orb_pad_favor.title`, `.text`, `.c1`-`.c4` labels and results; tooltips for the three edit states plus the grey-out reasons.
- **Fallback without N16:** choice 1 becomes +20 Cycles / +1 Heat; choice 2 costs 10 Cycles for nothing and is removed; choice 3 becomes 6 HP for 15 Cycles.

## Q:
- Q: Is a one-way `add_link` readable on the map without a new edge style?
- Q: Should the "favor" persist as a flag (`okafor_debt`, NEW: event flags) so a later Orbital event can call it in?
