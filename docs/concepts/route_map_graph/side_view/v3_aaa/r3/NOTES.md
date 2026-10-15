# Route map overview: AAA-2 "Realistic night", revision 3 (2026-10-15)

This round adds real volumetric fog with coloured beams, and a living idle loop. Every r3 look element is now a rule that reads the layout data, not a hand placement.

It uses the same run, layout and camera as r2. The look lives in one preset (`scripts/look_preset.py`), and the placements come from `scripts/rules_r3.py`.

Nothing is committed and the Godot build is untouched. Everything is rendered headless with Blender 5.2.2 and Cycles on the GPU (RX 6700 XT, HIP).

## Files

| File | What it is |
|---|---|
| `AAA2r3.png` | **The still.** 2560 × 1440 with the full frame UI. |
| `plates/AAA2r3_plate.png` | The same still without UI. |
| `fog_compare.jpg` | Four rows, each tile with its luma stats: r2 sky and fog; r3 sky and fog; round 1's coloured cones beside the same r3 region; r2 against r3 on the left (the bank round the mid-row bases). |
| `fog_test_sky.jpg` | The sky test crop sent for review mid-round. It is kept for the record; the final has the fixes below. |
| `idle_loop.mp4` | The idle loop: 1280 × 720, 24 fps, 96 frames (4.00 s), seamless. H.264 (constant rate factor HIGH), 3.3 MB, encoded with Blender's built-in FFmpeg through the sequencer. |
| `idle_loop.gif` | The same loop at 960 × 540, 8.7 MB. It has one shared palette and inter-frame transparency. Delays alternate 40 and 50 ms so the loop lasts exactly 4.00 s. |
| `proof_alt_layout.png` | The procedural proof: another street (build seed 5310) with another district palette (`sodium_teal`), the same preset and no hand edits. Plate, no UI. |
| `scripts/` | Everything needed to rebuild (see "Rebuild"). |

## Review rounds in this revision
1. **First pass:** six `vol_strata` bands, tuned as briefed.
   - Densities ×0.4.
   - The lowest band at z 44, interleaved with the city's depth layers.
   - Six coloured beams.
2. **Art director:**
   - The magenta beams read as flat slabs. Fix:
     - Every beam's full-power light is now light-linked to the fog media only, so a shaft lives where the fog is dense.
     - A faint unlinked twin keeps a thin thread through clear air.
     - Magenta power is cut by about 45 %, and the widest cone is narrowed (5° to 3°).
     - The cyan beams are kept.
   - The strata were barely visible.
3. **Designer:** "the fog lines are looking a little silly". The parallel bands were replaced by one continuous natural field (recipe below).
   - Three sources had cut vertical light pillars into the denser fog:
     - the fog's own emission, integrated through tower gaps;
     - the shadowed city glow;
     - the backglow.
   - Each was fixed: emission went down to 0.12, the city glow is now unshadowed, and the backglow is linked to the back haze only.
4. **Art director, three more notes:**
   - **Left smudge.** The blurred left "slab" was a dark mid-row tower whose silhouette the half-resolution in-scatter had smeared. The still's volume pass is now rendered at full resolution.
   - **Sky lines.** The "sky lane rules" were the neon crown rings of round towers, seen edge-on. A skyline-trim rule now keeps only the camera-facing half, broken into lit runs. The sky traffic also became separate vehicles with a bright head and a fading tail, each at its own angle, with no strobe dots.
   - **Banks.** Fog banks wrapping the building bases and a thin wisp in front of the first far layer were added, both lit from below in the district colours.
5. **Designer standing requirement:** everything must come from rules plus a preset (see "Procedural rules"), proven on another street.

## Task 1: the fog

### Recipe (`fog_r3.py`, numbers in `look_preset.PRESET["fog"]`)
The city fog is **one** heterogeneous Volume Scatter box: x −340..600, y 16..300, z 14..240.

**Density:**
```
peak × floor × top fade × edge fade × hf × [ base × clump + layer × clump × rag ] + bank + wisp
```

**Base terms:**

| Term | Value |
|---|---|
| Peak | 0.021 per BU |
| Base | 0.08 of the peak: the soft body under the layers |
| `hf` (height falloff) | exp(−max(z − 30, 0) / 55): dense low, thinning with altitude |

