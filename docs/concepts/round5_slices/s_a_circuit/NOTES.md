# s_a_circuit: CIRCUIT BOARD slices (round 5)

This family extends the MODEM sign. Each slice is a small PCB with these layers:

- a dark faceted substrate (about 12% copper-tone facets) tinted about 12% toward the program colour;
- copper traces under the solder mask, routed at 45 degrees;
- gold pads and vias, SMD parts with pins, and silkscreen;
- neon emissive traces in the program colour, with a white-hot core above about 0.55 intensity.

The glyph and number follow the 09 reference: a white glyph above a white Anton number, both with a dark outline, on a soft dark calm plate at 60% of the radius span. On wedges of 5 ticks or more, the glyph sits beside the number. Each tile has a 1.5 px neon rim in its colour and a bevel lit from the top left. The light is counter-rotated per slice, so the whole wheel shares one light.

All rendering was done in Pillow and numpy, with no Blender. Every image is rebuilt by `scripts/` (see the end of this file).

## Programs

| Program | Board (texture) | Behaviour (shader, loops over t in 0..1) |
|---|---|---|
| **EXPLOIT** (attack, pink) | 8 sharp traces rise straight, then cut diagonally into one breach via on the outer rim. | Packets accelerate along the traces into the breach (f = phase^1.6). Twice a loop the breach sparks: 11 random rays and a core flash. On the spark frame, 3 rows of the tile tear sideways (glitch). |
| **ZERO-DAY** (crit, hot pink/white) | One SMD chip in the inner band. Its 8 pins fan out at 45 degrees and climb the tile edges to the rim. | The chip core is always white-hot and flickers. Once per loop (t 0.45 to 0.85) the traces light in a cascade from the chip outward. Each one ends in a pad flash, then the rim flares. Most of the time the board is dark. |
| **FIREWALL** (defend, cyan) | Dense parallel bus lines at a 6.5 px pitch, with brick-staggered via pads, so it reads as a wall of traces. | A radial scan bar sweeps outward and lifts the bus to about 3.8x. Heat shimmer moves each row sideways with a sine (row offset = sin(y/7 + 4πt) · 1.3 px). |
| **SANDBOX** (shield, teal) | A cross-hatched ground plane inside a continuous guard ring, which is inset 7 px and stitched with vias every 13 px. | The stitching vias light in sequence around the ring. A containment wave travels inward across the hatch (driven by the distance-to-edge field), and the rim flares at the start of each pulse. |
| **PROXY** (evade, green) | Four traces come up from the hub, swing out to the side lanes and detour around a large blocked via near the rim. The dead direct route up the axis is drawn as dashed silkscreen. | Signal packets take the detour. Each has a faint ghost lagging 12% behind and shifted 2.5 px sideways ("slippery"). The blocked via's ring pulses. |
| **PATCH** (heal, mint) | Two side traces, each broken near the rim, with a "+" mark by each break. | A solder bridge grows in the gap with a repair spark (t 0 to 0.22). Then a green glow fills each mended trace from the hub to the rim, with a bright head, and fades. |
| **VIRUS** (afflict, violet) | A busy board with a "P0" patient-zero via in the outer corner. | An infection front expands from P0 (a distance field). Copper and pads behind the front glow violet, with a bright band at the front. Violet corruption blocks scatter along the front (reseeded at 24 Hz), and the substrate stains. It resets each loop. |
| **TROJAN** (deploy, lavender) | An innocent, tidy board: faint lavender idle packets and a plain "U7 N/C" chip. | The chip lid splits and slides apart, and its pins extend. A lavender die is revealed and its LED blinks at 8 Hz. Hidden payload traces arm from the chip to the rim. Then the lid closes. |
| **NULL** (miss, grey) | A dead board: greyscale substrate, oxidised copper, tarnished pads, and a burnt trace through a scorch (soot core, heat-discoloured rim, blistered copper flecks). | No glow at all. There is only a 1% luminance grain that changes per frame, and a dim grey rim. |

**Enemy (Meridian corporate PCB).** The board is a charcoal, lathe-machined substrate:

- concentric arc traces at a fixed pitch, crossed by radial spokes every 4 degrees;
- gold pads on every other grid node;
- a band of 45-degree container stripes in orange silkscreen at the outer edge;
- Meridian orange emissive only.

The arcs pulse inward in a fixed sequence, like a conveyor. The type is shown only by the glyph and a 3.5 px accent line in the type colour on the inner edge. The bezel is machined orange with container stripes and a notched hostile edge. The hub is a crane glyph on a CPU die. The story is that the player's boards are hand-routed and Meridian's are fabbed.

**Player bezel and hub.** The bezel is a dark PCB ring with a gold edge-connector finger on every tick and an outer pink neon tube. The hub is a CPU package: a pinned square die printed with the operative name and a status LED.

## Readability

- At hero size the white glyph and number with ~12% dark outlines over a 55% calm plate read on every tile, including FIREWALL, the busiest. They also hold in greyscale (`small_and_grey.png`, right).
- At r = 60 px, with a naive 6x shrink, the numbers still read but the glyphs become marginal: the thin dagger and drone blur. With a small-size LOD (`icon_scale` 1.55, silkscreen text dropped), the glyph and number fill the tile and both read. The board turns into colour texture, which is fine at that size. Use the LOD below a radius of about 120 px.

