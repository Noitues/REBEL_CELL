# MAINFRAME shop, street-graffiti take (exploration, 2026-10-21)

Exterior (Cycles, AAA-2 night) and interior (PIL mockup over the shop_v5 layout) restyled with the street-graffiti look from
`street_graffiti/` (street and Tokyo-canyon ideas only). No decisions logged; bible bent where the style needed it.

**What changes.** Exterior: the F1b layout (tower + red MAINFRAME sign, alley stair, front building with roll shutters) rebuilt as a
PBR street-level scene with graffiti in zones: bombed shutters, lower walls, the sign pole and door posts, the bin; a wet street;
multilingual blade signs, cables, a ramen hologram on the RAMEN sign; the MAINFRAME shop under the sign (half-up shutter, lit
counter glimpse, fascia). Interior: bombed wall behind the board, spray-stencil section labels, marker-tagged kraft price tags,
sticker-bombed clerk bezel, LEAVE as a peeling slap; prices, chips, daemons and the wheel are untouched.

## Files, timings, numbers
- `mainframe_shop_exterior.png` 1920x1080. GPU (RX 6700 XT, HIP), OIDN denoise, **48 spp requested, stopped by an 18 min time limit**
  (render 1153 s, wall 1177 s; the true spp reached is lower, probably about 40: not logged). Display median **0.165** (target 0.15-0.20).
  An earlier 52 spp run of an older, busier scene hit the 20 min cap and was discarded.
- `mainframe_shop_interior.png`: PIL, about 25 s on CPU. `mainframe_shop_sbs.jpg`: top f1b_night | graffiti exterior, bottom shop_v5 | graffiti interior.
- Previews: CPU Cycles 960x540, 20-24 spp, 1-3 min each (no GPU lock).

## Rebuild
```
S=docs/concepts/hq_styles/rebel_cell_graffiti/scripts
python $S/gs_tex.py                       # textures -> D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex (sign, atlases, shutters, signs, bin, fascia)
python $S/gs_final.py 1920 48             # GPU lock (FIFO) + Cycles; time limit 1080 s; writes final_beauty.npy
python $S/gs_post.py D:/rc_scratch/hq_styles/rebel_cell_graffiti/final_beauty.npy mainframe_shop_exterior.png 0.17 1920
python $S/gs_interior.py mainframe_shop_exterior.png mainframe_shop_interior.png
python $S/gs_sbs.py mainframe_shop_exterior.png mainframe_shop_interior.png mainframe_shop_sbs.jpg
sh $S/run_prev.sh <tag> 960 24            # CPU preview
```
Reused at run time, never edited: `round33_mainframe_sign/scripts/flicker_sign.py` (red v4 sign), `street_graffiti/scripts/graf_atlas.py`
(pieces, tags, signs fonts), `round12_modem_facade/scripts/post.py` (blur), `round34_firmware_daemons/scripts` (shop_v5 layout, patched
in memory: backdrop, `dymo`, `price_tag`, `pegboard`, `place_leave`; the stale `C:\...\worktrees` font path in `sticker_lib19` is rebound).
The round-12 scene itself is not reused (it is Eevee toon); only its camera, layout constants and sign anchor.

## Critique (squint test, per designer rule)
Process: first preview (p3) was wall-to-wall graffiti, and failed: you could not tell building from paint. The coordinator rule cut
the paint to zones (below 5 m, fading out by 11 m, broken up by a low-frequency patch mask, desaturated, glow 3.0 -> 0.9), lifted wall
values, thinned the haze. p7 passed. Then feedback: holo moved from bottom left to above the RAMEN blade, MAINFRAME shopfront made the
hero (centre stall demoted to "NOODLE", dim), sticker speckle removed from the facade and clustered on pole and door posts, upper half
given windows, AC units and one more blade.
- **Final exterior, at thumbnail size:** reads street, sign, shopfront, stair, shutters, sidewalk. Value order: red sign > shopfront and
  blades > graffiti > street. Graffiti covers roughly half of the ground-floor surfaces, almost none above 10 m.
