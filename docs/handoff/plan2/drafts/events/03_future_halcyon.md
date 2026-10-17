<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__03_future_halcyon; status ok; tokens in 6468 cache-write 0 cache-read 32007 out 2010; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_hal_stuck_crosswalk: Stuck Crosswalk

**Mechanic:** FUTURE, corporation halcyon, min_tier 1, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** A malfunctioning crosswalk controller can be turned into a weapon for the next fight, but each way of using it costs something or leaves a mark on the Cell.

## TerminalEventData fields
- id: `ev_hal_stuck_crosswalk`
- title: Stuck Crosswalk
- speaker: STREET_MERC (1)
- text: "A crosswalk signal on the Terminal feed is stuck on WALK, cycling the same four-second chime forever. Halcyon traffic AI keeps filing a repair ticket and closing it as 'resolved.' Every patrol route that crosses this junction is now timed to a light that no longer works. Somebody who knows the grid could hand that confusion to the next unit you meet."
- corporation_id: `halcyon`
- min_tier: 1
- dispatch_clue: false
- foreshadows: `&""`
- weight: 1.0

## Choices

### 1. Feed the loop to the patrols
- label: "Push the stuck cycle into patrol timing (-8 HP)"
- result_text: "The chime follows you into the next fight. A Halcyon unit stops mid-stride, waiting for a light that never changes. You took a static jolt from the junction box doing it."
- cycle_cost: 0
- hp_cost: 8
- effects: none
- reward: none
- next_combat_overrides (new): for the NEXT 1 combat: enemy starts Frozen (skips its first start-of-turn respin); enemy resistance -1 (min 0). Duration: next 1 combat.
- starts_combat (new): none
- map_edits (new): none

### 2. Sell the fault as a bug report
- label: "File it as a service ticket (+30 Cycles, +2 Heat)"
- result_text: "Halcyon pays a bounty for reported faults. They also log who reported it, and the ticket sits on your name."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 30; MODIFY_HEAT, target CAMPAIGN, amount 2
- reward: none
- next_combat_overrides (new): none
- starts_combat (new): none

### 3. Spread the fault wider (risky)
- label: "Broadcast the glitch across the district (-15 Cycles)"
- result_text: "The fault ripples out. For the next few fights Halcyon units hesitate at every crossing. But hesitating units also lash out when the light finally flips, and they hit harder."
- cycle_cost: 15
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new): for the NEXT 3 combats: player gets one extra free nudge on turn 1 of each; enemy damage +20% in each. Duration: next 3 combats.
- starts_combat (new): none

### 4. Leave it
- label: "Cross on the chime"
- result_text: "You walk through. The light holds. You don't."
- No costs, effects or overrides.

## Event wheel
Not used.

## Design notes
- **Decision shape:** The three paid options trade different currencies for different timeframes. Choice 1 is a short, sharp edge for one fight, paid in HP. Choice 2 is a plain economy-and-Heat trade. Choice 3 is the long game: three fights of tempo, with a threat tax on all of them.
- **Why none dominates:** Choice 1 is strong on a hard upcoming node, but HP is scarce. Choice 3 helps a run that expects several fights soon, but +20% damage is a real cost when the run is already low on HP. Neither is the obvious pick once HP is low. Choice 2 is the safe fallback, and Heat is a campaign-wide cost.
- **Numbers (placeholders vs GDD 4.2/4.3):**
  - 8 HP is about 13% of a 60 HP Breaker.
  - 30 Cycles is a mid-sized event payout, similar to the Billing Loop's.
  - +2 Heat is below a MINOR threshold step.
  - A free nudge is worth about 1 RAM per combat; +20% damage over three fights is roughly 6 to 10 extra HP lost, so it is a genuine cost against the nudge gain.
- **Interactions:** Frozen stacks with the Ghost class's resistance-stripping Perfect hook. Choice 1's -1 resistance pairs with Meridian-style Weight if the player's run crosses corporations, though this event is Halcyon-only. Choice 3's extra nudge helps Rigger's free-nudge hook. The overrides should be displayed in the next combat's HUD as chips so the player sees them before committing.
- **Dependencies:** `next_combat_overrides` is N16 (needs N2 for the enemy damage factor, though a flat +20% is tier-independent per R2). There is no data-only fallback for the overrides; as a fallback, drop choices 1 and 3 and ship choice 2 and 4 only. Enemy "starts Frozen" reuses the existing Freeze rule (GDD 2.5). Determinism: all overrides are fixed values with no RNG, and they persist in the run state across saves.
- **Text keys:** `ev_hal_stuck_crosswalk.title`, `.text`, `.c1` to `.c4` labels and results; a HUD chip tooltip key for "FUTURE: crosswalk fault" listing the active overrides.

## Q:
- Q: Should "next 3 combats" count only fights, or also elite and Rack fights? I assume all combats on this run count, including the final Rack.
- Q: Does the Frozen start apply to a boss-class enemy, or should bosses and mini-bosses be exempt from override choice 1?
