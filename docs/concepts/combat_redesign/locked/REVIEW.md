# Locked player family (ART CALL 53): art director review

Saved by the orchestrator from the art director's returned text. Board: `review_board.jpg`.

The locked board passes ART CALLs 51-53 with fixes. It reads as one system, the cards fit the spinner, and roadmap steps 1-2 are nearly done. Before steps 4-5 start there are four must-fix items: TOWER and WAVE use the RAM and Trace colours, two sector digits are half hidden, the hand overlaps the wheel rim, and played cards no longer show their names. Step 3 has not been done.

Review board: D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/review_board.jpg (3000x4585). It has four rows: E10 vs F1 vs locked p1, the card sheet, Solace vs Meridian, and zoomed crops of the defects. The script that builds it is D:/rc_tmp/claude/claude/C--Users-noitu-AppData-Roaming-Claude-scratch-workspaces-1c092eb2-44e7-479e-859a-83b75e36eb3c-d0376422-bd95-40f9-844b-6e7d2a954ea6-scratch-2026-11-01-0b9d75/4dfa2e73-e058-412d-b93c-b95aedb48b42/scratchpad/build_review_board.py

**What I looked at:** assembled p1, p2b and p3; corp p1 for Solace and Meridian; the card sheet; the wheel crop; the grey proof; the rings crop; before_after; and the WPAP hand crop. I did not open p2_preview, p1_nowords, srv, gh, Meridian p2b, type_band_key or legibility_1x_320.

## ART CALLs 51-53, note by note

**ART CALL 51**
- **1. Player-owned style:** met. The disc, nameplate, SEND IT, UNDO and cards are all paper, black key line and pink halo.
- **2. No dashed lines:** met. The audit found 0 dash calls and 0 dotted-mark calls on 7 plates. It checks drawing calls, not pixels.
- **2. This turn vs future:** met. The THIS TURN tape is silver; HOT/COLD/FAR and the W4-W6 tickets are in place.
- **3. Pending loss:** met. It is cross-hatch, and the hatch colour follows the cause (red).
- **4. Arrowed outline:** met. It is used for movement only (the yellow arrowed path on p2b).
- **5. Outline colours:** met. Enemy outlines are one graphite enamel.
- **6. Waves past 3:** met. W4-W6 are tickets.
- **7 and 9 (effect overlays, per-card hover plates):** not in this pass. They are roadmap steps 4 and 5.

**ART CALL 52**
- **1. Card titles:** met. White fill on a black plate with a keyline, 17.7:1. Cap height is 32.7 design px (37.6 on screen); Firewall is 29.5 (33.9 on screen).
- **3. No needle:** met on every plate.
- **Art-pass read (punk across the whole board):** reinterpreted. The rings are now enemy territory, so the punk look stops at the tower edge and the outer rings carry the corp. I accept this; it is what gives player vs corp its clarity.

**ART CALL 53**
- **Spinner:** met. Xerox inks, the linocut black key line with a block drop, a pink scissor-cut halo, and TURRET on Ben-Day bullseye rings.
- **O-28:** met. On the p1 wheel crop, both hatched slices (the top-right SHIELD and the right-hand TURRET) still show their type through the solid ring round the icon, and the seats still separate by value in the grey proof.
- **Cards:**
  - **WPAP frame, type plate and title plate:** met.
  - **Different colour behind each type word:** met. TOWER is teal #19D3BC, WAVE is violet #A683FF. The state has only these two types.
  - **Background art from the other punk styles:** met. All six are used (Ben-Day, linocut, collage, mural, xerox, Jinx).
  - **Xerox icon recoloured to contrast its background:** met.
  - **Problem 1, colour meaning:** the two type colours repeat HUD resource colours. Teal is close to the RAM cyan, and violet is the same violet as the Trace pips and the +Trace tab, which sits right next to the WAVE plate on Trigger.
  - **Problem 2, the WPAP look:** the faceted planes are now almost hidden behind the band art. Compare punk/wpap_faceted/hand_crop.jpg.

## Does the board read as one system?

Yes, and it is the best board in the series.
- **Three clear layers:**
  - **Player:** loud punk print on the disc, cards and buttons.
  - **Corp:** a calm enamel ring set. Solace shows a membrane pattern and helix rim; Meridian shows corrugated freight and a hazard rim.
  - **System:** the cyan terminal HUD.
- **Corp skins:** both corps read as themselves at a glance, and pink stays the player's.
- **Weaknesses:**
  - On Meridian, the amber HOLD danger arc sits next to the orange hazard rim, so the two can be confused.
  - The tower zone is very loud: 56.4% of it is above the loudness threshold, against 1.3% on E10. That is by design, but it pulls focus from the enemy rings.

## Are the cards cohesive with the spinner?

Mostly yes. They share the black key line, the paper-white glyph with a hard drop, the pink spot disc and the halo. Ben-Day dots and xerox texture appear on both. The links that break it:
- The type colours (teal, violet) and two of the band colours (sky blue, sunset) do not appear in the spinner's inks.
- The type colours sit on HUD meanings, as above.
- Nudge, Spin 2 and Spin 3 look nearly identical. The arc count of 1, 2 or 3 is the only difference, and it is small.

## Check numbers

**Draw asserts**
- Locked board: 60/60 on p1, nowords, srv and gh; 46/46 on p2 and p3; 21/21 on p2b.
- Corp plates: 60/60 on p1 and 21/21 on p2b, for both corps.

**Collisions and dashes**
- Collisions: 0 px on every pair between label classes. This misses the defects below because the tape, the label plates and the hand are not in the test.
- Dash audit: 0 dash calls and 0 dotted-mark calls.

