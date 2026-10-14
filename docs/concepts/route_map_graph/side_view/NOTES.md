# Route map: side view (concepts, 2026-10-14)

The designer's idea, taken from the mockup (`designer_mockup.webp`): the netrun is a walk along one street, seen side-on.
- The buildings are cut open on the route floors.
- Each route node is a **room on a floor**.
- The links are catwalks, skybridges and lift risers that climb and drop between buildings.
- The **TARGET** is the last tower on the street.

The renders use the locked language, not the mockup's flat vector style:
- the low-poly cel city kit (Blender 5.2, the round 30–35 primitives and toon ramp, ink from the id/normal/depth passes, grime, light spill, haze, rain);
- the round 35 `hq_climb` rooms, every one dressed;
- the round 31/32 node-type stickers;
- the round 44 frame kits.

Nothing is committed and the Godot build is untouched. `scratch/` is cleared at the end.

## Files

| File | What it shows |
|---|---|
| `V1_start.png`, `V1_mid.png`, `V1_hover.png`, `V1_step.gif` | **V1, cutaway street.** A night side elevation (orthographic). |
| `V2_start.png`, `V2_mid.png`, `V2_hover.png`, `V2_step.gif` | **V2, section drawing.** The same street as a corp schematic section plate. |
| `V3_start.png`, `V3_mid.png`, `V3_hover.png`, `V3_step.gif` | **V3, dollhouse dolly.** A 3/4 perspective with real room depth. Hover cuts the power, and the camera dollies with the token. |
| `compare_side.jpg` | The designer's mockup beside V1, V2 and V3 at mid-run, labelled. |
| `designer_mockup.webp` | The designer's input (unchanged). |
| `scripts/` | Everything needed to rebuild. See "Rebuild". |

### The run used in every render
- **The graph:** the parent round's graph (`../scripts/rgraph.py`), copied into `scripts/sgraph.py`, so the two rounds compare 1:1.
  - 19 nodes: 7 steps plus the start.
  - Node types: fight, elite, event, shop and Rack.
  - The TARGET Rack sits in the TARGET tower.
- **Start:** 3 options, all fights on floors +1, +3 and +5.
- **Mid:** the walked path is fight, then event, then the shop, where the operative is now.
  - Option 1 is a fight that leads to an elite.
  - Option 2 is the Rack, which leads to an elite or a fight.
  - 8 nodes are cut off.
- **Hover:** option 2 (the Rack).
  - Its tag shows (`RACK  L4`) and its branch blooms.
  - The node file in the sidebar shows TIER, TYPE, REWARDS and HP on arrival.
- **Step GIF:** the operative confirms option 2.
  - The token climbs the riser to the Rack floor, and the cable turns lime behind it.
  - On arrival, the next options turn orange (about 1.5 s of motion, then a hold).
  - GIFs are 960 × 540, the full frame at half size.

### Room dressing by type
Each type's dressing is set by the type, and each room also gets one of the 8 round 35 props as a second piece.

