# Route map overview: AAA-2 "Realistic night", revision 2 (2026-10-14)

The designer picked AAA-2 as the favourite look. This is the revision pass on it, applying all five designer notes plus the extra asks. It uses the same run, layout, camera and seeded build stream (4207) as `../AAA2_realistic_night.png`, so every room, link and anchor is where it was.

Nothing is committed and the Godot build is untouched. Everything is rendered with **Cycles on the GPU** (RX 6700 XT, HIP + HIP-RT, after the driver update), in headless Blender 5.2.2.

## Files

| File | What it is |
|---|---|
| `AAA2r2.png` | **The final.** 2560 × 1440 with the full frame UI. |
| `AAA2r2_hover.png` | Option 2 (the Rack) hovered. The power cut is done in 3D: every light and emitter outside the branch, the streaks included, drops to 22 %. The 2D cut adds 0.62 on top. The tag, node file and cursor show. |
| `plates/AAA2r2_plate.png`, `plates/AAA2r2_hover_plate.png` | The same two images without UI. |
| `buildings_sheet.png` | The new building shapes, labelled. They are built by the same kit, materials and renderer as the key art. |
| `compare_r2.jpg` | 2 × 2: AAA-2 before (round 1), AAA-2 r2, the r2 hover and the r2 plate, each with the critic's numbers. |
| `scripts/` | Everything needed to rebuild (see "Rebuild"). Copied from `../scripts` and changed here. |

## The designer's notes and how each was done

### 1. No cars: long-exposure light streaks
**Car geometry removed.** Nothing with a car shape is left in the frame (checked at full size on both stills):
- the 5 street cars;
- the parked cars in both parking structures;
- the foreground van;
- all 96 sky-traffic objects (bodies, lamps and the old red trails).

The 3 aerial downlights that rode the sky cars are gone too.

The street, parking and van geometry is built into a throw-away accumulator (`Sink`) instead of being deleted, so it still draws from the shared random stream and nothing else in the city moves (see "Determinism").

**Streaks** are drawn in `shapes_r2.py`, own seed 9400:
- **Shape:** camera-facing emissive ribbons along x. The colour is set per vertex: colour × strength × a smoothstep fade at both ends × ±10 % flicker.
- **Material:** `hr_streak` is additive (emission + transparent). It is hidden in the data passes and see-through in the volume pass. Its strength rides the object's `pwo`, so the hover power cut dims it.

**Street, 4 lanes:**
- **Near lanes** (y −13 and −17.2): white or warm headlight streaks going one way.
  - Colours: 60 % white 1.0/0.96/0.9, 30 % warm 1.0/0.78/0.5, 10 % cool LED.
  - Strength 2.6 and 2.0 × a random 0.3–1.0.
- **Far lanes** (y −28.6 and −31.8): red tail-light streaks going the other way, strength 3.4 and 2.8 × 0.3–1.0.
- **Lengths and gaps:** streaks run 12–80 BU with gaps of 10–55 BU.
- **Thickness:** 0.11–0.12 BU, about 1.3 px at 2560.
- **Extras:**
  - 35 % of cars have a fainter second line (the other lamp or the reflector).
  - 12 % have a dashed amber indicator.
  - 10 % are trucks, with amber marker lights at z 2.8.
- **Reflections:** every streak reflects in the puddles, because they are real emitters.

**Sky, 3 lanes:**
- **Lanes:** y 52 / z 86 white, y 57 / z 92 red, y 118 / z 120 red.
- **Streaks:** 10–38 BU long with 25–90 BU gaps. Each is straight, with a lane slope of ±0.035 and no waves.
- **Strobe:** each streak carries a dotted nav-strobe line just above it. That dotted line is the long-exposure signature of a passing aircraft, and it is what keeps these from reading as the "thin ruler lines" of the round-1 note.
- **Calm zone:** inside x 70–114, behind the decision set, sky streaks are damped to 35 %.

