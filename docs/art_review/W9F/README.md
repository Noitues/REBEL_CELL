# W9F — final accessibility and polish sweep

Branch `art/w9f-sweep` (from `art-pass`, W8d merged in). ART_BIBLE §12, §14, §4.3, §5.2–§5.3,
§6.8, §8, §9, §10. Presentation only: no rule, content value or save format changed.

## Review images (all JPG q85, 1280-wide thumbnails per screen, 53 screens each)

| File | What |
|---|---|
| `sheet_2.0_mouse.jpg` | every screen at text scale 2.0, mouse |
| `sheet_2.0_pad.jpg` | every screen at 2.0, pad (prompt bars, glyphs) |
| `sheet_1.0_mouse.jpg` | every screen at 1.0, mouse (regression reference) |
| `sheet_1.0_grey.jpg`, `sheet_1.0_deutan.jpg` | greyscale and deuteranopia (W10's Pillow filters) at 1.0 |
| `sheet_1.0_high_contrast.jpg` | `Settings.high_contrast` on |
| `sheet_1.0_reduce_effects.jpg` | reduce effects on (end states, no flashes, jack cross-fade) |
| `sheet_1.0_reduce_motion.jpg` | reduce motion on (no camera move, pan held, no shake, jack cross-fade) |
| `lint_report.md` | the runtime lint for 1.0/2.0 × mouse/pad (W9F lint rules) |
| `lint_report_high_contrast.md` | the runtime lint with high contrast on |

Reproduce (from the worktree):

```
python tools/visual_qa/capture_pack.py --out <dir> --scales 1.0,2.0 --inputs mouse,pad --filters none,grey,deutan -j 2 --sheets
python tools/visual_qa/capture_pack.py --out <dir>/hc --high-contrast --sheets
python tools/visual_qa/capture_pack.py --out <dir>/re --reduce-effects on --sheets
python tools/visual_qa/capture_pack.py --out <dir>/rm --reduce-motion --sheets
```

The harness now has 53 screens: W10's 43 plus `event_dispatch`, `deck_view`, `card_detail`,
`daemon_tray`, `modem_remove`, `modem_overwrite`, `tutorial`, `jack_in`, `pause_netrun` and
`pause_fight`, and two new axes (`--high-contrast`, `--reduce-motion`).

## Runtime lint (final)

| combo | screens | font | overlap | clipped | contrast |
|---|---|---|---|---|---|
| before W9F, 2.0 mouse (43 screens) | 43 | 33 | 34 | 2 | 76 |
| before W9F, 2.0 pad (43 screens) | 43 | 36 | 71 | 2 | 101 |
| 1.0 mouse | 53 | 0 | 0 | 2 | 9 |
| 1.0 pad | 53 | 0 | 0 | 2 | 6 |
| 2.0 mouse | 53 | 0 | 0 | 3 | 7 |
| 2.0 pad | 53 | 0 | 4 | 3 | 5 |
| 1.0 high contrast | 53 | 0 | 0 | 3 | 180 (see note) |

What is left, finding by finding (details in `lint_report.md`):
- contrast: the SAVED sticker caught mid-fade (its words at 5–10:1 when shown), the event's
  speaker plate (the lint samples the city beside the plate; the plate measures 11–12:1), the
  raid's disabled Continue (ink on its filled plate, 10:1 measured), the receipt's dash rule,
  and the REBEL_CELL corp's legend glyphs (4.3:1: icons need 3:1, §3.7).
- clipped: the tutorial note (12 of 15 lines: it scrolls; a RichTextLabel's own scroll isn't
  seen by the lint) and the fight's subtitle pages ending in the "…" continued mark (a page of
  a longer line, by design, H23 S3).
- overlap (2.0 pad): the codex's MORE BELOW tag over its scroll's last line (by design), and
  the SAVED sticker over an event's story for its 2.5 s (the pad bar pushes it up; W2's
  `Toast.spot` doesn't avoid paper text; left as a gap).
- high contrast: the lint reads a button's 3 px HC edge as its background; every one of the
  180 measures ≥ 11:1 at its glyphs ("low confidence").


## What changed (files)

