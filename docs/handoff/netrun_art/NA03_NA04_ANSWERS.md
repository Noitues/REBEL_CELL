# Art-pass answers to the NA-03 / NA-04 open questions

Date 2026-10-18. Answers the "Art-pass to answer (sent 2026-10-18)" lists in `docs/handoff/netrun_art/NA03_MODULES.md`
(O-C, O-D, O-G, O-H, O-K) and `docs/handoff/netrun_art/CHECKS_SPEC.md` (O-1, O-4, O-5, O-6, O-7, O-9, O-10, the stale
rail cite, R-VAL-1), plus two opinions on build-session calls.

**Conventions.** All citations are `file:line` at art-pass commit `6a58733c`, paths relative to `docs/concepts/` (short
names as in `route_map_graph/PIPELINE_SPEC.md` section 0: `CAC/` = `city_all_corps/scripts/`, `M44/` =
`route_map_graph/storyboard/scripts/m44/`, `SB/` = `route_map_graph/storyboard/scripts/`, `HK/` =
`route_map_graph/hq_meridian/scripts/hq_kit/`, `V3D/` = `route_map_graph/side_view/v3_dynamic/scripts/`, `PVC/` =
`route_map_graph/proc_vs_custom/scripts/`). A line marked **AD call (provisional)** is a judgment, not a code fact. A
line marked **Fact** is read straight from the code. The spec was not edited; its fixes are listed in "Spec edits" at the end.

The kit-unit factor throughout is `k_units` = 1.9 / 8 = 0.2375 (spec section 8, rescale rule).

---

# NA03

## O-C: shapes of `zoned.json`, `city_base.json`, rail and corridor polylines

**Short answer.**
- Fact: the concept `zoned.json` is one `json.dump` of a dict, no sorting, **lots** for every x/y, heights in **game
  height units** (multiply by `KH` = 0.165706 for BU). It has no `version`, no `layout_seed`, and the rail is a bare list of
  points with **no `deck_z`** and no width (the spec says the file carries `deck_z`; the concept keeps it in
  `city_preset.RAIL`). So the v1 file is a new schema: the field list below is the concept content, with the unit and
  the additions the port must make.
- Fact: there is no `cfg["corridor"]` in the one-city path. `cfg["corridor"]` (segments `(ax, ay, bx, by, half)`) and
  `cfg["corridor_low"]` exist only in the HQ kit, in **kit units** (O-H). The one-city rail is the polyline `rail` plus
  a width, from which the `(ax, ay, bx, by, half)` segments are derived.
- AD call (provisional): write `zoned.json` and `city_base.json` in **BU plan coordinates**, like `city.json` and
  `net.json` (NA02 Ruling O3), with `x = (lot_x - 6) * 6`, `y = -(lot_y - 6) * 6` (`M44/layout36.py` `W()`), heights in BU
  (`h * KH`). Keep `lots` out of the new files; the one remaining lot-valued number is `side_d` (O-H), which the file
  stores already converted.

### `zoned.json` (concept fields, `CAC/zoning.py:702-714`, `json.dump` at :715)

Types: `pt` = `[x, y]` floats; `poly` = list of `pt`; ids are strings. Unit column: L = lots (concept), BU = after the
conversion above, h = game height units.

| Field | Type | Unit | Meaning |
|---|---|---|---|
| `centre` | pt | L | `[6.0, 6.0]` (CX, CY) |
| `U`, `KH` | float | BU/lot, BU/h | 6.0, 0.165706 (`CAC/city_preset.py:19-20`) |
| `b_coast`, `b_split` | float | L (axis b) | seawall depth; split of the drowned quarter (`zoning.py:82-130`). `ab()` is the 45-degree screen frame, `zoning.py:41-48` |
| `lagoon_a` | [float, float] | L (axis a) | drowned quarter extent |
| `bay` | object | L | `BAY` (`city_preset.py:150`): `depth, width, head_start, head_k, min_water`, plus `ac` (bay centre a) |
| `hq` | {corp: pt} | L | final HQ lots (`zoning.py:118-129`, tethys pole `:158`) |
| `hq_old` | {name: pt} | L | previous HQ lots (refilled) |
| `hq_clear` | {aurelian, tethys: float} | L | HQ clearance extras |
| `landmarks` | [corp] | - | corps that have a landmark footprint |
| `clusters[]` | `{c:int, n:int, mean_b:float, centre:pt, to:"tethys"/"aurelian"/"sprawl"}` | L | the k-means result (Z2/Z3) |
| `buildings[]` | see below | | one entry per building (12 000 to 14 000) |
| `tiles[]` | `{q:poly, ab:[pt,pt] or null, col:[r,g,b] or null, tr:float, i:int, j:int, terr:str, wet:0/1, sub:float, u:float, lm:0/1, art:0/1}` | L | street tiles; `ab` = the lane segment; `tr` = lane traffic 0..1 (`zoning.py:283-297`, `:690-692`) |
| `plazas[]` | `{q:poly, terr:str, wet:0/1, sub:float}` | L | `:298-311` |
| `trails[]` | `{a:pt, b:pt, col:[r,g,b]}` | L | passthrough of the layout |
| `fist[]` | `{a:pt, b:pt}` | L | passthrough (Rebel Cell outline) |
| `lagoon_cells[]` | `[i:int, j:int, sub:float]` | cell index, L | `:354` |
| `arterials[]` | `{axis:"x"/"y", line:int, a:pt, b:pt, tr:float, col:[r,g,b], n:int, ext:[lo,hi]}` | L | `:377`, `ext` set at `:662-674` |
| `aqueduct` | `[pt, pt]` | L | `:420-423` |
| `rail` | list of pt, spacing about 0.5 lot | L | the freight-rail polyline, `:400`, written at `:708` |
| `highways[]` | `{name, pts:[pt..], z:float, to_port:bool}` | pts L, z BU | `:485` (z 24 / 30 BU, `city_preset.py:223-224`) |
| `ring` | `{pts:[pt..], z:float, w:float}` | pts L, z, w BU | `:515` (z 12, w 6) |
| `ramps[]` | `{pts, ends:[str,str], w:float}` | pts L, w BU | `:524` |
| `hub` | `{pts, w}` | L, BU | `:711` |
| `metro` | null | | always null in r3 (`:517-560`); drop it |
| `port` | `{a0,a1,depth,quay,z, wall:[[a,b] x41]}` | L (a,b), z BU | `:657` |
| `corr_cells` | `[[i,j]..]` | cell index | lot cells cleared by paths and the port (`:647, :654`) |
| `terr_count` | {district: int} | count | |
| `n_fill, n_crest, n_drowned, n_art, n_border` | int | count | diagnostics; drop from v1 |