**Layers.** The layers are a modulation on a warped height coordinate `zw`, not separate stripes:
```
zw = z + 18 × (wave(x, y) − 0.5) + x × 0.07 × (tilt(y) − 0.5)
```
- Each depth gets its own wave and its own wind tilt, so layers bend, merge and split.
- **Warp:** a 4D noise domain warp of ±40 BU along x (scale 80).
- **Two octaves:** banks at (x 0.004, y 0.012, zw 0.075), about 8–15 BU thick, and wisps at (x 0.009, y 0.02, zw 0.33), about 1–3 BU thick. They are mixed 0.62 / 0.38, then smoothstep-remapped 0.47..0.64.
- **Clumps:** low-frequency holes, at scales (0.0075, 0.014, 0.022) and remap 0.40..0.62. No layer runs full width.
- **Rag:** high-frequency ragged edges, a multiplier of 0.45 + 0.75 × noise(0.05, 0.05, zw 0.6).

**Banks:**
- **Mask:** the heightfield's bank map, an image with "near a building but open", blurred by 9 BU: alleys and tower bases.
- **Profile:** a z band from 24 to 38 with a sharp underside and a feathered top.
- **Breakup:** × clumps × rag.
- **Peak:** 0.10.

**Wisp:**
- **Shape:** a Gaussian of thickness 2.6 BU round z = 0.62 × skyline median (97.4 here). It tilts 0.03 per BU and waves ±5 BU.
- **Depth:** only in the depth slab just in front of the first far layer (y 48..64 here).
- **Breakup:** clumped by its own noise.
- **Peak:** 0.20.

**Floor:**
- **General:** 22 BU.
- **Over the decision set:** inside the decision set's view angle (its projected bounds, plus a margin from 0 to 0.07 in tan), the floor rises to the decision rooms' projected top + 5 BU.

**Shading:**
- **Scatter:** colour (0.85, 0.80, 1.0), anisotropy 0.45.
- **Underlight emission:** 0.12 × density × (1 − smoothstep(25, 130, z))² in the district palette along x.

**Other media:**

| Medium | Values |
|---|---|
| Plumes | 4 rooftop vents. Radius 1.2 + 0.28 h, lean 0.35–0.5, height 55–70, turbulent noise, peak 0.09. |
| Ground mist | Over the road (the street transect): z < 5.5, noise streaks, peak 0.016. |
| Back haze | Homogeneous, 0.0016. |

**Glow lights.** All are unshadowed and light-linked to the fog.

| Light | Count and power |
|---|---|
| City glow | 8 area lights, 120 × 60 BU, at 1.6e5 W, at two depths under the fog, spread across the frame |
| Bank under-glows | 4, at 8e4 W |
| Wisp under-glows | 2, at 6e4 W |
| Mist glows | 13 shop-front glows, at 900 W |

**Rain catches the beams:** in the post, each drop's brightness gains 1.6 × the local in-scatter.

**Neon and fog.** Neon meshes and text signs are not seen by volume-scatter rays (`neon_fog`), because their vertical strips cut pillars into the fog. Bloom carries their glow instead.

**Transmittance.** The heterogeneous media's transmittance is a separate Cycles pass (`trans`):
- every surface emits 1 to the camera, the world is white, and translucent things are clear;
- every medium has an absorption-only twin material;
- the post multiplies it with the analytic box transmittance.

### Beams (still)
Placed by the beam rule (see "Procedural rules"). Each beam is a spot light linked to the media, plus a faint unlinked twin; there is no shadow and no housing mesh.

| Rig | Origin (x, y, z) | Cone | Power (W) | Twin |
|---|---|---|---|---|
| Hero A, magenta (district a), left | 19, 29, 75.6 | soft 3.0° + core 0.9° (half-white hot core) | 4.8e7 + 1.32e8 | 0.3 |
| Hero B, cyan (district b), right | 154, 23, 63.6 | soft 4.5° + core 0.9° | 8.4e7 + 2.16e8 | 0.9 |
| Thin, cyan, right | 199, 32, 57.6 | 1.3° | 9.6e7 | 0.9 |
| Thin, amber, left | −71, 80, 53.6 | 1.3° | 9.6e7 | 0.3 |

