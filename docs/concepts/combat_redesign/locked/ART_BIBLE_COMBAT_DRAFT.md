# ART_BIBLE amendments: ring-wheel combat screen (roadmap step 9)

> **DRAFT, waiting for designer sign-off; not folded into ART_BIBLE.md.**
> Two designer-ruling notes are already in `docs/ART_BIBLE.md` (added 2026-11-04): 2.4 (DR-6, the
> combat enemy rings) and 3.14 (DR-9, the cutaway room). Nothing else in it has been edited. This
> file proposes the remaining changes as a diff-style list:
> each entry quotes an ART_BIBLE section heading, then says **Replace** or **Add** and gives the new text.
> Once the designer signs off, the fold is mechanical: apply the entries, bump the bible to v2.2, move
> the tokens into `Palette` in the same commit, and add a `DECISIONS.md` line (bible 2, "A token
> changed below MUST be changed in `Palette` in the same commit").

Date: 2026-11-02; brought in line on 2026-11-04 with the designer rulings DR-1..DR-10 (`VISUAL_PLAN.md`),
the two bible notes above, `locked/REVIEW_RESPONSE.md` and the rebuilt values (the rebuilt board, gate 1;
the effects rebuild of 2026-11-03; `GODOT_PORT_SPEC.md` and its generated `port/` data). Branch `art-pass`.
Author: art-pass (art bible editor).

**Round 2 (2026-11-04, docs pass).** Brought in line with round 2 of the rebuild: the art-pass calls C1-C18 of
`locked/REVIEW_RESPONSE.md`, "Round 2 (2026-11-04)", answering the re-review `R1_REREVIEW.md`. They are tagged
**[R]**: art-pass calls, open to the designer, not designer rulings. Every round-2 number is measured on the
published plates (`final/checks.json`, `hover/checks.json`, `backdrop/checks.json`, `transitions/metrics.json`).
DR-1..DR-10 are unchanged and still win. This file is still a **draft**. In this file, "C1"-"C16" in the
section 0 table are conflict numbers; the round-2 calls are written "call C1" to "call C18". The effects set
(3.22.F) was not re-rendered on the round-2 board.

**Sources** (later ones win where they disagree):
- `combat_redesign/VISUAL_PLAN.md`, the designer rulings DR-1..DR-10 (they win over everything below)
- `locked/REVIEW_RESPONSE.md` (the call on every AD-review finding: implementation or documentation) and
  `D:/Godot/rebel_cell/docs/reviews/ad_review_overnight_2026-11-02/AD_REVIEW.md`
- `locked/GODOT_PORT_SPEC.md` and `locked/port/*.json` (the rebuilt values, generated from the data)
- `docs/concepts/DIRECTION_REVIEW.md`, ART CALLs 51-53 and O-27 to O-29
- `combat_redesign/VISUAL_PLAN.md` (the R51 rulebook)
- `combat_redesign/locked/REVIEW.md` (the AD review of the locked board, O-29 fix list)
- `docs/concepts/SOLACE_SLICE_ROADMAP.md`, "Added 2026-11-01: combat screen"
- `locked/{wheel,cards,assembled,corp,final,hover,backdrop,transitions}/NOTES.md`
- `locked/effects/NOTES_CDHL.md` and `NOTES_MPST.md`

**How to read the authority of each rule.** Every rule below carries one of these tags:
- **[D]** designer ruling, given in an ART CALL or recorded as DR-n in `VISUAL_PLAN.md`. Binding once folded.
- **[R]** an art-pass call recorded in `REVIEW_RESPONSE.md` for an AD-review finding. It stands unless the designer overrules it.
- **[AP]** art-pass default taken while the designer has not ruled (ART CALL 53 lists them). The designer can overrule any of them.
- **[M]** a measured spec from the locked final pass, kept so the port matches the plates.

**Scope.** These rules cover the **ring-wheel combat screen** (Shifting Waves: one spinner, the
enemy rings around it, the bill on the right). The two-wheel D4 combat in bible 3.1-3.21 is not
redrawn by this work. Where a 3.x rule clashes with the ring board, the entry below scopes the old
rule to D4 wheels rather than deleting it. Whether the D4 combat should take the new player family
later is an open question (Q1 at the end).

---

## 0. Conflicts with the current bible (summary)

Each one is resolved by an entry below. The designer should confirm each resolution.

| # | Current bible says | The new combat work says | Proposed resolution |
|---|---|---|---|
| C1 | 1.2 "Rejected (do not reintroduce): spray paint and stencils, the dripping marker, ransom collage, ink brush". 1.1 anti-word "graffiti chaos" | The player family is punk print: xerox spot inks, linocut key line, Ben-Day, collage, mural and Jinx card art, stencil glyphs. The designer asked for street and sketchbook graffiti, then punk rock (ART CALLs 51.1, 52.2, 53) | Carve out the ring-wheel combat player family from the Rejected list. Keep the list for the city, the map and the D4 combat. "Graffiti chaos" stays an anti-word: the punk family is ordered (one key line, one halo, texture caps) |
| C2 | 1.2 Vinyl sticker: cards are vinyl stickers (gloss, white die-cut, peel). 3.18 sticker cards, yellow cost dot, hover scale ~1.36 | WPAP print cards: chamfered die-cut, facet planes, a type plate, cyan cost hex, hover 1.10x (ART CALL 53; since round 2 the hovered card lifts straight up at the hand scale, 1.00x [R, call C6]) | 3.18 is scoped to D4 combat; the ring board uses the WPAP card (3.22.D) |
| C3 | 1.2 Binary bits carry "damage shards", and 3.20 says "All FX use bits in the source colour" | Ring-board hits use 8 effect families with their own materials (pink comic hit, red X-halftone print, corp scan line...). Bits stay for the T5/T6 transitions only | 3.20 is scoped to D4; the ring board follows 3.22.F. Bits keep their transition job |
| C4 | 1.2 grease pencil: "Solid = what will happen; dashed = what-if". 3.17 dashed ghost blades. 3.5 status badge "dashed outline = predicted". 3.22 "+2 = dashed pale 3 px" lane | No dashed lines anywhere on the combat screen [D, ART CALL 51.2] | Dashes are banned on the ring board. What-if, predicted and +2 take the HOT/COLD/FAR grammar (3.22.B) |
| C5 | 3.22 E8/E9: "Pink has one job: unit screens"; CELL-9 and the code-base frame cyan; SEND IT yellow; lane trim pale blue; rider lavender | Pink belongs to the player: spinner, cards, guns, SEND IT, nameplate, damage we deal [D/AP, ART CALL 51.1 and O-27]. Enemy cells are corp enamel | Replace the 3.22 E8/E9 colour block |
| C6 | 3.22 lane outlines: NOW solid red 4 px, +1 solid pink 3 px, +2 dashed pale; lane style on the token base | One enamel outline for every enemy cell [D, ART CALL 51.5]; depth is read by the time grammar | Replace |
| C7 | 3.22 "the needle is sector 0"; 3.2 pointer blade | No needle on the new combat concept [D, ART CALL 52.3] | Replace on the ring board; D4 wheels keep their blades |
| C8 | 3.22 waves beyond the rim as concentric arcs; climax arc in HARM red | W4-W6 compressed to three tickets top-left [D, ART CALL 51.6 met] | Replace |
| C9 | 3.22 Soak is orange chevrons; shield a cyan bracket; Brace a cream clamp; FIREWALL an orange hatched wedge | Soak is SOAK blue hatch with a chevron notch; hatch is reserved for END TURN loss; Firewall is a pink flame band | Replace |
| C10 | 2.1 `NET_CYAN` / `PROTECT` = "defend/shield slices, block and shield FX". 2.3 slice colour = type (attack pink, defend cyan...) | SHIELD slice ink is blue #5E9BE0 (the rebuild's L* 60-72 inks); the protect FX is on its own P stock #F6C8DE; cyan means terminal and RAM only | Add a ring-board row to 2.3 and narrow `NET_CYAN` on that screen |
| C11 | 2.4 Solace secondary pink #FF4696, and the 2.4 rules that the DR-6 note amends for the enemy rings | Corp theme by material plus the corp hue on the rim, bezel lip, crest and cell edges; neutral slate cell fills [D, DR-6] | **Done:** the DR-6 note is in ART_BIBLE 2.4 (2026-11-04). Solace's pink is not a hue ink on the board (2.4 entry below) |
| C12 | 5.1 colour-blind check (Machado 2009) for every screen | The designer said to ignore colour-blind checks [D, ART CALL 52.4] | Proposed: the waiver covers the combat redesign concept pass. The greyscale check stays. The shipping build runs the CVD check as 5.1 says [AP; old Q2 closed, 5.1 entry] |
| C13 | 5.3 VfxTier T2 outcome: max 0.6 s, 60 % local flash | The 2026-11-02 set ran 24 of 32 effects at 650-1150 ms. The 2026-11-03 rebuild runs every effect at 0.6 s or less with no override; the kill flare is 2 frames at 55 % on the token; the resolve beat is 3.8 s against 4 s, skip on any input | **Resolved [R], REVIEW_RESPONSE 2.11:** the effects follow 5.3 as written (T2); no ring-board exception is needed |
| C14 | 6.4 combat layer order: FX world layer is under the HUD | The 2026-11-02 effects slot sat above the board, tower and HUD | **Resolved [R], REVIEW_RESPONSE 1.6:** board effects under the HUD and the hand (6.4 as written); only `fx_hp_through`, `fx_refund` and `fx_trace_add`, which land on HUD rows, sit above them. The rebuilt effects are composited that way |
| C15 | Appendix B 3: "the designer closed 'no design needs card type now'" (DECISIONS 2026-10-16) | ART CALL 53: a different colour behind each type band (TOWER, WAVE) [D] | ART CALL 53 is later and wins for the ring board. A `DECISIONS.md` line is owed |
| C16 | 2.10 focus brackets 3 px, 7 px outside | Hover FOCUS corners 2 px (legal) and 3.5 px (aimed), 12 px legs, on board cells | Board cells take the hover corner spec; chrome keeps 2.10 |

---

## 1. Pillars and media

### "### 1.1 North star"
**Add** after the tone line:
> **Ring-wheel combat (designer, ART CALLs 51-53):** the board reads as three layers, each with its
> own material: the **player** in loud punk print (spinner, cards, SEND IT, nameplate, the YOU strip),
> the **corp** in calm enamel and material (the rings, rim, tickets), and the **system** in cyan
> terminal glass (the HUD). "Graffiti chaos" stays an anti-word: the punk print is ordered by one
> key line, one halo and capped textures.

### "### 1.2 The media and their jobs (LOCKED)"
**Add** two rows to the media table:

| Medium | Job | Look | Never |
|---|---|---|---|
| **Punk print** (ring-wheel combat only) [D] | **What the player owns on the board:** the spinner, its slices and hub, the guns, Brace and soak marks, the cards, SEND IT, UNDO, the CELL-9 nameplate, and the YOU strip taped onto the terminal | Xerox flat spot inks with big distinct textures, the linocut black key line with a block drop, a pink scissor-cut halo, ink printed off register, Ben-Day shapes; WPAP faceted cards with band art from the other punk styles (3.22.C, 3.22.D) | Glow; cross-hatch shading (hatch means loss); covering a ring cell, landing arc or threat mark (GDD 9.2) |
| **Corp enamel** (ring-wheel combat only) [D, DR-6] | **What the enemy owns on the board:** ring cells, unit tokens, bezel, landing annulus, rim, crests, wave tickets | Clean vector on frosted enamel, perfect geometry, one hairline; per corp a material, with the corp hue only on the rim, bezel lip, crest and cell edges; neutral slate cell fills (ART_BIBLE 2.4 note; 3.22.E) | Pink; grit or hand-made texture; the clock (that is time grammar) |

**Replace** in the Vinyl sticker row, Job column, "cards," with:
> cards (on D4 combat; ring-wheel combat cards are punk print, 3.22.D),

**Replace** in the Grease pencil row, Look column, "Solid = what will happen; dashed = what-if." with:
> Solid = what will happen; dashed = what-if (not on the ring-wheel combat screen, where dashes are
> banned and the plan is always solid pencil, 3.22.B).

**Replace** in the Binary bits row, Job column, "damage shards," with:
> damage shards (D4 combat; on the ring board hits use the effect families of 3.22.F, and bits carry
> the T5/T6 transitions),

**Add** after "**Rejected (do not reintroduce):** ...":
> **Exception (designer, ART CALLs 51-53):** on the ring-wheel combat screen the player family uses
> xerox, linocut, Ben-Day, collage, mural, Jinx scribble and stencil-cut glyphs, inside the punk print
> rules of 3.22.C and 3.22.D. The Rejected list still holds everywhere else (city, maps, netrun, D4
> combat, menus).

---

## 2. Palette, tokens and typography

### "### 2.1 Brand and neutral tokens (kept from v1)"
**Add** under the table:
> **On the ring-wheel combat screen** [D/AP]: `CELL_PINK` means **ours** (the player's spinner,
> cards, guns, SEND IT, nameplate, damage we deal, the pink hatch on enemy HP). Nothing the enemy
> owns is pink. Measured pink-hue pixels in the enemy zone (r 214-500) on the rebuilt board: 1.38-1.39 % on
> the three skins (`final/checks.json` `corp`, round 2; 1.39 % at gate 1; 0.23 % on the 2026-11-02 board). The share is reported,
> not gated, and which marks the pink pixels in that zone come from is not yet broken down (Q4 below) [M].
> `NET_CYAN` means the **terminal and RAM** only (HUD plate edges, RAM coins, the
> card cost hex). It does not mark shields or blocks on this screen.

### "### 2.2 Semantic tokens (kept from v1; MUST pair with a shape, glyph or word)"
**Add** a ring-board token table (to land in `Palette` at fold time):

| Token | Hex | The one meaning | Paired with |
|---|---|---|---|
| `SOAK` | #3A7EF3 | Your soak choice | Blue hatch plus a 5 px chevron notch; funnel |
| `TRACE_VIOLET` | #A03CFF | Trace, only | Square r3 pip; the card +Trace tab |
| `BOSS_GOLD` | #D69A1A (2026-11-03 re-pick: #FFC428 was dE76 11.4 from `CRT_AMBER` and 11.3 from `RESIST_GOLD`, under the 15 floor) | The Adjuster (boss) and its ward | Gold cell edge, lozenge |
| `PLAN` (= `PENCIL_PLAN`) | #FFE200 | Your plan or preview (hover only, never in resolve) | Grease pencil, arrowed outline |
| `COLD_HARM` | #D9877C | A harm mark for turn +1 | One turn pip |
| `FAR_HARM` | #96767A | A harm mark for turn +2 and later | Two turn pips |
| `ENAMEL` | #D9E1EA | Neutral enemy structure (no meaning) | Hairline |
| `CREAM` (`CREAM_FADED`) | #FFF4D6 | HP ticks of hover-faded units only (p2b); the board's HP ticks are `CREAM_HP` | Vector tick |
| `CREAM_HP` | #DBD1B7 (2026-11-04, gate 1) | Enemy HP ticks on the board: CREAM at the E mark value, L* 84, under the HOT marks and the tower | Vector tick |
| `K_TYPE` | #CBD2DB (2026-11-04, gate 1) | K type: sector digits, ring tags, W tags and ticket glyphs, nowords tallies; L* 84, no glow | Engraved / stamped type |
| `HIT_PAPER` | #DED8CA (2026-11-04, gate 1) | The gun hit star fill and the tracer highlight (was #FBFAF4, L* 98); L* 86 | Starburst with ink keyline |
| `CLOCK` / `CLOCK_LIGHT` / `CLOCK_GROOVE` | #6E7580 (L* 49.0) / #969EAA (L* 64.8) / #282C34 (L* 17.9) (2026-11-03, review 2.9; VISUAL_PLAN A.4; target median L* 45-55) | The clock: one gunmetal material for every corp (the engraved band, its cells, the lip and groove, the Hold stamp). The silver `TAPE_LO` / `TAPE_HI` tape is retired | Engraved band, ink keyline |
| `SCHEDULE` | #FF8C1A (L* 69.5) | The clock's **live step only**: its cell edge, a soft glow under it, its chevrons, and the clock's own motion (rings step, Hold's slide); plus the W6 climax ticket's three hazard ticks (VISUAL_PLAN F) | The live cell, chevrons, hazard ticks |
| `P_STOCK` | #F6C8DE (L* 85.1; shade #D696B8) | The FX-P plate stock: block plate, clamp brackets, sparks, the broken-shield shards (review 3.10). Never the card bone `PAPER` | Plate with ink key |
| `CARD_TOWER` | #006E66 deep teal, white text | Card type TOWER | Type plate, facets |
| `CARD_WAVE` | #B4AAFF lilac, ink text | Card type WAVE | Type plate, facets |

**Round 2 [R, calls C2, C3, C15]:** `P_STOCK` is a meaning token in `corp/src/rb_tokens.py` and is in the
VISUAL_PLAN E table, so check d tests it against every other ink (0 failures on the 15 board plates). A mark's
colour as drawn, measured on the plate, sits within dE76 3 of its token. Measured: `FOCUS` 0.0, pencil wax 0.5
(board) and 0.0-0.9 (hover), HOT fill 0.0-2.4, gun tracers 0.4, Adjuster track 0.0. Every drawn mark is dE76 15
or more from the skin's corp inks (closest 22.3). Two hover plate pairs fail this (h03 tracer 3.8, h11 HOT fill
54.7; open). The E line (cell outlines, lane rings, arc frames, ring-tag boxes, queue feed) is `ENAMEL`'s hue at
L* 80, and the K structure lines are capped at the `K_TYPE` value (L* 84).

