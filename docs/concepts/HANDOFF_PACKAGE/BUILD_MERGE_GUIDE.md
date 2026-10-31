# Build merge guide: art's city work

Status as of 2026-10-30. Written from the branch heads, the config files, MAILBOX A-107 to A-114 and DIRECTION_REVIEW (round 42 onward). Where a fact was not found in those sources, it says "unknown". Nothing here was checked out or run.

Clones: `D:/rc_art/godot_lint` (layout chain), `D:/rc_art/godot_look_tide` (look chain, netrun zoom), `D:/rc_art/godot_look_traffic` (traffic variant), `D:/rc_art/godot_jackin` (jack-in prewarm).

## 1. Merge order

Merge in this order. Heads are from `git log -1 --oneline <branch>`.

1. **art/city-lint**, `78fbe945`. Adds CityLint: a pure audit of the layout (18 rules), a feed, a 25-seed sweep and a report runner (A-110, item 1). Full suite: unknown for this branch alone.
2. **art/city-layout-p0**, `6ea2d710`. Corridors in metres, street hygiene (sea, park, dead ends, connectivity), Site streets, dense-zone fill (A-110, items 2 to 4). Full suite: unknown for this branch alone.
3. **art/city-layout-p1**, `8a817aad`. Street hierarchy and frontage merge, height field with low-rise steering, waterfront and river band, shore apron, ramp ends (A-110, items 5 to 7; A-107, A-108). Full suite: unknown for this branch alone.
4. **art/city-test-fixes**, `a76b09b6`. Explicit integer comparators for the lot-coordinate sorts. Full suite green: the r42 run on `bbdc20ae` includes this merge (4070 tests, 0 failing).
5. **art/tide-r41**, `6cb8bd29`. Bay apron dressing, lit park paths and lamps, low-rise shape variety, lone apron buildings, edge step-down, sky-car dots hidden at plan zoom. Full suite: unknown on its own; included in the r42 run.
6. **art/tide-r42**, `bbdc20ae`. Schema smoke pins the 90 m highway corridor. Full suite: **4070 tests, 0 failing, 117 pending, PASSED** (4 shards). Schema smoke and validate_content pass.
7. **art/tide-r43**, `e2c9976c`. Park ground sink, deck-lot lawn dressing, raid-mode grade. Full suite: **4080 tests, 0 failing, 117 pending, PASSED**. Schema smoke and validate_content pass (3172 resources).
8. **art/tide-traffic-corp**, `5df3d8ae`, in `D:/rc_art/godot_look_traffic`. Corp-colour traffic variant, behind `traffic_corp_colour_on` (default off). The designer adopted it (2026-10-30). The review says it joins the chain after art/tide-r43. Base of this branch: unknown. Full suite: unknown; targeted tests only (56, 0 failing).
9. **art/jackin-prewarm**, `903853d4`, in `D:/rc_art/godot_jackin`. Based on game-v2 `b09f9b9d`, not on the city chain. Merge it after steps 1 to 7 (A-113, A-114). Full suite: unknown; 6 new tests in `test_city_prewarm.gd`; 15 failures already exist on game-v2 (section 6).

Not in the merge order:
- **art/netrun-zoom**, `f318f476`, in `D:/rc_art/godot_look_tide`, off art/tide-r43. Pending designer decisions (section 7). Targeted tests: 289, 0 failing. Full suite: not run.
- **art/zoom-lod-sheets**, `38f75b23`. Lab tool only. Do not merge.

## 2. Config switches

Defaults are read from the branch heads with `git show`. Switches are in `CityConfig` (`scripts/city3d/city_config.gd`) unless stated.

