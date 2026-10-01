# s_b_hardware: hardware materials

Every program is a physical slab of salvaged tech: bevelled, lit, rendered in Blender 5.2
(Cycles, orthographic top-down, 96 spp + OIDN). The glyph and value are overlaid in 2D, as
they would be in Godot. Geometry follows SPEC.md: 30 ticks, R 360 / hub 130 px, label centred
at 60% of the radius span, glyph about 34% of the chord.

## Programs

| Program | Texture / geometry | Shader behaviour (`shader_fx.gif`) |
|---|---|---|
| **EXPLOIT** | Anodised pink aluminium: metallic, brushed grain, about 130 scratches from the atlas that expose silver. The outer arc has a crowbar notch (a V-cut with a hooked step). | **Glint sweep.** A diagonal specular band crosses the tile in the first 55% of the loop, then rests. The scratches catch it 1.6x harder. |
| **ZERO-DAY** | A clear glass slab (transmission, IOR 1.52) over an emissive hot-pink core that is brightest at the impact point. The atlas cracks add roughness, bump and faint emission. | **Shimmer + crack flash.** A UV wobble stands in for refraction. The crack mask spikes white-pink twice per loop, with a blurred halo. |
| **FIREWALL** | A dark cyan anodised base with 8 arc-shaped heat-sink fins. The fins are real geometry that re-flows to any tick width. | **Heat haze.** A horizontal UV ripple grows toward the rim and travels outward, with a faint cyan shimmer band. |
| **SANDBOX** | A frosted acrylic box (transmission, roughness 0.32) on a teal tray. Inside sits a tilted emissive cube with a teal point light. | **Inner pulse.** The glow around the cube swells and fades, and the whole acrylic brightens about 18%. |
| **PROXY** | Green 2x2 twill carbon weave from the atlas, clear-coated. A diagonal band of mirror tiles has a few missing (salvaged). | **Reflection reroute.** A bright band slides along the mirror band, followed by a faint ghost. It lights only the mirror-tile mask. |
| **PATCH** | A PCB: solder mask, copper traces and tin pads from the atlas, under a strip of translucent green tape. Also SMD chips and a domed solder blob. | **Solder cools.** The blob flashes white-hot and cools through orange to settled metal. A trace-wake wave runs out from the joint. |
| **VIRUS** | A violet silicone slab (subsurface, soft 4-segment bevel) with veined noise. Emissive-tipped pustules are filtered per tile width. | **Pustules throb.** Each one swells by a UV pinch, out of phase with the others, and its violet glow follows. |
| **TROJAN** | A lavender brushed plate with a panel groove, a seam along the axis and a satin ribbon band with a bow. | **Panel cracks open.** The two halves slide apart along the seam (about 8 px). Light fills the gap, bleeds out and lights the panel line, then the panel seals. |
| **NULL** | Bare primer grey: matte, mottled, orange-peel bump, four rivets and a dead LED. | **Nothing.** It stays static on purpose. |

Live programs carry a small status LED at the rim in their colour. NULL's LED is dead.

## Enemy: Meridian, corporate machined (`wheel_enemy.png`)

One material (`m_meridian`) on every slice, banded by radius:
- a brushed-steel hub band with concentric machining marks;
- an orange powder coat with orange-peel bump;
- a yellow and black hazard rim;
- grooves between the bands.

The type shows only in the glyph and in a thin emissive inlay in the program colour,
between the coat and the hazard rim. The bezel is a hazard ring plus a castellated orange
powder-coated collar, with a steel lip and an orange hub glow.

## Readability

- The label is white with a dark outline (9% of the glyph size) and a soft shadow.
- A per-program dark elliptical plate (`PLATE` strength 0.3–0.62) calms the texture. It is
  clipped to the tile alpha.
- **r = 60 (`small_and_grey.png`).** In **A**, the hero frame is shrunk. The numbers still read,
  but the glyphs become blobs and the 2-tick glyphs are lost.
- **B** is the recommended LOD: the same tile art, the label drawn natively at a 10 px glyph
  minimum, plates 1.4x darker and FX off. In B every number and most glyphs read.
