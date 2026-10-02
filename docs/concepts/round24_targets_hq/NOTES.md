# Round 24: target buildings for every corp, and HQ updates on the city map

Locked rules followed:
- The combat backdrop is a close-up of the building under attack, built with the round 11 ziggurat pipeline.
- The approved cool day (round 11b) is the day look for every corp.
- Heat on combat is backdrop-only (none is shown here).

Earlier rounds are untouched. `scratch/` is git-ignored and cleared.

## Files
| File | What it shows |
|---|---|
| `target_<corp>_boss_night.png`, `target_<corp>_boss_day.png` | Each corp's boss site at night and in cool day: Solace, Halcyon, Orbital, REBEL_CELL. |
| `target_<corp>_regular_night.png` | Each corp's smaller regular site, at night. |
| `combat_<corp>.png` | The boss fight on that site. It uses the locked D4 player wheel, the round 18 corp boss wheel (tier III, phase 1), the HUD, the sticker cards, and the round 22 SEND IT sticker over EXECUTE. |
| `targets_compare.jpg` | Every corp's targets side by side. Meridian's come from round 11. |
| `hq_updates.png` | Before (round 6) and after (round 24) for each HQ. |
| `city_night_hq_v2.png` | The full city night view with the new HQs. Same framing and labels as `round6_city_restyle/views/restyle_night_full.png`. |

## Target buildings
Each scene is built in Blender 5.2 (headless) by `scripts/target_corps.py`, which extends the round 11 `target_scene.py`. The hero buildings are in `scripts/heroes24.py`. A style pass, `scripts/backdrop24.py`, then adds:
- ink, grime and streaks;
- bloom and light spill;
- depth haze and rain.

There are no baked labels; only diegetic signage on the buildings. Blocks that fall behind a wheel are kept low, dark and sparsely lit. Each corp also has:
- its own street neon colours;
- its own district shapes: Solace cylinders, Halcyon setbacks, Orbital needles;
- a tint on the toon lighting.

| Corp | Boss site | Regular site |
|---|---|---|
| **Solace** (lime, biotech) | **Renewal Engine**: a lime bioreactor capsule in a ribbed glass cage, wound with the white/lime double helix (echoes the HQ). Six implant pods piped in, a CONTINUUM sign, greenhouse cell domes, ambulances. | **Implant Provisioning Hub**: a clinic block with three capsule tanks, a lime cross pylon, cell domes and ambulances. |
| **Halcyon** (violet/amber, civic) | **The Civic Core**: a four-tier colonnaded civic ziggurat with amber window bands. The amber EYE crest sits on an apex pylon. Radar dishes, police cars on the plaza. | **Enforcement precinct**: a colonnaded block with an eye crest, a radar dish, police cars and an amber barrier line. |
| **Orbital** (ice-white/cyan, space) | **The Commons Array**: a lattice uplink mast with cyan status rings and a beam into the sky. Three big dishes and a ring of small ones, on a star-map plaza. | **Ground Station Alpha**: an ops block with roof dishes, a big pedestal dish, a radome and a fence. |
| **REBEL_CELL** (red, corrupted) | **DISPATCH**: a server stack of rack segments shoved out of line, with red vents and the FIST crest. An antenna crown, hijacked Cell relays cabled to the stack, a glitched plaza. | **Relay Rooftop**: a tenement roof with a jury-rigged relay mast, red rings, cables, a fist tag and spray strips. |

**Build** (from `scripts/`):
1. `blender -b --factory-startup --python target_corps.py -- <corp>_<boss|regular> <abs scratch/bl>` (about 2 minutes each).
2. `python backdrop24.py`
3. `python wheels_r18/render_bosses24.py`, `python wheels_r18/dump_boss_slots24.py` and `python combat_r23/render_player24.py`
4. `python combat_r23/make_combat24.py`
5. `python make_compare24.py`

## HQ updates
`scripts/city_hq_v2.py` edits the game's exported layout in memory; `city_layout.json` itself is read-only. The new parts are added as the game's own primitive kinds, right after each HQ's own parts. The round 6 restyler then draws them in the same order, with the same facets, toon bands, ink and neon.

| HQ | Change |
|---|---|
| **Meridian** | Two ship-to-shore gantry cranes straddle the ziggurat's front edges, to match its crest (a crane hook and a container). Each has portal legs, a long hazard-striped boom, an A-frame with tie rods, a trolley with a hanging container, and red boom-tip beacons. |
| **Orbital** | A LAUNCH PAD on the front of the tether platform: a pad with a ring light, a rocket (booster, upper stage, nose cone, fins, cyan bands), a service gantry with two swing arms and a red beacon, and exhaust steam. The HQ's neon moves to ice white. |
| **Halcyon** | The halo is removed. The EYE crest replaces it: an amber almond outline, a dark socket, an amber iris, a pupil, a glint and lashes. The HALCYON roof sign is lifted clear of the eye. |
| **Solace** | The Double Helix already matches the helix crest. Its neon moves from mint to the round 17 lime. |
| **REBEL_CELL** | No tower. Its fist-shaped roads already match the fist crest, so it is unchanged. |

## Weakest parts / open
- **Bright heroes between the wheels.** Solace's reactor and Halcyon's eye are the brightest things in the gap between the wheels (both were toned down once). The slice values still read, but if they compete, dim both one more step.
- **Orbital's launch pad is small in the full city view.** It reads in the `hq_updates.png` crop. The big ORBITAL district label covers part of it, which is a round 6 label position.
- **District colours on the city map are still the round 6 palette**, so Solace is teal-green and Orbital blue. Only the HQs moved to the round 17 palette. If the districts should follow, it needs a territory-colour pass.
- **Regulars use the same street grid as the bosses**, so the foreground is an empty plaza. The hand of cards covers most of it in combat.