**Fixed during review:**
- A first pass had wavy, arched sky streaks; they read as swooshes, not cars.
- A street pass at roughly double the density and strength read as a solid light band that out-shouted the route.

### 2. The route links in wax grease pencil (`wax_r2.py`)
- **Medium:** the bible's `ui31.Pencil`, opaque wax with grain drop-outs, a satin edge and a dark offset under-shadow (0.85).
- **Strokes:** each link's projected path is wobbled by 0.7 px, densified and Catmull-smoothed, then stroked with taper.
- **States:**

  | State | Wax | Width at 1080 |
  |---|---|---|
  | Walked | lime, solid | 8 |
  | Options | orange, solid | 8.5 |
  | Ahead | white dashes (14 on / 9 off) | 5.2 |
  | Past | grey, at 38 % | 4 |

- **Hover:**
  - the hovered option's link is solid orange;
  - the other option drops to 55 %;
  - the branch's ahead links turn to solid white wax;
  - the off-branch dashes drop to 42 %.
- **Glow:** only a faint glow in the state colour sits under the walked and option wax (blur 9 px, 0.5).
- **3D holo tubes:** dropped. `holo_route_aaa.py` is no longer exec'd, which also saves render time.
- **No wax under stickers:** every pencil mask is erased inside each sticker's ring (ring radius + ring width + 5 px) and each option's number chip. Links stop short of the icons. Checked at full size on both stills.

### 3. Node icons as vinyl stickers
Unchanged: the rounds 19/34/37/42 sticker kit, the state rings, the number chips and the TARGET sticker.

### 4. The hover (power cut) stays
`AAA2r2_hover.png` is option 2 (the Rack) hovered:
- the branch rooms light ×1.45;
- everything else drops to 22 % in 3D: lights, room faces, signs, ads, holos and streaks.

### 5. Alternate building shapes (`shapes_lib_r2.py`, `shapes_r2.py`, `buildings_sheet.png`)
Every shape is a prism: a CCW footprint extruded, so the walls face out. Mid-row and far buildings get their windows from the surface shader's window grid (u = x + y, so it wraps round a drum). The route row gets explicit window quads.

**Route buildings (3 of 8 are no longer boxes):**
- **Column 5 → a CUT DRUM.**
  - The radius is half the column's plan diagonal plus 0.15 (9.37 BU), so the drum contains the V3 box.
  - Storeys without a route room are full drum storeys:
    - two ribbon-window rows (40 % lit, warm);
    - vertical ribs on every second facet;
    - projecting floor plates;
    - a cyan shop band and an awning ring at street level.
  - Storeys with a route room keep only the back half of the drum, sliced flat at the column's front plane. The V3 room box, slabs and cut walls sit in the cut, so the three rooms read exactly as before.
  - The drum's front bulge at link height is inside the column width, so no link crosses it.
  - Its old blade sign was not rebuilt, because on the drum's shoulders it would sit right behind the alley links.
- **Columns 1 + 2 → an ADJOINING pair.**
  - A two-storey connecting podium in the alley, behind every link: storefront, lit windows, a set-back second storey and a roof terrace.
  - A 3-step terraced block on shared walls behind both columns (background class).
- **Column 0 → FAT.** A wide, stepped two-part annex on its left shares the column's wall, with a shop band and lit windows.

**Mid row and far city:**

| Before | After |
|---|---|
| Mid-row box tower x 14 | Round tower (drum, 2 setback drums, crown rings, spire) |
| Mid-row box + setbacks x 73 | 5-tier ziggurat |
| Mid-row slab x 150 | Fat block with a convex curved facade and floor bands on the curve |
| Mid-row tower x −56 | Round tower, joined on shared walls to a 3-block terraced run (the old slab x −90) |
| Megastructure x 22–70 | The critique's drum megastructure: 3 stepped drums, with its ads kept |
| Far city (3 layers) | Own stream 7300: 22 % drums, 14 % ziggurats, 10 % fat round-corner blocks, rest boxes |

