# Round 5 slices: s_d_corp_themes (the enemy side)

Each corporation has one slice material, and every program on its wheel uses it.
- **Type** shows three ways: the white glyph, an accent rim in the slice-type colour (a glowing
  inner line on all four edges), and a type-colour **tab** along the outer arc.
- **The value** is always a big white Bahnschrift Bold Condensed number with a dark outline.
- **The player wheel** works the other way round. Its slice fill *is* the type colour, over faint
  circuit traces, and it has no tab. A glance tells the two sides apart: the enemy reads as one
  material ringed with colours, the player as colour blocks.

Everything was made in 2D with numpy and Pillow, with no Blender. The wedge mask, bevel, plate,
rim and glow are analytic per pixel, so they map one-to-one onto a fragment shader.

## Files
| File | What it shows |
|---|---|
| `corp_sheet.png` | 5 corps × 5 programs (3-tick), plus a 2-tick and a 5-tick variant per corp |
| `wheel_enemy.png` | Meridian *Collections Agent* vs Solace *Triage Unit* |
| `wheel_enemy_2.png` | Orbital *Uplink Warden* vs REBEL_CELL *Dispatch Echo* |
| `wheel_player.png` | Neutral player *Breaker* beside a Meridian wheel, to show the contrast |
| `wheel_boss.png` | Halcyon *Civic Overseer* boss (phase 2/3), with a regular Halcyon wheel for comparison |
| `shader_fx.gif` / `shader_fx_strip.png` | Six looping behaviours: the 5 corps plus the Halcyon boss tile. 24 frames, seamless loop |
| `small_and_grey.png` | Every wheel at r = 60 px, as the full shader and as a small-size LOD. Below: hero size in greyscale |
| `scripts/` | `slicelib.py` (geometry, bevel, plate, glyphs, numbers), `themes.py` (corp textures and behaviours), `wheel.py` (bezels, hub, pointer, HP arc), `data.py`, `build_*.py` |

## The corporation themes

### Meridian Freight (orange #FF8C1A)
- **Texture:**
  - Orange-painted corrugated container steel: a trapezoid ridge profile every 24 px, lit from
    the left, with a crisp crest highlight.
  - Top and bottom rails with rivets, and sparse rust.
  - A stencilled cargo code (`MRDU 447102 3`) and a `MAX GROSS / TARE` plate.
  - A barcode sticker on the inner band.
- **Behaviour:** a conveyor scroll. The panel, stencils and stickers slide tangentially by one
  192 px period per loop. A red laser scan line sweeps the barcode band twice per loop, and a
  faint beam crosses the whole tile.
- **Bezel:** machined orange steel with a hazard-stripe band and 30 notched teeth.

### Solace Biosystems (mint #3DFF8B)
- **Texture:**
  - Sterile frosted glass in dark teal with diagonal specular streaks.
  - Cells under a microscope: about 70 metaball cells with a membrane, cytoplasm and nucleus.
  - A DNA double helix etched along the outer band.
  - An ECG trace on the inner band.
- **Behaviour:**
  - Cells slowly divide. Each cell has its own phase: it pinches into two metaballs, separates,
    then fades and re-forms.
  - A double heartbeat pulse (lub-dub at t = 0.10 and 0.25) flares the ECG and the membranes,
    and brightens the glass by 10 %.
- **Bezel:** white porcelain with mint vial capsules and a mint glass outer ring.

### Halcyon Civic (violet-blue #8C7BFF)
- **Texture:**
  - A blueprint: indigo paper with a fine 12 px grid and a major 48 px grid.
  - Concentric civic rings every 30 px around the hub.
  - Municipal paving tiles on the inner band.
  - Dimension-line annotations (`SEC-07 / H-CIV`).
- **Behaviour:** traffic and utility pulses. Bright dashes run up the major vertical lines, across
  the horizontal ones and around the rings, one 96 px period per loop.
- **Bezel:** violet steel with a colonnade (60 columns), a pale trim and a floating halo ring.
- **The boss** (*Civic Overseer*) is a richer version of this theme:
  - **Tiles:** a second gold counter-flow runs on the rings at twice the speed, with a gilded halo
    line near the rim.
  - **Bezel:** heavier, with two colonnade tiers (60 and 90 columns), gilt trim lines, a
    crenellated rim and a halo ring on six struts.
  - **Phase marker:** a `PHASE II / III` plaque with three diamond pips on the bezel. The current
    pip has a halo. The HP arc carries gold `P2` and `P3` notches at 2/3 and 1/3 HP.

### Orbital Commons (ice blue #7FA8FF)
- **Texture:**
  - A deep-space star map: seeded stars, the brightest with cross spikes, and faint nebula.
  - A dashed graticule and constellation lines.
  - Two tilted orbit ellipses.
  - Satellite solar-panel cells (a silver frame around deep-blue cells) on the inner band.
- **Behaviour:** a satellite (body, two panels and a trail) crosses each tile along orbit 1 once
  per loop. A diagonal glint sweeps across the panel cells.
- **Bezel:** gunmetal azimuth ring with graduations every 2° and 10° and labels every 30°
  (`000` to `330`).

### REBEL_CELL / DISPATCH (red #E8141E)
- **Texture:** black-red, with these layers:
  - **The Cell's own PCB, corrupted.** These are the 45°-routed traces and pads of the player and
    MODEM-sign language, broken up by noise. They carry a **chromatic fringe in the player's
    colours** (pink, cyan, green, violet) and "dead pixel" blocks of player colours. This is the
    mirror of the Cell.
  - Scan-glitch bars and 1-in-3 scanlines.
  - An **inverted (point-down) hexagon emblem** on the inner band, plus a ghost hex outline
    around the glyph.
