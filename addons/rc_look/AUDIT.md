# rc_look Phase 0 audit (2026-10-21, art/look-toolbox @ 7ecf49f0)

Read-only audit of the look code against ART_BIBLE §1.2, DIRECTION_REVIEW (newer rulings win), LOOK_PORT and the
golden plates. No code changed.

Evidence (not committed, scratch):
- Inventory: Haiku lane, summarised in the table below. Raw counts come from `wc -l` and `git diff --no-index --numstat`.
- Captures of today's look, all 1920x1080 via `run_windowed.py` @ 7ecf49f0: `D:/rc_scratch/rc_look/audit/shots/` (33 PNGs,
  `INDEX.md` holds the exact commands).
- Golden | Godot pairs: `D:/rc_scratch/rc_look/audit/pairs/{street_overview,street_decision,city_night,city_day,hq_<corp>}.jpg`
  (`D:/rc_scratch/rc_look/tools/pair_sheet.py`). The cameras are **not** matched (LOOK_PORT §7 finding 1), so these pairs
  show the look gap only, not parity.

## Headline findings

1. **The 2D media are further along than the brief assumed.** Grease pencil is already one engine (`GreasePencilMark`
   + `marker_stroke.gdshader`, 36 users). It already has wax at 0.96, dropouts, sheen, under-shadow, trim write-on, cloth
   wipe, seeded hash wobble and a `PencilLint` group for the "never covered" rule. Of the brief's ten pencil files, nine
   are callers of that engine. Only `hand_marks.gd` draws raw lines. The sticker sweep scheduler exists too
   (`StickerSweepQueue`). So the 2D work is look polish and closing gaps, not consolidation.
2. **The big gap is the 3D world** (city map, raid map, combat backdrop, street/route, HQ run). Nothing uses a
   `CompositorEffect`, `FogVolume` or `ReflectionProbe`. Ink, grade and bloom each live in a per-view spatial post
   (`city_post`, 455 lines, reads depth and normal-roughness). The HQ run is still on the cel spike shader
   (`tools/art_pipeline/city/hq_compound_toon.gdshader`), against AAA-2 plates. Shaders hold about 202 colour literals
   across 45 files, none fed from `Palette`.
3. **The two world looks** (cel at map zoom, AAA-2 "Realistic night" for netrun, route and HQ; `set_look_blend`) are
   not in the brief's 18 areas. Every world module (areas 4-9) has to serve both, or the designer rules on which looks
   it serves.
4. **The perf gate is already red.** The street is at 19.4 / 18.3 ms p95 against 16.7 ms (LOOK_PORT §7b), so every
   world module needs its cheap tier before it can add cost.
5. **Lane overlap with art-pass L4/L5.** The world modules touch the same files as the art-pass per-view parity loop
   (`city_post`, `netrun_shader_kit*`, `street_light_rig`, `route_rig`, `city_view_3d`). The two need one owner per file
   at a time.

## Per area

"Views" counts the distinct views that share the area (3D: city map, raid map, combat backdrop, street/route, HQ run,
title/menu backdrop; 2D: combat, raid, route, grid, HQ page, shop/loot, pause/campaign end, title). Gap is scored 1-5
from the captures. Score = views × gap.

