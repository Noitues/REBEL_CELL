# Netrun in the city's cel look: zoom-in storyboard (Solace slice)

Designer ruling 2026-10-30 (DIRECTION_REVIEW, cohesion answers 1-3): the netrun and the HQ netrun share the city's look zoomed in; the bar is `golden_plates/street_overview.png` and `hq_rebel_cell_overview.png`; the street carries its part of the city's corp colours; procedural detail grows as the camera zooms; rules may bend.

## Files
| File | What |
|---|---|
| `frame1_city.png` | r42 plan frame, district "Solace / Greenline Ave / Blk 07" highlighted (dim outside, lime outline, label) |
| `frame2_district.png` | District zoom, a few blocks, 3/4 view toward the helix park |
| `frame3_netrun_street.png` | The playable netrun street |
| `frame4_solace_hq.png` | Solace HQ approach at street level, helix and park |
| `storyboard_sheet.jpg` | frames 1-4 in order |
| `ref_vs_new.jpg` | golden street_overview vs frame 3, golden hq_rebel_cell_overview vs frame 4 |
| `squint_frame1..4.png`, `squint_sheet.jpg` | 1/16-scale area reduction plus blur, back up to 960x540 |
| `scripts/` | `nr_scene.py` (Blender scene generator and renderer), `nr_post.py`, `nr_frame1.py`, `nr_sheet.py` |

Frames 2-4 come from ONE procedural district (`nr_scene.py`, seed 7) seen by three cameras, so the buildings, corp colours and route are the same objects at every zoom. Frame 1 is the real r42 render with an overlay. Rendered with Blender 5.2 headless (`--factory-startup`), Cycles CPU, 128 samples, OIDN denoise, then `nr_post.py`. Run: `blender -b --factory-startup -P scripts/nr_scene.py -- f3 out.png 128 100`, then `python scripts/nr_post.py out.png frame3_netrun_street.png f3`. Heavy renders live in `D:/rc_scratch/netrun_cel/` (not committed).

## Research (refs)
Fetched this session (search result summaries, not deep reads):
- Rainy Shinjuku and Kabukicho night photography: the Pexels "rainy tokyo night" search and the soredenacho "Tokyo After Dark" guide. Takeaways used: rain turns every surface into a mirror and every puddle carries the neon, so the wet street doubles the light; warm lantern amber against cooler night sky.
- Shinjuku Golden Gai (Wikipedia): narrow bars stacked with small signs, warm red/amber lanterns, dense overlapping signage. Used for the bay-by-bay storefront signs, hanging lanterns and blade signs.
- Hi-Fi Rush (Unreal Engine developer interview, Tango Gameworks): "no gradations, nothing that feels 3D", the goal was to be indistinguishable from the 2D concept art. Used as the shading rule: flat colour, hard steps, ink line.
- Cel shading overview (How-To Geek, Wikipedia "Cel shading"): lighting quantised into a few flat shades, outlines as a slightly larger black shape drawn behind the object. This is exactly the inverted-hull ink used here.

From general knowledge, NOT fetched, so treat as soft refs: Sable (Moebius-style flat colour fields with thin outlines, little texture), and Hong Kong (Mong Kok/Wan Chai) night streets where large vertical blade signs project over the pavement and overlap in depth. The blade signs (4.5 to 9 m tall, 1.7 m wide) and the stacked sign layers in frame 4 come from that.

In-repo refs: golden plates (see ref_vs_new.jpg), `tide_raid/G1_parity/r42/plan_r42.png` and `r43/compare_r42_r43.jpg` for the city look, `solace_vertical/hq/H_overview_v5.png` as the old AAA-2 helix.

