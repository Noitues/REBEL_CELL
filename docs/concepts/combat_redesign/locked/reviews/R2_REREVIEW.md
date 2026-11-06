# AD re-review, rebuild round 2 (art-pass commit 403e9ade)

Reviewer: independent AD (this session). Date: 2026-11-04.
Snapshot reviewed: `D:/rc_scratch/review_snapshots/r2_403e9ade/` (read only; the live tree was not opened).
Judged against: VISUAL_PLAN.md DR-1..DR-10, ART_BIBLE 2.4 / 3.14 notes, the art-pass calls C1-C18 in REVIEW_RESPONSE.md "Round 2".
Opened at 1x or closer: `final/` p1, p2, p2b, p3, nowords (neutral), p1 Solace, p1 Meridian, `grey_proof.jpg`; `hover/contact_sheet.jpg` and h02, h03, h04, h05, h08, h09, h11 at 1x; `transitions/t05`, `t06`; `backdrop/before_after.jpg`. The other skin plates were covered by measurement, not by eye.
Effects: `effects/` is byte-identical to the round-1 snapshot (md5 of all 9 sheets, the beat strip, the GIF and the strips folder match). I reviewed every one of those sheets in R1, so they were not re-opened.
Measurements: my own probes on the snapshot PNGs (`r2m1.py`, `r2m2.py` in the session scratchpad).

## Gate verdict

**S1: 0. S2: 1. S3: 11.** This meets the designer's exit rule (no S1, fewer than 3 S2).

The one S2 is the effects set, which is still the round-1 render on the round-1 board. It is a mechanical re-render, not a design problem. I would not post A-116 or fold the bible draft until it lands, and it needs only a spot check of the effects sheets afterwards, not another full round.

I tier the h02 Brace hover lower than art-pass's own gate did (S3, not S2). Reason below.

## My six R1 S2 items

| R1 S2 | R2 status | My read on the r2 plates |
|---|---|---|
| 2.5 board pencil (p2 / p2b) | FIXED | p2 at y 825: 6 px wax between 2 px ink edges plus blend, about 13 px whole stroke. p2b arc: 7 px wax rows. PLAN px on p2 doubled (7573 → 15050). X caps are the same stroke. It reads as grease pencil at 1x |
| 2.6 h02 hand collision | **Residual, S3** (see below) | Fan no longer closes; all four titles and costs legible |
| FOCUS on p2b in leaf green | FIXED | 276 px of #D4FF00 in 4 separate components, 0 px of #96FE46, on all three skins |
| Bezel glyph discs and 1 px lines above HOT | FIXED | Cube-disc box (x 970-1000, y 555-585) p95 100 → 85.3. Frame band r 480-520: 0 px at L* 95 or more. The 470 px at L* 95+ inside r 480 are HOT cores |
| TWIST render-order bug | FIXED | `final/checks.json` `c14_determinism`: three renders in one process, registry intact on each step |
| Hover HUD 45 px taller | FIXED | Bill plate edge rows 77-78 and 425-426 on board p1, p2 and on h02, h04, h11 |

## Original findings

Unchanged from R1 unless listed here.

| # | R1 status | R2 status |
|---|---|---|
| 1.1-1.5, 1.7, 1.8 | FIXED / DOC | FIXED / DOC (hold on the r2 plates) |
| 1.6, 2.10, 2.11, 3.10 | FIXED | FIXED on the round-1 effects set; the set is not on the round-2 board (S2 below) |
| 1.3 Corp hue on a ring | DOC (DR-6) + FIXED | DOC + FIXED. Solace rim is now a celadon/teal rope; Meridian a rust hatched band |
| 2.5 Pencil | NOT FIXED | FIXED |
| 2.6 Hand collisions | NOT FIXED (h02) | Residual S3 (h02) |
| 2.14 Tickets | W5 step missing | FIXED; W6 / W5 / W4 edges step visibly at 1x |
| N1 Titles clipped | S3 | FIXED on p2 and 22 hover plates; h02 residual |
| N2 Solace rim green | S3 | FIXED (teal; no green on the rim at 1x) |
| N3 h04 halo on the frame band | S3 | FIXED; the halo sits on rings +1 and +2 only |
| N4 Flash limit / T6 pull-out | S3 | Flash FIXED (2 per second). T6 holds on the room (S3 below) |
| N5 Corp theme colour-only in luma | note | FIXED; the unwrapped rim strip on `grey_proof.jpg` shows a light twisted rope against a dark fine-striped band |

## Open items, tiered

