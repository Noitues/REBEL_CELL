# Procedural vs custom: what the generator loses, and the rules that close it

Written 2026-10-15 for the pipeline-tools spec that will generate every netrun procedurally. CPU only (PIL and
numpy); no renders were made and nothing outside this folder was changed.

## Re-run (one command)

From the worktree root:

```
python docs/concepts/route_map_graph/proc_vs_custom/scripts/run_proc_vs_custom.py
```

- About 30 s on the CPU. It rewrites the four sheets and everything in `metrics/`.
- `--only p2_hq,p3_city` runs some pairs only (no METRICS.md / rules_check.md rebuild). `--no-sheets` skips drawing.
- Inputs live in `scripts/pvc_config.json`: the paths, the UI masks, the landmark boxes, the crop boxes and the bands.
  Missing optional files are skipped and listed on the sheet.
- **For tonight's round-1 finals:**
  - The HQ finals (`hq_*/plates/*_v2_plate.png`) and the city revision (`city_all_corps/city_all_corps_night.png`)
    are read in place, so a plain re-run picks them up.
  - Any `D:\rc_scratch\hq_rev\tests\*_t2*_plate.png` is added to pair 2 automatically (the `globs` entry).
  - A new camera needs its landmark and crop boxes checked in the config. They are normalised boxes, so a new
    framing moves them.

## Files

| File | What it is |
|---|---|
| `sheet_p1_street.jpg` | Pair 1, the netrun street. AAA-2 r3 plate vs the one-city street (v3r2, walls closed). |
| `sheet_p2_hq.jpg` | Pair 2, the HQ netruns. Halcyon and Orbital, v1 vs v2 kit, **same cameras**. |
| `sheet_p3_city.jpg` | Pair 3, the whole-city key art. Round 30 `city_night_hq_v6` vs `city_all_corps_night`. |
| `sheet_p4_anchor.jpg` | The mainline City Grid anchor: main's W3_HQ capture and the storyboard HQ (from `mainline_match.jpg`). |
| `metrics/METRICS.md` | Every metric for every image (27 images), with the top-6 hue clusters. Also per-pair `.md` and `.csv`. |
| `metrics/rules_check.md` | Each proposed rule below, PASS / FAIL per image, with the measured value. |
| `metrics/all_metrics.json` | Raw numbers. |
| `scripts/pvc_metrics.py` | The metric definitions (see the module docstring). |
| `scripts/run_proc_vs_custom.py` | The runner: the tables, the sheets, the rule check. |
| `scripts/pvc_config.json` | The image list, masks, boxes. |

Each sheet has: the two main images side by side at the same pixel scale; 3 matched detail crops (custom on top,
procedural below); an analysis strip (a luma map with the landmark box, the skyline profiles, the facade band, the
masked UI, and the top-6 hue swatches); and a table of every measured image in that pair.

## The metrics, in one line each

All on sRGB-encoded luma (Rec.709 weights), the measure the r3 NOTES use. Every image is first resampled to 1280 px wide.

- **Values:** median luma, % under 0.10, % over 0.85.
- **Landmark ratio:** mean luma in the landmark box / mean luma in a ring around it (the box grown by its own size).
- **Detail:** mean Sobel magnitude. High-frequency share (power above 1/8 cycle/px) in an upper and a lower band.
- **Detail distribution (new; it turned out to be the most telling number):** mean Sobel per 64 px tile.
  - `detail CV` = std / mean over the tiles. Low means an even carpet of detail.
  - `calm` = the share of tiles under half the median. These are the quiet areas that let a focus read.
- **Palette:** hue entropy (36 bins, chromatic pixels only), the chromatic share, and the top-6 hue clusters with
  their shares.
- **Repetition:** the strongest off-centre autocorrelation peak in 128 px tiles of high-passed luma (p90 over tiles),
  and the share of tiles over 0.45.
- **Silhouette:** two skyline profiles.
  - `lit`: the first row from the top where the smoothed luma passes the frame's p80. This is the bright mass, and
    it is the measure for the street.
  - `sky`: the first textured row. This is the horizon measure for the city.
  - For each: the std over the full width, and the minimum std over any 1/4-frame window.
