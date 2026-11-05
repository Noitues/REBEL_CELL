# Combat redesign: visual-language plan (art director)

Date: 2026-11-01. Branch art-pass, documentation only. Serves ART CALL 51 (designer review of the E10 redesign).
Legend sheet: `VISUAL_PLAN_legend.png` (1920x1080, the grammars below drawn at use size).

**What this is.** The rulebook every designer in this redesign follows. It replaces BRIEF.md section 3 ("cohesion bible") wherever they disagree. BRIEF.md section 3.1 said "keep E10's whole read"; that instruction is withdrawn. The designer asked for a real redesign (note 10). Style, element shapes, line language and layout may all change. **Only the game information stays fixed**: the same state (`state_e10.json` f1 / f2 / f2t / f2b), the same numbers, words and rules text, and no new mechanics.

**R51 review (2026-11-01):** the exploration round is reviewed in `REVIEW.md` (board: `review/board.jpg`). Finalists: **F1 Black-book burner** (sketchbook graffiti tower + street-graffiti cards and SEND IT) and **F2 Zaun press** (Spider-Verse print, pushed misregistration, Arcane neon doodle layer). Rules changed by that review are marked **R51 review** below. No finalist plate may be rendered on the E10 board.

**Designer rulings (binding; added 2026-11-03).** These are the designer's explicit approvals made after this plan was written. Where they disagree with a rule below, or with a LOCKED ART_BIBLE section, the ruling wins. Reviewers judge the plates against these rulings. The art-pass calls made in response to the 2026-11-03 review are in `locked/REVIEW_RESPONSE.md` and are not designer rulings.

| # | Ruling | Designer's words | Overrides |
|---|---|---|---|
| DR-1 | No dashed lines; this turn must look different from future turns; cross-hatch replaces the HP slash; the arrowed outline is kept; outline colours must carry meaning; waves past W3 are compressed; slice-wide effect overlays in distinct families; hover dimming kept, with plates per card effect type; content rulings are out of scope (ART CALL 51) | 10-point note, 2026-11-01 | none |
| DR-2 | The player spinner is **punk rock**; there is no needle; colour-blind checks are ignored for this concept work (ART CALL 52) | "Punk rock." / "we shouldn't have needles in this new combat concept" / "Ignore color blind checks." | 0 law 5 and E "Contrast checks" (no CVD runs) |
| DR-3 | Cards are adapted to the new art style on a similar layout, with cohesion over keeping the black-book look | "feel free to adapt the card concept to the new art style keeping a similar layout. Rather have cohesion" | none |
| DR-4 | **Each slice type has its own colour and texture** | "each unique slice is a different color and texture instead of just all slices the same color" | 0 law 5 ("no slice-type colours"), E table row "Slice frame" |
| DR-5 | **No reserved colours** for player-family fills (slices, card type plates, card art) | "I dont think we need to avoid any colors" | A.1 invariant "never HARM red, PLAN yellow, SCHEDULE orange, SOAK indigo or GAIN green" (for fills; meaning tokens keep their meanings on *marks*) |
| DR-6 | **Corp enemy layers carry a corp theme**, even if only a colour shift; the test was colour-only vs colour plus material, with Meridian as the second corp | "prefer the corp layers have more of a theme related to the corporation, even if just a color shift" | ART_BIBLE 2.4 "Solace never appears on a link or ring" / "corp hue MUST NOT be used for any UI role" (for the combat enemy rings; see the 2.4 note) |
| DR-7 | Spinner: xerox A (flat spot inks, a distinct texture and grey value per slice type) with the linocut black key line and scissor halo, borrowing Ben-Day texture shapes; a solid coloured ring round the icon on hatched slices (ART CALL 53, O-28) | "Agree with art director suggestion." | A.1 direction table (G1-G5) |
| DR-8 | Cards: **WPAP card style, a different colour behind each type band** (WAVE, TOWER...); **background art drawn from the other punk card styles**; xerox icons recoloured to contrast the background (ART CALL 53) | "use WPAP card style with different color behind WAVE etc. then use different card background art pulling from the other punk card art styles. Keep the xerox icon approach but recolor to contrast the background." | A.1 "one hand" invariant, for the band art (the frame, key line, disc, icons and grain stay shared) |
| DR-9 | Combat backdrop: the procedural **cutaway** room (ART CALL 47, 2026-10-30) | "Some light procedural generation work to define the interiors, then we just toss that up. Seems like easiest and keeps on brand." | ART_BIBLE 3.14 camera rule, for regular Site fights and HQ-run nodes (see the 3.14 note) |
| DR-10 | **T5 / T6 story** (ART CALL 49 items 5 and 6, 2026-10-30; recorded 2026-11-04). T5: the wheel flies in (the player spinner: the enemy rings are what then surround it), then the enemy rings fly out of the iso room as binary bits and close round it. T6: the board dissolves into bits and the player is back on the netrun street; on a failed run, a netrun-failure screen follows instead | 5: "the wheel flies in, then the enemy invading rings fly from the isometric room as binary bits to surround the wheel, and combat starts." 6: "Combat ends and dissolves into bits, back to the netrun. Or the run fails, which needs a netrun-failure transition screen." | none. ART_BIBLE 1.2 still sets how the bits look (colour of their source, white-hot, flipping, tumbling, round the rim). Bits option A (O-25) and failure screen A (O-26) are art-pass picks, not rulings (`locked/transitions/NOTES.md`) |

**Parked (designer note 8, content rulings):** the inspect panel, hover tag text (`hover_tag` keeps its E10 form and content), the UNDO cause and pile counters. Nobody designs these in this pass.

---

## 0. The five laws (read these first)

1. **Every element belongs to exactly one family** (section A), and a family is told by its **material and line**, not by its colour. When you squint at the screen with colour removed, you can still tell the player's things from the enemy's things, from the clock, from the HUD.
2. **A line type has one meaning** (section B). Dashed lines have **no meaning** on the combat screen: they are banned.
3. **This END TURN is hot; future turns are cold** (section C). Hot means saturated, filled and glowing. Cold means desaturated, never glowing, with turn pips.
4. **Cross-hatching means "lost at the end of this turn"** (section D). The colour of the hatch says who causes the loss.
5. **Colour means a cause or an owner, never decoration** (section E). An outline that does not mean something is neutral. There are no lane colours. (Slice-type colours: superseded by designer ruling DR-4; each slice type has its own colour and texture.)

---

## A. Element families

There are seven families. Each signature below lists material, line, shape language, colour role, type and motion, so that no two families can look alike.

