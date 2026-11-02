# WPAP FACETED: per-slice colour and texture pass (ART CALL 52 follow-up)

Designer request: each slice type gets its own colour and texture, not one pink for all. Designer ruling: no colours are reserved or to be avoided.
Files: `slice_key.jpg` (colour, grey, red hatch, soak hatch per type, both palettes), `plate_A.png`, `plate_B.png` (full p1_decide, 1920x1080), `wheel_crop.jpg` (old vs A vs B at 2x), `src_snapshot/` (wp_lib.py palettes, wp_slice.py textures, wp_tower.py wedge and hatch). Hub, cards, rings, HUD, grammar and game data are unchanged.
In slice_key.jpg the wedge crops are rotated upright, so the icons are rotated with them; on the plates they stay upright.

## Slice types (the full set in the state and generator: BURST, SHIELD, TURRET, REPAIR)
Same type = same palette, same texture (facet cuts still differ per sector, as before).

| Type | A Riot Set (mid tone) | B Night Shift (mid tone) | Texture (both) |
|---|---|---|---|
| BURST | orange #FF7A1A, ramp #B0360A #E2500E #FF7A1A #FFA038 #FFCC6E, accent yellow #FFD628, glint #FFF2CE | acid yellow #FFD012, ramp #966800 #DEA000 #FFD012 #FFE854 #FFF6A8, accent orange #FF8418, glint #FFFCE2 | halftone dots, size grows toward the rim (explosion) |
| SHIELD | cobalt #326CFF, ramp #0E1C8A #1C40CE #326CFF #5C9CFF #96C4FF, accent cyan #20D6E8, glint #E2F0FF | cyan #12BAD2, ramp #064868 #087C9C #12BAD2 #54E0EC #A8F6F8, accent blue #2C6EFF, glint #E6FCFC | honeycomb outline |
| TURRET | hot pink #FF3DA8, ramp #6E0C68 #C4148A #FF3DA8 #FF6AC0 #FFA6D6, accent violet #9646FF, glint #FFE2F2 | violet #8A42FF, ramp #381084 #6024C4 #8A42FF #B276FF #D6AAFF, accent pink #FF3DA8, glint #F0E4FF | concentric target rings centred on the icon seat |
| REPAIR | acid green #60D624, ramp #0C6236 #1E9C38 #60D624 #A2EE40 #D4FF7E, accent teal #18CEAA, glint #F0FFD6 | hot pink #FF3DA8, ramp #820E64 #C8168C #FF3DA8 #FF70C0 #FFACD8, accent orange #FF9628, glint #FFE8F4 | staggered plus stitches |

Each slice is still 4 straight cuts into flat planes (5-tone ramp lit top-left, one accent plane, one glint plane). The texture is a value shift of whatever plane it sits on (darker on light planes, lighter on dark planes), so it survives greyscale; the glint plane stays clean.
Textures turn with the wedge (drawn in the wedge's own frame). They sit under the icon seat and the pips, which have their own ink keylines.

Family tie (still one punk set against the clean corp side): the same aubergine ink outline and hard drop on every wedge, the same pink misprint icon seats, the same white-pink light edge, same facet cut language, chrome studs and the faceted pink gem hub. All colours are fully saturated poster inks.
A pairs pink with TURRET (the guns' own colour); B moves pink to REPAIR and gives TURRET violet.

## Cross-hatch on every colour
Changes vs the single-colour version, applied to all slices:
- hatch pitch 6.4 -> 7.6 px, line 1.7 -> 1.8 px;
- every red line gets a 0.6 px aubergine keyline underneath, so red separates from orange, pink and yellow;
- the dark wash under the hatch is per type (A: BURST 0.32, SHIELD 0.26, TURRET 0.30, REPAIR 0.28; B: 0.34, 0.26, 0.30, 0.30) so the type colour still shows through;
- slice colours were not changed for the hatch.
Tested on all 8 slice colours, healthy and broken: the red mesh and its edge line read on all of them, in colour and in grey (the mesh reads as a dark/light grid). Weakest cases: red on orange BURST (A) and on yellow-orange facets (B), saved by the keyline; red on pink TURRET (A) is closer in hue than the others but still reads by the keyline and the edge line.
Soak (blue hatch) on the cobalt SHIELD (A) and on blue-ish planes is the one pairing that loses contrast; the keyline holds it, but a soaked cobalt slice is the least crisp case. If it matters, the fix is a lighter blue for soak on that slice, not a different slice colour.

## Shift away from the earlier palette
The old teal accent (A) and orange accent (B) were secondary inks tied to the plate; now every hue is a slice type. Orange (A BURST, B REPAIR accent) and cyan (A SHIELD accent, B SHIELD) are close to the HOT harm red/amber and NET_CYAN HUD edges; no check was made against them beyond a visual one, as the designer lifted the reserved-colour rule. The A plate's teal edge is close to B's cyan SHIELD, which is why the plate stays dark.

## Legibility notes
- Type read: colour, texture and shape (the icon) all say the type; in grey the four textures (dots, hexes, rings, plus) are clearly different.
- Rings on pink TURRET (A) are the lowest contrast texture at 1x; they read as a target at 2x.
- Broken slices lose most of the texture under the hatch (by design); colour still shows through.
- The pattern is not kept 6 px away from HP pips (the VISUAL_PLAN cap); the pips have their own ink keyline, and the icon seats are clean. Check in motion.
- Colour-blind checks skipped per ART CALL 52.
- Facet cuts are still random per seed, so a glint plane can land under a pip.

## Building it in Godot
Per type, one `Resource` (5 ramp colours, accent, glint, pattern id). The pattern is a tiling texture (or a shader on the wedge `Polygon2D`) in wedge-local UVs: dots with radius by distance, hex lines, rings centred at the icon seat, plus lattice. Colour shift is a multiply/screen blend on the facet colour. Hatch keyline: a second hatch tile in ink under the red one.
