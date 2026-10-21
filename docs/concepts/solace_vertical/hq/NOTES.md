# Solace HQ plates v5: the lime district helix in the park (2026-10-21)

Designer ruling (DIRECTION_REVIEW, last bullet): the HQ scene follows the new lime district helix (canonical landmark rule); re-render the HQ
plates with it in the park + plinth setting. Concept / golden-plate candidates only: the v4 golden plates are untouched, nothing is wired into
Godot, nothing is committed.

## Files
| File | What |
|---|---|
| `H_overview_v5.png`, `H_decision_v5.png`, `H_hover_v5.png` | 2560 x 1440 plates without UI (v4 plate size), same three cameras as v4 (`hq_cam`, unchanged) |
| `sheet_v5.jpg` | 2560 wide: v4 golden plate (left) vs v5 (right) per camera |
| `scripts/` | a COPY of `route_map_graph/hq_solace/scripts` with the v5 changes (the v4 scripts are not edited). New: `sd_kit.py`, `make_sd_kit.py`, `sd_lib.py`, `hq_prev.py`, `gpu_run.py`, `sheet_v5.py` |

## What changed (everything else is v4)
**Helix skin** (`hq_build.py`, preset `light`): lime-tinted glossy body (skin colour 0.46 / 0.74 / 0.30, coat 0.8, roughness 0.16) with a uniform lime
glow (`skin_k` 0.012) plus the fresnel rim (`rim_k` 0.12, pow 4); lit window frame rings (lime, pale lime on odd floors, `frame_k` 0.5); the
floor ring under every floor alternates lime / pink (`ring_k` 0.6); the skybridge decks stay dark porcelain and get lit edge rungs alternating lime /
pink per route floor (`rung_k` 1.0; the kick strips take the same colour, the centre strip is dimmed); a floating pink halo ring (r 52.5, tube 1.25)
over both strand tops with a lime inner ring (r 42), `crown_k` 4, crown light x2. Kept from v4 and the 2026-10-16 rulings: two strands, a full 360
degrees each, two sideways-oval cutaway windows per floor (truly horizontal / vertical outlines), hybrid interiors (built floors on route-node and
decision-framed floors, interior mapping elsewhere), flush walkways, NO people, non-node windows translucent, no beam, no centre column.

