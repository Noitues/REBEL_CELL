# s_e_wildcards: three premium slice treatments

Family **WILDCARDS**: the same 9 programs in three mini-styles, plus a mixed wheel, a full
Cv2-neon wheel and a Meridian-orange enemy. Everything is 2D (Pillow + numpy), procedural,
seeded (`crc32` of names), and rebuilt by `python scripts/make_all.py`.

## Files
| File | What |
|---|---|
| `programs_sheet.png` | Overview: 9 programs x 3 styles, with 2-tick and 5-tick variants per style |
| `programs_sheet_holo.png`, `_enamel.png`, `_cv2.png` | One sheet per style at master size, plus a row at r = 150 with the shader mid-cycle |
| `wheel_player.png` | Left: the full Cv2-neon wheel with the sticker overlay. Right: the **mixed** wheel |
| `wheel_player_cv2/_mixed/_holo/_enamel.png` | Each wheel alone at master size (r = 345 px) |
| `wheel_enemy.png` | Meridian "Collections Agent" in Cv2 neon orange, plus six single enemy tiles |
| `shader_fx.gif`, `shader_fx_strip.png` | 6 programs x 3 styles looping (24 frames). The strip shows t = 0, .25, .5, .75 |
| `small_and_grey.png` | All four player wheels at r = 60 px (with a 2x nearest zoom), and the Cv2 hero in greyscale |
| `scripts/slicelib.py`, `scripts/make_all.py` | The generator |

## Shared rules (all styles)
- **Local frame.** Each slice is shaded in its own coordinates: `lx` is the tangential distance
  from the centre line, `ly` the radial distance (master units, outer radius 360, hub 130).
  Textures and icons rotate with the slice. The wedge SDF is
  `e = min(r - 130, 360 - r, r*sin(half - |phi|) - gap/2)`. It drives the antialiasing, the
  bevels, the dome and the rim effects.
- **Icon.** A bold white glyph with a dark outline (36% of the chord at r = 268), over a bold
  condensed white number with a dark outline (1.08 x the glyph height). For wedges of 5 ticks
  or more the glyph sits beside the number. NULL shows a glyph only, at 1.3 x.
  Readability comes from three layers. Each style calms its texture under the icon (a
  super-gaussian "plate" darkening, the enamel cartouche, or darker facets). A soft shadow
  sits under the icon. The outline itself is about 8.5% of the glyph size.
- **Program shader flavour.** These are layered on top of each style's own shader:

| Program | Flavour |
|---|---|
| EXPLOIT | Glitch bands: `lx` offset per 9-unit band, in bursts, with a channel swap |
| ZERO-DAY | A white flash, twice per loop |
| FIREWALL | Scanlines, and a bright course sweeping outward |
| SANDBOX | The border pulses in program colour |
| PROXY | A lateral reroute shift of the texture |
| PATCH | A breathe, and a heal ring expanding from the icon |
| VIRUS | A broken infection wave from a seed point |
| TROJAN | An unpacking seam that opens down the centre line |
| NULL | A dead flicker, with static |

## 1. Holo foil collectible
The base foil colour is a rainbow `hsv(0.55*P + tilt_gradient + t, 0.66)`, mixed 45% toward the
program colour and modulated by the program's foil pattern `P`. A large blurred copy of the
program emblem is **embossed** into the foil: it shifts the hue by 0.33, and two offset samples
give the highlight and shadow rims. Each slice has a thin chrome-rainbow card edge.

| Program | Foil pattern |
|---|---|
| EXPLOIT | Diagonal diffraction lines |
| ZERO-DAY | Prism-star field plus rays from the icon |
| FIREWALL | Brick holo with mortar |
| SANDBOX | Nested squares around the icon |
| PROXY | Chevron diffraction |
| PATCH | Hex holo |
| VIRUS | Worley cellular foil |
| TROJAN | Diamond lattice |
| NULL | Desaturated "dead" matte foil |