- **Lights:** bright blobs (luma > 0.6) per megapixel, a proxy for the number of signs, windows and lamps. Focal
  concentration: the share of the top-1 % pixels that fall in the densest 3x3 cell.

## Pair 1: the netrun street (side view)

**Custom:** the AAA-2 r3 plate. **Procedural:** the one-city street, walls closed (`v3r2_street_closed`). Also
measured: the r3 proof plate, the v3_dynamic overview (UI masked), the REVEAL start, and storyboard f_0340.

| | custom r3 | procedural v3r2 |
|---|---|---|
| median / < 0.10 / > 0.85 | 0.141 / 31 % / 0.6 % | 0.115 / 39 % / 0.5 % |
| lit-skyline std (min 1/4 window) | **0.229 (0.140)** | 0.115 (0.031) |
| mean Sobel | **0.032** | 0.021 |
| bright blobs / MP | **550** | 328 |
| calm tiles | 20 % | **40 %** (too empty) |
| hue entropy / top hue cluster | **4.47 bits / 27 %** | 3.53 bits / 55 % |
| landmark ratio | 1.58 (globe + VOLTA) | 1.74 (the Meridian crane) |
| repetition p90 | 0.46 | 0.50 |

**What reads better in the custom street, and why:**
- **Silhouette.** The custom street is a wall of tall, stepped route columns, each with a crown: setbacks, neon
  rims, roof boxes. They rise to between 15 % and 70 % of the frame height, against a dark backdrop of taller towers.
  - The procedural front is a low, even band, with every top between 50 % and 60 % of the frame height. Two thin
    towers stick up out of it.
  - The lit-skyline std is half the custom's, and in its flattest quarter it is 1/4 of the custom's.
  - This is the "9:1 street front" problem the storyboard NOTES already name.
- **Signage density.** The custom frame carries about ten readable signs and ads, each a small lit composition:
  HALCYON, ORBITAL, SOLACE, SLEEP, VOLTA, CLINIC, WE MOVE, the noodle stall, OPEN 24, CAPSULE.
  - It also has two megastructures: the wireframe globe and the arch billboard.
  - The procedural street has one blank pink board and no text. That is most of the gap in bright blobs per
    megapixel (550 vs 328) and in Sobel (0.032 vs 0.021).
- **Street level.** In the custom, the bottom 25 % of the frame is the street itself: wet asphalt, streak lanes in
  two colours, kerb lamps, shopfront strips on every base, long coloured reflections, and a kiosk in the foreground.
  - In the procedural, the bottom 25 % is a field of cut roof blocks, a dark grid with specular glints. It reads as
    rooftops, not as a street, and it is where most of the 40 % calm tiles sit.
- **Fog and depth layering.** The custom has 3 to 4 readable planes: the backdrop towers in violet fog, a mid haze
  band, the route columns, and the street mist.
  - Its beams cut through fog and steam plumes rise from the roofs.
  - The procedural has one haze gradient behind the buildings and an empty sky above them. Its two beams sit in
    clear air, so they read as sticks, not shafts.
- **Palette.** The custom spreads over magenta, violet, cyan, teal, yellow and red, with no hue above 27 %.
  - The procedural is 55 % one violet-blue. The pink and cyan sit only in the ground-floor washes.
- **Materials and storytelling props.** The custom has stairs, walkways, a drum column, vents, antennas, AC boxes
  and lit interiors.
  - The procedural has plain boxes with window dots and trim strips: every building is the same material at a
    different size.

**What the procedural street does as well or better:**
- **Values.** They are in the AAA-2 band (f_0340: median 0.124, 36 % under 0.10). v3r2 sits a little dark.
- **Landmark.** The landmark is a real map object (the Meridian crane "A") with a good 1.74 ratio.
- **Repetition.** It is no worse than the custom.
- **Reading the route.** The route reads because the frontage is simple.

**An honest caveat.** The r3 street is mostly rules already (see the r3 NOTES, "Procedural rules"). The proof plate
(`c_proof`, a new seed) keeps the r3 look on values, palette and detail.
- It still fails the silhouette rule, because its wisp band lights the top of the frame.
- What did not carry over by rule is what the procedural street is missing: the hand-placed dressing (signs, ads,
  holo ads, megastructures, the drum column, stalls), and the tall street-set columns.

