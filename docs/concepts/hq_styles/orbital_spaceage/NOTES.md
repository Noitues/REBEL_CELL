# Orbital Commons in space-age retrofuturism (2026-10-21, exploratory concept)

`orbital_spaceage.png` (1920 x 1080, golden-plate overview camera, Cycles GPU) and `orbital_spaceage_sbs.jpg` (current golden plate | art deco | space-age).
Style change: the silo crescent keeps its layout (podium, silo, door leaves, five stations, gantry, truss antenna) but is re-skinned in white fibreglass,
brushed aluminium and international orange against black. Dishes become octagonal saucer pods (orange underside, ice window band, skylight ribs) on Y
pylons; the platform gets two parabolic launch arches flanking the rocket, a starburst deck (kite rays, atomic nodes, orange ring) and white launch-table
posts; the rocket is a white ogive needle (black roll band with ports, orange bands and tip, four swept fins) lit by four spotlight posts on the platform
edge (no pad flood: base pad floods x0.35, rocket service light x0.2); the antenna gets a Space Needle saucer and Ostankino-style guy cables; the gantry is
orange with white swing arms. City fill: steel-blue lacquer grid, ice-white windows, red signs and neon hidden, steel-blue fog.

## Timings and values (RX 6700 XT, HIP, OIDN)
- Final: 1920 x 1080, 52 spp, 985 s wall (GPU shared with other agents), median luma 0.157 (target 0.16, exposure solved in 4 steps). Lock wait 2401 s.
- Look-dev: v1 to v5, CPU 1280 x 720, 8 spp, 3 to 4 min each (mostly the scene build).

## Rebuild (Windows, Blender 5.2 headless; scratch D:/rc_scratch/hq_styles/orbital_spaceage/)
```
S=docs/concepts/hq_styles/orbital_spaceage/scripts
bash D:/rc_scratch/hq_styles/orbital_spaceage/prev.sh <tag>          # CPU preview: sa_run_hq.py mini <tag> cpu=true samples=8 res=[1280,720] fog_k=2
SA_SPP=52 python $S/sa_gpu.py "art_spaceage orbital final" <log> -- python $S/sa_run_hq.py art final     # GPU lock, one batch
python $S/sa_pack.py D:/rc_scratch/hq_styles/orbital_spaceage/final/plate.png                              # writes the png + sbs jpg
```
`sa_run_hq.py` imports the base pipeline (`route_map_graph/hq_orbital/scripts`) and `sa_blender_hq.py` execs its `hq_scene.py` with `sa_restyle.apply` inserted
before the render section; `sa_restyle.py` reuses helpers from `art_deco/scripts/deco_restyle.py` (read only). `gpu_lock.py` defers only to older waiting files (FIFO).

## References (pages read only; trait taken)
- LAX Theme Building, https://en.wikipedia.org/wiki/Theme_Building : white crossed arches over a saucer on legs; used as two white parabolic arches (z = H(1 - t^2), tapering thicker at the feet) with footings and an ice line on the intrados.
- TWA Flight Center, https://en.wikipedia.org/wiki/TWA_Flight_Center : Y-shaped piers, winged shells with skylight gaps between them; used as Y-forked pylons under the pods and radial ice ribs on the saucer tops.
- Space Needle, https://en.wikipedia.org/wiki/Space_Needle : hourglass profile, saucer with an accent colour (Re-entry Red / Galaxy Gold roof), skybeam; used as the hourglass flare and saucer with orange underside on the antenna.
- Launch Complex 39, https://en.wikipedia.org/wiki/Launch_Complex_39 : launch tower with retractable swing arms, mobile launcher platform on pedestals; used as white box swing arms with orange tips and eight pedestal posts round the silo.
- Ostankino Tower, https://en.wikipedia.org/wiki/Ostankino_Tower : tapering concrete shaft with a cone base, braced by taut steel ropes; used as three thin guy cables to the antenna top and a flared base ring.
- Chemosphere, https://en.wikipedia.org/wiki/Chemosphere : an octagonal pod on one tapering concrete column; used as the 8-sided pod shape on a single tapering column.
- Googie architecture, https://en.wikipedia.org/wiki/Googie_architecture : starbursts, atomic ornament, bright accent colours, neon; used as the kite-ray deck starburst, atomic star nodes, the sputnik starburst on the PAD pylon, orange accent neon.
- Baikonur (https://en.wikipedia.org/wiki/Baikonur_Cosmodrome): the page gave no pad structure detail; no trait taken from it.

## Weakest points
- Pod bunkers under the saucers are still the base's blocky white boxes (the rooms need them), so the pods read well from above but sit on slabs.
- White surfaces are lit mostly by self-emission and fog glow, so they read a little flat and grey; the rocket spots give the needle only a modest edge.
- The arches are stiff and stand like tall poles from this camera; the antenna saucer is large and its red beacon light is still visible as a red dot.
- City windows read as a field of white pin dots (star-like), which is cool but a bit busy; no TWA-style upswept wing roof or boomerang canopy was added.
