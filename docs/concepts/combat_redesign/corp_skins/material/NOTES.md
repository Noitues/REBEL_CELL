# Corp skin test B: colour + material + pattern (enemy layers)

Base: linocut plate A, p1 decide, bio cutaway. Player wheel, cards, HUD unchanged (pixel-identical outside the enemy layers, apart from the HUD being below).

## What changes
Cell field (empty and unit cells, gutters, cell edges), unit token frames, landing-arc frames and landing discs, bezel and landing annulus, the schedule tape (live, +N, HOLD cells and labels), the outer rim (new 11 px band), the future-wave tickets. Hue and the base E-material helix are the only things re-themed on the data side; all the game marks are the original drawing on top.

## Grammar check (by eye, not measured)
HOT/COLD/FAR trim, red cross-hatch, arrowed outlines, white enemy outline, HP ticks, chevrons, diamonds and NOW/+1/+2 tags are untouched and read on both skins. Pattern alpha is 10-20 percent. Lane rings stay white/grey (depth code) because the frame sits outside an ink groove. Not run: squint metric, grey proof, dE of unit kinds (kind washes are blended 40 percent toward the corp tint so kind separation shrinks; the glyph shape still carries kind; measure before locking).

## Pink clash (Solace)
Pink is demoted to under-glass rose nuclei, tiny and translucent; the corp reads lime/porcelain. Player pink remains the only flat saturated pink and is also told by linocut technique vs clean glass.

## Risks
- Solace lime tape is the loudest enemy mass (was orange); lime is near the player's HP green (#7BE07B) by hue, but they are in different places and the tape is a wide arc. Consider tape at 85 percent value.
- Overall Solace board is greener/darker green and a little busier than slate; Meridian cells are brown (oxide at 34 percent). Both lower the wheel's pink pop slightly less than expected (it still wins).
- Meridian orange coincides with the SCHEDULE orange: on Meridian the tape no longer differs from the rim and frames by hue; it is told by position and chevrons only. Hazard stripes are on the rim only, away from the tape.
- BOSS_GOLD adjuster cell and the yellow plan colour untouched; Meridian hazard avoids yellow for this reason.
- Hue-rotating the tape is a render trick; in Godot the tape needs per-skin colours (below).
- Meridian stencilled numbers not rendered (kept as an option).

## Godot build notes
- Data: one `CorpSkin` resource per corp: palette, textures, crest, tape tint, frame textures. Corp swap = swap resource.
- Cell material: shader on the ring-cell mesh: world-space (polar) membrane/rib pattern from one tileable 512 texture per corp (voronoi+bubbles for Solace, ribs via a polar sine for Meridian, no texture needed), multiplied at 10-20 percent over the kind wash. Cheap, one draw pass per ring.
- Token frame: pre-baked 64x64 sprite per corp (porcelain ring / octagon), under the existing disc; landing disc a 32x32 copy.
- Tape: draw with the schedule colour taken from the skin (do not rotate hue at runtime); pattern as a masked texture overlay.
- Rim: a ring texture (3-4k px strip, or polar shader) with the seamless integer turn counts used here (71 helix turns, 311 stripes); crests are six sprites at the spokes.
- Tickets: 9-patch per corp.
- Pre-baking everything to textures is also fine (static layers); only the tape text and marks need to remain live.
- Source snapshot: `src_snapshot/cs_skin.py` (skins), `cs_run.py` (patches over the F1 generator; run `python cs_run.py solace|meridian`; needs the working copy at D:/rc_scratch/corp_skin/material).
