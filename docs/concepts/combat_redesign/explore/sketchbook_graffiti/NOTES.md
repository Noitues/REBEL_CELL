# Sketchbook graffiti (G2): player wheel + hand

Files: `style_board.jpg`, `plate_A.png`, `plate_B.png`, `plate_{A,B}_wheel_2x.png`, `plate_{A,B}_hand_2x.png`, `src_snapshot/` (the style code).
Generator: copy of `combat_e10_design/final/src` at `D:/rc_scratch/combat_redesign/sketchbook_graffiti/src`, plus `sg_*.py` (style kit). Same game state (`state_e10.json` f1). Backdrop `room_bio_bare.png` (v3_1).

## The idea
The Cell draws its own board. The tower is **one page torn out of a black book and taped onto the corp's glass**; the cards are pages of the same book. Everything player-owned is paper, ballpoint, chisel marker and highlighter in one hand. Everything else on screen is glass and vector. Ownership reads before colour: it is the only paper on the screen.

How the hand is built (all procedural, `sg_lib.py`): construction lines in ballpoint blue stay visible (circles overshoot, spokes cross the rim), then a chisel/round marker fills each shape with zig-zag strokes that **miss the outline by 1-2 px**; overlapping passes darken; edges pool and fray; a 2-tone hatch of ballpoint gives the shadow side; a light-pink brush stroke is the highlight. Lettering is Permanent Marker with a hand outline and a block drop. Rules text is Ink Free in ballpoint blue, underlined by hand. Tape, staple, doodles (star, spark, arrow, X) are the only decoration.

**A, "page".** One dot-grid page, pink marker wedges, throw-up bubble hub, pink highlighter band under the HP ring, taped to the board; cards are torn graph-paper pages with a perforated spiral edge and a tape strip.
**B, "block".** Graph page, heavier black chisel outlines and a hand-hatched 3D block drop on each wedge, graffiti "shine" strokes, starburst hub, black marker band under the HP ring; cards are ruled index cards with a thick black border, black block titles with pink drop, staple.

## How it meets the plan
- **Family P, one hand.** Tower, slice HP, HP ring, guns, cards, SEND IT, nameplate and the taped YOU strip all share the marker/ballpoint/paper stroke. Pink `#FF3DA8` is the identity ink; paper `#F2EEE4`; ink `#111`; one secondary ink: ballpoint blue `#2C3E9E` (A; B uses grey pencil for construction). No glow on paint. Texture sits 6 px or more from icons and HP blocks; icons stay white silhouettes with ink, 52 px.
- **Line grammar.** L2 painted stroke = gun tracers, hub ring, brace/double lines (L10 is two painted strokes). L7 cross-hatch is drawn by hand: HARM red on the pending HP blocks, slice pips and breaking wedges; SOAK indigo is implemented (pip hatch plus chevron notch) but not exercised in f1. Pink hatch (our hits) is for the enemy HP and is not on this wheel. L8 dotted = FAR trim. **No dashed line in anything I drew.** The tracer idle stub and Brace plate (f2) are not drawn yet.
- **Time grammar (threat trim, T family kept flat and stencil-clean).** HOT: solid HARM with ink keyline, glow, 8 px END notch toward the tower. COLD: thinner, desaturated, one bead. FAR: dotted, two beads. The trim is deliberately the only machine-crisp thing on the page.
- **HP grammar.** 15 blocks in 3 groups of 5 at r 150-157 (groups split at the 30/150/270 spokes, where the tape sits). Lit = GAIN green marker block; lost this END TURN = dark socket plus HARM cross-hatch, solid red edge, 4 px soft glow (the one hot P mass). Slice pips: 2 per slice, same states (lit / harm / soak / mend / gone coded). The white slash is gone. YOU strip uses the same blocks (14 x 21 px, not the plan's 22 x 14: the HUD row is 330 px wide).
- **Colour.** Slice type is the icon only (all wedges pink). Wedge frames carry no colour. Red = enemy hatch, indigo = soak, green = life, pink = ours. Type band on cards is shape-coded (box for TOWER, pill with a wave squiggle for WAVE), not colour-coded. The RAM coin stays NET_CYAN and the loud tab TRACE_VIOLET, stuck on as die-cut stickers.
- **Rings and enemy side** are the unchanged E10 board and HUD (not toned); that includes E10's dashed lane outlines and the W4-W6 arcs, which belong to the enemy/clock streams. The plate shows the style in context, not the finished screen.
- **Ownership read.** Squint test (thumbnails on the style board): the paper disc and the paper cards are the brightest, roughest masses on screen. Greyscale keeps it.
- Content guard: every word and number of the E10 f1 plate is present (BREAKER, card titles/types/rules, costs, x3, +1, YOU, SEND IT, CELL-9 // BREAKER). Nothing new is added.

## Legibility risks
1. **Cards at 0.94 scale, 1x text.** Rules text (18 px hand, 160 px card) is readable but thin; the type tag is 12 px marker. If it fails the 320 px check, enlarge the card or drop the tag text to a glyph.
2. **Red next to red.** The HOT trim (solid red) and the pending HP hatch (red on dark) sit 10 px apart on the rim; they differ by fill (flat vs hatch) and glow, but the hatch is dense at 1x. Fix by giving the trim a stencil chevron shape (T) or moving the ring pips outward.
3. **Colour-blind check not run.** Pink `#FF3DA8` is next to HARM `#FF4433` on the same rim; the plan's deutan/protan/tritan dE check is still required (the paper ground helps: pink wedges are on paper, red is on dark sockets and hatching).
4. Small icons (rocket, bandage) at 52 px are fine on the plate but the rocket flame strokes thin out at 320 px.
5. Paper disc is the largest bright shape on a dark board; a dim variant (tinted paper, 85 percent value) may be needed so the rings stay the focus.
6. Open call: hatch run order. I ran the ring clockwise from the 30 degree spoke with the pending run last; the plan says "starts at the needle". Needs the clock designer's needle position.

## Building it in Godot
- **Textures baked, not shaders, for the hand.** Export the paper sheet (dot/graph/ruled, 1024 tileable), the torn-edge mask (6 variants of the disc and the card), the marker-stroke atlas (round, chisel, taper, 12 variants, premultiplied) and a hatch atlas (45/135 degrees, 4 pitches). These are 2D sprites on a `Control`/`Node2D` tower.
- **Per-slice sprites:** wedge fill (pink, 6 variants so no two slices match), ink outline sprite separate from the fill (the 2 px miss is the offset between the two sprites), icon silhouette + ink sprite. States are overlays: red hatch, indigo hatch, X stamp, disabled dark socket. HP blocks: one sprite per state, rotated into the ring (15 + 12 instances).
- **Shader (one, `canvas_item`):** takes the hatch atlas as a mask and the cause colour as a uniform; clips to the shape via a mask texture; optional wobble (UV noise, 0.6 px, 8 fps stepped "boil" for the hand-drawn feel, off in reduce-effects). A second tiny shader does the highlighter (multiply blend).
- **Cards:** one card scene; the art panel, the paper, tape, perforation and doodles are baked per card frame (A and B sets); the title, rules, cost and multiplier are live `Label`s with the Permanent Marker / Ink Free fonts over a baked outline pass (outline = `Label` outline in ink, drop = second `Label` offset). Hover grow and dim use the existing card scripts.
- **Tape, staple, tracers:** tracers are `Line2D` with a brush texture and taper curve (pink over an ink line); tape and staple are sprites. Impact starburst is a 6-frame sprite sheet.
- **Budget:** wheel 1 atlas 2048², hand 1 atlas 2048², no per-frame generation; drips (none used here) would be a particle sheet.