Measured [M] (2026-11-03 rebuild, AD review 2.2; DR-5 / DR-8 keep one hue per type): each type hue and
the Spin 3 band sit at CIE76 dE 15 or more from SOAK, SCHEDULE, BOSS_GOLD, TRACE, NET_CYAN, HARM,
GAIN, PLAN and the four slice inks (table: `cards/NOTES.md`, "2026-11-03 rebuild"). TOWER white text
on teal 5.87:1, plate vs paper 5.30:1; WAVE ink text on lilac 8.94:1, plate vs paper 1.79:1 (the ink
keyline and drop carry that edge); TOWER vs WAVE in grey 2.96:1 (L* 41 vs 73). The O-29 cobalt
#2F5BFF / orange #FF8A1F were retired: they sat beside SOAK / SHIELD and on SCHEDULE.

**Note:** VISUAL_PLAN listed `SCHEDULE` #FF8C1A as "the rings move". On the rebuilt board the clock is
gunmetal and `SCHEDULE` is the live step (and the W6 climax ticks, as VISUAL_PLAN F gives them). Orange
is no longer the WAVE card (lilac) or Meridian's rim (container rust, `HAZ_DESAT` 0), so the W6 ticks
no longer share a colour with them; the 2026-11-02 question (old Q6) is answered by this.

