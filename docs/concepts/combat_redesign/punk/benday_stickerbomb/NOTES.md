# BEN-DAY STICKERBOMB: player wheel and cards (punk concept, ART CALL 52)

Style source: reference 8 (Ben-Day pop comic with stickers). Working copy: `D:/rc_scratch/combat_redesign/punk/benday_stickerbomb/src` (F1 generator copy; new files `bd_lib`, `bd_tower`, `bd_cards`, `bd_ui`, `bd_guns`, `bd_hand`, `bd_render`, `run_bd.py`). F1 was only read, never edited.

Files: `style_board.jpg`, `plate_A.png`, `plate_B.png` (p1_decide, bio cutaway, 1920x1080), `wheel_crop.jpg` (A left, B right, 2x), `hand_crop.jpg` (A top, B bottom, 1x). Only the decide beat is rendered; p2, p2b and p3 were not.

## Idea
The Cell is the sticker slapped on the corp machine. The wheel is a die-cut sticker sheet, each slice is a die-cut sticker (white border, fat ink contour, hard ink drop) in flat pink with Ben-Day shade dots, the rim is a black-and-white checker band, the hub is a button badge with a lightning bolt, and six little patches (star, bolt, X, burst, heart, ring; no letters) sit in the gaps on the rim. The cards keep the F1 black-book layout (cost badge top left, big icon, title, type band, rules text) but are restyled as pop-comic panel stickers.
- **A, teal sticker sheet:** teal Ben-Day field with a sunburst, paper cards with a teal art band and a pink icon disc.
- **B, black polka jacket:** black page with white polka dots (the jacket in the reference), slices printed with a misregistered teal plate (2.8 px), teal hub, pink art band on black polka cards.
- **Cards, title legibility fix:** the title is black Anton on a white banner with a pink offset (about 15:1 contrast), on both variants. Type band is a checker strip with a pink tab and black Anton. Rules text is black Permanent Marker in a white caption box; the number is pink with an ink outline. RAM coin stays cyan, Trace tab stays violet.
- **Same hand everywhere:** SEND IT (pink slab, checker kerb, white Anton with ink), the nameplate and the YOU strip use the same ink, drop and dots.
- **Palette:** ink, pink (ours), paper, plus ONE secondary ink (teal) as the plan allows. No yellow (it is PLAN), no red outside HARM.
- **Needle removed:** the needle draw call is deleted from the renderer. The sector digit "0" at 12 o'clock stays; it is a game element, not the needle.

## Grammar kept
- No dashed lines: dash audit 0 on plate A. Dotted marks appear only as the +2 trim.
- HOT / COLD / FAR trim, ring cells, arrowed outlines and enemy rings are unchanged from F1 (same generator).
- Pending HP loss is cross-hatch in the cause colour on slices, pips, hub ring and the YOU strip. Hatch lines versus round dots: pattern differs by shape, not only by hue.
- Enemy side stays thin enamel on slate glass with no ink, so ink plus dots equals the player. W4-W6 stay as tickets. Same state, numbers and rules text (the draw order and text calls are untouched).
- Brace is a white die-cut plate with a double ink line, checker jaws and two pink rivets (L10 protection). Soak keeps the blue chevron funnel.

## Legibility risks
1. **Halftone ownership.** The plan gave dots to X effects. Here the wheel and cards own Ben-Day (fine, 5-6 px, 45 deg). X must then use the plan's fallback signature (light leaks, speed lines, krackle) or a much coarser dot, or hits will not read as events.
2. **Cross-hatch on dotted pink.** A pending-break slice (red hatch over pink with dots) is busier than F1's. It still reads as red hatch at 1x, but squint and 320 px greyscale were not run for this concept.
3. **Loudness.** Pink slices, white borders and the checker rim are louder than E10, as F1 was. SEND IT stays the brightest object (white text on pink with ink). The lifted card's offset print is still pink.
4. **Teal field versus enemy cool slate.** Hue differs (saturated teal against muted slate), but a colour-blind read was not done (the designer said to ignore it).
5. **Small pieces.** Slice pips are 8 px, patches 14 px, checker cells 3.5 px: patches are decoration and must never be read as marks. A patch over a pip or trim mark was avoided by placement (rim gaps at 30 + 60k deg only).
6. **Card overlap.** In the fan the neighbour covers about 20 px of the right edge; rules text is shifted left 5 px to keep the number visible, and the corner burst patch was moved to the bottom corner.
7. No content check or draw assert was run on these plates; the HUD, board and text calls are F1's, only the player-family art changed.

## Build in Godot
- **Slices and cards** are 9-slice sprites. The die-cut border, ink contour and drop are baked into one sticker texture per shape; the slice is six rotated copies of one wedge sprite (`Polygon2D` or `TextureRect`) with a baked pink fill. The Ben-Day shade is a tiling dot texture, or a shader that compares `fract` of a rotated UV to a radius from a gradient (a ramp, cheap, and it lets damage states change the radius).
- **Page disc, teal or black polka:** one dot-screen shader on a disc quad. Rim checker is a polar-checker shader (rows by radius, cells by angle), so the cell size stays constant.
- **Hub:** badge sprite with the name as a `Label` (Anton) on a parallelogram banner. Patches are six small sprites at fixed angles on the rim.
- **Icons:** the white silhouette plus a 2.2 px ink outline plus a hard 2.6 px drop, as a canvas-item outline shader or baked.
- **HP blocks, pips and hatch:** the F1 rules, an outlined rounded rect plus a hatch shader clipped to the block, colour from the cause.
- **Cards:** one scene (body, art band, banner, type strip, caption box), the art band shader is sunburst plus Ben-Day. Titles are Label nodes with an offset duplicate for the pink drop. Variant B changes only the body fill, band colour and disc colour (a theme resource).
- **Misregistration in B:** a second teal sprite behind each slice offset by (-2.8, 2.4); toggled off by the reduce-effects setting.
- Hover lift: card scale 1.1 and a pink offset duplicate, as in F1.
