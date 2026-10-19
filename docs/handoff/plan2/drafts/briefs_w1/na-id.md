<!-- W1 brief via Message Batches, claude-sonnet-5-5, batch msgbatch_01XJNbnNCPMUUX88XP2A5B47, custom_id brief__naid; status ok; tokens in 17046 cache-write 0 cache-read 33457 out 1883; cost $0.030. DRAFT brief: not yet dispatched. -->
<!-- shortened by a second pass (compress), cost $0.011 -->

# NA-ID: Godot ID capture (beauty.png + id.png + capture.json)

- **Goal:** Godot capture path writing `beauty.png`, `id.png`, `capture.json` per PIPELINE_SPEC 12.0, so section 12 checks (12.2 landmark ratio, R-FOCUS-1, 12.6 room readability) run on Godot frames. `id.png` is unlit, nearest-sampled, no UI. R = class: 0 sky, 1 landmark, 2 city, 3 link structure, 5 rooms, 6 movers (4 reserved). Class 5: G = room index, B = layer, both 1-based.
- **Base / tag:** `<BASE_SHA>` / `<TEMP_TAG>`
- **Agent:** fix-visual (Sonnet), no Opus (no RNG, saves, damage order, determinism). **Depends on:** NA-04, NA-23

## Read first
- `docs/process/agent_rules/common.md`, then the fix-visual area file.
- `docs/handoff/netrun_art/PIPELINE_SPEC.md` 12.0, 12.8.
- `docs/handoff/plan2/drafts/NA02_FIELDS.md` (`layout_seed` u64 decimal string, canonical JSON).
- `HANDOFF_PACKAGE/NA03_NA04_ANSWERS.md` (O-1, O-4, O-6).
- `docs/handoff/plan2/drafts/NA_ID_CLASSES.md` (you write it, Acceptance 7): group-to-class table, room/layer color rule, `capture.json` fields.
- No designer rulings apply. Scope: text 1.0, mouse and keyboard only.

## Files
- `scripts/city3d/id_capture.gd` (new): driver and class-material swap.
- `scripts/city3d/id_capture_classes.gd` (new): class constants, id-color function.
- `scripts/ui/netrun_scene.gd`: hook only if NA-23 left no entry point (smallest change, say so).
- `tools/netrun_art/`: capture entry script; real paths only.
- `tests/test_id_capture.gd` (new), `tests/test_manifest.json`.

## Acceptance
1. One call writes all three files for the current camera; both PNGs share resolution, viewport, pose and frame.
2. `id.png`: unshaded override material per class, no filtering, AA, fog, glow, tonemap, or UI. Every pixel R in {0,1,2,3,5,6}. Fixed seed and pose give byte-identical output on re-run.
3. Classes: sky/background 0; landmark compound 1; city prisms 2; link structure 3; room columns 5; landmark movers 6. Class 4 never written.
4. Class 5: G = room index (1-based), B = layer (1-based). Room column cut surfaces are class 2 with B > 0. G and B are 0 elsewhere. Values come from `run_graph.json` node id `L<layer>N<index>` (index + 1).
5. `capture.json`: camera pose, resolution, `layout_seed` (decimal u64 string), run id, `anim_t`, optional `kind`, `view`, `look`, `look_blend`, `corp`, `exempt`. Sorted keys, floats rounded to 1e-4.
6. Read-only for game state: no RNG, save or world change; camera and materials restored (test: state hash before equals after).
7. Write `docs/handoff/plan2/drafts/NA_ID_CLASSES.md`.
8. 12.2 and R-FOCUS-1 check code reads output unchanged. Smoke capture of a 7-layer fixture run graph shows nonzero class 1, 5, 6 pixel counts, reported in RESULT.

## Tests
- `tests/test_id_capture.gd`, tier `fast`: class-set check on small offscreen render; byte-identity over two runs; state-hash restore; `capture.json` schema.
- No plan under `test_plans/`.
- One windowed capture via `tools/run_windowed.py` to `docs/art_review/NA/NA-ID_beauty_id.jpg`; report `DONE-NO-CAPTURE` if the machine is loaded.

## Not in scope
- Check code, tolerances, golden plates (art-pass).
- Class 4 ground, Blender passes, UI overlay or hover frames.
- Geometry or image hashes.

## Conflicts
- `scripts/ui/netrun_scene.gd` belongs to NA-23..26 in W1; merge after NA-23.
- City shaders and CityView3D: NA-22 lands first and alone. No shader edits; use override materials.

## Report
The RESULT envelope from `docs/process/agent_rules/common.md`.

Q: Which node group names mark link structure (class 3) and landmark movers (class 6) in the NA-04 scene?
Q: Is `anim_t` frozen by the capture driver, or read from the scene clock?