| Area | Files |
|---|---|
| A1 netrun hookups | `netrun_scene.gd` (watch_drops, route key on cycle_target + its prompt, START DEFENSE PLAY, corp pattern in the grid-zoom view) |
| A2 whole words | `ui_wrap.gd` (`whole_words`), 17 call sites in `scripts/ui/**`, `campaign_end_stage.gd`, `motion_lab.gd`; `polaroid.gd` (caption band), `spinner_view.gd` (hub name) |
| A3 subtitles | `dialogue.gd` (`_fit_page` floor, scroll, refit, `screen_entered`, ink speaker on paper), `subtitle_strip.gd` (empty band folds) |
| A4 flatline | `city_look_data.gd` + `city_look.tres` (`flatline` context, `lean` key), `city_state.gd`, `city_grade.gd` (`blended`), `city_atmosphere.gd` (`blend_context`, `clear_campaign_progress`), `cyberdeck_background.gd`, `run_end_stage.gd`, `campaign_end_stage.gd`, `hq_scene.gd`, `netrun_scene.gd`, `tools/schema_smoke_test.gd` |
| A5 settle hook | `page_transition.gd` (`settle_motion()`), both stages off `Typing.META` |
| A6 spinner / deck | `spinner_view.gd` (price on UPGRADE, marker circle, lettering, canvas fit, prompt bar), `deck_view.gd`, `inspect_popup.gd`, `loadout_view.gd`, `ui_motion.tres` + `ui_motion_data.gd` (`upgrade_circle_draw`) |
| A7 Modem | `netrun_scene.gd` (CARDS window in one column) |
| A8 lint | `tools/visual_qa/review_pack.gd`, `lint_report.py`, `capture_pack.py` |
| B1 2.0 | layout tests at `Settings.TEXT_SCALE_MAX` (`LayoutScales` removed); `title_scene.gd` + `icon_line.gd`, `hq_scene.gd` (START stack, map keys fold), `tutorial_overlay.gd`, `combat_scene.gd` |
| B2 wording | `combat_scene.gd`, `hq_scene.gd`, `loadout_view.gd`, `deck_view.gd`, `focus_tip.gd` |
| B3 prompts | `pad_prompts.gd` (compact, glyph alone), `drip_button.gd` (`set_key_action`), `combat_scene.gd` (fight prompt bar), viewers' bars |
| B5 contrast | `dialogue.gd`, `zine_note.gd` |
| B6 motion | `fx.gd` (jack cross-fade, no shake under reduce motion), `motion.gd` |
| B7 tracking | `ui_theme.gd` (`track_label`, `step_of`, Primary/HeaderLabel), `terminal_window.gd`, `crew_card.gd`, `case_file_card.gd`, `run_receipt.gd`, `campaign_end_stage.gd`, `codex_spread.gd`, `fx.gd`, `raid_playout_panel.gd`, `hq_scene.gd` |
| Tests | `tests/unit/test_art_w9f_sweep.gd` (24 tests) + updates in pass20/21/22, pass20 screens, w8d |

## ART_BIBLE §12 / §14 checklist

