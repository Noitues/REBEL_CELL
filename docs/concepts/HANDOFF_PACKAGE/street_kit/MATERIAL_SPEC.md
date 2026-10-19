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
