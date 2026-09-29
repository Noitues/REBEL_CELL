# W9s — Accessibility settings slice

Branch `art/w9-settings` (from `art-pass`). ART_BIBLE §12, §5.4, §10 (resolve budget), §3.7.
Presentation only: no rule, content value or save format changed. `settings.json` gains
five keys; a file without them loads unchanged (tested).

## Public API (what other workstreams call)

```
# Settings (autoload) — all additive; every setter saves and emits `changed` (+ `hints_changed`)
const TEXT_SCALE_MAX := 2.0                                  # was 1.6 (Q5)
var colorblind_mode: StringName = &"off"                     # COLORBLIND_MODES: off, deutan, protan, tritan
var high_contrast: bool = false
var reduce_motion: bool = false
var resolve_speed: StringName = &"x1"                        # RESOLVE_SPEEDS: x1, x2, instant
var pad_glyph_set: StringName = &"auto"                      # PAD_GLYPH_SETS: auto, xbox, playstation, switch, deck
var pad_device: int = -1                                     # last pad that sent input
func set_colorblind_mode(value: StringName) -> void          # unknown values ignored (same for the next three)
func set_high_contrast(value: bool) -> void
func set_reduce_motion(value: bool) -> void
func set_resolve_speed(value: StringName) -> void
func set_pad_glyph_set(value: StringName) -> void
func effective_glyph_set() -> StringName                     # never &"auto"
func active_joy_name() -> String
static func glyph_set_for_joy_name(joy_name: String) -> StringName
const TEXT_SCALE_STEAM_DECK := 1.2
func device_probe() -> Dictionary                            # {feature, env, os, screen, joy_names}
var device_probe_override: Dictionary                        # tests inject a probe
static func is_steam_deck_from(probe: Dictionary) -> bool
func apply_first_run_defaults(probe: Dictionary) -> void     # called by load_settings when no file exists

# Motion (static; existing helpers and values unchanged)
const PAGE_SLIDE := &"slide"; const PAGE_FADE := &"fade"
static func camera_moves_allowed() -> bool                   # false under reduce motion
static func parallax_allowed() -> bool                       # false under reduce motion
static func page_transition_style() -> StringName            # PAGE_FADE under reduce motion
static func resolve_time_scale() -> float                    # 1.0 / 0.5 / 0.0
static func resolve_instant() -> bool
const FAST_FORWARD_ACTION := &"resolve_fast_forward"
const FAST_FORWARD_TIME_SCALE := 1.0 / SPEED_MAX             # 0.25
static func fast_forward_held() -> bool
static func resolve_time_scale_now() -> float                # min(scale, 0.25) while held

# High contrast
HighContrast.apply(theme: Theme) -> void                     # hooked at the end of UiTheme.build()
HighContrast.BG, HC_MIN_CONTRAST (7.0), HC_BUTTON_BORDER (3), HC_FOCUS_BORDER (4)

# Colour-blind correction
ColorblindFilter (autoload): layer (ColorblindLayer or null), sync(), active_mode()
ColorblindLayer (CanvasLayer 127): MODES, set_mode(), shader_mode(),
    static simulate(c, mode) / correct(c, mode)              # the shader's maths on the CPU
```

Input: `resolve_fast_forward` = **Shift** (project.godot, rebindable in Controls) and, on a
pad, **the right stick held in any direction** (added at start like the other pad binds;
hint name "RS").

## What changed (files)

| File | Change |
|---|---|
| `scripts/autoload/settings.gd` | 2.0 ceiling; the five settings, setters, `_pick` validation; glyph detection; Deck probe and first-run default; pad device tracking; fast-forward in REBINDABLE and its stick binds |
| `scripts/autoload/colorblind_filter.gd` (new autoload, `project.godot`) | adds/frees the correction layer on `Settings.changed` |
| `scripts/ui/fx/colorblind_layer.gd`, `shaders/colorblind.gdshader` (new) | LMS daltonize, linear light, `rc_common` include |
| `scripts/ui/kit/high_contrast.gd` (new) | the theme transform |
| `scripts/ui/kit/ui_theme.gd` | one hook line at the end of `build()` (one-off grant) |
| `scripts/ui/kit/motion.gd` | appended helpers only |
| `scripts/ui/kit/settings_panel.gd` | five rows + the Fast-forward rebind row; `_choice` helper (OptionButton, as window mode) |
| `project.godot` | `ColorblindFilter` autoload; `resolve_fast_forward` action |
| `assets/text/strings.csv` | 18 appended rows |
| `tests/unit/test_w9_accessibility_settings.gd` (fast tier) | 19 tests |
| `tests/helpers/layout_scales.gd` + 12 layout test scripts | layout tests hold screens to `LayoutScales.VERIFIED_MAX` (1.6) until W8 fits 2.0 |

