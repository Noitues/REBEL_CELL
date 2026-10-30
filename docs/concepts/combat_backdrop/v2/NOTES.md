# Combat backdrop v2: the Cutaway kit (art-pass, 2026-10-30, ART CALL 47)

Designer pick: option 2, the building from the netrun street cut open isometrically, fight in a lit floor, "light procedural generation to define the interiors". The E10 board (`D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png`) is untouched; only the backdrop is new. Solace slice, lime corp colour; pink used only where it serves (grow lamps, signs, rack LEDs).

## Files
- `room_bio.png`, `room_srv.png`, `room_gh.png`: composites under the E10 board, 1920x1080.
- `room_*_bare.png`: the graded backdrops without the board. `squint_*.png`: 1/16 scale + heavy blur of the composite.
- `kit_sheet.jpg`: every module and prop labelled, plus the three layout-grid diagrams and the rules. `sheet.jpg`: composites beside squints.
- `scripts/`: `kit_gen.py` (the seeded generator, pure python, no bpy: this is the logic to port to GDScript), `kit_lib.py` (modules + props in Blender), `bl_scene.py` (street slice + building + render, modes main/refl/mask), `post.py` (wet street, bloom, grade, board composite), `bl_kit.py` + `kit_sheet.py` + `sheet_v2.py` (sheets), `sign_tex.py` (neon sign textures), `render_room.sh`. Scratch is in `D:/rc_scratch/cutaway_kit/` (not committed).
- Pipeline per room: `render_room.sh <type> <seed> <name>` (3 Blender passes, Cycles CPU, flat emission, Freestyle ink) then `python post.py <name>`.

## The cutaway read
Ortho iso, 35.26 degree elevation, 50 px per metre. The target building is cut open at the TOP floor: the room floor plate sits on a hatched section slab, the two camera-facing walls are removed, the two back walls stay with windows and a door. Below it is the ground-floor lobby, open to the street behind four lime-edged pillars with the SOLACE blade and header signs. The cut edge = ink section line (Freestyle) + 45 degree hatch on the slab section + a lime neon line on the slab top edge + one corner post. Neighbours: tall towers behind and to the left (shop fronts, neon signs, small lit windows), LOW shops to the right (they must stay below the room floor or they hide it), a wet street in front (mirrored geometry pass blurred under the street, neon streaks, kerb lamps). The room is framed at screen (1500, 612) so it sits right of the HUD stack and above the card hand.
Grade (cohesion map pages, strong): backdrop x0.58 value, neon saturation pull 0.55, other 0.18; a feathered focus hull around the building lifts the room to x0.84 so it is the lit island. Neon gets a further 12% value loss outside the focus.

## Kit spec (art proposal for the Godot port)
Grid: room = 9 x 7 cells, 1 cell = 1 m, floor-to-wall height 3.3 m, wall thickness 0.3, slab 0.6.
| Module | Spec |
|---|---|
| Floor plate | 1x1 tiles inset 0.025 for panel seams, two alternating teal tones, banded light pool (2 steps) from the room lights |
| Wall panel | 0.3 thick, lower 1.0 m wainscot (dark teal) + corp-colour neon line at 1.0 m and at 3.15 m |
| Window | 2 m wide, sill 1.0, head 2.5; night glass (deep violet, a few lit city dots), mullion, corp-colour head bar |
| Door | 1.4 m, full height 2.3, lit frame in corp colour, cyan glass strip |
| Cut edge | slab 0.6 m with 45 degree hatch every 0.22 m, ink section line, neon top edge, corner post 0.2x0.3 with a neon strip |
| Shading | 3 toon bands from one fixed light (-0.5,-0.3,0.81), room ambient x0.8, banded light pools tinted with the room light colour, emissive parts unshaded |

Prop sets (footprint cells x height m; `*` hero). Room types are tied to the node and Site roles in GDD 4.1/4.2/11.7; the GDD defines no per-corporation Site "kinds" beyond those, so no new kinds were invented. The room type is a dressing choice per Site role, flavoured per corporation:
| Room | Used for (existing game objects) | Props |
|---|---|---|
| Bio-lab | Elite Router; Virus-exploit Site (Solace: patch that frees implants) | vat 1x1x2.5, vat bank 3x1, bench 3x1, centrifuge, incubator 2x1, monitor cart, *helix tank 2x2x3.2 |
| Server room | Server Rack nodes (layer 4 and 7); Breach-exploit Site | rack 1x1x2.5, rack row 4x1, cooling 2x1, console 2x1, UPS, low cable tray, *core tower 2x2x3.3 |
| Greenhouse / seed vault | Virus-exploit Site (seed = the open-source patch); Heat objective Sites | planter 2x1, plant tank, seed wall 3x1, grow lamp (pink), cistern, *seed tree 2x2x3.4 |
| Records / office | Router (standard combat); Intel-exploit and Scrub Records Sites | desk 2x1, cabinet, shelf stack 2x1, copier, box pile, *archive tower 2x2x3.0 |
| Lobby / reception | Terminal and Mainframe nodes; the ground floor of every building | reception 3x1, kiosk, seats, planter, *helix sculpture 2x2x3.0 |
Boss Site (The Genome Core): not rendered; suggested as the bio-lab hero scaled up with all vats lit.