`buildings[]` entry (`zoning.py:234-260`, `:680-695`; base fields from `CAC/../M44/citydata.py:165`):

| Field | Type | Unit | Meaning |
|---|---|---|---|
| `key` | int | | building key (refill blocks use 900000 + ...). Maps to `bid` in the game files |
| `q` | poly | L | footprint polygon |
| `c` | pt | L | centroid (`zoning.py:238`) |
| `z0`, `h` | float | h | base and height in game height units (x `KH` = BU). `h` is rewritten by the rail cap (`:693-695`) |
| `ts` | float | | taper scale, 1.0 = none |
| `ink` | [r,g,b] | | outline colour |
| `terr` | str | | district id (`rebel_cell, meridian, solace, orbital, aurelian, halcyon, tethys, ""`) |
| `ci` | int | | layout context index (-1 for refill blocks) |
| `u` | float | 0..1 | urban-core factor (`:260`) |
| `sub`, `wet` | float, 0/1 | L | subsidence and drowned flag |
| `crest`, `art`, `border`, `rail_side` | 0/1 | | `crest` always 0 in r3; `art` on an arterial; `border` = another district's building within 2 lots (`:680-683`, **this is a district border, not a netrun border link; see O-D**); `rail_side` within `side_d` of the rail (`:691`, absent on wet buildings) |

### Required additions for v1 (not in the concept file)

Fact for each: the value exists in `CAC/city_preset.py` but is not exported.

```
"version": 1, "layout_seed": "<decimal u64>",
"rail": {
  "pts":    [[x, y], ...],        # BU plan, ~3 BU apart (0.5 lot step, CURVES.step)
  "w":      4.8,                  # BU, zoning.py:460 (2.8 + 2.0)
  "half_clear": 4.5,              # BU: w/2 + CURVES.clear_margin*U = 2.4 + 2.1 (zoning.py:636, city_preset.py:208)
  "deck_z": 17.5,                 # BU, RAIL.deck_z (city_preset.py:162)
  "side_cap": 15.5,               # BU, RAIL.side_cap
  "side_d": 7.2,                  # BU = RAIL.side_d 1.2 lots * 6 (O-H)
  "pier_step": 7.0, "ramp": 60.0, "end_ramp": 45.0, "signal_step": 36.0   # BU, RAIL
}
```

The corridor segments that spec 12.4.1 and `in_corridor` (`HK/downtown.py:397-410`) want are derived, not stored:
for each consecutive pair of `rail.pts`, `(ax, ay, bx, by, half_clear)`. `in_corridor` samples the segment every 2 BU
(`downtown.py:403-404`), which is coarser than the 3 BU polyline spacing: sample by distance-to-segment instead.

### `city_base.json` (spec 2.2 intermediate)

Fact: it is the concept `unified.json` written by `M44/citydata.py:131-187` (`export`) and then read by
`SB/sb_onecity.py:apply_layout_rules` (`:80-140`, writes `unified_v3.json`). Keys: `centre, radius, tiles[], buildings[],
plazas[], trails[], fist[], fist_col, fist_half, terr{}, street, ground, hqs{corp: pt}, cell_base: pt`. Entry shapes are
the `tiles[]` / `buildings[]` rows above without the zoning additions (`tiles: {q, ab, col, tr, i, j}`,
`buildings: {q, z0, h, ts, ink, terr, ci, key}`, `plazas: {q, terr}`).

AD call (provisional): `city_base.json` stays an **in-memory structure** (as NA-03 proposes). It is `city.json` v1 before
`layout.rules` runs, so its schema is exactly the `city.json` schema; no separate file or schema. The two rules that
change it are `frontage_min_floors` 6 and `border_street_width` 8.0 BU (`SB/sb_onecity.py:69-70`), applied to border
links (O-D).

---

## O-D: which links are "border links"

**Short answer (AD call, provisional, computable from `net.json` v1).** A link is a border link iff

1. `link.state` is `"open"` or `"opened"` (a locked link is not traversable, `GridState.neighbors`), and
2. exactly one endpoint has `state` in `{"core", "owned"}`, and
3. the other endpoint has `state` in `{"corporate", "taken"}`.

Links between two owned nodes, links touching a `"cleared"` node, and corporate-to-corporate links are not border links.
No `corp` or owner field is needed (v1 has none; NA02 O9).

