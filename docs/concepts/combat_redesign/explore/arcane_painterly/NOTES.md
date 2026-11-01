# Arcane painterly (G4) : player family, variants A and B

Plates: `plate_A.png` (ZAUN WALL), `plate_B.png` (GOUACHE & INK), 1920x1080 p1_decide on room_bio_bare (v3_1). Crops 2x: `crop_{A,B}_{wheel,hand,youstrip}_2x.png`. Board: `style_board.jpg`.
Generator: `D:/rc_scratch/combat_redesign/arcane_painterly/src` (copy of final/src + `paint.py`, `tower.py`, `guns.py`, `cards.py`, `chrome.py`, `plate.py`, `board.py`). Run `python plate.py p1 A|B`.

## The idea
Everything the player owns is painted by one hand, brush bristle by brush bristle, and nothing else on the board is. Pink `CELL_PINK` is the identity ink, applied as the same L2 painted frame stroke on the tower slices, hub ring, gun tracers, card borders, SEND IT, nameplate and the YOU strip. The same ink keyline sits 1 px off-register under every pink stroke, and every edge is hand-cut (roughened, max ~1.3 px). The doodle layer (Jinx): thin neon-marker stars, bolt, spiral, heart, crown, cross, in the dead corners of the wedges (never within 6 px of an icon or HP segment).

- **A ZAUN WALL**: teal-grey painted steel, tangential brush arcs, grime runs, rivets, chipped card edges, scratches, riveted dark plates, Permanent Marker lettering with pink drop. Low key; the pink frames carry ownership.
- **B GOUACHE & INK**: aubergine gouache, radial flat-brush strokes, cream paper hub and a cream paper HP track, paper card canvases with pink masking tape, Anton lettering hand-jittered with ink. Higher value contrast on hub, cards and ring, so the player objects are the lightest things on the board. The tower layout is the same as A; the difference is material and value.

## How it meets the plan
- **Families:** P only is painted. E gets the plan's slate toning (`plate.py tone_enemy`: Packet/Worm/Jammer/Payload/Ring washes #3D5466 / #4B4A6E / #2D5D69 / #5B5560 / #55617A, so pink = ours alone). K, S, T and the rest of the board are the E10 generator unchanged (see risks).
- **Line grammar:** L2 painted stroke = all pink; L1 ink keyline under every mark; L7 cross-hatch = lost at END TURN (HP segments, slice pips, breaking slices; hatch colour HARM here, SOAK and CELL_PINK samples on the board); L8 dotted = +2 trim; no dashed line is drawn by my layers (tracers, ring, pips, trim). L9 glow only on hatched edges and the HOT trim. L10 (Brace plate) and L5/L6 not in p1, same style would apply.
- **Time (C) on the tower rim trim:** HOT red solid 6 px + glow + END notch wedge; COLD thinner desaturated solid; FAR dotted. No lane colours on the tower.
- **HP (D):** 15 segments in 3 groups of 5, 9 deg group gap, 2.5 deg segment gap, 7 px, r150-157; pending run = last 6, hatched, clockwise. Slice pips 2 per slice at r123.5. The white slash is gone. YOU strip = same 15 in painted blocks on a taped strip.
- **Colour:** slice frames are all pink (no type colours). Card type tags are neutral paper/ink (orange and cyan are not card colours; the TOWER/WAVE word carries it). Cost coin stays the S cyan RAM coin, stuck on like a sticker. Loud tab stays Trace violet.
- Same information: same wheel, pips, hand (Brace, Spin 3, Trigger, Twist), cost, x3, +1, rules text, SEND IT, CELL-9 // BREAKER, UNDO. No words added.

## Legibility risks
1. Pink player vs HARM red: the hatched red segments sit next to pink frames. Colour-blindness check (deutan/protan/tritan dE >= 12) was NOT run in this pass; the shape pairing (hatch, chevrons) carries the meaning, but the check is owed, with fallback #FF4FD0.
2. Texture is subtle at 1x (brush ridges are about 1-2 px); the read at 1x is pink frames + cross-hatch + icon silhouettes. Texture is judged at the 2x crops; 320 px squint not run.
3. Icon contrast: white silhouettes with ink sit on texture of low contrast (calm disc around icons). Slice icons are slightly warped by the hand-cut edge; the shield half-detail survives.
4. The 3 pending slice hatches (s1, s2) are dense lattices; at 1x they read as red mesh. Pitch 6.2 px could widen.
5. Not done in this pass: nowords plate, f2/p2/p2b/p3 beats (state builders exist but only p1 was rendered), hover plates, Brace plate / soak funnel / crack states (pip states mend/soak/gone and break X are coded and used by the board's samples only). Enemy side still carries E10 dashed lane outlines and red NOW outline (they belong to the K/E/T streams); I changed only the unit washes and LANE colours that took effect.
6. Rule broken by mistake: I twice ran `python -` heredocs (once completed instantly, once hung); the hung background task was stopped by id. Nothing else was affected.

## Build in Godot
- **Textures (baked once):** per-slice painted wedge albedo+height (the `Paint` canvas output), a stroke atlas of ~40 bristle strokes (alpha + height) for frames/tracers/HP blocks, paper grain, scratch and grime tiles (tileable), 16 doodle sprites (marker, ink keyline baked), hand-lettering baked per card title/name (static strings).
- **Shader (canvas_item, one for all P sprites):** albedo * (1 + k * dot(grad(height), light_TL)) impasto lighting from a packed height channel; edge roughen via a 256 px noise-displaced alpha (1.3 px); ink keyline offset 1 px as a second pass (sprite drawn twice, ink first); optional 1 px misregistration of the pink layer. No bloom; the HOT hatch edge uses the shared glow layer.
- **Dynamic parts:** HP segments and pips are 9-slice capsule sprites in 5 states (lit, harm hatch, soak hatch, mend, gone) with the hatch as a tiled texture masked by the capsule; the trim, tracers and doodles are authored strokes stretched along curves via `Line2D` with a bristle texture and taper curve.
- **Cards:** one card scene per variant: body sprite (painted, 168x232 + pad), art band sprite, glyph stamp sprite (white + ink + pink drop baked), Label nodes with baked lettering for titles and plain Plex for rules text; the fan reuses the existing hand_fan transform. Sprite sheets: tower atlas 2048, card atlas 2048, chrome atlas (SEND IT states, nameplate, YOU strip tape) 1024.
- **Perf:** all textures static; the painted sprites are 1x draw calls, no per-frame procedural work.
