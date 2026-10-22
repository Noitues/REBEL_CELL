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

## A in 3D (designer picked A Necrosis; world material, portable)
Files: `A3d_street_{creeping,close,catching}.png`, `A3d_hq_{overview,decision}.png`, `A3d_raid_{20,60,90}.png`, `A3d_gauge.png`, `sheet_A3d.jpg`.
- **Street** (street_r2 scene copy `scripts/street3d/`, Cycles, DECISION camera, GPU lock `solace_bloom`): `bloom3d_mat.py` = node groups BL_FIELD / BL_SHADER wrapped
  round every material's look under the section cut (r2_build.section) and the ground (sweep). Everything is a function of world position: ragged front with fingers and
  tendrils, domain-warped 3D Voronoi cell borders as veins, 45 degree world hatch, hairline pink front edge, plum diffuse body. `bloom3d_ribbons.py` adds emissive vein
  ribbon decals that crawl ahead of the front on the ground. Keep-out (solace.md): route-room AABBs (+10 %, jamb, frame ring) and link boxes are masked to zero for skin and ribbons;
  the Bloom sits in the material under the section cut, so ghosted/flattened blocks carry it only at their cut height. Mock operative on L2_1; gaps 2.5 / 1.25 / 0.6 layers (front at layer -0.5 / 0.75 / 1.4).
  Note: INFECTED-room plum wash and hairline on room frames were not drawn here (route chrome is build's). Post = street_r2 post at the CLEAN plate's exposure (0.372).
- **HQ** (v5 scene copy `scripts/hq3d/`, Cycles): the strand mesh gets a per-vertex `tube` attribute (z, phi, tower); `bloom3d_hq.py` shader reads it, so the front (one z for both strands plus phi-only tongues),
  veins (Voronoi on the tube cylinder stretched along z, so they follow the twist), fingers ahead of the front and the hatch run along the strand. The UP stair band stays clean and the windows are mesh holes.
  Windows below the front die: the shared emission material is wrapped (helix radius < 30, above the plinth; route-room index 5 untouched) to dim pink. Front: overview floor 9 of 27 (CATCHING),
  decision floor 9 minus 1.25 layers (CLOSE).
- **Raid** (district copy `scripts/raid_scene/`, Eevee cel + ink): `bloom3d_raid.py` wraps every cel material; field = noise-warped distance from the two defended nodes, per-lot values, tide line on walls.
  The percent is calibrated by cover-mask renders (bisect) so the infected share of non-defended visible area is 20.9 / 60.7 / 89.4 %. Defended nodes never recoloured. Re-inked with the clean ink pass.
- **Gauge strip / bits**: 2D as before, over the 3D CATCHING street frame.

Values (median / under 0.10 / over 0.85):
| Frame | clean | Bloom |
|---|---|---|
| street CREEPING | clean DECISION plate 0.141 (street_r2 plates.json, exposure 0.372) | 0.1487 |
| street CLOSE | same | 0.1414 |
| street CATCHING | same | 0.1486 |
| HQ overview | 0.1230 | 0.1231 |
| HQ decision | 0.1474 | 0.1473 |
| raid 20 / 60 / 90 | 0.2604 | 0.2553 / 0.2503 / 0.2588 |
All street/HQ within +-0.01 of clean. Raid 60 is 0.0101 under (the cel map is bright; the plum body lifts with `plum`).
Render times: street finals 428 s (CREEPING), 269 s (CLOSE), 1795 s (CATCHING, GPU shared with a concurrent job); street 640x360 tests 54-240 s; HQ finals 1920x1080 231 s overview / 93 s decision
(clean 156 / 135 s); HQ tests 35-42 s; raid 10-23 s per 1920x1080 frame plus 7 calibration renders of about 3 s.
Rebuild: `street3d/bloom3d_street.py run finals <STATE> 1920 48` then `plate <STATE> F_dec_closed`; `hq3d/bloom3d_hq_run.py b3d overview decision clean_overview clean_decision`;
`bloom3d_raid_run.py 20,60,90`; `bloom3d_strip.py`; `bloom3d_sheet.py`. Scratch `D:/rc_scratch/solace_v1/bloom3d/`.
Port notes: the field is pure position/attribute math (no textures), so it maps to a Godot spatial shader on world position (street, raid) and on a (z, phi) vertex attribute or UV (helix).
