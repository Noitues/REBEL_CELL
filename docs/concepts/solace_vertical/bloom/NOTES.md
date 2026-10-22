# Solace THE BLOOM v2: concept round (A Necrosis / B Mycelium / C Culture spill)

Concept only; the designer picks before anything is built. Rules come from `solace_v2_spec.md` (read-only); the art invents none.
No game text UI is designed: the FRONT chip and the raid INFECTION row are build's.

## Directions
- **A Necrosis**: plum-black skin, pink veins, hairline hot front edge, window light dying behind the front (hatched, never colour alone).
- **B Mycelium**: pale hyphae crawl out of the front first, then dark felt mats with glowing pink spore caps. Hyphae are strokes that follow the front's gradient and fork.
- **C Culture spill**: glossy pink agar, translucent, with bubbles and cells. The front is a meniscus (white rim, lighter refracting band, contact shadow): TIDE made literal.

## Medium mapping (ART_BIBLE 1.2)
- Bloom in the scene = World (AAA-2 plates on street and HQ; cel + ink on the raid map).
- TIDE gauge = CRT terminal (navy glass, cyan edge, Share Tech Mono, scanlines). The tube is filled with the direction's own material.
  Bands read by glyph, not colour: DORMANT dash, CREEPING 1 chevron, CLOSE 2, CATCHING 3, CAUGHT X block; the current band is bracketed.
- Forecast = red grease pencil, dashed (street: ground line where the front lands if the next node is entered, +715 milli; also a dashed tick on the gauge).
- CAUGHT = binary bits, pink (4 frames: intact, burst, flood, fade to black).
- Live % = bare Anton (raid: "60%" with no box), on a CRT bar with a CITY LOST X-block cap.

## Method (deviation from the brief: no new Cycles render)
The AAA-2 frames are composited in world space over the existing golden Cycles plates, as v1 did, so the GPU lock was not taken:
- Street: plate Z pass + camera (`D:/rc_scratch/street_r2/render_s1`) give world x / y / height; the front is in route-layer units (LX table).
  Operative on L1, front at layer -0.25 (gap 1.25, CLOSE per close_gap 2.0 / catch_gap 1.0; gap exactly 1.0 would already be CATCHING).
- HQ: object-index pass (id 1 strands, id 3 plinth) of the v5 overview; front row from the measured helix base/top rows at floor 9/27, same row on both strands, tongues along the strand; the plinth is the source (infected).
- Raid: Eevee cel + ink. `scripts/raid_scene/` holds patched copies of the district scene (`BLOOM_POS=1` writes a world-position pass, 7 s, Eevee only). Skin is laid in world space (ground x,y; walls x+y and height; roofs x,y) on the clean R5 raw, re-inked with the same ink pass and `post.py mapraid`.
  Defended home-server nodes (helix plaza r 46 BU, hospital r 42 BU at (108,-60)) are never recoloured. Ground floods first, walls to a tide line.
- Overlays (gauge, route marks, pencil, bits, Anton %) in PIL.

## Values
- Netrun frame medians (clean plate 0.1407): A 0.1342, B 0.1431, C 0.1411 (all within +-0.01). Skin gain applied: A x1.07 on clean dim pixels, B x0.25 and C x0.78 dimming of the dark covered part (bright hyphae, caps, rims kept).
- HQ medians (clean 0.1157): A 0.1145, B 0.1138, C 0.1168. Front row 877 of 1440 (base 1284, top 167).
- Raid: infection 60 % of non-defended visible area (bisected), 51 % of the frame; medians clean 0.2604, A 0.2013, B 0.2414, C 0.2648.
- Render times: street 15-16 s per frame, HQ 21-27 s, raid 31-35 s each (+ 7 s Eevee position pass once), gauge strip about 19 s each (numpy, CPU).

## Rebuild
```
cd scripts
BLOOM_POS=1 blender --factory-startup -b --python raid_scene/sd_main.py -- --dir D --park 1 --plinth 1 --mode ink --view raid --tod night --size 1920x1080 --out D:/rc_scratch/solace_v1/bloom/out/raid_pos.png
python bloom_street.py A,B,C CLOSE ; python bloom_hq.py ; python bloom_raid.py A,B,C 0.60 ; python bloom_strip.py ; python bloom_sheet.py
```
Scratch: `D:/rc_scratch/solace_v1/bloom/`. Needs the street_r2 render_s1 passes, hq_v5 index pass, district R5 raw/ink in `D:/rc_scratch/solace_v1/district/out`.

## Known limits
Street CLOSE shows little coverage (front a layer behind the operative, as asked). B and C textures are world-space on grazing ground, so they foreshorten. HQ skin is screen-space-scaled, not tube-coordinate. Gauge A fill is dark by design (plum on navy).
