# Street kit MATERIAL_SPEC: reproducing the golden plates in Godot 4

Source of every number: the street_r2 Blender scripts. Abbreviations for paths (all under `docs/concepts/route_map_graph/`):

- `R2` = `street_r2/scripts/` (r2_scene.py, r2_cycles.py, r2_config.py, r2_jobs.py, r2_build.py, r2_kits.py, r2_rules.py, r2_signs.py, r2_compose.py)
- `SB` = `storyboard/scripts/` (post_aaa.py, look_preset.py, sb_ocjobs.py, sb_cams.py)
- `M44` = `storyboard/scripts/m44/` (target_corps.py, exec'd by r2_scene.py)
- `D:` = `D:/rc_scratch/street_r2/` (render job dump, NOT in the repo; read for the finals job JSON, plan_s1.json and the finals Blender log)

Notation: `file:line`. "Blender default" = not set in code. BU = Blender unit.

## 0. READ FIRST: which look the golden plates are

The golden plates (`golden_plates/street_overview.png`, `street_decision.png`) are copies of `street_r2/plates/01_OVERVIEW_closed_s1_plate.png` and `02_DECISION_closed_s1_plate.png` (golden_plates/INDEX.md table, rows `street_overview`, `street_decision`; capture.json `source.final`). Capture `look` is `aaa2`.

They are NOT the toon + ink look. The pipeline (R2/r2_jobs.py:68-69 `job_block` sets `mode="cycles"`; R2/r2_scene.py:814-815 execs r2_cycles.py) is:

1. Cycles path trace with Principled BSDF surfaces (not toon), real lights, a real volume fog. Every toon material is replaced: R2/r2_cycles.py:112-129.
2. Python post `post_aaa.finish(..., "real", ...)` (R2/r2_compose.py:44-45). The "real" look sets `band=0.0, ink=0.0` (SB/post_aaa.py:37), so there is no toon banding and no ink lines in the plates.
3. The toon ramp (section 1), the facet tone jitter `fj` and the ink (section 2) exist only in the Eevee iteration mode (`python r2_jobs.py eevee`, "geometry only (toon look)", R2/r2_jobs.py:162 and street_r2/NOTES.md:320). They are documented below for completeness, marked EEVEE ONLY.

Implication for Godot: match the Principled + path-traced + fog + post look, not a cel shader. The geometry (jittered triangles, flat shading) carries the "facet grit".

---

## 1. Toon ramp (EEVEE ONLY, not in the plates)

| Field | Value | Source |
|---|---|---|
| Shader chain | Diffuse BSDF (all defaults) -> Shader to RGB -> RGB to BW -> Color Ramp (Fac) | M44/target_corps.py:242-245, 264-266 |
| Light direction feeding the Diffuse | Sun "key", energy 3.2, rotation XYZ (48, -28, -38) deg | M44/target_corps.py:690-695 (the lines `sun_d.energy = 3.2`, `sun.rotation_euler`) |
| Ramp interpolation | CONSTANT | M44/target_corps.py:246 |
| Ramp positions | 0.0, 0.12, 0.32 (3 elements) | M44/target_corps.py:248-250 |
| Number of bands | 3 (hard steps) | same |
| Night ramp colors (shadow, mid, lit) | (0.09, 0.08, 0.21), (0.20, 0.17, 0.36), (0.36, 0.30, 0.54) | M44/target_corps.py:711 (`MODES["night"]["ramp"]`) |
| Tint on ramp | TINT[CORP]; CORP = "meridian" -> (1, 1, 1); each color clamped to 1.0 | R2/r2_scene.py:77; M44/target_corps.py:716-717, 724 |
| Base color multiplication | Mix node (RGBA, MULTIPLY, Factor 1.0): `col` attribute (A) x ramp color (B) | M44/target_corps.py:256-259, 267-268 |
| Per-face tone jitter | Attribute `fj` -> Map Range (From 0..1 is the Blender default) to 0.86..1.12 -> Vector Scale of the product | M44/target_corps.py:253-255, 269-271 |
| Output | Emission node, Strength Blender default 1.0 (unlit, ramp does the lighting) | M44/target_corps.py:262, 272-273 |
| LIT_RAMP (`LITM`) | Copy of TOON plus a second Emission (Color = `col` attribute, Strength 0.42) added through an Add Shader; its ramp colors are copied from RAMP on every `set_mode` | R2/r2_scene.py:557-569, 590-593 |
| Ground in Eevee mode | `GROUNDM = TOON.copy()` | R2/r2_scene.py:554-556 |
| Eevee mode settings | view_transform Standard, taa_render_samples 16 (spec default), filter_size 1.5, world color night (0.03, 0.025, 0.06) | R2/r2_scene.py:686-689; M44/target_corps.py:711 |

What replaces it in the plates: section 4 (Principled).

## 2. Ink

| Field | Value | Source |
|---|---|---|
| Method in the golden plates | NONE. "real" look: `ink=0.0, ink_bg=0.0` | SB/post_aaa.py:37 |
| Inverted hull / Solidify / Freestyle / Line Art in Blender | NOT FOUND. Searched r2_scene.py, r2_cycles.py, r2_build.py, target_corps.py, post_aaa.py for solidify, freestyle, lineart, inverted hull: none. | - |
| Ink in the other looks (cel/hybrid, not used by the plates) | Post edge detect (CPU) on Eevee id / normal / depth passes: edge if id diff > 0.03, normal diff > 0.42, relative depth diff > 0.012; warp by noise amplitude `1.4 * (DW/2560)` px (noise cell 48 px); 3x3 max filter (about 3 px) then box-downsample; color (0.010, 0.008, 0.022); strength cel 0.95 (hybrid 0.62); fades with distance beyond 1.1 x camera dist over 260 units (floor 0.25); suppressed where emission luminance is high. Crease angle: no explicit angle (normal-difference threshold 0.42 on `N*0.5+0.5`, i.e. about a 0.84 change of the unit-normal component). | SB/post_aaa.py:267-292, 29-35 |
| Width in BU / px at 1080p for the plates | 0 (no ink). Pixel scale for the street overview camera (use for any line you add yourself): lens 40 mm on a 36 mm horizontal sensor (R2/r2_cycles.py:917-920; capture.json `camera.lens` 40.0, `dist` 114.6201, `shift_x` -0.0548, `shift_y` 0.1172). Focal length in px = 40 / 36 x 1920 = 2133.3 px. At the target distance 114.62 BU: 2133.3 / 114.62 = 18.61 px per BU. So 1 px = 0.054 BU there, and a 0.1 BU edge is 1.9 px. Decision camera: lens 30 mm, loc (139.52, -24.45, 12.29), tgt (122.61, 13.53, 5.70) (D:job_finals_s1_ov_closed_dec_closed.json), dist = 42.1 BU, focal = 30/36 x 1920 = 1600 px, so 38.0 px per BU. | derived |

## 3. Facet grit / surface noise

The grit is geometry (flat-shaded jittered triangles), not a noise texture. Cycles materials ignore the `fj` jitter attribute; only `col` is read (R2/r2_cycles.py:34-55).

| Field | Value | Source |
|---|---|---|
| Shading | `use_smooth = False` on every polygon (flat) | M44/target_corps.py:102-103 |
| Facade grid (`fgrid`, concrete_band faces seen by the camera, L > 2.0 and h > 3.0) | Quad -> jittered grid of triangles; cell 1.7 BU; nu = clamp(round(width/1.7), 2, 12), nv = clamp(round(height/1.7), 2, 30); interior vertices jittered +-0.28 cell along both edges and +-0.12 BU along the normal; diagonal alternates by (i+j) parity | R2/r2_scene.py:132-162, 205-206 |
| `facet_quad` (other quads) | 4 triangles around a pushed centre vertex; centre at u,v in U(0.3, 0.7), pushed along the normal by U(-0.035, 0.035) x size (0.01 on roofs); only if the longest edge is at least 2.5 BU | M44/target_corps.py:81-93, 129 |
| Per-triangle tone (EEVEE ONLY) | `fj` = patch value 0.5 + (patch - 0.5) x 0.6 + U(-0.4, 0.4) | R2/r2_scene.py:151-162 |
| Per-cell tone (Cycles, kit faces) | colour x U(`cell_tone`) = U(0.8, 1.2), clamped to 1.0 | R2/r2_config.py:60; R2/r2_kits.py:65-67 |
| Per-cell depth relief | up to `cell_relief` 0.22 BU on conc / panel cells; facade inset per floor from the rhythm record | R2/r2_config.py:60; R2/r2_kits.py:62, 99, 129 |
| Concrete base colors | 6 families (0.42,0.40,0.52), (0.38,0.44,0.52), (0.52,0.42,0.40), (0.36,0.42,0.40), (0.48,0.44,0.36), (0.40,0.38,0.46) picked by `abs(key) % 6`; mixed 0.28 toward the terrain color when the building has a terrain tag; roof face x 1.08 | R2/r2_scene.py:107, 176-178, 278 |
| Noise textures on surfaces | None on buildings. The only noise textures are on the ground / plinth roughness (section 7) and in the fog (section 6). | grep of r2_scene.py, r2_cycles.py |
| Roughness of buildings | 0.55 (concrete SURF), see section 4 | R2/r2_cycles.py:34, 102 |
| Drain pipes, ledges, window quads | Pipes: beam 0.14 wide, color (0.22,0.22,0.26), p 0.12 per seen face; ledges every 6 BU (`3.0 * k`, k step 2) of beam width 0.16 colored 0.8 x face color; window quads outset 0.05 BU | R2/r2_scene.py:211-214, 265-270, 232-235 |

## 4. Glass, panel, concrete, lit window, neon materials

All are Cycles materials built in r2_cycles.py. Surface color = `col` face attribute (linear float color) x `alb` (Vector Scale node) -> Principled Base Color. Principled settings not listed are Blender defaults (Metallic 0, IOR 1.5, Coat 0, Transmission 0, Subsurface 0).

| Material | Base color | Metallic | Roughness | Specular IOR Level | Emission | Source |
|---|---|---|---|---|---|---|
| Concrete / default surface `SURF` (oc_surf) | `col` x 0.85 | 0 (default) | 0.55 | 0.5 | none | R2/r2_cycles.py:34-55, 102 |
| Glass `r2_glass` (names ending `_glass` or starting `city_glass`) | `col` x 1.0; glass cell color `GLASS_COL` (0.22, 0.26, 0.34) x tone U(0.8,1.2) | 0.2 | 0.12 | 1.0 | none | R2/r2_cycles.py:138-146, 187-188; R2/r2_kits.py:15, 82 |
| Panel `r2_panel` (`_panel`, `city_panel`) | `col` x 1.0; METAL_COL (0.20, 0.20, 0.24) for mullions / rails | 0.3 | 0.45 | 0.5 | none | R2/r2_cycles.py:147, 189-190; R2/r2_kits.py:16 |
| Dark `r2_dark` (lamp posts, sign frames) | `col` x 1.0; lamp post (0.08, 0.08, 0.1) | 0 | 0.45 | 0.5 | none | R2/r2_cycles.py:148, 191-192, 205-206; R2/r2_build.py:343-344 |
| Lit surface `LITA` (oc_lit) | `col` x 0.85 | 0 | 0.55 | 0.5 | Emission Color = `col`, Strength 0.42 | R2/r2_cycles.py:104 |
| Lit window `WINA` (oc_win) | none (pure Emission) | - | - | - | Color = `col`, Strength `win` = 0.9 | R2/r2_cycles.py:107; D:job `look.win` 0.9 |
| Neon `NEONA` (oc_neon) | none | - | - | - | Color = `col`, Strength `neon` = 1.0 | R2/r2_cycles.py:106; D:job `look.neon` 1.0 |
| Lit room back panel `PANA` (oc_panel, room panels only) | none | - | - | - | Strength `panel` = 4.0 | R2/r2_cycles.py:108, 118-119; D:job `look.panel` 4.0 |
| Ground glow lanes `GLANEA` (oc_glane) | none | - | - | - | Strength neon x lane_dim = 1.0 x 0.5 = 0.5 | R2/r2_cycles.py:109, 120-121; D:job `lane_dim` 0.5 |
| Traffic streak ribbons `LANEM` (oc_lane) / fg streaks `FGLANEM` | none | - | - | - | Strength `lane_k` 2.5 / 2.5 x 0.8 = 2.0 | R2/r2_cycles.py:754, 778; D:job `lane_k` 2.5 |
| Lamp head `r2_lamphead` | none | - | - | - | Color = lamp color, Strength 8.0 | R2/r2_cycles.py:149, 193-194 |
| Sign board (textured), neon shape, megastructure | see section 8 | | | | | |
| Section-clip plinth top (cut near-side blocks) | (a, a, 1.2a) with a = `fill_albedo` 0.045 | 0 | noise 0.32 -> 0.03 (as the ground, section 7) | 0.7 | edge_k 0.0 | R2/r2_build.py:433-465; D:job `plinth` |

Window color pool: `WIN_COLS` = (1.0,0.68,0.28) x2, (1.0,0.8,0.5), (0.45,0.9,1.0), (1.0,0.42,0.72), (0.9,0.9,1.0) (M44/target_corps.py:174). The facade rhythm picks 2 tones per building from `window_tone_pool` (1.0,0.68,0.28), (1.0,0.8,0.5), (0.45,0.9,1.0), (0.9,0.9,1.0), (1.0,0.42,0.72) (R2/r2_config.py:60), each window x U(0.72, 1.0) (R2/r2_scene.py:231, 234). Crest windows (0.95, 0.24, 0.22) (R2/r2_scene.py:112, 230). Glass-curtain lit floors: 22 % of floors, colors (0.78,0.9,1.0) 70 % or (0.55,1.0,0.9), x U(0.5,1.0) (R2/r2_kits.py:75, 88-91). Window material is Emission only, so window brightness in linear = color x 0.9.

## 5. Sky / world

| Field | Value | Source |
|---|---|---|
| Type | A single flat Background color. No gradient, no ramp, no sky texture. | R2/r2_cycles.py:218-222 |
| Color | (0.006, 0.006, 0.014) linear | R2/r2_cycles.py:221 |
| Strength | 1.0 | R2/r2_cycles.py:222 |
| Gradient stops | NOT FOUND (there are none). Searched r2_cycles.py, r2_scene.py for Sky Texture / Gradient / ColorRamp on the world. The only ramps in r2_cycles.py are inside the fog material (section 6). | - |
| Where the sky is visible | Pixels with depth > 5000 are treated as sky by post (`sky = z > 5000`); the visible sky is the world color seen through the fog volume | SB/post_aaa.py:235 |
| Moon | see section 9 | |

## 6. Haze and fog

Volume, not post. One cube (the "oc_fog" object) with a Volume Scatter + a second Volume Scatter (haze) + three Emission volumes. The post has NO fog stage for these plates: `vol_combined.npy` and `trans_combined.npy` are not written by r2_cycles.py (`_exr_npy` only writes combined, emit, albedo, z, index: R2/r2_cycles.py:726-743), so post `vol = 0` and `T = 1`, and the fog is already inside the Combined pass (SB/post_aaa.py:238-241, 301-309).

Final LOOK values (D:job_finals_s1_ov_closed_dec_closed.json `look`; defaults SB/sb_ocjobs.py:36-46 overridden by R2/r2_jobs.py:44-48): `unit_scale S = 3.0`.

| Field | Value | Source |
|---|---|---|
| Fog box | X -700..900, Y -700..900, Z -0.5 .. 80 (top = max(240/S = 80, 2.5 x H_SKY = 71.5)) | R2/r2_cycles.py:664-667 |
| H_FRONT / H_SKY for seed 1 finals | 15.4 / 28.6 BU (computed at build time from roofs: median of frontage roofs, 90th percentile of backdrop roofs) | R2/r2_cycles.py:340-346; D:blender_finals_s1_ov_closed_dec_closed.log "ONECITY heights front 15.4 sky 28.6" |
| Scatter color | (0.88, 0.86, 0.90) for both the layered fog and the haze | R2/r2_config.py:142; R2/r2_jobs.py:47; R2/r2_cycles.py:499, 601 |
| Anisotropy | 0.45 (layered fog), 0.2 (sky haze) | R2/r2_cycles.py:500, 600 |
| Main body density | `body x hf x floor x where x fog_peak x S`; `fog_peak x S` = 0.0507 x 3 = 0.1521 per BU | R2/r2_cycles.py:571; D:job `fog_peak` 0.0507 |
| `hf` (height falloff) | exp(-max(Z - 0.5 H_FRONT, 0) / H_SKY) = exp(-max(Z - 7.7, 0) / 28.6) | R2/r2_cycles.py:554 |
| `floor_` | smoothstep(Z, 0.08 H_FRONT = 1.23, 0.3 H_FRONT = 4.62) (fog thins to zero at the ground) | R2/r2_cycles.py:568 |
| `where` (distance rule) | smoothstep(depth behind the street centre line, 7.0, 17.0) with depth = (Y - 9.0) x nrm_y (street line Y = 9.0, nrm = (0, 1)). So the fog is absent in front of Y = 16 and full from Y = 26. There is no camera-distance falloff; the falloff is by world position. | R2/r2_cycles.py:563-567; D:plan_s1.json `line` 9.0; D:job `nrm` |
| `body` | `clumps x 0.08 + lay x clumps`, then max with `wisp` (wisp_k 1.2) | R2/r2_cycles.py:560-570; D:job `wisp_k` |
| Strata structure | layers 0.42 H_FRONT = 6.5 BU apart on a height warped by noise (+-0.22 H); two 4D noises, banks scale (0.004, 0.012, 0.075) x S and wisps (0.009, 0.02, 0.33) x S, mixed 0.62 / 0.38, remapped (0.47, 0.64); clumps noise (0.0075, 0.014, 0.022) x S remapped (0.40, 0.62); wisp layer at 1.08 H_FRONT, thickness 0.12 H | R2/r2_cycles.py:551-562 |
| Ground bank (fog band on the camera side) | density = `gb_side x gb_z x (0.25 + 0.75 x gb_n) x ground_bank x S` = peak 0.04 x 3 = 0.12 per BU; `gb_z` = 1 - smoothstep(Z, 0.2 x 2.2 = 0.44, 2.2) so the band is full under 0.44 BU and gone at 2.2 BU; `gb_side` = smoothstep of camera-side distance from the centre line, 4.7 .. 8.2 BU (kerb 4.2 + 0.5 .. + 4.0); `gb_n` = noise (0.018, 0.03, 0.25) x S remapped (0.35, 0.68) | R2/r2_cycles.py:576-582; D:job `gb_top` 2.2, `ground_bank` 0.04, `plinth_off` 4.2 |
| Mid banks | `mb_z x where x smoothstep(banks, 0.42, 0.62) x mid_bank x S`; `mb_z` = smoothstep(Z, 0.05 H, 0.15 H) x (1 - smoothstep(Z, 0.5 H, 0.8 H)); peak 0.035 x 3 = 0.105 | R2/r2_cycles.py:583-585; D:job `mid_bank` 0.035 |
| Backdrop haze | smoothstep(depth, 30, 120) x exp(-Z / (2.4 x H_SKY = 68.6)) x back_haze x S = 0.004 x 3 = 0.012 per BU | R2/r2_cycles.py:588-592; R2/r2_config.py:125-127 |
| Sky haze (second scatter) | `haze x S x exp(-max(Z - H_SKY, 0) / 40)` = 0.0014 x 3 = 0.0042 per BU above 28.6 BU | R2/r2_cycles.py:595-599; D:job `haze` 0.0014, `haze_efold` 40 |
| Under-light (fog self-glow) | Emission volume, color = Color Ramp of (warped Z / (2.2 H_FRONT = 33.9)): 0.0 (1.0,0.16,0.6), 0.3 (0.16,0.8,1.0), 0.55 (1.0,0.549,0.102), 0.8 (0.16,0.8,1.0), 1.0 (1.0,0.16,0.6); strength = body density x `underlight_k` 0.07 | R2/r2_cycles.py:605-618; D:plan_s1.json `underlight` [[1.0,0.549,0.102],[1.0,0.16,0.6]]; D:job `underlight_k` |
| Ground-bank glow | Emission volume, ramp (0.3 -> (1.0,0.16,0.6), 0.7 -> (0.16,0.8,1.0)) over noise (0.012, 0.012, 0.05) x S; strength `gb x ground_glow 0.05` | R2/r2_cycles.py:619-630 |
| Mid-bank glow | Emission volume colored by the district bank stops along the street (13 stops, pink / cyan / meridian (1.0,0.549,0.102) / halcyon (0.549,0.482,1.0)); strength `mb x mid_glow 0.3` | R2/r2_cycles.py:631-653; D:plan_s1.json `bank_stops` |
| Steam plumes | 4 volume scatter cubes, color (0.9, 0.88, 0.95), anisotropy 0.3, density `radial x up x noise x plume_k 0.09 x S`; widths r U(1.4, 2.4) BU, heights U(7, 15) BU | R2/r2_cycles.py:798-846; R2/r2_config.py:128-129 |
| Cycles volume settings | volume_bounces 0, step_rate 4.0, max_steps 128 (`max_steps` not in LOOK, so the code default) | R2/r2_cycles.py:702, 705-706; D:job `step_rate` |
| Post fog stage | None for these plates (vol = 0, T = 1, so `vol_k` 1.3 and `vol_glow` do nothing here) | SB/post_aaa.py:301-309, 316-318 |

## 7. Wet ground

| Field | Value | Source |
|---|---|---|
| Material | Principled `oc_wet`: Base Color = `col` x 0.55; Specular IOR Level 0.7; Metallic 0 | R2/r2_cycles.py:70-98 |
| Roughness | Noise Texture (Position, Scale 0.09 x S = 0.27, Detail 5.0) -> Map Range (From 0.45..0.60 to 0.30..0.03), i.e. noise high -> roughness 0.03 (puddle), noise low -> 0.30; Map Range clamp is the Blender default (on). Other Noise Texture inputs Blender default (3D, Roughness 0.5, Lacunarity 2.0, Distortion 0, Normalize on). | R2/r2_cycles.py:83-93 |
| Ground colors (`col`) | asphalt plane z -0.02 (0.20, 0.20, 0.25); plazas mix((0.26,0.25,0.30), terrain, 0.12) at z 0.005; street tiles (0.13, 0.13, 0.16) at z 0.01. After the x 0.55 scale: tile = (0.0715, 0.0715, 0.088) | R2/r2_scene.py:355-362 |
| Lane glow strips on the street | emissive strips color = lane color x (0.10 + trf x 0.16) (wide band, z 0.02), narrow strokes 0.18 BU wide x alpha U(0.55, 0.90) + trf x 0.15 (z 0.04); material strength 0.5 | R2/r2_scene.py:370-381; R2/r2_cycles.py:109 |
| Reflection method | Path-traced glossy reflections of real geometry and lights in Cycles (glossy_bounces 3). No screen-space reflection, no reflection probe, no planar mirror. | R2/r2_cycles.py:699-701 |
| Streak length (post) | NOT FOUND in post (the "real" look has no streak/glare stage; `puddle_blur` is not set so the optional puddle blur is off: SB/post_aaa.py:294-297). The streaks in the plates are geometry: 4 lanes at lane offsets +-0.28, 0.62, -0.30, -0.64 of the half street width 4.0 BU; ribbons z 0.42..0.60 (heads) or 0.50..0.64 (tails), length U(3, 16) BU, gap U(4, 22) BU; head colors (1.0,0.92,0.8), (1.0,0.85,0.6), tail (1.0,0.12,0.08), (0.95,0.15,0.1), each x U(0.5, 1.3); plus 4 foreground lanes at offsets -6.5, -9.5, -13.0, -17.5 BU on the camera side, length U(4, 18), gap U(5, 26), colors (1.0,0.9,0.75) / (1.0,0.14,0.1) x U(0.5, 1.3), emission 2.0; ribbons slide in the animation only (static in plates) | R2/r2_cycles.py:750-796; R2/r2_config.py:118 |
| Lamp pool | No decal / disc. Each kerb lamp is a Point light 60 W, radius (shadow_soft_size) 0.25 BU, at head height 4.5 BU; the pool shape is the inverse-square falloff on the wet road. Colors warm (1.0, 0.72, 0.42) or cool (0.55, 0.85, 1.0) (every third cool); 64 lamps in seed 1 | R2/r2_cycles.py:271-274; R2/r2_rules.py:615-638; D:plan_s1.json (64 lamps); R2/r2_jobs.py:47 `lamp=60.0` |
| Street-level glows (give the puddle highlights) | 93 Point lights (seed 1), 20 W x U(0.6, 1.2), radius 0.6 BU, z 0.9, grid step 9 BU with p 0.55, from the kerb out to 60 BU on the camera side; colors from (1.0,0.62,0.3) x2, (1.0,0.2,0.62), (0.2,0.78,1.0), (0.62,0.38,1.0) + up to 3 district colors | R2/r2_cycles.py:275-296; D:log "ground glows 93"; D:job `ground_lamp` 20 |
| Puddles | Only the roughness noise above (no separate puddle geometry, no height) | R2/r2_cycles.py:83-93 |
| Camera-side plinth tops (the cut blocks in front) | Same wet recipe: noise scale 0.27, Detail 5, Map Range (0.42..0.60 -> 0.32..0.03), spec 0.7, base (0.045, 0.045, 0.054) | R2/r2_build.py:451-466 |

## 8. Sign light spill and sign emission

| Field | Value | Source |
|---|---|---|
| Spill method | No dedicated sign lights. Signs are emissive meshes; spill on walls and the wet road comes from Cycles global illumination (diffuse_bounces 2, max_bounces 6, indirect clamp 6.0) and from a halo baked into the sign texture. | R2/r2_cycles.py:699-704; grep of lights in r2_*.py (all lights are in r2_cycles.py:225-335) |
| Texture halo | `glow(im, k=0.55, r=8)`: image + 0.55 x Gaussian blur radius 8 px, in the sign PNG (texture long side 768 px) | R2/r2_signs.py:45-48, 77, 97 (glow k 0.6 at :97, 0.45 at :128); `size_for` long_px 768 |
| `hero_emit` | 4.0 | R2/r2_config.py:91 |
| `sec_emit` | 2.6 | R2/r2_config.py:91 |
| `shop_emit` | 1.5 | R2/r2_config.py:91 |
| `mega_emit` | 3.0 | R2/r2_config.py:91 |
| `backdrop_emit` | 2.4 | R2/r2_config.py:91 |
| `sign_k` | 1.0 | R2/r2_jobs.py:47 |
| Board material | Emission(texture color, Strength = emit x sign_k) + Glossy BSDF (Color (0.05, 0.05, 0.06), Roughness 0.15) via Add Shader; image interpolation Cubic. "holo" style: Transparent + Emission (additive, no glossy). | R2/r2_cycles.py:153-179, 199 |
| LOD shapes | t1 flat emissive silhouette: Strength round(emit x 0.8, 2) x sign_k; t3 detail rim: emit x 1.2 | R2/r2_cycles.py:200-204 |
| LOD distances (BU from camera) | t1 shape d <= 466, t2 full sign d <= 216, t3 detail d <= 70 | R2/r2_config.py:94-99; R2/r2_cycles.py:852-869 |
| Frames in plates | OVERVIEW: t1 17, t2 52, t3 0; DECISION: t1 0, t2 54, t3 15 | street_r2/plates/plates.json `sign_lod` |
| Megastructure | seed 1 kind "arch", emit 3.0; board = textured emission, neon part = Emission 3.0 x sign_k | D:plan_s1.json `mega`; R2/r2_cycles.py:207-215 |
| Wall light colors that act like sign spill | Facade wash spot per non-route frontage face (section 9), color = building trim color; trim palette = district sign palette (R2/r2_config.py:137-141) | R2/r2_cycles.py:313-324 |

## 9. Lights

Units are Blender light power (Cycles Watts), not lumens. All lights created in R2/r2_cycles.py; the pre-existing lights (the Eevee "key" sun) are hidden from render (:130-133).

| Light | Type | Energy | Color | Shape / angle | Notes | Source |
|---|---|---|---|---|---|---|
| Moon `oc_moon` | SUN | 0.05 | (0.55, 0.62, 1.0) | rot (40, 0, 30) deg, loc z 100 | Blender default angle for the sun disc (not set) | :243 |
| City glow (18 lights: 6 x positions in linspace(street_x0 - 120, x1 + 120) x 3 y at street_y + 40, + 120, - 60) | AREA rectangle | 900 W each (`cityglow`) | alternates the bank-stop district color, (1.0, 0.3, 0.7) and (0.25, 0.75, 1.0) | size 45 x 30 BU, z 2.0, rot (180, 0, 0) i.e. emits up | shadows off; light-linked to the fog volume only (lights haze, not surfaces) | :254-258, 674-676 |
| Room lights | AREA rectangle | 60 W x room width (`room` 60) | room tint | size (max(0.5, w - 0.4), depth x 0.8), rot (180,0,0) | one per room | :259-260; D:job `room` 60 |
| Kerb lamps | POINT | 60 W | warm (1.0,0.72,0.42) / cool (0.55,0.85,1.0) | radius 0.25 | 64 | :271-274 |
| Street-level glows | POINT | 20 W x U(0.6,1.2) | palette | radius 0.6 | 93 | :279-295 |
| Route column wash | SPOT | 1500 W (`wash`) | (1.0,0.16,0.6) / (0.16,0.8,1.0) alternating | cone 70 deg, blend 0.8, radius 0.2 | at street height 0.4, 3.5 BU in front of the face | :297-311 |
| Facade wash (every non-route frontage face) | SPOT | 2400 W (`facade_wash`) | the building's trim color | cone 60 deg, blend 0.9, radius 0.2 | z 0.3, 2.6 BU out, aimed up | :313-324 |
| Section spill (cut near-side frontage) | AREA | 14 W x width x height (`section_spill`) | trim color | width x min(12, top) BU | invisible to camera and glossy rays | :326-335 |
| Beam haze lights (6) | SPOT | 6.0e5 W (`beam`) | pink / cyan / amber (1.0,0.58,0.18) / cyan / pink / violet (0.62,0.38,1.0) | cone 30 deg, blend 1.0 | no shadow; light-linked to fog only; beam length 3.5 x H_FRONT = 54 BU | :348-491 |
| Beam shaft (visible) | emissive cone mesh | Strength `beam_emit` 3.0 x radial/axial profile; hot core x `beam_hot` 0.5 | as above, core pushed toward white (x 0.4 + 0.6) | half angle 6 deg; core sigma 0.13, soft sigma 0.42, soft weight 0.5 (the code default 0.3 is overridden by LOOK 0.5), efold 0.22, gone by 0.6 of length | camera-only (not seen by diffuse, glossy, transmission, shadow rays) | :379-472; D:job |

The seed-1 beam roofs (x, y, z): (99,141,65), (36,99,64), (169,54,49), (144,123,44), (111,30,44), (-83,30,44) (D:log "ONECITY beams").

## 10. Post chain, in order

Run by `post_aaa.finish(rdir, "real", shot, t=13.45, over={exposure})` (R2/r2_compose.py:44-45, 91-93); `t = SB.T["b4"] = 13.45` (SB/sb_cams.py:85-100; used only for the rain fall offset). Render width 1920, so `sc = 1920 / 2560 = 0.75` (SB/post_aaa.py:234). The "real" parameters are `LOOKS["real"]` (SB/post_aaa.py:37-41) updated by `look_preset.PRESET["post"]` (SB/post_aaa.py:396-401; SB/look_preset.py:93): exposure 2.4 (then overridden per plate), vol_k 1.3, vol_soft 0.25, vol_glow 0.8, vol_glow_thr 0.02, rain_vol 1.6.

| # | Stage | Parameters | Source |
|---|---|---|---|
| 0 | Input | Cycles Combined (denoised, linear, includes fog), Emission pass, Albedo pass, Depth. No sem pass exists, so the background-class desaturation / dimming (`bg_desat` 0.30, `bg_dim` 0.6, `bg_emit_cut`) never applies (bgm = 0). Banding: off (band 0). Ink: off. Volume: vol = 0, T = 1. | SB/post_aaa.py:220-250, 256-262, 267, 298-312 |
| 1 | Exposure (linear multiply) | Solved per plate so the median luma of the finished plate is 0.14 (secant, then x0.93 steps until >= 26 % of pixels are under 0.10 as long as median stays >= 0.125; exposure clamp 0.35..2.0). Solved values: OVERVIEW 0.626, DECISION 0.372, OVERVIEW route overlay 0.604, seed 2 0.657. | R2/r2_compose.py:33, 54-87; street_r2/plates/plates.json |
| 2 | Bloom (HDR, added before the tone map) | `hot = max(img - 1.2, 0) + emission x exposure x 0.04`; three Gaussian blurs of `hot` with sigma 6 x sc, 24 x sc, 135 x sc = 4.5 px, 18 px, 101.25 px (computed at 1/2, 1/4, 1/8 resolution); weights 0.12, 0.10, 0.08 added to the image | SB/post_aaa.py:316-322; LOOKS["real"] `bloom` (0.12, 0.10, 0.08), `bloom_thr` 1.2 |
| 3 | Tone map | Hue-preserving max-RGB shoulder: out = c x ACES(m) / m with m = max(r,g,b); ACES fit a=2.51, b=0.03, c=2.43, d=0.59, e=0.14; where m > 3 up to 20 % of the per-channel ACES result is blended in (weight 0.2 x clamp((m - 3) / 2)). This is the only "view transform" the plates have. | SB/post_aaa.py:133-144, 323 |
| 4 | Rain (3 layers, after the tone map) | Layer 1: 4000 drops (x sc), length 3-6 px, alpha 0.05, width 1, speed 0.6. Layer 2: 1800, 14-24 px, 0.10, 1, 1.0. Layer 3: 60, 60-95 px, 0.25, width 3, speed 1.6. Counts and lengths scale by sc. Drop slope: x + 0.2 L over L in y (slightly slanted). Blur sigma 0.6 x sc (width < 3) or 1.6 x sc. Brightness per drop 120..255/255. Rain color `rc` = clip(ACES(blur(img, 30 sc)) x 1.6 + 0.25, 0, 1). Lit factor = clip(0.25 + 2.4 x lum(ACES(b2 + 1.5 b3)), 0.25, 2.2). Reduced to x0.25 over the route rooms and cables. Seeded RNG 41. Fall offset = t x 1400 x sc x speed. | SB/post_aaa.py:43-49, 325-351 |
| 5 | Grade | Shadow tint (0.25, 0.45, 0.6) with k 0.30 weighted by clip(1 - 2.2 lum, 0, 1); highlight tint (1.0, 0.86, 0.86) x 0.25 weighted by clip(2 lum - 0.6, 0, 1); saturation 1.0; lift (0, 0, 0.004) via `out + lift x (1 - out)` | SB/post_aaa.py:352-362; LOOKS["real"] |
| 6 | Vignette (linear, before sRGB) | `out x (1 - 0.38 x clip(r - 0.35, 0, 1)^1.6)`, r = sqrt(((x - W/2)/(W/2))^2 + ((y - H/2)/(H/2))^2) / sqrt(2) | SB/post_aaa.py:363-366 |
| 7 | sRGB encode | Standard piecewise sRGB (12.92 / 1.055 ^ (1/2.4) - 0.055) | SB/post_aaa.py:147-149, 367 |
| 8 | Contrast (in sRGB-encoded values) | `0.18 x (x / 0.18)^1.12` | SB/post_aaa.py:368; LOOKS["real"] `contrast` 1.12 |
| 9 | Display knee | Above 0.66: 0.66 + (0.93 - 0.66) x tanh((x - 0.66) / 0.27), so the plate tops out at 0.93 | SB/post_aaa.py:50, 369-372 |
| 10 | Chromatic aberration | R sampled outward, B inward by `2.4 x sc x clip(r - 0.3, 0, 1)^1.5` px (0 in the middle, 1.8 px max scale) | SB/post_aaa.py:373-381; `ca` 2.4 |
| 11 | Film grain | Gaussian noise, blurred sigma 0.55 x sc, amplitude 0.03 x (1 - 0.6 x lum(out)), seed 107 | SB/post_aaa.py:382-385; `grain` 0.03 |
| - | Glare / star streaks | NOT FOUND. Searched post_aaa.py, r2_compose.py, r2_cycles.py for glare, streak, star, anamorphic. (Bloom is the only glow.) | - |
| - | Bokeh / depth of field | NOT FOUND. No `use_dof` / aperture in r2_*.py or the storyboard scripts; Blender camera DoF default is off. | - |
| - | Color grade LUT | NOT FOUND. The grade is the parametric formula in stage 5. | - |
| - | Blender compositor | NOT FOUND. The EXR multilayer is read raw by numpy (R2/r2_cycles.py:719-721, 726-743). | - |
| - | UI chrome | The golden plates are the "no-UI" plates (golden_plates scripts copy `plates/*_plate.png`); stills with UI are separate | golden_plates/scripts/make_plate.py:3-5 |

Post runs once at 1920 x 1080 after `resize((1920,1080), LANCZOS)`, which is a no-op for a 1920 render (R2/r2_compose.py:91).

## 11. Render

| Field | Value | Source |
|---|---|---|
| Engine | Cycles, GPU (HIP) | R2/r2_cycles.py:679-690 |
| Samples | 40 for the finals (NOTES: `finals 1 ov_closed dec_closed spp=40`; the code default is 48) | street_r2/NOTES.md:42; R2/r2_jobs.py:179; D:job `spp` 40 |
| Adaptive sampling | on, threshold 0.02 | R2/r2_cycles.py:692-693 |
| Denoiser | OpenImageDenoise (with Albedo pass stored) | R2/r2_cycles.py:694-698, 718 |
| Bounces | max 6, diffuse 2, glossy 3, volume 0, transparent 128 | R2/r2_cycles.py:699-703 |
| Indirect clamp | 6.0 (direct clamp: Blender default 0 = off) | R2/r2_cycles.py:704 |
| Seed | 0, animated seed off | R2/r2_cycles.py:707-711 |
| Resolution | 1920 x 1080, 100 % | R2/r2_jobs.py (frames `res` [1920, 1080]); R2/r2_cycles.py:723, 932 |
| Camera | Perspective, sensor_fit HORIZONTAL, sensor width 36, lens 40 (overview) / 30 (decision), shift_x / shift_y from the pose (overview -0.0548 / 0.1172; decision 0.0345 / 0.0002), clip: Blender default | R2/r2_cycles.py:914-922; D:job frames |
| View transform | "Standard" is set, but it does not touch the plates: the render is saved as OPEN_EXR_MULTILAYER 32-bit (scene-linear, no view transform baked), and the plate tone map is the Python tone map in section 10 stage 3. No Filmic / AgX anywhere. | R2/r2_cycles.py:713, 719-721 |
| Look | "None" (set when the scene was created; the scene reset keeps it) | M44/target_corps.py:56 |
| Exposure (Blender color mgmt) | Blender default 0.0 | not set |
| Gamma (Blender color mgmt) | Blender default 1.0 | not set |
| Film filter | Blender default pixel filter width 1.50 px (Eevee mode sets 1.5 explicitly, R2/r2_scene.py:688); Cycles: not set | - |
| Persistent data | on | R2/r2_cycles.py:712 |
| Color space of face colors | Float color attributes (linear). All colors in this document are linear values; Godot materials should take them as linear (not sRGB-encoded) | M44/target_corps.py:69 |
| Mapping of the volume to the output | Volume is part of Combined (no separate pass used) | section 6 |

---

## What makes the look (five things that matter most for parity)

1. **The path-traced light on a dark, wet scene, not a toon shader.** Surfaces are mid-grey-ish Principled materials (concrete 0.55 rough, glass 0.12 rough / 0.2 metal, panel 0.45 / 0.3) that are almost all lit by emissives and colored area / spot lights; the moon is 0.05 and the world is (0.006, 0.006, 0.014). Without strong colored GI from neon, windows and the facade / section-spill washes, the image goes flat black. Build the lighting as colored local lights plus emissive surfaces, not as a sun.
2. **The layered colored fog.** Density 0.152 per BU at the layer cores, forward-scatter (anisotropy 0.45), thinning with height (e-fold 28.6 BU above 7.7 BU), zero in front of the street line, plus a 0.12-per-BU ground band (0 to 2.2 BU) and 0.105 mid banks, all self-glowing in the district palette (pink / cyan / amber / violet) and lit by 18 fog-only area lights and 6 fog-only beam spots. This is what separates the layers of the skyline and hosts the beams; it is a volume, not a flat fade.
3. **The wet street: roughness 0.03 to 0.30 by noise, Specular IOR Level 0.7, tile albedo about 0.07.** The long soft reflections of signs, lamps (60 W warm / cool points), 93 street-level glow points and the geometry streak ribbons (emission 2.5 / 2.0) are what fill the foreground. Reflections must be real or well faked (planar / SSR plus lights), at a roughness that gives bokeh-like soft blobs rather than mirrors.
4. **The emissive hierarchy.** Signs: hero 4.0, secondary 2.6, shop 1.5, backdrop 2.4, megastructure 3.0 (texture color, with a baked glow halo); windows 0.9, neon trims 1.0, lit panels 4.0, lamp heads 8.0, room glows 60 W per BU width. Values are multiplied by face colors that are mostly below 1.0; the peak pixels come from emission, and the bloom (threshold 1.2 after exposure, three radii at 4.5 / 18 / 101 px, weights 0.12 / 0.10 / 0.08) is what makes them glow.
5. **The post tone chain and the exposure solve.** Linear exposure (0.626 overview, 0.372 decision, solved for median luma 0.14), max-RGB hue-preserving ACES shoulder, teal-navy shadow tint (0.25, 0.45, 0.6) at 0.30, warm-pink highlight tint (1.0, 0.86, 0.86), vignette 0.38, contrast 1.12 around 0.18 in sRGB space, a soft knee at 0.66 -> 0.93 ceiling, chromatic aberration 2.4 px at the edges, grain 0.03, and three layers of lit rain streaks. In Godot, tune exposure to the same median luma (0.14, with about 30 % of pixels under 0.10 and under 1 % over 0.85) before judging anything else.


---

# Addendum A: HQ netrun views (golden plates `hq_<corp>_overview` / `hq_<corp>_decision`)

Added 2026-10-19. Since the designer ruling of the same day (DIRECTION_REVIEW, "art-pass owns the Godot look"), this addendum is **art-pass's own working reference for the Godot HQ port (NA-31c)**. It is not a handoff for build to port from. It is the Cycles source of truth. The Godot target is the reachable Eevee twin of each plate (see LOOK_PORT), and Godot results are judged in the parity harness, not against these numbers alone.

Verified: re-posting the saved passes with each corp's `hq_post` reproduces all 12 golden PNGs exactly (mean abs diff 0, script `D:/rc_scratch/art_session/hq_verify.py`).



- `RM` = `route_map_graph/`
- `V3` = `RM/hq_meridian_v3/scripts/` (the shared HQ engine: hq_scene.py, hq_post.py, hq_jobs.py, hq_compose.py, fix_post.py, hq_preset.py (Meridian), look_preset.py, meridian_landmark.py)
- `KIT` = `V3/hq_kit/` (city_ring.py, downtown.py, section.py, states.py, lod.py; byte-identical in hq_meridian, hq_halcyon, hq_orbital, hq_rebel_cell, hq_solace: checked with `diff -rq`)
- `AU` = `RM/hq_aurelian/scripts/` · `HA` = `RM/hq_halcyon/scripts/` · `OR` = `RM/hq_orbital/scripts/` · `RC` = `RM/hq_rebel_cell/scripts/` · `SO` = `RM/hq_solace/scripts/`
- `S3` = `V3/hq_scene.py` · `P3` = `V3/hq_post.py` · `J3` = `V3/hq_jobs.py` · `HP3` = `V3/hq_preset.py` · `LP` = `V3/look_preset.py` (a copy of `RM/storyboard/scripts/look_preset.py`)
- `SB` = `RM/storyboard/scripts/` (post_aaa.py, the street post; compared in section 7)
- `GP` = `golden_plates/` (INDEX.md, `hq_<corp>_<view>_capture.json`, `_values.json`, `scripts/build_all.py`)
- `D:` = `D:/rc_scratch/` (render passes, job dumps; NOT in the repo)

Notation `file:line`. "Blender default" = not set in code. BU = Blender unit; in the HQ scenes 1 storey = 8 BU (the city landmark scale is `k_units` 0.2375, i.e. 1 city BU = 4.21 HQ BU), so HQ densities per BU are NOT comparable with the street's. All colours are linear floats.


---

## A.0. READ FIRST: which look the HQ plates are, and which code made them

`GP/INDEX.md` note 6 (line 57) says `look = aaa2` for the HQ rows. Confirmed: Cycles path trace, Principled BSDF surfaces, a real volume fog, emission, then a Python post. **No toon ramp, no band, no ink stage exists anywhere in the HQ pipeline** (grep of S3, P3, HA hq_scene/hq_post, V3 hq_compose for toon / ink / band / solidify / freestyle / outline: none; the only "band" in P3 is the LOD name `puddles_sharp_at`). See section 8.

Three things differ from the street and matter for a port:

1. **The post is not `post_aaa.finish`.** Each HQ corp has its own `hq_post.py` (a re-implementation "copied below" from post_aaa "real": P3:1-31). It is identical in V3, OR, RC, SO (diff 0 lines) and used by AU in place; `HA/hq_post.py` differs only by an `iris` argument (not used by stills). Section 7 lists every delta.
2. **Exposure is not solved per plate.** It is a preset number x a zoom factor x a hand trim in stops (section 7.1). `ratio_median` (12.2) is a measured result, not a solve target. NOT FOUND: any exposure solver in the HQ scripts (searched `solve`, `secant`, `target` in V3/*.py, HA/hq_*.py, RC/hq_*.py; only `V3/target_values.py` and `V3/hq_values.py`, which measure).
3. **One scene builder, two generations of it** (section 1). Aurelian and Meridian use the newest copy; Orbital, Rebel Cell, Solace use an older copy; Halcyon its own fork.

Blender 5.2.2 LTS, Cycles, GPU (HIP). Source: log tail `RM/hq_*/scratch/bl_stills_final_0.log` ("Blender 5.2.2 LTS (hash d13f752e3b9c ...)"); `S3:1129-1131` (`compute_device_type = "HIP"`, `use_hiprt = False`).

Plate size 2560 x 1440 (`GP/*_capture.json` `resolution`; `J3:31`). The plates are the **no-UI plates** (`H_*_plate.png`, `C3:79-83`); the route overlay is composited after (`C3:84-86`) and is not part of the look.

---

## A.1. Shared vs per-corp

One builder (`hq_scene.py`) + one post (`hq_post.py`) + one shared kit (`KIT`); the per-corp part is `hq_preset.py` (numbers, palette) and a landmark module (geometry + the landmark's own lights). Which scene file each plate came from (`GP/scripts/build_all.py:78-103, 139-142` gives the final PNG and folder):

| Corp (plate source) | Scene file actually executed | Relation to V3 `hq_scene.py` | Source |
|---|---|---|---|
| Meridian (`hq_meridian_v3/plates/H_*_v4_plate.png`) | `V3/hq_scene.py` | the newest copy (v4: mid-scale surface noise in `mat_plain`, per-frame key lights, per-frame light gains, occlusion python twin) | `S3:282-285, 620, 1098-1117` |
| Aurelian (`hq_aurelian/plates/H_*_v2_plate.png`) | `AU/hq_scene.py` = 12-line wrapper that `exec`s `V3/hq_scene.py` in place, after loading the Aurelian preset / graph / landmark first | identical engine, Aurelian modules | `AU/hq_scene.py:1-12`; `AU/aur_env.py:1-12` |
| Orbital (`H_*_v3`) | `OR/hq_scene.py` | V3 minus 34 diff lines: no `n2` mid-scale noise in `mat_plain`, no `EXTRA_LIGHTS` / `light_gain`, no `band_points` guard; `city_sign` x `LH.city_sign_gain` (preset has none, so 1.0) | `diff V3/hq_scene.py OR/hq_scene.py` |
| Rebel Cell (`H_*_v4`) | `RC/hq_scene.py` | V3 minus 45 diff lines: same omissions as Orbital; adds `HZ.room_inner` (0.17,0.14,0.15) and `HZ.room_strip` (1.0,0.72,0.45) for room interiors | `RC/hq_scene.py:561, 576` (via diff) ; `RC/hq_preset.py:115-116` |
| Solace (`H_*_v4`) | `SO/hq_scene.py` | V3 minus 52 diff lines: same omissions; adds `HZ.sky_ramp` (a graded sky, EASE interpolation) | `SO/hq_scene.py:988-997` (via diff); `SO/hq_preset.py:97-98` |
| Halcyon (`H_overview_v3`, `H_decision_E_v3`) | `HA/hq_scene.py` (1617 lines) | its own older fork: same render settings and fog/world code, own compound builder (tiers, podium, **the eye**), v3 material tweaks (see section 3), no `rough` material, an `eye` collection | `HA/hq_scene.py:1513-1560, 1337-1356` |

What differs per corp (everything else is the same code):

| Item | Where it lives | Notes |
|---|---|---|
| Palette (compound colours, district pair, accent) | `PRESET["hq"]["palette"]` (HA: `PRESET["halcyon"]["palette"]`) | section 3.1. The district pair `district_a/b` (neon around the lot, city beams, cityglow) defaults to the street's magenta (1.0,0.16,0.6) / cyan (0.16,0.8,1.0) (`LP:12-13`) unless the corp palette overrides it: only Aurelian does (`AU/hq_preset.py:43-44`). |
| Fog (`hq_fog`) | per-corp dict | section 4 |
| Light gains + landmark rig | `PRESET["hq"]["light"]` + the landmark module's `K.add_light` calls | section 5 |
| City ring / downtown | `PRESET["hq"]["city"]`, `["downtown"]` | seeds, ring radii, `win_p`, `win_k` (window emission scale) |
| Post | `PRESET["post"]` (exposure, knee_top) + `PRESET["hq"]["post"]` (black, exposure_zoom_k; Aurelian also exposure) + `["hq"]["frame_stops"]` | section 7 |
| Camera | `PRESET["hq"]["cam"]`; per-plate poses in `RM/hq_*/scratch/ov_stills.json` | section 2 |
| Landmark geometry / rooms | `meridian_landmark.py`, `aurelian_landmark.py`, `orbital hq_build.py`, `solace hq_build.py` (+ `hq_imap.py`), `rc_*.py` + `hq_build_A.py`, `halcyon` compound in `hq_scene.py` | out of scope here |

---

## A.2. Engine and render settings

Final-quality jobs: `D:/rc_scratch/hq_fix/<corp>/bl_stills/` etc. The job JSONs that survive in `RM/hq_*/scratch/job_stills_final_0.json` are the LAST chunk written (they hold only some frames) but their header keys are the quality dict; they match the code defaults below (job beats code default; here they agree), so the values are as run.

| Field | Value | Source |
|---|---|---|
| Engine | Cycles, GPU (HIP), `use_hiprt` False | S3:1143-1145, 1121-1140 |
| Samples | **64** (Meridian, Orbital, Rebel Cell, Solace, Aurelian); **128** (Halcyon) | job header `RM/hq_{meridian_v3,orbital,rebel_cell,solace,aurelian}/scratch/job_stills_final_0.json` (res 2560x1440, samples 64, threshold 0.015, step_rate 1.2); `RM/hq_halcyon/scratch/job_stills_final_0.json` (samples 128, threshold 0.01, step_rate 1.0); code `J3:31`, `HA/hq_jobs.py:30` |
| Adaptive sampling | on; threshold 0.015 (0.01 Halcyon); min samples min(16, spp) | S3:1147-1149 |
| Denoiser | OpenImageDenoise, input passes RGB_ALBEDO_NORMAL, prefilter ACCURATE, quality HIGH, GPU denoise | S3:1150-1156 |
| Bounces | max 6, diffuse 2, glossy 3, transmission 3, volume **0**, transparent 16 (Aurelian sets 128 per frame: a view ray crosses columns of cut blocks, 16 left a black mast) | S3:1159-1164; AU `aurelian_landmark.py:878-886`; `AU/hq_preset.py:59` |
| Indirect clamp | 6.0 (direct clamp Blender default 0) | S3:1165 |
| Caustics | reflective and refractive off | S3:1166-1167 |
| Light tree | on | S3:1158 |
| Volume | step_rate 1.2 (Halcyon 1.0), max_steps 256 (`JOB.max_steps` absent, code default) | S3:1168-1169; job header |
| Seed | 7 (street: 0) | S3:1157 |
| Resolution | 2560 x 1440, 100 % | job header; S3:1171-1172 |
| Output | OPEN_EXR_MULTILAYER 32-bit; passes Combined (denoised, includes fog), Emission, Object Index, Volume Direct, Depth (Depth is enabled but NOT written to npy). Saved as float16 npy: `combined`, `emit`, `voldir`, `index` | S3:1175-1190, 1252-1253; `exr_to_npy` S3:1193-1214 |
| View transform | "Standard", Look None, exposure 0, gamma 1 (the exr is scene-linear; the tone map is the Python post) | S3:1173-1174 |
| Camera model | Perspective, sensor_fit HORIZONTAL, sensor width 36, clip 0.5 .. 6000, lens / shift per plate (below) | S3:995-1010 |
| Light visibility | EVERY light has `visible_camera = False` | S3:646-649 |
| Object index classes | 0 sky, 1 compound, 2 city, 4 ground, 5 rooms, 6 movers, 7 light streaks (class 3 = Solace apron ring / Rebel MAINFRAME sign quad) | S3:466-485; GP/INDEX.md note 1 |
| Eevee | only a layout preview (`quality eevee`); not the plates | S3:1222-1239; J3:37 |

Cameras (`GP/hq_*_capture.json` `camera`; yaw 0 = north, clockwise; loc/tgt in BU, x east y north z up; sensor 36 mm horizontal):

| Plate | lens (mm) | shift_x | shift_y | loc | tgt | dist |
|---|---|---|---|---|---|---|
| aurelian overview | 36 | -0.0768 | -0.0046 | (-128.57, -347.24, 303.11) | (0, 6, 30) | 464.65 |
| aurelian decision | 42 | -0.0729 | 0.0182 | (53.07, -379.31, 177.90) | (-28.70, -97.77, 8.63) | 338.53 |
| halcyon overview | 40 | -0.0877 | -0.0144 | (370.64, -370.64, 304.15) | (0, 0, 48.5) | 583.19 |
| halcyon decision (E) | 30 | -0.0729 | 0.0023 | (218.53, 11.5, 100.27) | (33.5, 11.5, 50) | 191.74 |
| meridian overview | 36 | -0.0672 | 0.0241 | (-362.49, -517.68, 527.75) | (0, 0, 34) | 801.99 |
| meridian decision | 30 | -0.0729 | 0.0182 | (215.96, -88.96, 87.57) | (115, 12, 23) | 156.70 |
| orbital overview | 36 | -0.0729 | -0.0299 | (-154.20, 267.08, 339.35) | (0, 0, 20) | 443.95 |
| orbital decision | 30 | -0.0729 | 0.0182 | (0, 216.88, 99.96) | (0, 108, 56.6) | 117.19 |
| rebel_cell overview | 30 | -0.1269 | -0.0019 | (-80, -176.97, 145.02) | (-80, 104, 14) | 310.01 |
| rebel_cell decision | 30 | -0.0728 | 0.0225 | (-124, -115.40, 105.14) | (-124, 100.3, 10) | 235.75 |
| solace overview | 34 | -0.0622 | 0.0360 | (-645.92, 235.10, 525.23) | (0, 0, 175) | 771.46 |
| solace decision | 30 | -0.1119 | -0.0306 | (-100.85, 122.43, 187.86) | (0.23, 5.77, 141.65) | 161.12 |

Camera numbers are from the capture files, which `build_all.py:36-46` derives from `RM/hq_<corp>/scratch/ov_stills.json[frame]` (the job pose, checked to 0.3 deg). Aurelian's `GP` decision plate (`H_decision`) is not the `H_decision_inner` frame in the surviving job JSON.

Pixel scale (use for any line you add): focal in px = lens / 36 x 2560. E.g. 30 mm = 2133 px, 36 mm = 2560 px.

---

## A.3. Materials

All Cycles materials are built in `S3` (HA: `HA/hq_scene.py`). Surface colour = the face's `col` float colour attribute (vertex colour) x a procedural factor -> Principled Base Color. Principled inputs not listed are Blender defaults (Metallic 0, IOR 1.5, Transmission 0, Coat 0, Subsurface 0). Emission materials are pure Emission nodes.

### 3.1 Surface materials

| Material (accumulator users) | Base colour | Metallic | Roughness | Specular IOR Level | Coat | Source |
|---|---|---|---|---|---|---|
| `civic` (compound panels: wet composite / concrete / stone) | `col` x k x (0.78 + 0.22 x seam). `k` = (0.88 + 0.16 x grime) x (1 - 0.22 x streak); grime = smoothstep(Noise scale 0.06, detail 4, rough 0.6; 0.30 .. 0.75); streak = smoothstep(Noise scale 0.9, detail 3 on pos x (1,1,0.08); 0.50 .. 0.78); seam = smoothstep(Brick fac, 0 .. 1) of a Brick texture on (x+y, z): scale 1, mortar 0.035, brick width 2.3, row height 1.62 | 0 | 0.16 + 0.22 x streak | 0.5 (default) | weight 0.35, roughness 0.08. Bump: strength 0.25, distance 0.05 from the seam | S3:240-271 |
| `civic` in Halcyon | same, times `ptone` = (0.80 + 0.20 x brick-colour R, brick colours 0.25 / 1.0) x (0.55 + 0.9 x Noise scale 2.6 detail 8 rough 0.7): a per-panel tone (v3, R-REP-1) | 0 | same | 0.5 | same | HA/hq_scene.py:235-278 |
| `cut` (room frames / cut concrete) | via `mat_plain` below | 0 | 0.5 | 0.4 | 0 | S3:445 |
| `interior` (room shells) | `mat_plain` | 0 | 0.35 | 0.5 | 0.2 | S3:446 |
| `metal` | `mat_plain` | **0.7** | 0.32 | 0.6 | 0 | S3:447 |
| `rough` (V3 engine only) | `mat_plain` | 0 | 0.7 | 0.35 | 0 | S3:448 |
| `city_metal` | `mat_plain` | 0.7 | 0.32 | 0.6 | 0 | S3:455 |
| `mat_plain` colour (all above) | `col` x (0.8 + 0.4 x Noise A) with A = Noise scale 0.4 detail 5 rough 0.6 on Position. **V3 engine copies (Meridian, Aurelian) also x (1 + 2.6 x (Noise B - 0.5))**, B = Noise scale 3.5 detail 5 rough 0.7 (v4, R-REP-1). OR / RC / SO / HA do not have the B factor | - | - | - | - | S3:274-292 (B at 282-285); diff in section 1 |
| `glass` (compound glass, Principled, opaque) | `col` | 0 | **0.04** | **0.9** | weight 0.5 (roughness default 0.03) | S3:295-305 |
| `ground` (wet tiles k=1, asphalt k=0) | `col` x tile x (1 - 0.55 x puddle). tile = (1-k) + k x (0.55 + 0.45 x Brick fac), Brick on (x,y): scale 1, mortar 0.04, width 3.0, row 3.0; puddle = smoothstep(Noise scale 0.075 detail 5 rough 0.55 on Position; 0.47 .. 0.55) | 0 | 0.02 + 0.24 x (1 - puddle): **0.02 in puddles, 0.26 dry** | **0.6** | 0 | S3:352-382 |
| `ground` bump | Bump strength 0.08, distance 0.04, height = Noise(scale 2.2, detail 3) x (1 - puddle) + Brick fac x k x 0.6 | | | | | S3:374-381 |
| `city` (the 360-degree towers, downtown) | see 3.3 | 0 | max(0.6 - 0.5 x dark, 0.05) | 0.5 | 0 | S3:385-438 |
| Occlusion poche (cut top of a flattened foreground building) | Diffuse (0.010, 0.010, 0.013) | | | | | KIT/section.py:41, 134-136 |

Wet ground vs the street's: street roughness 0.03 .. 0.30 at noise scale 0.27, spec 0.7 (MATERIAL_SPEC 7); HQ 0.02 .. 0.26 at scale 0.075 (about 3.6x larger puddles per BU, in a 4x smaller BU), spec 0.6, plus tile bump.

Generic ground in the shared engine (the corp landmark may add its own plaza / roads): a 3200 x 3200 slab at z -0.05..-0.02, colour (0.06, 0.06, 0.07), k=0 (asphalt) (S3:698); downtown sidewalk slabs (0.22, 0.22, 0.24), k=1, top at z 0.16 (KIT/downtown.py:107). The square plaza / ring road / perimeter wall (plaza (0.40,0.42,0.45); road (0.055,0.055,0.06); walk (0.30,0.30,0.32); centre dashes (0.55,0.52,0.42) 0.012 high) are built ONLY when the preset has neither `downtown` nor `no_plaza` (S3:688-709): in practice none of the six corps' finals use it (all have `downtown` or `no_plaza`; Halcyon builds its own plaza).

Per-corp palettes (linear; `pal()` looks in the corp palette first, then the street palette):

| Corp | Palette entries that carry the look | Source |
|---|---|---|
| Meridian | steel (0.075,0.037,0.024); steel_alt rust (0.078,0.032,0.021), navy (0.035,0.046,0.056), ochre (0.07,0.049,0.025), oxblood (0.052,0.021,0.021), green-grey (0.025,0.035,0.032); gantry rust-orange (0.30,0.075,0.022); edge sodium-white (1.0,0.80,0.52); stone (0.085,0.075,0.07); keep (0.20,0.19,0.18); corp_orange (1.0,0.26,0.012); corp_red (1.0,0.027,0.02); yard_white (1.0,0.86,0.66); yard_cool (0.62,0.84,1.0); sodium (1.0,0.42,0.09); work (1.0,0.30,0.04); panel (0.30,0.31,0.33); concrete (0.20,0.20,0.21); glass (0.015,0.03,0.035). district_a/b = street magenta/cyan | HP3:60-81 |
| Aurelian | travertine (0.86,0.78,0.62); gilt (0.788,0.639,0.353); loggia (1.0,0.76,0.42); uplight (1.0,0.86,0.66); cavea_fill (1.0,0.90,0.76); server (1.0,0.78,0.40); rim_a verdigris (0.161,0.859,0.651); rim_b (1.0,0.80,0.55); **district_a (0.161,0.859,0.651), district_b (0.788,0.639,0.353), accent_cool (0.45,0.62,1.0), accent_warm (1.0,0.58,0.18)** | AU/hq_preset.py:34-50 |
| Halcyon | civic_white (0.80,0.93,1.0); civic_teal (0.30,1.0,0.86); scan (0.78,1.0,0.97); corp_violet (0.43,0.16,1.0); corp_amber (1.0,0.40,0.03) (the eye); panel (0.40,0.43,0.46); panel_dark (0.20,0.22,0.25); lockdown (1.0,0.05,0.08) | HA/halcyon_preset.py:22-34 |
| Orbital | ice (0.61,0.87,1.0); steel (0.30,0.33,0.37); caution (1.0,0.62,0.0); launch (1.0,0.30,0.06); marker (1.0,0.04,0.03); panel (0.40,0.43,0.46); concrete (0.24,0.25,0.26); glass (0.02,0.04,0.06); pad_albedo (0.06,0.065,0.075); door_albedo (0.11,0.12,0.14) | OR/hq_preset.py:19-28, 54 |
| Rebel Cell | cell_red (0.80,0.007,0.013); red_hot (1.0,0.05,0.07); pale_pink (1.0,0.45,0.48); sodium (1.0,0.45,0.10); neon_a (1.0,0.16,0.6); neon_b (0.16,0.8,1.0); panel_dark (0.14,0.14,0.15); concrete (0.16,0.16,0.17); room_inner (0.17,0.14,0.15); room_strip (1.0,0.72,0.45) | RC/hq_preset.py:21-28, 115-116 |
| Solace | porcelain (0.13,0.15,0.15); leaf (0.30,1.0,0.06); leaf_dim (0.10,0.45,0.04); pink (1.0,0.06,0.28); clinic (0.85,0.97,1.0); frost (0.55,0.75,0.62); glass (0.02,0.06,0.03); panel (0.40,0.43,0.44) | SO/hq_preset.py:20-30 |

### 3.2 Emission materials (all Emission nodes, Color = `col`)

Strength = per-face attribute `k` x per-object weight `pwo` x material factor `k_mat` (1.0 for `emit` and `city_emit`) (S3:308-318). `pwo` is a per-object, per-frame number set in `apply_frame` (S3:1049-1071): the LOD weights below, the room state ladder, and a power cut (not used in the 12 plates: `power` is null for overview and decision, J3:46-52 and the job dump).

| Emission use | Strength (`k`) | Source |
|---|---|---|
| Room ceiling strips (every room) | (0.80, 0.93, 1.0) at k 4.0, two strips at 0.3 d and 0.7 d; Rebel: colour (1.0, 0.72, 0.45) | S3:577-579; RC/hq_preset.py:116 |
| Room back-wall lights by kind | k 3.2 router (4 panels), 4.0 elite (3 racks), 2.6 terminal, 3.0 modem (3 shelves), colour = `TYPE_COL[kind]`: router (0.30,0.85,1.0), elite (1.0,0.36,0.10), terminal (0.20,1.0,0.50), modem (0.30,0.50,1.0), rack (1.0,0.70,0.20), target (1.0,0.22,0.12), start (0.83,1.0,0.0) | S3:491-492, 581-601 |
| Room emission weight by state (`pwo` on `room_<id>`) | option 0.9, target 0.85, current 0.6, reach 0.34, walked 0.32, grey 0.07 (unlisted state 0.3) | KIT/states.py:30; S3:1062-1064 |
| Compound LOD weights (`pwo`) | `sign` = 0.85 x ksig + 0.15; `small` = 0.25 + 0.75 x ksm; city: `city_sign` = ksig; `city_small` = 0.3 + 0.7 x ksm; everything else 1.0. ksig = smoothstep(zoom, 0.60, 0.82); ksm = smoothstep(zoom, 0.75, 0.92). Overview zoom 0 => sign 0.15, small 0.25, city_sign **0**, city_small 0.3. Decision zoom 1 => all 1.0 | S3:1049-1057; LP/KIT lod bands `hq_preset` `lod_bands` (HP3:143-146) |
| City rooftop beacons | (1.0, 0.06, 0.04) at k 10 (city ring), 9 (downtown antennas), 14 (downtown lamp heads: colour (1.0,0.62,0.3) 70 % or (0.85,0.92,1.0)) | KIT/city_ring.py:27, 73; downtown.py:171, 198-199 |
| City crown neon (ring) | district colours at k 4.0 x ring `far` (1.0 / 0.7 / 0.45) | KIT/city_ring.py:68 |
| City blade signs (ring) | district colours at k 5.0 x far; near-ring shop front 0.7 x colour at k 2.2; billboards 0.8 x colour at k 1.6 + text lines (1,1,1) at k 2.0 | KIT/city_ring.py:83, 88, 135, 140 |
| Downtown shop fronts / fascia / blades / crown trims / holo boards | shop 0.8 x `SHOP_COLS` at k U(1.2, 2.4); fascia `SIGN_COLS` k 2.6; blade k U(2, 4); crown trim k 3.0; roof holo 0.55 x colour k 2.4 | KIT/downtown.py:33-35, 221, 225, 238, 150, 179 |
| Traffic streaks (ring road, class 7) | ribbons 0.16 BU high at z 0.55 +- 0.1; head (1.0,0.92,0.82) 70 % / (1.0,0.72,0.45), tail (1.0,0.08,0.05); k U(2.0, 4.5) x (0.15 + 0.85 x fall^1.6) over 6 segments | KIT/city_ring.py:155-162 |
| Downtown streets streaks | same colours, k U(1.5, 3.5), 4 segments, z 0.5..0.65 | KIT/downtown.py:259-269 |
| Sky lanes | (1.0,0.9,0.8) 60 % / (1.0,0.1,0.06), 0.35 BU thick, k 4.0 x f^2, on square loops at half-size `sky_lanes` | KIT/city_ring.py:164-173 |
| Landmark seams / trim / logo / sign | per corp, `LH.seam_k` etc. (section 5.3) | landmark modules |
| Lockdown plane (red holo, an "affected" room) | Transparent / Emission mix; strength (0.25 + pattern) x 3.0 x pwo; not in the 12 plates' route state except where the graph says so | S3:321-349 |

Ghost edge lines of flattened foreground blocks are an Emission of (0.55, 0.68, 0.85) at strength `occ_edge` 0.6 x ghost x edge mask (KIT/section.py:42, 126-136; `OCC.edge` 0.6 at KIT/downtown.py:322). See section 8.

### 3.3 City (towers, downtown): `city` material

| Field | Value | Source |
|---|---|---|
| Base colour | per-tower `col` (0.075,0.07,0.09) 65-70 % or (0.10,0.085,0.09); x grime (0.7 + 0.6 x Noise scale 0.3 detail 6 rough 0.65) x (1 - 0.5 x dark); dark = window cell on and unlit | S3:428-434; KIT/city_ring.py:49; downtown.py:125 |
| Window grid | pitch su = 2.1 along (x + y), sv = 3.1 in z; opening 0.28 .. 0.72 of u, 0.32 .. 0.68 of v (Halcyon: jittered edges +-0.16 per cell) ; vertical faces only (abs(Normal Z) < 0.3) | S3:393-401; HA/hq_scene.py:167-183 (via diff) |
| Lit rule | lit = (floor-noise < 0.5, a white-noise per 23-BU column and storey) x (cell white-noise < face `k` x `win_p` x 2) | S3:411-420 |
| Window colour | warm (1.0, 0.66, 0.40) by default; cool (0.86, 0.92, 1.0) when the cell noise R > 0.78; the district_a colour when R > 0.95 | S3:421-423 |
| Window emission | `win_k` x exp((B - 0.5) x 1.7) x on x lit x pwo (B = cell white-noise blue channel) | S3:424-427 |
| `win_k` / `win_p` final | Meridian 0.34 / 0.36; Aurelian 0.55 / 0.36; Halcyon 0.30 / 0.30; Orbital 0.20 / 0.30; Solace 0.52 / 0.34; Rebel Cell 0.10 / 0.15 (variant A) | HP3:108; AU/hq_preset.py:75; HA/halcyon_preset.py:87; OR/hq_preset.py:71; SO/hq_preset.py:86; RC/hq_preset.py:182 |

### 3.4 Special materials per corp (not in the shared set)

| Corp | Material | Values | Source |
|---|---|---|---|
| Solace (windows) | interior-mapping shader: a virtual box (half width 10, depth 10.5, height 8.4, floor -3.15, window plane depth 1.45) sampling an atlas PNG (rows = lab / greenhouse / ward / dim), Principled base (0.02,0.03,0.03), roughness 0.30, coat 0.4 / 0.10; Emission Color = atlas colour x tint, Strength = (0.10 + 0.9 x lit) x pwo x `imap_k` 0.55 | SO/hq_imap.py:12-17, 129-140; SO/hq_build.py:320-322 |
| Rebel Cell (signs, holos, cloth) | textured quads: Emission(texture, interpolation Cubic) x pwo x k; "holo" mode = Transparent / Emission mix with alpha = max(RGB) x 0.9 (dithered); "cloth" = Principled roughness 0.85 with emission = texture x k | RC/rc_alley3.py:76-120 |
| Halcyon (the eye) | turret + iris emission (`eye_iris` pwo from the frame); gobo spot lights (section 5) | HA/hq_scene.py:1219-1334 |

---

## A.4. World, fog, haze, beams

### 4.1 World

| Field | Value | Source |
|---|---|---|
| Type | Background with a Color Ramp driven by the Z of `Texture Coordinate > Generated` (in a world shader this is the ray direction; NOT verified in Blender, assumed), strength 1.0 | S3:972-994 |
| Ramp stops | 0.0 -> (0.10, 0.035, 0.11); 0.12 -> (0.03, 0.016, 0.055); 0.42 -> (0.004, 0.005, 0.016); interpolation Blender default (Linear) | S3:985-991 |
| Solace override | 4 stops 0.0 (0.035,0.03,0.05), 0.05 (0.028,0.022,0.045), 0.16 (0.012,0.012,0.03), 0.45 (0.003,0.004,0.012), interpolation EASE | SO/hq_preset.py:97-98; SO/hq_scene.py:988-997 |
| Sun / moon | **NONE.** No SUN light in any HQ scene (grep `"SUN"` found only `AU/thumbs.py:386`, a thumbnail tool). Differs from the street, which has a 0.05 W moon. | grep |

### 4.2 Fog volume (one box, Volume Scatter only)

One cube object `fog` with a single Volume Scatter (no second haze scatter, **no emission volumes**; the glow in the fog comes only from lights linked to the media, section 5). Colour `hq_fog.colour`, anisotropy 0.45. Density (per BU) =

`(peak x J.fog_k) x (base + layer x clump x ragk) x hf x (flo x calm) + bank x bank_peak + haze x J.haze_k`

(`J.fog_k` and `J.haze_k` absent -> 1.0). Sources S3:822-886.

| Term | Definition | Source |
|---|---|---|
| warp | Z + 18 x (Noise scale 1.0 on (0.006 x, 0.006 y) - 0.5): the strata wobble | S3:830-835 |
| layer | smoothstep(0.62 x Noise(scale (0.004, 0.012, 0.075) x xyz, on warped Z) + 0.38 x wisp octave, remap `layer_remap` (0.47, 0.64)); the wisp octave (scale (0.009, 0.02, 0.33)) is faded in by zoom `wisps_on_at` (0.45, 0.70): overview has NO wisps | S3:836-849; LP:30-31 |
| clump | smoothstep(Noise scale (0.0075, 0.014, 0.022), remap (0.40, 0.62)) | S3:850-856 |
| ragk | 1 + ko x ((0.45 + 0.75 x Noise scale 0.05) - 1), ko = smoothstep(zoom, 0.25, 0.60) ("ragged edges" fade in with zoom; overview ragk = 1) | S3:857-865 |
| hf | exp(-max(Z - 30, 0) / `height_scale`) | S3:866-867 |
| flo | smoothstep(Z, `floor` - 6, `floor` + 4) (fog thins to zero at the ground) | S3:868 |
| calm | `k` + (1 - `k`) x smoothstep(max(abs x, abs y), `r`, `r` + `soft`): thin over the compound footprint so the landmark stays crisp | S3:870-872 |
| bank | smoothstep(sq, r0 - 10, r0) x (1 - smoothstep(sq, r1, r1 + 10)) x (1 - smoothstep(Z, z0, z1)) x clump, x `bank.peak`: a ring-shaped low ground bank outside the compound | S3:875-879 |
| LOD | zoom is the Value node `ZOOM`, set per frame to the frame's `zoom` (0 overview .. 1 decision) | S3:827-829, 1043-1045 |
| Cycles volume | volume bounces 0, step_rate 1.2, max_steps 256 | section 2 |

Per-corp fog dicts (`hq_fog`; the box is X,Y -N..N, Z 0..top):

| Corp | peak | base | height_scale | floor | box half / top | calm r / soft / k | bank r / z / peak | haze | colour | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| Meridian | 0.0065 | 0.10 | 60 | 10 | 1100 / 300 | 130 / 30 / 0.45 | (150, 260) / (0, 24) / 0.008 | 0.0005 | (0.94, 0.90, 0.88) | HP3:132-140 |
| Aurelian | 0.0055 | 0.10 | 60 | 10 | 1400 / 360 | 170 / 40 / 0.45 | (190, 320) / (0, 24) / 0.007 | 0.0005 | (0.94, 0.90, 0.88) | AU/hq_preset.py:92-100 |
| Halcyon | 0.0065 | 0.10 | 60 | 10 | 1100 / 300 | 105 / 45 / 0.35 | (100, 172) / (0, 9) / 0.012 | 0.0002 | (0.85, 0.82, 1.0) | HA/halcyon_preset.py:98-106 |
| Orbital | 0.0060 | 0.10 | 60 | 10 | 1100 / 300 | 125 / 45 / 0.35 | (125, 175) / (0, 9) / 0.012 | 0.0003 | (0.85, 0.90, 1.0) | OR/hq_preset.py:82-90 |
| Rebel Cell (variant A, finals) | 0.0065 | 0.10 | 60 | 10 | x ±1100, y from 85.6 (the section cut, no fog in front of the kerb) / 300 | 140 / 45 / 0.40 | (190, 300) / (0, 12) / 0.012 | **0.0013** (raised from 0.0003 for depth between the rows) | (0.95, 0.85, 0.90) | RC/hq_preset.py:94-108, 181 |
| Solace | 0.0065 | 0.10 | 70 | 10 | 1100 / 320 | 100 / 40 / 0.10 | (150, 210) / (0, 9) / 0.008 | 0.0006 | (0.86, 0.95, 0.90) | SO/hq_preset.py:101-109 |

Units: to compare with the street, multiply per-HQ-BU densities by 4.21 (about 0.027 per city BU at the peak vs the street's 0.152 per BU).

### 4.3 Plumes

8 Volume Scatter cubes (18 x 18 BU footprint, height U(55, 70) BU, seed 9510) on near-ring roofs at least 90 BU apart. Colour (0.9, 0.88, 1.0), anisotropy 0.4, density = radial x vertical shape x smoothstep(Noise scale 4 detail 6; 0.42 .. 0.70) x 0.09 (`plumes.peak`) x LODK. LODK = smoothstep(zoom, 0.50, 0.72): **no plumes in the overview plates, full in the decision plates**. Sources S3:904-945; LP:45-46; HP3:143-146.

### 4.4 Beams

Not geometry. Each beam is a Spot light: radius 0, blend 0.15, no shadow, **light-linked to the media collection only** (so it lights the fog, never a surface) (S3:961-967). Sky beams exist only as in-scatter in the fog.

| Beam set | Power | Cone | Colour / placement | Source |
|---|---|---|---|---|
| City beams (8 sectors, one per 45 deg on the tallest `mid`-ring roof, leaning radially out) | 1.6e6 x 60 x 0.6 x `city_beam_k` = 5.76e7 x `city_beam_k` (0.8 Meridian / Aurelian / Halcyon / Orbital, 0.7 Rebel, 0.6 Solace) | 1.3 deg | district_a / district_b / accent_warm / accent_cool by sector | KIT/city_ring.py:177-194; LP:50-61 |
| Corp beams (`hooks["beams"]`) | `HZ.beams.power` (Meridian / Aurelian / Halcyon 2.4e7, Orbital 2.6e7, Rebel 2.4e7, Solace 2.0e7) x per-use factor (Meridian keep beacon x1.6 power, x1.3 cone) | `HZ.beams.cone` (1.2, 1.1 Orbital / Rebel / Solace) | landmark crown / spires | HP3:94; meridian_landmark.py:941-942 |
| Halcyon civic searchlights | 3.0e7 W, cone 1.1, lean 0.10-0.34 | tier corners + podium corners | cold white | HA/halcyon_preset.py:64-65; HA/hq_scene.py:1196-1211 |

---

## A.5. Lights

Units are Blender light power (Cycles Watts). Created in `S3` (all go through `add_light`, S3:623-656; every light `visible_camera = False`) and the landmark modules. Group strings control per-frame scaling (S3:1081-1095): `room:<id>` follows the room state; `civic` / `city` / `start` / `corp` are reset to their base each frame.

### 5.1 Lights every HQ gets (engine-level)

| Light | Type | Energy | Colour | Shape / placement rule | Linking / shadow | Source |
|---|---|---|---|---|---|---|
| Room lights (one per route room except `start`) | AREA rectangle | `room_w` x STATE_K[state] x `room_k` (1.0) | 0.55 x TYPE_COL + 0.45 (a pale tint of the room kind) | size (w - 1) x (d - 1.5), at 0.45 d inside, 0.3 below the ceiling, aimed down | shadows on | S3:783-803, 1081-1091 |
| Room light (rooms with no frame: the central server) | POINT | `room_w` x 2 | (1.0, 0.3, 0.15) | radius 2 | on | S3:791-793 |
| Downtown street lamps (nearest `lamp_lights` to the keep, sorted by distance, ties by x,y) | SPOT | `lamp_w` 1800 | (1.0,0.62,0.3) 70 % / (0.85,0.92,1.0) | cone 100 deg, blend 0.9, radius 0.4, aimed straight down, at the lamp head (z 6.0) | no shadow | S3:805-810; KIT/downtown.py:196-200. Count: Meridian / Aurelian 120, Orbital / Solace / Halcyon 70 |
| City glow (8 sectors, radii alternate 430 / 700, z 6) | AREA 110 x 60 | 1.4e5 x `cityglow_k` x `J.glow_k` (1.0) | district_a (even sectors) / district_b (odd) | aimed up (+z), positions `(rad sin az, -rad cos az)` | no shadow; **linked to the media only** | S3:948-952; KIT/city_ring.py:197-204 |
| Bank glow (8, at `bank.r[0]` + 12, z 0.3) | AREA 30 x 14 | `bank_glow` (Meridian 1.0e4, Halcyon 4000, Orbital 3200, Solace 2500, Rebel 2500, Aurelian 1.0e4) | cycle `bank_glow_cols` (Meridian work/sodium, Halcyon teal/civic white, Orbital ice/sodium, Rebel cell_red/sodium, Solace clinic/leaf_dim, Aurelian work/sodium) | aimed up | no shadow; media only | S3:953-959; per-corp presets |
| Shop spill (12 street-level areas) | | `shop_w` | | built only when the preset has no `downtown`: **none of the finals** | | S3:812-818 |
| Beams | SPOT | section 4.4 | | | media only | S3:961-967 |
| Per-frame key lights (V3 engine only: Meridian decision) | SPOT | see 5.2 | | `extra_lights` from `frame_keys`, placed relative to the camera, aimed at a room or a point | `visible_volume_scatter` False (lights the landmark, not the fog in front) | S3:1098-1113; J3:80-88 |
| Per-frame light gains | multiply energy of lights by name prefix | Meridian decision: `wash_` x3, `legup_` x2, `span_down_` x2, `keep_wash` x2, `keep_key` x2 | | | | S3:1114-1117; HP3:124-126 |

### 5.2 Meridian decision key lights (V3 only)

`frame_keys["H_decision"]` (HP3:127-131): lmkey_0 rel camera (0,0,30), aim room `o2`, 1.8e6 W, (1.0,0.80,0.55), size 6, cone 55, blend 0.8; lmkey_1 rel (-40,40,30), aim (40,-100,10), 3.5e6 W, (1.0,0.78,0.5), cone 60; lmkey_2 rel (-60,60,40), aim (-30,-40,14), 3.0e6 W, (1.0,0.82,0.58), cone 75. Check: the surviving job dump `RM/hq_meridian_v3/scratch/job_stills_final_0.json` lists the same three with `light_gain`. Frame exposure trim -1.25 stops balances them (section 7).

### 5.3 The landmark rig per corp (key landmark lights, washes)

Preset values in `PRESET["hq"]["light"]` (final); light creation in the landmark module.

| Corp | Key landmark lights | Notable numbers | Source |
|---|---|---|---|
| Meridian | `legup_s_` / `legup_o_` SPOT cone 40 blend 0.6 at the gantry legs, `leg_up_w` 9.0e4 (x0.6 for the sodium twin); `span_down_` 5 SPOTs under the span, 2.8e4, cone 46, alternate yard_white / sodium; `keep_wash_` 2 SPOTs 6.0e4 cone 40; `keep_key` 5.0e4 cone 22; `lantern` POINT 5000 (1.0,0.42,0.16); `hook_spot` 1.2e4; `rim_0/1` AREA 120x60, 2.0e5, district_a / district_b, **light-linked to the `rim_rx` collection = the compound only**; `wash_s_/wash_` SPOTs 9000 at street height 0.6; `lane_` AREAs 9000; `quay_` SPOTs 3000x1.5; `tflood_` 1.2e5; `railgate_` 6000x3; `train_head` 2.0e6 / `train_glow` 8000; trucks 1500; ring 6000 | trim_k 2.2, seam_k 3.0, logo_k 3.5, sign_k 0.5, cityglow_k 0.25 | HP3:85-93; meridian_landmark.py:258-975 |
| Aurelian | `arena_n` SPOTs (flood_k 0.006 x arena power, blend 0.85); `up_q` 24 SPOTs 450 W, cone 44; `cavea_0/2` AREA 2.5e3 (1.0,0.90,0.76); `vault_key` SPOT 4.0e3 cone 24; `rim_q` AREA 9.0e3 verdigris, linked to `rim_rx`; 40 `cityfill_q` SPOTs 25000 W cone 95 blend 0.8 warm (frame mult overview 0.6, decision 1.45), linked to the city fill collection; `camfill` AREA 60x60 at z 100, 28000 (0.62,0.76,1.0) (same frame mults) | gilt_k 0.6, loggia_k 0.35, cove_k 0.35, server_k 4.0; `ov_loggia` 0.70, `ov_laurel` 0.60 in the overview; `up_frame` decision 0.8 | AU/hq_preset.py:54-62; aurelian_landmark.py:811-870 |
| Halcyon | uplights: SPOT 0.6 radius, `uplight_w` 320, cone 70 blend 0.6, cold white (0.80,0.93,1.0), one per gap between rooms on every face of every tier; plinth washes 400 (cone 60); `gate` POINT 900; the eye: `eye_wash` (2.2e6, cone 150, gobo half-planes, linked to compound + rooms + eye only), `eye_wash_vol` (x0.07, media only), `eye_blade` 9.0e6 cone 120, `eye_beam` 6.0e7 cone 2.2 (+ soft x0.35 cone 6.0, media only), `eye_glow` 6000 POINT. Eye azimuth 45 deg in both plates | cove_k 1.4, teal_k 1.6, slit_k 0.2, sign_k 0.12; cityglow_k 0.15 | HA/halcyon_preset.py:54-71; HA/hq_scene.py:1012-1040, 1219-1334; `RM/hq_halcyon/scratch/ov_stills.json` `eye_az` 45.0 |
| Orbital | `shaft` POINT 1.2e4 (launch orange) + `shaft_beam` SPOT 6.0e6 cone 9 blend 0.4 (media only); `rocket_svc` 2.5e4; `work_<id>` SPOTs flood_w x 0.5 ice, cone 70; `ant_key` 6.0e4 cone 34; `ant_red` POINT 6000; `rim_k` AREA 120x80, 1.4e5, district colours, linked to `rim_rx`; `pad_flood_k` 2.5e4 cone 48; 3 `key_room_` (1.0,0.95,0.88) + 3 `rim_room_` ice SPOTs `room_key_w` 9000 (x0.6), cone 40, re-aimed per frame; `underfog_k` AREAs 1.5e4 ice / sodium at z 0.4, media only | dish_k 3.0, trim_k 2.4, marker_k 14, halo_peak 0.010 | OR/hq_preset.py:51-58; OR/hq_build.py:108-110, 169, 214, 311-313, 340-365 |
| Rebel Cell | `mainframe_spill` AREA 1100 W red (1.0,0.08,0.08) (+ floor x0.35 and shop spill cyan); `alley_lamp_` SPOTs 2600 (1.0,0.72,0.42); `fist_spill`/`fist_glow_` AREAs red; `room_warm_` POINTs 900; `strip_` AREAs 9000 per street strip; `tun_` AREAs 900 green (0.62,1.0,0.72); `sod_`/`roof_` SPOTs `sod_w` 2500; `section_key` AREA 260x60, `key_w` 3.0e4 x 0.8, (0.8,0.82,0.95); `rim_k` AREAs 160x80, `rim_w` 8.0e4, linked to `rim_rx`; `target_wash_1..` AREAs 3000 + `target_room` 1500 around DISPATCH; sewer GREEN spots (lamp 900) | v3 final: `mf_k` 0.62 (MAINFRAME neon), `sign_k` 2.0, `win_k_net` 0.52, `cityglow_k` 0.10, city `win_k` 0.10, `mf_spill_w` 1100, `fist_spill_w` 2500 | RC/hq_preset.py:58-66, 162-190; rc_alley3.py:745-760, 795, 861, 902; hq_build_A.py:165-197 |
| Solace | `down_<tower>` SPOTs `down_w` 600 cone 80 blend 0.9 (slab downlights); `room_<id>` POINTs `room_w` x 0.6; `crown_glow` POINT 2.0e4 pink; `entry_glow` AREA `entry_w` 0.0 (off in finals); `plaza_wash_` AREAs 2.5e3 (1.0,0.78,0.55); `ground_spot_` SPOTs 3.5e4 cone 26 (clinic / (0.75,1.0,0.7)) aimed up the strands, linked to `rim_rx`; `rim_k` AREAs 90x140, `rim_w` 1.0e5, district colours, linked to `rim_rx`; `halofill_` AREAs 4.0e3 clinic, media only | rim_k 0.32 (fresnel rim on strands), porthole_k 0.45, glass_k 2.4, atrium_k 1.6, down_k 1.4, band_k 0.22, bridge_k 1.1, imap_k 0.55 | SO/hq_preset.py:60-73; SO/hq_build.py:316-349, 468, 493, 526, 536, 544, 576 |

Light-linking summary for a port: fog-only (receiver = media): cityglow, bankglow, all beams, Halcyon `eye_wash_vol` / `eye_beam`, Orbital `underfog` / `shaft_beam`, Solace `halofill`. Landmark-only (receiver = `rim_rx` = the compound collection): the rim AREAs, Solace ground spots, Aurelian rims. Everything else is global.

### 5.4 Occlusion (the section cut on foreground city blocks)

Not a light, but it changes what is lit. For every city building, a camera-dependent cut height and ghost opacity is computed (PIPELINE_SPEC 7.1): a building inside the cone from the camera to the route rooms is cut to a lit 6.4 BU stub (`stub`), its open top is the near-black poche, and if the stub still blocks the cone it is dithered to 18 % opacity with a faint cool edge line. Plates: Meridian overview "flattened/ghosted" counts in `RM/hq_meridian_v3/scratch/bl_stills_final_0.log`; per-corp numbers in INDEX.md. Defaults `OCC = margin 0.10, stub 6.4, ghost 0.18, edge 0.6, tsoft 0.035, vsoft 0.025` (KIT/downtown.py:322); Meridian overrides `margin 0.03, vsoft 0.012` (HP3:116), Aurelian `margin 0.10` (AU/hq_preset.py:81). Shader: KIT/section.py:76-171; Godot twin spec in its docstring (KIT/section.py:21-24).

---

## A.6. Ground, plaza, wet surfaces around the compound

| Item | Value | Source |
|---|---|---|
| Ground material | `ground` (3.1): puddle noise scale 0.075, roughness 0.02 / 0.26, spec 0.6, tile Brick 3 x 3 BU for k=1 surfaces | S3:352-382 |
| Base slab | 3200 x 3200, z -0.05 .. -0.02, (0.06, 0.06, 0.07), k 0 (Rebel Cell variant A: starts at `ground_cut_y` = 104 + 0.6 - 18 = 86.6, "no ground in front of the kerb") | S3:698; RC/hq_preset.py:89-90 |
| Downtown blocks | each block on a sidewalk slab (0.22,0.22,0.24) k 1.0 to z 0.16; streets are the gaps (7 BU wide, cell 30) of the base slab; streaks at z 0.5 (section 3.2) | KIT/downtown.py:62-76, 107, 242-270 |
| Street pools | Street-lamp SPOTs (5.1) are the pool source; there are no glow decals and no emissive ground lanes except the streaks (class 7) | S3:805-810 |
| Ground bank | the fog `bank` term (4.2): a ring of low fog just outside the compound lit by the 8 bank-glow areas | S3:875-879, 953-959 |
| Reflections | Cycles glossy bounces 3 (real reflections); post blurs the ground's reflections in the overview (7, stage 2) | S3:1161; P3:105-110 |
| Plaza / ring road / perimeter | NOT built by the engine for these six (all use downtown or `no_plaza`); each corp's landmark module builds its own podium / plaza / roads (e.g. Solace `plaza_wash`, Meridian ring road + lanes, Halcyon plaza) | S3:688; per-corp |

---

## A.7. Post chain

Run by `hq_post.finish(stem, zoom, t=2.0)` (each corp's own preset in memory). Image is 2560 x 1440, so `sc = 1.0` (street: 0.75). `t = 2.0` is the rain fall offset (`C3:79`). Input: Combined (denoised, fog included), Emission, Volume Direct, Object Index (P3:94-102). Order and parameters (P3:94-180), with the delta to the street's `post_aaa` "real" (MATERIAL_SPEC 10):

| # | Stage | HQ parameters | Delta vs street "real" |
|---|---|---|---|
| 0 | Input | `comb`, `emit`, `voldir` (blur 2.0 sc), `idx` (Object Index) | street reads Albedo, Depth; has no Volume pass |
| 1 | Ground reflection LOD | ground = Object Index == 4. k = 1 - smoothstep(zoom, 0.85, 1.00). If k > 0.01: gm = blur(ground, 1 sc) x k x 0.85; img = img x (1 - gm) + blur(img, 3 sc, half-res) x gm. Overview k = 1 (puddles softened), decision k = 0 | NEW: street has `puddle_blur` off |
| 2 | Exposure | `expo = exposure x (1 - exposure_zoom_k x zoom)`, then x 2^stops (7.1) | street: solved per plate to median 0.14 |
| 3 | Bloom (HDR) | hot = max(img - 1.2, 0) + emit x expo x 0.04 + max(voldir - 0.02, 0) x (1.3 x expo x 0.8 x **0.5**); Gaussians sigma 6 / 24 / 135 sc = 6 / 24 / 135 px at half / quarter / eighth resolution; weights 0.12 / 0.10 / 0.08 (Rebel Cell's 0.20/0.17/0.13 with thr 0.9 applies only to the red-sequence variant `HQ_DISTRICT_ONLY`, not to the plates) | street: bloom px = 4.5 / 18 / 101 (sc 0.75), no voldir term (vol = 0), no 0.5 factor. HQ adds the Volume-Direct halo. |
| 4 | Tone map | the same max-RGB hue-preserving ACES shoulder (a=2.51, b=0.03, c=2.43, d=0.59, e=0.14), per-channel ACES blended up to 20 % where max > 3 | same |
| 5 | Rain | the same 3 layers (4000 / 1800 / 60 drops, lengths 3-6 / 14-24 / 60-95 px, alpha 0.05 / 0.10 / 0.25, widths 1 / 1 / 3, speed 0.6 / 1.0 / 1.6), seed 41. Lit factor = (clip(0.25 + 2.4 x lum(ACES(b2 + 1.5 b3)), 0.25, 2.2)) x (0.55 + 0.45 x ksm) + 1.6 x clip(lum(voldir) x 1.3 x expo, 0, 1.5). **ksm = smoothstep(zoom, 0.75, 0.92): overview rain is x0.55, decision x1.0.** No route mask (street cuts rain to x0.25 over the route) | NEW: ksm LOD, voldir term from the Volume pass |
| 6 | Grade | teal-navy shadow tint (0.25, 0.45, 0.6) k 0.30 weighted clip(1 - 2.2 lum); highlight tint (1.0, 0.86, 0.86) x 0.25 weighted clip(2 lum - 0.6); saturation 1.0; lift (0, 0, 0.004) | same |
| 7 | Vignette (linear) | 1 - 0.38 x clip(r - 0.35, 0, 1)^1.6 | same |
| 8 | sRGB encode | piecewise | same |
| 9 | Contrast | 0.18 x (x / 0.18)^1.12 | same |
| 10 | **Black point** | out = (out - black) / (1 - black); black = **0.04** (Halcyon 0.03) | NEW (street none) |
| 11 | Display knee | above 0.66: 0.66 + (top - 0.66) x tanh((x - 0.66) / (top - 0.66)); top = **0.93 default; 0.88 Orbital, 0.87 Rebel Cell, 0.86 Halcyon** (Meridian, Aurelian, Solace default) | street: fixed 0.93 |
| 12 | Chromatic aberration | R out / B in by 2.4 sc x clip(r - 0.3, 0, 1)^1.5 px | same formula; at sc 1.0 the shift is at most 1.4 px at the corner (street, sc 0.75: 1.05 px) |
| 13 | Film grain | Gaussian sigma 0.55 sc, amplitude 0.03 x (1 - 0.6 lum), seed 107 | same |
| - | Lens flash | `flash` argument 0 for stills | n/a on the street |
| - | Bg dimming, `vol_soft`, route mask, sem pass | none | the street has the logic but it is dead for the street plates too |
| - | Bokeh, glare, LUT, Blender compositor | NOT FOUND (searched P3, HA/hq_post.py, C3) | same |

Constants: P3:24-31 (`P = dict(exposure=2.65, bloom=(0.12,0.10,0.08), bloom_thr=1.2, grain=0.03, ca=2.4, vignette=0.38, tint_k=0.30, shadow_tint, hi_tint, sat=1.0, contrast=1.12, vol_k=1.3, vol_glow=0.8, vol_glow_thr=0.02, rain_vol=1.6, lift)`), then `P.update(PRESET["post"])` and `P.update(PRESET["hq"]["post"])` (P3:27-28; Halcyon `PRESET["halcyon"]["post"]`, HA/hq_post.py:27-28).

### 7.1 Per-plate exposure (all 12 verified against the golden PNGs)

Final exposure = `exposure_base x (1 - zoom_k x zoom) x 2^stops` (`C3:76-81`, `fix_post.py:17-26`; `zoom` 0 overview, 1 decision from `ov_stills.json`). The `HQ_EXP_STOPS` env trim exists but is unnecessary: the preset reproduces every plate exactly.

| Corp | exposure_base | zoom_k | black | knee top | Overview stops -> final | Decision stops -> final | Source |
|---|---|---|---|---|---|---|---|
| Aurelian | **1.6** (set in `hq.post`, overrides the 2.85 in `PRESET["post"]`) | **0.0** | 0.04 | 0.93 | -0.08 -> **1.5137** | -0.38 -> **1.2295** | AU/hq_preset.py:88-89, 102 |
| Halcyon | 3.4 | 0.61 | 0.03 | 0.86 | +0.2 -> **3.9056** | 0 -> **1.3260** | HA/halcyon_preset.py:67, 109 |
| Meridian | 2.85 | 0.55 | 0.04 | 0.93 | 0 -> **2.8500** | -1.25 -> **0.5392** | HP3:120, 123, 142 |
| Orbital | 2.4 | 0.40 | 0.04 | 0.88 | +0.06 -> **2.5019** | 0 -> **1.4400** | OR/hq_preset.py:79, 92-93 |
| Rebel Cell | 2.4 | 0.25 | 0.04 | 0.87 | +0.35 -> **3.0589** | +0.2 -> **2.0677** | RC/hq_preset.py:84, 119, 130, 164, 191 |
| Solace | 2.6 | 0.32 | 0.04 | 0.93 | 0 -> **2.6000** | 0 -> **1.7680** | SO/hq_preset.py:95, 111 |

PIPELINE_SPEC line 629 ("Halcyon 3.4 / 0.61, others 2.4 / 0.40") and line 630 ("black 0.04 others") are out of date: only Orbital still has 2.4 / 0.40.

### 7.2 The value targets (not a solve)

`hq_values.py:3-7, 15-38` and `GP/scripts/make_plate.py:44-58`: median luma band 0.11-0.17 (warn 0.09-0.19), share under 0.10 in 0.25-0.40, over 0.85 <= 0.025, and the 12.2 landmark ratio `ratio_median` = median luma of Object Index classes {1,5,6} divided by median of {0,2} inside the landmark's box grown 35 % (pass band 1.5-2.0, warn above 2.0, fail below 1.5; `RATIO_PASS` make_plate.py:48). R-FOCUS-1: landmark box mean luma / ring mean luma >= 1.5. PIPELINE_SPEC 8.3 rule 2 says the ratio is reached **with light, not exposure** (rims, keys, floods); exposure is only trimmed per frame to hold the median. Nothing iterates exposure toward the ratio.

---

## A.8. Anything that is NOT AAA-2 (flagged)

- **No toon, ink, band or facet jitter stage is active in any of the 12 HQ plates.** Checked three ways: no such code in the HQ scene / post, the post is bit-exactly reproduced by the code in this document, and the street's `band`/`ink` keys do not exist in `hq_post.py`. (The street's own Eevee toon mode is also absent here: Eevee is only a layout preview, `S3:1222-1239`.)
- **LOUD:** the post is **not** `post_aaa.finish(..., "real")`. It is a separate copy with the deltas in section 7 (Volume-Direct halo, ground-reflection blur by zoom, black point, per-corp knee top, rain LOD, zoom-dependent exposure). Reproduce `hq_post.py`, not `post_aaa.py`, for the HQ views.
- **LOUD:** several lights are non-physical Cycles tricks that Godot cannot copy as-is: light linking to the media only (cityglow, bank glow, all beams, Halcyon wash_vol, Orbital underfog), light linking to the compound only (`rim_rx` rims), `visible_camera = False` on every light, spot cones of 1.1-1.3 deg at 2.4e7-5.8e7 W used purely as fog shafts (no beam mesh exists), Aurelian's 128 transparent bounces, `visible_volume_scatter = False` on key lights.
- The occlusion shader draws faint cool **edge lines** (emission (0.55, 0.68, 0.85)) on ghosted foreground stubs (KIT/section.py:113-136). It is the only line-like element in the 3D render; it is part of the spec rule (PIPELINE_SPEC 7.1), not ink.
- Not in the plates (do not render): the route overlay, labels, rings, wax links (`hq_compose.compose`, `C3:31-60`), the red lockdown planes when the graph does not ask for them.
- Mixed material generations: Meridian + Aurelian have the mid-scale surface noise (`mat_plain` B factor); Orbital, Rebel Cell, Solace, Halcyon do not. A port should expose it as a per-corp flag, not unify silently.

---

## A.9. What makes the HQ look different from the street (5 things)

1. **No moon, no sun: the light is the landmark.** World is a dim magenta-to-navy ramp (0.10,0.035,0.11 -> 0.004,0.005,0.016), no sun or moon; the HQ is picked out by hand-placed keys, washes and rims (up to 1e5-6e6 W spots) and its own emissives (seams 3.0, logo 3.5, trim 2.2-2.4), with the 360-degree city kept dim (window `win_k` 0.1-0.55, signs off in the overview via LOD).
2. **Thin, long fog lit only by linked lights.** One Volume Scatter box (peak 0.0055-0.0065 per BU, aniso 0.45, e-fold 60-70 BU above 30 BU, `calm` hole over the compound, ground bank ring) with NO emission volume: all glow is in-scatter from 8 city-glow + 8 bank-glow areas and fog-only 1.1-1.3 deg beam spots. Wisps, ragged edges and plumes fade in with `zoom` (overview has none).
3. **Zoom is a render input.** One scalar `zoom` (0 overview .. 1 decision) drives fog octaves, plumes (0.50-0.72), signage (0.60-0.82), small lights (0.75-0.92), rain brightness, ground-reflection blur, and the exposure factor (1 - zoom_k x zoom: decision exposure factor (1 - zoom_k) is 0.39-0.75, Aurelian 1.0).
4. **Hand-set exposure and a black point; no per-plate solve.** Preset exposure 1.6-3.4 x zoom factor x per-frame trim (-1.25 .. +0.35 stops), black point 0.04, knee 0.86-0.93; quality is judged by median / under_010 / `ratio_median`, achieved with light.
5. **Cutaway game rooms and sectioned city.** Route rooms are real lit boxes whose emission and area light follow a state ladder (0.9 / 0.85 / 0.6 / 0.34 / 0.32 / 0.07), and foreground city blocks are flattened to 6.4 BU stubs or ghosted at 18 % by the camera-to-rooms cone, so the rooms are never blocked.

---

## A.10. Per-corp table (plate values: `GP/hq_<corp>_<view>_values.json`)

| Corp | Key colour(s) (linear) | Landmark emissive | Fog tint | Exposure ov / dec | median ov / dec | under 0.10 ov / dec | over 0.85 ov / dec | ratio_median ov / dec |
|---|---|---|---|---|---|---|---|---|
| Aurelian | gilt (0.788,0.639,0.353), loggia (1.0,0.76,0.42), verdigris (0.161,0.859,0.651) as light only | gilt_k 0.6, loggia_k 0.35, cove_k 0.35, server_k 4.0 | (0.94, 0.90, 0.88) | 1.514 / 1.230 | 0.152 / 0.153 | 0.381 / 0.360 | 0.0076 / 0.0047 | 2.460 / 2.792 |
| Halcyon | civic white (0.80,0.93,1.0), teal (0.30,1.0,0.86), amber eye (1.0,0.40,0.03) | cove_k 1.4, teal_k 1.6, slit_k 0.2, eye wash 2.2e6 W | (0.85, 0.82, 1.0) | 3.906 / 1.326 | 0.127 / 0.155 | 0.388 / 0.331 | 0.0022 / 0.0029 | 2.622 / 2.352 |
| Meridian | corp orange (1.0,0.26,0.012), edge sodium-white (1.0,0.80,0.52), rust gantry (0.30,0.075,0.022) | seam_k 3.0, logo_k 3.5, trim_k 2.2, keys 1.8e6-3.5e6 W (decision) | (0.94, 0.90, 0.88) | 2.850 / 0.539 | 0.138 / 0.166 | 0.361 / 0.314 | 0.0178 / 0.0174 | 2.418 / **1.802** |
| Orbital | ice (0.61,0.87,1.0), launch (1.0,0.30,0.06), marker red (1.0,0.04,0.03) | trim_k 2.4, dish_k 3.0, marker_k 14, shaft 1.2e4 W + 6e6 W beam | (0.85, 0.90, 1.0) | 2.502 / 1.440 | 0.130 / 0.128 | 0.366 / 0.392 | 0.0078 / 0.0159 | 3.842 / 3.500 |
| Rebel Cell | cell red (0.80,0.007,0.013), red hot (1.0,0.05,0.07), sodium (1.0,0.45,0.10) | MAINFRAME `mf_k` 0.62 (red neon), `sign_k` 2.0, mf_spill 1100 W | (0.95, 0.85, 0.90) | 3.059 / 2.068 | 0.140 / 0.162 | 0.375 / 0.341 | 0.0183 / 0.0194 | 1.816 / 1.958 |
| Solace | leaf (0.30,1.0,0.06), clinic (0.85,0.97,1.0), pink (1.0,0.06,0.28) | rim_k 0.32, porthole_k 0.45, glass_k 2.4, imap_k 0.55 | (0.86, 0.95, 0.90) | 2.600 / 1.768 | 0.127 / 0.121 | 0.374 / 0.349 | 0.0073 / 0.0205 | 2.555 / 2.573 |

R-FOCUS-1 (landmark / ring mean luma): Aurelian 1.90 / 2.26, Halcyon 2.63 / 1.70, Meridian 1.63 / 2.70, Orbital 2.19 / 1.54, Rebel Cell n/a (box fills the frame), Solace 1.55 / 1.76 (`GP/*_values.json` `composition.R-FOCUS-1`). `ratio_mean` and `ratio_peak` are also in the values files (e.g. Meridian decision 2.42 / 8.27).

---

## A.NOT FOUND (what I searched)

- Exposure solver for the HQ plates: searched `solve|secant|target` in V3/*.py, HA/hq_*.py, RC/hq_*.py; only measuring tools (`hq_values.py`, `target_values.py`, `hq_tune.py` which prints stats for trial post keys).
- Halcyon eye azimuth sweep / blade height per plate: `ov_stills.json` stores `eye_az` 45.0 for both plates; the blade `sweep` z comes from `HA/hq_jobs.py:55-63` at job time and is not stored (the surviving job dump holds only `H_hover_S`).
- `World` "Generated" coordinate semantics (ray direction in a world shader): assumed, not checked in Blender (Blender not run).
- Bokeh / DoF, glare, LUT, compositor: none (searched hq_post, hq_compose, hq_scene).
- Per-frame job JSONs for all final frames: only the last chunk is kept in the repo scratch; values were taken from presets and confirmed by the bit-exact re-post.
