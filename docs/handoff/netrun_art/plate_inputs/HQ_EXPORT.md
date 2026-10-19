# HQ plate inputs (HQ-EXPORT, art-pass A-042)

The data art-pass renders its HQ plates from, written by the game from its own objects (nothing re-derived in Python).
Same plan as the street export (`tools/city/na23_lab.gd --export`).

## Run it

```
godot --headless --path . res://tools/netrun_art/hq_export_lab.tscn -- --out=<dir> [--corps=meridian,solace,halcyon,orbital,rebel_cell] [--seed=11] [--size=1920x1080] [--reach=24]
```

No renderer needed. Writes, per corporation, `<dir>/hq_<corp>/`:

| file | what |
|---|---|
| `hq_compound.json` | the compound as placed, the landmark id, the site lot, the ring city round it |
| `run_graph.json` | the rooms as the HQ run page lays them out, the edges, every layout slot |
| `hq_overview_capture.json` | the camera the page framed (`hq_<view>_capture.json`; `overview` is the only HQ view today) |

Code: `scripts/city3d/hq_plate_export.gd` (`HqPlateExport`), lab `tools/netrun_art/hq_export_lab.gd`, test
`tests/unit/test_hq_plate_export.gd`. The page's placement and entry are read through `HqRunView.compound_at()` /
`entry_world()`; the camera is `HqRunView.iso`, the one the page renders with.

## Text and frames

Canonical text as the street export (`NetrunArtExport.canonical`): UTF-8, LF, sorted keys, 1-space indent, floats fixed at
1e-4, `layout_seed` a decimal string. Two runs with the same `--seed` are byte-identical.

- **World** frame = Godot / glTF: Y up, BU = metres. A lot point `(i, j)` is world `((i - ox) * lot_bu, 0, (j - oy) * lot_bu)`.
- **Plan** frame = city.json's: `plan = [world.x, -world.z, world.y]` (x, y on the ground, then height). City `poly` points
  are plan x, y.
- **Transform** (`xf`) = 12 floats: basis x column, y column, z column (3 each), then the origin. `Transform3D(Basis(x, y, z), origin)`.

## hq_compound.json

- `version` 1, `corp`, `landmark` (the corp id: the compound replaces that corp's landmark in the city), `units` "BU",
  `layout_seed`, `lot_bu`.
- `site`: `hq_rect` `[i, j, w, h]` (lots; the HQ lot in city.json `hqs`), `place_lot` `[i, j]` (where the compound origin stands;
  the lot centre, or the manifest's own lot for `rebel_cell`'s canyon), `place_lot_source` "hq_rect" | "manifest", `origin_lot`.
- `compound`: `glb` (res path of the model), `manifest`, `transform` (the placement: identity basis, origin on `place_lot`),
  `plan_origin`, `footprint` = `world_rect` `[x, z, w, d]` (the ground the city's own buildings give way inside),
  `plan_corners`, `height`.
- `parts`: one per mesh node of the glb, sorted by node path: `name`, `tris`, `aabb` `[x, y, z, sx, sy, sz]` (mesh local),
  `local` (transform in the compound frame), `world` (= `compound.transform * local`).
- `ring`: the city round the HQ lot in city.json's own records: `buildings` (`bid`, `cell`, `terr`, `hq`, `key`, `parts`: `poly`,
  `z0`, `h`, `taper`), `streets`, `plazas`, `hqs` (every corp's rect), `origin_lot`, `window` `[i, j, w, h]` (the HQ rect grown
  by `reach_lots`), `reach_lots`. Buildings overlapping the footprint are included; the game hides them under the compound
  (use `compound.footprint`).

## run_graph.json

- `version`, `run`, `corp`, `layers`.
- `rooms`: one per run node, sorted by id: `id`, `layer`, `index`, `kind` (the page's route kind, `rack` is the Central
  Server), `state` (`walked` | `next` | `later` | `cut`), `number` (choice number, 0 = none), `server` (bool), `has_slot`,
  `point` (world), `plan`, `box` = `[minx, y, minz, maxx, y+r, maxz]` world BU, `r` the sticker radius at the page's scale.
  Today's HQ run is the breach: one room, the Central Server.
- `edges`: `{a, b, state}` (`a` empty = the entry), `entry` / `entry_plan`.
- `slots`: every slot of the compound layout whether or not the run uses it: `{layer, slot, point, plan}`; the Central Server is
  `layer 0, slot -1`.

## hq_overview_capture.json

`version`, `kind` "hq", `view`, `corp`, `run`, `look`, `time`, `layout_seed`, `resolution` `[w, h]`, and `camera`:
`projection` ("orthogonal" for the corps' pages), `loc` (the eye), `tgt` (the aim), `plan_loc`, `plan_tgt`, `yaw`, `pitch`
(degrees, `CityIsoCamera`: view direction `(cos yaw cos pitch, -sin pitch, -sin yaw cos pitch)` in world), `dist`,
`ortho_scale` (the frame's width in BU), `fov` (0 for orthographic), `lens` 0.0 (orthographic) and `shift_x` / `shift_y` 0.0
(the page centres the frame on `tgt`, no lens shift), plus a `note`.
