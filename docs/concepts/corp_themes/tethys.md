DRAFT (Batch API, Sonnet, 2026-10-18; AD review pending)

# TETHYS: THE WATER LEVEL ART PLAN

Art only. No rules are invented here. Anything the art needs from the rules is listed in **Questions for the design session**. Names follow the draft: Head steps LOW / RISING / HIGH / FALLING, Levels UPPER / LOWER, DOCK LOCK, DAM RUN.

---

## 0. Shared art rules (all three parts)

### 0.1 Head step → water height

One set of numbers. One lookup, one value. Every part reads it.

| Head step | Water plane at the dam (ZW) | Dry street | Head over dry side | Reads as |
|---|---|---|---|---|
| LOW | **+0.6 BU** | 0 | 0.6 | Barely above street. Gauge red line near the bottom tick. Lock chamber half empty. |
| RISING | **+2.5 BU** | 0 | 2.5 | The approved baseline in `DESIGN.md` (water 2.5 over dry 0). Caustics at maximum. |
| HIGH | **+5.0 BU** | 0 | 5.0 | Water stands near the crest parapet (crest road z 12 is still 7 BU above the water). Gates strain. |
| FALLING | **+3.2 BU** | 0 | 3.2 | Between RISING and HIGH. Streak marks on the wet face, ebb flow, foam lines. |

FALLING must not look like RISING. It differs in three ways: a wet band **above** the waterline on the wet face (the tide mark), water moving toward the sluice chutes (white water on every open gate), and a warm red tint on the gauge arrow. See 0.4.

Rule for the pier city: the main station sits on stilts to the seabed. A change of +4.4 BU between LOW and HIGH is small against a drum of 10.4 radius, so the station never changes shape. Only the lower ring, the breakwater top and the glass-tube walkways react (see A.2).

### 0.2 Warm = dam / dry, cool = water (the colour rule)

This is the existing rule from `DESIGN.md` section 1, and it carries the whole readability plan.

| Zone | Light | Neon | Used for |
|---|---|---|---|
| Dry city, dam, sluice bays, lock tower, causeway entrance | Sodium (warm), amber strobes, red beacons | Warm | Every dry or high-and-dry element |
| Water, station, pods, drowned streets, deck stair | Cool white key, abyss blue, photophore | Cool | Every wet or submerged element |
| The waterline itself | A thin 1-2 px bright line where warm meets cool | White | The tide mark. The eye finds the Head by finding this line. |

New rule for the water level: **the waterline is the only place both temperatures meet.** Never put a warm light below the waterline, and never put a cool light above it. The exception is the existing warm windows in drowned buildings, which stay warm, faded by `water_fade` (red dies first, so they shift toward amber-green with depth). They are the "lights left on" detail.

### 0.3 The gauge (current + next 3 steps)

One widget, used on the HQ netrun map, the street netrun and the raid map. Same glyphs, three sizes.

**Form: a vertical tide gauge**, the same shape as the dam's white-tick gauge, so the overlay matches the diegetic object.