- **Behaviour:** an aggressive horizontal tear. On 3 frames of every 8, bands of rows shift
  8–46 px, the R and B channels split ±4 px, and a hot red bar flashes. Between bursts there is a
  low-level jitter.
- **Bezel:** broken black-red segments that are radially offset (glitched), a broken red inner
  line, scan bars, and inverted-hex rivets.

### The Cell (player, neutral)
- **Fill:** the type colour, darker at the hub, with faint circuit traces.
- **Bezel:** plain graphite with 30 ticks.
- It deliberately has no tab and no glyph halo.

## Shared rules (all programs)
- **Wedge geometry:** r 130 to 360, with a 3 px gap between slices.
- **Glyph and number group:** centred at 60 % of the radius span.
  - The glyph is 34 % of the chord, white with a dark outline. Its inner details are tinted with
    the accent colour.
  - The number is 1.3× the glyph height.
  - On 5-tick slices the glyph and number sit side by side.
- **Readability plate:** an elliptical darkening of up to 55 % under the group, which also kills
  the emissive under it. The REBEL tear only moves the texture, never the glyph or the number.
- **Bevel:** a 7 px band. The light direction is rotated into each slice's frame, so lighting stays
  world-consistent as the wheel spins. There is also a 1 px crest highlight and a soft cavity
  shadow.
- **Glow:** the emissive buffer (rims, tab, scan lines, pulses) is blurred at 5, 16 and 40 px and
  added on top.

## Building it in Godot 4.7
1. **Mesh.** Make one `ArrayMesh` annulus sector per slice: `ticks × 6` segments, built in the
   slice's local frame with the axis pointing up. Pass the local position in `UV`
   (`UV = local_xy / R_OUT`) and the ticks in `CUSTOM0`. Rotate the `MeshInstance2D` to the slice
   angle. The wheel node spins, and the slices are its children.
2. **Shader.** Use one `canvas_item` shader per corp (`corp_meridian.gdshader` and so on), all
   including `slice_common.gdshaderinc`. The include holds:
   - the wedge SDF (`min(r_out-r, r-r_in, r*sin(half-|θ|) - gap/2)`): AA mask, bevel band, rim
     line and tab;
   - the light vector rotated by `-slice_angle`;
   - the readability plate.

   Uniforms:
   - `slice_half_angle`, `slice_angle`, `r_in`, `r_out`;
   - `accent : source_color`, `corp_tint : source_color`;
   - `loop_t` (driven from the view: `fposmod(time * speed + slice_offset, 1.0)`; it is
     cosmetic, so wall-clock time is fine);
   - `reduce_motion : bool` (freezes `loop_t`);
   - `detail_atlas : sampler2D`, `noise : sampler2D`.
3. **Corp atlas.** Use one 1024² `detail_atlas` per corp for the parts that are not cheap to make
   procedurally:
   - Meridian: stencils and barcode stickers.
   - Halcyon: annotations.
   - Orbital: star field, constellations and the satellite sprite.
   - REBEL_CELL: PCB traces, glitch bars and the hex.
   - Solace: none needed. Cells, helix and ECG are procedural; for a cheaper version, bake 64
     cell positions into a small data texture.

   Corrugation, grids, rings, panels, scan lines and the tear are cheap math in the shader. The
   tear is `uv.x += step(…)*hash(floor(uv.y*k), floor(loop_t*24))`, sampled on the texture
   layers only.
4. **Glyph and number.** Make these child nodes of the slice, not part of the shader, so the text
   stays crisp at any size: a `TextureRect` from a white glyph atlas (pre-outlined, or with an
   outline shader) and a `Label` in Bahnschrift Bold Condensed with an outline. Both are rotated
   with the slice, glyph above the number. Below about r = 120 px, switch to the **small LOD**:
   flat corp tint, plate off, glyph ×1.55, number ×1.55, tab and rim kept.
5. **Glow.** Use a `WorldEnvironment` glow over HDR emissive output (`COLOR.rgb *= 1.0 + emissive`),
   or an additive blurred copy in a `SubViewport` if 2D HDR is off.
6. **Bezel.** Each corp gets its own bezel shader using the same ring SDF (bands, angular blocks,
   bevel). The boss uses `boss=true` uniforms for the extra tiers, crenellation, halo and phase
   pips. The phase pips and the HP-arc notches are separate nodes driven by the boss phase state.

## Readability
- **Hero size:** everything reads, in colour and in greyscale. In greyscale the glyphs and numbers
  stay white on mid or dark material, and the type rims stay visible.
- **r = 60, full shader:** the numbers just about read as white digits. The glyphs blur, and the
  dagger and burst are the first to go. The corp textures turn into a coloured "grain", which is
  fine as identity, but the type then rests on the rim colour alone.
- **r = 60, small LOD:** numbers and glyphs read clearly. **Use the LOD under about r = 120.**

## Strongest and weakest
- **Strongest:**
  - **Meridian:** container steel, hazard bezel and scan line. It is the most "physical" and
    unmistakably freight.
  - **REBEL_CELL:** the corrupted copy of the Cell's own PCB, with its player-colour fringes,
    sells the mirror story.
- **Weakest:** **Orbital**. The star map is beautiful but quiet and dark. The satellite and glint
  are small at wheel scale, and the type rims carry most of the tile. It would gain from a
  brighter orbit line or a larger panel band.
- **Favourite:** **Meridian EXPLOIT**. Corrugated orange steel with a pink rim and the red
  barcode laser crossing under a white dagger and number.