- **Weak:** (1) the hologram reads as a floating saucer more than a ramen bowl; at this size the noodles are hair-thin. (2) The MAINFRAME
  shop under the sign is small and dark next to the shutters; the lit counter is a thin strip. (3) Upper-right is flat grey boxes with
  cardboard-like lit windows (no frames or depth). (4) Cables are dense but uniformly black. (5) Wet street shows reflections of the
  sign but little of the blades. (6) Sticker-bombed poles are near-black at distance. (7) Noise: denoised at fewer spp than asked; some
  smeared texture on distant paint.
- **Interior:** prices, chips, daemons, LEAVE and the offscreen wheel read before the decoration (checked at thumbnail). Weak: the red
  sign behind the clerk screen is dim and blurred (shop_v5 had a sharper sign); the right wall piece behind the bin is busy and the
  orange scrap by the bin is an untidy leftover; stencil letters on DAEMONS/FIRMWARE are legible but rough; slaps on the bezel hide the
  screen's rim, never its text.

## References (pages read, no downloads) and the trait taken
| Reference | Trait |
|---|---|
| [Golden Gai alleys, Nightlife Tokyo](https://nightlifetokyo.com/en/tokyo/guides/golden-gai-guide) | Alley density: hand-painted signs, lanterns, taped photos on tiny frontages; narrow stair-like passages. Used for the alley stair and stacked blades. |
| [Omoide Yokocho / Golden Gai overview, Japan Times](https://japantimes.co.jp/culture/2022/06/09/books/emergent-tokyo) | Tiny shops under rail tracks, lantern light, grills: warm small light pools against dark mass (shop glimpse, lamps). |
| [Apliu Street, Sham Shui Po](https://en.wikipedia.org/wiki/Apliu_Street) | Open stalls of cables, parts, second-hand devices in a dense grid: cables everywhere, parts-shop trade on the signs ("CHIPS", "電子零件"). |
| [Akihabara electric town, guide](https://www.tokyotourism.org/?p=1507) | Neon, billboards and screens filling the street after dark; electronics-parts shops in back alleys: vertical multilingual signs. |
| [Graffiti in the United States / NYC subway era](https://en.wikipedia.org/wiki/Graffiti_in_the_United_States) | Tag, throw-up, piece hierarchy and 1980s bubble letters and characters: shutters get one big piece plus throw-ups, tags last. |
| [Wildstyle](https://Www.wikipedia.org/wiki/Wildstyle) | Interlocking exaggerated letters: the `wild` factor on the big pieces. |
| [Shepard Fairey / Obey sticker, stencil, wheat-paste campaign](https://en.wikipedia.org/wiki/Shepard_Fairey) | Sticker slaps and wheat-paste on municipal furniture: stickers go on the pole, door posts, bin and clerk bezel, not on every wall. |
| [Blade Runner 2049 VFX, DNEG on Joi](https://www.awn.com/print/vfxworld/double-negative-delivers-joi-blade-runner-2049) | Holograms are not a classic blue wireframe: a soft emissive form with a projector read. Used for the ramen holo (cone from an emitter). |
| [Cyberpunk 2077 Night City, how CDPR built it](https://www.gfinityesports.com/article/cyberpunk-2077-cd-projekt-red-building-night-city) | Japantown mixes kiosks, vending machines, lanterns and mundane tech on doors: the sticker-bombed vending machine and door posts. |

Pages for Banksy placement and the BR2049 noodle stall returned nothing usable; the traits above come from what the pages did say.

## Buildable traits taken
1. Paint in zones: shutters and lower walls get the pieces, everything above 10 m stays architecture. 2. One big piece per shutter, throw-ups
and tags over it. 3. Stickers clustered on furniture (pole, posts, bin, bezel). 4. Dense vertical multilingual blades and cables as the canyon.
5. Small warm light pools (shop glimpse, lamp) against dark mass. 6. Holo as soft emissive form with a projector cone.

---
# Exterior v2: the original F1b scene plus a graffiti layer (designer: "why did we abandon the F1b look?")

`mainframe_shop_exterior_v2.png` (1920x1080) and `mainframe_shop_exterior_v1_v2.jpg` (f1b_night | v1 | v2). v1 (Cycles rebuild) is kept
as `mainframe_shop_exterior.png`; the interior is still built over v1's backdrop and has not been redone for v2.

**How.** `scripts/gs2_scene.py` runs the ORIGINAL scene (`round33_mainframe_sign/scripts/scene.py` = round-12 F1b + the red sign hook, MF_VAR=b,
night, Eevee toon) and injects `gs2_extras.extras()` before its figure/city/ground/lights, so geometry, camera, lights, palette, `post.py`
(ink, haze, bloom, rain, wet-floor reflections) are F1b's own. The fire escape and the alley stair are F1b's, untouched. Nothing in round12/33 is edited.
Added layer: decals made from F1b's own toon material with the albedo (and glow) swapped for an image, so they take the same banded light;
each decal reuses the pass index of the wall under it, so the ink pass draws no outline round paint. Blades, fascia and holo are registered
as emissive `sign` objects, so post.py's own wet-floor reflection and bloom include them. The red sign texture is clean (no tags, no stickers).
```
python $S/gs2_tex.py                     # tex2: clean sign, wall atlas x patch mask, shutters, pole strips, bin
sh $S/run_v2.sh v2f 100 48               # Eevee 48 samples + round12 post.py; about 2 min, no GPU lock
python $S/gs2_cmp.py mainframe_shop_exterior_v1_v2.jpg
```
Median of v2 is about the F1b night level (Eevee toon, not the AAA-2 0.15-0.20 grade). Timing: scene + render 1m50 to 2m10 at 1920x1080, 48 samples.

**Designer points.** (1) F1b look restored. (2) Fire escape untouched. (3) The sign-side pole is square: stickers sit on the two faces the
camera sees, each sticker wholly inside its face (no wrap, no seam), pole plain above 3.4 m; the bin is a cylinder with its UV seam at the back
and the emblem and slaps on the camera side. (4) The alley stair keeps F1b's geometry; lit riser strips and three cyan lamps wash the treads; no paint
beside it. (5) Reflections are F1b's own (screen-space gloss plus post.py's sign/emitter columns from the real beauty pass); nothing painted in.
(6) Sign, plate and frame clean. Whole sign in frame (F1b camera). MAINFRAME shop under the sign: fascia board, warm foyer glow, red spill on the wet pavement
from F1b's sign lights; the centre stall reads as a dim "NOODLE" horizontal. Hologram: bowl, noodles, two eggs, chopsticks, steam wisps, scanlines,
floating above the RAMEN blade with an emitter on the sign; no ground prop.

**Critique (squint test against f1b_night).** Reads as the same street at a glance: red sign, fire escape, stair, shutters, wet pavement. Graffiti sits
in zones (two shutters, left facade edge, alley wall at the stair mouth, the right-hand shopfront, pole, bin); value order is sign > shopfront and blades > paint.
Weak: (a) graffiti density is lower than v1 and the shutter pieces are only moderately big, since F1b has only two shutters in view; (b) the right side
(side-row shopfront) is the most painted and sits on the frame edge; (c) the ramen holo is small (about 170 px) and its steam reads as a few thin lines;
(d) Blade signs are brighter and cleaner than F1b's own glyph boxes, so they pull attention; (e) heavy rain from the original night state veils the paint at thumbnail size;
(f) the sign-side pole's fascia overlap: the MAINFRAME fascia is half hidden by the pole; (g) the faceted toon wall at left still carries some of the F1b red wash over the paint.
