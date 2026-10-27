# C "War Table": the Infected Tide raid as a tabletop diorama

**Thesis (one line):** the raid is a board game played on a tilt-shift miniature of the Solace territory: enemy moves are thick
Mini Metro lines carrying their own shape, every hit is an Into-the-Breach arrow with a number on a highlighted tile, defences are
vinyl stickers slapped on district tokens, and every outcome is a rubber stamp. Nothing on screen is a sentence.

Frames are 1920x1080 composites over the real Godot city plate (`city_noraid_nonet.png`, raid camera). Every Site, HOME and the
Solace HQ sit on the real node positions from `coords/default_forecast.json`. Rebuild with `python scripts/build.py` then
`python scripts/post.py` (needs PIL, numpy, scipy; plates read from `D:/rc_scratch/tide_concepts/plates`).

## Deliverables
| File | What |
|---|---|
| `01_decay.png` .. `09_hq_step.png` | the eight beats; playout is two frames (`06_playout_impact` shield stop, `07_playout_home` HOME hit) |
| `10_city_lost.png` | CITY LOST: the Bloom floods the board and runs onto the felt, then the skull stamp |
| `11_panels_removed.png` | the PLAN beat with the hand, tray and every table object removed: only marks, glyphs and the HUD |
| `squint/NN_*_squint.png` | per frame: 320 px thumbnail (left) and the same frame blurred 4 px at 1920 scale, then reduced (right) |
| `cvd/04_forecast_*`, `06_*`, `07_*` `_deutan` / `_tritan` | colour-blind simulations (Machado 2009, severity 1.0) |
| `sheet.jpg` | all beats in order with squint strips and the deutan/tritan rows |
| `scripts/` | `wt_lib.py` (geometry, grade, glyphs, bloom), `wt_scene.py` (beams, tokens, arrows, HUD), `wt_frames.py` (the beat states), `build.py`, `post.py`, fonts |