## Pair 2: the HQ netruns (v1 hand-built vs v2 kit)

The cameras are the same, so this is the cleanest pair.

| | Halcyon v1 | Halcyon v2 | Orbital v1 | Orbital v2 |
|---|---|---|---|---|
| median / < 0.10 | 0.127 / 39 % | 0.110 / **46 %** | 0.199 / 18 % | 0.118 / 41 % |
| detail CV / calm tiles | **0.59 / 25 %** | 0.29 / 4 % | **0.74 / 32 %** | 0.36 / 9 % |
| bright blobs / MP | 1502 | 3633 | 401 | 1860 |
| landmark ratio | 2.35 | 2.31 | 1.48 | 1.52 |
| repetition p90 | 0.58 | **0.37** | 0.77 | **0.31** |

Meridian v1 vs the v2 test (another camera): detail CV 0.65 vs 0.29, calm 26 % vs 3 %, and 61 % of the v2 test is
under 0.10.

**What reads better in v1, and why:**
- **Focal hierarchy through rest areas.** v1 rings the compound with a wide, quiet belt: wet ground, teal pylons,
  light streaks on the ring road. The city is far back.
  - The compound is the only busy thing in the middle of the frame, so the eye goes straight to it.
  - v2 fills every pixel up to the plaza with lit window dots of the same size and brightness. The detail CV
    halves (0.59 → 0.29), and the calm tiles drop from 25 % to 4 %.
  - The pyramid keeps its luma ratio (2.3) but loses its *isolation*: it is a bright object in a busy field, not
    in a dark one.
- **Street life.** v1 has motion cues: streak lanes, perimeter lamps, the red warning lights on the wall.
  - v2's city has almost no lit street level. The roads between the blocks are black; only the windows and some
    roof-top dashes are lit.
  - A city at night is read through its streets. Without them the v2 fabric reads as a starfield of windows.
- **Values.** The v2 kit runs dark. 46 % (Halcyon), 41 % (Orbital), 54 % (the Solace test) and 61 % (the Meridian
  test) of the frame is under 0.10, against a 25–40 % band. The dense city is mostly dark facades.

**What reads better in v2:**
- **Grounding.** The compound now sits *in* the city.
  - v1 Orbital floats on a black void with orange fog squares.
  - v2 places it in a real downtown, with a believable scale cue: the windows give the floor height.
- **Repetition.** It is lower in v2. v1's pylon grid and parallel streaks are more periodic than v2's
  randomised window dots (p90 0.58 / 0.77 in v1 vs 0.37 / 0.31 in v2).
  - So the kit's window placement is not visibly tiled. The problem is evenness, not tiling.
- **Landmark storytelling.** Orbital v2 puts a real rocket on the pad. In v1 the pad held a yellow coil.
- **Values in the decision shots.** They are mostly in band in both versions. v2 Halcyon decision (median 0.167,
  32 % under 0.10) is better than v1 there.

## Pair 3: the whole city key art

**Custom:** round 30 `city_night_hq_v6` (the mainline toon look, labels baked in, masked for the metrics).
**Procedural:** `city_all_corps_night` (AAA-2). The `v1` scratch copy is byte-identical to the current file.

| | custom v6 | procedural night | procedural mainline |
|---|---|---|---|
| median / < 0.10 | 0.237 / 9 % | 0.129 / 27 % | 0.225 / 0.1 % |
| mean Sobel | **0.067** | 0.028 | 0.037 |
| bright blobs / MP | **1574** | 48 | 314 |
| hue entropy / top cluster | **4.57 bits / 22 %** | 2.62 bits / 68 % | 1.87 bits / 76 % |
| detail CV | 0.10 | 0.64 | 0.57 |
| landmark ratio (Halcyon) | 1.30 | 1.41 | 1.30 |
| horizon std, min 1/4 window | (no horizon) | 0.008 | 0.007 |

**What reads better in v6, and why:**
- **Districts read without labels.** Each district has its own ground colour, as roads and roofs: the Meridian
  orange grid, the Halcyon violet, the Solace teal-green, the Rebel Cell red.
  - Each district also has its own massing: Meridian low and wide, the Sprawl tall and spiky, Halcyon stepped.
  - The palette has 6 balanced clusters, none above 22 %.
  - The procedural night is 68 % one steel blue. Its districts show only as faint tinted patches.
