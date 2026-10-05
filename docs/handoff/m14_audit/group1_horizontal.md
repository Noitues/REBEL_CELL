# M14 rolling audit: Group 1 (ART-1 Foundations), HORIZONTAL

Main 12c6ad3. ART-1 merges audited: 34efb96 (1A), 470b6dd (1C), 63d5a3e (1D), ceee852 (1B). Report only; nothing was fixed.

## Evidence run
- Fast tier, `python tools/run_tests.py --tier fast -j 2`: 93 scripts, **822 tests, 0 failing** (80 s).
- One gt.sh call with `test_motion_lab_demos`, `test_anim_r5_city`, `test_anim_r5_netrun` and `test_horizontal_pass21_screens` (full tier: the kit's lab demos and 1A's MSDF / signal-11 acceptance): **59/59 passed** (175 s), with `FONTS_MSDF = true`. That confirms CARRY_OVER rows 5 and 8 as fixed.
- A headless probe (scratchpad script, not in the repo) measured Anton stamp sizes at each text scale (B-2).
- One windowed perf run of the city spike, raid view, tier 2, with 4 other godot.exe running: frame_avg 2.82 ms, max 41.27 ms, gpu 2.21 ms, 33 draws, 2.23 M prims, 130.7 MB texture memory. The PERF line printed `size=(1280.0, 720.0)` (D-3). No ERROR lines in the log.

## No P1 found.

## 1A: palette, faces, theme
- **P3 A-1** `scripts/ui/kit/palette.gd`: `marker()` now returns Anton across 105 call sites, so the name misleads. This is logged in DECISIONS. Rename it when Group 2 / 4 move the screens.
- **P3 A-2** `docs/handoff/art_0/CARRY_OVER.md:5,8`: the MSDF / signal-11 and class-accent rows are still listed as open. 1A closed both, verified by the run above. Tick them.

## 1B: material kit
- **P2 B-1: Continuous motions that are not table entries.**
  - The CRT roll band (`shaders/kit/crt_terminal.gdshader:25-26,75-77`, roll_strength 0.03 and roll_seconds 7.0 as shader defaults) is never set by `crt_terminal_panel.gd:154-160`.
  - The sticker holo drift (`vinyl_sticker.gd:360` `HOLO_DRIFT := 0.04`, used by `sticker_fill.gdshader:45`) is the same.
  - Both animate on TIME with no `ui_motion.tres` entry, REQUIRED_IDS row or lab demo, and they can't be switched off through `Motion.live`. Only reduce effects stops them.
  - Inline timings break ANIMATION_HANDOFF ground rule 6: `binary_bits.gd:33` FLIP_SECONDS 0.06 and `:39` LINGER 0.1.
  - Expected: every motion is a switchable table entry (rules file, horizontal list).
  - Fix: add entries `crt_roll` and `sticker_holo_drift` and drive the uniforms from them. Move the bits' flip and linger into `bits_flight` or new entries.
- **P2 B-2: Stamp slots are fixed px while their Anton stamps scale with text.**
  - `corp_paper_panel.gd:15` slot 200x56 (drawn at `:121-126`); `decrypted_holo_panel.gd:22` slot 180x48 (drawn at `:150-160`). Both draw at `UiTheme.font_px(HEADING)`.
  - Probe, ruled box:

    | Text scale | DECRYPTED box (slot 180x48) | CLASSIFIED box (slot 200x56) |
    |---|---|---|
    | 1.0 | 139x50 (already taller than the slot) | — |
    | 1.6 | — | 210x77 |
    | 2.0 | 261x96 | 259x96 |

  - At 2.0 the corp stamp's right edge lands about 27 px outside the sheet: the slot sits at width - 216 and the half box is 130 px.
  - Expected: bible §5.6 text scale 2.0 with no overflow.
  - Fix: size the slot from the measured stamp (plus padding) and keep it inside the panel, or fit the stamp to the slot.