| Family | Material | Line (section B) | Shapes | Colour role | Type |
|---|---|---|---|---|---|
| **P PLAYER (the Cell)** | Hand-made: paint, spray, marker, paper, tape (the style direction chosen, see A.1) | L2 painted stroke | Irregular, hand-cut, slightly off-true (max 2 deg tilt, 1.5 px wobble) | `CELL_PINK` = ours | Anton + hand-lettered display |
| **E ENEMY (Solace corp)** | Clinical vector on frosted glass: perfect geometry, enamel hairlines, flat cool washes | L3 vector hairline | Perfect arcs, true circles, mitred corners, constant widths | Neutral enamel; kind washes are cool slate | None on the board |
| **T THREAT (what the enemy does to you)** | Stencil-cut: flat colour with a hard ink keyline, no texture | L1 keyline only, filled shapes | Chevrons, diamonds (HP through) | `HARM` | Hero digits only |
| **K CLOCK (time and schedule)** | Machined gunmetal dial: engraved grooves, stamped digits | L4 engraved line, L5 arrowed outline (schedule step) | Arc bands, ticks, notches | `SCHEDULE` orange on step cells only | Share Tech Mono on the bezel, Anton tags |
| **N PLAN (the player's intent)** | Grease pencil on glass: waxy, grainy, no glow | L6 grease pencil (+ L5 when it is a route) | Freehand paths, X end caps, underlines | `PLAN` yellow | Mono 23 (2026-11-03: 18 gave a 12.6 px cap height, under the 16 px floor) |
| **X EFFECTS (events, overlays)** | Light and print: additive light, halftone dot screens, speed lines, comic hit frames, krackle | L9 glow, halftone fill | Slice-wide and cell-wide fills, starbursts, shards | The colour of the cause (E) | None |
| **S SYSTEM (HUD)** | CRT terminal glass: flat navy glass, scanlines, cyan edge | L3 at Fine tier on the plate edge | Rectilinear plates, radius 8 | `NET_CYAN` = the terminal itself, RAM | Share Tech Mono 23, Anton heroes (2026-11-03: 18/22 gave 12.6/15.4 px cap heights; the floor is 16 px, and Mono 23 gives 16.1) |

The squint test is the acceptance test: at 320 px wide and in greyscale, P must read as rough and textured, E as thin and perfect, K as engraved metal, S as flat glass. T is the only flat, saturated, hard-edged red shape. X is the only light that blooms.

### A.1 P PLAYER: the art-style family

The tower, its slices, the player's HP, the guns, Brace, soak, the cards, SEND IT and the nameplate are **one object family**, drawn by one hand. **This is where art style is the goal** (designer note 1). Five directions compete. Two finalists are taken to full plates, and the designer picks one:

| Dir | Name | Signature on the tower | Signature on the cards | References (from knowledge) |
|---|---|---|---|---|
| G1 | **Street graffiti** | Wildstyle wedge fills in fat-cap spray with fade, chrome-and-outline letter logic on the slice edges, drips off the outer rim (max 3, never across a sector line), throw-up bubble outline on the hub | Each card is a painted wall chunk: spray fill, tag-style title with 3D drop, sticker slaps for cost | Miles' room and tag world in *Into the Spider-Verse*; Jinx's neon spray in Zaun (*Arcane*) |
| G2 | **Sketchbook graffiti** | Black-book page: ballpoint construction lines left visible, marker fill that misses the line by 2 px, hand cross-hatching for shadow, pencil arrows | Cards are torn black-book pages: graph or dot paper, marker title, doodles in the margin, a tape strip | Miles' sketchbook pages; Jinx's doodles and scrawled notes |
| G3 | **Spider-Verse print** | Offset-print misregistration (pink and cyan plates offset 2-3 px), Ben-Day dot shading, hand-inked contours of varying weight, comic panel borders | Cards are comic panels with a caption-box rules text and an inked title | *Into the Spider-Verse*: misregistered print, dots, inked lines, hit frames |
| G4 | **Arcane painterly** | Hand-painted brush texture over the wedge forms, visible brush highlights on the rim, ink accents on edges, a neon doodle layer over the paint | Cards are small painted canvases with brush-lettered titles and neon scribble accents | *Arcane*: painterly textures over 3D, brush highlights, Zaun grime |
| G5 | **Zine collage** | Cut-paper wedges, xerox grain, tape at the joints, ransom-note glyph cut-outs | Cards are photocopied flyers: xerox toner, cut-out title letters, staple | The project's own Punk Zine voice (STYLE_GUIDE 1) |

**Invariants every direction must keep (these are not open):**
- **Ownership read.** The tower and the cards must look like *the same hand made them*, and like nothing else on the screen. One shared texture or stroke (the "hand") appears on both.
- **The player is pink.** `CELL_PINK` #FF3DA8 is the identity ink. Paper is `PAPER` #F2EEE4 and the zine ink is `ZINE_INK` #111111. A direction may add **one** secondary ink of its own (for example spray chrome #C9D3E0 for G1, or ballpoint blue #2C3E9E for G2), but never HARM red, PLAN yellow, SCHEDULE orange, SOAK indigo or GAIN green.
- **Readability caps.** Texture contrast inside a slice is at most 18 percent of the icon's contrast, and no texture sits within 6 px of a slice icon or an HP segment. Slice icons stay white silhouettes with ink, 44 px (they may be redrawn in the style, but they must survive the nowords plate and the 320 px squint).
- **Not on the board's information.** Drips, tape, doodles and spray overspray never cross a ring cell, a landing arc or a threat mark (GDD 9.2: zine never covers the wheels). Decoration lives on the tower (r 0-162), on the cards and on the stickers.
- **Halftone belongs to X EFFECTS.** G3 may use dots only inside the hub art and the card art band, at 12 percent coverage or less. If G3 wins, X switches to its fallback signature (light leaks and speed lines, no dots).
- **No glow.** Paint does not glow. P never blooms (the X family owns light).
- **R51 review: value cap.** The brightest large P fill on the tower is L* 75 or less (paper discs multiplied to 70-72 percent value; cards at 88 percent). Peak value order: SEND IT, HOT T marks, the lifted card, tower slices, the rest of the hand, E cells. **2026-11-03 (art-pass, review response):** the K clock (tape, sweep, plates) sits below the tower at L* 45-55 gunmetal, with SCHEDULE orange on the live step only. Slice inks are L* 60-72, and the icon discs carry the tower's peak. Occupied E cells are at L* 40-45 vs empty cells at 28 (3:1 floor). Token discs never outrank HOT marks. **2026-11-04 (art-pass, gate 1; corrects the line before):** "HOT second under SEND IT" covers every mark, not only the families: every E, K, T and N mark class (enemy HP ticks, the Adjuster HP and plate, badges, sector digits, ring tags, bezel labels, wave tickets, token discs, COLD, FAR, the plan pencil) and the gun tracers and hit stars have their p99 at least 1 L* under the HOT p95, and every E and K mark has its p95 at least 1 L* under the tower p95 (rb_checks b, one row per class). So the E and K type sits at one value, L* 84: HP ticks `CREAM_HP` #DBD1B7, the sector digits, ring tags, W tags, ticket glyphs and nowords tallies `K_TYPE` #CBD2DB. The gun hit star is `HIT_PAPER` #DED8CA (L* 86), not white, and the armour rail edge is #C4CBD8. Still open: the thin 1 px ring and band lines (ring NOW outer boundary, schedule band edges) peak at L* 95-100 on the plates and are not yet a gated class (`locked/final/NOTES.md`, "2026-11-04 gate 1"). **Closed in round 2 (2026-11-04):** they are capped, classed and gated (A.2, A.4), and the token-disc rule holds per disc. The measured cell values are in A.2; the "L* 28 empty" figure above could not meet its own 3:1 floor (occupied L* 45 over empty L* 28 is 2.6:1 in luminance; 3:1 needs the brightest empty at L* 26 or less) and is replaced there.
- **2026-11-04 (art-pass, gate 1): tower loudness, squint vs ink value.** The O-29 squint target (tower zone r ≤ 212 under 50 % loud) and the review 2.15 prescription (slice inks at L* 60-72) cannot both hold. The squint counts a 16 px cell as loud above encoded luma 0.38, which is about L* 43, so any slice ink in the prescribed band is loud. Measured on the rebuild: 59.3 % (p1), 68.7 % (p2), 57.0 % (p2b), 68.2 % (p3); the locked first pass reads 56.4 / 65.3 / 54.3 / 64.4 %, and the gate measured the O-30 plates at 48.6 (p1) / 57.9 (p2) / 57.5 % (p3). So the rebuild is louder on this measure than O-30. Which change drives it (the slice inks, the textures, the lit ring NOW glass that falls inside the 16 px cells at r 197-212, the hub) was not isolated in this pass. Meeting 50 % would need the tower zone's cells mostly under L* 43, so slice inks well under the prescribed L* 60. **Call (art-pass):** the tower's loudness is gated by value, not by the squint share: slice ink means in L* 60-72, the icon discs carry the peak, and the tower p95 sits under the HOT marks and SEND IT (rb_checks b). The squint share is reported per plate (`final/checks.json` `squint_tower_zone`) and not gated. This is an open question for the designer (`final/NOTES.md`, "2026-11-04 gate 1").
- **R51 review: icons are re-inked, not re-designed.** One turret stays one turret, Brace stays the clamp, Twist stays the ring arrow.
- **R51 review: shading on P** is single-direction hatch only; cross-hatch stays L7 (loss at END TURN).
- **2026-11-03 stage 2 (art-pass, review 2.7 + check c):** the whole hand is on screen, with its lowest card pixel at least 12 px above the bottom edge (y ≤ 1067). The fan's left card is centred at x 1035, base y 904, with a 4° fan. The lifted card is centred at y 812 and pushes its neighbours 16 px. Rules text is Plex Condensed 21 on one line, or on two lines broken at a word (never shrunk), so its cap height is 16 px or more at the 1.10 hand scale. The NO RAM tab is Anton 17 (cap height 16.1 px).
- **2026-11-04 (art-pass, round 2; C6, C10; measured on the published plates).** The lift in the line above ("centred at y 812, pushes its neighbours 16 px") is replaced by H, the lift (C6): the lifted card stays at the hand scale and rises straight up to centre y 718 (slots 1-3), the fan never closes, and the cards right of it open 30 px (board p2) or 36 px (hover). Lowest hand pixel: 12 px above the edge on the board (15 on p3), y 1064-1067 on the hover plates. Value order as measured on p1 (neutral, p95 per class, `final/checks.json` check b): SEND IT 98.2 > HOT 94.9 > tower 89.5 > hand 83.1 > token discs 82.6 > K clock 69.5 (median 47.8) > E occupied glass 45.5 > room 37.8 > E empty glass 21.0. On the hover plates the lifted card reads p95 90.4-91.1 over the resting hand's 71.3-72.0. C10 (an art-pass call, open to the designer; it answers R1_REREVIEW question 1): the value gate governs the tower, and the squint share is reported only. Round 2 reads 59.3 % (p1), 68.7 % (p2), 57.0 % (p2b), 68.0-68.2 % (p3) and 59.9 % (nowords); no texture rework was done for it.

### A.2 E ENEMY: Solace corporate vector

The contrast to P. It is clean, cold, machine-made and perfect.
- **Cells:** frosted glass wash in a cool **kind slate** (Packet #3D5466, Worm #4B4A6E, Jammer #2D5D69, Payload #5B5560, Ring #55617A; Adjuster is gold, see below). The minimum dE between kinds is 10 in all four vision modes (the designer of this family must measure it and report). The E10 mauves are retired: with the player now pink, mauve units would read as player-owned.
- **Line:** L3 vector only. The edge is `ENAMEL` #D9E1EA at 1.5 px, with a 3 px ink line outside it. All cell outlines are this one colour on every ring: **no lane colours** (designer note 5).
- **Texture:** one Solace clinic motif (a thin double-helix rule) at 6 percent contrast inside the cell screen. It replaces the skull motif, the code text, the CRT dot grid and the programme bezel corners (all retired).
- **Tokens:** the disc is 54 px with an `ENAMEL` 2 px ring and the kind glyph from the kglyph2 master. There is no lane-coloured base ring.
- **Enemy HP:** `CREAM` #FFF4D6 vector ticks (D below). **2026-11-04 (gate 1):** on the board the ticks are `CREAM_HP` #DBD1B7 (L* 84), the same hue at the E / K mark value, so they sit under the HOT marks and the tower (A.1).
- **Adjuster (boss):** `BOSS_GOLD` #D69A1A (2026-11-03 re-pick, see E) is its body, its cell edge (2.5 px, L3), its ward and its HP. It is the one enemy mark with colour on its outline, because gold means "the boss". **2026-11-03 (review 2.13):** its HP is one solid gold edge cut into square segments by ink lines, with no beads and no white slash. The only hatch on the boss is the HP it loses this END TURN (L7 in the cause colour). **2026-11-04 (gate 1):** the track splits its two groups of five around the diamond plate (5 px clear of the plate's ink and glow), so no segment sits under the plate or the hit star. The plate's skull takes the token glyph value (#C8CED8, L* 83; it was white) and its inner edge `BOSS_GOLD_HI` #F0BE46.
- **2026-11-03 (art-pass, review 1.1):** occupied glass is lit (ring NOW mean L* about 44, +1 about 37, +2 about 31) and carries a programme screen (an inset frosted panel with an enamel frame). Empty glass is L* 21 / 16 / 12. The gate is occupied / empty luminance of 3:1 or more per ring. HP ticks are 9.5 px tall. **2026-11-04 (gate 1; corrects the numbers before, which were fill targets, not measured):** the gate is now occupied glass vs the **brightest single empty cell** of the same ring on the plate (or the probe cell of the same sector), not the ring's mean empty. Fill targets are occupied 44.5 / 39.5 / 34.5 and empty 19.5 / 14.5 / 11.0 (before the skin material). Measured on the 15 published plates (cell glass with marks cut out, L* of the mean luminance): occupied ring NOW 42.7-47.8, +1 38.7-39.7, +2 33.9-35.6; the brightest single empty cell per ring 20.6-24.0, 17.0-20.5 and 14.6-18.2; lowest ratios 3.20, 3.44 and 3.15 (`locked/final/NOTES.md`, "2026-11-04 gate 1"). A unit that dies at this END TURN keeps its lit glass (the gun tracers end on it); its loss is the L7 cross-hatch in the cause colour (`CELL_PINK`, our guns) clipped inside the cell with a solid 2 px L7 edge, and its chevrons are dimmed 55 % toward the bed (they will not land). The 62 % "gone" veil is retired. Check a gates live and dying cells; hover-dimmed cells and ghosts are reported only.
- **2026-11-04 (art-pass, round 2; R1_REREVIEW C3, C4, C7):** the E line is `ENAMEL`'s hue at L* 80 (`E_LINE_L`), graded per ring by the time grammar as before: the unit cell outlines, the token lane rings, the arc discs' lane rings, the landing-arc frames, the ring-tag boxes and the queue feed. At full `ENAMEL` with its glow these 1 px lines read L* 95-100 at their peak, above HOT. Every board pixel inside r 480 at L* 80 or more now belongs to a capture class of check b, and each class keeps its p99 at least 1 under the HOT p95 (E and K classes also keep their p95 at least 1 under the tower p95); an unclassed bright pixel fails the plate. The token-disc rule of A.1 holds per disc, not for the pooled class. The dying unit's glass is measured whole, its L7 hatch included and only the gun tracers cut, and gated like a live unit (3:1 vs the brightest empty cell of its ring); its glass is lifted 12 % in luminance under the hatch. Open: `FOCUS` drawn at its token (#D4FF00) is L* 94.1, so it cannot sit 1 under a HOT p95 of 94.9-95.4 and also stay within dE76 3 of its token. On board p2b, the only board plate with FOCUS, there are no HOT marks, so the HOT rule has no reference there and is not applied. The hover stage, where FOCUS and HOT meet, needs a designer call (an exception for FOCUS, or a darker FOCUS token).
- **2026-11-04 (art-pass, round 2, measured on the published plates; C3, C4, C7).** Board, 15 plates (check a): live ring-NOW occupied glass L* 42.6-43.2; the brightest single empty cell per ring 20.6-24.0 / 17.0-20.5 / 14.6-18.2; lowest live ratio 3.17 (neutral), 3.31 (Solace), 4.11 (Meridian), and on p2b 3.15 / 3.38 / 4.35. The dying glass, measured whole: 3730-4807 px at L* 49.6-51.2, 4.49-6.07:1 against the brightest empty cell (the glass between the hatch lines alone 3.82-5.25:1). Hover, 26 plates: check a passes on all, lowest gated ratio 3.10-4.29; the h03 dying cell under the tracer reads 3.98:1 and 4.19:1 (it was 2.62:1), the other dying cells 4.19-4.52:1. Unclassed bright pixels (L* 80 or more inside r 480): 0 on every board and hover plate. Token discs: p95 82.6-84.4 and p99 85.4-91.0 per disc. FOCUS is still open: drawn at its token it reads L* 94.1, and on the hover plates, where it meets HOT, the HOT p95 is 92.2-96.0, so the margin is -1.9 to +1.3. Reported, not gated, until the designer calls it.
- **2026-11-03 (art-pass, review 1.3 + 1.4, DR-6):** a corp skin themes the rings by material (Solace membrane, Meridian corrugation). The corp hue goes only on the rim, the bezel lip, the crest and the cell edges. Cell fills stay neutral slate with a low-chroma tint.
- **2026-11-04 (art-pass, round 2; C16, C18; within DR-6).** Solace's skin ink is the celadon / teal glaze family (E), not leaf green: the rope, cell edges, bezel lip, crest strands, token frame dot and ticket edges. Measured on the plates: the rim as drawn (r 491-498) has median #3B827F (L* 50.0, C* 23.5, h 192.7), dE76 61.3 from `GAIN` and 53.4 from the hub HP ring green (gate 25 or more), with 0 % green-hue pixels in the rim band. The two corp rims differ in luma as well as hue (C18): rim band mean L* 48.4 on Solace against 25.1 on Meridian; Solace a twisted rope at 52 cycles per turn and 5.4 L* amplitude, Meridian hazard stripes at 18 cycles and 1.6 L*. The unwrapped rims at the foot of `locked/final/grey_proof.jpg` show it in grey. Teal is on the board, hover, backdrop and transitions plates; the effects set (G) still shows the leaf-green rim.
- **Corp hue:** `corp_solace` #3DFF8B never takes a UI role. Solace shows by material (clinical glass, enamel, helix motif) and by the backdrop room.
- **2026-11-03 stage 2 (art-pass, review 2.8; the camera stays the cutaway per DR-9):** the room behind the board is readable again. In the rb_checks room region (x ≥ 1100, y ≥ 420, outside r 505, with the HUD, hand, buttons, nameplate and hover tag cut out), its mean L* is 28-34. The region also leaves out the UI scrim slabs (`hud_scrim`, the HUD column and hand grounds) wherever they darken the room by 15 % or more. Those slabs are UI ground. On p2 and p3 they covered half the region, because the taller HUD hides the lit upper room. Its p95 sits at least 1 L* below the ring-NOW occupied glass p95 (L* 40 when no ring-NOW cell is live, as on p2b), so the board still comes first. The grade (`bd_grade` rb2-1, `locked/backdrop/grade.json`) lifts the room with a local tone, not a flat haze, so ink lines survive. The hull follows the cutaway box's walls. **Seam:** where the city meets the room, the blur ramps in one pass, the city keeps 30 % of its chroma, and the haze takes the room's own light colour near the box. The neighbouring facades become one lit street, not a second purple picture. **Rooms per skin:** neutral and Solace fight in the bio lab. Meridian fights in the shop (the only kit room with no Solace sign), with its lime light pulled to an amber corp light (hue 20°, 0.88). The room is the one place the corp hue may sit outside the rim, lip, crest and cell edges (review summary: "colour on crest, lip and room").
- **2026-11-04 (art-pass, round 2; C9, an art-pass call open to the designer; it answers R1_REREVIEW question 2).** The 28-34 gate is on the room itself, with the UI scrim slabs cut. The room as seen, scrim kept, is reported and accepted, with no scrim change. Measured: board room 31.0-32.1, as seen 22.9-28.9 (p2 25.3-25.4, p3 22.9-23.1, p1 / p2b / nowords 28.0-28.9); the nine backdrop plates room 31.6-32.4, as seen 28.65-29.30, both gated 28-34 (`locked/backdrop/checks.json`). The grade is unchanged (`bd_grade` rb2-1).

### A.3 T THREAT

Chevrons (hit per slice), diamonds (HP that gets through), the threat trim on the slice rim, and the THROUGH hero digit. They are flat `HARM` #FF4433 stencil shapes with a 4.5 px `INK` keyline and no texture. This is the only family with saturated flat red. They obey the time grammar (C): hot this turn, cold for future turns. E10's best idea is kept: **solid chevron = hit, hollow chevron = growth still to come.** **2026-11-03 (art-pass, review 1.2 + 2.9):** a HOT solid chevron has a 2.8 px white-hot core (#FFEAE0) inside the HARM stroke, so HOT marks rank second only to SEND IT (A.1 order). **2026-11-04 (gate 1):** the core is 3.2 px. With the ring NOW glass lit (A.2), the HOT fill alone reads lower against its own cell than COLD does against its cell (`grammar_check.jpg`, luma contrast of the median fill vs the cell); HOT is carried by the fill, the white-hot core, the 4.5 px keyline and the notch together, and the core vs the cell is reported beside the fill ratio. See `locked/final/NOTES.md` "2026-11-04 gate 1" for the numbers. **2026-11-04 (round 2, review question 5, C11):** HOT is carried by its white-hot core, gated on the plate: the core (pixels within dE 14 of #FFEAE0) is 3 px or more wide at 1x and reads 4.5:1 or more against the ring-NOW occupied glass; the fill ratio is reported only. The cell chevron's core is drawn 4.2 px on a 7.2 px HARM_UP fill (the 3.2 px core measured 2.0 px solid at 1x), the landing-arc chevron's core 4.8 px on a fill 2.2 px wider than gram's (3.9 px measured 2.0-2.55 px per stroke). Measured per stroke on the plates: every cell chevron core is 3.0 px; the landing-arc cores are 3.5-4.0 px on the open arcs but 2.0-2.5 px on the small side-arc marks that the arc's own lane line crosses. That last case is open (`locked/final/NOTES.md`, "2026-11-04 round 2"). **2026-11-04 (round 2, measured; C11 is an art-pass call, open to the designer, answering R1_REREVIEW question 5):** on the board plates the core reads 3.0 px (pooled medial) at L* 94.0, core vs cell 4.92-5.01:1, fill vs cell 1.93-1.97:1 (reported). The under-minimum side-arc marks are 2.0-2.5 px, four per p1 / nowords plate and two per p2 / p3 plate (`final/checks.json` `i_hot_core.strokes_under_min`). On the hover plates C11 is reported only: where the ring-NOW cell is lit (h01, h05, h06, h08) the core is 3.0 px at 4.95-4.96:1; on h09 and h10 the dimmed chevrons read 2.5 px. **2026-11-03 (review 2.12):** a FAR landing mark carries its number in Anton 19: the hit count before the chevrons, and the HP-through count after the diamonds.

### A.4 K CLOCK

The bezel, needle, sector digits, schedule cells, ring tags, landing arcs and the wave queue. The material is machined gunmetal: fill #262B33 with L4 engraved grooves (1.4 px #0A0C10 with a 1 px #5C6472 highlight 1 px below, light from top-left). Ticks are engraved, not drawn. `SCHEDULE` #FF8C1A appears on schedule step cells only. The bezel's Solace teal enamel (R1 ruling 4) is withdrawn: the clock is neutral machinery, because a teal bezel would read as enemy. **2026-11-03 (art-pass, review 1.2 + 2.9):** the clock's plates (the THIS TURN cell, the HOLD plates and the +N plates) and the tape are one gunmetal, #6E7580, with engraved grooves and a #969EAA lip. Their median is L* 45-55, below the tower. `SCHEDULE` orange is on the live step only: its edge, its L5 chevrons and its glow. The silver tape remap is retired. Bezel words are Mono 23 (cap height 16.1 px). **2026-11-04 (gate 1):** K type (the stamped sector digits, the ring tags NOW W1 / +1 W2 / +2 W3, the W tags and kind glyphs on the tickets, the nowords tallies) is one ink, `K_TYPE` #CBD2DB at L* 84, with no glow. "Full value" on a ticket (stage 2) means this K type value: ticket glyph p90 L* 84 ± 4 is the gate. The ticket edges keep their time value (W6 50, W5 70, W4 100 %). **2026-11-04 (round 2, C3, C5):** the plate's and the bezel's 1 px ring and band lines, the bezel cube-glyph discs' glyph ink, the schedule layer's tape-end crescent and keylines and the ward arc keep nothing above K type (L* 84, hue kept), reduce from 2x with a box filter, and are capture classes of check b (K structure, K schedule lines, E ward arc). The landing-arc disc glyphs, turn dots, NOW dot, wear slash and twist mark are K type (they were white). The ticket edge steps are true on the plate (the skin hook had turned the value into a two-state flag) and measured (check g: each step 5 L* or more); the W6 hazard ticks sit in the ticket's top row between the W tag and the turn pips, clear of the bomb glyph's width pips.

### A.5 N PLAN

Hover path, trigger path, twist badge, plan underline, BEST LINE, option selection and the hovered-cell focus. The material is grease pencil: `PLAN` #FFE200, 7 px with a 3 px ink edge, a wax grain texture (8 percent noise) and **no glow**. When the player commits a plan (SEND IT, or a Trigger resolving mid-turn), pencil marks turn into P paint in the resolve beat (X effect FX-T).
- **2026-11-04 (art-pass, round 2; R1_REREVIEW C1, C2):** one pencil and one FOCUS drawer for the board and the hover set. `corp/src/rb_pencil.py` is the hover set's wax stroke (hv_core): 7 px `PLAN` wax, a 3 px ink edge each side, wax grain (8 % value noise that only darkens) with drag streaks and a ragged wax edge, round caps, no glow. It draws every board pencil mark: the p2 trigger path and its X caps (the same stroke), the p2b hover path and its open arrowhead, the consumed ghost outlines and the bill's plan underline. Pencil pixels reduce from 2x with a box filter, so the wax keeps its pigment and the ink edge does not ring. Gate (check f, on the plate): wax 6-8 px, ink edge 2.4-3.6 px per side, wax grain L* std 2 or more. `corp/src/rb_focus.py` draws `FOCUS` #D4FF00 as four separate 12 px corners only (2 px legal, 3.5 px aimed), never a joined bar or full outline, on the board p2b cell and in every focus_brackets call. The hover set is to import both instead of its own copies when it is re-rendered (hover stage, not done in this pass). (Done later in round 2: next line.)
- **2026-11-04 (art-pass, round 2, hover stage; C1, C2, C17; measured on the published plates).** The hover set draws with `rb_pencil` and `rb_focus`. Pencil on the plates: board p2 / p2b wax 6.0-6.1 px, whole stroke 12.8-13.0, ink 3.3-3.5 a side, wax grain L* std 4.27-4.45 (check f); the 18 hover plates with board pencil wax 6.0-6.5, stroke 12.66-13.0, ink 3.25-3.5, grain 3.82-4.65. The HUD pencil (10 hover plates) reads wax 6.0-7.0 and grain 4.19-4.82; its ink is 3.0-4.0 a side, over 3.6 on h01 and h10 nowords (reported). The wax reads about 1 px under the 7 px drawn because the blend pixels count as ink. FOCUS: four 12 px corners at #D4FF00, dE76 0.0 on all 26 hover plates and 276 px per board p2b plate at L* 94.1, with 0 px of the round-1 #96FE46. C17 (Twist hovers, h04 x4): the PLAN halo is the pencil outline on the cell of each unit whose landing the Twist changes, on the twisted ring, 2.5 px off the cell. Pencil px: ring NOW 1,893, ring +1 19,270, ring +2 12,362, bezel, frame band (r 480-500) and outside r 500 0; PLAN-coloured px at r 480-500 0 (round 1 had 8,921 there). Open: h08 (Hold) runs its PLAN arrow outside the rim from THIS TURN to NEXT, 13,029 pencil px at r 480-500 (6,261 PLAN-coloured); C17 covers Twist hovers only, so this is reported.
- **2026-11-04 (art-pass, gate 1; review 3.8):** BEST LINE and option selection leave this family. PLAN yellow means "what-if" only: the pencil marks, the hover and trigger paths, the twist badge (at 86 % value) and the WITHOUT TWIST what-if row. The BEST LINE chip is neutral: `TEXT_HI` type on the terminal plate with a `TEXT_MID` edge and a filled star. The best option chip and the selected option chip take a neutral `TEXT_HI` edge (3 px) and the star. So on one plate yellow never means both "what-if" and "best".

### A.6 X EFFECTS

Every event overlay (section G). The material is light and print: additive colour, halftone Ben-Day dots (6 px pitch, 45 deg screen), speed lines, starburst hit frames, krackle (black energy blobs) for enemy harm, and a 3 px misregistration only on impact frames. X is the only family that blooms. The colour is the cause colour (E).
- **2026-11-04 (art-pass, round 2 docs pass).** The effects as published are described in G, which replaces the family table and effect list that stood there. Two details of the paragraph above changed in the 2026-11-03 rebuild: the FX-H flood is X-only halftone (crossed marks, never round dots), and the FX-M print echoes are retired.
- **2026-11-04 (art-pass, round 2; C12, C13; art-pass calls, open to the designer).** C12: the resolve beat shows a "SKIP" key hint (Mono 23, cap height 16 px or more) at the HUD edge for the length of the beat. **Not published:** it exists only as a preview in the round-2 effects scratch tree, so the published beat still has no on-screen word. C13 (answering R1_REREVIEW question 6): the transition bits over the dark city are thinned until the worst 120 px tile flashes 2 or fewer times in any 1 s. A ring, spinner or ticket bit whose route runs d degrees round the rim from the lab is kept with probability p = near - (near - far) * clamp((d - 90) / 90): T5 near 100 % and far 50 %, T6 near 45 % and far 25 %; card bits are not thinned. Measured on the renders and on the decoded GIFs, both skins: worst tile 2 in any 1 s in T5 and T6, WCAG count 0, whole frame 0. T6 holds on the bare room (difference 0 to T4's last frame) because none of the seven pull-out variants tried kept every tile at 2; the hand-over from the room to the netrun street is not drawn (open). The bits keep the colour of their source: drawn vs plate hue dE76 median 0.00-0.42 per stream.

### A.7 S SYSTEM

The header, bill, objectives, RAM / Trace / Heat, UNDO, the hover tag and the bottom hint. They use the one terminal kit (`hud2.P()`): navy glass #050D1C at 93 percent, `NET_CYAN` edge 1.5 px, radius 8, scanlines at 4 percent. **Player-owned data on the HUD is taped on:** the YOU HP row is a strip of P paper (in the chosen style) taped onto the terminal, so player HP reads as the player's in both places (tower ring and HUD). **2026-11-03 (art-pass, review 1.5 / 3.11):** every HUD word is Share Tech Mono 23 (cap height 16.1 px) with 2 % tracking. Rows were re-spaced to fit. The objectives row wraps to its 2 x 2 grid when a single row would leave less than 22 px between challenges.
- **2026-11-03 stage 2 (art-pass, review 1.5, 3.7, 3.11):** every number in the bill is a digit: Anton 24 (22 on the NEXT row and the chain), followed by a small pip tally as a second mark. The minus, plus and equals signs are typeset in Anton 40 and centred on their ink. SPLIT is a written sum, ABSORBED + SOAK + YOU, with no route arrows or destination icons. The NEXT row sits at 70 % value: a COLD digit plus a filled COLD tally (45 % chroma, see C). WITHOUT TWIST shows its two numbers as digits ("2 → 1") in `COLD_CHEV`. The "00 → |" tally pair is retired. The nowords plate keeps full-size tallies and drawn operators, with no digits.
- **2026-11-03 stage 2 (review 3.5):** Heat is the atlas Heat glyph (`ATLAS_BURN`, 24 px, `CRT_AMBER` with an ink outline), never an emoji flame.
- **2026-11-03 stage 2 (review 3.6):** the REFUND word is on the HUD. It is a terminal tab hanging by a cyan hairline under the RAM coin it returns. The wheel keeps only the refund coin at the kill; the word never sits on the wheel.
- **2026-11-04 (art-pass, round 2; R1_REREVIEW question 3, C8):** one row grid for the board HUD and the hover HUD (`corp/src/hud_rows.py`), so no row moves when a hover starts. The bill always has the hover set's room round the hero digits (19 px above, 26 px below, 32 px digit gaps, 16 px in) and four NEXT row slots at a 30 px pitch: the NEXT row plus three option rows. Empty slots stay empty. On p2 the three plan options are rows in those slots (they were chips under the bill); a hover with options fills the same slots. Measured on the plates: the bill plate is y 76-427 (351 px) on p1, p2, p2b and nowords, which is the hover grid with its option rows. On p3 the resolve log takes the option-row space (bill 76-337, then the log); no hover starts in the resolve beat, and every row above is unchanged. The bill / WIN / RAM panel gap is 4 px (it was 8) and the REFUND tab is 96 px wide (it was 112), so the lifted card has its room (H, the lift).
- **2026-11-04 (art-pass, round 2, hover stage; C8 is an art-pass call, open to the designer, answering R1_REREVIEW question 3).** The hover HUD is the same `hud_rows` grid. Measured on all 26 hover plates: the bill plate is y 76-427 (351 px), the row record equals the board's, and the HUD bottom is 569 (607 on h03 with its REFUND tab, as on board p2). Rows on the board (check h): hero label y 90, hero digits 149, eq label 208, eq 232, split label 264, split 288, NEXT 320, WIN top 431, RAM top 519. h04's four option rows sit at y 307-423 in the reserved slots. On h03 the REFUND tab slides 33.2 px left to clear the lifted Trigger ([1171, 575, 1267, 607]; 0 px of any card in it, check k). The cost of C8: on p1, p2b and nowords the reserved rows are empty, about 90 px of empty bill at y 330-420.
- **2026-11-03 stage 2 (review 2.14):** the waves-left count shows once: the header chip `WAVES 6 LEFT`. The header pips are dropped on the words plates; nowords keeps the pips, because it has no number.

---

## B. Line grammar (the line budget)

There are ten line types. Each has **exactly one meaning**. A designer who wants a line that is not on this list brings it to the art director first.

| Id | Line | Spec at 1080p | The one meaning | Used by |
|---|---|---|---|---|
| L1 | **Ink keyline** | `INK` #0C0A16, coloured stroke + 4.5 px (2.25 each side) | "This mark sits on top." Separation only; it never carries meaning by itself | Every coloured mark on the board |
| L2 | **Painted stroke** | Tapered, 3-9 px variable width, 1.5 px wobble, texture of the chosen direction, `CELL_PINK` or `PAPER` | **Owned by the player** | Tower edges, slice frames, hub, gun tracers, Brace, soak, cards, stickers |
| L3 | **Vector hairline** | Constant width 1.5 px (Fine 2 px for containers), perfect geometry, `ENAMEL` #D9E1EA or `NET_CYAN` on HUD plates | **Machine-made structure** (enemy cells, tokens; HUD plate edges) | E family, S family |
| L4 | **Engraved groove** | 1.4 px dark groove + 1 px highlight below | **The clock's scale** | Bezel ticks, sector divisions on the bezel, ring gutters at the bezel |
| L5 | **Arrowed outline** (kept, designer note 4) | An outline channel 16 px wide, two 3 px edges, inner chevrons 10 px at a 24 px pitch pointing the way of travel, a 22 px arrowhead at the end | **Movement: this travels along here** | Hover path, Trigger path, schedule step (THIS TURN cell), Twist, Spin ghost, Shove, Pull, wave queue feed |
| L6 | **Grease pencil** | `PLAN` 7 px + 3 px ink, wax grain, no glow | **The player's plan or preview** | N family |
| L7 | **Cross-hatch** | Two hatch directions (45 deg and 135 deg), 2 px lines at a 5 px pitch, clipped to the shape, with a solid 2 px edge of the same colour | **Lost at the end of this turn** | HP, slice pips, a breaking slice, a dying unit's cell |
| L8 | **Dotted** | Round dots 4 px at a 9 px pitch | **Two or more turns away** | +2 trims, +2 landing arcs, +2 token rings. **R51 review: marks only.** Structural outlines (ring rims, +2 cell outlines, ticket edges, the board rim) are never dotted; FAR structure is a solid hairline at 50 percent value |
| L9 | **Glow** | Additive bloom 4-6 px at 35 percent or less | **Live: happens at this END TURN** (and X effects while they play) | Hot threat marks, the live schedule cell, X overlays |
| L10 | **Double line** | Two solid strokes with a 3 px gap (P version painted, E version vector) | **Protection: this stops or reduces a hit** | Brace clamp, SHIELD block plate, enemy armor cap, enemy shield bracket, the ward |
| (banned) | **Dashed** | none | **No meaning.** It is not used anywhere on the combat screen | E10's dashed uses map as listed below |

**2026-11-04 (art-pass, round 2 docs pass; what the published plates show).**
- **L6 is one stroke (C1).** One drawer, `corp/src/rb_pencil.py`, for every board and hover pencil mark, the X caps included; long hover marks keep the full width. Measured: wax 6.0-6.5 px, whole stroke 12.66-13.0 px, ink 3.25-3.5 px a side, grain L* std 3.82-4.65 (A.5). The gate is wax 6-8 px, ink 2.4-3.6 px a side, grain 2 or more.
- **L8 dotted is not drawn anywhere.** On every published board and hover plate the dash audit reads 0 dash calls, 0 dotted-mark calls and 0 pixel dot runs. FAR (+2) marks are drawn solid: the tower's FAR threat trim is one tapered stroke with two turn pips (O-29 fix 3, `locked/final/NOTES.md`), FAR landing marks carry their Anton 19 numbers, and FAR structure is the solid hairline at 50 % value. So the L8 row above and the "L8 dotted" FAR contour in C describe a line the plates do not use. Read FAR as: no fill, 50 % value, 25 % chroma, thin solid contour, two turn pips. This plan does not remove L8; that is for the designer.

**Where every E10 dashed line goes** (designer note 2: dashes were used for HP, outlines, movement and more):

| E10 dashed use | New line |
|---|---|
| +2 lane outline (white dash) | Solid `ENAMEL` hairline at 50 percent value (R51 review: was L8 dotted) |
| Next-turn / later threat trim (blue / white dash) | Threat trim in the time grammar: +1 cold solid, +2 L8 dotted |
| Hollow growth chevrons | Unchanged: hollow outline with no dash |
| Gun tracers (cyan dash) | L2 painted stroke in `CELL_PINK` (the player's gun) |
| Idle-gun stub | A short L2 stroke ending in an open painted ring |
| Ghosts (spin ghost, hover ghost) | 40 percent opacity copy plus an L5 arrowed outline for the motion |
| Gone socket (slice pip, HP) | Dark socket with a solid 1.4 px hairline |
| Mend preview (white 3/3 dash) | GAIN outline segment with a plus (D) |
| Played-card empty slot | Torn-paper outline (P), no dash. **2026-11-03 stage 2 (review 2.3):** the slot is flat and upright (no fan angle, no perspective cage). It is a torn dark paper liner (#15121A at 86 %) with a paper rim and a fibre edge, the card's ghost glyph at 46 % paper value, and the card name over PLAYED in Mono 21 |
| Hover path | L5 arrowed outline in pencil (kept) |
| Landing lane (white dashed to the bezel) | Removed. The landing arc already carries the read |

**What the arrowed outline is.** We read the designer's "arrowed outline" as the p2b hover path (a yellow outlined channel that follows the unit's route and ends in an arrowhead) and its sibling, the chevron-filled schedule cell (+2 THIS TURN). Both are kept and given the one meaning *movement*. This reading needs the designer's confirmation in the finalist report.

**Stroke tiers keep their job** (BRIEF 3.5): Hairline 1.2-1.6 px is engraving and segment edges. Fine 2-2.6 px is containers. Medium 3-4 px is identity borders. Bold 5.5-8 px is action and threat. A container never uses Bold, and a threat mark never uses Hairline.

---

## C. Time grammar (designer note 2)

What resolves at **this END TURN** must look different from **any future turn**, at a glance and in greyscale.

| When | Name | Fill | Value / chroma | Contour | Glow | Turn mark |
|---|---|---|---|---|---|---|
| **This END TURN** | **HOT** | Solid fill | 100 percent value, full chroma | Solid, Bold tier | L9 yes | **END notch:** a solid 8x8 px wedge notch on the mark's tower-facing end. The live schedule cell carries the word THIS TURN |
| **Turn +1** | **COLD** | Hollow (outline only) or 35 percent fill | 70 percent value, 45 percent chroma | Solid, one tier thinner | No | **One** turn pip (6 px round, `TEXT_MID` #AFC0D6) |
| **Turn +2 and later** | **FAR** | No fill | 50 percent value, 25 percent chroma | L8 dotted | No | **Two** turn pips |

Rules:
- **Board rings take the grammar.** Ring NOW is HOT: its unit cells are full-value glass, their threat chevrons glow, and their landing arcs are solid with the END notch. Ring +1 is COLD. Ring +2 is FAR. Depth is now read four ways without colour: position, value, contour (solid / thin / dotted) and the ring tag (NOW / +1 / +2). This replaces the red / blue / white lane outlines.
- **One HOT mass per family:** T has the NOW chevrons and diamonds; K has the live schedule cell; P has the pending HP hatch. Nothing in the future is ever HOT.
- **Turn pips** replace E10's white turns-until dots on the landing arcs. They sit at the arc's start cap, never on the arc line.
- **HUD:** the bill's main rows are HOT (this END TURN). The NEXT row is COLD: 70 percent value, no glow, and one turn pip before its label.
- **Resolve (p3)** shows what happened, so HOT marks lose their glow once the beat has played: it was now, and now it is done.
- **R51 review: the future recedes as a block.** Ring +1 cell glass at 80 percent value, ring +2 at 62 percent (option C's frost without the blur). COLD harm is a lifted solid #D9877C, not a darkened HARM (cold chevrons read brown).
- **Hollow is growth only on chevrons.** On a chevron, hollow means growth still to come (A.3). On every other mark, a +1 future thing is COLD (desaturated), not hollow, so the two readings never meet on one shape.

---

## D. HP grammar (designer note 3)

One grammar for every HP display: player HP ring, YOU tally, slice pips, unit HP, Adjuster HP, and arc wear. The segment is a rounded rectangle r3. **The white slash is retired.**

| State | Look | Meaning |
|---|---|---|
| **Current (lit)** | Solid fill: player `GAIN` #7BE07B as painted blocks (P style); enemy `CREAM` #FFF4D6 as clean vector ticks (on the board `CREAM_HP` #DBD1B7, L* 84, since 2026-11-04); boss `BOSS_GOLD` | HP you have now |
| **Lost at this END TURN, harm** | Socket dark, **L7 cross-hatch in `HARM`**, solid 2 px HARM edge, L9 glow 4 px | The enemy takes it when you press SEND IT |
| **Lost at this END TURN, soak** | L7 cross-hatch in `SOAK` #3A7EF3 + a 5 px chevron notch cut into the outer edge | Your soak choice spends it |
| **Lost at this END TURN, by us** (enemy HP) | L7 cross-hatch in `CELL_PINK` | Our guns, Strike, Trigger or Firewall take it |
| **Lost in a future turn** (NEXT row, +1 forecast) | COLD: ~~hollow 1.5 px outline~~ **filled tally in the cause colour at 70 percent value and 45 percent chroma** (2026-11-03 stage 2: hollow tallies read as zeros at 1x, and C reserves hollow for growth chevrons), one turn pip before the run | A forecast, not this turn |
| **Mend pending** (REPAIR) | Empty socket, 2 px `GAIN` outline, a centred 7 px plus, a small upward tick above | It comes back at END TURN |
| **Gone** (lost earlier) | Dark socket #0E1016, solid 1.4 px hairline #3A4150 | Already gone; nothing changes |
| **Blocked** (absorbed by SHIELD or Brace) | The segment stays lit. An L10 double-line plate (P, paint) sits in front of the incoming chevrons at the slice rim. Count is shown by the plate's tally ticks | It would have been lost, but your protection takes it |
| **Enemy shield layer** (Jammer) | Separate hollow hex pips (vector, `ENAMEL`) in front of the HP ticks, inside an L10 double-line bracket | Shield empties before HP |
| **Armor** | L10 double-line steel cap (`STEEL` #96A2B6, highlight `STEEL_HI` #E2E9F6) along the cell's outer edge | Each incoming hit is 1 less |

**The cause-colour rule:** cross-hatch always means "goes at this END TURN". The hatch colour says who takes it: red is the enemy, indigo is your soak, pink is you. In the nowords plate the hatch alone still reads as "going".

Sizes:
- **Player HP ring (R51 review: moved to the hub):** 15 segments **wrapping the hub at r 52-64**, in 3 groups of 5 with a 9 deg group gap and a 2.5 deg segment gap. It no longer sits on the rim, where red pending hatch merged with the red threat trim. The pending run starts at the needle and runs clockwise; no sector meaning is implied.
- **Thin-segment hatch (R51 review):** on any segment under 9 px, L7 is a single-direction 45 deg hatch, 1.6 px lines at a 4 px pitch, and the pending segment is 2 px thicker than lit ones (bulges outward). Two-direction hatch only on segments 12 px or more. If the hatch collapses to solid at 320 px, widen the pitch; never drop it.
- **YOU tally:** the same 15 segments, 22x14 px, in groups of 5, on the taped P strip. **2026-11-03 stage 2 (review 3.14):** the segments are 13.6 px wide and 22 px tall at a 16.4 px pitch, with an 8 px group gap. The pending hatch is two-direction at a 5.4 px pitch with 1.5 px lines, inside a 1.4 px HARM edge, so the hatch reads at 1x.
- **Slice pips:** 2 per slice, 30 deg capsules 8 px thick at r 128-136.
- **Unit HP:** ticks 6 px wide, 10 px tall, 3 px gap, sector gap 8 px, along the cell's outer edge. These are ticks, not long dashes, so they cannot read as a dashed border.

---

## E. Colour meanings (designer note 5)

Twelve meanings, and since 2026-11-04 round 2 a thirteenth, `P_STOCK` (C15, a P material). Every other outline or fill is neutral.

| Token | Hex | The one meaning | Shape it always pairs with |
|---|---|---|---|
| `CELL_PINK` | #FF3DA8 | **Ours:** the player's tower, cards, guns, damage we deal | Painted stroke (L2) |
| `HARM` | #FF4433 | **Damage to you** (from the enemy) | Chevron, diamond, red hatch |
| `GAIN` | #7BE07B | **Your life:** HP and slice pips you keep or regain; a landing that costs nothing | HP segment, check, plus |
| `SOAK` | #3A7EF3 (R51 review: #464EFF failed protan vs Trace, dE 2.4) | **Your soak choice** | Chevron notch, funnel |
| `PLAN` | #FFE200 | **Your plan / preview** | Grease pencil (L6) |
| `SCHEDULE` | #FF8C1A | **The rings move:** schedule steps | Bezel step cell, L5 chevrons |
| `BOSS_GOLD` | #D69A1A (2026-11-03: #FFC428 failed the palette check, dE76 11.4 vs `CRT_AMBER` and 11.3 vs `RESIST_GOLD`; the new pick is 17.3 or more from every token) | **The Adjuster** and its ward | Diamond body, gold lozenge |
| `NET_CYAN` | #5CE1FF | **The terminal and RAM** | HUD plate edge, RAM coin |
| `TRACE_VIOLET` | #A03CFF | **Trace** | Square r3 |
| `CRT_AMBER` | #FFB000 | **Heat** | Flame |
| `RESIST_GOLD` | #FFD24D | **Stars** | Star |
| `FOCUS` (`cell_acid`) | #D4FF00 | **Keyboard / target focus** | Four corner brackets only |
| `P_STOCK` | #F6C8DE | **The player's print stock** (2026-11-04 round 2, review 3.10 / C15): the pink paper plate under the FX-P effects; a P material, never a mark | Paper plate under a P effect |

**Neutral** (no meaning): `ENAMEL` #D9E1EA (enemy outlines), gunmetal #262B33 / #5C6472 (clock; plates and tape #6E7580 since 2026-11-03), `INK` #0C0A16, `PAPER` #F2EEE4, `TEXT_HI` / `TEXT_MID` / `TEXT_LO` #F2F6FF / #AFC0D6 / #7A889C, `STEEL` (armor, pairs with the double line), `CREAM` (enemy HP, pairs with the tick).

**2026-11-04 (art-pass, gate 1) additions and re-picks** (check d: every token, slice ink, card type colour and skin ink vs every meaning token and the light neutrals PAPER / ENAMEL / TEXT_HI / TEXT_MID, dE76 ≥ 15):
- `CREAM_HP` #DBD1B7 (L* 84): enemy HP ticks on the board. `K_TYPE` #CBD2DB (L* 84): K type (A.4). `HIT_PAPER` #DED8CA (L* 86): the gun hit star fill and the tracer highlight. All three are neutral values of existing hues, so no new meaning.
- TURRET slice ink #D6A33A → olive #AEB24E (texture #5A5E1A). The old ink sat at dE76 9.6 from `BOSS_GOLD`, in the sector of the Adjuster it shoots. DR-4 (own colour per slice type) and DR-5 (no reserved colours for fills) still hold: this is a re-pick for distance, not a ban.
- Solace porcelain (skin ink on the bezel lip, rim, crest roundel, token frames and ticket edges) #E6EFE4 → celadon #B8DCCC. The old one was dE 4.7 from `PAPER` (the player's paper) and 11.2 from `ENAMEL`.

**2026-11-04 (art-pass, round 2; R1_REREVIEW C15, C16, C2):**
- `P_STOCK` #F6C8DE is a meaning token (table above; `rb_tokens.TOKENS`), so check d tests it against every token, slice ink, card type colour and skin ink.
- Solace leaves leaf green (review N2: the rope #96FF46 / #4FA83A sat at dE 20.4 from the hub HP ring green). Its rope, cell edges, bezel lip, crest strands, token frame dot and ticket edges are the celadon / teal family of the glaze: teal #4FA6A2, deep teal #2E7F7E, teal highlight #6FC2BC, glaze #B8DCCC (LCh hue 190-195). Green on the board is `GAIN` and the player's HP ring only. Gate (check d): the rim as drawn (r 491-498 on the plate) is dE76 25 or more from `GAIN` and from the hub HP ring green (#7BD37B as the reviewer measured it).
- Drawn colours (check d, C2): the colour a mark is drawn in, measured on the plate, sits within dE76 3 of its token (FOCUS, the pencil wax, the HOT fill, the gun tracers, the Adjuster track), and every drawn mark colour is dE76 15 or more from the skin's corp hue inks. The skin's own ink on the rim, lip, crest, cell edges, token frames and ticket edges is the skin, not a mark.
- **Measured on the published board plates (round 2):** check d passes on all 15, 196-273 pairs per plate, 0 failures, lowest pair 17.3, with `P_STOCK` in the set. Drawn: FOCUS #D4FF00 at dE76 0.0, pencil wax #FEE100 at 0.5, HOT fill #FF6452 / #FF6956 at 0.0 / 2.4, gun tracers #FF3EA9 at 0.4, Adjuster track #D69A1A at 0.0. The closest drawn mark to a corp ink is 22.3 (Meridian). Solace rim as drawn: median #3B827F, 61.3 from `GAIN` and 53.4 from the hub HP green (51.0 / 44.1 by modal colour). Hover (26 plates): two plate pairs fail the drawn-colour test. On h03 x2 the gun tracer's modal colour is #FF40B0, dE76 3.8 from `CELL_PINK` over 1725 px (median #F941A6, 2.9). On h11 x2 the HOT fill inside the lit area is dimmed to #662C27, 54.7 from `HARM_UP` over 770 px. Both are open.

**What each E10 outline colour meant, and what happens to it** (this is the answer to note 5):

| E10 outline | Meant | Now |
|---|---|---|
| Red lane outline (ring NOW) | Lands this turn | Neutral `ENAMEL`. "This turn" is HOT (C) |
| Pale blue lane outline (+1) | Lands next turn | Neutral, COLD |
| White dashed lane outline (+2) | Lands in 2 turns | Neutral, L8 dotted, FAR |
| Slice frame green / pink / teal / lime | Slice type | All slices get the same P painted frame. The type is the icon only |
| Cyan code-base rings | "Ours" | Removed. P paint says "ours" |
| Cyan hub rim | Ours | The P painted rim |
| Dim orange empty-cell edge | Nothing (render artefact) | Removed |
| Pink unit-screen corners | Nothing (texture frame) | Removed |
| Gold Adjuster edge | Boss | Kept (gold = boss) |
| Orange bezel rim glows | Nothing | Removed. Orange is schedule steps only |
| Yellow hovered-cell outline | Plan focus | `FOCUS` corner brackets (R2 ruling Y12) plus the pencil path |

**R51 review: motion colour.** In hover every motion mark is the plan (`PLAN` pencil L6 + L5). In resolve it takes its owner's colour: `CELL_PINK` for anything a card does (Spin, Nudge, Twist, Pull, Shove), `SCHEDULE` only for the clock (rings step at END TURN, Hold's slide). Yellow never appears in resolve.

**Contrast checks the colour designer must run:** `CELL_PINK` vs `HARM` in deutan, protan and tritan (dE ≥ 12; if it fails, `CELL_PINK` moves toward #FF4FD0, never HARM). `GAIN` vs `FOCUS`. `SOAK` vs `TRACE_VIOLET` (R2 ruling Y1 numbers hold). Shape pairing is mandatory, so no meaning depends on hue alone (GDD 9.6).

---

## F. Wave info (designer note 6)

**Now:** W4 / W5 / W6 take three full concentric arcs outside the bezel (r 470-510, about 22 percent of the board's area). Each has unit pips at true sector angles, W tags and hazard ticks.

**The rules allow a compression:** a wave's sectors only exist once it enters ring +2 (rules E7, fixed lineup). Before that, only the kinds and widths are known. The angles are not information, so the arcs can go.

**New layout: the wave queue.**
- One **queue strip** of three tickets in the free top-left corner, x 24-252, y 24-112. It is K material (gunmetal ticket, L4 engraved edge).
- Each ticket is 72x56 px with a Share Tech Mono tag (W4 / W5 / W6, 16 px). It shows the units as kind glyphs at 20 px; each unit's width is shown as 1-3 short bars under its glyph (Packet 2 = two bars).
- Tickets go FAR → nearer, left to right: W6 (left, FAR dotted edge), W5, W4 (right, COLD solid edge, next to enter).
- **W6 climax:** a cut corner plus three `SCHEDULE` hazard ticks on the ticket edge.
- **Feed:** one short L5 arrowed outline (neutral `ENAMEL`, 12 px channel) runs from the W4 ticket to the bezel at ring +2's entry point. It says "W4 enters here next".
- **WAVES 6 LEFT** in the header becomes the queue's own count (header keeps the number, the queue keeps the pips; content guard: the word and the 6 stay). (2026-11-03 stage 2: the count shows once. The header chip carries it on the words plates; the pips are on nowords only.)
- **Freed space** (r 470-510): the landing arcs move out to r 436-470 so they no longer stack against the bezel (do-not 5: no more than two parallel arcs within 12 px). The board keeps its 24 px screen margin.
- **2026-11-03 stage 2 (review 2.14; tickets stay per DR-1):** tickets are 84x70 px. The W tag (Mono 23), the kind glyphs (27 px box, 23-27 px of ink, p90 L* 97-99 measured on every plate) and the width bars are all at full value. Time is on the ticket edge (W6 50, W5 70, W4 100 percent value) and the turn pips only. The count shows once, in the header chip (A.7).
- **R51 review:** tickets are 84x64 px (glyphs 24 px) with **solid** edges; time is by value (W6 50, W5 70, W4 100 percent) and pips. The freed band is spent on the player: the tower grows to **r 196** (threat trim r 200-210), rings NOW / +1 / +2 re-space into r 214-430. If a unit glyph drops under 44 px or a cell under 30 px deep, cap the tower at r 184. The card hand grows 1.15x.

---

## G. Effect overlays (designer note 7)

**Rewritten 2026-11-04 (art-pass, round 2 docs pass)** to describe the effects as they are published in `locked/effects/`: the 2026-11-03 rebuild, rendered on 2026-11-04 between 03:38 and 04:45. The plan this replaces (wedge-wide plates, three print echoes, white block sparks, an orange Twist sweep, lengths in frames) is in git at b26022f5 and earlier. Sources: `locked/effects/timings_MPST.json`, `timings_CDHL.json`, `NOTES_MPST.md`, `NOTES_CDHL.md` and `locked/port/fx_timings.json`. Their numbers are measured on the 60 fps frames that the published keyframes are cut from, as those notes state. Every row here is an art-pass call, not a designer ruling, except where a DR is named.

**Round-2 status.** The effects set was **not** re-rendered on the round-2 board. Its bases are the gate-1 board: the pencil before C1, the HUD rows before C8, the ticket edges before C5 and the leaf-green Solace rim before C16. On Solace, `fx_wave_enter`'s scan line is #96FF46. The set reads P stock from its own `fxk_lib` (#F6C8DE, the same value as the `P_STOCK` token, C15). The block-vs-break comparison copy on `fx_block_vs_break.png` throws white sparks, while the real P block throws P-stock sparks. The C12 skip hint is not in the published beat. Open: the re-render on the round-2 board, the comparison copy's sparks and the C12 hint.

**What holds for every effect**
- **Footprint.** One overlay per event, on a slice (the wedge or its trim band), a cell, an arc, a ring, or a path from the rim to the HUD. No slab and no flat wedge tint: both were retired in the rebuild.
- **Length.** Every effect is 600 ms or less (`CAP_MS` / `T2_CAP_MS` 600, no per-effect override; both registries assert it). Lengths and keyframes are given in ms.
- **Layer (review 1.6).** First the board layer (room, scrim, board, tower, units, arcs, guns, tags, digits). Then the effect. Then the HUD, YOU strip, hand, UNDO, nameplate and SEND IT. Three effects draw over the HUD, all allowed: `fx_hp_through` (up to 6580 px on the HUD), `fx_refund` (1091) and `fx_trace_add` (1696). Every other effect changes 0 HUD or hand px.
- **Flash (GDD 9.6).** In full motion every effect is at 2 flashes per second or less (`fx_slice_crack` and `fx_trace_add` 2, the rest 0-1); in reduce motion 1 or less. The limit is 3. Each effect has a reduce-motion form: no travel, no sparks, no glitch; the marks appear, hold and dissolve. Each strip ends in a yellow-framed reduce-motion tile.
- **Loudness (review 2.10).** On the shared gated meter (`fxk_lib.loud_frame`) the order is damage > kill > block > state on all three skins. Neutral values: damage 2817 (`fx_hit_land`) to 9540 (`fx_firewall_burn`); kill 1813; block 841 (`fx_soak_take`) to 1677 (`fx_brace_block`); state 85 (`fx_clear`) to 761 (`fx_hold`). The thinnest margin is block over state: 80 (73 on Solace).
- **Colour by cause and owner (E).** `CELL_PINK` for anything the player or a card does; `HARM` for what the enemy does to you; `SCHEDULE` for the clock; `GAIN` only on the L family; the skin's own enamel ink for corp state; `BOSS_GOLD` for the ward. Measured on every 60 fps frame of the C, D, H and L effects: 0 `GAIN` px outside the L family, and 0 `FOCUS` or lime px. No M, P, S or T effect draws a kill mark. In the resolve beat both kills have 0 `GAIN`, `FOCUS` or lime px. Yellow is in the resolve only as the commit's pencil marks while they burn into pink.

**The families, as drawn**

| FX family | Material on the plates | Colour |
|---|---|---|
| **FX-P Protect** (your defence holds) | P stock, never the card bone `PAPER` (review 3.10). The shield block is a small plate on the slice's trim band (r 186-204, 26 deg) that slams 1.2 to 1.0 with its tally ticks; the incoming chevrons stop dead at its edge and throw P-stock sparks. Brace is four clamp brackets on the wedge corners, a bar the chevrons crumple on, and a 16 px stamp on the arc glyph. Soak is the funnel and the pip fill. No wedge tint, no soak wash | `P_STOCK` #F6C8DE (shade #D696B8); `SOAK` on the funnel |
| **FX-H Harm** (the enemy hurts you) | Misregistered red print: an X-only halftone flood (crossed marks, never round dots), black krackle with a 2 px red offset, a red stencil X. A broken shield is the P-stock plate in shards | `HARM` + `INK` |
| **FX-D Damage** (we hurt them) | The player's comic hit frame: a painted pink tracer (a tapered ribbon with an ink key), an ink-keylined starburst with a white core, converging white speed lines cut at the tower rim (r 199), flat vector shards. A kill is in the cause colour, with a pink-tint core and no word | `CELL_PINK` (kill marks L* 59.4) + white |
| **FX-L Life** (gain) | The one soft glow: brush strokes, plus signs, a painted check, four-point sparkles. Ranked with the state changes | `GAIN` on dark; mint (214, 255, 206) with an ink key on the green REPAIR wedge; `NET_CYAN` for the RAM coin |
| **FX-M Motion** (things move) | No echoes and no smear: the print echoes were the loudest light of every motion effect, and are retired. One solid arrow: a 3 px core, a 2.5 px ink casing and an 11 px open head. On spin, twist, shove, rings step and Hold it is a stub (60 / 30 / 30 / 32 / 22 deg) that runs ahead of the mover and is eaten when the mover arrives; pull and the bump keep a short whole arrow. The mover turns or slides, overshoots a little and settles back | By owner: `CELL_PINK` for the cards (spin, twist, pull, shove, bump); `SCHEDULE` for the clock (rings step, Hold's slide), with the Hold stamp in the clock's gunmetal; neutral `ENAMEL` for the wave feed. The corp hue is only `fx_wave_enter`'s scan line that draws the new cell edges (DR-6) |
| **FX-C Corp** (the enemy changes state) | One 1.6 px vector scan line with a 1 px ink key, then one flat 4-frame flash on the new mark only. No slab, texture or trail | The skin's enamel ink: `ENAMEL` #D9E1EA (neutral), celadon #B8DCCC (Solace), rust #D88A4E (Meridian); `BOSS_GOLD` for the ward |
| **FX-S System** (Trace) | One glitch band per 33 ms step, 4-7 px tall, over the card and then the Trace row, while the next Trace pip lights | `TRACE_VIOLET` |
| **FX-T Commit** (SEND IT) | A burn front runs the pencil marks from yellow to pink paint, with a white-hot edge of 1.8 % of the route at 60 %. A ping at the route end, then the board, HUD and hand step from preview to resolve | `PLAN` to `CELL_PINK` |

**Every published effect** (32 ids; total ms; the main phases in ms; "latent" means no source in the E10 state, drawn on real units with stand-in marks)

| Id | Event (state source) | FX | Footprint | What it draws | ms |
|---|---|---|---|---|---|
| `fx_shield_block` | SHIELD slice absorbs a landing (f1: absorbed 6) | P | Trim band | Chevrons arrive (0-160); the P-stock plate slams 1.2 to 1.0 (110-170); impact, stop dead, P-stock sparks (160-280); hold; the plate lifts off (440-600) | 600 |
| `fx_brace_block` | Brace blocks a whole landing (f2: TURRET, braced_hit) | P | Slice and arc | The lane draws in; four clamp brackets close 1.12 to 1.0 (60-180); the chevrons run the lane and crumple on the bar (80-330); the stamp slams 1.2 to 1.0 on the arc glyph (330-400); all lift off, the printed glyph stays | 600 |
| `fx_soak_take` | A soaked slice takes the overflow (f2: SHIELD sector 1, soaked 1) | P | Slice | The overflow chevron arrives; the funnel draws in (80-220); the chevron shrinks into its mouth; the pip fills (300-420) | 600 |
| `fx_shield_break` | Our SHIELD slice breaks while blocking (f1: sector 1 hp_after 0) | H | Slice | The plate cracks (20-90) and splits into P-stock shards (100-460); red flood, krackle; the wedge darkens (160-420); the pips go | 600 |
| `fx_hit_land` | Landing hit, one pip lost (f1 log "hit") | H | Slice | Chevrons in (0-80), a frame flash, the X-halftone flood (80-200), krackle (100-440); the pip goes dark at 200 | 600 |
| `fx_hit_land_worm` | Worm wear (variant) | H | Slice | As `fx_hit_land`, plus a hook mark | 600 |
| `fx_hit_land_adjuster` | Adjuster strike (variant; latent) | H | Slice | As `fx_hit_land`, plus a gold rim flash | 600 |
| `fx_slice_crack` | Slice goes 2 to 1 | H | Slice | Flood pulse, a jagged crack across the glass off the icon (50-220), a tip spark, krackle | 500 |
| `fx_slice_break` | Slice goes to 0 (ability lost) | H | Slice | Flood, frame flash, a red stencil X stamped in the outer corner, never on the icon (100-170), black-out (130-400), a halftone fade over the icon | 600 |
| `fx_hp_through` | HP gets through (diamonds to YOU) | H | Rim to the YOU strip, over the HUD | The diamonds lift off at 44 deg, before the arc's "3" (0-140), fly (60-460) and slap onto the YOU strip (400-520); the hatched segments go dark | 600 |
| `fx_gun_hit` | Gun shot hits (f1 guns: hit) | D | Cell | The pink tracer paints (0-80); the hit frame opens: starburst R 44 (80-140), 14 converging speed lines, shards; the HP tick goes gone (140-230) | 600 |
| `fx_strike` | Strike card hits for 2 (latent) | D | Cell | A painted slash (0-90), starburst, speed lines, shards; two ticks go | 600 |
| `fx_trigger_hit` | Trigger hits units along its path (f2 tlog trig_unit) | D | Cells on the path | The route ignites from pencil to pink paint (0-240); a burst at s3 at 120 ms and at s4 at 240 ms | 600 |
| `fx_firewall_burn` | Firewall burns a sector (latent) | D | Sector column | Pink flame bands ring by ring (0-160, 60-220, 120-280), cut clear of the tokens and the wave tags' dots; the ticks; embers (380-600) | 600 |
| `fx_kill` | A unit dies (f1: Worm 2 shot dead; f2: Packet 1 Trigger-killed) | D | Cell | A flare on the token (17-50), the KO starburst, speed lines, vector shards; the cell empties (160-380). No word | 600 |
| `fx_ricochet` | Shot glances off armour (latent) | D | Cell | Tracer, a steel glint and sparks off the L10 cap | 500 |
| `fx_ricochet_gold` | Shot weakened by the ward (f2: BURST 4 to Packet 6, ward x2) | D | Cell | Tracer and a gold streak off the lozenge; no starburst. In E10 the warded shots deal 0, so no HP changes | 500 |
| `fx_repair_mend` | REPAIR mends 1 pip (latent) | L | Slice | Brush strokes rise (0-450), plus signs, the pip fills (260-400) | 600 |
| `fx_refund` | Trigger-kill refund, +1 RAM (f2) | L | Cell to the RAM row, over the HUD | The coin pops 14 px off the board's own refund coin with one thin cyan ping (0-90), flies to the RAM row (90-400), and the slot and the REFUND tab light | 600 |
| `fx_clear` | Nothing gets through (arc check) | L | Arc | A painted check at r 443, 78 deg, clear of the arc's diamonds and its "3"; glow and sparkles | 400 |
| `fx_spin` | Spin 3 turns the tower | M | Whole tower | A pink arrow stub runs ahead and the gun preview fades (0-100); the tower turns 183 deg (100-500) and settles back 3 | 600 |
| `fx_twist` | Twist turns ring +1 one sector (f2: [1, 1]) | M | Ring +1 | Pink arrow stubs draw (0-90); the ring turns 61.5 deg (90-430) and settles back 1.5 | 540 |
| `fx_pull` | Pull drags a unit inward | M | Two cells | A short pink arrow; the cell slides 59 px (90-400) and settles back 2 | 500 |
| `fx_shove` | Shove slides a unit one sector | M | Two cells | A pink arrow stub; the cell slides 62 deg (90-400) and settles back 2 | 500 |
| `fx_shove_bump` | Shove collision (variant) | M | Both cells | Arrow; the cell slides toward the shared edge; a bump line, two small pink starbursts and shards (200-320); it springs back. No HP change is drawn (RULES, open) | 480 |
| `fx_rings_step` | The rings step in at END TURN | M | All rings | A `SCHEDULE` tape arrow stub (0-100); every ring spirals in, -57 px and +120 deg (100-480) | 600 |
| `fx_hold` | Hold puts a 0 in the schedule | M | Bezel | The gunmetal hourglass stamp slams (0-100) and hands over to the printed HOLD glyph; the band turns over while a `SCHEDULE` stub runs the slot (100-420) | 560 |
| `fx_wave_enter` | The next wave enters ring +2 | M | Ring +2 and the queue | The feed arrow lights and the W4 ticket lifts (0-80) and rides into the entry (80-360); the cells scan in and the glyphs drop (300-480); the queue moves up one slot (360-540) | 600 |
| `fx_grow` | A unit grows +1 hit | C | Cell | The enamel scan line (0-133), then a flash on the new hollow chevron (133-200) | 400 |
| `fx_ward_on` | Ward applies to the units in the Adjuster's sector | C | Cell | A gold scan line (0-133), a flash on the lozenge, one thin ping | 400 |
| `fx_trace_add` | A loud card adds Trace (Trigger +1) | S | Card and the Trace row, over the HUD | The card glitches in 5 steps (0-166); the next pip pops in 3 steps while the row glitches (166-266) | 400 |
| `fx_commit` | SEND IT, or a Trigger resolving now | T | Plan marks, then the whole frame | SEND IT press (0-60); the burn front runs the marks (60-400); a ping at the route end (400-520); preview to resolve (400-600) | 600 |

The C/D/H/L designer also keeps a 500 ms `fx_shield_block` copy, used only on `fx_block_vs_break.png` (see Round-2 status). **Pruned (R51 review):** `fx_worm_wear` and `fx_adjuster_strike` are the `fx_hit_land` variants; `fx_armor_bounce` and `fx_ward_bounce` are `fx_ricochet` and `fx_ricochet_gold`. **Parked (latent):** `fx_jam`, `fx_shield_pop`, `fx_boss_phase` and `fx_lockdown`, which are not drawn.

**The resolve beat** (E10 p3; review 2.11; `timings_MPST.json` `resolve_beat_e10`, `resolve_beat_strip.jpg`, `resolve_beat.gif`)
- **Length.** 3800 ms against a 4000 ms limit. 17 tracks overlap, each its designer's own effect at its own timing, in the HUD chain order: commit 0-600, twist 420-960, trace_add 600-1000, trigger_hit 760-1360, kill (Packet 1) 1000-1600, refund 1100-1700, gun_hit 1300-1900, gun_hit on the Adjuster 1360-1960, ricochet_gold 1420-1920, kill (Worm 2) 1560-2160, shield_block and brace_block 1900-2500, soak_take 1930-2530 (under the shield plate), clear 2400-2800, the board settle 2640-2840, rings_step 2800-3400, wave_enter 3200-3800.
- **Skip.** Any input dissolves the frame to the settled frame in 200 ms (easeInOutCubic). The published beat has no on-screen word. C12 (a "SKIP" key hint at the HUD edge) is not published.
- **Flash over the whole beat** (neutral): whole frame 0, track boxes 1, 240 px tiles 2, 120 px tiles 2. One 60 px tile holds 3 in one second: the kill and gun-hit cluster on Worm 2, at the limit. Reduce motion: 2 at most.
- **Kills.** Both kills are `CELL_PINK`, with 0 `GAIN`, `FOCUS` or lime px.
- **NOT TO SHIP (RULES).** The beat draws ring +1 one sector back from SEND IT until Twist turns it (0-960 ms), because f2 holds ring +1 where Twist leaves it while the plates draw it untwisted. The bump draws no HP change. Both wait for the designer and the GDD.
- **Open.** Packet 1 is never seen alive, because p2 already draws it trigger-dead. The Adjuster shot has no HP-tick change in the beat.
---

## H. Hover (designer note 9)

**Kept:** the hover dimming (R2 ruling Y12: everything not involved composited to k 0.38).
**R51 review:** dim is value x 0.40, chroma x 0.45. All hover motion is pencil (L6 + L5 in `PLAN`). FOCUS brackets are corners only, 12 px legs, 2 px legal / 3.5 px aimed, never a full outline. Spin2 and Nudge are inset strips on h01; the Shove bump is an inset on h06. h10 and h11 are required. No review-note card on the plate.

**2026-11-04 (art-pass, round 2; R1_REREVIEW question 4, option (a), N1, C6): the lift.** One lift for the board and the hover set (`corp/src/rb_lift.py`). The fan keeps its slot positions and never closes over a neighbour: the cards left of the hovered card never move, and the cards right of it may only open (30 px on board p2). The hovered card lifts straight up out of its slot, upright, and is drawn on top. The UNDO / SEND IT column sits 12 px right on every plate (SEND IT's right edge x 1913). Every sibling's protected set is its cost hex, its title band, its rules line and, on Nudge / Spin, its ×N plate: 0 px of it under the lifted card (check e, on the board and on every hover plate; the lifted card is its alpha ≥ 128, print and hard drop included). On board p2 (Trigger out of slot 2 under the p2 HUD with its option rows) this holds only with: the lifted card at the hand scale (zoom 1.00; at 1.10 no lift height clears Spin 3's ×3 plate and stays under the HUD, and under 0.99 its rules line drops under the 16 px cap height), its pink print and hard drop to the right (they went down-left, over the card it rose out of), the 4 px HUD panel gaps and the 96 px REFUND tab (A.7). The lift centre is y 718 (clear window 714-723). So the hovered card no longer grows (`card_hover_grow` is 1.00, it was 1.10; this amends the general rule below): it reads as lifted by its height, full value against the 88 % rest of the hand, its print and its drop. The hover stage searches its own slots with its own HUD (`python rb_lift.py search <slot>`) and draws with `rb_lift.layout`.

**2026-11-04 (art-pass, round 2: the hover stage and the docs pass; measured on the published plates).**
- **Correction to "12 px right on every plate".** The board plates have the button column 12 px right. The hover plates have it 16 px right (`rb_lift` BTN_DX 16, fan open 36 px), the top of the 12-16 px the call allows. Measured by the column-profile edge of the button plates, SEND IT's lit plate ends at x 1893 in round 1, x 1905 on the round-2 board and x 1909 on the hover plates (UNDO 1879 / 1891 / 1895). So UNDO and SEND IT move 4 px right when a hover starts, until the board takes the hover numbers (open). The "x 1913" above is not what this measure reads.
- **The hover plates (C6).** 22 of 26 meet the rule: lift at hand scale to centre y 718 (slots 1-3), fan open 36 px, and 0 px of any sibling's cost hex, title band, rules line or ×N plate covered. Also 0 px within 2 px of UNDO / SEND IT, hand min r 456.9, 0 lifted px within 3 px of a landing mark, and lowest hand pixel y 1064-1067. On h03 the REFUND tab slides 33.2 px left to clear the lifted Trigger (A.7).
- **h02 x4 (Brace, slot 0) is NOT FIXED.** A straight-up slot-0 lift stays outside r 459 only at centre y 906 or lower. Clearing Spin 3's cost hex and title band then needs the cards to its right open 43 px or more. That reaches the buttons: 25 px within 2 px at open 38, and 568 px at 43. The plates show open 36 at y 906: Spin 3's cost hex is 166 px covered and its title band 208 px, and check e fails. The lifted Brace also comes within 3 px of the lane-470 landing diamonds (257 px). Three options are for the designer: move slot 0 and the buttons further right (about 22-23 px for the opening alone; an estimate, not rendered), let a slot-0 lift move sideways, or rule that slot 0 does not lift.
- **Twist (C17).** On h04 the PLAN halo sits only on the legal rings: 0 pencil px on the bezel, the frame band (r 480-500) and outside r 500 (A.5). The h04 row below is corrected to match.
- **Dimming (3.13).** On h02 the five slices not aimed at read at a luma ratio of 0.394-0.397 to the board, and the aimed slice at 1.00. Across the set the dim is 0.391-0.393 and the lit areas 1.00.

**General rule:** the hovered card grows (`card_hover_grow`). Everything the card **touches** stays at full value. Everything else drops to k 0.38. The card's result is then drawn in the plan family (N): pencil marks, an L5 arrowed outline for any motion, and the HP grammar for the outcome (pink hatch = what we take, red hatch = what we still lose). The bill switches to the plan's numbers (GDD 2.10 / 9.2 ghost preview). Legal targets get `FOCUS` brackets; the aimed target gets thick brackets.

Card effect types in this fight (the state's 11 cards; GDD A.1 / A.2 cards that do not exist in Shifting Waves are out of scope):

| Plate | Effect type | Cards (RAM / Trace) | Stays lit | Dims (k 0.38) | Added marks |
|---|---|---|---|---|---|
| `h01_tower_turn` | **Turn the tower** | Spin3 (1/0), Spin2 (1/0), Nudge (1/0) | Tower, ring NOW, landing arcs, bill | Rings +1 / +2, queue, objectives | 40 percent tower ghost at the new angle; a pink L5 arc around the hub showing the turn (3 sectors for Spin3); new gun tracers and landing diamonds at plan value |
| `h02_brace` | **Protect a slice** | Brace (1/0) | All six slices (legal), the landing arcs that hit them | Rings, queue | FOCUS brackets on every slice; on the aimed slice, a 50 percent clamp ghost (L10) and the block result on its landing arc |
| `h03_trigger` | **Resolve a unit now** | Trigger (1/1) | Legal units on rings +1 / +2, the cells in their inward paths, tower slices facing them | Ring NOW cells not in a path, schedule | FOCUS on legal units; the aimed unit's inward path as a pencil L5 arrowed outline; pink hatch on the HP it takes; refund coin ghost on a kill; violet +1 on the Trace row |
| `h04_twist` | **Turn one ring** | Twist (0/0) | Rings +1 and +2, their landing arcs, the schedule | Ring NOW, tower interior | ~~An orange L5 sweep~~ (2026-11-04 round 2 docs pass, as the plates show it: all hover motion is pencil, R51) a `PLAN` pencil L5 arrowed sweep along the chosen ring (one sector, +1 or -1), and the pencil outline (L6) on the cell of each unit whose landing the Twist changes, on the twisted ring only (C17; none on the frame band); ghosts of the affected units at their new landing; the twist badge on the ring tag; four option rows in the HUD's reserved slots (C8) |
| `h05_strike` | **Damage a unit** | Strike (1/0) | Every unit in range | Tower, schedule | FOCUS on units; pink hatch on the aimed unit's 2 HP; a KO ghost if it dies |
| `h06_shove` | **Move a unit sideways** | Shove (2/2) | Units on rings NOW and +1, their neighbour cells | Ring +2, schedule | A sideways L5 arrow to the adjacent sector; bump starburst ghosts if occupied |
| `h07_pull` | **Move a unit inward** | Pull (0/1) | Units with an empty inner cell, the Adjuster | Other units | An inward L5 arrow; the Adjuster's in-range ghost |
| `h08_hold` | **Stop the rings this turn** | Hold (0/0) | The schedule bezel, all rings | Tower interior, HUD except the bill | The live cell shows the hourglass ghost; the later cells slide one slot (L5 arrows); landing arcs recomputed at plan value |
| `h09_firewall` | **Burn a sector** | Firewall (2/2) | Each sector column (legal), units that will step into it | Tower | A pink burn band ghost across the aimed sector through all rings; pink hatch on the next 2 units' HP |
| `h10_soak` | **Soak choice** (END TURN toggle, not a card) | — | All slices, the landing arcs | Rings | Indigo funnel ghost on the hovered slice; the SOAK hatch on its pip and the HP saved on the YOU strip |
| `h11_unit` | **Unit hover** (inspect, p2b) | — | The unit, its route, the slices it lands on | Everything else | The kept p2b form: pencil arrowed route ending in an arrowhead, FOCUS brackets on the cell, the hover tag (content parked) |

The hover designer delivers one 1920x1080 plate per row on f1 (h03 also on f2 to show the refund), with the nowords variant for h01-h04.

---

## I. Elements by family (ids from BRIEF.md 4 and 8; 199 elements, `gun_result_sealed` retired)

**P PLAYER (art-style family; style per A.1)**
- Tower: `hub_disc`, `hub_inner_rings`, `hub_label`, `hub_emblem`, `slice_frame`, `slice_screen`, `slice_screen_code_text` (retired: no code text), `slice_gutters`, `icon_burst`, `icon_shield`, `icon_turret`, `icon_repair`, `codebase_frame` (retired: P paint is "ours"), `nudge_ghost` (retired, 3.22 Open)
- Player HP and slice state: `hp_ring`, `slice_hp_bars`, `slice_pip_lost_harm`, `slice_pip_lost_soak`, `slice_pip_mend`, `slice_pip_gone`, `slice_break_x`, `slice_cracked_mark`, `slice_broken_state`, `you_hp_tally` (taped P strip on S)
- Player defences: `brace_plate`, `slice_soak_marks`, `slice_soak_rim_arc` (retired: the funnel and pip carry soak), `slice_soak_break_x`
- Guns: `gun_tracers`, `gun_muzzle_beads`, `gun_idle_stub`, `gun_tracers_preview`, `resolve_fire_lines` (= gun_tracers_preview)
- Cards: `hand_fan`, `card_frame`, `card_header_strip`, `cost_badge` (RAM coin stays S cyan: the cost is a system resource on a player card), `art_band`, `card_icon`, `card_icon_set`, `card_multiplier`, `card_title`, `type_band`, `rules_text`, `loud_tab`, `loud_tab_resting`, `card_hover_grow`, `played_liner`, `cards_nowords`, `card_unaffordable`, `card_committed`, `card_exhaust_keyword`, `card_key_hint`
- Identity and verb: `send_it`, `send_it_states`, `nameplate`, `sticker_material`, `stickers_nowords`

**E ENEMY (Solace corporate vector)**
- `empty_cell`, `ring_separators`, `unit_cell_screen`, `unit_screen_bezel` (retired), `unit_screen_code_text` (retired), `screen_motif_skull` (→ helix motif), `unit_cell_outline` (neutral `ENAMEL`, time grammar), `token_disc`, `token_lane_base` (retired: no lane base), `token_halo`, `token_placement`, `kind_colour_set` (→ cool slate set, A.2), `glyph_packet`, `glyph_worm`, `glyph_payload`, `glyph_jammer`, `glyph_ring`, `unit_hp_row`, `armor_cap`, `shield_bracket`, `warded_mark`, `ring_unit_wide6`, `unit_gone_state`, `consumed_unit`, `trigger_killed_unit`, `dead_x` (→ fx_kill still: pink hatch + KO burst)
- Boss: `adjuster_cell`, `adjuster_cell_underlay`, `adjuster_diamond`, `adjuster_hp_bar`, `ward_arc`, `adjuster_armor_strike`, `adjuster_as_target`

**T THREAT**
- `chev_solid_stack`, `chev_hollow`, `chev_sector_column`, `threat_trim`, `arc_chevrons`, `arc_diamonds`, `hero_pair` (THROUGH digit HARM, LANDS neutral), `hero_nowords_proxy`, `trig_lands_group`, `trigger_tower_hit` (pencil N path ending in T chevrons)

**K CLOCK (time and schedule)**
- Dial: `board_backplate`, `bezel_ring`, `bezel_rim_lines`, `bezel_ticks`, `sector_digits`, `sector_digits_nowords`, `needle`
- Schedule: `sched_this_turn` (HOT, L5 arrowed), `sched_chevrons`, `sched_hold_cells`, `sched_hold_live`, `sched_plus_cells`, `ring_tags`, `ring_tags_nowords`, `ring_tag_no_wave`
- Landing arcs: `landing_arc_frame`, `landing_arc_full_circle`, `arc_glyph_disc`, `arc_now_dot` (→ END notch), `arc_turn_dots` (→ turn pips), `arc_wear_mark`, `arc_check`, `arc_soak_chevron`, `arc_brace_glyph`, `arc_twist_mark`
- Wave queue (F): `future_wave_arcs` (→ queue strip), `wave_arc_unit_pips` (→ ticket glyphs and width bars), `climax_hazard_ticks`, `wave_tags`, `waves_left`

**N PLAN**
- `hover_path` (L5 arrowed outline, kept), `trigger_path`, `twist_badge`, `plan_pencil_underline`, `best_line_tag`, `option_plan_glyphs`, `spin_ghost_preview` (ghost + L5), `hover_slice_highlight`, `hovered_cell_outline` (→ FOCUS brackets), `trig_groups`

**X EFFECTS** (section G list, plus these existing elements)
- `refund_burst`, `refund_token` (coin is S; the burst is X), `ram_refund_pop`, `gun_result_hit`, `gun_result_armor`, `gun_result_ward`, `gun_result_shield_pop`, every `fx_*` id in G

**S SYSTEM (HUD)**
- Plates and ground: `terminal_plate_kit`, `header_plate`, `header_title`, `help_button`, `bill_frame`, `hud_scrim`, `board_scrim`, `backdrop_grade`, `layout_grid`, `focus_brackets`, `bottom_hint`, `undo_chip`, `nowords_variant`, `card_targeting`
- Bill: `eq_row`, `eq_labels`, `tally_segments`, `operators`, `empty_socket`, `split_row`, `route_arrows`, `next_row` (COLD), `without_twist_row`, `row_tags`, `option_chips`, `option_name_label`, `option_outcome_bar`, `option_pair`, `chain_strip`, `chain_step_discs`, `chain_step_glyphs`, `chain_step_names`, `chain_result_tallies`, `chain_result_prose`
- Objectives and resources: `objectives_frame`, `star_glyph`, `win_label`, `challenge_labels`, `challenge_tallies`, `challenge_trigger_hits`, `ram_trace_frame`, `ram_trace_labels`, `ram_pips`, `trace_pips`, `trace_cap_hatch` (padlock, **not** hatching: L7 is reserved), `ends_heat`
- Parked (note 8): `hover_tag`, `no_target_tag` (keep E10 form)

**Retired in this plan:** `gun_result_sealed`, `slice_screen_code_text`, `unit_screen_code_text`, `unit_screen_bezel`, `codebase_frame`, `nudge_ghost`, `token_lane_base`, `slice_soak_rim_arc`, the white landing lanes, the three future-wave arcs (replaced by the queue).

---

## J. Do-nots (redesign)

1. No dashed line anywhere on the combat screen.
2. No outline colour without a meaning in E. Lane colours and slice-type colours are gone.
3. No HOT treatment (glow, full chroma, END notch) on anything that is not resolving at this END TURN.
4. No cross-hatch for anything except "lost at this END TURN" (the Trace cap is a padlock, a broken slice is a black-out, an unaffordable card is dim glass with a padlock on its cost and a "NO RAM" tab, 2026-11-03).
5. No P texture (paint, drips, tape, doodle) on enemy cells, landing arcs, threat marks or the HUD terminal, except the taped YOU strip.
6. No E vector perfection on P elements: if the tower looks machine-made, it has failed the ownership read.
7. No glow on P, E, K or S marks except the HOT ones in C.
8. Never place an X, slash, hatch badge or effect glyph over the icon it describes (BRIEF do-not 4 holds).
9. Never add a number, word or count. Never drop one either (content guard, R1 ruling 13).
10. Never use a corp hue for a UI role.

## K. How designers use this plan

- Every option is rendered at 1920x1080 on `docs/concepts/combat_backdrop/v3_1/room_bio_bare.png` from a **copy** of `combat_e10_design/final/src` in `D:/rc_scratch/combat_redesign/<designer>/`, on all four states (f1, f2, f2t, f2b) where the element appears.
- Each option sheet states its family, its line ids (L1-L10), its time state (HOT / COLD / FAR) and its colour tokens, so that review checks the plan, not taste alone.
- Checks per option: 320 px squint (greyscale too, for the family read in A), deutan / protan / tritan, the nowords plate, and the content guard (assert_draw_log still passes).
- Deliverables go to `docs/concepts/combat_redesign/<stream>/`. Nothing in `combat_e10_design/` or the approved E10 plates is touched.