- **Building mass.** In v6 every building is a lit, shaded volume with a dark ink edge, and there are thousands of
  window and roof lights (1574 blobs/MP, Sobel 0.067).
  - The procedural night draws the blocks as thin outlines on a dark ground (48 blobs/MP, Sobel 0.028), which is
    the rejected wireframe direction the AD review flags.
- **Landmarks.** In v6 they read by scale, silhouette and colour: the Solace helix, the Halcyon ziggurat with the
  eye, the Orbital disc. Their *luma* ratio is low (1.3), because the whole map is bright.
  - In the procedural night they are small, and no brighter than the fabric (1.41). The beams are what the eye
    follows (49 % of the top-1 % light sits in one cell, the beams' crossing).

**What reads better in the procedural city:**
- **Atmosphere and depth.** It has a sky, a sea, a coast, beams, value falloff and a real AAA-2 value band (median
  0.129, 27 % under 0.10).
  - v6 is a flat, even carpet: detail CV 0.10, no calm tiles, no depth falloff. As key art it is busy everywhere.
    This is the one place where the custom shows the "even carpet" fault.
- **One layout.** It is the true one-city layout, so every netrun and HQ can be traced back to it.

**Where it falls short:** the horizon is ruler-straight (built-top std 0.008 in its flattest quarter), as the AD
review says.

## The anchor: the mainline City Grid

The main W3_HQ capture and the storyboard HQ (mainline kit) are close to each other:
- median 0.181 vs 0.171;
- 13 % vs 11 % under 0.10;
- top hue 248° (violet-blue) in both, at 48 % vs 68 %.

The procedural city's mainline render sits close to them in value (median 0.225, top hue 248°). It is more
saturated (98 % chromatic pixels vs 49–70 %) and more mono-hued (76 % top cluster). So the mainline look is matched
in value but not yet in hue spread.

## Ranked gaps (procedural vs custom) and the generator rules that close them

The rules are parameterised, and each one has a metric in `metrics/rules_check.md` where one exists. The thresholds
come from the custom images that pass, with headroom. They are starting values: put them behind config (the
CLAUDE.md "no magic numbers" rule) and re-tune them after the round-1 finals.

### 1. Street-front silhouette is low and flat (street)
- **Lit skyline std:** 0.115 vs 0.229.
- **Flattest quarter:** 0.031 vs 0.140.

**Rule `frontage.silhouette`:**
- Route columns and frontage buildings on a netrun street:
  - rise to at least `frontage_min_floors` (6, already approved);
  - follow a seeded height rhythm, with neighbour heights differing by at least `height_step_min` (2 floors);
  - have at least 1 in 3 columns topped by a crown (a setback, spire, roof box or sign frame).
- **Test R-SIL-1:** lit-mass skyline std ≥ 0.15 frame heights.
- **Test R-SIL-2:** ≥ 0.08 in every 1/4-frame window.
- **Also:** no more than `max_equal_tops` = 2 adjacent buildings with tops within 1 floor of each other.

### 2. Hero signage and dressing are missing (street, HQ city)
- **Sobel:** 0.021 vs 0.032.
- **Bright blobs:** 328 vs 550 / MP.
- **Readable signs:** none vs about 10.

**Rule `dressing.signs`, placed by rule on the layout (the r3 NOTES' "next items for the toolkit"):**
- **Per route column:**
  - one hero sign (a blade or wall sign) in the district pair's hue, inside the column's footprint, lit at
    1.5–2.0× its local background (the luma ratio, as R-FOCUS-1);
  - one hero sign at least, inside the central 2/3 of the frame width.
- **Per frontage building:** a shopfront strip on the base, and a seeded chance `p_secondary` = 0.5 of a small
  secondary sign.
- **Per street:** at least `megastructures` = 1 (an arch board, a globe or a holo) on the tallest non-route roof
  off the decision box.
- **Per frame:** at least `signs_on_screen_min` = 6 legible text signs in the OVERVIEW.
- **Tests:**
  - R-DET-1: Sobel ≥ 0.028.
  - R-DET-2: ≥ 450 bright blobs / MP.
  - Plus a placement check that every sign sits on a building face (no floating r2 dressing).

### 3. The even carpet: no rest areas, so no focal hierarchy (HQ v2; the street goes the other way)
- **Detail CV:**
  - Halcyon: 0.29 vs 0.59.
  - Orbital: 0.36 vs 0.74.
  - Meridian: 0.29 vs 0.65.
- **Calm tiles:** 4–9 % vs 25–32 %.
- **The street fails the other way:** 40 % calm, with an empty sky and dead roofs.

**Rule `density.falloff`:**
- **Around the compound:**
  - a quiet apron of at least `apron_bu` (the v1 perimeter width, 160–292 BU) of low or no buildings;
  - the city's lit-window density ramps from `near_k` = 0.25 at the apron edge to 1.0 at `ramp_bu`;
  - beyond that, cut window density in seeded patches (`dark_block_share` = 0.2 of the blocks fully dark).
- **Tests:**
  - R-CALM-1: netrun views have a detail CV of 0.45–0.85.
  - R-CALM-2: 12–32 % calm tiles.
- **Note:** the mainline map and the v6 key art are intentionally even carpets. The rule is scoped to the netrun
  views.

### 4. No street-level light in the city fabric (HQ v2, city)
v1's streak lanes and lamps carry the "city at night" read. In v2, only the windows are lit.

**Rule `streets.light`:**
- Every road segment visible to the camera carries:
  - streak lanes (the r3 `street_lanes` rule, with the fractions per road class);
  - street-lamp chains every `lamp_step` BU;
  - lit shopfront bases on `p_shopfront` = 0.6 of the street-level facades.
- **Test (to add):** at least 25 % of the bright pixels in the HQ OVERVIEW fall on the road mask. That needs a road
  ID pass from the kit; until then, compare blobs/MP and streak counts.

### 5. Palette collapses to one hue (street, city)
- **Hue entropy:**
  - Street: 3.53 vs 4.47 bits.
  - City: 2.62 vs 4.57 bits.
- **Top cluster:** 55–68 % vs 22–27 %.

**Rule `palette.districts`:**
- Each district in view must own at least `district_hue_min` = 4 % of the chromatic pixels, in its own hue, through:
  - its fog bank glow (the r3 bank glows, in alternating district colours);
  - its trims;
  - its ground and roads.
- The ambient fill hue is capped so that no hue cluster exceeds 45 %.
- **Tests:**
  - R-HUE-1: entropy ≥ 3.8 bits.
  - R-HUE-2: top cluster ≤ 45 %.
- **Exemption:** HQ interiors and corp HQs are allowed one corp hue (Meridian is 73 % orange in v1, and that is
  correct).

### 6. Fog and depth planes are not built on the one-city fill (street)
- The sky above the skyline is empty.
- The beams stand in clear air.
- There are no plumes and no mid haze band.

**Rule `atmosphere.layers`:** run the r3 fog rules (city field, banks, wisp, plumes, beam filter) on the one-city
heightfield, with these additions:
- `sky_max_share` = 0.25: the frame above the lit skyline may be at most 25 % empty sky. Otherwise pull the
  backdrop tower rows forward or raise the camera tilt.
- Every beam must cross fog density above `beam_fog_min` for at least 60 % of its on-screen length.
- At least 3 depth planes with distinct mean luma: backdrop, mid, front. Adjacent planes differ by at least
  `plane_step` = 0.03 median luma, measured in the depth bands.
- **Test:** R-CALM-2's upper bound catches the empty sky now (40 % calm fails). A depth-banded luma test needs the
  Z pass, which the kit has.

### 7. The street foreground is rooftops, not street (street)
The bottom 20–25 % of the procedural frame is the cut roof grid.

**Rule `foreground.street`:**
- At the OVERVIEW camera, the bottom band (`fg_band` = 0.20 of the frame height) must show the road surface:
  wet material, at least 2 streak lanes, and kerb lamps.
- Cut buildings in that band are allowed only as near-black edge silhouettes, at the frame's side edges (the r3
  "foreground silhouettes" rule).
- **The fix:** move the camera target or lower the street fill in front of the road. Do not paint over it.
- **Test (to add):** the lower-band hue entropy and blob count must reach 80 % of the full-frame values.

### 8. Landmarks don't lead (city key art; marginal on the street)
- **Halcyon in the city:** a landmark ratio of 1.41 (v6 is 1.30, but v6 reads by scale and silhouette).
- **Meridian HQ:** 1.09 / 1.25.

**Rule `landmark.lead`:**
- Each corp landmark in frame:
  - is lit at ≥ 1.5× its ring luma;
  - covers ≥ `lm_area_k` = 6× the median block's on-screen area;
  - carries a rim or outline that the fabric doesn't use;
  - the hero landmark sits within 0.12 frame heights of a rule-of-thirds point.
- The beams may not out-shine the landmark: the top-1 % light must not sit in a cell without a landmark.
- **Test:** R-FOCUS-1 (all landmarks ≥ 1.5×). `lm_centre_thirds_dist` is in the JSON.

### Lower-ranked (each still gets a rule)
- **9. Ruler-straight horizon (city).** The flattest-quarter horizon std is 0.008.
  - **Rule `horizon.break`:** the coastline and the seawall get seeded inlets and headlands of amplitude
    `coast_amp`, and at least 3 skyline spikes taller than 2× the median roof, spaced at least 1/6 of the frame
    apart.
  - **Test:** R-HOR-1, built-top std ≥ 0.015 in every 1/4 window.
- **10. The v2 kit exposes too dark (HQ).** 41–61 % of the frame is under 0.10.
  - **Rule `values.solve`:** the kit's exposure solve targets a median of 0.14 and 30 % under 0.10, after the
    vignette (the city NOTES found the vignette applied after the solve).
  - **Tests:** R-VAL-1/2/3.
- **11. Same-material boxes (street, city night).** Every building is one material at a different size.
  - **Rule `materials.mix`:** at least `material_kinds` = 4 facade kits per district (glass curtain, concrete
    band, panel and grille, lit atrium), with no two adjacent buildings sharing one, and roof clutter from at least
    3 kinds.
  - **Test (to add):** a facade-crop texture-class count, or a material-ID pass histogram.
- **12. Repetition guard.** It is not a current gap: the procedural windows are less periodic than the custom
  pylons and streaks.
  - **Rule:** keep it so. No more than `max_same_module_adjacent` = 2 identical facade modules side by side.
  - **Test:** R-REP-1, autocorrelation p90 ≤ 0.60.

## What procedural already does better
- **Continuity.** The street, the HQ and the city are one layout. The street IS the map's border link. Hand-built
  sets can't promise that.
- **Grounding and scale.** The v2 HQs sit in a real downtown, where v1 sat on a black void, and the window dots
  give the floor height for scale.
- **Density on demand.** The kit fills any camera with city: 2–4× v1's bright blobs per MP. The task now is to
  *thin* it by rule, not to add more.
- **Less tiling.** The repetition p90 is 0.31–0.37 in v2 against 0.58–0.77 in v1. The seeded window placement does
  not read as a stamped grid.
- **Consistency of values.** The procedural street frames sit in the AAA-2 band without hand grading (f_0340: 0.124
  / 36 % / 0.6 %). The kit can hit the band once the solve is fixed.
- **Atmosphere at city scale.** The city night has a real sky, sea, value falloff and beams. The v6 custom is a flat
  carpet with no depth.
- **Better story props where the rule knows the story.** The Orbital v2 rocket, and the Meridian crane as the
  street's landmark.

## Limits of these numbers
- **Pair 1's cameras differ.** The custom is closer and taller in frame, so part of the silhouette and detail gap is
  framing. The storyboard NOTES' frontage rule (a) is the same fix.
- **The v6 key art is a different look** (the mainline toon). Values and saturation are not comparable to the AAA-2
  night. The hue spread, the massing and the landmark reads are.
- **f_0340 is a 1280 frame with film grain.** The grain fills every tile with texture, so its calm share (0 %) and
  its built-top profile are not reliable. The lit profile is fine.
- **The v3_dynamic overview and the anchor panels** still carry route overlays and labels outside the masks. Treat
  their palette and blob counts as approximate.
- **The landmark boxes are hand-placed per camera** in the config. A new framing needs them moved.
