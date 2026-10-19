# NA-02 frozen field list (netrun-art data contract v1)

Date 2026-10-18. Owner: orchestrator (D8). Input to brief `docs/handoff/plan2/drafts/briefs/na02.md`.
Precedence: the agreed contract (`NA02_CONTRACT_PROPOSAL.md` C1-C4, art-pass HANDOFF_PACKAGE, accepted by the build
session 2026-10-18) WINS over `docs/handoff/netrun_art/PIPELINE_SPEC.md`. Where they differ the row says
"spec superseded (C#)". Nothing is added beyond spec + contract; gaps are in **Open** at the end.

Build-session notes on the contract (binding):
- `layout_seed` = `CityModel.city_seed` (signed int) written as its two's-complement u64, decimal string.
- Export from a full-city build only (`CityModel.build` with no `rect`).
- A cell is never split across chunks (`NeonCity._lot` draws a merged building once, from its front lot). Group prisms
  by `cell`; `bid = "i:j"` from `cell.position`; HQ stand-ins get `"hq:<corp>"`.
- The Godot ID capture is a later slice (NA-04). Its class table is fixed now: 0 sky, 1 landmark compound, 2 city,
  5 rooms, 6 landmark movers; 3 and 4 reserved.

Fixtures (copied from the art session, frozen): `tools/netrun_art/fixtures/na02_vectors.json`,
`tools/netrun_art/fixtures/seeds_ref.py` (regenerates the vectors byte-identically).

## 1. Canonical JSON rules (all five files)

| Rule | Value |
|---|---|
| Encoding | UTF-8, LF line ends, one trailing LF, no BOM |
| Key order | object keys sorted ascending by code point, at every depth. Arrays keep the order given in each table |
| Floats | rounded to 1e-4, written fixed with trailing zeros trimmed to at least one decimal (`1.0`, `0.5`, `12.3457`); no exponent, no `-0.0` (write `0.0`), no NaN or Inf |
| Ints | plain JSON integers, only for values within +-2^53 |
| u64 | every u64 is a **decimal string** (`layout_seed`, `art_seeds` values, vectors). GDScript ints are signed and JSON numbers lose precision above 2^53 |
| Versions | `version` is the int `1` in every file. Spec 2.3 `version` (rules-version string) superseded (C1) |
| Ids | strings. Sort ties break by id, never by dictionary order (CLAUDE.md rule 7) |
| Whitespace | not fixed by the contract (Open O12); the byte-identity test compares the exporter against itself |

Units: BU (Blender units; 1 lot = `lot_bu` = 6.0 BU). Plan coordinates `[x, y]`: x = east = Godot world X, y = north =
-(Godot world Z). Plan origin = world (0, 0) = lot `origin_lot`. Heights are BU above local ground.

## 2. `city.json` v1 (contract C1, C2)