| # | Area | Files today (main) | Views | Duplicates / drift | Gap vs plate / concept (screenshot) | Gap | Score |
|---|---|---|---|---|---|---|---|
| 1 | Shader lib + tokens | `shaders/lib/rc_common` (36 lines, ~40 includers), `netrun_clock`, `palette.gd` (663), `ui_theme.gd` | all | ~202 vec3/vec4 colour literals in 45 shaders; corp palette debt (§2.4: Solace/Halcyon/Orbital still on v1 values); no shader globals | Not visible directly. It is the cause of drift between views. | 3 | enabling |
| 2 | Quality / tier layer | `vfx_tier.gd` (111), `flash_limiter.gd`, `settings.gd`, `high_contrast.gd`, `ui_motion.tres` (4249) | all | ~35 files read `reduce_effects`/`reduce_motion`/`high_contrast`/`colorblind_mode` themselves (city_view_3d, city_motion_layers ×4, route_rig, street_route_view, fx.gd, raid_pencil, neon_city, ...) | Not visible directly. Risk: modules disagree on what reduce motion means. | 3 | enabling |
| 3 | Look lab + parity harness | `tools/netrun_art/parity_sheet.py` (street only), `post_parity_lab`, `city_a2_parity_lab`, `id_capture.gd`, `tools/visual_qa/*`, ~40 `tools/design_lab` labs | — | Labs per view; no neutral gallery; HQ and city not wired into the sheet | No 3-column sheet yet; no module lab | 4 | enabling |
| 4 | Toon shading | `city_building` (683), `toon_bands.gdshaderinc`, `dress_solid`, `combat_backdrop` (168), `portrait_feed` (148), spike `hq_compound_toon` (46); glue `city_materials`, `landmark_materials`, `hq_compound_materials`, `street_r2_materials` | 5 (map, raid, combat bg, street, HQ) | Band constants split: `toon_bands` include vs inline ramp in the HQ spike shader | `pairs/hq_meridian.jpg`: the HQ is flat ochre cel with heavy ink against the plate's lit stone, containers and street light. `pairs/street_decision.jpg`: flat unshaded facades. `shots/screen_combat_aiming.png`: the backdrop is posterised noise. | 4 | 20 |
| 5 | Ink lines | `toon_ink` (85), `toon_ink_hull` (43), `id_flat`, ink inside `city_post`; glue `toon_ink_material.gd` | 5 | Hull, material and post ink are three paths; no `CompositorEffect` | `shots/screen_combat_aiming.png`: ink crawls on the backdrop. `pairs/hq_meridian.jpg`: ink weight is the same near and far. | 3 | 15 |
| 6 | Light spill / glow / bloom | `light_spill`, `ui_light_spill`, `city_glow*`, `city_pool*`, `spot_pool`, `spot_light`, `street_light_rig.gd`, bloom in `city_post` | 5 | glow/pool vs `_xray` (+3 −2 each), `spot_light` vs `spot_pool` (+4 −4), `light_spill` vs `ui_light_spill` (+43 −43) | `pairs/street_decision.jpg`: no lit frontage wall, no spill washes. `pairs/city_night.jpg`: no hierarchy of light (corp beams missing except one flat Halcyon cone). L3: bloom carries 25 % of the plate's energy (needs a bright-pass prefilter). | 5 | **25** |
| 7 | Atmosphere | `city_fog` (129), `beam_shaft` (79), `city_beam` (23), `route_depth`, `netrun_shader_kit*.gd`, `city_motion_layers.gd`; rain is procedural inside the kit | 4 (street, route, HQ, city) | `beam_shaft` on the netrun clock, `city_beam` not; no FogVolume | `pairs/city_night.jpg`: no tall corp beams, no haze layers. LOOK_PORT §7b: sky blobs from fog-only lights, a fog-top band at the roofline. `pairs/street_decision.jpg`: no depth layering. | 5 | **20** |
| 8 | Wet ground + water | `wet_street` (129), `street_r2_surface`, `city_water` (111), `city_water_plane` (167), `city_water_smear`, `city_seabed`, `city_water.gd` (638) | 4 | `city_water` vs `_plane` vs `seabed` duplicate wave and colour code; SSR only in AAA, no probe | `pairs/street_decision.jpg`: no long sign reflections (blobs/MP 94 vs 459). `pairs/city_night.jpg`: cartoon ripple water and **two black holes in the bay** (bug). | 4 | 16 |
| 9 | Post chain | `city_post` (455), `city_tilt_shift`, `route_grade`, `heat_glitch`, `scanline`, `distortion`, `jack_cover`, `colorblind` | 4 | `city_post` is a spatial quad per view, not a compositor chain; L3 exact to 0.4/255 without bloom | L3 sheet: bloom halos (6.1/255), CA. Its fix (bright pass) belongs with area 6. | 3 | 12 |
| 10 | Street-view layers | `street_r2_*` (≈3,400 lines), `route_rig.gd`, `route_*` shaders, `netrun_section`, `occlusion_helper`, `reveal_tiers` | 3 (street, route, HQ approach) | None (one builder) | `pairs/street_decision.jpg`: black foreground towers fill half the frame, no continuous frontage, skyline flat. Part of this is geometry, which is build's (LOOK_PORT off-limits list). | 4 | 12 |
| 11 | Signage + neon | `street_r2_sign*`, `dress_sign`, `dress_neon`, `holo_billboard`, `dress_plume`, `dress_kit.gd`, `neon_city.gd` (4,119) | 4 | `dress_neon` vs `dress_sign` (+38 −38 sibling); street and city sign paths separate | `pairs/street_decision.jpg`: 2-3 small signs vs the plate's hero signs (ORBITAL, KARAOKE, DATA, TEA) with spill | 4 | 16 |
| 12 | Grease pencil | `GreasePencilMark` (586), `grease_pencil_word` (242), `grease_pencil_art`, `pencil_shapes`, `pencil_lint`, `marker_stroke` (229); callers aim_line, nudge_lock, pencil_note/set, hq_plan, route_ink, raid_*; `hand_marks.gd` raw | 8 | Three word paths (`pencil_set`, `chrome/pencil_words`, `grease_pencil_word`); `hand_marks` bypasses the engine; world anchoring done per view (raid_map_anchor, netrun_frustum) | `shots/screen_route.png` + `screen_grid_site_selected.png`: the TARGET word reads as glowing neon marker, not wax. `screen_combat_aiming.png`: the aim line is thin and smooth at hero size. No world-space anchor API. Ruling conflict: the netrun plan pencil is **orange** (DIRECTION_REVIEW 2026-10-15) vs bible yellow. | 2 | 16 |
| 13 | Vinyl sticker | `kit/vinyl_sticker` (229, baked-art peel/gloss/dissolve), `chrome/vinyl_sticker` (92, vector verb stickers with glitch fill), `sticker_fill`, `card_sticker_fx`, `vinyl_sticker.gd` (1,010), `StickerSweepQueue` | 8 | The two `vinyl_sticker` shaders are **two designs, not drifted copies** (+77 −214); they share only `grey` and the include | `screen_raid_setup.png`, `screen_combat_aiming.png`: SEND IT, START DEFENSE and RAID SETUP read well | 1 | 8 |
| 14 | CRT terminal | `kit/crt_terminal` (91), `crt_panel` (35), `scanline` (29), `hex_dump.gdshaderinc` (100), `crt_terminal_panel.gd` (385), `typing.gd`, `cyber_type.gd` | 8 | Scanlines written three ways (`crt_terminal`, `crt_panel`, full-screen `scanline`) | Terminals read well on every screen; the edge glow and hex dump are faint at 1080p | 1.5 | 12 |
| 15 | Corp paper + decrypted holo | `corp_paper` (53), `zine_paper` (30), `decrypted_holo` (78), `glass_blur`, `rubber_stamp`, `corp_paper_panel.gd` (302), `decrypted_holo_panel.gd` (302) | 5 | `corp_paper` vs `zine_paper` (+19 −42) | `screen_raid_setup.png`: paper reads. THREAT INTEL and the Site file (`screen_grid_site_selected.png`) read as green **terminals**: no bands, no edge RGB split, no visible cracked seal. That is a §1.2 media fail (holo vs terminal). | 3 | 15 |
| 16 | Binary bits | `binary_bits` (63), `bits_atlas.png`, `binary_bits.gd` (225), `bits_path.gd`, `bit_path.gd` (211), `bits_seam`, `combat_beat_fx`, `fx_draw` (304) | 3 (combat, route entry, raid) | `bits_path.gd` (kit) vs `bit_path.gd` (fx): two path classes | **Not captured**: no way to force a beat was found. Gap unknown, so it needs a lab before scoring. | ? | ? |
| 17 | Blender → Godot | `tools/art_bake/*`, `tools/art_pipeline/*`, `hq_compound_materials.gd`, `assets/city/**/manifest.json` | HQ, city landmarks | No post-import script; materials assigned per stage by name | Feeds area 4 on the HQ (the spike toon shader) | 3 | enabling |
| 18 | Performance | `city_mesh_kit` (597), `city_lod` (204), `netrun_instance_pack` (75), `tools/city_perf_probe.gd` | 3D views | — | Street 19.4 ms p95 > 16.7 ms (hard gate) | 4 | gate |

