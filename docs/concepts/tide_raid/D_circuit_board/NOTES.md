# D "Circuit Board" (round 2): Solace Infected Tide raid

**Thesis:** at raid time the corp's night city is revealed as its circuit. The streets are copper traces, Sites are IC chips, HOME is a hand-soldered rebel chip bodged onto the board, and every beam is an oscilloscope pulse on the real streets (sine = D, square = N, sawtooth = E), so type is read by waveform shape as well as hue.

Frames: `frames/01_decay … 10_city_lost`, `11_panels_removed`, plus two extras that solve the sealed-route and HUNTER reveals (`12_sealed_reveal`, `13_hunter_lock`). Squint strips: `squint/*_strip.png` (320 px | 4 px blur at 1920, then shown at 320; the raw `_320.png` and `_blur4.png` are beside them). Colour-blind sims: `colorblind/` (forecast, both playouts, panels-removed; deutan and tritan, Machado 2009). Rebuild: `scripts/` (`python frames.py` then `python post.py`).

All frames are composited in Python (PIL, numpy) over the real Godot plate `city_noraid_nonet.png`, using the coords JSON for the street polylines and Site nodes (one coordinate set, default scenario; the plate's camera is the same in every scenario). The plate is zoomed 1.6x about the territory and re-graded (deeper night, crushed mid-greys, windows kept vivid). Nothing is committed.

## Refs (what I take, what I avoid)
Web search was thin on most of these (results flagged below); the rest is my own knowledge.
- **Macro PCB photography.** Take: copper traces under solder mask with vias and pads, ENIG-gold or tin finish on pads, bundles of parallel traces, 45 degree routing with chamfers, silkscreen outlines of dies. Lighting tip from a PCB forum: shoot at a shallow angle so tented vias and crisp traces catch light, which is why traces here carry a top-lit highlight and a dark relief casing. Avoid: the all-green mask; the city must stay plum night. [pedalpcb thread](https://forum.pedalpcb.com/threads/photo-of-back-of-3-channel-mixer-splitter-pcb.25452/latest), [PCB parts explainer](https://www.luisllamas.es/en/parts-of-a-pcb).
- **Tron (1982/Legacy).** Search returned nothing useful on its light lines (only vehicle design notes); the take is from memory: emissive lines on a black ground, the city mirrored as the circuit world. Take: glow-on-dark traces, light as the only colour. Avoid: a fully abstract grid; ours stays on the real streets.
- **TIS-100 / Shenzhen I/O (Zachtronics).** Search gave only forum chatter: Shenzhen I/O was liked for placing and wiring real-looking components, but needed the manual. Take: components as small legible parts on traces (fuse, jumper, capacitor), signals as simple waveforms. Avoid: manual-dependent legibility; every part here is a pictogram plus a waveform token.
- **Ghost in the Shell (1995).** Search could not confirm net-dive design details (low-quality sources), so this is from memory of the cyber-brain/net shots: a dense real city with a thin, luminous information layer over it. Take: the layer sits on the city, it does not replace it. Avoid: wireframe-only rendering.
- **Deus Ex: Human Revolution hacking.** A node graph with entry, capture steps and a trace risk (pcgamer interview and previews). Take: the idea that every step along a path carries an odds reading, and that a hostile trace "hunts" along one route. Avoid: its text-heavy node cards.
- **Hackers (1995) "City of Text" (own).** The film's ground plane is a circuit board with purple traces and the towers are glass boxes ([scifiinterfaces review](https://scifiinterfaces.com/tag/3d-rendering/)). Take: the circuit as ground plane under the towers, the exact move the designer asked for. Avoid: the text-on-towers clutter.
- **Rez / Tetsuya Mizuguchi (own, from memory).** Pulses and waveforms as the only moving parts, colour-coded enemy types. Take: waveform as identity.
- **Previous rounds (round 1 critic).** Take: Into the Breach style number-on-target, ring-gauge HOME preview, outcome dots on the response chips, plum Voronoi Bloom, the skull for CITY LOST. Avoid: the near-day grade (kept night), beams off the streets (these follow the polylines), and the panel-wall look.

## Medium mapping (ART_BIBLE 1.2 vocabulary)
- Vinyl sticker cards (module 13): hand cards are die-cut white-edge stickers with a component picture and a type waveform badge, no words.
- CRT chips (module 14): the HUD tiles and the four response chips (scanlines, cyan bezel).
- Corp paper stamp: the verdict tag (`DAMAGED`) hangs off HOME with a worn rubber stamp.
- Binary bits and shard bursts (module 16): bits scatter on both playout frames.
- Grease pencil (D28): DOWN = one orange-red wax slash, TAKEN = pink wax X. One helper (`Scene.grease`), as the brief asks for both raid models.
- Glyph atlas: tier badges, wrench, heart, skull, lock, flame, chevrons are drawn as simple bold glyphs.
- **Departures:** the city gets a copper AR layer over the whole board (a new overlay, not in the bible); the type tokens are waveforms (new); HOME is an off-lattice hand-soldered scrap board (new).

## Palette
Copper `#C8723C` / highlight `#FFB070`; tin `#C8D6E0`; chip graphite `#1C1E2A`/`#2E3244`; D blue `#3F8BFF` (sine); N magenta `#FF40D6` (square); E signal yellow `#FFE21A` (sawtooth). Tiers (ruled A-103): UNTOUCHED `#B8FFF2`, HOLDS `#19C9B4`, SITES LOST `#FFB21E`, DAMAGED `#FF6A1A`, BREACHED `#FF2D44`, CITY LOST white-plum skull. Focus halo lime `#C6FF2E` (used nowhere else). Bloom: plum `#1B0B22`, veins `#E04A9A`, hot front `#FFA6D8`. HOME integrity ring cyan-white `#BEF5FF`.

Tier second channel: each tier has its own silhouette and glyph, not only a hue: circle+ring, shield, diamond+broken link, hexagon+cracked heart, spiked star+cracked heart, skull.

## How each beat reads with no text
1. **01 decay.** Two DOWN chips turn black with pink X marks while a plum Voronoi corrosion with a hot hairline front eats the board; a plum INFECTED card flies up to the HUD tally and one card slot is already plum with an X.
2. **02 draw.** The hand fans out from the deck pile at bottom right (two cards still in flight with motion trails). The known beams are drawn dim on their streets as the incoming threat, sealed routes as static.
3. **03 plan.** A fuse card is dragged out of the hand on a dashed wire to the lime drop ring on the chip. A ghost fuse shows on the pad, and the two D beams are already drawn cutting off at that Site, with a "2" for how many it answers. Placed parts (capacitor on the DOWN chip, jumper on the other) are soldered on.
4. **04 forecast.** The beams show where they end: a waveform that runs up to the fuse, a stop bar, then a dashed flat line (the oscilloscope flatline = nothing arrives). Probe tiles on chips carry the tier badge plus a number (HOLDS 2, SITES LOST 1, DAMAGED -4); the HOME ring shows the 4 damage ticks in orange. The logic-analyzer strip lists each beam in firing order, a lane of its waveform, then its outcome badge(s): known = one badge, sealed = static forking to three badges, hunter = static forking to two. Worst case drives the ring.
5. **05 response.** Four CRT chips (DEPLOY / HOLD / MOVE / SACRIFICE) each with three outcome badges; the lime rectangle is the pick. Map keeps the probe on HOME.
6. **06 playout impact.** The D pulse reaches the glass fuse: white flash, glass shards, sparks, bits, ground shockwave in teal; the fuse is blown (dark glass, broken filament) and a teal HOLDS badge floats up. The trace behind it is a dead flatline.
7. **07 playout HOME.** The revealed N (magenta square wave) arrives at the HOME chip: orange shockwave rings, sparks, smoke, bits, a big `-4`, the ring ticks tear off, the HUD HOME tile goes orange.
8. **08 aftermath.** Quiet board: two DOWN chips with orange slashes and decay clock rings (the older one hot and nearly full), blown fuse, scorched HOME, and the DAMAGED stamp tag hung off HOME on a string.
9. **09 hq step.** Action tokens float over the chips they act on, joined by solder tethers: wrench 20 (lime focus on the most urgent DOWN chip), wrench 10, heart repair 25 at HOME, a card+ token, and the chevron to end the turn. No sentences.
10. **10 city lost.** The plum corrosion floods the whole board, black chips with X marks, the corp CPU still lit, a huge white skull with a plum halo, the HUD tally shows more plum cards than cyan.
11. **11 panels removed.** The forecast beat minus the hand, the analyzer strip and the go button: only beams, probes, chips, the HOME ring, sealed header, fork reticles and the HUD. It carries the beam endpoints, the worst-case number and the HOME ring.
12. **12 sealed reveal (extra).** Sealed routes are ciphertext static hugging the street (a lane beside the trace) with a keyed pin header at the corp CPU: three lock tiles A B C. At reveal, tile A unlocks and shows its type waveform, the static on A's street collapses into the yellow sawtooth, B and C stay static. No text, only the lock state and the waveform.
13. **13 hunter lock (extra).** Before: two candidate streets as dotted ghost traces with a reticle on each and a seesaw arrow between them (04). At lock: the reticle tightens and doubles on one street, which lights as its type waveform; the other street goes grey and dotted and its reticle fades.

## What build would have to change (layout and flow)
- A trace/board layer under the raid camera: copper bands on the net link polylines (cased cap-and-join line shader, top-lit), vias at nodes, plus a procedural secondary trace field fading with distance from the territory (cheap: one baked ground texture in the iso lattice, masked by a radial falloff).
- Sites as chip meshes (flat slab + pin rows) in place of the hexes; HOME gets its own off-lattice prefab. State comes from existing site_state.
- Beams as arclength-parameterised ribbons with a lateral waveform function per type (sine, square, saw). Known beams get a stop point = the first matching guard along the path; draw wave until it, a dashed flat after.
- Sealed routes: a noise-ribbon shader on the union of the A/B/C polylines offset to one side, and a 3-pin header prop at the corp CPU with lock tiles; reveal = unlock + collapse of one ribbon's noise into its waveform.
- HUNTER: reticle sprites on both candidate streets, a seesaw arrow, and a lock animation. (The hunter streets are the short linked streets in the plates; if the game's hunter is meant to be a longer street the ghost should follow that.)
- Probe tiles: one per Site that has a non-trivial forecast (tier badge + number), a declutter budget (max about 4), placed with a leader line.
- HOME ring gauge (50 ticks) with preview ticks. Analyzer strip: one lane per beam in firing order; per-beam outcome sets from the existing forecast model (sealed and hunter need their candidate outcomes, not just the worst case).
- Verdict as a tag; no panels are needed for any beat.

## What the Godot look would need
- The grade: deeper night with crushed mid-greys and vivid windows, scoped to the raid camera (the other screens must not inherit it).
- A lattice-aligned ground overlay (traces) that draws over buildings as an AR layer with bloom; copper bloom and a data-traffic particle trail along secondary traces for life.
- Bloom A necrosis shader driven from TAKEN/INFECTED sites with a ground-space Voronoi (already planned) and a mask that dims the trace layer inside it.
- Billboarded probe tiles and a glyph atlas for tier badges; a small decal for the grease marks.

## Risks and honest weak points
- **Dense.** The copper layer is loud. It is what makes it a circuit, but the primary route reads mainly through colour value and casing, and beams (saturated, glowing) win over it only because they are the brightest, most saturated thing on screen. At 320 px the blue beams and the HOME ring still read; the orange net is the first read in the squint strips, though.
- **Copper vs E yellow.** Both live in the orange-yellow family. Under deutan the copper net turns yellow like the E beam; only shape (sawtooth with high amplitude) and glow separate them. A grey or tin net would solve it at the cost of the "copper" ask.
- **The t1 cluster.** K1 and K2 converge on the same two stubs near HOME; waveform lanes keep them apart but it is still the busiest area. The fuse stop bar and the probes are small there.
- **Sealed and hunter.** Better than round 1 (a lock header, static, collapse into a waveform) but the static band is a sparkle ribbon that can read as noise or glitter, and the hunter streets in the plates are short, so the lock reads small. The hunter reticle needs a real animation to sell it.
- **Surface of the city.** The traces are drawn flat on the ground plane and overlap the buildings (an AR layer, no occlusion). Convincing from this camera but not physically grounded.
- **Beat 03/04 route alignment.** Beams follow the plate polylines, so they visit the Site stubs only where I chose (the fuse Site); other Sites are touched implicitly.
- **Static outcome sets.** The forecast outcomes (HOLDS, SITES LOST, DAMAGED, UNTOUCHED) are my own consistent set for the default scenario, not computed by the game.
- **Tritan/deutan.** Tier hues partly collapse (teal to grey, orange to yellow) but every tier has its own silhouette and glyph, and the waveform shapes survive; the numbers also carry. See `colorblind/`.
- **No motion.** All of the pulse travel, spark and noise-collapse beats are stills.
