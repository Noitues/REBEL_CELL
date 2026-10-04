# Round 32: the netrun route, one map or separate?

The round 31 blueprint route was rejected. This round lays the same netrun out five ways, combined with the city map and separate from it, then builds the two strongest as full mockups with GIFs. All screens are 1920×1080 in the locked look:
- Cv2 + E Blender renders (the round 30 pipeline: toon ramp, facets, ink from the id/normal/depth passes, bloom, haze, rain);
- node kinds as die-cut stickers;
- links and pads as the raid's circuit inlay, with lime #D4FF00 marking what the Cell holds;
- CRT terminal panels for the Cell's live values;
- holo panels for decrypted corp intel;
- grease pencil for plans (yellow) and threats (red), true to the rules.

Nothing is committed. `scratch/` was cleared.

## Files

| File | What it shows |
|---|---|
| `options_overview.png` | **A–E side by side.** Each option has a thumbnail, ratings for readability, art reuse and GDD fit, pros and cons, and what it means for the city and raids. The recommendation is at the foot. |
| `route_c.png` | **C, TRANSIT PATH.** The link from the Cell's Relay 4 to Meridian Depot 15, unrolled into a city corridor. See below. |
| `route_c.gif` (2.6 MB) | Pick the Site on the city map (JACK IN), zoom to Meridian, then the camera swoops down onto the link and the route builds in. Then one step: pick 2, the optional Server Rack. The token rides the link, the link turns lime behind it, the other L4 branch greys out, and the pencil and the NEXT panel redraw from the Rack. |
| `route_b.png` | **B, BUILDING CLIMB.** Meridian HQ's container keep in cutaway, for the T4 boss run. See below. |
| `route_b.gif` (2.5 MB) | The same city-map pick, a swoop to the closed keep, then the Cell's scan line sweeps up and peels the front walls off (the cutaway reveal). Then one step up to the floor-4 Rack. The room turns lime, the cut rooms go dark, and the panels update. |
| `scripts/` | See Build. |

### `route_c.png` in detail
- Four lanes (rows), with a cross street in every gap.
- Nodes are pads on the lanes. Links are inlay traces that weave between lanes through the cross streets. A crossing gets its own track, so every link stays traceable.
- The Site, with its final Rack, sits at the right end of the link.
- The walked path is lime. Meridian's links are orange, and cut-off links are grey.
- Pencil: the current node is ringed, and dashed what-ifs follow the real links to choices 1 and 2. In red, PORT AUTHORITY guards the final Rack.
- CRT panels: RUNNER, NEXT (with Heat costs), HEAT, and the buttons.
- Holo panel: the Site intel.

### `route_b.png` in detail
- 7 tiers of open shipping containers. Floors are layers and containers are rooms.
- The optional Rack is the middle room of floor 4. The crane cab on top is the final Rack, THE MANIFEST.
- Walked rooms take the Cell's lime. Cut-off rooms go grey and dark.
- Links run up through the ceilings and along the floor slabs.
- An elevator-style floor indicator steps up the keep's left edge.

## Recommendation: D, the hybrid (A to pick, C for every Site, B for the HQ)

1. **Pick on the city map.** It already exists: the round 31 THE GRID HUD with JACK IN. A zoom of 1 s or less, which can be skipped, carries the camera into the route view.
2. **Every Site netrun is a TRANSIT PATH (C).** The run *is* the link between the Cell's node (or the previous Site in the tier chain) and the target.
   - This turns GDD 4.1 into something you can see: "cross-links start locked... opened links are routes for raids too".
   - The traces you walk turn lime. After a clear, the city map shows that same link lit, and raids can travel it.
   - It reads left to right like the old route. It reuses the raid pads, the inlay links and the street kit, and the Site stands at the end of the route.
3. **The corp HQ boss run (T4) is a BUILDING CLIMB (B).**
   - The finale climbs the building the player has looked at all campaign: Meridian's keep, Halcyon's tiers, Solace's helix, Orbital's silo going *down*.
   - It costs one interior kit per corp, for 4 boss runs, not one per Site.
4. **Raids stay on the city map**, with the same pads and links. A pad means the same thing in every view: a place on the network.

**A (fully combined)** fits the original vision, but it fails on readability:
- 15–20 route nodes per Site on dense iso art at map scale;
- a pad that means a fight here and a Site in raids;
- about 20 sockets needed around every Site.

**E (siege rings, my option)** keeps everything on the city map but locally around the Site. Its radial layout has no clear "forward", and the building hides the far side.

## How each option maps onto the GDD netrun (4.2)

| | Layers (7) | Branching (2–4 per layer) | Racks (L4 optional, L7 final) | Node types | Node count |
|---|---|---|---|---|---|
| **A** combined | Street "columns" toward the Site on the iso lattice | Rows = parallel streets; real sockets, so gaps are irregular | L4 is any socket; L7 is the Site itself | Stickers over raid pads | About 18 pads per Site, on top of the raid nodes |
| **B** climb | Floors (bottom = L1, top = L7) | Containers per floor: 4/4/3/3/3/2/1 drawn. Wider floors don't fit 16:9 | L4 is the middle room; L7 is the crane cab / top room | Sticker plus room light and props (racks, desks, shelves, drones) | 20 rooms |
| **C** transit | Columns along the link (L1–L6), with L7 the Site at its end | Rows = 4 lanes; links jog through the cross street in each gap. 2–4 rows used per layer | L4 is any lane pad; L7 is the Site's gate | Stickers over pads | 18 pads plus the Site |
| **D** hybrid | C for Sites, B for HQs | as C / B | as C / B | as C / B | as C / B |
| **E** rings | Rings closing in on the Site | Nodes along each ring | L7 is the Site | Stickers over pads | About 19 pads |

