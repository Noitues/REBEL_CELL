# Solace HQ as a modern-art sculpture (v2 exploration, 2026-10-21)
`solace_modernart.png` (1920x1080, golden plate overview camera), `solace_modernart_sbs.jpg` = current golden plate | art nouveau | modern art.
Nothing outside this folder was edited: `scripts/modernart_run_hq.py` patches the base `hq_solace` pipeline at run time
(hook in `modernart_blender_hq.py`; `deco_restyle.py` helpers imported read-only). The base tube / window / office geometry of the
landmark is emptied at run time and replaced.

## What the style changes
- The HQ is a monumental helix sculpture: two broad glossy lacquer RIBBONS (one lime #96FF46, one pink #FF4696; 62 BU wide, 2.6 thick, shallow bow
  so highlights roll across them, lime / pink edge-light strips on both edges) wound once round (full 360 deg twist, same radius / pitch as the
  canonical helix). Reflection-only softboxes (invisible to camera and fog) and two cool/pink spots give the lacquer long highlights.
- Base pairs = colour-blocked slabs spanning the ribbons, one per floor, each split into two colour fields with a thin black seam:
  Mondrian red / yellow / blue / white / black; route floors are thicker lime | pink slabs with a colour-block room on top (the nodes' places).
  Topped by a mirror-steel ball (Kapoor).
- Plaza = white glossy gallery plinth on a black reveal. City fill = v1's cool teal-black (verdigris mullions, pale cool windows, blue-green mist). No fine ornament.

## Timings / values
Final: 1920x1080, 52 spp (see below for the measured values). CPU look-dev previews at 960x540, 8 spp, 1.5-4 min each (5 runs).

## Rebuild
```
S=docs/concepts/hq_styles/solace_modernart/scripts
bash $S/prev.sh <tag>        # CPU preview -> D:/rc_scratch/hq_styles/solace_modernart/solace/<tag>/plate.png
DECO_SPP=52 python $S/modernart_gpu.py art_modernart <log> -- python $S/modernart_run_hq.py solace art g1
python $S/modernart_sbs.py   # after copying plate.png to solace_modernart.png
```

## References (pages read only, nothing downloaded) and the trait taken
- Jencks DNA sculptures, Clare College Cambridge / Newcastle DNA Spiral: https://www.cam.ac.uk/node/22183 and https://co-curate.ncl.ac.uk/dna-spiral-times-square-newcastle
  - a double helix as pure public sculpture: two clean continuous strands, rungs as separate bars, read from a distance.
- Kapoor, Cloud Gate: https://rapidwelding.com/blog/articles/the-bean
  - polished stainless plates, mirror finish, no visible joins (mirror ball, long softbox highlights, ribbon smooth shading).
- Koons, Balloon Dog: https://www.dimensions.com/element/balloon-dog
  - mirror-polished steel under a transparent colour coat: saturated lacquer with a clear coat (ribbons and slabs are coated saturated colour).
- Serra, The Matter of Time / Torqued Ellipses: https://en.wikipedia.org/wiki/The_Matter_of_Time
  - big sweeping curved steel walls seen as a single mass: the ribbons are broad curved walls, not tubes.
- Calder and Mondrian: https://buffaloakg.org/artworks/k196124-cone and https://christies.com.cn/lot/lot-5621981
  - pure fat primaries plus black and white, a static stabile rooted to a plinth: the colour-blocked slabs and the plinth.