The concave crescent in the sheet is the second curved-facade type. It is in the kit and the sheet but not placed in the key art: there was no free plot where it would show.

### Extra asks
- **The lotus holo is gone.** In its place, at the same spot, is a readable **SOLACE** holo ad: the Solace emblem, the word, and "SLEEP IS A PRESCRIPTION". It has scanlines, an RGB split and a 6000 W violet point light. It sits next to the Solace billboard as one campaign.
- **Option 1 is separated from the cool ahead rooms.**
  - In 3D: a saturated cyan monitor wall (0, 0.7, 1.0) over a warm amber floor glow and a warm ceiling strip, a stronger 2700 K key (0.7 against 0.25) and a saturated room light.
  - Measured on the plate (`grey_check_aaa.py`):

    | Room | Hue | Saturation | p90 |
    |---|---|---|---|
    | Option 1, before | 182° | 0.17 | — |
    | Option 1, after | 163° | 0.39 | 0.84 |
    | Ahead rooms | 191° | 0.22–0.23 | — |

    Option 1 is still among the brightest rooms (p90 0.84). The Rack is first (0.86).

## Kept from AAA-2
The value structure, puddles and reflections, wind-sheared fog strata cards, HALCYON and ORBITAL billboards, the TARGET tower as the darkest mass, the red pencil TARGET and the frame UI.

## Numbers (critic's `crit_stats.py` / `stats_aaa.py`, sRGB luma)

| Image | Median | p95 | % < 0.10 | % > 0.85 | Bright sat. |
|---|---|---|---|---|---|
| AAA-2 before, plate | 0.132 | 0.793 | 40.1 % | 2.7 % | 0.26 |
| AAA-2 before, with UI | 0.140 | 0.835 | 37.7 % | 4.3 % | 0.25 |
| **AAA-2 r2, plate** | **0.138** | **0.725** | **35.5 %** | **0.9 %** | **0.31** |
| AAA-2 r2, with UI | 0.145 | 0.815 | 33.8 % | 3.8 % | 0.28 |
| AAA-2 r2 hover, plate | 0.062 | 0.507 | 67.5 % | 0.4 % | 0.34 |
| AAA-2 r2 hover, with UI | 0.055 | 0.761 | 69.7 % | 4.1 % | 0.26 |

- **Plate targets:** the plate meets every target. The median is 0.138 against "about 0.14" (`stats_aaa` flags MISS at its strict 0.14 floor).
- **With UI:** the extra pixels over 0.85 are the white dossier, the lime toggle and the stickers, as in round 1.
- **Hover:** it is dark by design.
- **Grade change:** with the holo tubes and the car lights gone the frame lost light (median 0.116 at the old grade). Exposure went from 2.6 to 3.0 and the pivot contrast from 1.25 to 1.12. That lifted the median and *lowered* p95 and the clipped share.

## Render times (GPU: RX 6700 XT, HIP + HIP-RT; Blender 5.2.2)

| Pass | Settings | Final | Hover |
|---|---|---|---|
| Cycles main | 2560 × 1440, **128 spp** adaptive (threshold 0.01), OIDN (albedo + normal; `denoising_use_gpu` set) | 172 s | 184 s |
| Cycles volume | 800 × 450, **64 spp** (4× round 1), OIDN | 186 s | 225 s |
| Eevee data passes | 3840 × 2160 | 14 s | 14 s |
| Scene build, Blender start, EXR read | — | about 30 s | about 30 s |

Post plus compose take about 1.5 min per still in numpy and PIL. **Total: about 8 minutes per still** (round 1 on the CPU: 9–10 min at 32 spp).

The buildings sheet main pass took 173 s.

