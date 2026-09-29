# W10 — Visual QA automation (review packs and visual lint)

Branch `art/w10-visual-qa` (from `art-pass`). This workstream adds tools only. No game view, scene, kit
component, content, rule or save format changed. ART_BIBLE §13 "Automated visual checks", §14.

## How to use it (copy-paste)

Run these from **your worktree** (the harness goes through `tools/run_windowed.py`, which refuses the main
checkout). Each Godot run gets its own user:// folder, so your settings, saves and profile are never read or
written. Output folders inside the project get a `.gdignore`, so Godot never imports the PNGs.

```
# the screens and what each one shows
python tools/visual_qa/capture_pack.py --out C:/tmp/vqa --list

# an "after" pack of just your screens (W3 example), with lint and contact sheets
python tools/visual_qa/capture_pack.py --out docs/art_review/W3/after --screens combat_start,combat_hover,combat_aiming --scales 1.0,1.6,2.0 --inputs mouse,pad --sheets

# the review axes the orchestrator checks (ART_PLAN §4): 1.0 and 1.6, mouse and pad, plus greyscale
python tools/visual_qa/capture_pack.py --out docs/art_review/W3/after --screens combat_start,combat_hover --scales 1.0,1.6 --inputs mouse,pad --filters none,grey --sheets

# diff it against the baseline (same relative paths: <combo>/<screen>.png)
python tools/visual_qa/diff_pack.py docs/art_review/W10/baseline/full docs/art_review/W3/after docs/art_review/W3/diff

# contact sheets / lint report again for an existing pack
python tools/visual_qa/contact_sheet.py docs/art_review/W3/after
python tools/visual_qa/lint_report.py docs/art_review/W3/after

# the static lint (CI gate) and lowering its baseline after you migrated literals out of a file
python tools/run_tests.py --select visual_lint -j 1
python tools/visual_qa/update_lint_baseline.py
```

Note: `baseline/full` exists only in the W10 worktree (it is git-ignored, 1.2 GB). From another worktree,
either point `diff_pack.py` at `C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-w10/docs/art_review/W10/baseline/full`,
or capture your own "before" on your branch's base first (same command, `--out .../before`).

### All options