- **Count:** the preset asks for K = 6. On this street only 4 roofs pass the rule, which requires:
  - off the decision set;
  - on frame;
  - a long visible shaft;
  - at least 45 BU of spacing.
- **Lean:** each beam leans away from the frame centre, 0.12–0.42 sideways and 0.18–0.3 back.

### Numbers (sRGB luma, the critic's measure)

| Image | Median | p95 | % < 0.10 | % > 0.85 |
|---|---|---|---|---|
| r2 plate | 0.138 | 0.725 | 35.5 % | 0.9 % |
| **r3 plate** | **0.140** | **0.690** | **31.4 %** | **0.70 %** |
| r3 with UI | 0.143 | 0.803 | 31.7 % | 3.7 % (the UI whites, as in r2) |
| Loop plate, frames 0 / 48 | 0.133 | — | 34.4 / 34.2 % | 0.76 / 0.74 % |
| Proof plate | 0.152 | 0.708 | 31.9 % | 0.69 % |

**In-scatter over the decision rooms** (still, the volume pass):

| Room | Inside | Ring round it |
|---|---|---|
| Current, L3_2 | 0.0001 | 0.0019 |
| Option 1, L4_0 | 0.0002 | 0.0029 |
| Option 2, L4_1 | 0.0003 | 0.0020 |

For scale, the frame mean is 0.0088 and the sky mean is 0.0189. Nothing is bright behind the decision set.

## Task 2: the idle loop

### How it is rendered (no per-frame denoiser boil)
Light transport is linear in the emitters. So the city is rendered once, only what moves is rendered per frame, and `post_loop.py` sums the layers.

| Layer | Render | When |
|---|---|---|
| `base` | Main pass, 1280 × 720, 128 spp + OIDN; moving things removed, flicker emitters at rest | once |
| `layer_<g>` (11) | Emission-only: the group is the only emitter, and every surface keeps its material, so the group's spill and its puddle reflection come with it. 64 spp + OIDN. | once |
| `vol_static` | The still's own volume pass at 1280 × 720, 48 spp: every medium, no beams | once |
| `beams_full` | The same pass with only the beams | once |
| `trans` | Heterogeneous transmittance | once |
| `dyn_###` | Emission-only: the streak lanes and the spinning globe, with their wet-street reflections. 64 spp + OIDN, fixed seed. | 96 frames |
| `beams_###` | The beams through the homogeneous haze only (cheap, no shader media). 640 × 360, 32 spp + OIDN. | 96 frames |

**Per-frame beam composite:**
```
beams = b(t) × (s + k × τ_fog)
```
- `b` is temporally filtered [1 2 1] / 4, cyclically.
- `s` = 1.107 and `k` = 0.153 are fitted against `beams_full`, so the shafts brighten where they cross the fog.

**Fog drift** is a loop-safe 2D cross-fade scroll:
```
(1 − p) S(sp) + p S(s(p − 1))
```
It moves 26 px per loop (at 1280) at the top of the frame and fades to nothing below 55 % of the height, so the street cones and god rays stay put. The 3D drift is implemented (`set_fog_time`) but not used per frame: see "Limits".

**Rain:** each drop falls a whole number of wraps per loop.

**UI:** the overlay mattes are computed once; the grade, cursor and gloss are applied per frame.

**Loop check** (`scratch/tools/loopcheck.py`; the scratch folder is deleted after delivery):

| Measure | Value |
|---|---|
| Mean frame-to-frame difference | 0.0023 |
| Largest difference | 0.0036, at the seam 95 → 0 |

Frames 94 and 95 are the billboard's designed glitch frames, so the seam is a planned cut. Looking at the frames themselves:
- consecutive frames show no popping and no noise boil;
- the streaks read as traffic;
- the seam crop at 95 → 0 matches.

### Animation list (periods in frames at 24 fps; everything periodic in 96)

