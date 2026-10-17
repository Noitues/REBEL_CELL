<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__01_future_solace; status ok; tokens in 6464 cache-write 0 cache-read 32007 out 2170; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_sol_courtesy_waiver: Courtesy Waiver

**Mechanic:** FUTURE, corporation solace, min_tier 1, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** Call in a favor from a Solace billing clerk who owes you. Do you take a quiet edge on the next fight, a deeper one that tags the whole route, or keep the favor in your pocket?

## TerminalEventData fields
- **id:** `ev_sol_courtesy_waiver`
- **title:** Courtesy Waiver
- **speaker:** `RC.Voice.STREET_MERC` (1)
- **text:** "The Terminal is a Continuum claims window, still logged in. A clerk named Odile sits behind it, three weeks from a performance review she won't survive. Last spring you got her mother's leash reinstated, and she hasn't forgotten. 'I can waive something on their side,' she whispers. 'Courtesy adjustment. Just don't make me pick what.' Her badge light is already blinking. Someone is watching her queue."
- **corporation_id:** `solace`
- **min_tier:** 1
- **dispatch_clue:** false
- **foreshadows:** `&""`
- **weight:** 1.0

## Choices

### 1. "Waive the next dispatch" (small, safe)
- **label:** Waive the next dispatch (next fight: enemy starts Frozen)
- **result_text:** "Odile flags a 'scheduling conflict.' Somewhere down the line, a unit sits idle waiting for an authorization that never comes."
- **cycle_cost:** 0
- **hp_cost:** 0
- **effects:** none
- **reward:** none
- **next_combat_overrides (new):** applies to the next combat only (duration 1 combat):
  - `enemy_wheel_frozen = true` (enemy skips its first start-of-turn respin; existing Freeze rule, GDD 2.5)

### 2. "Rewrite the whole route's file" (big, costs you)
- **label:** Rewrite the route file (next 3 fights: enemy −1 resistance, enemy HP −15 %; you −6 HP, +2 Heat)
- **result_text:** "Odile types for ninety seconds without blinking. The clerk's work holds, but the audit flag she trips follows you out the door."
- **cycle_cost:** 0
- **hp_cost:** 6 (a feedback spike through the jack)
- **effects:**
  - `MODIFY_HEAT`, target CAMPAIGN, amount 2
- **reward:** none
- **next_combat_overrides (new):** duration 3 combats:
  - `enemy_resistance_delta = -1` (floor 0)
  - `enemy_hp_pct = -15` (percent of the enemy's max HP, applied at combat creation; the R2 band validator is bypassed intentionally and the HP floor is 1 per phase)

### 3. "Ask for a pre-authorized exit" (utility, hedge)
- **label:** Ask for a pre-authorized exit (next fight: one free nudge, enemy phase layout revealed; pay 15 Cycles)
- **result_text:** "'Courtesy adjustments come with a processing fee,' Odile says, almost apologizing. 'Policy.' You pay. She slides you the unit's service chart."
- **cycle_cost:** 15
- **hp_cost:** 0
- **effects:** none
- **reward:** none
- **next_combat_overrides (new):** next combat only:
  - `player_extra_free_nudges = 1` (a second free nudge each turn of that fight)
  - `reveal_phases = true` (phase list and next layouts visible from turn 1, which also shows them under Chart Hidden)

### 4. "Keep the favor"
- **label:** Tell her to keep her badge clean
- **result_text:** "Odile exhales. 'Then you owe me nothing, and I owe you everything.' She logs out. You can't tell whether that is mercy or a debt you'll regret."
- **cycle_cost / hp_cost:** 0
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount −1 (her file stays clean, so the audit trail does too)
- **reward:** none
- **next_combat_overrides:** none (this is the safe option with no future effect)

## Design notes
- **No dominant option.** Choice 1 is free but narrow: Freeze skips one respin, so it only helps if you plan for turn 1. Choice 2 is worth about 3 easier fights (−15 % HP is roughly half a phase on a normal, ~0.5 turns), but costs 6 HP (≈10 % of a Breaker) and +2 Heat; against GDD 4.2 pacing (5 combats per run, ~1 Heat per elite), it is a real price. Choice 3 costs ~15 Cycles (about a third of a typical shop slice) for information plus tempo, and suits an elite or mini-boss you can see coming. Choice 4 is a Heat-neutral decline for players who are already at the edge.
- **Run economy:** the HP and Cycles costs are small against ~100 Cycles and 45–60 HP per run, so the choice hinges on which upcoming node you expect.
- **Interactions:** the `enemy_hp_pct` override stacks with R2 band checks (needs the validator to ignore overrides). Frozen composes with Compliance Lock: Freeze is not blocked by resistance, per GDD 2.5. Chart reveal pairs with the Genome Core's Chart Hidden buff and cancels it for one fight.
- **Determinism:** all overrides are static values stored in run state (`next_combat_overrides`, checkpoint-safe), so previews equal results and no RNG is consumed.
- **Counting rule:** combats are counted by completed fights, not nodes visited, so a skipped node doesn't burn a charge.
- **Text keys:** `ev_sol_courtesy_waiver.title/text`, `.c1`–`.c4` labels and results, plus a run HUD chip per active override ("WAIVER ×3").

## Q:
- Q: Should an override persist through a death-adjacent abandon, or end with the netrun? (Proposed: ends with the netrun.)
- Q: Does Choice 2's HP cut apply to a mini-boss's last Rack fight, or only to normals and elites?