### "### 2.3 Slice colours (kept)"
**Add**:
> **Ring-wheel combat spinner (designer, ART CALLs 52-53):** each slice type has its own spot ink,
> texture and grey value. This supersedes VISUAL_PLAN law 5 ("no slice-type colours") for the
> spinner.
>
> | Slice | Ink | Texture | Grey value (seat) |
> |---|---|---|---|
> | BURST | #F06EAE pink (texture #9E2A66) | big xerox dots | mid |
> | SHIELD | #5E9BE0 blue (texture #234E8C) | xerox scales | dark |
> | TURRET | #AEB24E olive (texture #5A5E1A) | Ben-Day bullseye rings centred on the icon | light |
> | REPAIR | #3FB59A green (texture #1D6656) | xerox plus crosses | light |
>
> Inks as of 2026-11-04 (`corp/src/rb_tokens.py` `SLICE_INK` / `SLICE_TEX`): the 2026-11-03 rebuild put the
> wedge inks at mean L* 60-72 (review 2.15; the icon discs carry the tower's peak), and gate 1 moved TURRET
> from #D6A33A to olive, because it sat at dE76 9.6 from `BOSS_GOLD` in the Adjuster's sector. Every slice
> ink is at dE76 15 or more from every meaning token, the light neutrals and the other slice inks (check d).
> The O-29 inks (#FF3DA8 / #2A58F0 / #FFD21F / #4BD67E) are retired.
>
> The four separate in grey by seat value as well as by texture. The xerox checker texture is
> retired, because it read as the loss hatch. Slice names are the game's (BURST, SHIELD, TURRET,
> REPAIR); the punk key's ZERO-DAY / SANDBOX / EXPLOIT / PATCH were agent labels and are not used.

### "### 2.4 Corporation palettes (LOCKED kits, round 18 values)"
**Already in the bible (2026-11-04):** the designer-ruling note for the combat enemy rings (DR-6): the corp
theme is carried by material and by the corp hue on the rim, bezel lip, crest and cell edges; cell fills stay a
neutral slate ladder with a low-chroma tint; the corp hue sits at ΔE 15 or more from Cell lime, GAIN, FOCUS and
HARM. Nothing more to fold here. How the rebuilt board meets it [M] (3.22.E has the detail):
> - Cell fills are the same neutral slate on every skin (`kind_gain` 1.0 on every ring of every skin).
> - Hue inks (round 2 [R, call C16, within DR-6]): Solace is the celadon / teal glaze family, teal #4FA6A2,
>   deep teal #2E7F7E, teal highlight #6FC2BC and glaze #B8DCCC (it was leaf #96FF46 / leaf_deep #4FA83A, which
>   sat at dE76 20.4 from the hub HP ring green); Meridian container rust #B0602C / #D88A4E; neutral steel.
>   Solace's secondary pink is not a hue ink on the board, so pink stays the player's. Green on the board is
>   `GAIN` and the player's HP ring only. Measured: the Solace rim as drawn (r 491-498) has median #3B827F,
>   dE76 61.3 from `GAIN` and 53.4 from the hub HP green (gate 25 or more).
> - **The 2.4 note's "material and hue" is measured (round 2 [R, call C18]):** the two corp rims differ in
>   luma as well as hue. Rim band mean L* is 48.4 on Solace and 25.1 on Meridian. Solace is a twisted rope at
>   52 cycles per turn and 5.4 L* amplitude; Meridian is hazard stripes at 18 cycles and 1.6 L*. The unwrapped
>   rims are at the foot of `final/grey_proof.jpg`. So the note stands as written.
> - Meridian's rim stripes and outer lip are container rust, off `SCHEDULE`, and kept clear of every amber game mark.

### "### 2.9 Typography"
**Add** after the table:
> - **Punk print card titles (ring-wheel combat, designer ART CALL 52.1):** white fill on an ink plate
>   with a 1.4 px ink keyline and one hard pink offset (never the only edge). Never yellow or pink
>   letters. Anton 38 design px, capitals, tracking 1.0, rotation -2 deg, no skew, glow or gradient.
>   Cap height at least 30 screen px at hand scale (measured 35.9 px at 1.10x; FIREWALL 32.4) [M].
>   Rules text IBM Plex Sans Condensed Medium 21 design px, never shrunk (a long line wraps to two),
>   ink on cream: cap height 16.2 px at the 1.10x hand scale, over the 16 px floor of check c [M].
>   Cost digit Anton 27 on the cyan hex; type word Anton 19; NO RAM Anton 17 (16.1 px cap).

### "### 2.10 Focus and state colours in chrome"
**Add**:
> - **Board focus (ring-wheel combat):** board cells and slices take `FOCUS` lime **corners only**:
>   12 px legs, 2 px for a legal target, 3.5 px for the aimed one, never a full outline. A corner
>   slides up to 12 deg inward if it would touch a digit, label, tag, badge or ticket, and is never
>   dropped. Chrome keeps the 3 px / 7 px brackets above.
> - **One FOCUS drawer (round 2 [R, call C2]):** board and hover draw the corners with the same code
>   (`corp/src/rb_focus.py`): four separate corners, never joined into a bar. Measured: dE76 0.0 from #D4FF00 on
>   all 26 hover plates and on the board p2b plates (276 px each, L* 94.1); 0 px of the old #96FE46. **Open:**
>   drawn at its token, FOCUS reads L* 94.1, so it cannot also sit 1 L* under the HOT p95 (92.2-96.0 on the
>   hover plates). That is reported, not gated, until the designer rules (an exception for FOCUS, or a darker
>   token).

---

## 3. Combat

### "### 3.1 The screen (LOCKED layout, round 31 / round 43 HUD v4)"
**Add** at the top:
> This section and 3.2-3.21 describe the **two-wheel D4 combat**. The ring-wheel combat (Shifting
> Waves) is in 3.22, which overrides them on that screen.

### "### 3.14 Combat backdrop (LOCKED)"
**Already in the bible (2026-11-04):** the designer-ruling note on the room (DR-9): Site and HQ-run fights show the
cutaway room; the boss fight keeps the perspective close-up. **Add** after that note (the grade, rb2-1; it supersedes
the step-6 grade and its squint acceptance of the 2026-11-02 draft, which made the room too dark to read, mean L* 21):
> - **Ring-wheel combat grade (rb2-1, `backdrop/grade.json`, `corp/src/bd_grade.py`) [M]:** one full-screen post on the
>   room layer, under the board, on sRGB-encoded values, in the grade.json `order`: the focus hull follows the cutaway
>   box (a polygon, feathered in and out); one blur ramp runs across the hull edge, not a cross-fade; a corp light
>   (only where a room sets it); chroma, with the neon and player-pink pulls and the city keeping part of its chroma;
>   contrast about a pivot; hull and city value; a local tone that takes its gain from the local mean luma, capped;
>   a luma shoulder whose ceiling is solved per room; a haze ramp from the room to the city in the room's own key
>   light, then the night haze; the vignette and the falloff toward the board side. Every value is per room in
>   `grade.json` and goes to config; GODOT_PORT_SPEC.md 4.1 and its Appendix C carry them, generated.
> - **Pink belongs to the player:** magenta-to-rose room hues lose chroma (the pink pull). The violet night city is
>   left alone.
> - **Seam:** where the city meets the room there is one blur ramp, the city's chroma is calmed, and the room's light
>   is carried into the haze. The neighbouring facades read as one lit street, not as a second picture.
> - **Rooms per skin:** neutral and Solace fight in the bio lab. Meridian fights in the shop (the only kit room with
>   no Solace sign), with the shop's lime light pulled to an amber corp light.
> - The board scrim stays: a 6 px frosted pool plus `SCRIM` #02030A, as grade.json's last step gives it.
> - **Acceptance (per plate, rb_checks b, L* of mean luminance):** in the room region (x ≥ 1100, y ≥ 420, r > 505,
>   with the HUD, hand, buttons, nameplate, hover tag and the UI scrim slabs, where they darken the room by 15 % or
>   more, cut out) the mean L* is 28-34 and the p95 is at least 1 below the ring-NOW occupied glass p95 (L* 40 when
>   no ring-NOW cell is live). Measured on the 9 backdrop plates: mean L* 31.8-32.5, p95 L* 38.1, all pass; all 15
>   final plates pass rb b [M]. **Round 2 [R, call C9]:** the gate is on the room itself; the room as seen, UI scrim
>   kept, is reported and accepted, with no scrim change. Measured on the round-2 plates: backdrop room 31.6-32.4,
>   p95 37.8-38.0, as seen 28.65-29.30 (both gated 28-34 on these p1 plates); board room 31.0-32.1, as seen
>   22.9-28.9 (p2 25.3-25.4, p3 22.9-23.1; reported). The grade is unchanged (rb2-1).

### "### 3.17 Card-play preview (LOCKED, animated, round 17)"
**Add** at the top:
> D4 wheels only. The ring-wheel combat previews through hover (3.22.G): no dashed ghosts, no ghost
> blades.

### "### 3.18 Sticker cards (LOCKED)"
**Add** at the top:
> D4 combat. Ring-wheel combat cards are the WPAP punk print card of 3.22.D (designer, ART CALL 53).
> The WPAP card has its own states (3.22.D: rest, hover lift, played liner, unaffordable, nowords) and
> does not take the sticker peel, slap and dissolve-A motion [AP; the designer can overrule. The
> 2026-11-02 question, old Q5, is closed by this call].

### "### 3.20 Damage shards and combat FX (LOCKED list)"
**Add** at the top:
> D4 combat. Ring-wheel combat effects follow the eight families of 3.22.F; bits are kept there for
> the T5 / T6 transitions.

### "### 3.22 Ring-wheel combat: Shifting Waves "converged" look (LOCKED as front runner, designer 2026-10-28)"
**Replace the whole section** with the text below. The old body moves to the changelog as
superseded. Kept from it: one board, top-down concentric rings, rings radially aligned with the
slices, spinner only (PL7, no table restates the sectors), the bill column, the rail rule (bezel
text at least 16 px), and the "never add or drop a number or word" content guard.

