# Round 38: one city, lighter buildings, the real-scope test, flying-car models

## Files
| File | What |
|---|---|
| `city_grid.png`, `raid_management.png`, `run_transit.png`, `three_views.png`, `zoom_through.gif` | The round 37 set with the lighter buildings. |
| `scope_city_grid.png`, `scope_raid.png`, `scope_transit.png` | The **real-scope test** (below). |
| `cars_models.png` | Sky-lane flying cars as low-poly models at the close, transit and grid zooms, against the round 37 streaks. |
| `contact_sheet.jpg`, `scripts/` | |

## 1. Lighter buildings (raid / transit)
- **Opacity:** 0.32 → **0.42**.
- **Colour over the ground pass:** ×0.40 → **×0.62**.
- The network is unchanged and still the brightest layer. Windows, roof neon and facade facets now read.
- **The see-through is now keyed to the view band, not to the raw zoom.** It ramps over lod 1.45–1.75, so a raid fitted wider (see 2) still gets the raid look. The same band drives the lane dimming and the node-detail switch.

## 2. Scope test: is one model still right at real scale?
**The data (read-only):** `content/corporations/meridian.tres` is a shipped campaign.
- **Sites:** 32 (13 T1, 9 T2, 9 T3, 1 T4 boss) plus the home server, with every link and locked link. This matches GDD 4.1 (30–40 Sites per corp, one corp per campaign).
- **Placement:** its `map_position` columns (tier) run along the Cell → Meridian HQ axis and fan out across it. Each Site snaps to the nearest free street junction, at least 4.5 lots apart.
- **Links:** routed on the real streets: 52 links, 31 of them locked or not yet open.

**Mid-campaign network** (after about 11 runs):
- 9 owned nodes plus CORE (7 T1, 2 T2, with node types);
- 2 grey;
- **10 available**, i.e. every Site linked from an owned one;
- 10 white.

**The raid camera is FITTED to the network:**
- It covers the owned nodes plus CORE, with a 1.18 margin for the panels, in 16:9, clamped to ortho 150–420.
- Here that gives **ortho 311**, 1.8× the hand-framed round 37 raid (176).
- The Meridian convoy enters through the available Site nearest the HQ.

**The transit** is the longest border link (CORE → Fleet Telematics Hub).
- It carries the GDD 4.2 run map: 7 layers of 2–4 nodes, Server Racks at layers 4 and 7, and branching links.
- The camera is fitted to the link: **ortho 190**, not 88.

**Findings:**
- **City grid:** holds.
  - 32 Sites plus the network fill the Cell → Meridian wedge cleanly.
  - Pins and tier badges stay legible.
  - Available (orange) vs owned (lime) is the strongest read.
  - Two labels collide (a T2 pin on the HALCYON tag); the game needs label avoidance.
- **Raid:** holds, with two changes this round.
  1. **See-through by view band** (done here). At the fitted ortho 311 the buildings went near-solid under the old zoom rule.
  2. **Minimum socket size:** 22 px at management zooms (done here). At ortho 311 the old 13 px sockets were dots.

  At this scale the threat lane and the 10 owned sockets read. The defence tray and terminals cover about 20 % of the frame, so the fit keeps that margin.
  - **Recommendation:**
    - fit-to-network clamped to 150–320;
    - above 320 (late game), split the raid into the threatened sector plus a minimap;
    - keep sockets at least 22 px on screen.
- **Transit:** this is the weakest at real scale.
  - Real links between Sites are long (8–14 lots), and a 7-layer run map needs about 190 ortho. That is closer to the raid zoom than to round 37's intimate 88.
  - The run's nodes and links overlap the Site link's own bus and the city.
  - **Recommendation:** keep the one city, but in transit:
    - hide the Site-graph links except the walked one;
    - fit the camera to the run map, not to the Site link;
    - optionally lay the 7 layers along the link's street with 2-lot lateral spacing (as in round 36).