**Evidence (Fact).**
- The concept's `"border"` is not a territory boundary. `M44/layout36.py:build_network` creates link states `owned`,
  `border`, `grey`, `white`. `"border"` is created only at `layout36.py:222`: a link from a connected owned node (or the core)
  to a node whose state is `"available"`. `"grey"` (used-up Sites) gets a `"grey"` link; `"white"` Sites (not yet
  available) get `"white"` links (`:212-229`).
- Node states in the concept (`layout36.py:189-198`): `available` = a Site one step beyond the owned ring, toward the corps (orange);
  `grey` = used up; `white` = not yet available. So a border link is the player's frontier: territory to the next runnable Site.
  The consumers confirm it: `transit_view` calls it "owned -> available" (`layout36.py:234`); `apply_layout_rules` widens the
  streets of border links only (`SB/sb_onecity.py:103`); `sb_onecity.py:5` calls it the selected Site's border link.
- Mapping to the game: GDD 4.2 / `GridState`: "Raids start from corporate Sites adjacent to your territory" (GDD line 189) and "A TAKEN
  Site next to your territory becomes a raid entry point" (GDD line 214). `available` therefore equals
  `CORPORATE` (or `TAKEN`, the reclaim netrun target) adjacent to a `CLAIMED` or home Site. `grey` equals `CLEARED` (GDD 233: cleared Sites are
  used up). In `net.json` v1 terms those are `corporate`, `taken`, `cleared`, `owned`, `core`.
- Difference from the concept: the concept links each available Site to its single nearest owned node. A real grid can have several
  owned neighbours of one corporate Site; the rule above marks all of those links. That only widens more streets (still a pure
  function of v1 fields, ties irrelevant). `transit_view` needs at least one border link (`max()` of an empty list would raise,
  `layout36.py:236`): if there is none, `layout.rules` is a no-op and `derive.street` uses the selected Site's own link.

---

## O-G: zoom convention

**Short answer.** Two named parameters, never an unqualified `zoom`, both functions of the camera distance `d` (BU), per
spec 5.1 (Designer Q3: LOD by distance).

| Name | 0 | 1 | Formula | Concept |
|---|---|---|---|---|
| `zoom_dive` | the HQ page camera (distance `d0`) | the street OVERVIEW (distance `d1`) | `log(d0 / d) / log(d0 / d1)`, clamped 0..1 | `SB/sb_ocjobs.py:94-102` (`zoom_of`); consumers `look_w` `:105`, `zcut` `:111` |
| `zoom_detail` | the street OVERVIEW (`d_ov`) | DECISION (`d_dec`) | `log(d_ov / d) / log(d_ov / d_dec)`, clamped 0..1 | `HK/lod.py:33-34` (`zoom`) |

Fact: the clash is real and has no code reconciliation. `HK/lod.py:4` documents "0 = OVERVIEW .. 1 = DECISION"; `LOD_BANDS`
(`lod.py:16-23`) carries the same six number pairs as the storyboard's `lod_bands` (`SB/look_preset.py:74-80`), whose header says
"0 = city aerial, 1 = street" (that is the dive axis). The numbers 0.25-0.60 etc. mean different distances on the two axes.

**Module proposal (AD call, provisional).**
- `lod.weights(d_bu, bands=None, floors=None)` takes a **distance** and uses the spec 5.2 distance table as the normative band
  data (`d(z) = d0 * (d1 / d0)^z`, d0 = 3833, d1 = 114.6; e.g. `fog_octaves` 0.25 -> 3833 * 0.4157 = 1593, matching 1594). Keep the
  `FLOORS` of `lod.py:25` (signage 0.0, small lights 0.25). This is what the street and the HQ both call; no band reads a zoom number.
- `lod.zoom_dive(d, d0, d1)` and `lod.zoom_detail(d, d_ov, d_dec)` are the two converters above. `zoom_dive` is used only for `look_blend`,
  the section cut (`z_cut`) and the fog / city-glow level ramps (all path parameters of the dive); `zoom_detail` only for the HQ exposure by zoom.
- Mapping between them when the HQ OVERVIEW camera is the street OVERVIEW (`d1 == d_ov`, spec 5.1 table): both are affine in `ln d`, so
  `zoom_dive = 1 + zoom_detail * ln(d_ov / d_dec) / ln(d0 / d_ov)` for `zoom_detail >= 0` (`zoom_dive` itself saturates at 1 there;
  below `d_ov`, every dive band is already complete).
- `poses_<run>.json`: store `zoom_dive` and `zoom_detail` as two floats (not one `zoom`); the sb_ocjobs `zoom_hq` / `zoom_dive`
  naming in NA03 section 3.x becomes `zoom_dive` plus `zoom_detail`. The `lod_bands` table lives in `look.preset` (spec 2.2); until that module exists,
  `lod` ships the distance table as `DEFAULT_BANDS` and `look.preset` re-exports it.
- `d_dec` has no concept value (`lod.zoom` only receives it as a parameter, no caller in `hq_meridian`). It must come from the HQ DECISION
  pose (`HM/hq_cam.py`); do not invent one.

---

## O-H: units of `RAIL.side_d` and `corridor_low`

**Short answer (Fact).**
- `RAIL.side_d` = 1.2 is in **lots**. `zoning.py:684-691`: `dmin` is a distance between lot-coordinate points (footprint corners `b["q"]`, centroid `b["c"]`)
  and the lot-coordinate rail `simp`, and is compared with `RA_["side_d"]`; the comment at :684 says "within side_d lots". So
  `side_d` = **7.2 BU**. `RAIL.side_cap` 15.5 and `deck_z` 17.5 are BU (the same block converts `side_cap` with `KH`, `:693`).
