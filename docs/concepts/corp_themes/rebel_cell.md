DRAFT (Batch API, Sonnet, 2026-10-18; AD review pending)

# REBEL_CELL theme ART plan: "THREE LINES, ONE CLOCK"

Working name only. ART only. Nothing here is built. Rules I need are in the last section.

## 0. Inputs and what I treat as given

| Item | Status | How the art treats it |
|---|---|---|
| Ruling 2026-10-18: light form in street netruns, full form in HQ, one raid hook | Given | Sections A, B, C. |
| Theme premise: three operatives (rooftop, street, sewer), one shared clock, converging on the mainframe | Given | Drawn as three levels that arrive together. |
| HQ landmark (approved, in NOTES.md) | Locked | Section B "Locked" table. Nothing changes there. |
| Sync Strike details (STALL, COUNTERED, detours, parked two, lone throw, operative death) | Proposal in the HQ notes, not in the GDD | Drawn only as conditional states, marked "pending". |
| Attached draft: relay, Counter source, Hack puzzle, Exploit keys, "sign leans to the countered lane" | Mechanics proposals or unapproved art | Not used. |

Two name issues:
- **"DISPATCH"** is the boss and core in the notes. You also call the plan view the DISPATCH view. I use "DISPATCH view" for the plan view only. See Q2.
- **"Sewer"** (your brief) vs **"service tunnel" and "Undercroft"** (approved art). I call the lane SEWER in this plan. It is built as the service tunnel. See Q3.

## 1. Shared theme grammar (used by A, B, C, D)

### 1.1 Three levels = three patterns, not three hues

The route kit already uses lime, orange, white and grey. The HQ accents (pink BREAKER, cyan GHOST, green RIGGER) are allowed only on token frames and a thin edge line. So outside the HQ netrun, levels are told apart by line pattern.

| Level | Pattern (1440p, 2 px stroke; 3 px in DISPATCH view) | HQ lane |
|---|---|---|
| ROOF | Dotted, 2 px dots, 8 px pitch | L, BREAKER (pink edge line in HQ only) |
| STREET | Solid | C, GHOST (cyan edge line in HQ only) |
| SEWER | Dashed, 12 on / 6 off | R, RIGGER (green edge line in HQ only) |

### 1.2 Glyphs

| Glyph | Shape | Size | Used in |
|---|---|---|---|
| TRILINE | Three strokes (dotted, solid, dashed), right ends meeting at a 4 px dot | 24 px (48 px in DISPATCH view) | A tag, C tag, D marker, DISPATCH view title |
| SYNC RING | Ring with 3 pips. Pips align at 12 o'clock when in step | 40 px | DISPATCH view. Restyle of the existing SYNC dial only. |
| GATE | Vertical hairline, world space | 1 BU wide | A, B |
| Switch, shaft, COUNTERED outline | Existing HQ glyphs | - | B (COUNTERED is pending, Q5) |

### 1.3 The BEAT (one cosmetic clock for every form)

- Loop is 4 s at 24 fps, so 96 frames. Frame 96 must equal frame 0. Check: mean abs difference ≤ 1/255.
- All periods divide 96 (96, 48, 32, 24, 16, 12, 8).
- Three packets (small light dashes) travel on the three levels. Each has a different distance and speed. All arrive at the gate on frame 0.
  - Different speeds with the same arrival reads as "same clock".
- At the beat, the gate flashes for 3 frames only. At most one flash per loop. This is safe for flicker.
- The beat is a global shader value computed from time. It reads no game state. See Q4.

### 1.4 Colour and value rules

| Rule | Value |
|---|---|
| Netrun frame median luma | 0.14 target. I propose ±0.015 tolerance. |
| Landmark | About 2× its local background. |
| Light-form motif | Peak ≤ 1.5× local background. It is never the brightest thing in frame. |
| Motif cost to the median | ≤ 0.005. Measure every still with the layer on and off. |
| Cell red | #E8141E for windows and tracers. Tracers at 35-55 % emission. |
| DISPATCH red | The preset value (no hex in the notes). Used for switches, shaft, gate flash. |
| Report per still | Median, % < 0.10, % > 0.85, landmark / local ratio (same table as the notes). |
| Greyscale check | Every still. The three levels must still read by pattern. |

### 1.5 Occlusion rule (global)

The existing camera-rig rule stays. City buildings in the cone are flattened, then ghosted. Theme art is never an occluder. It must also never cover a route room. Three rules:

