# HQ netrun: Meridian Freight, "the yard cycle" (2026-10-15)

The Meridian HQ run (the boss compound) in the approved route-map look (AAA-2 r3): realistic night, wet ground, fog with
coloured beams, light-streak traffic, grease-pencil links, vinyl stickers, the hover power cut, the r3 value targets,
plus the designer's HQ lighting rule (2026-10-15 audit): the landmark is keyed, rimmed and separated from the city by
lighting, about 1.5-2x the local background, and readable as a silhouette at 320 px.

Nothing is committed; the Godot build is untouched. Everything is rendered headless with Blender 5.2.2, Cycles on the
GPU (RX 6700 XT, HIP, plain BVH2) inside the shared GPU queue (`D:\rc_scratch\GPU_QUEUE.md`); Eevee only for layout
previews.

## Files

| File | What it is |
|---|---|
| `H_overview.png` | The OVERVIEW: high 3/4 from the north-north-west. The container fortress, the ship-to-shore crane over the north wall, the freight train in the rail yard, MANIFEST CONTROL with THE MASTER MANIFEST (red pencil TARGET). 2560 x 1440 with UI. |
| `H_decision.png` | DECISION at n1 (north wall, step 6): the train is IN at the west end (board it: NOW ONLY), the crane is swinging the hook to the wall (yellow pencil: where it will be next step). Option 1 = walk the rampart, option 2 = ride the train. |
| `H_hover.png` | The same, hovering the train ride: the power cut, the branch lit, the node file, the rule note (shunts east next step, leaves in 3: still aboard = ejected, Heat +1). |
| `H_mechanic_states.png` | The design-language sheet: the room states incl. RIDE ON OFFER, three cycle steps (on the train, the hook at the wall, the hook in the yard), the dial, the rule cards (round 43 vs proposal vs GDD). |
| `H_reveal.mp4` / `.gif` | 6.5 s HQ beat: the rail dolly beside the arriving freight train, then the crane-up past the gantry into the OVERVIEW while the hook lifts out of the yard; route and UI draw in last. 1280 x 720 / 960 x 540, 24 fps. |
| `plates/*_plate.png` | Every still without UI. |
| `scripts/` | Everything needed to rebuild (see "Rebuild"). |

## 1. Layout rules (`scripts/hq_graph.py`; numbers in `hq_preset.PRESET["hq"]["compound"]`)

| Element | Rule |
|---|---|
| Fortress | A rectangle of container walls: outer faces at abs(x) = 80, abs(y) = 60; 3 courses of 9 BU (+ a merlon course of half containers); four corner towers of 5 CROSSED courses (orientation alternates per course). |
| Rooms | A room is a container slot cut open on the wall's OUTER face (14 x 8 x 10). The route walks the RAMPART: west wall northbound (courses 0-1-1-2), the NW tower, the north wall eastbound over the track, the NE tower, the SKYWAY into the yard, up MANIFEST CONTROL's north face. |
| Links | Facade catwalks at sill height; ladders where the course changes; exterior stairs round the corner towers; the glazed skyway (t2 > m1); the server lift. |
| Gate / start | The gatehouse on the west wall (`gate_u`), the lit portcullis, the container drawbridge on chains over the moat; the Cell's hack box beyond it. |
| Moat / rail yard | Moat on the west, south and east sides; the NORTH side is the rail yard: the through track (the train's) and a siding with a parked train. |
| Movers | The CAR (a room on the train's flatcar) and the HOOK (a room on the crane's spreader). Their positions are functions of the mechanic time (`car_x`, `hook_xyz`): continuous, so the clips move them. |
| The server | THE MASTER MANIFEST: the open vault on MANIFEST CONTROL's roof (open all round, so the TARGET reads from every angle). |
| Ties | Path order (the node list), never dict order. |

## 2. Preset variant (`scripts/hq_preset.py`)

`look_preset.py` is r3's, unchanged; `hq_preset.py` deep-copies it and adds `PRESET["hq"]` (palette, compound, mech,
light, beams, city, road, cam, post) and `PRESET["hq_fog"]`, plus the storyboard's `lod_bands` (same keys and bands as
Halcyon). Palette: rust-dark container steel in five course colours, Meridian orange #FF8C1A (the sign, the work lights,
the lit seams, the boom neon), red #FF2E28 (beacons, gate lamps), sodium yard light, cold mast floods, hazard amber.

