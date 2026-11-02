# Corp skin test A: colour only

Base: punk linocut plate A (p1 decide). Only the enemy layers were re-coloured; player wheel, cards, HUD and the backdrop are the same pixels as before. Code: `src_snapshot/` (`corp_skin.py` token tables + recolour, `skin_run.py` renders, `mk_crop.py` the crop). Palette: `tokens.md`.

## What changes
- Wave ring cells and outline, gutters, ring floor, unit token discs and frames, landing arcs, future-wave tickets and ring tags (NOW W1, +2 W3), THIS TURN / HOLD tape, the outer rim and its schedule track.
- Solace: leaf-green glass cells, lime enamel lines, lime tape, green rim, porcelain-lime discs. Meridian: container-steel cells, warm-white enamel lines, orange tape (it was already orange), orange-bronze rim, bone discs.
- Shapes, materials, patterns, line weights, positions: identical.

## What stays
- ART CALL 51 grammar: HOT/COLD/FAR still read by brightness step of the same enamel ramp (the ramp is monotonic in luminance, so the order cannot flip); red cross-hatch pending loss, arrowed movement outline, pink guns, boss gold, HP and cause colours are not touched.
- Player vs corp: the wheel stays hot pink with black ink. Against Solace green it is a complementary pair (strongest contrast). Against Meridian steel and orange it is still clear.

## Solace pink clash (secondary #FF4696 vs the player's pink)
Handled by not using it. Pink means "ours" on this board (wheel, guns, our-damage hatch), so Solace's secondary is withheld from every enemy stroke and fill. The token exists only as a softened blush (#F4B6CE) reserved for tier II marks later, as a low-saturation fine accent, never on a cell edge or the tape. Solace reads by green glass, lime enamel and (future) helix/cell patterns instead. Meridian's red #FF2E28 is withheld for the same reason against HARM red; the oxide #B8402A is the reserved stand-in.

## Risks
- Meridian: the orange rim and the orange THIS TURN tape are the same hue, so the tape has less pop than on the old neutral rim. Option: darken the rim to steel and keep orange only as its hairline.
- Solace: lime tape is the loudest enemy mark and sits near the lime HUD green (YOU HP blocks). It reads as "enemy" only because of the green glass around it.
- Hue-based remap: any enemy mark that was cool or neutral turns corp-tinted, including some cyan-ish dots near the cell hairlines; anything orange (14 to 40 degrees) moves with the tape. Gold (boss, hold bracket, plan) was kept, so on Solace the gold bracket is now the only warm yellow on the ring.
- Meridian steel is darker overall than the old slate; the cell wells separate from the floor by about 2 steps, no more.
- Not run: draw asserts were run by the generator (no failures printed), but no squint metric, grey proof or CVD (designer said ignore CVD). Effects, hover plates and hand states not re-skinned (p1 only).
- Process note: one stray empty `python -` was started by mistake (no code ran, it only waited on empty stdin); it may still be idle as a python process I could not kill.
