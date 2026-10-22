# Raid concepts (raid design lab, 2026-10-22)

Six radically different raid designs, all drawn against **one shared scenario** so they can be compared:

- **Trigger.** The Cell's Heat goes 49 → 51 and crosses the MAJOR threshold at 50. Solace queues a raid.
- **When.** The raid lands when the player next returns to HQ (between netruns). Concept E moves it two netruns out.
- **Network.**
  - Home Server 50.
  - Firewall Relay 30, with a built-in 3-damage gun.
  - Vault Terminal 20.
  - Safehouse 20, with a Breaker stationed.
  - Relay 15.
  - Proxy Relay 15.
- **Corp entries.** Two Solace Sites: Clinic (north-east, next to Relay) and Depot (south-east, next to Proxy).
- **Threats** (A.5 values):

  | Threat | Integrity | Damage | Speed | Routing | Silhouette |
  |---|---|---|---|---|---|
  | Collector | 12 | 5 | 1 | shortest route to home | hook-claw box |
  | Auditor | 8 | 3 | 2 | richest node (Vault) | eye diamond |
  | Enforcer | 25 | 9 | 1 | weakest node (Proxy) | spiked block |

- **Armory.** Turret (4 damage, reach 1), ICE Lock (holds 2 steps), Decoy (pulls threats), and the Breaker operative.

## Shared constraints

**Hands-off execution.** Every concept is plan → commit → **zero-input autoplay**. The designer intends execution to feel like
an auto-battler. Only speed (1x/2x/4x) and skip are available while a raid plays.

**Visual language** (low fidelity, the same in every mockup):

| Element | Look |
|---|---|
| Threats, threat routes, corp sites | cobalt `#3D6BFF` (designer ruling) |
| The Cell | yellow |
| Damage | red |
| HOLDS | teal check |
| DOWN | white bolt on a grey node |
| TAKEN | cobalt flag and a red grease-pencil X (D28) |
| Integrity | pips; projected loss is shown as red striped pips |

The verdict words follow D28: CELL HOLDS / BREACHED, plus CLEAN DEFENSE where D27's clean case applies.

## Layout

| Folder | Concept | Reference family |
|---|---|---|
| `a_telegraph/` | Exact whole-raid telegraph on the network, step scrubber | Into the Breach |
| `b_siege_lanes/` | Routes as lanes, wave flags, HP ledger per tick | Kingdom Rush, Thronefall, Arknights, Defense Grid 2 |
| `c_strength_duel/` | Siege banner per node, ATK vs DEF with itemised modifiers | Civilization VI / VII |
| `d_autobattler_loadout/` | Lineup match per lane, slots and synergies, tick sim strip | Super Auto Pets, Backpack Battles, The Bazaar, TFT |
| `e_countdown_allocation/` | Countdown over netruns, gauges with notches, hard calls | Frostpunk |
| `f_plan_ledger/` | Threat × step ledger, guaranteed totals row, sign orders | (plan board / spreadsheet) |

Each concept folder holds:
- `SPEC.md`;
- `<round>/mockups/1_warning … 5_aftermath.png`;
- `<round>/scrambled/` (every letter replaced, digits kept);
- `<round>/sheet.jpg` and `sheet_scrambled.jpg`;
- the critic's review for that round.

Mockups are rendered by `tools/raid_concepts/render_all.py`, using PIL and the shared kit `rc_draw.py`.

## Round 2 (2026-10-22)
Each concept folder has `SPEC_R2.md`, the current rules, which supersede `SPEC.md` where they differ. Its frames are under `r2/`.

- **Numbers come from code, not hand-drawn.**
  - **A, B and F.** All numbers come from `tools/raid_concepts/sim.py`, a small Python mirror of
    `scripts/core/raid_resolver.gd` (move, hold, fire, damage, cascade, take; step cap 30), run on the shared scenario.
    The plans run are:

    | Plan | Assets | Result |
    |---|---|---|
    | **BARE** | none | home −20, 3 DOWN, 1 TAKEN |
    | **DECOY ONLY** | Decoy on Firewall | home −12, nothing lost |
    | **LURE** | turret + ICE on home, Decoy on Firewall | home −9, nothing lost |
    | **SHIELD** | turret + ICE on home, Decoy on Proxy | home 0, 2 DOWN, 2 TAKEN |

  - **C, D and E** have their own rules. A rule function in their module computes every number they show.
- **SCUFFED** is a new mark: a teal check with a red corner and `-N`, for a node that held but lost integrity.
- **Shared kit:**
  - a countdown dial;
  - the Heat → raid "why" chain (51 > 50);
  - two-number threat chips with a route glyph (house = shortest to home, coin = richest node, cracked shield = weakest node);
  - asset cards with glyph stats;
  - loss icons inside the verdict stamp.
- **Finding: no clean defense in this scenario.** Under today's rules, none of the 2058 placements from this Armory
  gives one. The Enforcer always reaches a node or home. See RECOMMENDATION.md.
