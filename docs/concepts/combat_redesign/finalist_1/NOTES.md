# F1 BLACK-BOOK BURNER: the combat screen, redesigned (ART CALL 51)

Finalist 1 of the combat redesign: *the Cell drew its board in its black book, then pasted it up on the wall.* Sketchbook-graffiti base (the tower) plus street-graffiti donor (cards, SEND IT, nameplate, YOU strip). Direction source: `REVIEW.md` F1 + `VISUAL_PLAN.md` (R51 review rules).
Everything here is rendered on the **redesigned board**, never the E10 board, from one generator copy: `D:/rc_scratch/combat_redesign/finalist_1/src` (snapshot in `src_snapshot/`; entry points `run_all.py`, `f1_fxplates.py`, `f1_hover.py`, `f1_checks.py`, `f1_infocheck.py`). Nothing in `combat_e10_design/` was edited.
Only the game information stays fixed: same sim state (`state_e10.json` f1 / f2 / f2t / f2b), same numbers, same words, no new mechanics.

## What is in this folder

| File | What |
|---|---|
| `p1_decide.png`, `p1_nowords.png` | decide beat (f1), and its nowords proxy (bars and tallies instead of words and digits) |
| `p2_preview.png` (+ `_f2t`, `_f2b`) | the plan preview on f2 (best line), f2t (Trigger only), f2b (Brace only) |
| `p2b_hover.png` | unit hover (Packet x3, f1) with the hover tag in its parked E10 form |
| `p3_resolve.png` (+ `_f2t`, `_f2b`) | resolve beat |
| `p1_decide_srv.png`, `p1_decide_gh.png` | the same plate on the server-room and greenhouse cutaways (bio is the default) |
| `fx_moment_1_block_vs_break.png` | slice-overlay moment 1 (f1): shield BREAK, slice break, shield BLOCK, hit lands, side by side |
| `fx_moment_2_brace_soak.png` | slice-overlay moment 2 (f2): Brace clamp, soak funnel, shield block |
| `hover_brace.png`, `hover_twist.png`, `hover_trigger.png` | hover plates, one per card effect type: protect a slice, turn one ring, resolve a unit now |
| `legend_f1.png` | one-page key: families, time marks, HP states, colours (every tile is a crop of the real plates) |
| `crops_2x.jpg` | 2x crop sheet: wheel / hand / HP / time marks / tickets |
| `before_after_p1.jpg` | E10 `p1_decide` (before) and F1 (after) |
| `squint_320_colour_grey.jpg`, `squint_1_16_blur.jpg`, `cvd_p1_decide.jpg`, `cvd_p2b_hover.jpg`, `grey_proof.jpg`, `checks.json` | squint 320 px colour and grey, the 1/16 + blur image the metrics read, deutan / protan / tritan, the greyscale proof, all numbers |
| `game_info_check.json`, `assert_draw_log.txt` | game-information checks (see the end) |

## The one-line answer to each designer note

1. **Art style and player-owned.** The tower is a black-book page and the hand is wheat-paste: paper, marker, ballpoint, tape and a block drop, none of which exists anywhere else on screen. Pink marker is "ours". The board is clean enamel on slate glass, so ownership reads from material and line, not from the pink alone.
2. **Dashes.** None. The dash audit logged 0 dashed draw calls on every plate. Dotted is spent on exactly one mark, the +2 threat trim. Each thing has its own line (see the line table).
3. **HP with a white line.** Retired. Lost-at-END-TURN is a cross-hatch in the colour of its cause (red = the enemy, blue = your soak, pink = us). The pending block bulges 2 px thicker than a kept block, so it reads without colour.
4. **The arrowed outline** is kept for movement: the THIS TURN schedule cell, the hover route, the Twist sweep, the wave-queue feed.
5. **Outline colours.** There are none left. Every enemy outline is one enamel hairline; "when" is told by value, weight and pips, not by hue. Twelve colours, each one meaning, on `legend_f1.png`.
6. **Wave info.** The three W4-W6 arcs (about a fifth of the board) are gone. Three 84 x 64 tickets sit top-left with one neutral feed arrow; the freed rim went to the tower (r162 to r196).
7. **Slice-wide overlays.** Protect = a paper plate (taped black-book page, marker double line); Harm = print (red halftone flood, black krackle, misregistered plate); Soak = a marker funnel. Block and break are told apart in one frame (moment 1).
8. Content rulings (inspect panel, hover tag text, UNDO cause, pile counters) untouched.
9. **Hover dimming kept** (value x0.40, chroma x0.45); three hover plates.
10. **Real redesign, not tuning.** Style, shapes, line language, layout and the board itself changed; only the information is the same.

