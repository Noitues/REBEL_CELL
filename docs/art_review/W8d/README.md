# W8d — Campaign end, WON and LOST (branch `art/w8d-campaign-end`)

This pass covers ART_BIBLE §11 "Campaign end (WON / LOST)", §8 T4, §6.4, §6.6, §9.3, §12 and critique `62/63` and §9.
It is presentation only: no rule, content value or save format changed.

## Pictures

| File | What it shows |
|---|---|
| `before_after/campaign_{won,lost}_<combo>.jpg` | The W10 harness, before (`art-pass/docs/art_review/W10/baseline/full`), after, and a heatmap. There are 8 sheets: 1.0 mouse, 1.6 pad, 2.0 mouse and 1.0 greyscale. |
| `won_t4_strip.jpg` | The WON T4 (`campaign_end_lab.tscn --end=won`, 30 fps, every 300 ms). The landmark falls, the X is sprayed on stroke by stroke, the overspray settles, the city leans to the corp, CORP DOWN slams, the wall goes up, then the paper, receipt and actions. |
| `lost_t4_strip.jpg` | The LOST T4. The hexagon cracks from the top and splits, the city greys, CELL BURNED slams, and the wall shows one operative flatlined and one hurt. |
| `lint_report_after.md` | The W10 runtime lint over the after pack (all 6 combos, grey included). The only W8d findings are story lines scrolled out of the paper's view. The lint doesn't clip by scroll view, so they are false positives. The rest belong to `fx.gd` ("SAVED") and `dialogue.gd` (the band's "…"). |
| `campaign_end_art.jpg` | The baked art. The five landmark silhouettes in their corp hues, then in greyscale (the shape names the corp), then the Cell hexagon whole, cracked and cracked in grey, then the spray overspray. |

At 1.6 and 2.0 the page stacks and scrolls, and the actions sit right under the hero, so pad focus lands beside the verdict. The sheets are captured after merging W8b, with its one-row top bar.

## What changed (files)

- **New kit files:**
  - `scripts/ui/kit/campaign_end_stage.gd` (`CampaignEndStage`) builds both templates and plays the T4. It also handles layout by room, the SCRIM and the grey grade.
  - `corp_fall_art.gd` (`CorpFallArt`) is the corp billboard: its hue frame, `CorpPattern`, a falling baked landmark, and two `marker_stroke` strokes plus the baked overspray.
  - `cell_crack_art.gd` (`CellCrackArt`) is the Cell hexagon. Its crack reveals from the top, then the two halves part.
  - `stamp_overlap.gd` (`StampOverlap`) lays the stamp across the foot of the art.
  - `crew_wall.gd` (`CrewWall`) holds a taped, tilted Polaroid per operative and sets each expression.
  - `corp_glyph_field.gd` (`CorpGlyphField`) shows a corp's landmark glyph plus its ICE number on the receipt.
- **Art:** `assets/art/campaign_end/*.svg` holds 5 landmarks, the 2 hexagon halves, the crack and the overspray. All are white or grey, tinted at runtime. Their `.import` files are force-tracked at 2x. The generator is `tools/art/w8d_svgs.py`; `render_w8d.gd` and `w8d_sheet.py` build the review sheet.
- **`scripts/ui/hq_scene.gd`:** only the body of `show_end()` changed. It uses the same sources as before: `revealed_beats`, the profile, `ice_records_text()` (now the receipt's tooltip) and the two actions. It still calls `_set_panel(stage, "end")`, then clears the glass on the panel host, wires `city_lean` to `set_campaign_progress`, and plays the T4.
- **Motion:** `content/config/ui_motion.tres` gains `campaign_end_won` and `campaign_end_lost` (T4, 2.4 s, stamp amplitude 2.2). They are also added to `REQUIRED_IDS` and to the motion lab's DEMOS.
- **Captures:** `tools/design_lab/campaign_end_lab.tscn` for Movie Maker.
- **Strings:** `assets/text/strings.csv` has 5 appended keys.
- **Tests:** `tests/unit/test_art_w8d_campaign_end.gd` (11 tests, fast tier, in the manifest).

## ART_BIBLE §14 checklist

| Item | Result |
|---|---|
| §3/§4/§5 tokens only | **Pass.** The static lint shows 0 new findings. Colours come from `Palette`, sizes from `UiTheme` steps × text scale, and timings from `ui_motion.tres`. |
| Materials not mixed | **Pass.** PAPER pieces (story, receipt, Polaroids, stamp) sit taped over the city. The buttons are GLASS. The billboard is a CITY object sprayed by the Cell. |
| Focal order / one primary | **Pass.** The order is stamp and art, then the wall, then story and records, then actions. New campaign is the only Primary (tested). |
| Six states | **Pass** through the kit buttons. The rest is display only. |
| 1.0 / 1.6 / 2.0 | **Pass.** There is no clipping, overlap, text under 12 px or overflow past the width, for both templates at all 3 scales (tested). |
| Contrast §3.7 | **Pass.** Paper text is INK. The stamp sits over a SCRIM-dimmed, blurred city. |
| Greyscale | **Pass.** The corp reads by landmark shape and pattern, and the verdict by its word and art (a sprayed X versus a split hexagon). LOST is grey. See the grey sheets. |
| Pad | **Pass.** The prompt bar shows, and focus starts on New campaign (tested). |
| Motion / tiers / reduce effects | **Pass.** T4 runs 2.4 s, skippable with any press. A page settle ends it, and reduce effects gives the end state at once (tested). There is no flash. |
| No placeholder / leftovers | **Pass.** The city shows behind the stage, and the MORE BELOW tag fades with the paper. |
| Review stills | **Pass** (this folder). |

## Decisions (one line each)

1. §11: WON's "corp landmark falling" is a billboard (hue frame, `CorpPattern` at 35%, a baked silhouette) whose landmark tips 20° over its right foot and sinks 10%. That keeps the shape readable in the end state.
2. §11: the "spray" is two W6 `marker_stroke` strike-throughs at ±48° in CELL_PINK, drawn one after the other. The baked overspray and drips fade in over the last 20%.
3. §3.6: the landmark silhouettes are new 200×300 SVGs in white and greys, tinted at runtime. W8a's 48 px glyphs stay the receipt's icons.
4. §11 LOST: the Cell's hexagon is the ring with an upward chevron (the landmark glyph's "inverted" mark turned right way up). The crack is INK, revealed from the top, and the halves part 9 px each way with a 4° tilt.
5. §6.6 / §3.3: CORP DOWN is GAIN and CELL BURNED is HARM, both at the hero step, as W8c's verdicts. The word and the art carry the meaning without colour.
6. §11 LOST grey: I reuse W8c's desaturate-and-dim shader (`RunEndStage.GRADE_CODE`, amount 1, dim 0.35). A W7 grey context would mean editing W7's files, so it isn't cleanly additive.
7. §2 CITY: a full-stage GlassScrim (blur + SCRIM) sits over the city, behind a BackBufferCopy so that LOST's grey reaches it. Without it, the stamp met the lit city at under 3:1.
8. §9.3: WON leans the city from its current progress to 1.0 toward the corp over the sequence, through the `city_lean` signal (the screen calls W7). New campaign sets it back to 0.
9. §11 crew wall: on WON the living are TRIUMPHANT; on LOST they are HURT. The dead are FLATLINED either way. Tilts come from a fixed list within ±4°, each with a tape strip. The caption is the name, with the full name in the tooltip.
10. §4.2: story text is folded at word boundaries to ≤ 70 characters (`UiTip.fold_to`). Plex runs narrower than its "n" column, so a 70-"n" width let about 85 characters through.
11. §5.3: side by side at 1.0, a long story scrolls inside its paper. Stacked (1.6 and 2.0), the page scrolls and the paper shows all its words, so there is never a scroll inside a scroll.
12. §6.4 / §12: when the page stacks, the actions move directly under the hero, so pad focus lands next to the verdict.
13. §12: the records use icon + number fields (WON, CLOSE and ICE StatFields). Each corp's best ICE sits by its landmark glyph (tooltip: the name). Then "NEXT CAMPAIGN: UP TO ICE n" and the existing "Something opens…" line. The full sentence from `ice_records_text()` is the tooltip.
14. §8 T4: one tween drives a single time value, and every piece is set from it (`_apply(u)`). A skip, a settle and reduce effects therefore all land on `_apply(1)`.
15. §5.2 / §5.3: at 1.0 the whole page fits the screen with no page scroll, with mouse and with pad. The screen hands the stage its prompt bar (`foot_bar`) and the stage keeps clear of it (tested). To fit, the art is 208×216 (the hexagon 192×208), the page margins and row gaps use `SP_M`, and the story's floor is FitScroll's minimum view.
16. §6.4: when the page stacks, the two actions sit side by side, so the focus scroll shows both and the page's MORE BELOW tag never lands on Back to title.

## Couldn't do / known gaps

- The grey grade and the scrim cover the page area only. The subtitle band and the prompt strip keep the city's colour, as in W8c.
- The city lean stays set explicitly after the page (W7 has no "unset"). New campaign sets it to 0. **Request (W7):** `CityAtmosphere.clear_campaign_progress()`.
- The lab's bake wait doesn't hold the first frame: the strips' frame 0 shows the city before its bake lands.
- `main` has ANIM-R5's own `show_end` (the "see-through campaign end" with a ForecastStamp verdict, `81f1a5f`). When art-pass merges to main, keep this stage.

## Bible rules I'd question

- §8 "T4 becomes a cross-fade" under reduce effects: as W8c says, the stage shows its end state and the page's own cross-fade brings it in.
- §11 doesn't say where the stamp goes on WON. A billboard needs a scrim to stay readable over a lit city, so §2's scrim rule should mention full-screen stages as well.