## 3. The mechanic: GDD vs proposal

| What | Source | Status |
|---|---|---|
| The boss Site = Meridian's Central Server, THE MASTER MANIFEST | GDD 11.7 | **Real.** GDD 8.4b still says "The Manifest" (flagged, Q4). MANIFEST CONTROL as a building is concept-only (round 35). |
| HQ run = a compound with a unique mechanic | Bible 4.6 / 4.7, round 43 | Art direction; **not in the GDD** (bible Appendix B: all mechanic rules are proposals). |
| The crane / train cycle; rooms ride the movers; every move re-makes its links; the next move telegraphed in yellow pencil | Round 43 (decision: "Meridian: the crane/train cycle") | Kept (proposal). |
| The 6-step cycle as drawn: train ARRIVES / IN WEST / SHUNTS EAST / IN EAST / LEAVES / GONE; crane YARD / SWINGS OUT / AT THE WALL x2 / INTO THE YARD x2 | This round | **Proposal**, adapted from round 43's step list so it works on a rampart route; preset `mech.train`, `mech.crane`, `mech.phase`. |
| A ride skips 3 rooms; boarding exists only while the mover is beside you (NOW ONLY); max 1 ride a run | This round | **Proposal** (preset `max_shortcuts`). |
| Still aboard when the train leaves: ejected at the gate, Heat +1 | Round 43 open question | **Proposal**, shown only as the hover note and the sheet card. |
| Visual language: hazard badge on a ride's sticker, ON THE TRAIN / ON THE CRANE chips, NOW ONLY chip on a vanishing link, yellow pencil ring + arrow for the next move, THE YARD CYCLE dial | This round | **Design-language proposal**; the locked state colours are unchanged (a ride on offer is orange like any option). |

GDD-fit: the GDD netrun (4.2) is 7 layers of 2-4 nodes; the compound is a chain of 12 rooms + 2 rides. Node kinds follow
round 43's mix; the GDD guarantees (a Mainframe in layers 3-5, about one Elite per layer) are not checked.

## 4. Camera beats

