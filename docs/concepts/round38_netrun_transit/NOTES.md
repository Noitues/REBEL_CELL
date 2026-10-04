# Netrun transit v2 (on the unified city model)

This is the netrun transit view rebuilt on the round 39 unified city: the same city model, its post pass and the locked round 37 netrun UI. Nothing is committed and `scratch/` is cleared.

## Files

| File | What it shows |
|---|---|
| `transit_v2.png` | The run mid-way, with the cursor on the legend, so **all 18 nodes** show. See below. |
| `transit_step.gif` (2.3 MB, 7 frames) | See below. |

### `transit_v2.png` in detail
- **What is shown:**
  - the start (your node, a lime raid pad);
  - 7 layers: 2/3/3/3/3/2 nodes, then the Site;
  - the walked path in lime;
  - the current Terminal, carrying the token;
  - **2 numbered next options** in orange;
  - the rest of the run in white, and nodes behind you in grey;
  - the TARGET, circled red.
- **Paths:** **single dashed lines** on the ground. Buildings occlude them, and the x-ray hatch shows them through buildings.
- **HUD:**
  - the corp-paper dossier, with the AT LARGE stamp by the name and the HEAT 52 stamp;
  - the Site info window (same as the map version);
  - DECK and MENU;
  - the key strip (node types, ring states, SHOWING ALL NODES).
- **Heat:** calm Heat B, with one soft searchlight pool.

### `transit_step.gif` frames
1. **Default:** the hidden-nodes rule, so only walked, current, next and target are drawn.
2. Pick 2.
3. The token rides the dashed path. The run path turns lime behind it and stays orange ahead.
4. The new next options light up.
5. Hover the legend: every node and path fades in.

## What changed and how
1. **Single dashed paths.** `transit38._runpath1` draws one centred dash band (period 2 BU, 1.15 on). It replaces the round 39 double trace and is animated by `t` (the dashes crawl toward the target).
2. **The path meanders through the blocks, not along the raid-line streets.** `runmap38.py` routes every edge with A* on a 1/8-lot grid of the real city:
   - **Buildings:** footprints from `unified.json` are walls.
   - **Streets** cost ×6, so a path *crosses* a street instead of riding it.
   - **Kerb band:** the half-lot band beside a street costs ×3, which pushes paths into the blocks.
   - **Open ground** between buildings is cheap, plus a seeded noise field.
   - **Weave:** each edge goes through a seeded waypoint pushed 1–2 lots sideways.
   - **Separation:** once an edge is placed it raises the cost along its own path, so later edges find their own alleys.
   - **Node spots:** free ground inside the blocks (courtyards and gaps), at least 2 lots apart, held to their layer's band along the link.
3. **Zoom.** Orthographic scale **130** (round 39 was 190), framed by a grid search so all 18 nodes clear the HUD. The run spans the 16.5-lot border link m1_d to m2_d (Priority Lane Exchange, T2), so all 7 layers fit on one screen. At 118 the start and target would sit under the HUD. Going closer still means the run map pans (round 37 pan cues) and stops fitting one screen.
4. **Scope (GDD 4.2).**
   - 18 nodes: the start, 16 nodes across layers 1–6, and the Site Rack (layer 7).
   - Layer 1 is all Routers; there is a Modem in layers 3 and 5, an Elite in each of layers 3–6, and the optional Server Rack in layer 4.
   - 27 edges, and branches merge: 10 nodes have two incoming paths, and the Site takes both layer 6 nodes.
5. **Cars.** The sky-lane car layer is off in this view. At this zoom the far dots read as extra paths, and the medium box LOD reads as slabs. The ground traffic stays.

## Open questions
- The kerb-avoidance cost and the node minimum spacing are numbers. In the game they belong in `campaign_config` (`run_path_kerb_cost`, `run_node_min_spacing_lots`).
- On a much longer border link (round 39's was 30 lots), 7 layers will not fit at orthographic scale 130. Either the camera follows the current layer and the map pans, or long links get a wider layer spacing. This needs a ruling.

## Build (from `scripts/`, with `NET36=net_scope.json`)
1. `python layout36.py`
2. `python emblems20.py`
3. `python scope39.py`
4. `python runmap38.py`: writes `run38.json` and the transit camera.
5. `python run38.py`: the Blender 5.2 headless render.
6. `python transit38.py all`

All randomness is seeded.