Both mockups follow the GDD guarantees:
- L1 is all Routers;
- there is a Modem in L3–5;
- there is about one Elite a layer in L3–6;
- Terminals are about 25% of the rest;
- one route is walked: Router, Terminal, Elite (current), then the choice of a Router or the optional L4 Rack.

## What it means for the city and raid node systems

- **One node language.** The circuit-inlay pad and the lime/corp-colour inlay link (locked for raids, round 21) are reused as the netrun's nodes and links.
  - The meaning is the same: a pad is a place on a network. Corp colour means the corp's; lime means the Cell's.
  - Raid nodes keep their own icons and health fills. Route nodes carry kind stickers.
- **City map after a run (C).**
  - The link between the start node and the Site is drawn lit (lime once the Site is claimed, neutral grey if left unclaimed).
  - That link is the cross-link the GDD opens. Raids route along it.
  - No new city data is needed: the link already exists in the Grid.
- **Mid-run raids** (GDD 4.4 interlude) zoom out of the route view to the city map, run the raid, and zoom back in. C is already "on" a city link, so the transition is short.
- **Claiming** is unchanged. B adds nothing to the city, because the HQ cutaway is its own view.

## Godot build notes

- **Route data is unchanged.** `NetrunMap` (layers → nodes → edges) stays the single source. Each view is a pure presenter with Signal Up, Call Down:
  - the view emits `node_chosen(node_id)`;
  - the state moves the token.
- **C corridor.**
  - The corridor is a 3D scene, or a pre-rendered backdrop per corp district plus a Node2D overlay. It is generated deterministically from the link id: lanes = rows, a cross street per gap, and block dressing from a seeded RngService stream.
  - Node screen positions come from the layer index × row. In 3D, a `Camera3D.unproject_position` feeds the 2D overlay, the same way `anchors.json` is exported here.
  - Traces are `Line2D` (3 lanes, round joints) with the inlay shader from raids: a glow pass plus a core line. Each edge gets a polyline routed by the row/cross-street rule, with a per-gap track offset when vertical spans overlap (the rule is in `r32_scene.c_edge_paths`).
  - States are shader params: walked = lime, current options = corp colour bright, reachable = corp colour 60 %, cut = grey 40 %.
- **B keep.**
  - The keep is a modular room scene (container shell, interior prop set by node kind, an emissive ceiling light) stacked on a floor grid. The front wall is a separate mesh for the reveal.
  - Room state is a light colour and energy on the room's OmniLight or emissive, plus a darken/desaturate on the cut rooms (a CanvasItem overlay, or a material param).
  - Links run along the slab seams. Horizontal runs sharing a seam get track offsets of ±6 px.
- **Zoom transition.**
  - The city map camera tweens its zoom toward the Site's map position (0.5 s). It crossfades through a scanline wipe into the route view, whose camera starts high and settles (0.5 s). Skip snaps to the end.
  - For B, a cyan scan line sweeps up and dissolves the front-wall mesh (a clip plane or alpha on a `y` uniform).
- **Step animation.** The token follows the edge polyline (`Path2D` / `PathFollow2D`, about 0.5 s). The trace's lime `progress` uniform follows it. Then the reachable set is recomputed, and nodes that became unreachable tween to grey (0.2 s). The pencil marks redraw.
- **Pencil.** As locked: `Line2D` with a round cap and an under-shadow. The dashed what-if is sampled along the real edge polyline (offset 12–13 px), so it is always true to the rules.

## Designer questions (for DECISIONS.md)

1. **Does a netrun start from a node?** C needs a start node: the claimed node or cleared Site adjacent to the target. The tier chain already implies one. When several are adjacent, use the one with the lowest id (a deterministic tie-break).
2. **Does the walked link persist on the city map?** C shows it lit after the run. The GDD opens cross-links via Intel Exploits and objectives; C would make a cleared Site's approach link visible as well. This is a presentation question only, unless raids should also use it.
3. **The HQ climb (B) as the T4 finale.** Each corp would need a cutaway of its HQ. Orbital's silo would be a descent. This is an art cost of 4 boss interiors.
4. **E's rings as defence sockets.** This would need a GDD rule, and E is not recommended.

## Build (from `scripts/`, Blender 5.2 headless)

1. `blender -b --factory-startup --python r32_scene.py -- street ../scratch/bl still`, then the same call with `tower ../scratch/bl still`. These write the passes and `*_anchors.json`.
2. `... -- street ../scratch/bl anim`, `... -- tower ../scratch/bl anim walls`, `... -- tower ../scratch/bl anim`. These write the GIF camera frames; the walls variant keeps the city identical.
3. `python finish_all.py`: the ink, grime, bloom, haze and rain finish (round 30 backdrop pipeline).
4. `python route_c.py all`, `python route_b.py all`, `python overview.py`.

Shared code:
- `target_corps.py` is copied from round 30. Its setup, materials, `container()`, `depot()`, light and pass code are exec'd by `r32_scene.py`.
- `r31lib.py` and `sticker_lib19.py` are copied from round 31.
- `r32ui.py` holds the inlay traces and pads, the node stickers (the MODEM is MAINFRAME blue), holo, the Meridian seal, the terminal buttons, the dashed pencil and the GIF writer.
- `peek.py` and `gifsheet.py` are check helpers.

All randomness is seeded.
