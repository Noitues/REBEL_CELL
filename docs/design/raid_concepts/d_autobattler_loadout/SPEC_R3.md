# D: Auto-battler Loadout (round 3)

Lanes under the package, using `tools/raid_concepts/d3_lane_sim.py`. Each threat fights its declared target in its own
lane, with fixed lanes: Collector → HOME, Auditor → VAULT, Enforcer → PROXY.

## Pieces
- 3 of 5 are drafted.
- Slots sit on the three lane nodes, and the crew counts as a fourth piece.
- Sentry fires 3 × 2.
- Railgun 8 hits the highest-damage lane within 2 hops.
- Lanes tick together for 6 ticks.

The per-lane strips show every hit (diamond numbers) and every kill (a skull glyph). Of 540 plans, 10 are clean.

## Plans
- Bare: home scuffed; VAULT and PROXY TAKEN; patch 30.
- **Plan 1** (Turret on PROXY, ICE + Railgun on HOME, crew on VAULT): **CLEAN**, patch 15.
- Plan 2 (Turret + ICE on PROXY, Decoy on HOME, crew on VAULT): home −15, patch 30.

## Planning frame
The planning frame previews dropping the turret into PROXY's slot, and shows PROXY's lane outcome before and after.

## Playout
Hands-off; a playhead runs the strips.

Code: `concept_d3_loadout.py`.
