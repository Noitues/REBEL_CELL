# Art deco cyberpunk concept stills (2026-10-20)

Seven panels from `BRIEF.md`. Each `NN_*_deco.png` is 1920 x 1080; `NN_*_sbs.jpg` is current (left) vs deco (right) on the same
camera; `contact_sheet.jpg` is all seven (2560 px wide). Every image is a Cycles render (AAA-2 pipeline: volume fog, PBR, wet
ground, light streaks) except panel 7 (PIL over panel 6). Nothing in the base pipelines was edited: the runners patch the base
scene sources in memory at run time and send every output to `D:/rc_scratch/art_deco/`.

## What deco changes, per panel
1. **Whole city** (A2 hero camera, `deco_city.py`; v3 = v2 without the corp crown towers, per the designer; `01_whole_city_v2_v3.jpg`): cool
   near-black lacquer fill (blue-grey grid and windows, no gold on ordinary towers) in a blue-charcoal fog with a thicker low layer
   (fog_peak 0.16, fog_base 0.10, fog_h 40). Each landmark keeps its stepped gold plinth, ground sunburst, crossed fan crown with spire
   and gold searchlight fan; beams, traffic, water and camera unchanged. Median 0.160.
2. **Halcyon** (`deco_corp_halcyon.py`): the seven tiers keep the pyramid, now with a gold cornice, stepped merlons, chevron band and
   corner piers per tier, triple violet lines on each setback edge, amber double lines above; the Eye is a sunburst fan crown.
3. **Meridian** (`deco_corp_meridian.py`): the gantry (legs, span, keep, corner towers) in gold fluted piers with chevron hazard bands,
   stepped crowns, orange triple-line neon up the legs and along the span, a fan crown behind the keep.
4. **Orbital** (`deco_corp_orbital.py`): the pad is a sunburst (48 pairs of ice-white lines + gold inlay arcs), the silo and podium step in
   gold rings, the dish bunkers sit on concentric rings, the antenna is a stepped sheath with a fan crown. The rocket keeps its slim
   silhouette (gold bands hugging the body, ice lines, three streamline fins).
5. **Solace** (`deco_corp_solace.py`): the helix in brass ribs (a gold annulus on every floor, double on route floors), lime / pink
   double lines run both strands, the plaza podium steps in three gold tiers, a crossed fan crown over the Genome Core.
6. **Netrun street** (`deco_street.py`; v5, `06_netrun_street_v4_v5.jpg`): v4 without the hero crown (designer: wrong at street level). The canyon-axis gap is
   filled with an ordinary deco frontage (same piers, spandrels, windows, shopfront as its neighbours); the lit-window share is back to about 60 %. Everything
   else as v4: lens 26 with a small upward shift, near-black clearcoat frontages, fluted gold piers, framed dark-glass amber windows with capped emission,
   bulb-lit shopfronts, gold-framed signs, globe lamps, wet asphalt, gold and fog on separate light paths (glossy-only cards, volume-off warm lights, a fog-only
   cool light, no light linking). Median 0.149, 735 s at 36 spp (48 spp ran over 20 min; I stopped my own Blender and re-ran at 36).
7. **Combat wheel** (`deco_panel7.py`): the round-41 typical screen rebuilt over panel 6. A (`07_combat_A_deco.png`): frame only, brass
   bezel steps, 30 tick rays with chevrons, stepped hub collar. B (`07_combat_B_deco.png`): also the slices: gold inlay edges with
   neon pairs in each slice's own colour, three stepped (setback) outer arcs, a sunburst hub medallion, a spire pointer. The CRT
   slice art, glyphs and the bare-Anton numbers are untouched. `07_combat_sbs.jpg` is current | A | B.

## Shared look (`deco_restyle.py`)
Lacquer facade (base 0.16 x original, coat 1.0), gold leaf (metal 1.0, tiny emission so thin gold never dies), brass trims, neon as
thin parallel box lines (2-3 lines, 0.06-0.3 BU), fan crowns (concentric gold arcs, ribs, neon arcs), Ferriss fog: warm charcoal
scatter (0.70, 0.66, 0.62), a noise-banked upper veil, city glow lights neutral warm, floodlights at the foot of the tallest towers.
All randomness is `random.Random(seed + index)`.

