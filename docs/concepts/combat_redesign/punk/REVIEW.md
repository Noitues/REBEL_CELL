# Punk-rock spinner concepts: art director review

Saved by the orchestrator from the art director's returned text. Board: `board.jpg`.

I built the board and opened every plate, wheel crop and the key hand crops next to the 10 reference images. Rows are sorted by rank.

Board: D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/board.jpg (2798x3894). Each style gets a row with plate A, plate B and the wheel crop, labelled with rank, reference number and variant names. The last row is the card-title pick (plate_pick plus the 2x hand). The script is saved at D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/make_board.py. To redraw the rank labels, pass them as arguments, e.g. `linocut=#1`.

## What all 7 have in common
- **Needle:** gone in all 7. The half-clipped "0" chip at 12 o'clock is the ring's sector digit. Only jinx_scribble redrew digits 0-5 so they sit unclipped on top, and the winner should take that fix.
- **Card layout:** all 7 keep it (cost badge top-left, big icon, title, type band, rules text). In every concept the title now reads better than F1's pink title.
- **Restyle scope:** only the inner disc, the cards and the UI plates (SEND IT, nameplate, YOU strip) were restyled. The outer schedule rings, trim and tape are still F1 slate. That limits cohesion in every concept, and the next pass should carry each style's line and texture onto the ring borders and the THIS TURN tape.
- **Checks not run:** none of the plates went through the draw asserts or the game-info check, and only p1_decide was rendered.

## Ranking
Criteria: punk read, faithful to its reference, player-vs-corp contrast, wheel info legibility, wheel-card cohesion, title legibility.

1. **TWO-TONE LINOCUT (ref 6), plate A.**
   - The strongest punk read: black ink key block, hot pink printed slightly off register, bone paper, woodcut gouge strokes, scissor-cut halo.
   - Closest to its reference. Pink and black against the lime corp is the cleanest ownership split of the 7.
   - The cards are the same print as the wheel, so cohesion is the best of the set. Titles are black Anton on bone with plain-font rules text, about as legible as the card-title pick.
   - The wheel reads well in A, where the red cross-hatch on pink stands apart from the parallel gouge strokes.
   - Plate B (black slices) weakens the cross-hatch grammar: a pending-loss slice is black with red hatch, a normal slice is black with pink hatch, and they look alike.
2. **SPIDER-PUNK COLLAGE (ref 1), plate A.**
   - The loudest and most "poster" of the set: cut-paper magenta wedges, lightning shards, ransom-note hub, sunburst cards.
   - Very faithful to its reference, and cards and wheel are clearly one family.
   - The yellow lightning and yellow title strips clash with yellow as the plan-mark colour in the ART CALL 51 grammar. The rule in LAYOUT.md also bans a yellow title fill.
   - Louder than F1's squint target. The ransom-letter BREAKER is the weakest text at 1x.
   - Plate B (vinyl hub, cobalt) is calmer, but its orange-and-blue cards drift from the pink wheel.
3. **XEROX FLYER (ref 5), plate A.**
   - The most legible of the 7. Flat magenta blocks over a black key with halftone shading leave the slice state, HP pips and cross-hatch crisp.
   - Titles are black on a white label, and the rules text is in a plain font. The cards are good cohesion: halftone headers with pink icon discs.
   - It reads as a flyer but tamer than ranks 1-2: the photocopy grit and misregistration are subtle at 1x. The cyan misprint fringe sits near the HUD cyan.
   - The ransom-tile hub name is weak at 1x.
4. **BEN-DAY STICKER BOMB (ref 8), plate B.**
   - Clean die-cut pink slice stickers and a checker rim, and the wheel info is crisp.
   - It reads as pop comic more than punk.
   - Plate A's teal cards break cohesion with the pink wheel and sit near the HUD cyan. B's pink cards fix that.
   - Titles are fine. The handwritten rules text is small.
5. **JINX NEON SCRIBBLE (ref 4).**
   - It gets the Arcane neon doodle right, and its sector-digit redraw is the best digit fix of the set.
   - It reads as Arcane neon more than punk.
   - Plate A's violet wedges weaken player ownership and sit near the TRACE purple. Plate B (pink) is better.
   - The doodles add noise around the icons, and the handwritten rules text is the smallest of the 7.
   - The "3" digit sits on the HOLD cell edge.
6. **SPIDER-VERSE MURAL (ref 2).**
   - Nice illustration, but the airbrush gradients and sunset cards read as synthwave or Spider-Verse, not punk.
   - Red hatch on orange-pink is less crisp, so pending loss weakens.
   - The brick mostly shows as mortar lines, and the drips are tiny at 1x.
7. **WPAP FACETED (ref 7).**
   - Faithful facets, but they fight the game information: the pending-loss hatch over facets is muddy, and damaged slices no longer pop.
   - It reads as pop art rather than punk. The teal (A) and orange (B) clash with the HUD cyan and the HOT harm red.
   - The cards are good, and the titles read (white on ink with a pink offset).

## Recommendation
**Pick 1: LINOCUT A as the base.** Still needs:
- Pull the scissor-cut halo, gouge marks and off-register print onto the outer rings, trim and THIS TURN tape.
- Take jinx's sector-digit redraw so "0" is no longer clipped.
- Keep the gouge strokes out of the slice interiors, or limit them to one direction, so the red cross-hatch stays the only crossing hatch.
- Thicken the 1.5 px misregistration a little so it reads at 1x.
- Drop plate B, or give its slices bone paper.
- Run the grey proof, the dash audit and the game-info check, then render p2/p2b/p3.

**Pick 2: SPIDER-PUNK COLLAGE A, toned down (hybrid with the card-title pick).** Still needs:
- Recolour the lightning shards and title strips from yellow to bone or white, so yellow stays the plan colour. Titles become black on a bone strip, following card-title pick A.
- Bring loudness back to F1's squint target: fewer shards, quieter purple halftone ground.
- Replace the ransom-letter hub name with a single clean tile.
- Remeasure loudness and render the other beats.

**Pick 3: hybrid of XEROX A and LINOCUT (safe and legible).** The xerox flat blocks and halftone shading, with the linocut black key line and scissor halo. This gives the best wheel legibility with more punk grit. Still needs:
- Raise the grit and misregistration to read at 1x.
- Drop the cyan fringe, since it sits near the HUD cyan.
- Replace the ransom hub with one clean label.

On titles: card-title pick A (black marker tag, white keyline, pink offset) is already what linocut and xerox do in their own styles. Write it in as the title rule for whichever concept wins. Neutral fill, no yellow or pink letters, and at least a 30 px cap height.

The only file I wrote outside the scratchpad is the board script. Nothing was committed and F1 is untouched.