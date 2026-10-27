# Tide raid: reference baseline (fresh critic, 2026-10-27)

Purpose: set the bar a REBEL_CELL city-map raid screen must beat (BRIEF_POLISH "Target"). Rubric: each axis /10, with 10 = best
shipped example in the genre. V is against AAA. Readability = squint read, colour-blind safety, clutter control. Motion/feel
and Wordlessness are as defined in the brief.

## Evidence and honesty flags
- Images: official Steam store screenshots, in `D:/rc_scratch/tide_concepts/refs/<game>/`, URLs in `refs/SOURCES.md`.
  Contact sheet: `ref_baseline_sheet.jpg` (4 frames per game, 8 games).
- **Seen as images:** Into the Breach, Mini Metro, Frostpunk, Invisible Inc., Frozen Synapse, Bad North.
- **Frames fetched but not the target screen (scored partly from knowledge):** Watch Dogs 2 (the store frames are open-world
  beauty shots, no ctOS overlay) and Cyberpunk 2077 (store frames show no Breach Protocol or scanner).
- **No images fetched, scored from knowledge only:** Google Maps 3D / Immersive View.
- Motion/feel is never visible in stills: every Motion score is from knowledge of the games' animation, flagged as such.

## Score table

| Reference | S | V | Read | Motion | Wordless |
|---|---|---|---|---|---|
| Into the Breach (enemy-intent turn) | 7 | 6 | **9** | 6 | 7 |
| Watch Dogs 2 (ctOS / DedSec) | 7 | 8 | 5 | 7 | 6 |
| Cyberpunk 2077 (Breach, scanner) | 7 | **9** | 5 | 7 | 4 |
| Google Maps 3D / Immersive View | 3 | **9** | 8 | **8** | 8 |
| Mini Metro | 6 | 5 | **9** | **8** | **9** |
| Frostpunk | **8** | **9** | 6 | 6 | 6 |
| Invisible Inc. | 7 | 7 | 8 | 5 | 6 |
| Frozen Synapse | 7 | 5 | 8 | 7 | 7 |
| Bad North | **8** | 8 | 8 | **8** | **9** |

## Per-reference notes

### Into the Breach (S7 V6 R9 M6 W7)
- **Earns it:** the intent telegraph is the genre's best readability: every enemy attack is an arrow and a red-tinted target
  tile, shown before you commit. A grid of flat-lit tiles, one hue per meaning (blue = yours, red = threat), a clean dark
  frame. Tension comes from the deterministic "you can see exactly what will go wrong" board. 3D-ish isometric props give
  depth without noise.
- **Borrow/beat:** (1) intent is drawn ON the world, from source to target tile, always visible, never behind a hover;
  (2) one threat colour, one friendly colour, one neutral: all else is desaturated; (3) the previewed outcome (damage pips on
  the target) is shown in-place, so the player never does arithmetic. REBEL_CELL must beat it on lighting and material
  (ITB is flat sprites) while keeping its legibility.
- **Weaknesses:** low V (sprite tiles, UI-heavy chrome, text-dense side panels); the board is small and static, so little
  spectacle; red/blue read is mostly hue, weak for deutan without the arrows; animation is brisk but plain.

### Watch Dogs 2 (S7 V8 R5 M7 W6; overlay from knowledge)
- **Earns it:** a real, lit, occluded city (fog over the bridge, towers, depth) with the ctOS layer as glyphs and
  wireframe-ish markers anchored to world objects. The jack-in is the player's power fantasy; objects get hacked "in place"
  so the overlay feels like part of the city.
- **Borrow/beat:** (1) markers pinned to world geometry with depth fade and occlusion; (2) hover-to-reveal context (the
  ping/profiler): much info appears only on focus; (3) photographic city as the base, thin line-art as the layer.
- **Weaknesses:** overlay clutter in dense scenes, icon soup, small text, white/cyan on bright daylight washes out;
  the hacking overlay is a utility, not a composed spectacle; colour carries too much meaning.

### Cyberpunk 2077 Breach Protocol and scanner (S7 V9 R5 W4 M7; from knowledge)
- **Earns it:** AAA lighting, neon and atmosphere; the scanner desaturates the world and tints interactables, a strong
  "mode shift" that makes the layer feel like a different way of seeing. Breach Protocol is a tight green-on-black
  code matrix with a timer: tense, stylish, instantly its own thing.
- **Borrow/beat:** (1) the world-grade shift on entering the hack layer (desaturate, contrast, tint the actionables);
  (2) one saturated accent against a restrained field; (3) type with rhythm: monospaced, tracked, tiny labels as texture.
