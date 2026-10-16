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

## Results (revision 1, 2026-10-16 00:00)

The first pass is backed up in `D:\rc_scratch\city_all_corps\v1\` (images + scripts). Before / after crops (left v1,
right revision, same camera and pixels) are in `D:\rc_scratch\city_all_corps\crops\` (`scripts/crops.py`).

Scene: 14 232 buildings, 35 227 ring props, about 670 k faces; 7 landmarks; Tethys bay, seabed and trench; the
Meridian freight viaduct (551 BU, 7 corners).

| Render | Engine | Resolution | Samples | Build | Render | Wall |
|---|---|---|---|---|---|---|
| hero (AAA-2) | Cycles GPU (HIP, BVH2, OIDN) | 3840 x 2160 | 40 | 10.6 s | 255.0 s | 275 s |
| close (AAA-2) | Cycles GPU (HIP, BVH2, OIDN) | 2560 x 1440 | 40 | 9.5 s | 127.7 s | 142 s |
| hero (MAINLINE) | Eevee | 3840 x 2160 | 16 TAA | 15.1 s | 4.0 s | 29 s |

Values (sRGB luma of the final PNG; AAA-2 targets: median about 0.14, 25-40 % under 0.10, at most 2.5 % over 0.85):

| Image | Median | Under 0.10 | Over 0.85 | Exposure k | Toe | v1 (median / under 0.10) |
|---|---|---|---|---|---|---|
| `city_all_corps_night.png` | 0.140 | 28.4 % | 0.24 % | 0.891 | 1.0 | 0.128 / 28.1 % |
| `tethys_flooded_closeup.png` | 0.140 | 27.6 % | 1.66 % | 4.557 | 1.85 | 0.136 / 17.9 % |
| `city_all_corps_mainline.png` | 0.213 | 0.7 % | 0.02 % | n/a | n/a | 0.221 / 0.2 % (mainline look, not held to the band) |

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
5. `python crops.py`: the before / after crops against `v1\`.
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
