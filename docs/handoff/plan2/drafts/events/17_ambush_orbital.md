<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__17_ambush_orbital; status ok; tokens in 6419 cache-write 0 cache-read 32007 out 2148; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_orb_rumor_flare: Rumor of a Dead Bird

**Mechanic:** AMBUSH, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Chase a rumor that a decommissioned satellite dumped its cache, which means an impromptu fight against an uplink relay with a stake and a reward, or sell the rumor on, or ignore it.

## TerminalEventData fields
- **id:** `ev_orb_rumor_flare`
- **title:** Rumor of a Dead Bird
- **speaker:** STREET_MERC
- **text:** "Heard it on the roof-dish net, third hand, so salt it. A bird Orbital wrote off last quarter coughed up its whole cache on a one-minute window, and the relay that caught it never reported the dump. Now that relay is guarding a gift it swears it doesn't have. Could be a payday. Could be bait with a bandwidth bill. Rumors cost nothing until you act on one."
- **corporation_id:** `orbital`
- **min_tier:** 2
- **dispatch_clue:** false
- **foreshadows:** (empty)
- **weight:** 0.8

## Choices

### 1. Chase the rumor (fight)
- **label:** Chase it: crack the relay (fight, stake 10 HP, reward Daemon)
- **result_text:** The relay lights up the moment you touch its port. "No dump on record," it says, and starts charging.
- **cycle_cost:** 0
- **hp_cost:** 0 (the stake is paid only on a loss; see below)
- **effects:** none up front
- **reward:** granted on a win: one random Daemon from the Server Rack rare pool (`events` RNG stream, checkpointed)
- **(new) starts_combat:** enemy `uplink_relay`
  - **combat_overrides:** tier +1 over the node's tier (cap 4); `enemy_hp_by_tier` read at the raised tier, with damage from `enemy_damage_by_tier` as usual (R2); no other changes.
  - **stake:** `on_defeat_effects` = MODIFY_HEAT +4 (CAMPAIGN) as the relay "files the intrusion". There is no extra HP stake: the run's own HP is already at risk in the fight.
  - **on_victory:** reward as above, plus GAIN_CYCLES +15.
  - **flee:** none. Once started it must be fought.

### 2. Verify first (a safer fight)
- **label:** Ping the relay first (-12 Cycles; weaker fight, smaller reward)
- **result_text:** You pay for a handshake that tells you which rumor is real. It's real, but thinner than advertised, and the relay still picks the fight.
- **cycle_cost:** 12
- **hp_cost:** 0
- **effects:** none
- **reward:** granted on a win: one Firmware (common pool)
- **(new) starts_combat:** enemy `uplink_relay`
  - **combat_overrides:** tier unchanged; the first enemy turn is skipped (the relay starts frozen, using the existing FREEZE rule).
  - **stake:** none on defeat.
  - **on_victory:** reward as above.

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
- **No dominant option.** Chase is high variance: the Daemon is the best reward in the Terminal pool, but the relay is a tier above the node, and a loss adds Heat on top of the damage. Verify costs Cycles up front and gives only a common Firmware, but the frozen opening takes away the first-turn burst that hurts most. Selling is a pure economy choice that costs Heat. Leaving it is free.
- **Numbers** (placeholders vs GDD 11): a T2+ run holds roughly 40–80 Cycles at a Terminal. +18 is about a third of that, comparable to Billing Loop's +30 with +3 Heat, so the sale is deliberately a little weaker. Chase's +15 Cycles plus a Daemon beats a typical Router reward, and +4 Heat on defeat is a bit more than one Elite Router (+1), which makes losing hurt.
- **R2 check.** `uplink_relay` is a one-phase normal with a T3 band of 44–56 HP. At T+1 the relay is in the next band up (T2 node: 44–56; T3 node: 56–70). At the reference 14 damage per turn, 3.5 turns gives about 49 HP, so a T2 node's chase relay (T3 values) is a fight of 3–4 turns. This fits the normal-enemy target and keeps the raised tier a real cost rather than a long slog.
- **Determinism.** The Daemon draw uses the checkpointed `events` stream and happens only on a win, so rewinding past the fight can't reroll it.
- **Text keys:** `EV_ORB_RUMOR_FLARE_TITLE`, `_TEXT`, `_C1`–`_C4` labels and results, plus a defeat line: "The relay logs you. The bird stays dead."
- **Dependencies:** N16 only (`starts_combat`, `combat_overrides`, `on_defeat_effects`, `on_victory`). **Data-only fallback:** none for the fight itself. Without N16, choice 1 can fall back to HP-cost 8 for the Daemon at a 50 % lower reward, and choice 2 is removed.

## Q:
- Q: Should a lost impromptu fight cost the operative nothing beyond the HP lost and the Heat stake, or end the node (forcing a retreat)?
- Q: Does "tier +1" cap at the run's access tier, or can it reach T4 on a T3 node?
