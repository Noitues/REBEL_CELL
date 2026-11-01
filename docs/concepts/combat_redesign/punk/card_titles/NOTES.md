# Card titles: the pick

Question: BRACE, SPIN 3, TRIGGER, TWIST were hard to read on the F1 black-book cards. The cause is measurable: pink fill on cream paper is 2.8:1, and the chrome rim plus pink extruded drop add noise inside the letter.

Four treatments, all in the black-book / graffiti hand, rendered as the real 4-card hand at 2x on the real combat backdrop (`sheet.jpg`, files `hand2x_*.jpg`), with 1x and 320 px checks (`legibility_1x_320.jpg`):
- A: black marker tag with a white keyline and a thin pink offset print (the owner colour stays in the shadow, not the fill).
- B: white chisel letters, black outline, hard black drop.
- C: highlighter-yellow fill, black outline, hard drop.
- D: cream letters on a black tape strip (torn ends, pink offset).

## Pick: A, black marker tag with white keyline
- It is the only option that passes the contrast rule on both surfaces the title sits on. The black fill beats the cream paper (17.4:1) and the white keyline beats the dark art band (15.3:1). B, C and D rely on one surface or add a shape, and their dark edge merges with the band (1.2 to 1.3:1).
- At 320 px wide the hand strip reads BRACE / SPIN 3 / TRIGGER / TWIST with open counters. The original pink does not.
- It is the black-book signature (ink on paper), so it stays cohesive in every punk style: ink and a paper keyline travel to linocut, xerox, stencil, mural. Nothing in it depends on the F1 palette.
- It keeps the owner read: pink sits only in the thin offset print, the icon and the owner scribble. C is rejected because yellow is the plan-mark colour in the ART CALL 51 grammar and would blur "card" with "plan". B is a close second (white chisel looks best on a busy dark poster). D is the fallback for styles whose paper is busy (collage, Ben-Day): the strip makes the title independent of what is behind it.

## Plate
`plate_pick.png` is the full p1 decide plate (1920x1080) with the A titles. Everything else is F1 unchanged (ART CALL 51 grammar, same game information), except:
- The needle is removed (ART CALL 52 note 3): the small marker at 12 o'clock on the outer schedule ring at sector 0. The half-round sector-0 digit chip beside it stays; it is the ring's own digit, not the needle. If the designer reads it as a leftover, hide that chip as well.

## Rules and layout
`LAYOUT.md` holds the zone boxes and the legibility rule other styles must meet.

## Files
- `sheet.jpg`: 4 options and the original at 2x, rules, 1x and 320 px strips
- `legibility_1x_320.jpg`: true 1x pixels and 320 px wide, side by side, per option
- `hand2x_orig|A|B|C|D.jpg`
- `plate_pick.png`
- `src_snapshot/`: changed generator files (`st_cards.py` title_draw modes, `f1_hand.py` cache key, `f1_render.py` needle removed, run scripts). Full working copy: `D:/rc_scratch/combat_redesign/punk/card_titles/src`. Set `RC_TITLE=A|B|C|D` to render a mode.
