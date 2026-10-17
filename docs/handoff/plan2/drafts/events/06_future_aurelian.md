<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__06_future_aurelian; status ok; tokens in 6468 cache-write 0 cache-read 32007 out 2145; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_aur_service_lift: Service Lift

**Mechanic:** FUTURE, corporation aurelian, min_tier 2, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** Take a Lanista's staff shortcut that skips the arena queue: the next fight starts with its enemy softened, but the fight after it is rigged against you.

## TerminalEventData fields
- id: `ev_aur_service_lift`
- title: Service Lift
- speaker: STREET_MERC (1)
- text: "Behind the concession stands there's a freight lift stenciled STAFF ONLY, TERMS APPLY. The panel says it drops straight past the next two bouts to the Lanista's own box seats. Somebody has taped a patron's VERDICT chit over the camera. Nothing in this arena is free, but the shaft is dark and nobody is watching."
- corporation_id: `aurelian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 1.0

## Choices

**1. Ride the lift to the box seats**
- label: "Ride to the box seats (next fight easier, the one after harder)"
- result_text: "You step out behind the Lanista's chair and rewire the bout sheet before anyone looks up. The first client is already limping. By the next bout the house has noticed the edit, and it bets against you."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new), as a list:
  - Combat 1 (the next combat, duration 1): `enemy_hp_pct = -30`, `enemy_status_start = FROZEN` (skips its first respin; this is the Freeze effect), `reveal_phases = true`.
  - Combat 2 (the combat after that, duration 1): `enemy_damage_pct = +25`, `player_free_nudge = false` (the free nudge does not refresh on turn 1).
- starts_combat: none
- map_edits: none

**2. Pry the access panel and take only the tools**
- label: "Strip the panel (+20 Cycles, next fight slightly easier)"
- result_text: "You gut the lift controls for parts and leave the shaft dead. The lock-picks fetch a few Cycles, and the missing relay leaves a hole in the next client's coverage."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 20
- reward: none
- next_combat_overrides (new): next combat only, duration 1: `enemy_resistance = -1` (minimum 0).
- starts_combat: none
- map_edits: none

**3. Pay the toll on the lift's meter**
- label: "Pay the toll (-30 Cycles, next two fights easier)"
- result_text: "The meter takes your Cycles and prints a receipt: BREAD, CIRCUS, TERMS APPLY. The lift hums, and the arena staff on the next two floors pretend not to see you."
- cycle_cost: 30
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new): next 2 combats, duration 2: `enemy_hp_pct = -15` each, `player_free_nudge = +1` (a second free nudge on turn 1 only).
- starts_combat: none
- map_edits: none

**4. Take the stairs**
- label: "Take the stairs"
- result_text: "You climb the long way. Clean, slow and unremarkable."
- effects: none
- reward: none
- next_combat_overrides (new): none
- map_edits: none

## Design notes
- **The decision:** the first choice is a loan. The big discount (-30 % HP, Frozen start, phases revealed) is paid for by the next fight after it. The Frozen start and phase reveal are valuable only if the first fight is a dangerous one, and unknowable for the fight after. A player with low HP may refuse the second fight's +25 % damage, while a strong run may happily take it.
- **No dominant option:**
  - Choice 2 is a small safe edge (+20 Cycles is about two Router fights of income, GDD 11 placeholder) with only -1 resistance.
  - Choice 3 is the cleanest bonus but costs real shop money (30 Cycles is roughly a Firmware discount), and the per-fight discount is only half the loan's.
  - The free choice 4 keeps everything neutral. Choice 1 deals the most damage on the first fight but is the only option that can harm the run.
- **Determinism:** every override is a plain data field on a run-level `next_combat_overrides` queue (N16). Each entry has a count that decrements when a combat is created. The queue is saved with RunState and the preview shows the modified HP and statuses exactly, so previews equal results. No random input.
- **Stacking:** if the player meets other FUTURE events, overrides on the same combat add (HP percents sum, resistance clamps at 0). The queue order is first-come.
- **Dependencies:**
  - N16 (`next_combat_overrides`) is required, with no data-only fallback for the multi-combat queue.
  - Fallback: choices 2 and 4 could be built with only a one-combat override, or with existing effects (Cycles). The Frozen start uses the existing Freeze logic applied at combat creation.
  - Reveal phases uses R7's Chart Hidden toggle, which needs N5 and a `reveal_phases` flag. If N5 is not ready, drop it from choice 1.
- **Text keys:** `ev_aur_service_lift.title`, `.text`, `.c1`, `.c2`, `.c3`, `.c4` (labels and results); a HUD chip key `chip.next_fight_mod` ("Service Lift: -30 % HP, Frozen") so the player can see the pending modification on the map.
- **Tone:** the Lanista, patrons, clients and the VERDICT chit stay in-world. The speaker is a street voice commenting on the arena from below, which differs from corporate-voiced events.

## Q:
- Q: Should a pending override show on the map as a chip before the next combat starts, and should the +25 % punishment in choice 1 be hidden until it fires?
- Q: Should "the combat after" skip non-fight nodes only, and count Elite fights, or only the next Normal Router?