| Name | File | Default | What turning it on does |
|---|---|---|---|
| `art_look` (`CityView3D.art_look`, a var, not a config export) | `scripts/city3d/city_view_3d.gd:62` | `true` | Enables the art look in the city view: corp colour, the r6 look, park and apron dressing, the bay. `route_rig.gd:79` sets it `false` (section 3). |
| `r6_look` | `city_config.gd:1027` | `true` | The cel and ink look (gated together with `art_look` and `corp_color_on`). |
| `zoom_rules_on` | `city_config.gd:1467` (netrun-zoom) | `false` | Turns on the netrun zoom rules (per-band LOD). Off: no zoom node, all zoom uniforms 0. Only on art/netrun-zoom. |
| `zoom_layers_on` | `city_config.gd:1399` (netrun-zoom) | `false` | Turns on the per-zoom layers (dressing node and shader switch). Ignored while `zoom_rules_on` is on. Only on art/netrun-zoom. |
| `traffic_corp_colour_on` | `godot_look_traffic` `city_config.gd:717` | `false` | Corp-coloured traffic: roads go neutral grey, cars take the corp hue, seeded traffic (platoons, speed variance), decks at 3.5x street speed, light-streak swap above `traffic_streak_px_per_s`. Only on art/tide-traffic-corp. |
| `raid_grade_building` | `scripts/data/tide_look_data.gd` (values in `content/config/tide_look.tres`) | `Vector2(0.62, 0.72)` | Raid-mode brightness and saturation for buildings. Applied during FORECAST, REVEAL, RESPONSE, PLAYOUT (`TideRaidGrade`). |
| `raid_grade_neon` | same | `Vector2(0.48, 0.38)` | Same, for neon. |
| `raid_grade_ground` | same | `Vector2(0.86, 0.88)` | Same, for ground. |
| `raid_grade_water` | same | `Vector2(0.86, 0.92)` | Same, for water. |
| `raid_grade_haze` / `raid_grade_secs` | same | `0.45` / `0.35` | Neon haze keep, and the tween time of the grade. |
| `park_ground_sink_on` | `city_config.gd:714` | `true` | Lowers the asphalt under park lawn lots so lawns cover it (no grey diamonds). Margin: `park_ground_sink_margin` 0.02. |
| `deck_street_dress_on` | `city_config.gd:715` | `true` | Dresses deck street lots as lawn, as the bare lots round them. |

Raid grade on/off: unknown. No separate switch was found; the grade follows the raid phase rule.

## 3. `CityView3D.art_look`

`route_rig.gd:79` sets `view.art_look = false` (comment: "round 23: the raid city's art districts are not the street netrun's look"). This keeps the city look out of the netrun. The netrun-zoom branch leaves that line unchanged.

Build must keep it `false` until the designer decides the netrun look. The ruling of 2026-10-30 (ART CALL 46) says the netrun and HQ share the city's cel look, zoomed in. Nothing in the art branches flips the switch yet. If build adopts the city look in the netrun, it must set `view.art_look = true` in route_rig.gd and check the netrun zoom. Whether the designer wants that flip now: unknown.

## 4. Shaders and classes changed or added

Classes are in `scripts/`. Shader paths are in `shaders/`.

- `CityLint` (`scripts/core/city_lint.gd`): pure layout audit, 18 rules, 25-seed sweep.
- `CityLintReport` and `CityLintSweep` (`scripts/core/`): report and sweep runners.
- `CityLowRise` (`scripts/core/city_low_rise.gd`): low-rise steering for the height field.
- `CityA2Corridors` (`scripts/city3d/city_a2_corridors.gd`): rail, station, ramp and wall-highway corridors in metres.
- `CityA2Streets` (`scripts/city3d/city_a2_streets.gd`): street hygiene and the street grid.
- `CityA2Builder`, `CityLintFeed`, `CityNeonKit`, `CitySolacePark`: modified by the layout chain.
- `CityParkKit.ground_sink` and `CityMeshKit.ground_mesh_on` (sink map): park ground sink.
- `CityApronDress` (`scripts/city3d/city_apron_dress.gd`): apron dressing and `live_streets`.
- `TideRaidGrade` (`scripts/ui/raid/tide_raid_grade.gd`): raid-mode grade rule, called from hq_scene.
- `CityTrafficCorp` and `CityTrafficGen` (`scripts/city3d/`, traffic branch): corp traffic and seeded traffic.
- `CityChunkGeometry`, `CityPrewarm`, `MeshBlueprint`, `ScenePrewarm` (`scripts/city3d/`, `scripts/ui/`, jackin branch): worker-thread builds and netrun scene preload.
- Netrun-zoom only: `CityZoomRules`, `CityZoomLayers`, `CityZoomStreet`, `CityZoomPlan`, `CityZoomRoad`, `CityZoomDress`, `CityZoomHero`, `CityZoomOcclude`, `CityZoomSky`, `CityZoomFrame`, `CityStreetPlan` (`scripts/city3d/city_zoom_*.gd`, `city_street_plan.gd`).
- Shaders: `shaders/city/city_post.gdshader` (raid grade classes each pixel by roughness tag and dims it). Netrun-zoom only: `shaders/city/city_zoom_layer.gdshader`, `shaders/city/city_zoom_haze.gdshader`, `shaders/city/city_zr_road.gdshader`.
- Traffic branch: the shader diff is against an unverified base, so the exact set is unknown. Run `git diff` against the branch base to list it.

## 5. Known conflicts with game-v2 (A-114)