Source: `CityModel` of a full-city build (`scripts/city3d/city_model.gd`), via the prisms the recorder produced
(`city_layout_recorder.gd`). `city_layout.json` (the recorder's file) is internal; spec 2.2 `layout.import_city` input
is superseded (C1).

### Header

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `version` | int | none | constant | `1` |
| `layout_seed` | string | decimal u64 | `CityModel.city_seed` | two's-complement of the signed int (`city_seed & 0xFFFF...` printed unsigned) |
| `units` | string | none | constant | `"BU"` |
| `lot_bu` | float | BU per lot | `CityConfig.lot_bu` | `6.0` |
| `origin_lot` | [float, float] | lots | `CityConfig.district_centre` | `[CX, CY]`; world (0,0) = this lot point (`CityIsoCamera.lot_to_world`) |
| `buildings` | array | none | see below | sorted by `bid` (string compare) |
| `streets` | array | none | `CityModel.streets` | sorted by `lot` (i, then j) |
| `plazas` | array | none | `CityModel.plazas` | sorted by `lot` (i, then j) |
| `hqs` | object | none | `CityModel.hqs` | keys = corp ids |
| `hq_overlaps` | array | none | diagnostic (v1 addition, W0 HQRECT) | `[{ "bid", "corp" }]`: every non-HQ building whose cell intersects an HQ rect, sorted by (bid, corp). Empty after the layout fix (an HQ rect is exclusive); a non-empty list is a layout bug, and no building is dropped silently |

### `buildings[]` (one per cell)

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `bid` | string | none | `cell.position` | `"i:j"` (ints, decimal, `-` allowed). HQ stand-in: `"hq:<corp>"`. Spec 3.1 `key` and 3.2 `(ci, key)` superseded (C2). Not `CityModel.building` (depends on chunk order) |
| `cell` | [int, int, int, int] | lots | prism `cell` (`Rect2i`) | `[i, j, w, h]`; cells do not overlap, so `bid` is unique |
| `terr` | string | none | prism `terr` | district / corp id |
| `hq` | bool | none | prism `hq` | `true` for the stand-in towers |
| `key` | int | none | prism `key` | legacy extrusion key, kept for golden-image look-dev parity only; value = the `key` of the first part in `parts` order. HQ stand-in tiers carry `7919 + k` |
| `parts` | array | none | prisms of this cell | sorted by `(z0, tier index)`; HQ: one part per tier |

### `buildings[].parts[]`

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `poly` | [[float, float], ...] | BU, plan coords | prism `poly` (world X, Z) | each point `[x, -z]`; vertex order as recorded (not re-sorted) |
| `z0` | float | BU above local ground | prism `y0` | already BU (`z0 px * height_px_bu`) |
| `h` | float | BU | prism `h` | |
| `taper` | float | ratio | prism `taper` | top scale; 1.0 = no taper |

`ink` (Color) is not in v1. Colors are art-side.

### `streets[]`

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `lot` | [int, int] | lots | street `lot` | `[i, j]` |
| `along_i` | bool | none | street `along_i` | |
| `along_j` | bool | none | street `along_j` | |
| `traffic` | float | share 0..1 | street `traffic` | |

Street `col` (Color) is not in v1.

### `plazas[]`

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `lot` | [int, int] | lots | plaza `lot` | |
| `terr` | string | none | plaza `terr` | |

### `hqs{}`

`{ "<corp id>": [i, j, w, h] }`, ints in lots, from `CityModel.hqs` (`Rect2i`).

### Optional sections in v1

Terrain, water, rails and other planner layers: **absent** for today's fixed city. When present they follow
`city_A2.json` converted to BU. Adding them is a v2 data change only; the v1 fields above do not move (C1). The
per-seed generator NA-12 fills this same file.

## 3. `net.json` v1

The city network (Sites and their links) for `derive.street`. Spec 2.2 `layout.import_net` describes the shape; the
contract is silent, so the spec stands. Source: the corp's `CityGridData` (`SiteData`), `GridState`, and
`CityLayout.site_points` (lot per Site; presentation only).

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `version` | int | none | constant | `1` |
| `layout_seed` | string | decimal u64 | as city.json | ties the net to the city |
| `nodes` | array | none | `CityGridData.sites` | sorted by `id` |
| `nodes[].id` | string | none | `SiteData.id` | |
| `nodes[].lot` | [float, float] | lots | `CityLayout.site_points[id]` | lot point (`floor + 0.5` is the lot centre, as `CityLandmarks.site_lot`) |
| `nodes[].state` | string | none | `GridState.status_of` + `is_home` | `"core"` (home), `"owned"` (CLAIMED), `"corporate"`, `"cleared"`, `"taken"` (spec lists `owned`/`core`/`...`; full set mapped from `SiteStatus`) |
| `links` | array | none | `SiteData.links`, `locked_links` | sorted by `(a, b)` with `a < b` |
| `links[].a`, `links[].b` | string | none | `SiteData.id` | `a < b` string compare (as `GridState.link_key`) |
| `links[].state` | string | none | `GridState.is_link_open` | `"open"`, `"locked"`, `"opened"` (locked link opened by Intel), spec leaves values open |
| `links[].pts` | [[float, float], ...] | lots | none | spec: link polyline in lots. See Open O3 |

## 4. `run_graph.json` v1

The netrun map of one run, 1:1 with `MapGraph` (`scripts/core/map_graph.gd`; held in `RunState.map`). `version` is
`1` so N16 can bump it.

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `version` | int | none | constant | `1` |
| `layers` | int | count | `MapGraph.layer_count()` | |
| `nodes` | array | none | `MapGraph.all_nodes()` | sorted by `(layer, index)`; count equals `node_count()` |
| `nodes[].id` | string | none | node `id` | `L<layer>N<index>` (`MapGraph.make_id`) |
| `nodes[].layer` | int | 1-based | node `layer` | |
| `nodes[].index` | int | 0-based | node `index` | |
| `nodes[].type` | string | none | node `type` (`RC.InfilNodeType`) | `"router"`, `"terminal"`, `"mainframe"`, `"server_rack"` |
| `nodes[].elite` | bool | none | node `elite` | |
| `edges` | array | none | node `next` | one per `(id -> next)` pair; sorted by `(a, b)` |
| `edges[].a`, `edges[].b` | string | none | node id, `next` entry | forward edge a -> b; `b` is on layer(a)+1 |

Edge count equals the sum of `next` sizes. Node `heat` is a gameplay value and not exported (Open O5).

## 5. `key_locations.json` v1

The central-server access-key locations (spec 2.0 step 2, 8.8). Per D5 and the brief, a key location is an **Exploit
Site building**, using today's Exploit semantics; B2/D5 may change them later.

| Field | JSON type | Unit | Source | Notes |
|---|---|---|---|---|
| `version` | int | none | constant | `1` |
| `layout_seed` | string | decimal u64 | as city.json | |
| `locations` | array | none | Sites with `SiteData.exploit_type != NONE` | sorted by `site` |
| `locations[].site` | string | none | `SiteData.id` | |
| `locations[].corp` | string | none | owning corp id | the territory the Site belongs to |
| `locations[].bid` | string | none | building under the Site's lot | `"i:j"` of the building whose `cell` contains `floor(CityLayout.site_points[site])`; must exist in `city.json` |
| `locations[].exploit` | string | none | `SiteData.exploit_type` (`RC.ExploitType`) | `"intel"`, `"breach"`, `"virus"` |

Art uses `bid` for the per-corp key-landmark types (spec 8.8) and the stream `key_landmark.<corp>`.

## 6. `derive_<run>.json` v1 keys

Spec 2.3 as amended by C3. `<run>` is the run id. The same file serves street (`kind: "street"`) and HQ
(`kind: "hq"`) netruns. Every building reference is a `bid` (C2).

| Key | JSON type | Unit | Notes |
|---|---|---|---|
| `version` | int | none | `1`. Spec 2.3 string rules version superseded (C1) |
| `kind` | string | none | `"street"` or `"hq"` |
| `layout_seed` | string | decimal u64 | root of `art_seeds` |
| `art_seeds` | object | none | `{ "<stream name>": "<u64 decimal string>" }`, keys are stream names of section 7 (per-object streams are derived by the consumer from `art_seed(stream, *keys)`, so only the scene-level seeds are listed). Spec 2.3 `{stream: int}` superseded (C3) |
| `seed_key` | removed | | dropped (C3) |
| `street` | {a: [x, y], c: [x, y]} | BU plan | chosen leg, extended |
| `nrm` | [x, y] | unit vector | street face normal |
| `start_left` | bool | none | |
| `span` | int | floors | 1 or 2 |
| `columns` | [[layer, bid]] | layer int, `bid` string | route column per layer |
| `route_keys` | [bid] | none | every building part of every route column (name kept; entries are `bid`) |
| `col_info` | [{layer, bid, top, u0, u1, face}] | layer int, BU | column extents. Spec `key` renamed `bid` (C2) |
| `rooms` | {node id: {front, back, floor, span, bld, parts, layer, kind}} | BU world | `front`/`back` are 4-element arrays as in the spec; `bld` is a `bid` |
| `edges` | [{a, b, type, path}] | BU | link polylines on the facade plane |
| `overview`, `decision` | pose objects | BU | solved camera poses (spec section 6) |
| `frontage` | [[bid, h, floors, taper]] | BU | `[string, float, int, float]` |

Who fills what is Open O4.

## 7. Art streams and seed algorithm (contract C3)

```
art_seed(layout_seed, stream, *keys) =
    fnv1a64( utf8( compact_json( [ str(layout_seed), "art/" + stream, *keys ] ) ) )
```

- `layout_seed` is the u64 decimal string (section 2 header). It is the **first array element, as a JSON string**.
- Compact JSON: separators `,` and `:` with no spaces, `ensure_ascii` (non-ASCII as `\uXXXX`, lowercase hex),
  no float keys. Keys are ints or strings only (no bool, no float). Negative ints are allowed.
- FNV-1a 64: offset `0xcbf29ce484222325`, prime `0x100000001b3`; per byte `h = ((h ^ b) * prime) mod 2^64`.
- Result u64 is written as a decimal string wherever stored.
- Draws: `splitmix64` seeded with the art seed: `state += 0x9E3779B97F4A7C15`; `z = state`;
  `z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9`; `z = (z ^ (z >> 27)) * 0x94D049BB133111EB`; `out = z ^ (z >> 31)`
  (all mod 2^64). `uniform(x) = (x >> 11) * 2^-53`. Python `random` only in Blender-only dressing.
- No `RngService` stream is read or advanced. Spec 3.5 rule 2 (seed "derived from an RngService-derived seed")
  withdrawn (C3). Per-object streams are keyed by content ids, never draw order (spec 3.5 rule 3).

Stream names (spec 3.5 table, plus the C3 additions). Legacy literals live in spec 3.5 and are not part of the
contract.

| Stream | Keys (per object) | Use |
|---|---|---|
| `building` | `bid` | building detail |
| `scene` | none | one-city scene misc |
| `lanes_tile` | `i`, `j` | lane strokes per street tile |
| `cars` | none | parked street cars |
| `sky` | none | sky lanes |
| `room_wall` | node id | room wall windows |
| `hero_sign` | column index `k` | blade sign panels per column |
| `ground_glow` | none | street-level glows |
| `street_lanes` | none | moving streak lanes |
| `beams` | none, or `bid` for street beams | beam lean and sweep |
| `plumes` | none | steam plumes |
| `glows` | none | bank and wisp glows |
| `windows_flicker` | none | idle window switches |
| `flicker` | none | flicker tables |
| `glitch` | none | billboard glitch slices |
| `city_fill` | none | AAA fill city |
| `zoning`, `post` | none | all-corps city (spec table: `zoning` .. `post`; the intermediate names are Open O6) |
| `downtown` | none | HQ downtown fallback |
| `ring` | none | HQ ring city fallback |
| `landmark.<corp>` | none | landmark detail |
| `cycles` | none | Cycles sampling seed |
| `variance` | `bid` | art variance draws per lot (spec 3.5b; added by C3, audit row 40) |
| `terrain` | none | terrain (C3) |
| `fauna.tethys` | creature keys (ints/strings) | Tethys fauna (C3) |
| `key_landmark.<corp>` | `bid`, index | key-location landmark types (C3, spec 8.8) |

`derive_<run>.json` `art_seeds` carries one entry per stream above that has no keys, plus `variance`, `terrain`,
`fauna.tethys` and `key_landmark.<corp>` base seeds (keys omitted).

### Test vectors (FNV-1a 64 art seeds, 11)

Source: `tools/netrun_art/fixtures/na02_vectors.json` (generated by `tools/netrun_art/fixtures/seeds_ref.py`; the JSON also
holds the first 3 splitmix64 outputs and `uniform_first` per case). Compact JSON hashed is
`[layout_seed_string,"art/"+stream,*keys]`.

| # | layout_seed | stream | keys | seed |
|---|---|---|---|---|
| 1 | 0 | building | `["0:0"]` | 15701598436461993137 |
| 2 | 1 | building | `["12:7"]` | 9165574956381771384 |
| 3 | 1 | building | `["hq:meridian"]` | 4640807537992070582 |
| 4 | 424242 | room_wall | `["n3"]` | 17818933182050907662 |
| 5 | 424242 | lanes_tile | `[4, 9]` | 8166113371222797496 |
| 6 | 18446744073709551615 | scene | `[]` | 3474837307278791102 |
| 7 | 9007199254740993 | hero_sign | `[2]` | 2191170140961925557 |
| 8 | 77 | variance | `["7:3"]` | 17623002874232533020 |
| 9 | 77 | key_landmark.tethys | `["21:14", 0]` | 14899214495525913472 |
| 10 | 123456789 | fauna.tethys | `[-3, "pod"]` | 10005971198481274621 |
| 11 | 5 | beams | `["été"]` (non-ASCII key) | 3454596537168434450 |

The exporter and `ArtSeed.derive` must reproduce all 11, including u64 max, 2^53+1, a negative key and a non-ASCII
key. Cases 6 and 7 need unsigned arithmetic in GDScript (signed 64-bit wraps correctly for multiply and xor; print
unsigned).

## Open

Each item says what the code or contract cannot supply today. None blocks the v1 files above unless noted.

- **O1 key export unit/order.** `bid` for a multi-part cell and the `key` value choice (first part) is derived here,
  not in the contract. Confirm. Also whether HQ stand-in tiers are one building with N parts (this doc: yes).
- **O2 city_seed sign.** `layout_seed` for a negative `city_seed` uses the two's-complement u64 (build-session note).
  The code has `CityConfig.city_seed = 7` (non-negative); no negative seed exists to test against.
- **O3 `net.json` `links[].pts`.** No link polyline exists in code: `SiteData.links` is an id list and
  `CityLayout.site_points` gives Site points only. `pts` needs a routing rule (straight `a -> b`, or a street path).
  Also `net.json` coordinates: spec says lots, `city.json` is BU. This doc keeps lots for `net.json`; decide, or
  convert to BU plan coords.
- **O4 who writes `derive_<run>.json`.** The game can supply `version`, `kind`, `layout_seed`, `art_seeds` only.
  `street`, `nrm`, `columns`, `col_info`, `rooms`, `edges`, `overview`, `decision`, `frontage` come from `derive.street`
  (Python tools, NA-03). Does the NA-02 exporter write a partial v1 (game keys), with the tools filling the rest?
- **O5 run_graph extras.** Node `heat` (gameplay) and the run id are not in spec or contract; excluded. Confirm. The
  file name carries `<run>`, but no run-id field exists in `run_graph.json` or `derive`.
- **O6 stream names `zoning` .. `post`.** The spec table gives a range (seeds 7701-7708) with only two names; the
  intermediate stream names are not given. Art to supply or drop.
- **O7 Site to building.** No `Site -> bid` mapping exists in code; Site lots are presentation-only
  (`CityLayout.site_points`) and can fall on an HQ plaza, off the city, or share a lot (`spread_report`). The
  exporter must pick the building whose `cell` contains the lot, and fail the export for a Site with none
  (acceptance 8). Likely needs a placement rule for D5.
- **O8 Exploit semantics.** "Exploit Site" = `SiteData.exploit_type != NONE` (INTEL, BREACH, VIRUS) today; `objective`
  EXPLOIT also exists. Confirm which field is authoritative.
- **O9 `net.json` state names and the `corp` field.** `GridState.SiteStatus` has no `owned`/`core` values; the
  mapping in section 3 is derived. A Site's owning corp is not stored on `SiteData`; it comes from the `CorporationData`
  that holds the grid.
- **O10 derive nested shapes.** Spec gives `front[4]`, `back[4]`, `parts`, `kind` and the pose dicts without element
  types or units beyond "world BU". NA-03 fixes them with the Python port; this list freezes top-level keys only.
- **O11 ID capture class table.** Fixed (section header) but no Godot code exists; NA-04 owns it.
- **O13 new node kinds.** Spec shows rest, workshop and cache room kinds; `MapGraph` has only router, terminal, mainframe, server_rack. If N16 or a later slice adds kinds, `run_graph.json` bumps to v2 (or adds enum values) and `rooms[].kind` follows.
- **O12 whitespace.** Pretty-print indent vs compact is not stated by spec or contract; the exporter picks one and the schema tests keep it.

## Spec deltas (vs PIPELINE_SPEC §2.0c / §2.3, re-imported at main 0bc5ab46)

This file wins. Art-pass to align §2.0c / §2.3 to it.

| # | Spec text | This file | Why |
|---|---|---|---|
| D1 | `city.json` v1 header lists `version` 1 (int) | same; plus `buildings[].key` rule (first part's key) and sort orders for streets/plazas/parts | needed for byte-identity |
| D2 | `net.json` has no version, no `layout_seed`; `state` unspecified | adds `version` 1 and `layout_seed`; `state` in {core, owned, corporate, cleared, taken}; `links[].state` in {open, locked, opened} | all JSON files carry `version` 1; states mapped from `GridState` |
| D3 | `net.json` links `pts in lots` | kept, but code has no polyline (Open O3) | |
| D4 | `run_graph.json`: "nodes, layers, kinds (incl. rest, workshop, cache), edges, walked state" | `layers`, `nodes[] {id, layer, index, type, elite}`, `edges[] {a, b}`. `type` is the 4 `RC.InfilNodeType` values. **No** rest/workshop/cache kinds (not in `MapGraph` today; N16 / later bump) and **no** walked state (it lives in `RunState`, not `MapGraph`; the file is the static graph, `version` 1) | 1:1 with `map_graph` (acceptance 7). Open O13 |
| D5 | `key_locations.json`: `bid`, kind, corp | `version`, `layout_seed`, `locations[] {site, corp, bid, exploit}`; `kind` renamed `exploit` (intel/breach/virus) and `site` added | Exploit Site = key location (D5), Site id is the stable key |
| D6 | `derive_<run>.json` `version` is a string (rules version) | int `1` | contract C1 versions |
| D7 | derive producer = the tools only | tools fill all keys; the game contributes only `version`, `kind`, `layout_seed`, `art_seeds` (Open O4) | |
| D8 | derive `art_seeds`: "one seed per art stream" | scene-level (unkeyed) streams plus the base seeds of `variance`, `terrain`, `fauna.tethys`, `key_landmark.<corp>`; keyed per-object seeds are computed by the consumer | per-object seeds are infinite in number |
| D9 | `rooms[].kind` takes rest/workshop/cache | accepted as string values of the derive file; no game node type feeds them yet (O13) | |
| D10 | `street`/`nrm`/`start_left` street only; HQ derive omits them | accepted: they are present iff `kind == "street"` | |
| D11 | derive has no `layout_seed` | adds `layout_seed` (decimal string) | art_seeds root must be traceable |
| D12 | REST / WORKSHOP / CACHE colors, sticker shapes | not contract fields; art values | coordinator ruling |

## Rulings on the Open list (build session, 2026-10-18)
These close O1-O13 for v1; NA-02 implements them.
- **O1:** confirmed (bid from `cell.position`; `key` = first part's key; an HQ stand-in is one building with N parts).
- **O2:** confirmed; vectors 6 and 7 pin unsigned printing in GDScript (print the u64 from its two halves).
- **O3:** `net.json` uses **BU plan coordinates** like `city.json`. `links[].pts` in v1 = the straight segment
  `[a, b]` (2 points, Site point to Site point). A street-routed polyline is a v2 bump.
- **O4:** NA-02 writes a **partial** `derive_<run>.json` v1 with the game keys only (`version`, `kind`, `layout_seed`,
  `art_seeds`, `run`); NA-03's `derive.street` fills the rest into the same file.
- **O5:** node `heat` stays out. Add `run` (string, the run id the file name carries) to `run_graph.json` and derive.
- **O6 (art-pass 0b17be5b):** city streams `city.zoning`, `city.build`, `city.ring`, `city.streaks`, `city.beams`, `city.sea`, `city.landmark`, `city.post` (legacy seeds 7701-7708 in that order, `city_preset.SEEDS`); scene-level, so in `art_seeds`.
- **O7:** a Site's `bid` = the building whose `cell` contains the Site lot; else the nearest building by Chebyshev
  lot distance, ties by `(i, j)` ascending, within 4 lots; else the export fails naming the Site. Pure function, test it.
- **O8:** Exploit Site = `SiteData.exploit_type != NONE` (authoritative); `objective` is not read.
- **O9:** the derived mapping in section 3 stands; the corp comes from the `CorporationData` holding the grid.
- **O10:** top-level keys only in v1 (as written); NA-03 freezes nested shapes in its schema bump.
- **O11:** the Godot ID capture is its own W1 slice; the class table is fixed here.
- **O12:** pretty-printed, indent 1 space, sorted keys, LF, trailing newline.
- **O13:** `run_graph.json` v1 = the static graph with today's 4 types; new node kinds bump it (N16 / D4 nodes).
- **Spec and vectors pinned (2026-10-18):** art-pass f4f3f839 (BLOCKERs 1-5), b68f2871 (§3.6 tie-break by bid),
  6a58733c (signed seed rule). `tools/netrun_art/fixtures/na02_vectors.json` now has 14 vectors (3 signed seeds: -1,
  INT64_MIN, -424242, with `layout_seed_signed`); the 11 earlier ones are unchanged.

## id.png encoding (confirmed ours, NA-23b, 2026-10-19)
`id.png` is the game's ID capture (O11), not the art pass's: **R = class** (0 sky, 1 landmark compound, 2 city, 3 link
structure, 5 rooms, 6 landmark movers); **G = the 1-based place of the room in the run graph** (0 = none; on class 5 it is
the room index); **B = layer** (the room's layer; 0 elsewhere). **Route-column walls** are class 2 with **B = 1**;
**occlusion stubs** are class 2 with **G = 255, B = 0**. `route_occlusion_record` (`checks/image_checks.py`,
`composition.json` `route_occlusion`: `cut_layer_min` 1, `stub_room` 255) reads exactly this.
