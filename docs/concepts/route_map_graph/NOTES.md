# Route map graph: netrun route map redesign (concepts, 2026-10-14)

These are concept renders for the designer rulings of 2026-10-14 on the netrun route page. The page must show the full
run graph. Past and cut-off parts are greyed and translucent. Node type reads from the node itself. Tags appear on
hover only. Each branch must show where it leads.

The brief changed twice while this round ran:
1. **Three directions.** I made A, B and C. The designer then picked **A, "cable graph on the city"**.
2. **A iterated.** The lead idea for this step: hovering makes the route bloom up the buildings. I made four
   A-variants, A1 to A4.
3. **Go bold.** Two new families: **S** (street level) and **X** (cyberspace, two variants).

Nothing is committed and the Godot build is untouched. `scratch/` is cleared at the end.

All renders use the same realistic mid-run state:
- **The graph:** 19 nodes in 7 layers plus the start (`scripts/rgraph.py`). Layer 1 is all Routers. There is a
  Modem in layers 3 and 5, an Elite in layers 3 to 6, the optional Rack in layer 4 and the TARGET Rack in layer 7.
- **Walked so far:** fight, then event, then the shop, where the operative is now.
- **Option 1:** a fight, which leads to an elite.
- **Option 2:** the Rack, which leads to an elite or a fight, then a fight or an elite.
- **Cut off:** 8 nodes. They show at 26 %.

## Files

### Round 1: three directions (A was chosen)

| File | What it shows |
|---|---|
| `A_start.png`, `A_mid.png`, `A_legend_hover.png`, `A_node_hover.png` | **A, cable graph on the city.** All four views. In `A_node_hover`, option 1 is picked and CONFIRM is live. |
| `B_mid.png` | **B, lifted schematic.** The city dims to 42 %. The graph sits on a terminal plate, layered bottom to top with a ruler from L0 to L7. A lime leader ties the current layer to its real lot. |
| `C_mid.png` | **C, branch lanes.** A left-to-right metro plate. Each numbered option owns a coloured line, and links that two options share run as parallel lines. |
| `compare.jpg` | The current build (the W3_ROUTE AFTER frame) beside the mid-run frames of A, B and C. |

B and C stopped at their mid-run frame when A was chosen.

### Round 2: A iterated, the route blooms up the buildings

Every variant is at mid-run. "Hover" means option 2 (the Rack branch) is hovered.

| File | What it shows |
|---|---|
| `A1_rest.png`, `A1_hover.png`, `A1_motion.gif` | **A1, bloom climb.** |
| `A2_rest.png`, `A2_hover.png`, `A2_motion.gif` | **A2, rooftop beacons.** |
| `A3_rest.png`, `A3_hover.png`, `A3_motion.gif` | **A3, street current.** |
| `A4_rest.png`, `A4_hover.png`, `A4_motion.gif` | **A4, power cut** (my own bold idea). |
| `compare_A.jpg` | A1 to A4, rest beside hover. |

### Round 3: go bold

| File | What it shows |
|---|---|
| `S_rest.png`, `S_hover.png`, `S_motion.gif` | **S, street level.** A perspective camera about 25° down, at a real fork of the city. The GIF is a step forward down the right-hand street. |
| `X1_rest.png`, `X1_hover.png`, `X1_motion.gif` | **X1, light grid.** |
| `X2_rest.png`, `X2_hover.png`, `X2_motion.gif` | **X2, dense net.** |
| `X3_rest.png`, `X3_hover.png`, `X3_motion.gif` | **X3, neon street.** From the designer's mockup `designer_mockup_X3.webp`. See "X3, neon street" below. |
| `X_transition.png` | One frame of the jack-in: the 3D city dissolving into X1 with the locked binary-bits dissolve. |
| `compare_bold.jpg` | Best A (A4), S, X1, X2 and X3, each at rest and hovered. |

### Scripts

`scripts/` holds everything needed to rebuild these renders. See "Rebuild" below.

## Round 1: A, B and C

