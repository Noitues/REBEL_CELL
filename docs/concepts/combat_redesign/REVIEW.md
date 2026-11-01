# Combat redesign: art-director review of the exploration round

Date: 2026-11-01. Branch art-pass, documentation only. Serves ART CALL 51 (designer notes 1-10 on the E10 redesign).
Board: `review/board.jpg` (all ten style plates side by side, ranked; made by `review/make_board.py`).
Plan changes from this review are written into `VISUAL_PLAN.md` (marked **R51 review**).

I opened every plate, style board and crop listed by the eight streams. The verdicts below come from the images. Where a stream's notes disagree with its image, the image wins.

---

## 0. The headline problem: every style plate still looks like E10 from across the room

All five style streams redrew only the player family (tower r 0-162, cards, SEND IT, nameplate, YOU strip). The rest of the screen is the E10 board: dashed ring outlines, red, blue and white lane outlines, the three W4-W6 arcs, and mauve or lightly toned cells. At 1x the tower is about 320 px of a 1080 px screen. So at a glance **all ten plates read as "E10 with a pink centre"**. That is exactly what note 10 rejected ("only got very minor tuning").

The grammar stream (`grammar/plate_base.png`) and the effects stream's stand-in board (`effects/fx_plate_a_resolve_tower.png`) show that the board itself can look new: no dashes, neutral enamel, slate glass, the wave queue in the corner, a clear rim. **The finalists must be rendered on that redesigned board, never on the E10 board again.** Section 2 gives the board direction both finalists share.

---

## 1. Style ranking and finalists

Ranked on: art style first, then player-owned read, then Spider-Verse / Arcane level of craft, then legibility.

| Rank | Direction | Verdict from the images |
|---|---|---|
| **1** | **Sketchbook graffiti (G2)** | The most art-led and the strongest "ours" read: one pen draws the tower, the cards, SEND IT and the nameplate. The ballpoint construction line, the marker fill that misses it, and the hand hatching are real craft, closest to Miles' black book. Weak: the paper disc is the brightest thing on screen; icons were loosened too far (the Brace "V" box does not read; turret slices became two rockets); rules text is thin at 1x. A (dot-grid page) beats B (index card), but B's heavier ink outline is better. |
| **2** | **Street graffiti (G1)** | Best cards and best SEND IT of the round (A: wheat-paste paper, Anton tag title with chrome drop, tape type strip, marker rules, drips on SEND IT). The tower is not wildstyle: it is a pink pie with marker trim, and it reads busy. Pink cards (B) are the brightest objects on screen. |
| **3** | **Spider-Verse print (G3)** | The cleanest and most legible; icons survive best; the comic-panel card with a caption box is polished; the kirby-burst hub and the burst SEND IT are on reference. The misregistration is too timid at 1x, so it risks reading as E10 with a filter. Defect: the Twist icon reads as "?". |
| 4 | Zine collage (G5) | The strongest written rules and a ransom alphabet nobody else has. On screen, A's black tower sinks into the dark board (the owned mass disappears) and ransom titles are slow to read. B's cream tower fights the HOT marks. |
| 5 | Arcane painterly (G4) | The procedural bristle reads as scratch noise, not Arcane brushwork, and is gone at 1x. The dark tower with pink spokes loses the owned mass. Only the neon doodle layer is worth keeping. |

### Finalist F1: BLACK-BOOK BURNER (sketchbook graffiti + street graffiti)

*The Cell drew its own board in its black book, then pasted it up on the wall.* The tower is a black-book page (G2). The cards, SEND IT and the YOU strip are wheat-pasted burner pieces (G1). One pen links them: the pink chisel marker plus the ballpoint blue.

