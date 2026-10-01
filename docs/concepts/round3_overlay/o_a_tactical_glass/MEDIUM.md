# O_A — Tactical Glass

**Medium.** The Cell plans on a clear acrylic sheet laid over the screen, like a heist planning table. The overlay is made of two materials that contrast with each other and with the faceted Cv2 world:
- **Grease-pencil (china-marker) strokes.** They are waxy and nearly opaque, with streaks along the stroke direction, ragged but clean edges and real relief. One key light from the top left catches their upper edges, and they cast a 4 px shadow onto the screen below.
- **Crisp printed and physical items.** These are stencil type, registration crosshairs, edge grid ticks, dashed range rings, reticles, vinyl waypoint dots, masking and gaffer tape, and laminated cards and ID badges. The laminates have a clear pouch rim, a glare band, scratches and a punched slot.

The acrylic itself adds a faint haze, a reflection band, corner streaks and finger smudges.

**Palette.** Hot pink `#FF2B8F` is the Cell's signature: verbs, OURS and THIS ONE. The other wax colours each have one job:
- fluoro orange `#FF7312` for targets
- red `#F72120` for threats and FLAGGED
- yellow `#FFDB29` for the route and highlights
- warm white `#F2F0E3` for notes

Printed items use off-white at about 55% opacity, or yellow and red vinyl.

**Lettering.** The lettering is a custom single-stroke skeleton alphabet (`scripts/glyphs.py`), not a font. Each glyph lists its strokes in writing order. Every instance gets a slight random scale, rotation and baseline offset, a wobble, overshoot at the stroke ends, and a slant of about 10°. A bristle brush then renders the result. Stencil type is used only for the "printed" layer, which keeps the voices clearly apart: the machine prints and the human writes.

**Why it reads AAA.** The marks are restrained: 4–5 marks per screen, each colour has one meaning, and the planning-room idiom is coherent. The materials feel physical, with wax relief, lamination gloss and shadows that lift the overlay off the screen. Precise printed items sit beside loose handwriting, as on the planning screens of tactical espionage games, but the pink wax keeps it rebellious.

**Godot 2D build.**
- **Wax strokes:** each stroke is a `Line2D`, or a mesh built from the skeleton, textured with a tiling bristle-streak strip. Its UV.x is arc length, so a `progress` uniform discards fragments beyond it. That gives stroke-by-stroke writing, with pen-lift gaps as timeline keys. A baked or SDF height produces normals for a cheap lit shader with a key light and specular. The idle glint is one band uniform that sweeps every ~3.2 s.
- **Paper items:** cards, tape and badges are pre-rendered textures with a gloss and glare pass in the shader. A slight parallax tilt makes them feel loose.
- **Acrylic:** a full-screen `CanvasLayer` adds the sheen, streaks and smudge textures. All overlay items share one drop shadow offset.
- **Page exit:** a screen-space smear shader (a curved front, directional blur and streak noise) wipes the layer, then frees it.

All of this is deterministic and fed by content `.tres` files: the colours, timings and the word list.

**Risks.**
- **Legibility:** small white notes over busy art need the darken pass under the overlay.
- **Skeleton alphabet:** it needs care, because poor glyphs read as a "comic font" and lose the confident hand.
- **Stroke data for every new word:** these could be authored or generated, but localization needs a skeleton set for each script.
- **Overuse:** too many cards or tape turns the overlay into scrapbook clutter. Keep 3–6 marks per screen.
- **Cost:** wax lighting plus the smear pass costs fill-rate on the full-screen layer, so bake the static marks.