| Part | Spec |
|---|---|
| Body | A vertical glass column, 14 px wide x 96 px tall at 1080p. Trench fill (#06112A). 1 px white tick marks. |
| Slots | 4 stacked cells, top = NOW, then NEXT 1, 2, 3 reading downward. Each cell 22 px tall. |
| Step glyph in each cell | A wave profile, 18 px wide: LOW = flat line near base. RISING = slope up. HIGH = line near top with a crest. FALLING = slope down. Abyss blue stroke on trench. |
| NOW cell | Photophore (#7CF2E4) outline, 2 px. The wave glyph is filled. |
| NEXT cells | Dim: 60 %, 40 %, 25 % opacity. No outline. |
| Water fill inside the column | Abyss blue, level matches the NOW step. A 1 px white waterline. |
| Tide tick | A small dot row under the column. One dot per node until the next step, from the draft's rule (every 2 completed nodes). Filled dots = done. |

The gauge reads in three layers, so it works at a glance: the **fill height**, the **glyph shape** and the **outline**.

The FALLING glyph needs a second cue. Lightless red (#C8264E) is reserved for tier II and must not be used here. So the FALLING glyph gets a small downward chevron in white next to it.

### 0.4 Step cues, side by side (one table to hold the line)

| Head step | Water height | Gauge glyph | Wet face | Caustics | Gates | Surface |
|---|---|---|---|---|---|---|
| LOW | +0.6 | flat line | Wet band: none, dry concrete visible down to the toe | Weak (x0.5) | Mostly shut, dark grates | Calm, thin foam at the dam |
| RISING | +2.5 | slope up | Clean waterline, no band | Strong (x1.0, full) | One in three open | Gentle ripple |
| HIGH | +5.0 | line with crest | Water to near the crest; dry face sweats | Medium, broad, scattered (more depth = softer) | Gates shown straining: closed, with white spray at the seams | Choppy, foam streaks |
| FALLING | +3.2 | slope down + chevron | Tide mark band above the water, darker and wet | Strong (x0.9) | Every gate in the bay open, white spillway water | Flow lines toward gates |

Caustic strength follows the draft's note (stronger at RISING and FALLING). In HIGH the caustics soften because the water is deeper over the seabed; in LOW they weaken because there is less water to refract through.

### 0.5 Readability constants (applies to all parts)

- **Value band.** The approved renders have a median luma of 0.14. Water-level cues must sit at least 0.10 above local value: the waterline, the gauge fill and the tide mark. Do not rely on a hue shift alone, because the dark band swallows it.
- **46 px rooms.** A route room is about 46 px across. A waterline must read inside one: a 2 px bright line needs 12 px of coloured fill (blue below, none above) to survive. Smaller than that, show the state with the Level glyph instead.
- **Occlusion rule.** The camera-rig rule (`occlusion.py`) cuts dry buildings in the sight cone to the 6.4 BU stub. In Part B and Part C the water-level art must never be hidden by a cut building, and a cut building must not lose the water line that crosses it. The water line is drawn on the cut stub too (see B.1).

---

## PART A. TETHYS HQ: THE DAM RUN

### A.1 The 4 Head states as scene states

The scene is the approved pier city, dam, station and deep stair. The Head only moves **water-plane parameters** and a handful of dam props. It never moves geometry. This matches the draft's art hooks (`head_step`, `head_next[3]`).

| Element | LOW (+0.6) | RISING (+2.5) | HIGH (+5.0) | FALLING (+3.2) |
|---|---|---|---|---|
| Water plane above the dry street | 0.6 | 2.5 | 5.0 | 3.2 |
| Water plane inside the breakwater (calm ring) | -1.2 under baseline | baseline | +2.0 over baseline | +0.8 over baseline |
| Breakwater top (z +1.3, ZW) | Stands 1.8 above water, dry concrete + photophore line visible | Stands 0.9 above water | **Awash**: water over the top at 0.4 BU. Photophore line seen under water. | Stands 0.5 above, wet with a tide mark |
| Glass-tube pier walkways (deck z about +0.5) | Clear of the water, all lit | Slightly above water | Lower third of the tube drowned, photophore floor strip glows through the water | Wet, with run-off lines |
| Pier-end and ring pods (drum base about ZW +1) | Skirt fully visible | Skirt feet in the water | Skirt half under, lit portholes in the skirt go cyan through the water | Skirt streaked, wet band |
| Main station | Unchanged | Unchanged | Unchanged (the hull stands clear) | Unchanged |
| Drowned quarter | Streets at 5-24 BU depth, rooftops and lamps visible | Baseline | Rooftop of the shallowest drowned buildings go under | Baseline with debris pulled toward the dam |
| Dam gauge red line | Near the bottom tick | Mid | Near the top tick | Mid-high, arrow down |
| Lock chamber | Low, mitre gates dry up to the sill | Mid | Full | Draining, standing water streaks on the walls |

**Which rooms drown.** The water plane is a global value. The draft's rule is per-node: UPPER nodes stay on the surface, LOWER nodes are the decks, the causeway's underside and the flooded rooms. Art maps this like so:

| Place | Level (per the draft) | What drowned looks like |
|---|---|---|
| Dam road, sluice bays, lock tower, station crown, pod tops | UPPER | Never drowned. Awash at HIGH (water licks the lowest edge, white spray). |
| Causeway underside, the pod skirts, the decks 1-5, moon pool, ring walkway | LOWER | Drowned at HIGH. The room is dimmed, lit windows go cyan-green, an abyss-blue tint fills it, bubbles stream up from its vents. |

**Closed / drowned node look.** The draft says LOWER nodes at HIGH are closed unless an Exploit or Sluice opens them. The art treats "closed" as "drowned and sealed":

- **Drowned and closed:** deep blue-black fill at 70 %, windows dimmed to 30 %, a red sealed hatch glyph (a small bulkhead icon with a bar across it) where the door sits. Water surface shown above the room as a bright waterline. Bubbles rise from the seams.
- **Open (LOW / RISING / FALLING):** warm window lights on, no tint, a small door glyph, no waterline across the room.
- **Drained (via Divert):** the room is shown **dry in a flooded zone**: a thin white air-line (a meniscus drawn as a curved 2 px line) round the room, warm window lights, a dry-stained wall, faint condensation. This is the one case where warm lights appear in the deep, and the air-line is the justification.

A closed node must never look like a destroyed node. The hatch glyph is the discriminator: closed rooms have intact windows, only dimmed.

### A.2 Caustics and the warm/cool rule per Head step

The approved water values (`tethys_preset.WATER`) stay as the baseline. The Head multiplies two of them.

| Parameter | LOW | RISING | HIGH | FALLING |
|---|---|---|---|---|
| Caustic strength (baseline 3.0) | x0.5 | x1.0 | x0.7 | x0.9 |
| Caustic depth e-fold (baseline 46) | x0.7 | x1.0 | x1.4 | x1.0 |
| Caustic patchiness (baseline 0.30) | 0.15 | 0.30 | 0.45 | 0.30 |
| Light shaft count (baseline 16) | 8 | 16 | 16 | 12 |
| Surface bump (baseline 0.05) | 0.02 | 0.05 | 0.10 | 0.07 |
| Fog sigma step from Pressure | n/a | n/a | n/a | n/a |

Rationale: at HIGH the water column is deeper, so ripples spread over a wider area and look softer. At LOW there is too little water above the seabed for strong ripples. At RISING and FALLING the surface is moving and the ripples sharpen.

**Warm/cool rule check per state:**

| State | Rule held? | How |
|---|---|---|
| LOW | Yes | More of the dam shows, so more warm. The drowned quarter shrinks. The balance tilts warm. |
| RISING | Yes | The baseline. |
| HIGH | Yes, with risk | The water reaches the dam's lower sodium floods. Rule: the floods on the dry-face toe stay (they are on the dry side, behind the dam). The wet-face lamps (cool) are submerged and go dim. No warm light is ever placed on the wet face below the waterline. |
| FALLING | Yes | The ebb exposes the tide-mark band, drawn in a warm wet-concrete tone, which reads as "dam" not "water". |

### A.3 The tide gauge and Level glyphs on the HQ overlay

**Gauge placement.** Top-left of the route map, in the safe zone. It reuses the gauge from 0.3. Its diegetic twin stays on the dam: the dam's white-tick gauge shows the current step in-world, so a viewer sees the same number twice.

**Level glyphs** (one per node, drawn on the node pin):

| Glyph | Meaning | Form |
|---|---|---|
| UPPER | Surface | A small wave line with a **dot above it**. White. |
| LOWER | Below the surface | A wave line with a **dot below it**. Abyss blue. |
| UPPER, awash (HIGH) | The draft's HIGH modifier | The UPPER glyph, with the wave line drawn thicker and a small spray tick. |
| LOWER, closed (HIGH) | Flooded and closed | The LOWER glyph under a red hatch bar. |
| LOWER, drained | Diverted | The LOWER glyph with a white air-line round it. |

Glyph size: 14 px, to sit on a 46 px room pin in the corner without covering the type icon. Glyph and type icon must never share the same corner.

**Forecast on the map (the next-3 preview).** The draft says nodes' Level and openness are visible ahead. The art shows a ghost tint on future-closing nodes: a node that will be closed at the next HIGH step gets a thin dashed abyss-blue outline (1 px). It appears only when the player holds Tide Tables (the Intel Exploit) or when the next step is within the gauge window. Without that the map shows only the current state.

### A.4 Sluice-bay puzzle node look

The puzzle node is in the dam (layers 2 and 6). Art reuses the dam's real sluice gate bay as the node's scene.

| Element | Spec |
|---|---|
| Node pin | The standard room pin with a gate-bay icon: two vertical piers and a lift gate between them. Hazard stripe across the top (yellow-black, the dam's hazard band). Warm, since it is on the dam. |
| Scene (when entered) | A close frame of one sluice bay: 4 gates in a row (the draft says 4). Each gate: raked piers, a steel leaf, a hoist gantry. |
| Gate state | **Open** = leaf lifted, white water down the spillway chute. **Shut** = dark culvert grate with a red light. This is the existing dam rule. |
| Forecast row | Under the gates, a row of 4 wave glyphs from 0.3 (the next four steps), with the player's chosen action **ghosted**: a thin photophore outline round the step the action would change. |
| The 3 actions (Hold, Skip, Divert) | Three pads under the forecast. Hold = a pause bar glyph. Skip = a double chevron. Divert = a branch glyph. Each pad is a 46 px target. |
| Solved state | The picked gate leaf animates up or down, and the gauge column updates. |

Warm/cool split in the scene: the bay is **warm** (sodium on the dam face), the water behind and below the gates is **cool**. The gate leaf is where they meet, and the white spillway water is the bridge.

### A.5 The DOCK LOCK filling

The lock is one node (layer 3) and the draft says it fills over a 4-turn clock. The art has a **filling meter** with four states, one per turn.

| Turn | Lock chamber water | Mitre gates | Signals | Gauge |
|---|---|---|---|---|
| 0 (entry) | At the canal level (low) | Both shut | Red | Unchanged |
| 1 | +25 % of the way to the drowned-quarter level | Shut | Red | Unchanged |
| 2 | +50 % | Shut, strain lines at the seams | Red, blinking | Unchanged |
| 3 | +75 % | Shut, white spray at the seams | Red, fast blink | Unchanged |
| 4 (end of fight) | Full, level with the drowned quarter | **Win:** gates swing open, signals go green. **Over the limit:** gates stay shut, water over the gate tops, signals stay red. | | The Head steps once (the draft's rule), the gauge animates |

The diegetic read: chamber water level, spray at the seams, signal blink rate. The overlay read: a 4-pip clock (4 small dots, filled as turns pass) next to the lock pin, in the same style as the tide ticks. Do not add a second progress bar; the pips and the diegetic water are enough.

### A.6 Pressure-deck rims

The Pressure number (0-4, rising 1 per layer from layer 8) is the draft's depth cost. The decks already have lit porthole rims. The art uses the **rim** as the readout.

| Pressure | Deck rim | Fog sigma step | Extra |
|---|---|---|---|
| 0 | Photophore ring, thin, even | baseline | Normal |
| 1 | Ring brightens, 1 amber segment | +4 % | One amber tick on the rim |
| 2 | 2 amber segments, ring slightly warm | +8 % | Rim-light flicker at 0.5 Hz |
| 3 | 3 amber segments | +12 % | Porthole glass shows a hairline crack decal |
| 4 | Full amber ring, faint red pulse | +16 % | Cracks on all portholes, bubbles from the rim seams |

Amber, not red, because lightless red is tier II and material only. The amber is "the hull is working", not "enemy". The wheel's RAM cap pip (a draft requirement) uses the same amber, so the two read together.

### A.7 How the 11 layers map to the 4 acts and the slots

The draft's layer table and slot classes are taken as given. The art assigns **the camera, the light and the water state each act is shown in**.

| Layer | Act | Slot class | Place | Dominant light | Level mix | Water read |
|---|---|---|---|---|---|---|
| 1 | I Dry Side | `dam_bay` | Dam road | Warm (sodium, amber strobes) | UPPER | Water to one side, dry city to the other. The waterline is the whole backdrop. |
| 2 | I Dry Side | `dam_bay` | Sluice bays | Warm | UPPER | Gates, spillways, white water. |
| 3 | II Lock | `lock` | DOCK LOCK | Warm to cool across the chamber | UPPER | The filling chamber. |
| 4 | III Piers | `pier_end` | Causeway, pier-end pods | Cool, warm lamps on the causeway | UPPER and LOWER | The first drowned views. |
| 5 | III Piers | `pier_end` / `ring` | Pier-end and ring pods | Cool | UPPER and LOWER | Wide pier city, calm ring. |
| 6 | III Piers | `ring` | Ring pods (sluice node here) | Cool | UPPER and LOWER | Breakwater awash at HIGH. |
| 7 | III Piers | `inner` | Inner pods | Cool, station key light | UPPER | Closest view of the station. |
| 8 | IV Stair | `station` | Main deck, crown | Cool, warm windows | UPPER | Pressure 0. Looking down from the station. |
| 9 | IV Stair | `deck` | Decks 1-2 | Cool, deepening | LOWER | Pressure 1. |
| 10 | IV Stair | `deck` | Decks 3-5, THE VENT CAP | Abyss blue, cyan moon pool | LOWER | Pressure 2-3. The moon pool well. |
| 11 | IV Stair | `core` | Moon pool, THE BLACK SMOKER | Hot orange core on trench black | LOWER | Pressure 4. Deepest. |

**Warm-to-cool progression.** The run starts almost entirely warm (layers 1-2), crosses at the lock (layer 3), is cool for the piers and stair, and ends on a single hot orange point at the vent (layer 11). The colour rule drives the pacing.

### A.8 Camera per act (descent, not climb)

The player descends. In every act the camera starts high and ends lower than where it began. This is the main way art tells the player that depth is progress.

| Act | Camera | Pitch | Yaw | Distance | Look-at | Direction of travel on screen |
|---|---|---|---|---|---|---|
| I Dry Side | High 3/4 over the dam, looking at the dam road and sluice bays with the pier city small in the back | 50 | 118 | 160 | The dam line | Left to right along the dam |
| II Lock | A tighter dam-top view, the lock chamber centred | 45 | 118 | 95 | The DOCK LOCK | Toward the lock |
| III Piers | The approved overview (pitch 50, yaw 135, dist 210), then dropping with each layer: layer 4 pitch 46, layer 7 pitch 40 | 50 down to 40 | 135 down to 118 | 210 down to 142 | The station | Inward and down toward the station |
| IV Stair | A steep down-look: pitch 40 at layer 8 easing to **pitch 62 at layer 11**. The look-at point moves down the stair with the player. | 40 up to 62 | 118 | 142 down to 90 | The current deck, then the moon pool | **Straight down**. The "descent" shot. |

Note on the pitch in Act IV: higher pitch means looking more downward (50 is 3/4, 90 is top-down). Act IV rises from 40 to 62 so the view looks more steeply down the well. This is the opposite of a climb, where the camera would pitch up and show the sky. In Act IV the sky should leave the frame.

Camera moves per layer are an ease of 0.8 s. Rule: the horizon (the waterline) never rises up the frame in Acts III and IV; it drops. If it rises, the shot reads as a climb.

**Occlusion note.** The dam-line cameras (Acts I and II) look over the dry city, where the occlusion rule cuts nothing (see `DESIGN.md` section 7). Acts III and IV look at the water, so occlusion applies only to the towers that stand out of the water (an open item in `DESIGN.md` 11).

### A.9 Frame list for a new round of finals (HQ)

All 2560 x 1440, 40 spp, Cycles, `post_city.aaa`, same pipeline as the approved finals. Each frame shows one Head step. The scene is the approved HQ with only the water parameters and dam props from A.1.

| # | Frame | Camera | Head step | What it must show |
|---|---|---|---|---|
| 1 | `hq_head_low_overview` | Overview (pitch 50, yaw 135) | LOW | Dry dam face, shallow water, breakwater standing dry, weak caustics. The "safe window". |
| 2 | `hq_head_rising_overview` | Overview | RISING | The approved baseline. The control frame. Re-render for matched exposure. |
| 3 | `hq_head_high_overview` | Overview | HIGH | Breakwater awash, pier tubes half drowned, water near the crest. |
| 4 | `hq_head_falling_overview` | Overview | FALLING | Tide mark band, all gates open and spilling, ebb flow lines. |
| 5 | `hq_head_low_dam` | Act I camera (pitch 50, yaw 118, dist 160) | LOW | Dam face, full gauge reading low, warm side dominant. |
| 6 | `hq_head_high_dam` | Act I camera | HIGH | The same frame at HIGH. Pair with 5 for a before/after. |
| 7 | `hq_sluice_bay` | Close on one bay (pitch 35, dist 60) | RISING | Four gates, mixed open and shut, forecast row space left clear for overlay. |
| 8 | `hq_lock_filling_t2` | Act II camera | RISING | Lock chamber at turn 2: half full, spray at seams, signals red. |
| 9 | `hq_lock_open` | Act II camera | RISING | Win state: gates open, signals green, full chamber. |
| 10 | `hq_lock_failed` | Act II camera | HIGH | Over-limit state: water over the gate tops, signals red. |
| 11 | `hq_pier_ring_high` | Act III camera (pitch 44, yaw 125, dist 175) | HIGH | Ring walkway awash, pod skirts half drowned. |
| 12 | `hq_decks_p0_p4` | Act IV camera (pitch 62, dist 90) | LOW | The deck stair at Pressure 4 for a rim-light reference. The Head is LOW to keep the stair readable. |
| 13 | `hq_decks_drowned_high` | Act IV camera (pitch 55, dist 110) | HIGH | LOWER rooms closed and drowned: hatch glyph space, dimmed windows, bubbles. |
| 14 | `hq_decks_drained` | Act IV camera | HIGH | One Diverted deck dry inside the flooded stair: the air-line. |
| 15 | `hq_moonpool_server` | Act IV camera (pitch 62, dist 90) | FALLING | The moon pool and THE BLACK SMOKER. |
| 16 | `hq_decision_high` | Decision camera (`t_dec`) | HIGH | The decision pose with a branch at HIGH: the closed branch needs to be readable from the pose. |
| 17 | `hq_hover_low` | Hover camera (`t_hov`) | LOW | Hover grade over a branch (spec 9.4). |

Frames 1-4 are the same camera at four steps. They must hold identical exposure so the only change is the water. That quartet is the hero set for the design session.

Frame 2 is a re-render. It is rendered to confirm the new Head multipliers (A.2) do not shift the approved baseline, and it is the baseline the other three frames are measured against.

### A.10 Kit reuse vs new (HQ)

| Element | Status | Note |
|---|---|---|
| Pier city, dam, lock, causeway, deck stair, moon pool, server | **Reuse** | Approved. No geometry changes. |
| Dam gauge | **Reuse** with a tweak | Add a movable red line bound to `head_step`. |
| Water plane, caustics, light shafts | **Reuse** | Parameters only (A.2 table). |
| Sluice gate leaf and spillway | **Reuse** | Already open or shut per gate. Bind to `gate_state[]`. |
| Lock mitre gates and chamber water | **Reuse** | Add four fill levels (A.5). |
| Deck rims | **Reuse** | Add amber segments and fog step (A.6). |
| Breakwater | **Reuse** | Needs the awash state (water over the top at HIGH). Small shader or plane change. |
| Tide mark band on the wet face | **New** | A decal strip above the waterline. Warm wet-concrete tone. FALLING only. |
| Closed hatch glyph, drained air-line | **New** | 2D overlay and one small 3D meniscus ring for the drained room. |
| Tide gauge widget, Level glyphs, forecast ghost | **New** (2D) | UI only. |
| Pad and room-state overlays | **New** (2D) | Reuse the existing pin kit for shape, add state layers. |
| Bubbles at drowned seams | **New** (small) | A particle set, rising from the vents. |

### A.11 Readability risks (HQ)

| Risk | Cause | Mitigation |
|---|---|---|
| LOW and RISING look almost identical from the overview | 1.9 BU difference against a 210 BU camera distance | Do not rely on the water plane alone. The gauge, the breakwater dryness (1.8 vs 0.9 above water) and the caustic strength carry it. Check the overview pair at 50 % downscale. |
| FALLING reads as RISING | Similar height (3.2 vs 2.5) | The tide mark band, open gates and arrow chevron are the discriminators. All three must appear, not one. |
| Waterline lost in the 0.14 value band | The whole scene is dark | The waterline is the one bright line. Give it 0.10 over local luma. Verify with the plate values. |
| A 46 px room cannot show a waterline | Too small | Rooms show the Level glyph and closed hatch instead. The waterline is only drawn on scene frames, not on pins. |
| Closed LOWER rooms read as destroyed | Both are dark | The hatch glyph plus intact dimmed windows. Test with a greyscale pass. |
| The calm-ring window hides the water change inside the breakwater | The ring is glass-calm by design | Outside the ring carries the surface cues (chop, foam). Inside the ring the cue is the breakwater top and the pod skirts. |
| Server hidden when the water rises | HIGH adds depth over the moon pool | The moon pool is already a lit well. Keep its cyan column unattenuated. Check frame 15 at HIGH if the design session wants that pairing. |
| Warm lamps on the wet face drown at HIGH | They go under the new waterline | Rule from A.2: no warm light below the waterline. Move the lowest wet-face lamps to the cool set. |
| Pressure amber confused with the warning strobes | Both amber | Strobes are on the dam only, never on the decks. Different places, different rhythm. |

---

## PART B. TETHYS STREET NETRUN

The spec is a one-city street, side view, buildings with floors as rooms. The Head crosses the facade as a **water line**. LOWER rooms are below it.

### B.1 The water line per Head step across the facade

The street scene is a flat side view, so the water line is a **horizontal line across the whole frame**, drawn at a height set by the Head. Every building is cut by it. The line is one continuous element, not per-building.

| Head step | Water line height | In floors (assuming about 3 BU per floor at the building scale) | Reads as |
|---|---|---|---|
| LOW | Just above the street, under the first-floor sill | **Ground floor dry**, the line is at kerb height | Wet pavement, puddles, nothing flooded |
| RISING | Half the ground floor | Ground floor half under | Street awash |
| HIGH | Top of the ground floor and into the second | Ground floor fully under, 2nd floor sill awash | LOWER rooms drowned |
| FALLING | Between RISING and HIGH, with a tide mark above | About 1.5 floors | Tide mark band shows how high it was |

Water line values are in fractions of a floor, because the street view is built from floors. The BU values from 0.1 are kept for the HQ and Part C, where the dam sets the scale. The street uses floors. The design session can fix the exact floor height once the street kit is final (see Questions).

**The line on cut buildings.** The occlusion rule cuts dry buildings in the cone to the 6.4 BU stub. The street water line must be drawn on the stub too. Implementation: the line is a separate full-width strip, drawn on top of the building layer and below the sign layer. It does not depend on building height, so a cut building still shows the line.

**Line anatomy** (so it reads at a glance):

| Layer | Spec |
|---|---|
| Surface line | 2 px white-cyan, brightest element in the frame band |
| Meniscus | A 4-6 px soft glow above the line, reading as the surface catching light |
| Body | Everything below the line is tinted abyss blue, graded by depth |
| Foam | Small white flecks at the line where it meets each facade (the water laps at the walls) |
| Tide mark (FALLING) | A darker, wet band 1 floor tall above the line, with a hard top edge |

### B.2 How LOWER rooms below the line read as flooded

A street room is a floor of a building. The Level assignment is the draft's: UPPER rooms above the street water, LOWER rooms below it.

| Property | LOWER room (drowned) | UPPER room (dry) |
|---|---|---|
| Tint | Abyss blue overlay, depth-graded (deeper = darker, red gone) | None |
| Windows | Lit windows shift to cyan-green, dimmed to 50 % (the `water_fade` rule, same as the HQ drowned quarter) | Warm, full strength |
| Contents | Floating debris: a chair, a sign board, a lamp, kelp cable fronds | Normal interior props |
| Particles | Bubbles rising, slow | None |
| Motion | Slow sway on the debris and cables (2 s loop) | Static |
| Edge | A soft caustic ripple on the ceiling and walls, from the surface above | None |
| Door glyph (closed at HIGH) | A red sealed hatch, as in A.1 | Normal door |

The same Level glyph as the HQ (14 px, corner of the room pin). It shows what the tint shows, so a colour-blind viewer is not left out.

**Drained rooms** (Divert): an air-line round the room, warm lights, dry-stained wall, as in A.1. In the street this is a **dry room inside the flooded zone**, and it is the one place a warm light sits below the water line. The air-line is what makes it legal.

**Level boundary.** Some buildings have a floor that straddles the line. Rule: a room is judged by the **water line against its floor sill**. If the line is above the sill the room is LOWER and drowned. The art tints from the sill, not from the middle of the room. A partial flood is not shown: it is either under or not.

### B.3 Street water, reflections, the gauge

**Street water.**

- The street surface at the bottom of the frame is a **water plane** seen edge-on. At 0.6 BU it is a wet reflective road. At 5 BU it is a canal between the facades.
- Surface texture: soft ripple lines that run **along** the facade, so the surface follows the street. At HIGH the lines are broader and choppier. At FALLING the lines point toward the dam end of the street (the flow direction).
- Debris on the surface: cars partly under, a bus on its side, floating signs (the clutter kit from `DESIGN.md` section 4, reused). Floating items ride on the water line, so the line moves with the Head.

**Reflections.**

- The facade above the water line is reflected in the water below it: a mirrored copy, flipped vertically, at 30 % opacity, blurred, with the same ripple distortion as the surface.
- Warm sodium lamps reflect as long warm streaks. This keeps the warm-above, cool-below split visible.
- At LOW the reflection is strong (calm, thin water on dark road). At HIGH the reflection is weak (chop breaks it up). This is another LOW-to-HIGH cue for free.
- Reflections are 2D (a flipped, blurred, masked copy) in a side view, so there is no ray tracing and no cost.

**The gauge in the street view.** The same widget as 0.3. In the street it is mounted on a **lamp post or wall at screen-left**, so it appears as an object in the scene as well as an overlay. A diegetic twin of the HQ dam gauge: a white-tick pole on the street corner with a red line. The overlay version sits top-left.

### B.4 Reuse of `street_r2`

`street_r2` is the approved one-city street. It stays as the base. The Tethys version is a layer stack on top.

| Layer | From `street_r2` | Tethys addition |
|---|---|---|
| Back sky and distant skyline | Reuse as is | Add the dam as a distant warm band at one end (the dam is the temperature border seen from the street). |
| Building facades with floors as rooms | Reuse as is | Water line strip, the LOWER tint, the closed hatch. |
| Street level, cars, kerb | Reuse as is | Replace the road surface with the water plane, and the cars with the partly-submerged clutter. |
| Signs and neon | Reuse as is | Neon below the line goes cool and dim (`water_fade`). Neon above the line stays as authored. |
| Foreground props | Reuse | Add a gauge pole. |

**The Tethys street palette.** `street_r2` carries the full city palette. Tethys uses only the **warm above, cool below** rule from `DESIGN.md`, and adds the abyss-blue and photophore tokens from the identity file. It does not replace the city palette. The dry facade keeps its authored colours, so the street still reads as the one-city street.

### B.5 Frame list for a Tethys street netrun

All rendered from the `street_r2` pipeline, 2560 x 1440. Pins and overlay are separate plates.

| # | Frame | Head step | What it must show |
|---|---|---|---|
| 1 | `street_tethys_low` | LOW | Wet road, ground floor dry, puddle reflections strong, gauge pole at the corner. |
| 2 | `street_tethys_rising` | RISING | The line mid ground floor. Foam at the walls. |
| 3 | `street_tethys_high` | HIGH | Ground floor drowned, line at the 2nd sill, debris afloat, reflection broken by chop. |
| 4 | `street_tethys_falling` | FALLING | Tide mark band, flow lines toward the dam, wet streaks. |
| 5 | `street_tethys_high_closed` | HIGH | Closed LOWER rooms with hatch glyphs, placeholder space for pins. |
| 6 | `street_tethys_drained` | HIGH | One drained room dry inside the flood, with the air-line. |
| 7 | `street_tethys_forecast` | RISING | The forecast ghost outlines on the rooms that will close, with the gauge showing HIGH next. |
| 8 | `street_tethys_hover` | LOW | The hover grade over one branch. |

Frames 1-4 are the same street at four steps and must hold identical exposure.

### B.6 Kit reuse vs new (street)

| Element | Status |
|---|---|
| `street_r2` facades, rooms, cars, signs, sky | **Reuse** |
| Gauge widget, Level glyphs, hatch glyph | **Reuse** from Part A |
| Clutter (cars, lamps, signs, kelp) | **Reuse** from the HQ clutter kit (2D-flattened versions) |
| Water line strip with meniscus and foam | **New** (2D) |
| Facade tint below the line, depth graded | **New** (2D, one shader or a gradient mask) |
| Reflection (flipped, blurred copy) | **New** (2D) |
| Tide mark band | **New**, shared with the HQ decal |
| Gauge pole prop | **New** (small) |
| Drained room air-line | **Reuse** from Part A |

### B.7 Readability risks (street)

| Risk | Cause | Mitigation |
|---|---|---|
| The water line is hidden behind a building that gets cut to the stub | The occlusion rule | The line is a separate full-width strip above the building layer. It never depends on building height. |
| A 46 px room straddles the line | The line crosses it | Judge from the floor sill (B.2). Show the Level glyph, not a half tint. |
| The line merges with the dark street in the 0.14 band | Everything is dark | 2 px white-cyan line plus a meniscus glow at 0.10 over local value. Test on the plate. |
| LOWER tint reads as night | The blue tint is dark | The tint carries a soft caustic on the ceiling and rising bubbles, which night does not have. |
| Reflection clutter hides the room pins | Pins and mirrored lamps compete | Reflection is capped at 30 % and blurred. Pins sit above the line where possible. Check the hover plate. |
| FALLING and RISING share a line height | Close values | Same three cues as the HQ: tide mark, flow lines, chevron on the gauge. |
| Warm neon below the line looks wrong | `water_fade` shifts it, but not enough | Apply the full `water_fade` to every emitter below the line. No exceptions except the drained rooms. |

---

## PART C. TETHYS RAID VIEW

The raid map is the city map. The player defends home-server nodes against corp waves. The Head must show on the **city map** without hiding the defence nodes.

### C.1 How the Head shows on the raid map

The city map already has the Tethys drowned quarter, the dam and the pier city (the approved landmark and quarter). The Head moves the water plane on that map. The raid view is a **high 3/4 view of the whole district**, so the water change is visible as a **shoreline shift** and a **dam state**.

| Head step | Drowned quarter shoreline | Dam | Streets near the dam | Pier city |
|---|---|---|---|---|
| LOW | Pulled back from the dam, more street exposed along the toe canal | Wet face mostly dry, gates shut | Dry | Breakwater dry, skirts clear |
| RISING | The baseline shoreline | One gate in three open | Dry | Baseline |
| HIGH | Pushed past the baseline. The shallowest drowned blocks go fully under, and some near the quarter edge show only their roofs | Water near the crest, spray at the seams | Toe canal fills, apron road awash | Breakwater awash |
| FALLING | Back toward baseline with a tide mark ring round the drowned quarter | All gates open, white water on every spillway | Wet, with flow streaks | Wet with a tide mark |

**The shoreline is the cue.** At raid-map scale the water height itself is invisible. What reads is the **edge**: where water meets dry street. A bright 2-3 px shoreline (same recipe as the street waterline) follows the edge and moves with the Head. In FALLING a second, fainter ring shows where the edge was.

**The gauge on the raid map.** The same widget as 0.3, top-left. Next to it, a **wave counter** is shown if the raid has timed waves. The raid already has its own HUD (the player's raid timer or wave counter), and the gauge must not touch it. Gauge top-left, raid HUD wherever it already sits (see Questions: this needs the raid HUD layout).

**Dam on the raid map.** The dam is the landmark that carries the Head at a distance. Its gauge red line is large enough to read, and the gates are visible as open (white) or shut (dark). Four gates visible in the raid camera frame is the target. Check this against the camera in the frame list.

### C.2 Which defence nodes read as underwater (without inventing which ones)

The brief says not to invent which nodes are affected. Art defines **a look for "underwater" and a look for "dry"**, and a **binding point**: each defence node carries a `level` field (UPPER or LOWER), and the art reads that field. Which nodes get which Level is a design question (Q below).

What the art does define:

| State | Look of a defence node pin | Look of the node's lot on the map |
|---|---|---|
| UPPER (dry) | Normal pin, warm base glow, Level glyph UPPER | The surrounding lot is dry, normal |
| LOWER, Head open (LOW / RISING / FALLING) | Pin with the LOWER glyph, a thin abyss-blue outline | A shallow water sheen on the lot |
| LOWER, Head closed or flooded (HIGH) | Pin dimmed to 50 %, abyss-blue tint over the pin, a waterline across the pin at its base, LOWER glyph with the hatch bar | The lot is submerged: water plane over it, rooftop only |
| Drained (if the design allows Divert on the raid map) | Pin at full strength with the white air-line | A dry pocket in the flooded lot |

**Rule for a flooded defence node.** It must remain **selectable and legible**. A defender who cannot read a node during a raid loses the game for art reasons. So "underwater" is shown by tint, waterline and glyph, never by hiding or darkening below the value band. Floor for a flooded pin: 0.25 luma over local value (higher than the 0.10 used for waterlines, because a pin is an input target).

**The map layer for the water.** The flooded lot is drawn as a **translucent water sheet** over the lot, below the pin layer and above the building layer. The pin is never under the water sheet in z-order, so the water cannot hide it. The sheet only tints the lot and the facade behind the pin.

**Enemy wave read.** Corp waves come across the city map. The Head changes how a wave looks only if the design says it does (the draft's HQ rules are netrun-only). The art leaves enemy markers unchanged. Wave units crossing flooded ground get a small wake ring (2 px) as a free flavour touch, but that is optional and does not carry rules information.

### C.3 Frame list for the raid view

Rendered from the city map camera pipeline, 2560 x 1440. The overlay (pins, gauge, raid HUD) is a separate plate.

| # | Frame | Head step | What it must show |
|---|---|---|---|
| 1 | `raid_tethys_low` | LOW | Shoreline pulled back, dam gates mostly shut, UPPER and LOWER pins in open state. |
| 2 | `raid_tethys_rising` | RISING | The baseline map. Control frame. |
| 3 | `raid_tethys_high` | HIGH | Shoreline pushed out, shallow blocks to rooftop, flooded LOWER pins dimmed with waterline. |
| 4 | `raid_tethys_falling` | FALLING | Tide ring, all gates open, flow streaks. |
| 5 | `raid_tethys_high_pins` | HIGH | Close crop of a flooded lot at map zoom, to prove a flooded pin is legible. |
| 6 | `raid_tethys_wave_cross` | HIGH | A wave crossing flooded ground, to check marker legibility over water. |
| 7 | `raid_tethys_dam_state` | HIGH | The dam as a map landmark: gates, red line, spray. |

Frames 1-4 hold identical exposure.

### C.4 Kit reuse vs new (raid)

| Element | Status |
|---|---|
| City map render, drowned quarter, dam, pier city | **Reuse** (approved) |
| Water plane parameters per Head step | **Reuse** from Part A |
| Gauge widget, Level glyph, hatch glyph, air-line | **Reuse** from Part A |
| Shoreline line (bright edge of the water on the map) | **New** (a 2D edge pass over the water mask) |
| Tide ring (the faint second shoreline in FALLING) | **New** (same pass) |
| Flooded lot water sheet | **New** (2D translucent layer per defence-node lot) |
| Pin flooded state (dim, tint, waterline) | **New** (2D pin variant) |
| Wave wake ring | **New**, optional |

### C.5 Readability risks (raid)

| Risk | Cause | Mitigation |
|---|---|---|
| The Head change is invisible at map scale | The water plane moves a few BU on a very wide map | The shoreline edge pass and the dam gates carry it. Do not rely on plane height. |
| A flooded defence pin becomes unreadable | Tint and dim stack into the value band | 0.25 luma floor for pins. Water sheet is below the pin in z-order. |
| Raid HUD collides with the gauge | Two top-left widgets | Needs the raid HUD layout (Question). Fallback: gauge at top-right. |
| Waves look the same over water and land | Marker colours are fixed | The wake ring on water, and the water sheet tint behind the marker. |
| Many nodes are LOWER at once and the map goes uniformly blue | Design decides the Level mix | Cap how much of the map tints at once in the art (water sheet opacity 35 % at most). Raise it with the design session (Question). |
| Shoreline and the existing dam shoreline double up | Two bright edges | The shoreline pass excludes the dam wet face, which already has its own line. |
| FALLING vs RISING on the raid map | Same plane height ranges | The tide ring and open gates, as elsewhere. |

---

## Cross-part summary

| Item | Part A (HQ) | Part B (Street) | Part C (Raid) |
|---|---|---|---|
| Camera | 3/4 orbit, descent per act | Flat side view | High 3/4 over the city map |
| Water cue | Plane height + breakwater + caustics | Horizontal line across facades | Shoreline edge + dam gates |
| Gauge | Top-left overlay + dam twin | Top-left overlay + pole twin | Top-left overlay (check raid HUD) |
| LOWER look | Dimmed and tinted room, closed hatch | Tinted floor below the line | Dimmed pin, water sheet over the lot |
| Level glyph | UPPER / LOWER on pins | Same | Same |
| Reuse | High (approved HQ) | High (`street_r2`) | High (city map) |
| Main new work | Tide mark decal, hatch, gauge, breakwater awash | Water line strip, tint, reflection | Shoreline pass, water sheet, pin variants |
| Biggest risk | LOW vs RISING at overview; FALLING vs RISING | Line behind cut buildings; 46 px rooms | Invisible change at map scale; flooded pin legibility |

**Shared widgets to build once:** the tide gauge, the Level glyph set (UPPER, LOWER, awash, closed, drained), the closed hatch glyph, the air-line, the tide mark band. All three parts use them.

---

## Questions for the design session

1. **Water heights.** Are LOW +0.6, RISING +2.5, HIGH +5.0 and FALLING +3.2 BU acceptable as art values, given that the rules draft only names the four steps? Changing them changes only parameters.
2. **Does FALLING need to look different from RISING in the rules, or only in the art?** The art separates them with the tide mark, open gates and a gauge chevron. If the rules treat them the same, the art could merge them.
3. **Does the Head step show in the street netrun on a different clock?** Does it advance on completed rooms, as in the HQ draft, or on something else? Art needs the clock only for the tick dots on the gauge.
4. **Floor height for the street.** How many floors does the street view show, and does the water line need to land on exact floor boundaries, or can it sit mid-floor with the "judged from the sill" rule in B.2?
5. **Which street rooms are LOWER?** Is Level assigned per room (a data field) or by floor number (every floor under the line)? The art assumes the water line decides the look, and the Level field decides the rules.
6. **Which raid defence nodes are UPPER or LOWER?** The art has a look for each but does not choose. Is Level a per-node field set by the designer, derived from district position, or randomised per raid? How much of the map may be LOWER at once?
7. **Does the Head advance during a raid?** If so, on what clock (per wave, per timer)? Art needs the clock to place the tick dots and to know whether the shoreline animates during play.
8. **Raid HUD layout.** Where do the raid timer and wave counter sit? The gauge goes top-left unless the raid HUD already uses that corner.
9. **Do enemy waves change when the Head changes?** The art leaves wave markers alone. If waves are slowed or sped by water, art needs a marker state for it (the optional wake ring is the hook).
10. **Closed vs drowned vs sealed.** The art shows a closed LOWER room at HIGH as "drowned with a sealed hatch". Does the design want a separate look for "closed by rule" and "closed by an enemy"? Only one is drawn here.
11. **Drained rooms on the street and raid maps.** The draft's Divert exists in the HQ netrun. Does it exist in street netruns and raids? If not, the air-line look is HQ only.
12. **Head forecast visibility.** Is the full forecast (next 3) always shown, or only when the player holds Tide Tables? The art draws the gauge with the next 3 by default, and the ghost outline on future-closing nodes only with the Exploit. Confirm.
13. **Which Head step is the safe state in each mode?** The HQ draft calls LOW the safe window for the stair. If the street and raid modes invert that (HIGH is the safe window), the colour of the gauge fill and the "danger" cues should flip with it.
14. **Occlusion for towers that stand out of the water.** `DESIGN.md` open item 2 still stands. Do the netrun cameras ever go to the sea side or lower pitch, and should the occlusion rule extend to the towers above the water?
15. **Lock failure look.** The draft's over-limit outcome sets the Head to HIGH at entry to layer 4. Should the art show the failed lock as a persistent scene state through Act III (a damaged, leaking gate), or only for the transition?