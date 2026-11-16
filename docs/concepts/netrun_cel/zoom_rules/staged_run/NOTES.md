# Staged run (B-103, option 1) — DRAFT for designer review

Branch `art/staged-street-run` (worktree `D:/rc_art/staged_run`). View only. Seed 7, windowed captures
(`tools/look_parity/nr_zoom.tscn --zr --run=L --anchor=hq:meridian --poses=... --hl --freeze`).

## What was staged
- **One run per target.** `CityZoomStreet.set_target(t)` with a layered target builds a `CityZoomRun` once:
  - the 3 staged rows over the whole segment plus 1 lot at each end;
  - the near block melted from the staged rows back to the camera line plus 1 lot: buildings are hidden, and the
    lots read as wet forecourt, near cross streets included;
  - every gap in the frontage row gets a view-only infill building.
- **While the camera is on the run**, the occluder classes, the staged road and the road mesh stay fixed for the
  whole slide.
- **Picks (seed 7, anchor = Meridian HQ centre, lot 48,40):**

  | Layers | Run | Centre | Look | Infill lots | Min pose score |
  |---|---|---|---|---|---|
  | 8 | 18 lots | 53.5, 47.5 | N | 7 | 0.56 |
  | 10 | 22 lots | 49.5, 53.5 | N | 8 | 0.47 |

  The Meridian landmark stands behind the frontage.
- **Slide cost (10 layers, two passes over every layer):**
  - Chunk/skip rebuilds: 1 (on entry only).
  - Road mesh rebuilds: 1.
  - The storefront dressing still rebuilds about every 2 layers, at 0.4–0.7 s each. It is per-camera: lens
    suppression depends on the pose.
  - Other poses: 1–6 ms.
  - Entering the run: about 3 s, once. It includes the first chunk rebuild of the hidden set.

## Files
- `run8_first_L0.png`, `run8_middle_L4.png`, `run8_last_L7.png`: the 8-layer run.
- `run10_first_L0.png`, `run10_middle_L5.png`, `run10_last_L9.png`: the 10-layer run.
- `run10_city_overview_highlight.png`, `run8_city_overview_highlight.png`: the City band with the target
  highlight.

## Look calls
- **Infill = the nearest frontage building's facade:**
  - the template's key, territory, ink and setbacks;
  - flat roof, plain family mesh, the city's building material;
  - height = the mean of the nearest buildings either side.
  - The storefront dressing treats it as a frontage building (shop bays and fascia signs continue across the old
    cross street).
- **The melted near side is plain wet forecourt.** No lanes are drawn on it.
- **Landmark and compound lots are never melted** (`CityView3D.cleared_lots`). The picker rejects a run whose
  camera they block. The first capture pass put the end cameras inside the Meridian HQ landmark: landmarks are not
  prisms, so the picker could not see them.
- **The picker never invents a whole wall:** at most 35% of the frontage row may be infill.

## Weak points
- **Only flat ground stages.** The slope gate rejects every run near the Halcyon, Orbital and Solace HQs, so those
  sites still fall back to the relaxed pick (cameras can stand in walls).
  - Designer question: flatten the ground under a run?
- **An elevated highway deck crosses the frame** behind the frontage in both runs, as a dark band at about 45% of
  the frame height. It is not staged. Hiding the deck over the run is a possible next rule.
- **City ground lane stripes show through the forecourt** in places (diagonal / crosswalk marks at the bottom of the
  frame).
- **The picker takes about 2.5–3 s** near a flat site (0.1–0.6 s elsewhere); A-132's picker took 130–230 ms. Call it
  once per street, not per frame.
- **The dressing rebuild (0.4–0.7 s every ~2 layers)** remains per pose. It is the next cost to stage per target.
- **Streaks are seeded once around the run centre**, so the end poses may show fewer car lights.
