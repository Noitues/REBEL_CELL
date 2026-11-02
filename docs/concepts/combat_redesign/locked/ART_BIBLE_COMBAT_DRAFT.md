# ART_BIBLE amendments: ring-wheel combat screen (roadmap step 9)

> **DRAFT, waiting for designer sign-off; not folded into ART_BIBLE.md.**
> Nothing in `docs/ART_BIBLE.md` has been edited. This file proposes changes as a diff-style list:
> each entry quotes an ART_BIBLE section heading, then says **Replace** or **Add** and gives the new text.
> Once the designer signs off, the fold is mechanical: apply the entries, bump the bible to v2.2, move
> the tokens into `Palette` in the same commit, and add a `DECISIONS.md` line (bible 2, "A token
> changed below MUST be changed in `Palette` in the same commit").

Date: 2026-11-02. Branch `art-pass`. Author: art-pass (art bible editor).

**Sources** (later ones win where they disagree):
- `docs/concepts/DIRECTION_REVIEW.md`, ART CALLs 51-53 and O-27 to O-29
- `combat_redesign/VISUAL_PLAN.md` (the R51 rulebook)
- `combat_redesign/locked/REVIEW.md` (the AD review of the locked board, O-29 fix list)
- `docs/concepts/SOLACE_SLICE_ROADMAP.md`, "Added 2026-11-01: combat screen"
- `locked/{wheel,cards,assembled,corp,final,hover,backdrop,transitions}/NOTES.md`
- `locked/effects/NOTES_CDHL.md` and `NOTES_MPST.md`

**How to read the authority of each rule.** Every rule below carries one of these tags:
- **[D]** designer ruling, given in an ART CALL. Binding once folded.
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
| C2 | 1.2 Vinyl sticker: cards are vinyl stickers (gloss, white die-cut, peel). 3.18 sticker cards, yellow cost dot, hover scale ~1.36 | WPAP print cards: chamfered die-cut, facet planes, a type plate, cyan cost hex, hover 1.10x (ART CALL 53) | 3.18 is scoped to D4 combat; the ring board uses the WPAP card (3.22.D) |
| C3 | 1.2 Binary bits carry "damage shards", and 3.20 says "All FX use bits in the source colour" | Ring-board hits use 8 effect families with their own materials (pink comic hit, red X-halftone print, corp shutter...). Bits stay for the T5/T6 transitions only | 3.20 is scoped to D4; the ring board follows 3.22.F. Bits keep their transition job |
| C4 | 1.2 grease pencil: "Solid = what will happen; dashed = what-if". 3.17 dashed ghost blades. 3.5 status badge "dashed outline = predicted". 3.22 "+2 = dashed pale 3 px" lane | No dashed lines anywhere on the combat screen [D, ART CALL 51.2] | Dashes are banned on the ring board. What-if, predicted and +2 take the HOT/COLD/FAR grammar (3.22.B) |
| C5 | 3.22 E8/E9: "Pink has one job: unit screens"; CELL-9 and the code-base frame cyan; SEND IT yellow; lane trim pale blue; rider lavender | Pink belongs to the player: spinner, cards, guns, SEND IT, nameplate, damage we deal [D/AP, ART CALL 51.1 and O-27]. Enemy cells are corp enamel | Replace the 3.22 E8/E9 colour block |
| C6 | 3.22 lane outlines: NOW solid red 4 px, +1 solid pink 3 px, +2 dashed pale; lane style on the token base | One enamel outline for every enemy cell [D, ART CALL 51.5]; depth is read by the time grammar | Replace |
| C7 | 3.22 "the needle is sector 0"; 3.2 pointer blade | No needle on the new combat concept [D, ART CALL 52.3] | Replace on the ring board; D4 wheels keep their blades |
| C8 | 3.22 waves beyond the rim as concentric arcs; climax arc in HARM red | W4-W6 compressed to three tickets top-left [D, ART CALL 51.6 met] | Replace |
| C9 | 3.22 Soak is orange chevrons; shield a cyan bracket; Brace a cream clamp; FIREWALL an orange hatched wedge | Soak is SOAK blue hatch with a chevron notch; hatch is reserved for END TURN loss; Firewall is a pink flame band | Replace |
| C10 | 2.1 `NET_CYAN` / `PROTECT` = "defend/shield slices, block and shield FX". 2.3 slice colour = type (attack pink, defend cyan...) | SHIELD slice ink is cobalt #2A58F0; the protect FX is a bone plate; cyan means terminal and RAM only | Add a ring-board row to 2.3 and narrow `NET_CYAN` on that screen |
| C11 | 2.4 Solace secondary pink #FF4696 | Solace pink demoted to tiny rose nuclei on the combat board, so pink stays the player's [AP, O-27] | Add a combat-skin rule to 2.4 |
| C12 | 5.1 colour-blind check (Machado 2009) for every screen | The designer said to ignore colour-blind checks [D, ART CALL 52.4] | Proposed: the waiver covers the combat redesign concept pass. The greyscale check stays. The shipping CVD check is the designer's call (Q2) |
| C13 | 5.3 VfxTier T2 outcome: max 0.6 s, 60 % local flash | 24 of the 32 new effects run 650-1150 ms; the kill flare is 70 % white on one cell | Proposed: register the ring-board effects per family with their measured lengths (3.22.F). Needs a call (Q3) |
| C14 | 6.4 combat layer order: FX world layer is under the HUD | The effects slot sits above the board, tower **and HUD**, below the hand (`extra` hook). VISUAL_PLAN G ends "... FX-S → HUD" | Proposed: board effects under the HUD, except `fx_hp_through`, `fx_refund` and `fx_trace_add`, which land on HUD rows and sit above them (Q4) |
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
| **Corp enamel** (ring-wheel combat only) [AP, O-27] | **What the enemy owns on the board:** ring cells, unit tokens, bezel, landing annulus, rim, crests, wave tickets | Clean vector on frosted enamel, perfect geometry, one hairline; per corp a colour **plus** a material and pattern (3.22.E) | Pink; grit or hand-made texture; the THIS TURN tape (that is time grammar) |

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
> owns is pink: measured pink-hue pixels in the enemy zone (r 214-500) are 0.23 % on every skin, all
> from game marks [M]. `NET_CYAN` means the **terminal and RAM** only (HUD plate edges, RAM coins, the
> card cost hex). It does not mark shields or blocks on this screen.

### "### 2.2 Semantic tokens (kept from v1; MUST pair with a shape, glyph or word)"
**Add** a ring-board token table (to land in `Palette` at fold time):

| Token | Hex | The one meaning | Paired with |
|---|---|---|---|
| `SOAK` | #3A7EF3 | Your soak choice | Blue hatch plus a 5 px chevron notch; funnel |
| `TRACE_VIOLET` | #A03CFF | Trace, only | Square r3 pip; the card +Trace tab |
| `BOSS_GOLD` | #FFC428 | The Adjuster (boss) and its ward | Gold cell edge, lozenge |
| `PLAN` (= `PENCIL_PLAN`) | #FFE200 | Your plan or preview (hover only, never in resolve) | Grease pencil, arrowed outline |
| `COLD_HARM` | #D9877C | A harm mark for turn +1 | One turn pip |
| `FAR_HARM` | #96767A | A harm mark for turn +2 and later | Two turn pips |
| `ENAMEL` | #D9E1EA | Neutral enemy structure (no meaning) | Hairline |
| `CREAM` | #FFF4D6 | Enemy HP (neutral) | Vector tick |
| `TAPE_LO` / `TAPE_HI` | #768E8E / #E8EEF4 | THIS TURN tape: one silver for every corp | The tape band, ink keyline |
| `CARD_TOWER` | #2F5BFF, white text | Card type TOWER | Type plate, facets |
| `CARD_WAVE` | #FF8A1F, ink text | Card type WAVE | Type plate, facets |

Measured [M]: TOWER white text on cobalt 4.94:1, plate vs paper 4.47:1; WAVE ink text on orange
7.86:1, plate vs paper 2.04:1 (the ink keyline and drop carry that edge); TOWER vs WAVE in grey
2.19:1. Bone #F1EAD6 was tried for WAVE and rejected at 1.04:1 against the card paper.

**Note:** VISUAL_PLAN listed `SCHEDULE` #FF8C1A as "the rings move". On the locked board the clock is
silver (the tape), and orange now means the WAVE card and Meridian's hazard rim. `SCHEDULE` keeps
no role on the ring board except the W6 climax ticks (Q6).

### "### 2.3 Slice colours (kept)"
**Add**:
> **Ring-wheel combat spinner (designer, ART CALLs 52-53):** each slice type has its own spot ink,
> texture and grey value. This supersedes VISUAL_PLAN law 5 ("no slice-type colours") for the
> spinner.
>
> | Slice | Ink | Texture | Grey value (seat) |
> |---|---|---|---|
> | BURST | #FF3DA8 (the player pink) | big xerox dots | mid |
> | SHIELD | #2A58F0 cobalt | xerox scales | dark |
> | TURRET | #FFD21F yellow | Ben-Day bullseye rings centred on the icon | light |
> | REPAIR | #4BD67E green | xerox plus crosses | light |
>
> The four separate in grey by seat value as well as by texture. The xerox checker texture is
> retired, because it read as the loss hatch. Slice names are the game's (BURST, SHIELD, TURRET,
> REPAIR); the punk key's ZERO-DAY / SANDBOX / EXPLOIT / PATCH were agent labels and are not used.

