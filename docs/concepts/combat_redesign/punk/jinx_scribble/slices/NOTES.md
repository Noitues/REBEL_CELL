# JINX SCRIBBLE: per-slice colour and texture pass (ART CALL 52 follow-up)

Designer request (2026-11-01): each unique slice gets its own colour and texture instead of one colour for all. Designer also said no colour needs avoiding, so nothing is reserved.
Files: `slice_key.jpg`, `plate_A.png`, `plate_B.png` (p1_decide, bio cutaway, 1920x1080), `wheel_crop.jpg` (old vs A vs B at 2x), `src_snapshot/` (`js_slices.py` is the new code, installed after `js_tower.install()`; `sl_*.py` are the render and board scripts). The rest of the concept (hub, cards, SEND IT, nameplate, rings, trim, needle removed, ART CALL 51 grammar, game information) is unchanged.

## Slice types (from the state and generator)
BURST (game name ZERO-DAY, sectors 0 and 4), SHIELD (SANDBOX, sectors 1 and 3), TURRET (EXPLOIT, sector 2), REPAIR (PATCH, sector 5). Same type = same colour and texture.

## Palette and texture
| Type | Texture | A Night wall: neon key and texture / body dark to rim | B Hot paint: paint / highlight / shade |
|---|---|---|---|
| BURST | POW starburst outline with spark ticks and a lightning zig | NEON PINK #FF2E9A / #600A3C to #96125C | HOT ORANGE #FF701A / #FFAA5A / #962806 |
| SHIELD | fish scales (overlapping scallop arcs) | CYAN #28DEFF / #063E60 to #0A6084 | ELECTRIC BLUE #2E70FF / #82AAFF / #0A1E82 |
| TURRET | targeting reticle (two rings, four ticks) plus dot grid | ACID LIME #BEFF32 / #284606 to #42680A | PAINT YELLOW #FAD61C / #FFF082 / #826400 |
| REPAIR | staggered plus crosses | SAFETY ORANGE #FF8A1E / #683004 to #9E4A06 | HOT PINK #FF2E9A / #FF8CCD / #820850 |

- A: the wedge body is a dark tint of the type colour with dry-brush strokes; the texture, the key line, a soft glow and the inner edge are the neon type colour; the misregistered plate is cyan (pink on SHIELD, because its key is cyan).
- B: full-colour paint with the F1 marker fill, light and dark brush strokes; texture and key line are ink; cyan plate offset as before.
- One punk set, one hand: every slice keeps the same ink block drop, chalk construction, doodle vocabulary (margin doodles between slices), highlight chalk strokes, the pink page rim, pink-led hub (B) and the same line weights. The old random doodles inside wedges are gone, the textures replace them. Textures never use parallel runs, so a parallel hatch still only means pending loss.
- Cards, SEND IT, nameplate unchanged (A dark with pink frame, B pink body). In B the pink cards sit with a multi-colour wheel; the pink REPAIR slice and pink hub carry the link.

## Shift away from reserved colours
None kept. ART CALL 51 said slice-type colours are banned; the designer overrides that. The slice colours do now overlap other roles, which is a known cost: B TURRET yellow and A REPAIR orange sit near the plan yellow and the schedule orange; A and B SHIELD cyan sits near the HUD cyan (RAM, NET); B BURST orange is near the schedule orange and HARM red-orange. The cause colour of the hatch (red HARM, blue SOAK) and the texture, not colour alone, keep these apart; the ring cells around the wheel are slate so the confusion is contained to the wheel disc.

## Red cross-hatch legibility
Tested on every type colour in both variants, with all six slices set to pending loss (slice_key, right column). On orange, yellow and pink bodies the plain red hatch got lost, so the hatch treatment changed (slice colours did not): a darker ink underlay hatch (3.0 px, same lines as the red 1.9 px hatch), an ink keyline outside the red edge, and a light ink wash (16 percent) over the slice. The clear disc around the icon stays, tinted by the slice colour, so a pending slice still shows its type colour through the hatch and in the disc. Result: red reads on all eight slice looks; the weakest are B BURST (orange) and A BURST (pink), still clearly crossing lines because of the ink underlay. Texture is mostly hidden under the hatch, colour and the icon disc carry the type there.

## Legibility notes
- Grey proof (slice_key middle column): the four textures stay distinct in grey. A: starburst, scales, rings and dots, plus crosses. B: all four lose colour but read by line pattern; B SHIELD (blue) and B BURST (orange) have near equal grey values, the texture separates them.
- At 1x the textures are small (2 to 3 px lines); the starburst and plus crosses read best, the dot grid on TURRET is the weakest (the reticle rings carry it).
- Green HP pips sit on lime in A: A TURRET is a dark olive body, so the pips and their ink outline stay readable. In B the yellow body also takes the pips fine.
- Checks not run: dash audit, game-info asserts, colour-blind proofs. Only p1_decide is rendered.

## Godot build
Per type: one wedge base sprite per colour and one seamless texture sprite per type (tinted at runtime in A, ink in B), clipped to the wedge; the hatch is the existing tiled shader with an ink underlay pass.
