<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__04_future_orbital; status ok; tokens in 6465 cache-write 0 cache-read 32007 out 2160; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_orb_cold_witness: The Witness on the Rim

**Mechanic:** FUTURE, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** A deorbit-survivor will testify against the Commons, and the testimony can be spent on one of two future fights. Or you can spend her to buy a clean break. Do you pay in Heat, HP, or a blind spot?

## TerminalEventData fields
- id: `ev_orb_cold_witness`
- title: The Witness on the Rim
- speaker: STREET_MERC (1)
- text: "A maintenance tech sits in a pressure-suit liner behind the Terminal, still shaking. She was on the platform when Orbital Commons deorbited a crew's worth of 'underperforming assets' and logged it as debris. She saw the burn schedule and the countdown. She says she'll swear to it, but only if someone makes the sky stop listening. A launch-pad relay is already pinging her badge."
- corporation_id: `orbital`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. "Take her burn schedule" (the countdown is the weapon)
- label: Take the burn schedule (+0 Cycles, +2 Heat)
- result_text: "She reads off timings from memory. Every handoff, every gap. You write them on your wrist. The relay stops pinging, but only because it logged you."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / +2
- reward: none
- (new) next_combat_overrides: scope = next 2 combats. Enemy starts the fight **Frozen** (skips its first start-of-turn respin). A `phase_reveal` flag shows the enemy's next layout one phase ahead. Both apply only to the enemy's first phase.
- (new) starts_combat: none
- (new) map_edits: none

### 2. "Cover her exit with your own signal" (spend yourself)
- label: Mask her signal (−8 HP)
- result_text: "You route the relay's attention through your own implant. It burns. She slips away down the service ladder, and leaves a sealed packet taped under the Terminal."
- cycle_cost: 0, hp_cost: 8
- effects: none
- reward: Firmware, uncommon (working description: a Calibrated-style chip that raises one slice's sub-tick quality)
- (new) next_combat_overrides: scope = next 1 combat. The free nudge refreshes once more (+1 free nudge on turn 1), and the first enemy satellite docked in that fight is removed on spawn.
- (new) starts_combat: none
- (new) map_edits: none

### 3. "Sell her to the relay" (the clean break)
- label: Hand her to the relay (+45 Cycles, +4 Heat)
- result_text: "The badge ping goes quiet. A payment clears from a line item called 'witness remediation.' You don't look at the ladder."
- cycle_cost: 0, hp_cost: 0
- effects: GAIN_CYCLES / CAMPAIGN / +45; MODIFY_HEAT / CAMPAIGN / +4
- reward: none
- (new) next_combat_overrides: scope = next 2 combats. Enemies deal +15% damage, since the Commons now has your signature on file. Duration ends after the second combat or when the netrun ends.
- (new) starts_combat: none
- (new) map_edits: none

### 4. "Walk past" 
- label: Walk past
- result_text: "She doesn't call after you. The relay's ping resumes a few seconds later."
- No costs, no effects, no overrides.

## Design notes
**Why it's interesting.** No option dominates. Choice 1 is a two-fight tempo edge for a small Heat cost, and Heat feeds raid timing. Choice 2 costs HP (about 13% of a 60 HP Breaker) for one stronger fight and a Firmware; you won't know how the HP debt plays out until later. Choice 3 is the greedy line: +45 Cycles is roughly one Mainframe purchase, but two fights at +15% damage can cost more than 8 HP at T2–T3. The cost is deferred rather than shown in the HP bar, so players have to weigh it blind.

**Economy check (placeholders).** Typical Terminal reward is +25–30 Cycles. Choice 3's +45 is deliberately above that. The Heat cost (+4) is above a standard Router's 0 and near an Elite's +1 per node, so it matters but doesn't force a raid by itself.

**Interactions.**
- Choice 1's "Frozen start" stacks with spin-resistance enemies (Weight) without undoing it, because Freeze only skips the respin.
- Choice 1's phase reveal is a direct counter to a boss's Chart Hidden buff. Reveal applies only to non-boss fights in the first draft; bosses ignore it.
- Choice 3's damage rise is tier-independent per R2 (a buff, not a scaled amount) and is applied once, not stacked, if the player triggers similar events.
- Choice 2's satellite removal is a no-op when the next fight has no satellite. The override then carries to the next fight that does. The free nudge does not carry.

**Determinism.** Overrides are plain run-state data (`next_combat_overrides`), consumed deterministically at combat creation. No RNG. Previews read them before the fight starts, so the preview equals the result.

**Data-only fallback.** Without N16, Choice 1 can be a one-fight Firmware swap, Choice 2 a plain Firmware reward, and Choice 3 the Cycles plus Heat alone (the damage rise has no fallback).

**Text keys.** `evt.orb_cold_witness.title/body`, three `choice.*.label/result` pairs, HUD chip strings for "SCHEDULE KNOWN" (Frozen + reveal), "SIGNAL SPENT", and "ON FILE" (+15% damage).

## Q:
- Q: Should "next 2 combats" count only fights, or Terminal-skipped nodes too? I assumed fights only.
- Q: Does the +15% enemy damage from "ON FILE" stack with a Heat-based modifier, or does the higher one win?