**Shader (tilt).** `tilt` (vec2: card tilt, or the wheel's spin velocity, or the mouse) rotates the hue
gradient direction and moves a glint band along the slice. Sparse sparkles twinkle.

## 2. Enamel pin / cloisonné
Fields come from an integer label function per program. Gold walls appear wherever a label
changes (edge detect, dilated about 1.6 units) and around the wedge rim. A dark navy
**cartouche** behind the icon is the readability plate, outlined in gold. The enamel picks up
ambient occlusion next to the walls. A glossy dome comes from `sqrt(e/55)`, giving Blinn
specular light from the top left.

| Program | Fields |
|---|---|
| EXPLOIT | Slash stripes |
| ZERO-DAY | Sunburst rays |
| FIREWALL | Gold-mortar bricks |
| SANDBOX | Nested frames |
| PROXY | Chevron bands |
| PATCH | Bandage strip with holes |
| VIRUS | Spore cells with dark nuclei |
| TROJAN | Crate planks with a lid band |
| NULL | Matte grey with pewter walls (gloss x 0.3) |

**Shader (specular sweep).** A screen-space diagonal band, plus a thin secondary line, crosses
the whole wheel, so all the pins catch it one after another.

## 3. Faceted Cv2 neon (the game's base)
The triangle mesh is generated per program in polar space, rasterised to a facet-ID map in local
space, and given per-facet colour, a random facet normal (Lambert shading), a `lit` flag and a
`phase`. The look adds gritty seams (dark facet edges), hash grain, a few scratches, and a neon
rim on the outer arc. Lit facets get neon edges. Facets near the icon are darkened (the plate).

| Program | Facet pattern |
|---|---|
| EXPLOIT | Few rings, high jitter: long sharp shards, dark slivers |
| ZERO-DAY | A starburst fan from the icon, alternating hot pink and white |
| FIREWALL | 7 low-jitter courses with alternating diagonals (layers) |
| SANDBOX | A symmetric enclosure |
| PROXY | Zigzag reroutes (diagonals alternate by column) |
| PATCH | A calm, even, alternating grid |
| VIRUS | High jitter with 22% dark shards: chaotic spread |
| TROJAN | A lavender shell around a dark core with a few bright "payload" facets |
| NULL | Four big dead grey facets, no neon |

**Shader (sequence).** `boost = pow(clamp(1 - fract(t - phase)/0.2, 0, 1), 2)`, so each facet
flares once per loop, in the order of its phase:

| Program | Order of the flare |
|---|---|
| EXPLOIT | Radial outward (a thrust) |
| ZERO-DAY | Around the burst |
| FIREWALL | Course by course |
| SANDBOX, PATCH | Distance from the icon |
| PROXY | Lateral |
| VIRUS | Distance from a seed (infection) |
| TROJAN | Inward (unpacking) |
| NULL | Random and dim |

### Enemy: Meridian corporate (Cv2 neon)
- **One material family.** Every slice uses the same orderly mesh parameters (low jitter
  0.18) and the same Meridian palette: orange #FF8A1F, amber #FFB547, rust #B4430E and
  near-black shards.
- **Type** is shown by the glyph and by program-colour accents: the outer neon rim, an inner
  band at the hub, and the lit facet edges.
- **Bezel.** A machined hazard-stripe bezel with notched orange teeth, an amber pointer, and
  the Meridian mark in the hub.

## Mixed wheel (my picks)
| Program | Style | Why |
|---|---|---|
| ZERO-DAY | **Holo** | It is rare and flashy, and a foil card is literally "the rare pull" |
| VIRUS | **Holo** | The cellular foil reads as infectious, and the tilt makes it crawl |
| FIREWALL | **Enamel** | Gold mortar bricks are the most "solid, blocking" image of the three |
| SANDBOX | **Enamel** | Walled fields are "contained" by construction |
| EXPLOIT, PROXY, PATCH, TROJAN, NULL | **Cv2 neon** | The base. Shards suit EXPLOIT best, and NULL must stay dead |

## Which mini-style fits the Cv2 base and the sticker overlay
**Faceted Cv2 neon is the base, and holo foil is the accent.**

- **Cv2 neon** is the only one of the three that belongs to the same world as the chosen
  combat screen: matte triangulated low-poly, grit, and orange and grey bezels. It reads at
  r = 60, and in greyscale its value pattern comes from the facets, not from hue.
- **Holo foil** is the natural partner of the **sticker overlay**. The overlay already uses
  holographic die-cut vinyl (the crew card and the SEND IT sticker), so a foil slice reads as
  "a sticker slapped on the wheel". Reserve it for rare or upgraded programs (ZERO-DAY, or an
  upgraded slice) so it stays special.
- **Enamel** is the most legible and the most "premium object", but its gold-and-dome finish is
  a different material language from Cv2's matte facets. It fits best as a reward or
  collection skin (cosmetic unlock, or boss-loot wheels), not on the default wheel.

**Favourite:** the mixed wheel's **holo ZERO-DAY** on a Cv2 wheel. It is a rare program that
literally looks like a rare holo card next to the matte facets. Close second: **Cv2 EXPLOIT**
shards.

## Building it in Godot 4.7
- **Mesh.** For each slice, build one `MeshInstance2D` (or a `Polygon2D`) wedge: an arc
  polygon from 130 to 360 in about 4 segments per tick, generated at runtime from tick
  count and start tick. Put local coordinates in `UV`
  (`UV = vec2(lx, ly)` in master units, computed per vertex), so the fragment shader works in
  the same frame as these scripts. Store `half_angle`, `ticks` and `program_id` as instance
  uniforms (`instance uniform`, valid on CanvasItem shaders in 4.x), so one `ShaderMaterial`
  per style serves every slice.
- **Shaders.** There is one `.gdshader` per style (`slice_holo`, `slice_enamel`, `slice_cv2`), and
  each switches on `program_id` for its pattern function. That makes 3 materials, not 27.
  - **Uniforms:** `t` (loop time), `tilt` (vec2, from spin velocity or the mouse),
    `sweep_pos`, `program_color`, `accent_color`, `plate_strength`, `lod`, `fx_enabled`.
  - **Wedge SDF:** computed in the fragment shader from `UV`, as above. It gives
    antialiasing with `fwidth`, the bevels, the dome normals (`dFdx`/`dFdy` of the height) and
    the rim.
- **Facet maps (Cv2).** Bake each program's facet-ID map once at build time, as an R8/RG8
  texture in a small **atlas** (9 programs x 3 tick sizes). Do it from the same generator in
  a tool script, or ship PNGs exported by `facet_mesh`. A second 1D texture holds the
  per-facet base colour, the `lit` flag and the `phase`. The shader samples the ID
  (nearest-neighbour), then looks up colour and phase. Seams come from comparing the ID with
  `dFdx`/`dFdy` neighbours. Enemy families just swap the palette texture.
- **Holo and enamel patterns** are cheap analytic functions (sin, fract, hex distance, a small
  Worley over 16 to 32 uniform points). The enamel walls work best baked: bake the label map
  per program into the atlas, and run edge detection in the shader or bake the wall mask.
  The embossed emblem is the glyph SDF from the icon atlas, blurred.
- **Icons.** Use an SDF/MSDF glyph atlas (9 glyphs) plus a `Label` or `TextMesh` for the number,
  or one `CanvasItem` per slice that draws glyph and number with an outline. Both are
  children of the slice node, so they rotate with it. Keep icons **out of** the texture shader
  so they never glitch: the program flavour only affects the texture.
- **LOD.** Below r ≈ 100, pass `lod = 1.35`: the icon scales up, `plate_strength` goes up, and
  the program flavour is off (`fx_enabled = false`). Below r ≈ 70, drop the glyph outline glow
  and the sparkles.
- **Determinism.** The visuals only read `t` and `tilt`. No gameplay RNG is touched, and the
  mesh seeds are fixed per program.

## Readability findings
- At **r = 150** (the in-game rows on the sheets), every program reads in all three styles.
  Enamel is the clearest, because of the cartouche.
- At **r = 60** (`small_and_grey.png`, with the LOD on), the numbers stay readable on all four
  wheels. The glyphs read as shapes, but fine interior detail disappears: the shield's courses
  and the knight's eye are lost, and the dagger and burst still read. Holo is the noisiest at
  r = 60. Cv2 and enamel are the cleanest.
- **Greyscale.** The white icons and dark outlines carry everything. In Cv2, colour type is lost
  in grey, as expected, but the glyphs separate the programs.
