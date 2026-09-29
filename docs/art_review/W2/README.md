# W2 — Component library (branch `art/w2-components`)

ART_BIBLE §6 (six states), §6.4–§6.8, §7.4, §10, §12. Presentation only: no rule, content
value or save format changed. W2 builds the widgets; W8 swaps them in on the screens.

## Images

| File | What it shows |
|---|---|
| `components_1.0.png`, `components_1.6.png`, `components_2.0.png` | `tools/design_lab/components_lab.tscn` at text scale 1.0 / 1.6 / 2.0: every component (Primary, Secondary, Tertiary, Danger, menu item, toggle, slider, stepper, tile picker, code field, stamp, sticker) in all six states (idle, hover, focus, pressed, disabled, refused), the one toast (refusal and note), a tooltip whose repeated title is dropped, the SAVED stamp, and the redrawn status icons (open / filled) and kit marks. |
| `components_grey.png` | The 1.0 sheet in greyscale: every state still reads (lift, brackets, lock badge, no-entry mark, knob side). |
| `pad_glyphs.png` | Every glyph set (Xbox, PlayStation, Switch, Steam Deck) × every button (faces, shoulders, triggers, D-pad and its directions, both sticks and their clicks, Menu / View), with a prompt bar per set. Lab `--glyphs --scale=1.6`. |
| `before_after/*.jpg` | W10 harness, before (art-pass baseline) / after / changed pixels, at 1.0 mouse and 1.6 pad: `raid_result`, `title`, `options`, `combat_refused`. `diff_report.md` and the runtime `lint_report_after.md` beside them. |

Captured with `python tools/run_windowed.py --log lab.log -- res://tools/design_lab/components_lab.tscn -- --scale=1.6 --out=<png>` and `python tools/visual_qa/capture_pack.py --screens raid_result,title,options,combat_refused …` then `diff_pack.py` against `art-pass/docs/art_review/W10/baseline/full`.

