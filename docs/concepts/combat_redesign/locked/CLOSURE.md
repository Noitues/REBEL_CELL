# Combat redesign art pass: closure (2026-11-06)

This effort is closed. The review loop met the designer's exit rule (no S1 and fewer than 3 S2) on round 2.
Sign-off still waits on the designer: see "Before sign-off" below.

## Where it stands

| Item | State |
|---|---|
| Last reviewed commit | `403e9ade` on `art-pass` (frozen copy: `D:/rc_scratch/review_snapshots/r2_403e9ade/`) |
| Reviewer verdict, R2 | **S1 0, S2 1, S3 11.** Meets the exit rule. Report: [reviews/R2_REREVIEW.md](reviews/R2_REREVIEW.md) |
| Earlier reviews | [reviews/AD_REVIEW.md](reviews/AD_REVIEW.md) (2026-11-03), [reviews/R1_REREVIEW.md](reviews/R1_REREVIEW.md) (R1: S1 0, S2 6, S3 9), [REVIEW_REBUILD.md](REVIEW_REBUILD.md) (internal) |
| Per-finding calls | [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md), "Round 2 (2026-11-04)" table |
| Designer rulings | VISUAL_PLAN.md, "Designer rulings (binding)" (DR-1..DR-10) |
| Published sets | `final/` (board, 15 plates), `hover/` (26), `transitions/`, `backdrop/` (9) are on the round-2 board. `effects/` is still the round-1 set. |
| Generator source | `D:/rc_scratch/combat_redesign/locked/corp/src` plus the per-stage tools, copied to [scratch_src/](scratch_src/) (scripts and notes only, no renders) |

## Before sign-off

1. **R2-1 (S2, IMPL): re-render the effects set on the round-2 board.**
   - Scope: sheets, strips, beat strip and GIF, plus the C12 SKIP tab.
   - The Solace scan line in fx_wave_enter / fx_grow must change from #96FF46 to the C16 teal.
   - Re-run the loudness and layer checks.
   - Send the effects folder alone to the reviewer for a spot check, not a full round.
   - Partial round-2 work exists (not published): `scratch_src/round2/effects/` (bases, hp_through, refund, trace rows, pencil burn, P_STOCK, teal scan line, SKIP tab).
   - The runner is `tools/run_r2.py`, and `tools/publish_r2.py` publishes. Run with `-j 1`: one core only.
   - Designer, 2026-11-04: "Not now".
2. **Designer answers the three open questions below.**
3. Only after the designer signs off: post A-116 (draft in [MAILBOX_DRAFT.md](MAILBOX_DRAFT.md)) and fold [ART_BIBLE_COMBAT_DRAFT.md](ART_BIBLE_COMBAT_DRAFT.md) into `docs/ART_BIBLE.md`. Neither is done.

## Open questions for the designer

The reviewer's recommendation is listed first for each one.

| # | Question | Recommendation | Alternative |
|---|---|---|---|
| Q1 | **Slot-0 hover lift** (R2-2): slot 0 lifts about 10 px and the other slots lift about 190 px. Brace's edge covers a sliver of Spin 3's cost hex and title band, though everything stays legible. | A card lifts as far as it can without covering a ring cell, so slot 0 lifts less. Record this in VISUAL_PLAN H, and reword the protected-set gate to "no glyph of the cost, title or rules line covered". | Keep a fixed lift height for every slot, and accept or move the fan. |
| Q2 | **End of T6** (R2-6): after 7 pull-out variants each gave 3 flashes in the 0.8 s, T6 holds on the room. | T6 ends on the bare room. The return to the street is T4 reversed, as its own beat with its own flash test. | T6 cuts, or cross-fades over 0.25 s, to the street. |
| Q3 | **FOCUS brighter than the tower** (R2-3): FOCUS #D4FF00 reads L* 94.1, above the tower p95 (89.5) and less than 1 under HOT p95. | Accept it as a named third exception above the tower (SEND IT, HOT, FOCUS). | Dim FOCUS. That changes the C2 colour. |

Two rules questions stay with the GDD and the rules sessions, not art: the Shove bump HP and how Twist renders.

## S3 items left for the next board publish

None of these blocks the port spec. Each ID points to its R2_REREVIEW entry.

- **R2-4 IMPL:** white burst cores on h03, h05 and h09. Use HIT_PAPER as the 1.2 call set.
- **R2-5 IMPL:** the side-arc HOT cores are 2.0-2.5 px, under the 3 px minimum.
- **R2-6 DOC:** the FEEL line on the t06 sheet says "you are on the street", but K4 is the room. Fix the text.
- **R2-7 IMPL:** UNDO / SEND IT sit 12 px right on the board and 16 px on hover. Pick one constant.
- **R2-8 IMPL:** the h03 tracer is only dE 3.8 from CELL_PINK.
- **R2-9 IMPL or DOC:** the h11 HOT fill is dimmed inside the lit area.
- **R2-10 DOC or IMPL:** the h08 Hold pencil on the frame band is defensible, so say why in the hover key. Key or remove the unkeyed yellow arc on the lower-left rim.
- **R2-11 IMPL:** the plain render path and the capture-hook path in corp/src differ by up to 48/255 at r 430-460.
  - Suggested fix, from the round-2 backdrop stage: in `gram.a2_frame`, draw the frame fill into its own `L2` layer and alpha-composite it.
  - Make the two paths agree before the port spec is frozen.
- **R2-12 DOC:** the pencil wax measures 6.0 px against the 7 px spec. Restate A.5 as measured, or widen the wax by one.

The reviewer accepted two costs, which are not findings: the 90 px of empty bill left by the reserved option rows, and the lifted card at 1.00 zoom.

## Process notes

- **Round 2 overran.** It took about 9 hours because it folded in every call and every S3 item and re-rendered every set. The designer cut it short.
- **Rules from now on:**
  - A fix round covers only the reviewer's S1/S2.
  - It re-renders only what those touch, then goes straight back to the reviewer.
  - All rendering uses one CPU core.
- **Repo move.** The git store moved from `C:\Users\noitu\Documents\Godot\rebel_cell` to `D:\From_C_drive\rebel_cell`. The worktree's `.git` file was repaired to point there on 2026-11-06.
- **Stale copy.** `D:\rc_claude\repo\rebel_cell` is an older copy from 2026-10-19. Do not use it.