### "### 2.4 Corporation palettes (LOCKED kits, round 18 values)"
**Add** to the Rules list:
> - **Combat skins (ring-wheel combat, art-pass default O-27):** on the board a corp shows as colour
>   **plus material and pattern**, never as a colour wash (3.22.E). Solace's secondary pink is
>   demoted there to rose nuclei under glass (about 34 % alpha), so pink stays the player's.
>   Meridian's hazard rim is desaturated 25 % and kept clear of every amber game mark.

### "### 2.9 Typography"
**Add** after the table:
> - **Punk print card titles (ring-wheel combat, designer ART CALL 52.1):** white fill on an ink plate
>   with a 1.4 px ink keyline and one hard pink offset (never the only edge). Never yellow or pink
>   letters. Anton 38 design px, capitals, tracking 1.0, rotation -2 deg, no skew, glow or gradient.
>   Cap height at least 30 screen px at hand scale (measured 35.9 px at 1.10x; FIREWALL 32.4) [M].
>   Rules text IBM Plex Sans Condensed 21 design px (floor 15), ink on cream. Cost digit Anton 27 on
>   the cyan hex; type word Anton 19.

### "### 2.10 Focus and state colours in chrome"
**Add**:
> - **Board focus (ring-wheel combat):** board cells and slices take `FOCUS` lime **corners only**:
>   12 px legs, 2 px for a legal target, 3.5 px for the aimed one, never a full outline. A corner
>   slides up to 12 deg inward if it would touch a digit, label, tag, badge or ticket, and is never
>   dropped. Chrome keeps the 3 px / 7 px brackets above.

