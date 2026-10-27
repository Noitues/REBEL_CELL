# Tide raid, direction B "ctOS Profiler"

**Thesis:** the city stays night-noir and the raid is a hacked surveillance feed laid on the buildings: data-packet trains run in conduits, every threatened Site pops a profiler tag (glyph + %), and every outcome is a mark on the map, never a panel.

Frames are composites over the real Solace plates (`city_noraid_nonet.png`, regraded, zoomed 1.7x onto the territory) with every mark placed from the coords JSON (site anchors = the link-polyline tips, HOME and HQ from the same). Rebuild: `python scripts/build_frames.py [frame...]` then `python scripts/post.py` (strips, CVD sims, sheet.jpg). Scenarios: default (draw, plan, forecast, response, playout impact, aftermath, hq_step), decay (decay), lost (HOME hit, CITY LOST).

## Files
- Beats: `decay, draw, plan, forecast, response, playout_impact, playout_home, aftermath, hq_step`.png; `city_lost.png`; `all_panels_removed.png`; `sheet.jpg`.
- `strips/<frame>_320.png` and `strips/<frame>_blur4_1920.png`; `cvd/{forecast,playout_impact,playout_home}_{deutan,tritan}.png` (Machado 2009, severity 1.0, linear RGB).
- `scripts/`: `ctos_common.py` (camera, geometry, palette, glyphs, grade), `ctos_scene.py` (infection, conduits, tags, chips, HUD), `build_frames.py`, `post.py`.

