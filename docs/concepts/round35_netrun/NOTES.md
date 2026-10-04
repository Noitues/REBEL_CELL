# Round 35: netrun views after the in-depth review

Hybrid D stays: Site runs are a transit path, HQ runs get their own view, and raids happen on the city map.

The designer's rules for this round:
- **No planning.** All pencil plans and plan UI are gone. The player picks a path through the city, and every new node takes a run.
- **No cap on choices.** A run can go from **any** owned node to **any** unowned node across a border link, so the number of choices comes from the graph alone.
- **Node states:**
  - **lime:** owned or walked;
  - **orange:** available now;
  - **WHITE:** not yet available;
  - **GREY:** past or used up. Grey nodes stay on the map; they are never removed.

All work is in `docs/concepts/round35_netrun/`. Nothing is committed and `scratch/` is cleared.

## Files

| File | Point | What it shows |
|---|---|---|
| `city_view.png` | 1–5 | The city view (details below). |
| `transition_1_zoom.gif` | 6 | **One camera.** The iso city zooms straight onto the link. At city scale the link is one orange trace, and it splits into the run's branches as the camera arrives. There is no cut, because it is the same city kit (see `building_language.png`). |
| `transition_2_unfold.gif` | 6 | **The link unfolds.** Everything but the chosen link dims. The link widens into a strip, and that strip is the transit view (a wipe along the link). |
| `transition_3_bits.gif` | 6 | **Jack in.** The map dissolves into bits (the locked dissolve A), except the link. The transit view then builds up from bits, starting at the start node. |
| `building_language.png` | 7 | **One city kit.** The same iso camera (35°, orthographic), the same lot grid and one building per lot, at three zooms: city (1300), raid (640) and netrun transit (355). The bottom row shows the same block enlarged. |
| `transit_view.png` | 7–11 | The Site run in the new kit, with **Heat option A** (details below). |
| `transit_view_heat_b.png` | 11 | **Heat option B:** the city reacts (searchlight cones and police strobes, the locked H1 language). The number lives on the dossier as a "HEAT 41: WATCH LIST" stamp. |
| `transit_step.gif` | 8 | One step. The token rides the link, the link turns lime, and the newly available nodes pop out of white into orange. |
| `hq_climb.png` | 12 | The keep cutaway (details below). |
| `hq_compound.png` | 13 | The HQ seen from above, raid-style (details below). |
| `hq_compound_dynamic.gif` | 13 | The crane carries its node from the yard to the train, and its link switches from the yard side to the rail side. The train rolls north, and its car nodes link in only while they are alongside the gate. |
| `hq_compare.png` | 13 | Climb and compound side by side, with pros, cons and a recommendation. |

### `city_view.png` in detail
- **Zoom and density:** a higher zoom and a denser network, with more Sites on a finer lattice.
- **States:**
  - lime Cell territory;
  - **every** orange Site across a border link (8 here; there is no cap);
  - white Sites that aren't available yet;
  - grey Sites already run.
- **Tier** is printed on each node. The three **tier-3 key nodes** carry a gold key plate and a gold socket ring.
- **TARGET** keeps its red circle and label, with a "CENTRAL SERVER // KEYS 0/3" chip.
- **Dimmed city:** parts of the city that don't matter to this campaign are greyed and dimmed (off the Cell-to-HQ band, and Halcyon's grounds).
- **Info window:** TIER, TYPE and REWARDS only (decrypted).
- **Dossier:** the corp-paper file on the operative, including the raid station effect.
- **Heat:** a terminal strip.
- **Panning:**
  - a minimap with the view box;
  - edge chevrons;
  - pan, zoom and next-available hints in the key strip.

### `transit_view.png` in detail
- Individual buildings, as in the raid view.
- No NEXT panel and no reward preview.
- **States:**
  - walked nodes are lime;
  - the 2 available nodes are orange;
  - the rest of the route is **white**, with white-washed stickers so each node's type still reads;
  - cut-off nodes are **grey**.
- The node info window is the same one as on the map.
- The Port Authority keeps its red circle and name.
- The dossier is on the left. **Heat option A** is a compact terminal strip at the top.

### `hq_climb.png` in detail
- **Links merge:** every link into a room meets at one socket under it, and every link out leaves from one socket above it.
- **Rooms:** each room has unique dressing (8 variants: pipes, cot, forklift, barrels, desk, cargo net, fan, vending machine) on top of its node-type props.
- **Crane:** a thick truss crane loads the **freight train** at the right.
- **Top room:** the **CENTRAL SERVER** (gold chip), with THE MANIFEST in red pencil.

### `hq_compound.png` in detail
- **Camera:** the same azimuth as the city, at 55°.
- **Layout:** container walls, a moat, a drawbridge gate, the yard, the gantry crane, and the rail line with its train.
- **Nodes** sit on the yard's buildings and stacks, **on the crane's load** and **on the train's cars**.
- **Central Server:** MANIFEST CONTROL, a real building at the back of the yard.

