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

## Round 2: direction D "Mixed bundles" (designer's pick)
Files: `D_map.png`, `D_night.png` (1920x1080), `sheet_r2.jpg` (A/B/C night thumbnails on top, D map + night below). Same lot plan, cameras and render settings as round 1.
- **Bundles**: `make_bundles()` in `sd_main.py` (`--dir D`). Seed points on a 2.6-cell jittered grid (seeded, deterministic), every lot joins its nearest seed (a bundle of about 3-9 lots, 5-8 typical), kits assigned greedily so neighbouring bundles differ and counts stay balanced (in the map frame: C 49, A 37, B 38 lots). Park-ring lots follow their bundle too (A greenhouse dome, B petri dish, C reflecting pool). A skybridges only join A towers inside an A bundle; C bundles get pale pads and cool-white fill lights; fill lights in C bundles only.
- **Hospital**: C's porcelain cross-plan hospital with helipad and the lime cross beacon, unchanged.
- **B toward lime** (D only): glass tint (0.62, 1.0, 0.32) night / (0.30, 0.74, 0.12) cel; pink nuclei 0.5 of the sphere radius (was 0.36) on a new `neon_p` material (strength 34 vs 9 for `neon_s`).
- **Helix fix**: the beam mesh (`helix_beam()`) is off for every direction now (`BEAM = False`); it read as a dark solid column on the map and a solid in Cycles. No light-shaft replacement: with the current fog density a spot shaft would not read as light. Re-rendering A/B/C with the current script therefore gives them no beam either (their round-1 PNGs keep it).
- **Rebuild**: `scripts/run_d.sh` (GPU lock; map raw, id pass, night), then `ink.py out/D_map_raw.png out/D_ink.png out/D_map_inked.png 2.6`, `post.py map ...`, `post.py night ...`, `sheet_r2.py <this folder> sheet_r2.jpg`.
- **Times** (1920x1080): map Eevee 7.6 s + id pass 1.3 s; night Cycles 87 s (72 spp adaptive, OIDN), about 2.3 min wall for the whole batch.

### Round 2b: D night fix (too bright, forms lost)
`D_night.png` re-rendered with `--dir D --mode night` (on by default for D night; `--n2 0` reproduces the first D night, kept as `D_night_r2a_bright.png`). Same camera and layout. Changes, all gated on `N2` in `sd_main.py`:
- Emission x0.35 everywhere (`sd_lib.EMIT_K`: windows, ribbons, clinic bands, glass, rings); ordinary-city windows and the helix windows/skin x0.55-0.6 (helix stays the brightest). Pink nuclei: `neon_p` x0.07 (they were clipping to white), lime nuclei `neon_l` x0.16, rungs/halo `neon_s` x0.3.
- Cool moon sun 0.28 -> 1.7 plus a faint violet counter-sun 0.35, brighter blue sky (horizon 0.07/0.07/0.16, zenith 0.018/0.026/0.06), exposure -0.6 -> -1.15, fog density 0.00038 -> 0.00018, helix lime point light 6e4 -> 3.5e4, C fill lights 5e4 -> 1.2e4, post bloom x0.35 (`post.py night in out 0.35`).
- C porcelain (towers, hospital) 0.80/0.83/0.80 -> warm grey 0.34/0.32/0.29; C pads 0.50 -> 0.16.
| 1920x1080 final, sRGB luma | before | after |
|---|---|---|
| median | 0.368 | 0.141 |
| mean | 0.469 | 0.210 |
| > 0.95 (clipped) | 7.73 % | 0.29 % |
| > 0.85 | 15.53 % | 0.74 % |
| < 0.05 | 0.0 % | 5.8 % |
Render 250 s (72 spp adaptive, OIDN; slower than before because more indirect light now matters). Tuning previews at 640x360 on CPU (`scripts/stats.py` prints the numbers).

## Round 3: raid zoom + daylight (direction D)
Files: `D_raid.png` (cel + ink, night), `D_raid_day.png` (cel + ink, day), `D_day.png` (Cycles AAA-2 daylight, same camera as `D_night.png`), `sheet_r3.jpg`. `D_night.png` untouched.
- **Raid camera** (`--view raid`): CityIsoCamera values, yaw 135 deg, pitch 40 deg, orthographic 300 BU wide (Godot yaw 135 maps to a camera at the SE looking NW in the Blender frame; forward = (-0.54, 0.54, -0.64)). Target (-24.8, -10.6, 0) puts the helix right of centre with the hospital low in frame. The hospital's cross beacon turns to face this camera (-45 deg) in raid mode only.
- **Night palette** (`--tod night --view raid`): toon bands 0.14 / 0.30 / 0.56 (were 0.30 / 0.58 / 0.95), dimmer cool sun 1.7 + faint pink fill, window emission x0.8, C porcelain grey-violet, bloom and haze reduced (`post.py mapraid`). Ink pass and ink.py unchanged (2.6 px). Median 0.21, 0.0% > 0.95.
- **Cel day** (`--tod day`): tinted 3-band ramp (cool shadow 0.52/0.58/0.90, warm mid 0.88/0.82/0.70, warm light 1.12/1.05/0.92), warm sun 3.2 + cool fill, windows dark glass blue, neon x0.45, daylight pads/streets/trees, blue sky and haze (`post.py mapday`). Median 0.56, 0.0% > 0.95.
- **Cycles day** (`--mode night --tod day`): warm sun 3.0 (elev 40) + blue gradient sky, no volume (any Principled Volume, even density 1e-4, blacked the whole scene in this setup, so haze is a post gradient `post.py dayhaze 0.22`), emission x0.03 (helix skin/windows x0.12 of that, rungs and halo faint, hospital cross `neon_x` x0.4 visible but subtle, nuclei faint pink), window cells become dark reflective glass (metallic 0.5, roughness 0.06) via `sd_lib.DAY`, leaf-green glass, warm-white porcelain (0.66/0.63/0.56) with sunlit setbacks, daylight pads and streets. Exposure +0.1, 72 spp adaptive, OIDN. Median 0.40, 0.9% > 0.95 (target 0.40-0.45, < 1%).
- **Times** (1920x1080): Eevee raid night 2.3 s + ink 1.4 s; raid day 2.1 s + 1.6 s; Cycles day 25 s render (about 45 s wall each with the build).
- **Rebuild**: `scripts/run_r3.sh` (all five jobs under the GPU lock), then `ink.py R3_raid_raw R3_raid_ink out 2.6` + `post.py mapraid`; same with `mapday` for the day raid; `post.py dayhaze D_day_raw.png D_day.png 0.22`; `sheet_r3.py <folder> sheet_r3.jpg`. `tr.sh` is the quick preview for the cel views.
