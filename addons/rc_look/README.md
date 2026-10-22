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
## Modules 4 / 5: toon bands and ink (`RcLookToon`, `RcLookInk`)

One set of cel-band and ink helpers for the props / busts / aircraft (toon_ink, toon_ink_hull) and the city (city_building, landmark_toon, hq_compound_toon, city_post). Each helper is the exact form of the code it replaces, so a view moves onto it with identical pixels. Built in the lab first; no view migrated yet.

| API | What |
|---|---|
| `shaders/rc_toon.gdshaderinc`: `rcl_band(x, lo, hi)` | 0 shadow, 1 mid, 2 lit (toon_band_index) |
| `rcl_band_shade(x, lo, hi, mid, low)`, `rcl_band_tint(shade, low, shadow_tint)` | the band's share of full light, and its tint (shadow_tint in shadow to white when lit) |
| `rcl_band_ramp(x, lo, hi, c_low, c_mid, c_lit)`, `rcl_rim(n, v, p)` | a three-colour ramp by band; the fresnel rim (1 - n . v)^p |
| `shaders/rc_ink.gdshaderinc`: `rcl_hull_width(width_px, wobble, n01)`, `rcl_hull_clip(clip, n_clip, width_px, viewport)` | the hull's wobbling width; the vertex grown width_px px outward on screen |
| `rcl_ink_normal_edge(c0, cn, thr)`, `rcl_ink_depth_thr(edge, ortho, ortho_ref)`, `rcl_ink_depth_edge(zc, zn, thr)` | the post pass's normal / material edge and its depth edge (threshold scaled with the ortho size) |
| `RcLookToon` / `RcLookInk`: `.preset(name)`, `.band / band_shade / band_tint / rim`, `.hull_width / hull_clip / normal_edge / depth_thr / depth_edge` | exact GDScript mirrors |
| `config/look_toon.tres` (`RcLookToonConfig`, `RcLookToonPreset`) | `props` (0.12 / 0.55, the kit) and `city` (0.118 / 0.363, CityConfig.ramp_edges): two named band sets, pinned by test |
| `config/look_ink.tres` (`RcLookInkConfig`, `RcLookInkPreset`) | `hull` (2.5 px, wobble 0.35), `post` (1 px, edges 0.42 / 1.2), `post_backdrop` (edges 0.8 / 3.0, no wobble); ortho_ref 300; pinned by test |
| lab: `--module=toon` | per band set: the band strip (shader over mirror chips) and two overlapping spheres inked by the post pass and by the hull |

## Module 12: grease pencil

Wax on glass for plans and threats (ART_BIBLE §1.2). The engine stays in `scripts/ui/kit/materials/` (36 views use
it); the module adds the face, the look numbers, the hand and the world anchor.

**Draw a mark or a word** (the only ways pencil reaches the screen):

| API | Use |
|---|---|
| `PencilSet.under(host)` then `begin()`, `stroke(key, strokes, ink, progress, wiped, dashed, seed, hero)`, `circle(key, centre, radii, ink, seed, progress, hero)`, `word(key, text, centre, step, ink, k, shown_to, shown_from, tilt, hero)`, `end()` | a view's keyed pencil pass; marks not laid again wipe off |
| `PencilSet.show_on(host, strokes, ink, seed)` | one mark on a view that draws in `_draw` |
| `GreasePencilMark` (`hero`, `ink`, `dashed`, `seed`, `progress`, `wiped_share`, `write_on()`, `wipe()`) | one mark, written on in writing order |
| `GreasePencilWord` (`text`, `ink`, `text_step`, `hero`, `shown_to`, `shown_from`) | **the one word path**: RC Wax letters as wax strokes on a GreasePencilMark |
| `HandMarks.show_x / show_loop / clear`, `x_strokes`, `loop_strokes` | a remove X (red) and an upgrade loop (yellow) |

**Inks.** `GreasePencilMark.Ink.PLAN` yellow (`Palette.PENCIL_PLAN`), `THREAT` red, `PLAN_NETRUN` orange
(`Palette.PENCIL_PLAN_NETRUN`: the netrun plan, the HQ page's plan pencil; art-pass ruling d). Pencil never spills
light (`UiSpillShadows`): wax casts its crisp under-shadow and never glows.

**Weights.** `GreasePencilMark.stroke_width(hero)`: a mark 10 px, a hero mark 16 px at 1080p (the aim arc and loop, a
TARGET ring), scaled with the text size, one screen width whatever the map's zoom. A hero mark's wax is dry (edge
grain, core breaks) and lifts into a few seeded pressure gaps. A hero word (`GreasePencilWord.hero`: the kit's HIT IT, a
TARGET) is fat wax (0.27 em, was 0.20) with a lighter core (`GreasePencilMark.core_light`).

**Clear of the HUD.** The aim's spec takes `avoid` (the HUD's words, global px; `CombatScene.hud_word_rects()`):
`AimLinePencil.clear_shaft` tries other bows for one that crosses none, else starts the shaft past its last crossing.
The grid TARGET word is placed by the pure `CityMapOverlay.target_word_tries` / `pick_word_spot` and kept wholly inside
the map's open part.

