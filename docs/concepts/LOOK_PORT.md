# LOOK_PORT: making the Godot views match the renders

Owner: art-pass (designer ruling 2026-10-19, DIRECTION_REVIEW "art-pass owns the Godot look").
Scope: the 3D look of the netrun street, route, HQ netrun and city night views. These are the AAA-2 plates in
`golden_plates/INDEX.md`. Game UI, rules and data stay with build.

## 1. Why the old process failed (so we don't repeat it)

| Failure | Fix in this process |
|---|---|
| Path-traced Cycles plates were handed over as a spec of numbers (MATERIAL_SPEC). Godot's rasterizer can't reach some of them: light linking, camera-invisible lights, fog-only beams, real GI bounces and glossy reflections. | A **reachable twin** for every plate (section 3). The designer rules on the gap once. After that, Godot is judged against what it can do. |
| The city geometry lived twice, in Python rules and a GDScript twin, and drifted (seed-1 frontage median 15 BU against 24). | **One geometry source.** Godot generates the scene, and Blender renders from Godot's `plate_inputs` export. Any gap left is then look only. |
| The look was ported in slices against fix lists, round after round over the mailbox. | **Whole frame first**, with one owner per view (art-pass). It's tuned in a tight loop: edit, capture, compare, all inside one session. |
| Approval came from numbers or from screenshots taken at another camera. | The **parity harness** (section 4): same camera, same frame, side by side, with numbers per region. Nothing lands without its sheet. |

## 2. Workspace and integration

- Clone `D:/rc_art/godot_look`, branch `art/look`, cut from `w1-close`. Pushes are disabled, so build fetches from it.
- Before each step: `git fetch origin w1-close` and merge into `art/look`. That's read-only on build's repo.
- To hand over: post `A-NNN: art/look ready @ <sha>` in MAILBOX.md. Build then fetches, runs its full suite and merges.
- Art-pass runs the full test suite, the schema smoke test and content validation before every ready post (CLAUDE.md).
  The look files must not change game behaviour. Any hook game logic reads (highlight states, the city clock, hover) stays
  working, and gets a test wherever we change it.
- Windowed captures only through `python tools/run_windowed.py`. Godot output goes to a file. Run `--import` first.

## 3. The reachable twin (the target Godot is judged against)

For each golden plate, render a Blender twin restricted to features Godot 4.7 Forward+ has:

| Cycles feature in the plate | Twin replacement (the Godot equivalent) |
|---|---|
| Path-traced GI | Eevee with no raytracing: ambient/world light plus the emissive bounce faked by fill lights. In Godot: SDFGI or VoxelGI off/on, decided per view. |
| Glossy reflections on the wet ground | Eevee screen-space reflections plus a reflection probe. In Godot: SSR plus a ReflectionProbe. |
| Volume Scatter box with procedural density | Eevee volumetrics with the same density field baked into a 3D texture. In Godot: FogVolume with a density texture, or volumetric fog. |
| Fog-only lights (light linking to media) | Lights with surface contribution 0 and volumetric contribution 1. In Godot: a light with `light_energy` set low and `light_volumetric_fog_energy` set high, plus cull masks. |
| Fog-only beam spots (1.1-1.3°) | A narrow spot with volumetric energy only, or a cone mesh with an additive fog shader where the volumetric resolution can't hold a 1° cone. |
| `visible_camera = False` lights | Godot lights are never visible to the camera, so nothing changes. |
| Rim lights linked to the compound only | Light `cull_mask` set to a compound layer. |
| Python post (`post_aaa` "real", `hq_post`) | Ported as one CompositorEffect / post shader chain. It's the same math on the same linear HDR, so this part reaches exact. |

Rules:
- The twin uses the same cameras, the same geometry (from `plate_inputs`) and the same post code.
- The designer sees golden | twin side by side once per view and rules on whether the gap is acceptable. If not, art-pass
  finds a Godot technique that closes it (more lights, a baked texture, a custom shader) and updates the twin.
- After that ruling the twin is the parity target. The golden plate stays the north star in reviews (memory:
  parity-against-golden-plates).

## 4. Parity harness

One command per view:

```
# capture (na23_lab / hq_run_lab, windowed) -> r2 twin on the exported plate_inputs -> netrun_art.parity_sheet (3 columns), see section 6
```

