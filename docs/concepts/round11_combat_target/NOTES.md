# Round 11: combat over the target building

This round applies the designer's five notes on round 10. Everything else carries over from round 10:
- Screens & Data slices, with the glyph and value block kept upright;
- the V2 telemetry border;
- sticker cards, the HUD, and the overlay kit;
- Breaker vs The Manifest (with VIRUS and PROXY mocked into Breaker's wheel, as in round 10).

## Files
| File | What it shows |
|---|---|
| `slices_r11.png` | The new EVADE and AFFLICT slices: hero tiles, r = 150 and r = 60 wheels, and greyscale. The library holds the reserved BURN/DISSOLVE effect, two mask backdrops and the reserved vial icon. |
| `target_building_night.png`, `target_building_day.png` | The backdrop alone: the Freight Ziggurat at Lane 15. |
| `combat_boss_night.png`, `combat_boss_day.png` | Breaker vs The Manifest. |
| `combat_regular_night.png` | Breaker vs Route Optimizer, in front of a smaller Meridian container depot. |
| `contact_sheet.jpg` | All of the above. |

The scripts are in `scripts/`. Renders are cached in `scratch/`, which git ignores. Build order:
1. `blender -b --factory-startup --python target_scene.py -- boss|regular <scratch/bl>` (about 2 minutes each).
2. `python backdrop.py`
3. `python make_slices11.py`
4. `python make_combat.py all`

## 1. The new backdrop: a close-up of the target
**The building is authored in Blender 5.2 (headless, Eevee), not an upscale of the city render.** `target_scene.py` builds the Freight Ziggurat, following `round5_city_overview/hq_crops.png`:
- five stepped orange tiers, each with pilasters, an amber window band, a neon lip, and cargo on its terrace;
- loading docks with hazard sills;
- MERIDIAN FREIGHT and LANE 15 signage;
- the gantry crane over it: hazard-striped beams, braced legs, a trolley, a hanging container and red beacons;
- a plaza with a ring light and lamps, flanking container stacks, and trucks on the avenue.

The surrounding blocks are procedural, with windows, roof neon and antennas.

**Style: Cv2 gritty low-poly with E cel shading.**
- Every wall is split into jittered triangles with a tone jitter on each triangle.
- Lighting is 3 hard toon bands (cool shadows, warm lit faces), with separate day and night palettes.

`backdrop.py` then adds, in post:
- wobbly ink lines, found from part-id, normal and depth edges, lighter with distance;
- painted grime and streaks;
- bloom plus neon light spill onto walls and streets;
- depth haze and rain.

**No district labels.**

**Composition.**
- The ziggurat sits in the gap between the wheels, with the crane across the top of the screen.
- Blocks that project behind a wheel are kept low, dark and sparsely lit. The script checks this per building with the camera projection.
- Taller, brighter towers frame the edges and top.
- In combat, each wheel's area is softened (blurred) and darkened by about 55%, and there are darker bands under the hand and the top bar.

**The regular fight** uses a smaller target: a Meridian container depot. It has a sawtooth-roof warehouse, the DEPOT 15 sign, a stacked yard, a yard gantry and floodlight masts.

## 2–4. Slices
- **EVADE (PROXY).**
  - Icon: round 6's double chevron.
  - Screen: a road-sign detour. A bold white route arrow runs up the lane beside the value block and turns hard 90° along the top band. The packet takes the turn with afterimages. A striped "road closed" barrier marks the old road.
  - This replaces the zigzag hops, which read as lightning.
- **AFFLICT (VIRUS).** Round 10's ooze effect (option B) with the biohazard icon (option C).
- **Library (kept, not in use).**
  - The blotch effect that eats the hex dump, reserved for BURN / TORCH / DISSOLVE programs.
  - Two Guy Fawkes-style mask backdrops, program TBD:
    - one large faint mask with a glitch band and RGB split;
    - an anonymous crowd of masks with one lit.
  - The poison vial, as a reserved icon.

## 5. Grease pencil
Strokes are now near-opaque (alpha 0.96), about 1.7× thicker and waxy. Each stroke has:
- a rough wax edge, small dropouts and a lighter sheen line;
- saturated colours: plan yellow #FFE200, threat red #FF1C2C;
- a dark under-shadow, so it reads on both day and night backdrops.

There are still 5 overlay marks. None of them covers a slice value or an HP number.

## Open issues
- **The day backdrop is warm and hazy.** The toon-lit orange ziggurat against pale towers is busier than at night, and the wheels rely on the darkened pools. The night shot is the stronger pairing.
- **The boss wheel and banner cover the right third of the ziggurat and the crane's right leg.** The centre gap shows the building's spine (signage, tiers, hanging container). A smaller boss offset, or a camera yawed about 10° left, would show more of it.
- **In the regular shot, the DEPOT 15 sign sits behind the yard gantry and the aim arrow.**
- **Hand cards still sit partly off the bottom edge**, as in round 10.
