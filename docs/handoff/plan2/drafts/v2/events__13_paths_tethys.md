<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__13_paths_tethys; status ok; tokens in 4771 cache-write 0 cache-read 32585 out 3283; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, enemy unresolved):** Choice 3 no longer names any enemy and has no `starts_combat`. It is now a pure `TURN_NODE` edit (lowest-index Router in the next layer becomes an Elite Router, type revealed). The Elite that spawns comes from the Tethys elite pool by the normal node rules, so no Meridian id is used. The bonus reward is a node-level `combat_overrides` entry (`reward_bonus = firmware_rare`) on the converted node, paid on clear. This is an N16 field, with an N18 reward row as the alternative. Result text changed per Fix 1.
- **Issue 2 (BLOCKER, ADD_LINK constraints):** The constraint is now hard (Fix 2), not a Q. The target is the lowest-index node exactly 2 layers ahead. The link is invalid, and the choice greyed with a stated reason, if the target layer is 4 or 7, or if the skipped layer holds the only Mainframe. I also added a guard on layers 3–5: the skipped layer must not be the last layer that offers a Mainframe. The first v1 Q is answered and removed.
- **Issue 3 (MAJOR, RNG):** Choice 2 is now deterministic (Fix 3): cut the highest-index Elite Router in the next layer, otherwise `REVEAL_TYPE` on the lowest-index unrevealed node of that layer. The events-RNG note is dropped. On the D4 "Intel: no" concern: the fallback reveals one node's type, only when no Elite exists, and the choice is greyed out if the layer has neither an Elite nor an unrevealed node.
- **Issue 4 (MAJOR, balance):** Choice 3 now costs 30 Cycles and 6 HP, and Choice 2 costs 8 HP and −3 Heat (Fix 4). Choice 4 stays a free decline. That is the baseline: every other choice pays for something it changes. Choice 3 greys out if the next layer has no Router.
- **Issue 5 (MAJOR, muddled fields):** Fields not used are listed as "none". The text no longer promises effects "for the rest of this dive". It now says the edit holds, which matches a permanent map edit.
- **Issue 6 (NIT, arithmetic and N#):** The Heat comparison is corrected: +4 Heat is four Elite Router clears' worth of Heat, so a clear price. The unsupported Billing Loop comparison is removed. I added a Dependencies line (Fix 5): N16, N2, no data-only fallback.
- **Issue 7 (NIT, GDScript syntax):** `foreshadows: none`.
- **Critic Q1 (show conversion before commit):** Yes. The preview must equal the result, so the map highlights the node that will change. The surprise is dropped. The second v1 Q is closed.
- **Critic Q2 (Heat vs HP):** Kept as Heat for the shortcut, because the Tethys Heat identity fits a loud breach. A new Q is added below.
- **Kept, because strong:** the text, the three edit kinds (add, cut, convert) mapped to Heat, HP and Cycles, and deterministic edits saved in run state.

# ev_tet_hatch_fault: Hatch Fault

**Mechanic:** PATHS, corporation `tethys`, min_tier 2, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** A flooded service duct opened itself. Pin it open for a loud shortcut, force it shut to thin the next layer, or rewire it to a bigger fight for a better prize?
**Dependencies:** N16 (map_edits, combat_overrides), N2. No data-only fallback: without N16 the event can only use HP, Cycles and Heat, so drop the event.

## TerminalEventData fields
- id: `ev_tet_hatch_fault`
- title: Hatch Fault
- speaker: STREET_MERC
- text: "The bulkhead hatch is cycling by itself: open, seal, open, a hydraulic cough every four seconds. Condensation runs down the Terminal's screen. A maintenance light reads EQUALIZING, and nothing has equalized in an hour. Behind the hatch is a duct nobody drew on the map. Water pushes at the seal and the lock can't decide, so you get to."
- corporation_id: `tethys`
- min_tier: 2
- dispatch_clue: false
- foreshadows: none
- weight: 1.0

## Choices

**1. Pin the hatch open**
- label: "Pin it open (+4 Heat)"
- result_text: "The lock groans and holds. A wet, cold passage to the next layer but one, and every pressure sensor on the hull just logged the breach."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount 4
- reward: none
- map_edits (new): ADD_LINK from this node to the lowest-index node exactly 2 layers ahead. Permanent for this run.
  - Invalid (choice greyed, reason shown: "The duct would skip a Rack or the last Mainframe") if the target layer is 4 or 7, or the skipped layer holds the only remaining Mainframe, or it is the last layer in 3–5 that offers one.
- starts_combat / combat_overrides / next_combat_overrides (new): none

**2. Force it sealed**
- label: "Force it shut (-8 HP, -3 Heat)"
- result_text: "You lean on the wheel until the seal bites. Your shoulder pays for it. The duct stays drowned, and the hull logs read as a clean seal."
- cycle_cost: 0
- hp_cost: 8
- effects: MODIFY_HEAT, target CAMPAIGN, amount -3
- reward: none
- map_edits (new): CUT_OPTION: remove the highest-index Elite Router in the next layer. If none, REVEAL_TYPE on the lowest-index unrevealed node in that layer. Greyed out if the layer has neither.
- starts_combat / combat_overrides / next_combat_overrides (new): none

**3. Rewire the lock**
- label: "Rewire it (30 Cycles, -6 HP)"
- result_text: "You bridge the pressure sensor to the wrong relay. The hatch swings onto a duct that wasn't on any chart. A fat shape already sits on the next relay."
- cycle_cost: 30
- hp_cost: 6
- effects: none
- reward: Rare Firmware ("Pressure Seal": a slice gets permanent ENCRYPTED and +1 output), paid on clearing the converted node.
- map_edits (new): TURN_NODE: the lowest-index Router in the next layer becomes an Elite Router, type revealed. Greyed out if the next layer has no Router.
- combat_overrides (new): on the converted node only, `reward_bonus = firmware_rare`. Lasts until that node is cleared. The enemy is drawn from the Tethys elite pool by the normal node rules.
- starts_combat / next_combat_overrides (new): none

**4. Walk on**
- label: "Leave the hatch cycling"
- result_text: "You step over the coaming and let the lock argue with itself. Behind you the hatch coughs open again."
- cycle_cost: 0, hp_cost: 0, effects: none, map_edits (new): none

## Event wheel
Not used.

## Design notes
- **Three edits, three asks.** Choice 1 adds a link (skips a layer's fights, shops and Terminals) for Heat. Choice 2 cuts an option (a safer map) for HP and some Heat relief. Choice 3 turns a node (a deliberate Elite fight) for Cycles and HP, paid back by a Rare Firmware. Choice 4 is free and changes nothing.
- **No dominant option.** Choice 3 is the only one that pays out loot, but it costs about 30 Cycles (one Mainframe purchase), 10% of a 60 HP operative (6/60), and an Elite fight at the current HP. A weak run should take Choice 2 or 4. Choice 1 is for a strong, Heat-tolerant run that wants speed. Choice 2 is 13% of 60 HP (8/60).
- **Economy (GDD 11 placeholders):** an Elite Router clear gives +1 Heat, so +4 is four Elite clears' worth. -3 Heat is a modest sink. The converted Elite also adds +1 Heat when cleared.
- **Determinism:** every edit applies at event resolution and is saved in run state. There is no RNG. The map preview highlights the link, the cut Elite, the revealed node, or the converted node before commit, so the preview equals the result.
- **Interactions:** the Rack layers 4 and 7 and the Mainframe guarantee are protected by the Choice 1 constraint. Under the full-graph display (D7) the new edge draws highlighted. Choices 2 and 3 can't be combined on the same layer, because the event fires once.
- **Text keys:** `evt.tet_hatch_fault.title`, `.text`, `.c1`–`.c4` (labels and results), `map.edit.new_link`, `map.edit.node_converted`, `map.edit.invalid_skips_rack`.

## Q:
- Q: Is +4 Heat the right price for skipping a layer, or should Choice 1 also cost a few HP so it isn't free for a healthy run?
- Q: Should the converted Elite's bonus Firmware be a fixed item ("Pressure Seal") or a Rare roll from the Tethys pool?