> ### 3.22 Ring-wheel combat: the locked punk board (designer ART CALLs 51-53 and rulings DR-1..DR-10; art-pass defaults O-27 to O-29; rebuilt 2026-11-03 / 2026-11-04)
> Reference: `combat_redesign/locked/final/` (p1_decide, p2_preview, p2b_hover, p3_resolve,
> p1_nowords, the Solace and Meridian plates, card_sheet, grey_proof, grammar_check);
> `locked/hover/`, `locked/effects/`, `locked/backdrop/`, `locked/transitions/`. Rulebook:
> `combat_redesign/VISUAL_PLAN.md` (R51), with the changes listed here.
>
> **Laws.**
> 1. Every element belongs to one family (player, corp, threat, clock, plan, effects, system), told
>    by **material and line**, not by colour alone. In greyscale the player's things, the corp's, the
>    clock and the HUD stay apart.
> 2. A line type has one meaning. **No dashed lines on the combat screen** [D].
> 3. This END TURN is HOT; future turns are COLD or FAR [D/AP].
> 4. Cross-hatch means **HP lost at this END TURN**; the hatch colour is the cause [D/AP].
> 5. Colour means a cause or an owner. An outline with no meaning is neutral enamel.
> 6. **No needle** [D]. Only the game information is fixed: never add or drop a number, word or count.
>
> #### 3.22.A Geometry (1080p, centre (536, 540), angle 0 = 12 o'clock, clockwise) [M]
> | Element | Radius (px) |
> |---|---|
> | Tower (spinner) | 0-196 (threat trim 200-210) |
> | Player HP ring | wraps the hub at r 52-64: 15 segments in 3 groups of 5 |
> | Ring NOW / +1 / +2 | 214-271 / 271-328 / 328-385 |
> | Schedule band (the gunmetal clock) | 391-417; marks stay inside 388 |
> | Landing lanes | 436, 453, 470 |
> | Rim | 489-500 |
> | Hand | outside 455 at every pixel (asserted) |
>
> - Sector digits 0-5 sit on their own top layer, above cells, the band, plates and tags. Digit 0 is at
>   -4.5 deg, clear of the band start. Every digit punches a 2.6 px hole through the band, plate and
>   label layers.
> - The bill, objectives and RAM / Trace terminal sit top right; the hand bottom right with UNDO and
>   SEND IT; CELL-9 bottom left; the wave queue top left.
>
> #### 3.22.B Visual grammar
> **Time: HOT / COLD / FAR** [D/AP; measured on every skin].
>
> | When | Look | Turn mark |
> |---|---|---|
> | **HOT**, this END TURN (ring NOW) | Solid fill, full value and chroma, Bold tier, glow at most 35 % over 4-6 px | END notch: a solid 8x8 px wedge on the tower-facing end; the live schedule cell reads THIS TURN |
> | **COLD**, turn +1 (ring +1) | Solid, one tier thinner, 70 % value, 45 % chroma; harm marks `COLD_HARM` #D9877C; cell glass at 80 % value | One turn pip (6 px round, `TEXT_MID`) at the start cap, never on the line |
> | **FAR**, turn +2 and later (ring +2) | 50 % value, 25 % chroma; harm marks `FAR_HARM` #96767A (lifted so they survive Meridian brown); cell glass at 62 % value; structure is a solid 50 % hairline | Two turn pips |
>
> - Value order HOT > COLD > FAR holds on every skin (rb b, all 15 plates). On the rebuilt board check d
>   holds every HOT / COLD mark at dE76 15 or more from the measured cell colours (lowest pair of all
>   groups, all plates: 17.3) [M]. The 2026-11-02 luma / dE2000 table is retired with that board.
> - **Bright marks (round 2 [R, calls C3, C4]):** every board pixel inside r 480 at L* 80 or more belongs to a
>   classed mark, and each class keeps its p99 at least 1 under the HOT p95. E and K classes also keep their
>   p95 at least 1 under the tower p95, and token discs are tested per disc. An unclassed bright pixel fails the
>   plate. Thin structure lines are drawn at the K type value and reduced from 2x with a box filter. Measured:
>   0 unclassed bright pixels on every board and hover plate; the highest other-class p99 on a HOT plate is
>   92.7, against a HOT p95 of 94.9-95.4; token discs read p95 82.6-84.4 and p99 85.4-91.0. Value chain, p1
>   neutral (p95): SEND IT 98.2 > HOT 94.9 > tower 89.5 > hand 83.1 > token discs 82.6 > clock 69.5 > occupied
>   glass 45.5 > room 37.8 > empty glass 21.0 [M].
> - **HOT core (round 2 [R, call C11]):** HOT is carried by its white-hot core: 3 px or more at 1x, and 4.5:1
>   or more against the ring-NOW occupied glass. The fill ratio is reported only. Measured: core 3.0 px at
>   L* 94.0, 4.92-5.01:1; fill 1.93-1.97:1. **Open:** small side-arc marks read 2.0-2.5 px where their lane
>   line crosses them (4 per p1 / nowords plate, 2 per p2 / p3 plate).
> - One HOT mass per family: threat has the NOW chevrons and diamonds, the clock has the live step
>   cell, the player has the pending hatch. Nothing in the future is HOT. In resolve (p3) HOT marks lose
>   their glow.
> - **Hollow means growth only on chevrons:** solid chevron = a hit, hollow chevron = growth still to
>   come. Any other +1 mark is COLD, never hollow.
> - The bill's main rows are HOT; the NEXT row is COLD with one turn pip.
> - **Bill numbers (2026-11-03 stage 2, review 1.5 / 3.7):** each number is an Anton digit (24, or 22
>   on NEXT) followed by a small pip tally as a second mark. The operators are typeset Anton 40 (−, +, =).
>   SPLIT is a written sum, ABSORBED + SOAK + YOU. NEXT is a COLD digit plus a filled COLD tally at
>   70 % value and 45 % chroma (never hollow). WITHOUT TWIST shows digits. Heat is the atlas Heat glyph
>   in `CRT_AMBER`. The REFUND word is a HUD tab under the RAM coin it returns, never on the wheel.
> - **No dotted marks** [AP, gated]: VISUAL_PLAN B still lists L8 dotted for the +2 threat trim, but no
>   plate draws one: 0 dotted calls and 0 pixel dot runs on every plate (the O-30 dot audit, part of the
>   plate gate `all_pass`), and both effects designers treat dotted as banned. FAR is value plus two pips.
>   (The 2026-11-02 question, old Q7, is closed by the gate. Round-2 docs pass: VISUAL_PLAN B now carries a
>   dated note that the plates draw no L8, and it keeps the L8 row for the designer to rule on.)
>
> **Cross-hatch = HP lost at this END TURN** [D/AP].
> - Two directions (45 and 135 deg), 2 px lines at a 5 px pitch, clipped to the shape, with a solid
>   2 px edge in the same colour and an **ink keyline under every hatch line** (red vs ink 5.7:1).
> - On a segment under 9 px: one direction, 1.6 px lines at a 4 px pitch, and the pending segment
>   bulges 2 px. Two-direction hatch only on segments 12 px or wider. If it closes up at 320 px, widen
>   the pitch; never drop it.
> - **YOU strip (2026-11-03 stage 2, review 3.14):** segments are 13.6 x 22 px at a 16.4 px pitch, with
>   an 8 px group gap. The pending hatch is two-direction, 1.5 px lines at a 5.4 px pitch, inside a
>   1.4 px HARM edge, so it reads at 1x.
> - **Hatch colour = cause:** `HARM` red = the enemy takes it; `SOAK` blue (plus a chevron notch) = your
>   soak spends it; `CELL_PINK` = we take it (enemy HP). Hatch swatches on each skin's own cell
>   (neutral / Solace / Meridian): red 2.9 / 2.6 / 2.9:1, pink 3.0 / 2.8 / 3.0:1, blue 2.6 / 2.4 / 2.5:1 [M].
> - **O-28:** on a hatched slice the texture vanishes, so a solid slice-ink seat ring round the icon
>   carries the type. The hatch stops at r 37 round the icon.
> - Cross-hatch is used for nothing else: the Trace cap is a padlock, a broken slice is a black-out,
>   an unaffordable card is dim glass, and P shading is single-direction only.
> - Other HP states (VISUAL_PLAN D): lit, COLD future loss (a filled COLD segment or tally at 70 %
>   value and 45 % chroma in the cause colour, plus a pip; never hollow, since hollow means growth on
>   chevrons only; the 2026-11-02 hollow 1.5 px outline is retired), mend pending (GAIN outline with a 7 px plus), gone (dark socket #0E1016, solid
>   1.4 px hairline #3A4150), blocked (segment stays lit behind a protect plate). The E10 white slash is
>   retired.
>
> **Arrowed outline = movement only** [D, ART CALL 51.4].
> - A 16 px channel, two 3 px edges, inner chevrons 10 px at a 24 px pitch, a 22 px arrowhead.
> - Kept [D, DR-1]. Colour by who moves the thing (VISUAL_PLAN E, R51): `PLAN` yellow in hover (the
>   plan); `CELL_PINK` in resolve for a card (Spin, Nudge, Twist, Pull, Shove, the bump, the commit
>   ping); `SCHEDULE` for the clock (rings step, Hold's slide), with the Hold stamp in the clock's
>   gunmetal; neutral `ENAMEL` for the wave feed and the queue feed arrow. The corp hue moves only as
>   the `fx_wave_enter` scan line that draws the new cell edges (DR-6). Yellow never appears in resolve.
> - Used by: the hover route, the Trigger path, the live schedule cell, Twist, Spin ghost, Shove,
>   Pull, the wave-queue feed. The M effects' own resolve arrow is thinner and a stub (3.22.F).
>
> **Enemy outline** [D, ART CALL 51.5].
> - One enamel hairline for every enemy cell on every ring: no lane colours, no slice-type outline
>   colours. In the neutral skin it is graphite enamel; a corp skin may tint the frame material, never
>   by ring.
> - The NOW cell outline is Bold with glow and the END notch; +1 thinner with one pip; +2 a solid
>   50 % hairline with two pips.
> - `BOSS_GOLD` is the one coloured enemy outline (2.5 px): gold means the Adjuster.
> - A hovered unit gets FOCUS corners and the pencil route; its outline does not change colour.
>
> **No dashes, no needle** [D].
> - 0 dash calls and 0 dotted-mark calls on every plate (audited per draw call). Every E10 dashed use
>   is remapped per VISUAL_PLAN B (gun tracers become a pink painted stroke, ghosts a 74 % copy plus
>   the arrowed outline, played-card slots a solid liner, landing lanes removed...).
> - Watch for accidental dots: the pixel dot-run audit (O-30) runs on the rendered pixels of every
>   plate and gates at 0 runs [M]; thin 1 px lips are where dots appear first, so band edges are a
>   solid ink keyline.
> - No needle or 12 o'clock marker. The clock's band starts at 12 o'clock and digit 0 sits beside it.
>
> **W4+ wave tickets** [D, ART CALL 51.6; AP layout].
> - Three tickets in the top-left corner, FAR to near, left to right: W6, W5, W4. Each is 84x70 px with
>   a Mono 23 tag, unit kind glyphs in a 27 px box (23-27 px of ink) and 1-3 width bars per unit; tag,
>   glyphs and bars at full value (2026-11-03 stage 2, review 2.14).
> - Solid edges. Time is shown by the edge value (W6 50 %, W5 70 %, W4 100 %) and pips, never by a
>   dotted edge, and never by dimming the glyphs. **Round 2 [R, call C5]:** each step is 5 L* or more on the
>   plate. Edge p90, W6 / W5 / W4: 49.7 / 63.2 / 82.2 (neutral), 46.4 / 58.4 / 75.0 (Solace), 41.4 / 51.6 / 66.1
>   (Meridian) [M]. Glyph ink is 23-25 px, p90 L* 86.3-87.8.
> - The W6 climax ticket has a cut corner and three hazard ticks. The ticks sit in the ticket's top row
>   between the W tag and the turn pips, clear of the bomb glyph's width pips (round 2, call C5: ticket
>   x 60.0-78.5 inside the free span 57.0-81.4).
> - One neutral-enamel arrowed feed runs from W4 to the board edge.
> - `WAVES 6 LEFT` stays in the header, and that is the only place the count shows (no header pips on
>   the words plates; nowords keeps the pips). Ticket material comes from the corp skin (`ticket`).
>
> #### 3.22.C Player family: the spinner (designer ART CALL 53; xerox A + linocut key and halo + Ben-Day shapes)
> - **Halo:** a pink scissor-cut sticker edge round the whole spinner with black chisel nicks. It is a
>   silhouette cue, not a type cue.
> - **Page:** a black key ring, then the paper disc with toner speckle, at 0.76 value (`PAGE_V`).
> - **Slice:** a scissor-cut wedge with a black key line (3 px) plus a block drop and a paper keyline.
>   Spot ink is printed 2.8 px off register (a paper sliver on one side, ink over the key on the
>   other), with a stencil highlight. Inks and textures as in 2.3. Wedge ink at 84 % value (`FILL_K`);
>   O-28 seats keep full ink.
> - **Icon seat (O-28):** a solid slice-ink disc, a paper scissor ring and a black key ring on every
>   slice. **Icon:** a white stencil glyph with a black key line and drop. Icons are re-inked, never
>   redesigned (one turret stays a turret).
> - **Hub:** a pink starburst off register, black key, paper disc, bolt, one clean black name tile
>   (no ransom letters; nowords shows the bolt only).
> - **Same hand elsewhere:** the nameplate, the YOU strip taped onto the terminal (HP cells, hatch =
>   pending loss), SEND IT as a pink slab with toner halftone and white lettering with a black edge,
>   UNDO as a paper tab with a black keycap. The terminal hint line stays system text.
> - **Caps:** no glow on the player family. Decoration never crosses a ring cell, landing arc or threat
>   mark. Texture contrast inside a slice is at most 18 % of the icon's, and no texture sits within
>   6 px of an icon or HP segment.
> - **Loudness knobs** [M]: halo value x0.90 (`HALO_K`), texture x0.90 (`TEX_K`). On the rebuilt board
>   the tower-zone loud share (squint, loud above 0.38) is p1 59.3 %, p2 68.7 %, p2b 57.0 %, p3 68.0-68.2 %,
>   nowords 59.9 % (`final/checks.json` `squint_tower_zone`, round 2), over the O-29 fix-9 target of 50 %, while
>   the tower's value order holds (rb b, every plate). It is reported, not gated [R, call C10: the value gate
>   governs the tower; no texture rework]. Which governs the tower, the squint share or the ink value order,
>   stays open to the designer (VISUAL_PLAN A.1; Q2 below).
>
> #### 3.22.D Player family: WPAP cards (designer ART CALL 53)
> - **Frame:** a chamfered die-cut WPAP card on the black-book layout, flat facet planes, slanted
>   plates, hard offset drops.
> - **Facets:** two planes in the type colour at 32 %, two in the type's dark at 28 %, one white glint
>   plane at 25 %, each with a 0.7 px ink cut edge (brief 25-35 %).
> - **Type colour** (the plate under the title, a thin rule on the title plate, the corner facet, the
>   facets): TOWER deep teal #006E66 with white text; WAVE lilac #B4AAFF with ink text (2026-11-03,
>   dE 15 or more from every meaning token and slice ink). The state has only these two types; do not
>   invent more. Violet stays the +Trace tab only.
> - **Band art** draws on the other punk styles, one per card (DR-8): Ben-Day (Nudge sky, Spin 2 mint,
>   Spin 3 magenta #FF00F0, with 1 / 2 / 3 solid ink arcs and Ben-Day density 0.55 / 0.85 / 1.15),
>   linocut (Brace, Pull), collage (Strike, Shove), mural (Firewall: a brick wall on fire; Twist: three
>   ring bands with the middle one turned), xerox (Hold), Jinx (Trigger). Every card has its own motif.
>   Arcs, bolts and bars on bands are decoration, not data.
> - **Icon (xerox, recoloured):** a paper-white glyph with a 2.5 px key line and hard black drop on a
>   spot-ink disc with a misprinted second-ink crescent, a black ring, then a white scissor halo with
>   an ink drop. Disc vs the art round it at least 2.5:1 (measured 2.53-6.41) [M]. Brace, Firewall,
>   Pull, Shove and Twist use ink discs with pink in the crescent; Trigger and Hold pink discs (Hold with
>   a black toner pool).
> - **Cost** stays a system resource: cyan hex, Anton digit. **+Trace** tab in `TRACE_VIOLET`.
> - **States:** normal (resting hand at 88 % value); hover (round 2 [R, call C6]: the card lifts straight up
>   out of its slot at the hand scale, 1.00x, with its pink misregistered print and hard drop to the right; the
>   fan keeps its slots and never closes, and only the cards right of the lifted one open; until round 2 it
>   was 1.10x with the hand pushed right 16 px); played (2026-11-03 stage 2, review 2.3: a flat, upright torn
>   dark-paper liner with a paper rim and fibre edge, no fan angle and no perspective cage; the ghost
>   glyph at 46 % paper value; the card name over PLAYED in Mono 21 at 62 / 74 % paper value); unaffordable (dim glass, value x0.5, chroma x0.4, two flat
>   glass planes, never hatch, plus at full value the cost badge, a padlock on it and a "NO RAM" tab;
>   nowords keeps the padlock only); nowords (bars and tallies, glyph and art kept).
> - **Hand:** cards at 1.10x, step 168, no pixel inside r 455 (measured 457.7 on all 15 stage-2 plates). The corner
>   may cover the rim between r 455 and r 500. **2026-11-03 stage 2 (review 2.7):** the whole hand is
>   on screen, with its lowest pixel at least 12 px above y = 1080 (left card centred at x 1035, base
>   y 904, fan 4 deg; the lifted card centred at y 812, neighbours pushed 16 px). Rules text wraps to
>   two lines at a word break, never shrinks (Plex Condensed 21, cap height 16.2 px at 1.10x). When the lifted card is in slot 0, the fan slides right 32 px and
>   the lift drops 40 px.
> - **The lift (round 2 [R, call C6], the reviewer's option (a); it replaces the y 812, push-16 and slot-0
>   lines above):** one lift for board and hover (`corp/src/rb_lift.py`). The lifted card rises straight up to
>   centre y 718 (slots 1-3). The cards right of it open 30 px on board p2 and 36 px on the hover plates. The
>   UNDO / SEND IT column moves right 12 px on the board plates and 16 px on the hover plates, so the buttons
>   move 4 px when a hover starts (open). Every sibling's protected set (cost hex, title band, rules line, ×N
>   plate) has 0 px under the lifted card, gated (rb e). On board p2 this fits under the HUD only with the 1.00x
>   lift, the print and drop to the right, 4 px HUD panel gaps and a 96 px REFUND tab. Measured: 0 px on board
>   p2 and 22 of 26 hover plates; hand min r 457.7 (board) and 456.9 (hover); lowest hand pixel 12 px above
>   y 1080 (15 on p3), 1064-1067 on hover. **Not met on h02 x4 (Brace, slot 0):** at the only lift height that
>   keeps the card outside r 459 (y 906), Spin 3's cost hex is 166 px covered and its title band 208 px. The
>   options are for the designer (VISUAL_PLAN H).
>
> #### 3.22.E Corp skins (designer ruling DR-6, the ART_BIBLE 2.4 note; ART CALL 53)
> - **Material, plus the corp hue on the rim, bezel lip, crest and cell edges only** [D, DR-6], built as
>   data (one `CorpSkin` per corp), so a corp swap is a skin swap. The cell fills are the same neutral
>   slate on every skin. The neutral skin is clean graphite enamel. Solace: membrane-pattern glass cells,
>   a helix rim (round 2: a long-lay teal rope [R, calls C16, C18]), a porcelain roundel. Meridian: corrugated steel cells, octagonal container token frames,
>   a container-rust striped rim, crane crests, shipping-tag tickets. A colour-only skin is rejected: Meridian read as the old
>   slate, and Solace's flat green fought the pink player.
> - **Skin inks are checked like tokens (2026-11-04, gate 1):** every skin ink sits at CIE76 dE 15 or more
>   from every meaning token and from the light neutrals `PAPER`, `ENAMEL`, `TEXT_HI` and `TEXT_MID`. Solace's
>   porcelain moved from #E6EFE4 (dE 4.7 from `PAPER`, the player's paper) to a celadon glaze #B8DCCC.
> - **What a skin may change:** the cell material (low-chroma tint only), bezel, landing annulus, arc
>   frames, rim, crests, token and disc frames, tickets, optional empty-cell marks, and the C-family
>   scan-line ink. **What it may never touch:** the clock, the cell fills, HP, the hatch, HOT/COLD/FAR
>   marks, threat marks, outline meaning, hover and plan marks, the player family.
> - **One gunmetal clock for every corp** (VISUAL_PLAN A.4, review 2.9): the band, its cells, the lip
>   and the groove in `CLOCK` / `CLOCK_LIGHT` / `CLOCK_GROOVE`, `SCHEDULE` on the live step only; HOLD
>   amber and plan yellow are untouched. The band edge is the solid ink keyline. Clock pixels match the
>   neutral plate on 96.9 % (Solace) and 97.3 % (Meridian) on the round-2 plates (97.0 / 97.4 % at gate 1);
>   the rest are units overlapping the band [M].
>   The silver THIS TURN tape (`TAPE_LO`..`TAPE_HI` remap) is retired.
> - **Pink is the player's:** no enemy glyph, skin or effect is pink. Enemy-zone pink on the rebuilt
>   board is 1.38-1.39 % on the three skins (round 2; 0.23 % on the 2026-11-02 board); it is reported, not gated, and its
>   sources are not yet broken down (Q4 below) [M].
> - **Kind separation:** the corp tint must not collapse unit kinds. The fills are one neutral slate per
>   kind and ring on every skin, and `kind_gain` is 1.0 everywhere (the 2026-11-02 per-skin push,
>   Solace 2.4 / 2.1 / 2.0 and Meridian 1.0 / 1.1 / 1.2, is retired with DR-6). Plate read-back,
>   dE2000 (`final/checks.json` `corp`): Packet 1 vs Worm 2 on ring 0 25.5-25.7, Packet 1 vs Worm 3 on
>   ring 0 13.2-13.7, Payload 4 vs Packet 5 on ring 1 9.2-9.5 over the three skins [M]. The **kind
>   glyph carries kind**; the wash is the second channel.
> - **Skin inks are cell edges, rim, lip and crest only**, at ΔE 15 or more from Cell lime, GAIN, FOCUS
>   and HARM (DR-6) and dE76 15 or more from every meaning token (check d) [M]: Solace teal #4FA6A2, deep
>   teal #2E7F7E, teal highlight #6FC2BC, glaze #B8DCCC (round 2 [R, call C16]; the leaf #96FF46 / #4FA83A
>   pair is retired); Meridian rust #B0602C, rust_hi #D88A4E; neutral steel. **Gate (round 2):** the rim as
>   drawn is dE76 25 or more from `GAIN` and from the hub HP ring green; measured 61.3 / 53.4 (median), 51.0 /
>   44.1 (modal). The board, hover, backdrop and transitions plates show the teal; the effects set does not
>   (3.22.F).
> - **Corp marks never mimic game marks:** Meridian's rim stripes and outer lip are container rust
>   (`HAZ_DESAT` 0, off `SCHEDULE`), and the inner bezel lip is black, so amber game marks (HOLD, the
>   Adjuster arc) keep a gap from the rust (37 px measured on the 2026-11-02 board, not re-measured on
>   the rebuilt one) [M]. FAR harm is lifted so it reads on oxide brown.
> - Skin data format and hooks: `GODOT_PORT_SPEC.md` section 7 and Appendix B (generated from
>   `port/skin_tables.json`), `locked/corp/NOTES.md` and `locked/final/NOTES.md` ("Skin hooks").
>
> #### 3.22.F Effect families and flash limits (designer ART CALL 51.7; roadmap step 4; rebuilt 2026-11-03)
> Every event is one overlay on its footprint: a slice (the wedge or its trim band), a cell, an arc, a ring,
> or a path from the rim to the HUD. Each family has its own material so it never reads as another family or
> as a skin (`effects/NOTES_CDHL.md`, `NOTES_MPST.md`; the full list is VISUAL_PLAN G, rewritten 2026-11-04).
> **Round-2 status:** the published effects are the 2026-11-03 rebuild, rendered on the gate-1 board. They
> were **not** re-rendered on the round-2 board, so their bases show the board before calls C1, C5, C8 and C16
> (on Solace, `fx_wave_enter`'s scan line is the old leaf #96FF46). The call C12 skip hint is not published.
> The block-vs-break comparison copy throws white sparks where the real P block throws P-stock ones.
>
> | Family | Means | Material | Effects |
> |---|---|---|---|
> | **C corp** | The enemy changes state | One clean 1.6 px vector scan line with a 1 px ink key, in the skin's own enamel ink (neutral `ENAMEL` #D9E1EA, Solace celadon #B8DCCC, Meridian rust #D88A4E); then one flat 4-frame flash on the new mark only; ward in `BOSS_GOLD`. No slab, no texture, no trail; never pink, never the clock's colours. The 2026-11-02 shutter slab and its lips are retired | grow, ward_on |
> | **D damage** | We hurt them | Player pink, the comic hit frame: a painted tapered tracer ribbon with an ink key, an ink-keyed `CELL_PINK` starburst with a white core (`HIT_PAPER` star fill on gun hits), converging white speed lines cut at the tower rim, flat vector shards; kills in the cause colour; no Ben-Day | gun_hit, strike, trigger_hit, kill, ricochet (+ gold), firewall_burn, shove_bump |
> | **H harm** | The enemy hurts you | Misregistered red print: an X-only halftone flood (never round dots), black krackle with a 2 px red offset, a red stencil X; the broken shield is the P-stock plate in shards | hit_land (+ worm, Adjuster), shield_break, slice_crack, slice_break, hp_through |
> | **L life** | Gain | The only soft glow: brush strokes, plus signs, a painted check, four-point sparkles; `GAIN` on dark, mint with an ink key on the green REPAIR wedge; the RAM coin in `NET_CYAN`. Ranked with the state changes | refund, clear, repair_mend |
> | **M motion** | Things move | **No print echoes** (retired: on the shared meter they were the loudest light of every motion effect). One solid arrow in the owner's colour: a 3 px core, 2.5 px ink casing, 11 px open head; a stub on spin, twist, shove, rings step and Hold, eaten when the mover arrives | spin, twist, pull, shove, rings_step, hold, wave_enter |
> | **P protect** | Your defence holds | Everything on the **P stock** #F6C8DE (review 3.10), never the card bone `PAPER`: a small shield plate on the trim band, four clamp brackets for the brace, a small brace stamp, P-stock sparks. The flat wedge tint and the SOAK wash are retired (SOAK stays a mark: the funnel). No starburst, red or glow. The 2026-11-02 bone #F1EAD6 plate is retired | shield_block, brace_block, soak_take |
> | **S system** | Trace | A stepped violet glitch: one band shear per 33 ms step (4-7 px tall), R/B split, violet tint, scanlines | trace_add |
> | **T commit** | SEND IT / a Trigger resolves | Pencil yellow burns into pink paint front to back, with a narrow white-hot burn edge; a pink ping at the route end | commit |
>
> Rules for every effect:
> - Effects **never add cross-hatch**. They resolve the board's existing hatch into a gone socket or a
>   dark pip.
> - Slice-wide overlays keep the icon seat (r 37) clear, except where the effect fades the icon on
>   purpose (shield_break, slice_break). Never put an X, slash or glyph over the icon it describes.
> - No dashed or dotted lines: trails are one continuous tapered ribbon. No needle. The arrowed outline
>   appears only in M and T.
> - State changes are real before and after states from the generator, never painted.
> - **Layer** [R, REVIEW_RESPONSE 1.6]: every effect draws **under the HUD and the hand** (bible 6.4);
>   only `fx_hp_through`, `fx_refund` and `fx_trace_add`, which land on HUD rows, draw above the HUD.
> - **Length** [R, REVIEW_RESPONSE 2.11]: every effect is VfxTier T2, **0.6 s or less, with no per-effect
>   override** (bible 5.3 as written). Reduce forms are 0.6 s or less too.
> - **The resolve beat** [R, REVIEW_RESPONSE 2.11]: the effects of one END TURN play as **concurrent
>   tracks** in the HUD chain order (SEND IT, 1 TWIST, 2 TRIGGER, 4 GUNS, 3 BRACE + 5 LANDS, 6 RINGS
>   STEP, W4 enters), each at its own timing: **3.8 s against a 4 s limit; any input skips it** (a
>   0.2 s dissolve to the settled frame) [M]. The 2026-11-02 rule (sequenced, never two in one 100 ms
>   window) is retired. **Skip hint (round 2 [R, call C12]):** a "SKIP" key hint (Mono 23, cap height 16 px
>   or more) sits at the HUD edge for the length of the beat. It is **not published**: the published beat
>   has no on-screen word yet.
> - **Loudness order** [R, review 2.10]: damage > kill > block > state (gain ranks with state), measured
>   as the peak transient (sum of L*/100 over the pixels a frame changes, 60 fps) on every skin, with both
>   designers' sets on one meter: it holds on all three skins [M].
> - **Flash limit:** at most 3 flashes in any 1 s window, measured at 60 fps on WCAG relative luminance
>   (method in the effects notes). Every effect passes on every skin, full and reduce motion; the whole
>   resolve beat passes too (3 in any 1 s at the 60 px tile in full motion, the limit; 2 in reduce) [M].
>   The largest single event is the kill flare: 2 frames at 55 % on the token (under the 60 % local
>   flash of 5.3).
> - **Durations** [M]: every total, phase and reduce form per effect is in `timings_CDHL.json` and
>   `timings_MPST.json`, merged and generated into `port/fx_timings.json` (GODOT_PORT_SPEC.md Appendix A),
>   to go into `content/config/ui_motion.tres`.
> - **Reduce motion:** every effect has a still form. No travel, overshoot, sparks or glitch steps;
>   state changes are short dissolves; arrows, plates and stamps appear whole with a short fade.
> - **Transitions T5 / T6** tell the designer's story (VISUAL_PLAN DR-10: the wheel flies in, the enemy
>   rings fly from the iso room as bits; combat dissolves to bits back to the netrun, or a failed run
>   cuts to the netrun-failure screen, design A). They keep bits option A (O-25). Every bit follows 1.2:
>   it takes the colour of its source, read from the board pixel it becomes or leaves (the 90th
>   percentile of C*ab over a 9 px disc, L* held in 55-80); it is white-hot `HIT_PAPER` for its first
>   80 ms, flips every 70 ms and tumbles; it goes round the rim (orbit r 506-532 at 1080p) and only
>   moves radially inside it. The band keylines, ghosts and lock take their band's median bit colour;
>   the spinner keyline stays pink; ghosts are one solid hairline. T5 starts on the room as T4 leaves
>   it (the bare room) and dims to the plate's grade from K2 to the lock; T6 returns to it. 0
>   whole-frame flashes; worst 120 px tile 3 in any 1 s, the limit (CIE L*, both skins) [M].
>   **Round 2 [R, call C13]:** the bits over the dark city are thinned until the worst 120 px tile flashes
>   2 or fewer times in any 1 s. A ring, spinner or ticket bit d degrees round the rim from the lab is kept
>   with p = near - (near - far) * clamp((d - 90) / 90): T5 near 100 % and far 50 %, T6 near 45 % and far
>   25 %. Card bits are not thinned. Measured on the renders and the decoded GIFs, both skins: worst tile 2
>   in T5 and T6, WCAG count 0. No T6 pull-out variant stayed within that, so T6 holds on the bare room
>   (call C13); the hand-over from the room to the netrun street is open. The bits keep their source's hue
>   (drawn vs plate hue dE76 median 0.00-0.42 per stream).
>
> #### 3.22.G Hover and dimming (designer ART CALL 51.9)
> - **Keep the hover dimming:** everything the card does not touch drops to value x0.40 and chroma
>   x0.45. The resting hand is at 70 %; UNDO, SEND IT and the nameplate at 62 %.
> - The hovered card lifts (WPAP hover state). Its result is drawn in the plan family: grease-pencil
>   marks, the yellow arrowed outline for any motion, ghosts at 74 % with a pencil outline (the origin
>   veiled), a pencil ring on every number the plan changes (LANDS, THROUGH, YOU pips, spent RAM, added
>   Trace), the board's own hatch grammar for the outcome, and a burst only on a hit that removes HP,
>   beside the token.
> - Legal targets get FOCUS corners (2.10). The bill switches to the plan's numbers.
> - Every plan comes from the sim with the card actually played (preview = result); ghosts are the
>   sim's plan units, never shifted copies.
> - Board digits, labels, tags, badges, tickets, the clock's band and label plates are drawn back on top
>   of hover marks.
> - One plate per card effect type (h01 tower turn ... h11 unit hover), with nowords variants:
>   `locked/hover/`.
> - **Round 2 [R, calls C1, C6, C7, C8, C17; measured on the 26 hover plates]:**
>   - **One pencil (call C1).** Board and hover draw every pencil mark with one stroke (`corp/src/rb_pencil.py`):
>     7 px `PLAN` wax, a 3 px ink edge each side, wax grain, no glow; X caps the same stroke; long marks
>     keep the full width. Gated on the plate: wax 6-8 px, ink 2.4-3.6 px a side, grain L* std 2 or more.
>     Measured: wax 6.0-6.5 px, stroke 12.66-13.0, ink 3.25-3.5, grain 3.82-4.65. The HUD pencil ink reads
>     3.0-4.0 px a side (reported).
>   - **The lift (call C6)** is 3.22.D's. 22 of 26 plates have 0 px of any sibling's protected set covered;
>     h02 x4 (slot 0) does not.
>   - **One HUD (call C8).** The hover HUD is the board's row grid (`corp/src/hud_rows.py`), so no row moves
>     when a hover starts: bill y 76-427 on every board and hover plate. The board reserves the option rows
>     (empty on p1, p2b and nowords, about 90 px).
>   - **Dying glass (call C7).** A unit that dies this END TURN keeps its lit glass, gated like a live unit:
>     3:1 or more against the brightest empty cell of its ring (h03 3.98 and 4.19:1; board 4.49-6.07:1).
>   - **Twist halo (call C17).** On a Twist hover the pencil halo is only on the legal rings: the outline on
>     the cell of each unit whose landing changes, 2.5 px off the cell. 0 pencil px on the bezel, the frame
>     band (r 480-500) or outside r 500. h08 (Hold) still runs its arrow on the frame band (reported).
>   - **Dimming:** dim 0.391-0.393 of the board's luma, lit areas 1.00. The lifted card reads p95 90.4-91.1,
>     over the resting hand's 71.3-72.0.
>   - **Open:** two plate pairs fail the drawn-colour test, h03 x2 (gun tracer #FF40B0, dE76 3.8) and h11 x2
>     (the HOT fill dimmed to #662C27 inside the lit area).
>
> #### 3.22.H Loudness and checks
> - **Peak value order:** SEND IT, the HOT threat marks, the lifted card, the tower slices, the rest of
>   the hand, the enemy cells. Measured on round 2 (p1 neutral, p95): SEND IT 98.2 > HOT 94.9 > tower 89.5 >
>   hand 83.1 > token discs 82.6 > clock 69.5 > occupied glass 45.5 > room 37.8 > empty glass 21.0 (3.22.B).
> - Measured p1 on the rebuilt board, whole plate: squint mean 0.240, p95 0.483, loud 12.8 % (E10
>   4.1 %). Nearly all loud cells are the tower and the hand. **The tower is governed by the value order
>   (rb b) [R, REVIEW_RESPONSE: tower loudness by value order]**; its squint share is reported, not
>   gated, and which of the two the designer wants to govern is open (Q2).
> - **Every combat plate must pass** (the locked checks, `final/checks.json` `all_pass`, all true on the
>   15 rebuilt plates; GODOT_PORT_SPEC.md 13.3 lists each with its GUT equivalent):
>   - draw asserts against the state (63/63 p1, 49/49 p2 and p3, 24/24 p2b);
>   - mark collisions (digits, labels, tags, badges, tickets, leader) at 0 px;
>   - occluders (the band, label plates, hand) at 0 px, except a HOLD label on its own plate and the
>     hover leader crossing the band once;
>   - hand outside r 455, and its lowest pixel at least 12 px above y 1080;
>   - 0 dash and 0 dotted calls, and 0 pixel dot runs;
>   - rb a: occupied cell glass at least 3.0x the luminance of the brightest empty cell of its ring;
>   - rb b: the value order (SEND IT > T HOT marks > P tower > P hand > E cells occupied > E cells
>     empty; K and E marks under the HOT marks and the tower) and the room L* 28-34;
>   - rb c: every text cap height 16 px or more at 1080p (cards at the hand scale);
>   - rb d: dE76 15 or more for every token, slice-ink, card-type and skin-ink pair;
>   - rb e: no hand pixel under SEND IT or UNDO, no lifted card over a sibling's cost hex, title band,
>     rules line or ×N plate (round 2, call C6);
>   - the wave tickets' kind glyphs 16 px or more of ink, at the K type value;
>   - nowords with 0 alphanumeric text calls;
>   - a greyscale proof and a squint;
>   - round 2 [R]: every bright pixel in a class (call C3); drawn colours within dE76 3 of their token and
>     15 or more from the corp inks (calls C2, C16); rb f, the pencil (call C1); rb g, the ticket edge steps
>     (call C5); rb h, the HUD rows (call C8); rb i, the HOT core (call C11); and a determinism assert before
>     every publish (call C14: p3, p1_clean, p3 again in one process, 0 px difference).
> - **Not done on the rebuilt board (gate 1):** thin 1 px ring and band lines peaked at L* 95-100 and
>   were not gated (`final/NOTES.md`, gate 1). **Closed in round 2 (call C3):** they are capped at the K type
>   value, reduced with a box filter and classed; 0 unclassed bright pixels on every plate.
> - Parked (designer note 8): the inspect panel, hover tag content, UNDO cause, pile counters.

---

## 5. Accessibility and motion

### "### 5.1 Never colour alone"
**Add**:
> - **Combat redesign waiver (designer, ART CALL 52.4):** colour-blind checks are not run on the
>   ring-wheel combat concept work. The greyscale proof and shape pairing still apply (every meaning
>   pairs with a shape: hatch, chevron, pip, square, corner, glyph). The waiver does not reach the
>   shipping build: there 5.1 stands as written (MUST run the Machado check on this screen) [AP; the
>   designer can widen the waiver. The 2026-11-02 question, old Q2, is closed by this call].

### "### 5.3 VfxTier (kept; `scripts/ui/fx/vfx_tier.gd`)"
**Add**:
> - **Ring-wheel combat effects** (3.22.F) follow this section as written [R, REVIEW_RESPONSE 2.11]: every
>   effect is T2, 0.6 s or less, with no per-effect override (the 2026-11-03 rebuild cut the 2026-11-02
>   lengths of up to 1150 ms); the kill flare is 2 frames at 55 % on the token, under the 60 % local
>   flash. Every effect and the whole resolve beat pass the 3 flashes per second limit [M]. The resolve
>   beat (3.8 s, concurrent tracks, skip on any input) is a sequence of T2 effects, not a T3 event.

### "### 5.4 Reduce effects and reduce motion"
**Add**:
> - The ring-board effect notes call their still forms "reduce motion"; they match **reduce effects**
>   here (no particles, sparks, glitch or flashes). Under reduce motion alone, effects keep their flashes
>   but drop travel. Map both settings to the same still form until the build splits them.

---

## 6. Asset production notes (Godot 4.7)

### "### 6.3 FX"
**Add**:
> - **Ring-wheel combat:** board effects are composited in one `CombatFxLayer` slot **under the HUD and
>   the hand** (6.4; in the generator, `f1_render.SPLIT` below / above), with a second slot above the HUD
>   for `fx_hp_through`, `fx_refund` and `fx_trace_add` only. Slice-wide overlays mask by the wedge with
>   the icon seat cut out; cell-wide ones by the cell polygon. Timings, easing and keyframes from
>   `timings_CDHL.json` / `timings_MPST.json` (merged in `port/fx_timings.json`) go to `ui_motion.tres`.
>   The flash meter in `fxk_lib.flash_check` and the transient loudness meter are the acceptance tests.
> - **Corp skins:** one `CorpSkin` resource per corp (palette and hue inks, the C-family scan-line ink,
>   the room, the polar cell / bezel / annulus / arcframe material, a rim strip with integer turns, crest,
>   token and disc frame sprites, a ticket 9-patch). No `kind_gain`: the cell fills are global tokens.
>   The clock's colours are global tokens, not skin fields.
> - **Backdrop grade:** one post shader on the room layer with the per-room parameters of
>   `backdrop/grade.json` (rb2-1), or the graded rooms baked offline.

### "### 6.4 UI"
**Replace** the last bullet ("Layer order, combat ...") with:
> - Layer order, D4 combat (back to front): city + spill → wheels → heat-glitch post (optional) → FX
>   world layer (tracers, shards, dissolve, walls) → HUD → stickers → hand → moving card → damage
>   numbers → grease pencil → cursor. Pencil is above all UI.
> - Layer order, ring-wheel combat (back to front): room (graded) → board scrim → board (corp skin,
>   spinner, threat marks) → board text on top (digits, labels, tags, tickets, the clock's band) →
>   effects → HUD → effects that land on HUD rows (hp_through, refund, trace_add) → hand → UNDO,
>   SEND IT, nameplate → hover plan marks (pencil). Hover marks never cover digits, labels or tickets.
>   [R, REVIEW_RESPONSE 1.6: the 6.4 rule as written; the 2026-11-02 question, old Q4, is closed.]

## 7-9. Appendices

### "## 7. Appendix A: locked reference images"
**Add** rows:

| Element | Locked reference |
|---|---|
| Ring-wheel combat board (punk player family, neutral skin) | `combat_redesign/locked/final/p1_decide.png`, `p2_preview.png`, `p2b_hover.png`, `p3_resolve.png`, `p1_nowords.png` |
| Spinner | `combat_redesign/locked/final/` plates; `locked/wheel/wheel_crop.jpg` (first pass) |
| WPAP cards | `combat_redesign/locked/final/card_sheet.jpg` |
| Grammar (HOT/COLD/FAR, hatch, outlines) | `combat_redesign/locked/final/grammar_check.jpg`, `VISUAL_PLAN_legend.png` |
| Corp combat skins | `combat_redesign/locked/final/p1_decide_solace.png`, `p1_decide_meridian.png`, `p2b_hover_*` |
| Ring-board effects | `combat_redesign/locked/effects/fx_*.png`, `strips/` |
| Hover plates | `combat_redesign/locked/hover/contact_sheet.jpg`, `h00_key.png`, `h01`-`h11` |
| Backdrop grade | `combat_redesign/locked/backdrop/p1_*.png`, `grade.json` |
| T5 / T6 on the locked board | `combat_redesign/locked/transitions/t5_A.gif`, `t6_A.gif`, `sheet.jpg` |

**Replace** the Appendix A row reference for 3.22 (`combat_bible_test/converged/`) with "superseded
by `combat_redesign/locked/final/`".

### "## 8. Appendix B: open game-design to-dos that affect art"
**Add**:
> 13. **Ring-wheel combat:** the Shove bump HP rule (round 2 said both units lose a tick; not in the
>     E10 state); the Twist render in the resolve beat (ring +1 drawn one sector back until Twist turns
>     it; not to ship until ruled); the Adjuster at END TURN (rings step does not move it); latent
>     effects with no state source (strike, steel ricochet, firewall_burn, the Adjuster hit_land,
>     repair_mend); whether nudge returns on the ring board.

### "## 9. Appendix C: contradictions between rounds and how this bible resolves them"
**Add** rows:

| # | Contradiction | Resolution here |
|---|---|---|
| 26 | 3.22 E8/E9 "pink = unit screens" (2026-10-28) vs ART CALL 51-53 "pink = the player" | Pink = the player on the ring board; units are corp enamel (C5) |
| 27 | 1.2 Rejected list (spray, stencil, collage) vs the punk player family | Exception for the ring-board player family only (C1) |
| 28 | Dashed what-if, dashed predicted, dashed +2 lane vs "no dashed lines" | No dashes on the ring board; time grammar instead (C4) |
| 29 | VISUAL_PLAN law 5 "no slice-type colours" vs the ART CALL 52 per-slice colour pass | Per-slice inks (2.3 ring-board row) |
| 30 | VISUAL_PLAN "SCHEDULE orange moves the rings" vs the 2026-11-02 silver tape and orange = WAVE card / Meridian | The clock is gunmetal with `SCHEDULE` on the live step and in the clock's motion (2.2, 3.22.E; VISUAL_PLAN A.4); WAVE is lilac and Meridian's rim rust, so orange has no other job |
| 31 | VISUAL_PLAN ghost at 40 % vs locked hover ghost at 74 % | 74 % with a pencil outline (3.22.G) |
| 32 | O-29 brief "WAVE bone #F1EAD6" vs bone at 1.04:1 on card paper; then the O-29 WAVE orange #FF8A1F on SCHEDULE | WAVE lilac #B4AAFF, TOWER teal #006E66 (2026-11-03 rebuild; one hue per type, DR-5 / DR-8; dE76 15 or more from every meaning token and slice ink) |
| 35 | 2026-11-02 effects over the HUD and up to 1150 ms vs bible 6.4 and 5.3 | 6.4 and 5.3 as written [R, REVIEW_RESPONSE 1.6, 2.11]: under the HUD, 0.6 s or less (3.22.F) |
| 36 | O-27 "colour plus material, one neutral tape" vs DR-6 | DR-6 (the 2.4 note): material plus the corp hue on rim, lip, crest and cell edges; neutral slate fills; one gunmetal clock |
| 33 | DECISIONS 2026-10-16 "no design needs card type now" vs ART CALL 53 type colours | ART CALL 53 (later) for the ring board; DECISIONS line owed (C15) |
| 34 | VISUAL_PLAN "halftone belongs to X effects" vs Ben-Day on the spinner and cards | Round dots belong to the player; harm uses an X-only screen; damage uses no dots |

### "## 11. Changelog"
**Add** (at fold time):
> - **v2.2 (date of sign-off):** ring-wheel combat redrawn (ART CALLs 51-53, O-27 to O-29): the punk
>   print player family (xerox / linocut / Ben-Day spinner, WPAP cards, type colours), the visual
>   grammar (HOT/COLD/FAR, hatch = END TURN loss by cause, arrowed outline = movement, one enemy
>   outline, no dashes or dots, no needle, W4+ tickets), corp skins per DR-6 (material plus the corp
>   hue on rim, lip, crest and cell edges; neutral slate fills) with one gunmetal clock, eight effect
>   families under the HUD, each 0.6 s or less, with a resolve beat under 4 s and measured flash and
>   loudness limits, hover dimming, the rb2-1 backdrop grade and the cutaway room (DR-9). 3.22
>   "converged" superseded. D4 sections scoped.

---

## Open questions for the designer

Only questions that no designer ruling (DR-1..DR-10), bible note (2.4, 3.14) or `REVIEW_RESPONSE.md` call
answers are kept. The 2026-11-02 list is closed below with where each answer lives.

1. **Q1. D4 scope.** The D4 work waits until this board passes (AD review section 5; REVIEW_RESPONSE).
   Once it does: does the punk player family stay on the ring-wheel combat only, or replace the D4
   player wheel and the vinyl sticker cards everywhere?
2. **Q2. Tower squint vs ink value (VISUAL_PLAN A.1; R1_REREVIEW question 1).** The tower is governed by the
   value order today [R, call C10]; its tower-zone loud share (round 2: p1 59.3 %, p2 68.7 %, p2b 57.0 %, p3
   68.0-68.2 %, nowords 59.9 %) is over the O-29 fix-9 target of 50 % and is reported, not gated (3.22.C).
   Should the squint share govern the tower instead (which would mean duller slice inks), or does the value
   order stand?
3. **Q3. Shove bump HP (a RULES question, REVIEW_RESPONSE S3).** Round 2 said both units lose a tick;
   the E10 state has no such rule, so the bump draws no HP change. The GDD decides.
4. **Q4. Pink in the enemy zone.** 1.38-1.39 % on the three skins on the rebuilt board (round 2), against 0.23 % on the
   2026-11-02 board, where all of it came from game marks. Which marks it comes from now is not yet
   broken down. Is a bar wanted on the rebuilt board, and at what share?
5. **Q5. Twist render (a RULES question, REVIEW_RESPONSE S3).** The resolve beat draws ring +1 one
   sector back from SEND IT until Twist turns it. It is marked not to ship until the designer rules
   how a Twist resolves on screen.
6. **Q6. Skip word.** Any input skips the resolve beat (a 0.2 s dissolve). There is no on-screen word
   for it in the published beat. Round 2 called for one [R, call C12: a "SKIP" key hint at the HUD edge],
   but it is not published yet. Is the hint wanted, and in that form?
7. **Q7. The round-2 calls.** Calls C1-C18 (REVIEW_RESPONSE "Round 2 (2026-11-04)") are art-pass calls. The
   ones the re-review asked the designer about are C8 (HUD height), C9 (room as seen), C10 (tower), C6 (the
   slot-0 lift: three options), C11 (HOT core) and C13 (T6 holds on the room). Two more are open: FOCUS
   against HOT (an exception for FOCUS, or a darker token), and whether VISUAL_PLAN keeps the L8 dotted line
   that no plate draws.

**Closed since 2026-11-02** (old numbers):
- Old Q2 colour-blind checks: the waiver covers the concept pass only; the shipping build follows 5.1 [AP] (5.1 entry).
- Old Q3 effect lengths: every effect is 0.6 s or less, no override [R, REVIEW_RESPONSE 2.11] (C13, 5.3, 3.22.F).
- Old Q4 effect layer: under the HUD, except the three HUD-row effects [R, REVIEW_RESPONSE 1.6] (C14, 6.4).
- Old Q5 card lifecycle: the WPAP card keeps its own states, no sticker motion [AP] (3.18 entry).
- Old Q6 W6 climax ticks: they stay `SCHEDULE` (VISUAL_PLAN F); orange has no other job now (2.2 note).
- Old Q7 dotted: dropped, and gated by the dot audit [AP] (3.22.B).
- Old Q8 loudness: the tower is governed by the value order [R, REVIEW_RESPONSE]; the squint share is the new Q2.
- Old Q9 type colours: a different colour behind each type band [D, DR-8], with no reserved colours [D, DR-5]; the hues TOWER teal #006E66 / WAVE lilac #B4AAFF are the 2026-11-03 rebuild's [R, REVIEW_RESPONSE: card colours] (2.2).
- Old Q10 art-pass defaults: the arrowed outline is kept [D, DR-1]; O-27 is superseded by DR-6 (the 2.4 note).