- **P2 B-3: Translate once.**
  - `DECRYPTED` is a const drawn with draw_string and never translated (`decrypted_holo_panel.gd:21,153,160`). It is not in `assets/text/strings.csv`; ART-1 added no rows there.
  - English defaults are drawn raw: `corp_name` "SOLACE BIOSYSTEMS" and `stamp` (`corp_paper_panel.gd:18,27,111,126`), and `system_word` / `hint` (`system_word_sticker.gd:20,25,73,77`).
  - The Label-based parts keep auto-translate on: the CRT label `"> " + text` (`crt_terminal_panel.gd:48,108`) and the paper field `"%s: %s"` (`corp_paper_panel.gd:79`). Text a caller already translated is translated again, and raw text never matches a key.
  - Fix: state "caller passes translated text" in the components' docs. Set `auto_translate_mode = DISABLED` on those Labels, as the project already does in `crew_chip.gd:31` and `loadout_view.gd:84`. Mark DECRYPTED with `TextDb.mark` / `tr` and re-export.
- **P2 B-4: The CRT glass differs from the bible and from 1A's TerminalPanel; three CRT looks now coexist.**
  - `CrtTerminalPanel` feeds `Palette.CRT_GLASS_TOP/BOTTOM` (#0B1630 / #050A1A, alpha 1.0) into the shader (`crt_terminal_panel.gd:156-157`). That overrides the shader's 0.94 alpha, so the kit glass is fully opaque.
  - Bible §2.1 says TERMINAL_BG is rgba(5,13,28,.92-.95) (palette.gd:56, 1A's TerminalPanel).
  - The three CRT looks: `shaders/crt_panel.gdshader` (UiTheme, `ui_theme.gd:616`), 1A's TerminalPanel stylebox, and `shaders/kit/crt_terminal.gdshader`. `SystemWordSticker._draw` draws a fourth CRT box from a new StyleBoxFlat every frame (`system_word_sticker.gd:59-64`).
  - This breaks plan §5.2 "one uber-material per medium (CRT, sticker, pencil, toon)".
  - Fix: one CRT material on TERMINAL_BG / TERMINAL_EDGE. TerminalPanel and SystemWordSticker adopt it; crt_panel.gdshader retires or merges.
- **P2 B-5: Palette tokens don't follow 1A's naming.** (palette.gd:206-230, the 1B block)
  - `VINYL_*` names the medium 1A calls `STICKER_*`, and `CRT_GLASS_*` names the one 1A calls `TERMINAL_*`.
  - `TOON_INK` #0C0A16 (`:230`) duplicates 1C's `GLYPH_INK` (`:552`).
  - `HOLO_SCRIM` (`:228`) re-types SCRIM's rgb as float literals instead of `Color(SCRIM, 0.88)`.
  - `STICKER_FILL_PINK/RED` carry meaning (the Cell's verbs, threat words) but are missing from `PAIRED_WITH` (§5.1). The pink disagrees with 1A's `STICKER_COMMIT = CELL_PINK`.
  - The block splits 1A's font block (FONT_PENCIL `:204`, FONT_DISPLAY `:233`), and `:233` lost its formatting (`const FONT_DISPLAY :="`).
  - Fix: rename to the 1A prefixes, alias the duplicates, add PAIRED_WITH rows, and move the block below the fonts.
- **P3 B-6** `pencil_lint.gd:99-100`: `_walk` uses `get_children()`, which skips internal children. The kit's own panels add their drawing parts as INTERNAL (`corp_paper_panel.gd:49-63`), so the cover rule can't see them. The lint also ignores `z_index` / `top_level`, and counts any scripted Control as drawing (false positives).
- **P3 B-7** Per-character drawing breaks shaping for complex scripts: `vinyl_sticker.gd:305,319` and `grease_pencil_word.gd:99-103`. This is known (the baked per-locale atlas is ART-4/10); note it there.
- **P3 B-8** `KitDemo` is a dev-only lab helper but lives in `scripts/ui/kit/materials/kit_demo.gd`. Its demo string isn't translated (dev only).

## 1C: glyphs
- **P3 C-1** `assets/glyphs/glyph_sdf.gdshader` has no rc_common include and no VfxTier. It is static, but the group acceptance says "every shader has reduce_effects (global) and a VfxTier".
- **P3 C-2** `tools/validate_content.gd` doesn't run `GlyphTableData.validate()`. Only the smoke check (`schema_smoke_checks.gd:520-545`, logged, fine) and `test_art1_glyphs` cover it, so content validation alone won't flag new content without a glyph.

## 1D: city spike
- **P2 D-1: The spike shaders skip rc_common, reduce_effects and VfxTier.**
  - `tools/spike/city/shaders/city_car.gdshader:17` moves traffic on raw TIME, and `city_post.gdshader:96` drives rain / fog on raw TIME. Neither includes rc_common; nor do `city_building` or `city_ground`.
  - The report asks ART-5 to promote these (report "What ART-5 needs" 5, 7).
  - Expected: Group acceptance "every shader has reduce_effects (global) and a VfxTier".
  - Fix: include rc_common now and route TIME through `rc_time`. Their `time_scale` uniform can stay.
- **P2 D-2: Decoration from an RNG, not hashes.**
  - `scripts/city3d/city_traffic.gd:23,36-39` uses a `RandomNumberGenerator` (`randf` / `randi_range`). ANIMATION_HANDOFF ground rule 1 says decoration randomness comes from hashes, never randf.
  - What the brief asked me to check: it is seeded (`RngStreams.make_stream(cfg.city_seed=7, &"city_traffic")` = `hash([7, "city_traffic"])`) and deterministic (`test_city3d_spike.gd:141-147` compares two builds).
  - It is isolated: not in `RngStreams.STREAM_NAMES`, never saved, no game stream consumed. So there is no replay risk.
  - It is also not "an RngService stream passed in": it is built inside `build()`.
  - Fix: KitNoise / `NeonCity._h` hashes, or log the exception in DECISIONS.
- **P2 D-3: The perf claims are only partly trustworthy.**
  - (a) Numbers are for a 3,710-building district, about 26 % of the 14,100-building city. The report itself projects about 8 M primitives for the whole city, against 2.2 M measured. So "budget met" is not shown at production scale.
  - (b) The Deck estimate is 10-12 ms, over the 8 ms city budget. The report says this is unmeasured.
  - (c) Frame max reached 9-21.7 ms in the report and 41.3 ms in my run. These spikes are blamed on sharing but not separated from real hitches.
  - (d) The PERF line prints `get_visible_rect()`, which is the 1280x720 canvas under `canvas_items` stretch, not the render size (`city_spike_3d.gd:369-371`). The 1920x1080 and 1280x800 claims can't be checked from the logs.
  - (e) `gpu_ms` reads the root viewport only (`:364-365`), so it excludes the half-resolution ground SubViewport pass.
  - Trust: my rerun under similar load (4 other godot.exe) matched the reported averages within about 2 % (2.82 vs 2.78 ms; 130.7 vs 127 MB). Contention inflates rather than deflates, so the averages are fair upper bounds for the district.
  - Fix: log the window and render size and the SubViewport GPU time. Measure the whole city (chunked) and the spikes alone in ART-5; the Deck stays open.
- **P2 D-4: Plan §5.2 budgets were not set in config.**
  - Plan §5.2 says "Budgets (set in ART-1, in config)": city ≤ 8 ms, wheels + FX ≤ 4 ms, draw calls and material count per screen, and texture memory.
  - Only `budget_ms = 8.0` exists (`scripts/city3d/city_spike_config.gd:82`, spike-only), and nothing reads it. There is no gate test and no texture budget for the 106-131 MB measured.
  - Fix: add the budget group to campaign_config and a check in the perf probe. This is shared with cross-group.
- **P3 D-5** `tools/spike/city/city_spike_config.tres` is empty, so every number is a script default.
  - Literal colours sit in `city_spike_config.gd:97-167`; `ink` (0.05,0.04,0.09) is roughly TOON_INK / GLYPH_INK but not taken from Palette.
  - It is a Resource schema outside `scripts/data/`, with no smoke check and no schema log.
  - That is acceptable for a spike, but ART-5 must promote it properly (report item 1).
- **P3 D-6** `city_layout_recorder.gd:24-75` subclasses NeonCity and overrides or reads its private members (`_fist_segs`, `_placing`, `_painter`, `_prepare_build`, `_hq_rects`, `_traffic`, `_street_ink`). The coupling is brittle, and the brief said read-only use of content and CityBakeCache.

## Cross-group (machinery later groups will trip on)
- **P2 X-1: Two 3-band toons that disagree, plus three spill implementations.**
  - 1B `shaders/kit/toon_ink.gdshader:20-23`: edges 0.55 / 0.12, multiplicative shades 1 / 0.62 / 0.32, hull ink.
  - 1D `city_building.gdshader:12,135` with config `ramp_edges` (0.118, 0.363): absolute ramp colours, post-pass ink.
  - Spill: 1B `LightSpill` 2D, 1B's `spill_lights[8]` for 3D, and 1D's screen-mip spill in `city_post`.
  - Both DECISIONS entries say "to be unified", but no owner is named.
  - Fix: name ART-5 (or a 1B follow-up) as owner of one toon / ink / spill material, and agree the band numbers.
- **P2 X-2: BitPath (2C) vs BitsPath (1B), and StickerSeam vs VinylSticker.**
  - Both bit paths are quadratic Beziers with `RIM_CONTROL 1.5` and their own hash noise (`BitPath.noise` vs `KitNoise`).
  - `bits_seam.gd:3-7` says the switch to 1B's emitter is "an edit to this file only". That is false. `BinaryBits.burst` takes starts and a target and builds its own BitsPath plan (`binary_bits.gd:51,84`), so it cannot draw a BitPath's free flight, spiral dissolve, inflow or drift. Its arrivals would also differ from the ones 2C schedules HP ticks on.
  - 1B merged after 2C (ceee852 after be4a400), but neither seam was switched, and nothing tracks that.
  - Motion meanings diverge as well:
    - squash 1.13/0.86: the slap 2C describes on `card_stamp` (`ui_motion.tres:941`); 2C's `card_slap_ring` (`:2299`) is the contact ring and gloss sweep;
    - squash 1.13/0.84: 1B's `sticker_slap` (`:2675`);
    - `card_peel` is a 0.12 s pop; `sticker_peel` is a 0.30 s curl.
  - Fix: one bits model (BitsPath extended with BitPath's phases, or the reverse) and one sticker material. Add a CARRY_OVER row.
- **P2 X-3: The shader guard has a gap.** `tests/unit/test_vfx_tiers.gd:278-284` `_shaders()` uses `DirAccess.get_files_at("res://shaders")`, which is not recursive. `shaders/fx/`, `assets/glyphs/` and `tools/spike/city/shaders/` are unguarded; `shaders/kit/` has its own test. That gap is how D-1 slipped through. Fix: walk the project for every `*.gdshader`, with an explicit exempt list (e.g. `tools/visual_qa/cvd_filter.gdshader`).
- **P3 X-4** Group 1 acceptance is still open:
  - no `docs/timeline/*_18_art1_*` (only 17_art0 exists);
  - every box in `ART_1_BATCH.md:115-122` is unticked;
  - the group's full-suite run is not recorded yet.
- **P3 X-5 Process.**
  - No merge since 1ea160d carries "# Conflicts:" lines.
  - Four merges kept the default message "Merge branch 'main' into worktree-agent-…": 7f11118, a504cd8, c167e52, 0795c5f.
  - ART-1 branches commit per acceptance criterion: 1A 5 commits, 1B 12, 1C 5, 1D 5.

## Rules checked and clean
- **1B shaders:** every one of the 10 kit shaders includes rc_common and routes each TIME line through rc_time / rc_live (`test_art1_material_kit` checks this).
- **1B register and motion:** `KitMaterials.ALL` gives every material a VfxTier. All 16 kit motion ids are in ui_motion.tres, REQUIRED_IDS and the lab DEMOS, each playing on the real piece through KitDemo (`test_motion_lab_demos` green). Reduce effects and headless show end states. MotionSkip is registered for sticker, pencil and bits.
- **Static lint:** baseline unchanged by ART-1 and `test_visual_lint_static` green. No literal colours in `scripts/ui/kit/materials/*` or `glyph_icon.gd`.
- **Views never change state:** no game-state autoload writes in the kit, glyph or city3d code. The city3d logic classes are RefCounted.
- **Schema:** GlyphTableData is smoke-checked (`_art1_glyphs`) and logged. 1B's REQUIRED_IDS addition is logged.
- **Tests:** test_art1_palette_theme, test_art1_material_kit, test_art1_glyphs and test_city3d_spike are all in the manifest, fast tier.
- **Open questions:** 1B's CPU fallback and 1D's see-through band deviations are logged there.

VERDICT: NOT CLEAN. 0 P1 and 12 P2: B-1 to B-5, D-1 to D-4, X-1 to X-3. There are 11 P3.