**Squint, p1 whole plate (mean / p95 / loud share)**

| plate | mean | p95 | loud share |
|---|---|---|---|
| E10 | 0.184 | 0.368 | 4.1% |
| F1 | 0.225 | 0.496 | 12.5% |
| Locked | 0.233 | 0.504 | 14.0% |

- Corp ring zone loud share: 6.7% locked, 1.1% F1.

**Cards**
- Type word on its plate: 9.8:1 on TOWER, 6.5:1 on WAVE.
- TOWER vs WAVE in grey: only 1.52:1, so they separate by hue and the printed word.
- Glyph vs disc: 3.1:1 on the pink discs (Brace, Pull, Firewall, Hold).
- Disc vs the art around it: weak on Nudge (1.87), Shove (1.5) and Twist (1.4).

**Corp skins**
- Unit-kind separation, minimum dE: Solace 6.8 / 4.3 / 2.5 on rings 0-2; Meridian 7.2 / 4.5 / 2.7.
- Tape: matches the neutral tape on 97.7% of pixels (Solace) and 98.0% (Meridian).
- Pink in the enemy zone: about 0.28% on every skin, all from game marks.

**Game information:** all 11 cards match the state, and every required word and wave ticket is drawn (a draw-call test, not OCR).

## Game-information losses and collisions

1. On p3, played slots show only the glyph and PLAYED. The card name is lost; F1 kept the full card.
2. The sector digit 0 at 12 o'clock is half hidden under the THIS TURN tape (crop A on the board).
3. The sector digit 3 at 6 o'clock is half hidden under the HOLD THEN label plate and reads as a "J" (crop B).
4. The Brace card's top-left corner covers the outer rim and the tick marker at about 4:30 (crop C). Board-vs-hand overlap is never tested.
5. WAVE violet means the same as Trace violet in the HUD, and TOWER teal is close to RAM cyan (crops D and E). This is a colour-meaning clash rather than lost information.
6. On Meridian, the amber HOLD arc is next to the orange hazard rim, so a game mark can be mistaken for corp material.
7. Ring 2 unit kinds are close on every skin (minimum dE 2.3 to 2.7), so only the glyph carries kind there.
8. Not data, but worth knowing: the Spin arcs, Strike bolts and Shove bars are decoration. The Trace eye on the card tab is not the system eye glyph.
9. Meridian's stencilled numbers are still not drawn.

## Ranked fixes

1. **Type colours.** Move them off the resource colours: TOWER to cobalt #2F5BFF with white text, WAVE to bone #F1EAD6 with ink text. Cobalt is already listed as the spare in cards/NOTES.md. If bone looks too much like the paper, use warm orange #FF8A1F (from the original WPAP orange variant). Keep the +Trace tab violet so violet means Trace only. Re-measure type vs plate (at least 4.5:1) and type vs paper.
2. **Sector digits.** Draw the digits above the tape and the label plates, or move digit 0 about 4 degrees off the tape start and give digit 3 its own gap in the HOLD THEN plate. Add the tape, label plates and hand rectangles to the collision assert as "occluder" masks, and fail on any occlusion of a digit.
3. **Hand vs board.** Shift the hand right and down by about 40 px, or tighten the fan, so no card corner falls inside wheel radius 455. Add a hand-vs-board assert to the collision check.
4. **Played slots.** Print the card name under the glyph in the PLAYED liner, in the same small caps as PLAYED, at 70% opacity.
5. **Meridian rim.** Desaturate the hazard rim by 25% and add a 2 px black gap between it and the amber HOLD arc. Alternatively, swap the HOLD arc's fill to the HOT time-mark treatment, so amber belongs to game marks only.
6. **WPAP facets.** Raise the facet planes to 25-35% opacity over the band art, tinted in each card's type colour. This also puts the type colour behind the art, which matches the designer's "different colour" wording more closely.
7. **Spin family.** Make the arc count bigger (3 px strokes, a gap of at least 10 px), or tint the band's Ben-Day dots darker for Spin 2 and Spin 3, so the three cards separate at hand size.
8. **Weak icon discs.** On Nudge, Shove and Twist, raise disc vs art to at least 2.5:1 by swapping the disc ink. On Shove, a pink disc on the cool strips would do it.
9. **Tower loudness.** Pull the pink halo and the Ben-Day density down about 10% to bring the tower zone below 50% loud. Solace ring 0 can drop to gain 2.0 if it reads busy.
10. **Re-run the checks** on the assembled and corp plates: grey proof (the current one still shows the F1 placeholder cards), squint, and OCR or pixel text read-back.

## Roadmap steps 1-3: what is left

- **Step 1 (lock the player family):**
  - Fixes 1-4 and 6-8 above.
  - A new grey proof and squint on the assembled board.
  - A design call on loudness: accept 14% loud, or apply fix 9.
- **Step 2 (corp skins):**
  - Solace is done and Meridian works as a proof.
  - Still open: fix 5, the stencilled numbers, a squint and grey proof on the corp plates, and a close look at Meridian p2b.
  - The Godot skin data format is drafted in corp/NOTES.md.
- **Step 3 (grammar on the new skins):** not done. The HOT/COLD/FAR marks, the pending-loss hatch, the arrowed outline and the enemy outline still need a visual re-check on all three skins (neutral, Solace, Meridian), including how the red hatch reads on Meridian's brown.

**Your question:** yes, your decisions are enough to unblock the roadmap. Steps 1-3 can finish as fix passes with no new designer call. After the fixes (ideally after fix 1), steps 4 (effects) and 5 (hover plates) can start. The only designer input still useful is a yes on the new type colours.

Nothing is committed. The only file I wrote in the repo is review_board.jpg; the board script is in the scratchpad.