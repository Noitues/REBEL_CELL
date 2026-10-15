# Netrun entry storyboard (2026-10-15)

The netrun entry flow as an animatic and key frames. It runs from the HQ City Grid (the **mainline** look, as built
on main) through selecting the netrun and jacking in, then a dive that blends into the **AAA-2** street. At street
level the walls dissolve and the route is traced left to right, the markers are drawn, the camera zooms to the start
room and the player chooses.

It is rendered headless with Blender 5.2.2 (Cycles for AAA-2, Eevee for the mainline kit) on the RX 6700 XT, then
finished in numpy and PIL. Nothing is committed. Godot was never launched, and `D:\Godot\rebel_cell` was only read.

This is round 3 of the storyboard. The designer's rulings during the round are listed under "Rulings applied".

## Files

| File | What it is |
|---|---|
| `storyboard.mp4` | The animatic: 1280 × 720, 24 fps, 25.6 s (614 frames), 27.3 MB. H.264 through Blender's own FFmpeg (the sequencer). Each beat's title and the time code sit in the top-right corner. |
| `storyboard.gif` | 960 × 540 at 8 fps (every 3rd frame, 205 frames), with one shared palette and delta frames. 18.2 MB. |
| `boards/` | 14 key frames at 1920 × 1080, numbered by beat (list below). |
| `storyboard_sheet.jpg` | All the boards in a grid, captioned with the beat, the time and the frame. |
| `mainline_match.jpg` | The HQ frame beside the mainline captures (approved). |
| `test_frames/` | The four review frames of the v2 re-plan (a–d). |
| `scripts/` | Everything needed to rebuild (see "Rebuild"). `scripts/m44/` is the mainline city kit (round 40 unified city, from round 44). |

**Boards:**
1. HQ idle.
2. Hover: the Site file decrypts.
3. The plan is pencilled, with the JACK IN gloss.
4. The terminal types.
5. Binary rain on the chosen link.
6. The CRT collapse.
7. The dive, in the look-blend band.
8. The dive, low, with no route.
9. REVEAL: the first walls go to bits.
10. REVEAL: the left-to-right trace.
11. MARK: the markers and the TARGET.
12. DECISION after the zoom.
13. Hover option 1.
14. Hover option 2.

## Beats and timing (24 fps; 25.6 s)

