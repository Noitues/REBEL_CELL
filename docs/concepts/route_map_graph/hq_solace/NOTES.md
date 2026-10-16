# HQ netrun: Solace Biosystems, "the ladder" (2026-10-15, redesigned)

The Solace HQ run in the approved route-map look (AAA-2 r3) with the designer's HQ lighting rule. **Redesigned the same
day** after the designer's review of the first version (a ribbon double helix with pods, "looks like a dangerous roller
coaster"): the landmark is now two twisting towers joined by a glazed bow-tie skybridge on every floor, and the
route is a LADDER that starts at the bottom and winds up. A second note (v3) made each strand a smooth swept TUBE with
oval portholes in rows (an aircraft fuselage), skinnier and taller. Archived: the v1 ribbon helix in
`D:\rc_scratch\hq_solace\v1_helix\`, the v2 stacked-box towers in `D:\rc_scratch\hq_solace\v2_boxes\`. Nothing is committed; Cycles HIP in the shared GPU queue; Eevee for previews.

## Files

| File | What it is |
|---|---|
| `H_overview.png` | OVERVIEW: the twin towers twisting round each other, a lit bow-tie bridge on every floor (the DNA rungs), the green atrium slots drawing each tower's helix, the crown with THE GENOME CORE (TARGET) and the pink halo, the plaza podium; the city dark behind. |
| `H_decision.png` | DECISION on tower B, route floor 3 (building floor 6), after crossing at floor 2: option UP (tower B, floor 8) or ACROSS (the floor-6 bridge to tower A). Floors above route floor 5 are UNREAD. |
| `H_hover.png` | The same, hovering ACROSS: the power cut, the branch, the rule note. |
| `H_mechanic_states.png` | The sheet: UP / ACROSS options, CURRENT, READ, UNREAD, WALKED; three shots (ground floor, mid-climb after a crossing, the top); the SEQUENCE dial; the rule cards. |
| `H_reveal.mp4` / `.gif` | 6.5 s HQ beat: from the plaza looking up the gap between the towers (the bridges stack overhead like rungs), the camera rises up the gap, turning with the twist, then pulls out to the OVERVIEW. |
| `plates/`, `scripts/` | Plates without UI; everything to rebuild. |

## 1. Layout rules (`scripts/hq_graph.py`; numbers in `hq_preset "compound"`)

| Element | Rule |
|---|---|
| Strands | Two smooth swept TUBES (radius 9, a shared-vertex 40-segment mesh, smooth shaded, glossy porcelain) following the helix: centre 30 BU out at azimuth theta(z) = 90 + 11 z / 12.5 (11 degrees a floor), tower B opposite. 19 floors of 12.5 BU (~240 BU). |
| A floor | A row of 12 OVAL portholes round the tube (half axes 1.7 x 2.9, lit from inside, seeded tints, a few dark) with a thin frame ring each; a downlight ring under the row; a pale-mint light seam rises up the tube's outer side (the light inside the tower; mint, never the route lime). |
| Bridges | Every floor: a glazed BOW-TIE walkway between the tubes' inner sides (13 BU wide where it meets a tube, 4 BU at the waist), lit walls and floor; the route floors' bridges are brighter. |
| Rooms | Route floors 2, 4 .. 16 on both towers (A1..A8, B1..B8): a cutaway room set into the tube's FRONT (normal theta + 90), the tube's skin opened round it. Both towers' rooms of a floor face the same way, so a decision frames the current room, the room UP and the room ACROSS. |
| Links | UP: a stair up the outer edge of the front face (turning with the floors); ACROSS: along the bridge's front edge (the waist); the last floor climbs to the crown. |
| Crown / server | The top floor is a crown joining the towers; THE GENOME CORE sits open in its middle (GDD 11.7; the TARGET). |
| Base | A rectangular plaza podium with steps and the SOLACE name; the clinic gate (start) on the plaza. |

## 2. Preset variant
r3 look; `PRESET["hq"]`: porcelain white, Solace leaf #96FF46 (the atrium slots, window tints, the podium edge), pink
#FF4696 (the crown halo), clinic white (bands, bridges, the ground spots); the city darker (win_k 0.16, less neon) and
the fog halo toned down per the review. Solace lime stays in the 3D, never on a link or ring (bible 2.4).

## 3. The mechanic: GDD vs proposal

| What | Source | Status |
|---|---|---|
| Solace's Central Server = THE GENOME CORE | GDD 11.7 | **Real.** GDD 8.3 / App. A call the final server / boss "the Renewal Engine" (flagged, Q1). |
| The twin towers, the bridge per floor, the ladder (UP or ACROSS each floor) | Designer brief (2026-10-15 redesign) | **Proposal** (not in the GDD). Replaces round 43's three crossovers: every floor is a crossover now. |
| The strands are semi-random node sets | Round 43 decision | Kept: each tower's rooms draw from a seeded deck (preset `seed`, `deck`). |
| The READ rule: 2 route floors ahead are read on both towers, higher rooms UNREAD (kind hidden) | This round | **Proposal** (preset `mech.read_ahead`). With a crossing every floor, reading ahead is what makes UP vs ACROSS a choice. |
| No spinning walkways | Bible Appendix C #10 (round 43 over round 42) | Kept: the twist is architecture, not motion. |
| Visual language: UP / ACROSS chips on options, the '?' disc + UNREAD chip, frosted dim unread rooms in 3D, THE SEQUENCE dial (the ladder ahead) | This round | **Design-language proposal**; state colours unchanged. |

## 4. Camera beats
| Beat | Rule |
|---|---|
| DECISION | The ORBIT-AND-RISE: the azimuth faces the options' floor front (it turns 11 degrees a floor, so the camera orbits as the run climbs), pitch 12-26 by height, the framing solver over the current room + UP + ACROSS. |
| OVERVIEW | Yaw 99 (the front of the middle route floors), pitch 20, lens 34: both towers whole. |
| REVEAL | Up the gap between the towers, then the pull-out. |

## 5. Godot 4.7 mapping
| Element | Godot | Perf |
|---|---|---|
| Strands | Each tube one generated mesh (a `@tool` sweep along the helix, ~20 k tris); the portholes an instanced oval quad + frame (MultiMesh, ~450) with a per-instance lit / tint; the light seam an emissive ribbon. | 3-4 draws. |
| Bridges | One bow-tie mesh instanced 19x; route bridges a brighter instance uniform. | 1 draw. |
| Rooms | Room scenes on the route floors' fronts (16). | Lights: visible rooms only. |
| Downlights / ground spots | Emissive slab-edge strips + ~8 `SpotLight3D` ground spots (shadows off) + ~20 downlight spots (could be baked). | The downlight spots are the cost: bake or drop to emissive. |
| Read rule | A frosted-glass decal + dimmed room light per unread room (state uniform). | Free. |

## 6. Value checks and render log

| Still (2560 x 1440, 64 spp) | median | < 0.10 | > 0.85 | landmark / local background |
|---|---|---|---|---|
| H_overview | 0.071 | 62 % | 0.6 % | 0.369 / 0.046 = 8.0 |
| H_decision | 0.047 | 64 % | 1.8 % | 0.328 / 0.025 = 13 |

The landmark rule (1.5-2x) is far exceeded and the frame median is BELOW the r3 target (0.14): after the review asked
for a dark night city behind the tower, the city windows and the halo fills were cut and the towers' own light carries
the frame. The towers read at 320 px (`scratch/thumb_H_overview.png`). Fix for a next pass (light, not exposure): raise
the city ring's window strength (preset `city.win_k` 0.16 -> ~0.3) and give the plaza podium its own warm wash, which
lifts the median without bringing back the magenta wash.

Render log (Cycles HIP, shared queue): stills 294 s for three (with the build), sheet shots 72 s, the reveal 156 frames
at 960 x 540 in 949 s (~6 s a frame), compose 122 + 59 + 234 s, encode 19 s.

## 7. Gaps for the tools step
- The route floors are a preset list (every other floor); the overview yaw is a preset number (the front of the middle floors).
- Pane patterns are seeded, not authored; the SOLACE lettering position is a number.
- The reveal path is a hand-set rise + pull-out.

## 8. Open questions for the designer
1. The server's name: THE GENOME CORE (11.7) or the Renewal Engine (8.3)?
2. Read ahead: 2 route floors (here), 1, or "read a floor when you stand on its bridge"?
3. Should a crossing cost something (e.g. the bridge holds an encounter) so UP vs ACROSS is not free?
4. Route floors every other floor (8 a tower): fewer, taller climbs?

<!-- hq_rev v2 r2 -->
## v2 revision, round 2 (hq_rev)

### v2 round 2 (art director 20:55)
- The helix is lit. The strands are dark wet porcelain (albedo 0.13, was a pale 0.36) with a leaf-green
  bioluminescent RIM (fresnel emission, `rim_k` 0.9, `rim_pow` 5). The oval portholes are larger (2.1 x 3.3 half
  axes) and lit from inside in a green-white (`porthole_k` 2.6, was `band_k` 0.22), so they read as windows.
- The two towers are apart: `radius` 40 (was 30), a 62 BU gap between the tubes. The skybridges stand only on the
  ROUTE floors: these are the A <-> B cross-links, so the ladder in 3D matches the A/B panel row for row. This departs
  from the redesign's "a bridge on every floor": the non-route bridges filled the gap, and the two towers read as one
  form.
- No flat sky band. A graded night sky (`sky_ramp`, eased; dim violet haze at the horizon to near-black at the zenith),
  more haze (0.0005) so the far skyline fades, and the overview looks down more (`pitch_o` 27, was 20), so more city
  and less sky sits behind the tower.
- The plinth is dark (0.09) and dressed: planter beds with leaf-green edge light, a slatted base course and lit stair
  nosings. THE LIT ENTRY is a glazed clinic lobby at the top of the stair, with warm-white light inside, a leaf-green
  lintel and an area light onto the plaza. The plaza wash is down to 2.5e3 (was 9e3).

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
### v2 full render: tweaks after t2b (art director)
- Bridges only on the cross-links: confirmed.
- The landmark is toned toward about 2.5x its background: the rim is down to 0.5 (was 0.9) and the portholes to 1.6
  (was 2.6).
- No green spill on the bridge slabs: the bridges, podium and crown use a porcelain WITHOUT the rim
  (`porcelain_flat`); only the strands keep it.
- The overview looks down a touch more (`pitch_o` 29.5), which trims the last sky strip at the top.

### v2 final values pass (art director: overview median 0.096)
- Lifted with mid-distance city haze and glow, not the helix: `cityglow_k` 0.12 -> 0.22, haze 0.0005 -> 0.0006.
  The overview reads 0.118 / 39.7 % under 0.10, landmark ratio 2.76 (3.2 accepted). Only H_overview was re-rendered;
  H_decision / H_hover / the sheet are from the previous final pass.


<!-- hq_rev v3 -->
## v3 (designer review of round 1, 2026-10-16; art director approved t3)

Files: `H_overview_v3.png`, `H_decision_v3.png`, `H_hover_v3.png` (+ `plates/H_*_v3_plate.png`). The v2 files are
kept. Heavy passes: `D:\rc_scratch\hq_rev\solace\v3\`; the v2 scripts are backed up in
`D:\rc_scratch\hq_rev\solace\v2_scripts_backup\`.

### What changed (designer notes, in order)
| Note | v3 rule | Numbers (`hq_preset "compound"` / `"light"`) |
|---|---|---|
| 1. Keep the double helix | Same two swept porcelain tubes, the leaf-green fresnel rim, towers apart (radius 40). The tube is a touch fatter so the big windows read. | `tube_r` 9 -> 10 |
| 2. Two windows per floor | Every floor of each strand has exactly two windows: one INWARD (facing the other strand, the walkway) and one OUTWARD. Each is a landscape oval spanning 140 deg of its tube half (70 deg of arc each way) and 8.4 BU tall. Non-node windows are lit glass (lit from the middle, dim at the rim) with 5 mullions and a transom; every window has a frame ring. | `win`: span 140, half_h 4.2, zc 5.4, frame_r 0.32, mullions 6 |
| 2. The windows are the nodes | On the 8 route floors the INWARD window IS the route node: a real opening (the tube's vertices snapped onto the oval) into a curved room with a lit ceiling, kind-coloured back-wall panels and its own state-driven light. The bow-tie bridge (route floors only: the A <-> B cross-links) enters it at the room's floor. An unread room gets a frosted oval over the opening. | `bridge_w` (9, 4) |
| 2. Oval node outline | The 2D outline is the part of the 3D window oval the camera actually sees (outline points past the tube's limb are clamped onto it; a window the other strand hides counts as hidden). Stickers / chips sit on the visible oval's box. Code: `hq_graph.visible_outline`, `hq_overlay.room_shape`; `hq_cam.visible_room` uses the same test. | - |
| 3. Crisp plinth | The plinth deck and the street ring round it (out to the first block face) are their own passes (index 1 / 3), so the post's zoom-LOD ground blur (index 4) never touches them. Thin haze only: the fog's calm zone covers the plinth (k 0.10) and the ground bank starts past it. The plinth beams are off; the plaza wash lights surfaces only (light linking, never the haze); the entry area light is off (its pool at the stair foot read as haze; the lobby glows by its own trim). | fog `calm` 70/45/0.30 -> 100/40/0.10, `bank.r` 80-170 -> 150-210, peak 0.012 -> 0.008; `entry_w` 1.4e4 -> 0 |
| 4. Lighting kept (~2x, up to ~2.8x) | The glass area is ~4x v2's portholes and half the decision landmark is window, so: the glass glow down, the rim down a touch, the city windows up, the decision exposure a touch up. | `porthole_k` 1.6 -> 0.45 (with a centre-to-rim falloff), `rim_k` 0.5 -> 0.32, city `win_k` 0.42 -> 0.52, post `exposure_zoom_k` 0.40 -> 0.32 |
| 5. A full 360 deg per helix | 27 floors x 13.33 deg = one full turn per strand (v2: 19 x 11 deg = 209 deg). Twist rate matches the full-city landmark (helix angle atan(2 pi R / pitch): city 2 pi 7.5 / 62 = 37.2 deg; here 2 pi 40 / 337.5 = 36.7 deg). Route floors every third floor (3, 6 .. 24: still 8 levels). | `floors` 19 -> 27, `twist` 11 -> 13.33, `route_floors` |

The UP link and its stair run up each strand's FRONT band (phi 0, the solid band between the two windows); the mint
light seam moved to the BACK band. The bridge link runs along the bridge's front edge (as v2).

### Cameras (re-framed for the taller strands)
| Beat | Rule |
|---|---|
| OVERVIEW | Yaw 110 (scanned: it shows 15 of the 16 nodes, every walked node and both options), pitch 27, lens 34; the strands fill ~75 % of the frame height (`fill_o` (0.95, 1.0)), the TARGET at the top. |
| DECISION | Faces the front band of the decision's floors (the azimuth follows the twist), turned `CAM_BIAS` 22 deg toward the current window so its oval opens to the camera; the frame centres `CAM_CENTRE_K` 40 % of the way toward the active room (100 % pushed the UP option off the top). |

### Values (2560 x 1440, Cycles HIP, 64 spp)
| Image | median | under 0.10 | over 0.85 | landmark | local bg | ratio |
|---|---|---|---|---|---|---|
| H_overview | 0.127 | 37 % | 0.7 % | 0.347 | 0.146 | 2.37x |
| H_decision | 0.122 | 34 % | 1.8 % | 0.260 | 0.119 | 2.18x |
| H_hover | 0.006 | 84 % | 0.8 % | 0.068 | 0.006 | 12.2x (dark hover beat) |

### Godot 4.7 mapping (changes from v2)
- Strands: the tube sweep now cuts the node openings (the oval as a trim curve on the sweep); the windows are one
  instanced oval-patch mesh (MultiMesh, ~92 glass + 16 frames per strand pair) with a per-instance tint / lit value.
- Node rooms: one curved-room scene per route floor (16), placed on the inward normal; its light is the state light.
- Node outline: the overlay projects the window's outline and clamps it at the tube's limb (the same math as
  `visible_outline`; pure, per frame, 16 nodes x 72 points).
- Plinth: its own material instance outside the ground LOD blur; plaza lights in a light-cull mask that excludes fog
  volumes.

### Open questions for the designer
1. Outward windows stay non-node (art director, 2026-10-16: game design is not ours). A possible hook for the build
   and design sessions: an outward window could hold an optional side node, e.g. a shop or event reached from the
   inward room on the same floor.
2. The read-ahead rule (2 route floors) now spans 6 building floors (80 deg of twist): fine, or read by building floor?
