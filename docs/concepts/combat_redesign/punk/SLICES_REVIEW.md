# Per-slice colour pass: art director review

Saved by the orchestrator from the art director's returned text. Board: `slices_board.jpg`.

I built the board and re-ranked the 7 styles. **Top 3: XEROX A, then LINOCUT A, then SPIDER-PUNK COLLAGE A.** The per-slice pass helped every style, but it helped the ones with flat colour fields most.

I opened every slice key and wheel crop, plus the plates for xerox A, linocut A and Ben-Day B. I saw the other plates only at board scale. I did not reopen the 10 reference images this time, so punk read is judged against the ART CALL 52 review.

**Board:** D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/slices_board.jpg (4300x7984). There is one row per style, sorted by rank. Each row has the wheel crop as delivered (old, A, B, and for linocut also grey), the slice key, and the plate of the better variant. Labels give rank, reference number, best variant and a one-line verdict. Script: D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/make_slices_board.py. You can override a variant or rank from the command line, e.g. `linocut=B` or `xerox_flyer=#2`.

**Common to all 7:**
- **Slice types:** all 7 use the same 4 types: BURST, SHIELD, TURRET, REPAIR.
- **Hatch fix:** every style fixed the red hatch with an ink keyline under the red lines. None changed a slice colour for it.
- **Type hidden under the hatch:** on a pending slice the texture disappears, so the type has to come from the coloured ring round the icon (the icon seat). That ring is now the most important part of the slice art.
- **Checks not run:** only the decide beat (p1_decide) was rendered in every style. Nobody re-ran the loudness check (the squint metric), the dash audit or the game-info check.
- **Board edges not restyled:** the outer rings and the THIS TURN tape are still F1 slate everywhere.

## Ranking
Criteria: punk read, slice type at a glance and in grey, cross-hatch on every slice colour, palette cohesion with the cards and against the corp side.

**1. XEROX FLYER, variant A (spot inks on a white sheet).** Up from #3.
- **Slice types:** the clearest of the set. Flat pink, cobalt, yellow and green fields with big, distinct textures (dots, fish scales, checker, plus signs). Each type also has its own grey value (131, 91, 203, 162), so it reads in grey even before texture.
- **Hatch:** every hatched slice keeps a solid coloured ring round the icon, so the type survives under the hatch.
- **Cohesion:** pink BURST matches the cards' pink icon discs, and the white sheet ties the four inks into one printed set against the lime corp.
- **Weak point:** it is still the tamest punk of the top 3, because the grit and misregistration hardly show at 1x.
- **Variant B** (fluoro on black toner) is close, but the lime REPAIR and aqua TURRET drift from the pink cards, and its orange BURST needed a heavy dim to carry the hatch.
- **Still needs:**
  - Take the linocut black key line and scissor-cut halo (the hybrid from last round, now the main route).
  - Push grit and misregistration until they read at 1x.
  - Drop the cyan misprint fringe and replace the ransom-letter hub name with one clean tile.
  - Check the game names in the key (ZERO-DAY, SANDBOX, EXPLOIT, PATCH), which the agent did not verify.
  - Run the squint, dash-audit and game-info checks, and render p2, p2b and p3.

**2. TWO-TONE LINOCUT, variant A (black key plate, pink halo).**
- **Punk read:** still the most punk of the set, and the carved textures (gouge, punch dots, ripple cuts, pluses) read in the grey proof.
- **Slice types:**
  - Pink BURST and mint REPAIR have almost the same grey value, so only texture separates them.
  - The BURST gouge strokes are diagonal lines, close to the red hatch.
- **Hatch:** it reads everywhere thanks to the black under-line. But the hatched slices go muddy: violet turns maroon and yellow turns brown, so the slices look alike and the type rests on the halo alone.
- **Variant B:**
  - Its black BURST still looks like a pending slice.
  - The pink plate floods the wheel and competes with the cards.
- **Still needs:**
  - Make the halo round each icon larger and solid on pending slices.
  - Move pink and mint apart in value, or switch REPAIR to a lighter bone-green.
  - Change the BURST gouge to curved or vertical so it never looks like hatch.
  - Then the board-wide carry: halo, gouges and misregistration onto the rings and tape, and jinx's sector-digit redraw.

**3. SPIDER-PUNK COLLAGE, variant A (Poster).**
- **Poster read:** the loudest and most poster-like.
- **Slice types:** the textures read well (Ben-Day dots, fish scales, target rings, pluses). The lightning was recoloured to bone and the tape made neutral, which settled last round's yellow problem.
- **Hatch:** keyed in ink (deep navy on cobalt) and it reads on all 4.
- **Weak points:**
  - It is still louder than F1's squint target, and the four saturated wedges plus the purple halftone page make it louder than before.
  - Yellow TURRET now sits next to the yellow plan marks.
  - Hatched yellow becomes orange-brown.
  - The ransom-letter BREAKER is still weak at 1x.
- **Variant B** (Gig Flyer) has the weakest hatch case, red on tangerine BURST. Its SHIELD and REPAIR are close in grey (116 and 127).
- **Still needs:** fewer shards, a quieter page, a clean hub name, and a new loudness measurement.

**4. BEN-DAY STICKER BOMB, variant B (black polka page).**
- **Strengths:**
  - The best texture shapes of all 7 (sunburst rays, honeycomb, bullseye rings, plus screen).
  - The most complete testing: red hatch and blue SOAK hatch, both also in grey, on all 8 fills.
  - Pink cards match the pink TURRET.
- **Weak point:** it still reads as pop comic, not punk.
- **Variant A's** teal page breaks cohesion with the cards.
- **Still needs:** a punk direction (rougher die-cut, photocopy grit) if it is to compete. As it is, it is the best source of slice textures to borrow.

**5. JINX NEON SCRIBBLE, variant B (Hot Paint).**
- **Variant B:** the bright paint bodies keep the type colour under the hatch.
- **Variant A:** the dark tinted bodies go muddy olive and maroon when hatched, and the night-wall palette is low-contrast at plate scale.
- **Style:** it still reads as Arcane neon. Removing the doodles helped.
- **Still needs:** a stronger TURRET dot grid at 1x and a fix for the overlap with the HUD cyan. Its digit redraw is still worth taking.

**6. SPIDER-VERSE MURAL, variant A (brick and airbrush).**
- **Textures:** too faint. The rings and scales almost vanish in grey, and the airbrush gradients still read as synthwave.
- **Hatch:** good, but A's yellow TURRET and B's orange BURST rely on the keyline.
- **Still needs:** much bolder texture contrast. It is not a contender.

**7. WPAP FACETED, variant B (Night Shift).**
- **Colour per type:** each slice is cut into several facet colours (BURST is orange, yellow and red), so the one-colour-per-type rule blurs.
- **Hatch:** under it, all four types turn the same flat red and only the icon tells them apart.
- **Variant choice:** B's pink REPAIR ties to the cards better than A's green.
- **Still needs:** one dominant colour per slice and a clear coloured halo round the icon. Not a contender.

## Recommendation
- **Base:** XEROX A with the linocut black key line and scissor halo.
- **Textures:** borrow Ben-Day's texture shapes where xerox's are weaker. TURRET checker could become bullseye rings, but only if they stay bold.
- **Hold back:** keep LINOCUT A as the punk benchmark the hybrid must match.
- **Second option:** SPIDER-PUNK A, toned down.

**Rule for every style:** on a pending slice, the solid coloured ring round the icon is required, because it is the only thing that carries the type under the hatch.

The only file I wrote is the board script, besides the board itself. Preview crops are in D:/rc_tmp/claude/. Nothing is committed.