1. **Authoring placement.** Decor goes only in the far ring, beyond the route volume, and outside every room's screen box plus 10 %.
2. **Runtime.** The rig already passes the target volume (active room front points plus visible route nodes). Any theme instance whose footprint touches the cone, widened by the same 10 % margin, fades to 0. It uses the same 0.4 s ease in-out as buildings.
3. **Proof.** Every still gets a mask pass. Room boxes + 10 % are drawn over the frame. Theme pixels inside them must be 0.

## A. Street netrun: light form

### A.1 What is drawn

| Element | Look | Cost |
|---|---|---|
| Three tracer lines | One per level, on far-ring buildings: roofs along far roof edges, street along far kerb lights, sewer as faint grate and manhole glow at far street level. All run toward the gate. | 3 emissive strips |
| Packets | Three dashes, one per tracer. They arrive at the gate on frame 0 (see 1.3). | 3 quads |
| Gate | Vertical hairline at the far end of the main view axis, behind the route volume. Same side in every REBEL_CELL street netrun, so players learn it. | 1 quad |
| Fist hint | One far window cluster at SEQ 0: about 8 % of lit windows dim red. Uses the existing window shader. | 0 new assets |
| Corp tag (HUD) | TRILINE glyph at 24 px next to the corp name, Cell red at 70 %. Three 4 px pips under it light for 3 frames on the beat. | 1 icon |

No operative tokens appear in the street form. The traces are decor, not the player's squad. See Q1.

### A.2 States

| State | Look | Trigger (needs game data, Q6) |
|---|---|---|
| QUIET | Tracers at 60 %, packets running, gate flashes on frame 0. | Default, between rooms |
| ENGAGED | Packets paused. Tracers dim to 40 %. No beat flash. Decor must not compete with combat. | Room active (combat) |
| CLEARED | One beat with all three packets at the gate, then QUIET resumes. | Node cleared |

### A.3 Motion (96 f)

- Packets: 96 f travel, spawn fade-in on frames 4-12, gate flash on frames 0-2.
- Tracer shimmer: 48 f.
- Fist-hint windows twinkle: ±10 %, per-window phase, period 96 f.

### A.4 Colour, value and occlusion
Rules from 1.4 and 1.5.

The tag glyph is the only A element in the HUD. There is no gauge, which keeps the HUD budget.

### A.5 Stills to render (2560×1440)

| ID | Content | Pass if |
|---|---|---|
| A01 | Loop strip, keys f0, 12, 24, 48, 72, 95 | f95 → f0 seam clean; packets reach the gate together |
| A02 | ENGAGED | Motif ≤ 40 %; median in range |
| A03 | CLEARED at f0 and f3 | Flash ≤ 1.5× local |
| A04 | Layer off / on pair | Median delta ≤ 0.005 |
| A05 | Low camera, orbit extreme, cone mask on | 0 theme pixels in room boxes + 10 % |
| A06 | HUD tag at 1× and 2× | Three levels readable at 24 px |
| A07 | Greyscale | Patterns separate |
| A08 | Sparse district and dense district | Motif holds in both |

## B. HQ netrun: full form

### B.1 Locked (approved, do not change)

| Element | Approved description |
|---|---|
| District | Normal 12 BU street grid. No landmark tower. The red fist is drawn in lit windows. |
| Hero landmark | MAINFRAME v4 red sign: 11 BU wide, about 45 BU tall, on brackets off the shop between the drop and lane 1. It has its own spill. |
| Secondary | Red fist hologram, `fist_s` 20. DISPATCH (TARGET) is in the palm row's building. |
| Section | Side-view cut. Roof lane (L, BREAKER), street lane (C, GHOST), service tunnel (R, RIGGER). |
| Detour spaces | Roof huts above lane L; deeper pit below lane R. |
| Convergence | Kill-switch column plus service shaft joining the three levels to the server floor. |
| Undercroft | Sunken wet service street below the tunnel, with stalls, lanterns, poles and shopfronts. |
| Red sequence | `SEQ` 0 before, 1 blackout, 2 spreading, 3 full. `PULSE` lights the line blocks at the kill switch. Netrun frames use SEQ 2. |
| Accents | Pink, cyan and green on token frames and a thin edge line only. |
| Camera beats | DECISION, OVERVIEW, REVEAL. |
| Value exception | MAINFRAME at 9.4× its background is accepted as a neon-on-dark exception. Section frames sit at about 1.5×. I keep both (Q7). |

### B.2 What the theme adds (new, small)