Diff notes: most changed pixels are the city behind (camera timing, and the options capture landed on an unbaked Grid, which is not W2's). The W2 changes: the focused control's brackets (raid 1x speed, options row), the SAVED sticky (bottom right), the combat refusal toast on its sticky with the label step, and the disabled RESPIN sticker keeping its paper with a lock instead of a darkened fade. The before/after were taken just before the final tweak that also colours a focused row's words FOCUS (see decisions).

## What changed (files)

- New kit: `style_box_brackets.gd` (FOCUS brackets as a StyleBox, plus `draw_on`), `style_box_locked.gd` (disabled box with a lock badge), `kit_state.gd` (the six states, `force`, `refuse`, `draw_box`, `draw_frame`, `force_native`), `refusal_mark.gd`, `zine_toggle.gd`, `zine_slider.gd`, `stepper.gd`, `tile_picker.gd`, `code_field.gd`, `pad_glyph.gd`, `banner_queue.gd`.
- Rewritten / extended: `ui_theme.gd` (button variants, states, brackets, literal colours to tokens, MenuItem on the scale, glass tooltip), `ui_focus.gd` (1.03 focus scale), `toast.gd` (the one sticky toast), `toast_note.gd` (thin subclass, same API), `ui_tip.gd` (26–36 columns, body face past 3 lines, title de-dup, `for_input`), `focus_tip.gd`, `zine_stamp.gd`, `pad_prompts.gd`, `stat_icon.gd`, `confirm_dialog.gd`, `sticker_button.gd`, `drip_button.gd`.
- Token migration: `slice_icon.gd`, `icon_mark.gd`, `asset_icon.gd`, `daemon_sigil.gd`, `menu_motion.gd`, `graffiti_tag.gd`; `tools/visual_qa/lint_baseline.json` lowered (11 file/rule counts to 0, `ui_theme` 24 → 0).
- `scripts/autoload/fx.gd` (grant): the SAVED label only.
- Motion: 9 entries appended to `content/config/ui_motion.tres` (`focus_scale` T1, `button_refused` T2, `toast_in/hold/out`, `stamp_hold`, `zine_stamp_in` T2, `banner_gap`, `toggle_slide`), added to `UiMotionData.REQUIRED_IDS` and the motion lab's DEMOS.
- `assets/text/strings.csv`: `Copy`.
- `tools/design_lab/components_lab.gd/.tscn` (new); `tests/unit/test_art_w2_components.gd` (fast, 31 tests) + manifest.

## ART_BIBLE §14 checklist (what W2 touched)

| Item | Result |
|---|---|
| §3/§4/§5 tokens only | **Pass** in the owned kit files (static lint 0 colour / size findings in them). Component geometry constants (pill 44×24, tile 144×76) are per-file constants on the 4 px grid. Two exceptions noted below (fixed-size icon textures). |
| Materials not mixed | **Pass**: inputs, buttons, tooltip are GLASS; toast, stamp, sticker are PAPER on their own. |
| Focal order / one primary | n/a (components). Primary is the one filled pink variant. |
| All six states | **Pass** for every component (lab sheets; tested). Native Buttons get them from the theme; refused via `RefusalMark.flash`. |
| 1.0 / 1.6 / 2.0, nothing < 12 px | **Pass** in the lab sheets; no literal size under 12 in the owned files (ZineStamp hint 11 → caption). Glyph letters floor at caption. |
| Contrast §3.7 | **Pass**: disabled labels TEXT_MID ≥ 4.5:1 on their box (tested), DISABLED outline ≥ 3:1, toast and SAVED INK on NOTE_YELLOW. |
| Greyscale | **Pass** (`components_grey.png`). |
| Pad: prompts, glyphs, focus, wording | **Pass** for the kit: glyph + word prompts, brackets + scale, `UiTip.for_input`. Call-site wording audit is W9's. |
| Motion budgets / tiers / reduce effects | **Pass**: toast 0.18 / 2.5 / 0.2, stamp 0.12 in, focus T1 0.1 s; reduce effects gives end states (scale at once, stamp ring whole, toast held then gone). |
| No placeholder / leftovers | **Pass** for components (toasts free after their hold, RefusalMark frees itself, BannerQueue clears). |
| Review stills | **Pass** (this folder). |

## Decisions (one line each)

1. §6 Focus: brackets carry a 1 px INK keyline so FOCUS reads on paper and over the city.
2. §6/§12: the 1.03 focus scale plays for **pad** focus only (TV distance); mouse and keys get the brackets. Headless it stays 1 so layout tests keep exact rects. Tilted controls, ZineCards and `focus_no_scale` controls opt out.
3. §6.4: the plain `Button` keeps the list-row padding (10 px); only the explicit variants (Primary/Secondary/Danger) are label + 32 px, because plain buttons are mostly rows and grid cells (widening them broke the HQ crew layout at 1.6). W8 picks a variant for each standalone action.
4. §4.2: MenuItem is on the scale at `body` (was body + 2). `label` widened the HQ menu past the crew's two columns at 1.6; W8 can step it up when it reflows.
5. §6 Disabled: the lock is a badge on the top-right corner (outside the box), so disabled never changes a size; label TEXT_MID (DISABLED #6A7080 is only 3.9:1 on glass, below §3.7's 4.5).
6. §6 Focus: a focused plain row/menu line also colours its words FOCUS (a full-width row's brackets sit far apart).
7. §6.7: toast hold = max(2.5 s, the stamp reading rule), so long refusals stay readable; `toast_note_hold` (3.5 s) is retired but kept in the table (tests require the id). The old `toast` entry is unused.
8. §6.7: the sticky's tape is tilted, the note itself stays square (rotation would break the rect-based placement and the tests that read it).
9. §6.8: 36 columns at every text scale (was 56 / scale); a long tip in the body face counts its columns in that face's own letters.
10. §6.8: `for_input` swaps a stray mouse word in pad text ("click" → "press", "drag" → "move") and warns in debug builds.
11. §6.6: stamp words are `title` sized, shrinking to fit the ring, never under caption.
12. §12: auto glyph set reads the first connected pad's name (PlayStation / Switch / Deck by name, else Xbox); Xbox letters and PS shapes are coloured with §3.3 tokens (GAIN, HARM, NET_CYAN, RESIST_GOLD, STICKER_PINK).
13. §3.6: asset and Daemon hues no longer use corp hues (sentry GAIN, honeypot HEAT_FLAGGED, Daemon green GAIN).
14. §6.4: ConfirmDialog YES is Danger, NO Secondary (NO keeps first focus).

## Couldn't do / known gaps

- The Danger X and MenuItem chevron are fixed-size textures (12 / 10×14 px): they don't grow with text scale. `IconMark.attach(b, StatIcon.TRASH)` scales; W8 uses that on real Delete buttons.
- The StickerButton "RESPIN" lettering overruns its sticker at 1.6 when it carries the drawn icon (pre-existing `_fit`); visible in the lab.
- Native `CheckButton` rows show brackets at the far ends of a full-width row; they go when W8 moves Options to ZineToggle.
- The before/after options capture shows a flat city (a bake that wasn't ready in that run; not a W2 change).

## Bible rules I'd question

- §3.3 says DISABLED #6A7080 is also the text colour, but it is 3.9:1 on glass, under §3.7's 4.5:1. The kit uses TEXT_MID for disabled labels; the bible could say so.
- §6 asks for the 1.03 scale on every focus; on mouse click it grows the button under the pointer. Suggest "pad focus" in the table.