## Recommendations
- **City-to-link transition: 1 (one camera)**, once the city map is rendered in the one-kit style. It is the cleanest of the three, because nothing cuts. Until then, use 2 (unfold) on the painted map. Keep 3 (bits) as a stylised option in Settings.
- **Heat: B in the world with A as a backup.** The city reacts on every map, and the dossier stamp gives the exact number. Show the A strip on hover or with an Options toggle, so the number is never hidden.
- **HQ: the compound (option B in `hq_compare.png`).**
  - It reuses the raid camera and gives each corp's HQ its own moving rule:
    - Meridian: crane and train;
    - Solace: the helix's walkways rotate;
    - Halcyon: the eye's scan blocks nodes;
    - Orbital: the silo doors open and close routes.
  - Its Central Server is a real place.
  - The climb's dressed rooms become the close-up art for each node.

## Central Server names per corp (to iterate)
- Meridian: **THE MASTER MANIFEST** (in MANIFEST CONTROL)
- Solace: **THE GENOME CORE**
- Halcyon: **THE PANOPTICON**
- Orbital: **LAUNCH CONTROL**

## GDD fit and open questions for DECISIONS.md
1. **Any-owned-to-any-unowned runs.** This matches GDD 3.1 and 4.1: a netrun targets one Site, and adjacency comes from Grid links.
   - Open: when several owned nodes border the target, which one is the run's start? Proposal: it is only cosmetic (it sets the link the transit view unrolls), using the lowest node id.
2. **Tier-3 keys.**
   - The GDD's minimum path is T1 > T2 three times, then T3, then the boss; T2 Sites hold the Exploits.
   - "T3 nodes carry the Central Server unlock keys" is new wording; it may map onto the GDD's T3 > boss chain.
   - **Needs a ruling:** are the keys the Exploits, or a separate T3 item?
3. **Past = grey, never removed.** The GDD says cleared Sites are used up but can be **patrolled** (3.3). Should grey Sites stay selectable for a patrol run?
4. **Dynamic HQ compound.** Moving nodes are a **new mechanic**: links that change with the crane's position and the train's timing. **This needs a GDD rule** (deterministic: a function of the step count) before anything is built. The art only proves it reads.
5. **No reward preview in the transit view.** This follows the designer's note. The node type is still readable from its sticker in every state.

## Building language (point 7)
- **One lot table, three zooms.** The city map, the raid view and the netrun view all render from one seeded lot table: a footprint per lot, height, setback, roof trim colour and window grid.
  - The camera is the same iso projection everywhere (azimuth 45°, elevation 35°, orthographic). Only `ortho_scale` changes: 1300 for the city, 640 for raids, 355 for netruns.
  - The HQ compound uses the same azimuth at 55°.
- **No merged city blocks anywhere.** The round 32–34 corridor's merged blocks are replaced by the per-lot buildings in `iso_scene.py`.
- **Godot:**
  - one `CityLots` resource (seeded per campaign);
  - one MultiMesh per building family;
  - one `Camera3D` whose orthographic size is tweened for both zooms (city > raid, city > netrun). This is transition 1.

## Godot build notes
- **Node states** come from one pure function on the Grid graph (city) or the run graph (transit and HQ):
  - OWNED/WALKED, AVAILABLE (out-edges of any owned or current node), WHITE (reachable later), GREY (done or cut).
  - It is a material parameter on the pad shader. Stickers get a white-wash or greyscale uniform.
- **Climb merge links:** one in-socket and one out-socket per room. Links are routed as socket > seam > socket polylines, and runs sharing a seam overlap on purpose.
- **Compound dynamics:**
  - the train and trolley positions are `f(step)`;
  - edges are recomputed from a rule table each step;
  - the view tweens a node's pad along with its carrier (crane load, train car).
- **Heat B:** spotlight cones are the locked H1 searchlights. The dossier stamp is a `TextureRect` that swaps per band.

## Build (from `scripts/`)
1. Blender 5.2 headless:
   - `iso_scene.py -- ../scratch/bl transit|raid|city|anim`
   - `r32_scene.py -- tower ../scratch/bl still`
   - `compound_scene.py -- ../scratch/bl <0..7>`
2. `python finish_all.py`, plus `finish.py` for `compound_full` and the 960-px compound frames.
3. `python city_view.py`, `python transit_view.py all`, `python transitions.py all`, `python hq_views.py all`.

**Kits:**
- `r35ui.py`: the dossier, the info window, both Heat options and tier badges.
- From earlier rounds: `r32ui.py`, `r31lib.py`, `sticker_lib19.py`, `target_corps.py`, `route_d_city.py` (the Cell icon).

All randomness is seeded.