- **Performance / LOD** (the one model at real scale):
  - The model is ~14 100 extruded buildings, ~530 k faces of city detail, 5 HQs, ~950 sky cars and about 50 network decals.
  - **Godot plan:**
    - buildings in about 6 MultiMeshes, one per facade family;
    - LOD0 (facade grid, props) only within the raid frustum: about 1 500 buildings at ortho 311;
    - LOD1 (mass + emissive window texture) elsewhere;
    - the network is a single ground decal shader with node and link buffers (52 links, 33 nodes is trivial);
    - props culled by screen size.
  - That is about 1 500 detailed plus 12 600 LOD1 instances, well inside a mid-range GPU budget.
  - The see-through raid is one extra alpha pass over the buildings, which are already depth-sorted by the iso camera.
  - **Verdict: the one-model approach holds**, with fit-to-network raid framing, view-band LODs and the transit fixes above.

## 3. Flying cars as models
- **The model:** a wedge body, a dark glass cabin, lane-colour flank stripes plus an under-glow, white headlights and red tail lights. It is 3.4 u long, has about 40 faces, and sits on the same lanes, heights, colours and speeds as the streaks.
- **Close up and at the transit zoom**, they read as cars.
  - They must be excluded from the see-through building material: under the raid/transit treatment they get darkened like buildings, so the sheet shows them unfaded.
- **At the grid zoom** a model is about 2 px. It becomes a coloured head/tail dot and loses the motion read that the round 37 streaks give.
- **Recommendation:** models from the raid zoom in (LOD0, one MultiMesh per lane colour, about 950 instances) and streak billboards at the grid zoom (LOD1), swapped by ortho like the buildings.

## Build (round 38)
1. `python layout36.py`, then `python scope38.py` (reads `meridian.tres` and writes `net_scope.json`).
2. Renders:
   - `python run38.py stills`
   - `NET36=net_scope.json python run38.py scope`
   - `CARS38=models python run38.py cars`
   - `python run38.py zoom`
3. Sheets:
   - `python screens38.py city raid transit`, then `python screens38.py three gif contact`
   - `NET36=net_scope.json python screens38.py` (the scope sheets)
   - `python screens38.py cars`
4. `skylanes.py` is the shared sky-lane data (Blender models and post streaks).

---

# Rounds 36-37 (still valid)

**The ask (round 36):** round 35's "one kit" approach, but with the REAL city instead of the bland lot boxes.

**What it is:** all three views and the zoom are cameras on **one Blender model** built from the game's own city layout (`round6_city_restyle/city_layout.json`, read-only, the same source the round 25–34 city map and HQ close-ups use). It contains:
- every street tile with its lane colours;
- the 14 119 building extrusions (footprint, base, height, taper, ink colour);
- the plazas;
- the five locked HQs: Meridian (container fortress, crane, rail yard), Solace (helix), Halcyon (civic core with the eye), Orbital (silo), and the Cell's base;
- the round 34 Cell district: the grid restored, plus red windows in the crest.

The camera is one orthographic iso camera (yaw 135°, pitch 40°). Only its target and `ortho_scale` change.

## Files
| File | What |
|---|---|
| `city_grid.png` | The campaign City Grid (ortho 820). See "City grid" below. |
| `raid_management.png` | The Cell's district (ortho 176). See "Raid view" below. |
| `run_transit.png` | The netrun transit along one border link (RELAY 4 > DEPOT 15) at ortho 88. See "Netrun transit" below. |
| `three_views.png` | The three side by side, plus the same block enlarged from each render. Callouts **A** (node RELAY 4), **B** (the link) and **C** (its uplink-pad building) sit on the same world points in all six tiles, projected from world coordinates. |
| `zoom_through.gif` | One continuous camera, grid → raid → transit, 23 frames, 3.9 MB. Ortho is log-interpolated and the target moves with the zoom. Pins and tags retract between ortho 450 and 300, and the run's nodes appear below ortho 130. |
| `contact_sheet.jpg`, `scripts/` | |

