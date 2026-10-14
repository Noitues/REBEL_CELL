# Route map side view: V3 dynamic ("dollhouse dolly", iterated, 2026-10-14)

V3 from `../NOTES.md`, made dynamic for the designer's four asks:
1. a parallax camera that moves along the run;
2. two zoom levels;
3. a detailed, lit background;
4. varied architecture and connection types.

Every camera move here is a **real per-frame Blender camera** on the 3D street, not a 2D crop-zoom. Each video frame is its own Blender render, with its own projected overlay anchors.

The run is the parent's: the same 19-node graph and the same mid-run state.
- The walk is fight, then event, then the shop.
- Option 1 is a fight; option 2 is the Rack.

Nothing is committed, and the Godot build is untouched. Scratch files were deleted at the end.

## Files

| File | What it shows |
|---|---|
| `D_start.png` | Decision view at the run start. The camera sits left and looks right (yaw +24°). It frames the relay and the three options, with the street ahead receding to the right. |
| `D_mid.png` | Decision view mid-run, with the camera centred (yaw 0°). It frames the shop, option 1 (the fight, through the service tunnel) and option 2 (the Rack, by cargo lift). |
| `D_mid_hover.png` | The same view, hovering option 2. The branch blooms and the rest of the street drops to 32 % (power cut). The camera eases 22 % toward the Rack, turns 3° toward it and dollies in 4 %. The `RACK  L4` tag and the node file (with HP on arrival) appear. |
| `D_end.png` | Decision view in the last room before the TARGET (the elite on L6). The camera sits right and looks back left (yaw −24°). Option 1 is the TARGET, by maintenance tram rail, with the red pencil TARGET. |
| `O_overview.png` | The overview: the whole run (V1-like, yaw 0°, lens 40 mm), with the varied architecture and the layered city behind it. |
| `cam_run.mp4` | 7.7 s at 24 fps, 1280 × 720 (184 real Blender frames, encoded with Blender's own FFmpeg; there is no ffmpeg on PATH). It shows, in order: the start; three steps (fire escape, plank, duct) with the parallax pan; a hover ease onto option 2 and back; a zoom out to the overview; a zoom back in. |
| `zoom.gif` | The decision-to-overview transition alone: 35 frames, about 1.6 s, at 960 × 540. |
| `architecture_sheet.png` | 2560 × 2070. The 10 connection types, each between two stub buildings, with the route drawn as an orange dash and labelled with its step hint. Below them, the 7 building silhouettes. |
| `compare_v3.jpg` | The old V3 mid beside the new D_mid, D_mid_hover and O_overview (2 × 2, labelled). |
| `scripts/` | Everything needed to rebuild. See "Rebuild". |

## What changed from the old V3

| Old V3 | V3 dynamic |
|---|---|
| One fixed 3/4 camera. The step dolly was a 2D crop of the finished frame. | A camera rig (`cam_rig.py`) solves a pose for every state. The video renders every frame in Blender, and the overlays are re-projected per frame. |
| The far rooms were small and the past was large (the camera looked from the TARGET end). | The camera yaws with the run and always faces the unexplored side, so the decision set always fills the frame. |
| 8 identical-width blocks in one plane. Every link was a catwalk plus a lift riser. | Columns vary in width (12–18 BU) and depth (−3 to +3 BU), with 7 silhouettes. There is a mid row, three far layers and 10 connection types. |
| Floors were spread over 1–8 (option sets spanned 6 storeys). | Floors are compact (see Depth): an option set spans at most 4 storeys, so the rooms can be big. |
| The background was a two-layer hazed skyline. | Light shafts, searchlights, three lanes of sky traffic, alley glow, steam, rain lit by spill, height fog, and a background grade. |

## Camera rules (spec; `scripts/cam_rig.py` is the reference implementation)

**Pose.** A pose is the focus F, plus yaw ψ, pitch φ, distance D, lens f, and lens shift (sx, sy).
- The camera sits at `F − D·dir` and looks at F, where `dir = (sin ψ cos φ, cos ψ cos φ, −sin φ)`.
- ψ > 0 looks right, down the street (+x). There is no roll.
- The lens shift is in units of the frame width, as in Blender. In Godot, use `Camera3D.PROJECTION_FRUSTUM` with `frustum_offset`, so the framing keeps its perspective while it is off-centre.

**Usable area.** The street area is x 300–1900 and y 138–1012 px at 1080p. That is right of the sidebar, under the DISPATCH strip and above the legend. Every framing is centred in this rectangle, not in the frame.

### Yaw and pan along the route
- **Yaw:** `ψ(u) = 24° · (1 − 2u)`, with `u = current layer / (TARGET layer − 1)`, clamped to 0..1.
  - At the start (u = 0), ψ = +24°: the camera is on the left, looking right at what is ahead.
  - Mid-run (layer 3 of 6, u = 0.5), ψ = 0°: centred.
  - At the last room (layer 6, u = 1), ψ = −24°: the camera is on the right, looking back left.
- **Pan:** F is the centre of the 3D bounding box of the decision set, so the camera pans along the street as the operative advances.
- **Look bias:** after centring, the set is pushed 10 % of the usable width away from where the camera looks: `bias = −0.10 · ψ/24°`. This leaves screen room for the rooms ahead (at the start, they sit on the right).

### Decision view (the default)
- **The decision set:** the current room plus every available room, 8 world corners each.
- **Fixed values:** pitch 9° (looking down), lens 30 mm (36 mm sensor, horizontal fit).
- **Distance:** a bisection on D (60 iterations, log space) so the set's projected box fills **66 % of the usable width or 70 % of the usable height**, whichever binds. Then the shift centres the set (plus the look bias).
- **Measured on the stills** (the decision set fills about 70 % of the usable height):

  | Still | Camera distance | Option rooms on screen (wide) |
  |---|---|---|
  | D_start | 91 BU | about 210 px |
  | D_mid | 84 BU | about 290 px |
  | D_end | 62 BU | 520 px (the TARGET vault) |

  After a step into a single-option room (video frames 40–90) the set is tiny and the rooms reach about 330 px.
  - Possible cap: add a minimum distance (about 60 BU) if the designer finds that too close.

### Hover ease
- **The move:**
  - F moves 22 % of the way to the hovered room's centre.
  - ψ turns 3° toward it (by the sign of the room's x relative to F).
  - D × 0.96.
- **Timing:**
  - In: 0.30 s, ease-out cubic.
  - Hold while hovered.
  - Out: 0.35 s, smoothstep.
- **No-blink rule:** keep the parent round's rule. The hover is held while the cursor is on any option, with a 120 ms delay, so sweeping across options does not pump the camera.
- **The power cut runs on the same curve:**
  - everything outside the branch (and the current room) goes to 32 % and is 40 % desaturated, times hover_k;
  - branch rooms light ×(1 + 0.45 · hover_k) and spill their type colour.

### Step beat (after CONFIRM)
- **Camera:** a 0.9 s smoothstep from the decision pose of the old state to the decision pose of the new state.
- **Token:** it travels the connection path in the same 0.9 s and arrives slightly ahead (it runs at 1.12× the camera's progress).
- **Overlay:** the lime walked cable grows behind the token. The options that were not picked drop to 45–55 %.
- **Skip:** the beat is skippable (ANIM rules: the press snaps to the end pose).

### Overview
- **Points:** every room, plus the TARGET crown (+6 BU), plus the street start.
- **Fixed values:**
  - yaw 0.3 · ψ(u), which keeps a hint of where you are;
  - pitch 6°;
  - lens 40 mm (flatter, V1-like);
  - fill 95 % of the usable width or 90 % of its height.
- **Toggle:** the `DECISION | OVERVIEW` toggle right of the legend, the Z key, or the scroll wheel (scroll out = overview, scroll in = decision).
- **The transition:** 0.70 s smoothstep, both ways.
  - F, ψ, φ, f and the shift interpolate linearly; D interpolates in log space.
  - The decision-view spotlight vignette fades with it.
- **In the overview, CONFIRM, the number keys and hover still work** (hover does not move the camera there).

**The video's timeline** (`cam_rig.timeline()`, 24 fps):

| Time | What happens |
|---|---|
| 0.5 s | Hold at the start. |
| 3 × (0.9 s step + 0.25 s hold) | The three steps. |
| 0.30 s | Hover in. |
| 0.5 s | Hold. |
| 0.35 s | Hover out. |
| 0.25 s | Hold. |
| 0.70 s | Zoom out. |
| 0.5 s | Hold the overview. |
| 0.70 s | Zoom in. |
| 0.35 s | Hold. |

## Depth and occlusion rules
- **Route columns sit at their own depth:** `DY = [1, −3, 2.5, −1, 3, −2.5, 1.5, 0]` BU (the front face).
  - Rule: |DY[L+1] − DY[L]| ≤ 6 BU, alleys ≥ 10 BU, |yaw| ≤ 24°.
  - So a forward building's side wall projects at most 6 · tan 24° ≈ 2.7 BU into the alley and never reaches the neighbour's opening.
  - Links run diagonally in depth across the alley.
- **Compact floors** (presentation only; topology and types are the parent's).
  - The rule: siblings sit on consecutive floors where possible, a step moves at most 4 floors, and the TARGET is on floor 6.
  - The floors:

    | Layer | Floors |
    |---|---|
    | L1 | 1 / 2 / 3 |
    | L2 | 1 / 3 / 4 |
    | L3 | 2 / 3 / 5 |
    | L4 | 0 / 3 / 4 |
    | L5 | 1 / 3 / 5 |
    | L6 | 2 / 4 |

  - The decision set then spans at most 4 storeys.
  - It is also on-style: the mockup stacks lit rooms directly on top of each other.
  - L4_0 sits on the street floor because its link is the service tunnel.
- **Depth layers, from near to far (y in BU):**

  | Layer | Depth (y, BU) | What is there |
  |---|---|---|
  | Foreground occluders | −36 to −58 | lamp posts, a parked van, a kiosk, a fence, a sign gantry |
  | The road | −40 to −9 | cars, and the service-tunnel trench (y −9 to −1) |
  | The route row | −3 to +15 | |
  | The mid row | +18 to +52 | parking structures, a footbridge block, a billboard frame, setback towers, a slab |
  | Alley glow cards | +30 and +48 | |
  | Light shafts | +58 and +95 to +220 | |
  | Far city | +70, +140 and +260 | three layers |
  | Sky traffic | +52, +115 and +205 | lanes |

- **Mid-row placement:** mid-row blocks stand behind route columns, not behind alleys. Seen down an alley, you look past the route into the glow, the shafts and the far city.
- **Never hide an available room:**
  - Each foreground occluder is its own node.
  - In every shot, any occluder whose screen box overlaps the screen box of a protected room is hidden. The protected rooms are the current room plus the options; the box gets a 12 px margin and 40 px on top for the sticker. In Godot, the occluder dither-fades over 0.15 s.
  - This hid the fence in D_start and in 26 of the 184 video frames (the start and the first step). In the overview nothing is protected, because the rooms are small and the overlay carries them.
- **The check** (`check_occlusion.py`, from the semantic pass):
  - **What counts as blocked:** pixels of a facade, the mid row, the far city, the ground, a foreground occluder, or another column's cut or room, inside the opening shrunk by 3 px.
  - **Result:** in every still, and in every decision, hover and overview frame of the video, available rooms are **0.0 % blocked**. During the first step's pan, the option that was *not* picked (L1_2) reaches 4.4 % blocked at the frame edge, under the 8 % limit. Link structure crosses at most 2.5 % of an opening, and that is allowed.
  - **Limit:** the script fails above 8 %.
- **Links in front of rooms:** link structure may cross a room opening (the route arrives at the room). The overlay cables are drawn above everything.

## Connection types

All 10 are used in this run, plus the parent's conduit for one edge.
- **The rule:** the type follows the step class:
  - same floor: tube, plank or data-pipe;
  - rising: lift, fire escape, duct, tram or conduit;
  - falling: zip-line, duct, tunnel or roof jump.
- The type is a hint only. Every node type still reads from the room dressing and the sticker.

| Type | Geometry | Step hint | Used on |
|---|---|---|---|
| Skybridge tube | An octagonal tube with ribs, a lit glazing band and a deck. It may slope. | Level or a gentle climb | L1_2→L2_2, L2_1→L3_1 |
| Zip-line | A boom post at each end, a steel line, a trolley with a hand bar and a red tip light. | Down | L1_1→L2_0, L2_2→L3_1, L4_1→L5_0, L5_2→L6_1 |
| Cargo lift | A lattice shaft, a yellow cage at the source floor, a head wheel and amber warning lights. | Up (or down) | L0_0→L1_1, L3_0→L4_1 (option 2), L5_1→L6_1, L6_0→L7_0 |
| Ventilation duct crawl | A square duct with flanges, 45° bends and a grille glow. | One floor either way | L2_0→L3_0, L5_1→L6_0 |
| Fire escape | Switchback flights with landings every half storey, rails and posts. | Up, floor by floor | L0_0→L1_0, L1_1→L2_1, L2_2→L3_2, L4_0→L5_0, L4_2→L5_2 |
| Rooftop jump | A facade ladder up, a kicker ramp, a jump arc (overlay only), a hazard landing mat and a hatch. | Roof to roof, down | L3_2→L4_2 |
| Maintenance tram rail | Twin rails on sleepers and trestles, with a yellow tram car halfway up. | Steep climb | L5_0→L6_0, L6_1→L7_0 (the TARGET) |
| Window-to-window plank | A board between the window sills, a sag rope and a crate. | Level | L1_0→L2_0, L4_1→L5_1 |
| Data-pipe | A thick pipe at door height + 2.6 BU, with flanges, a cyan slit and **6 packets flowing** along it (animated). | Level | L3_1→L4_1 |
| Service tunnel | A caged stair shaft down, then a cut half-tube under the street (seen through a hazard-railed trench) with amber strip lights, then a hatch up into the room. | Down, under the street | L3_0→L4_0 (option 1) |
| Conduit catwalk (parent) | A catwalk plus a lift riser, as before. | Climb | L0_0→L1_2 |

- **Lanes:** the lift, fire escape, conduit and tunnel use an alley lane. The parent's order holds: rising, the one that ends higher goes further left; falling, the one that ends lower goes further left.
- **Self-check:** `sgraph3.py` checks that no links in one alley cross in elevation. It reports 0.
- **Arrivals:** the data-pipe enters 2.6 BU above the door, so it never shares a door segment with the lift that arrives at the same room.

## Background layers (ask 3) and performance

| Layer | How it is built | Godot build note |
|---|---|---|
| Far city | 3 layers of seeded towers (y 70/140/260) with crowns, antennas, red beacons and a few neon strips. | Static meshes, one material with a `layer_dim` uniform. The far layers can be baked into 2–3 large impostor cards. |
| Mid row | Parking structures (open decks, ramp, parked cars, deck light strips), a footbridge block, a billboard frame, setback towers, slabs, and blade signs. | Normal city-kit meshes. |
| Light shafts | 28 additive quads with a soft horizontal falloff and a vertical fade: magenta, cyan and violet. | Unshaded additive `MeshInstance3D`s, about 30 draws. No volumetrics. |
| Searchlights | 4 additive hexagonal cones on far roofs, swept by `sin(0.55 t)`. | Additive cones on a tween. |
| Sky traffic | 3 lanes at 3 depths, 32 vehicles with head and tail lights and additive trails, wrapping across 560 BU. | One `MultiMesh` per lane. |
| Alley glow | Additive gradient cards in the gaps behind the route, plus small glow sources at their foot. | Additive quads. |
| Steam | Noise-textured additive plumes from street grates and roof vents. | A `GPUParticles3D` with 6–10 particles per vent, or the same quads with a scrolling noise. |
| Rain | Post streaks, falling with t. Their alpha follows the blurred glow, so rain catches the light near signs and rooms. | A screen-space rain shader that samples a quarter-resolution glow buffer. |
| Haze and fog | Depth haze starts at 1.18 × the camera distance and ramps over 260 BU (violet, more magenta low). Height fog pools under 26 BU in the distance. | `WorldEnvironment` depth fog plus height fog, with the start distance driven by the rig. |
| Background grade | The mid row and far city are 40 % desaturated, ×0.62, softened 1.4 px and inked at 55 %. | Per-material uniforms on the background meshes, not a post pass. |

- **Is the background quieter than the route?**
  - Yes, in every still.
  - The only saturated background pieces are the mid-row billboards and blade signs. They are kept small and away from the decision set.
- **Performance estimate** (Godot 4.7, Forward+):
  - the route row is about the parent V1 / V3 cost;
  - the background adds about 150 draws: far layers as impostors, traffic as MultiMesh, about 40 additive quads;
  - no shadows, no volumetrics; fog is the built-in;
  - this should hold 60 fps on the target spec;
  - the camera move itself is free. Only the overlay re-projection (`unproject_position` for about 19 rooms and 25 links) runs per frame.
- **Blender cost here:** about 6 s per 1440 × 810 frame for 7 passes, and about 5 s per frame for the post plus overlay.

## How this extends to HQ netruns
An HQ netrun is a **compound**, not a street. Each corp HQ has its own authored set piece: the keep, the yard, the vault, the antenna farm. The same rig drives it with **camera beats**:
- **A beat is a per-layer record in the HQ content `.tres`:**

  | Field | Meaning |
  |---|---|
  | `yaw` | The yaw curve, or a fixed yaw, replacing ψ(u). |
  | `pitch` | Negative to look up a tower, positive to look down into a yard. |
  | `lens` | The lens for this layer. |
  | `look_bias` | Where to leave screen room. |
  | `fill` | The framing fill. |
  | `entry_move` | `pan` / `crane` / `orbit`, plus a duration. |

  - The decision framing solver, the hover ease, the overview and the occlusion rule stay as they are.
  - Only ψ(u) and the step tween are replaced by the beat's keys.
- **Examples by compound:**
  - **Meridian freight yard:** a long low orbit along stacked containers (yaw sweeps 40°). Rooms are container interiors, and links are crane hooks and conveyor belts.
  - **The keep climb** (the round 35 hq_climb ancestor): the run is vertical.
    - Layer = floor band, slot = a wing (left, centre, right).
    - The camera cranes up with pitch from −10° to +20°, and yaw swings between wings.
    - Links are internal: the lift core, stairwells and ventilation.
  - **The vault:** the last two layers drop below ground, and the camera follows the service tunnel with a low pitch.
- **Unique view per HQ:** the camera beats, the silhouette kit and the connection subset are content, not code. A new HQ is a new `.tres` (layout archetypes + beats + palette), so "unique views" do not need new systems.
- **The step-hint rule carries over** (lift = up, tunnel = down). HQ-only types are allowed: crane hook, conveyor, maglev shuttle. The type still never names the node.

## The 3-second check (done on every render)
- **D_start:**
  - The relay is lime, bottom left.
  - Three orange numbered rooms are stacked in the next block: 1, 2 and 3, all fights (cyan monitor walls and the fight sticker).
  - Each dashed orange line is visibly a different structure: 1 is the fire escape, 2 the lift lane, 3 the conduit.
  - The white dashed links beyond show the next block's rooms (event, fights, the shop sticker).
  - **Passes.**
- **D_mid:**
  - 2 is the Rack: gold cabinets and the rack sticker, reached by a dashed line up the lift lane.
  - 1 is a fight on the street floor. Its dashed line drops down the alley, runs under the street in the trench, and comes up into the room.
  - The white links show where each leads: 2 forks to a fight and an elite; 1 leads to the elite.
  - **Passes.**
- **D_mid_hover:** the branch of 2 (the Rack, then the fight, then the elite) is the only lit thing; the tag reads `RACK  L4`. **Passes; it is instant.**
- **D_end:**
  - 1 is the TARGET vault, circled in red pencil, reached by the tram rail.
  - The walked lime path reads back to the left.
  - **Passes.**
- **O_overview:**
  - The V1 read: every room, walked lime on the left, options 1 and 2 in the middle, the white branches to the TARGET.
  - **Passes for the next step.** The rest needs tracing, as in V1. That is what hover and the decision view are for.
- **Occlusion:** 0 % on all available rooms (above).
- **Fixed during the check:**

  | Problem | Fix |
  |---|---|
  | Contour bands on the ground and facades. The 8-bit depth was read as a 16-bit RGB PNG, which PIL truncates. | Depth and wz are written as single-channel 16-bit. |
  | Option sets spanned 6 storeys, so the rooms were too small. | The compact floors. |
  | Stacked rooms' stickers and number chips sat on the room above. | They moved to the room's left cut edge, 38 % down, with the chip to its left. |
  | Red neon strips on the TARGET tower crossed the TARGET vault, and its windows read as rooms. | The strips were removed; the windows became small dim slits (with their own seeded stream). |
  | The tram car sat in front of the elite room. | It moved halfway up the rail. |
  | The tunnel ran below the frame in D_mid. | It is shallower and closer to the facade, and the trench was moved. |
  | Mid-row blocks filled the alleys. | They moved behind the columns. A saturated pink alley card competed with the option-1 line, so it was cut to a small glow source plus a soft additive card. |
  | The background was too bright in the overview. | Background grade ×0.62 and darker far colours. |
  | The sidebar read "Keys 1-1". | Now "Key 1 goes now". |
  | The DISPATCH line ignored the current room. | Now per room. |

## Open questions for the designer
1. **Compact floors.** The decision view only works if an option set is at most about 4 storeys tall. Can the generator own that rule? Floors stay presentation-only. Two floors changed versus the parent: L4_0 is on the street, for the tunnel. Topology and types are untouched.
2. **Decision distance varies with the set.** One option means a very close camera; three spread options mean further out. Do we cap it (minimum about 60 BU), or keep the "big when the choice is simple" feel?
3. **The look bias of 10 %.** At the start, the set sits left of centre so the street ahead shows. Is that the right amount?
4. **Foreground occluders vanish when they would cover a protected room.** In the video this is a cut, a pop. The build should dither-fade it (0.15 s). Or should occluders simply never be placed in front of route columns?
5. **Connection type as a hint.** The lift means up and the tunnel means down. A zip-line or tunnel could later carry a rule (e.g. "a zip-line step can't be reversed", "a tunnel costs no Heat"). The brief says hint only, so they are presentation-only for now.
6. **HQ camera beats as content.** Are per-HQ camera beats a content field in the HQ `.tres` (proposed), or a hand-built scene per HQ?
7. **The overview while a hover is held.** Should hover in the overview also run the power cut (proposed: yes, without the camera ease)?
8. **The DISPATCH lines are placeholder copy and need a writer.**

## Not done / limits
- **Mid-row signs:** the billboards and blade signs show stripes and a disc, not real ad art.
- **The architecture sheet's strip edges** show a sliver of the neighbouring cell (one strip per 5 cells on one long line).
- **The video does not show the overview's hover.** The hover is held only in the decision view.
- **Foreground occluders pop** rather than fade in the video (see question 4).
- **Steam is subtle at 1080p.** It reads most at the start and in the overview.
- **The video is 1280 × 720** (the brief asked for at least 960 × 540). It was rendered at 1440 × 810 with 8 samples; the stills were rendered at 2880 × 1620 with 24 samples.

## Rebuild
Run everything from `scripts/`. Nothing launches Godot. Blender 5.2 runs headless; its logs go to `scratch/`.
1. `python emblems20.py` (the corp emblems used by the holo file seal).
2. `python sgraph3.py` (the layout self-check: 0 crossings).
3. `python jobs.py stills`, then `python post3.py <name>` for each of D_start, D_mid, D_mid_hover, D_end and O_overview.
4. `python compose3.py stills`, then `python check_occlusion.py stills`.
5. `python jobs.py video` (184 frames of passes), then `python compose3.py frames` (post plus overlay per frame), then `python check_occlusion.py video`.
6. `python finish3.py mp4`, `python finish3.py gif`, `python finish3.py compare`.
7. `python jobs.py sheet`, then `python finish3.py sheet`.

All randomness is seeded:
- Blender uses `random.Random(4207)`, with an atmosphere seed of 91 and per-floor seeds for the TARGET windows;
- the post noise and rain use fixed numpy seeds; the rain falls with t.

`sgraph3.py` imports the graph and states from `sgraph.py` (the parent's copy). The kit modules are copies from `../scripts/`, with their concepts-root path deepened by one folder.
