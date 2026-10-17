<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__26_wheel_any; status ok; tokens in 6359 cache-write 0 cache-read 32007 out 2259; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_service_hatch: Service Hatch

**Mechanic:** WHEEL, corporation any, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Spin a wheel of shortcuts and spend HP, Heat or Cycles on nudges to steer it, or skip the hatch and take the long way.

## TerminalEventData fields
- id: `ev_service_hatch`
- title: Service Hatch
- speaker: STREET_MERC (1)
- text: "Maintenance hatch behind the rack, stenciled with a route number that doesn't exist on any map. Somebody scratched a dial into the lid, six notches, each marked in grease pencil. Old runner trick: crank it and see where the crawlspace dumps you. The dial sticks, though. You can lean on it, but it costs."
- corporation_id: `&""`
- min_tier: 2
- dispatch_clue: false
- foreshadows: `&""`
- weight: 0.8

## Choices

**1. Crank the dial** (opens the event wheel)
- label: "Crank the dial (event wheel)"
- result_text: "The crawlspace swallows you. Wherever it spits you out, that's where you are now."
- cycle_cost 0, hp_cost 0, effects: resolved by the wheel, reward: none
- (new) event_wheel: `wheel_hatch` (below)

**2. Pry the lid and read the wiring**
- label: "Salvage the dial mechanism (+15 Cycles)"
- result_text: "Brass and a little gold. The shortcut is gone, but the scrap isn't."
- cycle_cost 0, hp_cost 0
- effects: GAIN_CYCLES, CAMPAIGN, amount 15
- reward: none

**3. Take the long way**
- label: "Walk on (heal 4 HP)"
- result_text: "You take the stairs like a civilian and catch your breath."
- effects: HEAL, SELF, amount 4
- reward: none

## Event wheel (`wheel_hatch`)
Six slices on 30 ticks, uneven. Pointer is on any tick (R10). Sub-tick quality follows R11, and an outcome fires on the slice under the pointer. Quality does not scale outcomes, so only the slice matters.

| # | size_ticks | Outcome | Effects |
|---|---|---|---|
| 1 | 4 | **Dead end** | Lose 6 HP and +2 Heat: `MODIFY_HEAT` CAMPAIGN +2; hp_cost 6 |
| 2 | 7 | **Crawlspace** | Rest in the dark: HEAL SELF 8 |
| 3 | 5 | **Skip** | (new) `map_edits`: mark the next layer's fight nodes as bypassed; the player moves straight to the layer after it. The bypassed node gives no rewards and no Heat. |
| 4 | 4 | **Stash** | `GAIN_CYCLES` CAMPAIGN +30 |
| 5 | 6 | **Guard post** | (new) `starts_combat`: `patrol_unit` at current tier, no overrides, stake: win = +20 Cycles; flee not allowed |
| 6 | 4 | **Loose cable** | reward: one random common Firmware from the Router pool (drawn from the `events` stream) |

Sizes sum to 4+7+5+4+6+4 = 30. The safe slices (Crawlspace and Loose cable) are the bigger and the smaller of the middle ones, and the best prize, Skip, is only 5 wide.

- **Starting position:** a `events`-stream roll sets a start tick when the event opens. The result is a checkpoint, so reloading can't reroll it.
- **Nudge budget:** 2 free nudges of ±1 tick each, ring OUTER.
- **Extra nudges:** each costs the player's choice of 2 HP, or 1 Heat, or 8 Cycles, shown on the button. Max 6 extra.
- **Commit:** a "Lock it in" button resolves the slice under the pointer.
- **Preview:** the slice under the pointer is always named, and arrows show the outcome after a ±1 nudge. Preview equals result, because nothing random happens after the start tick.

## Design notes
- **Is cranking dominant?** Take the wheel at the starting tick, with no nudges: the expected outcome is mixed (size-weighted, 4/30 dead end, 11/30 safe or a small prize, 5/30 skip, 6/30 patrol fight). Option 3 is a sure 4 HP and option 2 a sure 15 Cycles, so the wheel needs to beat roughly 15 Cycles of value. Nudging toward Skip is worth about a node (~2 minutes) and is the best payoff, but each nudge past the free two costs about a small shop item's worth in whichever currency you pick.
- **Which currency to burn:** HP, Heat or Cycles. A healthy run pays HP, a rich run pays Cycles, a run near a Heat threshold (10 / 25 / 50) pays neither. This ties into the Heat band without a fixed answer.
- **Patrol Unit risk:** it is a T2+ normal (1 phase, 3–4 turns, ~44 HP at T2 per R2), so the worst case is a fair fight, not a death. Dead end loses 6 HP and 2 Heat, which hurts a wounded run most.
- **Skip uses `map_edits`:** keep this data-light. If N16 is late, a fallback is "heal 8 and +20 Cycles" for the Skip slice, which keeps the shape but loses the unique reward.
- **Economy:** the run budget is ~15 minutes and ~5 combats, so skipping one node saves about a fifth of that. Cycles are placeholders against GDD 11.
- **Text keys:** `EV_HATCH_TITLE`, `EV_HATCH_BODY`, `EV_HATCH_SLICE_1` through `EV_HATCH_SLICE_6`, `EV_HATCH_EXTRA_NUDGE_COST`.
- **Dependencies:** N17 (event wheel) and N16 (`map_edits`, `starts_combat`). The data-only fallback is a 3-choice event with fixed outcomes and no wheel (Skip becomes +20 Cycles).

Q: Should a Skip that bypasses a Rack-layer node also forfeit the Rack's Schematics, or should Racks be exempt?
Q: Should the extra-nudge cost be fixed to one currency per wheel to keep the UI simple, or is the player's choice worth the extra button?
