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
| **N PLAN (the player's intent)** | Grease pencil on glass: waxy, grainy, no glow | L6 grease pencil (+ L5 when it is a route) | Freehand paths, X end caps, underlines | `PLAN` yellow | Mono 18 |
| **X EFFECTS (events, overlays)** | Light and print: additive light, halftone dot screens, speed lines, comic hit frames, krackle | L9 glow, halftone fill | Slice-wide and cell-wide fills, starbursts, shards | The colour of the cause (E) | None |
| **S SYSTEM (HUD)** | CRT terminal glass: flat navy glass, scanlines, cyan edge | L3 at Fine tier on the plate edge | Rectilinear plates, radius 8 | `NET_CYAN` = the terminal itself, RAM | Share Tech Mono 18/22, Anton heroes |

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
- **R51 review: value cap.** The brightest large P fill on the tower is L* 75 or less (paper discs multiplied to 70-72 percent value; cards at 88 percent). Peak value order: SEND IT, HOT T marks, the lifted card, tower slices, the rest of the hand, E cells. **2026-11-03 (art-pass, review response):** the K clock (tape, sweep, plates) sits below the tower at L* 45-55 gunmetal, with SCHEDULE orange on the live step only. Slice inks are L* 60-72, and the icon discs carry the tower's peak. Occupied E cells are at L* 40-45 vs empty cells at 28 (3:1 floor). Token discs never outrank HOT marks.
- **R51 review: icons are re-inked, not re-designed.** One turret stays one turret, Brace stays the clamp, Twist stays the ring arrow.
- **R51 review: shading on P** is single-direction hatch only; cross-hatch stays L7 (loss at END TURN).

### A.2 E ENEMY: Solace corporate vector

The contrast to P. It is clean, cold, machine-made and perfect.
- **Cells:** frosted glass wash in a cool **kind slate** (Packet #3D5466, Worm #4B4A6E, Jammer #2D5D69, Payload #5B5560, Ring #55617A; Adjuster is gold, see below). The minimum dE between kinds is 10 in all four vision modes (the designer of this family must measure it and report). The E10 mauves are retired: with the player now pink, mauve units would read as player-owned.
- **Line:** L3 vector only. The edge is `ENAMEL` #D9E1EA at 1.5 px, with a 3 px ink line outside it. All cell outlines are this one colour on every ring: **no lane colours** (designer note 5).
- **Texture:** one Solace clinic motif (a thin double-helix rule) at 6 percent contrast inside the cell screen. It replaces the skull motif, the code text, the CRT dot grid and the programme bezel corners (all retired).
- **Tokens:** the disc is 54 px with an `ENAMEL` 2 px ring and the kind glyph from the kglyph2 master. There is no lane-coloured base ring.
- **Enemy HP:** `CREAM` #FFF4D6 vector ticks (D below).
- **Adjuster (boss):** `BOSS_GOLD` #FFC428 is its body, its cell edge (2.5 px, L3), its ward and its HP. It is the one enemy mark with colour on its outline, because gold means "the boss".
- **Corp hue:** `corp_solace` #3DFF8B never takes a UI role. Solace shows by material (clinical glass, enamel, helix motif) and by the backdrop room.

### A.3 T THREAT

Chevrons (hit per slice), diamonds (HP that gets through), the threat trim on the slice rim, and the THROUGH hero digit. They are flat `HARM` #FF4433 stencil shapes with a 4.5 px `INK` keyline and no texture. This is the only family with saturated flat red. They obey the time grammar (C): hot this turn, cold for future turns. E10's best idea is kept: **solid chevron = hit, hollow chevron = growth still to come.**

### A.4 K CLOCK

The bezel, needle, sector digits, schedule cells, ring tags, landing arcs and the wave queue. The material is machined gunmetal: fill #262B33 with L4 engraved grooves (1.4 px #0A0C10 with a 1 px #5C6472 highlight 1 px below, light from top-left). Ticks are engraved, not drawn. `SCHEDULE` #FF8C1A appears on schedule step cells only. The bezel's Solace teal enamel (R1 ruling 4) is withdrawn: the clock is neutral machinery, because a teal bezel would read as enemy.

### A.5 N PLAN

Hover path, trigger path, twist badge, plan underline, BEST LINE, option selection and the hovered-cell focus. The material is grease pencil: `PLAN` #FFE200, 7 px with a 3 px ink edge, a wax grain texture (8 percent noise) and **no glow**. When the player commits a plan (SEND IT, or a Trigger resolving mid-turn), pencil marks turn into P paint in the resolve beat (X effect FX-T).

### A.6 X EFFECTS

Every event overlay (section G). The material is light and print: additive colour, halftone Ben-Day dots (6 px pitch, 45 deg screen), speed lines, starburst hit frames, krackle (black energy blobs) for enemy harm, and a 3 px misregistration only on impact frames. X is the only family that blooms. The colour is the cause colour (E).

### A.7 S SYSTEM

The header, bill, objectives, RAM / Trace / Heat, UNDO, the hover tag and the bottom hint. They use the one terminal kit (`hud2.P()`): navy glass #050D1C at 93 percent, `NET_CYAN` edge 1.5 px, radius 8, scanlines at 4 percent. **Player-owned data on the HUD is taped on:** the YOU HP row is a strip of P paper (in the chosen style) taped onto the terminal, so player HP reads as the player's in both places (tower ring and HUD).

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
| Played-card empty slot | Torn-paper outline (P), no dash |
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
| **Current (lit)** | Solid fill: player `GAIN` #7BE07B as painted blocks (P style); enemy `CREAM` #FFF4D6 as clean vector ticks; boss `BOSS_GOLD` | HP you have now |
| **Lost at this END TURN, harm** | Socket dark, **L7 cross-hatch in `HARM`**, solid 2 px HARM edge, L9 glow 4 px | The enemy takes it when you press SEND IT |
| **Lost at this END TURN, soak** | L7 cross-hatch in `SOAK` #3A7EF3 + a 5 px chevron notch cut into the outer edge | Your soak choice spends it |
| **Lost at this END TURN, by us** (enemy HP) | L7 cross-hatch in `CELL_PINK` | Our guns, Strike, Trigger or Firewall take it |
| **Lost in a future turn** (NEXT row, +1 forecast) | COLD: hollow 1.5 px outline in the cause colour at 70 percent value, one turn pip before the run | A forecast, not this turn |
| **Mend pending** (REPAIR) | Empty socket, 2 px `GAIN` outline, a centred 7 px plus, a small upward tick above | It comes back at END TURN |
| **Gone** (lost earlier) | Dark socket #0E1016, solid 1.4 px hairline #3A4150 | Already gone; nothing changes |
| **Blocked** (absorbed by SHIELD or Brace) | The segment stays lit. An L10 double-line plate (P, paint) sits in front of the incoming chevrons at the slice rim. Count is shown by the plate's tally ticks | It would have been lost, but your protection takes it |
| **Enemy shield layer** (Jammer) | Separate hollow hex pips (vector, `ENAMEL`) in front of the HP ticks, inside an L10 double-line bracket | Shield empties before HP |
| **Armor** | L10 double-line steel cap (`STEEL` #96A2B6, highlight `STEEL_HI` #E2E9F6) along the cell's outer edge | Each incoming hit is 1 less |

**The cause-colour rule:** cross-hatch always means "goes at this END TURN". The hatch colour says who takes it: red is the enemy, indigo is your soak, pink is you. In the nowords plate the hatch alone still reads as "going".

Sizes:
- **Player HP ring (R51 review: moved to the hub):** 15 segments **wrapping the hub at r 52-64**, in 3 groups of 5 with a 9 deg group gap and a 2.5 deg segment gap. It no longer sits on the rim, where red pending hatch merged with the red threat trim. The pending run starts at the needle and runs clockwise; no sector meaning is implied.
- **Thin-segment hatch (R51 review):** on any segment under 9 px, L7 is a single-direction 45 deg hatch, 1.6 px lines at a 4 px pitch, and the pending segment is 2 px thicker than lit ones (bulges outward). Two-direction hatch only on segments 12 px or more. If the hatch collapses to solid at 320 px, widen the pitch; never drop it.
- **YOU tally:** the same 15 segments, 22x14 px, in groups of 5, on the taped P strip.
- **Slice pips:** 2 per slice, 30 deg capsules 8 px thick at r 128-136.
- **Unit HP:** ticks 6 px wide, 10 px tall, 3 px gap, sector gap 8 px, along the cell's outer edge. These are ticks, not long dashes, so they cannot read as a dashed border.

---

## E. Colour meanings (designer note 5)

Twelve meanings. Every other outline or fill is neutral.

| Token | Hex | The one meaning | Shape it always pairs with |
|---|---|---|---|
| `CELL_PINK` | #FF3DA8 | **Ours:** the player's tower, cards, guns, damage we deal | Painted stroke (L2) |
| `HARM` | #FF4433 | **Damage to you** (from the enemy) | Chevron, diamond, red hatch |
| `GAIN` | #7BE07B | **Your life:** HP and slice pips you keep or regain; a landing that costs nothing | HP segment, check, plus |
| `SOAK` | #3A7EF3 (R51 review: #464EFF failed protan vs Trace, dE 2.4) | **Your soak choice** | Chevron notch, funnel |
| `PLAN` | #FFE200 | **Your plan / preview** | Grease pencil (L6) |
| `SCHEDULE` | #FF8C1A | **The rings move:** schedule steps | Bezel step cell, L5 chevrons |
| `BOSS_GOLD` | #FFC428 | **The Adjuster** and its ward | Diamond body, gold lozenge |
| `NET_CYAN` | #5CE1FF | **The terminal and RAM** | HUD plate edge, RAM coin |
| `TRACE_VIOLET` | #A03CFF | **Trace** | Square r3 |
| `CRT_AMBER` | #FFB000 | **Heat** | Flame |
| `RESIST_GOLD` | #FFD24D | **Stars** | Star |
| `FOCUS` (`cell_acid`) | #D4FF00 | **Keyboard / target focus** | Four corner brackets only |

**Neutral** (no meaning): `ENAMEL` #D9E1EA (enemy outlines), gunmetal #262B33 / #5C6472 (clock), `INK` #0C0A16, `PAPER` #F2EEE4, `TEXT_HI` / `TEXT_MID` / `TEXT_LO` #F2F6FF / #AFC0D6 / #7A889C, `STEEL` (armor, pairs with the double line), `CREAM` (enemy HP, pairs with the tick).

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
- **WAVES 6 LEFT** in the header becomes the queue's own count (header keeps the number, the queue keeps the pips; content guard: the word and the 6 stay).
- **Freed space** (r 470-510): the landing arcs move out to r 436-470 so they no longer stack against the bezel (do-not 5: no more than two parallel arcs within 12 px). The board keeps its 24 px screen margin.
- **R51 review:** tickets are 84x64 px (glyphs 24 px) with **solid** edges; time is by value (W6 50, W5 70, W4 100 percent) and pips. The freed band is spent on the player: the tower grows to **r 196** (threat trim r 200-210), rings NOW / +1 / +2 re-space into r 214-430. If a unit glyph drops under 44 px or a cell under 30 px deep, cap the tower at r 184. The card hand grows 1.15x.

---

## G. Effect overlays (designer note 7)

Every event has a **slice-wide** (whole wedge, r 44-162) or **cell-wide** (whole unit cell) overlay, grouped into six effect families. Each family looks distinct from the others. Each effect has a **still** (used on plates and in the p2 preview at 45 percent) and an **anim** (resolve beat, 60 fps). All effects follow GDD 9.6: no more than 3 flashes per second, and a reduce-effects variant (the still only, no halftone shimmer, no misregistration).

| FX family | Signature | Colour | Shape language |
|---|---|---|---|
| **FX-P Protect** (your defence holds) | A paper or paint plate slams over the wedge's outer 40 percent; a painted L10 double edge | `CELL_PINK` + `PAPER` | Flat plate, rivets drawn in the P style |
| **FX-H Harm** (the enemy hurts you) | Red halftone flood rolling in from the rim, black krackle blobs, a 3 px misregistration on the impact frame | `HARM` + `INK` | Flood, crack, krackle |
| **FX-D Damage** (we hurt them) | Comic hit frame on the enemy cell: pink starburst panel, speed lines toward the cell, shards in clean vector | `CELL_PINK` + white | Starburst, speed lines |
| **FX-L Life** (gain) | Rising GAIN brush strokes and sparkles | `GAIN` | Upward strokes, plus |
| **FX-M Motion** (things move) | Smear frames (3 echo copies at 30 / 20 / 10 percent) and an L5 arrowed sweep along the path | Owner colour: `CELL_PINK` tower, `SCHEDULE` rings, `PLAN` plan | Echo, arrowed sweep |
| **FX-C Corp** (the enemy changes state) | A clean vector scan-wipe (1 px enamel line sweeping across the cell, then a flat flash) | `ENAMEL`, `BOSS_GOLD` for the boss | Hard wipe, no texture |
| **FX-S System** (Trace and Heat) | A violet scanline glitch slice across the whole board, 6 px offset bands | `TRACE_VIOLET`, `CRT_AMBER` | Horizontal bands |

**Every effect** (ids are `fx_*`, owners in brackets):

| Id | Event (state source) | FX | Footprint | Still | Anim (frames at 60 fps) |
|---|---|---|---|---|---|
| `fx_shield_block` | SHIELD slice absorbs (f1: absorbed 6) | P | Slice-wide | Pink plate on the outer 40 percent; incoming chevrons stop at its edge | Plate slams in 6f, chevrons hit and deflect outward as white sparks 10f, hold 12f |
| `fx_brace_block` | Brace blocks a whole landing (f2: TURRET, braced_hit) | P | Slice-wide | Painted clamp plate (L10) over the full wedge; the landing arc stops at the clamp | Clamp closes 8f, impact ring 8f, chevrons crumple 12f |
| `fx_soak_take` | A soaked slice takes the overflow (f2: SHIELD sector 1, soaked 1) | P | Slice-wide | The wedge fills with an indigo funnel from the rim; the soak pip hatches | Funnel draws in 10f, pip drains 10f |
| `fx_shield_break` | Our SHIELD slice breaks while blocking (f1: sector 1 hp_after 0) | H | Slice-wide | The plate is cracked in 5-7 shards; red flood behind | Plate shatters into paper shards 12f (misregistered), red flood 10f, wedge goes dark |
| `fx_hit_land` | Landing hit, pip lost (f1 log "hit") | H | Slice-wide | Red halftone flood across the outer 50 percent, krackle at the rim | Flood rolls in 8f, krackle pops 6f, fade 10f |
| `fx_slice_crack` | Slice goes 2 → 1 | H | Slice-wide | A jagged white crack across the slice glass, off the icon | Crack draws 6f |
| `fx_slice_break` | Slice goes to 0 (ability lost) | H | Slice-wide | Wedge black-out with a red stencil X in the outer corner (never over the icon); halftone fade over the icon | Flood 8f, X stamps 4f, black-out 12f |
| `fx_hp_through` | HP gets through (diamonds → YOU) | H | Rim to HUD | Red diamonds on the arc | Diamonds fly to the YOU strip along a curve, 18f, the YOU hatch then empties |
| `fx_worm_wear` | Worm wears 1 more pip | H | Slice-wide | A second, smaller krackle with a hook mark | 6f after the hit |
| `fx_jam` | Jammer jams a slice (latent) | H | Slice-wide | Static noise in red bands over the wedge | Static 12f, holds as a COLD state |
| `fx_adjuster_strike` | Adjuster strike (latent) | H | Slice-wide | Gold-edged red flood | As fx_hit_land with a gold rim flash |
| `fx_gun_hit` | Gun shot hits (f1 guns: hit) | D | Cell-wide | Pink starburst on the cell at the tracer end; the HP tick hatches pink | Tracer paints 6f, starburst 6f, speed lines 8f |
| `fx_strike` | Strike card (2) | D | Cell-wide | Bigger starburst plus a painted slash | 10f |
| `fx_trigger_hit` | Trigger hit on a unit (f2 tlog trig_unit) | D | Cell-wide | Starburst at each struck cell along the yellow path | Path ignites pencil → pink paint 8f, then the starbursts in sector order |
| `fx_firewall_burn` | Firewall burn | D | Cell-wide | Pink flame-stroke band across the sector | 12f |
| `fx_shove_bump` | Shove collision | D | Both cells | Two small starbursts at the shared edge | 8f |
| `fx_kill` | A unit dies (f1: Worm 2 shot dead; f2: Packet 1 Trigger-killed) | D | Cell-wide | The cell is pink-hatched (L7) with a white-and-pink KO starburst at the token (no word) | Flash white 2f, vector shards fly 14f, cell left empty |
| `fx_shield_pop` | Enemy shield layer pops (Jammer, latent) | D | Cell-wide | Hex pips shatter (vector shards) | 8f |
| `fx_armor_bounce` | Shot bounces off armor (latent) | D | Cell-wide | Steel spark ricochet off the L10 cap | 8f |
| `fx_ward_bounce` | Shot weakened by the ward (f2: BURST 4 → Packet 6, ward ×2) | D | Cell-wide | Gold ricochet streak off the gold lozenge; no starburst | 8f |
| `fx_repair_mend` | REPAIR mends 1 pip (latent) | L | Slice-wide | GAIN brush strokes rising through the wedge | 14f |
| `fx_refund` | Trigger-kill refund +1 RAM (f2) | L | Cell to HUD | RAM coin with plus at the killed cell | Coin pops 6f, flies to the RAM row 16f |
| `fx_clear` | Nothing gets through (arc check) | L | Arc | GAIN check on the arc | 6f |
| `fx_spin` | Spin / Nudge turns the tower | M | Whole tower | 40 percent ghost of the tower at the new angle + a pink L5 arc around the hub | Smear echoes 12f |
| `fx_twist` | Twist turns ring +1 (f2: [1, 1]) | M | Whole ring | Orange L5 sweep along ring +1, one sector | Echo smear 12f |
| `fx_rings_step` | Rings step in and turn at END TURN (schedule +2) | M | All rings | The THIS TURN schedule cell's arrowed outline | Rings slide inward 16f with echoes |
| `fx_hold` | Hold puts a 0 in the schedule | M | Bezel | The hourglass stamp on the live cell | The schedule cells slide one slot later 12f |
| `fx_pull` | Pull drags a unit inward | M | Two cells | An L5 inward arrow | 12f |
| `fx_shove` | Shove moves a unit a sector | M | Two cells | An L5 sideways arrow | 12f |
| `fx_wave_enter` | The next wave enters ring +2 | M | Ring +2 | The queue feed arrow lights | The ticket slides into the ring 14f |
| `fx_grow` | A unit grows +1 hit | C | Cell-wide | The new hollow chevron | Enamel scan-wipe 8f, chevron flash 4f |
| `fx_ward_on` | Ward applies to units in the Adjuster's sector | C | Cell-wide | The gold lozenge | Gold scan-wipe 8f |
| `fx_boss_phase` | Adjuster phase change / armor on (latent) | C | Cell-wide | The gold cell with a steel cap | Gold wipe + cap clamps 12f |
| `fx_trace_add` | A loud card adds Trace (Trigger +1) | S | HUD and card | A violet square pops | Glitch band across the card 6f |
| `fx_lockdown` | Trace lockdown (latent) | S | Whole board | Violet bands over the board | 3 bands, 18f (within the flash cap) |
| `fx_commit` (FX-T) | SEND IT / a Trigger resolves now | N → P | Plan marks | — | Every pencil mark burns into pink paint 8f, then the beat plays |

**R51 review: pruning.** `fx_worm_wear` and `fx_adjuster_strike` are variants of `fx_hit_land`; `fx_armor_bounce` and `fx_ward_bounce` merge into `fx_ricochet`; `fx_jam`, `fx_shield_pop`, `fx_boss_phase`, `fx_lockdown` are parked (latent); `fx_clear` is a still only. Pull, Shove and Twist resolve in pink. Firewall is a pink flame band inside the column, 60 percent of cell depth, no white cores. The core build list is in REVIEW.md section 3.

**Layer order in resolve:** board → T threat → FX-M → FX-P / FX-H (tower) and FX-D / FX-C (rings) → FX-L → FX-S → HUD.

---

## H. Hover (designer note 9)

**Kept:** the hover dimming (R2 ruling Y12: everything not involved composited to k 0.38).
**R51 review:** dim is value x 0.40, chroma x 0.45. All hover motion is pencil (L6 + L5 in `PLAN`). FOCUS brackets are corners only, 12 px legs, 2 px legal / 3.5 px aimed, never a full outline. Spin2 and Nudge are inset strips on h01; the Shove bump is an inset on h06. h10 and h11 are required. No review-note card on the plate.

**General rule:** the hovered card grows (`card_hover_grow`). Everything the card **touches** stays at full value. Everything else drops to k 0.38. The card's result is then drawn in the plan family (N): pencil marks, an L5 arrowed outline for any motion, and the HP grammar for the outcome (pink hatch = what we take, red hatch = what we still lose). The bill switches to the plan's numbers (GDD 2.10 / 9.2 ghost preview). Legal targets get `FOCUS` brackets; the aimed target gets thick brackets.

Card effect types in this fight (the state's 11 cards; GDD A.1 / A.2 cards that do not exist in Shifting Waves are out of scope):

| Plate | Effect type | Cards (RAM / Trace) | Stays lit | Dims (k 0.38) | Added marks |
|---|---|---|---|---|---|
| `h01_tower_turn` | **Turn the tower** | Spin3 (1/0), Spin2 (1/0), Nudge (1/0) | Tower, ring NOW, landing arcs, bill | Rings +1 / +2, queue, objectives | 40 percent tower ghost at the new angle; a pink L5 arc around the hub showing the turn (3 sectors for Spin3); new gun tracers and landing diamonds at plan value |
| `h02_brace` | **Protect a slice** | Brace (1/0) | All six slices (legal), the landing arcs that hit them | Rings, queue | FOCUS brackets on every slice; on the aimed slice, a 50 percent clamp ghost (L10) and the block result on its landing arc |
| `h03_trigger` | **Resolve a unit now** | Trigger (1/1) | Legal units on rings +1 / +2, the cells in their inward paths, tower slices facing them | Ring NOW cells not in a path, schedule | FOCUS on legal units; the aimed unit's inward path as a pencil L5 arrowed outline; pink hatch on the HP it takes; refund coin ghost on a kill; violet +1 on the Trace row |
| `h04_twist` | **Turn one ring** | Twist (0/0) | Rings +1 and +2, their landing arcs, the schedule | Ring NOW, tower interior | An orange L5 sweep along the chosen ring (one sector, +1 or -1); ghosts of the affected units at their new landing; the twist badge on the ring tag |
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
4. No cross-hatch for anything except "lost at this END TURN" (the Trace cap is a padlock, a broken slice is a black-out, an unaffordable card is dim glass).
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
