<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__03_future_halcyon; status ok; tokens in 4831 cache-write 0 cache-read 32585 out 2940; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (choice 3 not a clean trade; extra-nudge scope unclear; unsupported HP claim):** Replaced choice 3 with the critic's override: next 2 combats, enemy HP -20% (percent of its own max) and enemy damage +25%. The extra nudge is dropped, so the "turn 1 or per turn" ambiguity no longer exists. The label now names the threat tax. The HP estimate is recomputed from the intake targets (see Numbers).
- **Issue 2 (a flat window dominated by choice 2):** Choice 1 now pairs Frozen with enemy HP -15%, so it shortens the fight rather than skipping a respin that barely matters. Choice 3 is a shorter fight bought with intake. Choice 2 stays the safe economy option; its Cycles and Heat are rebalanced against the others (see Design notes).
- **Issue 3 (resistance -1 and Frozen asserted without fit):** The resistance line is dropped. HP percent is a checkable benefit that reads the enemy's own max HP.
- **Issue 4 (N16 vs N2 contradiction):** Dependency line now matches the N-table: N16 only, no N2 dependence. Percent amounts read the enemy's own max HP (R2), and the +25% damage is a tier-independent buff.
- **Issue 5 (Heat wording):** Now "+2 Heat, one fifth of a MINOR step".
- **Issue 6 (Voice and foreshadows):** Kept, because the critic confirmed both are correct.
- **Issue 7 ("Billing Loop" reference):** Deleted.
- **Issue 8 (data-only fallback):** Added. If N16 slips, choice 1 becomes an immediate trade (-8 HP for +20 Cycles) and choice 3 is dropped.
- **Critic Q1 (bosses and mini-bosses exempt from HP %):** Adopted, because HP percent would break the R2 phase budgets. The HP part of the overrides skips mini-bosses and bosses; the damage part and Frozen still apply.
- **Critic Q2 (raid interlude counts toward "next N"):** Adopted as no, a raid interlude does not count.
- **Critic "Keep" items:** Four distinct currencies, HUD chips, and no RNG with run-state persistence are all kept.

---

# ev_hal_stuck_crosswalk: Stuck Crosswalk

**Mechanic:** FUTURE, corporation halcyon, min_tier 1, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** A broken crosswalk controller can weaken the next fight or two, but it costs HP, or it makes the enemies you meet hit harder.

## TerminalEventData fields
- id: `ev_hal_stuck_crosswalk`
- title: Stuck Crosswalk
- speaker: STREET_MERC (1)
- text: "A crosswalk signal on the Terminal feed is stuck on WALK, cycling the same four-second chime forever. Halcyon's traffic AI keeps filing a repair ticket and closing it as 'resolved.' Every patrol route through this junction is timed to a light that no longer works. Somebody who knows the grid could hand that confusion to the next unit you meet."
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
- next_combat_overrides (new): next 1 combat: enemy starts Frozen (skips its first start-of-turn respin, GDD 2.5); enemy HP -15% of its own max (percent mode, not rescaled by tier). Exempt from the HP part: mini-bosses and bosses (Frozen still applies).
- starts_combat (new): none
- map_edits (new): none

### 2. Sell the fault as a bug report
- label: "File it as a service ticket (+25 Cycles, +2 Heat)"
- result_text: "Halcyon pays a bounty for reported faults. They also log who reported it, and the ticket sits on your name."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 25; MODIFY_HEAT, target CAMPAIGN, amount 2
- reward: none
- next_combat_overrides (new): none
- starts_combat (new): none
- map_edits (new): none

### 3. Spread the fault wider
- label: "Broadcast the glitch across the district (-15 Cycles; weaker enemies that hit harder)"
- result_text: "The fault ripples out. For the next two fights Halcyon units stumble at every crossing, and they lash out when the light finally flips."
- cycle_cost: 15
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new): next 2 combats (elite and Rack fights count; a raid interlude does not): enemy HP -20% of its own max (percent mode; mini-bosses and bosses exempt); enemy damage +25% (a tier-independent buff, additive with enrage steps).
- starts_combat (new): none
- map_edits (new): none

### 4. Leave it
- label: "Cross on the chime"
- result_text: "You walk through. The light holds. You don't."
- No costs, effects or overrides.

## Event wheel
Not used.

## Design notes
- **Decision shape:** The options use different currencies. Choice 1 pays HP for a sharp one-fight edge. Choice 2 pays Heat for Cycles. Choice 3 pays Cycles and extra intake for a shorter fight, twice. Choice 4 pays nothing and gains nothing.
- **Why none dominates:**
  - Choice 1 is the best answer to a known hard next node, but HP is scarce.
  - Choice 3 is a tempo play, and its +25% is a real cost for a run already low on HP. It also tilts toward higher tiers, where intake is larger.
  - Choice 2 is the safe fallback, but Heat is campaign-wide and +2 Heat is one fifth of a MINOR step.
- **Numbers (placeholders vs GDD 4.2 and 4.3):**
  - 8 HP is about 13% of a 60 HP Breaker.
  - HP -15% on a 28-36 HP T1 normal is about 4-5 HP, roughly one fewer hit landing. It is also about half a turn of reference damage.
  - Choice 3: -20% on a 28-36 HP normal is about 6-7 HP, and +25% on a normal intake of 2-6 per turn over 3-4 turns, for 2 fights, is about 3-6 extra HP lost at T1-T2. A shorter fight offsets part of that, because less time means less intake. It is a trade rather than a gift.
  - 25 Cycles is a mid-sized payout.
- **Interactions:** Frozen stacks with the Ghost's resistance-stripping hook. The enemy damage buff adds to enrage steps (R4) and is not affected by `enemy_damage_by_tier`. Overrides show as chips in the next combat's HUD, so the player sees them before committing the route.
- **Dependencies:** N16 (`next_combat_overrides`); no dependence on N2. The HP percent reads the enemy's own max HP (R2). Frozen reuses the existing Freeze rule. Determinism: all values are fixed with no RNG, stored in the run state and saved with it.
- **Fallback if N16 slips:** choice 1 becomes an immediate trade (-8 HP for +20 Cycles); choice 3 is dropped. Choices 2 and 4 stay unchanged.
- **Text keys:** `ev_hal_stuck_crosswalk.title`, `.text`, `.c1` to `.c4` labels and results; a HUD chip tooltip key "FUTURE: crosswalk fault" listing the active overrides and remaining combats.

## Q:
- Q: Should an exempt boss or mini-boss show the HP part of the chip as "not applied", or hide it?
- Q: Does a combat abandoned by quitting and resuming still count down the override, or only on a finished combat? I suggest only on a finished combat.
