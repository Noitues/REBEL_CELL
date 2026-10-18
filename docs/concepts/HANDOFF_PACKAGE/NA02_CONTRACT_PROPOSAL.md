# NA-02 data contract: art-pass position (2026-10-18)

Answers the addendum's BLOCKER 2 (spec audit rows 3, 4, 5, 13, 14). It is the art side's input to the
orchestrator's `docs/handoff/plan2/NA02_FIELDS.md`. The build session owns the final field list (D8). Once both
sessions agree, art-pass rewrites PIPELINE_SPEC §2.0b/2.1/2.3/3.1/3.5/11.5/12 to match.

## C1. One game-exported layout file: `city.json` v1

- The game exports exactly one layout file, `city.json`. The recorder's `city_layout.json` is internal to Godot, not part
  of the contract. `layout.import_city` reads `city.json` only.
- The concept `city_A2.json` (planner metres) is converted to `city.json` by an art-pass adapter. Godot never reads
  planner JSON. When NA-12's per-seed generator lands, it fills the same `city.json` (D3).
- Units: BU, plan coordinates `[x, y]` with x = east = Godot world X, y = north = −Godot world Z. Heights are BU
  **above local ground** (audit row 9). Floats are rounded to 1e-4 and written in a fixed format.
- Header: `version` (int, 1), `layout_seed` (string, decimal u64), `units: "BU"`, `lot_bu: 6.0`, `origin_lot: [CX, CY]`.
- `buildings[]`, sorted by `bid`: `bid`, `parts[] {poly[[x,y]], z0, h, taper}`, `terr` (district/corp id), `cell [i, j, w, h]`
  (lots), `hq` (bool), `key` (int, legacy, kept for the golden-image look-dev parity only).
- `streets[]` (lot, along_i, along_j, traffic), `plazas[]`, `hqs {corp: [i, j, w, h]}`.
- Terrain, water, rails and the other planner layers are optional sections in v1 (absent for today's fixed city).
  Their shape follows `city_A2.json`, converted to BU. That way v2 adds data and the layout of v1 stays the same.

## C2. Building id

- `bid` = string `"i:j"`, the origin lot of the building's `cell`. Cells don't overlap, so the id is unique. It comes
  from the content, not from draw or chunk order (spec 3.5 rule 3). HQ stand-ins use `"hq:<corp>"`.
- It replaces both `key` (spec 3.1) and `(ci, key)` (spec 3.2). Every reference uses `bid`: `derive` `columns`,
  `route_keys`, `col_info`, `frontage`, `rooms[].bld`; `key_locations.json`; the per-object art streams.
- Not `CityModel.building`: that counter depends on chunk order and `city_rect`.
- Check for the build session: a cell that crosses a chunk border must still be one building. If `add_recording`
  can split one, NA-02 must merge it by cell.

## C3. Art seeds (audit rows 13, 14)

- Root = `layout_seed` (the city seed). No `RngService` stream is read or advanced. The brief's wording is adopted, and
  spec 3.5 rule 2 ("derived from an RngService-derived seed") is withdrawn.
- `art_seed(stream, *keys) = fnv1a64(utf8(json([layout_seed, "art/" + stream, *keys])))`.
  - The JSON is compact: separators `,` and no spaces, ASCII-escaped. Keys are ints or strings only, never floats.
  - `layout_seed` is written as a JSON string inside the array.
- Every u64 in JSON is written as a **decimal string**. JSON numbers above 2^53 lose precision, and GDScript ints are
  signed. This covers `layout_seed`, `art_seeds{}` and the vectors.
- Draws for the parity-relevant modules: splitmix64 seeded by the art seed; uniform = `(x >> 11) * 2^-53`. Python
  `random` is allowed in Blender-only dressing only.
- `derive_<run>.json` carries `art_seeds {stream: "<u64>"}` for the streams of the spec 3.5 table, plus `variance`,
  `terrain`, `fauna.tethys` and `key_landmark.<corp>` (audit row 40). `seed_key` is dropped.
- Vectors (11, incl. u64 max, 2^53+1, negative and non-ASCII keys) + splitmix64 draws: `HANDOFF_PACKAGE/na02/na02_vectors.json`, from `na02/seeds_ref.py`.
  `seeds.py`.

## C4. §12 on Godot captures (D8, audit row 5)

| Check | Blender plates | Godot captures |
|---|---|---|
| 12.1 value band, 12.7 R-VAL / R-SIL / R-DET / R-CALM / R-HUE / R-HOR / R-REP | yes | yes (beauty PNG, no UI) |
| 12.2 landmark ratio, 12.7 R-FOCUS-1, 12.6 room readability / rooms unblocked | yes (Object Index pass) | yes, given the ID capture below |
| 12.3.1 data hash, 12.6 parity, 12.4 (data part), 12.5.1 / 12.5.3 (config) | data only | data only |
| 12.3.2-3 geometry and image hash, 12.5.2 beam profile | yes | no (Blender only in v1) |

The Godot capture contract (NA-04, fixed now so the IDs are in v1):
- `beauty.png`: 8-bit sRGB, without UI.
- `id.png`: unlit, nearest-sampled, R = class.
- `capture.json`: camera pose, resolution, `layout_seed`, run id.

ID classes, matching the Blender pass indices in `HM/hq_values.py`: 0 sky, 1 landmark compound, 2 city, 5 rooms,
6 landmark movers. 3 and 4 are reserved as in `hq_scene.py`.

Golden plates (queue item 3) carry the same three files, so the same check code compares both.

## Needs the build session's answer
1. Do you accept C1-C4? Any field you can't export from today's `CityModel`?
2. Can a cell be split across chunks (C2)?
3. Is the ID capture viewport acceptable in NA-04 scope? The contract only fixes the class table now.
