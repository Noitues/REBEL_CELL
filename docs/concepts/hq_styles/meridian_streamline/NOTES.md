# Meridian Freight HQ in Streamline Moderne / Machine-Age (concept, 2026-10-21)

Single-HQ style exploration; nothing in the base pipeline was edited (`scripts/sl_run_hq.py` patches `hq_meridian_v3` at run time
through `sl_blender_hq.py`; art-deco helpers are imported read-only). Files: `meridian_streamline.png` (1920x1080), `meridian_streamline_sbs.jpg`
(current golden plate | art deco | streamline).

## What the style changes
- The Gatehouse Gantry keeps its layout: legs become stadium-section chrome-and-enamel towers (repeated white / orange / red speed bands, porthole
  rows, ribbon windows, lit glass-block pylons, a clock face, three swept tail fins and a mast), the span a chrome-edged girder with a catwalk rail,
  masts with pennants and three speed lines, the keep a teardrop streamliner hull with a flying bridge, the train a graphite Loewy bullet with pinstripes.
- Curtain walls carry a triple horizontal speed line (orange / warm white / red), a slanted orange hazard rim and a chrome coping; the S corner
  towers end in round drum setbacks and a chrome dome.
- The city fill is dark blue-steel with cool windows and a cool fog (no brown), small round caps on the tallest towers, so orange and red belong to Meridian only.

## Timings and values (RX 6700 XT, HIP, 1920x1080, 52 spp)
Final: 1135 s render + build (about 30 min waiting for the shared GPU lock first), frame median (luma) 0.157. Look-dev: CPU 1280x720 8 spp, about 170-220 s each (3 passes).

## Rebuild
```
S=docs/concepts/hq_styles/meridian_streamline/scripts
cd D:/rc_scratch/hq_styles/meridian_streamline
bash $S/prev.sh <tag> haze_abs=0.0013          # CPU preview, no GPU lock
SL_SPP=52 python $S/sl_gpu.py art_streamline_final gpu.log -- python $S/sl_run_hq.py art final haze_abs=0.0013
python $S/sl_sbs.py                            # writes the png and the sbs into this folder
```
Scratch (renders, logs, previews): `D:/rc_scratch/hq_styles/meridian_streamline/`.

## Weak points
- The keep teardrop is hard to read from this camera (it sits behind the span, low contrast); the train stands behind the N wall and is not visible.
- Chrome has little to reflect at night, so it reads as white edges more than polished steel; the S corner domes look like pagoda rings.
- The city fill is cool and clean but the HQ glow bleeds a little; no tower-scale streamline massing in the fill.

## References (pages read only; nothing downloaded or copied)
| Source | Trait taken |
|---|---|
| [Streamline Moderne (Wikipedia)](https://en.wikipedia.org/wiki/Streamline_Moderne) | Strong horizontal emphasis, rounded corners, porthole windows and glass brick, horizontal grooves/lines, ornament replaced by smooth lines, chrome and enamel; light built into the structure (Normandie's lit glass pillars) -> lit glass-block pylons and ribbon window bands up the legs |
| [Pan-Pacific Auditorium](https://en.wikipedia.org/wiki/Pan-Pacific_Auditorium) | Four upswept towers shaped like aircraft tails over a long flag-pole facade -> three swept chrome tail fins on each leg crown, a row of masts with pennants along the span |
| [Coca-Cola Building, Los Angeles](https://en.wikipedia.org/wiki/Coca-Cola_Building_(Los_Angeles)) | Ocean-liner metaphor: portholes, catwalk, flying bridge -> porthole rows, catwalk rail on the span, a rounded wheelhouse on the keep |
| [PRR S1](https://en.wikipedia.org/wiki/PRR_S1) | Loewy's bullet-headed shroud, wind-tunnel-tested clay model -> the bullet-nosed train and the teardrop keep hull (blunt nose, long tail taper) |
| [Raymond Loewy](https://en.wikipedia.org/wiki/Raymond_Loewy) | GG1 pinstripe scheme that highlights smooth contours -> thin parallel orange / white / red pinstripes running the full length of train, keep and walls |
| [20th Century Limited](https://en.wikipedia.org/wiki/20th_Century_Limited) | Dreyfuss's streamliner in blues and greys -> graphite blue-grey train livery against the orange speed lines |
| [Hoover Dam](https://en.wikipedia.org/wiki/Hoover_Dam) | Kaufmann's streamlined Art Deco redesign: turret-topped intake towers with clock faces, colour-coded machinery -> a clock face on each leg tower, coded white / orange / red band order |
| [Futurama (1939)](https://en.wikipedia.org/wiki/Futurama_(New_York_World%27s_Fair)) | Bel Geddes's streamlined, lit model city under glass -> the fill kept as a quiet, dark, evenly lit mass so the lit HQ model-piece reads |
