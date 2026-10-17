<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__01_future_solace; status ok; tokens in 5020 cache-write 0 cache-read 32585 out 3193; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (MAJOR, HP cut vs R3 floors):** kept the HP cut but defined it. `enemy_hp_pct` changes max HP at combat creation (rounds up, min 1). The R3 floors are computed from the reduced max HP with thresholds unchanged. The validator reads authored `hp_by_tier` only, never the run override. Fixed the mislabeled "stacks with R2 band checks" note.
- **Issue 2 (MAJOR, Choice 2 dominant):** applied the critic's fix: −10 % HP over 2 combats, hp_cost 8, +2 Heat. Removed the free resistance delta. Resistance −1 is now a separate effect that applies to elites and mini-bosses only (no value on normals, which mostly lack resistance). The note now states plain arithmetic: a normal has 1 phase of 3–4 turns, so −10 % is about 0.35 turns.
- **Issue 3 (MAJOR, Choice 1 weak):** Freeze is now defined as: FREEZE on the enemy wheel at combat start (skips the turn-1 respin; the pointer is already placed and shown). Added +1 free nudge on turn 1 of that fight. Removed the unverified Compliance Lock claim. GDD 2.5 lists no resistance clause for Freeze, but I could not confirm interaction with the Hub, so the note states only the verified rule.
- **Issue 4 (MAJOR, Choice 3):** the reveal applies to elites and mini-bosses only. For a normal fight there is nothing to reveal, so the 15 Cycles are refunded and the free nudge still applies. `player_extra_free_nudges` is flagged as an extension field of N16 (the spec lists "a free nudge" as an example).
- **Issue 5 (MAJOR, Choice 4):** the decline is now `MODIFY_HEAT 0` plus +5 Cycles, a neutral baseline instead of a strict upgrade.
- **Issue 6, 7 (NIT):** kept; the text, `STREET_MERC` and the lexicon use are correct.
- **Issue 8 (NIT):** added N16 (depends on N2) and the data-only fallback line.
- **Critic Q's:** answered in the notes. Overrides end with the netrun. Boss and mini-boss Rack fights are excluded from the HP cut.

# ev_sol_courtesy_waiver: Courtesy Waiver

**Mechanic:** FUTURE, corporation solace, min_tier 1, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** Call in a favor from a Solace billing clerk. Take a quiet edge on the next fight, a deeper two-fight discount that costs blood and Heat, a paid hedge for a tough fight, or leave her file clean for a little cash.

## TerminalEventData fields
- **id:** `ev_sol_courtesy_waiver`
- **title:** Courtesy Waiver
- **speaker:** `RC.Voice.STREET_MERC`
- **text:** "The Terminal is a Continuum claims window, still logged in. A clerk named Odile sits behind it, three weeks from a performance review she won't survive. Last spring you got her mother's leash reinstated, and she hasn't forgotten. 'I can waive something on their side,' she whispers. 'Courtesy adjustment. Just don't make me pick what.' Her badge light is already blinking, and someone is watching her queue."
- **corporation_id:** `solace`
- **min_tier:** 1
- **dispatch_clue:** false
- **foreshadows:** `&""`
- **weight:** 1.0

## Choices

### 1. "Waive the next dispatch" (small, safe)
- **label:** Waive the next dispatch (next fight: enemy Frozen on turn 1, +1 free nudge on turn 1)
- **result_text:** "Odile flags a 'scheduling conflict.' Somewhere down the line, a unit sits idle waiting for an authorization that never comes."
- **cycle_cost:** 0 · **hp_cost:** 0
- **effects:** none · **reward:** none
- **next_combat_overrides (new, N16):** next 1 combat:
  - `FREEZE` on the enemy wheel at combat start. It skips its turn-1 respin, so the pointer stays where it was placed and the layout is visible.
  - `player_extra_free_nudges = 1` on turn 1 only (extension field of N16).

