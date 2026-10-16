# TETHYS DEEP HQ: ATLANTIS STATION, round 2 (the floating pier city and the dam)

Concept and design pass for the Tethys Deep HQ after the designer review of round 1 (2026-10-16 morning). It is art
only: no game rules are set here. Room positions are plausible places for route nodes, nothing more. Nothing is
committed, and the Godot build is untouched.

The designer notes on the old close-up (`city_all_corps/tethys_flooded_closeup.png`):
1. On a good track, but not there yet.
2. More city clutter under the water.
3. A strong dam between the dry city and the drowned quarter.
4. A floating pier city (Kamino / Tipoca City), with the main HQ obviously the HQ.
5. Clearer water, with the caustics standing out.

The earlier direction also applies: explore dams and water locks, make the HQ fill its map lot, and keep the landmark
at about 2x its local background.

## 1. The concept in one line

**Tethys owns the waterline, so its HQ stands on it.** A white station city on stilts rises out of the drowned quarter,
and a massive dam holds that water above the dry streets. The only way in from the city is the company's own water
lock.

Three readable layers, front to back from the map camera:

| Layer | What it is | Its light |
|---|---|---|
| The dry city | Dense Tethys blocks, right up to the dam's service road | The city's own mixed light |
| THE DAM | Raw concrete wall: sluice gates, catwalks, pump houses, the DOCK LOCK | Sodium (warm) floods and uplights, amber warning strobes, red beacons |
| The drowned quarter + ATLANTIS STATION | Clear water over the drowned streets; the pier city on stilts; the deep stack under it | Cool white key, abyss-blue neon, photophore, the caustics |

The colour split is a rule: **warm = the dam and the dry city, cool = Tethys and the water.** The dam is the
temperature border, so the two zones separate even in a thumbnail.

## 2. The pier city (designer note 4)

All the shapes come from one generator, `_stack()` in `scripts/tethys_landmark.py`. Each pod is the station itself at a
smaller plan scale `s` and height scale `hs`. So the "small versions of itself" are literal: the same stilts, flared
skirt, lit drum, flattened dome and mast.

| Element | Plan / height scale | Size (BU) | Where |
|---|---|---|---|
| **Main station** | s 0.80, hs 1.05 | Drum r 10.4, cap to ~ZW+18, second tier r 5.3, mast to ~ZW+46 | Lot centre |
| Inner pods (6) | s 0.32, hs 0.42 | Drum r 4.2, with a second tier and a mini mast | r 20 on the six piers |
| Pier-end pods (6) | s 0.24, hs 0.32 | Drum r 3.1 | r 30.5, the ends of the piers |
| Ring pods (6) | s 0.19, hs 0.27 | Drum r 2.5 | r 26.5, between the piers |
| Piers | | Glass-tube walkways (deck, tube, ribs, photophore floor strip) on piles | Six radials, plus the hex ring through the outer pods |
| Stilts | | 10 under the station, 3-4 under each pod, dark (0.13, 0.15, 0.19), **down to the seabed** | Everywhere |
| Buoy fence | | 36 red buoys, every third lit abyss blue | The lot edge, r 34.5 |

**It fills its lot.** The outer pods reach r 33.7, the buoy fence sits at r 34.5, and the lot is
`city_preset.LANDMARK_FP["tethys"]` = a circle of r 34.