## Generation rules (kit_gen.generate(room_type, seed))
1. Seed = site seed mixed with the room type (crc32), so the same Site always gets the same room.
2. Walls: one door (1.4 m) on the back wall at x in {2,3,5,6}; 2-3 windows on the back wall (not within 1 cell of the door, 3 cells apart), 1-2 on the left wall.
3. Keep-out: a 3 cell clear aisle in front of the door; a 2x2 hero pad in the centre-back third (x 3-5, y 3-4, moved if it hits the aisle).
4. One hero prop per room, always; its glow is the main light.
5. Density target 0.50-0.70 of the 63 cells (per room type range). Fill: 70% of attempts try the wall band first (back row faces -y, left column faces +x), then the open floor with random facing; retry up to 500 times; a prop must fit free cells.
6. Variety: max 2 of a big prop, 3 of a small one. Current limitation: this cap stops the fill at about 0.32-0.41 (see gaps).
7. View rule: only props at most 1.2 m tall on the cut-edge cells (y < 2 or x >= 7), so nothing hides the floor.
8. Light: corp colour (lime) pool at the hero (r 4.2 m) plus one pool per 3 props (r 2.6); a type may add a second light colour (server room cyan, grow lamps pink). Pools are 2-step bands on floor and props.
9. Colour: the building's corp colour (lime for Solace) drives wall neon, door frame, cut edge and slab edge; the room light colour is the type's accent. Other corporations swap the palette (rim/body/window sets already exist in the city kit).
Seeds shown: bio-lab 11, server room 23, greenhouse 37.

## Squint verdicts (1/16 scale, composite; stats over the visible backdrop)
| Room | mean lum | p95 | loud (>0.38) | Verdict |
|---|---|---|---|---|
| bio-lab | 0.24 | 0.48 | 10.9 % | PASS. Board first (orange arc, wheel). The lit room is the second mass, a soft green block right of the HUD; vats are the brightest spot. The towers behind add a fine grid of lit windows that reads as texture, not a mass. |
| server room | 0.24 | 0.49 | 11.5 % | PASS, slightly loudest: the cyan pool plus lime trim is the most saturated block. Still reads second behind the board. |
| greenhouse | 0.24 | 0.44 | 9.8 % | PASS. Quietest; the room is a muted green mass with pink dots. |
The old baseline backdrop was mean 0.28, p95 0.44, loud 14.5 % (v1 cutaway concept: 0.16 / 0.36 / 2.7 %). v2 is lighter than v1 because the building and street are fully rendered; all three are below the baseline. If the board needs more air, drop `v_out` (post.py arg) from 0.58 to 0.5.

## Gap to the golden plates (honest)
- Facades: the golden plates have varied painted facade detail, dense signs, window clusters and cel gradients; here towers are flat boxes with random small lit windows and a few panel strips. Reads as a clean iso kit, not as painted street art. Needs a facade module pass (balconies, AC, pipes, billboards).
- Ink is Freestyle on structure only (crisp and even); the golden plates have wobbly, varied line weight. Windows, LEDs and floor seams have no ink.
- Street: the wet street is a blurred mirror pass plus streak quads and kerb lamps; the golden plate has rain, fog layers, bokeh, cars and crowd. No rain, fog or vehicles here.
- Interiors: props are boxes and 10-sided cylinders at game scale; the density cap leaves the floors 0.32-0.41 full, sparser than the "dense props" bar (fix: raise the variety cap or let the generator add floor clutter: cables, crates, puddles). Server room and greenhouse have weaker silhouettes than the bio-lab (blue-grey metal merges; plants are dull under the room ambient).
- No people or drones in the room, no animation, no lit-window flicker; the cutaway is a still plate.
- Only the left half of the frame (under the board) and the upper right (under the HUD) is filler city; that is by design, but the frame edges near the wheel show a faint grid from the window texture through the ring gaps.

## Research (cited)
- Cutaway base view in games: XCOM: Enemy Unknown's ant-farm base view and Fallout Shelter's side-on dollhouse cross-section (press: GamesRadar https://gamesradar.com/fallout-shelter-info, Stuff.tv https://www.stuff.tv/?p=425989, GamesRadar XCOM art interview https://www.gamesradar.com/xcom-enemy-unknown-interview-we-talk-artistic-inspirations-greg-foertsch). Into the Breach's tiled iso board with clear height and low-saturation ground (from memory, not fetched): the same rule as here, that the playfield tint carries the colour and the rest is muted.
- Iso cutaway illustration conventions (parallel projection, one open corner, section poche): stock isometric data-centre cutaways (e.g. https://stock.adobe.com/images/isometric-of-a-data-center-technology-vector-illustration/1553905184), plus the HKU tenement isometrics cited in `../NOTES.md`. Lab / server / greenhouse prop vocabulary: icons8 and Magnific isometric server-room and lab vector sets (https://icons8.com/illustrations/server-room, https://www.magnific.com/vectors/hightech-lab-setup/2). Search results for a greenhouse cutaway were thin; the seed tree and seed-drawer wall are our own invention for the Solace "seed vault" idea.
- Own art: `golden_plates/street_overview.png` and `hq_rebel_cell_overview.png` (polish bar), `tide_raid/G1_parity/r43` (cel bands), `cohesion/map_pages_r42/NOTES.md` (the strong grade), `netrun_cel/` (was empty when this ran; its street look is matched only through the shared neon signs and shop-front vocabulary).

## Open for the designer
- One room per Site role as above, or per corporation theme only? The mapping is a proposal.
- Whether the lobby stays visible under the room (here it is the framing that places the building "on the street") or the plate crops it for a lower, bigger room.
- Godot port path: the generator is data-in (type, seed) and data-out (prop list with cells and rotations), so the port is a GDScript generator plus the prop and module scenes; the street slice can reuse the netrun city.
