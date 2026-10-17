<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__16_ambush_halcyon; status ok; tokens in 6421 cache-write 0 cache-read 32007 out 2250; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_hal_maintenance_tunnel: Service Tunnel Shortcut

**Mechanic:** AMBUSH, corporation halcyon, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Take the municipal service tunnel to skip ahead, and fight the warden who patrols it, or walk the long way for nothing.

## TerminalEventData fields
- **id:** `ev_hal_maintenance_tunnel`
- **title:** Service Tunnel Shortcut
- **speaker:** STREET_MERC
- **text:** "A hatch behind the Terminal is stenciled MUNICIPAL ACCESS, AUTHORIZED PERSONNEL ONLY. Below it, a utility tunnel runs straight under the next two blocks of this Site. Halcyon's own maintenance schedule says it's empty until the 6 a.m. inspection. The schedule is wrong, though. Something is parked at the far end, and the tunnel lights just came on."
- **corporation_id:** `halcyon`
- **min_tier:** 2
- **dispatch_clue:** false
- **foreshadows:** `&""`
- **weight:** 0.8

## Choices

### 1. Force the tunnel (fight the warden)
- **label:** "Drop through the hatch (fight, skip ahead)"
- **result_text:** "The warden pivots as you land. You wanted the shortcut, so now you pay the toll."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** none directly; all consequences come from the fight.
- **reward:** none directly (see fight reward).
- **(new) starts_combat:** enemy `patrol_unit`, on a win.
  - **combat_overrides:** tier +1 over the node's tier, capped at T4. Enemy HP uses the `hp_by_tier` entry for the raised tier (R2). No other tweaks, so the fight is a standard 1-phase normal.
  - **stake:** the operative keeps whatever HP the fight costs. On a loss the usual death rules apply, with no event-specific penalty. +1 Heat when the fight starts (the alarm trips).
  - **reward (on win):** 30 Cycles, plus 1 Firmware drawn from the common pool on the `events` RNG stream.
- **(new) map_edits:** on a win, mark the next layer's combat node (the nearest Router or Elite Router ahead) as `cleared`. It is skipped and its Heat is not applied. No rewards are granted from the skipped node.

### 2. Bribe the maintenance AI
- **label:** "Pay the schedule off (-40 Cycles)"
- **result_text:** "A utility bot takes your Cycles and logs the inspection as complete. You walk through the tunnel alone, and the long route shortens anyway."
- **cycle_cost:** 40
- **hp_cost:** 0
- **effects:** none
- **reward:** none
- **(new) map_edits:** the same skip as choice 1: the next layer's combat node is marked cleared, no reward and no Heat from it.

### 3. Pull the breaker
- **label:** "Kill the tunnel lights (+2 Heat), then slip past"
- **result_text:** "Darkness, then a long crawl. The warden never spots you, but the grid logs a power fault at your hatch."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount 2.
- **reward:** none
- **(new) next_combat_overrides:** applies to the next combat only: enemy HP −15 %, no other change. This is the player's gain from scouting the tunnel's layout. Duration: 1 combat.

### 4. Walk on
- **label:** "Take the long way"
- **result_text:** "You seal the hatch. Somewhere underneath you, the warden goes back to waiting."
- no costs, no effects.

## Design notes
- **The decision:** choice 1 is a fight that pays for itself and skips a node. Choice 2 is the clean, expensive version of the same skip. Choice 3 is a cheap partial benefit with Heat. Choice 4 is the baseline. No option dominates:
  - Choice 1 is the strongest on reward (30 Cycles + Firmware + skip), but it is a T+1 fight against a normal with a threat that adds Heat and risks HP right before the unskippable fights.
  - Choice 2 beats it on safety and loses roughly 70 Cycles of value.
  - Choice 3 is best for a player already at high Heat who wants to save HP, if they accept the Heat cost. It is the weakest on gain.
- **Economy check:** a normal fight pays about 15–20 Cycles at T2 plus Heat 0. Skipping a node saves about 2 minutes (GDD 4.2 pacing). Choice 1's 30 Cycles + Firmware + skip is worth about a node and a half, offset by the T+1 fight and +1 Heat.
- **Patrol Unit:** as a normal at T+1 it fits the tunnel setting (a patrol officer), a 1-phase fight that tests whether the player can burst it in 3–4 turns (R1).
- **Interactions:**
  - Cold Exit and Scrubber Daemons are not affected.
  - Heat from choice 1 at threshold 25 may trigger a raid (GDD 4.3), which makes the decision riskier for a player near 24.
  - Skipping a node removes any Mainframe or Terminal on it, so a player should not take the shortcut over their only shop.
  - Choice 3's HP reduction is a data field on `next_combat_overrides` and does not affect phase thresholds (R2: percent values read the enemy's own HP).
- **Determinism:** the Firmware draw uses the `events` stream at a checkpoint (as N17). The fight and the skip are deterministic, so the choice-1 preview can state the enemy, its tier and the exact map edit.
- **Text keys needed:** `ev_hal_maintenance_tunnel.*` (title, text, 4 labels, 4 results), plus a map-edit toast "NODE SKIPPED".

## Q:
Q: Should the skipped node be marked cleared (its Heat and rewards lost) or removed from the graph (the player never sees it)? The first keeps the full-graph view of D7 consistent.
Q: Does a won impromptu fight count toward Rank (netruns survived) or toward Clean Signal and Kernel Sync Daemon counters? Proposed: yes for Daemon hooks, no for Rank.
