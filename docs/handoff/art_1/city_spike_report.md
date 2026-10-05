# ART-1 1D: the unified-city render spike

Bible §1.2 (World), §4.1–4.2, §6.1; plan §5.1–5.2; designer ruling 7 (pause point 0): fidelity
first, then an optimisation round, with the budget as a gate. Agent 1D, 2026-10-05.

**Recommendation: (a), real-time Godot 3D.** At the grid, raid and netrun zooms it is the closer of
the two to the references. It is the only one of the two that does what §4.1 locks: one model and one
camera, a continuous zoom, see-through buildings by view band, and car and building LOD by ortho.
After optimisation, at 1920×1080 on this PC it takes 2.5–2.8 ms a frame (GPU 2.0–2.3 ms) against
the city budget of 8 ms.

## What was built

The district is the same in both versions. It is the game's own layout: NeonCity's streets, lots,
territories, buildings and HQ lots, with seed 7. It is read through `CityLayoutRecorder`, the
successor of the round 6 `city_export_probe.gd` that the concept rounds were built from. The district
is the Halcyon border, a radius of 50 lots around lot (34, 22), which is the frame of the round 39 and
40 references. It holds Halcyon HQ and the Cell's district: 3,710 buildings, 5,187 extrusions and
2,608 street lots.

Following the round 34 lock, the Cell's district keeps the normal street grid, so the fist roads are
not laid out. The HQs are stepped stand-ins; the five locked heroes are ART-5's work.

| | (a) real-time 3D (`tools/spike/city/city_spike_3d.tscn`) | (b) baked layers + 2D motion (`city_spike_baked.tscn`) |
|---|---|---|
| Geometry | MultiMesh building families: unit prisms (4, 6 or 8 sides × 4 facet-row classes = 11 meshes). Each wall is split into a jittered triangle grid of about 1.7 BU, with a tone value per triangle. Each extrusion is one instance: footprint basis, base and height, with taper in `INSTANCE_CUSTOM` | The same extrusions rebuilt in Blender 5.2 with the concept's `fgrid` and window, ledge, trim and shopfront geometry (`blender/bake_district.py`) |
| Toon | Light function: 3 bands of N·L × shadow → night ramp × colour × tone jitter (`target_corps.mat_toon` numbers) | Eevee with the concept's toon node tree |
| Windows, trim, ledges, shopfronts | Procedural in the building shader: a window grid along the true wall frame, ledges from raid zoom, shopfronts at transit zoom, neon roof trim in the building's ink | Geometry |
| Ink, spill, bloom, fog, haze, rain, grade | One full-screen pass, a port of `post40.finish` that, like post40, works on display values. Ink comes from normal, depth and material edges with a wobble. Bloom and spill come from the screen mips over a threshold, because Godot has no emission-only buffer | `blender/post_bake.py`, a direct port of `post40.finish` from the id, normal, depth and glow passes |
| See-through (raid / netrun) | A ground-only SubViewport (layer 2, half resolution) under the buildings in the post pass: opacity 0.68, darkened ×0.86, chroma ×1.35 | The ground-only passes baked for the view |
| Traffic | Sky lanes over the district's busiest avenues, cars from a seeded `RngStreams` stream (`CityTraffic`). Three MultiMesh tiers (FAR, MEDIUM, CLOSE) moved in the vertex shader | The same cars projected with `CityIsoCamera` and drawn in 2D |
| Camera | One orthographic `Camera3D` (`CityIsoCamera`: yaw 135°, pitch 40°, ortho = view width) | One bake per view and zoom |

Shared, headless-tested logic lives in `scripts/city3d/`:

- `CitySpikeConfig`: every number, held in `tools/spike/city/city_spike_config.tres`;
- `CityIsoCamera`: projection, unprojection, ray and fit;
- `CityLod`: see-through band, car tiers with hysteresis, detail tiers and quality tiers;
- `CityLayoutRecorder` and `CityDistrict`: the layout, prisms, picking and bounds;
- `CityMeshKit`: unit prisms, instance mapping, ground, lanes and cars;
- `CityTraffic`.

The toon, ink and post shaders are my own prototypes in `tools/spike/city/shaders/`, because 1B owns
`shaders/kit/` and has not merged yet. They are to be unified with 1B's toon and ink material.

## Captures: read side by side with the references

All captures are windowed at 1920×1080 through `run_windowed.py`, one window at a time, and every
frame was read. Each crop shows 3D, then the bake, then the reference. The crops are in
`docs/art_review/ART-1/1D/`, which is git-ignored by Godot.