### City grid (`city_grid.png`)
- The real skyline and the HQs, with their district tags (round 30 v6 style).
- Every node raises a **pin** above the roofs with its tier badge (gold key plates on the T3 key Sites).
- Owned Sites are lime, available orange, not-yet white, already-run grey, and the Cell CORE pink.
- Links are drawn as one bright trace. Where a building hides a link, it shows through as a solid x-ray.
- **Heat B:** searchlight cones and pools on the Cell's border, plus the Heat strip.
- DEPOT 15 is selected and its info window open, with a JACK IN button and a legend.

### Raid view (`raid_management.png`)
- The same buildings close up.
- The node sockets are the circuit inlay on the street: frame, pins, integrity track and glyph. The CORE is EXPOSED under a spotlight.
- **Lime links:** the 3-trace bus with vias and packets.
- **Uplink pads:** on the node buildings, each with three lime risers up the corner and a beacon mast.
- The red Halcyon threat lane, with the convoy as v4 icons.
- The YOUR NODES terminal, the RAID INCOMING terminal, the defence card tray and START DEFENSE.

### Netrun transit (`run_transit.png`)
- The run's nodes ride the link's own streets, with branches one lot off.
- States: walked lime, current with the operative token, two available orange, the rest white.
- The dossier, the info window, the red pencil circle on DEPOT 15, and the DECK and MENU buttons.

## The shared kit rules
1. **One layout, one model.** The lot/road grid, every building and every lane colour come from the game's layout table, and the Sites sit on its street junctions.
   - Links follow its real streets (BFS over the street cells, simplified to corners), not straight lines. The link the netrun unrolls is the link the raid defends and the map shows.
   - The Cell's district uses the round 34 patch (`grid27`): the normal grid is restored and the crest is drawn in red windows only.
2. **One camera.** Orthographic, yaw 135°, pitch 40°. The only parameters are the target and the zoom (`ortho` in world units, 1 lot = 6 u):
   - **City Grid:** about 820. The whole campaign map: four HQs and the Cell.
   - **Raid:** about 176. One district, about 30 lots across.
   - **Netrun transit:** about 88. One link and its neighbouring blocks.
