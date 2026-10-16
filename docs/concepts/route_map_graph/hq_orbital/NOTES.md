# HQ netrun: Orbital Commons, "the retarget cycle" (2026-10-15, revised after the designer's review)

The Orbital HQ run in the approved route-map look (AAA-2 r3) with the designer's HQ lighting rule (the landmark keyed,
rimmed and separated from the city by lighting, about 1.5-2x the local background, readable at 320 px). Revised the
same day after the designer's review: the camera is front and centre on the active room and orbits the complex; the
antenna is a real truss tower with decks and two elite vaults; the rocket and the sabotage story carry the mechanic;
the launch cutscene is storyboarded; H_decision is lifted with lighting. The first version (a door crossing over the
silo) is archived in `D:\rc_scratch\hq_orbital\v1\`. Nothing is committed; Cycles HIP in the shared GPU queue; Eevee
for layout previews only.

## Files

| File | What it is |
|---|---|
| `H_overview.png` | OVERVIEW from the north-north-west (pitch 46): the launch podium, the silo with shut doors, the antenna tower with its elite vaults, the dish stations, the service gantry with LAUNCH CONTROL (TARGET), the override drawn in red pencil from the antenna's top room. |
| `H_decision.png` | DECISION, circuit 4, front and centre on ANTENNA DECK 2 (just cleared): option = one more circuit (NW dish) or the LAUNCH OVERRIDE to LAUNCH CONTROL (fire the rocket early into the shut doors: the HQ is destroyed). The dial: CIRCUIT 4, RETARGET 3/3, BAY DOORS SHUT, OVERRIDE LIVE. |
| `H_hover.png` | The same, hovering the override: the power cut, the branch, the rule note. |
| `H_rocket.png` | The rocket view at circuit 2: the doors open, the rocket risen out of the silo (the hero), two hacked bands lit lime on the hull, warning strobes, the RETARGET 2/3 readout with the new target, the gantry and LAUNCH CONTROL, the override still LOCKED (dashed pencil). |
| `H_launch_board.png` | The launch cutscene as a 7-panel storyboard: sabotage, pull out to the city, launch, the arc over the city, descent, the strike on an Orbital facility, back to the HQ; with timing. |
| `H_launch_strike.png` | The city-wide strike moment, 1920 x 1080, no UI. |
| `H_mechanic_states.png` | The design-language sheet: room states (option, the antenna's elite vault current / walked, the override TARGET), three shots (circuit start, the antenna, the sabotage), the dial, the rule cards. |
| `H_reveal.mp4` / `.gif` | 6.5 s HQ beat: inside the open silo looking up the rocket, up past its nose while it sinks and the doors close, then the pull-back to the OVERVIEW; route and UI last. |
| `plates/`, `scripts/` | Plates without UI; everything to rebuild. |

## 1. Layout rules (`scripts/hq_graph.py`; numbers in `hq_preset "compound"`)

| Element | Rule |
|---|---|
| Podium + silo | A round launch podium (r 64, h 10), the silo (r 17) at its centre: the yellow-black caution ring, launch-glow rings in the shaft, two door leaves with chevrons and an ice seam (open / shut reads at a glance). |
| Rocket | Body r 6, h 58, nose, fins, two red bands; three HACK BANDS of access panels (lit lime per retarget); a mover: below ground with the doors shut, risen 62 BU at a circuit's sabotage. |
| Stations | PAD (start), SE, NE, NW, SW dish bunkers on the ring (r 96), openings facing out; dishes with lit ice rims; the ringed-planet crest on the PAD. |
| Antenna tower | At azimuth 0: a tapering 4-leg truss (X braces every 8 BU, 104 BU + mast), equipment decks at 26 / 52 / 78 with lit railings, dishes on the top deck, red markers; two ENCLOSED ROOMS (elite vaults, red trim) on its outer face at decks 1 and 2, outer stairs between the decks. |
| Gantry + LAUNCH CONTROL | The red service gantry south of the silo (70 BU, service arms to the rocket); LAUNCH CONTROL is the glazed deck on it (the TARGET, open all round). |
| Links | The ring causeway; up the antenna's outer stair, down its west stair; the sabotage link to the silo rim; the override from the antenna's top room down to LAUNCH CONTROL. |

## 2. Preset variant
r3 look; `PRESET["hq"]`: ice #CDF0FF, pale steel, caution yellow, launch orange-red, red markers, the Cell's lime for a
hacked panel; the city darker. New light keys (the review): `pad_flood_w` (6 flood masts at the podium rim),
`svc_w` (the rocket's service light, rides the rocket), `room_key_w` (a key from the camera side + a rim from behind on
the active room and its options, moved every frame), `underfog_w` (fog lit from below round the podium), `strike` (the
cutscene: site, apex, glow, trail, blast).

## 3. The mechanic: GDD vs proposal

| What | Source | Status |
|---|---|---|
| Orbital's Central Server | GDD 11.7 "Launch Control"; 8.4d "the Commons Array"; round 43 "the missile bay" | Here LAUNCH CONTROL is the TARGET; names **flagged** (Q1). |
| The loop of stations, one missile a lap, sabotage at the lap's end, the 4th fired inside the shut bay destroys the base | Round 43 (decision: the missile loop) | Kept, reworded by the review (**proposal**; "destroy the HQ with its own rocket" is not a GDD win condition, 1.3). |
| Each circuit RETARGETS the rocket: it strikes Orbital's own facilities in the city / in orbit, not the city | Designer review 2026-10-15 | **Proposal** (narrative). |
| The last circuit's SHORTCUT (the LAUNCH OVERRIDE, from the antenna's top room) fires the rocket one round early into the SHUT doors | Designer review | **Proposal**. Here it unlocks after 3 retargets; on circuit 4 the player picks the override or one more circuit (Q3). |
| ELITE rooms on the antenna every circuit | Designer review | **Proposal** (the antenna is mandatory on every circuit). |
| Visual language: ANTENNA ELITE chips, RETARGET n/3 on the rocket node, the override in red pencil (dashed + LOCKED before 3/3), the rocket readout, the dial (circuit, retarget cells, the doors, the override), hacked bands lit in 3D | This round | **Design-language proposal**; state colours unchanged. |

GDD-fit: pacing (GDD 4.2 / 11.8: ~5 combats, ~15 min) does not survive four 7-room circuits: round 43's decision ("cut
encounters to keep within the time rule") still needs a rule (Q2).

## 4. Camera beats
| Beat | Rule |
|---|---|
| DECISION | FRONT AND CENTRE (the review): the camera stands off the active room's normal, the active room in the middle of the usable frame, the options in view; as the circuit advances the camera orbits the complex (pitch 16-26). |
| OVERVIEW | From the NNW, pitch 46, lens 36 (the antenna's elite vaults face the camera). |
| H_rocket | Low from the south-west (26 mm): the rocket, the gantry and LAUNCH CONTROL. |
| REVEAL | Up out of the silo along the rocket, then the pull-back. |
| The launch cutscene (future; storyboard frames) | After each circuit's sabotage: pull out to a city-wide view side-on to the rocket's arc (so it reads as an arc), the launch, the arc, the descent on an Orbital facility (or a satellite: a sky strike), the strike, back into the HQ. ~7 s, timing on the board. |
| The HQ-explosion cutscene (planned, NOT made) | Beat list: 1 the override at LAUNCH CONTROL, alarms, the doors stay SHUT; 2 the rocket ignites in the silo, the doors bulge, light leaks from the seam; 3 the doors blow, a fireball column; 4 the chain reaction runs round the ring (the prep / fuel lines): dish bunkers pop one by one, the antenna tower falls; 5 the city-wide shot: a mushroom of fire where the HQ was; 6 the Cell's lime hack mark on the skyline, the run is won. |

## 5. Godot 4.7 mapping
| Element | Godot | Perf |
|---|---|---|
| Podium, stations, dishes, gantry | Static meshes from the preset ring (`@tool`), dishes instanced. | ~30 k tris. |
| Antenna tower | A truss mesh generated once (legs + braces + decks), the two rooms as room scenes. | ~8 k tris. |
| Rocket | A scene: body + 3 band meshes (instance uniform `hacked`), the service light as a child. Doors / rocket tweened by the circuit state. | Free. |
| Keys on the active room | 3 + 3 SpotLight3D re-aimed on each step (shadows off). | 6 lights. |
| Launch cutscene | A `Path3D` arc, the rocket on a PathFollow3D, a trail ribbon (shader with a reveal uniform), a GPUParticles3D blast + an OmniLight flash; the city-wide camera on its own path. | Cutscene only. |

## 6. Value checks and render log

| Still (2560 x 1440, 64 spp) | median | < 0.10 | > 0.85 | landmark / local background |
|---|---|---|---|---|
| H_overview | 0.199 | 18 % | 1.4 % | 0.452 / 0.178 = 2.5 |
| H_decision | 0.164 | 14 % | 2.0 % | 0.389 / 0.137 = 2.8 |
| H_rocket | 0.175 | 13 % | 2.4 % | 0.454 / 0.152 = 3.0 |

H_decision was lifted with light, not exposure (the review): keys + rims re-aimed every frame on the active room and its
options, six launch-pad flood masts, the rocket's service light, fog lit from below round the podium. The landmark sits
2.5-3x its background (a touch above the 1.5-2 band; the shadows are lighter than r3's 25-40 % under 0.10).
Render log: stills 4 + sheet 3 + launch board 7 (960 x 540) + the strike still (1920) in one locked batch; see
`scratch/timings.json` / `hq_meridian/scratch/batch2.log` and batch3 for the reveal.

## 7. Gaps for the tools step
- Station azimuths, the antenna's decks and the gantry position are preset numbers.
- The struck site in the city is a preset point with its own block (it can overlap a city-ring tower); it should be chosen from the ring's roofs by rule.
- The cutscene cameras are hand-set poses; the circuit shown per still is a preset.
- Light levels (keys, floods, the shaft) were set on Eevee previews + one Cycles test.

## 8. Open questions for the designer
1. The server's name (Launch Control / the Commons Array / the Missile Bay).
2. Four 7-room circuits break the netrun pacing: shorter circuits after the first (cleared stations stay cleared) or fewer circuits?
3. On circuit 4: the override only, or the override OR one more circuit (as drawn)?
4. Sabotage cost: one fight at the rocket (round 43 proposal) or an event?
5. Strike targets: a fixed list of Orbital sites (the readout names) or the GDD's other Orbital Sites on the map?

<!-- hq_rev v2 r2 -->
## v2 revision, round 2 (hq_rev)

### v2 round 2 fixes (2026-10-15)
- The hover node file's cracked seal and tint defaulted to Meridian; it now uses ORBITAL (`sidekit.node_file`).
- The full v2 stills and sheet were rendered before the occlusion rule landed, so they use the v2 sloped section cut.
  The kit files now carry the rule.

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