| Element | Look |
|---|---|
| Beat in world | On frame 0 the three switch lamps in the column flash together for 3 frames. A vertical glow sweep rises up the shaft on frames 0-24. Same grammar as the street gate. |
| Packets | In the DISPATCH view only (B.3). In the live netrun the tokens carry the story. |
| Token idle | Three tokens bob ±1 BU, period 48 f, phase-offset by 16 f. They go in phase at the switch. |
| MAINFRAME sign | Slow breath ±8 % over 96 f, and a scan band moving down the sign once per loop. No lean, no new geometry. |
| Undercroft | Lantern strings sway on 96 f. Puddle reflections shimmer on 48 f. Low fog strata drift on a tileable 96 f noise wrap. |

### B.3 DISPATCH view (new, the plan view)

**What it is.** The OVERVIEW beat (pitch 7, yaw 0, camera locked while open) with a plan overlay. It is not a new scene. The stack in the briefing matches the stack in the world, so the player learns one layout. Roof is on top, street in the middle, sewer below.

| Part | Look and rule |
|---|---|
| Route ribbons | Three 3D ribbons at the room-front plane, drawn only in the gaps between rooms, never across a room face. Patterns from 1.1. The route keeps its lime / orange / white / grey node colours. |
| Step ruler | Hairline above the roof lane. One tick per route layer. |
| Lane tags | At the far left, 220×48 px chips: BREAKER, GHOST, RIGGER, with thin accent frames. |
| Detour branches | Drawn as a hook up (roof huts) or down (pit). Art draws the edge only. Cost is pending. |
| Convergence | From each lane's last room to its switch glyph, then the shaft, then the DISPATCH target marker in DISPATCH red. |
| Overlay | SYNC RING (40 px), three HP / RAM gauge slots (reserved, Q5), legend row. Body text at least 28 px at 1440p. |
| Cards | 70 % black cards only behind text, in the margin bands. No global dim, so the median stays near the 0.134 of the existing overview. |
| Safe zone | Cards go only outside the union of room boxes + 10 %. |
| Column rule | Same-step rooms in all three lanes share one x column (±1 BU). This is an art preset fix on the room positions. |

### B.4 States

| State | Look |
|---|---|
| PLAN (pre-run) | All route nodes in the kit's unread look. Ribbons at 60 %. Tokens at start. |
| LIVE | Cleared segments 100 %, current marker, unread 40 %. States are inherited from the route-map kit. |
| HOVER | Hovered lane 100 %, others 35 %. Rule note card in the margin (as H_hover). |
| IN STEP | SYNC RING pips aligned. |
| OUT OF STEP | Pips offset, lagging ruler column lit. No extra colour until the rule is ruled (Q4). |
| SWITCH READY | Three switch glyphs lit on the beat. |
| THROWN | All three solid. `PULSE` on the line blocks. SEQ 3. |
| SHOWDOWN | Two tokens parked at switches, one into the shaft (as H_showdown). |
| LANE DARK, COUNTERED, STALL | **Pending.** Hooks reserved, not designed. Q5. |

### B.5 Motion (96 f)

- DISPATCH view: three packets run on the three ribbons from each lane's current room to the switch column and arrive together at f0.
  - The switch glyphs flash for 3 frames.
  - The shaft sweep follows on f0-24.
  - In HOVER only the hovered lane's packet plays.
- `PULSE` envelope: 24 f total (attack 4, hold 4, decay 16). It fires once per loop in THROWN.
- The red sequence stays static per still. The window twinkle is ±10 % on 96 f.
- Camera: locked in loops.

### B.6 Occlusion
- Global rule 1.5 plus the cone rule from the notes. In DISPATCH view every route node is in the target volume.
- The sign, hologram, packets, ribbons and cards are never occluders. None may sit inside a room box + 10 %.
- Undercroft props stay out from in front of any room (already an approved rule). Cable bundles on poles get a mask check.

### B.7 Stills to render (2560×1440)

| ID | Content | Pass if |
|---|---|---|
| B01 | DISPATCH view PLAN | Three patterns read in greyscale; mask pass clean |
| B02 | DISPATCH view HOVER | Others at 35 %; note card in the margin |
| B03 | DISPATCH view LIVE, out of step | Lagging column readable |
| B04 | DISPATCH view in step, switches ready: f0, f12, f48 | Sweep reads as one motion |
| B05 | DISPATCH loop strip, 8 keys | Seam clean |
| B06 | Overview with beat, SEQ 2 | Median ≥ 0.125 |
| B07 | Decision with beat | Median ≥ 0.125. The old still was 0.118. |
| B08 | Switch THROWN, SEQ 3, pulse f0, f6, f24 | Re-render. The old plate had an unlit floor. |
| B09 | Showdown | Re-render, same reason |
| B10-B13 | Red sequence 1-4 from above | Median in range after the light fix (see risks) |
| B14 | Sewer room: (a) as approved, (b) with a drainage channel | Designer picks (Q3) |
| B15 | HQ loop strip: sign, tokens, lanterns, 8 keys | Seam clean |
| B16 | Value sheet, overlay on / off | Table per 1.4 |
| B17 | Cone mask proof on B01 and B06 | 0 theme pixels in masks |

