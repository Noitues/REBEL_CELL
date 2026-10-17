<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__26_wheel_any; status ok; tokens in 5333 cache-write 0 cache-read 32585 out 2937; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, determinism):** Start tick and the slice-6 reward are both drawn once, on event open, from the `events` RNG stream, then checkpointed together. Nothing random happens after open. Slice 6 now shows its Firmware on the slice, so the preview equals the result. Choice 1 now shows the start tick before the player commits (critic Q1: yes, because informed choice makes option 1 vs 2 a real decision).
- **Issue 2 (BLOCKER, `starts_combat`):** Slice 5 now lists the enemy, tier, overrides (none), the win stake, the loss rule and HP carryover. "Flee not allowed" is explained: the guard post is a forced fight, and the other slices are the escapes. The enemy HP is sourced from `patrol_unit`'s authored `hp_by_tier` (N2), not a band midpoint. The R2 normal band is 44-56 at T3 and 34-44 at T2; the exact value is whatever the enemy file authors.
- **Issue 3 (MAJOR, spell out outcomes):** Slice 1 is now `DEAL_DAMAGE SELF 6` plus `MODIFY_HEAT +2`. Slice 3 has precise `map_edits`: Rack nodes are exempt, and the final layer converts the slice to Stash.
- **Issue 4 (MAJOR, dominated choice):** Option 2 pays +10 Cycles and its label now matches its body. Option 3 heals 8 and gives -1 Heat. Stash pays +25.
- **Issue 5 (MAJOR, nudge economy):** One currency per wheel, 2 HP per extra nudge, max 3 extra (worst case 6 HP). This also resolves critic Q2 in the v1 and the v1 currency Q (fixed, to keep the UI simple). The Heat-band tension kept in v1 is dropped because there is now one currency; the Heat tension moves to the option 3 -1 Heat and slice 1 +2 Heat.
- **Issue 6 (NIT):** Removed the R11 sub-tick line and stated that pointer position inside a slice is irrelevant.
- **Issue 7 (NIT):** Speaker is `STREET_MERC` only.
- **Critic Q2 (Skip removing Heat):** Kept as is, because a bypassed node simply never happens. This is the player's reward for the Skip slice, which is the narrowest at 5 ticks.

# ev_service_hatch: Service Hatch

**Mechanic:** WHEEL, corporation any, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Crank a hatch dial of outcomes and pay 2 HP per extra nudge to steer it, or take a sure payout or a rest.

## TerminalEventData fields
- id: `ev_service_hatch`
- title: Service Hatch
- speaker: STREET_MERC
- text: "Maintenance hatch behind the rack, stenciled with a route number that exists on no map. Somebody scratched a dial into the lid, six notches, each marked in grease pencil. Old runner trick: crank it and see where the crawlspace dumps you. The dial sticks, though. You can lean on it, but it costs blood."
- corporation_id: `&""`
- min_tier: 2
- dispatch_clue: false
- foreshadows: `&""`
- weight: 0.8

## Choices

**1. Crank the dial**
- label: "Crank the dial (event wheel, start tick shown)"
- result_text: "The crawlspace swallows you. Wherever it spits you out, that's where you are now."
- cycle_cost 0, hp_cost 0, effects: resolved by the wheel, reward: none
- (new) event_wheel: `wheel_hatch` (below). N17.

**2. Pry the lid and sell the brass**
- label: "Salvage the dial (+10 Cycles)"
- result_text: "Brass and a little gold. The shortcut is gone, but the scrap isn't."
- cycle_cost 0, hp_cost 0
- effects: GAIN_CYCLES, CAMPAIGN, amount 10
- reward: none

**3. Take the stairs**
- label: "Walk on (heal 8 HP, -1 Heat)"
- result_text: "You take the stairs like a civilian, breathe, and keep your head down."
- effects: HEAL, SELF, amount 8 (FLAT); MODIFY_HEAT, CAMPAIGN, amount -1
- reward: none

## Event wheel (`wheel_hatch`)
Six slices on 30 ticks, uneven (R10, R11). Only the slice under the pointer matters; the position within the slice is irrelevant. The outcome fires when the player commits.

| # | size_ticks | Outcome | Effects |
|---|---|---|---|
| 1 | 4 | **Dead end** | DEAL_DAMAGE SELF 6; MODIFY_HEAT CAMPAIGN +2 |
| 2 | 7 | **Crawlspace** | HEAL SELF 8 (FLAT) |
| 3 | 5 | **Skip** | (new) `map_edits`: remove the fight nodes of the next layer from the reachable set and connect the current node to every node of layer+1. Server Rack nodes are exempt. If the next layer is the final layer, this slice resolves as Stash. The bypassed nodes give no rewards and no Heat. |
| 4 | 4 | **Stash** | GAIN_CYCLES CAMPAIGN +25 |
| 5 | 6 | **Guard post** | (new) `starts_combat`: enemy `patrol_unit`, tier = current, `combat_overrides` none. Stake: win = +20 Cycles; loss follows the normal death rules. HP carries over. No flee. |
| 6 | 4 | **Loose cable** | reward: the Firmware drawn at open (shown on the slice), a common Firmware from the Router pool |

Sizes: 4 + 7 + 5 + 4 + 6 + 4 = 30.

- **Open:** the start tick and the slice-6 Firmware are drawn once from the `events` stream, then checkpointed together. Reloading cannot reroll either.
- **Nudge budget:** 2 free nudges of ±1 tick, OUTER ring.
- **Extra nudges:** 2 HP each, max 3 extra (worst case 6 HP). The cost is shown on the button.
- **Commit:** "Lock it in" resolves the slice under the pointer.
- **Preview:** the slice under the pointer is always named, with arrows showing the result of a ±1 nudge. Nothing random happens after open, so the preview equals the result.

## Design notes
- **No dominant option:** a start tick near Stash (+25) beats option 2 (+10) at no cost, while a start tick near Dead end or Guard post gives the player a reason to pay nudges or walk away. Option 3 competes when hurt or hot (8 HP and -1 Heat vs the wheel's 6 HP and +2 Heat downside). Because the start tick is shown, choice 1 is an informed bet.
- **Spend vs prize:** the free two nudges reach adjacent slices. Reaching Skip (the best prize, about a node, ~2 minutes of a ~15-minute run) from a bad start can cost up to 6 HP. That is a bad trade only for a wounded run, which is the tension.
- **Guard post:** `patrol_unit` is a 1-phase normal (3-4 turns), with HP from its authored `hp_by_tier` (N2). It is a fair fight, and the player can nudge away from it.
- **Skip:** exempting Racks means banking and Exploits are never bypassed. A Skip that removes Elite Router nodes also removes their +1 Heat, which is accepted.
- **Text keys:** `EV_HATCH_TITLE`, `EV_HATCH_BODY`, `EV_HATCH_SLICE_1` to `EV_HATCH_SLICE_6`, `EV_HATCH_EXTRA_NUDGE_COST`.
- **Dependencies:** N17 (event wheel), N16 (`map_edits`, `starts_combat`). Data-only fallback: a 3-choice event with fixed outcomes and no wheel (Skip becomes +20 Cycles).

Q: Should Skip also bypass Terminal and Mainframe nodes on the next layer, or only fight nodes as drafted?
Q: Should the start tick be re-drawn if the player leaves the event and reopens it, or locked for the run?