| Element | Motion | Period / timing |
|---|---|---|
| Street streak lanes (4) | Ribbons scroll one lane period per loop. Near lanes +x (white / warm), far lanes −x (red). | 96. Periods 300 / 330 / 300 / 270 BU, i.e. 75 / 82.5 / 75 / 67.5 BU/s |
| Sky lanes (3) | Separate vehicles with a bright head and a fading tail, each with its own slope | 96. Periods 360 / 400 / 440 BU (90–110 BU/s); directions +, −, + |
| ORBITAL globe | Spins about its own axis by one longitude spacing; the tilted orbit ring stays still | 22.5° per 96 |
| Beams | Yaw ±4.5–6°, pitch ±¼ of that, each with its own phase | 96 |
| Fog | 2D drift (above) | 96 |
| Rain | 3 layers, a whole number of wraps per drop | 96 |
| Neon, HALCYON (vertical) | Hum: a per-frame gain of 0.86–1.0, with dropouts | Dropouts at frames 30–31 (0.22 / 0.55) and 71 (0.35) |
| Neon, ORBITAL (vertical) | Flicker burst | Frames 52–58 |
| Broken sign, NOODLE 9 (street level) | Stutter sequences and a dead spell | Frames 10–22 and 64–70 |
| Windows (3 cells) | Rare switch-offs | 24–70; 60–96 + 0–6; 40–52 |
| Nav strobes (3 phase groups, 21 beacons) | 2-frame flash at 2.2×, otherwise 0.12 | 24 frames (1 s), phases 0 / 9 / 17 |
| VOLTA billboard | Content cycles to the NOODLE ad and back, with a 2-frame slice / RGB-split glitch at each cut | A: frames 0–45; B: 48–93; glitches 46–47 and 94–95 |
| Holo ads (SOLACE, ORBITAL, HALCYON) | A soft scan band rolls down the panel; 1–2 glitch frames (slice offsets + RGB split) | Rolls per loop: 1 / 2 / 1. Glitch frames 37–38 / 77 / 15–16 |
| Puddles | The streak reflections (per-frame `dyn`); every flicker layer carries its own reflection | — |
| DISPATCH cursor | Block cursor blinks | 24 (12 on / 12 off) |
| Option sticker gloss | A rainbow diagonal sweep, one sticker at a time | Option 1: frames 12–41. Option 2: frames 60–89. |

### Mapping to Godot 4.7

