# Round 39: the one city at real scope, with each view's locked UI

Locked from round 38:
- the building opacity (it reads well at every zoom);
- the grid read.

Every view is the shipped Meridian campaign (`content/corporations/meridian.tres`: 32 Sites, mid-campaign network) on the one city model, with that view's latest locked UI drawn in.

## Files
| File | What |
|---|---|
| `city_grid.png` | **Zoomed in** to ortho 440 (round 38 was 820). See "City grid" below. |
| `raid_view.png` | The raid setup **fitted to the network** (owned nodes, the three entry Sites and room for the tray), at ortho 380. See "Raid view" below. |
| `run_transit.png` | The netrun along the longest border link (CORE → Fleet Telematics Hub), at ortho 190. See "Netrun transit" below. |
| `cars_lod.png` | The three car LODs. |
| `three_views.png` | The three views side by side. **A** marks the CORE and **B** the run's border link, projected from world coordinates. The car LOD strip sits below. |
| `scripts/` | |

### City grid (`city_grid.png`)
- **Panning:**
  - edge chevrons on all four sides;
  - the round 37 MINIMAP terminal (the real city render, the lime view box, your nodes, the red target);
  - "DRAG / WASD".
  - The TARGET is off-screen here, so it gets a red pencil **edge marker** pointing at Meridian HQ, with its chip. Pan up to reach it.
- **Meandering links:** each Site link is routed through 1–2 street junctions pushed 3–6 lots off the straight line (seeded per link), then BFS'd on the real streets with loops removed. That gives several turns instead of one L.
- **Round 37 netrun map UI (locked):**
  - option A rings (normal-colour Site icons; the state is the ring);
  - **hidden nodes** take their links with them;
  - the corp-paper dossier (the Heat number is on its stamp: calm Heat B);
  - PATROL on a cleared Site;
  - the info window and JACK IN;
  - the legend strip ("HOVER HERE: SHOW ALL NODES");
  - Options > Map "Always show all nodes".

### Raid view (`raid_view.png`)
The locked raid UI from rounds 19–23:
- **Red grease-pencil routes** A/B/C: solid, along the real streets, with circles and letters at the entry Sites.
- **Panels by fiction (E):**
  - YOUR NETWORK, a CRT terminal with status chips;
  - the WORK ORDER, an intercepted memo under glass, re-skinned to Meridian ("Manifest Audit", seal, footer);
  - THREAT INTEL, a holo carrying the Meridian mark, DECRYPTED, with scanned Meridian vehicle silhouettes.
- **Node health v2** (fill drains north → south): one node DISABLED (amber).
- **CORE** is EXPOSED under a calm spotlight.
- **Vehicle icons v4** with health discs and status pips, at each entry.
- The **R3 class beacon** (Breaker) on the Safehouse's uplink pad.
- The **sticker defence tray**, with ICE LOCK **parked** and the yellow pencil targeting arrow resolving into the yellow circle on the Vault. Its forecast ring and the IF PLACED terminal are shown too.
- START DEFENSE, with the speed/skip strip below it.
- See-through buildings at 42 %.

### Netrun transit (`run_transit.png`)
- **The run's map on the streets.** GDD 4.2: 7 layers of 1–4 nodes, Server Racks at layers 4 and 7. Every edge is a street path through side streets (same meander rule).
- **Thin double dashed paths:** lime walked, orange next.
- **Round 37 netrun details (locked):**
  - only walked / current / next / TARGET show (hidden nodes are not drawn);
  - node-type stickers in normal colours (sword = COMBAT) with option A rings;
  - the operative token;
  - the corp-paper dossier ("HEAT 52: HUNTED" stamp);
  - calm heat (one soft sweep);
  - the red TARGET circle on the final Server Rack;
  - the info window, DECK / MENU, and a key strip (COMBAT, ELITE, EVENT, SHOP, SERVER RACK).
- The Cell's own network stays dim underneath.

### Cars (`cars_lod.png`)
The three LODs, swapped by camera ortho with hysteresis:
| LOD | Zoom | What is drawn |
|---|---|---|
| FAR | ortho > 400 | a head dot + its lane-colour line |
| MEDIUM | ortho 150–400 | a small grey box (6 faces) + the line |
| CLOSE | ortho < 150 | the round 38 low-poly model + a thick speed line |

Cars are not part of the see-through building material.

## Notes
- **Raid zoom = the network's size.** It is a camera fit to the owned nodes, the raid's entry Sites and a margin for the panels and tray, clamped to ortho 220–380. Here it hits 380. A bigger network would need the sector split proposed in round 38.
- **Panels are re-skinned per corp.** In code, `ui20.MEMO_SEAL` / `MEMO_FOOT` and `ui21.CORP_SYMBOL` / `INTEL_CORP` are module settings, so the work order and intel follow the raiding corp. In Godot it is one corp theme resource.
- **Godot:**
  - **Run paths:** a decal pass with a dashed double-line shader (`dash_phase`, `gap`, `width_px`), one polyline buffer per visible run edge.
  - **Hidden nodes:** view-only state, as in round 37.
  - **Car LOD:** three MultiMeshes per lane colour (quad, box, model). Visibility ranges are set from the camera ortho.

## Open
- **City grid labels:** the HALCYON tag overlaps a T2 ring. The game needs label avoidance.
- **Raid at ortho 380 is crowded:** the route C arrow ends under the tray, near CORE. A wider network needs the sector split.
- **Transit turns:** the run paths have fewer side-street turns than they could. A stronger meander (more waypoints per edge) is a one-line change in `scope39.meander`.

## Build (from `scripts/`)
1. `python layout36.py`
2. `python emblems20.py`
3. `python scope39.py`
4. `python runmap39.py`
5. Blender 5.2 headless:
   - `NET36=net_scope.json python run39.py r39`
   - `CARS38=models python run39.py cars`
   - `blender -b --factory-startup --python vehicles20.py -- <abs>/scratch/bl`
6. `NET36=net_scope.json python screens39.py city raid transit cars three`