## C. Raid hook (city / raid map)

### C.1 What is drawn
At a home-server node under a REBEL_CELL raid, three thin approach traces arrive from the raid origin. They use the three patterns from 1.1 and have the same packet grammar as the street form. This mirrors the theme: the corp infiltrates you the way you infiltrate it. The traces are always three and are purely visual. They imply no rule about the raid's makeup.

| Element | Look |
|---|---|
| Approach traces | Three, 2 px, patterned. The ROOF trace is a low arc (≤ 6 BU). The STREET trace runs on the ground. The SEWER trace runs under a thin translucent ground cut. |
| Node decal | Three arrows entering at 120° spacing, each with its pattern, each ending in a pip. |
| Tag | TRILINE 24 px at the node. |
| Gauge | One 0-1 arc, `arrival` (needs a value, Q8). A 3-segment version only if the designer wants three sub-values. |

### C.2 States (assumed raid states, confirm in Q8)

| State | Look |
|---|---|
| WARNING | Traces static at 25 %. Slow pulse (96 f) on the tag. |
| INCOMING | Packets run and arrive together at f0. Arc fills with `arrival`. |
| ACTIVE | Arrows lock on. Ring of marching dashes (shift one pattern period per 96 f). |
| REPELLED | All three pips fade together over 12 f. Single clean flash. Ring dims. |
| BREACHED | Pips lock. The node's own block does a mini-blackout, then a slow red spread (the HQ SEQ look at node scale). |

Pips never show separate outcomes. See Q8.

### C.3 Colour, value and occlusion
- Cell red traces. Active ring peak ≤ 2× the node's halo.
- Frame median target on the raid map is unknown. I assume 0.14 until told otherwise (Q9).
- Occlusion rule on this map:
  - Traces and decals draw under node icons and labels.
  - Traces keep one node-radius clearance from any other node. Inside it they fade to 0.
  - All raid art stays ≤ 2 BU above ground except the thin roof arc.

### C.4 Stills to render

| ID | Content |
|---|---|
| C01 | WARNING |
| C02 | INCOMING at f0, f48, f95 |
| C03 | ACTIVE at f0, f48 |
| C04 | REPELLED at f0, f12, f36 |
| C05 | BREACHED at f0, f48, f95 |
| C06 | Crowded map, two raids near a third node (clearance test) |
| C07 | Tag at 1× and 2× |
| C08 | Greyscale and value sheet |

## D. Grid (city map) layer

Minimal layer. Items 1 and 2 are the proposal. Item 3 is optional.

| # | Element | Look |
|---|---|---|
| 1 | HQ district fist hint | The HQ district uses the window shader at SEQ 0 (about 8 % dim red windows). No new asset. District luma ≤ 1.3× neighbours. |
| 2 | HQ marker | TRILINE glyph plus a small MAINFRAME sign icon. ≤ 2× local. |
| 3 | Selection preview (optional) | On select, three thin patterned tracers run from the map margin to the HQ lot. They play the beat loop. They are off when a raid overlay (C) is on that node, to avoid clutter. |

| State | Look |
|---|---|
| HIDDEN | Plain district. |
| LOCATED | Fist hint plus marker. Window twinkle ±10 %, 96 f. |
| OPEN | Marker ring with one sweep hand on 96 f. |

State mapping is a build-session question (Q9).

Stills: D01 HIDDEN, D02 LOCATED, D03 OPEN, D04 selected with preview, D05 coexistence with a C raid overlay, D06 value sheet.

## E. Kit reuse vs new

| Reuse as is | New |
|---|---|
| Window shader (`SEQ`, `PULSE`), district generator, fist mask v2 | TRILINE glyph set and patterns (3 line styles) |
| Section cut, lane buildings, alley and tunnel rooms | Tracer strip and packet quad, gate line, beat uniform |
| Undercroft kit (floor, stalls, lanterns, strata) | DISPATCH view overlay: 3D ribbons, step ruler, lane tags, safe-zone mask |
| MAINFRAME v4 sign, fist hologram | SYNC RING restyle (3 pips) |
| Occlusion helpers (`downtown.occlusion_state`) | Raid decal set: arrows, pip ring, arrival arc |
| HQ preset accents, route-map kit node states | Grid marker, optional selection preview |
| Bloom and fog settings | Sewer room variant B14(b) |
| Existing H_ plates (reference) | Value script with overlay off pass; cone mask proof tool |