### Not in the 18 areas (found in the code map)
- **Two world looks** (cel / AAA-2, `set_look_blend`): cuts across areas 4-9.
- **City life motion:** `city_car`, `sky_car`, `streak_lane`, `motion_path.gdshaderinc` (no includer found), `city_flow`,
  `city_traffic`, `city_sky_lanes`. The "city is always alive" standing rule depends on it.
- **Heat in the world:** `heat_city.gd`, `city_heat_rig.gd`, `police_light`.
- **Network decal + x-ray:** `city_network*`, `city_influence`, `influence_reveal`.
- **Occlusion / section cut** (designer rule for every HQ): `occlusion_helper`, `netrun_section`.
- **Sky, terrain, vegetation, seabed:** `city_sky`, `city_ground`, `city_a2_terrain`, `city_terrain_color`,
  `city_vegetation_kit`, `city_park_kit`.
- **Interior mapping** (Solace windows, `imap_atlas.jpg`).
- **Bare Anton live numbers** (a §1.2 medium; no shared class found).
- **Portraits / CAM feed:** `portrait_feed` (148), `cam_feed`.
- **Greyscale trio drift:** `card_grey` (Rec.709, 0.18), `grey_dim` (Rec.601, 0.6), `screen_grey` (Rec.709, 0.35).
- **UI scrims / panel shadows:** `ui_scrim_pools` (150), `ui_panel_shadows`, `ui_scrim_look.tres`.
- **Wheels:** `wheel_disc` (870), `wheel_wedge`. Out of scope (each boss wheel has its own polish session).
- Stale: `hq_compound_toon.gdshader` cites `tools/spike/city/shaders/`, which no longer exists.

