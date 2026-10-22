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
`backdrop_*`, per-corp tint); `city_tilt_shift` (`rcl_saturate`), `route_grade`, `screen_grey` (`rcl_luma`). city_post is held
until art-pass clears it (an exact-match preset or a designer sheet).

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

## Module 6: light, spill, glow, bloom (`RcLookLight`)

One falloff family and one light space for every view, so a neon sign reaches as far in the UI as in the 3D city. Light
is added in linear light under a soft ceiling (never in display values); the 2D bloom keys on chroma so paper and white
never bloom, neon does. Built in the lab first; no view migrated yet (city views are claimed with art-pass, Solace first).

| API | What |
|---|---|
| `shaders/rc_light.gdshaderinc`: `rcl_fall_exp(d, reach, k)`, `rcl_fall_pow(d, reach, p)`, `rcl_fall(d, reach, shape, kind)` | falloffs: exp(-(d/r)^k) for glows and halos, (1-d/r)^p for pools and spill |
| `rcl_light_add(base_srgb, light_lin)` | add light: 1 - (1-b) exp(-L/(1-b)); base kept at L = 0, never past white |
| `rcl_bright(lin, threshold, knee, key)` | soft-knee bright pass; key 0 brightest channel (HDR 3D), 1 chroma (2D) |
| `shaders/rc_bloom.gdshader`, `RcLookLight.bloom_material(state)`, `.apply_bloom(mat, state)` | 2D screen bloom (screen mips, bright pass, add); strength by tier (`look_quality.tres` "light") |
| `RcLookLight.preset(name)`, `.at(preset, d)`, `.fall_exp / fall_pow / light_add / bright` | exact GDScript mirror |
| `config/look_light.tres` (`RcLookLightConfig`, `RcLookLightPreset`) | presets `glow`, `halo`, `pool`, `spill` (unit reach: pass distance over the emitter's size); bloom threshold / knee / key / mips / weights |
| lab: `--module=light` | preset strips (shader over mirror chips) and a neon sign scene with spill and bloom beside a paper card |

## Module 7: atmosphere (`RcLookAir`)

One air term for every view, mixed in linear light, and one sky gradient. Built in the lab first; no view migrated yet.

| API | What |
|---|---|
| `shaders/rc_air.gdshaderinc`: `rcl_air(d, y, vec4(start, density, height, high))` | air between the eye and a point: (1 - exp(-max(d - start, 0) density)) x mix(1, high, 1 - exp(-y / height)) |
| `rcl_air_mix(srgb, air_srgb, amount)` | the point seen through that air (linear-light mix) |
| `rcl_sky(e, top, horizon, ground, glow_k, ground_k)` | sky by elevation: top + (horizon - top) exp(-glow_k e); to ground below the horizon |
| `RcLookAir.preset(&"day" / &"night")`, `.amount / mix / sky`, `.apply(material, preset, prefix)` | exact GDScript mirror and material filler |
| `config/look_air.tres` (`RcLookAirConfig`, `RcLookAirPreset`) | per time of day: air colour, start, density, height, high; sky top / horizon / ground, glow_k, ground_k |
| lab: `--module=air` | sky, five skyline rows at 20-480 BU through the air, and a facade strip (shader over mirror chips) |