### 2. "Rewrite the route file" (big, costs you)
- **label:** Rewrite the route file (next 2 fights: enemy max HP −10 %; elites and mini-bosses also −1 resistance; you −8 HP, +2 Heat)
- **result_text:** "Odile types for ninety seconds without blinking. The clerk's work holds, but the audit flag she trips follows you out the door."
- **cycle_cost:** 0
- **hp_cost:** 8 (a feedback spike through the jack)
- **effects:** `MODIFY_HEAT`, target CAMPAIGN, amount 2
- **reward:** none
- **next_combat_overrides (new, N16):** next 2 combats:
  - `enemy_hp_pct = -10`: applied to max HP at combat creation (rounds up, min 1), before R3 floors are computed. Phase thresholds stay fractional, so floors use the reduced max HP. The validator reads authored `hp_by_tier` only. Not applied to mini-boss or Rack fights.
  - `enemy_resistance_delta = -1` (floor 0), only if the enemy is an elite or mini-boss.

### 3. "Ask for a pre-authorized exit" (hedge for a hard fight)
- **label:** Ask for a pre-authorized exit (pay 10 Cycles; next 2 fights: +1 free nudge each turn 1; the next elite or mini-boss also shows its phase layouts from turn 1)
- **result_text:** "'Courtesy adjustments come with a processing fee,' Odile says, almost apologizing. 'Policy.' You pay. She slides you the unit's service chart."
- **cycle_cost:** 10
- **hp_cost:** 0
- **effects:** none · **reward:** none
- **next_combat_overrides (new, N16):** next 2 combats:
  - `player_extra_free_nudges = 1` (turn 1 only, each fight).
  - `reveal_phases = true` on the first elite or mini-boss within the window (it also overrides Chart Hidden for that fight). Normals have nothing to reveal, so this part is simply unused.

### 4. "Keep her badge clean"
- **label:** Tell her to keep her badge clean (+5 Cycles)
- **result_text:** "Odile exhales. 'Then you owe me nothing, and I owe you everything.' She slips a petty-cash voucher across the glass. You can't tell whether that is mercy or a debt you'll regret."
- **cycle_cost / hp_cost:** 0
- **effects:** `GAIN_CYCLES`, target CAMPAIGN, amount 5
- **reward:** none
- **next_combat_overrides:** none

## Design notes
- **No dominant option.** Choice 1 is free but narrow: one fight, and a frozen first pointer helps only if the layout you see is favorable, so it is a plan-ahead tool. Choice 2 trades 8 HP (about 13–18 % of a Breaker's 45–60 HP) and 2 Heat for two easier fights. On a normal (1 phase, 3–4 turns), −10 % HP is only about 0.35 turns per fight. The real value is on elites, where it also strips resistance. Choice 3 costs 10 Cycles (about a tenth of a ~100-Cycle run) and is best saved for an elite or mini-boss you can see coming. Choice 4 is a small guaranteed payout and no Heat.
- **Interactions:** the Chart reveal cancels the Genome Core's Chart Hidden buff for that one fight. The HP cut changes max HP before R3 floors, so parking and thresholds scale with it and previews equal results.
- **Determinism:** every override is a static value stored in run state (`next_combat_overrides`, checkpointed). No RNG is consumed.
- **Counting rule:** combats count by completed fights, not nodes visited, so a skipped node doesn't burn a charge. Overrides end with the netrun.
- **Dependencies:** N16 (depends on N2). The extension fields are `player_extra_free_nudges`, `enemy_hp_pct`, `enemy_resistance_delta` and `reveal_phases`. Data-only fallback: apply FREEZE and MODIFY_RESISTANCE through existing ON_COMBAT_START effects on a run Daemon. The HP cut and the reveal have no fallback.
- **Text keys:** `ev_sol_courtesy_waiver.title/text`, `.c1`–`.c4` labels and results, plus a run HUD chip per active override ("WAIVER ×2").

## Q:
- Q: Should the elite/mini-boss reveal in Choice 3 carry over if no such fight falls within the 2-fight window, or lapse?
- Q: Is a flat 8 HP cost too light for a Breaker but too heavy for a 45 HP Botnet? Should it be a percent of max HP?
