# Round 40: city unified (cars medium LOD, raid gifs re-run in the one city)

The transit view is skipped this round (the netrun agent is redoing it).

## Files
| File | What |
|---|---|
| `cars_lod.png` | Car LODs. **Medium** has changed: the box is now filled in its lane's colour, about 35 % translucent, with the same colour on the outline and the line. Far is still a dot; close is still the model. |
| `raid_gifs/` | Every raid interaction, re-run on the unified city model, using the latest locked version of each. Raid UI sources are rounds 21, 22 and 23. Raid world sources: round 23 slow and repair, round 22 unit health and icons v4, and the Heat spotlights. Each gif is 2 MB or less and uses a shared palette with dither, so saturation is kept. Contents are listed in `raid_gifs/index.md`, with a sheet at `raid_gifs/index.jpg`. |
| `scripts/` | All the scripts. |

## How the raid gifs reach the one city (compat layer)
The locked gif code (rounds 19 to 23) is written against round 19's 6-node layout. It was ported rather than rewritten:

- **`scripts/build40.py`**
  - Maps the six raid roles onto the real Meridian scope, from `content/corporations/meridian.tres`. The map uses CORE plus the five owned Sites nearest it, picked by a permutation fit to the round 19 screen layout.
  - Picks the three entry Sites nearest the targets.
  - Writes `layout40.json` with links and routes that follow the street polylines (they meander like the grid links), plus a camera framing the district.
- **Compat world = real × K (K = 2).** At that scale the round 19 decal sizes (sockets, rings, health fill, frost and lure) keep their locked proportions.
  - `raidui/layout.py` provides round 19's `layout` API from `layout40.json`.
  - The netdecal links and frost are measured by arc length along the street polyline.
  - The hard-coded round 19 crops and parking spots are mapped by a similarity fit: `screens21.M19B` and `M19P`.
- **`raidui/finish19.py` is now an adapter.** It renders through `post40.finish`, so every frame shows the one-city finish:
  - see-through buildings at 0.42 opacity, dark ×0.62;
  - lane dimming, the x-ray network, sky lanes, fog and rain.
- **`unified40.py` builds the district defences at the compat node spots**, scaled 1.7× (ICE LOCK spire, railgun, turret, sentry, decoy).
  - It also renders a `defmask` pass, so the defences stay opaque through the translucent buildings.
  - Units (`raidui/vehicles.py sprites`) are scaled 1.7× to match.

## Rebuild (from `scripts/`)
1. `python scope39.py`, then `python build40.py` (layout).
2. `python run40.py setup noice decoy` (Blender 5.2 headless).
3. Vehicles: `blender -b --factory-startup --python raidui/vehicles.py -- ../scratch/bl sprites`, with `NET36=net_scope.json`.
4. In `raidui/`, with `NET36=net_scope.json`:
   - `python -c "import screens21 as S; S.build_gifs()"`;
   - then `screens22.build()`, then `screens23.build()` (these overwrite the redone gifs in order);
   - then `python extra40.py`, and finally `python index40.py`.
   - `GIF_ONLY=08,14` rebuilds only those gifs.
5. Cars: `run39.py` renders plus `screens39.py` cars_lod (post40 medium box).

Seeded throughout. The defence and unit scale (1.7) and K = 2 are concept numbers. In Godot the decals are sized in world metres.