**The hand** (`PencilShapes`, seeded KitNoise hashes, never `randf` / `randi`):
`hand_path(pts, seed, w)` (sideways wobble, ends kept), `hand_line(from, to, seed, w)` (bow, overshoot, hooked
downstroke), `hand_route(pts, seed, w)` (rounded corners with a run-on), `hand_circle(centre, radii, seed)` (egg,
jitter, seeded tilt, overlap tail), `arrow(shaft, head, seed)`, `bezier`, `trim`, `snap_to`.

**Pressure.** `RcPencilPressure.factor(d, length, width, seed)`: lands light, swells, lifts off in a flick (lengths in
stroke widths; a short flick stays pressed; `gap_every` / `gap_len` / `gap_width`: pressure gaps, `gap_at`). Mark,
hero and word profiles in the look.

**The face.** RC Wax (`assets/fonts/RcWax-Regular.ttf`, `Palette.FONT_PENCIL`, `Palette.pencil()`) and its stroke twin
(`pencil/rc_wax_strokes.json`, read by `RcWaxFont.layout(text, px, seed, look)`), both built from one stroke source by
`python addons/rc_look/tools/build_wax_font.py` (`--check`: exit 1 when the committed outputs are stale). Caps, digits,
punctuation; lowercase is small caps. Measuring with `Palette.pencil()` matches the strokes' advances. The capitals are
hand-built marker letters (`GLYPHS`, with `F` flourishes that run on from a stroke and stay out of the advance, and an
optional per-glyph overhang), drawn by a broad nib (an ellipse at `NIB_DEG` 25, `NIB_CONTRAST` 0.7, stamped and hulled:
smooth thick / thin, no caps or seams), with a bold start and a tapered end. In words (`RcWaxFont.layout`) each first
letter is `word_initial_scale` bigger with no advance change, and each letter slips, drops and turns by the word's
hash (`word_x_jitter`, `word_baseline_jitter`, `word_letter_turn`); the engine strokes use the nib through
`RcPencilPressure.nib` (`word_nib_*`), a box-cap start and a smooth fade at the end (`word_tail_*`).

**Lab.** `python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://addons/rc_look/lab/look_lab.tscn --
--module=pencil --shots=<dir> --window=1920x1080` (the shots render the vectors at 1080p).

**World anchor.** `RcPencilAnchor.screen_point(projector, p)`, `screen_path`, `px_per_unit`, `to_canvas`: a projector is
a `Camera3D` or a `Callable (Vector3) -> Vector2` (a view's own projection); behind the camera is `Vector2.INF`.
`RcPencilWorldAnchor` (a Node2D) pins its children to a world point each frame and hides behind the camera.

**Numbers.** `config/pencil_look.tres` (`RcPencilLook`): widths, the three pressure profiles, the hand (wobble, bow,
overshoot, hook, corners, loop jitter / egg / overlap / tail / tilt), the word (width per em, letter turn, baseline,
size, wobble, hero width, core light), the hero grain and the knot density. The engine's older locked numbers (dropouts, shadow offset, sheen, alpha) stay constants in
`GreasePencilMark`.

**Quality.** One tier: the pencil is cheap 2D (lab: 0.3-0.5 ms GPU for the whole stage at 1080p). Reduce effects and
headless show every write-on and wipe at its end state and stop the glint (Motion).

**Lab.** `python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://addons/rc_look/lab/look_lab.tscn --
--module=pencil --shots=<dir> --times=night,day --tiers=2 --flags=none,re,rm`

**Tests.** `tests/unit/test_look12_pencil.gd` (fast), `test_b1b_wax_pencil.gd`, `test_art1_material_kit.gd`.

## Module 15: decrypted holo (`RcLookHolo`)

A translucent tinted glass over the blurred screen, 4 px scanlines, slow scan bands, an edge-only RGB split and a cracked
corp seal (ART_BIBLE §1.2: hacked corp intel; never anything the Cell owns).

| API | What |
|---|---|
| `RcLookHolo.material(pass)` | a `ShaderMaterial` for `GLASS` (under the words) or `OVER` (scanlines and bands above them) |
| `RcLookHolo.apply(mat, size, tint, deep, state, body_k, overrides)` | fills a material: the config, the quality rules for `state`, the panel rect and the corp tint |
| `RcLookHolo.settings(state, body_k)` | every value as a Dictionary (pure), plus `backing_alpha` for the panel's local backdrop |
| `RcLookHolo.bleed_px(state)` | how far past its rect the glass control must draw (split and glow) |
| `RcLookHolo.draw_seal(ci, centre, radius, tint, crack_color, crest, seed)` | the cracked seal on a canvas item |
| `RcLookHolo.crack(centre, radius, seed)` | the fracture's points (deterministic: a hash of the seed, never RNG) |

Numbers: `config/look_holo.tres` (`RcLookHoloConfig`) and the `holo` module in `config/look_quality.tres`.
Rules: low tier drops the split and the screen blur; reduce motion freezes the bands (still drawn); reduce effects drops the
split and the roll; high contrast is opaque black glass with no effects. The game's call site is `DecryptedHoloPanel`.

Lab: `--module=holo` (see `lab/look_lab.gd`). Sheet: `tools/look_sheet.py --module holo ...`.