| Beat | Rule |
|---|---|
| DECISION | FRONT AND CENTRE (the designer's review pattern): the azimuth is the mean look vector of the distinct room normals holding the current room + the options; the current room sits in the middle of the usable frame, the framing solver pulls back until the options fit (56 % / 62 %), never closer than 135 BU; pitch 14-24 by layer. On the rampart this is a RAIL DOLLY: one wall, the camera tracks along it, no orbit (Halcyon orbits; Meridian slides). |
| Hover | The rig's ease (22 % toward, 3 deg, x0.96); the power cut on the same curve. |
| OVERVIEW | High 3/4 from the NNW (yaw 150, pitch 30, lens 40): both route walls, the crane, the train, the keep. |
| REVEAL (the HQ beat) | 6.5 s: tracking beside the arriving train (low, 24 mm), then the crane-up past the gantry into the OVERVIEW; the hook lifts out of the yard meanwhile; UI + route draw in over 5.4-6.3 s. |
| Occlusion | A room is drawn when its opening faces the camera; links hidden by the wall they run on (`seg_normal`). |

## 5. Godot 4.7 mapping

| Element | Godot | Perf |
|---|---|---|
| Containers | One container mesh (+ a half one) in a MultiMesh per wall / tower course, per-instance colour; the corrugation in the shader (sin of the tangent coordinate), rust from a world-space noise. | ~1.2 k instances, 1 draw per MultiMesh. |
| Rooms | One scene per node kind placed in its slot; a room light per visible room (state ladder). | ~10 room lights on screen. |
| Movers | `Path3D` / tweens driven by the cycle step: the train (a car scene carrying the CAR room scene), the trolley + spreader + HOOK room; the cable a scaled cylinder. | 3 nodes animate per step. |
| The cycle | A `MeridianYard` resource: `train[]`, `crane[]`, `phase`; `rides_max`. Links are rebuilt from it each step (the bible's de-power / re-make link grammar). | Pure data. |
| Landmark light | Seams + logos: emissive strips in the container shader (per-instance mask); work lights / tower floods: ~20 `SpotLight3D` (shadows off except 4); the back fog bank: a `FogVolume` box + 5 omni lights with volumetric energy only. | Lights are the cost: cull by the overview / decision camera. |
| City, fog, LOD | As Halcyon (hq_kit city ring as MultiMeshes, one FogVolume, the `zoom` band uniforms). | As Halcyon. |

## 6. Value checks and render log

The designer's audit (2026-10-15: "the HQ is far too dark, the structure can't be read") was answered with LIGHT, not
exposure: lit seams under every container course, the MERIDIAN logo panels on the towers, orange work lights along the
walls, sodium flood towers on the corners aimed in, keep washes, sodium yard poles, a sodium glint on the rails, the
crane's orange truss neon + white strobes + uplights + a hook spot, the train's running lights, wheel sparks and a
headlight beam, a rim from the city glow behind (light-linked to the landmark only) and the fog behind the compound lit
from below (the first Cycles test used a separate fog-bank volume: 346 s a 1280 test frame, the background read brighter
than the castle; it was folded into the main fog).

| Still (2560 x 1440, 64 spp) | median | < 0.10 | > 0.85 | landmark / local background |
|---|---|---|---|---|
| H_overview | 0.189 | 25.5 % | 1.4 % | 0.236 / 0.177 = **1.33** |
| H_decision | 0.185 | 20.4 % | 2.6 % | 0.177 / 0.191 = 0.92 (the frame is half landmark; the background is the lit fog over the yard) |
| H_hover | 0.022 | 73 % | 1.7 % | the hover power cut (everything outside the branch at 22 %), as designed |

r3 targets: median 0.14, under 0.10 25-40 %, over 0.85 <= 2.5 %: the overview / decision run brighter (median ~0.19)
and the decision is a touch over on the highlights; the landmark ratio meets 1.33 at the overview (target 1.5-2: one
more notch of wall light would reach it). Silhouette at 320 px: the walls and towers, the A-frame crane and the train
are all nameable (`scratch/ov_thumb.png`).

Render log (Cycles HIP, RX 6700 XT, shared queue): stills 3 x ~65 s (208 s with the build), sheet shots 53 s,
the reveal 156 frames at 960 x 540 / 12 spp in 770 s (~5 s a frame), compose 90 + 49 + 208 s, encode 19 s. The first
reveal frames were re-rendered after a camera fix (the dolly started inside a city tower).

## 7. Gaps for the tools step

- The route rooms' slots (wall + u + course) are a preset list, not generated from a rule (the rampart path order is the rule; the slots are numbers).
- The gatehouse position and the skyway's bend are numbers.
- The decision state shown (step 6 at n1) is picked by hand to show the mechanic.
- Light levels of the landmark rig were set from Eevee previews + one Cycles test; a new compound needs one calibration pass.
- The reveal's camera path is a hand-set dolly + crane-up, not a rule.
- Container IDs / barcodes are random stripes; there is no logo texture.

## 8. Open questions for the designer (for DECISIONS.md)

1. Meridian orange #FF8C1A is also the route's "next" orange. Here the fortress uses it for the sign, the work lights, the seams and the boom neon (the audit asked for orange work lights); the route stays wax pencil. Keep, or shift the corp light to sodium and keep orange for the sign only?
2. Max rides a run: 1 (here) or 2?
3. What happens when the train leaves with you: ejected + Heat +1 (proposal), or you ride out of the run?
4. Final server name: THE MASTER MANIFEST (11.7) or The Manifest (8.4b)?
5. Is a ride a node (an encounter on the car / the hook, as here: elite / fight) or a free move?

## Rebuild

From `scripts/` (Blender 5.2 headless; logs in `../scratch/`; nothing launches Godot):
1. `python hq_graph.py` (the layout + cycle self-check), `python hq_cam.py` (the poses).
2. `python hq_all.py stills,reveal,post` (GPU-locked batches: stills + sheet shots, the reveal in two halves; then
   compose, the sheet, the encode). Or by hand: `hq_jobs.py stills final all`, `hq_jobs.py sheet sheet all`,
   `hq_compose.py stills all`, `hq_compose.py sheet all`, `hq_sheet.py`, `hq_jobs.py reveal video`,
   `hq_compose.py frames reveal`, `hq_encode.py reveal`.
3. Previews without the GPU lock: `hq_jobs.py stills eevee all`. Test frames with the lock: `hq_test.py <names>`.

| Script | Contents |
|---|---|
| `hq_preset.py` | The Meridian variant of the r3 preset |
| `hq_graph.py` | The fortress layout, the graph, the yard cycle (movers), the shot lists (stills, sheet, reveal) |
| `hq_build.py` | The Blender build of the fortress, the crane, the train, MANIFEST CONTROL, the landmark rig |
| `hq_mechui.py` | The yard cycle's 2D language (badges, chips, the pencil telegraph, the dial, the sheet text) |
| kit `hqk_graph.py`, `hq_cam.py`, `hq_scene.py`, `hq_overlay.py`, `hq_jobs.py`, `hq_compose.py`, `hq_post.py`, `hq_encode.py`, `hq_sheet.py`, `hq_values.py`, `hq_test.py`, `hq_all.py`, `gpu_lock.py` | The HQ kit generalised from Halcyon's scripts (free-form layouts: any room frame, movers, a mechanic hook module); shared by the four corps |
| `hq_kit/` | Halcyon's hq_kit (city ring, LOD bands, states), copied unchanged |
| Kit copies | `kit44`, `ui31`, `r31lib`, `r32ui`, `r35ui`, `sidekit`, `wax_r2`, `sticker_lib19/31`, `markers42`, `city_view`, `route_d_city`, `crests15`, `emblems20`, `look_preset` from hq_halcyon |

Seeds: city 5311, containers 5320, yard stacks 5321, rails / signals 5322, landmark rig 5330, lanes 9402, beams 9500,
plumes 9510, Cycles 7.

<!-- hq_rev v2 r2 -->
## v2 revision, round 2 (hq_rev)

### v2 round 2 (art director 20:55 + designer note on the train)
- Values: an ORANGE-weighted haze bank round the fort (`hq_fog.bank`, r 128-230 BU, 0-34 BU high, lit from below by
  the bank glows in work orange and sodium), with a neutral haze further out. The city windows are lit
  (`win_p` 0.36, `win_k` 0.34), so the city mass reads as lit blocks instead of black window confetti.
- THE FREIGHT LINE OUT (designer: "Meridian needs a train track leading away ... Make is viable"). This is set dressing
  only: the route, the nodes and the overlay are unchanged.
  - A switch off the yard loop's north side.
  - The line runs north through a PORTAL in the platform wall: two container columns, a lintel container, the
    MERIDIAN FREIGHT stripe, and green and red signal lamps.
  - It crosses the moat on a truss bridge, then ramps up onto an elevated VIADUCT on piers at deck z 22.
  - The viaduct has parapets with the Meridian-orange rail glow, catenary masts, signal lamps, and a train's light
    streaks running out (white heads ahead, red tails behind).
  - It threads a cleared CORRIDOR (`downtown.corridor` / `city.corridor`): no lot or ring tower is built on it, so it
    never passes through a building.
  - It runs out of frame toward the port at y 1180.
  - Along the corridor the city steps down to low rail-side sheds and warehouses (`corridor_low`: within 40-46 BU of
    the axis, heights capped at 16-18 BU, no crowns), so the viaduct reads above the roofs from the overview.

### Occlusion: camera-rig rule (v2, all five HQs; designer note 2026-10-15)

Designer, verbatim: "The foreground blocking buildings should be flattened or made transparent when the camera needs to
look through them to see the HQ." This replaces the v2 sloped section cut. Code: `hq_kit/downtown.py`
(`occlusion_params`, `occlusion_state`: pure python, the rule itself) and `hq_kit/section.py` (the same rule as a
clip in the city materials). Called per frame from `hq_jobs.frame()`; `hq_scene` logs how many buildings it touched.

| Step | Rule | Numbers (`downtown.OCC`, a corp may override in preset `downtown.occ`) |
|---|---|---|
| Inputs | The camera position, and the TARGET VOLUME: the front points of the active room plus the visible route nodes (decision / hover: the current room + its options; overview: every route node). | - |
| Cone | Every ray from the camera to the target volume. Horizontal frame: `u` = the direction to the targets' centroid. Per target: lateral tangent `t = across / along` and vertical tangent `v = (z - cam z) / along`. Only targets **behind** a building can be hidden by it, so the cone is sampled at `NK` depths (knots) from the nearest to the farthest target. At each knot it holds `[t_min, t_max]` and `v_min` (the lowest ray) over the targets behind that depth, widened by `margin` of the whole volume's span (the ~10 % margin). | `margin` 0.10, `NK` 5 |
| Occluder | A city building is an occluder when its footprint (radius = half-diagonal) overlaps `[t_min, t_max]` at its depth, it stands in front of the farthest target, and its top reaches into the cone (`(top - cam z) / (along + r) > v_min`). Compound geometry is never an occluder. | - |
| Step 1: FLATTEN | An occluder is section-cut to a lit stub of `stub` BU (1-2 storeys: shop fronts, awnings and the lowest windows stay lit). Its open top shows a near-black POCHE, so it reads as a cut model and not as a hollow shell. | `stub` 6.4 BU |
| Step 2: GHOST | If the stub still reaches into the cone, it fades to `ghost` opacity. Its window dots stay (dimmed with it) and a faint cool edge line traces its box edges. It is never fully invisible. | `ghost` 0.18, `edge` 0.6 |
| Outside | Buildings outside the cone keep their full height. Roof clutter (tanks, antennas, holo boards) is cut with its building. | - |
| Easing | The cone has soft borders (`tsoft` lateral tangent, `vsoft` vertical tangent). As the orbit camera moves, a building's cut height and opacity slide across the band and never snap. In the game the values are per-instance targets eased over 0.4 s (below). | `tsoft` 0.035, `vsoft` 0.025 |
| Outputs | Per building: cut height (`top` + clutter outside the cone, `stub` inside, interpolated across the soft band) and opacity (1, or `ghost`). `occlusion_state(params, building)` returns exactly these values. | - |

Godot 4.7 mapping (camera rig, not content):
- The city is MultiMeshes. Each instance carries `INSTANCE_CUSTOM = (cut_height, opacity, centre-relative edge
  data)`. Each frame the camera rig (a `RefCounted` helper fed by the orbit camera, outside the deterministic core)
  runs `occlusion_state` per building in the near rings and writes the per-instance target.
- The view tweens each instance's current value toward its target over 0.3-0.5 s (0.4 s default, ease in-out), so
  buildings never snap when the cone sweeps across them.
- City shader (spatial, opaque pipeline): `if (world_vertex.z > cut_height) discard;` gives the per-instance height
  clip. A back-face branch draws the poche colour, so the cut reads as solid.
- Ghost: a dithered alpha fade (an alpha-hash / screen-door `discard` against a 4x4 Bayer threshold scaled by
  `opacity`), which keeps depth sorting stable without a transparent pass. Edge lines come from the box-local
  distance in the same shader. The window emission stays on and is multiplied by `opacity`.
- Cost: one uniform block, one per-instance vec4, no extra draw calls.

<!-- hq_rev v2 full -->
### v2 full render: the pipeline spec + a believable grade (art director)
- ONE freight line, shared with the city render. Spec deck z 17.5 one-city units (1 floor = 1.9 BU) = 73.7 BU in HQ
  units (1 storey = 8 BU): it clears the frontage along it by about 2 storeys and never towers over it.
- It leaves by the NORTH RAIL-YARD GATE (the portal on the north platform). The moat runs on the W, S and E sides only;
  the north side is the rail yard: a paved apron with three east-west sidings, no moat, no bridge.
- The incline is a 3 % freight grade (`viaduct.grade`). The climb starts in the rail yard (y 150) with a 40 BU vertical
  curve and carries on along the viaduct outside the wall. At 3 % the deck reaches 73.7 BU off frame; in frame it rises
  from grade to about 31 BU at the frame edge.
- The rail-side frontage follows the deck: its cap is the deck height at that point minus 2 storeys (16 BU), kept
  within 8-57.7 BU (`corridor_low` = (dist, hmax, s0, grade, zmax, clear, hmin)). So the deck always sits just above
  the roofs beside it.
- Values: t2b passes (overview 0.163 / 27 %, ratio 1.73).
