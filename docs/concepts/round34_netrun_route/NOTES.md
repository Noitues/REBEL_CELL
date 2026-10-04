# Round 34: netrun route, hybrid D (locked)

The designer locked **D**:
- Site runs are a **transit path** along a city link.
- The corp HQ boss run is a **building climb**.
- Raids stay on the **city map**.

This round applies the new rules:
1. A run starts from a **rebel-owned node**: one of the Cell's lime raid nodes.
2. The route expands outward and onward toward the target HQ.
3. Every step offers a **finite** set of options.
4. Every view shows three node states: **reachable**, **greyed but plannable**, and **walked** (lime).

The look is the same as round 32: Cv2 + E Blender renders, sticker node kinds, raid circuit-inlay pads and links, CRT terminal panels, holo intel, and grease pencil. Nothing is committed; `scratch/` is cleared.

## Files

| File | What it shows |
|---|---|
| `route_d_city.png` | **City-view planning** on the locked city map (round 30 v6). See below. |
| `route_d_transit.png` | **The Site run (transit path)**: the link RELAY 4 > DEPOT 15 unrolled into the city corridor. See below. |
| `route_d_transit.gif` (2.2 MB) | The city view (with HUD), then a zoom into the link RELAY 4 > DEPOT 15, then the camera swoop into the corridor. The route builds in, then one step: pick 1, the Elite Router. The token rides the link, which turns lime behind it. The next options (Router, optional Server Rack) light up out of the grey set, and the pencil plan carries on from the new node. |
| `route_d_climb.png` | **The HQ boss climb, entry.** See below. |

### `route_d_city.png` in detail
- **The Cell's network** is lime: Home Server, Firewall Relay, Proxy 2 and **Relay 4**, the start (pencil-ringed).
- **Reachable now** is a finite set of **3** Sites, numbered on terminal chips: T1 DEPOT 15, T1 YARD 9, and the Heat objective SCRUB RECORDS. They show as bright Meridian-orange pads on open links.
- **Plannable but not reachable yet** shows as grey pads and links with dim chips: T2 CUSTOMS 22, T2 PORT 31, T3 LANE 15, T3 TARIFF 40, and the HQ. A locked cross-link is grey dashes marked LOCKED.
- **The pencil plan** is solid on the next run (Relay 4 > Depot 15), then dashed RUN 1–3 through the grey Sites to **Meridian HQ**. In red: THE MANIFEST.
- **Panels:**
  - PLAN: the runs with a Heat forecast, ending at about 70 before the boss (GDD 4.1);
  - MAP KEY and RUNNER;
  - holo intel for the selected Site;
  - IF CLEARED;
  - the JACK IN sticker.

### `route_d_transit.png` in detail
- The start is the lime **RELAY 4 // YOUR NODE** pad.
- **Walked** is lime (start > Router > Terminal).
- **Only the next step is lit**: **2** choices, numbered (Elite Router, Router).
- Everything still reachable later is **greyed and plannable**: grey pads, greyscale stickers, grey links.
- Nodes the run can no longer reach are **ghosted**: faint pads, no stickers.
- The pencil plan is solid to the next pick, then dashed through the grey nodes to the Site's Rack, which PORT AUTHORITY guards (red).
- The NEXT panel lists exactly the lit choices. The holo shows the onward plan: CUSTOMS 22 > LANE 15 > MERIDIAN HQ.

### `route_d_climb.png` in detail
- The Cell's link from Lane 15 arrives at the keep's street door, the lime **BREACH POINT** (pencil-ringed, with the token).
- Floor 1 offers a **finite 3 doors**: lit rooms with orange outlines, numbered. The fourth container is sealed and is not a node.
- Floors 2–7 are **greyed and plannable**.
- The pencil plan climbs through them, banking at the floor-4 Rack, up to the crane cab. In red: THE MANIFEST.
- An elevator-style floor ruler runs up the left edge. The holo shows HQ intel, the HEAT panel shows 71, and NEXT lists 3 doors.

## Node states (one rule set for all three views)