### A, cable graph on the city (chosen)
- **Pros:**
  - It stays on the real city.
  - The layered rows plus the 45/90 cable runs read as a graph.
  - The greyed past keeps the full graph without clutter.
- **Cons:**
  - It is busier than B.
  - The structure depends on the layout rule: lots must be picked to fit the rows.

### B, lifted schematic
- **Pros:** the clearest structure of the three. "How many fights before the Rack" reads at once.
- **Cons:**
  - It leaves the city.
  - It is the most Slay-the-Spire-like.

### C, branch lanes
- **Pros:** "1 leads to …" reads by colour.
- **Cons:**
  - It needs three new lane hues.
  - Shared links become bundles.
  - The more merges the graph has, the more it turns to spaghetti.

## Round 2: the bloom (A1 to A4)

### The common base for all four
- **The graph floats over the city in clean layer rows.**
  - **The layout rule:** layer to screen row, bottom to top, 106 px apart. Inside a row, nodes are 300 px apart, with a
    26 px lean per layer along the street diagonal. A seeded jitter of ±34 px is added.
  - **Each node takes a real building under its sticker.** The building's roof centre is within 48 px sideways and 34
    to 150 px below the sticker. Taller facades are preferred, one building per node.
  - **A mast drops from the sticker to that roof.** It is drawn in the state colour, with a roof socket ring.
  - So the graph reads as a graph, and every node still owns a real building to light.
- **Hover = option 2.**
  - Its downstream (the Rack, then elite or fight, then fight or elite, then the TARGET) is the branch.
  - The other option's own future drops to 55 %.

### A1, bloom climb
- **Hover:**
  - An orange light pulse runs the hovered cable, then each downstream cable layer by layer, and leaves it lit.
  - Each downstream node's building lights **floor by floor** in its node-type colour: fight cyan, elite red-orange,
    Rack gold, TARGET red.
  - Neon traces run up the building's edges, and the roofline lights when the climb tops out.
  - The node's mast becomes a beacon beam in the type colour.
  - Buildings the cables pass light partly, in warm white at low strength.
  - The other branch stays calm.
- **Pros:** it is the designer's idea and it reads. The future of the choice lights up the real city, in the colours of
  its node types.
- **Cons:**
  - At rest the page is the plain A.
  - Small node buildings carry less light.

### A2, rooftop beacons
- **At rest:** each node is a sticker beacon on an antenna mast with a dish ring on its own roof.
- **Hover:** the branch's buildings get neon facade edges and rooflines only, with no windows, in type colour. The
  passed buildings get the same in option orange.
- **Pros:** the most graphic and the least noisy. It is a strong "blueprint lights up" read.
- **Cons:** neon outlines alone are weaker than full facades. I tried running the cables "down the facades and along
  the rooftops", and it tangled the graph, so I reverted it. The cables stay in the floating layer.

### A3, street current
- **At rest:** the links are soft ground currents with packets, white dashes running the line.
- **Hover:** the branch floods with five-strand light trails, and its buildings **flicker on** in warm white plus a
  type-colour trace.
- **Pros:** the most alive at rest.
- **Cons:**
  - The flicker-on is less specific than the type-colour climb.
  - The trails sit close in hue to the option orange.

### A4, power cut (my bold idea)
- **Hover:**
  - The city's power drops to about 32 % and it desaturates.
  - Every window goes dark **except the hovered branch**. Its node buildings stay lit in their type colours, and the
    buildings it passes stay warm.
  - The dead branch's cables go slack (45 %).
  - The future of the choice is the only light in the city.
- **Pros:**
  - The strongest read and the most "ours".
  - It is the same bloom as A1, so it adds no new art.
- **Cons:**
  - It is a whole-screen change on hover, so moving between two options blinks.
  - The fix: keep the cut while the cursor is on any option, and only re-route the light between options.
  - Fast sweeps across the map need a 120 ms hover delay.

**My pick for A: A4 on top of A1.** A1's floor-by-floor climb in node-type colour is the motion. A4's power cut is what
makes it read in under 3 seconds. A2's rooftop masts are kept, because they tie each floating sticker to its building.

