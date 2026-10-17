<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__06_future_aurelian; status ok; tokens in 5108 cache-write 0 cache-read 32585 out 3306; cost $0.025. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, HP percent vs R2 bands):** replaced the flat `enemy_hp_pct` with `enemy_hp_pct_post_band`. It applies after `hp_by_tier`, only to 1-phase normals and to mini-boss/Rack fights **with phase thresholds recomputed from the reduced max HP**. The result is clamped to at least 85% of the class band minimum (so −20% on a T3 normal lands at 44 × 0.85 = 37.4, i.e. 38, never lower). **Elites and bosses ignore HP overrides** (R2's 2-phase and 4–5-phase budgets are fixed); on those the fight gets a non-HP substitute (see choice 1 below). Values reduced to −20% (choice 1) and −10% (choice 3), as the critic suggested.
- **Issue 2 (BLOCKER, choice 3 free nudge undocumented):** the label now states everything: "−30 Cycles; next two fights: enemy −10% HP, +1 free nudge on turn 1". The duration is explicit (turn 1 of each of the two fights).
- **Issue 3 (MAJOR, hidden penalty):** the penalty is now in the label. The hidden-penalty Q is dropped, because hiding it would break preview = result. `player_free_nudge` is now listed as a field of its own and kept distinct from R4 enrage: the +25% damage is a flat modifier on that fight, not an enrage step, and it stacks multiplicatively with nothing (enrage adds its steps on top, additively per Q2 of the V2 questions).
- **Issue 4 (MAJOR, reinvented systems):** Frozen start is now `start_effects: FREEZE, target TARGET_WHEEL`. Resistance is `MODIFY_RESISTANCE` (amount −1, floor 0). `reveal_phases` is tagged "NEW: reveal flag" (an N16 flag, independent of Chart Hidden), with a fallback of dropping it.
- **Issue 5 (MAJOR, choices 2 and 3 weak or free):** choice 2 is now +10 Cycles, resistance −1 and **enemy +10% damage** on that fight (a real trade). Choice 3 stays the safe, pricier option. Because −10% HP twice plus a nudge for 30 Cycles is modest, it now also gives +1 free nudge as a clean upside rather than a hidden one.
- **Issue 6 (NIT, lore):** kept, because the designer asked for original names and the Aurelian lore is a placeholder; the speaker index `(1)` is correct.
- **Issue 7 (NIT, fallback):** stated: choices 2 and 4 can be built with a one-combat override plus the existing `ENEMY_RESISTANCE` rule modifier path.
- **Critic Qs:** the answers are folded in. Overrides apply to the next fight of the **same class as the one they target is not required**; they apply to the next N combats of any class, but HP overrides no-op on elites and bosses (stated in the label). Rack and boss fights count as combats, and HP overrides are ignored on bosses.

---

# ev_aur_service_lift: Service Lift

**Mechanic:** FUTURE, corporation aurelian, min_tier 2, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** Take a staff shortcut that softens the next fight, but the fight after it is rigged against you.

## TerminalEventData fields
- id: `ev_aur_service_lift`
- title: Service Lift
- speaker: STREET_MERC
- text: "Behind the concession stands there's a freight lift stenciled STAFF ONLY, TERMS APPLY. The panel says it drops straight past the next two bouts to the Lanista's own box seats. Somebody has taped a patron's VERDICT chit over the camera. Nothing in this arena is free, but the shaft is dark and nobody is watching."
- corporation_id: `aurelian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 1.0

## Choices

**1. Ride the lift to the box seats**
- label: "Ride to the box seats (next fight: enemy −20% HP, Frozen start, phases shown; the one after: enemy +25% damage, no free nudge on turn 1)"
- result_text: "You step out behind the Lanista's chair and rewire the bout sheet before anyone looks up. The first client is already limping. By the next bout the house has noticed the edit, and it bets against you."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new, N16), queue of two entries:
  - Entry 1 (next combat, duration 1): `enemy_hp_pct_post_band = −20` (normals, mini-bosses and Racks only; elites and bosses ignore it and take `start_effects: MODIFY_RESISTANCE −1` instead); `start_effects: FREEZE, TARGET_WHEEL`; `reveal_phases = true` (NEW: reveal flag; fallback: drop).
  - Entry 2 (the combat after, duration 1): `enemy_damage_pct = +25` (a flat modifier, separate from R4 enrage); `player_free_nudge_turn1 = false` (NEW field, listed here, shown in the preview).
- starts_combat: none
- map_edits: none

**2. Pry the access panel and take only the tools**
- label: "Strip the panel (+10 Cycles; next fight: enemy −1 resistance, enemy +10% damage)"
- result_text: "You gut the lift controls for parts and leave the shaft dead. The lock-picks fetch a few Cycles, and the missing relay leaves a hole in the next client's coverage. The client notices the missing relay too."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 10
- reward: none
- next_combat_overrides (new): next combat, duration 1: `start_effects: MODIFY_RESISTANCE −1` (floor 0); `enemy_damage_pct = +10`.
- starts_combat: none
- map_edits: none

**3. Pay the toll on the lift's meter**
- label: "Pay the toll (−30 Cycles; next two fights: enemy −10% HP, +1 free nudge on turn 1)"
- result_text: "The meter takes your Cycles and prints a receipt: BREAD, CIRCUS, TERMS APPLY. The lift hums, and the arena staff on the next two floors pretend not to see you."
- cycle_cost: 30
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new): next 2 combats, duration 2, each: `enemy_hp_pct_post_band = −10` (same class limits as choice 1); `player_free_nudge_turn1 = +1` (NEW field, turn 1 only).
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
- **HP rule (R2):** the override reduces max HP after `hp_by_tier`, clamped to 85% of the class band minimum. Phase floors (R3) use the reduced max HP. A T3 normal at 44–56 HP becomes 38–45 with −20%. Elites and bosses keep their authored HP, so their 2-phase and 4–5-phase budgets stay intact; they get a resistance cut instead.
- **The decision:** choice 1 is a loan: a strong first fight (HP cut, Frozen start, phases shown) against a hard second one. It is worth it if the first fight is the dangerous one and you can face a +25% damage fight without a turn-1 free nudge. Skip it at low HP.
- **No dominant option:**
  - Choice 2 pays 10 Cycles, about one Router fight of income (GDD 11 placeholder), against more incoming damage; the −1 resistance matters most against Meridian-style enemies.
  - Choice 3 is the safe, two-fight bonus and costs real shop money.
  - Choice 4 is neutral.
- **Determinism:** every override is plain data on a run-level queue saved with RunState. An entry's count decrements when a combat is created. The preview shows the modified HP, statuses and nudge count. No randomness.
- **Stacking:** HP percents add; resistance floors at 0; the 85% clamp applies once to the sum.
- **Dependencies:**
  - N16 is required, with no multi-combat fallback.
  - Choice 2 and a single-combat version of choice 4 can use existing effects (GAIN_CYCLES, MODIFY_RESISTANCE) plus the `ENEMY_RESISTANCE` rule path.
  - `reveal_phases` is a new N16 flag (it is not Chart Hidden from N5); if it is not ready, drop it from choice 1.
- **Text keys:** `ev_aur_service_lift.title`, `.text`, `.c1`–`.c4` (labels and results); the chip `chip.next_fight_mod` ("Service Lift: −20% HP, Frozen") shows a pending modification on the map.

## Q:
- Q: Should the +25% second-fight penalty in choice 1 reach elites and bosses (damage only), given HP overrides are ignored on them?
- Q: Should a pending override show as a map chip before the next combat starts (proposed: yes, per the preview rule)?