| Crop | What I read |
|---|---|
| `grid_3d_baked_ref.jpg` (vs `round39_city_unified/city_grid.jpg`) | 3D: the same violet night city. It has three hard bands (lit faces lavender, sun-side roofs light, far faces navy), dark wobbly ink on every silhouette and crease, neon roof trims in the building inks, and lane glow in the lane colours (red in the Cell's district, yellow and pink toward Halcyon). Brightness is within reach of the reference (luminance p10/50/90 0.12/0.22/0.50 against the reference's 0.17/0.29/0.63, with the reference's UI and network excluded). Gaps: Halcyon is a stand-in (the reference shows the locked hero), there are fewer lit windows on the HQ, and there is no network decal. The bake is darker and flatter (0.14/0.21/0.39). |
| `raid_3d_baked_ref.jpg` (vs `round40_city_unified/raid_view_v3.jpg`) | 3D: see-through at 0.68 with the streets showing under the buildings, MEDIUM car boxes in lane colours, and lane glow stepped back. It reads like the reference's city layer, without the network or the UI. The bake is much darker (median luminance 0.12 against 0.18 for the reference and 0.17 for 3D). |
| `netrun_3d_baked_ref.jpg` (vs the NETRUN panel of `three_views_v3.jpg`) | 3D: ledges and facets resolve, and shopfront bands appear at street level. The bake is again darker. |
| `close_3d_baked_ref.jpg` (vs the CLOSE panel of `cars_lod.jpg`) | 3D: CLOSE car models with a thick lane-colour speed line, see-through buildings, facets and tone jitter visible. The reference's roof trims are white-hot. Ours are lighter neon but not white (the neon gain is a config value). |
| `raid_before_after_opt.jpg` | The raid frame before and after the optimisation round: no visible change. |

**Why (a) and not (b).** Both use the same geometry recipe, so the stills could be tuned to converge.
My port of the bake post came out darker; I did not tune it as far as the 3D pass, and the reason is
structural rather than in the stills.

- A bake is one image per view and zoom. The bible's continuous zoom, the raid fit per network,
  see-through by view band, car and building LOD swaps and the panning City Grid all need either many
  bakes or a re-bake.
- The whole city (about 14,100 buildings, about 1,500 BU across) at raid density (5 px per BU) is
  about 7,400 px square per layer, roughly 220 MB RGBA per layer before glow and ground layers.
- Motion in (b) is a 2D overlay with no occlusion by buildings. 3D gets occlusion for free.

## Numbers

**Machine.** This PC: RX 6700 XT, Godot 4.7.2, Forward+, vsync off. Each figure is an average over 8 s
after 120 warm-up frames, from `--perf=8`. Frame time is wall time per frame; GPU and CPU are the
viewport's measured render times. During every measurement other agents were running 3–6 `godot.exe`
processes (headless test shards and one capture window), so the averages are representative but the
maxima include spikes from sharing.

**(a) 3D, after the optimisation round:**

| View | Tier / size | Frame avg | Frame max | GPU | CPU | Draw calls | Primitives | Texture memory | Video memory |
|---|---|---|---|---|---|---|---|---|---|
| grid (ortho 440) | 2 / 1920×1080 | **2.69 ms** | 11.3 | 2.31 | 0.26 | 31 | 2.19 M | 106 MB | 147 MB |
| raid (ortho 380) | 2 / 1920×1080 | **2.78 ms** | 21.3 | 2.22 | 0.23 | 33 | 2.23 M | 127 MB | 177 MB |
| netrun (ortho 190) | 2 / 1920×1080 | **2.53 ms** | 21.7 | 1.95 | 0.25 | 33 | 2.23 M | 127 MB | 177 MB |
| grid | 1 (Deck) / 1280×800 | **1.81 ms** | 9.1 | 1.44 | 0.25 | 31 | 2.19 M | 42 MB | 65 MB |
| raid | 1 (Deck) / 1280×800 | **1.81 ms** | 19.8 | 1.34 | 0.20 | 33 | 2.23 M | 48 MB | 76 MB |
| raid | 0 / 1280×800 (before the ground-pass change) | 1.72 ms | 19.3 | 1.03 | 0.20 | 20 | 1.15 M | 41 MB | 68 MB |

**Before the optimisation round** (tier 2 at 1080p: shadow atlas 4096, MSAA 2×, full-resolution
ground pass):

| View | Frame avg | GPU | Texture memory | Video memory |
|---|---|---|---|---|
| grid | 3.31 ms | 2.86 ms | 210 MB | 251 MB |
| raid | 3.46 ms | 2.69 ms | 283 MB | 349 MB |
| netrun | 3.16 ms | 2.36 ms | 283 MB | 349 MB |

**What the optimisation round changed** (all in config; frames compared, no visible change):

- the tier 2 shadow atlas went from 4096 to 2048;
- MSAA went off, because the ink pass already draws the edges;
- the ground-only pass went to half resolution (`ground_pass_scale`). It shows at 32 %.

The result: texture memory fell from 210/283 MB to 106/127 MB, and frame time fell by about 0.6 ms.

**(b) baked, raid at 1080p:** 3.64 ms a frame. That cost is CPU (GDScript `_draw` of 366 cars); the
GPU takes 0.94 ms. Draw calls: 345. Texture memory: 31 MB for one view's image. Bake cost: 4 views ×
7 passes at 2880×1620 took 44 s in Blender plus about 25 s of post, per region and zoom.

**The budget (city ≤ 8 ms) is met with room at every view and tier measured here.**

The Deck itself was not measured. Tier 1 at 1280×800 takes 1.3–1.4 ms of GPU on this card. The Deck's
GPU is roughly 8× slower, which by scaling suggests about 10–12 ms. That number is unreliable and
must be measured on a Deck. If it holds, tier 1 should take tier 0's levers, all in config:

- no shadows, which halves the primitives (1.15 M);
- render scale 0.6;
- no fog or rain;
- a coarser facet-row class.

## Calls I made (logged in DECISIONS "Art direction — ART-1 1D city render spike")

- **See-through band in config: lod 1.50–1.595 (ortho about 380–440).** The bible's 1.45–1.75 with
  post40's lod anchors would make the Grid (ortho 440) about 83 % opaque. The bible and round 39 say
  the Grid is solid and the raid is at the locked 0.68. The band was moved so both hold.
- **The ramp band edges include the world light** (N·L 0.118 and 0.363 rather than 0.147 and 0.393).
  The concept's Diffuse→RGB value includes the 0.03 world ambient.
- **The post works on display values, as post40 does.** Bloom and spill come from the screen mips over
  a threshold, standing in for post40's emission-only pass, and Godot's glow is off.
- **The district is the Halcyon border around the references' frame.** The Cell's district keeps the
  street grid (the round 34 lock) and the HQs are stand-ins.
- **Sky lanes run over the district's six busiest avenues** of the game's own streets, rather than
  round 26's hand-placed roads; car colours come from the `city_traffic` stream.

## What ART-5 needs

1. **Production classes** from the spike: `CitySpikeConfig` becomes the city config `.tres`, and
   `CityIsoCamera`, `CityLod`, `CityDistrict` (as `CityModel`, the whole city rather than a district),
   `CityMeshKit` and `CityTraffic` move into `scripts/city3d/` or `scripts/ui/kit/`. The scene becomes
   the one city behind the Grid, raid and netrun views. `NeonCity` and `CityBakeCache` retire, and
   `CityLayout`, the overlays and tests move onto `CityIsoCamera.project` and `CityDistrict.pick`.
2. **Whole-city scale:** 14,100 buildings is about 3.8× this district, so about 8 M primitives with
   shadows. Use the bible's LOD0/LOD1/LOD2 by camera ortho (unit prisms with fewer facet rows outside
   the view) and chunked MultiMeshes per area, so frustum culling works. Today a family is one
   MultiMesh across the district.