- **Weaknesses:** scanner is cluttered and text-heavy; Breach is almost pure text/hex (Wordless 4); fine type and thin
  glow fail the squint test; red/green/yellow semantics are poor for colour-blind players; Breach has no map.

### Google Maps 3D / Immersive View (S3 V9 R8 M8 W8; no images fetched, from knowledge)
- **Earns it:** photoreal city with correct occlusion, soft light and fog; the route is a single bold ribbon draped on
  the streets with a halo, the rest of the city is quietly de-emphasised. Camera flights ease like a film dolly. It is
  the benchmark for "a route over a real 3D city reads at a glance".
- **Borrow/beat:** (1) a route ribbon with an outer halo and a bright core that hugs the street, occluded by buildings
  with a faint see-through ghost; (2) de-emphasis by blur/desaturation of everything off-route; (3) eased, parallax
  camera moves that frame the route, not cuts.
- **Weaknesses:** no tension or stakes; no threat grammar; zero spectacle (S3); uniform tone, so no drama; labels are
  text-based for places.

### Mini Metro (S6 V5 R9 M8 W9)
- **Earns it:** pure squint design: flat colour field, thick coloured lines, five shape icons. Meaning is carried by
  shape + colour + position, with a tiny text count. Tension is the mounting pile of waiting shapes and a ring timer
  (pressure with no words). Motion: trains glide and settle with soft easing, lines snap and redraw smoothly, and the
  whole thing feels hand-made. Audio-reactive (from knowledge).
- **Borrow/beat:** (1) pressure shown as a physical quantity (a ring filling, a pile growing) not a number; (2) shape-coded
  identity so colour is never the only channel; (3) smooth eased line redraws that read as intent.
- **Weaknesses:** V is deliberately flat (nowhere near AAA); little depth; no lighting or material.

### Frostpunk (S8 V9 R6 M6 W6)
- **Earns it:** painterly, moody isometric city under snow with a heat-glow palette; the heat-map overlay (frame 4) is
  a real data layer over geometry with warm/cool contrast. Strong light-on-dark composition, fire as the focal point;
  the city reads as a living thing under threat (cold front, storm), conveying stakes through the world.
- **Borrow/beat:** (1) the whole city lit by a single threat/relief colour logic (cold = bad, orange glow = safe);
  (2) a data-overlay mode that extrudes the layer on top of the same geometry (frame 4 style); (3) the approaching
  storm as a horizon-scale, readable front.
- **Weaknesses:** the UI is dense and small-text; overlay colours (red/yellow/cyan on a heat map) are poor for deutan;
  mid-zoom is busy; motion is mostly ambient rather than a choreographed beat.

### Invisible, Inc. (S7 V7 R8 M5 W6)
- **Earns it:** a stylised isometric office with strong value structure: dark ambient, warm pools of light, red vision
  cones and tile outlines as the only saturated elements. Rooms outside vision go dark, so occlusion/fog is drawn into the
  design. White tile outlines for move/targets, red striped zones for guard sight: threat is a shape, not a label.
- **Borrow/beat:** (1) threat zones as hatched/striped shapes, giving a non-hue channel; (2) darken everything not
  in play so lit things pop; (3) outline-on-tile for selectable targets, one consistent line weight.
- **Weaknesses:** animation is functional and slow; the environment is repetitive; the stakes are shown by small icons
  and text.

### Frozen Synapse (S7 V5 R8 M7 W7)
- **Earns it:** plan-then-simulate is exactly the raid loop: you draw paths, then a playout resolves, with a scrub-able
  replay. A restrained blue-on-blue world with glowing emissive lines for shots, bright flare impacts and a clear
  "what will happen" preview line.
- **Borrow/beat:** (1) the planning-to-playout transition as a visible mode change; (2) impact flares: a bloom
  flash plus streak lines make a hit feel earned; (3) a scrub timeline on the playout.
- **Weaknesses:** abstract, bare geometry (V5); a single palette, so threat vs friend relies on hue; no atmosphere.

### Bad North (S8 V8 R8 M8 W9)
- **Earns it:** toy-diorama islands with soft light, long shadows and fog; the incoming longships are seen from far out
  and read by silhouette; the pressure is in the sea itself. Colour is limited (red raiders vs blue defenders), so
  the squint read is strong. Animation (waves, ship approach, buildings burning) sells the moment with no text.
