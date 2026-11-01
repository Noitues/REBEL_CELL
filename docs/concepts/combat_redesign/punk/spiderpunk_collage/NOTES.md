# Spider-Punk collage: player wheel and hand (ART CALL 52)

Files: `style_board.jpg`, `plate_A.png`, `plate_B.png` (full p1_decide, 1920x1080, bio cutaway), `wheel_crop.jpg` (A and B wheels at 2x), `hand_crop.jpg` (A and B hands at 1x), `src_snapshot/` (sp_*.py on top of the F1 generator; working copy in `D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/src`).

## Idea
The Cell cut its wheel out of a punk poster and pasted it up. Every player object is scissor-cut paper: a white cut edge, a black offset drop, Ben-Day halftone shading, jagged yellow (A) or cobalt (B) lightning shards where the slices meet, newsprint scraps, tape, a safety pin, ransom-note lettering. The corp board stays clean glass and machine hairlines, so ownership reads from material.
- **A POSTER**: black photocopy disc with a spiked rim and purple halftone, magenta wedges with jagged sides, yellow shards, yellow burst hub with a ransom-note BREAKER, safety pins, white-sheet cards (yellow title strip), magenta SEND IT slab.
- **B GIG FLYER**: newsprint disc with xerox halftone, yellow-edged wedges, cobalt shards, hub is a vinyl record with a magenta label, yellow tape, black photocopy cards (white title strip, cobalt type band), yellow SEND IT slab.
- **Cards**: F1 black-book layout kept (cost badge top-left, big icon, title, type band, rules text, Trace tab top-right), restyled. Titles are black Anton on yellow or white paper with a small colour offset print, so they are high contrast (about 15:1, was pink on dark). Rules text is black marker on newsprint, kept left of x=158 so the next card's overlap never cuts it. RAM coin stays cyan, Trace tab stays violet.
- **Needle removed** (not drawn on the schedule ring; the THIS TURN tape starts the ring).

## How it keeps the grammar
Board, rings, HUD, time marks (HOT / COLD / FAR trim), cross-hatch pending HP (red wedges and HP blocks, hatch colour = cause), arrowed outlines for movement, one enamel outline for enemy cells, W4-W6 tickets, brace/soak marks and all numbers and words are the F1 code, unchanged. Zero dashed lines (the F1 dash audit hook is still active; the pins, tape and shards are solid shapes). Slice pips, HP ring and break states are F1 draw calls on top of the new paper.

## Legibility risks
- Loudness: the wheel, hand and SEND IT are very loud against E10; the F1 squint target (0.08 loud share) was not re-measured and will likely be missed. Calming option: drop the purple margin halftone and the speed lines.
- Yellow is now ownership decoration, while PLAN grease pencil is yellow in plan beats and the schedule is orange. I used a warmer print yellow (255,204,0 vs 255,226,0); plan beats (p2, p2b) were not rendered here and need the pencil to keep its ink edge.
- The ransom-note BREAKER is about 11 px; legible at 1x but busy. A's pending-break red hatch on magenta is readable but close in hue.
- Cut jagged wedge sides narrow the gap to about 6 px at the inner end; the shards there are thin.
- Scraps, tape and pins sit only in margins and wedge corners, never on pips or HP blocks.
- Only p1 was rendered; hover, p2, p3 plates and effects overlays were not re-skinned. Colour-blind checks ignored per the designer.

## How it would be built in Godot
- Wedge paper: one Polygon2D per slice (jagged sides are baked into the polygon), a white 2 px outline via a second larger polygon, black drop via an offset copy; halftone as a shader (dot grid rotated 45 deg, radius from a gradient) with a 4 px pitch, lit/shade gradient from the light direction. Pending-break cross-hatch stays the existing shader.
- Shards: 6 pre-cut Polygon2D lightning strips behind the wedges, two palette variants.
- Page: a spiked-disc Polygon2D plus a halftone shader; scraps, tape and pins are small sprites at fixed rim angles.
- Hub: sprite (A burst) with per-letter tiles built from a Label per tile with a random +-7 deg tilt; B record is a disc sprite with a rotating sheen shader, which can spin with the Spin card.
- Cards: a Control scene (sheet polygon, panel with a rays shader, title strip as a StyleBox plus Label in Anton, type band, newsprint rules panel); the panel and strips are authored once and recoloured by palette variant. Fonts: Anton (titles), Permanent Marker (rules).
- Slice icons: the existing silhouettes with a 2 px ink outline and a 3 px offset plate (second sprite).