| Type | Room |
|---|---|
| **Fight** | A security room: a 3 × 2 cyan monitor wall, a guard desk, a gun locker with a cyan eye, and a ceiling turret with a red lens. |
| **Elite** | An armoured vault: steel plates and hazard frames, and the hulking Meridian-orange drone frame with a red eye. |
| **Event** | The odd room: a lone CRT on a plinth under a nest of hanging cables, a glowing aquarium and an empty chair. |
| **Shop** | Three lit vending machines, a market counter with a striped awning, and a blue MAINFRAME sign. |
| **Rack** | Server cabinets with amber and green LEDs, and cable trays. |
| **TARGET** | Five cabinets around a red core, high in the TARGET tower. The tower has a Meridian crown, a hazard band, a red-beacon mast and red crest windows. |
| **Start** (the Cell's relay) | A jury-rigged desk with a lime CRT stack, a couch and a pink poster. It carries the locked v4 fist disc. |

Each room is lit in its type colour: fight cyan, elite red-orange, event green, shop blue, Rack gold, TARGET red. So a room's type reads from its light before you look at its sticker.

## The three variations

### V1, cutaway street
- **At rest:**
  - A true orthographic side elevation at night, 10 px per BU.
  - Only the route floors are cut open; the other floors stay solid with lit windows.
  - The cut slabs and walls are dark poché, with the ink line on them.
  - **Depth:**
    - two hazed skyline layers and a far sky lane;
    - the street plane, with cars seen side-on, shopfront glow and awnings;
    - a foreground layer: a fence, lamp posts and a parked van;
    - a utility conduit cut under the street.
  - **Links:**
    - the walked path is a solid lime cable;
    - options are orange dashed;
    - links ahead are white dashed;
    - past or cut-off links are grey at 26 %.
  - Physical catwalks, rails and riser ladders sit under the cables, and the ink and spill make them read as structure.
- **Rooms by state:**
  - **Option:** brighter, with an orange cut frame and a glow.
  - **Current:** a lime frame.
  - **Walked:** a lime frame, with the lights dimmed to 55 % and desaturated (cleared).
  - **Ahead:** a white frame at 80 %.
  - **Past or cut off:** ghosted. The room is greyed and pushed 55 % toward the dark facade. The sticker is greyscale at 40 %, the frame grey at 35 %, and the links grey at 26 %.
- **Hover (A1 bloom, carried into rooms):**
  - The hovered link turns solid orange, and the branch's links are lit white.
  - Every room in the branch lights at ×1.45 and spills its type colour out of the opening.
  - Reachable rooms outside the branch drop to 55 %.
- **Pros:**
  - It is the designer's idea, read literally, and it reads.
  - The layout rule is a plain grid: one building per step, one floor per choice.
  - Going up and down is real: "option 3 is five floors up" is visible.
  - Node types read from the rooms, even in thumbnails (`compare_side.jpg`).
- **Cons:**
  - The facades are busy. Lit windows on solid floors compete a little with the rooms; the build should dim them further.
  - The cables bundle in the first alley at the start (3 risers side by side).
  - In the step GIF the camera does not move, so the step is small on screen.

### V2, section drawing
- **The look:** the same passes, re-shaded as a corp schematic plate. This is half the CRT, half the city.
  - A navy blueprint ground with a 40/200 px grid.
  - Facades are a dark section fill, with windows as cool traces.
  - The cut slabs and walls are poché with a cyan 45° hatch.
  - The ground is cross-hatched earth with the conduit glowing.
  - The ink is cyan outside the rooms.
- **Rooms keep their full light,** so they are the only warm, lit things on the plate.
- **Annotation:**
  - a level ruler, +00 to +10;
  - section grid bubbles 0–6 and T under the street, so **the step number is printed**;
  - a title, `SECTION A-A // LANE 15 // RELAY_4 > DEPOT_15`, with the key `GRID = STEP, LEVEL = FLOOR`.
- **Hover:** the plan is drawn in **yellow grease pencil** (locked grammar).
  - **Solid wax** is the step CONFIRM will take (current to option 2).
  - **Dashed wax** is the what-if branch behind it.
  - A wax ring goes round the hovered room.
  - The red pencil TARGET stays.
- **Pros:**
  - The clearest structure of the three. Steps and floors are labelled, so "2 more fights before the Rack" is countable.
  - The rooms pop hardest against the dark plate.
  - The pencil plan is our medium, used exactly as locked.
  - The cheapest to build: a 2D layer, no 3D street needed (see the build specs).
- **Cons:**
  - It leaves the night city mood. The plate is a document, not a place.
  - It is close to the parent round's direction B (lifted schematic), which was not chosen.
  - The blueprint cyan sits near the fight cyan.

### V3, dollhouse dolly (my bold take)
- **At rest:**
  - The same street through a 3/4 perspective camera (lens 45, about 12° yaw, looking down a little).
  - Every cut room shows its depth: floor, side wall and props in space.
  - You see the street surface with its cars, and the TARGET tower stands nearest, on the right.
  - The past recedes to the left.
- **Hover = a power cut plus a bloom:**
  - The whole street drops to about 32 % and desaturates.
  - Only the hovered branch (and the room you stand in) stays lit, and its rooms bloom in their type colours.
  - The branch cables are lit white.
  - The parent round's A4 power cut, now on rooms.
- **Step GIF:** the camera dollies in about 22 % and tracks the token as it climbs, then holds on the new floor.
  - In game this is a camera track, not a scene change.
- **Pros:**
  - The most "place". The rooms feel like rooms you are about to enter.
  - The power cut makes "what does option 2 lead to" a 1-second read.
  - The dolly gives the step weight.
- **Cons:**
  - Perspective makes the far left (the start) small.
  - Room openings at the near right are partly hidden by their own cut walls at this angle.
  - The TARGET pencil touches the right frame edge.
  - The hover is a whole-screen change. It needs the parent round's no-blink rule: hold the cut while the cursor is on any option, plus a 120 ms delay.
  - It is the most expensive build (a 3D camera on the city kit, see below).

## The 3-second check (done on every render)
- **Start:**
  - The three numbered options are three floors of the first building.
  - Each one's white dashed link runs into a typed room in the next building: 1 to the event, 2 to the fight, 3 to the fight.
  - **Passes.**
- **Mid at rest:**
  - 1 is a fight whose white link drops to the floor-2 elite.
  - 2 is the Rack, which forks to the elite and the floor-5 fight.
  - Following either one to the TARGET takes tracing. Readable in V1 and V2 because left-to-right is time and the rooms are typed, but not in 3 seconds past two steps.
  - V2's grid bubbles help count.
  - **Passes for the next step; partly for the rest.** That is why the hover exists.
- **Hover:**
  - In all three, the lit branch reads at once. In V3 it is instant: nothing else is lit.
  - **Passes.**
- **Fixed during the check:**
  - Stickers were moved off the rooms onto the top-left cut corner and shrunk, so they no longer hid the dressing.
  - Number chips were moved above the stickers. They had sat in the alley, under the risers and the pencil.
  - The hover tag was moved above the room.
  - The ROUTE buttons were stacked; the half-width GRID VIEW and Save & quit overlapped.
  - The V2 title was moved off the TARGET pencil.
  - The wax dashes were lengthened.
  - The current room was kept lit during the V3 power cut.

## Recommendation
**V1 as the route page, with V2's labels and V3's two motion ideas.**
1. **V1's orthographic cutaway street is the screen.** It keeps the locked city, it reads at rest, and its layout rule is trivial for the generator.
2. **Take V2's section bubbles and level ruler into V1** as a thin CRT overlay along the street's cut (the grid bubbles 0–6 and T sit in the ground section, which is otherwise empty). They answer "how many steps" without a tooltip.
3. **Take V3's hover power cut** in place of V1's milder 55 % dim. It is the strongest "what does this lead to" read. Use the parent round's no-blink rules.
4. **Take V3's dolly as the step beat:** a 1.5 s camera track with the token after CONFIRM. Doing this in an orthographic V1 means a 2D pan and zoom of the same scene, so it is cheap.

V2 alone is the fallback if V1's facades prove too busy on small screens. V3 as the main screen is not recommended: the perspective shrinks the past and hides parts of the near rooms.

## Build specs (Godot 4.7)

### Recommended tech: a 3D orthographic side camera on the city kit (V1)
- **One `Camera3D`, orthographic,** looking +y at the street front. Size 192 BU across 1920 px gives **10 px per BU at 1080p**.
- **The street is a seeded strip of the city kit:**
  - one building per column;
  - the route floors are a **cutaway variant** of the building mesh (front wall removed, slabs and side walls flagged as cut);
  - room dressings are packed scenes per node type, plus one random prop of 8.
- **The same building material as the city,** with a `cut` flag for the poché tone.
- **Overlays are a 2D `CanvasLayer`** projected from the 3D anchors (`Camera3D.unproject_position`):
  - cables (`Line2D` with a casing line under it);
  - sticker `Sprite2D`s, rings, chips, the tag and the pencil.
- **The V3 hover is cheap:**
  - a global `city_power` uniform;
  - a per-room `bloom` uniform on each room's light material;
  - window emission × `city_power` outside the branch.
- **The step beat:** tween the ortho `size` 192 → 157 (×1.22) and the camera x and z to follow the token, then return. Skippable (ANIM rules).
- **Why not pure 2D:** V1 depends on the ink, light spill and room light of the locked world. The same kit already exists for the city, the raid and the transit.
- **The 2D option:** a pre-baked 2D side-scroller layer is fine **for V2 only**. V2 is a flat plate plus room sprites, and it can be a `TextureRect` per room plus a procedural hatch shader.

### Layout rule (graph to street)

| Graph | Street |
|---|---|
| Layer L (0 = start, 7 = TARGET) | Building column L, left to right. Column width 13 BU (130 px), alley 7.5 BU (75 px). The TARGET tower is 16 BU wide. The first column starts at x 31.5 BU (315 px), right of the sidebar. |
| Node slot k in L | One floor of that building. Slots are sorted by height (k = 0 lowest), so a planar graph stays planar. |
| Floor f | z = f × 8 BU (80 px per storey). The start is on the ground floor (0). The TARGET floor is 8. In this concept the floors are hand-set (`sgraph.FLOOR`); the generator should seed them from the netrun `RngService` stream, sorted by k, within 1..7. |
| Building height | max(route floor) + 1–3 solid storeys. The TARGET tower is tallest (10). |
| Edge, same floor | A straight skybridge at door height (floor + 1.6 BU). |
| Edge, rising or falling | Catwalk out of the source room's right door, then a lift riser in its own alley lane, then a catwalk into the target's left door. 45° chamfers of 0.9 BU. |
| Lane order (no crossings) | Rising links: the one that ends higher takes the lane further left. Falling links: the one that ends lower takes the lane further left. Lanes are spread evenly across the alley: x = alley_x0 + alley_w × (j + 1)/(n + 1). |

- **Room opening:** column width − 2 × 0.7 BU cut walls (116 px), by storey − slab (71 px).
- **Ties:** by (layer, k), then node id.
- **Checks:** `sgraph.py` self-checks for zero crossing segments. The generator must also cap each alley at 4 lanes; with 3 slots per layer that holds.

### Sizes and colours (1080p)

| Element | Value |
|---|---|
| Stickers | Option 48 px, current 44, ahead 40, walked 36, grey 34, TARGET 62, start 42. Centred 2 px left and 6 px above the room's top-left cut corner. |
| State ring | Radius = sticker/2 + 6. 5 px for option and current, 3 px otherwise. |
| Room cut frame | Option orange #FF8C1A 4 px + glow r10. Current lime #D4FF00 4 px. Walked lime 2 px. Ahead white #F2F6FF 2 px at 80 %. Grey #7A7686 2 px at 35 %. |
| Option chip | 30 × 32 px, Anton 24. Centred above the sticker's top-left. |
| Walked cable | Lime, 7 px, casing #08060E 3 px each side, glow r8 × 0.55. |
| Option cable | Orange, 8 px, dashed 18 on / 9 off. Hovered: solid. |
| Ahead cable | White, 5 px, dashed 12 on / 9 off, at 92 %. Hover branch: solid, lit. |
| Past or cut-off group | Links grey 4 px at **26 %**. Rooms greyed (luma × 0.55, mixed 55 % toward #0F0D1C). Stickers greyscale at 40 %. |
| Walked room light | × 0.55, half desaturated. |
| Hover branch rooms | Light × 1.45, plus a type-colour spill r26 × 0.55. Others reachable at 55 %. V3 power cut: everything else × 0.32 and desaturated. |
| Room light colours | Fight #5CE1FF, elite #FF6028, event #3DFF8B, shop #5A96FF, Rack #FFC43C, TARGET #FF2C3C, start lime. |
| V2 plate | Navy #080F26, grid #5CE1FF at 6 % / 14 %, poché #211F3D + hatch 7 px, cut ink cyan at 80 %. |
| Legend hover | Everything at 100 %, plus all tags (ruling). |

### Performance
- **V1 / V3:** low to medium. One extra cutaway mesh per route building, about 19 dressed rooms, and the existing city material. Overlays are 2D.
- **V3 adds** a perspective camera and room-light uniforms.
- **V2:** low.

## GDD fit questions (for "Open questions for the designer")
1. **Node placement is now a layout rule.**
   - Layer = building and slot = floor (1–7) means the run generator must hand out floors per node.
   - GDD 4.2 has no floors. Is "height" pure presentation (seeded), or should it mean something (e.g. higher floors = Heat or elite)? My proposal: presentation only.
2. **Does the side street replace the transit view?**
   - The locked transit (bible 4.6) runs the route on the iso city between two Sites.
   - The side view is a different camera: a "street" that is not a real street of the city map. Is it a stylised street of the target Site's block, or does the city kit have to supply a real street for each border link?
3. **The step bubbles (V2) print the step index.** The round 44 route page had no text tags at rest. Are bubbles under the street (not on nodes) acceptable?
4. **Type-coloured room light** makes the type a colour role on the map (the bloom colours of the parent round). Elite red-orange sits near the option orange; the cut frame carries the state. Keep elite at #FF6028?
5. **Walked rooms are dimmed** (cleared), while the locked rule says walked = lime. The frame and cable stay lime and only the room light drops. OK?
6. **HQ runs:** the side street suits Site runs. The HQ compound (bible 4.7) stays overhead; the climb ancestor suggests the keep could use V1's cutaway. Out of scope here.
7. **DISPATCH lines** in the renders are placeholder copy and need a writer.

## Not done / limits
- **The legend-hover frame was not rendered** (the brief asked for start, mid and hover). It follows the parent round's rule: everything at 100 % plus all tags.
- **V3's dolly is a 2D crop and zoom of the finished frame,** not a per-frame Blender camera move. The chrome is redrawn unscaled on top. In Godot this is a real camera track.
- **The GIFs are half size** (960 × 540) to keep files small.
- **V2 is a post restyle** of the V1 Blender passes, using a semantic class pass (facade, cut, room, links, far city, ground).
- **Facade windows on non-route floors** are kept dim, but V1 could go further.
- **The V3 TARGET pencil touches the right frame edge.** In the build, shift the camera about 30 px left.
- **During the V3 dolly the past slides partly under the sidebar** for about 1 s. That is acceptable for a transition beat, but the build should bias the track toward the right.

## Rebuild
Run everything from `scripts/`. Nothing launches Godot. Blender 5.2 runs headless, with its log written to `scratch/`.
1. `python emblems20.py` (the corp emblems used by the holo file seal).
2. Write the V3 camera to `scratch/tq_cam.json`:
   `{"lens": 45, "loc": [160, -235, 60], "tgt": [112, 6, 38], "shift_x": -0.075}`
3. `python render.py side`, then `python render.py tq` (writes the layout JSON from `sgraph.py`, the Blender passes and the anchors).
4. `python post.py side`, then `python post.py tq` (the finished plates).
5. `python compose.py all both` (stills and GIFs).
6. `python compare.py`.

All randomness is seeded: Blender `random.Random(4207)`, and the post noise and rain use fixed numpy seeds.

The kit modules (`kit44`, `ui31`, `r31lib`, `r32ui`, `r35ui`, `sticker_lib19/31`, `markers42`, `city_view`, `route_d_city`, `crests15`, `emblems20`) are copies from `../scripts/`, with their concepts-root paths patched for this folder's depth.