- **Greyscale.** At hero size every label holds. The tiles themselves separate by texture
  (fins, weave, dots, PCB) rather than by value. Pink, violet and green fall to similar greys.

## Building it in Godot 4.7

1. **Bake the tile art.** Export one atlas cell per program at a fixed size: 3.6 x 3.6 units,
   x -1.8..1.8, y 0.9..4.5 in the tile-local frame, 720 px. Hub at the origin, axis +Y. A 60°
   tile fits the cell, so 2- to 5-tick tiles all sample the same cell.
   - Bake from the Blender scene with `blend_tiles.py`. Render each program upright, alone,
     with the camera framing the cell.
   - Pack the cells into `slice_albedo_atlas.png` (3x3).
   - Pack a matching `slice_mask_atlas.png`:
     - R: the program's FX mask (scratches, cracks, mirror tiles, PCB traces, seam/groove,
       pustules);
     - G: emission mask;
     - B: the label plate (or computed in the shader).
2. **Mesh.** One `Polygon2D` (or a `MeshInstance2D` with an `ArrayMesh`) per slice, built from
   the same wedge outline as `outline()`: the gap inset and the EXPLOIT notch are part of the
   polygon.
   - Set `uv` to the cell-local UV, `u = (x + 1.8) / 3.6`, `v = 1 - (y - 0.9) / 3.6`,
     offset into the atlas cell.
   - Rotate the node to the slice's centre angle so the texture turns with the wheel.
3. **Material.** One `ShaderMaterial` per slice (or a shared shader with per-instance
   uniforms).
   - `shader_type canvas_item;`
   - Uniforms:
     - `sampler2D albedo_atlas, mask_atlas;`
     - `vec4 cell_rect;`
     - `int program;`
     - `vec4 program_color;`
     - `float fx_time;`
     - `float fx_strength;` (0 at LOD or for NULL)
     - `vec2 anchor;`
     - `float plate_strength;`
   - Each behaviour above is 5–15 lines, a branch on `program` (or one shader per program):
     - glint: a band along `dot(local, dir) - fx_time*k`, times (0.45 + 1.6*mask.r);
     - shimmer, haze, throb and seam split: a UV offset before the albedo fetch, with the
       mask atlas giving the region;
     - flash, pulse and cool: emission added from `mask.g * f(fx_time)`.
   - Keep `fx_time` view-only (a `Time` or `Tween` value in the view). It is never game state.
4. **Labels.**
   - Draw the glyph from an SDF or MSDF icon atlas and the value as a `Label`/`TextLine` in
     Anton with an outline, as a child of the slice node, rotated with it.
   - Size: glyph = clamp(0.34 * chord, 10 px, 62 px), value at 1.05 x glyph.
   - At 5 or more ticks, put the glyph beside the value.
5. **Enemy.** One shared `ShaderMaterial` with a single albedo cell (the Meridian part). The
   only per-slice uniforms are `inlay_color` and the glyph. This is cheap, and it states the
   rule "corporate = uniform".
6. **LOD.** When the wheel radius is under about 120 px: set `fx_strength = 0`, raise
   `plate_strength` 1.4x and keep the 10 px label floor.

## Favourite

**FIREWALL.** Real fins re-flow to every tick width with no texture stretch. They read as
"blocking" in silhouette alone, even in greyscale, and the heat haze is cheap but alive.
Runner-up: **ZERO-DAY**, where the glass over the hot core with a crack flash is the most
"rare and dangerous".
Weakest: **TROJAN**. The plate reads as generic lavender metal, and its best moment (the seam
splitting) happens behind the label. The seam might be better off-axis.

## Files

The scripts are in `scripts/` (`python scripts/build_all.py [samples]`; intermediates go to
`$SBH_WORK`):
- `common.py`: geometry, layouts and the seeded feature placements;
- `make_textures.py`: the atlas cells;
- `blend_tiles.py`: the Blender scene, materials and renders;
- `ui.py`: glyphs, labels, plates and bloom;
- `compose.py`: the sheets and wheels;
- `fx.py`: the GIF and the strip.
