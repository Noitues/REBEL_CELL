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

---

# v2 and v3: 1950s pulp retro-futurism / Raygun Gothic (2026-10-21, exploratory)

Files: `orbital_retro_v2.png`, `orbital_v1_v2.jpg` (v1 | v2), `orbital_retro_v3.png`, `orbital_v2_v3.jpg` (v2 | v3). v1 is kept. Scripts: `sa2_*.py` (v2), `sa3_*.py` (v3), `sa2_pack.py`, `sa3_pack.py`.
Helpers `sa_restyle.py` (v1) and `deco_restyle.py` (art deco, read only) are imported; the base pipeline is untouched.

## Research for v2 / v3 (pages read only; trait taken)
- Raygun Gothic, https://en.wikipedia.org/wiki/Raygun_Gothic : single-support beams, acute angles, motion cutouts, brightly coloured panels; used for the bell towers on one tapering support and the swept fixed fins.
- Moonliner (Tomorrowland 1955), https://en.wikipedia.org/wiki/Moonliner : V-2 based, portholes, red/white livery, tallest object in the park (76 ft); used for the tall rocket with a porthole ring and a red-orange / white scheme read at a glance.
- Chesley Bonestell, https://en.wikipedia.org/wiki/Chesley_Bonestell : slim tapered body on four enlarged tail fins (Destination Moon), strong angled light from one side; used for the v2 big swept fins and the single-direction spotlights.
- Frank R. Paul, https://en.wikipedia.org/wiki/Frank_R._Paul : huge machines dominating the frame, bright colours, concept before figures; used for scale (rocket, saucers and dishes much larger than the rooms) and one dominant hero.
- Atomium, https://en.wikipedia.org/wiki/Atomium : spheres linked by tubes read as an atom at any distance, metal cladding, meridian lights; used for the three-orbit atom symbol and chrome tank spheres.
- Googie (Las Vegas sign), https://en.wikipedia.org/wiki/Googie_architecture : starburst as high-energy ornament; used for the v2 starbursts (removed in v3 by the designer).
- Disneyland Monorail, https://en.wikipedia.org/wiki/Disneyland_Monorail_System : single straddle beam, bubble-top cab, red / blue livery; used for the single-beam loop, three-car bullet train and station.
- Forbidden Planet, https://en.wikipedia.org/wiki/Forbidden_Planet : a huge disc-shaped C-57D (170 ft) in a desert; the page gave no shape detail, used only for the saucer scale. Flash Gordon serial, The Jetsons: pages gave nothing buildable (Jetsons: buildings on tall adjustable columns, which is the saucer-on-pylon idea).
- Saturn V (v3 stack): from general knowledge, not fetched: white stages, black roll-pattern panels, black interstages, escape tower.

## v2 (retro_v2): critique
- Reads: finned chrome / white rocket, atom tower with nucleus and orbits, three bubble domes, two saucer bell towers, monorail ring with turquoise train, three starbursts. Rocket is the brightest element and the atom emblem on the deck ties to the tower.
- Fails: everything glowed (neon at full strength), so shapes dissolved into bloom; two atoms (deck emblem and tower) competed; the starbursts read as sparklers; the buildings had no function; the bell towers were big grey mushrooms; the monorail read as a white ring road.
- Timing: first preview-driven GPU attempts with a transmission glass dome ran over 30 min and were killed (my own PID), so the domes became alpha glass. Final: 24 spp (the glass is slow), 801 s wall, median 0.157. Noisier than the 52 spp finals.

## v3 (retro_v3): what changed and critique
Designer notes applied: dimmer emissives (ice neon 1.6, white emit 0.08, city window boost 0.2, exposure target 0.14); the atom tower is gone and the atom symbol is the graphic on the launch bay doors (navy half-discs r 40, chrome rim, seam, nucleus plus three orbits); the rocket is a finless Saturn V style stack (white stages, black roll panels, black interstages, chrome stage rings, porthole ring, capsule, escape tower) with four large fixed fin structures on the launch ring (chrome with tangerine inset, foot block, rails to the stack); all starbursts removed; each building has a role:
- top left: mission control (white drum, curved window wall, radome, two dishes); left: broadcast studio (ON AIR sign, three dishes, TV lattice mast); top right: vehicle assembly hangar (tall door slot, low wings, emblem, roof dishes); far right: crew tower (bell, shaft, observation saucer, beacon); near right: fuel tank farm (three chrome spheres on legs, two horizontal tanks, pipes); near left: the antenna truss as uplink mast (dish array and a large dish); behind the rocket: the orange gantry with white swing arms; front: monorail station with an upswept canopy and a round sign, three-car train.
Preview critiques before the final (each viewed): b1 had the atom too small and hidden by the fins, the big dish covered the ON AIR sign and the tank spheres read as flat grey discs; b2 fixed the atom (doors r 40, bigger orbits and electrons), moved and shrank the dish, chrome tanks; b3 moved the sign clear of the dish, added the monorail sign and moved the train to the station.
Final squint test (view of `orbital_retro_v3.png` at thumbnail): the rocket with fins and the atom bay doors read at once, ON AIR, the hangar door and the saucer crew tower read, the monorail loop reads as a rail, the city is darkest. Weak: mission control reads as a plain drum (the window wall is a thin bright strip); the fuel farm spheres are grey and low contrast, the monorail station canopy looks like a bridge from this angle and the train is hidden under it; the fixed fins look like tent flaps from the camera, not quite tail fins; the city windows are still a white pin-dot field; the left uplink dish overlaps the studio.
- Timing: v3 final 52 spp, 1920x1080, 218 s render wall (345 s with the lock batch), median 0.145 (target 0.14); lock wait 3900 s.

