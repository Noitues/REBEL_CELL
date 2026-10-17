<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__12_paths_aurelian; status ok; tokens in 4931 cache-write 0 cache-read 32585 out 2903; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, borrowed Orbital enemy)**
  - Kept `geostationary_guard` as the only valid id, since Aurelian has no enemies yet. It is now explicitly "corporation-agnostic pool pick, swap is a data-only edit of one id".
  - Dropped the Q about a borrowed enemy.
- **Issue 2 (BLOCKER, no-op enrage and missing phase math)**
  - Removed the enrage override.
  - Added a real override: the Lanista's crowd opens a 5% max-HP SHIELD on the enemy at the start of phase 2 (a Triage-style hook is not needed; it uses `GAIN_SHIELD` in PERCENT mode, N1).
  - Added the R2 budget arithmetic.
- **Issue 3 (MAJOR, stake and hidden penalty)**
  - The label now states the cut.
  - The cut is mild: it removes a Router only if two or more Routers remain.
  - Added a reward of 25 Cycles on win.
- **Issue 4 (MAJOR, Choice 3 dominates)**
  - Heat is now +4, and the lane closure targets a stated node class (Terminal or Mainframe) shown in the label.
  - The net gain is cut to +30 Cycles.
- **Issue 5 (MAJOR, Rack reachability)**
  - The validator rule is now in the draft: it refuses any edit that leaves the final Rack unreachable, and a refused edit falls back to Cycles/Heat only.
  - Q1 is removed because it is answered.
- **Issue 6 (NIT)**
  - Choice 4 now has full fields, and the text keys are complete.
- **Issue 7:** kept, nothing to change.
- **Critic Qs**
  - The preview lists exact node ids, because previews must equal results.
  - The 6 HP cost is dropped, because the elite already costs HP.

# ev_aur_verdict_broadcast: Live Verdict Feed
**Mechanic:** PATHS, corporation aurelian, min_tier 2, weight 1.0, dispatch_clue false, foreshadows none
**One-line decision:** Pay Cycles for a clear read of the route ahead, fight an elite on the feed for a shortcut that costs you a lane, or sell the airtime for cash and a closed lane.

## TerminalEventData fields
- id: `ev_aur_verdict_broadcast`
- title: Live Verdict Feed
- speaker: STREET_MERC
- text: "The Terminal is locked onto an Aurelian arena broadcast: BREAD. CIRCUS. TERMS APPLY. A caption crawl lists today's VERDICTS, and each one is a route in this netrun. The Lanista's announcer reads the odds like a weather report. Patrons are betting on which lanes the clients survive, and the house pays out on whatever you make interesting. Your cut-in window is about ten seconds."
- corporation_id: `aurelian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 1.0

## Choices

**1. Read the odds**
- label: "Back the favorite (-20 Cycles; reveals the next layer, opens a link)"
- result_text: "The crawl names the favorite lane and the sealed lane behind it. You bet against the house's own tell. Doors you couldn't see are suddenly marked."
- cycle_cost: 20
- hp_cost: 0
- effects: none
- reward: none
- (new) map_edits:
  - `reveal_type`: every node on the next layer.
  - `open_link`: the first locked cross-link by node id order. If none exists, the reveal alone applies.
- (new) starts_combat: none
- (new) next_combat_overrides: none

**2. Enter the arena feed**
- label: "Step into the sand (elite fight; win: +25 Cycles and a shortcut, but the house takes a Router)"
- result_text: "You hijack the feed and the crowd roars. An enforcer is dropped in to give the patrons a show. Win, and the Lanista honors the terms: a shortcut opens, minus the house's cut."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: 25 Cycles on win (`GAIN_CYCLES`, CAMPAIGN, 25)
- (new) starts_combat: enemy `geostationary_guard` (pool pick, corporation-agnostic; swap to an Aurelian elite is a one-id data edit). Stake: on loss, normal death rules; edits and reward only on win.
- (new) combat_overrides (this fight only): at the start of phase 2, the enemy gains SHIELD = 5% max HP (`GAIN_SHIELD`, PERCENT, N1). The crowd props up the favorite, so the burst window must beat a shield.
- (new) map_edits (on win only):
  - `add_link`: from the current node to the lowest-id node two layers ahead.
  - `cut_layer_option`: remove the highest-id Router on the next layer, only if two or more Routers remain there.
- **Phase budget** (R2, T2 elite, 2 phases, 3.5 turns each at 11 dpt): about 77 HP total, within the 68-88 band. Threshold 0.5 gives phase 1 about 38 HP, 11 × 3.5 ≈ 38. The phase 2 shield adds about 4 HP (5% × 77), so the fight stays at 6-8 turns.

**3. Sell the airtime**
- label: "Sell the slot (+30 Cycles, +4 Heat; the next Terminal or Mainframe closes)"
- result_text: "A Patron's agent buys your ten seconds for a sponsor spot. They ask you to stay out of the lane the feed is framing. You take the money."
- cycle_cost: 0
- hp_cost: 0
- effects: `GAIN_CYCLES`, CAMPAIGN, 30; `MODIFY_HEAT`, CAMPAIGN, 4
- reward: none
- (new) map_edits: `cut_layer_option` on the next layer's highest-id Terminal or Mainframe (if none exists, the choice is relabeled in the preview as having no closure), then `close_link` on the first outgoing link of the current node by id order, leaving at least one path.

**4. Mute it**
- label: "Mute the feed and move on"
- result_text: "The crawl keeps scrolling without you. Somewhere a patron groans."
- cycle_cost: 0, hp_cost: 0, effects: none, reward: none, map_edits: none

## Event wheel
Not used.

## Design notes
- **Tension**
  - Choice 1 is a flat 20 Cycles for information and a quiet link. It is safe but gives no income.
  - Choice 2 carries real risk (an elite) and pays 25 Cycles plus a shortcut, at the price of one Router lane, so it fits builds that burst well.
  - Choice 3 pays 30 Cycles, but +4 Heat and a lost shop or event lane make it wrong when your next layer holds the node you want.
  - Choice 4 keeps the run untouched.
- **Determinism and validation**
  - Every target is chosen by node id order, with no RNG.
  - The preview lists the exact node ids and links changed, and Choice 2's edits fire only after the combat result.
  - The N16 validator refuses any `close_link` or `cut_layer_option` that would leave the final Rack unreachable. If refused, the choice falls back to its Cycles/Heat effects only, and the preview says so.
- **Dependencies:** N16 (`map_edits`, `starts_combat`, `combat_overrides`), N1 (PERCENT shield), and N3 for phase 2. Data-only fallback: Choice 3 keeps its Cycles and Heat, and Choice 1 becomes a Cycles-for-nothing trade, so N16 stays a prerequisite.
- **Text keys:** `ev_aur_verdict_broadcast.title`, `.text`, `.c1`-`.c4` labels and results, `map_edit.reveal_next_layer`, `map_edit.house_cut`, `map_edit.refused`.

## Q:
- Q: Should the preview show a "REFUSED, Cycles/Heat only" line before commit when the validator would block an edit, or only after?
- Q: Should the phase 2 shield in Choice 2 scale with tier through PERCENT, or stay a flat 5% at every tier?