| Option | Values | Default |
|---|---|---|
| `--out` | the pack folder (required) | |
| `--screens` | comma list from `--list` | every screen |
| `--scales` | text scales, e.g. `1.0,1.6,2.0` | `1.0` |
| `--inputs` | `mouse,pad` | `mouse` |
| `--reduce-effects` | `off,on` | `off` |
| `--filters` | `none,grey,deutan` | `none` |
| `--filter-mode` | `pillow` (derive grey/deutan from the unfiltered capture) or `shader` (render through `cvd_filter.gdshader`) | `pillow` |
| `--scramble` | pseudolocalised text (the storyboard's) | off |
| `--screen-timeout` | seconds per screen before it is recorded as `timeout` | 90 |
| `-j` | Godot runs at once | 1 |
| `--sheets` / `--no-lint` | build contact sheets / skip the lint report | |

Output: `<out>/<scale>_<input>_re-<off|on>_<filter>/<screen>.png` (1280×720), `<screen>.lint.json` and
`<screen>.status.json` beside it, `<out>/manifest.json` (screen, axes, path, status, error, warnings, Godot
errors), `<out>/lint.json` and `<out>/lint_report.md`, and with `--sheets` `<out>/sheets/`. A failed, hung or
crashed screen is recorded in the manifest and the run carries on with the next one (a crash relaunches Godot
on the remaining screens). A full 43-screen combo takes about 65 s; the full baseline matrix took 17 min with `-j 3`.

**Noise floor.** Two captures of the same build differ by under 0.1% changed pixels on most screens
(`--fixed-fps 60`, and the harness waits for city bakes). The title pages (title, codex) reach 2–5%,
because the city pans behind the menu, and the grids and raid setup reach up to 1.5% (idle lights). Treat
changes under those levels on those screens as noise.

## What changed (files)

| File | What |
|---|---|
| `tools/visual_qa/review_pack.gd`, `.tscn`, `review_pack_log.gd` | Harness scene: 43 screens, each from a clean state through the scenes' methods and run/campaign state; captures PNG, exports visible text Controls for the lint; per-screen timeout and script-error detection (a `Logger`). |
| `tools/visual_qa/capture_pack.py` | Driver: axes, `run_windowed.py`, private user://, crash recovery, manifest, lint and sheets. |
| `tools/visual_qa/cvd_filter.gdshader`, `filters.py` | Greyscale (Rec. 709) and deuteranopia (Machado 2009, severity 1) in linear light, as a screen shader and in Pillow (same maths; checked: they differ only where idle lights animate). |
| `tools/visual_qa/contact_sheet.py` | Per-combo sheets and per-screen sheets (rows: text scale; columns: input × RE). 400 px thumbnails, labelled; failed screens shown with the reason. |
| `tools/visual_qa/diff_pack.py` | before / after / heatmap per picture, `diff_report.md` sorted by changed-pixel %. |
| `tools/visual_qa/lint_report.py` | Runtime lint (rules a–e below). |
| `tools/visual_qa/visual_lint_static.gd`, `lint_static_cli.gd`, `lint_baseline.json`, `update_lint_baseline.py` | Static lint and its baseline. |
| `tests/unit/test_visual_lint_static.gd` (fast tier) | The CI gate. |
| `tools/playtest/storyboard.gd` | New `--reduce-effects` and `--filter=grey|deutan`, and a city-bake wait before each shot. Old flags unchanged. |
| `docs/TEST_SUITE.md` | New "Visual QA" section. |

### Runtime lint rules (`lint_report.md`)
- **a font:** on-screen size below the caption step (`round(12 × text_scale)`), or a `font_size` override that
  is not a §4.2 step × text scale (12/15/18/22/30/44, or 64–96 for hero).
- **b overlap:** the text areas (the glyph box, not the whole Control) of two visible text Controls intersect
  by at least 3×3 px, with ancestors and descendants excluded.
- **c clipped:** an ellipsis overrun that doesn't fit, fewer visible lines than lines outside a ScrollContainer,
  `clip_text` that cuts, or text holding "…".
- **d contrast:** the declared font colour against the background (the median of a 4 px ring just outside
  the text) under 4.5:1, or 3:1 at 24 px and up. The strongest glyph pixel is reported as a second opinion
  ("low confidence" when it passes).
- **e custom-drawn:** scripts that `draw_string` themselves (wheels, cards, map labels, Heat poster, HUD) are
  invisible to the tree walk and are listed per screen. Controls that draw their own label (sticker and BUY
  buttons) are left out of a–d. Text with no glyph pixel standing out of its surroundings is counted as
  covered by a modal and left out.

### Static lint rules (`test_visual_lint_static.gd`)
Per file under `scripts/ui/**`: `color` (a `Color(` with a number or string literal, `Color8(`,
`Color.html(`, `Color.hex(`; `palette.gd` exempt), `font_override` (`add_theme_font_size_override(.., <int>)`),
`draw_size` (a `draw_string`-family call with an integer-literal size), `font_const` (a `*FONT*` constant under 12),
and `font_size_assign` (`font_size = <int>`). Comments are ignored. A count above the baseline fails and names the
lines; a count below prints a note to lower the baseline; a new file starts at 0.

## Screens

All 43 are captured at every axis. "How" is what the harness does. `_x` means a private member, which could
break if the owner renames it (see requests).

| Screen | §11 | How |
|---|---|---|
| title | Title | campaign in a private slot, `continue_slot` |
| slots | Campaign slots | slot 1 saved (private save dir), `show_slots` |
| new_campaign, new_campaign_picker | New campaign | all corps unlocked in the private profile, `show_start`; picker: `CorporationPicker.show_popup()` |
| hq, hq_black_market, hq_crew | HQ | `new_campaign`; scroll to `BlackMarket` (500 Schematics) / `Roster` (four classes) |
| hq_loadout_deck, hq_loadout_spinner | HQ loadout | `open_loadout`; SPINNER: rank-3 operative with `seg_echo` swapped in, `show_spinner` |
| hq_pause | HQ pause | `open_settings` |
| grid, grid_site_selected, grid_raid_pending | City Grid | `show_grid`, `selected_site`, a pending raid |
| grid_meridian, grid_halcyon, grid_orbital, grid_rebel_cell | Corp grids | `new_campaign(.., corp)` with unlocks |
| raid_setup, raid_playout, raid_result, raid_report | Raid setup and playout | `show_raid`, `fight_raid` to step 2, `playout.skip_to_end`, `show_raid_summary` |
| raid_interlude | Raid interlude | Heat past the first major level, `netrun._maybe_raid_interlude`, `_show_current` |
| route | Route | `start_run` |
| combat_start … combat_refused | Combat | the storyboard's path (`_preview_card`, `select_card`, `end_turn`, respins) |
| combat_boss_p2, combat_boss_p3 | Boss phases | a Breach run built with `NetrunSession.start_special` (past the launch checks), boss HP set to 60% / 25%, one turn |
| combat_victory, combat_defeat | kill → VICTORY | `netrun._demo_combat_end("win"/"lose")`, replay skipped to its held outcome |
| loot, modem, modem_socket, event | Loot, Modem, Events | the storyboard's path; socket: `SocketPick.show_popup()` (seed 7 stocks Firmware) |
| codex, options, stats | Codex, Options, Stats | title pages; stats with a filled private profile |
| run_end | FLATLINED | run outcome DIED, phase ENDED |
| campaign_won, campaign_lost | WON / LOST | outcome set, `show_end` |

**Not captured (not on the brief's list, easy to add as screens):** the DISPATCH event variant, card detail
and deck view, Daemon tray, the Modem's remove-card and spinner-overwrite pages, the tutorial overlay, the
jack-in transition, the pause menu in a netrun or fight, and the Options tabs other than Accessibility.

With **reduce effects on**, `raid_playout` and `combat_resolving` show the end state (the playout and replay
are instant then); the manifest carries a warning.

## ART_BIBLE §14 checklist (for what W10 touched: tools only)

| Item | Result |
|---|---|
| Only §3 tokens, §4 steps, §5 spacing in the view | N/A (no view changed). The static lint now guards it. |
| Materials not mixed | N/A |
| Focal order, one primary | N/A |
| Six component states | N/A |
| 1.0 / 1.6 / 2.0: no clipping, overlap, truncation, text < 12 px | N/A for W10; **measured** for the game: see `baseline/lint_report.md` |
| Contrast §3.7 | N/A; measured (rule d) |
| Greyscale and scramble readable | N/A; the pack now captures greyscale, deutan and scramble |
| Pad prompt bar, glyphs, focus | N/A; the pack captures pad at every screen |
| Motion within budgets, RE shows end states | N/A; the pack captures RE on/off |
| No placeholder city, leftovers | The harness waits for city bakes, so a stand-in city in a picture is a real finding |
| Review stills added | Yes: `baseline/` |

## Baseline ("before", art-pass at 2fbc53e + W10 tools)

- `baseline/full/`: every screen × 1.0/1.6/2.0 × mouse/pad × RE off/on × none/grey/deutan. 1548 pictures,
  all captured, no Godot errors. Local only (git-ignored); view it in this worktree.
- `baseline/sheets/`: a per-screen sheet for each of the 43 screens (rows 1.0/1.6/2.0; columns mouse/pad ×
  RE off/on), plus the combo sheets for 1.0 mouse RE-off (none, grey, deutan), 1.0 mouse RE-on, 1.6 pad and
  2.0 mouse. The other combo sheets are in `baseline/full/sheets/`.
- `baseline/1.0_mouse/` and `baseline/1.6_pad/`: RE off, no filter, full size.
- `baseline/lint_report.md`: the runtime lint for all 12 unfiltered combos, with details for 1.0 mouse,
  1.6 pad and 2.0 mouse (`full/lint.json` has everything).

## Decisions

- Grey and deutan use the **Pillow path by default**. It computes the same linear-light maths as the shader on
  the final frame, and needs a third of the Godot runs. `--filter-mode shader` renders them in-engine; both
  paths were checked against each other (§12, §13).
- Text scale is written straight into `Settings.text_scale`, past the 1.6 clamp, as the storyboard does. W9
  raises the range (§12).
- Runs use `--fixed-fps 60` and wait for `CityBakeCache.busy() == 0` before each picture, so diffs are
  stable and a stand-in city is never captured by accident (§9.4, §13).
- Each Godot run gets its own user:// folder (`APPDATA`), a private slot and a private save dir, so the
  designer's files are never touched.
- Runtime lint "UiTheme-derived" means a §4.2 step × text scale: `UiTheme.font_px` doesn't exist yet (W1)
  (§4.3 rule 1).
- The caption floor is `round(12 × scale)` (19 px at 1.6), matching how UiTheme rounds sizes (§4.2).
- Contrast ignores Controls that draw their own label, and text that is covered by a modal (no glyph pixel
  stands out). Occlusion otherwise can't be seen by a tree walk (§3.7).
- The static lint counts lines per file and rule, with one implementation in GDScript. The Python updater
  runs it headless and lowers counts; it never raises one unless given `--reset` (§13).
- Committed: 49 sheets plus two full-size sets as JPG q85 (the PNGs were over twice the size), about 43 MB.
  The full matrix stays local.
- `docs/art_review/W10/.gdignore`, so Godot never imports review images.

## Couldn't do / known gaps

- The runtime lint can't see text drawn in `_draw` (wheels, cards, map labels, Heat poster, HUD values,
  stickers). Those files are listed per screen, and the static lint covers their literal sizes.
- Overlap can't tell occlusion. A modal over a page counts pairs unless the covered text is fully hidden.
- A few screens reach state through private members (see requests). If an owner renames one, that screen
  fails with a recorded reason; the rest still capture.
- Hover and focus come from state calls (`_preview_card`), not from a real pointer. The window is off-screen,
  so no real hover is ever captured.

## Bible rules I'd question (not changed)

- ART_PLAN W10 describes the lint as "a headless GUT test over instantiated screens". Contrast and real layout
  need a renderer, so the runtime lint is a report from the windowed pack, and only the static lint is a GUT
  gate (the brief agrees).
- §4.2 `hero` is a range (64–96), so "a size from the scale" can't be checked exactly for hero text; the lint
  accepts any size in the range.