| State | Meaning | Look |
|---|---|---|
| Walked / the Cell's | Owned by the Cell, or walked this run | Lime pad and lime 3-lane trace (the raid language) |
| Current | Where the operative is | Lime, with the pencil ring and the class token sticker |
| Reachable now | The finite next step only (city: open links from the start node; transit/climb: the current node's out-edges, 2–3) | Corp-colour pad, bright trace, full sticker, numbered terminal chip; listed in NEXT |
| Greyed, plannable | Not reachable now but reachable later on this path | Grey pad (lit 70 %), greyscale sticker at 82–85 %, grey trace; the pencil may plan through it |
| Behind / cut | Unreachable for the rest of this run | Ghost pad (25 %), no sticker |
| Locked (city) | A cross-link that is not open yet | Grey dashes plus a LOCKED chip |

## GDD fit

- **4.1 City Grid.**
  - The city view is the campaign layer: Sites, tier chains (T1 > T2 > T3 > boss), Heat objective Sites, and cross-links that start locked.
  - Shown reachable are the Sites adjacent to the Cell's territory over open links.
  - The plan follows the minimum winning path the GDD describes (tiers T1 > T2 > T3 > the boss), with Heat heading toward about 70 before the boss.
- **4.2 Netrun map.**
  - Transit: 7 layers with 2–3 nodes each in this mockup (the GDD allows 2–4). Layer 1 is all Routers, Layer 3 has the Modem, the L4 Rack is optional, and the L7 Rack is the Site.
  - Climb: 3/4/3/3/3/2/1 rooms, with floor 1's fourth container sealed. The L4 Rack and the L7 crane cab are both there.
  - The out-degree is 1–3 everywhere, so a step never shows more than 3 options.
- **3.1 / 3.2 network.** The start node is a real network node (a Relay). The walked link is drawn lime, as the Cell's.
- **7 Raids.** Unchanged. They use the same pads and links on the city map.

## Open questions for the designer (DECISIONS.md)

1. **Which owned nodes may start a run?**
   - Proposal: any Cell node adjacent (over an open link) to the target Site.
   - When several qualify, the player picks one. The default is the lowest node id (deterministic).
   - Should a Disabled node be allowed as a start? Proposal: no.
2. **What can be planned?** Proposal:
   - any Site in the same corp's Grid that is visible, including through locked cross-links, drawn as dashed what-ifs;
   - the plan is only pencil, so it never changes the rules.
   - Should the plan persist in the save? Proposal: yes, as a list of Site ids.
3. **How finite is "finite"?** The GDD allows 4 nodes a layer. This round caps the *visible* choices at 3 by keeping out-degree ≤ 3. Proposal: put `max_out_degree = 3` in campaign config, and keep layer width 2–4.
4. **The sealed container on the climb's floor 1** is decoration that keeps the pyramid shape. Floor 1 has 3 nodes, within the GDD's 2–4.
5. **Do the city's reachable Sites include Heat objective Sites** (SCRUB RECORDS) in the same finite set? They are shown that way here, and they count toward the 3.
6. **Climb entry.** Does the boss run start from the last T3 Site's link (Lane 15)? That is shown here. Or from any Cell node adjacent to the HQ?

## Godot build notes (deltas from round 32)

- **One state function.** `RouteView.state_of(node) -> {WALKED, CURRENT, REACHABLE, PLANNABLE, BEHIND}` is computed from the pure route graph:
  - REACHABLE = out-edges of the current node;
  - PLANNABLE = descendants of the current node minus REACHABLE;
  - BEHIND = everything else not walked.
  - The city view uses the same function on the Grid graph, with "current" = the chosen Cell start node.
  - The views only read it.
- **Pencil plans** are a list of node ids held in UI state, not game state. Each segment draws along the real edge polyline: solid for the first segment, dashed after it. Planning through PLANNABLE nodes is allowed. A BEHIND or LOCKED node shows as a dashed what-if (city) or can't be selected.
- **Numbered chips** come from the sorted REACHABLE list (by screen y, then node id), and the keys 1–3 map to them.
- **Zoom city > transit:**
  - the city camera zooms on the chosen link's midpoint (0.5 s);
  - then a cut to the corridor camera, which settles (0.5 s);
  - skippable.
  - The transit corridor is generated from the link id (seeded).

## Build (from `scripts/`)

1. `blender -b --factory-startup --python r32_scene.py -- street ../scratch/bl still`
2. `blender -b --factory-startup --python r32_scene.py -- tower ../scratch/bl still`
3. `blender -b --factory-startup --python r32_scene.py -- street ../scratch/bl anim`
4. `python finish_all.py`
5. `python route_d_city.py`, `python route_d_transit.py all`, `python route_d_climb.py`
6. `python clear_scratch.py`

What's in `scripts/`:
- **Copied from round 32 with round-34 edits:**
  - `r32_scene.py`: transit layers capped at 3 nodes; floor 1's first container sealed.
  - `r32ui.py` and `route_b.py`: the climb imports `route_b`'s loader.
- **Unchanged from round 32:** `finish*.py`, `r31lib.py`, `sticker_lib19.py`, `target_corps.py`.
- **Check helpers:** `city_probe.py` (the city lattice), `peek.py`, `gifsheet.py`.
