<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__11_paths_orbital; status ok; tokens in 6416 cache-write 0 cache-read 32007 out 1947; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_orb_pad_favor: A Favor on Pad Nine

**Mechanic:** PATHS, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Take a stranger's favor and have the map reshaped for you, or lean on the pad crew's debt and pay in a different currency.

## TerminalEventData fields
- id: `ev_orb_pad_favor`
- title: Pad Nine Favor
- speaker: STREET_MERC (1)
- text: "A night-shift range tech named Okafor waves you into a blast shelter at the foot of Pad Nine. She says her brother's implant got bricked after a launch-delay surcharge, and your Cell paid his reactivation fee last winter. She has not forgotten. The pad's access grid is open on her slate: gates, service tunnels, one flagged crawlway. She can edit one thing before the next window closes. A favor, she says, is the only currency Orbital can't repossess."
- corporation_id: `orbital`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. "Open the service tunnel"
- label: Ask for the service tunnel (a shortcut)
- result_text: "Okafor taps the slate. A maintenance hatch two layers ahead unlatches. 'Walk it quiet,' she says. 'I never saw you.'"
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount +1 (her edit leaves a trace)
- reward: none
- (new) map_edits: `add_link` from the current node's layer+1 node (the one with the most branches) to a node in layer+3, preferring a non-Elite; the added link is one-way. The combat on the target of this link keeps its normal rewards.
- (new) starts_combat: none
- (new) next_combat_overrides: none

### 2. "Ask for the launch manifest"
- label: Ask her to reveal the next layer (scouting)
- result_text: "She reads the manifest aloud: pad crews, gantry loads, what's fueled and what's waiting. You see the board before you step on it."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: `reveal_type` on all nodes in layers +1 and +2 (permanent for this netrun; no layout change)
- (new) next_combat_overrides: the next combat starts with `enemy_enrage_start_turn −2`, because the pad crew is alerted (duration: one combat)

### 3. "Close the crawlway behind you" (cost choice)
- label: Seal the flagged crawlway (−1 Elite, pay HP)
- result_text: "The crawlway is a rat hole of live cable. Okafor shuts the hatch with you still in it. It hurts. Ahead, one Elite route just loses its door."
- cycle_cost: 0
- hp_cost: 6
- effects: GAIN_CYCLES, CAMPAIGN, amount +15 (salvage from the cable)
- reward: none
- (new) map_edits: `remove_node` on one Elite Router (the nearest one ahead; if none, `convert_node` of the nearest Router to Mainframe instead). Links through it are re-routed to its successors so no layer becomes cut off.

### 4. "Call it even"
- label: Decline the favor
- result_text: "'Suit yourself.' She pockets the slate. 'The debt stays open.'"
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits: none

## Design notes
- **Trade-offs:** Choice 1 buys tempo (a shorter path means fewer fights and less Heat from routers, but fewer rewards) for +1 Heat. Choice 2 buys information and planning at the cost of a faster enrage next fight; the player can use it to avoid Elites or hunt Mainframes. Choice 3 is the safest route, since one Elite goes away, but 6 HP is roughly a fight's worth of attrition at T2 and the player gets 15 Cycles (about one shop item at the GDD 11 economy). Choice 4 keeps the run unchanged and costs nothing.
- **No dominant option:** The best pick depends on build and HP: a strong deck takes the free shortcut, a fragile one takes the seal, a planner takes the manifest.
- **Determinism:** All edits are chosen by fixed rules (most branches, nearest Elite), with ties broken by node id; no RNG is used. The preview can show the exact link or node affected before the player confirms.
- **Interactions:** Scrubber, Cold Exit and Clean Signal Daemons don't conflict. The shortcut can skip a Mainframe in layers 3-5 (the guarantee holds only at generation time; the designer should decide whether edits may break it).
- **Text keys:** `ev_orb_pad_favor.title`, `.text`, `.c1`-`.c4` labels and results. Map-edit tooltips: "NEW LINK", "REVEALED", "SEALED".
- **Fallback without N16:** choice 1 becomes +20 Cycles / +1 Heat, choice 2 becomes a reveal-less 2-Cycle nothing, choice 3 becomes the HP-for-Cycles trade alone.

## Q:
- Q: May a PATHS edit remove the guaranteed Mainframe in layers 3-5, or should edits be validated against the generation guarantees?
- Q: Should the "favor" thread persist (a flag `okafor_debt`) so a later Orbital event can call it in, or stay a one-off?