**GPU notes:**
- **HIP-RT trade-off:** HIP-RT's BVH build costs about 86 s per Cycles render on this scene (two per still: main and volume), but it traces about 3× faster than plain HIP BVH2. On the mini test: 14 s against 45 s of path tracing. It wins on every final pass. `"hiprt": false` in a job switches it off.
- **CPU fallback:** `render_aaa.gpu_setup()` falls back to the CPU and logs `RENDER DEVICE CPU` if no HIP device shows.
- **Volume pass cost:** it dominates. Spending more there (1280 × 720 at 96 spp) projected to about 12 min for that pass alone, so it stays at 800 × 450 / 64 spp.

**`vol_strata` (heterogeneous strata) on the GPU:** tested at final quality.
- **Cost:** about nothing extra (204 s against 186–225 s for the plain volume pass). On the CPU it was 7×.
- **Look:** it changes the image. The in-scatter p95 triples (0.014 → 0.044), and the lowest band (z 30–38) runs behind the decision rooms.
- **Decision:** to keep the strata the designer approved (and the value numbers), the finals keep the fog cards.
- **To use it:** `vol_strata` is ready behind its flag. It needs one tuning pass: densities × about 0.4, the lowest band moved to z ≥ 40, and the post's `vol_k` re-checked.

## Godot 4.7 feasibility

### Light-streak traffic
**Recommended:** scrolling streak shader on lane cards.
- **Setup:** each lane is one long, thin, unshaded additive quad (or a MultiMesh of 3–6 segments per lane), facing the camera at the lane's y and z.
- **Shader:** draws streak segments from a hash of `floor((UV.x · L − TIME · speed) / cell)`.
  - Each cell decides whether it holds a car, its colour (head or tail table) and its length.
  - It fades both ends with smoothstep and a slight flicker; the strobe line is a `step(fract(x / 1.1), 0.5)` mask.
- **Direction:** one lane scrolls +x with white and warm colours, the other −x with red. That gives the long-exposure read even in motion, because each streak is a whole car's path.
- **Calm zone and hover:** both are a uniform multiply (the calm-zone damping and the power cut).
- **Cost:** about 7 draw calls in total, negligible fill.
- **Wet street:** SSR and the reflection probe already pick the streaks up as emissive surfaces. For a stronger mirror read, add the planned vertical screen-space smear on the street material.

**Alternative:** GPUParticles3D with trails.
- **Setup:** one emitter per lane, `trail_enabled` with a ribbon draw pass and `trail_lifetime` 0.6–1.5 s, emission on the ribbon, about 10–20 particles per lane.
- **Pros:** it gives true motion and per-car variation.
- **Cons:** the ribbons need `transform_align` to the camera, sort with the fog cards, and cost one draw per lane plus particle simulation.
- **Verdict:** fine for a hero shot. The shader cards are cheaper and fully deterministic (seeded by lane), which suits the overview.

**Determinism:** streak placement is presentation only. Seed the hash per lane from the run seed, so a replay looks identical.

### Round and adjoining buildings in the city kit
**Drums:**
- A procedural `ArrayMesh`, or a CylinderMesh with `radial_segments` 24–44, `rings` = floors, no caps on cut storeys.
- The cut storey is a half-cylinder mesh (the arc from asin((front − cy)/r) to π minus that) with the V3 room scene parented inside it, exactly as here.
- Floor plates are thin cylinders, r + 0.35.
- The window grid shader already uses world x + y, so it wraps.
- **Cost:** about 300–900 triangles per drum. Use one MultiMesh per shape family for the far city.

**Ziggurats, curved fronts, round corners:** all are footprint extrusions. Add a `Footprint → ArrayMesh` builder to the kit, the same maths as `shapes_lib_r2.prism`, and pick a family per plot from the run's seeded stream. Tie-break by plot id, so the choice never depends on dictionary order.

