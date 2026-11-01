# WPAP FACETED: punk rock concept for the player wheel and cards (ART CALL 52)

Files: `style_board.jpg`, `plate_A.png`, `plate_B.png`, `wheel_crop.jpg` (A left, B right, 2x), `hand_crop.jpg` (A over B, 1x), `src_snapshot/` (wp_*.py, built on the F1 generator; F1 itself untouched).

## Idea
The Cell stops hand-drawing its board (F1 black book) and cuts it out of flat colour instead: a WPAP poster. The wheel is a poster plate cut into indigo planes. Each slice is a pink wedge sliced by 4 straight lines into flat planes (lit side top-left, one plane in the secondary ink, one glint plane). Icons sit in dark octagon ink seats with a pink misprint offset. Punk comes from the jacket details: chrome pyramid studs in the six gaps, slanted HP blocks, a faceted gem hub with a slanted name band, hard offset drops instead of soft shadows.
- A "Pink Riot": pink + violet planes, teal as the one secondary ink, indigo/teal plate.
- B "Acid Sunburst": pink + violet planes, hot orange as the one secondary ink, aubergine/wine plate.
Cards keep the black-book layout (cost badge top-left, big icon, title, type band, rules text) re-cut in the same planes: chamfered die-cut card, sunburst facet art band, octagon ink seat, title as WHITE Anton on an ink band with a hard pink offset (title legibility fix, about 15:1 contrast), flat type plate (TOWER = secondary ink, WAVE = violet), dark ink Plex Condensed rules text at 19-22 px on cream. SEND IT and the nameplate/YOU strip use the same planes. No needle: it is switched off (`S2.needle` no-op); the THIS TURN tape starts itself.

## Grammar kept (ART CALL 51)
No dashed lines anywhere new. HOT/COLD/FAR time marks are the F1 ones (HOT solid red with a flat halo and END notch, COLD #D9877C one pip, FAR dotted two pips); the HOT glow became a hard-edged halo to keep the "no gradient" rule. Pending HP loss is cross-hatch in the cause colour (red enemy, blue soak, pink ours), on HP blocks, pips and whole broken slices; hatch lines are now exact, even and straight. Arrowed outline (movement), one enamel outline for enemy cells, W4-W6 tickets, HUD text and numbers are untouched board code. Brace = cream L10 double-line clamp plate; soak = blue chevron funnel. Same game data as F1 (state_e10.json, same pips, HP 12->6, guns).

## Legibility risks
1. Pink is also the guns, so the guns' pink tracers must stay thin against the pink slices (they leave from the plate rim, so they read; check in motion).
2. The hatch wash on a broken slice hides the facets by design; the slice then reads as red/blue mesh. Cause colour is still the first read.
3. Secondary ink: teal (A) is close to NET_CYAN HUD edges; orange (B) is close to the HOT harm red/amber. B needs a dE check on the HOT trim next to orange facets; A on the HUD cyan. Colour-blind checks were skipped per ART CALL 52.
4. Slice facets are random per seed: a cut that leaves a thin sliver or puts the glint plane under a pip is possible; the generator rejects slivers under 6 percent but not pip overlap.
5. Plate planes are subtle at 1x (kept dark to hold the tower's value near E10); WPAP reads best on the slices and cards, less on the plate.
6. The hand overlaps by 20 px, so rules text is left-biased and shrunk to fit; the owner mark bottom right is partly covered.
7. "BREAKER" in the hub is 15 px; fine on a plate, small on a phone.

## Building it in Godot
- Wedges, plate, hub, studs, HP/pip blocks, brace plate, trim: `Polygon2D` / `Line2D` nodes with flat `color`; each wedge's facets are 5-8 pre-baked polygons (triangulated convex cells from the 4 cut lines), palette picked from a `Resource` per variant (ramp, secondary ink, glint). Rotation is a single Node2D rotation of the whole wedge group, so facets spin crisply with no shader.
- Outline and hard drop: duplicate polygon offset by (3,4) in aubergine, `Line2D` closed loop for the 2.4 px ink; no blur, no shader.
- Cross-hatch: one `ShaderMaterial` on the wedge/pip polygon (or a tiled hatch texture, repeat on, 45 deg, 6.4 px pitch, tinted by cause colour); it is the only texture.
- Icon seats: octagon `Polygon2D` + the existing glyph sprite with a pink copy offset 1.8 px.
- Studs: 4-triangle `Polygon2D` scene instanced 6 times.
- Cards: one `Control` scene (chamfered `Polygon2D` base, `Polygon2D` rays seeded per card id for the sunburst, `Label` with Anton for the title with a second offset `Label` in pink, `Label` with IBM Plex Sans Condensed for rules). Title and rules are real text, so they localise. Hover lift = scale 1.1 plus offset pink copy.
- Bake cost: the facet cuts here are random per seed; in Godot they should be data (JSON of polygon points per slice) so an artist can tune them.