**Tower (r 0-196, see 2.1)**
- **Disc:** dot-grid page, but not white: `PAPER` multiplied to 72 percent value (#AEAAA4 range) with a 6 percent dot grid; the slices then carry the light. Brightest large fill on the tower is L* 75 or less. Torn edge on the disc rim, 2 tape strips (kraft #C69A62) at 30 and 210 degrees only, never on the HP ring or a pip.
- **Slices:** pink chisel-marker fill (`CELL_PINK`) that misses the ballpoint construction line by 2 px; ballpoint (#2C3E9E) construction arcs visible inside the slice at 20 percent; the shadow side is a ballpoint single-direction hatch (never cross-hatch: L7 is reserved for loss at END TURN; G2's slice shading must change). Heavier ink outline from B (5 px tapered `ZINE_INK`) plus a 3x4 px block drop toward bottom-right, so the wedge reads as a graffiti letter piece.
- **Icons:** the E10 silhouettes, re-inked in marker, 44 px, white with ink. No re-designs: turret stays one turret, Brace stays the clamp, shield stays the shield. Texture stops 6 px from the icon.
- **Hub:** street-graffiti throw-up bubble (G1 A) in pink with chrome #C9D3E0 highlight and ink outline; "BREAKER" in Permanent Marker. The player HP ring wraps the hub (2.2).
- **Guns:** pink marker stroke with ink key, tapered, ending in a hand-drawn starburst at the hit.
- **Doodles:** star, spark, arrow, X and zig from the G2 kit, max 4 on the tower, on the disc margin only (between slice rim and threat trim), never over a pip, an HP block, a ring cell or a threat mark.

**Cards (G1 A wheat-paste, upgraded)**
- Torn wheat-paste paper at 88 percent value, a dark wall-colour art band (#221D2A) with a pink spray burst behind the icon (spray fade, no halftone), the Anton tag title in pink with chrome highlight, ink outline stack and 3x4 drop, the kraft tape type strip (TOWER / WAVE), rules in Permanent Marker at 18 px minimum with ballpoint underline. The RAM coin stays S cyan (system resource). The loud Trace tab stays violet.
- Hand is scaled 1.15 from E10 and fans 4 degrees per card. Lifted card: the pink offset print behind it (from hover).
- **SEND IT:** G1 A spray slab with chrome tag letters and max 3 drips. It is the single brightest object on the screen.
- **Nameplate and YOU strip:** taped wheat-paste paper, tag lettering. YOU blocks are marker blocks in `GAIN` with the L7 hatch for pending loss.

**What it must prove:** in greyscale at 320 px the tower reads as drawn (rough line, hatch, block drop) and the board reads as clean glass.

### Finalist F2: ZAUN PRESS (Spider-Verse print + Arcane neon)

*The Cell prints its own comic on a stolen press in Zaun, then tags it in neon.* Everything the player owns is a misregistered comic print (G3 A). Over it sits one neon doodle layer in Jinx's hand (from G4). The enemy and the machine never misregister.

**Tower (r 0-196)**
- **Disc:** G3 A paper page, multiplied to 70 percent value, inked key plate at varied weight (heavy on the shadow side, 2-6 px).
- **Misregistration pushed:** the pink plate sits **4 px** off the key plate and the press-cyan plate (#20B8E6) peeks **3 px** on the other side, on every P shape (slices, hub, HP blocks, card frames, SEND IT). This is the signature, so it must read at 1x; 2 px did not.
- **Slices:** flat pink with a darker shade plate (#C4167A) on the shadow half, hand hatching for form (single direction), icons in ink seats (G3 A).
- **Hub:** kirby burst with Ben-Day dots at 10 percent (the only dots on P; the hub art and the card art band only).
- **Neon doodle layer (Arcane):** pink neon marker doodles (crown, spiral, heart, X, zig) with a **hand-painted** look, max 4 on the tower margin, max 1 per card. It is paint, so it does not glow (no bloom; the "neon" is saturated pink with a white core stroke). One painted brush highlight on the tower rim at 10-11 o'clock (Arcane rim light), white at 40 percent, tapered.
- **Guns:** inked pink tracer with a 2 px cyan misregistration fringe.

**Cards (G3 A comic panel, upgraded)**
- Comic panel: kirby speed rays in the art band (pink on pink shade), Ben-Day dots at 10 percent max, Anton title in an ink caption bar with pink offset, type tag as a slanted ink tab, rules text in a caption box (IBM Plex Condensed, 18 px minimum).
- New icons where G3 failed: Twist must be a ring arrow, not a hook (use the E10 Twist glyph re-inked).
- **SEND IT:** the G3 A burst sticker, misregistered, the brightest object on screen.
- **YOU strip:** printed paper strip with the same offset, taped in kraft.

**What it must prove:** the misregistration and inked contour read at 1x in colour and in greyscale (double edge on everything ours, single clean edge on everything else).

### Rules both finalists share
- Peak value order (brightest first): SEND IT, HOT threat marks (T), the lifted card, P tower slices, the rest of the hand, E cells. The paper disc and the paper cards never out-value the HOT marks.
- No P texture within 6 px of an icon, an HP block or a pip. No decoration on the board outside r 0-212.
- Paint never glows; dots only in the hub and the card art band (F2), none at all in F1.
- Both finalists render the **full set**: p1_decide, p1_nowords, p2_preview, p2b_hover, p3_resolve on f1 / f2 / f2t / f2b, the bio room plus one srv or gh room, the 320 px squint (colour and grey) and the deutan / protan / tritan sheet. A finalist delivered on the E10 board is not reviewed.

---

## 2. Board and grammar direction (both finalists)

### 2.1 Layout: use the freed rim
The wave queue (2.6) frees r 470-510. Spend it on the player:
- Tower grows from r 162 to **r 196**. Threat trim sits outside the tower at r 200-210.
- Rings NOW / +1 / +2 are re-spaced into r 214-430; landing arcs at r 436-470. If any unit glyph drops below 44 px or any cell below 30 px deep, cap the tower at r 184 and report.
- The board keeps its 24 px screen margin. The card hand grows 1.15x.
- E family material for cells, tokens and enamel: start from the effects stream's stand-in painter (slate glass, helix motif, enamel 1.5 px), which already reads as new.

### 2.2 HP (note 3): cross-hatch, picked
Option A, cross-hatch. B (hazard stripe) is too loud and reads as a hazard, and C (drain core) looks like the +1 forecast.
- **The player HP ring moves off the rim and wraps the hub** (r 52-64, 15 blocks in 3 groups of 5). Three streams flagged red pending hatch merging with the red threat trim on the rim; this ends that, and the player's life sits at the heart of the tower.
- On any segment thinner than 9 px, L7 becomes a **single-direction 45 degree hatch at a 4 px pitch, 1.6 px lines**, and the pending segment is **2 px thicker** than lit ones (it bulges outward), with the solid edge in the cause colour. Two-direction hatch only where the segment is 12 px or more (HUD YOU strip, slice pips if they reach 10 px, unit cells). The hatch must still read at 320 px: if it collapses to solid red, widen the pitch, never drop the hatch.
- Hatch colour = cause: `HARM` red = enemy, `SOAK` = your soak, `CELL_PINK` = us.

### 2.3 Time (note 2): A "heat" with a light frost on the future
Option A (value, glow, END notch, turn pips) carries the read, including greyscale. Add one part of C, without the blur: the glass of ring +1 cells at 80 percent value and ring +2 at 62 percent, so the future recedes as a block. No blur: C's blur weakened the +2 arcs.
- HOT: solid, full chroma, Bold, L9 glow, END notch. COLD: solid, one tier thinner, 70 percent value, 45 percent chroma, one turn pip. FAR: 50 percent value, 25 percent chroma, L8 dotted, two pips.
- **Cold chevrons lift:** they read dark brown. COLD harm is #D9877C (solid, no glow), not a darkened HARM.
- **Dots are rationed (new):** L8 dotted applies to **marks only** (threat trim, landing arc, unit token ring). Structural outlines (ring rims, cell outlines on ring +2, ticket edges, the board rim) are never dotted: FAR structure is a solid hairline at 50 percent value. `plate_base.png` has dotted ring rims all round the board; at a glance that is dashes again.

### 2.4 Colour (note 5): legend accepted, two changes
- **SOAK returns to #3A7EF3** (E10's value). #464EFF fails protan against `TRACE_VIOLET` (dE 2.4), the same failure E10 already fixed. Re-check #3A7EF3 against `NET_CYAN` in all three sims (value contrast expected to hold).
- **Motion colour:** while hovering, every motion mark is the plan (`PLAN` pencil, L6 + L5). When it resolves, it takes the colour of its owner: `CELL_PINK` for anything a card does (Spin, Nudge, Twist, Pull, Shove), `SCHEDULE` orange only for the clock (rings step and turn at END TURN, Hold's schedule slide). Yellow never appears in resolve.
- Pink vs HARM passes in all sims (tritan 23); no fallback pink.

### 2.5 Line audit (note 2): accepted
The 12-item audit is accepted as written, with 2.3's dot ration. No dashed line remains. Hollow is growth on chevrons only. The arrowed outline (L5, note 4) is kept for movement.

### 2.6 Waves (note 6): A, the ticket queue
Option A, three tickets top-left plus one feed arrow, frees the whole rim. B (rim lane) is cluttered.
- Ticket edges are solid; time is by value (W6 50 percent, W5 70 percent, W4 full) and pips, not dotted edges.
- Tickets grow to 84x64 px so glyphs read at 24 px. The feed arrow (neutral enamel L5) ends at the bezel; it may end at the rim, since the sim has no fixed entry angle.

---

## 3. Effects (note 7): pruned and directed

Families stand as built (P protect, H harm, D damage, L life, M motion, C corp, S system, T commit); they are distinct in greyscale on `fx_00_overview`. P effects are re-skinned per finalist: F1's protect plate is a taped black-book page with a marker double line; F2's is a printed panel with an inked double line.

**Build for the finalist resolve plates (core, 22):** `fx_shield_block`, `fx_brace_block`, `fx_soak_take`, `fx_shield_break`, `fx_hit_land`, `fx_slice_crack`, `fx_slice_break`, `fx_hp_through`, `fx_gun_hit`, `fx_strike`, `fx_trigger_hit`, `fx_kill`, `fx_ricochet`, `fx_refund`, `fx_spin`, `fx_twist`, `fx_rings_step`, `fx_hold`, `fx_pull`, `fx_shove` (+ bump), `fx_wave_enter`, `fx_commit`.
**Keep, lower priority:** `fx_firewall_burn`, `fx_grow`, `fx_ward_on`, `fx_trace_add`, `fx_repair_mend`.
**Merged:** `fx_worm_wear` is a variant of `fx_hit_land` (adds the hook mark only). `fx_adjuster_strike` is `fx_hit_land` with a gold rim flash. `fx_armor_bounce` and `fx_ward_bounce` become one `fx_ricochet` (steel or gold streak).
**Parked (latent in Solace, no state shows them):** `fx_jam`, `fx_shield_pop`, `fx_boss_phase`, `fx_lockdown`.
**Still only, no anim:** `fx_clear` (the GAIN check on the arc).

Fixes:
- **Shield block vs shield break (the designer's example) must be told apart in one frame:** block = intact P plate, pink, chevrons stop and spark white at its edge; break = the same plate in 5-7 shards, red halftone flood behind, wedge goes dark. Keep them on one sheet side by side.
- `fx_brace_block`: show the landing arc stopping at the clamp.
- `fx_soak_take`: straighten the funnel on the wedge axis.
- `fx_hp_through`: render with the board and HUD in frame; diamonds fly along one smooth curve.
- `fx_firewall_burn`: too tall and white. A pink flame-stroke band inside the sector column, max 60 percent of each cell's depth, no white cores.
- `fx_pull`, `fx_shove`, `fx_twist`: pink at resolve (2.4), not yellow or orange.
- Halftone flood (FX-H) stays the X family's. If F2 wins, F2's P dots stay inside the hub and the card art band at 10 percent, so the flood never confuses with the player.
- Every effect keeps a reduce-effects still and the 3-flashes-per-second cap.

---

## 4. Hover (note 9): pruned and directed

The dimming is kept (designer's call) and the grammar key is accepted with these changes.
- **Dim:** value x 0.40, chroma x 0.45 (closer to the E10 k 0.38 the designer liked; 0.50 was too soft on the overview).
- **All motion in hover is pencil** (2.4): the L5 channel is `PLAN` yellow with ink edges. Pink and orange L5 appear only in resolve.
- **FOCUS brackets:** corners only, 12 px legs; legal 2 px, aimed 3.5 px. No full-cell lime outlines (some cells on `hover_trigger` read as outlined).
- **Plates (11):** h01 turn the tower (Spin3, with Spin2 and Nudge as two inset strips, not separate plates), h02 Brace, h03 Trigger (f1, plus the refund variant after Twist), h04 Twist, h05 Strike, h06 Shove (bump as an inset), h07 Pull, h08 Hold, h09 Firewall, **h10 soak toggle and h11 unit hover (missing; required)**. Nowords for h01-h04.
- The review-note card is moved off the plate (into a slip under the frame); it covers the room and adds words the game does not show.
- Re-render all hover plates on each finalist's art, after the finalist p1 plates are approved.
- Swapped-in cards (cards not in the approved f2 hand) keep their slip note; the state is unchanged.

---

## 5. Who does what next
1. F1 and F2 streams: full plate set on the redesigned board (section 2), per the finalist direction.
2. Grammar stream: render the board base for both finalists (layout 2.1, hub HP ring 2.2, frost 2.3, dot ration, SOAK #3A7EF3, tickets 2.6) and hand it over first.
3. Effects stream: re-skin P effects per finalist; build the core list on the board base.
4. Hover stream: plate list per section 4, after the finalists.
5. Designer: confirm the "arrowed outline" reading (hover path and the THIS TURN schedule cell) and pick F1 or F2.
