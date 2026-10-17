<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__16_ambush_halcyon; status ok; tokens in 5062 cache-write 0 cache-read 32585 out 3404; cost $0.025. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, illusory stake, choice 1 dominates 2):**
  - The fight is now a true ambush. The warden is already waiting at the far end and the lights come on as the player drops in, so the framing is an impromptu fight.
  - Stake: a loss kills the operative as normal, and +1 Heat applies at fight start whether the player wins or loses. The skip is granted only on a win.
  - The reward drops to 20 Cycles plus 1 common Firmware.
  - The ambush bite is the `combat_overrides` tier +1 with a first-turn Citation (OUTPUT_DOWN ×1 on the player's first landing). The critic offered a fallback if this edit is not available, and I kept it as a named fallback.
  - Choice 2 is no longer dominated: it costs 40 Cycles, which exceeds the fight's 20 Cycles plus Firmware, but it carries no HP, death or Heat risk.
- **Issue 2 (BLOCKER, choice 3 mislabeled and weak):**
  - Took the critic's alternative and made it a real skip: "Slip past" skips the next combat node, with no reward and +2 Heat. Label and effect now agree.
  - The old 15 % HP discount is gone.
  - Role: it sits between choice 2 (40 Cycles, no Heat) and choice 4 (nothing). It pays Heat instead of Cycles, which suits a player who is short on Cycles but low on Heat.
- **Issue 3 (MAJOR, R2 arithmetic and tier preview):**
  - The HP band is now shown: Patrol Unit at T+1.
  - The preview must state the enemy, its raised tier and the exact map edit.
  - The tier bump is applied only if the node tier is ≤ 3; at T4 it stays at T4, and the Citation penalty then carries the ambush.
- **Issue 4 (MAJOR, edit scope):**
  - The target is now "the nearest Router ahead", and Elite Routers are never skipped.
  - If there is no valid Router, both skip choices are hidden. This matches the critic's fix and answers Q1: Mainframes and Terminals are never skipped.
  - The edit is `cleared`, which keeps the D7 full-graph view consistent. The v1 Q on cleared versus removed is closed.
  - The Heat inconsistency is gone because Elites are excluded; a skipped Router carries 0 Heat.
- **Issue 5 (MAJOR, unsupported "70 Cycles"):** Removed. The value is restated as the skip (about a node of time) versus the fight's 20 Cycles plus Firmware.
- **Issue 6 (NIT):** Cold Exit and Scrubber interactions are now explained. `dispatch_clue` and `foreshadows` stay empty because none applies.
- **Critic Q2 (Heat on a turn-1 win):** Heat applies on fight start regardless of outcome.

# ev_hal_maintenance_tunnel: Service Tunnel Shortcut

**Mechanic:** AMBUSH, corporation halcyon, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Fight the warden waiting in the tunnel for a skip and loot at the risk of your operative, pay Cycles for a safe skip, trade Heat for a quiet one, or walk on.

## TerminalEventData fields
- **id:** `ev_hal_maintenance_tunnel`
- **title:** Service Tunnel Shortcut
- **speaker:** STREET_MERC
- **text:** "A hatch behind the Terminal is stenciled MUNICIPAL ACCESS, AUTHORIZED PERSONNEL ONLY. Below it, a utility tunnel runs straight under the next two blocks of this Site. Halcyon's maintenance schedule says it's empty until the 6 a.m. inspection. The schedule is wrong. Something is parked at the far end, and the tunnel lights just came on."
- **corporation_id:** `halcyon`
- **min_tier:** 2
- **dispatch_clue:** false
- **foreshadows:** `&""`
- **weight:** 0.8
- **Availability:** choices 1–3 are shown only if a skippable Router exists ahead; otherwise only "Walk on" is shown.

## Choices

### 1. Drop in and fight the warden
- **label:** "Drop through the hatch (fight: skip + loot, +1 Heat)"
- **result_text:** "The warden pivots as you land and the lights lock on you. It was waiting."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount 1, applied when the fight starts (win or lose).
- **reward:** see the fight reward below.
- **(new) starts_combat (N16):** enemy `patrol_unit`.
  - **combat_overrides:** tier = node tier +1, capped at T4. First-turn ambush: the player's wheel takes OUTPUT_DOWN ×1 on the slice under the first pointer, applied at combat start (N8, N9). Fallback if N8 is not ready: tier bump only.
  - **HP (R2):** Patrol Unit is a 1-phase normal. At T2→T3 the band is 44–56 HP. At 14 reference dpt × 3.5 turns that is about 49, so the fight takes about 3.5 turns (R1). At T3→T4 the band is 56–70 (18 dpt, about 3.5 turns).
  - **stake:** a loss means the operative dies under the normal death rules (GDD 4.2), and the +1 Heat is already paid. The skip is granted only on a win.
  - **reward (on win):** 20 Cycles, plus 1 common Firmware from the `events` RNG stream at a checkpoint.
- **(new) map_edits (N16):** on a win, mark the nearest Router ahead as `cleared` (no reward, no Heat). Elite Routers, Mainframes, Terminals and Racks are never targeted.

### 2. Pay the maintenance AI
- **label:** "Pay the schedule off (−40 Cycles, safe skip)"
- **result_text:** "A utility bot takes your Cycles and logs the inspection as complete. You walk the tunnel alone, and the route shortens."
- **cycle_cost:** 40
- **hp_cost:** 0
- **effects:** none
- **reward:** none
- **(new) map_edits:** the same skip as choice 1, granted immediately.

### 3. Pull the breaker
- **label:** "Kill the tunnel lights and slip past (+2 Heat, skip)"
- **result_text:** "Darkness, then a long crawl. The warden never sees you, but the grid logs a power fault at your hatch."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount 2.
- **reward:** none
- **(new) map_edits:** the same skip as choice 1.

### 4. Walk on
- **label:** "Take the long way"
- **result_text:** "You seal the hatch. Somewhere underneath you, the warden goes back to waiting."
- no costs, no effects.

## Design notes
- **Three prices for the same skip:**
  - Choice 1 pays in risk: 1 Heat plus a real chance of death, for +20 Cycles and Firmware.
  - Choice 2 pays in Cycles: 40, with no risk.
  - Choice 3 pays in Heat: 2, with no risk and no Cycles.
  - Choice 4 pays nothing and gains nothing.
  - No option dominates:
    - Choice 1 beats 2 only for a strong, healthy build that wants Firmware. A weak or damaged operative should pay.
    - Choice 3 beats 2 when Cycles are scarce and Heat is low, and loses badly near a threshold.
- **Economy check (GDD 11 placeholders):** a normal fight pays about 15–20 Cycles at T2 and a skip saves about 2 minutes (GDD 4.2 pacing). Choice 1 yields 20 Cycles, a Firmware and a skip, against a T+1 fight with a first-turn penalty and a death risk, which fits an elite-level reward for an elite-level stake. Choice 2's 40 Cycles buys safety. Choice 3's 2 Heat is two thirds of a minor step (3 Heat per minor threshold is the placeholder).
- **Interactions:**
  - Heat from choices 1 and 3 may cross a threshold such as 25 and trigger a raid (GDD 4.3). The preview should show the threshold distance.
  - Cold Exit (no NULL slice resolving) and Clean Signal (3 consecutive Perfects) count during the impromptu fight, because it is a normal combat. A won ambush also counts for Kernel Sync, but not for Rank, which counts netruns survived.
  - Skipping never removes a shop or event, because only a Router is a valid target.
  - The ambush penalty is a status on the player's wheel and keeps its stacks through any later phase change (R6), though Patrol Unit has only one phase.
- **Determinism:** only the Firmware draw is random, on the `events` stream at a checkpoint. The enemy, tier, penalty and map edit are fixed, so the preview can state all of them.
- **Text keys needed:** `ev_hal_maintenance_tunnel.*` (title, text, 4 labels, 4 results), plus a toast "NODE SKIPPED" and a preview line "AMBUSH: PATROL UNIT, T{n}".

## Q:
Q: Should the tier bump apply at T4 nodes, where it is already capped, or should the ambush add a second Citation instead?
Q: Should a lost ambush also drop the Heat refund, or is a flat +1 Heat acceptable on a death?