## Round 3: bold families

### S, street level
- **The view:**
  - A perspective camera about 25° down at the fork of streets i=26 and j=15, rendered by Blender from the same city
    kit.
  - Option 1 is the left street; option 2 is the right street.
  - Each option's building carries a **blade sign**: a dark plate with the node sticker, the state ring and the number
    chip.
  - Downstream nodes stand further along as smaller holo beacons over their roofs, shrinking with distance.
  - The TARGET is a tall red-pencilled beacon.
  - Links are ground lanes in the streets, perspective-correct: orange for options, white for ahead, lime for the
    walked street.
- **Hover:** the right-hand street blooms up its facades, with the node buildings in their type colour.
- **GIF:** a real 18-frame Blender dolly down the right-hand street, with the lanes and signs re-projected each frame.
- **The full-graph rule:** the walked path is behind the camera, so S adds a **BEHIND YOU** terminal strip (the walked
  icons in lime, "8 CUT OFF") plus GRID VIEW for the whole map. This bends the ruling: **designer call.**
- **The dossier** folds to a one-line tab ("[D] FILE"), because the left street needs that part of the screen.
- **Pros:**
  - The most immersive.
  - "What's down this street" is a natural question.
- **Cons:**
  - Only about 2 layers ahead read well.
  - The graph's structure ("how many fights before the Rack") is weak.
  - It needs node placement on real streets, so the generator must place nodes along the street graph.
  - It is the costliest to build.
- **Best use:** as the **step transition** between nodes (the S GIF) rather than the decision screen.

### X1, light grid
- **The view:**
  - The same camera and graph as A, in the net.
  - A black void, with a luminous lot grid on the floor (major lines every lot, minor every quarter lot).
  - The city is dark data blocks drawn only by their edges, brighter with height.
- **Nodes:** bright standing monoliths, an iso hex prism in the state colour, carrying the type icon.
- **Links:** light-lanes, two rails and a hot core.
- **Hover:** a **trace wall** races down the branch: a white-hot ribbon with a translucent orange wall standing on it,
  layer by layer.
- **Pros:**
  - The highest contrast and the cleanest read of the whole graph.
  - Cheap.
- **Cons:** it is austere, and it drifts from the low-poly cel city look.