## Building it in Godot 4.7

**1. Mesh.** Use one `MeshInstance2D` (or a `Polygon2D`) per slice: an annular sector from `r_in` to `r_out` with arc segments every 2 degrees. Give it UVs in tile space:

- `uv.x` is the angle across the wedge, from -1 to 1;
- `uv.y` is the radial fraction `s`, from 0 to 1.

Also pass the geometric half-angle and the radii. The shader then rebuilds the same fields the scripts use: `rr`, `ang`, `d` (distance to the tile border, for the bevel, rim, guard ring and AA mask) and `s`.

**2. Texture atlas, two pages.** Bake per program, per tick count, offline with these scripts (`Board.static_masks`, emissive paths):

- **page A (RGBA8, static):** R = copper, G = pads/vias, B = chips and pins, A = silkscreen. Bake a height map from these for the bevel lighting. Alternatively, bake the lit albedo straight from `shaded_base()` at 8 fixed light angles and pick the nearest angle.
- **page B (RGBA8, behaviour data):** R = the emissive trace mask. G = the arc-length parameter along the program's hero paths (0 to 1; it drives every travelling packet, cascade and mend glow as a step or smooth band on `G - phase`). B = a distance field from the program's hero point (breach, P0 node or ground-plane depth) for the infection front and the containment pulse. A = a per-trace random id for staggering.

Tick counts in use: 2, 3, 4 and 5. One atlas cell per (program, ticks) pair is about 36 cells at 512x512.

**3. Material.** Use one `ShaderMaterial` per program, shared by every slice of that program (`canvas_item`).

- **Uniforms:** `program_colour`, `phase` (driven by `TIME * rate` or by the spin), `ticks`, `half_angle`, `r_in`, `r_out`, `light_dir` (world light rotated by `-slice_angle`), `calm_strength = 0.55`, `rim_gain`, and `reduce_effects` (freezes `phase` on a lit key frame).
- **Behaviour:** select it with a `program_id` int uniform and a `switch`. Each case is a few lines on top of the page-B fields:
  - EXPLOIT: `pow(fract(phase*2 + id), 1.6)` packet on G, plus a spark burst near B = 0, plus a UV row tear when the spark is above 0.25.
  - ZERO-DAY: cascade `G < c` with `c = (phase - 0.45) / 0.4`.
  - FIREWALL: `exp(-((s - bar) / 0.06)^2)` scan bar, with the sine row offset added to UV.x for the shimmer.
  - SANDBOX: a wave on `d`.
  - PROXY: a packet on G, plus a ghost at G - 0.12 offset sideways in UV.
  - PATCH: fill `G < f`.
  - VIRUS: front on B, plus hash-noise blocks at the front.
  - TROJAN: an animated lid rect in UV.
  - NULL: grain only.
  - Meridian: an arc index from `s`, lit in the sequence `fract(phase * n)`.
- **Glow:** apply a two-radius blur of the emissive layer through the wheel's own `BackBufferCopy` or bloom (WorldEnvironment glow on the 2D canvas, HDR 2D on). Clip the glow to the tile mask so it doesn't bleed across tile gaps.

**4. Icon and number.** Keep these out of the shader. Use a child `Node2D` per slice, rotated with the slice. The glyph is drawn by `SliceIcon` (white fill, ink outline). The number is a `Label` or `draw_string` in Anton with `outline_size` of about 12% of the glyph size. Placement is at `s = 0.6`: stacked below 5 ticks, beside from 5 ticks up. Add a calm plate sprite (a soft black ellipse at 55% opacity) under them, or keep it in the shader as `calm_strength`.

**5. State.** All of this is view-only. `phase` comes from the view's clock and never feeds game state (Signal Up, Call Down).

## Favourite

**FIREWALL** is the strongest single tile. The bus-line wall with brick pads reads as a wall even when tiny. The scan bar and heat shimmer are cheap: one band function and one UV offset.

My favourite *look* is **ZERO-DAY**. It is a dark, quiet board with one white-hot chip, and then the rare cascade lights every trace to the rim. That is "rare, dangerous, flashy" carried by restraint, and it makes landing on it feel like an event.

**Weakest: PROXY.** The detour is clear when it moves, but in a still frame it reads as "some green traces". It needs a stronger cue for the blocked via, for example a red-violet X ring, or a brighter dashed ghost route.

## Files

- `programs_sheet.png`: the nine programs plus EXPLOIT at 2 and 5 ticks.
- `wheel_player.png`, `wheel_enemy.png`, `small_and_grey.png`.
- `shader_fx.gif` and `shader_fx_strip.png`: all 9 programs plus the Meridian board, 36 frames.
- `scripts/`:
  - `circ_lib.py`: geometry, boards, programs, glyphs, tile render;
  - `wheel_lib.py`: bezels, hub, pointer, HP arc, backdrop;
  - `make_sheet.py`, `make_wheels.py [player|enemy|both]`, `make_fx.py`, `make_small.py`;
  - `test_tiles.py`: a scratch preview.

Run them with plain `python <script>.py`, in this order: wheels before small. Everything is seeded and deterministic.
