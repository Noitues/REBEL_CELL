# rc_look: the LOOK-TOOLBOX

Reusable visual building blocks for REBEL_CELL, shared by the UI layers and the 3D renders so every view reads the same
light and colour. Look only: no rules, content ids or save data. Every module has an API class, one shader include,
its numbers in a `.tres`, a lab stage (`lab/look_lab.tscn`), tests in `tests/test_manifest.json` and an entry in
`docs/DECISIONS.md` under LOOK-TOOLBOX. Quality tier and accessibility flags reach a module only through `RcLookQuality`.

## Foundation (modules 1-3)

| API | What |
|---|---|
| `RcLookTokens` (`config/look_tokens.tres`), `tools/sync_tokens.gd` | Palette colours as shader globals `rc_<token>` |
| `shaders/rc_look.gdshaderinc` | tokens, sRGB transfer, luma, saturation, hash / noise / fbm, facet ids (`rcl_` prefix) |
| `RcLookQuality.resolve / of`, `RcLookQualityState`, `config/look_quality.tres` | tier and accessibility flags to a module's settings |
| `RcLookLabStage`, `lab/look_lab.tscn` | lab stages and captures with GPU ms |
| `tools/look_sheet.py` | reference / twin / Godot (+ diff) sheets |

## Module 9: grade (post chain)

One exposure curve for every rendered image: sRGB in, linear x exposure, extended-Reinhard highlight shoulder (white
point W lands on 1), back to sRGB, x tint (clamped), saturation around the display luma.

| API | What |
|---|---|
| `shaders/rc_grade.gdshaderinc`: `rcl_grade(srgb, exposure, white, tint, saturation)`, `rcl_expose`, `rcl_shoulder` | the shader side |
| `RcLookGrade.grade(c, exposure, white, tint, saturation)`, `.grade_preset(c, preset)`, `.shoulder(l, white)` | exact GDScript mirror (tests, contrast checks, previews) |
| `RcLookGrade.preset(name)`, `config/look_grade.tres` (`RcLookGradeConfig`, `RcLookGradePreset`) | presets: `cel` (identity), `aaa2` (the 3D city render: exposure 8, W 3) |
| `RcLookGrade.apply(material, preset, prefix = "grade_")` | fills `<prefix>exposure / white / tint / saturation` |
| lab: `--module=grade` | each preset on grey and neon-token ramps, shader strip over mirror chips |

Call sites: `shaders/arena/combat_backdrop.gdshader` (`graded`), `CombatBackdrop.graded` (numbers from CityConfig
`backdrop_*`, per-corp tint). Next: the UI grades (city_tilt_shift, screen_grey, route_grade) and city_post (announced
to art-pass first).

## Occlusion: the sight rule (`RcLookOcclusion`)

Designer 2026-10-21: hide or flatten every obstacle between the camera and the subject, in netrun and in combat. An
obstacle nearer than the subject's middle, outside the subject's own footprint, gives way when it rises above the
sight line inside the wedge to the subject's sides, or when its screen box covers the subject's (grown by `pad_px`).

| API | What |
|---|---|
| `RcLookOcclusion.sight(project, eye, forward, subject, pad_bu, sight_share, pad_px, half_bu)` | the sight record (camera as a `project` Callable; hold the camera while the record is used) |
| `RcLookOcclusion.hides(record, centre_xz, top)` | whether an obstacle on that ground point with that roof gives way |
| `RcLookOcclusion.screen_box(project, box)` | a world box's screen rect (empty behind the eye) |

Call sites: `BackdropCatalog.view_cut / occludes / projected_box` (combat close-ups, numbers from CityConfig
`backdrop_close_*`). Netrun's moving rig keeps its spec-pinned cone (`OcclusionHelper`, a twin of
`tools/netrun_art/occlusion.py`), which fades the same obstacles (cut / ghost / dissolve) instead of a hard cut.