### X2, dense net
- **The view:**
  - Every facade is scrolling hex, world-mapped, in cyan, pink, violet and gold per building.
  - Glitch rows with an RGB split, plus scanlines.
  - Each node not yet reached sits in a hexagonal honeycomb **ICE shell** in Meridian **tier-II red** (#FF2E28).
  - Packets of 0/1 bits ride every link.
- **Hover:** the branch is **DECRYPTED**. Its shells crack into six plates that fly out with bits, and the icons light
  white-hot.
- **Pros:** maximal and the most "netrunner".
- **Cons:**
  - The noisiest frame.
  - The ICE shell tints the node, so the type icon reads a little less at rest.

### X3, neon street (designer mockup)
I took the mockup's idea, not its rendering.
- **The view:**
  - A high 3/4 view, about 48° down, straight down street i=26. It is a real Blender camera on the same city kit
    (`render_street.py x3`).
  - The net draws the city as **neon line-art on black**. Each building's silhouette and face breaks are drawn in one
    of four neon inks: teal, pink, amber or violet (seeded per building).
  - The facades carry faint floor lines every 1.9 BU. The streets are thin kerb lines.
- **The route winds through the blocks at street level,** with right-angle turns, branching and rejoining:
  - walked: a solid lime lane coming in from below;
  - the two options: thick orange lanes;
  - the rest of the future: dashed white side lanes;
  - past and cut-off: grey at 26 %.
- **Nodes:** our stickers as neon signs on their buildings' roofs, each with a neon stem and its state ring. Far or tall
  nodes get a street-level plate over the lane end.
- **The TARGET** is the red pencil at the far end. That is the mockup's destination plate, without words at rest.
- **Hover** (the Rack):
  - The branch fills to a thick hot lane (white core, orange glow), racing out from the fork layer by layer.
  - The outlines of the branch's buildings light up: node buildings in their type colour, the buildings the lane
    passes in orange.
- **Pros:**
  - The most legible "city as wiring" picture.
  - The path reads like a real route through streets, but the whole run still fits on one screen.
  - The line city is cheap.
- **Cons:**
  - The walked past is below or behind the camera. It shows only as the lime lane entering the frame, so the
    full-graph rule is partly met (as in S).
  - The four-ink city competes with the state colours. The amber ink sits near the option orange; a calmer
    teal/violet-only city would read better.
  - It is the busiest frame after X2.
- **Build:**
  - The same edge shader as X1, with a per-building ink.
  - The lanes are a ribbon mesh on the street graph.
  - Hover is a per-building outline boost, using the same data texture as the A bloom.
  - Perf risk: **low to medium**. It needs the X1 edge pass plus a second camera.
- **Fit:** X3 is a sibling of X2 and **a designer call** for the same reasons as X: it breaks with the bible's main
  world style. If X is wanted at all, my order is X3 for a decision screen and X1 for the transition.

### X_transition
- One frame of the jack-in, using the locked round 35 `bitmask`, unchanged.
- Cells arrive by distance from the operative, plus jitter.
- The front shows 0/1 glyphs in lime, about a third of them white-hot.

### Designer calls for X
- Bible 1 rejected a plain wireframe or neon-painting city as the **main** world style. As the **net layer**, X is a
  deliberate contrast. **This is a designer call.**
- The chrome is kept unchanged in X, including the paper dossier. A net-restyled chrome is still owed if X is chosen.

## Recommendation
1. **The route page is A4 + A1.** Floating layered graph with masts to real roofs. At rest, the graph carries the
   structure. On hover, the power cut plus the floor-by-floor bloom shows the branch's future in the real city.
2. **S as the travel beat:** after CONFIRM, a 1.5 s street-level step down the chosen street, replacing nothing on the
   decision screen.
3. **X1 for the jack-in, or for HQ runs** (the bits dissolve into the net) if the designer wants a net layer.
   - **X3** is the best X for a decision screen.
   - X2 is too noisy for a decision screen, but its "decrypt" is a strong hover idea that A could borrow later.

## Build specs (Godot 4.7) for A4 + A1

### Layout
- **Rows:**
  - Layer `l` sits at row y = 966 − 105.7·l px (1080p map space; L0 at the bottom, L7 at 226).
  - Inside a row, `k` sits at x = 905 + (k − (n − 1)/2)·300 + 26·l, plus a seeded jitter of ±34 px x and ±12 px y.
    Use the `RngService` netrun stream.
- **Node buildings:**
  - Each node takes the building whose roof centre is within 48 px sideways and 34 to 150 px below the sticker.
  - Score = |dx|·1.5 + |dy − 80|·0.4 − 2·min(height, 16). Lowest wins.
  - One building per node. Break ties by building id, then node id.
  - The sticker moves to the roof's x. The mast runs from the sticker (+20 px) to the roof.
- **Cable routing (screen space, 45/90 only):**
  - A jog of |dx| ≤ gap − 2r is one 45° diagonal centred in the layer gap.
  - Otherwise the cable runs up, turns with r = 22 px chamfers, and crosses horizontally in the **middle of the gap**.
    Rightward runs sit 9 px low and leftward runs 9 px high, so no false bus joins form.

### Sizes and alpha

| Element | Value |
|---|---|
| Stickers | Option 68 px, current 62, ahead 60, walked 52, grey 50, TARGET 84, start 56 |
| State ring | Radius = sticker/2 + 7. Width 5 px for option and current, 3 px for the rest. A 1/2 px dark under-shadow. |
| Option-number chip | 30 × 32 px, Anton 24, at the sticker's top-left corner |
| Cables | Casing #08060E, 4 px each side |
| Walked cable | Solid lime #D4FF00, 7 px, glow r 8 / 0.55 |
| Option cable | Orange #FF8C1A, 8 px, dashed 18 on / 9 off, glow r 8 / 0.55 |
| Ahead cable | White #F2F6FF, 5 px, dashed 12 on / 9 off, at 92 % |
| Past or cut-off group (nodes, links, masts) | Grey #7A7686, cables 4 px, one group at **26 %** opacity, greyscale stickers, no glow |
| Legend hover | Past group at 100 %, plus all tags |
| Node hover | The other option's own future at 55 % |
| Masts | 2 px in the state colour on a 6 px casing. Roof ring 11 × 5 px. |
| Tags | Terminal chip, mono 14, state colour, "TYPE  L<n>". Hover only. |

### The bloom (A1)
- **Shader:** one city facade shader, with a per-building data texture of climb (0..1) and colour, indexed by the
  building id.
  - Already per building: the city is built per building, and each has an index.
- **Windows:**
  - Procedural in the fragment shader from world position: bays 1.6 BU (the window 0.8 wide, from 0.4), floors 1.9 BU
    (the window 0.7 high, the first row at 1.6).
  - Wall facing comes from the dominant horizontal normal axis.
  - A window is lit when floor(z − 1.6)/1.9 ≤ floor(climb·(top + 0.4) − 1.6)/1.9. That gives whole floors, so the light
    steps floor by floor.
  - Each floor's brightness is a seeded 0.55 to 1.0.
  - Window colour = type colour × 0.8 + white × 0.2, × 1.35 (cores run hot).
- **Facade wash:** below the climb front, type colour × 0.45 × fade.
- **Climb-front line:** 0.22 BU wide, × 0.9.
- **Edge trace:**
  - Silhouette and normal-break edges below the front, × 0.95.
  - At climb 1, the roofline × 1.2 and the roof × 0.18.
- **Glow:** two blurs, r 4 × 0.9 and r 14 × 0.55 (a Godot glow pass at about these levels).
- **Type colours:**

  | Type | Colour |
  |---|---|
  | Fight | #5CE1FF |
  | Elite | #FF6028 |
  | Event | #3DFF8B |
  | Shop | #5A96FF |
  | Rack | #FFC43C |
  | TARGET | #FF2C3C |

- **Passed buildings** (each hovered cable claims up to 3 buildings with ≥ 260 px inside a 20 px band): warm
  #FFBE82 at k 0.28, climb to 45 %, no trace.
- **Timing over 1.2 s (normalised t):**
  - The pulse runs each cable over 0.24 s, starting 0.2 s × (layer depth + 1).
  - Each building climbs over 0.38 s, starting 0.19 s + 0.2 s × depth (0 = the option).
  - The last climb (the TARGET) ends at about 1.19 s.
  - Un-hover reverses at 2× speed.

### The power cut (A4)
- **City:** a global uniform `city_power` goes from 1 to 0.32, with saturation from 1 to 0.6, over 0.3 s.
- **Window emission:** × city_power on every building not in the branch.
- **Dead branch:** its cables go to 45 %.
- **Hover rules:**
  - The cut holds while the cursor is on any option (no blink between options).
  - It releases 0.25 s after leaving all options.
  - Hover delay: 120 ms.

### Performance risk

| Family | Risk |
|---|---|
| A1, A4 | **Low.** One shader branch plus a 256 × 1 data texture updated during tweens. No extra passes. |
| S | **Medium to high.** A second perspective camera, a long draw distance (fog at about 260 BU hides the far city), signs as Sprite3D/billboards, and a 1.5 s camera dolly. It needs LODs on the far city. |
| X1 | **Low.** An unshaded black material, an edge shader (or a screen-space edge from normals and ids), and a grid floor shader. |
| X3 | **Low to medium.** The X1 edge pass, a second camera, ribbon lanes, and a per-building outline boost. |
| X2 | **Medium.** Triplanar scrolling hex on every facade, a glitch post-process, ICE shells per node, and packets as GPUParticles along Curve3D. |

## GDD fit questions (for "Open questions for the designer")
1. **Bloom colours.** The node-type colours are a new role on the map: fight cyan, elite red-orange, event green, shop
   blue, Rack gold, TARGET red. They are the stickers' own ring colours. The elite (#FF6028) sits near the option
   orange. Keep it, or push the elite to the red #FF2E28?
2. **Hover-only richness.** The rest frame still carries the structure (the ruling), and the bloom only adds to it.
   Confirm that hover may carry the "wow" without breaking "no tooltip needed".
3. **The power cut** reuses a world-dimming language. Does it clash with the raid de-power grammar (bible 4.7/4.8)?
   The cut is global and grey; raid de-power is per-link with sparks.
4. **The layout rule** asks the generator for lots that fit layer rows on the transit camera. GDD 4.2 does not cover node
   placement. Fine?
5. **S and the full-graph ruling.** The walked path is behind the camera, so S uses a BEHIND YOU strip plus GRID VIEW.
   Acceptable, or is S a transition only (my proposal)?
6. **S needs real streets.** The run's nodes must sit along the street graph between the two Sites (the transit link).
   The GDD does not specify this.
7. **X as the net layer.** Bible 1 rejected the wireframe or neon city as the main style; this is a deliberate contrast
   (designer call). Is X the jack-in transition, the HQ-run look, or neither?
8. **ICE colour in X2.** Meridian's corp hue is the option orange, so I used its tier-II red for ICE. For the other corps
   the corp hue works directly (Solace lime is a conflict too: Cell lime is reserved).
9. **Mid-run DISPATCH lines** are placeholder copy and need a writer.

## Not done / limits
- **The bloom is lit by deferred relight, not a per-frame Blender emission render.**
  - The A, S and X frames are built from Blender's own passes of the same scene and camera: beauty, window emission,
    world normal, world position, and a per-building index from the city footprints. The bloom is lit on those passes.
    This is exactly what the Godot shader would do, and it keeps 15-frame GIFs cheap.
  - The S dolly frames are real Blender renders (18 frames).
- **The legend hover and node-file views were rendered for A only** (`A_legend_hover`, `A_node_hover`). The variants'
  hover frames show the node file and tag, and their legend hover follows the A rule.
- **B and C stopped at mid-run**, by the designer's call.
- **The A2 cables-down-the-facades idea was tried and dropped:** it tangled the graph.
- **S frames the decision with 2 options only.** A 3-option fork would need a T-junction camera.
- **The GIFs are cropped to the map** (880 × 587, or 960 × 540 for S) to keep the files small.

## Rebuild
All rebuild steps run from `scripts/`, with Blender 5.2 headless. Nothing here launches Godot.

1. `python copy_kits.py`: copies the locked round 44 kits and patches their paths for this folder's depth.
2. Build the layout:
   - `python layout36.py`
   - `python emblems20.py`
   - `python scope39.py`
   - `RUN_V3=1 python runmap38.py` (all with `NET36=net_scope.json`)
3. `python render_plates.py`: the transit camera passes.
4. `python plate.py`: the finished city plate.
5. Round 1: `python directions.py`.
6. `python make_street39.py`, then `python render_street.py key` and `python render_street.py walk`.
7. The renders:
   - `python avariants.py`
   - `python street.py`
   - `python xnet.py`
   - `python render_street.py x3`, then `python x3.py`
   - `python compare.py`

All randomness is seeded.

## Designer feedback (2026-10-14)
- Hiding the walked path behind the camera is OK for street-level views (the full-graph ruling is bent here).
- A-set: **A1 Bloom climb** is the favourite. A4 reads well, but the designer prefers A1 alone.
- S-set: the designer likes the street-level navigation view.
- X-set: none are kept. X1 is rejected. X3 reads well, but it departs from the locked city look (no wireframe city; we don't revisit that choice). X2's scrolling coloured binary on the buildings is a cool effect; park it for reuse elsewhere.
- Next: wait for the side-view family before further iterations.