| Item (§) | Result | Evidence |
|---|---|---|
| §12 text scale 1.0–2.0: nothing clips, overlaps or truncates | **Pass** (layout tests) with gaps listed below | the 7 layout test scripts now run at `Settings.TEXT_SCALE_MAX` (`LayoutScales` removed; `test_every_layout_test_runs_at_the_text_scale_ceiling`); `sheet_2.0_mouse.jpg`, `sheet_2.0_pad.jpg`; lint below |
| §12 wheels ≥ 70% at 2.0 | Pass | W3's tests unchanged and green; the fight's pad bar sits in the status row (compact), the hand stays on screen |
| §12 greyscale / colour-blind | Pass | `sheet_1.0_grey.jpg`, `sheet_1.0_deutan.jpg`: HP and Heat carry numbers and words, corps their route pattern and landmark, raid results glyph + word (HOLDS / FELL), affordability lock + NEED n · HAVE m, card type by stock + HACK hatch, rarity pip, event outcomes ▲▼ + icon, slices glyphs |
| §12 reduce effects | Pass | `sheet_1.0_reduce_effects.jpg`: end states, no flash, the jack a cross-fade, FLATLINED / LOST end state at once |
| §12 reduce motion | Pass | `sheet_1.0_reduce_motion.jpg`; new: no shake (`Fx.shake_px`, `Motion.shake`), the jack cross-fades (no zoom), title pan held (W7), pages cross-fade (W9s); `test_reduce_motion_shakes_nothing` |
| §12 high contrast: opaque panels, 7:1 text, PaperInk on paper | Pass with low-confidence lint noise | `sheet_1.0_high_contrast.jpg`, `lint_report_high_contrast.md` (the contrast findings left are the lint reading a button's 3 px edge as its background: every one measures ≥ 11:1 at the glyph) |
| §12 pad: glyphs never bracketed letters, focus visible | Pass | a fight's prompt bar (glyphs) + SEND IT's drawn glyph, Deck/Spinner viewers' own prompt bars, Close never "[B]"; `test_pad_pages_speak_pad_and_show_their_prompt_bar`, `test_a_fight_has_a_pad_prompt_bar_and_glyphs_not_brackets` |
| §5.2.4 prompt bar on every page with a pad | Pass | title, slots, options, codex, stats, HQ, Grid, raid, route, combat (new), loot, Modem, events, run end, campaign end, pause, viewers (new): `sheet_2.0_pad.jpg` |
| §6.8 input-aware wording | Pass | every mouse-worded string goes through `UiTip.for_input` or a pad branch (`test_mouse_words_in_player_strings_go_through_for_input`); FocusTip swaps any left (`UiTip.pad_safe`) |
| §4.3 rule 2 (≥ caption) | Pass for Controls | lint font findings at 2.0 are custom-drawn-free; subtitle, status line, aim hint, tooltip shares, spinner lettering, Polaroid never go under caption × scale |
| §4.3 rule 3 (no mid-word breaks) | Pass | no `WORD_SMART` / `ARBITRARY` in `scripts/**` (tested); `UiWrap.whole_words` |
| §4.3 rule 4 (no text over text) | Pass with 2 known cases | lint overlap below |
| §4.2 tracking | Pass | `UiTheme.track_label`: Primary, HeaderLabel, window titles, dossiers, case files, receipts, codex headings, jack note, raid steps, campaign end paper |
| §3.7 contrast | Pass with lint noise | subtitle paper's speaker now ink; prompt bar has glass; remaining findings are "low confidence" (glyph pixel ≥ 4.5:1) |
| §5.3 ≤ 25% empty | Pass | Modem CARDS window in one column (`test_modem_cards_window_is_never_a_quarter_empty_in_one_column`) |
| §8 no full-screen flash below T4 | Pass | W6's tier gate unchanged; RE/RM sheets |
| §9 / §11 FLATLINED and LOST grey | Pass | the city's own `flatline` context covers the whole city (subtitle band, prompt strip); campaign end's scrim is one screen scrim (`test_run_end_greys_the_whole_city_and_hands_it_back`) |
| §14 static lint | Pass, lowered | `lint_baseline.json` 35 → 32 findings in 6 files |
| §14 review stills | Pass | this folder |


## Decisions

1. **Whole words (§4.3.3):** `UiWrap.whole_words` keeps a label at least as wide as its longest word (the component grows). Stepping the font down from the label's own width looped layouts (a resize changed the size that set the width), so a view that prefers a smaller step does it itself.
2. **Empty subtitle band (§5.2, §10.5):** one line while empty; it grows to two at big text when the first line comes and stays grown until the screen changes (one reflow per screen at most). Its dock keeps the full height, so paging is unchanged.
3. **Subtitle floor (§4.3.2):** a page never shrinks under caption × scale; a page still too tall scrolls in its label (following the typing); a page that no longer fits a new dock is paged again.
4. **Flatline (§9, §11):** an additive `CityLookData` context `flatline` (saturation 0, dim 0.35) and an optional grade key `lean` (share of the corp lean kept, default 1). `CityAtmosphere.blend_context(ctx, mix)` blends from the context in force and hands it back at 0. The stages grey through it when the screen gives them the city; alone (tests) they keep W8c's shader. Schema change logged; smoke test covers it.
5. **Campaign end scrim (W8d request):** one full-screen `GlassScrim` behind the HQ's whole UI while the end shows (a scrim inside the page can't reach past its ScrollContainer), the stage's own stands down.
6. **Settle hook (§10):** `PageTransition.settle` calls any `settle_motion()`; DripButton, RunEndStage, CampaignEndStage and SpinnerView use it. `Typing.META` is only typing's again, so ANIM-R5's `words_typing()` never sees a stage as words.
7. **Spinner viewer (§4.2, §6.6):** its lettering follows the text scale up to 1.3 (as W3's wheels) and divides by the scale the wheel is drawn at, so it reads at its step on screen; the hub name folds to two lines, then its first word condensed. The UPGRADE price is on the button ("UPGRADE · 150 CYCLES"); short, NEED n · HAVE m in `HARM`. The circle draws on with `marker_stroke` (`upgrade_circle_draw`, T2, 0.22 s; appended motion id).
8. **Viewers at 2.0 (§5.3):** the Deck and Spinner windows give up height (grid, then wheel scale ≥ 0.7) and then move up to stay on the canvas; the card detail sits under the subtitle band and its notes scroll.
9. **Pad in a fight (§5.2.4, §12):** a compact prompt bar in the status row (verbs at caption, 1.0 gaps; above 1.3 the Menu glyph alone), SEND IT draws its glyph, the Settings button gives way to the bar's glyph, stickers and nudge buttons drop "[LB]"-style letters. Switch verbs: TARGET / YOURS, INNER / OUTER.
10. **Viewers with a pad:** each viewer shows its own prompt bar (Select / Details / Close); its hint line is mouse-only.
11. **Wording (§6.8):** every mouse-worded tip has a written pad variant ("pick it up and move it"); `FocusTip` passes any tip through `UiTip.pad_safe` while a pad is in use (a tip built before the device changed).
12. **Tracking (§4.2):** `UiTheme.track_label` decides by face (Anton; Share Tech Mono only when the words are CAPS) and by the step the size lands in; the Primary and HeaderLabel theme variations are tracked.
13. **Reduce motion (§12):** no shake at all (it was reduce effects only) and the jack's zoom becomes the cross-fade.
14. **Map keys (§6.10):** the raid playout's and report's keys are the folding strip above 1.3 (the open key covered the verdict at 2.0).
15. **2.0 folds:** the title's Continue line folds its numbers under the lead; the new campaign's START / SHARE CODES stack from 1.8; the tutorial's Skip shortens before its buttons stack; the Polaroid photo shrinks so the floor caption keeps its band.
16. **Contrast:** the subtitle paper's speaker is ink (pink read 2.3:1); the pad prompt bar has glass behind it; the zine note's title is caption × scale in ink with its room following it.
17. **Runtime lint (W10 tool):** size judged on screen (font × every ancestor scale; a scaled subtree's override isn't judged against the steps); text under an open modal (kit modal group, pause, Options, viewers, card detail, full-screen scrims, the jack's cover) is left out of contrast and overlap; text is cut to its scroll view or clipping panel (the walk stops at a CanvasLayer); a label's own opaque box is its background.
18. **Tests:** W4's deck viewer caps cards at four a row, so pass21 now expects `DeckView.card_scale(2.0)` (1.83); pass20's SEND IT test expects the glyph, not "[X]".


## Still failing / known gaps

- **Custom-drawn text isn't linted** (wheels, cards, map labels, Heat poster, HUD values): W10's limit. Checked by eye on the sheets.
- **Lint noise left:** see "Runtime lint (final)" above; the one real item is the SAVED sticker lying on an event's story for 2.5 s at 2.0 with a pad.
- **The fight's status line** can still drop its key hints at 2.0 with keys (never cut: whole hints drop from the end; the pad bar has them all).
- **Combat in the standalone tutorial at 2.0** is tight: the note scrolls and the SAVED sticker can sit on the turn line for its 2.5 s.
- **Colour-blind modes** stay W9s' daltonize correction (not a per-token remap); the bible line ("remap") is still open with the designer.
- **Windowed-only proofs:** the flatline grade, the campaign-end scrim and the marker circle were checked in the review captures, not in headless tests (no renderer).

