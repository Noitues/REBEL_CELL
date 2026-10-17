<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__17_ambush_orbital; status ok; tokens in 5256 cache-write 0 cache-read 32585 out 2800; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, invented fields)** → `on_defeat_effects` and `on_victory` are removed. The fight now uses only `starts_combat` plus `combat_overrides` (N16). The win reward uses the existing combat-reward flow, and a loss is ordinary operative death (GDD 4.2). The Heat-on-defeat stake is dropped because it was moot. The real stake is `hp_cost` 8 paid on entry. `enemy_hp_by_tier` is renamed `hp_by_tier` (N2).
- **Issue 2 (BLOCKER, FREEZE)** → The frozen-relay claim is removed. Choice 2 now uses `hp_pct` −25 and a `wheel_override` that makes the relay's first slice NULL (N3 `wheel_override`). Fallback: the HP reduction only. The Daemon draw is tagged to the `events` RNG stream, checkpointed, drawn on a win only.
- **Issue 3 (MAJOR, arithmetic)** → The R2 check is redone. Cap = run access tier, so T4 is unreachable (this answers v1 Q2).
- **Issue 4 (MAJOR, dominance)** → Choice 2's reward is raised to an uncommon Firmware, and its cost is now 12 Cycles + 4 HP. Choice 1 gets a real entry stake (8 HP). The notes now weigh permadeath risk.
- **Issue 5 (MAJOR, uplink_relay unverified)** → I did not invent relay stats. The notes state the dependency on its existing one-phase normal data and use only R2 band values. The Billing Loop comparison is removed. The "gift" is framed as flavor text only.
- **Issue 6 (NIT)** → `dispatch_clue` is left empty. The fallback is rewritten coherently.
- **Issue 7 (NIT)** → Length is fine. Kept.
- **Critic Q1** → Answered: loss is lethal under GDD 4.2, which is binding. There is no retreat.
- **Critic Q2** → Kept as a normal, with no scope added. An elite stays an open question.

# ev_orb_rumor_flare: Rumor of a Dead Bird

**Mechanic:** AMBUSH, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Chase a rumor of a dumped satellite cache into a forced, lethal fight against an uplink relay for a Daemon, pay to take a softer version for a Firmware, sell the rumor, or ignore it.

## TerminalEventData fields
- **id:** `ev_orb_rumor_flare`
- **title:** Rumor of a Dead Bird
- **speaker:** STREET_MERC
- **text:** "Heard it on the roof-dish net, third hand, so salt it. A bird Orbital wrote off last quarter coughed up its whole cache in a one-minute window, and the relay that caught it never reported the dump. Now that relay is guarding a gift it swears it doesn't have. Could be a payday. Could be bait with a bandwidth bill. Rumors cost nothing until you act on one."
- **corporation_id:** `orbital`
- **min_tier:** 2
- **dispatch_clue:** (empty)
- **foreshadows:** (empty)
- **weight:** 0.8

## Choices

### 1. Chase the rumor (hard fight)
- **label:** Chase it: crack the relay (-8 HP, tougher fight, reward Daemon)
- **result_text:** The relay lights up the moment you touch its port. "No dump on record," it says, and starts charging.
- **cycle_cost:** 0
- **hp_cost:** 8, paid on entry
- **effects:** none
- **reward (on win):** one Daemon from the Server Rack rare pool, drawn from the `events` RNG stream at a checkpoint, on a win only; plus GAIN_CYCLES +15
- **(new) starts_combat:** enemy `uplink_relay`
  - **combat_overrides (N16):** `tier_delta` +1, capped at the run's access tier (never above T3 on T2–T3 nodes). HP is read from `hp_by_tier` at the raised tier, and damage from `enemy_damage_by_tier` (R2).
  - **stake:** the 8 HP entry cost. A loss is normal operative death with unbanked loot gone (GDD 4.2). The fight is forced: no flee.

### 2. Verify first (softer fight)
- **label:** Ping the relay first (-12 Cycles, -4 HP, weaker fight, Firmware)
- **result_text:** You pay for a handshake that tells you which rumor is real. It's real, but thinner than advertised, and the relay still picks the fight.
- **cycle_cost:** 12
- **hp_cost:** 4, paid on entry
- **effects:** none
- **reward (on win):** one uncommon Firmware
- **(new) starts_combat:** enemy `uplink_relay`
  - **combat_overrides (N16):** tier unchanged; `hp_pct` −25; `wheel_override` at start sets the relay's first slice to NULL (N3). **Fallback:** the `hp_pct` cut only.
  - **stake:** the entry costs; loss is operative death.

### 3. Sell the rumor
- **label:** Sell the rumor on (+18 Cycles, +1 Heat)
- **result_text:** Someone else will chase it. You pocket the fee, and the hop leaves a faint trail back to you.
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** GAIN_CYCLES +18 (CAMPAIGN); MODIFY_HEAT +1 (CAMPAIGN)
- **reward:** none

### 4. Ignore it
- **label:** Let it ride
- **result_text:** Nothing found, nothing lost, and nobody can say you were there.
- **effects:** none

## Design notes
- **No dominant option.** Chase has the best prize (Daemon + 15 Cycles) but costs 8 HP up front, runs a tier above the node, and a loss kills the operative. Verify pays 12 Cycles and 4 HP for a softer fight and a good-but-lesser Firmware, so it is the safe line for a hurt run. Selling is a pure economy choice that costs Heat. Ignoring it is free.
- **Numbers** (placeholders vs GDD 11): a T2+ run holds roughly 40–80 Cycles at a Terminal. The +18 sale is about a third of that, for +1 Heat.
- **R2 check.** `uplink_relay` is a one-phase normal (R1). Chase on a T2 node reads T3 values: band 44–56 HP; reference 14 damage per turn × 3.5 turns ≈ 49 HP, which is 3.5 turns. On a T3 node the cap holds the relay at T3, so the same 3.5 turns. T4 is unreachable. Verify: 49 × 0.75 ≈ 37 HP, about 2.6 turns plus the NULL opener. That is a little under the 3–4 target, which is acceptable for the softer option.
- **Dependency.** The relay's own slices and Hub are used as authored; this event adds no enemy content.
- **Determinism.** The Daemon draw uses the checkpointed `events` stream and happens only on a win, so a rewind cannot reroll it.
- **Text keys:** `EV_ORB_RUMOR_FLARE_TITLE`, `_TEXT`, `_C1`–`_C4` labels and results.
- **Dependencies:** N16 (`starts_combat`, `combat_overrides`), N2 (`hp_by_tier`), N3 (`wheel_override`). **Data-only fallback:** none for the fight. Without N16, choice 1 becomes an 8 HP cost for a common Firmware, and choice 2 is removed.

## Q:
- Q: Should an ambush with a Daemon reward use an elite (2 phases) rather than a boosted normal?
- Q: Should a forced, lethal fight on a Terminal be warned about in the choice label (for example a skull marker)?
