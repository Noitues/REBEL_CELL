# Netrun art pipeline: tools spec

Status: draft for the build session, 2026-10-15. Art only. This file says what to build; the sources it cites are
the reference implementations and the approved look values.

## 0. How to read this spec

**Path abbreviations** (all relative to `docs/concepts/`):

| Short | Path | What it is |
|---|---|---|
| `SB/` | `route_map_graph/storyboard/scripts/` | The one-city proof: look preset, derivation, dive, reveal |
| `M44/` | `route_map_graph/storyboard/scripts/m44/` | The mainline city kit and the one-city Blender build |
| `V3D/` | `route_map_graph/side_view/v3_dynamic/scripts/` | The camera rig (street side view) |
| `R3/` | `route_map_graph/side_view/v3_aaa/r3/` | The AAA-2 r3 look (notes, value targets) |
| `HK/` | `route_map_graph/hq_meridian/scripts/hq_kit/` | The HQ kit. Byte-identical copies sit in `hq_halcyon`, `hq_orbital`, `hq_solace`, `hq_rebel_cell` (checked by md5). |
| `HM/` | `route_map_graph/hq_meridian/scripts/` | The generalised HQ scene, jobs, compose, GPU lock |
| `HQ_<corp>/` | `route_map_graph/hq_<corp>/` | Per-corp NOTES and scripts |
| `CAC/` | `city_all_corps/scripts/` | The all-corps city: zoning, district building types, drowned quarter, freight rail |
| `DR` | `DIRECTION_REVIEW.md` | Decision log; the newest entries are at the end (lines 1358-1411) |
| `MAIN/` | `D:\Godot\rebel_cell\` (main branch) | The mainline Godot project, read-only for the tools. Its `scripts/city3d/` is not on this worktree's `main` ref. **AD ruling 2026-10-15:** every `MAIN/` path means the `D:\Godot\rebel_cell` main-branch file; the build session owns these files and makes any change to them. |

**Citations** are `file:line`. Where a value differs between sources, this spec picks one, says which, and lists
the conflict in section 15.

**Units.** One-city units (the only units the pipeline uses from now on):

| Unit | Value | Source |
|---|---|---|
| BU per lot (`U`) | 6.0 | `M44/layout36.py:24`, `CAC/city_preset.py:19` |
| Game height px to BU (`KH`) | `U / 41.64 * 1.15` (0.1657) | `SB/sb_onecity.py:71`, `M44/onecity_scene.py:39` |
| One floor (`floor_bu`) | 1.9 BU (the mainline window pitch) | `SB/sb_onecity.py:36` |
| One window column | 1.6 BU | `CAC/city_preset.py:22`, `M44/onecity_scene.py:155` |
| Lot to world | `x = (lot_x - CX) * U`, `y = -(lot_y - CY) * U`, `CX = CY = 6.0` | `M44/layout36.py:25-41` |
| Axes (tools) | Blender: x east, y north, z up | `HK/layout.py:6` |

**AD ruling 2026-10-15 (C1 / C7): ONE unit system: 1 floor = 1.9 BU, 1 lot = 6 BU.** The r3 street set and the HQ
kits were built at "1 storey = 8 BU" (`SB/look_preset.py:3`, `HM/hq_preset.py:4`). Every r3-derived density and length
is converted with `unit_scale` 3.0 (`M44/onecity_cycles.py:18`). The HQ kits are **rescaled** to one-city units: a
kit storey of 8 BU becomes one floor of 1.9 BU (a factor of 0.2375 on every kit length; section 8.6). How large a
compound is against its map lot is still open (Q1).

---

## 1. Scope and non-goals

**In scope.**
1. Tools that dress every netrun from ONE continuous city: every street netrun and every corp HQ netrun (Halcyon,
   Meridian, Orbital, Solace, Rebel Cell; Aurelian and Tethys next).
2. The look (AAA-2 for the netrun, mainline toon/ink for the HQ page) and the blend between them on shared geometry.
3. The camera rig, LOD by zoom, the section cut, the HQ occlusion rule, the entry sequence.
4. The Blender reference build and renders (look-dev, golden images, acceptance checks).
5. The export to Godot and the Godot runtime mapping (shaders, instancing, uniforms).
6. Automatic acceptance checks.

**Non-goals.**
1. **No game rules.** Routes, nodes, node kinds, layers, Heat and mechanics come from the game. The tools only place
   and dress them (DR 1402: "no game design in art-pass").
   **Hard rule (AD ruling 2026-10-15, C15): topology always comes from the game graph (GDD 4.2), mapped onto slots.**
   The HQ kit's `Compound` chains and the per-corp `seq` / `rooms` / `kinds` / `walk_*` lists (Halcyon's 21-room helix,
   Meridian's ring, Orbital's circuits, Solace's ladder, Rebel Cell's three lanes) are MOCK route data for concept
   renders only. In the pipeline a landmark exposes **slots** (section 8.4); the tools never generate nodes, edges,
   node kinds or shortcuts.
2. **Never redesign finished mainline art.** The mainline city, its HQ page and its post (`MAIN/scripts/city3d/`,
   `MAIN/shaders/city/city_post.gdshader`) are inputs. The only approved mainline changes are the three layout rules in
   section 3.2 (DR 1385-1388).
3. No new mechanics, no new content beyond what the game provides, no rule wording.
4. No views nothing uses (DR 1397: the district street renders were unnecessary).

---

## 2. Data flow

### 2.1 Overview

```
 GAME (MAIN, read-only)                     TOOLS (Python; Blender for the reference build)           GODOT (runtime)
 ---------------------------------          -------------------------------------------------         -------------------------
 CityLayoutRecorder  ─┐                     netrun_art.layout   import + layout rules  ─► city.json
   (lots, extrusions, │  city_layout.json ─►  (apply_layout_rules)                         │
    streets, plazas,  │                                                                    ▼
    HQ lots)          │                     netrun_art.zoning   districts, coast, rail ─► zoned.json
 City network ────────┘  net.json        ─►                                                 │
   (Sites, links,                                                                          ▼
    border links)                           netrun_art.derive   street netrun derivation ─► derive_<run>.json ──► NetrunArtDeriver
 Run graph (per run)  ── run_graph.json  ─►   (or hq.slots for an HQ netrun)                │                  (GDScript port,
   (nodes, layers,                                                                          ▼                   same JSON)
    kinds, edges,                           netrun_art.rig      poses, zoom, LOD weights ─► poses_<run>.json ──► NetrunCameraRig
    walked state)                           netrun_art.occlusion  per-frame cut / ghost ───────────────────────► OcclusionHelper
                                            netrun_art.blender.*  scene build, materials,                      (per-instance
                                                                  lights, media, render ─► EXR passes           INSTANCE_CUSTOM)
                                            netrun_art.post / overlay / compose ──────────► PNG / MP4 (look-dev,
                                                                                             golden images)
                                            netrun_art.export   kits + landmarks ─────────► .glb + .tres ────────► CityView3D
                                            netrun_art.checks   acceptance (section 12) ──► checks_<run>.json
