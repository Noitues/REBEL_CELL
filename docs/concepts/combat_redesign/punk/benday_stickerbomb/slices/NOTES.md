# BEN-DAY STICKERBOMB: per-slice colour and texture pass (designer request 2026-11-01)

Request: each unique slice a different colour and texture, not all the same pink. Designer follow-up: no colour needs to be avoided.
Files: `slice_key.jpg` (each type large, colour, grey, red hatch, grey hatch, Soak hatch), `plate_A.png`, `plate_B.png` (p1_decide, bio cutaway, 1920x1080), `wheel_crop.jpg` (old vs A vs B, 2x). Working copy: `D:/rc_scratch/combat_redesign/punk_slices/benday_stickerbomb/src` (new `bd_slice.py`, patched `bd_tower.py`). Hub, cards, rim, patches, HUD, board, needle removal and ART CALL 51 grammar are unchanged. Dash audit 0 on both plates.

## Slice types
The wheel has four kinds (the state and generator hold exactly these): BURST, SHIELD, TURRET, REPAIR. Slices of one kind match exactly.

| Type | Texture (shaped Ben-Day screen) | A colour | A texture ink | B colour | B texture ink |
|---|---|---|---|---|---|
| BURST | sunburst rays from the icon | #FFD21F sun yellow | #F0820A | #FF8A1F orange | #FFE066 |
| SHIELD | honeycomb, 12 px cells | #2F5CF0 cobalt | #8FB0FF | #22C7E8 aqua | #0A5C86 |
| TURRET | bullseye rings round the icon | #FF3DA8 the Cell's pink | #A80F72 | #FF3DA8 pink | #A80F72 |
| REPAIR | staggered plus-sign dots | #B58CFF lavender | #FFFFFF | #B8F03A acid lime | #3F8A10 |

Texture is clear within about 27 px of the icon so the icon medallion stays calm. The family glue is the same on every type: white die-cut border, fat ink contour and drop, Ben-Day shade dots bottom right (a darker tone of each colour), white gloss slashes, pink hub and checker rim. TURRET keeps the original Cell pink so the weapon slice is the identity colour. A sits on the teal page, B on black polka with the teal misregistration plate under each slice.

## Shifts away from earlier reserved colours
None are reserved now (designer). Noted for the record: yellow (was PLAN) is now BURST in A, blue (was Soak) is SHIELD in A, aqua is near the HUD RAM cyan in B, lavender is near the Trace violet in A, green stays HP pips and ring cells. The Soak chevron and blue Soak hatch still draw in the same blue; on cobalt SHIELD (A) the ink keyline separates them (see the Soak row of the key).

## Red cross-hatch (pending HP loss)
Redrawn as a deterministic cross-hatch at 45 and 135 degrees, pitch 8.2 px, red core 2 px, with an ink keyline 3.3 px wide under it, a red edge ring and an ink-backed red X. The same hatch is used on all four types and both variants (grammar unchanged: red, cross-hatch). The slice colour shows through the mesh, and the clear medallion round the icon keeps the type colour, so a doomed slice still says what it is. Tested on every colour in both variants: it reads on all eight fills. Slightly weakest on pink (turret) because the pink and red are close, saved by the ink keyline; on orange (B burst) the keyline does the same job. No slice colour was changed for the hatch.

## Legibility notes
- Grey proof (key, rows 2 and 4): types separate by value and by texture. Value ladder in A: yellow lightest, lavender, pink, cobalt darkest. Pink and lavender are closest in value, but plus signs versus rings tell them apart. In B, orange and lime are close in value, rays versus plus signs separate them.
- Textures avoid 45 degree lines (rays are radial, honeycomb is 30/90 degrees, rings are curves, plus is 0/90), so only the red hatch is a crossing diagonal mesh.
- Green HP pips keep their ink outline and read on all fills, least on lime (B REPAIR); watch it if the pip green moves.
- Loudness: more colour than the single-pink wheel; icon, pips and trim are unchanged and the white icons keep high contrast on every fill (lowest on lavender and yellow, saved by the 2.2 px ink outline).
- Not run: colour-blind checks (designer said ignore), game-info checks, p2/p2b/p3 beats. Only the decide beat is rendered.

## Build in Godot
Per-type fill and texture are one shader on the wedge sprite with a `kind` uniform (rays: angular stripes, honeycomb: hex distance, rings: radial fract, plus: staggered cross SDF), tint and texture colour from a per-variant palette resource. The hatch is a shader on the slice clipped to the wedge, with an ink keyline pass under the red pass.
