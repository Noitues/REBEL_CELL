# AD re-review, rebuild round 1 (art-pass commit b26022f5)

Reviewer: independent AD (this session). Date: 2026-11-04.
Snapshot reviewed: `D:/rc_scratch/review_snapshots/r1_b26022f5/` (read only; the live tree was not opened).
Judged against: VISUAL_PLAN.md "Designer rulings (binding)" DR-1..DR-10, ART_BIBLE 2.4 and 3.14 notes, REVIEW_RESPONSE.md calls.
Opened: all 15 `final/` plates (1x and 2x crops), `card_sheet.jpg`, `grey_proof.jpg`, `before_after.jpg`, `review_rebuild.jpg` (all 8 bands), all 8 effect family sheets, `fx_block_vs_break.png`, `resolve_beat_strip.jpg`, `hover/contact_sheet.jpg`, h02 / h03 / h04 at 1x, `backdrop/before_after.jpg` (all 4 bands), all 9 backdrop plates by measurement, `transitions/t05`, `t06`, `sheet.jpg`. The GIFs were not frame-stepped; the strips and metrics stand in for them.
Measurements: my own L* / C*ab / dE76 probes on the snapshot PNGs (`r1measure.py`, `r1m3.py`, `r1m4.py` in the session scratchpad). Where my numbers differ from `checks.json` I say so.

## Gate verdict

**S1: 0. S2: 6. S3: 9.** The designer's exit rule is no S1 and fewer than 3 S2, so round 1 does not pass yet, but every remaining S2 is an implementation item with a known fix, and four of the six are already on art-pass's own round-2 list. Nothing here needs a new designer ruling except the three questions at the end.