---

## 3. Combat

### "### 3.1 The screen (LOCKED layout, round 31 / round 43 HUD v4)"
**Add** at the top:
> This section and 3.2-3.21 describe the **two-wheel D4 combat**. The ring-wheel combat (Shifting
> Waves) is in 3.22, which overrides them on that screen.

### "### 3.14 Combat backdrop (LOCKED)"
**Add** at the end:
> - **Ring-wheel combat grade (roadmap step 6, locked board):** one full-screen post shader on the
>   room layer, under the board, applied on sRGB-encoded values in this order: focus-hull ellipse;
>   blur 0.4 px on the room and 4 px on the city; chroma (overall, neon pull 0.8, player-pink pull);
>   contrast 1.12 about a pivot of 0.16; hull and city value (city 0.55); a luma shoulder from 0.18
>   toward 0.30; haze 0; vignette 0.30 and a 0.30 falloff toward the board side. `hull_value` and
>   `chroma` are solved per room (bio 0.466 / 0.876 ... shop 0.415 / 0.826; event has contrast 1.24,
>   shoulder 0.32, pink pull 0.42). Values in `backdrop/grade.json` go to config [M].
> - **Pink belongs to the player:** magenta-to-rose room hues (about 302-350 deg) lose 45 % chroma
>   (58 % in the event room). The violet night city is left alone.
> - **Acceptance (measured squint: 1/16 box, 1 px blur, Rec709 luma, loud above 0.38):** room mean
>   0.125-0.145, room p95 at most 0.25, room loud 0 %, board/room at least 1.55, relative room detail
>   at least 0.80 of the old grade, saturation within 0.05, room pink under 0.1 %, board pixels
>   unchanged. All 7 rooms and both corp plates pass (room mean 0.135, board/room 1.61-1.67) [M].
> - The board scrim stays: 6 px frosted pool plus `SCRIM` #02030A at 55 %, r 330-560.

### "### 3.17 Card-play preview (LOCKED, animated, round 17)"
**Add** at the top:
> D4 wheels only. The ring-wheel combat previews through hover (3.22.G): no dashed ghosts, no ghost
> blades.

### "### 3.18 Sticker cards (LOCKED)"
**Add** at the top:
> D4 combat. Ring-wheel combat cards are the WPAP punk print card of 3.22.D (designer, ART CALL 53).
> Whether the peel, slap and dissolve-A lifecycle carries over to the WPAP card is open (Q5).

### "### 3.20 Damage shards and combat FX (LOCKED list)"
**Add** at the top:
> D4 combat. Ring-wheel combat effects follow the eight families of 3.22.F; bits are kept there for
> the T5 / T6 transitions.

### "### 3.22 Ring-wheel combat: Shifting Waves "converged" look (LOCKED as front runner, designer 2026-10-28)"
**Replace the whole section** with the text below. The old body moves to the changelog as
superseded. Kept from it: one board, top-down concentric rings, rings radially aligned with the
slices, spinner only (PL7, no table restates the sectors), the bill column, the rail rule (bezel
text at least 16 px), and the "never add or drop a number or word" content guard.