## Lighting and shading recipe
- Everything is emissive flat colour. No scene lights. Cycles lets the emissive faces light the wet ground, so reflections are real.
- Facades: one world-space window shader on a single mesh. Cell 2.3 m by 3.0 m, window 60% by 46% of the cell, per-cell random lit/unlit and warm / corp-tint / cyan colour. Body colour from a per-vertex attribute (corp body colour), so one material serves every building.
- Cel bands: tone by height in constant steps (1.0 storefront zone, 0.78, 0.56, 0.4, 0.3, 0.24 above), side faces x +-0.28, roofs +0.35, floor lines and column lines 38%/20% darker. Hard steps only, no gradients.
- Ink: inverted hull per box. A copy enlarged by ~3.4 px (scales with camera distance) with back faces only, dark violet `#0b0516`, vertices jittered +-35% for wobble. Blender Freestyle gave empty strokes on the big merged meshes, so I did not use it.
- Neon: thin emissive beams (0.09 to 0.16 m) on parapets, corners, tier steps, sign frames, in corp colour at emission 2 to 3.2. Signs are a dark board, a neon frame, and text (Impact, Yu Gothic Bold for the kana) at emission 3.
- Ground: Principled, dark violet, roughness from two noise layers: stretched along the street for streaks, plus blobs for puddles (0.03 to 0.34). Light streaks are emissive strips on the far lanes.
- Depth: emission colour mixes to violet `#5a2a78` by camera distance (exp fog, max 75%). Light beams are crossed transparent quads with alpha fading along the length.
- World: gradient `#b04aa0` horizon to `#3d1a70` zenith.
- Post (`nr_post.py`): two-radius bloom on the bright pass, a hue-preserving soft clip so lime stays lime, violet shadow lift, mild S curve, rain streaks, vignette, 1 px chroma split, grain.
- Palette: Solace lime `#96FF46` rims, pink `#FF4696` accents; Halcyon violet, Orbital ice, Meridian orange, Rebel red, Aurelian verdigris as the other corps. Corp pick per building is a fixed pattern (about 60% Solace in the street block, 70%+ within 90 m of the HQ), not random, so the mix is stable.

## Proposed procedural detail per zoom (for the Godot port)
| Zoom | Appears |
|---|---|
| 0 City (r42 frame) | Cv2 facet volumes, corp-colour parapet rim and corner rims, roof mast with red or accent tip, avenue colours, park and helix. Nothing smaller than a window grid. |
| 1 District (frame 2) | Window grid shader on the walls (lit fraction per building), lit ground-floor strip in a shop colour, roof billboards (blank board plus emissive face), water towers, tier setbacks with their own rims, trees as flat facet blobs, route ribbon and node discs with poles. |
| 2 Street (frame 3) | Storefront bays (3.6 to 5.2 m): lit window with goods shelves, frame, slanted awning, sign board with a brand name, or a ribbed shutter. Blade signs (kana or stacked letters), AC units, vertical pipes, fire escapes, hanging lanterns, roof water tower and HVAC, roof sign boards with text, wires across the street, lamp posts and poles, vending machines, manholes, crosswalks, lane dashes, car light streaks, wet puddle roughness. |
| 3 HQ approach (frame 4) | Same street detail near the camera, plus the helix at full size: bevelled strands with neon rim, pink and lime rungs, cell pods, halo ring, plaza rings and spokes, pink and lime lawn pods, Solace pod buildings round the plaza. |

Rule of thumb for the port: detail is generated by distance from the focus (r2 around the camera for street detail, r1 for district strip detail), seeded by building id, so the same building always gets the same signs at every zoom. Keep text as meshes or a sign atlas, one draw call per sign family.

