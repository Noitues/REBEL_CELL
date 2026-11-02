# Linocut, per-slice colour and texture pass (ART CALL 52 follow-up)

Designer: each slice type gets its own colour and texture; any colour is allowed. Everything else in the concept is unchanged (hub, cards, board, ART CALL 51 grammar, no needle, same game info). Files: `slice_key.jpg`, `plate_A.png`, `plate_B.png`, `wheel_crop.jpg` (old vs A vs B at 2x, colour and grey). Source: `src_snapshot/lc_tower.py` (palettes `PALS[v]['T']`, texture functions `tex_*`, hatch and pip patches), `make_key.py`, `make_wc.py`.

The wheel has four slice types (BURST, TURRET, SHIELD, REPAIR). Same type means same fill and same texture type (the gouges are hand-placed per slice, so they match in kind, not stroke for stroke).

## Palette A (black key plate, pink halo, bone cuts)
| Type | Fill | Texture | Icon |
|---|---|---|---|
| BURST | hot pink #FF2EA0 | GOUGE: slanted chisel lenses, bone highlights (the original linocut look) | black, bone halo |
| TURRET | yellow #FFC818 | PUNCH: round halftone dots on a 45 degree grid, bigger toward the shade side | black, bone halo |
| SHIELD | violet #763EEE | RIPPLE: broken arc cuts running along the rim | black, bone halo |
| REPAIR | mint #3EE296 | PLUS: staggered carved first-aid crosses, axis aligned | black, bone halo |
Texture ink is the black key (#0D0B11) on all four. Hub, halo (pink) and ring are as before.

## Palette B (reverse pull: pink plate, bone halo, black hub)
| Type | Fill | Texture ink |
|---|---|---|
| BURST | black #0D0B11 | pink gouges (original B look), pink icon |
| TURRET | bone #F0E9D6 | black dots, black icon with pink halo |
| SHIELD | blue #2454E8 | bone ripple arcs, bone icon with black halo |
| REPAIR | orange #FF8E14 | black pluses, black icon |
B is the darker, calmer pull; its fills run black, blue, orange, bone.

## Shift away from reserved colours
None avoided, per the designer. Notes on overlaps that were handled by treatment, not by changing colour: green (HP pips) vs mint, yellow vs the plan colour, orange vs harm red (B repair), blue vs the soak colour (B shield).

## Red cross-hatch (pending HP loss)
Tested on every slice colour in both palettes (key sheet row "RED HATCH", and an all-pending wheel). Plain red hatch got lost on yellow, mint, bone and orange (olive or grey wash). Fix, applied to all slices so the grammar is one thing: each hatch stroke now has a black key-block under-line (same stroke, 3.9 px vs 1.9 px red), the dark wash is lighter (0.14 vs 0.28), the red edge and the stencil X are unchanged. The icon keeps its cleared disc in the slice colour, so the slice type still shows while it is pending, and the hatch hides most of the texture (the disc plus the colour of the surviving edge carry the type). Result: red is readable on all 8 slice fills; weakest are B bone and A yellow, where the hatch turns the fill brownish but the lattice stays crisp.

## Legibility notes
- Grey proof (key sheet and wheel_crop bottom row): fill luminance order in A is violet < pink < mint < yellow; in B black < blue < orange < bone. Pink vs mint and orange vs blue are close in grey, but their textures (gouge / plus, ripple / plus) differ clearly, so type reads in grey too. Textures are about 2 px strokes, readable at 1x on the full plate but thin on the small ripple rows; the dots and pluses are the strongest.
- New: a carved black track sits behind each slice's HP pips, so the lit green and harm red pips read on every fill (pale green pips washed out on yellow and mint otherwise).
- Icons keep a halo in a contrast colour, so black icons on violet and bone icons on blue still read.
- The hatch overlays the textures; a pending slice is told apart from a normal one by the red lattice, not by texture.
- Loudness: A is now multi-hue and louder than the pink-only wheel; B is calmer. Not measured with the squint metric. CVD not checked (designer said to ignore it).
- Not re-run: draw asserts and info check beyond the render completing with check=True.

## Godot build
Per type: one fill colour, one baked texture atlas (4 textures, tiled by slice type), a pip-track Polygon2D under the pips, and the hatch shader draws a dark wider stroke below the red one.