**One pier points at the DOCK LOCK** (rule: arm 0's bearing is the HQ to the lock). The causeway from the dam lands on
that pier's end pod, so the approach is one straight line: city, lock, causeway, pier, station.

**Why it reads as the HQ:**
- **Size.** The station is about 3x the plan size of the next-largest pod and 2.5x its height.
- **Silhouette.** Only the station has the second tier, the tall mast and the abyss-blue halo ring. That is the
  TIDE WHIRL read: one ring turning round a calm centre. The station also carries the hero beam.
- **Light.** The station is lit by a soft cool key spot (0.9e6) and an abyss-blue fill (0.45e6). Its hull is
  grey-white (0.50, 0.53, 0.58), and its windows are warm.
  - AD review 2: the station was 4.5-5x its background, so the key, the hull white and the hue rings came down
    (rings x 0.55), and warm window detail went in. Target: 2-2.5x.
- **The 2x rule.** Measured on the test renders (section 8): HQ peak against its local background is 5.0x on the
  close-up and 4.5x on the overview, and HQ mean against background is 2.4-2.5x.

**Kamino, but corporate.** Tipoca City's repeated disc pods on stilts, linked by walkways, with one dominant centre.
The Tethys versions are pressure hulls with porthole rings and ribbon windows: a spa-clean company town, not a palace.

**Pod detail (AD review 2).** Each pod has:
- warm ribbon window bands on the drum (window colour 1.0, 0.80, 0.52, x 1.25);
- lit portholes round the skirt (lit share 0.75) and in the cap;
- 2-3 small antennae with red or white tip lights;
- a tilted dish on 60 % of them;
- a mini mast with a red beacon.

The seed comes from the pod, so the details differ pod to pod.

**THE BREAKWATER (AD review 2).**
- **The wall:** the hexagonal ring walkway now stands on a solid breakwater, 1.8 BU wide, from ZW -4 to ZW +1.3,
  through the 12 ring pods. It has a photophore line on top and a faint surf line on the outer face.
- **Inside the ring the water is glass-calm.** It is a material rule on the water surface (`tethys_build.calm_water`):
  within 25.5 BU of the station (±3 BU soft edge) there is no surface chop, and the reflection is 0.20 x Fresnel.
  Outside, the chop is the halved preset value and the reflection is 0.5 x Fresnel.
- **Why:** the calm ring is the see-through window. You look straight down into the moon pool and the server.

**Below the water** (the clear water shows all of it):
- **The stilt forest.** Every stilt runs down to the seabed (about -110 in the trench), dark, with ring beams at
  -1.6 and -14 below the waterline.
- **THE DEEP STAIR.** Five small pressure decks (r 5.6 down to 4.0, lit porthole rims, abyss and photophore rings,
  four lit rooms each) at ZW -5 / -8.5 / -12 / -15.5 / -19.
  - They step down from under the station along a spine to the server.
  - The decks are linked by glass drops with the lift light inside.
- **THE MOON POOL.** A lit well straight down from a floating collar ring at the calm surface to the server. Its
  rings (r 4.6, every 3 BU) alternate white and abyss blue, with four guide rails.
- **The ballast column.** The tide gauge, a glass column with an abyss-blue water core and a photophore waterline.
- **THE BLACK SMOKER** at the foot of the moon pool (section 6).
- **The placement rule (found in the tests).**
  - From the 3/4 map camera, a thing at depth d projects d / tan(pitch) toward the camera. A deep stack straight
    under the station lands on the causeway and behind the dam's wet face.
  - So the server is shallow (ZW -23) and 16 BU to screen-left of the station, **inside the lot and inside the
    breakwater**. In the overview it projects into the calm water between the station and the front-left pods.
## 3. The dam and the lock (designer note 3; "explore dams and water locks")

### The line
The dam follows the drowned quarter's land boundary, so the rule rebuilds on any city layout. The boundary is every
wet-cell edge that faces a dry cell landward of the seawall. The line takes the minimum depth `b` within ±2.5 lots
for each 1-lot step across, smoothed twice with a ±6-sample moving average. It runs from a -88 to a +88 (1132 BU)
and meets the seawall at both ends.

The result is a U-shaped basin: a straight front across the frame, with curved flanks back to the coast. The old
stepped 4.2 BU levee walls are buried inside the dam body.

### The profile

| Part | Value |
|---|---|
| Wet face | Vertical, at +6 BU (toward the water), from the crest down to -42 |
| Crest | Road at z 12, between 1 BU parapets, with a hazard band on the dry parapet |
| Dry face | Upper slope to a berm catwalk at z 6.8 (-3.0 to -4.6 BU), lower slope to the toe at -9.5 BU |
| Counterforts | Ribs on the lower slope every 7 BU |
| Water held | ZW 2.5, against the dry street at 0, so the water stands visibly above the city |

### Along the line

| Feature | Rule |
|---|---|
| **Sluice gate bays** | Every 44 BU of arc, except near the lock and the ends. Each bay has two raked piers (buttress noses down the dry face, 18 BU high), a steel lift gate with a hazard-striped top, a hoist gantry and hoist house, red beacons, and a white-tick water gauge on each pier nose. The wet-face gauge's red line marks the water level |
| Open gates | Every third gate: the leaf is lifted and white water runs down the spillway chute (streaks of uneven brightness) into the toe canal |
| Closed gates | A dark culvert grate with a red light |
| **Pump houses** | Every other gate: a lit block on the crest, with three penstock pipes down the dry face |
| **Catwalks** | The wet face: a steel grating at z 5.2, with handrail, posts and cool lamps. The dry face: the berm walk, with handrail and sodium lamps |
| **Warning lights** | Amber strobes on the dry parapet every 4 BU (every third one bright). Red beacons on every gate pier |
| **Light on the face** | Floodlight masts on the crest every 26 BU. Sodium uplights from the apron road every 11 BU wash the dry face, so the dam reads as a lit wall between the dark city and the dark water |
| **Toe canal + apron** | A narrow canal along the dam toe (water plane, low walls), a service road, and a yellow kerb line. Dry buildings within -16 to +9 BU of the line are removed (458 buildings), so the dam stands free |

### The DOCK LOCK (the Site type's big brother, the HQ's front door)
The lock sits on the dam point nearest the HQ.

| Part | What it is |
|---|---|
| Chamber | 8 BU wide, cut through the dam, with walls 2.2 BU thick |
| Gates | Mitre gates at both ends (V pointing upstream, hazard-striped tops) |
| Water | The chamber water sits halfway between the drowned quarter and the canal |
| Crest | The crest road bridges the chamber |
| Signals | Red traffic lights at both gates (the ward is lapsed, so the lock is shut) |
| Control tower | Dry side, 24 BU, lit floors, a glass cab, an abyss-blue ring, a red beacon, its own floodlight |
| Dock basin | On the city side: quay walls, lamps, a moored sub with nav lights |
| Causeway | From the upper gate to the pier-end pod: a 4.2 BU deck on piles to the seabed, a glass-tube walkway with alternate lit ribs, abyss edge strips, lamp posts alternating photophore and dive-light |

## 4. The drowned streets (designer note 2)

### The depth rule (new; found in the tests)
In round 1, almost all of the drowned quarter that the camera sees sat in the Atlantis trench: 60-115 BU deep
(`city_preset.WATER["trench"]`, radius 13 lots = 78 BU). Any street clutter there is invisible, however clear the
water.

The rule (`tethys_quarter.reshape_depth`, `tethys_preset.DEPTH`), applied to the zoning copy:
- **The drowned quarter is a shallow street grid:** 5 BU deep at the dam, sloping to 24 BU at the seawall.
- **The trench is kept only round the station:** full depth inside 42 BU of the HQ, blended out to 66 BU.
- **Drowned towers:** a tower that would now break the surface is cut to 1.2-5 BU under it (142 towers). A seeded
  10 % outside 70 BU of the HQ stand out of the water instead (14 towers).

The read is a dense drowned city just under the surface, with the station standing over its own dark abyss.
**Adopted** (AD review 2): the city agent will take it into the full-city model.

### The clutter

The clutter is generated per drowned street tile within 480 BU of the HQ, seeded by the tile, plus per drowned
building face.

| Item | Rule (tethys_preset.CLUTTER) |
|---|---|
| Kerbs and markings | Kerbs on both sides. A dashed pale centre line (it catches the caustics) |
| Cars | Up to 3 per tile (p 0.70, falling per extra car), drifted ±0.35 rad. 12 % flipped. **22 % with their headlights still on** |
| Buses and containers | p 0.035 / 0.07, some on their side |
| Street lamps | p 0.60 per tile, 1-2 per tile. 60 % still lit (warm). 18 % leaning. Sagging cables between pairs |
| Signs | Green street signs (p 0.22). Billboards on posts (p 0.10, 65 % lit in the city neon colours) |
| Debris | 1-5 rubble pieces per tile |
| **Kelp cables** | 1-4 per tile where the water is over 4 BU deep: loose power and data lines rising up to 22 BU, swaying like kelp, with algae tufts. 90 % have a glowing photophore fibre end |
| Drowned fronts | Shop fronts at the old street level (p 0.50, 62 % lit) and blade signs (p 0.38, 55 % lit) on every drowned building face |
| **Lit drowned windows** | Every drowned facade's lit share raised to at least 0.62 (was 0.45). Wet window emission x 3.6 before the water fade (was x 2.6) |

**Counts in the test build (265 drowned street tiles within reach):**

| Item | Count |
|---|---|
| Cars | 340 |
| Lamps | 183 |
| Signs and boards | 91 |
| Kelp cables | 659 |
| Debris | 825 |
| Drowned shop fronts and blades | 952 |

## 5. The water (designer note 5)
The recipe is unchanged (`water_fade`: the view leg plus the down leg, red dies first). Only the numbers change:

| Value | Round 1 | Round 2 |
|---|---|---|
| Extinction sigma (r, g, b) per BU | 0.090, 0.034, 0.016 | **0.052, 0.017, 0.0072** (about half: streets read 20+ BU down) |
| In-scatter | 0.003, 0.018, 0.055 | 0.002, 0.016, 0.050 |
| Caustic strength / floor | 1.1 / 0.12 | **3.0 / 0.0** (full contrast: dark gaps between bright ripples) |
| Caustic scale / ridge width / distortion | 0.05 / 0.22 / 0.9 | 0.095 / 0.11 / 0.8 (sharper, finer ripple lines) |
| Caustic depth e-fold / patchiness | 30 / 0.05 | 46 / 0.30 (reaches deeper, drifting bright patches) |
| Caustic colour | 0.22, 0.72, 0.78 | 0.42, 0.95, 1.0 (whiter, so it reads as light) |
| Light shafts | 9 at 1.0e7, cone 4° | 16 at 1.7e7, cone 3.2° |
| Underwater skylight | 20 000 | 34 000 |
| Surface wave bump / roughness | 0.22 / 0.035 | **0.05** / 0.02 (AD review 2: half of test 1); 0 inside the breakwater |
| Surface reflection | Fresnel (IOR 1.33) | **0.5 x Fresnel** outside the breakwater, **0.20 x** inside |
| Seabed albedo | x 1 | x 1.7 (sand, so the ripples land on something) |

## 6. Where route rooms could sit (plausible places only)
This is not a rule proposal. The BALLAST TIDE and TIDE proposals live in `new_corps/atlantis` and with the
design sessions.

| Place | Candidate room(s) | Why it is plausible |
|---|---|---|
| The lock control tower | Entry (DOCK LOCK) | The only door from the city; the netrun can start where the dry street meets the dam |
| The causeway | One link (or a room halfway) | A long exposed walk with lamp posts: a natural "corridor" |
| The six pier-end pods | 6 rooms | The arrival pod is on the causeway's axis; the ring walkway links all six end and ring pods |
| The six ring pods | 6 small rooms | Between the piers, on the hex ring: the alternative paths |
| The six inner pods | 6 rooms | Halfway in along each pier: the last room before the station |
| The station: main deck, crown | 2 rooms (elite or hub) | The drum ring and the second tier |
| THE VENT CAP (the Hub) | 1 room | On the last glass drop, between deck 5 and the core (`rooms["vent_cap"]`), at the moon pool: the last door before the server |
| The five pressure decks (the deep stair) | 5 floors of rooms | Four lit rooms on each rim; the glass drops between decks are the vertical links |
| The sluice gates | Optional set pieces | Gates open and close, and could carry the de-power / re-make link grammar (round 43) if a design session wants it |

The pixel positions of every candidate room for each render are in `<stem>_rooms.json`
(`tethys_build.py`, part 4).

### Central Server: THE BLACK SMOKER
- **Where:** at the foot of the moon pool, 16 BU to screen-left of the station centre. That is **inside the lot**
  (r 34) and inside the breakwater's calm water.
- **What:**
  - The Black Smoker's chimney stack rises from the trench floor (about -110): a vent mound and five black
    chimneys with hot orange mouths.
  - The core caps the stack at ZW -23: a dark hull ring, **the white server ring** (the target, r 3.6), an
    abyss-blue outer ring, a hot orange core, struts, and a key light up the well.
  - The core is literally the vent's cap.
- **THE RISER:** the server's cable riser runs up the moon pool's axis to the collar.
- **How it reads:** through the glass-calm water inside the breakwater, straight down the lit well. The calm ring
  is the see-through window, and it is physically motivated.
## 7. The overview test and the occlusion rule
The camera is a high 3/4 orbit: yaw 135 (the map direction), pitch 50, distance 210, lens 30, 1280 x 720, looking at
the lot with the causeway, the dam and the dense dry city in the lower part of the frame.

The occlusion rule is the camera-rig rule from the designer (2026-10-15), copied from
`hq_meridian/scripts/hq_kit/downtown.py` into `scripts/occlusion.py`, with the OCC values unchanged:
- **Target volume:** the station (rim, crown), the eight lot-edge points, deck 5, the server, the causeway and the
  lock tower.
- **Cut:** every dry building whose footprint and top fall inside that sight cone is cut to the 6.4 BU stub.
- **Applied to:** the zoning copy, as a per-building height (the same per-instance value Godot tweens).
- **Ghost:** not needed; no stub reaches into the cone.

**Result at this camera: 0 buildings cut, 0 ghosts.**
- From pitch 50 over the dam, nothing in the dry city reaches into the cone: the tallest blocks next to the lock are
  far below the sight lines.
- The rule is wired and will act for a lower orbit (the PREP line in each log reports `occ_cut`).
- **The dam is the real clearance:** the dam band (-16 to +9 BU) removes the city right in front of the water, so
  the HQ never needs the cut from the map side.
- **Open:** if the netrun camera orbits to the sea side or drops lower, the drowned towers that stand out of the
  water would need the same rule (only dry buildings are tested now).

## 8. Render log and values (tests)
All renders are Cycles HIP, plain BVH2, OIDN, 24 spp, through the GPU queue (lock `hq_tethys`, released after each
batch, every batch under 3 min). The post is `post_city.aaa` unchanged (black point, exposure solved to the r3
median, bloom, shoulder, toe search, vignette).

| Image | Size | Build | Render | Median | < 0.10 | > 0.85 | HQ peak / local bg | HQ mean / bg |
|---|---|---|---|---|---|---|---|---|
| `tethys_closeup_test.png` | 1280 x 720 | 12.6 s | 36.6 s | 0.140 | 34.2 % | 0.10 % | 0.859 / 0.170 = **5.0x** | 2.5x |
| `H_overview_test_plate.png` | 1280 x 720 | 11.8 s | 24.5 s | 0.140 | 33.4 % | 0.01 % | 0.843 / 0.186 = **4.5x** | 2.4x |
| `test_crop_pier_city.png` | full-res crop of the close-up (2560 frame) | 12.1 s | 15.0 s | | | | | |
| `test_crop_drowned_streets.png` | full-res crop of the close-up (2560 frame) | 11.8 s | 14.7 s | | | | | |

- AAA-2 targets: median about 0.14, 25-40 % under 0.10, at most 2.5 % over 0.85. Both tests are in band.
- The landmark rule (`post_tethys.landmark_ratio`): the 99th-percentile luma in a disc of 7.5 % of the frame width
  round the station, against the median of the ring out to 2.2x.
- The estimated final close-up: 2560 x 1440 at 40 spp, about 2.5-3 min of GPU (round 1 was 128 s).
- Values: `*_values.json`. Pixel anchors of every candidate room: `H_overview_test_rooms.json`.
- `compare_round1_round2.jpg`: round 1 against this test, side by side.

## 9. Reusable modules (for the full-city agent)

| Module | Entry point | What it does |
|---|---|---|
| `scripts/tethys_landmark.py` | `build(ns, centre=None, water_z=None, bed_z=None, lot_r=None, seed=None) -> info`; `landmark(ns) -> (label, crown, hue)` | The pier city. `landmark()` is a drop-in for `city_all_corps/landmarks.tethys()` |
| `scripts/tethys_quarter.py` | `prep_zoned(src, dst, occ=None)`; `build_dam(ns)`; `build_clutter(ns)` | The dam, the lock, the causeway and the clutter. Also `dam_line(O)`, `lock_pose(O, L)`, `causeway(O, L)` (pure Python) |
| `scripts/tethys_preset.py` | | Every number |
| `scripts/tkit.py` | | Geometry helpers (oriented box, tube, frustum, loft, slab) that write into `city_build.Acc` |

`ns` is the exec namespace of `city_build.py` after `city_world.py` and the head of `landmarks.py` (it must provide
`spot_at`). For a typical integration in the full-city build:

```python
import tethys_landmark as TL, tethys_quarter as TQ
# before building: run TQ.prep_zoned on the zoning (it removes the buildings under the dam, lock and causeway)
# after city_world.py and the landmark defs:
TQ.build_dam(globals()); TQ.build_clutter(globals())
tethys = lambda: TL.landmark(globals())        # replaces landmarks.tethys before the LM loop
```

The water values to copy are `tethys_preset.WATER` (they override `city_preset.WATER`), with `SEABED_K` and `WET_LIT`.

## 10. Files and rebuild

| Path | What it is |
|---|---|
| `DESIGN.md` | This file |
| `tethys_closeup_test.png` | The close-up test (1280 x 720, 24 spp); the 2560 x 1440 final is held for review |
| `H_overview_test.png` / `H_overview_test_plate.png` | The overview test with and without the route-placement overlay |
| `test_crop_pier_city.png`, `test_crop_drowned_streets.png` | Full-resolution crops of the close-up (Cycles border renders) |
| `compare_round1_round2.jpg` | Round 1 against round 2, side by side |
| `*_values.json`, `H_overview_test_rooms.json` | Value checks, room pixel anchors |
| `scripts/` | `tethys_preset`, `tethys_landmark`, `tethys_quarter`, `tkit`, `occlusion`, `tethys_build` (the Blender driver), `run_tethys` (the GPU-queue runner; `cam@res#x0:y0:x1:y1` for a crop), `post_tethys` (the post + values), `overlay_tethys`, `compare`, `crop`, `quick_png` |
| `scripts/city_base/` | A frozen copy of `city_all_corps/scripts` at commit a032bf6c (revision 2b): this pass never depends on the city agent's live edits |
| `D:\rc_scratch\tethys\` | Scratch: the zoning snapshot (`zoned_base.json`), the per-camera zoning copies, the renders |

Rebuild steps:

```
python scripts/run_tethys.py main t_close,t_over 0.5 prev                      # Eevee geometry check, no lock
python scripts/run_tethys.py aaa "t_close@0.5,t_over@1.0,t_close@1.0#0.36:0.35:0.62:0.82" 0.5 24 test5   # Cycles tests + a crop
python scripts/post_tethys.py D:/rc_scratch/tethys/test5/t_close_aaa tethys_closeup_test.png
python scripts/post_tethys.py D:/rc_scratch/tethys/test5/t_over_aaa H_overview_test_plate.png
python scripts/overlay_tethys.py H_overview_test_plate.png D:/rc_scratch/tethys/test5/t_over_aaa_rooms.json H_overview_test.png
```

The final would be `run_tethys.py aaa t_close 1.0 40 final`.

## 11. Decisions (AD review 2) and open questions

### Decided
- **The depth rule:** yes.
- **The server inside the lot:** yes. It is now 16 BU from the centre.
- **The see-through window:** the breakwater, the calm water inside it, and the moon pool.
- **Gates:** one in three open.
- **The netrun entry:** the DOCK LOCK.
- **Pods:** 18 of them.

### Open
1. **The overview camera is fixed at yaw 135.** The see-through placement is tuned to it (pitch 50; at the
   close-up's pitch 40 the server shifts toward the front pods). An orbiting netrun camera would need the window to
   stay readable at other yaws. The calm ring works from any side; the server's screen position does not.
2. **The occlusion rule now also needs the towers that stand out of the water** on a sea-side or lower orbit.
## 12. Wildlife (designer note, 2026-10-16) and test 6 / 7 values
Numbers: `tethys_preset.WILDLIFE` (seeds `fish` 7207, `whales` 7208). Builders: `tethys_quarter.build_street_shoals`, `build_shoal`;
`tethys_landmark.build_pier_shoals`, `build_whales`; helpers `tkit.fish`, `tkit.shoal_sim`. Wired in `tethys_build.py`
(`TETHYS_NOWILD=1` switches it off).
- **Fish shoals.** A small boids run per shoal (separation, alignment, cohesion, a swirl or drift field), 40-80 fish, seeded by the
  tile. Kinds: ball, ring, stream. Round the drowned streets (79 shoals, 4121 fish within 36-240 BU of the HQ), round the main
  station's stilt ring (3 stacked rings), each pod's stilts and a ball on each pier (22 shoals, 842 fish). Silver backs catch
  the caustics; 30 % carry a photophore glint. Fish are drawn about 1.4-2.4 BU long (larger than life) so they read.
- **Whale pod.** 4 adults (19-25 BU) and a calf (0.4 x), on an arc of r 45 BU round the station, beyond the breakwater (r 33.7),
  swimming clockwise, staggered in radius and depth (ZW -7 to -12), each raised over any drowned tower under it. One soft cool spot
  under the surface lights the pod.
- **Values** (all 1280 x 720, 24 spp): test 6 close-up median 0.140, 34.4 % < 0.10, HQ 3.65x peak / 1.91x mean; overview 0.140, 33.7 %,
  3.31x / 1.82x. Test 7 (wildlife): close-up 0.140, 34.2 %, 3.49x / 1.83x; overview 0.140, 33.4 %, 3.23x / 1.74x.
- **Open:** the fish are subtle at this camera (a few pale specks); the pod is partly hidden behind the pods in the close-up.

### Test 9 (AD review 3), 1280 x 720, 24 spp
Files `tethys_closeup_test9.png`, `H_overview_test9.png` / `_plate.png`. Changes: caustics inside the breakwater x0.03 on every material; outside, the
surf layer x0.5 and the seabed unchanged (`PIER.breakwater.caustic_in / caustic_surf_out`, patched into `water_fade` at run time in `tethys_build.py`);
cyan moon pool (collar, rings, soft emissive column, cyan spot) and a bigger server (r 4.4) with a warm rim ring and rim light; 25 dense fish shoals
(21 round the stilts, 4 over streets; 2168 fish; belly glow 0.3, glints 2.0); station emitters x0.75 (`PIER.emit_k`, win_k, ring_k).
Values: close-up median 0.140, 34.2 % < 0.10, HQ 3.33x peak / 1.74x mean; overview 0.140, 33.4 %, 3.11x / 1.70x.
Server patch (28 px) vs the ring around it: close-up 4.4x peak / 1.5x mean; overview 2.3x peak / 1.1x mean.

### Finals v2 (AD review 3 approved, designer notes)
- **Server** moved to the camera side of the moon pool, clear of the inner pod's shadow: `PIER.stair` seaward -12, lateral -9 (r 15 BU, inside the lot and the
  breakwater); rim light doubled (2.0e5).
- **Caustics outside the breakwater:** surf layer x0.30 and seabed x0.30 (`PIER.breakwater.caustic_surf_out / caustic_seabed_out`; was x1 / x1 in test 7,
  x0.5 / x1 in test 9); near zero (x0.03) inside. The water reads clear and calm with a gentle shimmer.
- **Fish (designer correction):** the stilt and pod ring shoals are removed. Only loose, irregular `drift` and `stream` shoals in open water: 9 over the drowned
  streets (40-170 BU from the HQ) and 6 in the open sea (38-50 BU, 5-11 BU down), 40-70 fish each, attached to nothing
  (`tethys_quarter.build_street_shoals`, `build_open_water_shoals`). **The fish are tuned for motion, not stills** (they read as faint specks in a still):
  in Godot, drive them with animated boids or a shader-driven swirl; do not brighten them further for stills.
- **City hook:** `tethys_landmark.build(ctx)` follows the `city_preset.LANDMARK_MODULES` contract (NOTES.md "Landmark modules"): builds the pier city, the
  street and open-water shoals and the whale pod with the city's accumulators and lights; sets `ctx.station["centre"]`; returns label / crown / hue. It
  inserts its own folder in `sys.path` (so `tethys_preset`, `tkit`, `tethys_quarter` import under importlib). Checked with a stub ctx on the zoning snapshot.
  The dam, lock and drowned-street clutter need the reshaped zoning (`prep_zoned`) and are not part of the hook. Set
  `LANDMARK_MODULES["tethys"]` to `.../hq_tethys/scripts/tethys_landmark.py` (not edited here).
- **Finals v2 values** (2560 x 1440, 40 spp, 130 s render each): `tethys_closeup_v2.png` median 0.140, 30.9 % < 0.10, HQ 3.91x peak / 1.87x mean;
  `H_overview_v2.png` (+ `_plate`) 0.140, 31.0 %, 3.72x / 1.88x. Server patch vs its surround: 5.3-5.4x peak, 1.85-1.9x mean (target 1.5x mean: met).