- **Borrow/beat:** (1) the silhouette-first threat: the incoming thing is the biggest dark shape in the frame;
  (2) a soft, desaturated environment with two accent hues only; (3) fire and collapse as the loss language.
- **Weaknesses:** stylised, not AAA-realistic; red/blue has deutan risk (mitigated by silhouettes); lighting is
  low-contrast and flat at times.

## The bar (best score per axis)

| Axis | Best | Held by | What it means |
|---|---|---|---|
| S (spectacle / tension) | **8** | Frostpunk, Bad North | The threat is a world-scale presence; the loss is visible on the map |
| V (visual quality vs AAA) | **9** | Cyberpunk 2077, Google Immersive View, Frostpunk | Real lighting, occlusion, materials, atmosphere |
| Readability | **9** | Into the Breach, Mini Metro | One meaning per colour, shape-coded, intent drawn on the board |
| Motion / feel | **8** | Mini Metro, Bad North, Google Immersive View | Eased, readable, wordless animation |
| Wordlessness | **9** | Mini Metro, Bad North | The state is readable with all text removed |

(No single reference beats 8 on S, so S is the easiest axis to clear; V and Readability are the hard ones because the
best-in-class on each is held by a different game: nobody combines AAA V9 with Readability 9.)

## What "beating it" requires of a city-map raid screen
Beating = a fresh critic scores the plate set **S 9, V 10 (or at least 9 plus the clearest read of any of them),
Readability 10 (at minimum 9 with no axis below the reference)** on this rubric. Concretely:

1. **V >= 9 while R >= 9 at once.** Real Blender-lit city with occlusion, materials, fog and bloom (CP2077 / Google
   level), yet the squint strip shows exactly three things: the beam, the HOME, the defended Sites. Nobody in the
   baseline has both; this is the win condition.
2. **The threat as a physical object, not a UI glyph.** Beams and the Bloom front are lit geometry in the street canyon,
   occluded by buildings with a faint see-through ghost (Google route ribbon), with a silhouette readable at 25% size
   (Bad North). Intent is drawn on the map from source to target (ITB), with the preview damage in place.
3. **Pressure shown as quantity, not numbers** (Mini Metro ring/pile; Frostpunk cold front): a visible HOME integrity
   and a Bloom that creeps in the frame, so S >= 9 without reading text.
4. **Shape + hatch + value, not only hue.** Every state has a non-colour channel (Invisible Inc. hatched zones, Mini
   Metro shapes); deutan and tritan sims must keep every state distinct; one threat accent, one friendly accent.
5. **A world-grade shift on jack-in** (CP2077 scanner / WD2 ctOS): the city desaturates and the actionable things are
   tinted, rather than a UI skin laid over an unchanged city. De-emphasise everything off the route (Google).
6. **Beat impact language.** A playout with flare + streak + screen-space bloom at the HIT and a held aftermath
   (Frozen Synapse), with a visible loss state (Bad North fire). A static plate must show the impact frame at full finish.
7. **Wordlessness test:** strip all text; a naive viewer still states what is attacking, what is defended and what is
   about to be lost. Text, when present, is large, short and typographically final (CP2077 fine-type is the cautionary
   tale: not thin, not tiny).
8. **Motion concepts must match the best (Mini Metro, Bad North, Google):** eased, anticipatory, with holds on the
   impact; each has a reduce-motion variant that keeps the meaning (a hold and a flash instead of a travel).

## Top 5 techniques to beat or borrow
1. **Intent drawn on the world, source to target, with the outcome previewed in place** (Into the Breach).
2. **Route/beam as a lit ribbon hugging the street with a halo, occluded by buildings, off-route city de-emphasised**
   (Google Immersive View, Watch Dogs 2 depth-pinned markers).
3. **World-grade shift when the layer opens: desaturate the city, one saturated accent, tint the actionables**
   (Cyberpunk scanner, Frostpunk heat-map overlay on the same geometry).
4. **Pressure and loss as physical quantity and silhouette, not numbers** (Mini Metro pile/ring, Bad North longships,
   Frostpunk storm front).
5. **Non-hue channel on every state (hatch, shape, outline weight) plus an impact flare/streak with a hold** (Invisible
   Inc. striped sight zones, Mini Metro shapes, Frozen Synapse impact bloom).

## Caveats
- Scores are one critic's judgement on partial evidence (see flags above); the Google and the two hacking-layer scores
  are knowledge-based and should be re-checked against captured frames if the bar becomes contentious.
- Reference games differ in genre; the bar is an axis maximum, not a single game to match.