## Research (web search, plus knowledge; what I take / avoid)
- **Watch Dogs / Watch Dogs 2 ctOS profiler** (wiki, Prima guide, noobfeed): tags hover over the target on a tether, colour-coded cursors and info bars (green to red for severity). Take: the tether-and-tag anchoring, the colour as threat code, the scan sweep revealing the world. Avoid: the info box as a paragraph of profile text (we show glyph + %, nothing else).
- **Deus Ex HR augmented HUD** (wiki): sight cones and last-known marks projected on the world. Take: marks that live in the world and outlines that stay thin. Avoid: the warm-gold palette (gold would collide with the amber SITES LOST tier) and the corner radar panel.
- **Cyberpunk 2077 scan / quickhack, Breach Protocol**: scan highlights network devices; targets expose their available hacks. Take: the network drawn as a lattice of sockets between buildings; actions offered at the object (HQ step sockets). Avoid: the RAM/menu overlays.
- **Google Maps 3D / Immersive View, Apple Maps, Waze**: a route is a thick, cased line with a clear origin and destination. Take: thick casing so lines read at the squint, travel-direction beads. Avoid: day grade and POI clutter (A's territory).
- **Cities: Skylines info views**: the city is dimmed and one dataset recoloured. Take: dim the world outside the profiled territory, lift inside. Avoid: whole-map recolour (we keep the buildings).
- **Frostpunk**: the city as a clock. Take: HOME's segmented HP ring, the deck strip with the skull line as a countdown. Avoid: the thermometer panel.
- **Into the Breach**: telegraph every hit before it lands. Take: the forecast shows a number on every threatened Site before the response. Avoid: tile arrows (that is C).
- **Mini Metro**: lines never ambiguous. Take: one lane per beam, fixed offsets so overlapping routes stay separable. Avoid: 45/90 clean-up (it would leave the real streets).
- **Own refs: Mirror's Edge Catalyst / Detroit: Become Human scan mode** (outline-on-geometry, a sweep revealing what is relevant) and **Tron Legacy / Ghost in the Shell holographic datastreams** (packets with distinct head shapes in a conduit). Take: edge-detected cyan wire on the real buildings in the swept area, packet heads with unique silhouettes. Avoid: full-screen wireframe (bible §1.2 rejects the wireframe net, see Departures).

## Medium mapping (ART_BIBLE §1.2) and departures
- World (city, infection, shield flashes): the Godot city plate; Bloom A Necrosis from INFECTED/TAKEN Sites.
- CRT chips: defense chips, profiler tags, HUD plates, HQ step sockets, DEPLOY fan (navy glass, cyan edge, scanlines).
- Vinyl stickers: the hand cards (white die-cut, ink body, one glyph + type pip, no words).
- Grease pencil (D28): DOWN slash, TAKEN cross, red dashed DECAY front, yellow drag line, red "stops nothing" cross; lime focus ring only on the hovered socket.
- Binary bits: card flight, shield impact, HOME hit, INFECTED card flying to the deck strip.
- Corp paper / stamp: only the HOLDS verdict slab (teal), as the one allowed verdict word.
- **Departures (said openly):** (1) a cyan building-edge wire grade over the swept territory; the bible rejects the "wireframe net", so this is an edge accent (thin, only inside the profiled area), not a wireframe city. A fallback is to drop it and keep only the conduits and sockets. (2) Tags are CRT glass with Anton numbers (bible: live numbers are bare Anton; here they sit on a CRT tag). (3) The type-shape heads are new glyphs.

## Palette (hex)
Grid/wire #7FD8E8, CRT cyan #5CE1FF, navy glass #06122B. Beams: D #3DB4FF (orb with 4 rotor ticks), N #FF40D6 (rotated square), E #B58CFF (wedge arrow). Sealed lines: pale #D7E1F5 with hex beads and a letter lock. Tiers: UNTOUCHED/EVADED #BFFFEF, HOLDS #19D3C5, SITES LOST #FFB000, DAMAGED #FF7A1A, BREACHED #FF4433, CITY LOST skull white on plum. Bloom: body #1A0A1E, veins #E8458F, front #FF9AD2. Pencil red #FF1C2C, plan yellow #FFE200, lime #D4FF00 only on the focus ring. Solace HQ #3DFF8B, HOME #FFE200.

## How each beat reads with no text
1. **DECAY**: a plum Necrosis patch spreads over the two Sites that were DOWN, their slash is crossed into TAKEN, two INFECTED cards (plum with an X) fly up to the deck strip, whose pink-rimmed cells grow toward the skull tick.
2. **DRAW**: a cyan scan sweep crosses the city and lights the lines behind it: the network is profiled, packet trains with type heads appear on the known routes, sealed routes arrive as ciphered hex lines with A/B/C locks; two cards fly out of the deck on bit trails.
3. **PLAN**: lifting the D card turns every legal socket on D routes into a blue pulse ring, the other lines dim, a ghost chip with a lime focus ring hovers on the target Site, a yellow pencil line drags card to socket.
4. **FORECAST**: each threatened Site has a profiler tag (hex glyph, % that it is hit, tier bar), a guard that stops a beam turns the tag teal, a chip that stops nothing is crossed in red pencil, HOME wears a 12-pip threat dial.
5. **RESPONSE**: DEPLOY fan (D / N / E heads above the chosen Site, each with a drop arrow in the tier it would give), HOLD and MOVE sockets at HOME, the dial recolours when an option is focused; the hand is dimmed.
6. **PLAYOUT**: (a) the packet head arrives at the D guard: hex shield flash in mint, blue bits crumble; the earlier hit Site is slashed with a burst. (b) the E packet reaches HOME: white ring, orange DAMAGED ring, bits, the HP number drops, an orange tint at the frame edge.
7. **AFTERMATH**: DOWN Sites slashed and ringed with the red dashed DECAY front and a clock, spent chips greyed, the teal HOLDS slab.
8. **HQ STEP**: HOME and each DOWN Site open sockets with a glyph and a Schematics cost (wrench = repair, house+ = patch, flame = cool, locked ones dimmed), tick bottom right ends the turn.
- **CITY LOST**: the Bloom floods the whole territory, the skull glyph with a plum halo, the verdict word under it.
- **All panels removed**: `all_panels_removed.png` is the forecast beat; it has no panel. Text on screen: numbers, "%" and the HUD counters only.

## Squint test (self-critique)
- Forecast, response, impact and CITY LOST read at 320 px and blur 4: amber tags cluster, the blue line, the yellow HOME ring, the white shield burst and the plum flood are all distinct blobs. DECAY reads (plum patch vs teal Solace). HQ STEP and AFTERMATH are weaker: sockets on the left are small, but the HOLDS slab and the tick carry them. Plan reads through the lime pulse and the card in the hand more than the sockets.
- Fixed during the pass: beams were too thin (added a dark casing, 5.6 px core), the infection was a flat bright pink fill (plum body, thin veins, hairline front, darker density), icons were off their streets (anchors moved to link tips), the decay plate camera was shifted 22 px (corrected).

## Colour-blind check
D / N / E differ by head shape (orb with ticks / square / wedge) as well as hue. Under deutan the D blue stays blue-white and N/E collapse toward grey-violet, but the shapes survive. Under tritan the amber tags stay yellow-dominant and the teal shield goes grey-cyan; the shield burst is recognisable by its hex cells, not colour. Tier colours also differ by glyph (shield, drop arrow, number).

## What build would have to change (layout/flow)
1. Drop the PLAN / HQ STEP / AFTERMATH / RESPONSE panels; keep the verdict slab, the HUD counters and the hand.
2. Raid camera: crop-zoom onto the Solace territory (~1.7x) so Sites sit ~100 px apart; all marks need room above each Site.
3. Per-Site tag slot above each pad with forecast percent per Site (needs per-Site hit odds from the forecast model) and a per-beam chance list for sealed routes.
4. A HOME dial of N outcome pips (outcome distribution), plus a segmented HP ring.
5. Response as a fan of D/N/E sockets at the chosen Site and HOLD/MOVE at HOME.
6. HQ step as sockets on HOME and DOWN Sites with costs; no list.
7. Deck strip INFECTED cells and the skull line stay a HUD item; DECAY needs a "cards fly to deck" beat.
8. Shared D28 helper for DOWN/TAKEN marks, hex-shield flash, packet heads for D/N/E, binary bit burst.

## What the Godot look would need
- A cool, deeper-contrast night grade and ~35 % dim outside the profiled territory (a post/light tweak, not a new city); a screen-space edge pass confined to a mask around the network, animatable as the scan sweep.
- Infection: plum-black, thin Voronoi veins, hairline hot front, dying windows (existing Bloom A shader, driven from INFECTED + TAKEN neighbours, not a disk).
- Conduit: a dark cased ribbon with an additive core and instanced packet heads; lane offset per beam.
- Bloom/glow on tags and rings; a vignette and light RGB split already exist in the plates.

## Risks and honest weak points
- The cyan edge wire is the riskiest departure from the bible; if rejected the city is flatter but the marks still read.
- Mockup density: tags overlap on t1_b / t1_c (crowded west end); the real game needs collision rules.
- Sealed routes overlap the known routes on the same streets; the lane offsets help but at forecast the shape heads are small, so type reading relies on the beads and the HQ-end heads.
- The 6b HOME hit uses the lost-scenario plate (red-ish bloom patch already on the map) and an orange wash that may read as too warm; HOLDS slab and HQ step cost glyphs are mockup-level.
- Hunter reticle is drawn but small; the HUNTER fork is barely visible in forecast.
- The Bloom patch in DECAY is bright pink at its rim (hairline front) and may read hotter than the plum-body ruling at the squint.
- Single stills: motion (sweep, packets, creep) is described, not shown.
