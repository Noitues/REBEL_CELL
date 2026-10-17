<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__18_ambush_rebel_cell; status ok; tokens in 6423 cache-write 0 cache-read 32007 out 2137; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_rc_holding_cell_tip: The Prisoner in the Trunk

**Mechanic:** AMBUSH, corporation rebel_cell, min_tier 2, weight 0.8, dispatch_clue false, foreshadows empty
**One-line decision:** Pay HP and Heat risk to fight a mirror-grade handler for a prisoner who may be a Cell veteran, or a bait. Or sell the tip and walk.

## TerminalEventData fields
- id: `ev_rc_holding_cell_tip`
- title: The Prisoner in the Trunk
- speaker: STREET_MERC
- text: "A burner message names a parked sedan on Level 9. Inside the trunk, a man in a Cell jacket is zip-tied, breathing slow, alive. Two feeds say he's ours. A third says he's the bait. The car has a handler proxy on the dash, humming a tune you almost remember. Whoever grabbed him wants someone to come looking."
- corporation_id: `rebel_cell`
- min_tier: 2
- dispatch_clue: false
- foreshadows: empty
- weight: 0.8

## Choices

### 1. "Cut him loose. Fight the minder." (the ambush)
- label: Cut him loose (fight, rescue stake)
- result_text (win): "The proxy folds mid-sentence. The prisoner coughs, gives you a name, and a cache location. His cuffs were real. So was the debt he owed."
- result_text (loss): "The minder drags you under the sedan's shadow. By the time you come to, the trunk is empty and the tip was always a lure."
- cycle_cost: 0
- hp_cost: 0
- effects: none outside the combat
- reward (on win): a rescued operative (ClassData, a rookie of an unlocked class, rank 0) **or** if the roster is full, a Daemon from the common pool
- (new) starts_combat: enemy `handler_proxy`
- (new) combat_overrides:
  - tier_delta: +1 (enemy reads one tier higher, capped at T4)
  - start_hp_pct: 100
  - player_start_ram: -2 (the ambush catches you cold), this combat only
  - heat_on_start: +2
- stake: on loss, the operative takes 12 HP damage (carried over, floor 1 HP) and +4 Heat. No operative death from this event.
- reward on win: rookie operative as above, plus 20 Cycles from the prisoner's cache.

### 2. "Check the car first." (cautious option, costs resources)
- label: Scan the sedan (-15 Cycles)
- result_text: "Your scanner finds a tether on the cuffs, feeding a live signal somewhere. You cut the tether, free the prisoner quietly, and he's gone before the signal drops. He leaves a spare chip."
- cycle_cost: 15
- hp_cost: 0
- effects: MODIFY_HEAT target CAMPAIGN amount +1
- reward: Firmware (common pool, one random drawn from the `events` RNG stream at a checkpoint)
- (new) starts_combat: none
- Note: no rescue and no operative, just a smaller, safe payout.

### 3. "Sell the tip to a rival." 
- label: Sell the location (+35 Cycles, +3 Heat)
- result_text: "A broker pays on the spot. Whatever happens to the man in the trunk, it isn't on your feed."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES target CAMPAIGN amount 35; MODIFY_HEAT target CAMPAIGN amount +3
- (new) next_combat_overrides: the next Router fight gains a `cell_informant` as a second-wave add-in? No: simpler, data-only: next combat, enemy damage factor +10% for 1 combat (the prisoner's friends hunt you). Duration: 1 combat.

## Design notes
- **No dominant option.** Choice 1 is the only way to get a body, but it carries a +1 tier fight at -2 RAM. At T2 a normal at T3 strength (about 44-56 HP per the R2 band) is a 3-4 turn fight, so the HP risk is modest but real (average loss 10-15 HP). Choice 2 trades 15 Cycles for a guaranteed, small Firmware with no risk. Choice 3 is the greedy and morally gray path: 35 Cycles is roughly one shop item but adds 3 Heat plus a 10% damage rider next fight.
- **Why `handler_proxy`.** It fits the REBEL_CELL "it mirrors you" theme without needing an elite. It is a normal, so the fight stays inside the R1 3-4 turn target. The +1 tier is the whole tweak; it is data-only.
- **Rescue economy.** A rookie is worth 15 Schematics at HQ, so the win is roughly +15 Schematics plus 20 Cycles. Loss costs 12 HP and 4 Heat, about the worth of one MAJOR-threshold step in reverse. Win rate at T3-scaled normal should be about 85-90%, so expected value is positive, but not by a huge margin.
- **Roster full fallback** prevents a dead reward.
- **Determinism.** The Firmware draw in choice 2 uses the `events` RNG stream and sets a checkpoint, so the result cannot be rerolled by reloading. The combat itself is standard.
- **Dependencies.** N16 (`starts_combat`, `combat_overrides`, `next_combat_overrides`) is required. Data-only fallback: replace choice 1 with a plain event that costs 12 HP and yields the operative at 50% chance via the `events` stream. The `player_start_ram` and `heat_on_start` fields are NEW sub-fields of `combat_overrides`; if unsupported, cut them and keep only `tier_delta`.
- **Text keys needed:** `ev_rc_holding_cell_tip.title`, `.text`, three choice labels, five result strings (win/loss/scan/sell).

## Q:
- Q: Should a loss on the ambush ever risk operative death, or stay capped at HP damage as drafted?
- Q: Should the sold tip in choice 3 later surface as a raid-win or HQ event (the prisoner returning)?