| # | Beat | Time (s) | What happens | Camera |
|---|---|---|---|---|
| 1 | HQ | 0.00–3.00 | The mainline HQ idles; the city is live. | The mainline City Grid camera, held: orthographic, yaw 135, pitch 40. The mainline HQ fit rule (claimed + launchable Sites, 40 BU margin, the page's free rect × 0.65, anchor (0.45, 0.42)) is capped at 460 BU, close to the mainline grid view's 440. |
| 2 | SELECT | 3.00–7.35 | The cursor moves to the Site (0.7 s). On hover, the tag shows and the holo Site file decrypts (0.55 s). On the click (4.9 s), an orange pencil circle draws round the Site, then the orange plan along the border link from Returns Processing to the Site (0.65 s). JACK IN pops in, gets its rainbow gloss (0.8 s), and is pressed (7.1 s). | Held. |
| 3 | JACK IN | 7.35–13.45 | The terminal types `jack --from RELAY_4 --to PRIORITY_LANE`, routing, handshake, CONNECTED (7.35–8.75). Binary rain falls on the chosen link only (8.75–10.0). The CRT collapses, line then dot (10.0–10.45), straight into the dive (the wheel lens was dropped). The dive runs 10.45–13.45, walls closed: no route, no room light. | **The dive** is one path defined in the mainline world. It starts at the HQ camera, emulated with a 300 mm lens so the start does not jump, and ends on the street OVERVIEW mapped into that world. F, yaw, lens and shift ease on smootherstep; frame width and lens interpolate in log space; the pitch lags (u^1.6), so the camera keeps looking down as it drops, then levels out. The AAA-2 camera of every frame is the same pose mapped back. |
| 4 | REVEAL | 13.45–17.09 | At street level the walls dissolve into bits, left to right from the start room. Each layer's links write on (0.22 s) before that layer's walls dissolve (0.25 s, 60 ms stagger); room light bleeds out as each wall goes. | OVERVIEW (held): camera (60, −257, 66), F (93.5, 5.7, 38), yaw 7.2, pitch 6, distance 266, 40 mm. |
| 5 | MARK | 17.09–18.09, then a 0.8 s hold | Stickers slap on (scale 1.35 → 1, 25 ms stagger). The room frames and state rings draw on (lime current, orange options, white ahead). The option numbers pop, the token lands, and the red pencil TARGET circle and word write on last (0.4 s). The route UI arrives with the markers (0.35 s). | Held. |
| 6 | ZOOM | 18.89–19.89, +0.5 s settle | — | OVERVIEW → DECISION (smoothstep, distance in log space). DECISION: camera (−17, −77, 30), yaw 24 (left, looking right), pitch 9, distance 91, 30 mm. |
| 7 | CHOOSE | 20.39–25.6 | The cursor comes in. Hover option 1 at 20.79 s (the power cut, the `FIGHT L1` tag and the node file). The held hover moves to option 2 at 22.59 s. A held decision ends the beat. | Hover ease 0.30 s (F 22 % to the room, yaw +3, distance × 0.96). The move to option 2 takes 0.30 s. |

## UI states per beat

| Beat | Page | UI |
|---|---|---|
| 1–2 | HQ (mainline layout) | Resource bar, VIEW LOADOUT, MAP KEY, CREW / MARKET / DEFENSE tabs, crew polaroids (RUNNER tag after the click), holo Site card, JACK IN with the jack command line under it, ON AIR ticker, and the red pencil TARGET (Central Server, off-screen here, with its chip). On the map: the network decal (thin lime-yellow claimed links with a soft cyan halo), small owned rings (CORE + the 6 owned Sites nearest the relay), the pinned Sites, and the selected Site with its orange ring. No name tags at rest; only the hovered Site shows its tag. |
| 3 | HQ, then the dive | The page dims 25 % under the terminal. The rain falls on the link. The furniture fades in the first 0.3 s of the dive, the network decal over 0.6 s. |
| 4 | Street | No UI: the reveal is the content. |
| 5–7 | Route page | NETRUN sticker, top strip (Heat, HP, Cycles), DISPATCH, dossier, ROUTE panel (CONFIRM disabled, "Keys 1-3 go now"), key strip, the DECISION / OVERVIEW toggle (it flips at the zoom's midpoint), the decision vignette, the hover tag and node file. |

## Rulings applied this round

- **Mid-dive value** (review): the dark night city is kept.
  - City-wide haze is at 20 %.
  - Fog density and the city glow ramp with zoom (`fog_density_by_zoom`, `cityglow_by_zoom`).
  - The aerial grade is exposure 2.0 and in-scatter 0.9, lerped to r3.
  - Test frame a measures median luma 0.137, with 30 % of pixels under 0.10.
- **Rooftop trims** (review): about 1 in 6 of before, broken into lit runs and dimmer.
- **HQ = mainline look** (designer): see "Mainline HQ" below.
- **The dive is the look transition** (designer): see "Dive" below.
- **The street order** (designer): see "REVEAL and MARK" below.
- **City alive at all times** (designer): see "City alive" below.
- **Wheel lens dropped** (designer): the rain and the collapse fill the time instead.
- **Answers:**
  - one press skips the whole entry;
  - the plan pencil is orange;
  - the AAA-2 city is kept for the netrun;
  - the 460 BU HQ cap is approved;
  - the calibration grade is kept;
  - the cross-dissolve dive is approved;
  - beams sweep during holds;
  - the zoom takes 1.0 s.

## Mainline HQ (beats 1–2 and the start of the dive)

- **Kit:** the mainline city was ported from the art-pass round 39/40 unified kit, rebuilt here in `scripts/m44/` (round 44's copy): Eevee passes and the `post40` finish.
- **Values:** an Explore pass read the mainline values from main (read-only). The kit already carries them:

  | Value | Mainline |
  |---|---|
  | Camera | yaw 135, pitch 40, orthographic, lot 6 BU |
  | Toon ramp | as the kit |
  | Ink | (0.05, 0.04, 0.09) |
  | Fog | (0.20, 0.17, 0.33) at 0.22 |
  | Haze | (0.08, 0.06, 0.16) at 0.34 |
  | Bloom / spill | 0.75 / 0.5 |
  | Rain | alpha 0.11 |
  | Grade | (0.94, 0.92, 1.04) |
  | UI scrim | × 0.86 inside the network rect, × 0.68 outside (saturation 0.85), the selected Site in a lit vignette |
  | Decal | claimed links CELL_TURF #D4FF00, thin, with a soft NET_CYAN halo |
  | Markers | no lime pools (ART_R1 4a) |
  | Tags | hover only (ART_R1 1a) |

- **Source of each element:**

  | Element | Mainline source |
  |---|---|
  | Camera, framing rule | `scripts/city3d/city_config.gd` (views, raid fit), `city_iso_camera.gd`, `hq_scene.gd` `fit_hq_map`, `raid_zoom_fit.gd` |
  | Post (ink, fog, haze, bloom, rain, grade) | `shaders/city/city_post.gdshader` with `city_config.gd` |
  | Scrim and focus vignette | `content/config/ui_scrim_look.tres` |
  | Decal widths and colours | `city_config.gd` `net_*`, `city_layout.gd` `grid_graph` |
  | Page layout (bar, MAP KEY, tabs, polaroids, holo card, JACK IN + command line, ON AIR, TARGET chip) | `PLAN1/W3_HQ.jpg` and `W3_GRID.jpg` (after), `ART_R1.jpg` 1a/4a, `ART-5/GRID_PER_CORP.jpg` |
  | Live city | `city_motion_config_data.gd` (sky cars, aviation lights) through `post40`'s own motion: sky-lane cars with streaks, blinking lights, link packets, drifting fog patches, rain |

- **City-only calibration grade** (kept by ruling): the Blender/Eevee recreation came out brighter and about twice as saturated as the Godot render. The city layer is graded toward the capture's map area: saturation × 0.64, gain (0.76, 0.76, 0.84), nudged violet on the designer's note. The network decal sits on top, ungraded.

  | Map area | Median luma | Chroma | Mean colour |
  |---|---|---|---|
  | Mainline capture | 0.214 | 0.085 | (0.25, 0.24, 0.28) |
  | Ours | 0.210 | 0.113 | (0.25, 0.23, 0.30) |

- **Fewer owned nodes** (designer: main's map is mostly city): the CORE plus the 6 owned Sites nearest the relay.

## Dive: from the mainline world to AAA-2 (the look transition)

- **One path, two worlds.** The camera path lives in the mainline world.
  - The AAA-2 street maps onto the border link the player pencilled in beat 2: Returns Processing → Priority Lane Exchange (`sb_mainline.mapping`: scale 0.575, rotation −255.6°).
  - So the dive lands exactly where the plan pointed.
- **Rendering.** For each frame:
  - the mainline world renders while zoom ≤ 0.60 (Eevee, its post with its live motion);
  - the AAA-2 world renders from zoom ≥ 0.16 (Cycles at 12 fps; the frames between are reprojected by depth).
- **The look blend.** `look_blend_by_zoom` (0.20–0.55) in the preset crosses the two worlds with a smoothstep, driven by the same zoom parameter as every LOD band.
  - Grade, fog (mainline fog patches → AAA-2 volumetrics), wet reflections (the puddle LOD), and materials (cel + ink → AAA-2 shading) all move together.
  - A **cloud veil** (drifting noise, lit violet from below, at most 62 % opaque, densest mid-band) hides the geometry swap: the camera drops through a cloud bank.
- **Godot mapping.** One world. A `look_blend` uniform (from the camera rig's zoom) drives:
  - the environment grade lerp;
  - the toon ramp ↔ PBR mix and the ink-outline fade in the city materials;
  - the post fog patches ↔ the FogVolume density;
  - SSR / puddle roughness;
  - a full-screen cloud card at mid-band.

## REVEAL and MARK (the street)

- **Order** (designer):
  1. No route light or path is visible until street level: the walls stay closed through the dive.
  2. The walls dissolve into binary bits, left to right from the start room; each layer's link writes on, then that layer's walls go.
  3. The markers draw.
  4. The zoom.
  5. The choose.
- **Rules** (`sb_reveal.py`, the `REVEAL` / `MARKS` tables):
  - The walls are rule-placed over every route room (the layout's room list).
  - The dissolve order is the layer order (start → TARGET), slots staggered.
  - The links of layer L−1 → L write on before layer L dissolves.
  - The stickers stagger in node order.
- **Composite:** two renders of the same OVERVIEW camera (walls closed / open).
  - Each room shows the open render in its dissolved 0.7 BU cells, plus a light spill that grows round it; the edge cells flash lime / cyan.
  - The 2D bits lift off the wall plane and fade in 0.55 s.
- **Godot:**
  - a dissolve shader on the facade material (`dissolve` instance uniform, world-cell noise threshold, emissive edge), Tweened per room;
  - one `GPUParticles3D` per wall for the bits;
  - the wax links as `Line2D` with a reveal Tween;
  - stickers scaled by a Tween, rings via an arc shader `progress`, the TARGET pencil by a wipe uniform.
- **Jack-out:** the same beat in reverse (walls reassemble from bits).

## City alive (designer rule: never frozen, in any beat)

| Beat | Activity |
|---|---|
| HQ, select, jack-in, early dive (mainline) | post40 motion every frame: sky-lane cars with light streaks, aviation lights blinking, packets on the links, fog patches drifting, rain. |
| Dive (AAA-2) | Every frame is rendered at its own time: street and fill traffic lanes moving, the globe spinning, beams sweeping, signs flickering (their `pwo` attribute, from the r3 tables in `sb_live.py`). Detail fades in by the `lod_bands`. |
| Street (REVEAL, MARK) | **The r3 idle loop exactly**, run at the run-start state: base, the 14 flicker layers (signs, strobes, windows, billboard swap, holo scan roll and glitches), beams per frame (fitted to the beams through every medium), streaks per frame, 2D fog drift, rain. Indexed by f % 96, so every shot is in phase. |
| Decision and hovers (held) | The same layers rendered at those cameras: flicker layers, beams and streaks per frame (12 fps, blended), drift, rain. |
| Zoom | Rendered per frame at its own time (signs flicker through `pwo`). |

## Atmosphere detail by zoom (`lod_bands` in the look preset)

| Band | Zoom range | What it does |
|---|---|---|
| `fog_octaves_by_zoom` | 0.25–0.60 | Fine octave and ragged edges. |
| `wisps_on_at` | 0.45–0.70 | — |
| `plumes_on_at` | 0.50–0.72 | — |
| `signage_on_at` | 0.60–0.82 | Text signs, holo ads, billboards. |
| `small_lights_on_at` | 0.75–0.92 | Rain catching light. |
| `puddles_sharp_at` | 0.85–1.00 | — |
| `fog_density_by_zoom` | 0.35 at zoom 0, ramping over 0.30–0.90 | — |
| `cityglow_by_zoom` | 0.45 at zoom 0, ramping over 0.30–0.90 | — |
| `look_blend_by_zoom` | 0.20–0.55 | The mainline → AAA-2 look. |

- **Zoom** is the log of the camera's distance to the street, normalised (0 = the HQ, 1 = the street OVERVIEW).
- **Godot:**
  - `visibility_range_begin/end` with fade for the signage, strobes and small lights;
  - the fog noise detail from a camera-distance uniform;
  - `GPUParticles3D.amount_ratio` for the plumes, rain and bits;
  - the `look_blend` uniform as above.

## What is reused and what is new

| Part | Reused | New |
|---|---|---|
| Mainline city, its post and its motion | The round 40 kit via round 44 (`m44/`) | Perspective shots and lens shift (`unified39.py`, `layout36.project`), a thinner decal option (`post40.link` `w_px` / `halo`), the HQ fit rule (`sb_mainline`), the calibration grade (`sb_mhq`) |
| AAA-2 street, look and idle loop | The r3 scene, rules, preset, loop pipeline and post | Run-start state, the fill city (`cityfill`, `fill_sb`), walls, LOD bands, live layers on every shot (`sb_r`, `sb_live`) |
| HQ page UI | round 44 kits (`kit44`, `ui31`, `markers42`, `r31lib`) | The mainline page layout (`sb_ui`, `sb_mhq`) |
| Jack-in (terminal, rain, CRT) | Kit panels | `sb_ui` |
| Route UI | `compose3`, `sidekit`, `wax_r2` | Run-start state, staged REVEAL / MARK (`sb_reveal`), cached overlays |
| Camera | `cam_rig` | The dive across worlds and the timeline (`sb_cams`) |

## Procedural rules and the gaps for the tools step

**Rules:**

| Rule | Where | What it does |
|---|---|---|
| City fill (AAA-2) | `cityfill.py`, seed 9950 | A street grid continuing the netrun road; seeded lots; heights capped so no route camera sees the fill and nothing covers the street. Moving traffic lanes and segmented trims come from `fill_sb.py`. |
| Mainline HQ framing | `sb_mainline.hq_cam` | The mainline fit rule, capped at the grid scale. |
| A ↔ M mapping | `sb_mainline.mapping` | The netrun street ↔ the selected Site's border link. |
| Walls and reveal order | `sb_r.build_walls`, `sb_reveal` | — |
| Rules pose vs fog pose | `rules_r3.py` | The look placements from one route camera; the fog's calm wedge follows the segment camera. |
| Sequence-wide occlusion | `sb_r.py` | The fence and the left near-black silhouette are hidden in every shot. |
| Sky-streak calm span | `shapes_r2.py` | The decision set's x span (was hand-set). |
| City-alive tables | `sb_live.py` | The r3 seeds, shared by renders and composite. |

**Hand placements left:**
- the r2 dressing listed in the r3 NOTES (text signs, ad planes, holo ads, megastructures, drum column, stalls);
- the near-layer silhouettes and the y 600 skyline wall (`dress2_aaa.py`);
- the L4_0 warm key (`light_aaa.py`), tuned for the mid-run still;
- the HQ page furniture positions (page layout);
- the tuned numbers: fill fog strength, city haze, the calibration grade, the cloud veil.

## Render notes

- **Holds** (street, decision, hovers): one render of each layer, with the per-frame layers composited.
- **Moving shots:** rendered at 12 fps; the frames between are depth-reprojected (`sb_frames.warp`: a z-buffered splat from both neighbours, a time-weighted blend, holes from the other neighbour).
- **Cross-fades:** 5 frames at each change between a moving and a held shot.
- **Mainline dive:** every frame rendered (Eevee, about 4 s per frame).
- **GPU queue:** the shared lock protocol (`D:\rc_scratch\GPU_QUEUE.md`), one lock per job.
- **Contention:** the machine was shared with other agents' renders and CPU-heavy batch jobs. CPU-heavy frame assembly must not run during GPU renders: it starved the render host 5–30×.

**GPU times of the final pipeline** (RX 6700 XT, wall clock, under heavy contention from other agents' renders and
batch jobs; see below):

| Job | What | Time |
|---|---|---|
| `loop_statics` | Street base, 14 flicker layers, the static media, transmittance (r3 loop pipeline, run start) | 404 s |
| `street_media` | The street's volume pass without beams / beams only, 1280 × 720, 48 spp | 383 s |
| `ov_closed2` | The street with every route wall closed (the reveal's "before") | 44 s |
| `loop_beams` | 96 beam frames | 715 s |
| `loop_dyn` | 96 streak / globe frames | 2882 s (slowed by contention: 10 s per frame alone, up to 330 s shared) |
| `dive` | The AAA-2 part of the dive (26 frames, full passes) | 1201 s |
| `dive_board` | Two 1920 dive boards | 153 s |
| `zoom` | 13 zoom frames, full passes (re-render after a wall-state fix) | 507 s |
| `dec`, `h1`, `h2` | Decision and hover holds: statics at 1920 + flicker layers + streaks and beams per frame | 318 / 1309 / 922 s |
| Mainline (Eevee) | The HQ render and the 42 dive frames of the mainline world | about 4 + 18 min |
| **Total, final pipeline** | | **about 2.9 h** |

**Over budget.** The brief asked for 1–1.5 h. The final pipeline alone is about 2.9 h. Superseded work (the v1 dive, v1 statics, the
first HQ in the AAA-2 kit, test renders) adds about 2 h, so the round used about 5 h of GPU wall time. Causes: three
re-plans mid-round (the designer's v2 order, the mainline HQ, city-alive everywhere), and the machine being shared:
another agent rendered on the GPU before the queue protocol existed, and CPU batch jobs starved Blender (a 1920 frame at
128 spp took 18 min instead of about 1.5).

**CPU (frame assembly, numpy / PIL):** about 6–15 s per frame, 4 workers, about 40 min for the 614 frames; boards about
10 min; encode about 3 min.

## Self-check of the animatic

Done on every frame (`scratch/check.py`): the mean absolute frame-to-frame difference at 320 × 180, its peaks, and
a contact sheet every 12 frames.

- **Does each beat read?** Yes.
  - HQ is the mainline page: live map, thin network, the Site with its tag on hover.
  - SELECT has the decrypt, the orange plan along the border link, and the JACK IN gloss and press.
  - JACK IN has the terminal (moved clear of the link), the rain on the chosen link only, and the CRT line then dot.
  - In the dive, the mainline city falls away into the cloud bank and comes out as the AAA-2 street. No route is visible.
  - REVEAL dissolves the walls left to right, the links write on, and the light bleeds out.
  - MARK slaps the stickers, draws the rings and numbers, and writes the TARGET last. The route UI arrives with it.
  - ZOOM lands on the start room, camera left looking right.
  - CHOOSE runs the option 1 power cut, then option 2 with the hover held.
- **Pops.** Two were found and fixed.
  - HQ → dive (frame 251). The jack-in dim disappeared at once, and the orthographic HQ render met the 300 mm perspective
    render: the difference was 0.070. Fix: the dim and the HQ render now cross-fade over the first 0.3 s, and it is 0.005 now.
  - The zoom frames had the route walls closed: the job gave every frame the dive's wall state. Fix: re-rendered with
    the walls open.
  - Every other segment change is under 0.012 (the 5-frame cross-fades between the moving and the held renders).
  - The large differences left are camera motion only. Through the dive they rise and fall smoothly from 0.004 to a 0.09
    peak at the fastest descent and back to 0.008, with no isolated spike. The zoom peaks at 0.14 mid-move.
- **Black frames.** None. The darkest frame has a mean luma of 0.154.
- **Denoiser boil.** None visible.
  - The street, decision and hover holds are single renders plus per-frame emitter layers (no per-frame denoised base).
  - The beams are filtered [1 2 1] / 4.
  - The moving shots are reprojected between renders, so the noise moves with the geometry.
- **Is the route clear in REVEAL / MARK / ZOOM / CHOOSE?** Yes: the trace is drawn link by link, then marked, then the
  decision frame dominates. The `FIGHT L1` tag for option 2 sits on the boundary between rooms 2 and 3 (the tag is
  placed at the room's top-left), but the lit branch and the cursor make the choice clear.
- **Board 07 (mid-dive)** is at the veil's peak, so it is the haziest frame of the film, by design.

## Open questions for the designer

0. **Answered (designer):** the Central Server off frame keeps its edge marker; the zoom timing is fine; the near-layer silhouettes are dropped from the dressing (done: `dress2_aaa.py` draws them into throw-away accumulators so the shared build stream is unchanged; no object, no render cost); the dive must be one continuous city (see "One continuous city").
1. **In-game durations.** The animatic takes 6.1 s from the press to the street: terminal 1.4, rain 1.25, collapse 0.45, dive 3.0. The locked transition is about 4.4 s. Proposed for the build: 0.9 + 0.7 + 0.3 + 2.4 = 4.3 s. The REVEAL + MARK (4.6 s here) could compress to about 3 s after the first runs, behind the "short jack-in" setting.
2. **The mainline Central Server is off-screen** at this framing (red edge marker). Should the HQ framing include it, or is the edge marker right?
3. **The look band** (zoom 0.20–0.55, about 0.6 s of the dive). Longer for a slower look change?
4. **The calibration grade** compensates for Eevee vs Godot rendering. In the build there is nothing to compensate (it is one renderer); the look blend just runs from the real mainline values.
5. **The near-layer silhouette** that blocked the DECISION view is hidden by rule in every shot. Drop it from the dressing?

## Limits and what I could not do

- **The mainline HQ is a recreation**, not a capture: the art-pass round 40 kit (which main was ported from) with the
  mainline values, plus a city-only calibration grade fitted to the captures. The geometry is round 40's, not the
  current main city mesh. Main's Central Server sits off this framing, so it gets the edge marker.
- **The mainline dive frames** use the kit's own motion (sky cars, lights, packets, fog patches, rain), not main's
  exact traffic system (street cars, sky-lane decks). The full Heat rig (searchlights, police) is not shown: Heat 58 is
  FLAGGED, which in main means 2 searchlights; the kit has none.
- **The dive's world swap is a cross-dissolve** behind the cloud veil; in the build it is one world with a blend uniform.
- **The AAA-2 dive frames** are rendered at 12 fps and reprojected; fast motion low in the dive shows slight
  softness on thin neon edges.
- **Street boards** (09–11) are the 1280 loop passes finished at 1920, so they are a little softer than the other boards.
- **The hover holds** composite their flicker layers per frame, but their streaks and beams are rendered at 12 fps and
  blended between.
- **Stall lights, nav strobes and flicker** come in by zoom only through the signage band and the street loop (the
  strobes are part of the loop layers); there is no separate stall-light group.
- **Godot was never launched** (no exact mainline frames were recorded; `run_windowed.py` was not needed).

## One continuous city (v3 proof: the dive only)

**Designer note:** the v2 dive cross-dissolved from the city map to a separate street set behind a veil. This proof
replaces that with ONE world.
- One scene, one city, one camera path, no veil and no swap.
- The netrun street IS the map's buildings along the selected Site's border link.

| File | What it is |
|---|---|
| `storyboard_v3_dive.mp4` | 9.5 s (229 frames), 1280 × 720, 24 fps, 12.3 MB. It runs: the Site hovered (beat 2), select, jack in, the dive, then the REVEAL start held 0.5 s. |
| `boards_v3/01_HQ_select.png` | The HQ beat. |
| `boards_v3/02_DIVE_mid_one_city.png` | Mid-dive (look blend about 0.5). |
| `boards_v3/03_STREET_reveal_start.png` | The street at the REVEAL start (walls closed). |
| `boards_v3/04_STREET_rooms_derived_preview.png` | The same frame with the walls opened, to show the 19 derived rooms inside the real buildings. |
| `scripts/sb_onecity.py` | The derivation rules (pure python). |
| `scripts/m44/onecity_scene.py`, `onecity_build.py`, `onecity_cycles.py` | The one scene: the mainline kit's builder plus the route buildings, rooms, walls, section and the AAA-2 shading. |
| `scripts/sb_ocjobs.py` | The camera path and the jobs. |
| `scripts/sb_ocframes.py` | Assembly. |

### Derivation rules (the core of the tools spec)

All rules are in `sb_onecity.py` (`RULES`) and the look preset (`lod_bands`). Nothing is hand-placed.

1. **The link.** The netrun follows the selected Site's border link: the polyline the beat-2 plan pencil draws (street
   centre points, in lots). Here it is Returns Processing → Priority Lane Exchange.
2. **Buildings as the game reads them.** A street-level base plus the stacked parts above it (z0 > 0, footprint inside
   the base) is ONE building. Its height is the top of its highest part.
3. **Frontage.** For each straight leg of the link and each side, the frontage is the buildings:
   - standing on the street (z0 = 0);
   - at least `min_width` 2.5 BU wide;
   - whose near edge lies within `front_band` 0.8–6.5 BU of the leg's centre line;
   - and that overlap the leg.

   A leg may be extended along its own street line by `extend` (12 BU before its start, 60 BU past its end) when the leg
   alone is too short. It is still the street the link runs on.
4. **Choosing the street.** The chosen leg and side maximise, in order:
   - the number of run layers that get a building (in link order from the relay, skipping a building without the floors
     for its layer);
   - then the total usable floors;
   - then the start-on-the-left orientation.

   Here: leg 3 (x 135 → 9 at y 9), north side. Its 13 frontage buildings are 3.3–20 BU tall. 8 are route columns; 5 were
   skipped as too short.
5. **Floors.** Usable floors = the real height / `floor_bu`. `floor_bu` is 1.9 BU, the mainline window pitch. On a
   tapered building, only the floors whose facade setback at the room top stays within `max_setback` (0.6 BU) count.
6. **Rooms.** A layer's rooms take consecutive real floors from `base_floor` (0), bottom up in slot order.
   - Each room sits on the building's street face, inset `room_inset` 0.45 BU from the corners and `room_depth` 2.6 BU
     deep.
   - **`room_floor_span` (1–2):** a room spans two consecutive floors (a double-height cutaway) when one floor would
     project under `room_px_target` (46 px at 1080p) at the street OVERVIEW. Here one floor projected 25 px, so span 2.
     A building that lacks the floors for two-floor rooms keeps single-floor rooms. The building is never rescaled.
   - Here: layers 0–3 and the TARGET are double-height; layers 4–6 (buildings 8.4, 10.7 and 4.1 BU tall) are single.
7. **Walls.** The facade cells and windows of a route building that fall inside a room opening are cut. Each opening
   gets its own wall object, built by the kit's own facade rule (`fgrid` facets plus windows in the building's colour):
   closed in the dive, dissolved in the REVEAL. The rest of the facade is the building's own.
8. **The section** (new; a continuous city needs it). In a real city the blocks across the street stand between any
   side-view camera and the netrun street.
   - Inside the corridor in front of the street (the camera side of the street centre line, along the street ±30 BU),
     everything above `z_cut` is not drawn.
   - `z_cut` follows the zoom (`section_by_zoom`): from above every roof at the HQ (60 BU) down to a 1.2 BU plinth at the
     street, eased over zoom 0.25–0.85. The foreground blocks visibly lower as the camera descends, like a section model.
   - It is a clip in the materials on the same geometry, the same mechanism as the wall dissolve. In Godot: a
     section-plane uniform in the city shaders.
9. **The camera.**
   - **Path:** one path in the city's own frame. It starts at the mainline HQ pose (orthographic, yaw 135, pitch 40,
     460 BU; emulated by a 300 mm lens) and ends at the street OVERVIEW solved by the v3_dynamic rig on the derived rooms
     (yaw 97.2, pitch 6, 40 mm, distance 140).
   - **Interpolation:** target, yaw and shift on smootherstep; frame width and lens in log space; pitch lagged (u^1.6).
   - **Orientation:** the camera looks into the street face (along its normal). Here the start (the relay end) lands on
     the screen's RIGHT: the link runs east → west, and the frontage on the north side is seen from the south. So the
     rig mirrors (camera right looking left, toward the unexplored side) instead of v3_dynamic's start-left.
10. **Two looks, one geometry.**
    - The mainline look is the kit's Eevee toon + ink passes and its post.
    - The AAA-2 look is Cycles on the SAME objects. Only the materials change: the kit's per-face colour through a
      Principled BSDF, a wet ground, and the emitters from the same colour attribute. Lights and media are added:
      - lamps along both kerbs every 6 BU;
      - each route column washed in the district pair from across the street;
      - city glow light-linked to the fog;
      - beams on the tallest roofs by the r3 rule;
      - the r3 fog field scaled to the mainline units (×3, the city being about 3× smaller).
    - The frame mixes the two by `look_blend_by_zoom` (0.20–0.55). This is a shading blend of identical geometry from an
      identical camera (the Godot equivalent: lerping material, lighting and fog uniforms on the same meshes), not a
      cross-dissolve between worlds.

### The proof's continuity check

| Measure | Result |
|---|---|
| Frame-to-frame mean difference (`scratch` check, 320 × 180) | Rises smoothly from 0.004 to 0.146 at the fastest descent and back to 0.002. No isolated spike, no black frame. |
| The look band (frames 170–186) | No jump. |
| The section lowering (zoom 0.25–0.85) | Continuous. |
| Room derivation (board 04) | All 19 rooms sit in real map buildings on real floors, behind their own walls. |

### Does the street end frame read as AAA-2? Partly. Flagged as a mainline layout question.

**What reads:**
- a dark, wet neon night city: median luma 0.22, 3 % of pixels under 0.10 (brighter shadows than the r3 targets of 25–40 %);
- lit fog and kerb lamps;
- the route columns washed in the district colours;
- the street seen side-on with the rooms inside its real buildings.

**What does not read:**
1. **The street front is low.** The real frontage buildings are 3.3–20 BU tall along a 126 BU street. That is a
   length-to-height ratio of about 9:1, against about 3.4:1 for the old street set (8 BU floors, 56 BU columns).
   - At OVERVIEW the route is a thin band across the middle of the frame. The rooms are about 50 px tall even
     double-height (they were about 150 px).
   - The cut foreground blocks fill the lower half.
2. **The AAA-2 signatures thin out.**
   - The beams have less fog and less height to cut through.
   - The rooms are small, and three layers are single-floor.
   - Without the old street set's dressing (ads, signs, holo ads), the frontage has no hero signage yet.

**Proposed on the map side** (a mainline layout question, not a fake):
- **(a) A street-front band in the city layout rules.** Buildings fronting any street that can host a netrun (the
  border links' streets) rise to at least 6 floors (about 11.5 BU). The aim: every layer's 3 rooms fit double-height
  and the frontage reaches a 4:1 length-to-height ratio. Only the street-front row changes; the skyline behind it
  stays.
- **(b) Optionally, a slightly wider street** (the street tile 6 → 8 BU) on border links, so the street reads at the
  side view.
- **(c) Hero signage by rule on route columns** (one blade or wall sign per column in the district pair), the item the
  r3 NOTES already lists for the tools step.

With (a), the OVERVIEW would frame the route at about the old proportions with no change to the HQ look.

### Godot mapping

| Element | Godot |
|---|---|
| Geometry | One city scene (the game's CityView3D) for the HQ, raid and netrun views. The netrun street is a query on the city layout: the link, its frontage and the room slots. No separate netrun scene is loaded. |
| Rooms | MeshInstance3D interiors inserted into the chosen buildings, plus wall meshes cut from the facade with the dissolve shader. The facade cut is a per-building mesh variant (the route columns are rebuilt with openings when the run starts). |
| Section | A world-space clip box uniform (`corridor`, `z_cut`) in the city building and neon shaders; `z_cut` comes from the camera rig's zoom. |
| Look | `look_blend` (from zoom) drives the WorldEnvironment lerp (fog, glow, tonemap), the city shaders' toon ↔ PBR mix and ink fade, the wet street's roughness, and FogVolume density. |
| Lights | Kerb lamps, facade washes and beams as Omni / Spot lights spawned by the same rules, with `visibility_range` fades by zoom. |

### Limits

- **The end hold (0.5 s)** reuses the last render: only the post's rain moves. The full sequence's street level is the
  r3 idle loop, which this proof does not re-run on the one-city street.
- **The mid-dive board (02)** mixes a 1280 mainline render with the 1920 AAA render, so it is a little softer.
- **The v2 animatic** (`storyboard.mp4`) still uses the separate street set. A full v3 sequence (reveal, marks, zoom,
  choose on the one-city street) would follow once the layout question above is answered.
- **GPU:** about 33 min in all.
  - Calibration tests about 6 min.
  - Mainline HQ 39 s, mainline dive (38 frames) 74 s.
  - Cycles dive (49 frames, 1280, 32 spp) 21 min.
  - Boards 4 min.
  - Lock waits on the shared GPU added about 40 min of wall time.

## Rebuild

Run from `scripts/`. Nothing launches Godot. `scratch/` was deleted after delivery; step 1 regenerates it.

1. Setup:
   - `python emblems20.py`, `python ads_aaa.py`;
   - mainline kit: in `m44/`, `python layout36.py`, then `NET36=net_scope.json python scope39.py`.
2. GPU, with the lock protocol (`../scratch/gpu.sh`):
   - `python sb_jobs.py loop_statics`, `street_media`, `ov_closed2`, `loop_beams`, `loop_dyn`;
   - `python sb_jobs.py zoom`, `dec`, `h1`, `h2`, `dive`, `dive_board`;
   - mainline: `python sb_mjobs.py hq`, `python sb_mjobs.py dive`.
3. `python sb_frames3.py frames -j 4` (after the GPU work), then `python sb_frames3.py boards`.
4. `python sb_encode.py mp4`, `gif`, `sheet`.

**v3 one-city proof rebuild** (from `scripts/`):
1. In `m44/`, run `python layout36.py` and `NET36=net_scope.json python scope39.py`. Then, from `scripts/`, run `python emblems20.py`.
2. GPU, one job per lock:
   - `python sb_ocjobs.py m_hq`;
   - `python sb_ocjobs.py m_dive`;
   - `python sb_ocjobs.py c_dive`;
   - `python sb_ocjobs.py c_boards`.

   The renders go to `D:/rc_scratch/storyboard/oc_m` and `oc_c`.
3. `python sb_ocframes.py frames`, then `mp4`, then `boards`.
