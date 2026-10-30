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