- Conflicts are expected in `city_view_3d.gd` and `city_water.gd`.
- The mesh functions now return blueprints, behind wrappers that keep the old names.
- Chunk, ground and park builders must go through `CityChunkGeometry`.
- The city chain is based on an older main, not game-v2. Merge the chain (steps 1 to 7) first, then rebase the jackin branch on top, or tell art which base to use.
- The chain touches `city_view_3d.gd`, `city_water.gd`, layout code, shaders and config (A-113).
- Build's data change A-112 (Solace-only names) is not in these branches. Renames in game data are build's work.

## 6. Tests

Run the full gate from the clone, not the fast tier:

- Full suite: `python tools/run_tests.py` (4 shards; `-j N` for N workers). See `docs/TEST_SUITE.md`.
- Schema smoke: `godot --headless --path . -s tools/schema_smoke_test.gd`
- Content validation: `godot --headless --path . -s tools/validate_content.gd`
- Single script: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`. Do not use `-gtest=`; it ran the whole suite in an art session.

Do not pipe Godot output and do not run `python -`.

Pre-existing game-v2 failures (A-114, on unmodified game-v2, 15 total):
- `test_anim4b_run_drag_drop`: 8
- `test_anim6_screen_motion`: 2
- 1 each: `test_b5_netrun_pages`, `test_pt_p1_loot_clicks`, `test_anim_r1_campaign`, `test_anim_r5_netrun`, `test_b3_raid_map_route`

Build owns these.

New tests on the chain: `test_city_lint`, `test_city_lint_sweep`, `test_city_layout_p0`, `test_city_layout_p1`, `test_city_lawn_ground`, `test_tide_raid_grade`, `test_city_prewarm`. Confirm each is in `tests/test_manifest.json` before the full run (`test_suite_integrity.gd` checks this).

## 7. Designer approvals pending before merge

- **final/ replacement:** `final_proposed/` (7 beats on r42, with r43 as the head) waits for the designer's review. `final/` is unchanged. The designer has not yet approved the replacement.
- **Golden plates:** the designer has not approved the city look as a plate set. The side-by-sides are not a parity claim. Art-pass accepted the r43 visuals; designer approval: unknown.
- **Netrun zoom:** round 2 fails the squint against street_overview. The zoom rules and the per-element LOD sheets (`netrun_cel/zoom_rules/lod_sheets/`) await review. The stage-street proposal (round 3) awaits the designer. The netrun camera ruling is street level (2026-10-30). Whether the designer accepts the stage-street rule: unknown.
- **Traffic:** the designer adopted corp-colour traffic and asked for tunes; the tunes are done (follow-up 3, `5df3d8ae`, GIFs in ab01a063). The designer's look at the follow-up 3 GIFs: unknown.

## 8. Open items

- The netrun look: the designer decided the netrun uses the city's cel look. Whether `art_look` flips for the netrun is build's call (section 3).
- The tall teal apron tower, the pale slab at the park and core edge, and the glass cluster are Site buildings. They need a build decision (r42, r43 notes).
- The layout P2 list (CityLint items not yet built) is open. The north park interior is featureless at plan zoom.
- Netrun zoom: bands and elements the code does not yet build show as "not yet built" in the LOD sheets.
- The Halcyon "win" dossier reads as a defeat, and the Solace win-screen numbers are placeholders. These are game data (build).
- Solace names: the data ids (hauler, courier, sink_the_cargo_logs) are unchanged; renaming them is build's job (A-112).
- Full-suite status of steps 1, 2, 3, 5, 8 and 9 is unknown. Run the full gate before merge.
- Jack-in: the 3.7 s frame-1 scene instantiate and the 1.5 s `CityView3D._on_model` remain on the main thread (A-114).

## Answers to the unknowns above (art-pass, 2026-10-30)
- **Suite status per branch:**
  - art/city-lint, art/city-layout-p0, art/city-layout-p1 and art/tide-r41 are contained in art/tide-r42 by merge. r42 passed the full suite with 4,070 tests and 0 failing.
  - art/tide-r43 (e2c9976c) passed the full suite with 4,080 tests and 0 failing.
  - The jack-in branch has its own full run, in A-114: 15 pre-existing game-v2 failures plus 1 of its own test that was fixed afterwards.
  - The traffic branch had targeted tests only: 56 tests, 0 failing. Run the full gate at merge.
- **Traffic branch base:** art/tide-r43.
- **Designer approvals:**
  - Corp-colour traffic is adopted (2026-10-30).
  - The r43 look and the replacement of `final/` are not yet approved. The designer has seen final_proposed, but has not signed it off.
- **Raid grade switch:** it has no separate config switch. `TideRaidGrade` turns it on for FORECAST, REVEAL, RESPONSE and PLAYOUT, and off for PLAN, AFTERMATH and HQ_STEP. The look values are in `TideLookData` (`raid_grade_*`).