**Setting** (`sd_kit.py`, generated from the district's `sd_main.py` round 5 `--park 1 --plinth 1` by `make_sd_kit.py`; `sd_main.py` untouched):
- the 3-tier circular plinth (district tiers 35 / 29.5 / 24 x 3.0 = r 105 / 88.5 / 72 BU, top 9.9 BU, so `podium` height = 9.9 and the helix stands on it),
  stairs at N / E / S / W, lime ring on every tier edge, pink ring r 17 and lime base ring r 12 (plinth units);
- the park: rolling lawn out to an organic boundary (r about 290 BU +- 60, lawn scale `SL` 1.5), 12 ponds, 9 winding lit footpaths (+ lanes) from the stair feet
  out through the tree line, about 790 trees (clumps + a double tree line); path lines widened (they were sub-pixel at HQ distance);
- A / B / C kit bundles (36 / 41 / 31 lots; capsule grove, culture cells, clean ward), bundle towers x1.8 height, and the C hospital with the standing
  lime cross at cell (0, -7) (south of the helix, in view in the overview and, behind the right strand, in the decision shot);
- the ordinary city beyond the tree line: `downtown` keep is now a circle r 360, r_out 440, the ring-city rings moved out (near 445-520, mid 540-700, far
  760-1040), the ring-road traffic streaks (they were on the old plaza) are off. The v4 plaza podium, planters, lobby, stair, SOLACE lettering and
  the plaza apron are not built (`hq_build.py` `PARK`); the clinic gate stays, moved to (22, -124) at the south stair foot.
- pass indices: helix 1, plinth 3, lawn + ponds 4, kits / hospital / trees 2 (so the values tool counts them as local background).

**Lighting** (same AAA-2 pipeline: Cycles HIP, volume fog, wet downtown streets; no pavement in the park so no wet ground there): the district materials
are used as built with every emission x`ek_scale` 0.07 (HQ post exposure is about 5.8x the district's), a cool moon sun 0.45 and a faint violet
counter-sun 0.08 light-linked to the park collection only (no haze lift), the C-bundle / hospital / path point lights x0.30; city window gain
`win_k` 0.52 -> 0.29 so the larger downtown does not lift the median. The kit materials read the object attribute `pwo`, so the hover power cut dims
the park with the city (as in v4).

## Numbers (2560 x 1440, 64 spp, `hq_values.py` on the finished plates; v4 golden in brackets)
| Plate | median | < 0.10 | > 0.85 | landmark / local bg | ratio |
|---|---|---|---|---|---|
| H_overview_v5 | 0.116 [0.127] | 45.0 % [37.4] | 0.50 % [0.7] | 0.572 / 0.179 | 3.20 [2.56] |
| H_decision_v5 | 0.144 [0.121] | 37.6 % [34.9] | 1.83 % [2.1] | 0.353 / 0.110 | 3.21 [2.57] |
| H_hover_v5 | 0.009 | 81.3 % | 0.08 % | 0.117 / 0.006 | 20.9 (power-cut beat, as v3 / v4) |

Medians are inside or just under the 0.12-0.15 target, clipping is under 2 %. The landmark ratio is above the 2.5 warn line on both plates (v4 was
2.56, pre-accepted): the lime skin is a large bright area and the park lit under it lowers the "background" classes less than the dark v4 city did.
Not tuned further (lowering the skin dims the lime look); lever if wanted: `skin_k` / `rim_k` in preset `light`, `ek_scale` in preset `park`.
Under-0.10 on the overview is higher than v4 because the lawn and the tree-line ring are dark.

## Render times (Cycles HIP, RX 6700 XT, GPU lock held as `solace_hq_v5`)
Final: overview 96.7 s, decision 125.3 s, hover 108.4 s (340 s wall for the three, scene build about 7 s each). Tests: 640 x 360 mini 6 s, 1280 x 720 test 18-22 s.
Iteration log: skin and kit emission tuned over 12 test batches (medians 0.25 -> 0.15 at test quality, which reads about 25 % above final).

## Rebuild
```
cd solace_vertical/hq/scripts
python make_sd_kit.py                      # regenerates sd_kit.py from district/scripts/sd_main.py (edit the constants at its top: SL, SPL, HK, RB0, HOSP_CELL)
set HQ_SCR=D:/rc_scratch/solace_v1/hq_v5/scratch        # job files + ov json (the scripts default to ../scratch)
python gpu_run.py "final stills" python hq_jobs.py stills final      # takes / releases the GPU lock (ME in gpu_lock.py), writes D:/rc_scratch/solace_v1/hq_v5/out/bl_stills
python hq_prev.py D:/rc_scratch/solace_v1/hq_v5/out/bl_stills/H_overview 0 ../H_overview_v5.png     # finish + values (zoom 0 overview, 1 decision / hover)
python sheet_v5.py
```
Preset knobs: `hq_preset.py` `light` (`skin`, `skin_k`, `rim_k`, `frame_k`, `ring_k`, `rung_k`, `crown_k`), `park` (`ek_scale`, `light_k`, `sun_k`), `downtown` / `city.rings`, `podium` / `start`.
The interior atlas is read from `D:/rc_scratch/solace_v1/hq_v5/atlas/imap_atlas.png` (a copy of the v4 atlas).

## Caveats
- The park fills only the lower centre of the overview (the camera is 770 BU out); the kit bundles are a belt of 2-3 lots between the park ring and the tree line.
- District kit materials are scaled copies: window cells are 1.5x the district's; the capsule towers are the nearest large shapes in the decision shot.
- The hospital cross faces the overview camera (`CROSS_ANG` -33).
- The 3D UP ramp ribbon still starts at the old podium edge point (y -48) now on the top tier; invisible at plate scale.
- No Godot port notes: this is a plate candidate. If accepted, the kit is the district's (`godot_s2`) plus the HQ interior shell; no new mechanics.
