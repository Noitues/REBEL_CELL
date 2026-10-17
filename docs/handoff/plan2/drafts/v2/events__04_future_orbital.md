<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__04_future_orbital; status ok; tokens in 4932 cache-write 0 cache-read 32585 out 2977; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, untagged keys):** all three choices now carry a typed `next_combat_overrides` dict with an explicit N# tag per key. `starts_combat` and `map_edits` are written as typed "none". The key table is in Design notes: N16 for the container, NEW: enemy_start_flags for the freeze flag, N13 for satellite removal, NEW: player_start_bonus for the free nudge, N3 for reveal. Reveal is data-only (see Q1).
- **Issue 2 (MAJOR, precedence, "Frozen" not a status):** renamed to the init flag `enemy_start_freeze`, not a status. Precedence is stated: `enemy_damage_pct` adds to Heat modifiers, and the same key never stacks across events (the highest wins). This answers v1's Heat-stacking Q. The Halcyon Curfew question is dropped, because the flag only skips the respin and never sets `nudge_locked`.
- **Issue 3 (MAJOR, C1 near-free):** C1 is now +3 Heat. Reveal is restricted to fights where it matters: the override counts only the next 2 fights, and `reveal_next_layout` is consumed only on Elite/Mini-Boss fights (skipped normals don't use up the count for that key). Freeze is also stronger: the enemy's first respin is skipped and the player gets to read the real layout, which is now the stated value.
- **Issue 4 (MAJOR, C3 fallback):** the fallback is now "Cycles +45 and Heat +6, no override", so the choice stays distinct (more Heat, no deferred damage).
- **Issue 5 (MAJOR, Calibrated):** the reward is tagged N12, with the fallback Patch+.
- **Issue 6 (NIT, C4 fields):** C4 now has the full field list.
- **Issue 7 (NIT, skipped nodes):** kept, because the Q is moot; overrides are consumed at combat creation only. Q removed.
- **Issue 8 (NIT, word count):** kept, within range.
- **Issue 9 (NIT, "+0 Cycles"):** removed from the label.
- **Critic Q2 (satellite no-op):** decided. The satellite removal carries over to the next fight that has a satellite, within the 1-combat window only if it's used; otherwise it is wasted. Simpler: it is wasted. Stated in notes.

# ev_orb_cold_witness: The Witness on the Rim

**Mechanic:** FUTURE, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** A deorbit survivor will testify. Spend her testimony on two fights, spend your own HP on one clean fight, or sell her for Cycles and carry a target on your back.

## TerminalEventData fields
- id: `ev_orb_cold_witness`
- title: The Witness on the Rim
- speaker: STREET_MERC
- text: "A maintenance tech sits in a pressure-suit liner behind the Terminal, still shaking. She was on the platform when Orbital Commons deorbited a crew's worth of 'underperforming assets' and logged it as debris. She saw the burn schedule and the countdown. She'll swear to it, but only if someone makes the sky stop listening. A launch-pad relay is already pinging her badge."
- corporation_id: `orbital`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Take the burn schedule
- label: Take the burn schedule (+3 Heat)
- result_text: "She reads timings from memory. Every handoff, every gap. You write them on your wrist. The relay stops pinging, but only because it logged you."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / +3
- reward: none
- (new) next_combat_overrides = {combats: 2, enemy_start_freeze: true (NEW: enemy_start_flags), reveal_next_layout: true (N3, elite/mini-boss fights only)}
- (new) starts_combat: none
- (new) map_edits: none

### 2. Mask her signal
- label: Mask her signal (−8 HP)
- result_text: "You route the relay's attention through your own implant. It burns. She slips down the service ladder and leaves a sealed packet taped under the Terminal."
- cycle_cost: 0, hp_cost: 8
- effects: none
- reward: Firmware, uncommon: Calibrated (raises every sub-tick of one slice one tier; N12). Fallback without N12: Patch+.
- (new) next_combat_overrides = {combats: 1, free_nudges_turn1: +1 (NEW: player_start_bonus), remove_enemy_satellites: 1 (N13)}
- (new) starts_combat: none
- (new) map_edits: none

### 3. Sell her to the relay
- label: Hand her to the relay (+45 Cycles, +4 Heat)
- result_text: "The badge ping goes quiet. A payment clears from a line item called 'witness remediation.' You don't look at the ladder."
- cycle_cost: 0, hp_cost: 0
- effects: GAIN_CYCLES / CAMPAIGN / +45; MODIFY_HEAT / CAMPAIGN / +4
- reward: none
- (new) next_combat_overrides = {combats: 2, enemy_damage_pct: +15} (N16). Fallback without N16: Cycles +45, Heat +6, no override.
- (new) starts_combat: none
- (new) map_edits: none

### 4. Walk past
- label: Walk past
- result_text: "She doesn't call after you. The relay's ping resumes a few seconds later."
- cycle_cost: 0, hp_cost: 0
- effects: none
- reward: none
- (new) next_combat_overrides: none; starts_combat: none; map_edits: none

## Design notes
**Why it's interesting.**
- **C1** buys tempo across two fights: the enemy's first respin is skipped, so you read its real first landing, and elites also show their next layout. It costs +3 Heat and does little against plain normals, so it is worth the most when an elite or mini-boss is close on the map.
- **C2** is the HP option: 8 HP is about 13% of a 60 HP Breaker. It buys one strong fight (an extra free nudge, a satellite gone) and a Firmware, but nothing across a second fight.
- **C3** is greedy. +45 Cycles is about one Mainframe purchase, but two fights at +15% enemy damage can cost more than 8 HP at T2–T3, and the cost is hidden in later HP loss.

**Economy.** A typical Terminal pays 25–30 Cycles. C3's +45 and +4 Heat are deliberately above that. Heat +3 to +4 matters for raid timing without forcing a raid by itself.

**Precedence.** `enemy_damage_pct` is a tier-independent buff (R2). It adds to Heat modifiers. The same key never stacks across events, so the highest value wins. Overrides are consumed in order, and `combats` counts fights actually created.

**Key table.**

| Key | Dependency | Fallback |
|---|---|---|
| `combats` / container | N16 | Plain rewards |
| `enemy_start_freeze` (skips the first start-of-turn respin; not a status) | NEW: enemy_start_flags | none |
| `reveal_next_layout` | N3 | none |
| `free_nudges_turn1` | NEW: player_start_bonus | Firmware only |
| `remove_enemy_satellites` | N13 | none |
| `enemy_damage_pct` | N16 | Heat +6 |

**Interactions.** Freeze doesn't undo Weight, because it only skips the respin. A satellite removal with no satellite in the fight is wasted; it does not carry over. Reveal applies to elites and mini-bosses only, and boss Chart Hidden is untouched.

**Determinism.** Overrides are run-state data read at combat creation. No RNG. The preview reads them before the fight, so the preview equals the result.

**Text keys.** `evt.orb_cold_witness.title/body`, four `choice.*.label/result` pairs, HUD chips "SCHEDULE KNOWN", "SIGNAL SPENT", "ON FILE".

## Q:
- Q1: Is `reveal_next_layout` worth a new engine flag, or should it ship as a text-only note on the preview until N3 lands?
- Q2: Should C3's +15% be visible on the map as a chip, or hidden until the fight so the cost stays blind?
