# WF: kit follow-ups

Branch `art/wf-kit-followups` (from `art-pass`). Presentation only: no rules, content values or save formats changed. The one settings addition (`city_quality`) is an additive key; old settings files load unchanged.

## Review images

Each image shows the **before** (`art-pass` at `81e9bbb`) above the **after**. They're drawn by `tools/design_lab/wf_kit_lab.tscn` at reference pixels.

| File | Item |
|---|---|
| `item2_tiles_1.0.png`, `item2_tiles_2.0.png` | TilePicker with the longest corp, class and home-server names |
| `item3_stickers_1.0.png`, `item3_stickers_2.0.png` | RESPIN / UNDO stickers with the growth cap on (`max_share` 0.2 of 1280 px) |
| `item4_polaroids_1.0.png`, `item4_polaroids_2.0.png` | Polaroid captions: combat 110×134 and crew compact 60×74 |
| `item7_paper_hc_1.0.png`, `item7_paper_hc_2.0.png` | Case file, receipt, badges, Polaroid and toast in high contrast |

The "before" receipt has no Cycles/banked row. That was a real bug: `RunReceipt.fields` called `String(int)` and raised a script error on the Stats page's run history. It is fixed in item 7.

## What changed (files)

| # | Item | Files |
|---|---|---|
| 1 | FitScroll / ScrollHint degenerate frames | `fit_scroll.gd`, `scroll_hint.gd` |
| 2 | TilePicker names wrap at word boundaries | `tile_picker.gd` |
| 3 | StickerButton growth cap (opt-in) | `sticker_button.gd` |
| 4 | Polaroid caption always fits | `polaroid.gd` |
| 5 | `CombatFxLayer.stamp(..., icon)` | `combat_fx_layer.gd` (`stamp()` and its draw only) |
| 6 | `Palette.HARM_INK` / `GAIN_INK` | `palette.gd`, `ART_BIBLE.md` §3.3; `case_file_card.gd`, `toast.gd` use them |
| 7 | High contrast on custom-drawn paper | new `paper_ink.gd` (`PaperInk`); `case_file_card.gd`, `run_receipt.gd`, `achievement_badge.gd`, `polaroid.gd`, `toast.gd`; `ART_BIBLE.md` §12 |
| 8 | Steam Deck city quality tier 1 | `settings.gd`, `city_atmosphere.gd` |
| 9 | Tracking in px per type step | `ui_theme.gd`, `ART_BIBLE.md` §4.2 |

- **Tests:** `tests/unit/test_art_wf_kit.gd` (fast tier, 18 tests).
- **Lab:** `tools/design_lab/wf_kit_lab.gd/.tscn`.

## ART_BIBLE §14 checklist (for what WF touched)

| Check | Result |
|---|---|
| §3–§5 tokens only | **Pass.** The new tokens are `HARM_INK`, `GAIN_INK`, `PAPER_STOCKS`, `TRACKING_PX` and `PaperInk.EDGE_PX`. The static lint baseline is unchanged: 0 up, 0 down. |
| Materials not mixed | **Pass.** Paper stays paper in high contrast (§12 line). |
| Focal order / one primary | Not affected. |
| Six states | **Pass.** TilePicker and StickerButton keep every state; the tile state logic is unchanged. |
| 1.0 / 1.6 / 2.0: no clip, overlap, truncation, mid-word break, < 12 px | **Pass** for tiles (every corp/class/home name), stickers (the words are laid out on the paper, clear of the icon) and Polaroid captions (every class, ranks, names, four frames). All are tested. |
| Contrast §3.7 | **Pass.** Paper inks are ≥ 4.5:1 on four stocks. High-contrast paper words are 7:1. The badge outline is 7:1 on black. |
| Greyscale / scramble | Not affected. HARM_INK and GAIN_INK are always paired with a word or glyph, as before. |
| Pad | Not affected. |
| Motion / VFX tiers | Not affected. The stamp icon uses the same `status_stamp` timing. |
| No placeholder / empty panel | Not affected. |
| Review stills | Captured here (`docs/timeline/` is the orchestrator's). |

## Decisions

1. **FitScroll (§5.3):** a content height above `MAX_VIEW_PX` × text scale counts as a pre-layout measure.
   - The view keeps its last good height.
   - It re-measures on the next frame, up to 3 times. It then clamps to 4096 px × scale.
   - ScrollHint ignores views that are that tall, and caps its row snap at one row's share.
2. **TilePicker (§4.3 r3):** each name gets up to 2 lines, at label, then body, then caption. After that the tiles grow; all tiles in a picker share one size so the grid stays even.
   - The size step is chosen per tile, so a long name can be a step smaller than its neighbours.
   - Meta and unlock lines wrap at caption.
3. **StickerButton (§12):** `MAX_SHARE` is 0.2 of the container, which is the page width by default.
   - The lettering yields to caption at the current text scale, then the scale is walked down to 1.0. The sticker's height, padding and icon follow the lettering.
   - The cap is **opt-in** (`max_share`). Combat's hand takes the width the stickers leave: with the cap on, the hand grew to 1.28 and the wheels fell to 84 px against an 87.6 px floor at 2.0 (`test_art_w3_wheels`). So combat must switch the cap on together with a hand-scale ceiling (see Requests).
4. **Polaroid (§4.3, W5):** the caption steps from label to body to caption, then abbreviates.
   - Abbreviation: `RANK n` becomes the W5 `tr("R%d")` form, and a name becomes its first word plus initials. One word stays whole.
   - If it still doesn't fit, it is condensed to 70% width, then scaled to the band, never below 12 px.
5. **Paper inks (§3.3):** `HARM_INK` #AB2E22 and `GAIN_INK` #396739 are the screen hues at 67% and 46%. They meet ≥ 4.8:1 on PAPER, PAPER_ALT, NOTE_PAPER and NOTE_YELLOW. STICKER_PINK is not covered (4.2:1).
6. **High contrast on paper (§12):** the new bible line says PAPER keeps its stock colour.
   - Words go INK. Edges are 2 px opaque INK. Tape and fills are made opaque over their stock.
   - The unearned badge's outline is `TEXT_MID`, as HighContrast does for disabled items, and its lock disc is opaque black.
7. **Deck (§13):** `Settings.city_quality` defaults to -1, which means the look's default. A Deck's first run sets it to 1. A design tool's `CityAtmosphere.quality` still wins.
8. **Tracking (§4.2):** the value is the table's px × text scale, rounded, and never below the 1.0 value. `UiTheme.tracked()` returns cached FontVariations. No view uses it yet; owners adopt it with their type.

## What I couldn't do

- **Combat call sites (items 3, 5, 6):** `combat_scene.gd` and `outcome_row.gd` aren't mine. The changes are listed in the report.
- **CrewCard high contrast:** CrewCard (W5) still turns its dossier black in high contrast. The new §12 line says paper keeps its stock. The switch is listed in the report.
- **The item 1 crash:** I couldn't reproduce the crash itself headless. The degenerate frame is reproduced (a 31,016 px view) and bounded. A GPU-side crash from a view that tall (glass blur / texture limit) would need a windowed run to confirm.

## Bible rules to revisit (not changed)

- §3.3: STICKER_PINK is too dark for the paper inks at 4.5:1. If a sticker ever carries harm/gain text, it needs `INK`.
- §12: "TEXT_HI on #000" applies to glass only. The PAPER line added here should be read as its exception.
