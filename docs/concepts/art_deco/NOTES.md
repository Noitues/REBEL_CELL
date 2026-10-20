# Art deco cyberpunk concept stills (2026-10-20)

Seven panels from `BRIEF.md`. Each `NN_*_deco.png` is 1920 x 1080; `NN_*_sbs.jpg` is current (left) vs deco (right) on the same
camera; `contact_sheet.jpg` is all seven (2560 px wide). Every image is a Cycles render (AAA-2 pipeline: volume fog, PBR, wet
ground, light streaks) except panel 7 (PIL over panel 6). Nothing in the base pipelines was edited: the runners patch the base
scene sources in memory at run time and send every output to `D:/rc_scratch/art_deco/`.

## What deco changes, per panel
1. **Whole city** (A2 hero camera, `deco_city.py`; v2 after the AD notes, v1 kept in `01_whole_city_v1_v2.jpg`): the city fill is
   near-black cool lacquer (grid and windows blue-grey, no gold on ordinary towers) in a blue-charcoal fog with a thicker low layer
   (fog_peak 0.16, fog_base 0.10, fog_h 40). The tallest 4.5 % of towers per district (at least 6 each, 32 in frame) are rebuilt as
   Ferriss shafts: a stout lacquer body with three setbacks (about 80 %), gold cornices and corner piers, parallel neon in the
   district's corp hue, a crown scaled 2.2x (fan arcs and spire), and a warm floodlight from below. Landmarks keep their stepped
   gold plinths, ground sunbursts, crossed fan crowns and searchlights; beams, traffic, water and camera unchanged. Median 0.160.
2. **Halcyon** (`deco_corp_halcyon.py`): the seven tiers keep the pyramid, now with a gold cornice, stepped merlons, chevron band and
   corner piers per tier, triple violet lines on each setback edge, amber double lines above; the Eye is a sunburst fan crown.
3. **Meridian** (`deco_corp_meridian.py`): the gantry (legs, span, keep, corner towers) in gold fluted piers with chevron hazard bands,
   stepped crowns, orange triple-line neon up the legs and along the span, a fan crown behind the keep.
4. **Orbital** (`deco_corp_orbital.py`): the pad is a sunburst (48 pairs of ice-white lines + gold inlay arcs), the silo and podium step in
   gold rings, the dish bunkers sit on concentric rings, the antenna is a stepped sheath with a fan crown. The rocket keeps its slim
   silhouette (gold bands hugging the body, ice lines, three streamline fins).
5. **Solace** (`deco_corp_solace.py`): the helix in brass ribs (a gold annulus on every floor, double on route floors), lime / pink
   double lines run both strands, the plaza podium steps in three gold tiers, a crossed fan crown over the Genome Core.
6. **Netrun street** (`deco_street.py`): every frontage on the route street gets a solid black-lacquer skin (floodlit from below by a
   material gradient), fluted gold piers running past the roofline, gold spandrels with parallel neon, lit windows, chevron panel,
   stepped parapet, three setbacks with a fan crown or spire, gold-framed marquee signs (signs pushed proud), deco globe lamps, Ferriss
   fog above the 3rd floor. Nothing floats in front of a facade.
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
python $S/deco_panel7.py D:/rc_scratch/art_deco/street/g1/plate.png D:/rc_scratch/art_deco/panel7_A.png   # also writes panel7_A_B.png
python $S/deco_pack.py
```
Look-dev previews: `prev.sh <corp> <tag>` (CPU, 960 x 540, 8 spp, no lock); `deco_run_city.py ... cpu`; `deco_run_street.py ... cpu`.

## Values and timings (RX 6700 XT, HIP, OIDN, 1920 x 1080)
| Panel | spp | render + build | frame median (luma) |
|---|---|---|---|
| 1 city (v2) | 64 | 119 s wall | 0.160 |
| 2 Halcyon | 56 | 88 s wall | 0.169 |
| 3 Meridian | 56 | 90 s | 0.169 |
| 4 Orbital | 56 | 85 s | 0.169 |
| 5 Solace | 56 | 108 s | 0.161 |
| 6 street | 48 | 305 s | 0.165 |
| 7 panels | none (2D) | about 20 s | A 0.133, B 0.141 (a dark HUD) |
HQ and city post: the pipelines' own finishers (`hq_post.finish`, `post_city.aaa --soft`) with the exposure solved to the target
median; the HQs use a cooler grade (shadow tint 0.50 / 0.50 / 0.52, saturation 0.80). The street uses `r2_compose.solved`.

## Known weak points
- Panels 3 and 5 are the least deco: the lacquer / gold city fill reads as warm mud next to the corp hue, and the landmarks sit in it.
- Panel 6: the camera is close, so crowns and setbacks are above the frame; the fog veil is subtle; some globe lamps float at post tops.
- Panel 1: tower ornament is tiny at this distance; the landmark fans and sunbursts carry the read.
- Panel 7 B: the spire pointer overlaps the base needle slightly.
