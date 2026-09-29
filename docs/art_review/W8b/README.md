# W8b: HQ, new campaign, Grid, raid, maps, top bar (branch `art/w8b-hq-grid`)

ART_BIBLE §2 DECK, §5.2–5.3, §6.4–6.10, §10.2, §11 (HQ, New campaign, City Grid, Raid,
Route), §12. Presentation only: no rule, content value or save format changed.

## Pictures

| File | What it shows |
|---|---|
| `before_after/<screen>_<combo>.jpg` | W10 harness, before (`art-pass/docs/art_review/W10/baseline/full`) and after (commit `1a89c7e`). Screens: hq, hq_black_market, hq_crew, hq_loadout_deck, hq_loadout_spinner, new_campaign, new_campaign_picker, grid, grid_site_selected, grid_raid_pending, grid_meridian / halcyon / orbital / rebel_cell, raid_setup, raid_playout, raid_result, raid_report, route. Combos: 1.0 mouse, 1.6 pad, 2.0 mouse, plus 1.0 greyscale for the seven grids (64 sheets). |
| `diff_report.md` | The changed-pixel share of every sheet, largest first. |
| `ring_swap_strip.jpg` | A Rank 3 ring swap (`tools/design_lab/w8b_strips.tscn --mode=ring_swap`, 100 ms steps). The swapped segment fills, recolours in FOCUS, is named, and pulses twice. |
| `crew_stamp_strip.jpg` | An operative picked on the Site card (`--mode=crew_stamp`). The picked Polaroid gets the pink edge and JACK IN plug stamp and rides beside JACK IN. |
| `lint_report_after.md` | W10 runtime lint over the after pack (see "Lint left" below). |

## What changed (files)

- **`scripts/ui/kit/hud_stats.gd`, `hud_bar.gd` (top bar):**
  - one row at every scale, with a height set by the scale alone;
  - tags share the width evenly (100–132 px) and each value steps title > label > body > caption;
  - labels and captions fold into the tooltip from 1.3;
  - the title and VIEW LOADOUT fold;
  - FOCUS brackets on CARDS and DAEMONS while a matching item is carried (`watch_drops`);
  - a fight's bar fits its values by the digits' height.
- **`subtitle_strip.gd`:** one line at 1.0, two above.
- **HQ** (`hq_scene.gd`, new `deck_frame.gd`, `deck_monitor.gd`):
  - the full DECK frame (bezel, keyboard row, cables);
  - a CRT Grid monitor with amber readouts;
  - focal order JACK IN > monitor > WANTED > crew;
  - crew in 3 columns (2 at big text);
  - the pending raid shown on one line.
- **Black Market:** RECRUIT / BOOSTS / UNLOCKS groups, each item with an icon and a price tag. Locked items use W2's disabled look, with the reason in TEXT_MID.
- **New campaign** (new `planning_picker.gd`):
  - corporation dossier tiles, home and class tiles with locks;
  - an ICE Stepper;
  - seed and share code in a folded GLASS drawer;
  - one primary, START;
  - no native OptionButton, SpinBox or LineEdit.
- **Loadout** (`loadout_view.gd`, new `ring_swap_mark.gd`):
  - one modal size and place across the DECK and SPINNER tabs, over a full scrim;
  - the wheel scales to fill;
  - swap chips wrap whole words, set against the wheel's scale so they read at the caption floor;
  - RingSwapMark plays on a swap.
- **Site card** (`crew_chip.gd`):
  - Polaroid chips pick the operative, with a stamp and a rider;
  - a node tile picker;
  - a fixed card height;
  - one primary per Grid state.
- **Maps** (`city_map_overlay.gd`, `grid_map_view.gd`, `netrun_map_view.gd`, `route_legend.gd`, `legend_spot.gd`, `map_legend.gd`):
  - 28 px nodes and defences;
  - GLASS label pills with leaders and a clear gap;
  - threat routes drawn in CorpPattern dashes;
  - tokens only (23 literal colours removed);
  - YOU ARE HERE is a tab on the pin;
  - the route key folds from 1.3 and never scales under the floor.
- **Raid** (`raid_playout_panel.gd`, `raid_verdict.gd`, `raid_fx_layer.gd`):
  - the stamp reads LIVE, then RESULT;
  - Continue shows as locked;
  - losses in HARM and holds in GAIN, each with an icon and a word;
  - START DEFENSE is the setup's primary and stays on the first screen at 1.0 / 1.6 / 2.0;
  - the layout switches at 1.3 and 1.8;
  - hits on home that land together fly as one number.
