# Assembled locked player family (ART CALL 53): wheel + WPAP cards

Plates (1920x1080, bio cutaway, E10 state): p1_decide, p2_preview, p2b_hover, p3_resolve, p1_nowords; p1 also on srv and gh. Also checks.json, before_after.jpg, src_snapshot/ (changed modules).
Generator: D:/rc_scratch/combat_redesign/locked/assembled/src. Run `python asm_render.py <p1|p2|p2b|p3|nowords> [bio|srv|gh] 1`, then `python asm_numbers.py`, then `python asm_checks.py`.

## What was integrated
- Wheel src copied; card renderer lifted (card_render.py + fonts + glyphs). f1_hand.card_hi now calls card_render.draw_card(name, 352, state). Lifted card uses state 'hover' (its own pink print); played slots use 'played' (solid liner, glyph + PLAYED); nowords uses the nowords state. Resting hand cards stay at 0.88 value.
- Fixes found by the new checks (all real, all fixed in src):
  1. Sector digit 3 touched the HOLD THEN label (29 px). Label shifted 2.2 degrees along the arc (r2_sched.hold_label).
  2. Warded badge, unit 3, was 1 px onto a ring tag (E10 assert, not obsolete). asm_units.token now shrinks the badge 1 px at a time until 0 px on tags, tray, chevrons and glyph.
  3. p2b hover leader dot and line lay over the hovered unit's badge (195 px). a2_hover.leader now tries exit angles until clear; the line has one extra elbow.
  4. nowords UNDO keycap showed the letter Z. Now an undo chevron.

## Results (all in checks.json)
- Draw asserts (E10 build10.draw_asserts plus badge px asserts), final run: p1 60/60, p2 46/46, p2b 21/21, p3 46/46, nowords 60/60, srv 60/60, gh 60/60. None of the E10-layout asserts turned out obsolete (the F1 board still registers chevrons, diamonds, dots, bars), so none were removed. Before fix 2 each plate had that one 1 px failure.
- Collision assert (new, layout-aware): the real drawn masks of sector digits, schedule labels, ring/hover tags, badges and future tickets, alpha >= 128 at 1x, all pairs across classes. Final: 0 px on every plate and every pair. Before fixes: digits x labels 29 px (p1, p2, p3, srv, gh), badges x tags 195 px (p2b). Not covered: overlap inside one class (tag on tag), and board text against the hand or HUD.
- Dash audit: 0 dashed line calls and 0 dotted-mark calls at runtime on all 7 plates; grep of card_render, lw_*, f1_hand, asm_render shows no dash arguments. Pixel-level dash detection was not run.
- Squint (1/16 box + 1 px blur, luminance; mean / p95 / loud share above 0.38), p1_decide, whole plate: E10 0.184 / 0.368 / 4.1 %; F1 0.225 / 0.496 / 12.5 %; locked 0.233 / 0.504 / 14.0 %. So the locked plate is louder than E10 on every number and slightly louder than F1. Tower r<=212 loud: E10 1.3 %, F1 60.4 %, locked 56.4 %. Hand zone (x>=840, y>=780) loud: E10 19.2 %, F1 49.9 %, locked 50.6 %; hand mean 0.387 vs F1 0.421. Rings r214-430 loud: E10 0.2 %, F1 1.1 %, locked 6.7 % (the neutral rim and tape are brighter than F1's). HUD unchanged from F1 (3.8 % vs 4.2 %). Other plates are in checks.json. Nothing was tuned to pass; there is no agreed threshold for the loud share, so I report it as a finding: the player side is far louder than E10 by design, the corp ring zone is louder than F1.
- Game information vs state_e10.json:
  - Card table: all 11 cards, RAM cost, Trace, name, rules text and type equal the state and the E10 build10 table (11/11).
  - Cards actually drawn in each plate (hook on card_render.text): every hand card draws exactly its name, type word, rules text, cost digit, the +Trace tab only where state Trace > 0 (Trigger only) and the multiplier on Spin 3. Pass on p1, p2, p2b, p3, srv, gh. p3: played slots show glyph and PLAYED only, not the card name (F1 ghosted the full card art). This is a small information loss for the played cards; say if you want the name back.
  - Required words from the state are present in the draw-call text on every wordful plate: TURN, SHIFTING WAVES, WAVES 6 LEFT, tickets W4 W5 W6, NOW W1, +1 W2, +2 W3, YOU, LANDS, THROUGH, RAW, SHOT, BRACE, RIDER, SPLIT, ABSORBED, SOAK, NEXT, WIN, SLICES KEPT, KILL ADJUSTER, TRACE LOW, RAM, TRACE, ENDS = HEAT, BREAKER, SEND IT, UNDO, CELL-9. None missing. This is a concatenated-text test, not OCR.
  - Units and HP: covered by the draw asserts above (chevrons, diamonds, soak, brace, Adjuster bar, hero pair, turns-until dots against the sim) and by asm_numbers (slice pips, HP ring lit/pending, trim zones, all four frames: all match). Those compare the state with what the drawing functions are told to draw; there was no pixel read-back.
  - Character inventory vs E10 text_e10.json: nothing missing on p1, p2b, p3, nowords (0 chars, both). p2 is missing 1,1,W,G,G,A,V,V: that is the E10 inventory counting the lifted Trigger card twice; the locked hand draws it once. Extra characters (p1: 51) are new or discarded draw calls (second UNDO and Z copy because the F1 UNDO is blanked after it is drawn, nameplate and hub name text, type words). I did not attribute every extra character, so treat this test as "no omissions", not "exact".
- nowords: 0 alphanumeric draw calls.
- before_after.jpg: E10 final | F1 | locked, with full plate, hand crop, wheel crop and the squint image.

## Open points
- Cards at 1.15x: title and type word read; rules text is small at 1x as before. Lifted Trigger hides the Spin 3 multiplier (same as F1).
- The p2b leader line now has an elbow to stay off the badge.
- Spinner and tower are far louder in squint than E10 (the 56 % loud cells in the tower zone). If E10-level calm is wanted for the player side, that is a style decision, not a bug.
- Process note: I ran bare `python -` (empty stdin, no code) twice by mistake and `python -c` one-liners a few times early on for inspection; none wrote files. All render and check work ran from script files. Nothing committed, nothing under D:/Godot/rebel_cell, no Godot or Blender.