### Determinism
No global `randf`/`randi`/`randomize` in look code. Look code uses seeded instances only (city_a2_builder, terrain,
traffic, sky traffic, ambient props, paper_staging) plus hashes (`kit_noise`, `marker_stroke`).

### Capture harness: `run_end` is not reproducible (2026-10-21)
Two `capture_pack.py --screens run_end` captures of the same code differ by up to 254/255 over the whole frame
(animated grid, sparkles, text edges, cursor). Never use `run_end` as before/after proof of a look change; prove a
shader there with a direct A/B (old vs new shader over a fixed card, windowed). Noise floor of that A/B for a
screen-texture shader: 1-2/255 (old vs old). `route`, `route_focus` and `combat_start` reproduce exactly.

## Critical pass (designer ask 2026-10-21: "very harsh, ready to ship")

Standard: ship quality means it would pass next to the concept or plate in a trailer frame, not "reads". Close-ups,
1:1 or 1.5x, at `D:/rc_scratch/rc_look/audit/crit_{pencil,media,world}.jpg` (`tools/crop_sheet.py`). Every item
below fails that bar unless marked **ok**. This pass raises several gap scores from the first table.

### World (3D)
- **Combat backdrop: fail, the worst on the most-seen screen** (`crit_world.jpg` row 1, Solace site). The ink
  crawls as doubled, stair-stepped outlines on every edge. The surfaces are posterised with green ghosting and vertical
  striping. A black ink line cuts across the frame at mid-height. The helix is a smeared green blob. Nothing reads as a
  plane. The concept (r11 / r41) has clean planar facets, a crisp 2 px ink, warm key against cool shadow, and readable
  lane signage. Gap **5**.