> ### 3.22 Ring-wheel combat: the locked punk board (designer ART CALLs 51-53; art-pass defaults O-27 to O-29)
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
> | Schedule band (THIS TURN tape) | 391-417; marks stay inside 388 |
> | Landing lanes | 436, 453, 470 |
> | Rim | 489-500 |
> | Hand | outside 455 at every pixel (asserted) |
>
> - Sector digits 0-5 sit on their own top layer, above cells, tape, plates and tags. Digit 0 is at
>   -4.5 deg, clear of the tape start. Every digit punches a 2.6 px hole through the tape, plate and
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
> - Value order HOT > COLD > FAR holds on every skin. Sector-3 chevrons vs their cell (luma / dE2000):
>   neutral 3.12/48, 3.59/43, 2.81/30; Solace 3.11/54, 3.38/48, 2.71/38; Meridian 2.89/38, 3.17/35,
>   2.46/23 [M].
> - One HOT mass per family: threat has the NOW chevrons and diamonds, the clock has the live tape
>   cell, the player has the pending hatch. Nothing in the future is HOT. In resolve (p3) HOT marks lose
>   their glow.
> - **Hollow means growth only on chevrons:** solid chevron = a hit, hollow chevron = growth still to
>   come. Any other +1 mark is COLD, never hollow.
> - The bill's main rows are HOT; the NEXT row is COLD with one turn pip.
> - Dotted marks: VISUAL_PLAN kept L8 dotted for the +2 threat trim only. No locked plate draws one
>   (0 dotted calls on every plate) and the effects designers treat dotted as banned. Proposed: drop
>   dotted, so FAR is value plus two pips (Q7).
>
> **Cross-hatch = HP lost at this END TURN** [D/AP].
> - Two directions (45 and 135 deg), 2 px lines at a 5 px pitch, clipped to the shape, with a solid
>   2 px edge in the same colour and an **ink keyline under every hatch line** (red vs ink 5.7:1).
> - On a segment under 9 px: one direction, 1.6 px lines at a 4 px pitch, and the pending segment
>   bulges 2 px. Two-direction hatch only on segments 12 px or wider. If it closes up at 320 px, widen
>   the pitch; never drop it.
> - **Hatch colour = cause:** `HARM` red = the enemy takes it; `SOAK` blue (plus a chevron notch) = your
>   soak spends it; `CELL_PINK` = we take it (enemy HP). Hatch swatches on each skin's own cell
>   (neutral / Solace / Meridian): red 2.9 / 2.6 / 2.9:1, pink 3.0 / 2.8 / 3.0:1, blue 2.6 / 2.4 / 2.5:1 [M].
> - **O-28:** on a hatched slice the texture vanishes, so a solid slice-ink seat ring round the icon
>   carries the type. The hatch stops at r 37 round the icon.
> - Cross-hatch is used for nothing else: the Trace cap is a padlock, a broken slice is a black-out,
>   an unaffordable card is dim glass, and P shading is single-direction only.
> - Other HP states (VISUAL_PLAN D): lit, COLD future loss (hollow 1.5 px outline in the cause colour
>   plus a pip), mend pending (GAIN outline with a 7 px plus), gone (dark socket #0E1016, solid
>   1.4 px hairline #3A4150), blocked (segment stays lit behind a protect plate). The E10 white slash is
>   retired.
>
> **Arrowed outline = movement only** [D, ART CALL 51.4].
> - A 16 px channel, two 3 px edges, inner chevrons 10 px at a 24 px pitch, a 22 px arrowhead.
> - Colour by who moves the thing: `PLAN` yellow in hover (the plan); `CELL_PINK` in resolve for a card
>   (Spin, Nudge, Twist, Pull, Shove); silver for the clock (rings step, Hold), drawn at r 426 beside the
>   tape, never on it; the corp colour for the wave (lime Solace, orange Meridian, graphite neutral);
>   neutral enamel for the queue feed arrow. Yellow never appears in resolve.
> - Used by: the hover route, the Trigger path, the THIS TURN schedule cell, Twist, Spin ghost, Shove,
>   Pull, the wave-queue feed.
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
> - Watch for accidental dots: a 1 px tape lip broke into dots once remapped to silver, so the tape
>   edge is the solid ink keyline only.
> - No needle or 12 o'clock marker. The THIS TURN tape starts at 12 o'clock and digit 0 sits beside it.
>
> **W4+ wave tickets** [D, ART CALL 51.6; AP layout].
> - Three tickets in the top-left corner, FAR to near, left to right: W6, W5, W4. Each is 84x64 px with
>   a mono tag, unit kind glyphs at 24 px and 1-3 width bars per unit.
> - Solid edges. Time is shown by value (W6 50 %, W5 70 %, W4 100 %) and pips, never by a dotted edge.
> - The W6 climax ticket has a cut corner and three hazard ticks.
> - One neutral-enamel arrowed feed runs from W4 to the board edge.
> - `WAVES 6 LEFT` stays in the header. Ticket material comes from the corp skin (`ticket`).
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
> - **Loudness knobs** [M]: halo value x0.90 (`HALO_K`), texture x0.90 (`TEX_K`). Tower-zone loud share
>   (squint, loud above 0.38) 48.6 % on p1 and under 50 % on p2b, nowords and both corp p1 plates.
>   It is over target on p2 (57.9 %) and p3 (57.5 %); see Q8.
>
> #### 3.22.D Player family: WPAP cards (designer ART CALL 53)
> - **Frame:** a chamfered die-cut WPAP card on the black-book layout, flat facet planes, slanted
>   plates, hard offset drops.
> - **Facets:** two planes in the type colour at 32 %, two in the type's dark at 28 %, one white glint
>   plane at 25 %, each with a 0.7 px ink cut edge (brief 25-35 %).
> - **Type colour** (the plate under the title, a thin rule on the title plate, the corner facet, the
>   facets): TOWER cobalt #2F5BFF with white text; WAVE orange #FF8A1F with ink text. The state has
>   only these two types; do not invent more. Violet stays the +Trace tab only.
> - **Band art** draws on the other punk styles, one per card: Ben-Day (Nudge sky, Spin 2 mint, Spin 3
>   yellow #FFD21F, with 1 / 2 / 3 solid ink arcs and Ben-Day density 0.55 / 0.85 / 1.15), linocut
>   (Brace, Pull), collage (Strike, Shove), mural (Firewall, Twist), xerox (Hold), Jinx (Trigger).
>   Arcs, bolts and bars on bands are decoration, not data.
> - **Icon (xerox, recoloured):** a paper-white glyph with a 2.5 px key line and hard black drop on a
>   spot-ink disc with a misprinted second-ink crescent, a black ring, then a white scissor halo with
>   an ink drop. Disc vs the art round it at least 2.5:1 (measured 2.53-6.41) [M]. Brace, Firewall,
>   Pull, Shove and Twist use ink discs with pink in the crescent; Trigger and Hold pink discs (Hold with
>   a black toner pool).
> - **Cost** stays a system resource: cyan hex, Anton digit. **+Trace** tab in `TRACE_VIOLET`.
> - **States:** normal (resting hand at 88 % value); hover (1.10x, pink misregistered print, longer
>   drop, the hand pushes right 16 px); played (solid blue-grey liner, faint glyph, the card name above
>   PLAYED in mono small caps at 70 %); unaffordable (dim glass, value x0.5, chroma x0.4, two flat
>   glass planes, never hatch); nowords (bars and tallies, glyph and art kept).
> - **Hand:** cards at 1.10x, step 168, no pixel inside r 455 (measured 458.9). The corner may cover
>   the rim between r 455 and r 500. When the lifted card is in slot 0, the fan slides right 32 px and
>   the lift drops 40 px.
>
> #### 3.22.E Corp skins (art-pass defaults O-27, ART CALL 53)
> - **Colour plus material**, built as data (one `CorpSkin` per corp), so a corp swap is a skin swap.
>   The neutral skin is clean graphite enamel. Solace: membrane-pattern glass cells, a helix rim, a
>   porcelain roundel. Meridian: corrugated steel cells, octagonal container token frames, a hazard
>   rim, crane crests, shipping-tag tickets. A colour-only skin is rejected: Meridian read as the old
>   slate, and Solace's flat green fought the pink player.
> - **What a skin may change:** cells (material and tint), bezel, landing annulus, arc frames, rim,
>   crests, token and disc frames, tickets, optional empty-cell marks. **What it may never touch:** the
>   THIS TURN tape, HP, the hatch, HOT/COLD/FAR marks, threat marks, outline meaning, hover and plan
>   marks, the player family.
> - **One neutral silver THIS TURN tape for every corp:** a remap of the schedule fill to `TAPE_LO`..
>   `TAPE_HI`, keeping chevrons and text as tone; HOLD amber and plan yellow are untouched. The tape
>   edge is the solid ink keyline. Tape pixels match the neutral plate on 97.7 % (Solace) and 98.0 %
>   (Meridian); the rest are units overlapping the band [M].
> - **Pink is the player's:** no enemy glyph, skin or effect is pink. Enemy-zone pink 0.23 % on every
>   skin, all from game marks (our guns' marks and hatch).
> - **Kind separation:** the corp tint must not collapse unit kinds. Each skin carries `kind_gain` per
>   ring (a Lab push of the four kind washes from their mean, baked per skin swap), solved so the
>   skinned minimum dE2000 is not below the neutral skin's (6.8 / 4.3 / 2.3 on rings 0-2). Solace
>   gains 2.4 / 2.1 / 2.0, Meridian 1.0 / 1.1 / 1.2. Ring 2 kinds stay close on every skin (about 2.5),
>   so the **kind glyph carries kind**; the wash is the second channel.
> - **Corp marks never mimic game marks:** Meridian's hazard stripes are cut 25 % in chroma, and the
>   inner bezel lip is black, so amber game marks (HOLD, the Adjuster arc) keep at least 37 px of gap
>   from hazard paint [M]. FAR harm is lifted so it reads on oxide brown.
> - Skin data format and hooks: `locked/corp/NOTES.md` (Godot `CorpSkin` resource) and
>   `locked/final/NOTES.md` ("Skin hooks").
>
> #### 3.22.F Effect families and flash limits (designer ART CALL 51.7; roadmap step 4)
> Every event is a slice-wide (whole wedge) or cell-wide overlay. Each family has its own material so
> it never reads as another family or as a skin:
>
> | Family | Means | Material | Effects |
> |---|---|---|---|
> | **C corp** | The enemy changes state | A flat opaque shutter slab in the corp's own frame material with a hard 2 px lip (neutral steel straight, Solace porcelain with a lime rounded lip, Meridian stencil paint with an oxide notched lip); one flat 4-frame flash; ward in boss gold | grow, ward_on |
> | **D damage** | We hurt them | Player pink: a painted tapered tracer ribbon with an ink key, an ink-keyed starburst with a white core, white speed lines, flat vector shards; no Ben-Day | gun_hit, strike, trigger_hit, kill, ricochet (+ gold), firewall_burn, shove_bump |
> | **H harm** | The enemy hurts you | Misregistered red print: an X-only halftone flood (never round dots), black krackle with a 2 px red offset, a red stencil X | hit_land (+ worm, Adjuster), shield_break, slice_crack, slice_break, hp_through |
> | **L life** | Gain | The only soft rising glow: brush ribbons, plus signs, sparkles in GAIN (mint #D6FFCE with an ink key on the green REPAIR wedge); the RAM coin in `NET_CYAN` | refund, clear, repair_mend |
> | **M motion** | Things move | Three print echoes (26 / 52 / 78 ms, tinted 25 % to the mover) plus the arrowed outline in the owner's colour | spin, twist, pull, shove, rings_step, hold, wave_enter |
> | **P protect** | Your defence holds | A bone #F1EAD6 plate with a 3.4 px ink key, a pink double line, ink rivets, a hard (3, 5) offset shadow at 55 %; flat tints; white spark ticks; no starburst, red or glow | shield_block, brace_block, soak_take |
> | **S system** | Trace | A stepped violet glitch: 6 px band shears, 3 px R/B split, 35 % violet tint, scanlines; 33 ms steps, new rows each step | trace_add |
> | **T commit** | SEND IT / a Trigger resolves | Pencil yellow burns into pink paint front to back, white-hot 2 frames deep; a pink ping at the route end | commit |
>
> Rules for every effect:
> - Effects **never add cross-hatch**. They resolve the board's existing hatch into a gone socket or a
>   dark pip.
> - Slice-wide overlays keep the icon seat (r 37) clear, except where the effect fades the icon on
>   purpose (shield_break, slice_break). Never put an X, slash or glyph over the icon it describes.
> - No dashed or dotted lines: trails are one continuous tapered ribbon (echo-dot trails read as
>   dotted and were replaced). No needle. The arrowed outline appears only in M and T.
> - State changes are real before and after states from the generator, never painted.
> - **Layer order in resolve:** board, threat marks, M, then P / H on the tower and D / C on the rings,
>   then L, then S, then HUD. Effects on one beat are **sequenced** in this order and never stack in
>   the same 100 ms window.
> - **Flash limit:** at most 3 flashes in any 1 s window, measured per effect at 60 fps on WCAG
>   relative luminance. A transition is a swing of at least 0.10 whose darker end is below 0.80; a wave
>   is 25 % of the effect's own footprint swinging the same way within 100 ms; a flash is an opposing
>   pair of waves. All 32 effects and variants pass on every skin, full and reduce motion: worst case 2
>   per second (ward_on, slice_crack in full motion; shield and brace blocks in reduce motion) [M]. The
>   largest single event is the kill flare: 2 frames of 70 % white on the cell only.
> - **Durations** [M]: 400-1150 ms (in / hold / out per effect in `timings_CDHL.json` and
>   `timings_MPST.json`), to go into `content/config/ui_motion.tres`.
> - **Reduce motion:** every effect has a still form. No echoes, travel, overshoot, sparks or glitch
>   steps; state changes are 200-300 ms dissolves; arrows, plates and stamps appear whole with a
>   100-120 ms fade.
> - **Transitions T5 / T6** keep bits option A (O-25), recoloured: ring glyphs in the corp skin colours,
>   a fourth keyline in the neutral tape silver, the spinner keyline in pink, card trails in their type
>   colour (cobalt, orange, violet sparks on the +Trace card), destination ghosts as one solid hairline.
>   0 whole-frame flashes; worst 60 px tile 2 flashes per clip [M].
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
> - Board digits, labels, tags, badges, tickets, the tape and label plates are drawn back on top of
>   hover marks.
> - One plate per card effect type (h01 tower turn ... h11 unit hover), with nowords variants:
>   `locked/hover/`.
>
> #### 3.22.H Loudness and checks
> - **Peak value order:** SEND IT, the HOT threat marks, the lifted card, the tower slices, the rest of
>   the hand, the enemy cells.
> - Measured p1, whole plate: mean 0.205, p95 0.493, loud 12.2 % after the backdrop grade (E10 4.1 %).
>   Nearly all loud cells are the tower and hand; the rooms are at 0 % loud. The target for the
>   player side is open (Q8).
> - **Every combat plate must pass** (the locked checks):
>   - draw asserts against the state (63/63 p1, 49/49 p2 and p3, 24/24 p2b);
>   - mark collisions (digits, labels, tags, badges, tickets, leader) at 0 px;
>   - occluders (tape, label plates, hand) at 0 px, except a HOLD label on its own plate and the hover
>     leader crossing the tape once;
>   - hand outside r 455;
>   - 0 dash and 0 dotted calls;
>   - nowords with 0 alphanumeric text calls;
>   - a greyscale proof and a squint.
> - Parked (designer note 8): the inspect panel, hover tag content, UNDO cause, pile counters.

---

## 5. Accessibility and motion

### "### 5.1 Never colour alone"
**Add**:
> - **Combat redesign waiver (designer, ART CALL 52.4):** colour-blind checks are not run on the
>   ring-wheel combat concept work. The greyscale proof and shape pairing still apply (every meaning
>   pairs with a shape: hatch, chevron, pip, square, corner, glyph). Whether the shipping build runs
>   the Machado check on this screen is a designer call (Q2).

### "### 5.3 VfxTier (kept; `scripts/ui/fx/vfx_tier.gd`)"
**Add**:
> - **Ring-wheel combat effects** (3.22.F) are measured per effect against the 3 flashes per second
>   limit (worst 2). Many run longer than the T2 0.6 s cap (hp_through 1150 ms, brace_block 1060,
>   firewall_burn 1000, refund and repair_mend 900). Proposed: register each with its measured length
>   as T2 with a per-effect duration override in `ui_motion.tres`, and the kill flare (70 % local, one
>   cell) as T3 (Q3).

### "### 5.4 Reduce effects and reduce motion"
**Add**:
> - The ring-board effect notes call their still forms "reduce motion"; they match **reduce effects**
>   here (no particles, sparks, glitch or flashes). Under reduce motion alone, effects keep their flashes
>   but drop travel and echoes. Map both settings to the same still form until the build splits them.

---

## 6. Asset production notes (Godot 4.7)

### "### 6.3 FX"
**Add**:
> - **Ring-wheel combat:** effects are composited in one `CombatFxLayer` slot above the board and
>   tower (in the generator, the `extra` hook). Slice-wide overlays mask by the wedge with the icon
>   seat cut out; cell-wide ones by the cell polygon. Timings, easing and keyframes from
>   `timings_CDHL.json` / `timings_MPST.json` go to `ui_motion.tres`. The flash meter in
>   `fxk_lib.flash_check` is the acceptance test.
> - **Corp skins:** one `CorpSkin` resource per corp (palette, `kind_gain[3]`, cell texture and a polar
>   cell shader, bezel / annulus / arcframe textures, a rim strip with integer turns, crest, token and
>   disc frame sprites, a ticket 9-patch). The tape colour pair is a global token, not a skin field.
> - **Backdrop grade:** one post shader on the room layer with the per-room parameters of
>   `backdrop/grade.json`.

### "### 6.4 UI"
**Replace** the last bullet ("Layer order, combat ...") with:
> - Layer order, D4 combat (back to front): city + spill → wheels → heat-glitch post (optional) → FX
>   world layer (tracers, shards, dissolve, walls) → HUD → stickers → hand → moving card → damage
>   numbers → grease pencil → cursor. Pencil is above all UI.
> - Layer order, ring-wheel combat (back to front): room (graded) → board scrim → board (corp skin,
>   spinner, threat marks) → board text on top (digits, labels, tags, tickets, tape) → effects →
>   HUD → effects that land on HUD rows (hp_through, refund, trace_add) → hand → UNDO, SEND IT,
>   nameplate → hover plan marks (pencil). Hover marks never cover digits, labels or tickets (Q4).

---

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
>     E10 state); the Adjuster at END TURN (rings step does not move it); latent effects with no state
>     source (strike, steel ricochet, firewall_burn, the Adjuster hit_land, repair_mend); whether
>     nudge returns on the ring board.

### "## 9. Appendix C: contradictions between rounds and how this bible resolves them"
**Add** rows:

| # | Contradiction | Resolution here |
|---|---|---|
| 26 | 3.22 E8/E9 "pink = unit screens" (2026-10-28) vs ART CALL 51-53 "pink = the player" | Pink = the player on the ring board; units are corp enamel (C5) |
| 27 | 1.2 Rejected list (spray, stencil, collage) vs the punk player family | Exception for the ring-board player family only (C1) |
| 28 | Dashed what-if, dashed predicted, dashed +2 lane vs "no dashed lines" | No dashes on the ring board; time grammar instead (C4) |
| 29 | VISUAL_PLAN law 5 "no slice-type colours" vs the ART CALL 52 per-slice colour pass | Per-slice inks (2.3 ring-board row) |
| 30 | VISUAL_PLAN "SCHEDULE orange moves the rings" vs the silver tape and orange = WAVE card / Meridian | The clock is silver (3.22.B) |
| 31 | VISUAL_PLAN ghost at 40 % vs locked hover ghost at 74 % | 74 % with a pencil outline (3.22.G) |
| 32 | O-29 brief "WAVE bone #F1EAD6" vs bone at 1.04:1 on card paper | WAVE orange #FF8A1F (the brief's fallback) |
| 33 | DECISIONS 2026-10-16 "no design needs card type now" vs ART CALL 53 type colours | ART CALL 53 (later) for the ring board; DECISIONS line owed (C15) |
| 34 | VISUAL_PLAN "halftone belongs to X effects" vs Ben-Day on the spinner and cards | Round dots belong to the player; harm uses an X-only screen; damage uses no dots |

### "## 11. Changelog"
**Add** (at fold time):
> - **v2.2 (date of sign-off):** ring-wheel combat redrawn (ART CALLs 51-53, O-27 to O-29): the punk
>   print player family (xerox / linocut / Ben-Day spinner, WPAP cards, type colours), the visual
>   grammar (HOT/COLD/FAR, hatch = END TURN loss by cause, arrowed outline = movement, one enemy
>   outline, no dashes, no needle, W4+ tickets), corp skins as colour plus material with one neutral
>   tape, eight effect families with measured flash limits, hover dimming, the backdrop grade. 3.22
>   "converged" superseded. D4 sections scoped.

---

## Open questions for the designer

1. **Q1. Scope.** Does the punk player family stay on the ring-wheel combat only, or replace the D4
   player wheel and the vinyl sticker cards everywhere?
2. **Q2. Colour-blind checks.** The waiver (ART CALL 52.4) is applied to the concept pass. Should the
   shipping build run the Machado check on this screen (bible 5.1 says MUST)?
3. **Q3. Effect lengths.** 24 of the 32 effects run past the T2 0.6 s cap (up to 1150 ms). Accept per-effect
   overrides, or shorten them to fit T2?
4. **Q4. Effect layer.** Board effects under the HUD (VISUAL_PLAN G) or above it (the generator's
   `extra` slot)? The proposal is under, except the three effects that land on HUD rows.
5. **Q5. Card lifecycle.** Do the WPAP cards keep the sticker peel, slap and dissolve-A motion (3.18),
   or get their own?
6. **Q6. W6 climax ticks.** They are still orange, which now also means WAVE cards and Meridian. Keep
   them, or move them to HARM?
7. **Q7. Dotted.** Drop L8 dotted entirely, so FAR is value plus two pips, as the plates already show?
8. **Q8. Loudness.** Tower zone is under 50 % loud on p1 but 57.9 % on p2 and 57.5 % on p3; the whole
   plate is 12.2 % loud vs E10's 4.1 % (R51 proposed 8 % or less). Accept, or dull the yellow and green
   slice inks?
9. **Q9. Type colours.** Confirm TOWER cobalt / WAVE orange (the AD said the only designer input still
   useful was a yes on these).
10. **Q10. Art-pass defaults.** Confirm O-27 (colour plus material, one neutral tape) and the ART CALL
    51 grammar, which ART CALL 53 lists as defaults the designer has not ruled on.
