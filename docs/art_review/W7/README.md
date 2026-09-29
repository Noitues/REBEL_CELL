# W7 — The city (branch `art/w7-city`)

ART_BIBLE §9 (all), §2 CITY, §3.6, §8 T0, §10.6, §12, §13. Presentation only: no rule, content
value or save format changed. One additive data schema (`CityLookData`, logged below).

## Review images

| File | What it shows |
|---|---|
| `lighting_before_after.jpg` | Title, HQ, Grid: W10 baseline vs after (the W10 harness). Last row: the HQ window city in the city lab, `--legacy` (W7 off) vs on: per-ink glow, haze bands, wet streets, rim light, the HQ grade. |
| `heat_states.jpg` | The net city (Solace) at COOL / NOTICED (searchlights) / FLAGGED (patrol drones, red/blue rim on corp buildings) / HUNTED (−25 % saturation, heavier haze). |
| `territory_before_after.jpg` | Three claimed Sites: the old flat lasting wash (the critique's khaki) vs CELL_TURF hatch on the claimed roofs, spray tags, light leaking into the haze. |
| `grade_contexts.jpg` | The same district in the title, HQ, net and combat grades. (Combat is shown with its veil off: the lab passes `--dim=0`.) |
| `map_mode.jpg` | Mock map nodes over the city, map mode off vs `set_map_mode(true)` (city −40 % and blurred; nodes untouched). |
| `placeholder_before_after.jpg` | A view whose bake hasn't landed: the old flat lifted blocks vs skyline masses at the placement's real heights with lit windows, in the grade. Bottom row: the real title screen caught before its bake, baseline vs after. |
| `life_strip.jpg` | Six frames 0.7 s apart (FLAGGED, two claims): aircraft with blinkers, patrol drones, billboards looping in corp hue + pattern, window lights. |
| `reduce_effects.jpg` | FLAGGED with claims and a calm panel, effects on vs reduce effects (no aircraft, drones, rim flicker or sweep; billboards on their first frame). The calm panel shows the dim + desaturation behind text. |
| `perf.md` | Frame time before/after on title, grid and combat at 1080p, and the quality tiers. |

Captures: `tools/design_lab/city_lab.tscn` (new; options in its header) through
`tools/run_windowed.py`, and `tools/visual_qa/capture_pack.py` for the screens.

## What changed (files)

New:
- `scripts/ui/kit/city_atmosphere.gd` (`CityAtmosphere`): the per-city director; public API below.
- `scripts/ui/kit/city_state.gd` (`CityState`), `city_grade.gd` (`CityGrade`): pure state and grade maths.
- `scripts/ui/kit/city_life.gd` (`CityLife`): T0 life, a pure `frame()` draw list; billboards on a cached sub-layer.
- `scripts/ui/kit/city_turf.gd` (`CityTurf`): hatch + spray tags on claimed buildings.
- `scripts/ui/kit/city_silhouette.gd` (`CitySilhouette`): the §9.4 pre-render.
- `scripts/ui/kit/city_palette.gd` (`CityPalette`): city-only tones, each citing §9.
- `scripts/data/city_look_data.gd` (`CityLookData`) + `content/config/city_look.tres`: every number.
- `tools/design_lab/city_lab.gd/.tscn`, `city_perf.gd`, `legacy_silhouette.gd` (review only).
- `tests/unit/test_art_w7_city.gd` (12 tests, full tier).

Changed:
- `shaders/city_live.gdshader`: the lit composite (glow per ink, reflections, haze, rim, searchlights, leaks, grade, map dim/blur, calm zones), behind a `lit` switch; off = the old pass exactly.
- `shaders/city_lights.gdshader`: T0 period floor, calm zones hide the blinking lights.
- `shaders/influence_reveal.gdshader`: the lasting wash is a hatch (`hatch_px`, `wash_gain`).
- `scripts/ui/kit/neon_city.gd`: hooks only — `atmosphere()` (+ `_ready` line), `_draw_silhouette` delegates, pan holds under reduce motion, 23 literal colours → tokens, `SIGN_FONT_PX`, `INFLUENCE_GROUND_TINT` 0.16 → 0.06.
- `scripts/ui/kit/city_bake_cache.gd`: the freed-painter fix (`_alive_painter`, 5 call sites).
- `scripts/ui/kit/wireframe_background.gd`: camera eases cut under reduce motion; forwarding API.
- `scripts/ui/kit/cyberdeck_background.gd`: `heat_band` goes to the city (the old window sweep is replaced by §9.3's searchlights); forwarding API.
- `tools/schema_smoke_test.gd` (`_w7`), `tools/visual_qa/lint_baseline.json`, `tests/test_manifest.json`.

## Public API

```
NeonCity.atmosphere() -> CityAtmosphere        # made on first use; never on a bake painter
CityAtmosphere:
  set_context(&"title" | &"hq" | &"net" | &"combat")   # default: net city → net, panning → title, else hq
  set_heat(heat: int)                                  # band via Palette.heat_band (config MAJOR levels)
  set_heat_band(band: int)
  set_campaign_progress(progress: float, corp_id: StringName)  # lean ≤ 20 % to the corp hue
  set_territory(claims: PackedVector2Array)            # claimed Sites' grid lots
  set_map_mode(on: bool)                               # §9.5: −40 % + blur
  set_calm_zones(rects: Array[Rect2])                  # canvas rects of text panels
  set_calm_controls(controls: Array[Control])          # followed while visible
  follow_campaign(on: bool)                            # heat/progress/territory from the campaign unless set (default on)
  static quality: int  (-1 = config default, 0..2)     static enabled: bool (review "before")
CyberdeckBackground / WireframeBackground: set_context, set_heat, set_campaign_progress,
  set_territory, set_map_mode, set_calm_controls (forward to the city)
```

## ART_BIBLE §14 checklist (what W7 touched)

| Item | Result |
|---|---|
| §3 tokens only, no literals in views | **Pass**: neon_city 23 → 0 literal colours; new tones in `CityPalette` (a token file; see requests). |
| Materials not mixed | **Pass**: all CITY; the calm zones keep GLASS readable over it. |
| Focal order / primary / states / text scale / pad | n/a (backdrop). |
| Contrast behind text | **Pass (mechanism)**: calm zones dim 45 % (+30 % under high contrast) and desaturate 75 %; screens must register their panels (call sites below). |
| Greyscale | **Pass**: territory reads by hatch + tags, corp billboards by CorpPattern, patrols by shape. |
| Motion/VFX within tier; reduce effects end states | **Pass**: every loop ≥ 3 s (validated), rim flicker 0.8 Hz ≤ 1 Hz, no flashes; reduce effects = static end state (tested). |
| No placeholder city | **Pass**: silhouette masses with windows, graded, fading to the bake. |
| Review stills | **Pass** (this folder). |

## Decisions (one line each)

1. HDR 2D is off in `project.godot`; not flipped. Lighting is shader-side in the city's own composite (`city_live`), no screen copy, so glass blur over it samples the graded city (§9.1, §13).
2. The per-context grade is parametric (contrast, saturation, warmth, lift, dim, corp lean) rather than a LUT texture: same result, numbers in config (§9.1).
3. A context's `dim` is the total darkening it asks for; the screen's own `NeonCity.dim` veil counts toward it, so combat's 0.55 veil is not darkened twice (§9.1).
4. Campaign progress, when not passed: the claimed + cleared weight of the corp's Sites over its Site count (from `CityInfluence`) (§9.3).
5. Cities that follow the campaign read heat, territory and progress from it (read only, like the influence poll), so the city reacts before screens add call sites; explicit setters win (§9.3, signal up/call down).
6. Territory: the old flat wash became a hatch at 40 % (`wash_gain`), claimed roofs get their own hatch and 3 spray tags per Site, ground lean 0.16 → 0.06 (§9.3, critique gifs/16).
7. Window lights: the existing GPU blink layer is the "window toggle", floored at 3 s in the shader; `beacon_blink`'s 1.6 s is floored too (T0 §8). ui_motion.tres untouched.
8. Life timings live in `city_look.tres`, not ui_motion (they are T0 loops, not eased motions; one place for the city's tuning) (§8).
9. Reduce effects: aircraft and drones are not drawn, billboards hold frame 0, searchlights stand still, rim flicker off (§8, §12).
10. HQ's old window searchlight sweep (fast, across the glass) is replaced by §9.3's district searchlights.
11. `crt_overlay` was not swapped in: the city's scanlines live in the same pass as its lighting; splitting would cost a second full-screen pass (§13).
12. Silhouette colours use the context grade (mode 2 of `city_live`) (§9.4).
13. Default quality tier 2; tier 0/1 exist for §13 (see perf.md); Deck default tier 1 recommended.
14. `city_bake_cache.gd:183`: the city branch does **not** touch `_stop`; applied the minimal fix.

## Couldn't do / known gaps

- The screens don't call the API yet (not my files): context/map mode/calm zones need the call sites below. Until then: contexts default by city type, heat/territory/progress follow the campaign.
- Sirens: audio isn't mine. Hook: `CityAtmosphere.state.hunted()` (a `band` change) — AudioDirector can poll it or a `heat_state_changed(band)` signal can be added on request.
- Frame time regresses >15 % relative on title and grid (absolute +0.2–0.8 ms GPU at 1080p; 200+ fps). Quality tiers added; Deck unmeasured.
- The real-screen captures of the title catch it before its bake lands (the blank-bake bug the city branch fixes); the lab shows the lit city.

## Bible rules to look at (not changed)

- §9.1 "combat dims the city 35 %" vs combat_scene's existing 0.55 veil: pick one number.
- §8 T0 "≥ 3 s period" conflicts with `beacon_blink` 1.6 s and FLAGGED's "≤ 1 Hz" flicker (a T0 backdrop effect faster than T0); I read §9.3 as its own rule.