- **Raid / grid map (cel): fail.** Every tower is the same grey-violet prism with no window light, no tone jitter per
  facet, and faint, broken ink. The concept's (r40 raid_view_v3) value range, lit windows, violet trim on the landmark
  and its hierarchy are all missing. Gap **4**.
- **Street (AAA-2): fail.** The facades are flat unlit rectangles with decal windows. That is the §1.2 "never" (flat
  blocks or placeholders). No panel relief, AO or light gradient; signs are small and few, with no spill; the foreground
  towers are black voids. Gap **5**.
- **HQ run: fail.** It's on the cel spike shader against AAA-2 plates: the same flat ochre with heavy ink, and no lit
  stone, containers or street streaks. Gap **5**.
- **City night: fail.** Cartoon ripple water, the bay holes, a purple painted terrain, and a single flat corp beam
  against the plate's six volumetric beams. Gap **5**.

### Grease pencil: fail (gap 2 → **4**)
The engine is right; the look isn't. Against r11 `combat_boss_night` and the r3 overlay kit (`crit_pencil.jpg`):
1. **It reads as a vector line, not wax.** The width is uniform end to end, with no pressure swell or taper and no
   lift-off flick. The concept stroke swells and thins, and shows grain and clumps.
2. **Too thin for its job.** 9 px at 1080p against the concept's ~14-18 px at hero marks (aim arc, target ring).
3. **Geometry is machine-perfect.** The aim arc is an exact quadratic; underlines are ruler-straight; the threat route
   has polyline corners; rings are perfect ellipses, doubled. The concept underline overshoots and ends in a hooked
   downstroke; the rings overlap at their closure, as a hand draws them.
4. **A soft coloured halo** surrounds yellow and red strokes in combat, raid and grid. Wax on glass casts a crisp dark
   shadow; it doesn't glow. Source not found in the pencil code (no glow in `marker_stroke` or `GreasePencilMark`):
   to trace in the lab.
5. **The TARGET word looks like neon marker**: gradient fill, inner highlight, pink outer glow. Concept words
   ("HIT IT") are chunky wax with a cast shadow. On the grid the word also sits over its own target ring.
6. The bristle, dropout and sheen detail is invisible at play size: it's tuned below the screen's resolution.

### Decrypted holo: fail (gap 3 → **4**)
THREAT INTEL in Godot is an opaque, flat green box. Against r40 and ui_kit:
- no translucency (the city should show through at 78 % tint);
- no scan bands and no visible 4 px scanlines;
- no hologram content (the concept projects the unit models);
- no corp seal, cracked or otherwise;
- a cyan/green terminal-style edge, where the concept has RGB split on the edge only.
With Solace's lime it reads as the Cell's own terminal: a §1.2 fail.

### Corp paper: mostly ok (gap **2**)
Stamp, clips and redactions are **ok**. Faults:
- The stock is flat grey-white with faint fibres; the concept is warm cream with ageing and edge vignetting.
- The letterhead is a weak grey-green, not in the corp colour.
- **§1.2 media mix:** a pink dashed CRT-style forecast disc ("IF THE RAID RUNS NOW / HOME −10") sits on the paper.
  Forecasts are terminal. That is a layout call for build, so it goes to art-pass as an item, not toolbox work.

### CRT terminal: near ok (gap **2**)
Navy glass, cyan edge and type are **ok**. The hex dump and scanlines are invisible at 1080p (the concept shows both);
the corner notch is missing; and the panels are flatter than ui_kit's (no inner edge glow).

### Vinyl sticker: ok (gap **1.5**)
SEND IT, START DEFENSE and RAID SETUP read well. Faults: the extrude is shallower and the rest gloss weaker than the
concept's (ui_kit JACK IN, r41 SEND IT); the keyline is thin on the small stickers.