## Where rules bent
- Pink is used freely: sign neon, awnings, rungs, nodes, the helix halo. It is the Solace secondary, so it stays on theme, but it appears on the street, not only on unit screens (designer ruling 3).
- Non-Solace corp buildings appear in the Solace block with their own rim colours (violet, orange, red, verdigris, ice). Designer asked for weighting, not purity.
- Route colour: nodes are coloured by type (pink fight, yellow event, cyan rest, lime shop, white HQ), and the route line is lime. Node poles are 9 m tall with a diamond cap so the route reads from far away. These are not in the GDD; they are placeholders for readability.
- The street is 30 m wide and the south side is left open in frame 3 so a camera can see the whole north facade row; real streets in the city are narrower. The south side is built for frames 2 and 4.
- Camera for frame 3 is raised (19 m) so the wet ground and the route are visible. A ground-level camera flattens the route to a thin line.
- Heights, widths and signs are art-scale, not GDD-derived. No game rules were touched.
- Solace brand names are invented (SOLACE, LEAFLET, HELIX, CHLORO, BIO-TEA, PETAL, SPORE BAR, VIRIDIAN, GENEBAR, SOLACE RX, and so on). Other names (NOODLE, KARAOKE, PAWN, VOLTA, HOTEL, DATA, PHARMA) are generic, taken from the golden plate. No real brands. The kana strings are decorative; I did not check them with a native reader.
- "GREENLINE AVE / BLK 07" on frame 1 is a placeholder label, not a game name.

## Squint test (1/16 scale, blurred, see `squint_sheet.jpg`)
- Frame 1: the lit quad reads as the only bright block in a dark field. Pass.
- Frame 2: the helix and the lawn read as a clear right-hand mass, but the avenue is hidden behind near rooftops and the route is almost invisible; the helix top is cropped. Pass for the park, fail for the avenue and route. This is the weakest frame; it needs a camera that looks along the avenue and a lower south row (next round).
- Frame 3: reads as one street: a bright storefront band, a lime-yellow route running across the lower third with five blobs for the nodes, and a dark facade mass above. Pass.
- Frame 4: the helix is the strongest shape, the two facade walls frame it, and the avenue converges to the plaza. Pass.

## Gap to the golden plates
Frames 3 and 4 hit the *content* of the plates (cel facades, neon-edged signs, dense storefronts, wet street with reflections and streaks, water towers, fire escapes, wires, corp signs) but not the *finish*:
- The plates have far more small-scale detail per metre (hundreds of mid-size window panels, balconies, pipes, antennas, roof clutter). Mine is a clean toon with a regular window grid.
- The plates have a darker value structure and calmer saturation; my frames are brighter and more saturated overall, especially in frame 3, where the upper facades are lit more evenly than in the plate.
- The plates have painted texture, haze at street level and long coloured car streaks; mine has a flat shader, a fog tint and a few strips.
- Frame 3 has no sky or skyline silhouette (the back towers fill the frame), so it lacks the plate's silhouette variety. Frame 4 sky is a flat dark gradient.
- No searchlight beams are visible in the frames (they are in the scene but out of shot).
- Nothing animated, so the wheel/HUD layout and the combat backdrop are not tested here.


---

# v2 changes (files in `v2/`)

Designer feedback after v1: frames 3 and 4 read as Tron wireframe; frame 1 to 2 did not feel like a zoom; the HQ netrun is hand-authored. v2 answers all of it. Frames: `v2/frame1_city.png` to `v2/frame4_solace_hq.png`, `v2/storyboard_sheet.jpg`, `v2/ref_vs_new.jpg` (plates on the left), `v2/zoom_match.jpg`, `v2/squint_*`. The v1 files above are kept for comparison.

