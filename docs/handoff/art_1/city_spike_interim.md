# ART-1 1D: city spike, interim answer for ART-5

This is the early answer for the agents starting the city. The full report, with the side-by-side
crops and all the numbers, is `docs/handoff/art_1/city_spike_report.md`.

## 1. The technique: real-time Godot 3D

My confidence is high. The spike already holds this pick after the fidelity round and the
optimisation round.

**Fidelity.** I built both techniques on the same district and captured them windowed at the grid,
raid and netrun zooms. The real-time version matched the round 39/40 references more closely than the
baked one:

- the three toon bands;
- wobbly ink on every silhouette;
- neon roof trims;
- lane glow;
- see-through buildings at 0.68 opacity over the streets in the raid and netrun views;
- the three car LOD tiers.

**Why baking loses.** The baked layers use the same recipe, so their stills could be tuned closer. The
problem is structural: a bake is one image per view and zoom. The continuous zoom, the raid fit, the
see-through band and the LOD swaps would each need many bakes or a re-bake. The whole city at raid
density comes to about 220 MB per layer.

**Performance.** On this PC, after optimisation:

| Setting | Frame time | GPU time | Draw calls | Texture memory |
|---|---|---|---|---|
| 1920×1080, tier 2 | 2.5–2.8 ms | 2.0–2.3 ms | 31–33 | 106–127 MB |
| Deck tier at 1280×800 | 1.8 ms | — | — | — |

Both are well inside the city's 8 ms budget. The Deck tier has not yet been run on a real Deck.

## 2. What to build against

### Scene structure

There is one `Node3D` city. `tools/spike/city/city_spike_3d.gd` is the working template; it contains:

- a `WorldEnvironment` with no ambient light and no glow, and the sky colour as background;
- one `DirectionalLight3D` key light, whose direction is the config value `to_light`;
- one MultiMeshInstance3D per building family, all sharing one toon/facet ShaderMaterial;
- a ground mesh and a lane-glow mesh, both on render layers 1 and 2;
- the sky-lane cars as three MultiMeshInstance3D nodes, one per LOD tier;
- one orthographic `Camera3D` with `keep_aspect = KEEP_WIDTH`, where `size` is the ortho width;
- a full-screen post quad, a child of the camera, at `render_priority -100`;
- a ground-only SubViewport with a Camera3D whose cull mask is layer 2, at half resolution, which feeds
  the post's `ground_tex`.

### Classes

These are in `scripts/city3d/`, are pure apart from the recorder, and are tested in
`tests/unit/test_city3d_spike.gd`.

- **`CitySpikeConfig`** (a Resource; values in `tools/spike/city/city_spike_config.tres`) holds every
  number. It is to be renamed as the production city config. Its keys:
  - World: `lot_bu` (6), `height_px_bu`, the district.
  - Camera: `yaw_deg` (135), `pitch_deg` (40), `camera_distance`, `views` (target lots and ortho per
    view).
  - LOD: `lod_ortho_*` anchors, `see_through_lod_from/to` (1.50/1.595), `see_through_opacity/dark/chroma`,
    `car_far_above`, `car_close_below`, `lod_hysteresis`, `detail_*_below`.
  - Quality tiers (index = `Settings.city_quality`, Deck = 1): `quality_*` arrays, `ground_pass_scale`,
    `budget_ms`.
  - Buildings: facets, window, ledge and trim values.
  - Toon ramp: `ramp`, `ramp_edges`.
  - Post: ink, haze, bloom, spill, fog, rain and grade values.
  - Traffic: `lane_colors`, `sky_lane_heights`, car gap and speed.
- **`CityIsoCamera`:**
  - `for_view`, `transform()` for the Camera3D;
  - `project` and `unproject` (world to pixel and back);
  - `ray_origin`, `forward`, `lod_of`;
  - `fit(points, margin, lo, hi)` for the raid fit.

  **Every overlay places itself with `project`.**
- **`CityLod`:** `opacity(lod)`, `city_share`, `car_tier(ortho, current)` with hysteresis,
  `detail(ortho, current)`, and `quality(city_quality)`.
- **`CityLayoutRecorder`** (extends NeonCity, placement mode only) reads the game's own layout.
  **`CityDistrict`** turns it into world-space prisms (footprint, `y0`, `h`, taper, ink, territory,
  key, building), street lots, plazas and HQ rects. It also provides `pick` and `pick_building`
  (picking by screen pixel). The production `CityModel` is this, built for the whole city.
- **`CityMeshKit`:**
  - `unit_prism(sides, rows, cols, …)` builds the family meshes. Vertex data: CUSTOM0 holds tone,
    roof and rim; UV is the wall corner; UV2 is the wall edge.
  - `instance_transform(poly, y0, h)` gives the footprint basis, never mirrored.
  - Instance data: `INSTANCE_CUSTOM = (taper, trim ink index + 1, seed, crest)`, and `COLOR` is the
    base colour from `base_color`.
  - `ground_mesh` and `lane_mesh` build the ground and lane glow.
  - `car_mesh(tier)` builds the car tiers.
- **`CityTraffic`:** sky lanes over the busiest avenues; cars from the `RngStreams` stream
  `city_traffic`; `position_at(car, t)`.

### Shaders

These are spike prototypes in `tools/spike/city/shaders/`, to be unified with 1B's `shaders/kit/`
toon and ink material:

- `city_building.gdshader`: the toon `light()`; procedural windows, ledges, shopfronts and roof trim.
- `city_ground.gdshader`: the ground and the lanes, including the 28 % lane gain.
- `city_car.gdshader`: the car tiers, moved in the vertex shader.
- `city_post.gdshader`: the post40 port. It does the see-through composite, ink, grime, spill, bloom,
  fog, haze, rain and grade, all on display values.

### Assets

Use glTF 2.0 through `tools/art_pipeline/` (plan §5.3) for the parts the procedural kit does not make:

- the five HQ heroes;
- props (AC units, tanks, antennas, billboards, uplink pads);
- the low-poly car model;
- landmarks.

Ordinary buildings stay procedural, as MultiMesh unit-prism families taken from the layout table.
**Do not model ordinary buildings.**

### Constraint for overlays

The network decal draws into **render layer 2** (the ground), so that it shows under see-through
buildings. Its x-ray at the City Grid uses a second pass with the depth test set to GREATER. Overlays
read the camera only through `CityIsoCamera`.

## 3. Still open

- **Whole-city scale.** The full city is about 3.8 times this district. It needs chunked MultiMeshes
  per area, so that frustum culling works, and fewer facet rows outside the view: LOD0, LOD1 and LOD2
  by ortho.
- **Steam Deck.** Tier 1 needs measuring on a real Deck. Scaling the PC numbers suggests 10–12 ms there.
  The tier-0 levers are already in config: no shadows, render scale 0.6, no fog or rain.
- **Network ground decal.** Not built yet (`post36.Net36` and `netdecal21`).
- **HQ heroes.** The spike uses stepped stand-ins.
- **Still to build:**
  - the Cell's crest of red windows;
  - holo billboards;
  - aviation lights;
  - the round 26 road shapes (loops and stacks);
  - Heat props;
  - pausing when the map is covered;
  - freezing under reduce effects (the shaders already take a `time_scale`).
- **Designer questions** (DECISIONS, "Open questions"):
  - the see-through band was moved to lod 1.50–1.595 so the Grid is solid and the raid is at 0.68;
  - confirm the 3D pick.