The rebuild is a different board from 090ad870. The eight S1 findings are closed: the enemy family now reads (occupied vs empty cells, lowest ratio 3.15 by their check, 3.01 by gate 2's wider mask, both over 3:1), the clock is gunmetal, the bill is typeset at 16 px with digits, effects sit under the HUD, T5/T6 are rendered from the board layers with no CONCEPT frames, kills are pink. The documentation rule the designer set was followed: DR-1..DR-10 are quoted in VISUAL_PLAN and the two LOCKED bible sections carry dated notes. I judged against those rulings and list disagreements as questions, not findings.

## Original findings

Class is the response's class. Status is mine. "DOC" means the ruling is recorded and the plate follows it.

| # | Finding | Class | Status | Evidence (my read) |
|---|---|---|---|---|
| 1.1 | Occupied vs empty cells | IMPL | FIXED | p1 occupied NOW glass L* 43, empty brightest 21.9; the unit cells read as lit glass with HP ticks at 1x on all three skins |
| 1.2 | Value order inverted | IMPL | FIXED, two holes (S2 below) | sweep p95 93 → 71, tape 82 → 61, clock median 48, tower 89.5, SEND IT 98. Holes: bezel cube glyph discs L* 100 (x 970-1000, y 555-585) and 1 px ring / band lines L* 95-100 |
| 1.3 | Corp hue on a ring | DOC+IMPL | DOC (DR-6) + FIXED | Cell fills neutral on both skins; theme on rim rope, lip, crest. Meridian rim median rgb 139,84,42: dE 50 from SCHEDULE, 56 from HARM. Solace rim rgb 84,162,57: dE 22.8 from GAIN, 20.4 from the hub HP ring green (S3 note) |
| 1.4 | COLD lost on Meridian | IMPL | FIXED | COLD chevrons L* 68 on a cell at 15-20; Meridian lowest cell ratio 4.12 |
| 1.5 | Bill unreadable | IMPL | FIXED | Mono 23 labels, Anton digits with tally second, NEXT row at 70 % filled COLD, SPLIT written out, REFUND tab under the coin. Readable at 1x |
| 1.6 | Effects above the HUD | IMPL | FIXED | Every strip shows 0 px over the HUD; hp_through / refund / trace_add cross by rule |
| 1.7 | Transitions DONE with CONCEPT frames | IMPL | FIXED | Badges REAL / RENDER / COMP only; T5 K1 is the bare room (frame L* 28); T6 K6 = failure screen A. Not done by their own note: T6 pull-out iris (S3) |
| 1.8 | GAIN on kill marks | IMPL | FIXED | Dying cell = pink L7 hatch; fx_kill pink; 0 GAIN px on kill marks on the D sheet |
| 2.1 | Eleven techniques | DOC | DOC (DR-8) | Card sheet: shared frame, key line, pink disc, xerox icons, grain hold the deck together |
| 2.2 | Type colours collide | DOC+IMPL | DOC (DR-5) + FIXED | TOWER teal #006E66, WAVE lilac #B4AAFF, Spin 3 band off BOSS_GOLD; lowest dE 30.8 |
| 2.3 | Wireframe played slots | IMPL | FIXED | Flat upright torn-paper liners with ghost glyph; p3 and card sheet. Dim (word p95 L* 64) but readable |
| 2.4 | Hover duplicates the HUD | IMPL | FIXED | h04: four NEXT option rows in the one HUD, no second bill |
| 2.5 | Pencil is not pencil | IMPL | **NOT FIXED on board p2 / p2b** | Hover set: 7 px wax + 3 px ink, grain visible on h03 / h04 arcs. Board p2 and p2b (all skins): 2-4 px flat yellow vector, X caps 4 px, no grain, same as A05 |
| 2.6 | Hand collisions on hover | IMPL | **NOT FIXED on h02** | 22 of 26 hover plates pass; the four Brace plates close the fan over the neighbours (SPIN and TRIGGER titles cut to fragments). p2 passes the cost/rules rule but hides the "3" of SPIN 3 and its x3 badge |
| 2.7 | Card bottoms clipped | IMPL | FIXED | Lowest hand pixel y 1064-1067 on every plate |
| 2.8 | Room off / iso not perspective | DOC+IMPL | DOC (DR-9 camera) + FIXED | Room box L* mean 32, p95 39 on all skins; the bio room reads as a room at 1x. Meridian = shop under amber. Scrim read 25 on p2/p3 is an art-pass call (question 2) |
| 2.9 | Three clock materials | IMPL | FIXED | One gunmetal #6E7580; SCHEDULE orange only on the live sweep |
| 2.10 | Effect loudness inverted | IMPL | FIXED | Shared gated meter: damage 2817-9540 > kill 1813 > block 841-1677 > state 85-761, all skins |
| 2.11 | 12.7 s beat | IMPL | FIXED | 3800 ms, skip at any input, every effect ≤ 600 ms, no overrides |
| 2.12 | FAR trim without key | IMPL | FIXED | FAR marks on the bezel carry Anton 19 numbers |
| 2.13 | Adjuster hatch and beads | IMPL | FIXED | Solid gold segmented track, no hatch, 0 px covered |
| 2.14 | Tickets unreadable | DOC+IMPL | DOC (DR-1) + FIXED, one step missing (S3) | W6 / W5 / W4 glyphs 23-27 px at L* 84; kind glyphs read at 1x. W5 edge equals W6 (self-reported) |
| 2.15 | Tower too loud | IMPL | FIXED as prescribed | Slice inks median L* 63-70, discs carry the peak at 89.5. Squint 57-69 % is reported, not gated (question 1) |
| 3.1-3.14 | S3 set | IMPL / DOC | FIXED (3.4 DOC, DR-5) | Clamp HOLD, brick FIREWALL, ring TWIST, NO RAM + lock, atlas Heat glyph, REFUND tab, "2 → 1", neutral BEST chip, one RAM treatment, P stock pink paper, log Mono 23, source-coloured bits, non-aimed slices dimmed to 0.39, YOU hatch 13.6 x 22 px |

## Round-1 defects, tiered

Art-pass asked for a tier on each, not a re-measure. My tiers:

| Defect | Tier | Class | Note |
|---|---|---|---|
| FOCUS brackets on board p2b drawn in #96FE46 as a joined bar | **S2** | IMPL | Confirmed: 247 px lime / 0 px FOCUS on p2b neutral, 1348 px on p2b Solace where the same colour is the corp rim. The hover set has it right (h03: 599 px #D4FF00, 0 lime), so board and hover disagree. On Solace this is the exact 2.4 collision DR-6's dE 15 floor exists to prevent. Fix the constant and the four-corner draw in the board generator; re-render the four dependent sets |
| Bezel cube glyph discs at L* 99-100 and 1 px ring / band lines at L* 95-100, above HOT | **S2** | IMPL | These are the brightest marks on the enemy rings at 1x. "HOT second under SEND IT" is the rule the rebuild was built around and it is not true on the pixels. Glyph ink to K_TYPE L* 84; structure lines to a capped value and added to check b as a class |
| Ring NOW token discs fail the per-disc rule (p95 91 vs tower 89.5) | S3 | IMPL | 1.5 L* over; invisible at 1x. Fix with the glyph change above |
| W5 ticket edge shows no 70 % step | S3 | IMPL | The code sets it; the plate does not show it. Also fix the NOTES claim |
| h03 dying cell 2.62:1 under a gun tracer | S3 | IMPL | One cell, one plate pair. Gate the dying glass like a live unit, as 1.1's call says |
| Generator draws the wrong TWIST glyph depending on render order | **S2** | IMPL | Not a visible defect today, but a one-source-of-truth bug that can silently corrupt any published plate. Fix before the next publish, add a determinism assert |
| Hover HUD 45 px taller than the board HUD | **S2** | IMPL | Measured: board HUD plate edge rows 12-300, hover rows 77-335 (h02), 77-425 with option rows (h04). Every hover pops the bill. Recommendation under question 3 |
| Stale docs (VISUAL_PLAN G, final/NOTES "Not done", REVIEW_RESPONSE last row, P stock not a token) | S3 | DOC | The designer's rule is documentation as well as implementation; fix with round 2 |

## New in this pass

| # | Finding | Tier | Class | Evidence |
|---|---|---|---|---|
| N1 | Card titles clipped by the lifted card | S3 | DOC+IMPL | h03: "SPIN" (3 hidden); h04: "TRIGGE"; h02: "SPIN" and "TRIGG" at 40 %. The 2.6 call protects cost and rules line only. Add the title band to the protected set; a card's name is its identity |
| N2 | Solace rim green sits next to the hub HP ring green | S3 | IMPL (art-pass call within DR-6) | Rim rgb 84,162,57 vs hub HP ring rgb 123,211,123: dE 20.4. Passes the 15 floor, but at 1x the enemy rim and the player's HP ring are the two green objects on the board. Celadon #B8DCCC is already the Solace ink; a celadon or teal rope rim would keep the theme and leave green to GAIN. Not a ruling conflict: DR-6 asks for a theme, not for leaf green |
| N3 | h04 full-circumference PLAN ring on the frame band | S3 | IMPL or DOC | 8921 PLAN px at r 480-500 (the outer bezel), 1258 at r 300 (ring +1). Twist turns ring +1 or +2; the loudest mark says "the whole board". If the outer halo means "pick a ring", say so in the hover key; otherwise put the halo on the legal rings |
| N4 | T6 pull-out iris not composited; tile flash at the limit (3 in 1 s) in T5 and T6 | S3 | IMPL (open) | Self-reported. The hold-on-room is acceptable as a concept; the limit needs margin before port (question 4) |
| N5 | Corp theme is colour-only at squint | note | DOC | On `grey_proof.jpg` the Solace and Meridian rims are the same rope in luma. DR-6 allows "even if just a color shift", so this is not a finding; the bible 2.4 note says "material and hue", which overstates what the plates carry. Either add a luma-visible material difference or soften the note |

## What passes that I want to say passes

- The 2x HUD crop of p2 is the first bill in this project I would ship: labels, digits, tally, operators, option rows with a neutral best star, REFUND under the coin.
- The ticket queue is readable at 1x and the time grammar (dots on the ticket, no number) is consistent with DR-1.
- The effect sheets are now a system: one loudness meter, one layer rule, one T2 cap, reduce-motion tile per effect, block vs break side by side on the same slice.
- The resolve beat at 3.8 s with skip is the right length.
- T5 K1-K6 tells the DR-10 story without a concept frame.

## Questions for the designer (not findings)

1. **Tower loudness.** The O-29 squint target (50 % loud in the tower zone) and the 2.15 prescription (slice inks L* 60-72) cannot both hold; the rebuild sits at 57-69 %. My recommendation: drop the squint share as a gate and keep the value gate (tower p95 under HOT and SEND IT). The tower is the player's object and the punk-rock ruling (DR-2) wants it loud; what matters is that it never outranks SEND IT or the HOT threat marks, and it does not.
2. **Room under the UI scrim** reads L* 25 on p2 / p3 (28-34 without the scrim). Recommendation: accept. The scrim is UI ground and the room is still a room on p1.
3. **Hover HUD height.** Recommendation: reserve the option-row space in the board HUD at all times (empty rows at the NEXT position), so nothing above it moves on hover. A 45 px pop on every hover is a flicker the player will feel. If the designer prefers the compact board HUD, the option rows should extend downward below the bill's bottom edge only.
4. **h02 slot-0 lift.** Recommendation: option (a). Keep the fan positions fixed, lift the hovered card straight up, and move the UNDO / SEND IT column 12-16 px right (its right edge is at about x 1880; there is room). Never close the fan over the neighbours.
5. **HOT carried by its white-hot core** (fill 1.90:1, core 4.86:1). Recommendation: accept, with the core kept at 3 px or more at 1x.
6. **T5 / T6 tile flash at the limit.** Recommendation: take the bit density over the dark city down until the worst tile is 2 in any 1 s before port.
7. **Rules:** Shove bump HP and the Twist draw in the resolve beat stay with the GDD; the art correctly shows no HP change and marks the workaround not to ship.

## Build order for round 2

1. Board generator: FOCUS constant + four corners; glyph ink and 1 px lines to the capped class; per-disc token value; W5 step; dying-glass gate; TWIST render-order fix with an assert.
2. Board pencil on p2 / p2b to the hover pencil (same `hv_core` stamp).
3. Hover: h02 by option (a); title band into the protected set; HUD height per question 3; h04 halo per N3.
4. Re-render hover, effects, transitions, backdrop from the new board (they are all built from gate-1 layers).
5. Docs: VISUAL_PLAN G, final/NOTES, REVIEW_RESPONSE last row, P stock token, 2.4 note wording (N5).
6. Then one full independent pass. Expected result if 1-5 land: S1 0, S2 0, S3 ≤ 4 (N2, N4, N5 and the squint question), which passes the designer's rule.

## Process notes

- No bare `python -` was run in this pass. Every probe ran from a `.py` file by path.
- Nothing was committed; this file is untracked under `docs/reviews/ad_review_overnight_2026-11-02/` on main.
- I did not frame-step the GIFs; the strips and `metrics.json` were taken as the record of them.
