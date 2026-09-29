# Art pass: final report (M13, branch `art-pass`)

**Date:** 2026-09-29. **Governing documents:** `docs/ART_BIBLE.md` and `docs/ART_PLAN.md`. The per-workstream detail is in `docs/art_review/W<n>/`, and every decision is in `docs/DECISIONS.md` under "Art pass …".

## Result
- **All workstreams merged into `art-pass`:** W1–W7, W8a–W8d, W9s, W9F, W10, and WF (the kit follow-ups). Nothing is merged into `main`; the designer merges `art-pass` later.
- **Checks on the final commit:**
  - full suite: **1414 tests, 0 failing** (the baseline had 1094);
  - schema smoke test: PASS;
  - content validation: PASS.
- **Final capture:** 318 pictures of **53 screens**, 0 failed and 0 Godot errors. They cover the baseline's five combinations (1.0 mouse, 1.0 grey, 1.0 with reduce effects, 1.6 pad, 2.0 mouse), and the diff is against the W10 "before" pack.
- **Critique coverage:** all 28 finding groups in `VISUAL_CRITIQUE.md` are done. The table is in `ART_PLAN.md` §6.2.
- **ART_BIBLE §14:** every item passes. The per-item table with evidence is in `W9F/README.md`.

## Runtime lint on the final pack (`lint_report_final.md`)

| combo | screens | font | overlap | clipped | contrast |
|---|---|---|---|---|---|
| 1.0 mouse | 53 | 0 | 0 | 2 | 10 |
| 1.0 mouse, reduce effects | 53 | 0 | 1 | 2 | 5 |
| 1.6 pad | 53 | 0 | 0 | 2 | 6 |
| 2.0 mouse | 53 | 0 | 0 | 3 | 8 |

For comparison, the W10 baseline had 33–36 font and 34–71 overlap findings at 2.0, and `terminal_window` alone had 1,280 font findings.

The remaining contrast findings are mostly marked "low confidence" by the lint: a mid-fade SAVED sticker, button edges, and a map-key swatch. The "clipped" ones are the codex's MORE BELOW tag over its last line, which is by design.

Text drawn by a script's own `_draw` can't be seen by the lint, so it was checked by eye on the sheets.

## What to look at
- `gallery/`: before | after pictures of 22 key screens at 1.0 mouse and at 2.0 mouse. Start with:
  - `combat_start`, `hq`, `loot`, `modem`, `event`;
  - `run_end` (FLATLINED), `campaign_won`, `campaign_lost`;
  - `slots`, `codex`, `stats`.
- `sheets/`: contact sheets of all 53 screens in each final combination.
- `diff_report.md`: every picture's changed-pixel %.
- The full-resolution final pack is local only (git-ignored): `docs/art_review/FINAL/full/` and `diff/`, in the `art-pass` worktree.

## Headline changes (the critique's "embarrass in a trailer" list)

| Critique | Now |
|---|---|
| Full-screen magenta and green flashes | Gone. The flashes are wheel-local T3 bursts, and no full-screen flash is allowed below T4 (tested). |
| Empty black FLATLINED screen, text-only campaign won | Staged T4 screens: a flatlined Polaroid, a grey city and a hero stamp. WON and LOST each have their own template. |
| Flat placeholder city | A silhouette pre-render, then the lit city: glow, haze, wet streets, and Heat and territory reactions. |
| "42⁶42" and "12 → 6 = −3" | One number per hit, placed clear of the HP, with "(12 capped)". The net line under HP equals the real result. |
| Faded magenta Continue | A locked disabled state: `DISABLED` edge, lock badge, 4.5:1 label. |
| Debug-looking forms | Case-file slots, a planning-table new campaign, and tile, stepper and code fields everywhere. There are no native dropdowns left in any screen. |
| Text-only cards | A riso illustration stand-in on every card, rarity shown by stock, holo foil, and no truncation. |
| Classes looking like pairs | Eight silhouettes, eight accents and eight bezels, all pairwise distinct (tested). |
| Orbital and REBEL_CELL grids looking unthemed | Orbital is now #7FA8FF. Every corp has a pattern and a landmark, which carry through in greyscale. |

## Accessibility (§12)
- **Text scale:** up to 2.0 on every screen, with every layout test run at 2.0.
- **Colour:** colour-blind correction (deutan, protan, tritan), and a high-contrast mode (including a paper rule).
- **Motion:** reduce motion and reduce effects are separate settings.
- **Pad:** drawn pad glyph sets that auto-detect the pad, a prompt bar on every page, and input-aware wording.
- **Resolve speed:** 1×, 2× or instant, with hold-to-fast-forward.

## Art assets and briefs
- **Painted-art briefs:** 47 for cards and 24 for characters, in `docs/art_briefs/`.
- **Pixel-art concepts** (not game assets): `W4/concepts/` and `W5/concepts/`.
- **Baked SVG art:**
  - the logo, the NEVER SLEEP and TRUST NO ONE scrawls, and the MODEM sign;
  - corp landmarks and the campaign-end pieces;
  - generators in `tools/art/`.

## Open for the designer
The list is in ART_BIBLE §16, items 5–11:
- the colour-blind "remap" vs "correct" wording;
- the §8 duration column;
- T0 timing vs the FLAGGED flicker;
- the combat dim;
- handwriting at 16 px;
- the focus-scale and disabled-colour wording;
- city performance: +12–23% frame time, about 200 fps worst case at 1080p, and the Steam Deck not yet measured.

Also:
- The toast can sit over an event's story at 2.0 with a pad.
- The unmerged `main` branches, ANIM-R5 netrun and ANIM-R5 city, overlap several files. The resolution notes are in DECISIONS under W7, W8c and W8d, including "keep `CampaignEndStage`" and "keep `RunEndStage`".