### Binary bits: unscored
No capture exists yet: the lab comes first.

### Revised scores (views × gap)
| Area | Before | After |
|---|---|---|
| 4 Toon | 20 | **25** (5 × 5) |
| 5 Ink | 15 | **25** (5 × 5: the combat backdrop crawl) |
| 12 Pencil | 16 | **32** (8 × 4) |
| 15 Paper + holo | 15 | **20** (5 × 4, holo) |
| 14 CRT | 12 | 16 |

So by score the pencil is the single biggest item, and toon + ink tie with light. The order below stays as approved
(foundation, then light), because the world modules share the post chain and Foundation's lab. **Recommendation:** run
pencil polish as a 2D track right after Foundation, in parallel with the world modules. It shares no files with them.

## Order (approved by the designer 2026-10-21)

Foundation is fixed first, as the brief says. After it, the order is by score, with paired areas done together:

1. **A. Foundation** (1 tokens + shader globals, 2 tier resolver, 3 gallery lab + one-command sheet with HQ and city
   wired). Lean: no migrations beyond what each later module needs.
2. **Light: 6 spill/glow/hierarchy + 9 bloom prefilter** (25 + the L3b bloom fix). Biggest visible gap on every 3D view;
   needs a `CompositorEffect` bright pass, so it also seeds the post chain.
3. **7 Atmosphere** (20): haze layers, FogVolume with baked density, fog-only lights without sky blobs, corp beams.
4. **4 Toon + 5 Ink** (20 + 15): one world material family and an ink `CompositorEffect`. The HQ moves off the spike
   shader (needs 17's slot mapping).
5. **8 Wet + water** (16), including the bay black-hole bug.
6. **11 Signage** (16), then **10 Street layers** (12; geometry stays build's).
7. **15 Holo** (the §1.2 fail) then **12 Pencil polish** (wax TARGET word, hero-size aim line, world anchor API,
   `hand_marks` onto the engine, one word path).
8. **16 Bits**: lab first, then score.
9. **14 CRT** (one scanline), **13 Sticker** (docs + shared include only; the two designs stay two).
10. **17, 18** run alongside: each module ships with its cheap tier and its GPU ms in the lab.

## Questions for the designer / art-pass
1. **Order:** take the order above, or lead with the 2D media (12, 15) because they're cheaper wins?
2. **Lane:** the world modules (4-9) overlap the art-pass L4/L5 per-view loop on the same files. Proposal: the toolbox
   builds each module in its lab and migrates the call sites; art-pass keeps tuning the per-view values in `.tres`. One
   file has one writer at a time, claimed via the mailbox.
3. **Looks:** should the world modules serve both cel (map zoom) and AAA-2 (netrun, route, HQ), or AAA-2 only, with cel
   left as is?
4. **Plan pencil colour in the netrun:** orange (DIRECTION_REVIEW 2026-10-15) or yellow (bible)? Default: orange for the
   netrun plan only, through a token.
5. **Sticker shaders:** keep both designs (baked-art cards vs vector verbs) under one include, rather than force one
   shader?

## Rulings received (2026-10-21)
- Designer: the order above is approved; the review standard is "very harsh, ready to ship".
- Art-pass (b): the toolbox builds modules and migrates call sites; art-pass tunes the per-view `.tres` values. One
  writer per file: the toolbox announces before editing `city_post`, `netrun_shader_kit*`, `street_light_rig`,
  `route_rig` or `city_view_3d`.
- (c) Both looks: every world module ships a cel preset and an AAA-2 preset on one API.
- (d) The netrun plan pencil is orange through the token `pencil_plan_netrun`; yellow everywhere else.
- (e) Both sticker shaders stay, under one include, named by design (kit vs chrome).
- First, ahead of Foundation: fix the city-night bay black holes (an L5 regression), with a before/after sheet.