- `corridor_low` (the HQ-kit tuple in `HK/downtown.py:425-439`, presets `route_map_graph/hq_meridian/scripts/hq_preset.py:118, 124`) is in **kit units**
  (storey 8 BU). Fields: `(dist, hmax, s0, grade, zmax, clear, hmin)` = (distance from the corridor axis, max height, start distance along the
  corridor, grade, max deck height, clearance under the deck, min height). Evidence it is kit units: `zmax` 73.7 * 0.2375 = 17.50 = `RAIL.deck_z`; `clear` 16 * 0.2375 = 3.8.
  Converted (Meridian preset at :118): `(10.93, 13.70, 11.88, 0.03, 17.50, 3.80, 1.90)` BU; the variant at :124 has `dist` 40 -> 9.5 BU. The corridor
  `half` values 9.0 / 6.5 become 2.14 / 1.54 BU, and the straight corridor `(66, 100) -> (66, 1250)` becomes `(15.7, 23.8) -> (15.7, 296.9)`; that straight kit viaduct is
  superseded (spec 3.4 L4).
- `cfg["corridor_low"]` is used by the HQ downtown only (`downtown.py:121`, `city_ring.py:122`). The one-city path never builds that tuple.

**Consequence / AD call (provisional).** The two mechanisms disagree: one-city uses 7.2 BU and a flat 15.5 BU cap; the kit used about 10.9 BU and
a graded cap (`13.7` max, `deck - 3.8`). Unify on the zoning mechanism (`rail.side_d`, `rail.side_cap`, both in `zoned.json`) and retire the kit tuple from the
pipeline; the HQ scene then reads the rail from `zoned.json` (spec 3.4 L4 already says so). The spec 12.4.2 threshold ("every top <= `deck_z - 2` = 15.5 BU within
`corridor_low` distance") becomes "within `rail.side_d` = 7.2 BU of the polyline, every top <= `rail.side_cap`". The generator also scales caps by a spread of 0.7-1.0
(`downtown.py:439`), so the check never fires where the generator is correct.

---

## O-K: kit-unit constants

Rule used: every length in the HQ kit (`HK/*.py`, `hq_preset.py`, `HM/*`) is in kit units and converts with `k_units` 0.2375; every length in `city_preset.py`,
`M44/*`, `SB/*` is already one-city BU. Unitless numbers (opacity, tangents, grades) do not convert.

| Constant | Source | Concept value | Kind | One-city BU | Note |
|---|---|---|---|---|---|
| `OCC.stub` | `HK/downtown.py:319` | 6.4 | kit | 1.52 by conversion | **Not converted.** Spec 7.2's **3.8 BU = 2 * floor_bu** is an AD ruling (C1; the rule says a 1-2 floor stub), not `6.4 * 0.2375`. Keep 3.8 as already one-city. |
| `CLUTTER` | `HK/section.py:35` | 25.0 | kit | 5.94 (spec: "6 BU") | Spec 7.2 is right; keep one constant. `downtown.py:392` hard-codes `25.0` again: the port must use the single constant. |
| `section_params` band, overview | `HK/downtown.py:307, 310` (`k[1]*... + 30.0`, `k[1] + 30.0`) | 30.0 | kit | 7.125 | Pad added to the keep's lateral support. |
| `section_params` band, rooms | `downtown.py:302` (`... + 24.0`) | 24.0 | kit | 5.70 | Pad added to the rooms' lateral support. |
| `section_params` `margin` | `downtown.py:277` (default `margin=1.5`, subtracted at `sec_zref=zr - margin`) | 1.5 | kit | 0.356 | An absolute height offset, not the 10 % cone margin of `OCC.margin` 0.10 (name collision with spec 7.2 `margin`): name it `zref_margin`. |
| `OCC.margin`, `ghost`, `edge`, `tsoft`, `vsoft` | `downtown.py:319` | 0.10, 0.18, 0.6, 0.035, 0.025 | unitless | same | no conversion |
| front fade | `downtown.py:386`, `section.py:114` (`_sstep(..., 6.0)`) | 6.0 | kit | **1.425** | Spec 7.2 lists "6.0 BU": that is a kit number; convert it. AD call. |
| edge band | `section.py:127` (`w = 0.4`) | 0.4 | kit | 0.095 | Spec 7.2 lists 0.4 BU; convert. Ground tolerance `0.16` (`section.py:134`) -> 0.038. |
| `NK` | `downtown.py:320` | 5 | count | same | |
| `POCHE`, `EDGE_COL` | `section.py:33-34` | colours | - | same | |
| `RAIL.*` (`deck_z, side_cap, pier_step, ramp, end_ramp, signal_step`, widths) | `city_preset.py:162-163` | 17.5, 15.5, 7.0, 60, 45, 36 | one-city BU | same | `side_d` is lots (O-H); `gate_u, wall_s, gate_out` are BU (`zoning.py:386`); `coast_reach` unused in r3. |
| `RULES.floor_bu, front_band, room_inset, room_depth` | `SB/sb_onecity.py:36-39` | 1.9, (0.8, 6.5), 0.45, 2.6 | one-city BU | same | |

**AD call (provisional): `k_fit`.** The section band pads (7.125 / 5.70) and `zref_margin` (0.356) are lengths in the city around the landmark, not parts of the landmark,
so they take `k_units` only. The landmark support they are added to already carries `k_fit`. If the build session scales the whole HQ scene uniformly by `k_fit`
(spec 8.6.2), apply `k_fit` to the 5.70 / 7.125 / 0.356 instead; this should be decided with the HQ camera numbers, and is the one
O-K item that needs a second look when the first HQ slot generator runs.

---

# CHECKS (NA-04)

## O-1: `capture.json` fields that scope the 12.7 (and 12.1) rules

**Short answer (AD call, provisional): add these keys to `capture.json`; they are optional extra keys (v1-compatible), unknown keys ignored.**

| Key | Values | Used for |
|---|---|---|
| `kind` | `"street"`, `"hq"`, `"city"` (equals `derive.kind` for the first two) | the netrun type |
| `view` | `"overview"`, `"decision"`, `"hover"`, `"street"` (close street level), `"city"` (whole-city key art) | which phase of the beat |
| `look` | `"aaa2"`, `"mainline"`, `"blend"` | R-VAL scope |
| `look_blend` | float 0..1 (0 mainline, 1 AAA-2); required when `look == "blend"` | the 12.1 exempt rule (0 < look_blend < 1) |
| `corp` | corp id, `""` for street and city | HQ exemptions |
| `exempt` | `{hover_cut: bool, red_seq: bool, flash: bool}` | 12.1 / 12.7 exemptions |

Scope table (the reference scoping from `PVC/run_proc_vs_custom.py:58-60, 146-163`, rewritten on those keys; the left column is the
reference `RC` scope name):

| Rule | Reference selection | On `capture.json` |
|---|---|---|
| R-SIL-1/2, R-DET-1/2 (`side`) | `SIDE_IDS` or `view == "side"` (`:59, :151`) | `kind == "street"` and `view == "overview"` (also `decision`? **no**: the reference excludes `street_close`) |
| R-CALM-1/2 (`netrun`) | not `CITY_IDS`, not `a_*`, not `p_tethys` (`:160`) | `kind in {"street", "hq"}` |
| R-HUE-1/2 (`street_city`) | `SIDE_IDS` or `CITY_IDS` or view in (`side`, `street_close`) (`:154`) | `kind in {"street", "city"}`; `kind == "hq"` exempt (spec 12.7 "corp HQ views exempt") |
| R-VAL-1/2/3 (`aaa2`) | not in `NOT_AAA2` (`:58, :149`) | `look == "aaa2"` and no `exempt` flag and not (`look == "blend"`) |
| R-FOCUS-1 (`landmark`) | an `lm_ratio` exists (`:152`) | the id.png has class {1, 5, 6} pixels (O-4) |
| R-HOR-1 (`city`) | `CITY_IDS` and a `sky_std` measured (`:156`) | `kind == "city"` |
| R-REP-1 (`all`) | always | always |

Exemption flags: `exempt.hover_cut`, `exempt.red_seq`, `exempt.flash` for any 12.1 check; `look == "mainline"` is held to median 0.214 +- 0.03 (spec 12.1)
instead; 0 < `look_blend` < 1 is reported only. `view == "hover"`: exempt from 12.2 (spec 12.2 "hover frames exempt").
Fact: `capture.json` today has no such keys (`CHECKS_SPEC.md` 1.1, `PIPELINE_SPEC.md:1351`); the reference decides by image id and config file.

---

## O-4: no landmark in frame

**Short answer (AD call, provisional): skip with a report, status `"n/a"`, not fail** when the capture does not expect a landmark. Two cases:

- `kind == "hq"` and `view in {"overview", "decision"}`: the frame must contain a landmark. Zero pixels of classes {1, 5, 6} here is a real error
  (the landmark was cut out of frame): **fail**, note "landmark absent".
- Anything else (street, city, street close, hover): no {1, 5, 6} pixels -> `{status: "n/a", value: null, note: "no landmark in frame"}`.

Also `n/a` (never a crash): an empty local-background mask (no {0, 2} pixel inside the grown box), and an empty ring in R-FOCUS-1.

Evidence (Fact): the reference crashes or silently drops on both cases. `HM/hq_values.py:30` calls `ys.min()` on an empty mask (raises); `:37` omits `ratio`
when the background mask is empty; `PVC/pvc_metrics.py:252-268` divides by `max(lr.mean(), 1e-4)` (a NaN ring gives NaN). The reference table treats a missing or
NaN value as `n/a` (`PVC/run_proc_vs_custom.py:180`: `val is None or np.isnan(val)` -> `"n/a"`). The spec's record status set (pass, warn, fail) has no `n/a`; the
cleanest fix is a fourth status `"n/a"` that exits 0 and is listed in the report (the alternative in `CHECKS_SPEC.md` 1.2, `pass` with `note: "n/a"`, loses the difference between "passed" and "not applicable").

---

## O-5: unit of the `corridor_low` distance in 12.4

**Short answer.** In 12.4 the distance is **BU one-city**: `rail.side_d` = 7.2 BU (1.2 lots * 6), read from `zoned.json`. See O-H for the evidence and the kit-unit tuple
(46 kit units = 10.9 BU) that this replaces. The check is "every building top within 7.2 BU of the polyline is <= `rail.side_cap` 15.5 BU". The check inputs are `zoned.json` and
`city.json` heights in BU; no unit conversion sits inside the check. Note for a golden test: `city.json` heights are BU and `zoned.json` building heights in the concept are game units (O-C).

---

## O-6: mapping `check_occlusion` classes to `id.png`

**Short answer.** The check needs more than the class: it needs the **room index** and the **layer** of the pixel. The reference sem pass carries them already, so the id.png
addition is compatible with v1 (R stays the class): **G = room index, B = layer**, on class 5 pixels and on the cut surfaces of room columns. No separate mask.

**Evidence (Fact).**
- `V3D/scene3.py:137-142`: `SEM = (cls, room / 32, col / 10)`, i.e. R = class, G = room index, B = layer index. Classes (`scene3.py` `set_sem` call sites):

| sem R | Meaning | `scene3.py` line |
|---|---|---|
| 0.1 | facade (default), including trims | 137, 710, 733, 735, 1290 |
| 0.2 | foreground occluders and street trench | 1017, 1036, 1365, 1406 |
| 0.3 | cut surface of a room column (carries layer in B) | 703, 1032, 1298 |
| 0.5 | room surface (G = room, B = layer) | 418 |
| 0.6 | mid-row | 1120, 1382 |
| 0.7 | link structure (allowed in front of rooms, reported only) | 1010, 1363 |
| 0.85 | far city | 1148, 1232 |
| 0.95 | ground foreground | 1077 |

- `V3D/check_occlusion.py:53-58`: blocked = classes 0.1, 0.6, 0.85, 0.95, 0.2 or (0.3 or 0.5 with a layer different from the room's own `G.LAYER[i]`); links = 0.7. The opening is the
  projected `rooms[i].front` polygon shrunk by `MinFilter(7)` (:48); limit 8 % (:23). The sem image is resampled NEAREST (:35).

**Mapping to `id.png` (AD call, provisional).**

| `check_occlusion` class | `id.png` class | Counted as |
|---|---|---|
| 0.1, 0.6, 0.85, 0.2 | 2 (city) | blocked |
| 0.95 (ground foreground) | 2 in Godot; 4 (ground) in the Blender pass | blocked (both) |
| 0.5 room surface, other layer | 5 (rooms) with `B != own layer` | blocked |
| 0.5 room surface, own room | 5 with `B == own layer` | unblocked |
| 0.3 cut surface, other layer | 2 with `B != own layer` and `B > 0` | blocked |
| 0.3 cut surface, own layer | 2 with `B == own layer` | unblocked |
| 0.7 links | **3** (use the reserved class 3: "link structure") | reported only |
| (not in sem) landmark compound / movers | 1 / 6 | HQ views only: 1 blocked, 6 reported only |
| (not in sem) sky | 0 | unblocked |

Required id.png additions (all v1-compatible: R is unchanged, G and B are zero today):
- G = room index, 1-based (0 = none), on class 5 pixels (byte value, not `room/32`).
- B = layer, 1-based (0 = none), on class 5 pixels and on class 2 pixels that belong to a room column's cut surface.
- Class 3 = link structure. Leave class 4 alone (the Blender pass uses it for ground, `CHECKS_SPEC.md` 1.1).
- id.png must be unlit, nearest-sampled, no anti-aliasing, no UI (already the capture contract).

This closes the "second mask" question: not needed, but the Godot capture must write G and B, which is an NA02 header note, not a schema bump.

---

## O-7: skyline range, facade band, R-FOCUS-1 box

**Short answer (AD call, provisional): per-view defaults, keyed on `kind`/`view`; boxes from `id.png`.**

Fact: the reference has **no default** skyline range: `measure` runs `skyline()` only if the config lists it (`PVC/pvc_metrics.py:375`); the facade band defaults to
the whole frame, `spec.get("facade", [0, 0, 1, 1])` (`:372`). Values in `PVC/pvc_config.json`:

| View | skyline `rng` (fractions of height) | facade band | Source |
|---|---|---|---|
| street OVERVIEW (most) | `[0.0, 0.85]` | `[0.0, 0.10, 1.0, 0.80]` | config :17, :21, :46, :51, :56 |
| street with a low horizon (storyboard closed) | `[0.05, 0.85]` | `[0.0, 0.40, 1.0, 0.80]` | :31, :41 |
| street reveal | `[0.0, 0.70]` | `[0.0, 0.10, 1.0, 0.65]` | :35 |
| street close (DECISION) | none | `[0, 0, 1, 1]` | :60 |
| HQ views | none | `[0, 0, 1, 1]` | :75-94 |
| city key art | `[0.05, 0.40]` | none (whole frame) | p3_city config |

Proposal: defaults `skyline = [0.0, 0.85]` for `kind == "street"` and `view == "overview"`, `[0.05, 0.40]` for `kind == "city"`; no skyline for HQ; facade `[0.0, 0.10, 1.0, 0.80]` for
street overview, `[0, 0, 1, 1]` otherwise. Both overridable by `checks.composition.skyline.<kind>` and `.facade.<kind>.<view>`; the horizon fraction should
come from `capture.json` once a camera pose exists (the `0.85` is just "everything above the street").

**R-FOCUS-1 box: use `id.png`** (the box is the bounding box of classes {1, 5, 6}). Fact: the reference `RC` values come from hand-placed `landmark` boxes in the config (`pvc_config.json`
:20-21, :75), so the id.png box and the config box differ slightly (e.g. `c_aaa2r3` 1.576 with the hand box). That difference is the reason NA-04 acceptance 2 runs in
`--mode reference` (O-3): for the reference comparison, read the box from the config, not from id.png. For the production check (`--mode spec`) an id.png box is exact and cannot drift.

---

## O-9: Blender-vs-Godot tolerances

**Short answer (AD call, provisional): compare a Godot capture to the Blender golden of the same scene and pose with these tolerances; every number is unmeasured
and must be replaced by the first measured delta.** No file in the concept gives a cross-renderer tolerance. The only image tolerance in the spec is the 12.3.3 GPU-render
one (mean abs diff <= 1/255, max <= 8/255 on a 320 x 180 downsample), which is Blender-to-Blender and out of NA-04 scope.

| Quantity | Tolerance | Why |
|---|---|---|
| median luma | +- 0.02 | two thirds of the 12.1 pass half-width (0.03); the Q4 sheet shows 0.02 steps still read as the same night (`route_map_graph/decisions/DECISIONS.md` Q4) |
| share under 0.10 | +- 5 percentage points | the 25-40 % band is 15 pp wide; this is the metric that moves fastest |
| share over 0.85 | +- 1 percentage point | the threshold is 2.5 % |
| landmark ratio (12.2) | +- 0.15 | the pass band 1.5-2.0 is 0.5 wide |
| composition metrics (12.7: lit_std, sobel_mean, blobs_per_mp, detail_cv, rep_p90, ...) | +- 10 % relative | they are statistical |
| hue entropy | +- 0.2 bit; hue top share +- 0.05; calm share +- 4 pp | absolute, because these are small numbers |

Config key: `checks.tolerance.renderer` (see O-10). The tolerance applies to the *delta between the two captures*; each capture is still held to the threshold itself.

---

## O-10: schema of `checks.composition`

**Short answer (AD call, provisional): one JSON file with these keys.** Thresholds are the spec 12.7 values; constants are the `PVC/pvc_metrics.py:38-47` module constants,
so a port reads them from the file rather than hard-coding them.

```json
{
  "version": 1,
  "checks": {
    "value": {
      "median_pass": [0.11, 0.17], "median_warn": [[0.09, 0.11], [0.17, 0.19]],
      "median_pass_reference": [0.12, 0.17],
      "under_010": [0.25, 0.40], "over_085_max": 0.025, "mainline_median": [0.184, 0.244]
    },
    "landmark_ratio": { "pass": [1.5, 2.0], "warn_above": 2.0, "grow": 0.35,
                        "classes_landmark": [1, 5, 6], "classes_background": [0, 2] },
    "composition": {
      "work_w": 1280, "resample": "lanczos",
      "constants": { "bright_blob": 0.6, "chroma_s": 0.25, "chroma_v": 0.15, "rep_tile": 128, "rep_stride": 64,
                     "rep_lag": [4, 48], "rep_tiled": 0.45, "detail_tile": 64, "valid_tile_share": 0.9,
                     "built_std": 0.022, "built_run": 0.35, "lit_percentile": 80, "profile_median": 13 },
      "rules": {
        "R-SIL-1":   { "metric": "lit_std", "op": ">=", "value": 0.15, "scope": { "kind": ["street"], "view": ["overview"] }, "rule": "frontage.silhouette" },
        "R-SIL-2":   { "metric": "lit_min_q_std", "op": ">=", "value": 0.08, "scope": { "kind": ["street"], "view": ["overview"] }, "rule": "frontage.silhouette" },
        "R-DET-1":   { "metric": "sobel_mean", "op": ">=", "value": 0.028, "scope": { "kind": ["street"], "view": ["overview"] }, "rule": "dressing.signs" },
        "R-DET-2":   { "metric": "blobs_per_mp", "op": ">=", "value": 450, "scope": { "kind": ["street"], "view": ["overview"] }, "rule": "dressing.signs" },
        "R-CALM-1":  { "metric": "detail_cv", "op": "between", "value": [0.45, 0.85], "scope": { "kind": ["street", "hq"] }, "rule": "density.falloff" },
        "R-CALM-2":  { "metric": "calm_share", "op": "between", "value": [0.12, 0.32], "scope": { "kind": ["street", "hq"] }, "rule": "atmosphere.layers" },
        "R-HUE-1":   { "metric": "hue_entropy_bits", "op": ">=", "value": 3.8, "scope": { "kind": ["street", "city"] }, "rule": "palette.districts" },
        "R-HUE-2":   { "metric": "hue_top_share", "op": "<=", "value": 0.45, "scope": { "kind": ["street", "city"] }, "rule": "palette.districts" },
        "R-FOCUS-1": { "metric": "lm_ratio", "op": ">=", "value": 1.5, "scope": { "landmark": true }, "rule": "landmark.lead" },
        "R-HOR-1":   { "metric": "sky_min_q_std", "op": ">=", "value": 0.015, "scope": { "kind": ["city"] }, "rule": "horizon.break" },
        "R-REP-1":   { "metric": "rep_p90", "op": "<=", "value": 0.60, "scope": {}, "rule": "repetition.guard" }
      },
      "skyline": { "street": [0.0, 0.85], "city": [0.05, 0.40] },
      "facade":  { "street_overview": [0.0, 0.10, 1.0, 0.80], "default": [0, 0, 1, 1] }
    },
    "tolerance": { "renderer": { "median": 0.02, "under_010": 0.05, "over_085": 0.01, "lm_ratio": 0.15, "relative": 0.10 } }
  }
}
```

Fact: the thresholds equal `PVC/run_proc_vs_custom.py:41-55` (R-VAL-1 aside, see R-VAL-1 below); the constants equal `pvc_metrics.py:38-47` and the in-function values
(`0.022`, `0.35`, `80`, `13`). A missing `scope` key means "all". `op` is one of `>=`, `<=`, `between`.

---

## Rail citation: the correct line range in `CAC/zoning.py`

**Fact.** `CAC/zoning.py:353-375` at `6a58733c` is the end of the drowned-quarter cell list (:354) and the T1 arterial code (`# ---- T1 arterials` at :355, loop to :380). The rail is:

| What | Lines |
|---|---|
| L4 rail polyline: gate lot, `RAIL_WEST` waypoints, centripetal Catmull-Rom to the port (`simp`) | **381-402** (polyline built at :400) |
| path record `kind="rail", w=2.8 + 2.0` | 460 |
| landmark clearance check of every path | 606-615 |
| corridor clearing (buildings and cells within `w/2/U + clear_margin` lots; `r_` at :636) | 616-660 |
| rail-side height cap (`rail_side`, `side_d` lots, `side_cap` BU) | 684-697 |
| `rail=simp` in the export dict | 708 (`O = dict(` at :702) |
| `RAIL`, `RAIL_WEST`, `CURVES` presets | `CAC/city_preset.py:162-163, 227, 208` |

Use 381-402 for "the zoning rail"; for the clearing and the building cap cite 616-660 and 684-697. The spec's other citations of the same range (`PIPELINE_SPEC.md:338` and C8 at :1615,
`353-390`) are stale in the same way, and the `city_preset.py:149` cite for `RAIL` (:343, :346) is now :162-163.

---

## R-VAL-1: 0.12-0.17 or 0.11-0.17?

**Short answer: spec 12.1 is normative.** `rules_check.md` is not older by file date, but it still encodes the superseded provisional band.

**Evidence (Fact).**
- `PVC/run_proc_vs_custom.py:50` (`R-VAL-1 ... (0.12, 0.17)`, PASS/FAIL only) was written in commit `018dcbb1` (2026-10-15) and was never changed.
- The designer ruling is `route_map_graph/decisions/DECISIONS.md` Q4 (added in `81105e36`, 2026-10-16 10:05): pass 0.14 +- 0.03 (0.11-0.17), warn 0.09-0.11 and 0.17-0.19,
  fail below 0.09 or above 0.19. The sheet says its 0.12-0.17 is "the spec's provisional ... made symmetric". Spec 12.1 took it in `64ef8bf9` (2026-10-16 11:22).
- `route_map_graph/proc_vs_custom/metrics/rules_check.md` was last regenerated in `ded90765` (2026-10-16 12:12, after the ruling) but from the unchanged `RULES` table, so the file
  carries the pre-ruling band and no warn state. It is a stale-rule artefact, not a newer decision.

This matches the build session's O-3 ruling: `--mode reference` reproduces `rules_check.md` (0.12-0.17, no warn) for acceptance 2; `--mode spec` is the product.

---

# Two build-session calls

- **(a) numpy and Pillow allowed in `tools/netrun_art`:** agree. Guards: keep `io` / canonical dump, seeds and the data-hash paths free of numpy (use plain floats so 12.3.1 and the
  Python-vs-GDScript parity hold), pin numpy 2.x, and keep Pillow behind `checks` and the look-dev overlay.
- **(b) NA-03 writes the HQ slot generator and the derive v2 nested schemas, art-pass reviewing both:** agree on the generator (no concept source, the build session owns the algorithm; art-pass
  reviews the look later); for the schemas, art-pass must review the **schema document before NA-03 codes against it** (poses, lod/section, dress lists are read by the Blender scene,
  the checks and the Godot runtime; the dress lists in particular are not designed yet), then freeze as v2.

---

# Spec edits (to `route_map_graph/PIPELINE_SPEC.md`; not applied)

1. **Lines 338, 1393, 1615:** `CAC/zoning.py:353-390` and `:353-375` -> `CAC/zoning.py:381-402` (rail polyline), `:616-660` (corridor clearing), `:684-697` (rail-side cap).
2. **Lines 343, 346:** `CAC/city_preset.py:149` -> `:162-163`. At `6a58733c` `RAIL.ramp` is 60.0 (and `end_ramp` 45.0), not "ramp 30": verify which the designer intends and correct the line or the value.
3. **Section 7.2:** add a "Unit" column. `stub` keeps 3.8 BU with the note "ruling C1, not `6.4 * k_units` (1.52)"; `CLUTTER` 25 kit -> 5.94 BU; `front fade` 6.0 -> **1.425 BU**; `edge band` 0.4 -> **0.095 BU**; add rows
   `section_params` pads 7.125 BU (overview) / 5.70 BU (rooms) and `zref_margin` 0.356 BU, each marked "kit units x 0.2375" with the `k_fit` caveat from O-K. Rename `margin` 0.10 to `cone_margin` to
   avoid the clash with `section_params(margin=1.5)`.
4. **Section 12.4.2 and 12.4.1:** state the corridor distance as `rail.side_d` = 7.2 BU (1.2 lots) and the half-width as `rail.half_clear` = 4.5 BU; add the `rail` object (O-C) to the `zoned.json` description at 2.2.
5. **Section 2.2 `layout.rules` row (and the 2.0c `net.json` description):** define a border link as in O-D.
6. **Section 5.1:** name the parameters `zoom_dive` / `zoom_detail`, state that `lod.weights` takes a distance (BU), and add the `zoom_dive = 1 + zoom_detail * ln(d_ov/d_dec)/ln(d0/d_ov)` relation (O-G).
7. **Section 12.0:** add the `capture.json` keys of O-1 (`kind, view, look, look_blend, corp, exempt{}`), the id.png `G` = room index and `B` = layer on class 5 and room-column cut surfaces, and class 3 = link structure (O-6).
8. **Section 12.1 / 12.7:** add a note that `proc_vs_custom/metrics/rules_check.md` and `run_proc_vs_custom.py:50` carry the superseded 0.12-0.17 band; spec values win. Add the `checks.composition` schema of O-10 as the config contract and the O-4 behaviour ("n/a" status, fail for an HQ overview or decision frame without a landmark).
9. **Section 12.7:** add the default skyline range and facade band of O-7.
