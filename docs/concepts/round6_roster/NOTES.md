# Round 6: the roster in the Screens & Data style (family C)

Every wheel uses C's frame:
- a per-slice CRT bezel with a hairline and power LED;
- polar-UV screens, barrel bulge, scanlines and phosphor glow;
- a big white glyph and value on a darkened read plate.

Only the screen content changes from wheel to wheel.

All slice lists, pointers, orbits, resistance, hub cores, inner rings, drone spawns and boss
phases are read live from `content/` by `scripts/tresdata.py`. That is a read-only `.tres`
parser. Real wheels are **6 slices × 5 ticks (60°)**, so every slice uses C's wide layout, with
the glyph beside the value.

## Changes to C's programs (per the designer's verdict)

| Program | Change |
|---|---|
| SANDBOX | **Replaced** by A's guard-ring PCB, boxed in, inside the C screen: a cross-hatched ground plane, a bold guard-ring trace following the screen edge, stitching vias every 13 px (lit in sequence), and white corner brackets. It reads at r = 100. |
| PROXY | **Bolder**. The live route has a thick glowing underlay, 4.5 px marching dashes and arrowheads, with large lit nodes. The abandoned route stays visible as a broken red trace with an X. |
| VIRUS | **Toned down**. Infected-block brightness is now 0.16–0.46 (was 0.3–0.8), the infection front is muted lavender instead of white, and pink outliers are rarer and dimmer. |
| Others | Unchanged. |

Special enemy slices get their own glyphs:
- Tariff: a receipt with a coin; it shows its RAM drain (3).
- Citation: a punched ticket with "!".
- Solar Flare: a sun with separated rays.
- Dose: a capsule.

Rule chips sit under the value: `+1 RES` (inertia) and `-1 RAM` / `-2 RAM` (drain).

## Operatives (`op_<class>.png`, `operatives_sheet.png` at r = 220)

Each class gets:
- a bezel ornament;
- the matching motif on its hub-ring rim;
- its accent colour;
- a class mark in the hub;
- the hub core name;
- its rank-1 inner ring of 3 segments (between the slices and the hub), each with a segment glyph and label.

Each alternative reuses its base's motif and adds one thing.

| Class | Bezel / hub ring | Inner ring (content) |
|---|---|---|
| Breaker | Riveted plates (pink) | x2 / PIERCE / BLANK |
| Wrecker (alt) | The same plates, plus **welded seams and dents** (orange) | x2 / PIERCE / BLANK |
| Ghost | **Flickering translucent** rim, broken neon dashes (cyan) | PIERCE / x2 / ECHO |
| Phantom (alt) | Ghost's flicker, plus an **after-image double rim** (violet + cyan) | PIERCE / x2 / ECHO |
| Rigger | **Cable-wrapped** rim with 4 plugs (green) | ACCEL / x2 / ECHO |
| Overclocker (alt) | Rigger's wrap, plus **vented fins** with amber-hot tips | ACCEL / x2 / ECHO |
| Botnet | **Orbiting dot ring**, plus 3 docked drones (Swarm Core, max 3) | ECHO / CORRUPT / x2 |
| Hivemind (alt) | Botnet's dots linked into a **hex lattice**, plus 4 drones (Hive Core, max 4) | ECHO / CORRUPT / x2 |

Breaker and Wrecker share a starting wheel in content, and so do Ghost/Phantom, Rigger/Overclocker
and Botnet/Hivemind. Only the frame, the hub and the drones set each pair apart.

Each op file also shows:
- the r = 100 small variant;
- a greyscale hero;
- the hub core text;
- the segment rules;
- the slice chips.

## Enemies (`enemies_<corp>.png`, `enemies_sheet.jpg`)

D's corporate materials now sit inside C's screen frames. Every slice of a corporation uses one
skin. Type shows through the glyph, a type-colour hairline rim and a 3.5 px type tab along the outer edge.

| Corp | Screen skin | Bezel |
|---|---|---|
| Meridian | Corrugated container steel, a stencilled `MRDU` code, a gross/tare plate, a barcode sticker with a laser line | Hazard stripes, 30 notched teeth |
| Solace | Frosted teal glass, dividing cells, a DNA helix on the outer band, an ECG on the inner band | White porcelain, mint vial capsules, a glass glow ring |
| Halcyon | Indigo blueprint with 12/48 grids, civic rings, paving tiles, `SEC-xx / H-CIV` annotations | Violet colonnade, a pale trim, a halo arc |
| Orbital | **Brighter than D's**: lit nebula, denser and bigger stars with spikes, a constellation, orbits, a satellite, solar-panel band | Azimuth ring with labels from 000 to 330 |
| REBEL_CELL | The Cell's own PCB, corrupted: red traces, player-colour fringes, dead pixels, tears, an inverted hex | Broken, offset black-red segments with hex rivets |

Picks, preferring enemies whose mechanics show on the wheel:

| Corp | Regulars | Elite |
|---|---|---|
| Meridian | Route Optimizer (2 readers: 0 / 15), Drone Dispatcher (2 courier drones) | Last-Mile Enforcer (orbit +2, escort drone) |
| Solace | Care Swarm (3 care drones), Compliance Officer (hub lock, RES 3) | Recall Unit (orbit +2, RES 1) |
| Halcyon | Transit Controller (2 readers, orbit +1), Permit Office (2 civic drones) | Zoning Board (orbit +2, drone) |
| Orbital | Tracking Station (2 readers), Weather Satellite (orbit +4) | Geostationary Guard (orbit +3, drone) |
| REBEL_CELL | Cell Informant (orbit +3), Dead Drop (2 echo drones) | Mirror (`rc_template_elite`: a corrupted copy of the Breaker wheel, 2 readers, RES 1) |

How the mechanics are drawn:
- **Extra pointers** are numbered needles (1, 2, 3).
- **Orbit** is a dashed arc with an arrowhead and a `+N` label, ending at a ghost-outline pointer that marks the next position.
- **Drones** are docked CRT tokens on a tether. Each has its name, a drone glyph and a green HP pill.
- **Resistance** is a hex `R n` badge on the hub, labelled `HUB LOCK` for Compliance Lock.

## Bosses (`boss_<id>.png`, `bosses_sheet.jpg`)

Bosses are drawn at 120% of regular wheels. Each has:
- a heavier bezel: a second outer band with crown studs, and a doubled colonnade for Halcyon;
- a nameplate banner hung on chains;
- phase pips on the HP arc at 66% (P2) and 33% (P3).

The HP arc fills from the right, so the pips sit where each phase triggers. Phase 2 is the
content's first `BossPhaseData`. Its pointers, orbit, wheel override and spawns are all applied.

| Boss | Phase 1 signature | Phase 2 |
|---|---|---|
| The Manifest | Manifest board (`PKG / LANE`) and a red routing laser through every slice | PEAK SEASON: hazard band, red-hot tint, a second laser lane, 2 readers |
| Renewal Engine | Giant heartbeat, and every screen counts down `RENEWS IN 00:xx` | PAYMENT OVERDUE: infected magenta cells, erratic ECG, 2 readers |
| The Civic Core | Gold counter-flow on the civic rings, lit district blocks | STATE OF EMERGENCY: red grid, siren stripes, 3 readers (0 / 10 / 20) |
| The Commons Array | A gold constellation across the star maps | SOLAR FLARE whiteout sweeps the screens, 2 readers orbiting +4 |
| DISPATCH | Order log (`> ORDER 0x11 ISSUED`) over the corrupted Cell board | Runs **your** programs: each screen shows the player's C program, red-shifted and torn. Wheel override (Citation, Solar Flare), 2 readers |

## Small size and accessibility
- **Small size.** Below about r = 120 every wheel uses C's small variant: glyph ×1.45, value ×1.15,
  texture gain 0.55, read plate 0.85, corp skin gain 0.6. See `contact_sheet.jpg`, where wheels are
  at r = 100 and bosses at r = 120.
- **Greyscale.** Type reads from the glyph alone (see the greyscale panel in each `op_*.png`). The white glyph and value with a dark outline carry the contrast.

## Assumptions to confirm
- **Values I chose.** Tariff shows its RAM drain (3) as its value. Citation, Dose and Solar Flare have no number (their `base_output` is 0).
- **Drawing choices.**
  - Slot 0 is drawn centred under pointer tick 0.
  - Ring segment 0 is centred at the top.
  - Every possible drone is shown docked (`max_active`).
  - Botnet and Hivemind show the drone caps of their hub cores.
- **Mirror.** It has no `corporation_id`, so it uses the REBEL_CELL skin with a Breaker mark.

## Build in Godot 4.7
This is the same shader as round 5 C (see `round5_slices/s_c_screen_data/NOTES.md`). It adds:
- a `skin_id` uniform: player, or one of the 5 corps;
- `boss_phase`;
- `type_color`, for the hairline and tab;
- per-corp atlas cells for the materials.

The class bezel, hub-ring rim, pointers, orbit arc, drone tokens and badges are separate
`Node2D` layers above the wheel, driven by the same content data (`WheelData.pointer_ticks`,
`pointer_orbit_per_turn`, `passive_resistance`, `EnemyData.spawns`, `BossPhaseData`).

## Files
- **Deliverables:** `op_*.png` ×8, `operatives_sheet.png`, `enemies_*.png` ×5, `enemies_sheet.jpg`, `boss_*.png` ×5, `bosses_sheet.jpg`, `contact_sheet.jpg`.
- **Scripts:**
  - `tresdata.py`: the content parser;
  - `slicelib.py` / `programs.py`: C's code, extended;
  - `skins.py`: SANDBOX PCB, corp skins and boss effects;
  - `roster_wheel.py`: wheel assembly;
  - `roster.py`: specs from content;
  - `make_roster.py render|compose|all`: about 4 minutes. Renders are cached in `scratch/renders` and deleted after the build to stay under the size limit.
