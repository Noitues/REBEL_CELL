# City, all corps: the one city with all seven corp districts (key art, 2026-10-15)

One city render that shows every corporation's district, like the earlier whole-city key art
(`round30_meridian_castle/city_night_hq_v6.jpg`), but built on the one-city layout and rules and in the approved AAA-2 look.

Nothing is committed and the Godot build is untouched. Everything is rendered headless in Blender 5.2.2: Cycles on the GPU
(RX 6700 XT, HIP, plain BVH2, OIDN) for the AAA-2 images, Eevee for the mainline check. All randomness is seeded
(`city_preset.SEEDS`).

## Files

| File | What it is |
|---|---|
| `city_all_corps_night.png` | **The hero shot**, 3840 x 2160. A high 3/4 aerial (yaw 135, the map's own direction, pitch 47) of the whole city at night in the AAA-2 look: fog banks lit by each district, beams, light-streaks on the arterials, the seven landmarks, the sea and the seawall. |
| `city_all_corps_labeled.png` | The same image with the district labels: the corp name in its hue, the crest disc and the landmark's name, in the map's tag style (the round 30 v6 tag: dark slanted plate, hue bar), with a leader to the landmark. |
| `city_all_corps_mainline.png` | The same camera in the MAINLINE City Grid look (toon ramp, ink, the post40 finish and the sb_mhq capture match). |
| `tethys_flooded_closeup.png` | 2560 x 1440. The drowned quarter from above the levee: clear water over the submerged blocks inside the curved seawall, fading to deep blue with depth and distance, soft caustic ripples, the shafts, ATLANTIS STATION in its trench. |
| `zoning_map.png` | A top view of the zoning (districts, the drowned quarter, the coast, the arterials, the aqueduct, the landmark clearances). |
| `scripts/` | Everything to rebuild (see "Rebuild"). |

## Results (revision 2, 2026-10-16 00:13: hero re-rendered; the close-up is the approved revision-1 render)

The first pass is backed up in `D:\rc_scratch\city_all_corps\v1\` (images + scripts). Before / after crops (left v1,
right revision, same camera and pixels) are in `D:\rc_scratch\city_all_corps\crops\` (`scripts/crops.py`).

Scene: 14 232 buildings, 35 227 ring props, about 670 k faces; 7 landmarks; Tethys bay, seabed and trench; the
Meridian freight viaduct (551 BU, 7 corners).

| Render | Engine | Resolution | Samples | Build | Render | Wall |
|---|---|---|---|---|---|---|
| hero (AAA-2), rev 2 | Cycles GPU (HIP, BVH2, OIDN) | 3840 x 2160 | 40 | 10.1 s | 266.2 s | 281 s |
| close (AAA-2) | Cycles GPU (HIP, BVH2, OIDN) | 2560 x 1440 | 40 | 9.5 s | 127.7 s | 142 s |
| hero (MAINLINE), rev 2 | Eevee | 3840 x 2160 | 16 TAA | 10.1 s | 4.7 s | 21 s |

Values (sRGB luma of the final PNG; AAA-2 targets: median about 0.14, 25-40 % under 0.10, at most 2.5 % over 0.85):

| Image | Median | Under 0.10 | Over 0.85 | Exposure k | Toe | v1 (median / under 0.10) |
|---|---|---|---|---|---|---|
| `city_all_corps_night.png` | 0.140 | 28.7 % | 0.25 % | 0.882 | 1.0 | 0.128 / 28.1 % (rev 1: 0.140 / 28.4 %) |
| `tethys_flooded_closeup.png` | 0.140 | 27.6 % | 1.66 % | 4.557 | 1.85 | 0.136 / 17.9 % |
| `city_all_corps_mainline.png` | 0.213 | 1.0 % | 0.02 % | n/a | n/a | 0.221 / 0.2 % (mainline look, not held to the band) |

Also in `D:\rc_scratch\city_all_corps\final\value_checks.json`. The post now takes the fog veil off at a black point
(0.85 x the frame's 5th percentile per channel, `AAA["black_point"]`) and solves exposure with the vignette inside the
solve; the toe is raised only if the dark share is still under 27 %.

## Rebuild

1. `python zoning.py` writes `zoned.json` and `zoning_map.png` to `D:\rc_scratch\city_all_corps\` (bay, outline flags,
   the rail search and the rail-side height cap).
2. `python run_jobs.py aaa hero,close 1.0 40 final`: the Cycles passes, under the GPU lock (`D:\rc_scratch\GPU_QUEUE.md`).
   Each Cycles run also writes `D:\rc_scratch\city_all_corps\meridian_rail.json` (the rail polyline, world BU).
3. `python run_jobs.py main hero 1.0 16 final_main`: the Eevee mainline pass (no lock).
4. `python make_all.py`: the post, the labels and the value checks, written into this folder.
5. `python crops.py`: the before / after crops against `v1`; `python beam_check.py <png> <anchors.json>`: the beam rule.
CPU previews (no lock): `sh cpu_prev.sh <cam> <res_k> <spp>`. Debug switches: `CITY_NOFOG`, `CITY_NOWVOL`, `CITY_NOWATER`.

## Art director review of the first pass: what changed

1. **Outlines (no wireframe grid).** Crown trims at 25 % of their old rate except on buildings flagged `art` (within
   1.3 lots of an arterial) or `border` (another district within 2 lots); street lanes at 25 % except arterial tiles;
   ring trims at 2.5 %; ring street glow cut to 0.3 (main roads) / 0.08 (others). Where a trim is dropped the roof gets
   1-3 clutter boxes and, at 35 %, a warm roof lamp (`OUTLINE` in `city_preset.py`). Crop `1_outlines_sprawl`.
2. **Districts without labels.** Rebel Cell heights x 0.7, red-weighted blade / box signs, lantern strings on every
   street face, glow power x 1.8 (`rebel_glow_k`). Meridian: container stacks on 95 % of freight roofs. Aurelian:
   travertine facades, gilt trims and gilt fog glow (verdigris now only on domes), no longer twin to Solace. Orbital:
   six flood masts lighting the podium disc, a light ring at the rim, the rocket keyed white. District glow mix 0.25.
   Crops `2a`-`2d`.
3. **Tethys and the coast.** The seawall and the coast curve into a bay (`BAY`: Gaussian bow 16 lots deep round the
   drowned quarter, headlands past 120 lots); the drowned blocks sit inside the wall under clear water; pump towers
   every 66 BU of arc follow the curve. Drowned windows: lit share at least 0.45 and wet facades x 2.6 emission before
   the water fade. A sea-mist volume from 30 lots past the coast thickens with path length, so the horizon dissolves.
   The low fog is 96 % cleared over the bay (`bay_clear`), the haze band too. Crop `3_bay_horizon`.
4. **Fog strata.** The low district banks (hue-lit by the district glow) plus a torn upper sheet at z 58 BU, and a low
   shore bank along the dry side of the levee. Hero median 0.140, 28.4 % under 0.10. Crop `4_fog_strata_full`.
5. **Beams.** Only roofs whose base AND a point 150 BU up the beam fall inside the central frame (24 % / 12 % margins);
   each beam is a soft 3 degree cone plus a 0.9 degree hot core (two spots); power raised to 2.2e8 / 2.6e8 so they
   read after the black point. The lower-left pink and cyan beams are gone. Crop `5_beams_lower_left`.
6. **Tethys close-up.** The voronoi crack caustics are replaced by soft noise-ridge ripples (two layers, distorted,
   blue-green, low floor, patchy). The shore city is darker (plazas 0.13, wet concrete 0.17), sits in the shore fog
   bank, and keeps its lit windows, kerb lamps and arterial streaks. The seawall curves. 27.6 % under 0.10 (was 17.9 %).
   Crops `6a`-`6c`.
7. **Meridian freight rail (designer note + pipeline-spec ruling).** The line is the street-tile BFS from the fort gate
   to the coast (zoning L4): it runs only over street centre lines, so it threads between buildings and never crosses
   one, then a jetty over the bay to a container terminal on the seawall. Per the art director ruling it leaves through
   the NORTH rail-yard gate (the yard, wagons, lamps and gantry crane moved to the fort's north half; a spur from the
   middle track runs out through a 6 x 5.2 BU orange-lit portal in the north container wall). The deck stands at
   17.5 BU (ramp up over 60 BU from the gate, down over 45 BU to the terminal at 8.7 BU); all 130 dry buildings within
   1.2 lots of the line are capped at a 15.5 BU roof (7 needed cutting) and keep plain roofs. Orange rail glow on both
   deck edges, orange signal lamps every 36 BU, two train light-streaks. The polyline (world BU, with deck z per corner)
   is exported to `D:\rc_scratch\city_all_corps\meridian_rail.json` as the source of truth for the HQ kit. These rail
   changes are IN this render (the GPU pass ran after the ruling). Crop `2b_meridian_rail`.

### Still open (honest self-review)

- The outline grid is much quieter, but the remaining arterial trims / lanes and the dimmed ring street glow still
  read as a faint grid in the outer ring at hero scale. A next pass could drop the ring glow further.
- From the hero height the viaduct reads as a thin warm line; it reads clearly only in the close crops and the Eevee
  debug view (`prev\dbg_rail_q.png`).
- Beams still read fairly rod-like at 3840 px (the soft cone is subtle); one landmark hero beam leaves the top edge.
- The close-up meets the dark share with a toe of 1.85 on top of the black point (the bay water fills the frame).

## Art director review of revision 1 (revision 2: hero only, 2026-10-16)

Revision 1 is committed as is; the close-up is approved and was not re-rendered.

1. **Beams.** The 6 roof beams and the two-spot rods are gone. Now ONE beam per landmark, rising from its crown (6: REBEL_CELL
   has no crown). Each one follows the storyboard round-3 recipe (`m44/onecity_cycles.py`): an emissive cone seen by the camera
   only, with a hot gaussian core over a wide soft skirt. It is brightest at the source and gone by 60 % of its length, with a
   slow noise breakup. A wide, fully soft 30-degree spot, linked to the fog only, lights the air round it (`AAA["beam"]`: length 420 BU, half-angle 1.1
   deg, emit 1.1, haze 1.2e7). Each beam is shortened in 10 % steps until its fade end sits inside the frame; Tethys is cut to 340 BU.
   The rule check (`beam_check.py`, final PNG luma) passes for every landmark:

   | Landmark | Landmark peak | Local bg | Ratio (>= 1.5) | Beam peak (< landmark) | End in frame |
   |---|---|---|---|---|---|
   | Aurelian | 0.999 | 0.315 | 3.17 | 0.858 | yes |
   | Halcyon | 1.000 | 0.324 | 3.09 | 0.796 | yes |
   | Meridian | 0.942 | 0.230 | 4.10 | 0.737 | yes |
   | Orbital | 1.000 | 0.240 | 4.17 | 0.801 | yes |
   | Solace | 0.949 | 0.290 | 3.27 | 0.696 | yes |
   | Tethys | 0.733 | 0.221 | 3.32 | 0.502 | yes |

2. **Outer ring grid.** Outside the seven districts (the sprawl and the ring), trim and lane emission is at 30 % of revision 1
   (`OUTLINE["out_k"]`; the ring street glow is now 0.09 / 0.024). Warm roof lamps (30 % of ring buildings) and a higher
   ring window lit share (0.14) carry the outer city. Crop `1_outlines_sprawl` (now v1 vs revision 2).
3. **Rail legibility.** The orange deck-edge glow is wider (0.12 -> 0.45 BU) and brighter (0.55 -> 0.9). There are three
   train light streaks (two with container wagons), 0.6 BU wide. At hero scale the line now reads from the north gate to
   the seawall terminal. Crop `2b_meridian_rail`.

Hero values: median 0.140, 28.7 % under 0.10, 0.25 % over 0.85 (exposure 0.882, toe 1.0). The crops in
`D:\rc_scratch\city_all_corps\crops\` were refreshed (the hero crops now show revision 2; the close-up crops are unchanged).
Still open: the Halcyon and Solace beams sit close to their landmark peaks (0.80 / 0.70 against 1.0 / 0.95). The outer
ring is quiet now but slightly flat.