**Adjoining blocks and podiums:**
- Plot pairs share a wall: build the podium as one mesh spanning the alley between two columns, behind the link lane.
- The alley still holds the connection meshes, which run at y = DY − 0.7, in front of the podium face at y = 4.2.
- **Rule:** a podium may only fill an alley up to the lowest link's door height minus 2 BU.
- **Occlusion:** the round-1 rule still holds. Nothing new is placed in front of a route room; the drum's front bulge sits inside the column width at link height.

**Cost:** these add only triangles (drums and steps): about +15–25 k triangles for the overview and no new materials.

## Determinism
The shared build stream (4207) is untouched. Every replaced or removed piece is still built, into a throw-away accumulator (`Sink`), so its random draws happen in order. Every new piece builds from its own seed (`OwnRng`) and hands the shared stream back.

| Seed | Use |
|---|---|
| 9101–9104 | mid-row shapes |
| 9200 + plot | far-city alternates |
| 7300 | far-city shape choice |
| 9301 / 9302 | the drum |
| 9310 | the podium, terraced block and annex |
| 9400 | streaks |
| 9500 | the sheet |
| 501–504 | wax pencil grain |

Seeds kept from round 1: dressing 5150 / 6161, kerb 4242, post rain 41 and grain 107, the ads (9).

## Not done / limits
- **`vol_strata` is not used in the finals** (see above): it is now cheap but changes the look, so it needs a tuning pass.
- **The UI is still the 1.33× affine upscale of the 1080 overlay kit.** The wax is therefore slightly softer than the 3D.
- **The grey "past" wax is translucent and thin.** It is visible on close inspection and nearly gone at a glance, which matches "past grey translucent".
- **The crescent (concave) facade** is in the kit and the sheet, but not placed in the key art.
- **The SOLACE holo stands next to the SOLACE billboard.** It reads as one campaign. If the designer wants a different corp there, it is one line in `shapes_r2.py` plus one in `ads_aaa.py`.

## Rebuild
Run from `scripts/`. Blender runs headless and logs to `../scratch/`; nothing launches Godot.
1. `python emblems20.py`, then `python ads_aaa.py` (12 ad textures, including `holo_solace`).
2. `python jobs_aaa.py real final`, then `python jobs_aaa.py real final hover`.
   - Use `test` or `mini` for quick checks.
   - Extra flags: `cpu`, `hiprt=0`, `vol_strata`, `streak_k=<x>`.
3. `python finish_aaa.py still real`, then `python finish_aaa.py still real hover`.
4. `python sheet_r2.py` (renders and labels `buildings_sheet.png`), then `python finish_aaa.py compare_r2`.
5. `python stats_aaa.py <png>` and `python grey_check_aaa.py <plate> ../scratch/bl_real`.

**New files:**

| File | Contents |
|---|---|
| `shapes_lib_r2.py` | `Sink`, `OwnRng`, footprints, `prism`, `ziggurat`, `round_tower`, `curved_block`, `terraced_run`, `far_alt`, `cut_drum` |
| `shapes_r2.py` | the drum, podium and annex; the car removal; the streaks; the Solace holo |
| `shapes_sheet_r2.py` | the sheet's geometry |
| `sheet_r2.py` | renders and labels the sheet |
| `wax_r2.py` | the wax route links |

**Changed copies:**

| File | Change |
|---|---|
| `scene_aaa.py` | the drum column, the car sinks, the mid-row and far shapes, option 1's room colours, the exec order |
| `dress_aaa.py`, `dress2_aaa.py` | drum column dressing, lotus removal, the drum megastructure |
| `light_aaa.py` | no car downlights, option 1's key and colour, the Solace holo light |
| `render_aaa.py` | GPU, HIP-RT, `denoising_use_gpu` |
| `jobs_aaa.py` | sample counts |
| `post_aaa.py` | the "real" exposure and contrast |
| `compose_aaa.py` | the wax links |
| `finish_aaa.py` | r2 names and `compare_r2` |
| `grey_check_aaa.py` | the room hue column |
| `ui31.py`, `r31lib.py`, `stats_aaa.py` | paths, one folder deeper |