## Rebuild (v2 / v3)
```
S=docs/concepts/hq_styles/orbital_spaceage/scripts
bash D:/rc_scratch/hq_styles/orbital_spaceage/prev3.sh <tag>        # CPU preview of v3 (prev2.sh for v2)
SA_SPP=52 python $S/sa_gpu.py "art_spaceage orbital v3" <log> -- python $S/sa3_run_hq.py art final3
SA_SPP=52 python $S/sa_gpu.py "art_spaceage orbital v2" <log> -- python $S/sa2_run_hq.py art final2 samples=24
python $S/sa3_pack.py D:/rc_scratch/hq_styles/orbital_spaceage/r3/final3/plate.png     # orbital_retro_v3.png + orbital_v2_v3.jpg
python $S/sa2_pack.py D:/rc_scratch/hq_styles/orbital_spaceage/r2/final2/plate.png     # orbital_retro_v2.png + orbital_v1_v2.jpg
```

---

# v4 (designer-approved changes on v3, 2026-10-21)

Files: `orbital_retro_v4.png`, `orbital_v3_v4.jpg` (v3 | v4). Scripts: `sa4_restyle.py`, `sa4_run_hq.py`, `sa4_blender_hq.py`, `sa4_pack.py` (v3 and v2 kept).
Changes: (1) fixed fins are now tall tail fins hugging the stack (raked leading edge, short vertical trailing edge, tip above the first stage ring), white enamel with an orange leading edge, on a white foot block; (2) the atom on the bay doors has bigger orbits (minor radius 20.5 clears the fins) and a tangerine nucleus ring round the stack's base, so no line runs under the rocket; (3) mission control: wide warm-lit panoramic window wall (156 deg) with two rows of dark console / monitor silhouettes, chrome mullions and a large rooftop dish aimed at the camera; (4) fuel farm: bright white spheres with two orange bands on chrome legs, two white horizontal tanks, twin pipe runs up the podium wall to a manifold at the launch ring; (5) hangar: 64-tall high bay with a 10 x 56 door slot (chrome frame, segment lines), tangerine and ice stripes down the facade, flag mast with a striped banner; the roof dishes (they read as projector reels) are gone; (6) monorail station: platform and upswept canopy on the inner side of the beam, round sign on a pole, the three-car train stands on the beam in front of it (the canopy no longer spans the beam).
## Critique (previews c1, c2 and the final, each viewed)
- c1: fins, atom, hangar and tank farm worked. The canopy on the outer side hid the train and looked like a bridge or pergola, so in c2 the station moved to the inner side: the train is now visible. The canopy is still a plain grey slab from this angle.
- Squint test against v3: the stack with its tall fins now reads as a finned rocket, the orbits ring the launch pad cleanly, the hangar reads as a tall building with a door slot rather than a projector, the tank farm reads as tanks. Value order holds: rocket, then doors, then buildings, then city.
- Weak: mission control's silhouettes are only legible in the full-size image (a warm band at thumbnail); the pipe runs are thin dark lines that vanish at thumbnail; the monorail canopy is flat grey; the hangar banner is tiny; the fin foot blocks read as a plain white ring base; the left uplink dish still touches the ON AIR sign.
- Timing: 40 spp, 1920x1080, render wall 271 s (412 s with the lock batch), median 0.145. A first attempt at 52 spp ran over 20 min while another agent's Blender was also on the GPU, so I killed my own PID (29828) and re-queued at 40 spp. Lock waits 2553 s and 1952 s.
## Rebuild
```
S=docs/concepts/hq_styles/orbital_spaceage/scripts
bash D:/rc_scratch/hq_styles/orbital_spaceage/prev4.sh <tag>
SA_SPP=40 python $S/sa_gpu.py "art_spaceage orbital v4" <log> -- python $S/sa4_run_hq.py art final4
python $S/sa4_pack.py D:/rc_scratch/hq_styles/orbital_spaceage/r4/final4/plate.png
```
