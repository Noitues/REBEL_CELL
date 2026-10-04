# Round 36: one city for the City Grid, the raid and the netrun transit

**The ask:** round 35's "one kit" approach, but with the REAL city instead of the bland lot boxes.

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
1. `python layout36.py`: exports the city around the model centre, plus the Site network on the real streets.
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