| Element | Godot | Perf notes |
|---|---|---|
| City fog field | **Volumetric fog** (Forward+) with **FogVolume** boxes and a `FogMaterial` shader. Its `density` is computed from the same rules: height falloff, warped-height layer noise from 3D `NoiseTexture3D`s, the bank map as a `Texture2D` sampled at world xz, and the decision-set floor as uniforms. Drift: `TIME` × wind uniform in the noise UV. | Froxel fog resolves the large banks and clumps. The 1–3 BU wisps smear at medium settings: the wisp and the thinnest layers become 1–2 additive cards (as in r1's card recipe). Set `volumetric_fog_length` to about 400, depth slices 64–96. About 1.5–3 ms at 1080p on mid GPUs. VfxTier low: cards only. |
| Beams | **SpotLight3D**, `light_volumetric_fog_energy` 4–8, `spot_angle` 1–4°. Only the heroes get a second wide, soft SpotLight3D. Sweep: an AnimationPlayer (or a script `sin(TIME)`) on rotation. | In fog, a shaft is only visible where the FogVolume density is non-zero, the same "beam follows fog" rule as here. Cost is per light in the froxel pass: 4–6 lights are fine. Shadows off. |
| City glow and bank glows | OmniLight3D / SpotLight3D facing up with `light_volumetric_fog_energy` only. Set `light_energy` 0 or a cull mask, so they light the fog, not the facades. | 8–14 cheap lights with no shadows. |
| Plumes | GPUParticles3D with additive soft billboards, or a small FogVolume with an animated noise density. | Particles: about 60 per vent. |
| Ground mist | A low FogVolume over the road, height falloff 0.4. | — |
| Street and sky streaks | The r2 scrolling-streak lane shader (`TIME` × speed; lane period = speed × loop), unshaded additive. The sky lanes use the "head + fading tail" profile and a per-vehicle slope from the hash. | About 7 draw calls. The SSR / reflection probe picks them up on the wet street. |
| Globe holo | A MeshInstance3D rotated by an AnimationPlayer: 22.5° per 4 s loop, or continuous. | — |
| Neon flicker, broken sign, strobes, windows | One `emission_multiplier` instance uniform per sign, beacon group or window, driven by an AnimationPlayer track or a tiny script from a seeded table, so it is deterministic. The flicker's light spill is an attached OmniLight3D with the same curve. | Instance uniforms: no extra materials. |
| Billboard cycling and holo glitch | The ad shader has two textures with a `mix` uniform, a slice-offset glitch keyed on `floor(TIME × fps)` and a rolling scan band, `fract(UV.y − TIME / T)`. | — |
| Rain | GPUParticles3D streaks near the camera plus a screen-space rain layer. Brightness × the volumetric fog sample is too costly, so the beam brightening uses a mask of the beam cones in screen space instead. | — |
| Puddles | SSR and a reflection probe on the wet street material; they respond to every moving emitter automatically. | — |
| UI cursor and gloss | A Control `modulate` blink (1 s period); the existing `foil.gdshader` `gloss_pos` tween on one sticker at a time. | — |

## Procedural rules (designer requirement)
Every r3 element is placed by a rule from the layout data. Nothing is hand-placed for this street. A new layout plus `look_preset.py` gives the same look.

**Inputs** (`rules_r3.py`, run inside the scene build after the geometry is merged):
- the route layout and the job's room states (which rooms are the decision set);
- the camera pose;
- a **city heightfield**: rays cast straight down every 3 BU over x −200..380 and y 14..320, hitting the solid city meshes only. It gives roof heights and a building mask;
- a **street transect**: rays down across the road at the camera's x.

| Element | Rule | Inputs | Preset keys |
|---|---|---|---|
| Decision calm zone and fog floor | The decision rooms' corners are projected to the view tan range in x and the top elevation tan. Inside that range (+ margin) the fog floor rises to the projected top + margin. | Room states, layout rooms, camera | `fog.floor`, `fog.floor_margin`, `fog.calm_margin` |
| City fog field | Height falloff × warped-height layers × clumps × rag (above) | — | `fog.peak`, `base`, `height_scale`, `warp`, `wave`, `tilt`, `layer_scales`, `layer_mix`, `layer_remap`, `clump_scale`, `clump_remap`, `box_y`, `box_top`, `aniso`, `colour`, `underlight_k`, `wind` |
| Fog banks | Bank map = blur(building mask, reach) × (1 − building mask), as a shader image. Density in a z band, × clumps. | Heightfield | `fog.bank_peak`, `bank_z`, `bank_reach` |
| Wisp | A thin layer at the skyline median × fraction. Its depth slab sits just in front of the first depth where the built share passes 25 %. | Heightfield | `fog.wisp_peak`, `wisp_frac`, `wisp_thick`, `wisp_tilt` |
| Bank and wisp glows | Under the densest smoothed bank spots (spaced 45 BU) and along the wisp. Off the decision set, on frame, colours alternating a / b. | Heightfield, camera | `fog.bank_glow_n`, `bank_glow_w`, `wisp_glow_n`, `wisp_glow_w` |
| City glow | 8 lights at two depths, spread across the frame's view range, alternating a / b | Camera | `cityglow_k` |
| Steam plumes | Candidates: heightfield roof maxima in a z range, plus the route columns' own roofs without a decision room. All must be off the decision angle and on frame. The rule then shuffles the candidates with seed 9510 and picks N, at least 50 BU apart. | Heightfield, layout | `plumes.n`, `peak`, `height`, `lean`, `min_spacing`, `roof_z` |
| Beams | The K tallest non-route roof maxima (local max over 12 BU), filtered: in a y range, off the decision angle, on frame, with a long visible rise above the roof. Then spaced. The tallest on each side of the frame is that side's hero (left = district a, right = district b); the rest take their side's palette. Each leans outward. Seed 9500. | Heightfield, camera | `beams.k`, `heroes`, `min_spacing`, `y_range`, `roof_min`, `min_rise`, `power_k`, `hero_*`, `thin`, `haze_twin*`, `lean`, `lean_y`, `sweep_deg`, `side_colours` |
| Street streak lanes | Road edges come from the transect (z 0.04–0.14), then the centre line. Lanes sit at fractions of each half. | Street geometry | `street_lanes.fractions_near`, `fractions_far`, `len`, `gap`, `periods` |
| Sky lanes | z = skyline median × fraction, at depths from the preset | Heightfield | `sky_lanes.z_frac`, `y`, `len`, `gap`, `slope`, `periods`, `calm_k` |
| Mist and mist glows | The mist box follows the road; glows run along the near kerb at a fixed step | Street geometry | `mist.peak`, `height`, `glow_w`, `glow_step` |
| Skyline trims | A closed neon ring keeps its camera-facing half, broken into lit runs (about 40 %). The skipped facets are still built into a throw-away accumulator, so the shared stream is unchanged. | Every ring trim | (rule; on by default) |
| Flicker and broken signs | Seeded by screen rule: the two largest on-screen text signs off the decision box buzz and flicker; the largest street-level one stutters. | Sign objects, camera | `loop.*` |
| Billboard cycling | The on-screen billboard: the VOLTA arch ad, off the decision box | Ad objects | — |
| Windows | 3 isolated warm window cells in the building band, off the decision box, at least 120 px apart, seed 9601 (2D, from the base emission) | Base emission | `loop.windows` |
| Nav strobes | Every red beacon panel above z 40 on screen, split into 3 phase groups by x order | Neon faces | `loop.strobe_*` |
| Foreground silhouettes | Near-black, only at the frame edges (the r2 near layer, class 0.95). No bright or blurred foreground block. | — | — |
| Grade and value targets | — | — | `post.*`, `targets.*` |

**District palettes:** `look_preset.PALETTES` holds `neon_bay` (the default) and `sodium_teal`. The job key `palette` switches them.

### The proof plate (`proof_alt_layout.png`)
`jobs_aaa.py real final idle ... build_seed=5310 palette="sodium_teal"`. It uses the same preset and the same scripts, with no hand edits.

**The rules re-placed everything:**
- **Skyline:** median 147.7 BU (against 157.1), so the wisp sits at z 91.6.
- **Beams:** 4 rigs, different from the still:
  - hero magenta at (19, 29);
  - cyan at (178, 68);
  - cyan at (154, 23);
  - amber at (1, 74).
- **Plumes:** 4 different vents.
- **Glows:** 6.

**What did not carry over by rule, so would still need manual help on a truly new layout:**
- **r2 dressing is still hand-placed:**
  - the text signs (HALCYON, ORBITAL, SOLACE…);
  - the ad planes and the holo ads;
  - the two megastructures;
  - the drum column (column 5);
  - the stall and alley-light positions.

  These keep their world positions. On this seed they still land on buildings, but a different route graph could leave some of them floating. They are the next items for the toolkit.
- **The wisp is too strong on this street.** It reads stronger here (a bright teal band across the upper frame), because the lower skyline puts it in front of the mid row. The wisp glow should be normalised by the wisp's projected size; noted for the preset.
- **The route graph was not changed;** only the city's build seed was. The route rooms' interiors change with the seed.

## Render times (RX 6700 XT, HIP; Blender 5.2.2)
**BVH:** plain BVH2 for everything this round. HIP-RT's BVH build costs about 86 s per render on this scene. BVH2 builds in seconds: the 1280 test main pass took 11 s against 212 s.

**Still:**

| Pass | Settings | Time |
|---|---|---|
| Cycles main | 2560 × 1440, 128 spp, OIDN | 61 s |
| Cycles volume | 2560 × 1440, 48 spp, OIDN (full resolution, against the blurred-silhouette smudge) | 256 s |
| Transmittance | 2560 × 1440, 32 spp | 9 s |
| Eevee data | — | 7 s |
| Scene build and Blender start | — | about 7 s |
| Post + compose | numpy / PIL | about 38 s |
| **Total** | | **about 6.5 min** |

**Loop:**

| Stage | Detail | Time |
|---|---|---|
| Statics | base 17 s + 14 layers × 8 s + data | 238 s |
| Layers re-render (final) | — | 87 s |
| Static media (`loop_media.py`) | `vol_static` + `beams_full` | 77 + 57 s |
| Beams | 96 frames × 2.1 s | 221 s |
| Dyn | 96 frames × 7.5 s (one 130 s first-frame build) | 745 s |
| **GPU, final pipeline** | | **about 24 min** |
| Post | 96 frames, CPU | 425 s |
| MP4 encode | — | about 10 s |
| GIF encode | — | about 10 s |

**Total loop, about 31 min.** Debugging re-renders added about 7 min of GPU on top; their causes are under "Limits".

**Proof plate:** 370 s render + 40 s post.

## Limits and what I could not do
- **The loop's fog drift is 2D.** Per-frame 3D drift (`set_fog_time` is implemented in every medium's shader) costs about 30 s per frame; the shader updates re-sync the volume. That is about 50 min, over budget.
  - **Splitting the media did not work.** With overlapping volume objects, a light linked to one medium lights only the parts its receivers dominate, so splitting the media changes the look. The drift is therefore applied in 2D to the whole static in-scatter, fading to nothing below 55 % of the frame.
  - **The still's look relies on that linking behaviour.** The Godot fog will not have it; the preset numbers will need one calibration pass there.