## What changed vs E10, per family

**P PLAYER (the Cell)**
- *Tower*: r162 to **r196**. A dot-grid page (paper multiplied to 72 percent value, largest fill below L* 75) with a torn rim and two kraft tapes at 30 and 210 degrees, never on an HP block or a pip. Six pink chisel-marker slices that miss a ballpoint construction line by about 2 px; ballpoint construction arcs at about 25 percent; shadow is a single-direction ballpoint hatch (never cross-hatch, which stays reserved for "lost at END TURN"). A tapered ink outline (2.6 to 5 px, heavy on the shadow side) and a 3 x 4 px block drop make each wedge read as a letter piece. Icons are the E10 silhouettes re-inked (twin pod, single missile, split heater, bandage) at about 44 px; nothing redrawn. Hub = G1 throw-up bubble in pink with a chrome #C9D3E0 highlight and BREAKER in Permanent Marker. Four doodles (star, spark, X, zig) on the page margin only.
- *Player HP ring* moved off the rim and wraps the hub (r52-64, 15 blocks in 3 groups of 5). It ended the red hatch merging into the red trim.
- *Guns*: tapered pink marker strokes with an ink keyline, ending in hand starbursts; armor = steel chevron, ward = gold chevron, shield pop = hex shards.
- *Cards*: wheat-paste paper, a dark wall band (#221D2A) with a pink spray burst behind the icon (no halftone), Anton tag title in pink with a chrome rim, ink outline stack and drop, kraft tape type strip, Permanent Marker rules (about 22 px on screen) with a ballpoint underline. RAM coin stays cyan, Trace tab stays violet. The hand is 1.15x and fans 4 degrees per card; the lifted card gets a pink offset print; a played card leaves a torn-paper outline (solid, never dashed).
- *SEND IT*: spray slab, chrome letters, 3 drips, the brightest object on screen. *Nameplate* and *YOU strip*: taped wheat-paste with tag lettering; YOU blocks are GAIN marker blocks and the pending run is the L7 hatch.

**E ENEMY (Solace)**: slate glass in kind washes, a thin double-helix rule at about 7 percent, one enamel hairline on every ring. Ring +1 glass at 80 percent value and ring +2 at 62 percent, no blur. Cell outlines: NOW bold with glow and END notch, +1 thinner with one pip, +2 a solid 50 percent hairline with two pips (never dotted). The red, blue and white lane outlines are gone.

**T THREAT**: chevrons and diamonds keep "solid = hit, hollow = growth". The trim moved to r200-210 and follows the time grammar: HOT bold red with glow and an END notch, COLD a thinner #D9877C bar with one pip (it used to read brown), FAR dotted with two pips.

**K CLOCK**: bezel and schedule unchanged (gunmetal, orange only on the schedule step cells, L5 arrowed outline on THIS TURN). The W4-W6 arcs became the ticket queue (W6 50 percent, W5 70, W4 100, plus pips; W6 has the cut corner and three hazard ticks). Ring tags have solid edges.

**N PLAN**: grease pencil stays yellow in plan beats (p2, p2b, hover). In resolve (p3) every card motion and mark takes the owner colour (pink). No yellow marks in p3.

**X EFFECTS**: see moments 1 and 2. **S SYSTEM**: the HUD terminal kit is E10's; the YOU tally is replaced by the taped strip and the HUD hatch follows the new grammar.

## Layout (numbers)

Tower page r192 (torn), slices r71-177, HP ring r52-64, hub r46, icon r120, slice pips r163-171, threat trim r200-210, rings NOW / +1 / +2 r214-271 / 271-328 / 328-385 (57 px deep, tokens fit), bezel r388-422, landing arcs lanes r436 / 453 / 470, board plate r488 (was r516). The tower cap of r184 was **not** needed: slice icons are 44 px and the shallowest ring cell is 57 px deep (limit 30).

## Line language (what each line means)

L2 painted stroke = ours; L3 vector hairline = machine; L4 engraved = the clock; **L5 arrowed outline = movement**; L6 grease pencil = a plan, not yet; **L7 cross-hatch = lost at this END TURN**; L8 dots = two turns away (trim only); L9 glow = live at this END TURN; L10 double line = protection (Brace clamp, shield plate, enemy armor).

## Checks run

All numbers are in `checks.json` and `game_info_check.json`; the generator that produced them is `src_snapshot/` (`f1_checks.py`, `f1_infocheck.py`).

**Dash audit.** Every `L2.line(dash=...)` call and every dotted mark is logged while rendering. Final run on p1, nowords, p2, p2b, p3, srv, gh, f2t, f2b: **0 dashed calls and 0 dotted calls**. Two dashed draws were still inside the inherited HUD generator (the GUNS tracer mark in the resolve chain strip, and the NEXT-row alternative tally outline); I made both solid and rendered the plates in this folder after that fix. The dotted +2 threat trim only appears where a +2 landing hits a slice, which none of these states do on the tower.

**Squint (1/16 box + 1 px blur, luminance; loud = cells above 0.38).** p1_decide, F1 against E10:

| region | F1 mean / p95 / loud | E10 mean / p95 / loud |
|---|---|---|
| whole plate | 0.225 / 0.496 / 0.125 | 0.184 / 0.368 / 0.041 |
| board disc r<=490 | 0.236 / 0.443 / 0.121 | 0.186 / 0.308 / 0.003 |
| tower r<=190 | 0.420 / 0.513 / 0.759 | 0.244 / 0.335 / 0.016 |
| rings r214-385 | 0.235 / 0.341 / 0.010 | 0.207 / 0.321 / 0.002 |
| HUD | 0.155 / 0.354 / 0.042 | 0.133 / 0.227 / 0.001 |
| hand zone | 0.431 / 0.722 / 0.517 | 0.283 / 0.450 / 0.204 |

Reading: the squint mass is now the **tower** (loud 0.76 inside r190, against 0.016 before) and the **rings stay quiet** (loud 0.010, close to E10's 0.002). What is ours is the loudest thing on the board and what is the corp's is calm glass. The cost is real: the whole plate is louder than E10 (loud 0.125 against 0.041), so the quiet room the R3 fix pass bought is spent. Other beats are in `checks.json`.
Peak value at 1x (luminance p99.5): SEND IT 0.995, hand 0.887 (the tower and rings read 1.0 only because of white icons and white enamel tokens). By mean value, SEND IT is highest (0.455 against hand 0.438 and tower 0.435), which is the order the AD asked for, but by a small margin.

**Greyscale proof.** `grey_proof.jpg` (tower crop and board crop, luminance only) and `squint_320_colour_grey.jpg`. Read them by eye: the tower shows a rough tapered outline, a single-direction hatch, a block drop and a torn rim; the board shows perfect arcs, one constant hairline and the helix rule. Honest caveat: a crude texture statistic (Laplacian std) does **not** separate them (tower 64, board 71, because the board region includes tokens and chevrons), so I do not claim a metric proves it. The edge-wobble measure points the right way but weakly: slice rim 3.3 px std from a straight fit, ring edges 1.9 and 2.3 px. The eye read is the evidence.

**Colour-blind.** `cvd_p1_decide.jpg`, `cvd_p2b_hover.jpg` (Machado 1.0: normal, deutan, protan, tritan). Pending hatch survives because it is a pattern, not a hue. I did **not** re-measure dE for SOAK #3A7EF3 against NET_CYAN and TRACE_VIOLET in this pass (the AD notes E10's #3A7EF3 already passed the Trace check; cyan and blue are also separated by shape). That is an open check.

**Game information.**
- *Numbers (f1, f2, f2t, f2b)*: slice pips drawn equal the pips in the state (pending = hp - hp_after, soak count = soaked, total = max); the hub HP ring has 15 blocks with kept = hp_after and pending = hp - hp_after; the threat-trim zones per sector and time class equal the zones derived from the units' fates; every gun shot is drawn (5 on f1). All four states: `slice_pips_match`, `hp_ring_match`, `trim_match` = true.
- *Draw asserts*: the E10 geometry asserts (`build10.draw_asserts`) ran on p1, nowords, p2, p2b, p3: **173 PASS, 0 FAIL** (`assert_draw_log.txt`). They were written for the E10 layout, so they show the unit badges and trays still do not collide, not that the new layout is right.
- *Text*: compared as an order-free character inventory of everything drawn as text, F1 against the approved E10 plate (`game_info_check.json`). p1, p2b and p3 lose no character. p2 shows 8 "missing" characters; I traced them: the E10 text log draws the lifted Trigger card twice (once resting, once lifted), so it holds a second "TRIGGER", "WAVE", "Resolve a unit" and "+1". F1 draws that card once. Word by word, every other E10 string on p2 is on the F1 plate (TRIGGER ONLY, BRACE + SOAK ONLY, BEST: ALL THREE, 6 > 1, 9 > 1, 3 > 0, BEST LINE, WITHOUT TWIST). Extra characters in F1 are the same words split differently (letter-spaced HUD text, "TURN" and "SHIFTING WAVES" as two draws, "CELL-9" and "// BREAKER" as two draws).
- *Nothing invented*: no new word, number or mechanic. Additions that are not information: the "PLAYED" tag on the three torn-paper slots in p3 (a label for the played-slot state that E10 showed with a dashed slot; card names stay visible under it) and the margin doodles.

## Deviations and honest notes

1. **p3_resolve on f2t and f2b are not rendered.** Those two frames carry no `chain` list (the numbered resolve strip) and the HUD needs it. p2_preview exists for f2, f2t and f2b; p3_resolve for f2 only. I did not invent a chain strip.
2. **p2b hover plate** shows the f1 unit hover (Packet x3) with the hover tag still in its E10 form (parked, note 8). It is the one box left in the old language.
3. **Gun results in p3** are drawn as in decide (pink strokes ending in starbursts). The armor chevron, ward chevron and shield pop exist in `f1_guns.py`, but no shot in these states uses them, so no plate shows them.
4. **Slice-overlay moments are stills (the peak frame)** laid over the real resolve plate; there are no animation frames. Moment 1 puts four overlays on one wheel (shield break, slice break, shield block, hit lands) so they can be compared in one frame: that is a comparison board, not one beat of the game. Moment 2 (f2) is a true beat: the Brace clamp, the soak funnel and a shield block.
5. **Hover plates**: Brace, Twist and Trigger only. The Brace ghost is the same clamp the resolve beat uses (pink-tinted, pencil outline round the wedge). Twist's sweep is pencil yellow in hover and goes pink in resolve (the AD's motion-colour rule); the ring-tag twist badge is still the E10 yellow pill.
6. **Cards at 1x** read, but "Turn the tower 3" and "Turn one ring 1" sit close to the card edge at marker size and the Spin 3 title is squeezed. Every card uses the same pink spray burst behind its icon (no per-card colour).
7. **Hub**: the bubble, chrome highlight and BREAKER read, but the HP ring at r52-64 crowds the bubble (hub r46). A 6 px gap would help; I kept the AD's radii.
8. **Loudness**: this direction is a lot louder than E10 (loud fraction 0.125 against 0.041, hand zone 0.52 against 0.20; board-disc p95 0.443 against 0.308). The AD's cap (largest slice fill L* 75 or less) is met. If the designer finds it too loud, the cheapest lever is the hand and the tower page value, not the slice pink.
9. **Open / not done**: no colour-blind dE re-measure (see Checks); `legend_f1.png` is crowded in its top row and two captions run into the next tile; the nowords cards keep a pink bar in place of the title (a proxy, as in E10).
10. **For the designer to confirm**: (a) the arrowed-outline reading (hover path, THIS TURN schedule cell, queue feed arrow, Twist sweep); (b) whether player-owned should be this loud; (c) the split of hands: the tower is marker on a black-book page, the cards and SEND IT are spray on a wall. That split is the AD's design but it is the likeliest thing to read as two hands.
