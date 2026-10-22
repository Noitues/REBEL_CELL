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

## Module 8: wet and water (`RcLookWet`)

One set of wet-surface and water helpers for the wet street, the wet plinth, the sea, its plane, the shore smears and the seabed, each the exact form of the code it replaces. Built in the lab first; no view migrated yet. The F0 policy stays per view (a designer call; the lab sheet shows the three side by side).

| API | What |
|---|---|
| `shaders/rc_wet.gdshaderinc`: `rcl_fbm3_n(p, oct)` | the puddle noise: normalised octave sum of `rcl_vnoise3` (= netrun_clock's nr_noise3) |
| `rcl_puddle_rough(n, rough_noise, rough_wet)` | roughness dry (`rough_wet.x`) to puddle (`.y`) across the noise range |
| `rcl_fresnel(cos_t, f0)`, `rcl_f0_ior(ior)` | Schlick (power 5); the dielectric F0 of an IOR |
| `rcl_ggx_d(nh, a)`, `rcl_ridge(n, width)`, `rcl_shore(d, len)` | isotropic GGX distribution; caustic / marble veins; the shore fade exp(-d / len) |
| `RcLookWet`: `.preset(name)`, `.puddle_rough / fresnel / f0_ior / ggx_d / ridge / shore` | exact GDScript mirrors (not the noise) |
| `config/look_wet.tres` (`RcLookWetConfig`, `RcLookWetPreset`, `.f0()`) | `street` (F0 0.16 x specular), `plinth` (0.08 x specular), `water` (IOR 1.33, boost 0.2); pinned by test to CityShaderConfigData wet and CityConfig.water_plane |
| lab: `--module=wet` | the three F0 policies: Fresnel strips (shader over mirror) and a wet street reflecting neon bars at street level and from the city camera |

## Module 11: signage and neon (`RcLookSign`)

One set of neon tube, sign stroke, glow and flicker helpers. The forms the game already uses are exact (beam_shaft's white-hot mix, dress_neon's flicker, city_glow's blink and beacon); the tube profile and core are new. Built in the lab first; no view migrated yet. Whether tubes get a white-hot core is the designer's call: the lab sheet shows flat / lightened / hot.

| API | What |
|---|---|
| `shaders/rc_sign.gdshaderinc`: `rcl_gauss(r, sigma)`, `rcl_hot(col, core01, hot)`, `rcl_hot_to(col, core_col, k)` | gaussian profile; mix toward white (beam_shaft, bit glyphs) or toward a core colour; `rcl_neon_core(tube, core_col, tint)` the per-tube core (white tinted 0.15 toward the tube) |
| `rcl_tube_cov(d, half_w, pix)`, `rcl_tube_core(d, core_w)` | a stroke's antialiased coverage; the thin core on its centre line |
| `rcl_flicker(t01, bursts, seed, burst_len, hum_hz, hum_floor)`, `rcl_blink(ph, duty, off)`, `rcl_beacon(ph)` | dress_neon's flicker; city_glow's blink and beacon |
| `RcLookSign`: `.preset(name)`, mirrors above, `.tube_color(preset, col, d)` | exact GDScript mirrors; the colour across a tube under a preset |
| `config/look_sign.tres` (`RcLookSignConfig`, `RcLookSignPreset`) | `flat` (today), `lighten` (0.4 toward the tube's core), `hot` (0.9 on a core 35% of the tube); flicker / blink numbers pinned to dress_neon / city_glow |
| lab: `--module=sign` | the word OPEN in neon under each preset with glow (rcl_light_add) and the 2D bloom; the tube cross-section (shader over mirror) |

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

## Module 13: vinyl sticker look (`RcLookVinyl`)

One include for every vinyl sticker form the game draws, each the exact arithmetic of its source shader so a later
migration is pixel-identical (max 0). **Lab only**: the designer approved this module lab-only (raid redesign pause);
nothing is migrated and no raid screen is wired. The old shaders (`kit/vinyl_sticker`, `kit/sticker_fill`,
`chrome/vinyl_sticker`, `fx/card_sticker_fx`) and their builders are untouched.

| API | What |
|---|---|
| `shaders/rc_vinyl.gdshaderinc` | `rcv_fold_frame`, `rcv_folded_alpha`, `rcv_blurred`; kit: `rcv_kit_rim`, `rcv_kit_gloss_t` / `_spec` / `_gloss`, `rcv_kit_band_dd`, `rcv_kit_flap`, `rcv_kit_dissolve`, `rcv_kit_shadow`, `rcv_kit_composite`; shared: `rcv_foil`, `rcv_band_w`, `rcv_band_mix`, `rcv_grey`; chrome: `rcv_chrome_marker`, `_marker_fill`, `_glitch_keep`, `_glitch`, `_band_dd`; fill: `rcv_holo_fill`, `rcv_gradient_fill`; card: `rcv_card_front`, `_scan_line`, `_gloss`. Every literal is a `const RCV_*` |
| `shaders/rc_vinyl_kit / _chrome / _fill / _card.gdshader` | thin wrappers with the old shaders' uniforms (the stale colour defaults replaced by the real stock values) |
| `RcLookVinyl.kit_material(id, art, body, overrides)`, `.chrome_material(...)`, `.fill_material(...)`, `.card_material(size)` | materials for a stock or verb colour |
| `RcLookVinyl.kit_uniforms(id, body)`, `.chrome_uniforms(id, font_px, top, bottom)`, `.kit_pose(pose)` | what the builders set at rest, and the frozen poses (hover, fold, band, dissolve, disabled, slap) |
| `RcLookVinyl.fold_frame / folded_alpha / kit_rim / gloss_t / spec / kit_gloss / foil / band_mix / kit_band_dd / chrome_band_dd / kit_flap / dissolve_verdict / grey / shadow_alpha / chrome_marker / chrome_marker_fill / glitch_* / holo_fill / card_*` | exact GDScript mirrors (rgb as `Vector3`) |
| `RcLookVinyl.peel_leg`, `.edge_for` | VinylSticker's peel leg and word edge |
| `config/look_vinyl.tres` (`RcLookVinylConfig`, `RcLookVinylPreset`) | every number: the `Shader:` groups equal the include's `RCV_*` constants by name (a test keeps them equal), the `Builder:` groups are what VinylSticker / VerbSticker / StickerSeam set from code, `presets` are `kit_pink / red / yellow / white / ink / kraft / holo` and `chrome_pink / yellow / blue / grey / glitch` |
| lab: `--module=vinyl` | stocks at rest, pink poses on the new wrapper and the old shader, chrome verbs both ways, holo fill, card, and the GDScript mirror beside the shader |

**Proof.** `python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://addons/rc_look/lab/look_lab.tscn --
--module=vinyl --prove --prove-only` renders every stock x pose, the four fold corners, every chrome verb, the holo fill
and the card through the old shader and the new wrapper into SubViewports and prints `vinyl_prove: <case> max <n>`
(8-bit levels; 0 = identical) and, for the mirror, its gap to the shader (no shadow, no dissolve). The hash forms
(dissolve cells, holo sparkles) run on float32 sin on the GPU, so the mirror matches their form, not their pixels.

Numbers it does not own: the motion amplitudes and durations stay in `ui_motion.tres` (`sticker_*`); the palette stays
`palette.gd` (the test pins every preset to it).

### Open rulings (kit vs chrome, found by the inventory; both forms are kept)

1. **Band geometry.** The kit's holographic band runs along (1, 1) (lines `dot(px, n) = c`, `n = (-0.707, 0.707)`, it moves
   down-left); the chrome band runs along x + y = sweep (the other diagonal, it moves down-right). DECISIONS calls both
   "45 degree". `rcv_kit_band_dd` and `rcv_chrome_band_dd` keep each.
2. **Chrome white sweep.** `rcv_chrome_marker_fill` still lays a second, white band (slant 0.45) on the same `sweep`
   uniform as the rainbow band, contradicting the chrome header ("not white") and DECISIONS ("one narrow band").
3. **Disabled look.** Kit: full grey (1.0) and alpha 0.8; chrome: 80 % grey, alpha 1. `Palette.STICKER_DISABLED_GREY`
   says 80 % grey. Config: `kit_disabled_grey` / `kit_disabled_alpha` / `chrome_disabled_grey`.
4. **Extrude and shadow colour.** Kit: `VINYL_EXTRUDE` #09080C for both; chrome: `VINYL_INK` #141118 (shadow at alpha
   0.55). Presets carry each (`shadow_color`).
5. **Pink verb.** The fill is `STICKER_FILL_PINK` #FF60AC to #DE1270 in both; `STICKER_COMMIT` (#FF3DA8) is a third pink
   (HUD name sticker, hot button). The presets use the fill.
6. **Chrome `sweep_width` is written twice** by VerbSticker (draw: 35 % of the size; `run_sweep`: the band half width),
   so a redraw mid-sweep changes the band. The chrome uniform defaults here follow `chrome_uniforms` (the draw value).
7. **Chrome fills have no RED or WHITE.** A verb with a missing art file falls to PINK.
8. **Stale defaults** (replaced in the wrappers): kit `shadow_color` (now VINYL_EXTRUDE), chrome `top/bottom_color`,
   `glitch_b`, `white_color`. Pixels in the game are unchanged: the builders always overwrote them.
9. **Card stand-in.** `card_sticker_fx` is still the played-card seam although the kit sticker (1B) has landed; whether the
   seam switches to the kit look is a designer call.