1. **Capture Godot**: build's existing capture scene for that view, windowed via run_windowed.py, from the clone. It writes the
   linear EXR when the capture path supports it (sRGB PNG otherwise), plus `plate_inputs/` (city, derive, net, camera).
2. **Render the twin**: Blender headless on the same `plate_inputs` and camera, with the GPU lock, using the Eevee twin mode
   (Cycles on request for the golden reference on that geometry).
3. **Post**: both go through the same post when Godot exports linear. Otherwise the twin's post output is compared with the Godot frame.
4. **Sheet**: golden | twin | Godot, plus a difference heat map, at 1920 wide. Region boxes (sky, skyline, frontage, street, route, landmark)
   come from the shared camera projection.
5. **Numbers per region**: median luma, share under 0.10, share over 0.85, mean hue and saturation of the top 5 % of emissive pixels, and
   fog depth contrast (near vs far skyline luma). Each has a pass band against the twin.
6. Output: `D:/rc_scratch/look_parity/<view>_s<seed>_<sha>/sheet.png` + `values.json`. A review needs both.

Pass = every region inside its band **and** an art-bible §1.2 read of the sheet: media jobs, the hierarchy of light, the fog layers.
Numbers alone never pass (A-020).

## 5. Order of work

| Step | What | Done when |
|---|---|---|
| L0 | Clone, import, survey of the look code and the capture tools (this file, section 6) | survey written below |
| L1 | Harness v0 on the **current** street (seed 1): capture Godot, render the Cycles reference on build's geometry (r2_from_build already does this), sheet + numbers | first sheet exists; it shows today's gap honestly |
| L2 | Twin mode in the street Blender job (Eevee, the limits in section 3); twin sheet to the designer | designer rules on the gap |
| L3 | Post chain port: `post_aaa` "real" as a Godot compositor effect, verified on a fixed linear input to within 1/255 of the Python | exact-match test passes |
| L4 | Street overview pilot on the A2 city (after build's CITY-A2 step 1 and its plate_inputs): materials, lights, fog, reflections tuned in the loop | parity pass on overview + decision |
| L5 | Route view, then HQ (NA-31c; MATERIAL_SPEC addendum A), corp by corp, then the city night view (NA-12 r4) | parity pass per view |

## 6. Godot look code map (survey of `art/look` @ 1f1a429b, 2026-10-19)

**Renderer:** Forward+ (the default; there's no `[rendering]` section). Volumetric fog, SSR and per-light fog energy are all available.
Quality knobs live in CityView3D's `quality` dict and `Settings.city_quality`.

**Everything is built in code.** Each of the four views is a Control page hosting one `CityView3D` (SubViewport plus its own World3D).
No 3D `.tscn` holds any of the look.

| Layer | Files (art-pass owns once P6/P7 have merged) |
|---|---|
| Environment, sun, look blend, AAA exposure | `scripts/city3d/city_view_3d.gd` (`_build_scene` ~L620, `set_look_blend` ~L309 with 0 = cel and 1 = AAA-2, `set_aaa_exposure` L348). **Shared with game code (35 commits since 10-01): claim per change.** |
| Netrun environment, fog volume, sky | `scripts/city3d/netrun_shader_kit.gd` (`configure_environment` ~L399), `netrun_shader_kit_aaa.gd` (post uniforms, world, moon, SSR L72-86) |
| Street / route rig | `scripts/ui/route_rig.gd` (`_apply_street_look` ~L271, `_build_atmosphere` L341, `_apply_fog_density` L404); `scripts/city3d/street_light_rig.gd` (lamps, washes, fog-only glows and beams; caps in `aaa.lights`) |
| Shaders | `shaders/city/*` (surfaces, fx, route, post `city_post` with `aaa_*`), `shaders/street_r2/*`, `shaders/lib/rc_common.gdshaderinc` |
| Tuning | `content/config/city_shaders.tres` (blocks look / building / wet / beam / streak / fog / sky / `aaa`), `street_r2*.tres`; shape guarded by `CityShaderConfigData.validate()` |
| HQ | `scripts/ui/hq_run/hq_run_view.gd` (game signals: don't touch), `scripts/city3d/hq_compound_stage.gd`, `hq_compound_materials.gd`, `landmark_look.gd`, `landmark_materials.gd`; GLBs `assets/city/hq_compounds/*`; the toon shader `tools/art_pipeline/city/hq_compound_toon.gdshader` (**cel, not AAA-2**: replace under NA-31c) |
| City map | `scripts/ui/kit/neon_city.gd` (Band.GRID), `city_backdrop_look.gd`, `shaders/city/city_map_veil`, `city_lights`, `city_live` |

**Off limits (game state or geometry):** `city_plan.gd`, `city_layout_ruler.gd` and `netrun_art_layout_rules.gd` (heights, with Python
twins pinned by `test_layout_parity` / `test_r2_golden`), `street_route_data.gd`, `street_route_view.gd`, `hq_run_view.gd`,
`netrun_session.gd`, `campaign_config*`. Any geometry change goes to build as a B/A entry.

**Tests that pin look values** (keep them green; update with a DECISIONS entry when a value changes on purpose): `test_aaa_street_look`,
`test_city_shaders(_render)`, `test_city_water_look`, `test_na24_dressing`, `test_id_capture`, `test_street_cam_target`,
`test_parity_netrun / _route / _hq_run`, `test_na26_route_port`, `test_na23_route_*`. Headless tests don't render, so look changes also
need a windowed capture and the checks.

**Tools we reuse (don't rebuild):**
- Street capture: `python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://tools/city/na23_lab.tscn -- --seed=1 --shots=<dir> --states=overview,decision --size=1920x1080` (`--export=<dir>` writes plate_inputs; `--cfg.<field>.<key>=<json>` overrides config live, so it's the tuning loop).
- HQ capture: `res://tools/art_pipeline/hq_run/hq_run_lab.tscn -- --out=<dir> --states=run_<corp> --raw`. City: `city_lab --states=<corp>:netrun|city`.
- IdCapture writes beauty / id / depth / capture.json (region masks for the per-region numbers).
- Sheet: `cd tools && python -m netrun_art.parity_sheet --views street_overview,street_decision --seed 1 --out <dir>` (golden on top, Godot
  at the plate camera below, 12 numbers each). **HQ and city aren't wired yet**: art-pass adds them.
- Checks: `python -m netrun_art.checks --images DIR --plates DIR`; drift: `python -m netrun_art.checks.drift`.
- Golden plates: read from art-pass via `git show` (pinned 7772e6ba).

**So the harness in section 4 is:** na23_lab / hq_run_lab capture → parity_sheet, extended with (a) a third column, the reachable twin
rendered by r2 from the same `--export` plate inputs, (b) the region numbers from IdCapture's id.png, (c) the HQ and city views.

## 7. L1 baseline (w1-close @ 1f1a429b, seed 1): `look_parity/L1_baseline/`

Sheets: golden plate on top, Godot at our NetrunCameraRig camera below (`netrun_art.parity_sheet`, run from the capture worktree).

**Finding 1, the root cause: Godot and the plate don't frame the same street.** On the decision view, Godot's camera is 624 BU from
the plate camera and its yaw is off by 90°. Pitch, lens, shift and distance all match, but the layout derives a different street.
So every earlier side by side compared two different shots. That is LOOK_PORT §1 row 2 measured: until Godot exports the
plate_inputs and the twin renders from them, look tuning has no fixed target.

**Finding 2, the look gaps** (art-bible §1.2 read, ranked):
1. Facades are flat, unshaded panels (the cel look's decal windows on solid colour). There's no Principled response and no facade
   or section-spill wash, so the frontage wall that carries the plate never reads.
2. There's no continuous lit frontage at street level. The plate's street is a wall of shop fronts, signs and lamps; Godot shows
   separate towers with gaps into darkness.
3. The wet street has no long reflections of signs and lamps (`blobs_per_mp` 175 against 459; `over_085` 0.0007 against 0.0099).
4. The sky is navy-black. The plate has a magenta haze and layered fog between skyline depths, and Godot's fog reads only as
   puffs around lamps.
5. There are few readable signs and none at hero scale; the emissive hierarchy is missing.
Numbers on the decision view: median 0.122 against 0.141, under_010 0.44 against 0.33, 12.2 and R-VAL-2 fail.

**Order this confirms:** L4 starts by framing the same street (the A2 export plus the twin from it). Then facade materials and
washes (gaps 1-2), reflections (3), fog/sky (4), signs (5), with a parity sheet after each.

### 7b. L1b, after P6 (w1-close @ 8208c5be): `look_parity/L1b_8208c5be/`
- Values are closer (overview median 0.125 against the plate's 0.130, under_010 0.32 against 0.30), but the frame reads murkier. Three or four
  large coloured sky blobs come from the high fog-only lights near the camera ray (B-036 item 2), and they read as fake moons. That is
  an art-bible §1.2 fail: the sky must be a haze field, not light sources.
- The reflections don't show at this camera: blobs/MP is 18 against 676 overview and 94 against 459 decision. The street is in deep
  shadow behind the towers. The camera is still 681 BU off the plate's, so this is not yet a test of P6's wet street.
- 12.2 still fails, and the facades are still flat (gaps 1 and 2 unchanged).
- Inherited from P6 (B-036, now on the art-pass board): P7 (stubs / storefront rooms / no light columns), sky blobs, a fog-top
  band at the roofline, by-eye numbers, bokeh count and saturation, **perf 19.4 / 18.3 ms p95 against the 16.7 ms line** (reflection
  march 40 steps plus 18 lights, about 8 ms). Perf is a hard gate on every art/look ready post.

## 8. L3, post chain parity (art/look @ eca4a7a1, fix 6bf02d88): `look_parity/L3_post/`

Test: one linear HDR frame (Cycles `T_ov_closed_combined.npy`, 960x540, street_b1 render_s1) through both chains at the
plate's exposure 2.4. Plate = `post_aaa` "real" from stage 6 (`netrun_art/post_parity.py`, with emit / volume bloom,
background dim and rain off: Godot has no passes for them). Godot = the real `city_post` aaa branch configured by
`NetrunShaderKitAaa.setup_post` (`netrun_art/post_parity_lab`, a SubViewport, rain and wet reflections off).
Sheet: top plate | Godot; bottom diff x8 with bloom | diff x8 without bloom.

| run | before fix (mean / p99 / max, /255) | after fix |
|---|---|---|
| frame plumbing (no post) | 0.07 / 1 / 1 | same |
| chain without bloom | 9.6 / 13 / 17 | **0.4 / 6 / 8** |
| full chain | 8.8 / 13 / 45 | 2.1 / 14 / 52 (bloom halos 6.1) |
| full + CA | 9.4 / 23 / 166 | 2.8 / 21 / 159 |

Found and fixed (city_post, art/look):
1. **Shadow tint.** Godot divided the tint by its luminance, so shadows turned teal without losing light; the plate
   multiplies by the raw tint (luminance 0.43). Godot's mids were 9.6/255 brighter than the plate on the same input. Now raw.
   The street's `aaa.post.exposure` 0.6 was solved against the old tint: re-run `exposure_solve` before the next sheet.
2. **Grain** was 44 % of the plate's (sum of three uniforms x 1.15 = sd 0.58); now x 2.0 (sd 1.0): 5.9 vs plate 7.6 before the
   luminance weight.

Open (L3b):
3. **Bloom carries 25 % of the plate's energy** (mean lift 0.42 vs 1.70 /255; 4 % vs 16 % of pixels lifted). Cause, confirmed
   by emulation: Godot thresholds after the mip average, so a thin neon tube is averaged below 1.2 before the threshold.
   Per band: b1 100 %, b2 37 %, b3 9 %. The fix is a bright-pass prefilter (threshold at full res, then the mip chain), which
   needs a second pass (CompositorEffect or a bright-pass SubViewport); weigh it against the perf gate (19.4 ms p95 already).
4. **CA**: the plate shifts R/B after the knee by `cq * k` (1.41 k in the corners, nearest pixel); Godot shifts the HDR input
   by a unit direction * k with bilinear taps. Edge-only, max 159/255 on thin lit edges near the frame border. Low priority.
5. Not testable on a still with this harness: emit term in the bloom (`emit * exposure * 0.04`), volume glow, background
   dim/desat (sem pass), rain (procedural in Godot, PIL lines in the plate). They move to L4 with the scene twin.
