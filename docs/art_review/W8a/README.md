# W8a: title family and shared glass

Branch `art/w8a-menus`. The "before" pictures are the W10 baseline (`art-pass/docs/art_review/W10/baseline/full`), and the "after" pictures come from the W10 harness (`tools/visual_qa/capture_pack.py`) on this branch.

## Pictures

| File | What |
|---|---|
| `<screen>_1.0_mouse.jpg`, `_1.6_pad.jpg`, `_2.0_mouse.jpg`, `_1.0_grey.jpg` | Before and after, side by side, for title, slots, options, codex, stats and hq_pause. |
| `regression_43_1.0_mouse.jpg` | All 43 harness screens at 1.0 mouse, after the shared-panel change. |
| `page_transition_strip.jpg` | Title → slots (glass slides in from the right) and title → codex (glass tabs slide in, the paper spread drops), at 0.1 s steps. Captured with `--demo-page-after=<page>`. |
| `baked_art.jpg`, `logo_rebel_cell.png` | The baked SVGs as the game rasterises them: logo, NEVER SLEEP, TRUST NO ONE, and the five landmark glyphs. |

**Review round 1:** I recaptured title, options and modem (`modem_*.jpg`) at every scale after the orchestrator's review.
- NEVER SLEEP and TRUST NO ONE are redrawn as solid marker graffiti: `CELL_PINK` letterforms with an `INK` keyline, a hard shadow, and drips with bulbs.
- Options keeps a side room inside its scrolling view wide enough for the pad focus scale plus brackets, so no row clips (tested for every tab at 1.0, 1.6 and 2.0, pad and mouse).
- LEAVE THE MODEM is placed under the spinner in the REMOVE A CARD window (granted edit in `netrun_scene.gd`).
- The plan note is taped only over the menu's frame.

The other screens' pictures predate two small fixes: the plan note's empty fourth line and the empty-slot hint in `TEXT_HI`.

## What changed (files)

- **Shared panels**
  - item 1: `terminal_window.gd` and `zine_panel.gd`: type comes from the scale, SCRIM behind glass, panels size to their content, `scroll_body` and `scroll_content`.
  - item 2: `page_transition.gd`: one direction per material, a fade under reduce motion, the page settles before it moves, `open_modal`/`close_modal`/`after_modals`.
- **Title** (`title_scene.gd`)
  - Baked `LogoArt` with its drip. The menu is on GLASS.
  - One plan note and one `ScrawlArt`, both taped to the menu.
  - A GLASS uplink (`StatField` grid).
  - A prompt bar with a pad.
  - W7 calm controls on the menu and the uplink; every other page calms behind itself.
  - Pages trim their scrolling view if they outgrow the room under the logo.
- **Slots:** `case_file_card.gd`.
- **Codex:** `codex_spread.gd`. `codex.gd` now tags entries with `slice`, `status` and `corporation`.
- **Stats:** `achievement_badge.gd` and `run_receipt.gd`.
- **Options:** `settings_panel.gd`, rewritten on `TilePicker`, `ZineToggle` and `ZineSlider`.
- **Pause:** `pause_menu.gd`.
- **Art**
  - `assets/art/` (logo, scrawls, landmarks) and `svg_art.gd`, `logo_art.gd`, `scrawl_art.gd`.
  - Generator: `tools/art/w8a_svgs.py`. Review render: `tools/art/render_svgs.gd`.
- **`icon_line.gd`:** additive `icon_color`, so the Continue glyphs are ink on the pink primary.
- **Tests:** `test_art_w8a_menus.gd` (17 tests). I also updated tests that depended on the old widgets: pass12, pass18, pass20, pass21, pass24, w9, and title_and_menus.

## ART_BIBLE §14 checklist (title, slots, options, codex, stats, pause)

| Item | Result |
|---|---|
| Tokens, type steps and spacing only | **Pass.** Static lint is 0 for every file I own; baseline lowered. |
| Materials not mixed | **Pass.** Paper folders and receipts sit on glass as their own components. |
| Focal order and one primary | **Pass.** Title: logo → Continue → city. Slots: Load. Pause: Resume. Options and codex: none. |
| Six component states | **Pass** through the W2 kit. The tabs add a `CELL_PINK` rule when chosen. |
| 1.0 / 1.6 / 2.0 without clipping, overlap, truncation or text under 12 px | **Pass** by test (`test_title_pages_fit_at_every_text_scale`) and in the captures. The runtime lint's remaining overlaps are rows scrolled under the MORE BELOW hint, plus the pause menu over the HQ. |
| Contrast (§3.7) | **Pass** on the glass. The run-receipt "contrast" findings are ink on paper that the lint can't see (low confidence). |
| Greyscale | **Pass.** The corp is carried by its pattern and landmark, badges by outline and lock, toggles by knob side and tick. |
| Pad | **Pass.** Prompt bars on title, slots, options and pause. No bracketed hint with a pad. No mouse wording in Options. |
| Motion within budget | **Pass.** Pages take ≤ 0.35 s, modals ≤ 0.22 s, and the logo drip is T0 and static under reduce effects. |
| No empty panel over 25% | **Pass.** Options, codex, stats and pause shrink to their content. |
| Stills and strips | **Pass** (this folder). |

## Decisions

- **§4.3 rule 5:** the logo and scrawls are original path-drawn SVGs (no embedded font), rasterised at the drawn size by `SvgArt`. The NEVER SLEEP subtitle shows in any locale except English.
- **§11 Title:** the profile readout stays as a quiet GLASS "UPLINK" of icon + number fields. Keeping the paper tags would have made more than one PAPER note.
- **§6.5 Picker:** each tile gets a short name plus a meta line (for example Deutan / green-weak), because tiles draw one line and would cut long names. Toggles get a short label, with the old long wording as a caption under each one.
- **§5.3 one size across tabs:** every section is built once, and the view is as tall as the largest section, capped by the room. Wrapped labels get their width before they are measured.
- **§5.3 pause "sized to content":** the menu is narrow around its lines and `MENU_SIZE` wide only while Options or the Codex are open. It re-centres on the box its host placed, so no host change is needed.
- **§6.5 text field:** the campaign code sits in a read-only `CodeField` sized to the whole code. `code_line()` is kept for callers.
- **§3.7:** the Continue glyphs use `INK` on the primary (added `IconLine.icon_color`).

## Could not do / known gaps

- **Fixed in review round 1: the Modem overlap** (`test_anim4b_run_drag_drop` at 1.6). `LeaveModem` now follows the spinner. I placed it under the spinner rather than under the whole window, because under the window it would leave the screen at 1.6.
- **`FitScroll`/`ScrollHint` (W2) can crash when content measures huge for one frame** (wrapped labels at width 0). I fixed my callers by giving wrapped labels their width up front. The hint's layout chase itself is unchanged.
- **High contrast** is not drawn specially for the custom-drawn paper pieces (case file, receipts, badges).
- **2.0 slots:** one case file per row, and the view shows about one folder at a time.

## Bible notes

- §6.5 could state that tiles hold a short name plus meta, since long option names don't fit a tile.