```

Rule: the derivation, rig and occlusion modules are **pure Python with no Blender import** (as `SB/sb_onecity.py`,
`HK/*.py` are today). They have a GDScript twin in Godot that must produce identical JSON for the same inputs
(parity test, section 12.6). Blender code never decides a placement; it only builds what the pure modules output.

### 2.2 Modules and files

**AD ruling 2026-10-15 (C21): ONE package, `tools/netrun_art/`, with per-corp landmark plugins
(`tools/netrun_art/corps/<corp>/`).** Copies of shared modules (the five `hq_kit/` copies, the per-corp `hq_scene`,
`hq_jobs`, `hq_compose`, `gpu_lock` and kit copies) are forbidden: a corp contributes only its plugin (preset, slots,
`landmark.build`, mechanic visuals) and imports everything else.

| Module | Inputs | Outputs | Reference source |
|---|---|---|---|
| `layout.import_city` | `city_layout.json` from `MAIN/scripts/city3d/city_layout_recorder.gd` (extrusions: base polygon in lots, z0, h px, taper, ink, terr, key; street lots: lane colour, traffic; plazas; HQ rects) | `city_base.json` in BU | `M44/layout36.py` (`unified.json`) |
| `layout.import_net` | the network: nodes (id, lot, state owned/core/...), links (a, b, state, pts in lots) | `net.json` | `M44/layout36.py:242` `load_net`, `M44/scope39.py` |
| `layout.rules` | `city_base.json`, `net.json`, `LAYOUT_RULES` | `city.json` (frontage raised, border streets widened) | `SB/sb_onecity.py:80-140` `apply_layout_rules` |
| `zoning` | `city.json`, `city_preset.ZONING`, `WATER`, `BAY`, `RAIL`, `LANDMARK_FP` | `zoned.json`: district per building, HQ lots, landmark clearances, coast, drowned quarter, arterials, aqueduct, the freight-rail polyline + `deck_z` (the one source for the line; 3.4 L4) | `CAC/zoning.py` (rules Z1-Z6, L1-L4, T1) |
| `derive.street` | `city.json`, `net.json`, the selected Site, `run_graph.json`, `RULES` | `derive_<run>.json` (schema 2.3) | `SB/sb_onecity.py:143-409` |
| `hq.slots` + `corps/<corp>/layout.py` | `zoned.json` (HQ lot), `run_graph.json`, the corp preset | `derive_<run>.json` (same schema, `kind: "hq"`) | `HK/layout.py`, `HQ_<corp>/scripts/hq_graph.py` |
| `look.preset` | none | the AAA-2 preset, the mainline preset, `lod_bands` | `SB/look_preset.py`, `SB/sb_ocjobs.py:36-44`, `CAC/city_preset.py:95-117` |
| `rig` | `derive_<run>.json`, rig config | poses (OVERVIEW, DECISION, HOVER), the dive path, `zoom` | `V3D/cam_rig.py`, `SB/sb_ocjobs.py:70-115`, `HK/orbit.py`, `HM/hq_cam.py` |
| `lod` | `zoom`, `lod_bands` | band weights | `HK/lod.py`, `SB/look_preset.py:74-91` |
| `occlusion` | camera position, target points, building list | per building `(cut_height, opacity)` | `HK/downtown.py:319-394` |
| `section` | street corridor, `zoom` | `z_cut`, plinth weight | `SB/sb_ocjobs.py:111-115`, `M44/onecity_build.py:148-263` |
| `dress` | `derive_<run>.json`, `zoned.json`, preset | signage, beams, lamps, washes, fog fields, streak lanes, glows as placement lists | `M44/onecity_build.py:98-126`, `M44/onecity_cycles.py:169-371, 612-648` |
| `hq.downtown`, `hq.city_ring` | HQ cfg | building boxes + dressing (fallback only, section 8.2) | `HK/downtown.py`, `HK/city_ring.py` |
| `corps.<corp>.landmark` (plugin) | corp preset, slots, `zoned.json` (e.g. Meridian's rail polyline) | landmark meshes, landmark light rig, movers | `HQ_<corp>/scripts/hq_build.py` |
| `blender.scene` | everything above | `.blend` (optional), EXR passes | `M44/onecity_scene.py`, `M44/onecity_cycles.py`, `HM/hq_scene.py` |
| `post`, `overlay`, `compose` | EXR passes, overlay state | plates, finished stills and frames | `SB/sb_ocfull.py`, `HM/hq_compose.py`, `SB/wax_r2.py`, `SB/sb_reveal.py` |
| `export` | kits, landmarks, presets | `.glb`, `.tres` | new |
| `checks` | plates, passes, scene JSON | `checks_<run>.json` | `HM/hq_values.py`, `HQ_halcyon/scripts/hq_landmark.py`, `V3D/check_occlusion.py` |
| `gpu_lock` | none | the shared queue lock | `HM/gpu_lock.py` |

### 2.3 The derivation output (`derive_<run>.json`)

The contract between the tools and Godot. Fields as written today by `SB/sb_ocjobs.py:47-57`, plus three new fields.

| Field | Type | Meaning |
|---|---|---|
| `kind` | `"street"` or `"hq"` | New |
| `street` | `{a: [x, y], c: [x, y]}` BU | The chosen leg, extended (`extend`) |
| `nrm` | `[x, y]` | The street face normal (camera looks along it) |
| `start_left` | bool | The start sits on the screen's left |
| `span` | 1 or 2 | Floors per room (global choice; a building may fall back to 1) |
| `columns` | `[[layer, building key]]` | Route column per layer |
| `route_keys` | `[key]` | Every building part of every route column |
| `col_info` | `[{layer, key, top, u0, u1, face}]` | Column extents |
| `rooms` | `{node id: {front[4], back[4], floor, span, bld, parts, layer, kind}}` | Room boxes (world BU) |
| `edges` | `[{a, b, type, path[]}]` | Link polylines on the facade plane |
| `overview`, `decision` | pose dicts | Solved poses (section 6) |
| `frontage` | `[[key, h, floors, taper]]` | The street's frontage, for checks |
| `seed_key` | int | New: the art seed key (section 3.5) |
| `art_seeds` | `{stream name: int}` | New: one seed per art stream, derived on the game side from an `RngService`-derived seed and exported here, so Blender never invents a seed (proposal, Q9) |
| `version` | string | New: the rules version (bump on any rule change) |

---

## 3. One-city derivation rules

### 3.1 Buildings as the game reads them

1. A street-level base (`z0 <= 0.05`) plus every stacked part whose footprint centre lies inside it (`z0 > 0.05`) is
   ONE building. Its height is the top of its highest part (`SB/sb_onecity.py:143-161`).
2. Building ids are the game's extrusion `key`. Ties anywhere break by key, then node id (CLAUDE.md rule 7). Never by
   dict order.

### 3.2 Mainline layout rules (designer-approved 2026-10-15; DR 1385-1388; `SB/sb_onecity.py:69-70`)

These change the city both looks are built from (the HQ map and the netrun street). Mainline counterparts belong in
`MAIN/content/config/city_config.tres` and the city layout builder; that port is a mainline task, not an art tool.

| Key | Default | Rule |
|---|---|---|
| `frontage_min_floors` | 6 | Every street-level building fronting a border-link street rises to at least `(6 + abs(key) % 3) * floor_bu + 0.1` BU (11.5, 13.4 or 15.3 BU), so the front is not a flat wall (`SB/sb_onecity.py:134-138`). A building's height counts its stacked parts. Only the street-front row changes. |
| `border_street_width` | 8.0 BU | Border-link streets widen from the 6 BU base tile: each frontage street face steps back `(8 - 6) / 2 = 1` BU. Ground tiles are unchanged. |
| `base_street_width` | 6.0 BU | The base street tile |
| `hero_sign_rule` | `{blade: true, band: true, palette: (district_a, district_b)}` | Section 9.1 |

**Scope of "border-link street":** every straight leg of every link with `state == "border"` in the network,
extended along its own street line by `max(extend)` = 60 BU each way (`SB/sb_onecity.py:102-110`). Frontage test:
near edge within `front_band` (0.8, 6.5) BU of the leg centre line and overlapping the extended leg.

See also (AD 2026-10-15): the frontage height rhythm and crowns in 13.1 `frontage.silhouette`; hero signs per route column in `dressing.signs` (9.1).

### 3.3 Street netrun derivation (`SB/sb_onecity.py`, `RULES` at line 36)

| Key | Default | Meaning |
|---|---|---|
| `front_band` | (0.8, 6.5) BU | Near-edge distance band from the leg centre line |
| `min_width` | 2.5 BU | Minimum frontage width along the leg |
| `extend` | (12.0, 60.0) BU | A leg may extend 12 BU before its start and 60 BU past its end along its own street line |
| `floor_bu` | 1.9 BU | One floor |
| `base_floor` | 0 | The first room floor |
| `max_setback` | 0.6 BU | On a tapered building, a floor counts only while the facade setback at the room top stays within this |
| `room_inset` | 0.45 BU | Room inset from the building's corners |
| `room_depth` | 2.6 BU | Room depth behind the street face |
| `room_px_target` | 46 px at 1080p | One floor below this at OVERVIEW makes rooms double-height |
| `ov_pitch` | 2.0 deg | OVERVIEW pitch (near level) |
| `ov_base_frac` | 0.815 | OVERVIEW: the frontage base sits at this share of the frame height |

Rules, in order:
1. **The link.** The netrun follows the selected Site's border link polyline, ordered from the relay end
   (`SB/sb_onecity.py:164-168`).
2. **Frontage** per leg and side (`frontage`, lines 178-204): street-level buildings, width >= `min_width`, near edge in
   `front_band`, overlapping the extended leg; ordered by distance along the leg, then key.
3. **Assignment** (`assign`, 211-223): layer L takes the next frontage building (in link order) with at least
   `base_floor + rooms(L) * span` usable floors; shorter buildings are skipped. Fail if the frontage runs out.
4. **Choose the street** (`choose_street`, 226-250): maximise, in order, (layers assigned, total usable floors,
   start-on-the-left). Ties then by leg index, then side (+1 before -1).
5. **Floors** (`floors`, 44-57): `int(h / floor_bu)`; on a tapered building (`ts < 0.99`) only while
   `(1 - ts) * depth / 2 * z / h <= max_setback`.
6. **Span** (`derive`, 380-388): render the OVERVIEW with span 1; if one floor of the start room projects under
   `room_px_target`, use span 2. A building without the floors for span 2 keeps span 1. Never rescale a building.
7. **Rooms** (`room_boxes`, 253-278): rooms of a layer take consecutive floors from `base_floor`, bottom up in slot
   order (`K`). Box: inset `room_inset` from the corners, `room_depth` deep, z from `floor * 1.9 + 0.12` to
   `(floor + span) * 1.9 - 0.12`.
8. **Walls** (`M44/onecity_build.py:28-80`): cut every facade face of a route building whose centre lies inside an
   opening (pad 0.12 BU, depth -0.45..0.25 BU); build one wall object per room from the kit's own facade rule
   (`fgrid` cells 1.7 BU, windows in the building colour, 35 % lit). Walls are closed until the REVEAL.
9. **Room interiors** (`M44/onecity_build.py:81-96`): floor, ceiling, back and sides tinted from the node-kind colour
   (`ROOM_TL`, line 15), a lit back panel (width `min(w - 0.6, 3.2)` BU), a dark frame (0.16 BU), one area light per room.
10. **Links** (`link_paths`, 281-310): Manhattan paths on a plane 0.5 BU in front of the street faces: out of room a
    0.3 BU, across at the mid point, into room b. This is where the grease pencil draws.
11. **Section** (section 5.3).

`ROOM_TL` (node kind to room light colour, linear RGB; `M44/onecity_build.py:15-16`):

| Kind | Colour |
|---|---|
| router | (0.36, 0.88, 1.0) |
| elite | (1.0, 0.38, 0.16) |
| terminal | (0.24, 1.0, 0.55) |
| modem | (0.35, 0.59, 1.0) |
| rack | (1.0, 0.77, 0.24) |
| target | (1.0, 0.17, 0.24) |
| start | (0.83, 1.0, 0.0) |

### 3.4 District building types per corp (`CAC/city_preset.py:29-55`, generators in `CAC/city_build.py:282-541`)

Zoning (`CAC/zoning.py`, rules Z1-Z6, L1-L4, T1; numbers `CAC/city_preset.py:58-69`):
1. Z1: the five game territories keep their buildings.
2. Z2-Z3: unclaimed buildings split into `k_neutral` 3 k-means clusters (farthest-point init from the lowest key). The
   coastal cluster (mean depth within `coast_band` 40 lots) becomes TETHYS; the one nearest the centre AURELIAN; the
   rest THE SPRAWL.
3. Z4-Z6: the coast is the deepest building + 0.8 lot from the map camera (yaw 135); the seawall bows into a bay
   (`BAY` depth 16, width 60, headlands from 120 with k 0.004); the seaward `lagoon_frac` 0.68 of Tethys is the
   **drowned quarter** (ground subsides 2.5 -> 30 BU, water at z 2.5, levee 4.2, seawall 8.0; `WATER`, lines 72-92).
4. L1-L2: HQ lots are the layout's; a new corp's HQ lot is its district's pole of inaccessibility (ties: lower lot x,
   then y). Every landmark clears `landmark_r` 5.6 lots. Rebel Cell has no landmark: its base lot is refilled.
5. L3: the Aurelian aqueduct runs the district's best street line, +- `aqueduct_ext` 8 lots.
6. **L4: the Meridian freight rail. AD ruling 2026-10-15 (C8): ONE line, and this derivation is its source of truth.**
   - Path: from the fortress gate (`RAIL.gate_dx` -34, `gate_dy` -16.6 BU) a BFS over free street tiles (never a
     building, never inside the landmark footprint) to the nearest coast cell; collinear points dropped
     (`CAC/zoning.py:353-390`). The gate is on the fortress's north side (the rail-yard side; AD ruling C24).
   - **Deck height: `deck_z` = 17.5 BU.** It clears the tallest street front the layout rules can make (6 floors +
     the 0-2 key floors: `8 * 1.9 + 0.1` = 15.3 BU) plus 2.2 BU, so it clears a 6-floor frontage (11.5 BU) plus 2 BU
     anywhere along the line. It replaces `RAIL.deck_z` 9.0 (`CAC/city_preset.py:149`) and the HQ kit's 22
     (kit units; `HM/hq_preset.py:51`).
   - Buildings within `corridor_low` of the line stay at least 2 BU under the deck (cap 15.5 BU).
   - Piers every 7 BU on street tiles, ramp 30, signals every 36 (`CAC/city_preset.py:149`).
   - The HQ scene imports this polyline and `deck_z` from `zoned.json`. The straight viaduct at x 66 to y 1180 in the
     Meridian kit (`HM/hq_preset.py:51-52`) is a placeholder to be replaced.
7. T1: arterials are street runs of >= 36 tiles with mean traffic >= 0.55.

| District | `lang` | Hue | Facade albedo family | Lit share | Signature by rule |
|---|---|---|---|---|---|
| Meridian | `freight` | (1.0, 0.549, 0.102) | rust-brown | 0.34 | stacked containers on roofs (2-6, 0.95 BU courses), sodium roof lamps |
| Solace | `capsule` | (0.239, 1.0, 0.545) | pale green-grey | 0.40 | capsule bays, rounded crowns |
| Halcyon | `civic` | (0.549, 0.482, 1.0) | violet-grey | 0.36 | civic setbacks, cornices |
| Orbital | `spire` | (0.498, 0.659, 1.0) | blue-grey | 0.38 | masts with red beacons (h > 18), dishes, ice crown trim |
| Rebel Cell | `tenement` | (0.91, 0.078, 0.118) | brick-red | 0.40 | Tokyo canyon: stacked blade signs, box signs, shop fronts, holo panels; heights x0.7 (`REBEL_H`) |
| Aurelian | `roman` | (0.161, 0.859, 0.651) | travertine | 0.36 | colonnades, statues, campanili |
| Tethys | `hull` | (0.184, 0.42, 1.0) | wet hull | 0.34 | hull plating, porthole windows |
| Sprawl | `sprawl` | (0.75, 0.72, 0.82) | grey | 0.30 | holo panels on tall roofs |

Crown-trim probability per `lang`: freight 0.16, capsule 0.20, civic 0.20, spire 0.25, tenement 0.14, roman 0.15,
hull 0.22, sprawl 0.20 (`CAC/city_build.py:517-518`). Outline dimming off arterials and district borders:
`OUTLINE` (`CAC/city_preset.py:147`), because a full trim grid reads as the rejected wireframe look.

Side-street views use this same one-city build plus each corp's building language (DR 1399).

See also (AD 2026-10-15): facade kits >= 4 per district in 13.1 `materials.mix`; the repetition guard in `repetition.guard`; the city horizon in `horizon.break`.

### 3.5 Seeds and named RNG streams

Today every tool seeds `random.Random(<literal>)`. The pipeline replaces literals with **named art streams**:

1. `art_seed(stream, *keys) = hash64([layout_seed, "art/" + stream, *keys])`, using a fixed, documented hash
   (e.g. FNV-1a 64 over the UTF-8 of the JSON array). Same algorithm in Python and GDScript.
2. `layout_seed` is the seed the game used to build the city (the CityLayoutRecorder's seed). Art streams never read
   or advance the game's `RngService` streams (`map`, `combat`, `rewards`, `events`, `raids`; `docs/TECH_SPEC.md:57-62`),
   so dressing can never change a game outcome. Adding an `art` stream family to `RngService` is a TECH_SPEC change:
   log it in `docs/DECISIONS.md` (open question Q9).
   **Proposal (AD ruling 2026-10-15, C23; still Q9):** the game derives the art seeds from an `RngService`-derived seed
   and exports them into `derive_<run>.json` (`art_seeds`, section 2.3). The tools and Blender read seeds only from
   there; they never invent one. The legacy literals below are for golden-image parity in look-dev only.
3. Per-object streams are keyed by content ids, never by draw order: a building's stream is `(stream, key)`, a room's
   `(stream, node id)`, a tile's `(stream, i, j)`. Adding or removing one object then never changes another.
4. Floating point: placement code rounds world positions to 1e-4 BU before hashing or comparing.

Stream table (current literal in brackets; keep the literal as the stream's `legacy` value for golden-image parity):

| Stream | Use | Legacy seed (source) |
|---|---|---|
| `building` | city building detail per key | `key * 7 + 13` (`M44/onecity_scene.py:120`, `CAC/city_build.py:286`) |
| `scene` | one-city scene misc | 3636 (`M44/onecity_scene.py:34`) |
| `lanes_tile` | lane strokes per street tile | `i * 7919 + j` (`M44/onecity_scene.py:276`) |
| `cars` | parked street cars (mainline look only) | 1936 (`M44/onecity_scene.py:287`) |
| `sky` | sky lanes | 2626 (`M44/onecity_scene.py:312`) |
| `room_wall` | room wall windows per room | `abs(bld) * 31 + len(id)` (`M44/onecity_build.py:59`) |
| `hero_sign` | blade sign panels per column | `9970 + k` (`M44/onecity_build.py:110`) |
| `ground_glow` | street-level glows in the plinth field | 7719 (`M44/onecity_cycles.py:188`) |
| `street_lanes` | moving streak lanes | 9402 (`M44/onecity_cycles.py:618`, `R3/NOTES.md:388`) |
| `beams` | beam lean and sweep | 9500 (`HK/city_ring.py:180`); street beams use a key hash (`M44/onecity_cycles.py:358-360`) |
| `plumes` | steam plumes | 9510 |
| `glows` | bank and wisp glows | 9520 |
| `windows_flicker` | idle-loop window switches | 9601 |
| `flicker` | flicker tables | 9700 |
| `glitch` | billboard glitch slices | 9800 / 9900 |
| `city_fill` | AAA fill city (legacy street set) | 9950 (`SB/NOTES.md:214`) |
| `zoning` .. `post` | all-corps city | 7701-7708 (`CAC/city_preset.py:24`) |
| `downtown` | HQ downtown fallback: towers, dressing, traffic | cfg seed, +1, +2 (`HK/downtown.py:27`); per corp 4340 / 5340 / 6340 / 7340 |
| `ring` | HQ ring city fallback | per corp (Meridian 5311, `HM/hq_preset.py:107`) |
| `landmark.<corp>` | landmark detail | Meridian 5320-5330 (`HQ_meridian/scripts/hq_build.py:20`) |
| `cycles` | Cycles sampling seed | 0 (one-city), 7 (HQ) (`M44/onecity_cycles.py:573`, `HM/hq_scene.py:1118`) |

### 3.6 Determinism rules

1. Same `city.json`, `net.json`, `run_graph.json`, preset and `layout_seed` give a byte-identical `derive_<run>.json`
   and identical placement lists.
2. No placement reads the clock, the file system order, a set's iteration order or a dict's insertion order.
3. Sorting keys are explicit tuples ending in an id (`SB/sb_onecity.py:203`: `(along, key)`; `HK/layout.py`: path
   order).
4. Moving things (lanes, beams, flicker) are functions of time `t` and their stream; they loop on `T` = 4.0 s at 24 fps
   (96 frames; `SB/look_preset.py:69`).

---

## 4. Look presets

### 4.1 AAA-2 (the netrun look)

Base preset `SB/look_preset.py` (the r3 street set, 8 BU storeys). The one-city build reads its own `LOOK` block
(`SB/sb_ocjobs.py:36-44`, "calibrated on the one-city tests") over the defaults in `M44/onecity_cycles.py`.
**AD ruling 2026-10-15 (C3): `sb_ocjobs.LOOK` is the source of truth**; the NOTES table (`SB/NOTES.md:480`) and the
tool defaults lag it. LOOK will be refreshed from the storyboard v3 revision (beams and fog), which renders tonight;
the rows to refresh carry `TODO(refresh after sb v3 rev)`.

**Palette** (`SB/look_preset.py:11-18`; alternative palettes `PALETTES` lines 99-103):

See also (AD 2026-10-15): the per-district hue spread and the hue-cluster cap in 13.1 `palette.districts`.

| Key | neon_bay (default) | sodium_teal |
|---|---|---|
| `district_a` | (1.0, 0.16, 0.6) magenta | (1.0, 0.42, 0.08) |
| `district_b` | (0.16, 0.8, 1.0) cyan | (0.1, 0.95, 0.75) |
| `accent_warm` | (1.0, 0.58, 0.18) amber | (1.0, 0.2, 0.25) |
| `accent_cool` | (0.62, 0.38, 1.0) violet | (0.45, 0.55, 1.0) |
| `underlight` ramp | a 0.0, b 0.3, a 0.55, b 0.8, cool 1.0 | same names |

**Materials** (`M44/onecity_cycles.py:27-128`):

| Key | Default (one-city) | Source |
|---|---|---|
| surfaces | Principled, per-face colour x 0.85, roughness 0.55, specular 0.5 | `onecity_cycles.py:27-48` |
| wet ground | colour x 0.55; roughness from noise (scale 0.09 x `unit_scale`, detail 5) mapped 0.45..0.6 -> 0.3..0.03; specular 0.7 | `:63-92` |
| `neon` | 1.0 (`sb_ocjobs.py:36`; tool default 3.2) | `:99` |
| `win` | 0.9 (default 1.6) | `:100` |
| `panel` (room back panel) | 4.0 | `:101` |
| lit surfaces (`LITA`) | emission 0.42 | `:97` |
| `lane_dim` | 0.5 (street glow strips at half the neon level) | `:102` |
| world | (0.006, 0.006, 0.014) | `:134` |
| moon | sun 0.05 W, (0.55, 0.62, 1.0), rot (40, 0, 30) deg | `:156` |

**Lights by rule** (`M44/onecity_cycles.py:157-219`):

| Key | Default | Rule |
|---|---|---|
| `cityglow` | 900 W (default 2.5e3) | 6 x 3 area lights (45 x 30 BU) at z 2, along the street +- 120 BU, at street y + 40, + 120, - 60; magenta / cyan alternating; light-linked to the fog only, unshadowed |
| `room` | 60 W per BU of room width | One area light per room, room-kind colour |
| `lamp_step`, `lamp` | 6 BU, 80 W (default 25) | Point lamps along both kerbs at +- 2.6 BU, z 1.6; warm (1.0, 0.72, 0.42), every 3rd cool (0.55, 0.85, 1.0) |
| `wash` | 1500 W (default 120) | One spot per route column from 3.5 BU across the street, z 0.4, aimed at (nrm, 0.55), cone 70, blend 0.8; district a / b alternating |
| `ground_lamp`, `ground_glow_step`, `ground_glow_depth`, `ground_glow_p` | 20 W, 9 BU, 60 BU, 0.55 | Jittered glows among the plinths on the camera side, z 0.9, palette colours |

**Fog: one heterogeneous scatter volume** (`M44/onecity_cycles.py:373-541`). All heights in units of `H_FRONT`
(the median frontage roof across the street, within 18 BU of it) and `H_SKY` (the 90th-percentile roof 18-160 BU
behind, within 180 BU) (`:224-230`; fallbacks 14 BU and 2.2 x H_FRONT).

| Term | Default | Rule |
|---|---|---|
| `fog_peak` | 0.0507 per BU x `unit_scale` (tool default 0.021) | Peak density `TODO(refresh after sb v3 rev)` |
| body | `clumps * 0.08 + layers * clumps`, max with the wisp | `:449-450` |
| height falloff | `exp(-max(z - 0.5 H_FRONT, 0) / H_SKY)` | `:434` |
| strata | `0.5 + 0.5 sin(2 pi zw / (0.42 H_FRONT))`, `zw = z + warp + tilt`, warp +-0.22 H_FRONT (noise 0.006/0.010/0.02 x S), tilt 0.07 per BU along the street | `:431-435` |
| octaves | banks (0.004, 0.012, 0.075) x S, wisps (0.009, 0.02, 0.33) x S, mixed 0.62 / 0.38, remap 0.47..0.64 | `:436-439` |
| clumps | (0.0075, 0.014, 0.022) x S, remap 0.40..0.62 | `:440` |
| wisp layer | at 1.08 H_FRONT, half-thickness 0.12 H_FRONT, `wisp_k` 1.2 | `:441-442` `TODO(refresh after sb v3 rev)` |
| where | only behind the street face: smoothstep(`fog_front` 7, 17) BU | `:447` |
| floor | smoothstep(0.08 H_FRONT, 0.3 H_FRONT) | `:448` |
| ground bank | camera side beyond the kerb + 0.5..4 BU, thick to 0.2 `gb_top`, gone at `gb_top` 2.2 BU; `ground_bank` 0.04 x S | `:456-462` `TODO(refresh after sb v3 rev)` |
| mid banks | 0.05..0.8 H_FRONT, banks noise remap 0.42..0.62; `mid_bank` 0.035 x S | `:463-465` `TODO(refresh after sb v3 rev)` |
| back haze | `haze` 0.0008 x S above H_SKY, e-fold `haze_efold` 40 BU; anisotropy 0.2, colour (0.82, 0.78, 1.0) | `:468-474` `TODO(refresh after sb v3 rev)` |
| scatter | colour (0.85, 0.80, 1.0), anisotropy 0.45 | `:378-380` |
| underlight | ramp by `zw / 2.2 H_FRONT` in the palette, strength `density * underlight_k` 0.07 | `:478-490` `TODO(refresh after sb v3 rev)` |
| ground glow | ramp magenta..cyan by noise, strength `gb * ground_glow` 0.05 | `:491-502` `TODO(refresh after sb v3 rev)` |
| mid glow | cyan / violet / magenta by noise along the street, `mid_bank * mid_glow` 0.3 | `:503-518` `TODO(refresh after sb v3 rev)` |
| box | x, y -700..900; top `max(240 / S, 2.5 H_SKY)` | `:529-531` |
| render | `step_rate` 4.0, `max_steps` 128, volume bounces 0 | `:570-571` |

**Fog strata rule (r3 recipe, scaled):** layers about 0.42 H apart that bend, merge and split (warped, tilted height
coordinate); two octaves; clumps so no layer runs full width; one wisp just above the frontage roofs; thinning above
0.5 H; never in front of the street face, so the corridor and the rooms stay clear (`SB/NOTES.md:480`). On the r3
street set the same recipe ran on absolute numbers (`SB/look_preset.py:22-43`; `R3/NOTES.md:48-92`).

See also (AD 2026-10-15): depth planes, the empty-sky cap and beams-in-fog in 13.1 `atmosphere.layers`; the exposure
solve after the vignette in `values.solve`.

**Beams: soft volumetric cones, never solid rods** (`M44/onecity_cycles.py:232-371`):

| Key | Default | Rule |
|---|---|---|
| `beams` | 6 | Count |
| `beam_rise` | 1.35 | Candidate roofs clear 1.35 x H_FRONT |
| reach | 25 < d < 170 BU from the street midpoint, > 12 BU behind the street, not a route column | `:236-243` |
| spacing | >= 45 BU; pick by height desc, then key | `:244-250` |
| colours | a, b, warm, b, a, cool (by pick order) | `:253` |
| lean | x: `0.12 + 0.30 h1`, y: `0.18 + 0.12 h2`, `h1 = (key * 2654435761) % 1000 / 1000`, `h2 = (key * 40503) % 1000 / 1000`; away from the street midpoint | `:358-361` |
| haze spot | one SPOT per beam, `beam` 6.0e5 W, `beam_cone` 30 deg, **blend 1.0**, no shadow, light-linked to the fog only | `:366-368` `TODO(refresh after sb v3 rev)` |
| shaft | emissive cone mesh, length `beam_len` 3.5 x H_FRONT, half-angle `beam_half` 6 deg, start radius 0.18 BU, 48 segments; camera-visible only | `:332-352, 369-370` `TODO(refresh after sb v3 rev)` |
| shaft radial profile | `s^2 = 1 - (1 - facing)^2`; core gaussian sigma `beam_core_s` 0.13 (weight `beam_core_w` 1.0), skirt gaussian sigma `beam_soft_s` 0.42 times `(1 - s^2)` (weight `beam_soft_w` 0.5) | `:289-296` `TODO(refresh after sb v3 rev)` |
| shaft axial profile | `exp(-t / beam_efold 0.22)`, gone by `beam_fade` 0.6 of the length (smoothstep 0.27..0.6), 2.5 % fade-in | `:301-304` `TODO(refresh after sb v3 rev)` |
| breakup | world noise scale 0.09: `0.55 + 0.45 smoothstep(0.35, 0.65, n)` | `:305-313` |
| hot core | `beam_hot` 0.5 toward white | `:318-320` `TODO(refresh after sb v3 rev)` |
| emission | `beam_emit` 3.0; transparent + emission: adds light, never occludes | `:321-328` `TODO(refresh after sb v3 rev)` |
| sweep (idle loop) | yaw +-4.5..6 deg, pitch +-1/4 of it, own phase, period 96 frames | `SB/look_preset.py:59`, `R3/NOTES.md:208` |

Rules for the beam style (**AD ruling 2026-10-15, C4: soft volumetric cones only, no core spot, never rods; the r3
beam values `hero_soft`, `hero_core`, `hero_b_core`, `thin`, `haze_twin*` in `SB/look_preset.py:54-57` are
superseded**). The shaft's radial "core" term above is a soft gaussian inside the cone's own profile, not a light:
1. No core spot. No spot with cone < 10 deg is linked to the media (round 2b dropped the 0.9 deg core: "it read as a
   stage laser", `SB/NOTES.md:480`).
2. The visible shaft has no hard silhouette: the skirt term goes to 0 at the silhouette.
3. The shaft fades along its length; it never ends in a disc.
4. A beam shows where it crosses fog: the haze spot is linked to the fog only.
5. Beams sweep during holds (`SB/NOTES.md:82`).

**Light streaks for traffic** (DR 1362: no car geometry in the netrun look):

| Key | Default | Rule |
|---|---|---|
| street lanes | 4 lanes at fractions (0.28, +1), (0.62, +1), (-0.3, -1), (-0.64, -1) of the half street width (`street_width` 8 / 2) | `M44/onecity_cycles.py:620-622`; head lights white / warm one way, tails red the other |
| streak length, gap | 3..16 BU, 4..22 BU, colour gain 0.5..1.3 | `:627-637` |
| `lane_period`, `lane_k` | 80 BU per 4 s loop, emission 2.5 (`sb_ocjobs`; tool default 5.0) | `:615-616, 642-647` |
| streak profile (HQ) | 4 segments, brightness `0.15 + 0.85 f^1.6` toward the head, width 0.14 BU, z 0.5..0.65 | `HK/downtown.py:239-267` |
| sky lanes (r3) | 3 lanes at `z_frac` (0.62, 0.68, 0.85) of the skyline median, len 6..16, gap 60..160, slope 0.05..0.12, periods 360 / 400 / 440 | `SB/look_preset.py:65-67` |

**Post and grade** (`SB/look_preset.py:93`, `SB/sb_ocfull.py:37`):

| Key | Default | Note |
|---|---|---|
| `exposure` | 0.83 on the one-city street (`OC_EXPOSURE`), r3 2.4 | The dive lerps from 2.0 to the street value by `look_w` (`SB/sb_ocfull.py:150-151`) |
| `vol_k`, `vol_soft`, `vol_glow`, `vol_glow_thr` | 1.3, 0.25, 0.8, 0.02 | r3 post |
| `rain_vol` | 1.6 | Rain drop brightness gains 1.6 x the local in-scatter |
| HQ exposure by zoom | `exposure * (1 - exposure_zoom_k * zoom_detail)`; Halcyon 3.4 / 0.61, others 2.4 / 0.40 | `HQ_halcyon/scripts/halcyon_preset.py:107`, `HM/hq_preset.py:127` |
| HQ black point | 0.03 (Halcyon), 0.04 (others); Halcyon knee top 0.86 | same |

**The value band and how it is checked** (`SB/look_preset.py:94`, `HM/hq_values.py`):
- Luma = Rec.709 `0.2126 R + 0.7152 G + 0.0722 B` on the final 8-bit sRGB PNG plate (no UI), values / 255.
- Targets: median about **0.14**; **25-40 %** of pixels under 0.10; at most **2.5 %** over 0.85.
- Section 12.1 gives the pass rule, the tolerance and the exempt frames.

### 4.2 Mainline preset (toon / ink; the HQ page and the top of the dive)

Values from the mainline project (`SB/NOTES.md:89-103`; `CAC/city_preset.py:111-117`). Godot owns these
(`MAIN/scripts/city3d/city_config.gd`, `MAIN/shaders/city/city_post.gdshader`, `MAIN/content/config/ui_scrim_look.tres`);
the tools only mirror them for look-dev.

| Key | Value |
|---|---|
| Camera | orthographic, yaw 135, pitch 40, lot 6 BU |
| Toon ramp (night) | (0.09, 0.08, 0.21), (0.20, 0.17, 0.36), (0.36, 0.30, 0.54) |
| Ink | (0.05, 0.04, 0.09) |
| Fog | (0.20, 0.17, 0.33) at 0.22 |
| Haze | (0.08, 0.06, 0.16) at 0.34 |
| Bloom / spill | 0.75 / 0.5 |
| Grime | 0.15 |
| Rain | (0.75, 0.82, 1.0), alpha 0.11 |
| Grade | (0.94, 0.92, 1.04) |
| UI scrim | x 0.86 inside the network rect, x 0.68 outside (saturation 0.85); the selected Site in a lit vignette |
| Network decal | claimed links CELL_TURF #D4FF00, thin, with a soft NET_CYAN halo |
| HQ framing | claimed + launchable Sites' iso box + 40 BU margin, into the page's free rect (230, 90, 1460, 800) x 0.65, anchor (0.45, 0.42), ortho clamp (220, 640), capped at 460 BU (`SB/sb_mainline.py:22-25`) |
| Look-dev calibration grade (Blender only) | saturation x 0.64, gain (0.76, 0.76, 0.84); NOT used in Godot (one renderer) |

### 4.3 One camera, two looks, shared geometry

1. The geometry is identical in both looks. Only materials, lights and media change (`SB/NOTES.md:395-406`).
2. `look_blend = smoothstep((zoom_dive - 0.20) / (0.55 - 0.20))` (`SB/sb_ocjobs.py:105-108`;
   `SB/look_preset.py:87`).
3. In Godot one `look_blend` uniform drives (`SB/NOTES.md:136-141, 489`):
   - the WorldEnvironment lerp (fog, glow, tonemap) from the mainline values to the AAA-2 values;
   - the city materials: toon ramp -> PBR mix, ink outline fade;
   - the mainline post fog patches -> the FogVolume density;
   - the wet street: SSR / roughness (the `puddles_sharp_at` band too);
   - lights spawned by rule (kerb lamps, washes, beams) fade in with `visibility_range` and `look_blend`.
4. The v3 one-city proof uses no cloud veil (one world). The v2 veil (max 62 % opaque, `SB/NOTES.md:135`) is not part
   of the pipeline.

---

## 5. LOD bands by zoom

### 5.1 The zoom parameters

Two sources use the same band numbers on different domains (conflict C5). The pipeline defines both explicitly:

| Parameter | Domain | Formula | Used by |
|---|---|---|---|
| `zoom_dive` | 0 = the HQ page camera, 1 = the netrun OVERVIEW | `log(d0 / d) / log(d0 / d1)` with d the camera distance to the OVERVIEW target (`SB/sb_ocjobs.py:94-102`) | look blend, section, fog density, city glow, the dive LOD bands |
| `zoom_detail` | 0 = the netrun OVERVIEW, 1 = DECISION | `log(d_ov / d) / log(d_ov / d_dec)` (`HK/lod.py:33-34`) | HQ exposure by zoom, the HQ detail bands |

**Pipeline rule (proposed): in Godot, LOD is by absolute camera distance in BU.** Godot's `visibility_range` is
distance-based anyway, and it makes the street and HQ consistent. The band edges below are the dive bands converted
with the storyboard's anchors: d0 = 3833 BU (the 460 BU HQ frame emulated by a 300 mm lens: `460 * 300 / 36`), d1 =
114.6 BU (the street OVERVIEW, `SB/NOTES.md:479`); `d(z) = d0 * (d1 / d0)^z`. They are defaults to calibrate once in
Godot (open number N1).

### 5.2 Bands

| Band | `zoom_dive` (a, b) | Fade-in distance (BU, from -> to) | Content | Godot |
|---|---|---|---|---|
| big layer | always on | - | fog banks, every beam, building and window lights, street-light rivers, the route | - |
| `fog_octaves_by_zoom` | 0.25-0.60 | 1594 -> 466 | the fine fog octave, ragged edges | fog noise detail from a camera-distance uniform |
| `wisps_on_at` | 0.45-0.70 | 790 -> 328 | the thin wisp strata | uniform |
| `plumes_on_at` | 0.50-0.72 | 663 -> 307 | rooftop steam plumes | `GPUParticles3D.amount_ratio` |
| `signage_on_at` | 0.60-0.82 | 466 -> 216 | text signs, holo ads, billboards, blade signs, shop fronts | `visibility_range` + fade; MultiMesh instance alpha |
| `small_lights_on_at` | 0.75-0.92 | 276 -> 152 | small lights, beacons, stall lights, rain highlights | `visibility_range`; HQ floor 0.25 (`HK/lod.py:25`) |
| `puddles_sharp_at` | 0.85-1.00 | 194 -> 115 | puddle reflections sharpen | SSR / roughness uniform |
| `fog_density_by_zoom` | level 0.35 at 0, ramp 0.30-0.90 | 1336 -> 163 | fog density multiplier | FogVolume density |
| `cityglow_by_zoom` | level 0.45 at 0, ramp 0.30-0.90 | 1336 -> 163 | city glow multiplier | glow light energy |
| `look_blend_by_zoom` | 0.20-0.55 | 1898 -> 556 | mainline -> AAA-2 | `look_blend` |
| `section_by_zoom` | (60, 0.4, 0.25, 0.85) | 1594 -> 194 | the section cut (5.3) | section uniform |

Sources: `SB/look_preset.py:74-91`, `HK/lod.py:16-25`, `SB/NOTES.md:176-195`. Every band is a smoothstep on its
interval; HQ bands keep a floor (`FLOORS`: signage 0.0, small lights 0.25).

### 5.3 The section cut by zoom (street netrun)

1. **Corridor:** the camera side of the street centre line (side test `(p - a) . nrm < -0.4`), along the street from
   min(a, c) - `corridor_pad` to max(a, c) + `corridor_pad`, `corridor_pad` 30 BU (`M44/onecity_build.py:157, 191-199`).
2. **Cut height:** `z_cut(zoom_dive) = exp(lerp(ln 60, ln 0.4, smoothstep((zoom_dive - 0.25) / 0.60)))`, and no cut
   (1e4) while the smoothstep is 0 (`SB/sb_ocjobs.py:111-115`). Inside the corridor, everything above `z_cut` is not
   drawn.
3. **Plinth rule:** what is left of the cut blocks beyond the camera-side kerb (`plinth_off` = border street width / 2
   + 0.2 = 4.2 BU) and below `z_cut` goes near-black and wet: albedo 0.012 (blue x 1.2), the puddle roughness (noise
   scale 0.27, 0.42..0.6 -> 0.32..0.03), specular 0.7, no trims, no emission, no top-edge line (`edge_k` 0). It switches
   on as `z_cut` falls from 5.0 to 1.5 BU (smoothstep), so the HQ and the upper dive are untouched
   (`M44/onecity_build.py:159, 200-249`).
4. Same geometry; a clip in the materials. In Godot a world-space clip-box uniform (`corridor`, `z_cut`) in the city
   building and neon shaders (`SB/NOTES.md:488`).

### 5.4 What is generated or shown per zoom state

| State | Geometry | Atmosphere | Dressing | Section / occlusion |
|---|---|---|---|---|
| HQ page (`zoom_dive` 0) | the whole city, mainline look | mainline post fog patches, haze | mainline motion (sky cars, aviation lights, packets, fog patches, rain) | none |
| dive (0..1) | same | fog density and glow ramp; look blend 0.20-0.55 | bands fade in | section lowers 0.25-0.85 |
| street OVERVIEW (1) | + route rooms, walls (closed, then dissolving) | full AAA-2 | everything; idle loop | plinths |
| street DECISION | same | same | same | plinths; foreground occluders dither-fade (section 7.4) |
| HQ OVERVIEW (`zoom_detail` 0) | the HQ, its city | big layer; HQ detail bands at their floor | landmark rig, movers | occlusion cone over every route node |
| HQ DECISION (`zoom_detail` 1) | same | full | full | occlusion cone over the active room + its options |

---

## 6. Camera rig

### 6.1 Pose model (`V3D/cam_rig.py:1-14, 80-112`)

1. A pose is `(F, yaw, pitch, dist, lens, sx, sy)`. The camera sits at `F - dist * dir`,
   `dir = (sin yaw cos pitch, cos yaw cos pitch, -sin pitch)`. No roll.
2. Projection: 36 mm sensor, horizontal fit, 1920 x 1080 reference. Lens shift in units of frame width. In Godot:
   `Camera3D.PROJECTION_FRUSTUM` with `frustum_offset` (`V3D/../NOTES.md:47`).
3. Usable area (px at 1080p): x 300-1900, y 138-1012 (right of the sidebar, under the top strip, above the legend).
   Every framing is centred in it (`V3D/cam_rig.py:26`).
4. Framing solver: bisection on `dist` (60 iterations, geometric mean of [5, 3000]) until the point set fills `fw` of
   the usable width or `fh` of its height, whichever binds; then the shift centres the set (plus a bias)
   (`V3D/cam_rig.py:122-143`). HQ adds `dmin` and an optional fixed `centre` (`HK/orbit.py:124-144`).
5. Moves interpolate F, yaw, pitch, lens and shift linearly and dist in log space, eased by smoothstep
   (`V3D/cam_rig.py:108-112`).

### 6.2 Street rig parameters

| Key | Default | Source |
|---|---|---|
| `YAW_MAX` | 24 deg; `yaw(u) = 24 (1 - 2u)`, `u = layer / (TARGET layer - 1)` | `V3D/cam_rig.py:30, 146-147` |
| `PITCH_D`, `LENS_D` | 9 deg, 30 mm | `:31-32` |
| `FILL_W`, `FILL_H` | 0.66, 0.70 | `:33` |
| `LOOK_BIAS` | 0.10; bias = -0.10 yaw / 24 | `:34` |
| `HOVER_PULL`, `HOVER_YAW`, `HOVER_DOLLY` | 0.22, 3 deg, 0.96 | `:35` |
| `OV_YAW_K`, `PITCH_O`, `LENS_O`, `FILL_OW`, `FILL_OH` | 0.3, 6 deg, 40 mm, 0.95, 0.90 | `:36` |
| `T_STEP`, `T_HOVER_IN`, `T_HOVER_OUT` | 0.9 s, 0.30 s (ease-out cubic), 0.35 s (smoothstep) | `:37` |
| `T_ZOOM` (Z toggle) | 0.70 s today; **proposed 1.0 s**, the same as the entry zoom (designer question Q10; AD ruling 2026-10-15, C11) | `:37` |
| entry zoom (OVERVIEW -> DECISION after MARK) | 1.0 s + 0.5 s settle | `SB/sb_cams.py:106`; DR answer (`SB/NOTES.md:83`) |
| hover no-blink delay | 120 ms | `V3D/../NOTES.md:83` |
| token lead | 1.12 x the camera's progress | `:90` |

**One-city overrides** (`SB/sb_onecity.py:357-378`):
1. The camera looks along the street face normal. `yaw0 = atan2(nrm)`.
2. The yaw bias sign follows where the start lands: `sgn = +1` if the start is on the screen's left, else -1 (the rig
   mirrors: camera right looking left).
3. OVERVIEW: yaw `yaw0 - sgn * 7.2`, pitch `ov_pitch` 2.0, lens 40, fill 0.95 / 0.90, framed on every room's 8 corners;
   then shifted so the lowest room front sits at `ov_base_frac` 0.815 of the frame height.
4. DECISION: yaw `yaw0 - sgn * 24`, pitch 9, lens 30, fill 0.66 / 0.70, bias `sgn * 0.10`, on the current room + options.

**Parallax:** the DECISION focus F is the centre of the decision set, so the camera pans along the street as the
operative advances; yaw follows `yaw(u)`; the step is a 0.9 s smoothstep between the two DECISION poses
(`V3D/../NOTES.md:51-92`). Depth layers (mid row, far city, sky lanes) give the parallax.

**Zoom states:** DECISION is the default. OVERVIEW is on the Z key, the `DECISION | OVERVIEW` toggle or the scroll wheel
(DR 1359). In OVERVIEW, CONFIRM, the number keys and hover still work; hover does not move the camera there.

### 6.3 The dive path (`SB/sb_ocjobs.py:70-91`)

1. Start: the mainline HQ pose (orthographic, yaw 135, pitch 40, frame width 460 BU), emulated by `HQ_LENS` 300 mm.
2. End: the street OVERVIEW pose.
3. `s = smootherstep(u)`; target, yaw (shortest way) and shift lerp by `s`; frame width and lens interpolate in log
   space by `s`; pitch lags: `sp = smootherstep(min(1, 1.08 u)^1.6)`.
4. Duration `DIVE_S` 3.0 s in the animatic; 2.4 s proposed in game (section 10).

### 6.4 HQ orbit camera (front and centre)

| Key | Default | Source |
|---|---|---|
| DECISION azimuth | mean of the look vectors (minus the outward normal) of the **distinct** room normals holding the current room + options; one face: straight at it; a corner choice: on the corner | `HK/orbit.py:167-173`, `HM/hq_cam.py:166-179` |
| front and centre | after framing, shift the lens so the current room's centre sits in the middle of the usable frame (`centre_current` true) | `HM/hq_cam.py:194-215` |
| pitch beat | `lerp(pitch_lo, pitch_hi, layer / top layer)` | `HM/hq_cam.py:182-185` |
| `dmin` | 135 BU kit default (Orbital 110, Solace 120, Rebel 120) | `HK/orbit.py:29`, corp presets |
| `look_ahead` | 0 | `HK/orbit.py:29` |
| hover | 22 %, 3 deg (sign by the room's side in camera right), x 0.96 | `HK/orbit.py:185-193` |
| OVERVIEW (kit) | pitch 26, lens 40, fill 0.95 / 0.90; azimuth on the corner whose two faces hold the most live route rooms (walked, current, options, ahead), tie to the current face | `HK/orbit.py:195-230` |
| OVERVIEW (per corp) | fixed `ov_yaw`, `pitch_o`, `lens_o`, `ov_centre` from the preset | `HM/hq_cam.py:230-231` |
| face visibility | a room is drawn when `dot(face normal, to camera) > vis_margin` 0.12; far rooms ghost as faint state rings in OVERVIEW / legend hover; far links as wax at 45 % | `HK/orbit.py:236-241`, `HQ_halcyon/NOTES.md:117` |
| step | 0.9 s; a corner stair 1.6 s with a 45 deg swing | `HQ_halcyon/NOTES.md:115` |

Per-corp camera values (`hq_preset.py` `cam`):

| Corp | pitch_lo-hi | lens | dmin | fill | OVERVIEW pitch / lens / yaw |
|---|---|---|---|---|---|
| Halcyon | 13-24 | 30 | 135 | 0.66 / 0.70 | 26 / 40 / corner rule (fixed corner, DR 1391) |
| Meridian | 21-27 | 30 | 135 | 0.50 / 0.54 | 40 / 36 / 140 (`HM/hq_preset.py:125-126`) |
| Orbital | 16-26 | 30 | 110 | 0.56 / 0.62 | 46 / 36 / NNW (`HQ_orbital/scripts/hq_preset.py:77`) |
| Solace | 12-26 | 30 | 120 | 0.56 / 0.62 | 20 / 34 / 99 (`HQ_solace/scripts/hq_preset.py:76`) |
| Rebel Cell | 17-19 | 30 | 120 | 0.74 / 0.74 | 62 (`HQ_rebel_cell/scripts/hq_preset.py:82, 92`); DECISION is the side view at yaw 0 |

These distances are in HQ-kit units; in the pipeline they are multiplied by `k_units` 0.2375 (section 8.6).

**The HQ entrance beat** (once per HQ run): 6.0-6.5 s, a per-corp move ending on the OVERVIEW, route and UI drawn in
over the last 0.9-1.0 s (Halcyon: half-orbit from the plaza, 175 BU, pitch -9, 24 mm, smoothstep over 86 %;
`HQ_halcyon/NOTES.md:118`). The paths are hand-set today (a gap: section 13).

### 6.5 Camera beats as content

The HQ beats are content fields, not code (`V3D/../NOTES.md:220-243`): per layer `yaw` (curve or fixed), `pitch`,
`lens`, `look_bias`, `fill`, `entry_move` (`pan` / `crane` / `orbit` + duration). The solver, hover ease, overview and
occlusion rule are shared.

---

## 7. Occlusion rule (designer-approved 2026-10-15; DR 1411)

### 7.1 The rule

1. **Target volume:** the front points of the HQ's active room plus the visible route nodes. DECISION / HOVER: the
   current room + its options. OVERVIEW (`zoom_detail < 0.5`): every route node (`HM/hq_jobs.py:55-67`).
2. **Cone:** every ray from the camera to the target volume, widened by a **10 % margin** of the volume's span.
3. **Occluder:** a city building whose footprint meets the cone of the targets behind it and whose top reaches into
   the cone. Compound (landmark) geometry is never an occluder.
4. **FLATTEN:** an occluder is section-cut to a **1-2 floor lit stub** (shop fronts, awnings and the lowest windows
   stay lit). Its open top shows a near-black poche, so it reads as a cut model, not a hollow shell.
5. **GHOST:** if the stub still reaches into the cone, it fades to **15-20 % opacity** (default 18 %) with faint edges;
   its window dots stay, dimmed with it.
6. **Ease:** 0.35 s ease-in-out, one value for street and HQ (AD ruling 2026-10-15, C14; inside the designer's 0.3-0.5 s). **Never fully hidden.**
7. Buildings outside the cone keep their full height. Roof clutter is cut with its building.

### 7.2 Parameters (`HK/downtown.py:319-320`, `HK/section.py:30-35`)

| Key | Default | Meaning |
|---|---|---|
| `margin` | 0.10 | Cone widening, share of the target volume's span (lateral and vertical tangent) |
| `NK` | 5 | Depth knots, nearest to farthest target |
| `stub` | 3.8 BU = `2 * floor_bu` (one-city units; the kit's 6.4 was in kit units) | Stub height: 2 floors (the rule's 1-2 floor stub; AD ruling 2026-10-15, C1) |
| `ghost` | 0.18 | Ghost opacity |
| `edge` | 0.6 | Edge-line emission; edge band 0.4 BU; edge alpha boost 0.22 |
| `tsoft`, `vsoft` | 0.035, 0.025 | Soft cone borders (lateral, vertical tangent) |
| front fade | 6.0 BU | Soft fade past the farthest target |
| `CLUTTER` | 25 BU kit units (6 BU after `k_units`) | Roof clutter above a building's top (the uncut height is `top + CLUTTER`) |
| `POCHE` | (0.010, 0.010, 0.013) | Cut-top colour (back faces) |
| `EDGE_COL` | (0.55, 0.68, 0.85) | Ghost edge colour |
| ease time | 0.35 s ease-in-out (AD ruling 2026-10-15, C14) | Godot tween on the per-instance values, street and HQ |

A corp may override through `downtown.occ` in its preset (`HK/downtown.py:331`).

### 7.3 Algorithm (exact twin in Python, Blender and Godot)

`occlusion_params(cam, pts, cfg)` (`HK/downtown.py:323-357`):
1. Centroid `o` of the targets; `u` = the horizontal unit vector camera -> `o`.
2. Per target: `al = max((p - cam) . u, 1)`, lateral `t = ((p - cam) x u) / al`, vertical `v = (z - cam z) / al`.
3. Margins: `msp_t = margin * max(span(t), 0.02)`, `msp_v = margin * max(span(v), 0.02)`.
4. Knots `k = 0..NK-1` at depth `a0 + (a1 - a0) k / (NK - 1)`; each holds `[min t - msp_t, max t + msp_t]` and
   `min v - msp_v` over the targets at or behind that depth.

`occlusion_state(p, b)` for a building `b = (x, y, top, hx, hy)` (`HK/downtown.py:374-394`):
1. `r = max(hypot(hx, hy), 0.5)`; `al`, `la` as above; `alc = max(al, 1)`.
2. The cone at depth `al - r` (piecewise-linear knots).
3. `lat = sstep((la + r) / alc - tmin, tsoft) * sstep(tmax - (la - r) / alc, tsoft)`.
4. `front = (al > 0) * sstep(amax - (al - r), 6)`.
5. `blocks(z) = sstep((z - cam z) / max(al + r, 1) - vmin, vsoft)`.
6. `fc = lat * front * blocks(top)`; `stub = min(stub, top)`; cut height `zc = stub + (1 - fc) (top + CLUTTER - stub)`.
7. `g = fc * blocks(stub)`; opacity `1 - g (1 - ghost)`.
8. Returns `(min(zc, top), opacity)`.

Blender clip: `HK/section.py:44-171` (per-face attributes `bc` = (x, y, top), `bh` = (hx, hy, 0); dithered render
method; back faces show the poche when `fc > 0.5`).

### 7.4 Godot mapping

1. The city is MultiMeshes. Each instance carries `INSTANCE_CUSTOM = (cut_height, opacity, edge data)`.
2. Each frame a view-side `RefCounted` helper fed by the camera rig runs `occlusion_state` for the buildings in the
   near rings and writes per-instance **targets**. The view tweens current values toward targets over 0.35 s (ease
   in-out). Outside the deterministic core; it never changes game state.
3. Shader (opaque pipeline): `if (world_up > cut_height) discard;` where `world_up` is the **world Y** coordinate in
   Godot (Y-up). The source text writes `world_vertex.z` (Blender axes; conflict C9).
4. Back-face branch draws the poche colour.
5. Ghost: alpha-hash / screen-door discard against a 4 x 4 Bayer threshold scaled by `opacity`; no transparent pass.
   Edge lines from the box-local distance. Window emission x `opacity`.
6. Cost: one uniform block, one per-instance vec4, no extra draws.
7. **Street netruns** use the same helper for foreground occluders in DECISION (protected rooms = current + options;
   screen-box margin 12 px, 40 px on top for the sticker; `V3D/../NOTES.md:157-160`), with the same 0.35 s ease-in-out (the v3
   dynamic proposal was 0.15 s: conflict C14). The street section (5.3) handles the corridor; this rule handles what
   the section leaves.

---

## 8. HQ kit, generalised

### 8.1 Shared modules (one copy, in `tools/netrun_art/hq/`)

| Module | API | Owns | Source |
|---|---|---|---|
| `layout` | `Compound(cfg, watch)`; graph API (`NODES, KIND, ROW, LAYER, FACE ...`, `states`, `edges`, `edge_path`, `room_front/corners/center`) | slots on a stepped square landmark (`spiral` / `switchback` / `faces`), link types (ramp, gallery, corner_stair, stair, climb, core_lift); scan rule hook | `HK/layout.py` (DEFAULTS line 36) |
| `orbit` | `Orbit(C, cfg)`: `decision`, `hover`, `overview`, `zoom_of`, `visible_face` | section 6.4 | `HK/orbit.py` |
| `downtown` | `build(cfg, A, geo, pal)`; `occlusion_params`, `occlusion_state`; `in_corridor`, `corridor_low` | dense blocks to the walls (fallback, 8.2); the occlusion rule; corridors | `HK/downtown.py` |
| `section` | `insert(material)`, `set_frame(scene, params)` | the occlusion clip in Blender materials | `HK/section.py` |
| `city_ring` | `build`, `beams_by_azimuth`, `glows_by_azimuth`, `inward_face` | the 360 ring city (fallback, 8.2) | `HK/city_ring.py` |
| `lod` | `LOD_BANDS`, `FLOORS`, `zoom`, `band`, `weights` | section 5 | `HK/lod.py` |
| `states` | `STATE_COL`, `STATE_K`, `LOCKDOWN_K`, `ring_colour`, `scan_lines`, `eye_badge` | the room-state language | `HK/states.py` |
| `scene` | `hq_scene.py <job.json>`; hook contract 8.5 | materials, room kit, city, fog, plumes, glows, beams, state ladder, power cut, movers, passes | `HM/hq_scene.py` |
| `jobs` | `frame(...)`, shot lists, quality table, Blender launcher | per-frame state incl. the occlusion cone | `HM/hq_jobs.py` |
| `compose` | plates + overlay | the overlay solved per pixel from two renders (on black and on 50 % grey): `out = plate * m + b` | `HM/hq_compose.py:1-7` |
| `values` | `check(plate, stem, thumb)` | value band, landmark ratio, 320 px thumbnail | `HM/hq_values.py` |
| `gpu_lock` | `acquire`, `release`, `holder` | the shared GPU queue (one Cycles job at a time; batches <= ~45 min) | `HM/gpu_lock.py` |

Quality table (`HM/hq_jobs.py:30-38`):

| Quality | Resolution | spp | adaptive threshold | volume step rate |
|---|---|---|---|---|
| final | 2560 x 1440 | 64 | 0.015 | 1.2 |
| sheet | 1280 x 720 | 48 | 0.02 | 1.5 |
| video | 960 x 540 (upscaled) | 12 | 0.06 | 3.0 |
| test | 1280 x 720 | 32 | 0.04 | 2.0 |
| mini | 640 x 360 | 16 | 0.06 | 3.0 |
| eevee | 960 x 540 | 24 TAA | - | - |

Object pass indices (the landmark check reads them; `HM/hq_scene.py:464-481`): 0 sky, 1 compound, 2 city, 4 ground,
5 rooms, 6 movers, 7 streaks.

### 8.2 The city around an HQ

1. **Default (one continuous city):** the HQ sits on its map lot; the surrounding city is the map's own buildings
   from `zoned.json`, with each district's building language (3.4). Blocks come right up to the landmark footprint
   (`LANDMARK_FP`, `fp_margin` 0.25 lots; `CAC/city_preset.py:132-141`). No open perimeter (DR 1395, 1406).
2. **Fallback:** where the exported city does not reach (outside `RADIUS` 122 lots, `M44/layout36.py:26`), fill with
   `downtown.build` then `city_ring.build`. Downtown defaults (Meridian, `HM/hq_preset.py:120-123`): `street0` 8,
   `cell` 30, `street` 7, `h_near` (16, 44), `h_far` (34, 96), `tall_p` 0.08, `sign_p` 0.6, `holo_p` 0.07, `trim_p`
   0.4, `lamp_step` 15, `lamp_lights` 120, `lamp_w` 1800. Ring defaults: near 300-372, mid 400-540, far 620-980 BU;
   8 beam sectors on the mid ring; 8 billboards; sky lanes at (700, 150), (780, 182), (860, 226)
   (`HM/hq_preset.py:107-118`).
3. **AD ruling 2026-10-15 (C6): dense city to the walls wins** (the newer decision). The `perimeter` keys
   (`perimeter.r`, pylons, wall) are legacy and default to 0 (no belt, no pylons, no wall). Halcyon's cleared belt
   (`HQ_halcyon/NOTES.md:65`) is not built.
4. Cameras clear their view with the occlusion rule (section 7), never with a cleared belt or empty ground.

### 8.3 Landmark lighting rule

1. The landmark reads **1.5-2x the local background** in median luma: landmark = pass indices 1, 5, 6; local
   background = indices 0 and 2 inside the landmark's screen box grown 35 % (`HM/hq_values.py:15-38`).
2. It is done with **light, not exposure**: keys, rims (light-linked to the landmark), cornice coves, seam strips,
   logo panels, floods, uplights, fog lit from below round the compound (`HQ_meridian/NOTES.md` section 6).
3. The silhouette reads at 320 px wide (the thumbnail check).
4. Active-room keys: a key from the camera side + a rim from behind on the active room and its options, re-aimed every
   frame (Orbital `room_key_w`; `HQ_orbital/NOTES.md` section 2).

### 8.4 Mapping the game's graph onto a landmark

**Hard rule (AD ruling 2026-10-15, C15): topology always comes from the game graph (GDD 4.2), mapped onto slots.**
The kit's `Compound` chains (`HK/layout.py:36` `rows`, `path`, `shortcuts`, `kinds`) and the corp `seq` / `rooms` /
`kinds` / `walk_*` / `orbit.walks` lists (e.g. `HM/hq_preset.py:59-86`) are MOCK route data for concept renders only.
The pipeline keeps them only as test fixtures. Rule:
1. Each corp module exposes **slots**: ordered positions (frame, normal, size, tier / course / floor) on its landmark,
   plus allowed link geometries between slot classes.
2. The game's run graph (layers, nodes in slot order, edges) is assigned to slots in layer order, then node order,
   exactly as the street assignment walks frontage buildings (3.3 rule 3).
3. Link geometry follows the step class (same level / rising / falling), as the street's connection types do
   (`V3D/../NOTES.md:167-192`). The type is a hint and never names the node.
4. Mechanics (the eye, the yard cycle, retargets, the read rule, the sync strike) are driven by game state passed in
   per frame (`mt`, `room_state`, `affected`, `movers`; `HM/hq_scene.py:8-10`). The tools only visualise them.

### 8.5 Per-corp landmark modules (`corps/<corp>/landmark.py`)

Hook contract: `build(K) -> hooks` where `K` carries the accumulators, geometry helpers, materials, preset, graph,
log and the room kit; `hooks` may hold `accs`, `beams`, `mover_lights`, `no_cut`, `no_room_light`, `local_rec`,
`post_build` (`HM/hq_scene.py:745-790`; `HQ_meridian/scripts/hq_build.py:20-31`).

| Corp | Landmark (by rule) | Mechanic visual (driven by game state) | Key numbers (kit units) | Source |
|---|---|---|---|---|
| Halcyon | Square stepped pyramid: tiers of `tier_h` 13 on a 6 BU podium, rooms 14 x 8 x 10 in the faces; THE PANOPTICON vault open on four faces; the eye turret (drum r 12.5, amber rim, teal iris) | The eye: a gobo'd gaze spot (90 deg sector, linked to the compound only, 7 % fog twin), the blade scan line (constant elevation), the lighthouse beam (2.2 + 6 deg cones, -9 deg), lockdown red x 2.2 + scan-line plane | `HK/layout.py:36`; `halcyon_preset.py` | `HQ_halcyon/NOTES.md` sections 1-6 |
| Solace | Twin helix towers: two smooth swept tubes (r 9, 40 segments) at 40 BU from centre, theta(z) = 90 + 11 z / 12.5 deg, 19 floors x 12.5; rows of 12 oval portholes (half axes 2.1 x 3.3) with frame rings; leaf-green fresnel rim (`rim_k` 0.9, `rim_pow` 5); glazed bow-tie skybridges (13 BU at the tubes, 4 at the waist) only on route floors; the crown with THE GENOME CORE; a dark dressed plinth with a lit entry | The ladder: UP / ACROSS; UNREAD rooms frosted and dimmed | `HQ_solace/NOTES.md` sections 1, v2 r2 | |
| Orbital | Round launch podium (r 64, h 10), silo (r 17) with door leaves, the rocket (r 6, h 58, rises 62 BU), dish stations on a ring (r 96), a 4-leg truss antenna tower (104 BU, decks at 26 / 52 / 78) with two elite vaults, the red service gantry with LAUNCH CONTROL | Doors open / shut, rocket height, hacked bands lit lime, the override link | `HQ_orbital/NOTES.md` section 1 | |
| Meridian | Container fortress: walls at abs(x) 80, abs(y) 60, 3 courses of 9 BU + merlons; corner towers of 5 crossed courses; loop track and platforms; **the moat on the W, S and E sides only; the north side is the rail yard and the gate the freight line leaves by** (AD ruling 2026-10-15, C24); the slewing keep crane (z 86, jib 128); MANIFEST CONTROL; **the freight line** (AD ruling 2026-10-15, C8): a switch off the loop's north side, a portal in the platform wall, then the ONE line from `zoned.json` (the rail search, 3.4 L4) at `deck_z` 17.5 BU (city units) on piers, with signals and catenary masts; rail-side sheds stay 2 BU under the deck. The kit's straight viaduct at x 66 (deck z 22, piers 24, masts 36, corridor half-width 6.5 / 9.0) is a placeholder to be replaced | Shuttle containers wall <-> train every other turn, the crane slew, movers carrying rooms | `HM/hq_preset.py:40-89` | `HQ_meridian/NOTES.md`, v2 r2 |
| Rebel Cell | No tower. A Tokyo-alley district on the real block grid; option A: three stacked lanes in one section cut along a real street line (roofs, alley, service tunnel under the street); THE UNDERCROFT sunken service street; the **MAINFRAME v4 red sign** as the hero landmark (`mf_w` 11 BU, about 45 BU tall); the red fist hologram secondary (`fist_s` 20) | The window sequence `SEQ` (0 before .. 3 full) and `PULSE` | `HQ_rebel_cell/NOTES.md` sections 1-2, v2 r2 | |

### 8.6 Scale: the landmark in the one city

**AD ruling 2026-10-15 (C1 / C7): one unit system; the HQ kits are rescaled to it.**
1. Unit rescale (fixed): the kits were built at "1 storey = 8 BU"; in the pipeline one storey is one floor of 1.9 BU,
   so every kit length is multiplied by `k_units` = 1.9 / 8 = **0.2375** (rooms 14 x 8 x 10 become 3.3 x 1.9 x 2.4 BU;
   Halcyon's tier 13 becomes 3.1 BU; the Meridian walls at 80 / 60 become 19 / 14.25 BU). With it: light positions,
   the camera's `dmin` and distances, and the HQ fog field scale by `k_units`; light powers by `k_units^2`; densities
   by `1 / k_units`. Rooms keep readability through a pixel target (as the street's `room_px_target` 46 px).
2. **Still open (Q1):** the compound's footprint against its map lot. After the rescale, the Meridian keep (half-size
   136 BU in kit units, `HM/hq_preset.py:120`) is about 32 BU, close to the map footprint square 32 BU
   (`CAC/city_preset.py:134`), but other corps differ. Whether a landmark must fit `LANDMARK_FP` exactly (an extra
   per-corp fit factor) or the HQ lots grow is the designer's call.

### 8.7 Adding a new corp (Aurelian, Tethys)

1. Add the district to `city_preset.DISTRICTS` (hue, sec, mat, win, lit, `lang`) and a `lang` generator in the city
   building module. Aurelian `roman` and Tethys `hull` exist (`CAC/city_preset.py:45-50`).
2. Add `LANDMARK_FP` (Aurelian ellipse 36 x 30; Tethys circle 34, no refill: water) and the HQ lot rule (L1: pole of
   inaccessibility; Tethys over the drowned quarter).
3. Write `corps/<corp>/preset.py` (deep copy of the AAA-2 preset + `hq` block: palette, light, cam, post, fog
   variant) and `corps/<corp>/landmark.py` (slots + `build(K)`).
4. Run the checks (section 12) on OVERVIEW, DECISION and HOVER test frames before any final render.
5. Aurelian and Tethys HQs each need a design pass first (DR 1398); Tethys explores dams or water locks; its
   underwater look is clearer water with a deeper distance fade (`WATER.sigma` (0.090, 0.034, 0.016), `inscatter`
   (0.003, 0.018, 0.055), caustics, shafts; `CAC/city_preset.py:82-91`).

---

## 9. Dressing rules

### 9.1 Signage

1. **Hero signage on route columns** (`M44/onecity_build.py:98-126`): every route column carries
   - a blade sign at its street-face corner on the start side, 0.25 BU in, from z 2.2 to `max(4.5, top - 1.6)`, in
     `max(3, int(height / 1.4))` stacked panels (each 0.35..1.15 BU out from the face, 0.18 BU gaps), every third
     panel lightened (`0.6 c + 0.4`), on a 0.12 BU pole;
   - a lit band 0.32 BU tall at `top - 0.75`, inset 0.4 BU;
   - colours alternate district a / b along the street (the band takes the other colour, x 0.85).
2. City signage (all buildings): blade signs on 16 % of street faces over 5 BU, shop-front bands on 55 % of street
   faces, roof holo billboards on 16 % of roofs over 14 BU (`M44/onecity_scene.py:171-229`).
3. Signage sits in the `signage_on_at` band.
4. The r2 street-set dressing (text signs, ad planes, holo ads, megastructures, drum column, stalls) is hand-placed
   and is NOT ported; the rules above replace it (section 13).
5. See also (AD 2026-10-15): sign density, hero-sign placement and megastructures in 13.1 `dressing.signs`; street-level light (streak lanes, lamp chains, shopfronts) in `streets.light`; the road in the OVERVIEW foreground in `foreground.street`.

### 9.2 Grease-pencil links (`SB/wax_r2.py:1-29`)

| State | Colour | Width (px at 1080) | Dash | Alpha | Glow |
|---|---|---|---|---|---|
| walked | LIME (212, 255, 0) | 8.0 | solid | 1.0 | 95 |
| option | ORANGE (255, 140, 26) | 8.5 | solid | 1.0 | 110 |
| ahead | WHITE (242, 246, 255) | 5.2 | 14 on / 9 off | 1.0 | 0 |
| past | GREY (122, 118, 134) | 4.0 | solid | 0.38 | 0 |

Hand wobble 0.7 px per vertex; links stop `CLEAR_PAD` 5 px short of a sticker ring and never run under a sticker or a
number chip. The pencil never touches UI (ROUTE_REQUIREMENTS 14). The red pencil marks the TARGET (circle + word). In
Godot: `Line2D` with a reveal Tween (`SB/NOTES.md:162`).

### 9.3 Vinyl-sticker nodes

1. Each node type has its own room dressing plus a vinyl sticker; type reads by shape, not colour only
   (ROUTE_REQUIREMENTS 3). No corner badges.
2. Stickers sit at the room's left cut edge, 38 % down, with the number chip to its left (`V3D/../NOTES.md:272`).
3. Tags show only on hover; legend hover shows all (ROUTE_REQUIREMENTS 4).
4. Numbers only on the current options (keys 1-n).
5. Gloss: a rainbow diagonal sweep, one sticker at a time on a scheduler (DR 1349); `foil.gdshader` `gloss_pos`.

### 9.4 Hover power cut

1. Everything outside the hovered branch (and the current room) dims; the branch lights; the whole branch to the
   TARGET lights (ROUTE_REQUIREMENTS 2).
2. Street (v3 dynamic): outside to **32 %**, 40 % desaturated; branch rooms x (1 + 0.45 hover_k) with type-colour
   spill (`V3D/../NOTES.md:84-86`).
3. HQ: outside to **22 %** in 3D, branch x 1.45; 2D x 0.62 (`HM/hq_jobs.py:39`; `HQ_halcyon/NOTES.md:114`).
4. It runs on the hover ease curve (0.30 s in, 0.35 s out). The level is a designer question (Q6; AD ruling 2026-10-15, C10).

### 9.5 The plan pencil (HQ page)

On the click: an orange pencil circle round the Site, then the orange plan along the border link from the relay to
the Site (0.65 s). Orange is the plan colour (DR 1370). The netrun street is derived on that same link (3.3 rule 1).

### 9.6 Always-alive city (DR 1372)

Traffic streaks, beams, flicker, holos, fog drift and rain run in every beat and screen; only detail changes with zoom.

| Element | Motion (loop T = 4 s, 96 frames) | Source |
|---|---|---|
| street lanes | one lane period per loop | `R3/NOTES.md:205` |
| sky lanes | vehicles with a bright head and fading tail | `:206` |
| beams | sweep yaw +-4.5..6 deg | `:208` |
| fog | drift (wind 4 BU/s; Godot: `TIME * wind` in the noise UV) | `SB/look_preset.py:36`, `R3/NOTES.md:226` |
| rain | 3 layers, whole wraps per loop | `:210` |
| neon hum / flicker bursts / broken sign | per-sign `emission_multiplier` instance uniforms from seeded tables | `:211-213, 233` |
| windows | rare switch-offs (3 cells) | `:214` |
| nav strobes | 2-frame flash at 2.2x, else 0.12; 3 phase groups | `:215` |
| billboards / holo ads | content cycle with 2-frame glitch; scan band roll | `:216-217` |
| mainline (HQ page) | sky-lane cars with streaks, blinking aviation lights, packets on links, drifting fog patches, rain | `SB/NOTES.md:170`; `MAIN/scripts/city3d/city_motion_*.gd` |

---

## 10. Entry flow as a runtime sequence

Timeline from the animatic (`SB/sb_cams.py:85-104`); proposed in-game durations from `SB/NOTES.md:300` (open number
N2). **One press skips the whole entry** to the end state of beat 7 (DECISION, markers drawn, UI in).

| # | Beat | Animatic (s) | Proposed in game | What happens |
|---|---|---|---|---|
| 1 | HQ | 0.0-3.0 | idle | Mainline HQ page, city alive; tags hover-only |
| 2 | SELECT | 3.0-7.35 | player-driven | Hover: tag + holo Site file decrypts (0.55 s). Click: orange circle, then the orange plan along the border link (0.65 s); JACK IN pops, rainbow gloss (0.8 s), press (0.25 s squash) |
| 3a | JACK IN: terminal | 7.35-8.75 | 0.9 s | `jack --from <relay> --to <site>`, routing, handshake, CONNECTED; page dims 25 % |
| 3b | Binary rain | 8.75-10.0 | 0.7 s | On the chosen link only |
| 3c | CRT collapse | 10.0-10.45 | 0.3 s | Line, then dot; no wheel lens |
| 3d | Dive | 10.45-13.45 | 2.4 s | The dive path (6.3); look blend; section lowers; walls closed; no route light. Furniture fades in the first 0.3 s, the network decal over 0.6 s |
| 4 | REVEAL | 13.45-17.09 | (with 5: about 3 s behind "short jack-in") | Walls dissolve into bits left to right from the start room: first wall after 0.35 s; per layer L the links L-1 -> L write on (0.22 s), then layer L's walls dissolve (0.25 s, 0.06 s stagger); room light bleeds out; edge cells flash lime / cyan; bits (0.7 BU cells) lift off and fade in 0.55 s (`SB/sb_reveal.py:32`) |
| 5 | MARK | 17.09-18.09 + 0.8 s hold | | Stickers slap (scale 1.35 -> 1, 0.18 s, 25 ms stagger); rings / room frames (0.40 s from 0.15 s; lime current, orange options, white ahead); numbers pop (0.12 s at 0.45 s); token lands; red pencil TARGET circle + word last (0.40 s at 0.60 s); route UI with the markers (0.35 s) (`SB/sb_reveal.py:33-34`) |
| 6 | ZOOM | 18.89-19.89 + 0.5 s | 1.0 s | OVERVIEW -> DECISION (smoothstep, dist in log space); the toggle flips at the midpoint |
| 7 | CHOOSE | 20.39- | player-driven | Hover ease 0.30 s, power cut, tag + node file |

Rules:
1. Nothing on the route is visible until street level.
2. Jack-out is the same REVEAL in reverse (walls reassemble from bits).
3. Godot: a dissolve shader on the facade material (`dissolve` instance uniform, world-cell noise threshold,
   emissive edge), Tweened per room; one `GPUParticles3D` per wall for the bits; rings via an arc shader `progress`;
   the TARGET pencil by a wipe uniform (`SB/NOTES.md:159-163`).
4. The sequence is a view: it emits signals up (`entry_finished`, `entry_skipped`) and never changes game state.
5. The NIGHT_SKY hold stays for loads; the dive covers loads (ROUTE_REQUIREMENTS 11).
6. HQ netruns: the same beats 1-3, then the corp's entrance beat (6.4) in place of the street dive and REVEAL.

---

## 11. Blender to Godot mapping

### 11.1 Baked vs real time

| Element | Godot | Baked or real time |
|---|---|---|
| City buildings | Generated at runtime from the game's layout (the mainline already builds the city); the one-city rules (3.2) in the layout builder; MultiMesh per material family with `INSTANCE_CUSTOM` | real time, generated |
| Route columns | Rebuilt with openings at run start (per-building mesh variant); room interiors as `MeshInstance3D` scenes per node kind | real time, generated at run start |
| Landmarks | Built once by the tools, exported `.glb` per corp (modular parts: walls, courses, tubes, truss), placed on the HQ lot; movers as scenes | baked meshes, placed at runtime |
| Room kits | One scene per node kind (+ per-corp variants) | baked |
| Signage art | Texture atlases (blade panels, billboards, holo ads) | baked |
| City look | Materials with `look_blend`; toon ramp + ink (mainline) and PBR (AAA-2) in one shader | real time |
| Fog | Volumetric fog + FogVolume boxes with a `FogMaterial` shader (the recipe in 4.1: height falloff, warped-height strata from `NoiseTexture3D`, clumps, banks, wisp as 1-2 additive cards where froxels smear it) | real time |
| Beams | **AD ruling 2026-10-15 (C4): soft volumetric cones only, no core spot, never rods.** ONE SpotLight3D per beam: `spot_angle` 30 deg (the haze spot), `spot_angle_attenuation` fully soft, `light_volumetric_fog_energy` only, shadows off; plus an additive soft-cone shaft mesh with the radial / axial profile of 4.1. No second "hero" spot and no 1-4 deg core spot (the r3 mapping, `R3/NOTES.md:227`, is superseded). `TODO(refresh after sb v3 rev)` | real time |
| City glow, bank glows | Omni / Spot lights with volumetric energy only (cull mask: no facades) | real time |
| Kerb lamps, washes | Omni / Spot lights by the same rules, `visibility_range` fades | real time |
| Streaks | Unshaded additive scrolling-streak lane shader (`TIME * speed`); sky lanes head + tail | real time |
| Flicker, strobes, windows | `emission_multiplier` instance uniforms from seeded tables | real time |
| Rain, plumes, bits | GPUParticles3D, `amount_ratio` by band | real time |
| Puddles | SSR + reflection probe on the wet street | real time |
| Section, occlusion, wall dissolve | uniforms / instance uniforms in the city shaders | real time |
| Far city (fallback ring) | 2-4 impostor cards | baked |
| Overlay (pencil, stickers, rings, tags) | Control / `Line2D` / existing kit; `unproject_position` per frame for rooms and links | real time |

### 11.2 Materials and shaders (new or changed)

| Shader | Uniforms |
|---|---|
| `city_building` | `look_blend`; section `corridor` (a, c, nrm, pad), `z_cut`, plinth `on` range; per instance `cut_height`, `opacity`, edge data; `dissolve` (route walls) |
| `city_neon` / emissive | same clips; `emission_multiplier` |
| `city_fog` (FogMaterial) | `H_FRONT`, `H_SKY`, peak, octave weights by band, the street box, wind |
| `beam_shaft` | colour, core / skirt sigmas and weights, e-fold, fade, hot core, noise |
| `wet_street` | puddle noise, roughness range, `puddles_sharp` |
| `streak_lane` | speed, lane period, head / tail profile |

Godot is Y-up: every z in this spec is world Y in Godot.

### 11.3 Lighting

1. No shadows on rule lights except the few named in a corp rig (Meridian: 4 of ~20 floods).
2. Light linking does not exist in Godot: "fog only" lights use `light_energy` 0 with volumetric energy, or a cull
   mask; "landmark only" rims use a cull mask on the landmark layer.
3. Room lights only on rooms whose face sees the camera (about 8 of 21 at Halcyon).

### 11.4 Performance budgets (open numbers; N3)

| Item | Estimate in the sources | Budget |
|---|---|---|
| Frame | 60 fps target spec (`V3D/../NOTES.md:216`) | OPEN |
| Volumetric fog | 1.5-3 ms at 1080p, `volumetric_fog_length` ~400, 64-96 slices (`R3/NOTES.md:226`) | OPEN |
| Beams | 4-6 spot lights in the froxel pass | OPEN |
| City / bank glows | 8-14 lights, no shadows | OPEN |
| Room lights | ~8-10 visible | OPEN |
| Background draws | ~150 (impostors, MultiMesh traffic, ~40 additive quads) | OPEN |
| Ring city towers | ~2 k in 3 MultiMeshes | OPEN |
| Landmark tris | Halcyon ~25 k, Orbital ~30 k + 8 k truss, Solace ~20 k per tube | OPEN |
| Occlusion helper | per frame over near-ring buildings | OPEN |

### 11.5 File formats

| Data | Format | Notes |
|---|---|---|
| City and network import | JSON (`city_layout.json`, `net.json`) | from the mainline recorder |
| Derivation, poses, occlusion params | JSON (schema 2.3), UTF-8, sorted keys, floats rounded to 1e-4 | the Python <-> GDScript parity contract |
| Presets | Python dicts in the tools; exported to `.tres` Resources for Godot (read-only at runtime; CLAUDE.md rule 3) | new schema classes need a DECISIONS entry and the schema smoke test (rule 8) |
| Meshes | glTF 2.0 binary (`.glb`), Z-up -> Y-up by the exporter, per-vertex colour attribute `col`, building id attribute | |
| Textures | PNG (8-bit sRGB), EXR (linear, look-dev only) | |
| Render passes (tools) | multilayer EXR -> `.npy` (Combined, Emission, Denoising Albedo, Depth, Object Index, Volume Direct) | `HM/hq_scene.py:1154-1180` |
| Look-dev output | PNG plates and stills, H.264 MP4 through Blender's sequencer | |
| Check reports | JSON (`checks_<run>.json`) | |

---

## 12. Acceptance checks the tools run automatically

Every check writes pass / warn / fail with numbers to `checks_<run>.json`. A fail blocks a final render batch.

### 12.1 Value band

| Item | Default |
|---|---|
| Measure | Rec.709 luma of the final 8-bit sRGB plate without UI |
| Median | 0.14, pass 0.12-0.17 (R-VAL-1; provisional, derived from hand-built passes; AD 2026-10-15). Tolerance still Q4. |
| Under 0.10 | 25-40 % (R-VAL-2) |
| Over 0.85 | <= 2.5 % (R-VAL-3); the solve runs after the vignette (rule `values.solve`, 13.1) |
| Exempt (reported, not failed) | hover power-cut frames; mainline-look frames (held instead to the capture: median 0.214 +- 0.03, `SB/NOTES.md:120`); Rebel Cell red-sequence frames; beam-pass flash frames of an entrance beat; look-blend frames (0 < look_blend < 1) are reported only |

### 12.2 Landmark ratio

| Item | Default |
|---|---|
| Measure | median luma of pass indices {1, 5, 6} over median of {0, 2} inside the landmark's screen box grown 35 % (`HM/hq_values.py:18-38`) |
| Pass | 1.5 <= ratio <= 2.0 |
| Warn | ratio > 2.0 (Halcyon 2.9 was accepted as is, DR 1390) |
| Fail | ratio < 1.5 |
| Silhouette | 320 px thumbnail written for review (manual) |
| Shots | OVERVIEW and DECISION; hover frames exempt |

### 12.3 Determinism

1. **Data hash (exact):** run the pure modules twice (and in a fresh process with a different `PYTHONHASHSEED`);
   SHA-256 of `derive_<run>.json`, placement lists and occlusion params must match.
2. **Geometry hash (exact):** SHA-256 of the exported mesh buffers (positions rounded to 1e-4, attributes) for the
   same seed.
3. **Image hash:** a deterministic preview render (Eevee, or Cycles on CPU, fixed seed, no adaptive sampling,
   denoiser off) at 640 x 360 must hash-match across two runs. GPU Cycles with OIDN is not guaranteed bit-exact: for
   final GPU renders the check is a tolerance (mean absolute difference <= 1/255 on a 320 x 180 downsample, max
   <= 8/255). Conflict C22.
4. **Seed sensitivity:** changing `layout_seed` changes the dressing hash; changing only an unrelated building's key
   changes no other building's placement (per-key streams, 3.5 rule 3).

### 12.4 No intersections with rails or viaducts

1. No building footprint (inset 0) meets a corridor segment (`in_corridor`, `HK/downtown.py:397-410`); the zoning
   rail never crosses a building or the landmark footprint (`CAC/zoning.py:353-375`).
2. Within `corridor_low` distance the building tops stay at least 2 BU under the viaduct deck (`deck_z` 17.5 BU, so
   tops <= 15.5 BU; AD ruling 2026-10-15, C8).
3. Viaduct piers stand on street tiles only.
4. ONE line: the HQ scene's rail polyline and `deck_z` are byte-equal to `zoned.json`'s (C8).
5. Also checked: no link path (2.3 `edges`) passes through a non-route building's volume; no room opening is inside
   another building; no foreground dressing (stalls, lanterns, poles) stands in front of a room opening
   (`HQ_rebel_cell/NOTES.md` v2 r2).

### 12.5 Beam style

1. **Config:** no media-linked spot with cone < 10 deg; every media-linked spot has blend >= 0.8; no shadowed beam;
   every beam shaft uses the shaft material (4.1).
2. **Image:** on the beam-only pass, sample 5 profiles across each shaft at 20 / 35 / 50 / 65 / 80 % of its visible
   length. Fail if any profile has a step of more than 25 % of its peak between adjacent pixels at 1080p (a hard
   edge), or if the profile's 10-90 % rise width is under 3 px (a rod). Defaults to calibrate (N4).
3. **Count and spacing:** beams <= `beams` (6), spacing >= 45 BU, none on a route column.

### 12.6 Further checks

| Check | Rule | Source |
|---|---|---|
| Python / GDScript parity | Same inputs -> identical `derive_<run>.json` from both implementations | new |
| Room readability | every room's front projects >= 46 px tall at OVERVIEW 1080p (span rule), >= `room_px_target` | `SB/sb_onecity.py:36` |
| Available rooms unblocked | <= 8 % of an available room's opening blocked (opening shrunk 3 px), in DECISION / HOVER | `V3D/../NOTES.md:161-165` |
| Occlusion never hides | every building's opacity >= `ghost`; stub >= min(stub, top) | 7.1 |
| Frame continuity (sequences) | mean absolute frame-to-frame difference at 320 x 180 has no isolated spike (> 3x its neighbours) and no black frame (mean luma > 0.05) | `SB/NOTES.md:265-295` |
| Wax clear of stickers and UI | no pencil pixel inside a sticker ring + 5 px or a UI rect | `SB/wax_r2.py:8-9, 28` |
| 1280 x 720 readability | DECISION at 1280 x 720 renders every sticker >= 24 px and every option number legible (manual review frame produced automatically) | ROUTE_REQUIREMENTS 3, 13 |

### 12.7 Composition checks (AD 2026-10-15)

The procedural-vs-hand-built tests (13.1) run automatically on every OVERVIEW and DECISION plate (no UI, UI masked)
with the metric code of `proc_vs_custom/scripts/pvc_metrics.py` moved into `netrun_art.checks`. Thresholds live in
config `checks.composition` and are **provisional; derived from hand-built passes**.

| ID | Views | Threshold | Fail action |
|---|---|---|---|
| R-SIL-1 / R-SIL-2 | street | lit skyline std >= 0.15; >= 0.08 in every 1/4 window | fail (rule `frontage.silhouette`) |
| R-DET-1 / R-DET-2 | street | Sobel >= 0.028; >= 450 blobs / MP | fail (rule `dressing.signs`) |
| R-CALM-1 / R-CALM-2 | street, HQ | detail CV 0.45-0.85; calm tiles 12-32 % | fail (rules `density.falloff`, `atmosphere.layers`) |
| R-HUE-1 / R-HUE-2 | street, city | entropy >= 3.8 bits; top cluster <= 45 % | fail; corp HQ views exempt (rule `palette.districts`) |
| R-FOCUS-1 | any frame with a landmark | landmark / ring mean luma >= 1.5 | fail (rule `landmark.lead`); complements 12.2, which uses medians and pass indices |
| R-HOR-1 | city views | built-top std >= 0.015 in every 1/4 window | fail (rule `horizon.break`) |
| R-REP-1 | all | autocorrelation p90 <= 0.60 | fail (rule `repetition.guard`) |
| R-VAL-1/2/3 | AAA-2 | 12.1 | fail (rule `values.solve`) |

Exempt as in 12.1 (hover power cut, mainline frames, red sequence, flash frames). The landmark and crop boxes come
from the scene's object-index pass, not hand-placed boxes. The rules without a test yet (`streets.light`,
`foreground.street`, the depth planes of `atmosphere.layers`, `materials.mix`) report their proxy numbers until their
passes exist.

---

## 13. Procedural vs hand-built

**AD 2026-10-15.** Merged from `proc_vs_custom/COMPARISON.md` (the measured comparison of hand-built and procedural
frames: the street, the HQs v1 vs v2 on the same cameras, the city key art, and the mainline anchor).

- **Sheets:** `proc_vs_custom/sheet_p1_street.jpg`, `sheet_p2_hq.jpg`, `sheet_p3_city.jpg`, `sheet_p4_anchor.jpg`.
- **Numbers:** `proc_vs_custom/metrics/METRICS.md` (every metric, every image), `metrics/rules_check.md` (each test
  below, pass / fail per image), `metrics/all_metrics.json`.
- **Metric definitions:** `proc_vs_custom/scripts/pvc_metrics.py` (module docstring). Inputs, masks and landmark boxes:
  `scripts/pvc_config.json`.
- **Re-run (CPU, about 30 s), from the worktree root:**
  `python docs/concepts/route_map_graph/proc_vs_custom/scripts/run_proc_vs_custom.py`
  (`--only p2_hq,p3_city` for some pairs; `--no-sheets` skips drawing).

All metrics are on Rec.709 luma of the sRGB frame resampled to 1280 px wide. Every threshold below is a config value
and is **provisional; derived from hand-built passes** (the custom frames that pass, with headroom). Re-tune after the
round-1 finals.

### 13.1 Ranked gaps and the rules that close them (AD 2026-10-15)

Each rule is a config block in the look / layout preset. Units are one-city units (section 0).

| Rank | Gap (measured, procedural vs custom) | Rule (config block) | Parameters (defaults) | Tests |
|---|---|---|---|---|
| 1 | Street front low and flat: lit-skyline std 0.115 vs 0.229; flattest quarter 0.031 vs 0.140 | `frontage.silhouette` | `frontage_min_floors` 6 (approved, 3.2); `height_step_min` 2 floors between neighbours (seeded rhythm); `crown_share` >= 1/3 of columns topped by a crown (setback, spire, roof box or sign frame); `max_equal_tops` 2 adjacent tops within 1 floor | R-SIL-1, R-SIL-2 |
| 2 | Hero signage and dressing missing: Sobel 0.021 vs 0.032; 328 vs 550 bright blobs / MP; 0 vs about 10 readable signs | `dressing.signs` | per route column one hero sign (blade or wall) in the district pair's hue inside the column's footprint, lit 1.5-2.0x its local background; >= 1 hero sign inside the central 2/3 of the frame width; per frontage building a shopfront strip on the base and `p_secondary` 0.5 of a small secondary sign; `megastructures` >= 1 per street (arch board, globe or holo) on the tallest non-route roof off the decision box; `signs_on_screen_min` 6 legible text signs at OVERVIEW; every sign on a building face | R-DET-1, R-DET-2, sign-placement check |
| 3 | Even carpet, no rest areas (HQ v2): detail CV 0.29-0.36 vs 0.59-0.74; calm tiles 4-9 % vs 25-32 %. The street fails the other way (40 % calm) | `density.falloff` | `apron_bu` (kit 160-292 BU = 38-69 BU one-city) a quiet apron **of dimmed buildings, not empty ground** (see the note below); lit-window density from `near_k` 0.25 at the apron edge to 1.0 at `ramp_bu`; `dark_block_share` 0.2 of blocks fully dark, in seeded patches. Netrun views only (the mainline map and key art stay even) | R-CALM-1, R-CALM-2 |
| 4 | No street-level light in the city fabric (HQ v2, city) | `streets.light` | every camera-visible road segment: streak lanes (r3 `street_lanes`, fractions per road class); lamp chains every `lamp_step` BU; lit shopfront bases on `p_shopfront` 0.6 of street-level facades | to add: >= 25 % of the bright pixels on the road mask at HQ OVERVIEW (needs a road-ID pass; until then blobs / MP and streak counts) |
| 5 | Palette collapses to one hue: entropy 3.53 / 2.62 vs 4.47 / 4.57 bits; top cluster 55-68 % vs 22-27 % | `palette.districts` | `district_hue_min` 4 % of chromatic pixels per district in view, in its own hue (bank glows, trims, ground and roads); `hue_cluster_max` 45 % for the ambient fill. Exempt: HQ interiors and corp HQs (one corp hue allowed) | R-HUE-1, R-HUE-2 |
| 6 | Fog and depth planes not built on the one-city fill: empty sky, beams in clear air, no plumes or mid haze | `atmosphere.layers` | the r3 fog rules on the one-city heightfield (4.1), plus `sky_max_share` 0.25 empty sky above the lit skyline (else pull backdrop rows forward or raise the tilt); `beam_fog_min` density over >= 60 % of each beam's on-screen length; >= 3 depth planes (backdrop, mid, front) with `plane_step` >= 0.03 median luma between adjacent planes (Z pass) | R-CALM-2 upper bound; to add: depth-banded luma test |
| 7 | Street foreground is rooftops, not street: the bottom 20-25 % is the cut roof grid | `foreground.street` | `fg_band` 0.20 of the frame height at OVERVIEW shows the road: wet material, >= 2 streak lanes, kerb lamps; cut buildings there only as near-black edge silhouettes at the frame sides. Fix by camera target or lower street fill, never by painting | to add: lower-band hue entropy and blob count >= 80 % of the full-frame values |
| 8 | Landmarks don't lead: Halcyon in the city 1.41; Meridian HQ 1.09 / 1.25 | `landmark.lead` | each landmark in frame lit >= 1.5x its ring luma; covers >= `lm_area_k` 6x the median block's on-screen area; carries a rim or outline the fabric doesn't use; the hero landmark within 0.12 frame heights of a rule-of-thirds point (`lm_centre_thirds_dist`); the top-1 % light never in a cell without a landmark (beams don't out-shine it) | R-FOCUS-1 |
| 9 | Ruler-straight horizon (city): flattest-quarter std 0.008 | `horizon.break` | seeded coast inlets and headlands of amplitude `coast_amp`; >= 3 skyline spikes taller than 2x the median roof, >= 1/6 frame apart | R-HOR-1 |
| 10 | The v2 kit exposes too dark: 41-61 % under 0.10 | `values.solve` | the exposure solve targets median 0.14 and 30 % under 0.10 **after the vignette** (the city NOTES found it applied after the solve) | R-VAL-1/2/3 (12.1) |
| 11 | Same-material boxes (street, city night) | `materials.mix` | `material_kinds` >= 4 facade kits per district (glass curtain, concrete band, panel and grille, lit atrium); no two adjacent buildings share one; roof clutter from >= 3 kinds | to add: facade texture-class count or a material-ID pass histogram |
| 12 | Repetition guard (not a gap today: v2 p90 0.31-0.37 vs v1 0.58-0.77) | `repetition.guard` | `max_same_module_adjacent` 2 identical facade modules side by side | R-REP-1 |

**Note on rule 3 (AD ruling C6 applies):** the comparison proposed the v1 perimeter width as an apron "of low or no
buildings". Section 8.2 rules dense city to the walls, so the apron here is a **lighting** rule: the buildings stay,
their lit-window density ramps down near the compound and some blocks go dark. Rooms stay visible through the
occlusion rule (7).

**Test IDs and thresholds** (all provisional; derived from hand-built passes; config `checks.composition`):

| ID | Applies to | Measure | Threshold |
|---|---|---|---|
| R-SIL-1 | street | lit-mass skyline std (frame heights) | >= 0.15 |
| R-SIL-2 | street | same, in every 1/4-frame window | >= 0.08 |
| R-DET-1 | street | mean Sobel magnitude | >= 0.028 |
| R-DET-2 | street | bright blobs (luma > 0.6) per megapixel | >= 450 |
| R-CALM-1 | netrun views (street, HQ) | detail CV over 64 px tiles | 0.45-0.85 |
| R-CALM-2 | netrun views | calm tiles (Sobel < half the median) | 12-32 % |
| R-HUE-1 | street, city | hue entropy (36 bins, chromatic pixels) | >= 3.8 bits |
| R-HUE-2 | street, city | top hue cluster share | <= 45 % |
| R-FOCUS-1 | every landmark in frame | landmark-box mean luma / ring mean luma | >= 1.5 |
| R-HOR-1 | city views | built-top std in every 1/4 window | >= 0.015 |
| R-REP-1 | all | high-passed 128 px tile autocorrelation, p90 | <= 0.60 |
| R-VAL-1/2/3 | AAA-2 | median / under 0.10 / over 0.85 | 0.12-0.17 / 25-40 % / <= 2.5 % (12.1) |

### 13.2 What procedural already does better (AD 2026-10-15)

- **Continuity:** the street, the HQ and the city are one layout; the street IS the map's border link.
- **Grounding and scale:** the v2 HQs sit in a real downtown (v1 sat on a void); window dots give the floor height.
- **Density on demand:** 2-4x v1's bright blobs per MP. The task is to *thin* it by rule (rule 3), not add more.
- **Less tiling:** repetition p90 0.31-0.37 (v2) against 0.58-0.77 (v1).
- **Consistent values:** procedural street frames sit in the AAA-2 band without hand grading (f_0340: 0.124 / 36 % /
  0.6 %); the kit hits it once the solve is fixed (rule 10).
- **Atmosphere at city scale:** sky, sea, value falloff and beams; the hand-built v6 key art is a flat carpet.
- **Story props where the rule knows the story:** the Orbital v2 rocket; the Meridian crane as the street's landmark.

### 13.3 Still hand-placed or hand-tuned

Items known to be hand-placed or hand-tuned (each needs a rule above or a new one):

- Street: the r2 dressing (text signs, ad planes, holo ads, megastructures, drum column, stalls), the near-layer
  silhouettes (dropped), the y 600 skyline wall, the L4_0 warm key, the HQ page furniture positions, tuned numbers
  (fill fog strength, city haze, calibration grade) (`SB/NOTES.md:223-228`).
- Halcyon: plinth lettering and crest positions, gatehouse position, the shown decision states, the eye blade
  height, the reveal lighthouse speed and flash, light levels, room interiors in code (`HQ_halcyon/NOTES.md:256-265`).
- Meridian: room slots, gatehouse and skyway bend, the shown state, light levels, the reveal path, container IDs
  (`HQ_meridian/NOTES.md` section 7).
- Orbital: station azimuths, antenna decks, gantry position, the struck site, cutscene cameras, light levels.
- Solace: route floors list, overview yaw, pane patterns, lettering position, reveal path.
- Rebel Cell: lane rooms' x positions and roof heights, the countered room, the fist box and ring radius.

---

## 14. Open questions for the designer, and the ROUTE_REQUIREMENTS gaps

### 14.1 Open questions (real ones only)

1. **Q1 HQ compound footprint vs the map lot.** The unit system is settled (AD ruling 2026-10-15: kits rescaled by
   0.2375, 8.6). Open: must each rescaled landmark fit its `LANDMARK_FP` exactly (an extra per-corp fit factor), or do
   the HQ lots on the map grow to the compound?
2. **Q2 Slot counts.** Topology comes from the game graph, mapped onto slots (hard rule, AD ruling 2026-10-15, 8.4).
   Open: is each corp's slot count (rooms per face / course / floor) an art constraint the game's HQ graphs must
   respect, or must every landmark add slots on demand?
3. **Q3 One LOD by distance.** At the street OVERVIEW the storyboard shows full signage; at the HQ OVERVIEW the HQ kit
   fades signage to 0. Accept distance-based bands (5.1), which keep both?
4. **Q4 Value band tolerance.** Median 0.14 +- 0.03 as the pass rule?
5. **Q5 Landmark ratio above 2.0.** A warning (as proposed, since Halcyon 2.9 was accepted) or a fail?
6. **Q6 Power-cut level.** 32 % + 40 % desaturation (street) or 22 % (HQ)? One value for both?
7. **Q7 Entry durations.** 0.9 + 0.7 + 0.3 + 2.4 = 4.3 s from press to street, and REVEAL + MARK compressed to about
   3 s behind a "short jack-in" setting (`SB/NOTES.md:300`)?
8. **Q8 Central Server off-screen on the HQ page** keeps its red edge marker, or the HQ framing includes it
   (`SB/NOTES.md:301`; DR 1352 says an off-screen corp HQ gets the edge arrow)?
9. **Q9 Art RNG streams.** Presentation randomness from named `art/*` streams, never from the game's streams (3.5).
   Proposal (AD ruling 2026-10-15): the game derives the art seeds from an `RngService`-derived seed and exports them
   into `derive_<run>.json` (`art_seeds`), so Blender never invents a seed. It needs a TECH_SPEC / DECISIONS entry.
   Approve?
10. **Q10 Z-toggle zoom time.** The entry zoom takes 1.0 s (designer answer); the DECISION / OVERVIEW toggle is 0.70 s
    in the rig (`V3D/cam_rig.py:37`). Proposed: 1.0 s for both (AD ruling 2026-10-15, C11).

**For the build session / designer, not art tooling** (AD ruling 2026-10-15, C16):
- Heal / rest points (ROUTE_REQUIREMENTS 7). GDD 4.2 has no heal or rest node type. No art tooling is built for it
  until the GDD has such a node; then it is one `ROOM_TL` entry plus a sticker keyed by the node kind.

**Open numbers** (calibrated by the build session, not designer questions):
- N1: the LOD band distances in Godot (5.2), one calibration pass on the street and one HQ.
- N2: in-game entry durations (section 10; tied to Q7).
- N3: performance budgets (11.4).
- N4: the beam-profile image thresholds (12.5).
- N5: the Godot fog calibration: r3 relied on Blender light linking, which Godot lacks (`R3/NOTES.md`, "Limits").

### 14.2 ROUTE_REQUIREMENTS gaps (`route_map_graph/ROUTE_REQUIREMENTS.md`)

The file marks four items "GAP" (7, 8, 9, 12) and two "check in the build" items (3, 13).

| Item | Gap | Proposed resolution |
|---|---|---|
| 7 | Heal / rest points need an at-rest marker | **Out of scope for art (AD ruling 2026-10-15, C16).** Moved to the "for the build session / designer" list in 14.1: GDD 4.2 has no such node, so no art tooling until it does. |
| 8 | Heat per node (Rack Heat) and the raid threshold | **Proposed:** a Heat chip on the Rack room's sticker (value from the game); a red pencil tick "RAID AT <n>" on the first link where the game reports cumulative Heat crossing the threshold. The tools draw what the game passes in (`heat_by_node`, `raid_threshold_edge`); they compute nothing. |
| 9 | Node numbers and layers self-evident | **Open (playtest).** Layers read as buildings left to right (street) or spiral turns (HQ). Option: a step ruler in OVERVIEW only, drawn under the street at the column centres. |
| 12 | GRID VIEW and ROUTE VIEW share one graph language | **Proposed:** the HQ page draws the run path on the City Grid with the same wax states (lime walked, orange plan / option, white ahead, grey past), the same stickers and the same state rings, in the mainline look; the plan pencil (9.5) is the first instance. Mainline task with these values. |
| 3 | Elite vs fight sticker shapes at 1280 x 720 | **Check** 12.6 "1280 x 720 readability" produces the review frame. |
| 13 | 1280 x 720 readability of DECISION | Same check. |

---

## 15. Conflicts between sources (resolved here or carried)

| # | Conflict | Resolution in this spec |
|---|---|---|
| C1 | Units: one-city floor 1.9 BU and lot 6 BU (`SB/sb_onecity.py:36`, `CAC/city_preset.py:3-4`) vs "1 storey = 8 BU" in the r3 preset and every HQ preset (`SB/look_preset.py:3`, `HM/hq_preset.py:4`) vs the downtown's 3.1 BU window pitch (`HK/downtown.py:17-18`) | **AD ruling 2026-10-15:** one unit system (1 floor = 1.9 BU, 1 lot = 6 BU); `unit_scale` 3.0 for r3 values; HQ kits rescaled by 0.2375 (8.6); occlusion stub 2 floors = 3.8 BU |
| C2 | Section plinth: 1.2 BU in `SB/NOTES.md:383` and the `look_preset` comment (`SB/look_preset.py:89`) vs the value 0.4 (`SB/look_preset.py:90`, `SB/NOTES.md:477`) | 0.4 |
| C3 | Look values: `SB/NOTES.md:480` (beam 5e6, cone 10, fog_peak 0.039, underlight 0.06) vs `SB/sb_ocjobs.py:36-44` (beam 6.0e5, cone 30, fog_peak 0.0507, underlight 0.07, beam_soft_w 0.5) vs the tool defaults in `M44/onecity_cycles.py` (beam 2e7, fog_peak 0.021, cityglow 2.5e3, lamp 25, wash 120, neon 3.2, win 1.6) | **AD ruling 2026-10-15:** `sb_ocjobs.LOOK` is the source of truth; refreshed from the storyboard v3 revision (beams, fog) rendering tonight; `TODO(refresh after sb v3 rev)` on the fog and beam rows (4.1, 11.1) |
| C4 | r3's Godot beam mapping (spot 1-4 deg, hero cores 0.9 deg; `R3/NOTES.md:227`, `SB/look_preset.py:54-56`) vs the v3-r3 rule "soft cones, no core, no rods" (`M44/onecity_cycles.py:259-265`; `SB/NOTES.md:480`) | **AD ruling 2026-10-15:** soft volumetric cones only, no core spot, never rods; the hero core and spot removed from the Godot mapping (11.1); r3 beam values superseded; checked by 12.5 |
| C5 | Zoom domain: storyboard 0 = HQ aerial .. 1 = street OVERVIEW (`SB/look_preset.py:72`) vs HQ kit 0 = OVERVIEW .. 1 = DECISION (`HK/lod.py:4`), same band numbers | Two named parameters; Godot LOD by distance (Q3) |
| C6 | Halcyon's cleared perimeter belt that every camera stands in (`HQ_halcyon/NOTES.md:65, 136, 276`; `perimeter` keys in every preset) vs "no open perimeter, dense city close" (DR 1395, 1406; `HK/downtown.py:1-3`) | **AD ruling 2026-10-15:** dense city to the walls wins; `perimeter` keys legacy, default 0; cameras clear the view with the occlusion rule (7), never a cleared belt (8.2) |
| C7 | HQ kits build their own synthetic downtown + ring city vs one continuous city from the map lots (DR 1385-1388, 1399); compound size vs `LANDMARK_FP` (Meridian keep half 136 BU vs map square 32 BU) | **AD ruling 2026-10-15:** one unit system, HQ kits rescaled to it (8.6); map lots by default, kit city as fallback (8.2); compound footprint vs map lot stays open (Q1) |
| C8 | The Meridian freight line: HQ kit = a straight viaduct north at x 66 to y 1180, deck z 22 (`HM/hq_preset.py:51-52`) vs city = a BFS over street tiles to the nearest coast cell, deck z 9.0 (`CAC/zoning.py:353-390`, `CAC/city_preset.py:149`). DR 1410 wants the same line in both | **AD ruling 2026-10-15:** ONE line; the city derivation's rail search (3.4 L4) is the source; the HQ scene imports the same polyline and `deck_z` 17.5 BU (clears the tallest frontage 15.3 BU, i.e. a 6-floor front + key floors, plus 2.2 BU); the straight x 66 viaduct is a placeholder to replace; checked by 12.4 |
| C9 | Occlusion Godot text uses `world_vertex.z` (`HQ_meridian/NOTES.md`, `HQ_halcyon/NOTES.md:346`); Godot is Y-up | World Y |
| C10 | Power cut 32 % + 40 % desat (`V3D/../NOTES.md:85`) vs 22 % / x 1.45 (`HM/hq_jobs.py:39`, `HQ_halcyon/NOTES.md:114`) | **AD ruling 2026-10-15:** kept as designer question Q6 |
| C11 | Zoom time 0.70 s (`V3D/cam_rig.py:37`) vs "the zoom takes 1.0 s" (`SB/NOTES.md:83`, `SB/sb_cams.py:106`) | **AD ruling 2026-10-15:** designer question Q10; proposed 1.0 s for both |
| C12 | Meridian camera: NOTES section 4 (pitch 14-24, fill 56 / 62 %, overview yaw 150, pitch 30, lens 40) vs `HM/hq_preset.py:125-126` (21-27, 0.50 / 0.54, 140, 40, 36) | The preset (later, v2) |
| C13 | Landmark rule "1.5-2x" vs measured ratios 0.92-13 (Meridian 1.33 / 0.92, Halcyon 2.9-3.3, Orbital 2.5-3.8, Solace 3.2-13, Rebel 1.46-3.8; `hq_rev_STATUS.md:73`, corp NOTES) | 12.2: < 1.5 fails, > 2.0 warns; Q5 |
| C14 | Foreground occluder fade 0.15 s on the street (`V3D/../NOTES.md:159`) vs 0.3-0.5 s for the HQ occlusion rule (DR 1411) | **AD ruling 2026-10-15:** one value for street and HQ: 0.35 s ease-in-out (7.1, 7.2, 7.4) |
| C15 | HQ kit `layout.Compound` generates run topology (`HK/layout.py:36` rows 6-5-4-3-2-1; per-corp `seq` lists) vs scope "routes and nodes come from the game"; GDD 4.2 is 7 layers of 2-4 nodes | **AD ruling 2026-10-15:** the Compound / `seq` lists are MOCK route data for concept renders; topology always comes from the game graph (GDD 4.2) mapped onto slots: a hard rule in 1 and 8.4; slot counts in Q2 |
| C16 | ROUTE_REQUIREMENTS 7 asks for heal / rest markers; GDD 4.2 has no heal / rest node type | **AD ruling 2026-10-15:** out of scope for art; moved to the build session / designer list (14.1); no art tooling until the GDD has such a node |
| C17 | The brief counts 5 ROUTE_REQUIREMENTS gaps; the file marks 4 "GAP" items (7, 8, 9, 12) and 2 checks (3, 13) | All six covered in 14.2 |
| C18 | Street rig: v3 dynamic always starts camera-left looking right (`V3D/../NOTES.md:52-55`) vs the one-city mirror when the start lands on the right (`SB/sb_onecity.py:357-378`, `SB/NOTES.md:393-394`) | The one-city rule (mirror by geometry) |
| C19 | `SB/NOTES.md:109-114` cites mainline files "on main" (`scripts/city3d/...`); this repo's `main` branch has none of them; they live in `D:\Godot\rebel_cell\` | **AD ruling 2026-10-15:** cite them as `D:\Godot\rebel_cell` main-branch paths (`MAIN/`); the build session owns them (section 0) |
| C20 | Frontage height: "about 11.5 BU" (DR 1386) vs "6 x 1.9 = 11.4 BU" (`SB/NOTES.md:458`) vs the code `(6 + key % 3) * 1.9 + 0.1` (`SB/sb_onecity.py:135`) | The code |
| C21 | The HQ kit exists as five identical copies (`hq_<corp>/scripts/hq_kit/`), and the generalised scene / jobs / compose as per-corp copies | **AD ruling 2026-10-15:** ONE package, `tools/netrun_art/`, with per-corp landmark plugins; copies forbidden (2.2) |
| C22 | "Same seed gives the same image hash" vs GPU Cycles + OIDN not being bit-exact | **AD ruling 2026-10-15:** agreed: exact hash on data, geometry and a deterministic preview render; tolerance on GPU finals (12.3) |
| C23 | CLAUDE.md rule 2 (randomness only via `RngService` streams) vs every art script seeding `random.Random(<literal>)` | **AD ruling 2026-10-15:** kept as Q9, with the proposal that art seeds come from `RngService`-derived seeds exported into `derive_<run>.json` (`art_seeds`), so Blender never invents seeds (2.3, 3.5) |
| C24 | Meridian NOTES section 1 says the moat is on W, S and E with the north side the rail yard; v2 says the moat runs round all four sides (`HM/hq_preset.py:44-46`) | **AD ruling 2026-10-15:** moat on W / S / E only; the north side is the rail yard and the gate the freight line leaves by (matches the designer's rail note; 8.5) |
