# Grammar designer notes (VISUAL_PLAN B-F, current style)

Generator copy: `D:/rc_scratch/combat_redesign/grammar/src` (gram.py, gramlib.py, gram_render.py, sheets.py). Nothing in combat_e10_design was touched. Plates are 1920x1080 on `room_bio_bare.png` (v3_1), state f1 (p1). Style is the E10 cel look with only the grammar changed (the tower is pink and the enemy slate, as required by the colour rules).

## Files
| File | What |
|---|---|
| `line_audit.jpg` | 12 rows, E10 vs now: every dashed or dotted line on p1, what it meant, what replaces it |
| `time_A.jpg`, `time_B.jpg`, `time_C.jpg`, `time_compare_grey.jpg` | time options: crops in situ, rules, side by side in colour and greyscale |
| `hp_A.jpg`, `hp_B.jpg`, `hp_C.jpg` | pending-damage options: whole state vocabulary at 2x, in-situ crops at 3x |
| `colour_legend.jpg`, `colour_applied.jpg` | the reduced set as a legend card (with the note 5 table and colour-blind checks), and E10 vs now |
| `waves_compare.jpg` | E10 arcs vs option A vs option B |
| `plate_base.png` | full plate: time A + hatch A + queue A + reduced colours (the plan as written) |
| `plate_time_B.png`, `plate_time_C.png` | full plates, time options B and C |
| `plate_hp_B.png`, `plate_hp_C.png` | full plates, HP options B and C |
| `plate_wave_B.png`, `plate_wave_none.png` | wave option B; E10 arcs with the new grammar (comparison) |

## 1. Line audit (note 2)
Dashed uses on p1 as coded: +2 unit outline, +2 landing arc frame, +1/+2 threat trim, gun tracers, hollow growth chevrons (plus the +2 token ring in the E10 code). Read as dashes without being coded as dashes: HP ring, unit HP ticks, the tape ring and hazard ticks of the wave arcs, the turn-dot pill. All dashed lines are gone. The only broken line left is the L8 dotted line, and it means "two or more turns away" (+2 outline, +2 arc frame, +2 trim, W5/W6 ticket edges). Gun tracers are now one solid pink stroke with an ink edge. Growth chevrons are hollow with a solid channel.

## 2. Time (note 2: this END TURN vs any future turn)
- **A Heat (the plan):** the mark carries time. NOW: full value, bold solid outline with glow, END notch. +1: 70 percent value / 45 percent chroma, thin solid, one pip. +2: 50 / 25, dotted, two pips. Applies to cell outline, token ring, chevrons, landing arcs, tower trim, ring tags, HUD NEXT row.
- **B Dial:** every contour is the same solid line (weight steps only), a fuse dial (full disc / half / quarter) says the time on cells, arc caps and tags. Clear and countable, but one more icon to learn, and the dial is small at 1x.
- **C Frost:** the future rings and their arcs sit behind frosted glass (blur, desaturate, lift) with a pane-edge hairline at the NOW ring. Fastest read at a squint; costs legibility of the +2 content (arcs of +2 are weak).
Recommendation: A, with C's pane edge as an optional ring-floor tint. A reads in greyscale (time_compare_grey.jpg) and keeps all content crisp. Hot is a glow and a notch, not red: a red HOT would collide with HARM.

## 3. HP (note 3: the white slash)
Cross-hatch (the plan, A) replaces the slash everywhere: tower ring, slice pips, unit ticks, HUD YOU row, slice break wedge. Hatch colour is the cause: red enemy, indigo soak, pink us (enemy HP lost to our shots). Also drawn and distinct: current (solid), +1 forecast (tinted hollow, cold), mend (empty socket, green outline, plus and a tick), gone (dark socket, hairline), blocked (lit segment behind an L10 pink double line), enemy shield (hex pips in a double bracket), armor (steel double-line cap, drawn in situ on the Payload).
- **A cross-hatch:** best in the HUD and ticks; on the 7 px tower ring it is a fine mesh (two lines fit).
- **B hazard stripe:** most visible at 1x, reads as "caution", but one direction only and no glow, so it is the loudest and least refined.
- **C drain core:** quietest; at a glance it looks like the +1 forecast. Weakest option.
Changes beyond the plan: player HP ring is 15 blocks in 3 groups of 5 (r 150-157), pending run starts at the needle. Slice pips use the same draw call.

## 4. Colour (note 5)
Twelve meanings only (legend card). What each E10 outline colour meant is in the table on the card: lane colours became time grades of one neutral enamel, slice frames became one pink frame (type = icon), cyan hub/code rings became pink, mauve units became cool slate, teal bezel became gunmetal, the orange WAVES LEFT chip became neutral (orange = schedule steps only), tracers became pink. Check: CELL_PINK vs HARM passes (min dE 23.3, tritan), so the fallback pink is not needed. **SOAK #464EFF vs TRACE_VIOLET fails protan (dE 2.4)**, the same failure that made E10 change to #3A7EF3: pair soak by the chevron notch (already done) or revert to #3A7EF3. The plates use the plan's #464EFF.

## 5. Waves (note 6)
- **A queue tickets:** three 74x62 tickets top-left (W6 dotted far, W5 dotted, W4 solid), kind glyphs with width bars, W6 cut corner and three schedule ticks, one L5 arrow to the rim. Frees the full r 470-510 band (about 22 percent of the board disc). Landing arcs moved to r 436 / 474.
- **B rim lane:** the three as annular plates on one lane, r 491-511, 31 degrees each, arrow past W4. Keeps the "waves come from outside" metaphor, but sits on the dense rim and is hard to read. Pick A.
Deviation: the feed arrow ends at the board rim, not at a true ring +2 entry (that entry is not at a fixed angle in the sim).

## Known gaps and honesty
- Cold chevrons read dark brown (45 percent chroma on a dark bed); could take a value lift.
- The unit token glyph ring at +2 is a solid thin ring (dots do not fit a 54 px disc).
- Option C (drain) of the HP grammar and wave option B are the weaker ones.
- Not done here: hover/p2/p3 plates, the nowords variant, the p2b arrowed-outline hover path (L5 is only built for the wave feed so far), the YOU strip tape, and the effect overlays (section G).
- assert_draw_log was not run (the grammar changes geometry on purpose).