- **Tests:**
  - `tests/unit/test_art_w8b_screens.gd` (24 tests);
  - layout tests for these screens raised from `LayoutScales.VERIFIED_MAX` to `Settings.TEXT_SCALE_MAX`;
  - older tests updated where they asserted the replaced looks.
- **Other:**
  - `strings.csv` (appended);
  - `lint_baseline.json` (lowered);
  - `review_pack.gd` (the picker screen);
  - `ui_wrap.gd` (WORD instead of WORD_SMART).

## ART_BIBLE §14 checklist

| Item | Result |
|---|---|
| Tokens / steps / spacing | **Pass**: the static lint is 0 in hud_bar, hud_stats, city_map_overlay, grid_map_view, raid_playout_panel and netrun_map_view. |
| Materials not mixed | **Pass**: DECK frame and CRT (DECK), top-bar tags and chips (PAPER), map pills and drawers (GLASS), city (CITY). |
| Focal order / one primary | **Pass** (tested): START; JACK IN, or RAID SETUP while a raid is pending; START DEFENSE; the locked Continue. |
| Six states | **Pass**: through the W2 kit (TilePicker, Stepper, CodeField, buttons, chips with focus brackets). |
| 1.0 / 1.6 / 2.0 | **Pass** (tested, all screens): no clipping, overlap, cut words or text under 12 px. Pages scroll with MORE BELOW at big text. |
| Contrast §3.7 | **Pass**: locked market items at 4.5:1; high-contrast drawing in the tags, chips, monitor, pills and route key. The remaining lint entries are listed below. |
| Greyscale / scrambled | **Pass**: outcomes by icon and word; corps by CorpPattern; stats by icon plus number (see the `_1.0_grey` sheets). |
| Pad | **Pass**: prompt bar; Settings drops its bracketed key while a pad is active; focus brackets. |
| Motion / reduce effects | **Pass**: ring swap and stamp within §10.2; reduce motion skips the Grid lean; the modal fades through PageTransition. |
| No placeholder / leftovers | **Pass**: the empty-armory note is designed; no stacked flying numbers. |
| Review stills and strips | **Pass**: this folder. |

## Lint left in W8b files (after pack), judged not real

- **`deck_monitor` MonitorTitle and readout under the Loadout modal:** the modal sits over the page by design, and the contrast is measured through the blur scrim. The readout reads at 16:1 on the monitor itself.
- **`hq_scene` PlayoutContinue contrast:** the lint takes the font colour against the page behind, not the button's own stylebox (measured 10:1, low confidence).
- **`hud_bar` VIEW LOADOUT on hq_black_market:** the other element is PirateRadio text scrolled out under the page's clip.
- **`map_legend` on raid_result (1.6 and 2.0):** the home-hit number crosses the key while it flies to the top bar. The overlap is transient.
- **`map_legend` swatch glyphs on grid_rebel_cell:** the swatch is REBEL_CELL red (#E8141E, kept by §15). It is a colour sample; the words carry the meaning.
- **Swap chips "font override is not a step":** the chips sit in the scaled wheel, so their override is the step divided by the wheel scale. On screen they read at exactly the step (tested).

## Decisions

- **§6.9:** the top bar is always one row. Values step down instead of wrapping; labels fold into the tooltip from 1.3.
- **§5.2:** the subtitle band is two lines above 1.0, so pages show whole sentences.
- **§2 / ruling Q4:** the HQ gets the full DECK frame. Other pages drop it and dim the city (map mode).
- **§5.3:** the raid setup re-lays out at 1.3 (loadout to the side column) and at 1.8 (START DEFENSE inside the raid card).
- **§4.3.3:** wrapping is whole words only (WORD), including UiWrap. A chip grows rather than breaking a word.
- **§11 City Grid:** the raid map shows no tier pips. Its zoom floor is 0.36, or 0.2 at big text.
- **§10.2:** simultaneous home hits merge into one number carrying their sum.

## Couldn't do / gaps

- The empty subtitle band is tall at 2.0 (two lines are reserved).
- Raid fits at 2.0 work but with tight margins.
- The paper inks (`HARM_INK` / `GAIN_INK`) were not needed: no W8b paper piece carries HARM or GAIN words.

## Bible questions

- §4.2: the lint could measure on-screen size for scaled subtrees (wheel chips) instead of the override.
