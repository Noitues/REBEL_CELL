# NA-ID: id capture classes, colour rule, capture.json (W1, 2026-10-19)

The game's id capture (PIPELINE_SPEC 12.0). Driver: `IdCapture` (`scripts/city3d/id_capture.gd`); constants: `IdCaptureClasses`.
Street entry: `tools/city/na23_lab.gd`. HQ / landmark / city entry: `tools/netrun_art/id_capture_lab.tscn` (windowed, `tools/run_windowed.py`).

## Files per capture
`beauty.png` (8-bit sRGB, no UI), `id.png` (unlit, nearest-sampled, no UI, no AA / fog / glow / tonemap), `depth.png` (16-bit gray,
linear camera depth in BU x 100, 65535 = sky or beyond), `capture.json`. All four share resolution, viewport, pose and frame.
Two runs of the same seed and pose give byte-identical `id.png` and `depth.png` (checked on street, HQ, landmark and city frames).

## Classes (R of `id.png`)
| R | Class | Where it comes from |
|---|---|---|
| 0 | sky / background | nothing drawn (black clear; the ground layer is hidden in the id pass, so there is no class 4) |
| 1 | landmark compound | every mesh under the CityView3D `landmarks` layer (landmarks, staged HQ compounds); light cones (`lm_beam`) are hidden |
| 2 | city | building prisms (`city_building` `id_mode`), and every other visible mesh outside rooms (roof props, dressing) |
| 3 | link structure | meshes under a node in group `id_link` (none shipped yet: the network is a ground decal) |
| 5 | rooms | `route_room` meshes of the street rig |
| 6 | landmark movers | meshes under a node in group `id_mover` (none shipped yet: the compounds are static) |
Class 4 is reserved and never written. Every pixel R is in {0, 1, 2, 3, 5, 6}.

Group names (`IdCaptureClasses.GROUP_LINK` = `id_link`, `GROUP_MOVER` = `id_mover`): a builder adds the group to a node; the pass
paints every mesh under it. A mover under a landmark stays 6.

## G and B (NA02_FIELDS "id.png encoding"; supersedes the brief's "G = room index")
- Class 5 (rooms): G = the room's 1-based place in the run graph (unique per room), B = its layer.
- Route-building walls: class 2 with B = 1 (the cut surfaces of a room column).
- Occlusion stubs (a building cut or ghosted by the 7.1 rule): class 2, G = 255, B = 0.
- G and B are 0 everywhere else. Bytes are written as exact sRGB values (the unshaded shaders convert them to linear).

## capture.json
Sorted keys, floats rounded to 1e-4, tab-indented. Fields: `version` (1), `resolution` [w, h], `layout_seed` (decimal u64 string),
`run` (run id), `anim_t` (the clock the frame was frozen at, then restored), `camera` (the street rig's `NetrunPose.to_json()`, or for
other frames `position`, `rotation_deg`, `projection`, `size` / `fov`, `near`, `far`), and when given `kind` (street / hq / city),
`view`, `look`, `look_blend`, `corp`, `exempt` {hover_cut, red_seq, flash}.

## Read-only
The pass swaps `material_override` on meshes, hides the ground / network / sky / traffic layers, the fog and the post, and the rig's
extras, and freezes the rig clock; every swap is restored (`tests/unit/test_id_capture.gd` hashes the view before and after). No RNG, save or
world state is read or written.