3. **Building LOD per zoom.** It is the same building at every zoom; detail is authored once and simply resolves or disappears:
   - **Always:** the extrusion mass, taper, roof neon trim (in the building's own ink), window grid, territory tint, red crest windows, and the HQ heroes.
   - **From the raid zoom** (it disappears at the city zoom):
     - the triangulated facade grid of about 1.7 m cells on the faces the camera sees;
     - ledges every 6 m, blade signs, drain pipes;
     - AC units, water tanks, antennas with red aircraft lights, roof holo billboards;
     - cars with head and tail lights on the lanes, sky-lane fliers;
     - the uplink pads and risers.
   - **Transit only** (it reads only up close): shopfront glow bands at street level, awnings and the pipes' detail. There is no extra geometry; the detail is already in the model.
   - **Godot LODs:**
     - **LOD0** (raid and transit): the full mesh.
     - **LOD1** (city): the mass plus the window emissive texture, with ledges, signs and props culled by screen size.
     - **LOD2** (far city): the extrusion only.
4. **Node and link rendering per zoom** (`post36.Net36`: one ground decal whose anatomy is a function of `lod` = log-zoom between the three ortho values):
   - **Link:**
     - **City:** a single bright trace about 3 px wide, plus a soft halo.
     - **Raid and transit:** the 3-trace bus 1 u apart, with vias every 4 u and moving packets.
     - Border and not-yet links are dashed.
   - **Node, city zoom:**
     - a socket with a filled glow disc and a tier ring;
     - a billboard pin rising above the roofs with the tier badge or key plate;
     - the CORE carries the Cell icon.
   - **Node, raid zoom:**
     - the full socket: frame, pins, pin-1 notch, integrity track and glyph;
     - owned sockets shift from map lime to the raid's "holds" green.
   - **Node, transit zoom:** the same socket, plus the run's own smaller nodes (glyph sockets with stickers) along the link.
   - **Occlusion:**
     - Network decals are evaluated on a ground-only position pass, so a node or link behind a tower is never lost.
     - At the city zoom it shows through solid.
     - At raid and transit zoom it shows through as a hatched ghost.
     - In Godot this is a second depth-test-greater pass with a hatch shader.
   - **Lane dimming:** at the management zooms the street's own lane glow drops by up to 60 %, so the network leads. The city zoom keeps the full real-city look.
5. **Heat** is the same world effect at every zoom (round 35 option B): searchlight pools and cones on the Cell's border. At the city zoom the Heat strip carries the number.
6. **UI by zoom:**
   - City: tags, pins, the Heat strip, info window and legend.
   - Raid: the terminals and the card tray.
   - Transit: the dossier, info window and node stickers.
   - Tags and pins fade out between ortho about 450 and 300, so the gif's middle is clean world.

## Godot build notes
- **`CityModel` resource:**
  - It is baked from the layout table, seeded per campaign.
  - It holds a MultiMesh per building family, the street mesh with a lane-colour vertex attribute, prop MultiMeshes (AC, tanks, antennas, signs, billboards) and the HQ scenes.
  - Visibility ranges: props and facade-detail meshes fade by camera `size` (ortho), not by distance.
- **One `Camera3D`** (orthographic):
  - `size` is tweened log-linearly between the three values.
  - The target follows the zoom so the destination stays framed.
  - There is no scene change between grid, raid and netrun; the UI layers swap on `lod` thresholds with hysteresis.
- **Network = one ground decal shader** (the street-plane material):
  - **Uniforms:**
    - a node buffer: position, state enum, kind or glyph atlas index, tier, integrity, exposed flag;
    - a link polyline buffer: points, state, packet phase;
    - `lod`.
  - **Anatomy:** a branch on `lod` (single trace vs bus, glow disc vs socket detail). It is the `post36.Net36` prototype.
  - **X-ray pass:** a second pass of the same shader with depth test GREATER and a hatch, or a solid fill at city `lod`.
- **Pins:** Sprite3D billboards with `fixed_size`, from the socket to +34 u. Alpha follows `lod`.
- **Node buildings:** the uplink pad is a small mesh placed on the nearest building to an owned socket. The risers are an emissive strip mesh up its nearest corner.
- **Sky lanes and cars:** they are locked from round 26. Their particle and path systems are shared by every view.

## Build (from `scripts/`)
1. `python layout36.py` (round 37: `run37.py`, `unified37.py`, `post37.py`, `screens37.py` replace the 36 versions): exports the city around the model centre, plus the Site network on the real streets.
2. `python run36.py stills`: Blender 5.2 headless; the three views at 2880×1620, plus ground-only position passes.
3. `python run36.py zoom`: the 30 zoom frames at 960×540.
4. `python screens36.py city raid transit`, then `python screens36.py three gif contact`.

**Scripts:**
- Base: `unified36.py`, built on the round 30 HQ pipeline (`target_corps.py` and `heroes24–30`, copied unedited).
- Data: `citydata.py` and `grid27.py` from round 34.
- UI: `r31lib`, `r32ui`, `r35ui` and `route_d_city` from round 35; `ui19` and `icons22` from rounds 19–22.

Seeded throughout.

## Open
- **The network on the map is invented.** Sites are picked on real junctions by rule; the game's own Site table should replace this.
- **The city zoom is dense.** Pins keep it readable, but labels can collide (SOLACE vs its T2 pin). The game needs label avoidance.
- **The raid's threat lane** runs mostly behind towers near the Halcyon edge. Its x-ray ghost is faint.
- **The transit view** doesn't show the walked part of the link in lime yet.
- **The gif** stays under 4 MB by halving the frame rate in the dense city part and dropping the rain. The stills carry the full grade.