The storyboard state is art-only and invented for the concept (it follows the rules in the brief, not the build's exact numbers):
first raid at HEAT 80, HOME 44/50; DOWN t1_d and t2_intel become TAKEN at DECAY (INFECTED 2, healthy 8); guards D, D on t1_c and N
on t1_b; beams K1 (D), K2 (D), sealed A (E), B (D), C (N) all start at the Solace HQ; A is revealed at PLAN, C by FORECAST.
Outcome: K1 stopped by a guard, K2 downs t1_c, B and C stopped, A (no E guard) hits HOME for -6 = DAMAGED.

## Refs: what I take, what I avoid
I ran web searches; most returned only general descriptions (no teardown-level detail), so where I say "known" the claim is from my
own knowledge of the game, not from a source I opened this pass.

- **Into the Breach** (Subset Games; Game Developer interview, GameSpot and Giant Bomb reviews found by search: attacks are fully
  telegraphed, target and damage are shown before you commit, one screenshot holds the whole board state, no hidden rolls).
  *Take:* the fat arrow onto a highlighted target tile with the damage number on it; the whole board shown at once; the stacked HOME
  bar. *Avoid:* its flat grid; our arrows are drawn to the street geometry and the stopped hit gets a flat T end, not an arrow.
- **Mini Metro** (search: described as cleaner than Vignelli system maps; stations carry circle/triangle/square shapes). *Take:* thick
  flat lines, rounded 0/90/iso-diagonal corners only, parallel lanes where lines share track, shapes riding the line.
  Circle/triangle/square are our D/N/E passenger shapes. *Avoid:* its white paper background; ours is a lit night city.
- **Frostpunk** (search: the temperature display is front and centre and the largest element; Frostpunk 2 overlays heat per district).
  *Take:* one big readable gauge as the city's clock: the HOME ring (50 ticks, one per HP) and the decay clock on DOWN tokens.
  *Avoid:* its dark-and-grim palette and text-heavy law panels.
- **Tilt-shift miniature photography** (search: keep one band sharp, blur grows with distance from it, push saturation and
  contrast so it reads like a toy). *Take:* all three; the focus band is the Solace network. *Avoid:* heavy blur on the marks
  (marks are never blurred) and ghosting.
- **RAF Fighter Command plotting table** (own; Wikipedia "Plotter (RAF)" and IWM Duxford ops-block guide, found by search: counters
  on a table, with a height clip). *Take:* the war-table idea itself: tokens pushed over a big map, the room reads it at a glance.
  *Avoid:* the military tone: ours is paper, stickers and grease pencil.
- **Papers, Please / rubber stamps** (own knowledge; the search returned only stamp-shop pages). *Take:* the slam of a stamp
  on corp paper as the verdict, with ink erosion and a ghost misprint. *Avoid:* APPROVED/DENIED wording; our verdicts are the ruled tiers.
- **Google Maps 3D / Apple Maps 3D / Waze** (own knowledge, not re-researched). *Take:* the camera: a semi-isometric 3D city
  with graded saturation; route ribbons are direction A's job, so C avoids casings with chevrons and avoids POI pins.
- **Cities: Skylines info views** (own knowledge). *Take:* a dimmed city under a saturated overlay. *Avoid:* the whole-map heat
  wash: the Bloom is a bounded necrosis, never a flat disc.
- **Watch Dogs ctOS** (own knowledge). *Avoid:* floating profiler tags, scan sweeps and wireframes: direction B's ground.
- **Two of my own:** the RAF table and rubber-stamp refs above.

## Medium mapping (ART_BIBLE 1.2 / the game's vocabulary)
- **City map:** the 3D city stays cel + ink, regraded as a lit miniature (see Godot look). World.
- **Beams:** Mini Metro lines, ink-outlined, drawn as an overlay on the table plane. They are map marks, not lit.
- **Defence cards:** vinyl sticker cards (module 13): white die-cut border, paper stock by verb (cream GUARD, yellow SHIFT, pink
  JAM), glyph in the existing atlas (shield, curved arrow, zigzag), the beam-type shape in the corner. Slapped on district tokens.
  *Departure:* they are shrunk to 37% and stuck on a physical token.
- **HUD:** the existing CRT chips (module 14), reduced to icon + number: HEAT, HOME, healthy/INFECTED balance scale, RAID.
  *Departure:* the INFECTED/healthy counters become a balance scale that tips; the skull is the tip-over.
- **Verdicts:** rubber stamp on a corp paper tag (module "corp paper / tag stamps"), Anton, ink-eroded.
- **DOWN / TAKEN:** the D28 grease pencil: DOWN = red X on a toppled token with the decay clock; TAKEN = pink ring + X on a plum token.
  One helper (`grease_x`, `grease_circle`) draws both.
- **Impacts:** shard bursts with binary 0/1 bits (module 16) and a hex shield flash; a knocked-over pawn with a grease X.
- **New, not in the vocabulary yet:** district tokens (ziggurat hex stacks, tier = height), round vinyl action discs, the HOME ring
  decal, the foam-board slab and felt table.

## Palette (hex)
| Role | Hex |
|---|---|
| Beam D (circle), N (triangle), E (square) | #3F8CFF, #F6F1E7, #FFD23F |
| UNTOUCHED / EVADED (cool mint) | #BFFBF0 |
| HOLDS (teal) | #1FB8A6 |
| SITES LOST (amber) | #F29A1F |
| DAMAGED (orange) | #FF7A1A |
| BREACHED (HARM red, stamp + grease X) | #FF3B30 |
| Bloom: body, veins, hot front | #1A0B1F, #FF3FA0, #FF96D7 |
| Focus halo (lime, nothing else) | #D4FF00 |
| Cel ink; corp paper; sticker stocks | #1B1424; #F1E8D2; #F2EEE4 / #F2DC7A / #F4C3CF |
| CRT chip, edge | #081224, #5CE1FF |
| Table felt | #0E181B |

N moved off #FF40D6 (ruled "reads against plum") to ivory with a dark centre line, so it never touches the pink Bloom. E is a
signal yellow; amber for tiers is deliberately more orange so the two stay apart.

## How each beat reads with no text
Words used on screen: the card verbs (GUARD, SHIFT, JAM), the four responses, the verdict (DAMAGED, CITY LOST), numbers. No sentences.
1. **DECAY:** the two DOWN tokens' decay clocks are full, a pink grease ring closes on each, the plum Bloom body spreads under them
   with veins and a hot front, and two plum INFECTED cards fly to the balance scale, which tips by one.
2. **DRAW:** the HQ shows its queue as chips (two circles, three sealed envelopes, a crosshair for the hunter); known lines are inked in,
   sealed ones are grey dashed; a vinyl card is dealt into the hand, lifted, with motion ticks.
3. **PLAN:** guards are stickers on tokens (stacked two on t1_c); a lime halo marks the district being worked; a held card hovers with a
   lift shadow; sites on the picked beam's path get ground rings in that beam's hue. A is revealed (yellow squares).
4. **FORECAST:** the ITB board: each beam's arrow lands on a highlighted tile. Teal flat-ended arrow with a shield = stopped. Amber "1" = one
   Site goes down. Orange "-6" onto HOME with the hatched stack on the ring = HOME damage. The hollow "B" is still sealed. The row of
   tiles under the slab is the odds (one tile per outcome, in tier colours).
5. **RESPONSE:** lines fade to 55%; four round vinyl discs on the table (drop, shield-and-pause, four arrows, flame); each has three
   outcome dots in tier colours; the chosen disc is lifted with a lime halo.
6. **PLAYOUT impact:** K1's bead runs to t1_c, the guard stickers flash (hex shield flash, binary bits), the D pawn is knocked off the line
   with a grease X, a teal shield badge settles; the other lines drop to 25%.
7. **PLAYOUT HOME hit:** A's bead (yellow) reaches HOME: red burst, ring segments blown out, a "-6" paper tag, the HUD number turns
   orange; t1_c lies toppled with a red X and spent stickers peeled off beside it.
8. **AFTERMATH:** the verdict stamp DAMAGED (orange, house glyph) on a corp tag; DOWN tokens carry the decay clock at three-quarters; TAKEN tokens sit in plum.
9. **HQ STEP:** three round action tokens placed on the table with white pencil arrows: wrench (carries the clock) to the DOWN token,
   shield to the HOME ring, flag to end; the HQ shows next raid's sealed envelopes.
10. **CITY LOST:** the Bloom floods most of the slab, runs over the foam edge onto the felt, HOME goes dark, the scale falls to the plum
    side, the skull stamp lands on a corp tag.
11. **Panels removed:** `11_panels_removed.png` is PLAN with the hand and the table props gone. The run is playable from marks alone.

## What build would have to change (layout / flow, short spec)
1. Remove the PLAN / FORECAST / RESPONSE / AFTERMATH / HQ STEP panels. The map plus a bottom hand (cards on the table, no frame) is the screen.
2. Site marks are district tokens on the net node, not hexes above the node. (The shipped overlay's Site hex xy and the 3D net node
   differ by up to about 90 px on t1_b; C anchors on the net node, so build must pick one frame for Sites, links and marks.)
3. Beam lines are routed in 0/90/iso-diagonal, lane-offset per beam (12.5 px at 1.85x) from `site_path`; they no longer follow the 3D net poles.
4. Forecast needs per-beam data: outcome tier per beam, the target Site, damage to HOME, and which beams are revealed (A/C solid, B sealed).
5. Response becomes four on-table discs, with the three-dot outcome preview per option.
6. Outcome tier + stamp is a view of the raid result; the decay clock needs "raids until TAKEN" per DOWN Site.
7. HUD: replace the INFECTED/healthy text with the balance scale driven by the two counts.
8. Camera: raid view pulled in about 1.85x on the network with the tilt-shift band centred on it; marks stay unblurred (a separate layer).
9. HOME ring: 50 tick decal (max HP) in the ground plane; a preview range on it.
10. Optional: spent guard stickers persist beside the toppled token until the next raid.

## What the Godot look would need
- A grade pass for the raid camera: saturation about +25%, exposure about 1.5x with a lamp-pool falloff (centre on the network, edges to about 30%).
- Variable tilt-shift on the world layer only (focus band centred on the network, up to about 8 px blur); marks in a layer above it.
- Window lights get a small bloom (the plates' tiny lit windows are what makes it read as a miniature).
- A table background and foam-board slab edge (a simple quad with a bevel and drop shadow), plus the felt/mat grid.
- The Bloom shader: plum body, Voronoi veins, hairline front and dying windows exist as Bloom A; reuse with the ground-plane ellipse metric (ratio 0.643).
- Shaders for ink-eroded stamps and grease-pencil strokes already exist as D28; reuse.
- Plate resolution: at 1.85x the 1920 plate is soft; render the raid camera at 2x for a crisp world layer.

## Risks (honest)
- **Density at the t1 cluster.** Four Sites sit 65 px apart on screen; two stickers, an arrow and a badge on t1_c is tight. It reads at 1920 but
  would not at 1280. Needs a zoom-on-hover or a fanned callout.
- **Tritan:** the D line (cobalt) turns teal in the simulation and looks like the HOLDS teal. Shapes (circle riders) and role (line vs badge) separate them;
  tier colours also collapse in deutan (amber and orange both read yellow; HOLDS reads grey). The shield glyph, flat end and numbers carry it, but
  SITES LOST vs DAMAGED is weak in deutan.
- **Beams are not on the streets**: they float over the city on the Mini Metro grid. That is the concept, but the "real map" feel of direction A is lost.
- **Sealed routes** are drawn with a real path (as the shipped plate does). If the paths must stay secret, the grey dashed lines should become one fog band.
- **Stamp prop and pencil** on the table are decoration; they cost nothing but must not compete with the HUD on a 16:9 layout.
- **Tilt-shift softness** on the world is strong (up to 8 px) and makes the city feel like a model, but the city's own life (traffic, searchlights) will be blurred
  at the top and bottom; the tile band should follow the camera.
- The hunter is the weakest mark: two thin dotted strings and a crosshair pawn. It is visible but not yet beautiful.
- Not done: the actual motion. The slam, topple, bead and drip need an animation pass; here each is one frozen frame.