- **Windows switch in 2D.** Selecting window quads in 3D for emission layers failed: the merged window mesh's quads are flush with their walls and the camera-visibility test rejected them all. The 2D switch is visually the same, because a window's spill is negligible.
- **Persistent-data pitfall (found and fixed).** Object custom-property changes (`pwo`) do not reach Cycles under persistent data without `update_tag()`. The first layer pass had to be re-rendered.
- **Sky vehicles move horizontally in the loop,** even when tilted. A lane object can only translate; the tilt is small (0.05–0.12).
- **GIF palette:** the shared 255-colour palette shifts a few orange elite stickers toward red. The MP4 is exact.
- **UI resolution:** the loop's UI is the 1080 overlay downscaled to 720; the still's is the 1.33× upscale, as in r2.
- **Beam count:** 4 beams, not 6. The rule found only 4 qualifying roofs on this street; `beams.k` is 6.

## Rebuild
Run from `scripts/`. Blender runs headless and logs to `../scratch/`; nothing launches Godot. (`scratch/` was deleted after delivery: step 1 regenerates the ad textures.)
1. `python emblems20.py`, then `python ads_aaa.py`.
2. **Still:**
   - `python jobs_aaa.py real final idle main,vol,trans,data hiprt=false vol_res=[2560,1440] trans_res=[2560,1440] vol_samples=48`
   - then `python finish_aaa.py still real` and `python fog_compare.py`.