3. **The network ground decal** (bible §6.1, `post36.Net36` and `netdecal21`), drawn into the ground
   layer so it shows under see-through buildings, plus x-ray with depth test GREATER at the City Grid.
4. **The five locked HQ heroes** (Blender to glTF through `tools/art_pipeline/`), the Cell's crest
   (red windows), holo billboards, aviation lights, rain and fog per §4.2, Heat props, and the sky-lane
   road shapes (loops, stacks) as baked paths.
5. **1B's shared toon and ink material**, to replace `tools/spike/city/shaders/`. 1B's light-spill
   uniforms should feed the post pass's spill.
6. **Tier 1 measured on a Steam Deck**, with the tier-0 levers ready in config.
7. **Pause and reduce effects:** every ambient layer pauses when the map is covered or the window loses
   focus (§6.1). Reduce effects freezes traffic, rain and fog (the shaders already take a
   `time_scale`).

## Files

- **Logic and tests:** `scripts/city3d/*.gd` and `tests/unit/test_city3d_spike.gd` (fast tier).
- **Real-time 3D:** `tools/spike/city/city_spike_3d.gd/.tscn`, `shaders/*.gdshader` and
  `city_spike_config.tres`.
- **Bake:** `tools/spike/city/export_district.gd/.tscn` (district JSON for Blender),
  `blender/bake_district.py` and `blender/post_bake.py`, and `city_spike_baked.gd/.tscn`.
- **How to run:**
  - capture: `python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://tools/spike/city/city_spike_3d.tscn -- --size=1920x1080 --view=grid --shot=<png> --freeze=1`;
  - perf: `--perf=8 --settle=120 --quality=<0..2>`;
  - bake: export the district, run Blender with `-b --factory-startup --python bake_district.py -- <json> <dir> grid,raid,netrun,close 2880 1620`, then run `python post_bake.py <json> <dir> <views>`.
