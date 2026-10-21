# Solace district: concept round 1 (2026-10-20)

Concept renders for the Solace district around the HQ helix, three directions on ONE shared layout. Concept only; nothing here is wired into Godot.

## Files
| File | What |
|---|---|
| `A_map.png`, `B_map.png`, `C_map.png` | cel map view, 1920x1080: Eevee, orthographic (scale 330 BU, 38 deg down, az -135), 3 hard toon bands, wobbly ink lines, light spill, haze |
| `A_night.png`, `B_night.png`, `C_night.png` | AAA-2 realistic night hero, 1920x1080: Cycles (HIP), 72 spp max (adaptive), OIDN, world volume fog, wet streets, ~45 deg oblique from ~235 BU |
| `sheet.jpg` | 2560 wide: Godot-now + plate crops on top, rows A/B/C x (map, night) |
| `scripts/` | everything to rebuild (own scene builder; does not import the city scripts) |

## The shared layout (same for A, B, C)
- 21 x 21 lot grid, pitch 24 BU (lot 16 + street 8), about 500 x 500 BU around the helix, plus an ordinary-city ring out to +-480 BU so the hero horizon is not empty. Lot plan is seeded (`--seed`, default 7), one plan for all directions.
- Plaza (r < 36 BU): pale disc with lime/pink ring lights, the helix on its drum. Greenbelt ring r 40-92 BU (trees, lamp beads, one park feature per ~5 park lots). Hospital Site SE of the helix at (108, -60), 2x2 lots, with a park apron so it is not hidden by towers.
- Solace fabric to ~r 150, then ordinary purple/amber city fades in (probability ramp 150-245 BU), as in the plate.
- Heights: Solace towers 16-44 BU (low near the helix so the 86 BU landmark stands clear); ordinary 24-68 BU.

## Landmark (identical in all three; ART_BIBLE 2.4 + DIRECTION_REVIEW 2026-10-16)
Two strands, each one full 360 deg turn over 83.5 BU (tube r 3.4, centreline r 7.5), no centre tower. Per floor (4.2 BU): one flush bow-tie walkway deck, rung edges alternating lime / pink (base pairs), and two sideways-oval windows per strand (one facing the walkway, one outward), projected so the outlines are truly horizontal/vertical in the world; window faces are a translucent faux interior (warm / lime / pink, ceiling dark, mullion); every 5th outward window is a bright lime "node". Lit lime tube skin, pink crown halo + lime inner ring, soft lime beam. Brightest object in every frame.

## Directions
- **A Capsule grove (plate+)**: round capsule towers (22-gon, domed caps, neon ring under the cap), lime/pink grow-light ribbon windows, some stacked double capsules, low drums with rooftop greenhouse domes, glass bubble skybridges between neighbouring capsules, greenhouse domes in the greenbelt, pink beacons on masts. Hospital: big glass-domed drum + three capsule wings, lime cross beacon.
- **B Culture cells**: slim windowed core + 4-8 glass spheres budding off it (daughter cells, pink / lime nuclei), petri-dish plazas (glass rim, agar, colonies, ring lights) in the greenbelt. Hospital: sphere cluster round a big pink-nucleus hub.
- **C Clean ward**: porcelain-white 3-tier towers with lime glass bands, green terrace setbacks with trees, a vertical greenhouse strip on one face, a crown of 7 slabs each twisted 11 deg (helix-twisted), low clinic wings with roof gardens, reflecting-pool plazas. Cool-white fill lights; pink only as small beacons. Hospital: porcelain cross plan with a helipad.

## Render settings
- Map: Eevee (`BLENDER_EEVEE`), 24 TAA samples, materials = Diffuse -> ShaderToRGB -> constant 3-stop ramp x base colour (bands 0.30 / 0.58 / 0.95), windows and neon flat emission, low-poly (half segment counts), flat shading, "Standard" view transform. Ink is NOT Freestyle: Freestyle stroked only pad borders at 1 px and a retry hung for 10+ min on the merged meshes, so ink is a second Eevee pass (`--mode ink`: R = building id, G = facing, B = depth, no AA) edge-detected in `ink.py` (id change, crease, depth jump), thickened 2.6 px at 1920, wobbled with sine displacement, composited in `#06031A`-ish violet-black. `post.py map` adds light spill (blurred saturated highlights) and a violet far-haze toward the top of frame.
- Night: Cycles HIP (RX 6700 XT), `device=GPU`, 72 spp adaptive, OIDN (GPU), max bounces 7 / transmission 6, volume fog density 0.00038 (aniso 0.35), moon sun 0.28 + lime/pink point lights, "Standard" view transform, exposure -0.6. `post.py night`: gentle bloom + vignette.
- Render times (GPU lock held): map Eevee 12.6 s (A), 5.8 s (B), 12.2 s (C) + ~5 s ink pass each; night Cycles 115 s (A), 70 s (B), 58 s (C) of render, 2.1 / 1.3 / 1.1 min wall incl. scene build. Test renders: 640x360 at 24 spp 5 s; 1280x720 at 48 spp ~110 s.

## Rebuild
```
set B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
%B% --factory-startup -b --python scripts/sd_main.py -- --dir A --mode map   --size 1920x1080 --scale 330 --out A_map_raw.png
%B% --factory-startup -b --python scripts/sd_main.py -- --dir A --mode ink   --size 1920x1080 --scale 330 --out A_ink.png
python scripts/ink.py A_map_raw.png A_ink.png A_map_inked.png 2.6 && python scripts/post.py map A_map_inked.png A_map.png
%B% --factory-startup -b --python scripts/sd_main.py -- --dir A --mode night --size 1920x1080 --spp 72 --out A_night_raw.png   (take the GPU lock first)
python scripts/post.py night A_night_raw.png A_night.png
python scripts/sheet.py <this folder> sheet.jpg
```
`scripts/run_final.sh`, `run_night_final.sh`, `make_map.sh` are the exact batches used (paths point at `D:/rc_scratch/solace_v1/district`; `batch.py` + `gpu_lock.py` take the shared GPU lock with `ME = "solace_v1"`). Other args: `--dir A|B|C`, `--seed N`, `--cam x,y,z,tx,ty,tz`, `--device CPU` (low-res tests), `--scale N` (ortho BU).

## Findings / caveats
- Blender 5.2: a point attribute named `uv` is reserved and silently reads as zero in Cycles (Eevee read it); the shaders use `cuv`. A default factory scene's Freestyle lineset has no linestyle, which makes Freestyle report "strokes set empty".
- `gpu_lock.py` from art_deco deadlocks against another waiter (each yields to any `GPU_WAITING_*`). The local copy never keeps its waiting file while an older waiter exists. art_deco's own helper still yields to anyone, so a newer waiter must stay out of the way.
- Weak spots: B's pink nuclei are subtle in the night hero (lime ones read white); A hospital dome reads pale in the map; C crowns are busy at map scale; helix interior gets dense ink in the map (rung edges + window rims). Hospital identity is a standing lime cross beacon (no text).
- Not done / not decided: no Godot material mapping yet, no bubble skybridges in B/C, no pink-heavy variant. Pick a direction (or a mix, e.g. A towers on the C plaza) and the next round can specify the Godot kit.