| # | Item | Tier | Class | Note |
|---|---|---|---|---|
| R2-1 | Effects not re-rendered on the round-2 board; SKIP hint (C12) unpublished | **S2** | IMPL | The package has two boards. The effect bases carry the leaf Solace rim, the old pencil and the old HUD rows, and the Solace scan line in `fx_wave_enter` / `fx_grow` is still #96FF46, which C16 retired. Re-render all sheets, strips, the beat strip and GIF on the round-2 board, publish the SKIP tab, re-run the loudness and layer checks |
| R2-2 | h02 Brace (slot 0) hover | S3 | DOC+IMPL | At 1x the Spin 3 cost digit and full title are legible on all four plates; what is covered is a sliver of the hex facet and the title band's black end. No information is lost, which was the original finding. What remains is a rule problem: slot 0 lifts about 10 px while every other slot lifts about 190 px. That needs a designer pick, not another render pass (question 1) |
| R2-3 | FOCUS L* 94.1 vs the HOT p95 94.9-95.4 (C3 conflict) | S3 | DOC | FOCUS cannot be on-token and 1 under HOT. Recommendation: name FOCUS as the third mark allowed above the tower (SEND IT, HOT, FOCUS). It is 2-3.5 px of corner bracket, never a fill |
| R2-4 | White burst cores on h03 / h05 / h09 | S3 | IMPL | The 1.2 call set the hit star to `HIT_PAPER` L* 86. Use it on the hover bursts too |
| R2-5 | Side-arc HOT cores 2.0-2.5 px (C11) | S3 | IMPL | 2-4 small marks per plate where the lane line crosses them |
| R2-6 | T6 holds on the room; the room-to-street hand-over is not drawn | S3 | DOC+IMPL | DR-10 says "back to the netrun". The sheet's FEEL line still says "you are on the street" while K4 is the room. Fix the text now; the hand-over is question 2 |
| R2-7 | UNDO / SEND IT sit 4 px further right on hover plates than on the board | S3 | IMPL | One constant (board 12, hover 16). Pick one |
| R2-8 | h03 gun tracer dE 3.8 from CELL_PINK (limit 3) | S3 | IMPL | Trivial |
| R2-9 | h11 HOT fill dimmed inside the lit area | S3 | IMPL or DOC | Either the lit landing slices keep their HOT marks at full value, or the hover key says they dim |
| R2-10 | h08 Hold: pencil on the frame band, plus an unkeyed yellow arc on the lower-left rim | S3 | DOC or IMPL | Hold acts on the schedule and the clock lives on the rim, so the rim arrows are defensible. Say so in the hover key and key or remove the lower-left arc |
| R2-11 | `corp/src` plain render path differs from the capture-hook path (lane line under the translucent fill, up to 48/255 at r 430-460) | S3 | IMPL | One source of truth. The port will follow one path; make them agree before the port spec is frozen |
| R2-12 | Pencil wax measures 6.0 px against a 7 px spec | S3 | DOC | Restate A.5 as measured (6 px wax, 3.5 px ink a side, 13 px whole) or widen the wax by one |

Accepted costs, not findings:
- The reserved option rows leave about 90 px of empty bill on p1, p2b and nowords. That is the price of a HUD that does not move on hover, and I recommended it.
- The lifted card is now at 1.00 zoom. It still reads as lifted through its height and pink print.

## Questions for the designer

1. **Slot-0 hover (h02).** Three options from art-pass: move slot 0 and the buttons about 22 px further, let a slot-0 lift move sideways, or rule that slot 0 lifts less. My recommendation: rule that a card lifts as far as it can without covering a ring cell, so slot 0 lifts less, and state that in VISUAL_PLAN H with the protected-set gate reworded to "no glyph of the cost, title or rules line covered". The board's dim and the pink print already carry the hover; a consistent rule matters more than a consistent height.
2. **T6 ending.** Recommendation: T6 ends on the bare room, and the return to the street is T4 played in reverse as its own beat, flash-tested on its own. Trying to fit both into 0.8 s is what breaks the flash limit.
3. **FOCUS above the tower** (R2-3). Recommendation: accept as a named exception.

## Recommendation

The review loop has met its exit rule. Remaining work before sign-off, in order:
1. Re-render the effects set on the round-2 board with the SKIP hint (R2-1). Send me the effects folder alone for a spot check.
2. Designer answers the three questions; art-pass records them as DR-11..DR-13 or as calls.
3. S3 items R2-4 to R2-12 ride with the next board publish; none blocks the port spec.

## Process notes

- No bare `python -` was run in this pass. Two `python -c` one-liners with fixed strings were run for crops and a JSON read; they read no stdin.
- Nothing was committed; this file is untracked under `docs/reviews/ad_review_overnight_2026-11-02/` on main.
- GIFs were not frame-stepped; the storyboards and `metrics.json` were taken as the record.