3. **Loop:**
   1. `python loop_jobs.py statics`
   2. `python loop_jobs.py layers`
   3. `python loop_media.py`
   4. `python loop_jobs.py beams`
   5. `python loop_jobs.py dyn`
   6. `python post_loop.py`
   7. `python encode_loop.py mp4` and `python encode_loop.py gifd 3`
4. **Proof:** the still's job with `build_seed=5310 palette="sodium_teal" out=bl_proof`, then `post_aaa.finish("../scratch/bl_proof", "real")`.

**New files:**

| File | Contents |
|---|---|
| `look_preset.py` | The preset |
| `rules_r3.py` | The rules |
| `fog_r3.py` | Media, glows, beams |
| `loop_r3.py` | Loop renders |
| `loop_jobs.py` | Loop job launcher |
| `loop_media.py` | Static loop media through the still's pass |
| `post_loop.py` | Per-frame composite, UI touches |
| `encode_loop.py` | MP4 through the sequencer, GIF |
| `fog_compare.py` | The comparison sheet |

**Changed copies:**

| File | Change |
|---|---|
| `light_aaa.py` | r3 hooks: no street mist box, no white searchlights, back haze 0.0016, `fog_r3.py` exec |
| `fogcards_aaa.py` | The cards are off under r3 |
| `render_aaa.py` | Transmittance pass, `neon_fog`, `vol_hide` / `vol_only_prefix`, `volume_biased` flag, loop hook |
| `post_aaa.py` | Transmittance input, per-frame inputs, loop-safe rain, beam rain, fog glow, the preset's grade |
| `shapes_r2.py` | Streaks built on the rule lanes; head + tail sky vehicles |
| `shapes_lib_r2.py` | The skyline-trim rule |
| `scene_aaa.py` | `build_seed` |
| `jobs_aaa.py` | JSON extras, `out=` |
| `finish_aaa.py` | r3 names |

**Seeds** (the shared build stream 4207 is unchanged; 5310 is the proof's):

| Seed | Use |
|---|---|
| 9402 / 9403+ | Loop lanes |
| 9410 | Still sky vehicles |
| 9500 | Beams |
| 9510 | Plumes |
| 9520 | Glows |
| 9601 | Windows |
| 9700 | Flicker tables |
| 9800 / 9900 | Glitch slices |
