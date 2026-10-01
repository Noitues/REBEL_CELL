# Round 7: three spinner versions (built on the round-6 Screens & Data wheel)

Every version keeps the core of C:
- a CRT screen per slice;
- a big white glyph and value on a dark read plate;
- the same pointer, hub, inner ring and HP arc.

Every version shows the same three subjects, built from real `content/` data:

| Subject | Wheel |
|---|---|
| Breaker | crit 12, atk 6 ×3, def 5, miss; inner ring x2 / PIERCE / BLANK |
| Route Optimizer | readers at ticks 0 and 15 |
| The Manifest | phase 1; Priority Routing hub; phase pips at 66% and 33% |

## Files
| File | What it is |
|---|---|
| `compare.jpg` | A 3×4 grid. Rows are Breaker, Route Optimizer and The Manifest. Columns are the current round-6 version, V1, V2 and V3. |
| `v1_*.png`, `v2_*.png`, `v3_*.png` | 1920×1080 per subject. Each has the wheel, the version's rules, and an "all 9 programs" strip so you can also judge PROXY, PATCH, SANDBOX and TROJAN. None of the three subjects carries those four. |
| `v_bosses_compare.jpg` | The three boss treatments of The Manifest, large. |
| `small_and_grey.png` | Every version at r = 60 (small variant), in colour and greyscale, plus the hero in greyscale. |
| `scripts/` | The round-6 scripts, plus `versions.py` (V1–V3 renderer), `mascots.py` (V2 watermarks) and `make_versions.py [render\|compose\|all]` (about 1.5 minutes). |

## V1 "Program cartridges": identity from silhouette

### Slices
Each slice has a shell moulded in its program colour (an 11 px bezel), its own edge and a `NAME.exe` tab on the rim:

| Program | Shell |
|---|---|
| FIREWALL | Brick-toothed edge |
| VIRUS | Wobbly, cell-like edge with cilia dots |
| EXPLOIT | Jagged, sawtooth edge with a crack |
| SANDBOX | Riveted box with corner brackets |
| PROXY | Offset double frame |
| PATCH | Taped seams |
| TROJAN | Gift band and bow |
| ZERO-DAY | Burning glow and a wax seal |
| NULL | Broken shell with a dangling, unplugged plug |

The edges are modulations of the slice's distance field, so in Godot they are a few lines in the same slice shader.

### Borders
A sculpted ring:
- **Breaker:** ten heavy riveted plates and a crowbar clamp.
- **Meridian:** a corrugated band, container corner-castings and twist-locks.
- **Boss:** eight armoured segments.

### Boss extra
An orbit of six armoured satellite modules. Each module shows one of the boss's programs.

## V2 "Living programs": identity from content

### Slices
Each program has a mascot watermark in its screen, drawn as a dark silhouette with a bright outline under the glyph. The read plate drops to 0.55 so the mascot shows.

| Program | Mascot |
|---|---|
| FIREWALL | Brick golem |
| ZERO-DAY | Skull |
| VIRUS | Worm |
| TROJAN | Horse |
| PROXY | Mask |
| PATCH | Bandage-heart |
| EXPLOIT | Cracked padlock |
| SANDBOX | Cube with a face |
| NULL | Plug |

The mascots also show on enemy skins, so enemy slices gain identity too. Intended motion is listed in `mascots.MASCOT_NOTE`: the golem stomps on hits, the worm crawls, the padlock springs open.

### Borders
The bezel is a live readout strip. Class or corp telemetry scrolls round it in mono type with a bright "write head", and emblem badges sit at the free cardinal points.

### Boss extra
- A projected hologram crown: emitter beams, a spiked halo, a visored corporate face and the corp emblem, with scanlines and an RGB split.
- A second concentric ring of 12 mini program slices.

## V3 "Mixed media": identity from material

### Slices
Every screen sits in its own anodised metal housing in its program colour. The housing is brushed, with a hard bevel and a deep groove, a 3 px gap, four screws, vent slots and an engraved `MOD-<PROGRAM>` plate.

### Borders
- **Player:** a salvaged ring with vinyl die-cut stickers (NO CORP, CELL, 404, a skull…), scratches, tape and a grease-pencil tally.
- **Enemy:** a clean machined ring with fine lathe grooves, an engraved corp name, the corp mark and an orange pattern band.

### Boss extra
- Four conduits plugged into the bezel from off-screen.
- Two power gauges (PWR, LOAD) on the rim.
- A three-lamp phase meter (P1 to P3) built into the bottom of the rim.

## Readability check (`small_and_grey.png`)
- At r = 60, every version keeps the white glyph and number readable, and greyscale holds.
- **V2:** the watermarks fade out at r = 60, which is acceptable: they are flavour, not information.
- **V1:** the silhouettes still read at r = 60 (teeth, jags, the seal glow).
- **V3:** the housings read as a uniform frame when small.

## My take
- **V1** gives the most identity per slice at a glance.
- **V2** is the most "programs that execute", and the strongest once animated.
- **V3** gives the best contrast between player and enemy (salvage vs machined).

A natural hybrid would combine V1 silhouettes, V2 mascots in motion, and V3's player/enemy border split.
