# Proposed ART_BIBLE amendments from the converged Shifting Waves pass (NOT applied; ART_BIBLE.md is untouched)

Each item is replacement or added text for the named section. They come from drawing the converged board (one board: code base in the centre, 3 wave rings around it) strictly in the bible's own media. Evidence: `p1_decide.png`, `p2_preview.png`, `p2b_hover.png`, `p3_resolve.png`, `compare_converged.jpg`, `e7_readiness.jpg`. The five amendments from the bible study (BB_bible NOTES section 6) are 1-5 below; 6-9 are new, found while building.

## 1. Forecast surface (replaces the "No forecast tags, no NEXT plates" bullet in 3.1)
> **Forecast (modes with scheduled threats only, e.g. Shifting Waves).** Directly under the HP result chips sits one **NEXT row**: the label `NEXT` (Share Tech Mono 20 px) then the same chips in the same order, `[final] (absorbed) -other`, computed from the sim's own preview of next turn if nothing more is played. The row is a CRT plate, never a tag on the board. While a card with options is hovered (Twist +1 / -1), the NEXT row splits into one row per option (max 3), the selected one outlined in yellow, and each row may carry a 6-cell sector strip (sector digit over raw landing value). This-turn chips do not change when the card changes only next turn (state it in one mono line: "this turn costs the same"). Other modes keep "no forecast tags".

## 2. Ring wheel (new 3.2b, after "Wheel frame")
> **Ring wheel (a board that carries the fight).** One wheel frame may carry up to 3 concentric **ring cells** around the player's wheel, drawn in family C: the unit's programme screen in the owning corp's bezel. Rings are radially aligned with the player's slices so a sector is one radial strip. The frame may be scaled to r = 460 (1080p) when it carries the board; the code base keeps r >= 170 slices. Ring depth is told four ways, never colour alone: concentric position, a lane style on the cell border (now = solid red 4 px, +1 = solid pink 3 px, +2 = dashed pale 3 px), the same style on the unit token base, and the words `NOW`, `+1`, `+2` on the ring gutter at 30 deg. An empty cell is dark glass with a 30 % lane border. Sector digits 0-5 sit in the bezel; the needle is sector 0. A unit more than one sector wide is ONE cell spanning its sectors with the token centred, and every slice it covers gets threat trim (3.4b).

## 3. Schedule bezel (replaces the readout-rail rule in 3.2 for wheels that print a schedule)
> **Schedule bezel.** The readout rail stays for slice values. A printed rotation or timer schedule is drawn as **bezel cells** on the wheel's outer bezel instead: one cell per printed step, from the needle clockwise, arc length = step x 60 deg, chevrons in the direction of travel, text laid along the arc in Share Tech Mono >= 16 px (`+2 THIS TURN`, `+2 NEXT`, `+1 THEN`, `HOLD` for 0). The live step is filled; later steps are dark with bright text. A preview that changes the live step extends it with a yellow cell (`TWIST+1`) and shows the alternative as a dashed notch (`TWIST-1`). **Rail rule:** any rail or bezel text must be >= 16 px at 1080p; otherwise it moves to chips or bezel cells. Text on the lower half of a wheel is flipped so it reads left to right.

## 4. Threat trim (new 3.4b, and one line in 2.3)
> **Threat trim.** Slice colour stays the slice TYPE (2.3). Hostile ownership and timing are carried by trim: enemy cells sit in the corp bezel (Meridian orange) and take the lane border of 2b. A player slice that will be hit this turn gets a solid `HARM` #FF4433 LED arc on its outer edge; one hit next turn gets a dashed pink arc. Trim is a shape (solid / dashed) and always has its number in a chip or cell. **Slice states:** `HOLDS 1` (a shield that blocks and survives at 1 HP) = amber badge `9>1` plus the word HOLDS; `BROKEN` = red badge `6>0`, red hatch while previewed, black-out and red X once resolved, plus the word BROKEN. The two never share colour or word.

## 5. Unit glyph set and unit cells (adds to 3.5 and 3.4)
> **Unit glyphs (twin check required).** Packet = square with an arrow, Worm = zigzag, Jammer = ring with a slash, Payload = diamond with two bars, Adjuster = skull. White silhouette, ink outline, as 3.5. **Unit cell read order**, single file along the cell's own axis: `[token][was][value][HP][arrival]`. Token = glyph on a disc of radius 27 in the unit's programme colour (72 %) with the lane style as its border; value = Anton 36 (arriving damage); `was` = struck old value in mono, only for a wounded unit; HP = plate glyph + number, `8>3` in red when this turn changes it; arrival = arrow + sector digit in the lane colour, back rings only. Plain text with ink stroke, no boxes. Kind must be readable at 320 px by colour **and** silhouette size: token >= 54 px.

## 6. State overlays, adds to 3.8
> BROKEN and HOLDS 1 as in 4; PREVIEWED BROKEN = red hatch at 60 %; FIREWALL MARK (sector burn pending) = orange hatched wedge with a flame glyph, `-4` pop per unit burned.

## 7. Card-play preview, replaces the last two sentences of 3.17 for wave cards
> A card that acts on the enemy, not the wheel, previews on the schedule bezel (3), the NEXT rows (1) and the unit arrival digits, which update to the hovered option. No ghost cells on a ring wheel (ghosts on 18 cells are clutter): ghosts show a number only. The player's plan or a hovered unit's path is the only grease pencil: yellow, 7 px with an ink edge, spiralling through the cell centres ring by ring to the slice it hits, with one CRT tag (`WORM lands in 2: 20 on BURST (6 HP)`). Other units dim to 38 % while a unit is hovered.

## 8. Clutter rule, adds to 3.21
> Ring wheel budget at rest: <= 12 loose chips on the board (ring labels 3 + slice HP badges 6 = 9 as drawn); sector digits and the schedule are bezel engravings, unit HP/arrival are cell text, not chips. Everything else lives in the right-hand plates.

## 9. Bill closure, adds to 3.1
> Under the HP chips one mono line closes the bill with the sim's own numbers: `62 RAW - 10 SHOT DOWN = 52 = 33 THROUGH + 19 ABSORBED` (resolve: `14 RAW - 5 RIDER = 9 = 0 THROUGH + 9 ABSORBED`). A raw figure must never be shown before the gun phase it does not survive.

## 10. Layout (3.1) when the wheel carries the board
> The wheel is placed left (about (500, 545), outer r 460); the right 900 px hold, top to bottom: title plate, YOU bill, NEXT rows, ADJUSTER plate with range track, RAM / TRACE terminal; the hand bottom right with SEND IT overlapping its last card; CELL-9 sticker bottom left; UNDO above SEND IT. Nudge buttons: not drawn when nudge is a card (designer call still open from the bible study).

## 11. Waves and wide units (E7 readiness, e7_readiness.jpg; illustrative)
> Printed waves beyond the rim are concentric arcs outside the bezel, one per wave, each with a `W<n>` tab and pips for its units; the climax wave is the outermost arc in HARM red with yellow hazard stripes. A `WAVES N LEFT` CRT plate with N pips and a struck-out pip per past wave. A Trigger shot that pierces is the player's plan: yellow pencil along the sector with an X on each unit pierced.
