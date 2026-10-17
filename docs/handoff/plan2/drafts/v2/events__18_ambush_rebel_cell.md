<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__18_ambush_rebel_cell; status ok; tokens in 5035 cache-write 0 cache-read 32585 out 2858; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, invented fields):** Cut `player_start_ram` and `heat_on_start`. Choice 1 now uses only N16 fields: `starts_combat` (enemy, `combat_overrides` with `tier_delta` only, `stake`, `reward`). The loss Heat (+4) is now the only Heat on that path.
- **Issue 2 (BLOCKER, tier arithmetic):** Rewrote the notes. A T2 run fights a T3 normal (44-56 HP, 3-4 turns); a T3 run fights T4 (56-70 HP). Removed the "85-90 % win" and "10-15 HP" claims; replaced them with "estimated 8-14 HP lost, win rate set by the sim."
- **Issue 3 (MAJOR, choice 3):** Deleted the unfinished `cell_informant` text. The rider is replaced with existing systems: `MODIFY_HEAT +3` and a `SHOP_STOCK` rule modifier (-1 stock at the next shop only). That removes the unruled damage rider, which would have broken R2.
- **Issue 4 (MAJOR, choice 2):** Raised the cost to 20 Cycles. The reward is a common-pool Firmware, with the pool named and the draw on the `events` stream at a checkpoint.
- **Issue 5 (MAJOR, perverse fallback):** The roster-full fallback is now a *common* Daemon, but with the 20 Cycles dropped, so it is no longer worth more than a rookie. The loss stake is kept: 12 HP (floor 1) and +4 Heat, with no operative death (this follows the critic's "keep").
- **Issue 6 (MAJOR, fallback line):** Replaced it with "if N16 is not built, hide the event (weight 0)."
- **Issue 7 (NIT):** Result texts are now 3 sentences. Added a `heat_effects` note (none authored). Text keys are listed completely and exactly. The duplicate "reward" line is merged.
- **Issue 8 (NIT):** The one-liner now says "handler proxy", not "mirror-grade handler".
- **Triage rows:** Both are covered by issues 1 and 2.
- **Kept, because the critic marked it strong:** the three-way choice (fight / pay / sell), the capped loss, and `handler_proxy` as a normal that keeps R1's 3-4 turns.

# ev_rc_holding_cell_tip: The Prisoner in the Trunk

**Mechanic:** AMBUSH, corporation rebel_cell, min_tier 2, weight 0.8, dispatch_clue false, foreshadows empty
**One-line decision:** Risk HP and Heat to fight a handler proxy at one tier higher for a prisoner who may be a Cell veteran or bait; pay to free him quietly for less; or sell the tip and walk.

## TerminalEventData fields
- id: `ev_rc_holding_cell_tip`
- title: The Prisoner in the Trunk
- speaker: STREET_MERC
- text: "A burner message names a parked sedan on Level 9. Inside the trunk, a man in a Cell jacket is zip-tied, breathing slow, alive. Two feeds say he's ours. A third says he's the bait. A handler proxy sits on the dash, humming a tune you almost remember. Whoever grabbed him wants someone to come looking."
- corporation_id: `rebel_cell`
- min_tier: 2
- dispatch_clue: false
- foreshadows: empty
- weight: 0.8
- heat_effects: none authored

## Choices

### 1. Cut him loose and fight the minder
- label: Cut him loose (fight)
- result_text (win): "The proxy folds mid-sentence. The prisoner coughs up a name and a cache location. His cuffs were real, and so was the debt he owed."
- result_text (loss): "The minder drags you under the sedan's shadow. When you come to, the trunk is empty. The tip was always a lure."
- cycle_cost: 0
- hp_cost: 0
- effects: none outside the combat
- (new) starts_combat (N16):
  - enemy: `handler_proxy`
  - combat_overrides: `tier_delta` +1 (capped at T4). It sets both the enemy's `hp_by_tier` entry and its damage factor.
  - stake, on loss: 12 HP damage carried over (floor 1 HP) and MODIFY_HEAT +4. No operative death.
  - reward, on win: a rescued rookie operative (an unlocked class, rank 0) plus GAIN_CYCLES 20. If the roster is full, a common-pool Daemon replaces the operative and the 20 Cycles are dropped.
- Fallback if `tier_delta` is unsupported: fight plain `handler_proxy` at the run's tier.

### 2. Scan the sedan first
- label: Scan the sedan (-20 Cycles)
- result_text: "Your scanner finds a tether on the cuffs, feeding a live signal somewhere. You cut it and free the prisoner quietly. He's gone before the signal drops, leaving a spare chip in your palm."
- cycle_cost: 20
- hp_cost: 0
- effects: MODIFY_HEAT target CAMPAIGN amount +1
- reward: Firmware, common pool, one draw from the `events` RNG stream at a checkpoint
- (new) starts_combat: none
- No operative and no fight: a safe, smaller payout.

### 3. Sell the tip to a rival
- label: Sell the location (+35 Cycles, +3 Heat)
- result_text: "A broker pays on the spot and asks no questions. Whatever happens to the man in the trunk, it isn't on your feed. The shops on this level start hearing your name."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES target CAMPAIGN amount 35; MODIFY_HEAT target CAMPAIGN amount +3
- (new) next_combat_overrides: none. Instead, a one-node rule modifier: `SHOP_STOCK` -1 for the next Mainframe in this run only (an existing modifier type).

## Design notes
- **No dominant option.** Choice 1 is the only path to a body, and it carries a tier-up fight. Choice 2 pays 20 Cycles and +1 Heat for a safe, modest Firmware. Choice 3 nets 35 Cycles (about one shop item) but adds 3 Heat and thins the next shop.
- **Tier arithmetic.** `tier_delta` +1 means a T2 run fights a T3 normal (R2 band 44-56 HP, 3-4 turns), and a T3 run fights a T4 normal (56-70 HP). Estimated loss is 8-14 HP per fight. The win rate is to be set by the sim. If it is below 90 %, drop `tier_delta` to 0 rather than add new override fields.
- **Why `handler_proxy`.** It is a normal with a mirror theme and keeps the fight inside R1's 3-4 turns, so the ambush is a speed bump, not a detour.
- **Rescue economy.** A rookie recruits for 15 Schematics at HQ. The win is therefore about 15 Schematics plus 20 Cycles. A loss costs 12 HP and 4 Heat, with no operative death.
- **Determinism.** The Firmware draw in choice 2 uses the `events` stream at a checkpoint, so a reload cannot reroll it. The combat is standard and its preview equals its result.
- **Dependencies.** Choice 1 needs N16 (`starts_combat`, `combat_overrides.tier_delta`, `stake`, `reward`) and N2 (`hp_by_tier`). Choices 2 and 3 are data-only. If N16 is not built, hide the event (weight 0).
- **Text keys:** `ev_rc_holding_cell_tip.title`, `.text`, `.c1.label`, `.c1.win`, `.c1.loss`, `.c2.label`, `.c2.result`, `.c3.label`, `.c3.result`.

## Q:
- Q: Should a loss on the ambush ever risk operative death, or stay capped at HP damage and Heat as drafted?
- Q: Should `tier_delta` shift both HP band and damage factor (as drafted), or HP only?
