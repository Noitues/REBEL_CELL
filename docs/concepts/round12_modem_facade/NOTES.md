# Round 12 notes: MODEM facade (v2, after orchestrator review)

## What's here
- `f1_*`, `f2_*`, `f3_*` `{rain,day,night}.png`: 1920x1080, same camera and layout for all nine.
- `compare.jpg`: 3x3 grid (rows are options, columns are states).
- `with_ui_mock.png`: F1 RAIN with ghost panels (MICROCHIPS / CARD BUILDER / SHOP NOTES / INVENTORY).
- `scripts/`: `scene.py` + `flib.py` (Blender 5.2 headless: geometry, toon material, lights, beauty + aux
  passes), `post.py` (sky, haze, ink, bloom, sign reflections on the wet floor, steam, rain),
  `render_one.sh`, `run_all.sh`, `sheets.py`, `ui_mock.py`.
  Run `sh scripts/run_all.sh`, then `python scripts/sheets.py` and `python scripts/ui_mock.py`. It takes
  about 2.5 minutes and is seeded.

## v2 layout (follows ref6 panel 05)
- Eye 6 m across the street, one-point perspective, vanishing point at about x 636 (the alley).
- **Shop tower** (left): MODEM sign at x 52-212, y 26-688. Below it, a recessed **foyer** with cyan
  display screens, a lit door, a soffit strip, a lone figure and a wet floor.
- **Alley** (x ~520-800): a narrow passage straight ahead. It has a lit stair rising away, a stair that
  turns right behind the front building, a door light at the landing, hanging cables, glyph signs,
  steam, puddles and depth haze.
- **Front building** (smaller, right of the alley, x ~770-1510): roll shutters (one half-open with
  warm light), faded unreadable posters, AC units, pipes, cables, a small holo ad, ledge lights and
  rooftop clutter. Its alley-side wall takes the pink spill.
- **Behind**: the shop's low wing, a calm, darker row of buildings with a street lamp, then layered
  towers with lit windows, a distant holo billboard and haze. In front, wet asphalt and a kerb carry
  the long sign reflections.
- **DAY**: low sun from the right. The front building throws its shadow across the alley mouth, the
  pavement and the lower shop facade, and the fire escape shadows land on the brick.

## Recommendation: F1 Tenement
Pink spill on brick shows the sign best, and the zig-zag fire escape matches the alley stair. Its front
building is the calmest under the panels. F2 Garage has the most identity (hazard beam, roll
shutter, container stack) but is louder. F3 Kiosk stack is the busiest next to the sign.

## Weakest parts
- **Weak day shadow.** The front building is right of the alley, so its shadow reaches only the
  lower-right of the shop facade. It isn't one big wedge across it.
- **Lost F2 cladding.** The corrugated stripes are finer than the facet size, so the F2 cladding reads
  as flat.
- **Faint billboard.** The distant holo billboard is only a hint behind the haze.