## Review images

- `options_before_after.png` — Options, Accessibility tab: before (W10 baseline) / after.
- `colorblind_deutan.jpg`, `colorblind_protan.jpg`, `colorblind_tritan.jpg` — Solace grid
  (green/red heavy) and `combat_start`, off vs corrected.
- `colorblind_deutan_simulated.jpg` — the W10 deutan **simulation** rendered in-engine
  (`--filter-mode shader`, layer 128) over no correction / over the deutan correction
  (layer 127). The harness runs unchanged; JACK IN, CORRUPTED chips and the pink slices
  separate from grey once corrected.
- `high_contrast.jpg` — `title`, `hq`, `combat_start`, normal vs high contrast.
- `text_scale_2.0/combo_2.0_mouse_re-off_none.jpg` (contact sheet, all 43 screens) and its
  `lint_report.md` (212 font, 25 overlap, 10 clipped, 36 contrast findings).
- `capture_w9.py` reproduces all of them (seeds W9 settings into each harness run's
  private user:// folder; no harness change).

## Text scale 2.0 breakages (W8's list)

Seen in the 2.0 captures, plus the 12 layout tests that failed at 2.0 (now held at 1.6).

| Screen | Breakage at 2.0 | Owner |
|---|---|---|
| Every page with the top bar (hq, grid*, raid*, route, loot, modem, event, campaign end) | `HudBar` tags wrap to two rows (§5.2 "never wraps"); on `run_end` only two tags fit | W8b (`hud_bar`/`hud_stats`) |
| combat_* | top-bar tags squeezed to a sliver at the top edge; nudge key hints ([Q]/[E]) overlap forecast chips; tags crowd the wheel tops; hand card rules text doesn't grow (custom draw); `test_horizontal_pass20` nudge hint covers tag | W3 (+ W4 cards) |
| combat_victory / combat_defeat | OPERATIVE note covers the right side; DISPATCH box clips ("We lost o") | W3 / W8c (`dialogue.gd`) |
| hq | roster cards crushed to one narrow column, Pirate Radio note clipped, CELL STATUS clipped; HQ panel 1289 px > 1280 (`test_panel_widths`); dossier HP not on the first screen (`test_anim_r1_campaign`) | W8b |
| hq_crew | a dossier 397 px in a 396 px view (`test_horizontal_pass24_screens`) | W8b / W5 (`crew_card`) |
| hq_loadout_spinner | mid-word breaks in the socket list ("Clas s defa ult", "Corr upt") — §4.3 rule 3 | W8b (`loadout_view`) |
| hq_loadout_deck | card grid runs under the modal edge (scrolls, no hint) | W8b / W4 |
| hq_pause | campaign code wraps inside the pause panel; panel overlaps the HQ menu | W8a |
| grid* (all corps) | site card truncated (JACK IN cut at the bottom); runs list starts off the card | W8b |
| raid_setup | 1373 px wide (`test_horizontal_pass12`); armory cards clipped; defence card off screen (`test_horizontal_pass22_screens`); subtitle ends in "…" | W8b |
| raid_playout / raid_result / raid_report | MAP LEGEND panel covers CORE and the HOLDS stamp; raid nodes leave the map area (`test_horizontal_pass23_screens`); feed text clipped | W8b (`map_legend`, `raid_playout_panel`) |
| route | ROUTE key shrinks to unreadable text (lint: 11 font findings, `route_legend`) | W8b |
| modem / modem_socket | microchip text below caption; MODEM sign cropped; LEAVE THE MODEM off the bottom; subtitle covers buttons (`test_horizontal_pass20_screens`) | W8c |
| event | story paper text overlapped by its title and speaker plate; subtitle "…" | W8c |
| new_campaign | row widths at the edge, TODAY'S RUN cut at the bottom | W8a |
| options | panel runs past the bottom (resolve speed row and Close off screen) | W8a |
| campaign_won / campaign_lost | DISPATCH line truncated; story top cut under it (overlap findings) | W8d |
| run_end | FLATLINED stamp small, top bar two tags | W8d |
| HQ, Modem subtitles | subtitle covers controls and stat tags (`test_horizontal_pass21_screens`) | W8b (`subtitle_strip`) |
| (runtime lint) | `terminal_window` fixed sizes (146 font findings), `fx.gd` SAVED label | W8, W2 |

## ART_BIBLE §14 checklist (what W9 touched)

| Item | Result |
|---|---|
| §3 tokens / §4 steps / §5 spacing | Pass: HighContrast uses `Palette` tokens; new constants named; static lint unchanged |
| Materials not mixed | N/A (no component restyled) |
| Focal order, one primary | N/A |
| Six component states | Pass for high contrast: every theme state keeps a visible edge; focus 4 px `FOCUS` |
| 1.0 / 1.6 / 2.0 | 2.0 is now reachable: **fails on most screens** (table above; W8's job, per brief) |
| Contrast §3.7 | Pass: high-contrast theme text ≥ 7:1 (tested); disabled `TEXT_MID` on #000 ≈ 11:1 |
| Greyscale / colour-blind | Pass: correction verified under the in-engine deutan simulation |
| Pad | Pass: new rows focusable; no mouse wording in new strings; fast-forward has a pad bind |
| Motion within budgets | N/A (helpers only; consumers are W3/W7/W8) |
| Review stills | Yes (this folder) |

## Decisions

- Colour-blind "remap corp and semantic hues" (§12) is a **global daltonize pass**, because `Palette` values are compile-time constants read everywhere; a per-token remap would need every view to re-read colours. Patterns and glyphs stay the primary cue.
- Daltonize in linear light with the classic LMS matrices (Fidaner et al.); tritan shifts the blue-yellow error into red and green.
- Correction layer 127: above every game layer, under W10's simulation filter (128), so a simulation capture shows what a player with the correction sees.
- High contrast turns every filled theme box to #000 and keeps a state tint as an opaque 2 px edge; grabbers and the slider fill stay coloured (opaque). All text `TEXT_HI`, focus `FOCUS`, disabled `TEXT_MID` (§3.7 bans faded disabled text).
- Reduce motion only answers the questions; `Motion.live(id)` still governs reduce effects. `camera_moves_allowed()` ignores reduce effects (reduce effects keeps its meaning).
- Fast-forward: Shift, and the right stick on a pad — the only unbound pad control, so nothing collides. W3 must exempt it from the MotionSkip "a press completes the motion" rule (see requests).
- `FAST_FORWARD_TIME_SCALE` = 1/`SPEED_MAX` (4×), the kit's existing top speed.
- Glyph detection: substring rules, plus a "ps"/"ps<digit>" *word* rule so "gamepads" isn't a PlayStation pad; Sony counts as PlayStation; unknown = xbox.
- Steam Deck default 1.2 is `Settings.TEXT_SCALE_STEAM_DECK`; test runs skip the device probe unless one is injected.
- Layout tests: the 12 scripts that failed at 2.0 check up to `LayoutScales.VERIFIED_MAX` = 1.6; W8 raises it to `Settings.TEXT_SCALE_MAX` when the screens fit.
- Options: resolve speed and colour-blind use the existing OptionButton pattern (W8a restyles as W2 pickers); pad glyphs sit in Controls.

## Couldn't do / known gaps

- High contrast reaches only the **theme**: views with their own colour overrides or `_draw` (paper notes, top-bar tags, wheels, cards, the Options toggles' `TERMINAL_TEXT` override) are unchanged. W2/W8 components must read `Settings.high_contrast`.
- The `combat_start` high-contrast shot shows a darker city than its normal shot; the theme doesn't touch the city, so it is capture variance (bake timing).
- Items 4–7 landed in one commit (they share Settings' declarations and `from_dict`).
- `UiTheme` can't be compiled from a `-s` tool script (it names the `Settings` autoload); this was already true before the hook.

## Bible rules I'd question

- §12 "Colour-blind modes remap corp and semantic hues": with constant tokens a remap can't be done per hue without touching every view; I suggest the bible say "correct" (daltonize) instead.
- §12 "TEXT_HI on #000" conflicts with PAPER components (ink on paper). High contrast should say what paper does (suggest: paper stays, ink `INK` on `PAPER` already ≥ 15:1).