Godot mapping (small):
- One global shader param `theme_beat` (0-1).
- Tracers: one MultiMesh of 4 quads.
- DISPATCH ribbons: three `MeshInstance3D` strips fed by room front points.
- Fade uses the same per-instance target and 0.4 s tween as the occlusion rig.

## F. Risks

| # | Risk | Mitigation |
|---|---|---|
| 1 | Red sequence plates have median 0.010 (fail). Decision plate is 0.118 (< 0.14). | Notes' fix: street lamps on the grid, brighter `win_k` for plain windows in the before and blackout beats. Light, not exposure. B10-B13 depend on it. |
| 2 | H_hover, H_switch and H_showdown were rendered before the floor lighting pass. | Re-render B08, B09 and the hover base. |
| 3 | Landmark ratio is about 1.5× on section frames vs the 2× rule. Sign is 9.4× (exception). | Keep the exception. Ask whether it carries over (Q7). |
| 4 | Accent clash: pink / cyan / green vs route lime / orange. Green RIGGER is close to lime. | Pattern first, hue second. Accents stay on frames and edge lines. Greyscale check on every still. |
| 5 | Decor read as the route in street netruns. | Far ring only, low red, fixed gate, mask proof. Paused in ENGAGED. |
| 6 | Three tracers may suggest three operatives when the player has fewer. | No tokens outside HQ. Ask Q1. |
| 7 | DISPATCH view clutter: 3 lanes × many rooms plus text over a busy overview. | Cards only in margins. 28 px min text. Greyscale and mask checks. |
| 8 | Name clash: DISPATCH view vs DISPATCH boss and core. | Q2. |
| 9 | Sewer lane vs approved service tunnel / sunken street. | B14 options; Q3. |
| 10 | Flicker and loop seams. | One 3-frame flash per loop. Seam test on every loop. |
| 11 | Same-step rooms not aligned across lanes. | Preset fix (±1 BU) before B01. |

## Questions for the build session

| # | Question | Why art needs it |
|---|---|---|
| Q1 | Is Sync Strike (three operatives, shared clock) now the HQ rule or only the theme? How many operatives can run? If fewer than three, do I draw fewer lanes? Should street netruns show operative tokens? | Lane count; whether decor can imply a squad. |
| Q2 | Is "DISPATCH view" the final name, given the DISPATCH boss and core? | UI title text. |
| Q3 | Is lane R a sewer or the approved service tunnel with the Undercroft? | Pick B14(a) or (b). |
| Q4 | What is a "step" in game, and is there any real time? Which game state drives `seq` (0-3), `pulse`, `lane_pos`, `switch_state`, in-step / out-of-step? Should the beat sync to any game event? | The 4 s beat is cosmetic. Mapping is a rule. |
| Q5 | Are STALL, COUNTERED, detour cost, parked support, lone throw and operative death in? Is HP / RAM shared or per operative (three gauge slots vs one)? | Pending states and gauge layout. |
| Q6 | In street netruns, what does the game pass: room active, node cleared, tier, Heat? Should the light form change with any of them? | QUIET, ENGAGED, CLEARED triggers. |
| Q7 | What is the landmark in a street netrun? Does the 9.4× MAINFRAME exception apply in the HQ netrun and the DISPATCH view? | The 2× measure. |
| Q8 | Raid: which states exist? What value can I get (time to contact 0-1)? Does a raid have three parts or outcomes? Where do raids come from? Do REBEL_CELL raids exist at all, given it is the final campaign? | C states, gauge, origin of traces. |
| Q9 | Grid: HQ district discovery states? Does selecting HQ open the DISPATCH view? Is there a layer toggle? What median luma applies to the Grid and the raid map? | D states and value rule. |
| Q10 | DISPATCH view: entry point (Grid, pre-launch, mid-run toggle)? Is it read-only, or do players assign operatives to lanes? | Whether it needs interactive affordances. |
| Q11 | Are pink / cyan / green fixed class accents, and are the route colours (lime / orange / white / grey) final? | Colour lock. |
| Q12 | Is there a reduce-motion setting? What should loops do under it? | Pause behaviour. |
| Q13 | Does the HQ netrun show SEQ 2 (as drawn) or SEQ 3? Does 0.14 apply to the DISPATCH view? | Value targets. |