## Real city data (frames 1 to 3, and the city behind frame 4)
- Source: the r43 tide clone (`D:/rc_art/godot_look_tide`, branch art/tide-r43), the default plan capture (same as plan_a). I made an untracked copy of `parity_capture.gd` as `tools/look_parity/nr_dump.gd` in that clone (not committed there; `v2/scripts/mk_nr_dump.py` regenerates it). With `--lot-dump` it also writes every prism (footprint polygon, ground, height, territory, corp colour kind), every street, plaza and park lot, the HQ rects, the terrain height per lot and the iso camera. Committed copies: `v2/data/lots_city.json` (4756 prisms, 165 x 165 lots) and `v2/data/lots.json`.
- Frame 1 is that same capture (`nr_plan.png`, not committed, 4 MB) with a highlight polygon built from real lots (lots i -47..-29, j -31..-17) and the frame-2 zoom box. The helix, plaza and park are the real ones.
- Frames 2 to 4 are rebuilt in Blender from the dump (`v2/scripts/nr_city.py`, assembled by `mk_nr_city.py` from `nr_scene_v2.py` (look kit) and `nr_city_part.py` (layout)). Scale: 1 world BU = 2 m, so a lot is 12 m. Each building is the real lot footprint, real ground height, real height and real corp colour (CityCorpColor kind: 1 Solace, 2 Halcyon, 3 Meridian, 4 Orbital). Streets, parks and plazas come from the same lot sets. Ground is the real terrain per lot (smoothed at corners).
- Camera match proof: `v2/zoom_match.jpg`. Frame 2 uses frame 1's camera (yaw 135, pitch 40, ortho) at x3 on the block centre. Panels: the frame-1 crop of the zoom box, frame 2, a 50% blend, and frame 2's edges over frame 1. The plaza rings, park edge and tall-tower positions land in the same places. Separate proof of the data: `v2/scripts/nr_check_proj.py` projects every prism roof centre with the game's iso maths onto the capture, and they sit on the roofs.
- What does not match in frame 2: the elevated highway at left, the dense hand-placed tree canopy, the pods in the park and the Cv2 facet shading of frame 1 are not in the dump. I used box footprints (the game's towers are round or faceted), a simple taper step, and blob trees. Frame 2 is also graded darker than frame 1 (value notes below), brightened to bridge. It is a match in layout, heights, corp colours and camera, not in rendering.
- Frame 3 street: the real 3-lot-wide boulevard (rows j -26..-24, lots i -44..-30) with the park on its north side. The camera stands at the park edge looking south across it to the real row of buildings at j -23 and beyond. The corp mix there is whatever the data gives (about half Solace in the region: 121 of 248 buildings).
- Avenue check (designer item 2): the real street at lot row j -37 runs from i about -80 to -52 and ends at the park lawn, which continues to the Solace plaza (rect i -43..-34, j -42..-33, centre j -37). So a real avenue does point at the helix, to within half a lot. Frame 4 stands on it at lot i -78 and looks east. The stretch between the avenue end and the plaza is lawn, so the last part of the route crosses the park (an authored path, not a street).

## Real vs authored
- Real (from the data): lots, footprints, heights, ground, corp colour, which lots are street, park and plaza, which sides of a building face a street, the city skyline behind the helix, and the searchlight towers (the four tallest real buildings of each view).
- Procedural on top (seeded by the real prism key, so a building keeps the same signs at every zoom): windows, accents, storefronts, signs, blade signs, AC units, fire escapes, roof water towers and signs, lamps, pavements, car streaks.
- BESPOKE, hand-authored, NOT procedural: the Solace HQ set piece in frame 4 (also visible in frames 2 and 3): the helix (170 m, 2.6 turns, pink and lime rungs, cell pods, halo ring), the plaza rings and spokes, and the route's approach across the lawn. The Solace HQ stand-in prisms from the dump are removed and replaced by this set. The other three HQ stand-ins (Halcyon, Meridian, Orbital) stay as the data has them.
- Only the city behind the HQ matches the procedural city: in frame 4 the avenue, the buildings and the skyline come from the same data as frame 3.

## Designer notes, one by one
1. Value structure: facade bases are now about 10 to 20% value (body strength 0.5, down from 0.82; palette darkened; height bands softer). The lit storefront band (emission 2.2 to 3 plus a pavement spill quad) is the brightest horizontal in frame 3.
2. Selective neon: about 45% of Solace buildings and 28% of the others carry one accent (a parapet line, one vertical corner strip, or a crown). The rest have no glow, only the ink hull. Ink is thinner (2 px, dark, wobbly), never glowing. Corp colour lives in the accent, the window tint and the signs.
3. Windows: cell 0.95 x 1.25 m (a third of v1), irregular size per cell, 10 to 30% lit, warm amber majority, about 24% cool corp tint, a few cyan-white. Frame 2 uses x2.6 cells so they do not turn to noise at ortho scale.
4. Atmosphere: ground mist (Volume Scatter box, 8 m high, density 0.028), long red and white car streaks on the boulevard and the avenue, searchlight beams that fade along their length (up to four per frame, from real towers), a sky with a horizon glow and noise cloud, and a fog tint by distance. Frame 3 has a sky strip and a skyline (limited, see gaps).
5. Texture: facade grime (two noise layers, vertical streaks) multiplied into the cel bands, so the base stays flat.
6. Route markers: ribbon half-width 0.34 m (was 0.55), small ground discs (1.0 to 1.4 m), and only the selected node has a pole, marker and white ring. In frame 3 the route is the first read at squint through placement and contrast: it is the only continuous bright lime horizontal on a dark ground.
7. Frame 2 looks at the real block with frame 1's camera (see above), and frame 4 shows the helix uncropped.
Signs: kept the density and added blade signs with icons (cross, ring, leaf, drop, bars, helix, pill, bowl), roof billboards with a coloured panel, icon and text, and icon-bearing shop boards.

## Squint (v2, `v2/squint_sheet.jpg`)
- Frame 1: pass. The highlighted block is the lightest shape on a dark city.
- Frame 2: the park, plaza rings and the building mass read, but the route and the street do not (windows and buildings make a noisy mass at this scale). Fail for the route. It needs a calmer window grade or a wider route at ortho scale.
- Frame 3: pass. One lime line across the lower third with a single bright marker, a bright storefront band above it, and a dark facade mass. It reads as one street with a clear route.
- Frame 4: pass. The helix and the beams are the strongest shapes, the avenue's route is a bright vertical line to its base, and the real skyline is a clear dark band.

## Gaps vs the plates (v2)
- Closer in mood: dark facades, selective accents, small dense windows, a wet street with mist and long streaks, a sky, searchlights, bays of signs with icons.
- Still short: the plates have far more micro detail per metre (balconies, pipes, roof clutter, painted panel breakup) and a calmer palette (mine is more saturated, especially the purple sky in frame 4 and the amber windows). Their sign hierarchy is flatter and more graphic. Frame 3's real boulevard has tall buildings (up to 80 m), so tops are cut and the sky is only a strip; the plate shows whole towers against sky. Frame 4's lawn trees are low-poly blobs and read as toys, and the foreground ground is dark and empty. The helix is a plain tube, not the glass-and-cell look of the Solace brand sheet.
- Footprints are boxes, the facade style keys of the data are unused, and the Godot port will need its own window and sign systems. This is concept art only.

## Procedural detail per zoom, revised for real data
| Zoom | From the data | Procedural on top |
|---|---|---|
| City (frame 1) | everything: lots, heights, corp colour, parks, plazas, helix | nothing |
| District (frame 2) | same | window grid (2.6 m cells), corp accent on about a third of buildings, a lit ground-floor strip on the first street side, roof billboards on tall buildings, street colour lines, tree blobs |
| Street (frame 3) | same, plus which sides face a street | storefront bays, awnings, sign boards with icons, blade signs, AC units, fire escapes, lanterns, roof water towers and billboards, pavement and kerb, lamps, wires, car streaks, wet ground, mist |
| HQ approach (frame 4) | the avenue, the city behind, the park lots | the authored HQ set (helix, plaza, route across the lawn) |
Rule: detail level is chosen by distance in lots from the camera focus (street detail within about 16 lots, district detail within about 55), seeded by prism key.

## Process notes
- The windowed capture ran through the clone's `gpu_lock_run.py` and `run_windowed.py`, as its `run_capture.sh` does. `gpu_lock_run.py` registers the lock holder as "tide_g1", so the lock file named that session while my two short captures ran.
- Heavy renders are in `D:/rc_scratch/netrun_cel/v2c/` and the raw capture is in `D:/rc_scratch/netrun_cel/city/` (not committed). `nr_city.py` reads `lots_city.json` from `D:/rc_scratch/netrun_cel/city/`; the committed copy is `v2/data/lots_city.json`.