## Rebuild (Windows, Blender 5.2 headless, GPU lock `D:/rc_scratch/GPU_LOCK` via `deco_gpu.py`)
```
S=docs/concepts/art_deco/scripts
python $S/deco_gpu.py <label> <log> -- python $S/deco_run_hq.py halcyon art g3 ';;' ... meridian / orbital / solace
python $S/deco_gpu.py <label> <log> -- python $S/deco_run_street.py g1 1920 48 'cfg={"target":0.16}'
python $S/deco_gpu.py <label> <log> -- python $S/deco_run_city.py g1 0.5 64 'cfg={"min_top":18,"min_half":1.1,"n_towers":500,"n_fans":40,"fan_k":1.2,"fan_half":1.6,"target":0.16}'
python $S/deco_panel7.py D:/rc_scratch/art_deco/street/v2/plate.png D:/rc_scratch/art_deco/panel7_A.png   # also writes panel7_A_B.png
python $S/deco_pack.py
```
Look-dev previews: `prev.sh <corp> <tag>` (CPU, 960 x 540, 8 spp, no lock); `deco_run_city.py ... cpu`; `deco_run_street.py ... cpu`.

## Values and timings (RX 6700 XT, HIP, OIDN, 1920 x 1080)
| Panel | spp | render + build | frame median (luma) |
|---|---|---|---|
| 1 city (v3) | 64 | 119 s wall | 0.160 |
| 2 Halcyon | 56 | 88 s wall | 0.169 |
| 3 Meridian | 56 | 90 s | 0.169 |
| 4 Orbital | 56 | 85 s | 0.169 |
| 5 Solace | 56 | 108 s | 0.161 |
| 6 street (v5) | 36 | 735 s | 0.149 |
| 7 panels | none (2D) | about 20 s | A 0.133, B 0.141 (a dark HUD) |
HQ and city post: the pipelines' own finishers (`hq_post.finish`, `post_city.aaa --soft`) with the exposure solved to the target
median; the HQs use a cooler grade (shadow tint 0.50 / 0.50 / 0.52, saturation 0.80). The street uses `r2_compose.solved`.

## Known weak points
- Panels 3 and 5 are the least deco: the lacquer / gold city fill reads as warm mud next to the corp hue, and the landmarks sit in it.
- Panel 6: the fog veil is moderate, not Ferriss-thick; no focal point up the canyon now; gold is still yellowish; windows are framed, not recessed.
- Panel 1: tower ornament is tiny at this distance; the landmark fans and sunbursts carry the read.
- Panel 7 B: the spire pointer overlaps the base needle slightly.

## Halcyon v2 (graded Chrysler arcs; `02_halcyon_deco_v2.png`, `02_halcyon_v1_v2.jpg`)
Exploratory variant, `deco_corp_halcyon.py` with `d.v2=true`. Stainless-white (not gold) sunburst arcs stand on the four corners of the top four tiers,
graded 4.5 / 6.5 / 9 / 12 BU from low to high so the pyramid reads as one crown rising to the Eye (whose gold sunburst stays the only gold). Each arc has radial ribs and the triangular
windows between them lit violet #B06EFF from inside. v7's violet setback lines, the camera and the city fill are unchanged.

## References (read only; nothing downloaded or copied)
| Source | Trait taken |
|---|---|
| [Chrysler Building](https://en.wikipedia.org/wiki/Chrysler_Building) | A crown of seven concentric terraced arches, ribbed and riveted in a radiating sunburst of Nirosta stainless steel, with triangular vaulted windows (smaller copies on the setbacks), a steel needle spire, and lit by tube lights framing the windows plus floodlights. Taken: radial ribs, stainless metal, triangular windows lit from inside, stepped arc sizes. (Seven arcs per crown was cut to one per corner per tier, graded across four tiers, to avoid busyness.) |
| [Empire State Building](https://en.wikipedia.org/wiki/Empire_State_Building) | Symmetric base / shaft / capital with sharp setbacks and a mast; coloured floodlights at night. Taken: arcs sit on each tier's corner, growing toward the top. |
| [Guardian Building](https://en.wikipedia.org/wiki/Guardian_Building) | Mayan-revival deco built from geometric coloured brick, terra cotta and tile rather than figurative ornament; Monel instead of brass. Taken: geometric, coloured (violet) window fields and a non-gold metal accent. |
| [Aztec Hotel](https://en.wikipedia.org/wiki/Aztec_Hotel) | Abstracted Maya forms mixed with deco (the page gives no concrete detail). Taken: the ziggurat stays the base form. |
| [Hugh Ferriss](https://en.wikipedia.org/wiki/Hugh_Ferriss) | Setback studies, buildings in fog and soft focus, spotlights, shadows as important as lit surfaces. Taken: the fog veil and a dark base; the arcs read as lit shapes against it. |
Not found in the pages read: 30 Rockefeller Plaza was not fetched; Ferriss page does not confirm light from below.
