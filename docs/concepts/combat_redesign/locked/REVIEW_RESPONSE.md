# Response to the independent AD review of 2026-11-03

Review: `D:/Godot/rebel_cell/docs/reviews/ad_review_overnight_2026-11-02/AD_REVIEW.md` (captures A01-A11).
Responder: art-pass, 2026-11-03.

**Rule for this response (designer, 2026-11-03).** "If I explicitly approved something then it should be captured in a document so the reviewer doesn't think differently. A review response is either an issue with implementation or with the documentation. Make a call, update documentation, update implementation where needed."

Each finding gets one of four classes:
- **DOC**: the plate follows an explicit designer ruling that the documents did not record. The ruling is now written into `VISUAL_PLAN.md` ("Designer rulings") and, where it amends a LOCKED section, into `ART_BIBLE.md`. The plate stays.
- **IMPL**: the plate is wrong against the documents. It is fixed in the rebuild.
- **DOC+IMPL**: the ruling stands and is now recorded, but the way it was drawn is wrong. Both are fixed.
- **RULES**: a game-rules question for the GDD, not an art call.

The designer's explicit rulings are quoted in `VISUAL_PLAN.md`, "Designer rulings (binding)". The rest are art-pass calls, marked as such and open to the designer.

## S1

| # | Finding | Class | Call |
|---|---|---|---|
| 1.1 | Occupied and empty enemy cells look the same | IMPL | Accepted. Occupied cells get a visible glass wash and a programme screen (L* 40-45, empty cells L* 28), HP ticks readable at 1x, and a width read. A new check fails the plate below 3:1. **2026-11-04 (gate 1) correction:** the L* pair was a target that cannot meet its own floor (L* 45 over L* 28 is 2.6:1; 3:1 needs the brightest empty at L* 26 or less). Measured now, against the brightest single empty cell of each ring: occupied NOW 42.7-47.8, +1 38.7-39.7, +2 33.9-35.6; brightest empty 20.6-24.0, 17.0-20.5, 14.6-18.2; lowest ratios 3.20 / 3.44 / 3.15. |
| 1.2 | The value order is inverted | IMPL | Accepted. The THIS TURN sweep and the clock go down to gunmetal at L* 45-55; HOT chevrons go up to second place under SEND IT; token discs are capped. A.1 now lists the clock. A new check sorts p95 L* per family. |
| 1.3 | Corp hue on a ring breaks 2.4 LOCKED | DOC+IMPL | The designer explicitly asked for corp-themed enemy layers: "prefer the corp layers have more of a theme related to the corporation, even if just a color shift". That ruling is newer than 2.4, and 2.4 now records it as a combat-ring exception. The way it was drawn is wrong: hue on the cell fill flattened the occupied/empty read. **Call:** the theme is carried by material and by hue on the rim, lip, crest and cell edges. Cell fills stay a neutral slate ladder, with only a low-chroma tint. The corp hue must sit at dE 15 or more from Cell lime, GAIN, FOCUS and HARM (this was the reason behind 2.4). |
| 1.4 | COLD is lost on Meridian | IMPL | Accepted. COLD gets a keyline and value separation on every skin, checked by the token dE test against each skin's cell colour. |
| 1.5 | The bill is unreadable | IMPL | Accepted. Labels are at least 16 px cap height (Mono 23 = 16.1 px; 2026-11-03 correction: Mono 18/22 measured 12.6/15.4 px); numbers become digits with the tally as a second mark; NEXT is at 70 % value; SPLIT gets written operators. A new cap-height check is added. |
| 1.6 | Effects are drawn above the HUD | IMPL | Accepted. Effects go under the HUD and the hand (ART_BIBLE 6.4); only hp_through, refund and trace_add may cross it. |
| 1.7 | Transitions were reported DONE with CONCEPT frames | IMPL | Accepted. T5/T6 key frames are rendered from the generator with no CONCEPT stamps, and K1 shows the room at a readable level. The process rule now reads: a step is DONE only if no frame carries a CONCEPT badge. |
| 1.8 | GAIN green on enemy kill marks | IMPL | Accepted. Kill marks and kill ghosts move to the cause colour (CELL_PINK for our kills). FOCUS keeps its four corner brackets only and never marks a dead unit. |

## S2

| # | Finding | Class | Call |
|---|---|---|---|
| 2.1 | Eleven techniques on one deck | DOC | The designer explicitly asked for this (ART CALL 53): "use different card background art pulling from the other punk card art styles". The deck is tied together by the WPAP frame, the black key line, the pink spot disc, the xerox icons and the shared print grain. No change, beyond keeping that shared kit strict. |
| 2.2 | Card type colours collide with meanings | DOC+IMPL | The designer explicitly wants "different color behind WAVE etc.", and ruled "I don't think we need to avoid any colors". So the reviewer's single bone plate is rejected, and each type keeps its own hue. **Call:** within that freedom, art-pass picks type hues at dE 15 or more from the meaning tokens they sit next to (SOAK, SCHEDULE, BOSS_GOLD, TRACE), since nothing is lost by that. The tokens are re-picked by the palette-collision check. Spin 3's band moves off BOSS_GOLD. |
| 2.3 | Played slots are wireframe cages | IMPL | Accepted. They become the torn-paper outline (VISUAL_PLAN B), flat with no perspective skew. |
| 2.4 | Hover duplicates the HUD | IMPL | Accepted. One NEXT row per option, as in ART_BIBLE 3.22. |
| 2.5 | Pencil is not pencil | IMPL | Accepted. Pencil is 7 px wax with a 3 px ink edge and grain (A.5). The "( 9 )" brackets are retired; the HUD rows get room for a real ring, and nothing is drawn over the HP strip. |
| 2.6 | Hand collisions on hover | IMPL | Accepted. New checks: the hand stays clear of SEND IT and UNDO, and the lifted card stays clear of the neighbouring card's cost and rules line. |
| 2.7 | Card bottoms are clipped | IMPL | Accepted. The whole card shows, with a 12 px margin above y=1080. |
| 2.8 | The room grade switched the room off; the room is iso, not perspective | DOC+IMPL | The camera is DOC. The designer picked the iso cutaway in ART CALL 47: "Some light procedural generation work to define the interiors, then we just toss that up. Seems like easiest and keeps on brand." ART_BIBLE 3.14 now records that regular Site fights and HQ-run nodes use the cutaway room, and the boss fight keeps the HQ perspective close-up. The grade is IMPL: the room comes back to a readable level (room mean L* 28-34, board still first by the family order check). Meridian gets a non-Solace room, and the city strip gets a seam treatment. |
| 2.9 | The clock family uses three materials | IMPL | Accepted. One machined gunmetal material, engraved, with SCHEDULE orange on the live step only. |
| 2.10 | Effect loudness order is inverted | IMPL | Accepted. Damage > kill > block > state. fx_grow and fx_ward_on are quieted, and fx_gun_hit is lifted. |
| 2.11 | The resolve beat takes 12.7 s | IMPL | Accepted. The whole beat runs under 4 s with skip; every effect fits the 0.6 s T2 cap; no per-effect overrides. This answers the overnight question, as an art-pass call. |
| 2.12 | FAR trim has no key | IMPL | Accepted. The FAR mark carries its number (ART_BIBLE 3.22, "a number always goes with it"). |
| 2.13 | The Adjuster cell has hatch and beads | IMPL | Accepted. The hatch is removed (hatch is reserved for loss at END TURN), and the bead row becomes a solid gold edge. |
| 2.14 | Wave tickets are unreadable | DOC+IMPL | Compressing W4+ into tickets is the designer's (ART CALL 51 note 6), so the tickets stay. Their glyphs go to 16 px or more at full value, and the wave count is shown once. |
| 2.15 | The tower is too loud | IMPL | The designer asked for punk rock but never ruled on value. **Call:** readability first (ART_BIBLE 1.1). Slice inks sit at L* 60-72 and the icon discs carry the peak. The punk read is carried by texture, key line and halo. This answers the overnight question, as an art-pass call. |

## S3

| # | Finding | Class | Call |
|---|---|---|---|
| 3.1 | The HOLD icon looks like a pause button | IMPL | Redrawn as a clamp on the ring step. |
| 3.2 | FIREWALL and TWIST share a band | IMPL | Each card gets its own motif. |
| 3.3 | The unaffordable state is just a brown card | IMPL | It gets a lock glyph on the cost and a "NO RAM" word. |
| 3.4 | Cyan scribbles on TRIGGER | DOC | Any colour is allowed in card art (designer: "I don't think we need to avoid any colors"). NET_CYAN keeps its meaning on HUD marks only. |
| 3.5 | Heat shown as emoji flames | IMPL | Replaced with the atlas Heat glyph. |
| 3.6 | The REFUND tag is a terminal plate inside the wheel | IMPL | It moves to the HUD edge, or uses the P sticker material. |
| 3.7 | "WITHOUT TWIST 00 -> \|" tally | IMPL | Shown as digits. |
| 3.8 | The BEST LINE chip uses PLAN yellow | IMPL | It becomes a neutral chip with a star. |
| 3.9 | Three RAM treatments | IMPL | One RAM treatment. |
| 3.10 | The FX-P block plate uses card stock | IMPL | It gets its own stock (pink-tinted paper). |
| 3.11 | The resolve log text is small | IMPL | At least 16 px cap height. |
| 3.12 | Transition bits are white | IMPL | The bits take the colour of their source (ART_BIBLE 1.2). |
| 3.13 | Brace hover: the tower stays at full value | IMPL | The non-aimed slices dim too. |
| 3.14 | The hatch on YOU segments reads as solid | IMPL | The YOU segments get bigger, or the hatch period is widened at 1x. |

## Rebuild status, stage 2 (2026-11-03)

Stage 1 fixed S1 and most of S2/S3 (`final/NOTES.md`, "2026-11-03 rebuild"). Stage 2 did the rest of the IMPL items and published the set into `final/` and `backdrop/`. Where a call above was refined in the doing, the refinement is written here and in `VISUAL_PLAN.md` (dated 2026-11-03 stage 2).

| # | Done as | Refinement of the call (art-pass) |
|---|---|---|
| 1.5 | Digits (Anton 24 / 22) with the pip tally as a second mark; typeset Anton 40 operators; SPLIT written as ABSORBED + SOAK + YOU; NEXT row at 70 % value | NEXT tallies are **filled COLD** (45 % chroma, 70 % value), not hollow. Hollow read as zeros at 1x, and VISUAL_PLAN C reserves hollow for growth chevrons. VISUAL_PLAN D's "hollow outline" row is amended to match. SPLIT drops the route arrows and destination icons on the words plates (nowords keeps its drawn operators). |
| 2.3 | Played slots are flat, upright torn dark-paper liners with a paper rim, the ghost glyph, and the name over PLAYED in Mono 21 | Upright, with no fan angle, so nothing reads as a perspective cage. |
| 2.7 | The whole hand is on screen, with the lowest pixel ≥ 12 px above y 1080 on every plate (measured, `checks.json` `stage2_measures`) | Rules text wraps to two lines at a word break rather than shrinking. The same fix makes card text pass check c. |
| 2.8 | rb2-1 room grade; Meridian on the shop room; seam treatment | **Gate:** room mean L* 28-34 in the rb_checks room region (x ≥ 1100, y ≥ 420, r > 505, with UI, hand and hover tag cut out, and the UI scrim slabs wherever they darken the room by 15 % or more). The scrims are UI ground: on p2 and p3 they covered half the region and pulled its mean to 25 while the room itself read 32. The room's p95 must sit below the **ring-NOW** occupied glass p95, by 1. When no ring-NOW cell is live (p2b: the hover dims ring NOW, and the only live unit left at full value is on ring +2, whose glass is L* 32 by the ring-depth grammar, p95 37), the reference is the occupied ring-NOW glass floor, L* 40. Comparing the room to ring +2 glass on a hover plate would test the hover dim and the depth grammar, not "board first". **Seam:** the hull follows the cutaway box. One blur ramp runs across the box edge, the city keeps 30 % of its chroma, and the haze takes the room's own light near the box, so the neighbouring facades read as one lit street. **Meridian:** the shop (the only kit room without a Solace sign) under an amber corp light. The room is where the review's summary allows corp colour ("colour on crest, lip and room"). The camera stays the cutaway (DR-9). |
| 2.14 | Tickets stay (DR-1). The tag, kind glyphs (23-27 px of ink, p90 L* 97-99, `checks.json` `stage2_measures`) and bars are at full value. Time is on the ticket edge and pips only. The count shows once, in the header chip | The header pips are dropped on the words plates. nowords keeps them, because it has no number. |
| 3.5 | Heat is the atlas Heat glyph (`ATLAS_BURN`) in `CRT_AMBER` with an ink outline | |
| 3.6 | The REFUND word is a terminal tab under the RAM coin it returns; the wheel keeps only the refund coin | Of the two options, "HUD edge" was taken: the word sits next to the resource it changes. |
| 3.7 | WITHOUT TWIST shows "2 → 1" as digits | |
| 3.11 | The resolve log text passes check c (≥ 16 px) | |
| 3.14 | YOU segments are 13.6 x 22 px, with a two-direction hatch at a 5.4 px pitch and 1.5 px lines | |
| check c | Passes on every plate, card text included | Plex 21 rules text on one or two lines; NO RAM Anton 17; played-slot words Mono 21. |

## Gate 1 (2026-11-04): the independent gate on stage 2

The gate failed three items and listed claims that were wrong or missing. Each is classed as before: an implementation issue (IMPL, fixed in `corp/src` and re-published in `final/` and `backdrop/`) or a documentation issue (DOC, the call written into `VISUAL_PLAN.md` dated 2026-11-04). The numbers are in `final/NOTES.md`, "2026-11-04 gate 1".

| Gate item | Class | Call |
|---|---|---|
| 1.2 "HOT second under SEND IT": HP ticks, sector digits and the NOW W1 tag outranked HOT; check b had no rows for them | IMPL | Every E, K, T and N mark class and the gun tracers and hit stars get a row in check b (p95, p99, median); p99 at least 1 under the HOT p95, and every E and K p95 at least 1 under the tower p95. HP ticks go to `CREAM_HP` #DBD1B7 and K type (digits, ring tags, W tags, ticket glyphs, nowords tallies) to `K_TYPE` #CBD2DB, both L* 84. The hit star goes to `HIT_PAPER` #DED8CA, the twist badge to PLAN at 86 % value, and the Adjuster skull to the token glyph value. Highest mark p99 on any plate: 92.7, under HOT 94.2. The armour rail edge goes to `STEEL_HI_E` (row below). Thin 1 px ring and band lines are not yet covered (row below). |
| 2.14 "full value" on the tickets | DOC | "Full value" means the K type value, L* 84, not white. The ticket gate is glyph p90 L* 84 ± 4 (measured 86.3-87.8). |
| Check d: TURRET #D6A33A vs BOSS_GOLD dE76 9.6; the check skipped BOSS_GOLD | IMPL | TURRET is olive #AEB24E. Check d tests every slice ink, card type colour and skin ink against every token and the light neutrals: 0 failures, lowest pair 17.3. |
| 3.8 BEST LINE still PLAN yellow, no star | IMPL | Neutral chip (TEXT_HI type and filled star, TEXT_MID edge); the best and selected option chips get a neutral TEXT_HI edge. PLAN stays on pencil and what-if only (VISUAL_PLAN A.5). |
| Check a held against the mean empty, not the brightest; the dying Worm read darker than an empty cell | IMPL | Check a uses the brightest single empty cell. The dying unit keeps its lit glass and shows its loss as the L7 cross-hatch in the cause colour with a solid L7 edge (VISUAL_PLAN B); it is gated like a live unit. |
| The hover tag text was not captured | IMPL + DOC | It is captured and reported as parked (designer note 8), not gated. Any text outside the hooked drawers fails check c. |
| `cards_all_fields_drawn` was false | IMPL | The checker reads the wrapped rules text as drawn; it is true. |
| The tower-zone squint went up and was not reported | DOC (open) | Reported per plate: 57.0-68.7 % loud vs the 50 % target, **not met**. The squint's loud line (about L* 43) cannot coexist with the 2.15 prescription (slice inks L* 60-72). Call: the tower is gated by value (b), and the squint is reported only. Open question for the designer (VISUAL_PLAN A.1). |
| The room gate on p2 / p3 holds only with the scrim cut | DOC | The scrim slabs are UI ground and stay. The gate stays on the room itself (28-34), and the as-seen value (scrim kept) is now reported too: p2 25.3-25.6, p3 24.7-24.8, p1 29.8-30.1. |
| HOT chevron vs its own cell 1.90:1, below COLD 2.63 | DOC | Lit ring NOW glass (1.1) lowered the fill ratio. HOT is carried by fill, white-hot core (3.2 px; core vs cell 4.86:1), keyline and notch; both ratios are reported, and HOT keeps the highest peak (VISUAL_PLAN A.3). |
| Doc numbers: 1.1 "L* 40-45, empty 28"; A.2 "21 / 16 / 12" | DOC | Replaced by the measured values (1.1 above, VISUAL_PLAN A.2). |
| Adjuster plate and hit star hid about 2.5 of 10 HP segments | IMPL | The track splits around the plate; 0 px covered. |
| p3 log said "Payload dead: refund" | IMPL | It reads "Packet dead: refund", from the state's tlog. |
| Solace porcelain #E6EFE4 dE 4.7 from PAPER | IMPL | Celadon #B8DCCC. Skin inks are now tested against the light neutrals too. |
| The reviewer's probe boxes no longer land on what they name | IMPL | `corp/src/rb_probes.py` re-aims each box from the plate's masks; `final/checks.json` `review_probes` gives each box with its reading on the named pixels and on the whole box. |
| Found in gate 1: the armour rail edge read L* 100 on the ring +1 tray | IMPL | `STEEL_HI_E` #C4CBD8; the gate's tray probe drops from p95 96.1 to 90.8. |
| Found in gate 1: thin 1 px ring and band lines (ring NOW outer boundary, schedule band edges, the tape-end crescent) peak at L* 95-100 after the LANCZOS downsample | IMPL | **Not done.** They are not capture classes, so check b does not see them (`final/NOTES.md`). |
| Not re-rendered in gate 1: 1.6, 1.7, 2.4, 2.5, 2.6, 2.10, 2.11, 3.9, 3.10, 3.12, 3.13 (hover, effects, transitions) | IMPL | **Corrected 2026-11-04 (round 2 docs pass):** this row was true only during gate 1. All three sets were re-rendered on the gate-1 board in round 1 (2026-11-04 03:36-06:01; `REVIEW_REBUILD.md`, "Stale docs"). In round 2, hover, transitions and backdrop were re-rendered again on the round-2 board; effects were not. The status of each item is in "Round 2 (2026-11-04)" below. |

## Transitions re-render (2026-11-04): 1.7 and 3.12

`transitions/` is re-rendered on the board published in `final/`, on both skins. Numbers: `transitions/NOTES.md`, "2026-11-03 rebuild", and `transitions/metrics.json`. All values are CIE L*.

| # | Class | Done as | Call |
|---|---|---|---|
| 1.7 | IMPL | Every T5 and T6 key frame is rendered at 1920x1080 by `transitions/scripts/render3.py` from the board generator's own layers. They recompose the published plate to within 2/255 and are never enlarged. No frame carries CONCEPT. K1 is the bare room as T4 leaves it: frame mean L* 28.2; in the review's room box (1200-1800 x 450-800), mean 47.8 and p95 80.3. It is never black. | **Implementation.** The O-30 K1 used the graded room without the board (frame L* 20.1), which read black. K1 is now T4's last frame. The room dims to the plate's grade from K2 to the lock, as the v3 storyboard and port spec 10 already said. T6 ends on the same room. Badges are now REAL, RENDER (generator from the board layers) and COMP. |
| 1.7, T6 FAIL | IMPL | The FAIL keys are the netrun_fail design A generator (`nf_trans.py`) on the published plate. K6 equals `A_crt_feed.png` (difference 0). | **Implementation.** The v3 concept terminal frame is retired. The screen is design A, the art-pass pick O-26. |
| 3.12 | IMPL | Each bit reads its colour from the board pixel it becomes (T5) or leaves (T6): the 90th percentile of C*ab over a 9 px disc, with L* held in 55-80. White-hot `HIT_PAPER` for 80 ms, flipping every 70 ms, tumbling, round the rim. 0 of 3593 T5 draws and 0 of 3319 T6 draws cross the wheel face (neutral). | **Implementation.** ART_BIBLE 1.2 was the rule and the old bits broke it: fixed skin colours, near white (L* about 89). The skin fields `bits_rings` and `bits_accent` are retired (port spec 7 and 10). The neutral ring +1, +2 and frame-band bits are slate grey-blue (C* 7-11, L* 55 median), because those rings are neutral slate by call 1.3. That is their source colour, not white. |
| T5 / T6 story | DOC | The ruling is now recorded as `VISUAL_PLAN.md` DR-10 (ART CALL 49 items 5 and 6). | **Documentation.** The designer's words fix what T5 and T6 show. Bits option A (O-25) and failure screen A (O-26) are art-pass picks. |
| Found in the re-render | IMPL | The tower's drop shadow stayed on the room at the end of T6 (max 10/255); it now goes with the core sweep, and the last frame equals the bare room (0). The T5 card-deal trail now goes white-hot and flips like every other bit. The spinner now has the storyboard's 4 % overshoot (the code had 1.4 %). | |
| Not done | IMPL | **Not done:** the T4-reverse iris and pull-out inside T6. Composited, it fails the strict tile flash test (5 pairs in 0.8 s, limit 3). So `t6_A.gif` holds on the room, and the storyboard K4 is the v3 street composite (COMP). The worst 120 px tile sits at the limit, 3 in any 1 s, in T5 and T6 (WCAG 0). Board defects carried in the plate layers are the board owner's (`transitions/NOTES.md`, Not done). | |

## Status after rebuild round 1 (2026-11-04 07:30)

The full per-finding table, with measurements, is in `REVIEW_REBUILD.md` (internal final review plus gate 2). Summary:
- **S1:** all 8 are FIXED or DOC.
- **S2:** 2.5 (board pencil on p2 and p2b) and 2.6 (hover h02 slot-0 lift) are NOT FIXED. Every other S2 is FIXED or DOC.
- **S3:** all are FIXED or DOC.
- **New defects found in round 1, being fixed in round 2:**
  - FOCUS brackets on board p2b are drawn in Solace leaf, not FOCUS #D4FF00, and as a joined bar, not four corners.
  - Bezel cube-glyph discs and 1 px ring and band lines peak at L* 95-100, above HOT, and check b does not see them.
  - Ring NOW token discs fail the per-disc rule; the rule only passes when pooled.
  - The W5 ticket edge does not show its 70 % step.
  - The h03 dying cell is 2.62:1.
  - The generator draws the wrong TWIST glyph depending on render order.
  - The hover HUD is 45 px taller than the board HUD.
  - Stale docs: VISUAL_PLAN G, final/NOTES, and the "not re-rendered" row above. (Fixed in the round-2 docs pass, 2026-11-04.)

Round 2 makes art-pass calls on the open questions in `REVIEW_REBUILD.md` and records them here when it lands. (It has: "Round 2 (2026-11-04)" below.)

## Round 2, board stage (2026-11-04): R1_REREVIEW build order steps 1-2

The board generator items of `R1_REREVIEW.md` as art-pass called them (C1-C18), re-rendered on all 15 board plates and measured on the published PNGs. Numbers: `final/NOTES.md`, "2026-11-04 round 2"; rules: `VISUAL_PLAN.md` (dated round 2). Hover, effects, transitions and backdrop are later stages (build order 3-4) and are **not** re-rendered here. (Later in round 2, hover, transitions and backdrop were re-rendered on this board; effects were not. The combined status is in "Round 2 (2026-11-04)" below.)

| Call | Status (board) | What is true on the plates and in the checks |
|---|---|---|
| C14 TWIST glyph by render order | FIXED | The old e10 card library no longer re-registers the KA_* glyphs; `round2/board/c14_assert.py` (p3 Solace, p1_clean, p3 Solace in one process) runs before the publish and must give 0 px difference with the registry intact. |
| C2 FOCUS | FIXED | One drawer (`rb_focus.py`): #D4FF00, four separate 12 px corners. Check d measures drawn colours: FOCUS dE76 0.0, pencil wax 0.5, HOT fill 0.0-2.4, gun tracers 0.4, Adjuster track 0.0 from their tokens; every drawn mark 22.3 or more from the corp inks. Open: FOCUS at its token is L* 94.1, so it cannot also sit 1 under the HOT p95 (94.9-95.4); on board p2b there are no HOT marks, so the HOT rule does not apply there. Designer call before the hover stage (VISUAL_PLAN A.2). |
| C3 bright marks | FIXED | Structure lines, cube-glyph discs and arc marks capped and classed; every bright board pixel inside r 480 sits in a class (unclassed bright px gate). |
| C4 token discs | FIXED | The A.1 rule per disc. |
| C5 tickets | FIXED | W6 / W5 / W4 edge steps measured on the plate (check g); the W6 hazard ticks moved off the bomb's width pips. |
| C1 pencil | FIXED on the board | One drawer (`rb_pencil.py`, the hover set's stroke) on p2 / p2b; wax, ink edge and grain gated on the plate (check f): whole stroke 12.8-13.0 px (13 drawn), wax 6.0-6.1 px (the wax-to-ink blend pixels count as ink), ink 3.3-3.5 px per side, grain L* std 4.3-4.5. The hover set imports it (done in the hover stage, "Round 2" below). |
| C8 HUD rows | FIXED on the board | Option-row space reserved on every board HUD; the row record equals the hover grid (check h). The hover set uses `hud_rows.py` (done in the hover stage, "Round 2" below). |
| C16 / C18 Solace rim | FIXED | Celadon / teal rope; dE76 vs GAIN and the hub HP green measured; the two corp rims compared in luma on `grey_proof.jpg` and in `checks.json` `corp.rim_luma_C18`. |
| C11 HOT core | FIXED on the cell chevrons; OPEN on 4 side-arc marks | Core 3.0 px medial (gate 3), core vs cell 4.92-5.01:1 (gate 4.5), fill 1.93-1.97:1 reported (check i). Every cell chevron core is 3.0 px per stroke; the landing-arc cores are 3.5-4.0 px on the open arcs. Four small side-arc marks on p1 / nowords (two on p2 / p3) read 2.0-2.5 px where the arc's lane line crosses them: not fixed, listed in `checks.json` `i_hot_core.strokes_under_min`. |
| C15 P stock | FIXED / DOC | `P_STOCK` #F6C8DE is a token in `rb_tokens.py` and the VISUAL_PLAN E table; check d covers it. |
| C6 hand lift (board) | FIXED on board p2, with art-pass calls | Straight-up lift, fan never closes, buttons 12 px right, protected set with the title band and the ×3 plate, 0 px covered. To fit under the p2 HUD with its option rows, the lifted card no longer grows (1.00, it was 1.10), its print and drop go right, and the HUD panel gaps are 4 px and the REFUND tab 96 px. The hover plates are the hover stage. |
| C7 dying glass (board) | FIXED on the board | The dying cell is measured over its whole glass, hatch included and guns cut, and gated like a live unit. The h03 case was done in the hover stage (3.98 / 4.19:1, "Round 2" below). |
| C9 / C10 | DOC (unchanged) | Room gate on the room itself, scrim reading reported; the value gate governs the tower, the squint share is reported. |
| C12, C13, C17 | Not this stage | Effects, transitions and hover. Later in round 2: C13 and C17 done; C12 not published ("Round 2" below). |

`REVIEW_REBUILD.md` items closed in this stage:
- **Dying-cell rows on too few px.** Check a now measures the dying glass whole: 3730-4807 px, where it was 198 and 253 px. It reads 4.49-6.07:1 (check a in `final/checks.json`). This line said 4.48-6.06 until the round-2 docs pass; that was `round2/board/work/dying_glass.json`'s own ratio arithmetic on the same cells. The glass between the hatch lines alone reads 3.82-5.25:1 (`dying_glass.json`).
- **Wrong NOTES claims.** The gate-1 lines on the W6 / W5 / W4 edges and on "that one unit" are marked as corrected in place, and the measured values are in `final/NOTES.md` "2026-11-04 round 2".
  - The edges read W6 / W5 / W4 at L* 49.7 / 63.2 / 82.2 (neutral), 46.4 / 58.4 / 75.0 (Solace) and 41.4 / 51.6 / 66.1 (Meridian).
  - The token discs were three units, not one. Each disc now passes on its own.

## Round 2 (2026-11-04)

This section is the record of round 2 as a whole: the board stage above, then the hover, backdrop and transitions stages, which re-rendered their sets on the round-2 board, and this docs pass. The effects stage did **not** publish: `effects/` still holds the round-1 files, on the gate-1 board. It answers the independent re-review `D:/Godot/rebel_cell/docs/reviews/ad_review_overnight_2026-11-02/R1_REREVIEW.md` (S1 0, S2 6, S3 9; exit rule: no S1 and fewer than 3 S2).

How to read it:
- **Class** is as defined at the top of this file: DOC, IMPL, DOC+IMPL or RULES.
- **Status** is FIXED, NOT FIXED or DOC (the ruling or call is written down and the plate follows it). A FIXED item is published and measured. Anything that is not is NOT FIXED.
- **Numbers** are CIE L* (of sRGB luminance) and dE76, measured on the published PNGs. They come from `final/checks.json`, `hover/checks.json`, `backdrop/checks.json` and `transitions/metrics.json`, which the stages measured on files byte-identical to the published ones. Lines marked "docs-pass probe" were measured again in this pass on the published PNGs (`D:/rc_scratch/combat_redesign/locked/round2/docs/probe_plates.py`, `probe_plates2.py`). Effects numbers are round 1's (`effects/NOTES_CDHL.md`, `NOTES_MPST.md`), measured on the 60 fps frames the published keyframes are cut from.
- **Calls C1-C18** are art-pass calls, open to the designer. Only DR-1..DR-10 (`VISUAL_PLAN.md`) are designer rulings.

### Every finding, round 2 status

**Original findings (AD_REVIEW 2026-11-03).**

| # | Finding | Class | Status | Measured (round 2 unless it says otherwise) |
|---|---|---|---|---|
| 1.1 | Occupied and empty cells look the same | IMPL | FIXED | Check a on 15 board plates: live ring-NOW glass L* 42.6-43.2; the brightest single empty cell per ring 20.6-24.0 / 17.0-20.5 / 14.6-18.2; lowest live ratio 3.17 (neutral), 3.31 (Solace), 4.11 (Meridian); p2b 3.15 / 3.38 / 4.35. The dying glass (C7) 49.6-51.2 over 3730-4807 px, 4.49-6.07:1. Hover: check a 26/26, lowest gated ratio 3.10-4.29 |
| 1.2 | Value order inverted | IMPL | FIXED | p1 neutral p95: SEND IT 98.2 > HOT 94.9 > tower 89.5 > hand 83.1 > token discs 82.6 > K clock 69.5 (median 47.8) > E occupied 45.5 > room 37.8 > E empty 21.0. Unclassed bright px (L* 80 or more, r < 480): 0 on all 15 plates and 26 hover plates. Highest p99 of any other class on a plate with HOT: 92.7 (gun tracers and hit stars, p3), against a HOT p95 of 94.9-95.4. The round-1 holes are closed (C3, C4, rows below) |
| 1.3 | Corp hue on a ring | DOC+IMPL | DOC (DR-6) + FIXED | Cell fills neutral slate on every skin. Solace rim (r 491-498) median #3B827F, dE76 61.3 from GAIN and 53.4 from the hub HP green (C16; docs-pass probe: #3A827F, 61.3 / 53.4, 0 % green-hue px in the band). Meridian rim rust, band mean L* 25.1. Every drawn mark 22.3 or more from every corp ink (check d) |
| 1.4 | COLD lost on Meridian | IMPL | FIXED | Meridian lowest cell ratio 4.11; check d 0 failures on every plate (196-273 pairs, lowest 17.3) |
| 1.5 | Bill unreadable | IMPL | FIXED | 98-120 text draws per worded plate, 0 under the 16 px cap (smallest 16.1). Bill plate y 76-427 with the reserved option rows (C8) |
| 1.6 | Effects above the HUD | IMPL | FIXED (round-1 set) | 0 px above the HUD for every effect except `fx_hp_through` (6580 px), `fx_refund` (1091) and `fx_trace_add` (1696), which are allowed. **Not re-rendered in round 2:** the effect bases are the gate-1 board |
| 1.7 | Transitions DONE with CONCEPT frames | IMPL | FIXED | Re-rendered in round 2 (C13). Badges: T5 RGGGGR on both skins, T6 RGGRGR; no CONCEPT frame on T5 or T6. T5 K1 is the bare room: frame mean L* 28.2 (decoded GIF 28.0), the review's room box mean 46.8 / p95 78.6 on the GIF. FAIL K6 equals `A_crt_feed.png` (difference 0) |
| 1.8 | GAIN on kill marks | IMPL | FIXED | Board: the dying cell is the CELL_PINK L7 hatch (`kill_hatch` class). Effects (round 1): 0 GAIN px on every C / D / H effect, and no M / P / S / T effect draws a kill mark; in the beat, both kills 0 GAIN / 0 FOCUS / 0 lime px |
| 2.1 | Eleven techniques | DOC | DOC (DR-8) | `card_sheet.jpg` (round 2): shared frame, key line, pink disc, xerox icons and grain |
| 2.2 | Type colours collide | DOC+IMPL | DOC (DR-5) + FIXED | TOWER #006E66 (type word 5.87:1 on its plate), WAVE #B4AAFF (8.94:1); check d lowest pair on any plate 17.3 |
| 2.3 | Wireframe played slots | IMPL | FIXED | Flat upright liners on p3 (draw asserts 49/49 on every skin) and `card_sheet.jpg` |
| 2.4 | Hover duplicates the HUD | IMPL | FIXED | h04: four option rows (y 307-423) in the one HUD, PLAN px in the rows 0; bill y 76-427 on every hover plate |
| 2.5 | Pencil is not pencil | IMPL | FIXED | Board p2 / p2b (check f): wax 6.0-6.1 px, whole stroke 12.8-13.0, ink 3.3-3.5 a side, grain L* std 4.27-4.45. Hover, 18 plates with board pencil: wax 6.0-6.5, stroke 12.66-13.0, ink 3.25-3.5, grain 3.82-4.65; HUD pencil (10 plates): wax 6.0-7.0, grain 4.19-4.82, ink 3.0-4.0 a side (reported) |
| 2.6 | Hand collisions on hover | IMPL | **NOT FIXED (h02 x4)** | Board p2 (3 skins): 0 px of every sibling's cost hex, title band, rules line and ×3 plate under the lifted Trigger; hand under SEND IT / UNDO 0 px. Hover: the same on 22 of 26 plates. h02 x4 (Brace, slot 0): Spin 3's cost hex 166 px and title band 208 px covered (C6) |
| 2.7 | Card bottoms clipped | IMPL | FIXED | Lowest hand pixel 12 px above y 1080 (15 on p3); hover 1064-1067 |
| 2.8 | Room off; iso not perspective | DOC+IMPL | DOC (DR-9) + FIXED | Board room mean 31.0-32.1 (gate 28-34). Backdrop, 9 plates: room 31.6-32.4, as seen 28.65-29.30, both gated 28-34. Board p2 / p3 as seen 22.9-25.4, reported (C9) |
| 2.9 | Three clock materials | IMPL | FIXED | One gunmetal; K clock p95 69.5, median 47.8 |
| 2.10 | Effect loudness inverted | IMPL | FIXED (round-1 set) | Shared meter, all three skins: damage (hit_land 2817 lowest) > kill (1812-1816) > block (841-1678) > state (768 or less) |
| 2.11 | 12.7 s beat | IMPL | FIXED (round-1 set) | Beat 3800 ms against 4000, skip on any input in 200 ms, every effect 600 ms or less, 0 overrides (`port/fx_timings.json`) |
| 2.12 | FAR trim without key | IMPL | FIXED | FAR marks carry Anton 19 numbers (draw asserts pass on every plate) |
| 2.13 | Adjuster hatch and beads | IMPL | FIXED | Track 2860 px, 0 covered; drawn #D69A1A, dE76 0.0 from BOSS_GOLD |
| 2.14 | Tickets unreadable | DOC+IMPL | DOC (DR-1) + FIXED | Glyph ink 23-25 px, p90 L* 86.3-87.8 (K type). Edge time steps W6 / W5 / W4 now on the plate (C5) |
| 2.15 | Tower too loud | IMPL | FIXED as prescribed | Tower p95 89.5, under HOT (94.9-95.4) and SEND IT (98.2). Squint share 57.0-68.7 %, reported (C10) |
| 3.1 | HOLD looks like pause | IMPL | FIXED | Clamp glyph (card art unchanged since round 1; `card_sheet.jpg`) |
| 3.2 | FIREWALL and TWIST share a band | IMPL | FIXED | Own motifs (brick wall, ring bands) |
| 3.3 | Unaffordable is a brown card | IMPL | FIXED | NO RAM tab, Anton 17, cap 16.1 px at the hand scale, fits its tab; padlock on the cost |
| 3.4 | Cyan scribbles on TRIGGER | DOC | DOC (DR-5) | |
| 3.5 | Heat as emoji flames | IMPL | FIXED | Atlas Heat glyph |
| 3.6 | REFUND plate in the wheel | IMPL | FIXED | Tab under the RAM coin, 96 px wide (C6). h03: the tab slides 33.2 px left to clear the lifted card, 0 px of any card in it (hover check k) |
| 3.7 | "00 → \|" tally | IMPL | FIXED | "2 → 1" as digits |
| 3.8 | BEST LINE in PLAN yellow | IMPL | FIXED | Neutral chip and star (h04 star median C* 4.3-4.8, rule 12 or less); 0 PLAN px in the option rows |
| 3.9 | Three RAM treatments | IMPL | FIXED | Hover RAM check 26/26: 0 pencil, FOCUS or hover px on the RAM coins or TRACE pips |
| 3.10 | FX-P plate on card stock | IMPL | FIXED (round-1 set) + DOC (C15) | `fx_P_protect.png`: 55217 px within dE76 8 of P stock, median L* 84.7. P stock is now a token (C15) |
| 3.11 | Resolve log text small | IMPL | FIXED | p3: 120 text draws, smallest cap 16.1 px |
| 3.12 | Transition bits white | IMPL | FIXED | Re-measured on the round-2 plate: drawn vs plate hue dE76 median 0.00-0.42 per stream; share within 3: 0.91-1.00 (rings, spinner, tickets), 0.88-0.96 (cards) |
| 3.13 | Brace hover tower at full value | IMPL | FIXED | h02: the five non-aimed slices at luma ratio 0.394-0.397, the aimed slice 1.00 |
| 3.14 | YOU hatch reads solid | IMPL | FIXED | 13.6 x 22 px segments, two-direction hatch (unchanged since stage 2) |

**Defects found in round 1** (`REVIEW_REBUILD.md` and its gate 2; the re-review's tiered list).

| Defect | Class | Status | Measured |
|---|---|---|---|
| FOCUS on board p2b in #96FE46, a joined bar | IMPL | FIXED (C2) | Each p2b plate: 276 px within dE76 8 of #D4FF00 at L* 94.1, 0 px of #96FE46 (docs-pass probe); four separate 12 px corners. Hover: FOCUS #D4FF00 at dE 0.0 on 26/26, 0 px of #96FE46 |
| Bezel cube-glyph discs and 1 px lines at L* 95-100 | IMPL | FIXED (C3) | Unclassed bright px 0. K structure p95 / p99 84.1 / 84.1; E cell outlines p99 84.9-85.2. Docs-pass probe: in the reviewer's cube-disc box (x 970-1000, y 555-585) p99 83.9 on p2 / p3 and 87.8 on p1, where the box also holds a K arc mark (class p99 87.8); the 470 px at L* 95 or more left inside r 480 on p1 are near-white HOT core (median sRGB 255, 243, 233) on the ring-NOW chevrons and the landing arcs |
| Ring-NOW token discs fail per disc | IMPL | FIXED (C4) | Every disc on every plate p95 82.6-84.4, p99 85.4-91.0 (units 1-3 read 90.9-91.0 / 94.0-94.3 at gate 1) |
| W5 edge shows no 70 % step | IMPL | FIXED (C5) | W6 / W5 / W4 edge p90: 49.7 / 63.2 / 82.2 (neutral), 46.4 / 58.4 / 75.0 (Solace), 41.4 / 51.6 / 66.1 (Meridian); smallest step 10.2 (gate 5) |
| W6 hazard outline notches the bomb's width pips | IMPL | FIXED (C5) | Ticks at ticket x 60.0-78.5, inside the free span 57.0-81.4 (nowords 47.5-66.0 in 32-81.4) |
| h03 dying cell 2.62:1 under the tracer | IMPL | FIXED (C7) | h03 x2: 3.98:1 (sector 3) and 4.19:1 (sector 4); other dying cells on hover 4.19-4.52:1 |
| Wrong TWIST glyph by render order | IMPL | FIXED (C14) | p3 Solace, p1_clean, p3 Solace in one process: 0 px differ, max 0, registry intact on every step (`final/checks.json` `c14_determinism`); the assert ran before the board and backdrop publishes |
| Hover HUD 45 px taller than the board HUD | IMPL | FIXED (C8) | Bill plate y 76-427 (351 px) on board p1 / p2 / p2b / nowords and on all 26 hover plates; HUD bottom 569 (607 with the REFUND tab on p2 and h03) |
| Stale docs (VISUAL_PLAN G, final/NOTES "Not done", the "not re-rendered" row, P stock not a token) | DOC | DOC (this pass) + FIXED (C15) | G rewritten to the published effects; the NOTES and REVIEW_RESPONSE rows corrected; `P_STOCK` in `rb_tokens.TOKENS` |
| Dying-cell rows on 198 / 253 px (gate 2) | IMPL | FIXED | The whole dying glass, 3730-4807 px |
| Wrong NOTES claims (W6 / W5 / W4 values; "that one unit") | DOC | DOC | Corrected in place in `final/NOTES.md` |
| HOT fill vs its cell 1.90:1 | DOC+IMPL | DOC (C11) + FIXED on the cell chevrons; **NOT FIXED** on small side-arc marks | Core 3.0 px (pooled medial), core vs cell 4.92-5.01:1, fill 1.93-1.97:1 (reported). Every cell chevron core 3.0 px; open landing arcs 3.5-4.0 px. 4 side-arc marks per p1 / nowords plate and 2 per p2 / p3 plate read 2.0-2.5 px where their lane line crosses them |
| Tower squint louder than O-30 | DOC | DOC (C10) | 59.3 % p1, 68.7 % p2, 57.0 % p2b, 68.0-68.2 % p3, 59.9 % nowords; reported |
| Room as seen L* 24.7-25.6 on p2 / p3 | DOC | DOC (C9) | As seen: p2 25.3-25.4, p3 22.9-23.1, p1 / p2b / nowords 28.0-28.9; gated room 31.0-32.1 |
| Skip has no on-screen word | IMPL | **NOT FIXED** (C12) | The SKIP tab exists only as a test render in the round-2 effects scratch tree; the published beat has no word |
| T5 / T6 tile flash at the limit (3 in 1 s) | IMPL | FIXED (C13); T6 pull-out not composited (call) | Worst 120 px tile 2 in any 1 s in T5 and T6, both skins, on the renders and the decoded GIFs; WCAG 0 |
| p2: the lifted Trigger hid the "3" of SPIN 3 and its ×3 | IMPL | FIXED (C6) | 0 px of Spin 3's title band and ×3 plate covered |

**New in the re-review (N1-N5)** are answered in the reviewer table below.

**Found in round 2** (by the stages and this pass).

| Item | Class | Status | Measured |
|---|---|---|---|
| UNDO / SEND IT move 4 px when a hover starts | IMPL | **NOT FIXED** | Docs-pass probe (column-profile edge of the button plates): SEND IT x 1893 on round 1, 1905 on the round-2 board (+12), 1909 on the hover plates (+16); UNDO 1879 / 1891 / 1895. The hover stage ran `rb_lift` at BTN_DX 16 and OPEN_PX 36; the board plates were rendered at 12 and 30 |
| h03 x2: gun tracer drawn colour | IMPL | **NOT FIXED** | Modal #FF40B0, dE76 3.8 from CELL_PINK (limit 3), over 1725 px; its top bin holds 11 px; the median #F941A6 is dE 2.9. The same pixels are on the board image |
| h11 x2: HOT fill dimmed inside the lit area | IMPL or DOC (open) | **NOT FIXED** | #662C27, dE76 54.7 from HARM_UP, over 770 px: the board's unit-hover state dims these marks where the hover lights the landing slices |
| FOCUS vs HOT | DOC (open) | Open (designer call) | FOCUS at its token reads L* 94.1; the HOT p95 is 94.9-95.4 on the board and 92.2-96.0 on the hover plates. FOCUS cannot be within dE76 3 of its token (C2) and 1 under the HOT p95 (C3) at once. Reported, not gated |
| h08 Hold: pencil on the frame band | IMPL (reported) | Reported | 13,029 pencil px at r 480-500, 6,261 PLAN-coloured; C17 covers Twist hovers only |
| `corp/src` render path: `gram.a2_frame`'s translucent fill replaces the lane line under it on the plain path | IMPL | **NOT FIXED** | Up to 47-48/255, with 7180-8387 px over 2/255, at r 430-460 between a plain `lw_render` and the published plates (`round2/backdrop/work/paths_diff.json`); the backdrop and transitions stages render through the capture hooks, which match the plates to 1-2/255 |
| Effects not re-rendered on the round-2 board | IMPL | **NOT FIXED** | `effects/` files are dated 2026-11-04 03:38-04:45 (round 1). Their bases are the gate-1 board, so they carry its items where a crop shows them (the CDHL notes list the pencil, ticket edges, FOCUS colour, token discs and thin lines), its HUD rows and the Solace leaf rim (the MPST sheet's Solace scan line is #96FF46; the leaf rim seen on `fx_M_motion.png` in this pass) |
| The reserved option rows leave the bill empty at y 330-420 | DOC (cost of C8) | Reported | About 90 px of empty bill on p1, p2b and nowords |

### The calls C1-C18 (art-pass calls, open to the designer)

| Call | Class | What it says | Status | Evidence |
|---|---|---|---|---|
| C1 Pencil | IMPL | One pencil (VISUAL_PLAN A.5): 7 px wax, a 3 px ink edge each side, wax grain; one drawer (`rb_pencil`) for board and hover; X caps the same stroke; long hover marks keep full width; gated on the plate (check f) | FIXED (board and hover) | 2.5 above. Open edges: the wax reads 6.0-6.1 px against 7 drawn (the blend pixels count as ink), at the low edge of the 6-8 gate; the HUD pencil ink reads 3.75-4.0 px a side on h01 and h10 nowords (reported) |
| C2 FOCUS | IMPL | `FOCUS` #D4FF00 as four 12 px corners only, one drawer (`rb_focus`); check d on drawn colours: within dE76 3 of the token, 15 or more from the corp hue | FIXED | FOCUS dE 0.0, pencil wax 0.0-0.9, HOT fill 0.0-2.4, gun tracers 0.4 (board), Adjuster track 0.0; closest drawn mark to a corp ink 22.3. Two hover plate pairs fail d2 (h03 tracer, h11 HOT fill; table above) |
| C3 Bright marks | IMPL | Every board pixel inside r 480 at L* 80 or more is in a check-b class; glyph ink at K type (L* 84), structure lines capped and classed; only SEND IT and HOT above the tower p95; every other class p99 1 under the HOT p95 | FIXED | 1.2 and the round-1 defect rows above |
| C4 Token discs | IMPL | The A.1 rule per disc | FIXED | p95 82.6-84.4, p99 85.4-91.0 per disc |
| C5 Tickets | IMPL | The W6 / W5 / W4 edge steps 50 / 70 / 100 % visible and measured; W6 hazard ticks clear of the bomb's pips | FIXED | Rows above |
| C6 Hand lift | DOC+IMPL | The reviewer's option (a): fan positions kept, the hovered card lifts straight up, the fan never closes; the button column 12-16 px right; protected set = cost hex, title band, rules line (and ×N plate), 0 px covered on board p2 and every hover plate | FIXED on board p2 and 22 hover plates; **NOT FIXED on h02 x4** | Board p2 lift: slot 2, centre (1371, 718), zoom 1.00 (it was 1.10), fan open 30 px, buttons +12. To fit under the HUD this needed the 1.00 zoom, the print and drop to the right, 4 px HUD panel gaps and a 96 px REFUND tab (VISUAL_PLAN H). Hover: open 36 px, buttons +16, slots 1-3 at y 718. h02: a straight-up slot-0 lift clears r 459 only at y 906 or lower, and clearing Spin 3 needs the fan open 43 px or more, which reaches the buttons (25 px within 2 px at open 38, 568 at 43). Options for the designer: move slot 0 and the buttons further (about 22-23 px, an estimate), let a slot-0 lift move sideways, or rule that slot 0 does not lift |
| C7 Dying glass | IMPL | The dying cell under the tracer reads 3:1 or more against the brightest empty cell; the dying glass is gated like a live unit (1.1) | FIXED | Board 4.49-6.07:1 over the whole glass; h03 3.98 / 4.19:1 |
| C8 HUD height | DOC+IMPL | The board HUD always reserves the option rows (empty rows at the NEXT position); board and hover HUD rows identical, measured | FIXED | Rows above. Cost: about 90 px of empty bill on p1, p2b and nowords |
| C9 Room | DOC | The gate is on the room itself (mean L* 28-34); the as-seen value with the UI scrim on p2 / p3 is reported and accepted; no scrim change | DOC | Board room 31.0-32.1, as seen 22.9-28.9; backdrop room 31.6-32.4, as seen 28.65-29.30 |
| C10 Tower | DOC | The value gate (b) governs the tower (tower p95 under HOT and SEND IT); the squint share is reported, not gated; no texture rework | DOC | Tower p95 89.5 < HOT 94.9-95.4 < SEND IT 98.2; squint 57.0-68.7 % |
| C11 HOT core | DOC+IMPL | HOT is carried by its white-hot core: core 3 px or more at 1x and 4.5:1 or more against its cell; the fill ratio is reported | FIXED on the cell chevrons; **NOT FIXED** on small side-arc marks | Rows above |
| C12 Resolve beat skip hint | IMPL | A "SKIP" key hint (Mono 23, cap 16 px or more) at the HUD edge for the length of the beat | **NOT FIXED** | Drawn only as a preview in `round2/effects/` (tab (1706, 673)-(1892, 705) under the p3 HUD foot at y 667, "ANY KEY" + "SKIP" in Share Tech Mono 23, per `round2/effects/fx_mpst/work/skip_tab.json`); not published, so not measured here |
| C13 Transitions | IMPL (+ DOC for the T6 hold) | Lower the bit density over the dark city until the worst 120 px tile flashes 2 or fewer times in any 1 s in T5 and T6; try the T6 pull-out within that limit, or hold T6 on the room and record the call | FIXED; T6 holds on the room (call) | Keep rule p = near - (near - far) * clamp((d - 90) / 90): T5 near 1.0 far 0.5, T6 near 0.45 far 0.25. Worst tile 2 in T5 and T6 on both skins (WCAG 0); seven pull-out variants all left a tile at 3, so T6 ends on the bare room (difference 0) and T6 K4 equals T5 K1. The hand-over from the room to the netrun street is not drawn (open) |
| C14 Render order | IMPL | Find and fix the leaked state; a determinism assert before every publish | FIXED | The old e10 card library re-registered the KA_* glyphs; `rb4_patch` restores them. Assert: 0 px |
| C15 P stock | DOC+IMPL | `P_STOCK` #F6C8DE a token in `rb_tokens.py`, in the VISUAL_PLAN token table, covered by check d | FIXED on the board and in the docs | Check d 0 failures with P stock in the token set. The published effects still read it from `fxk_lib` (same value; round-1 set) |
| C16 Solace rim | IMPL (within DR-6) | The Solace rim leaves leaf green for the celadon / teal family of #B8DCCC; dE76 25 or more from the hub HP green and GAIN; the cell edges and crest follow | FIXED on board, hover, backdrop and transitions; **not** on the effects set | Rim median #3B827F; 61.3 / 51.0 from GAIN (median / modal), 53.4 / 44.1 from the hub HP green. Teal also on the cell edges, bezel lip, crest strands, token frame dot and ticket edges |
| C17 Twist halo | IMPL | On every Twist hover the PLAN halo only on the legal rings; 0 PLAN px on the frame band (r 480-500) | FIXED | h04 x4: pencil px ring NOW 1,893, +1 19,270, +2 12,362; bezel, frame band and outside r 500: 0; PLAN-coloured px at r 480-500: 0 |
| C18 Corp material in luma | IMPL | The Solace and Meridian rims differ in luma pattern, visible on `grey_proof.jpg`, so the ART_BIBLE 2.4 note's "material and hue" holds | FIXED (the note is kept, with the measure added) | Rim band mean L* 48.4 (Solace) vs 25.1 (Meridian); dominant pattern 52 vs 18 cycles per turn, amplitude 5.4 vs 1.6 L*. On `grey_proof.jpg`'s unwrapped rim strip the Solace rope is a light twisted band and the Meridian rim a dark band with fine stripes (seen at 1x in this pass) |

### The re-review, row by row

| R1_REREVIEW row | Reviewer's status or tier | Round 2 |
|---|---|---|
| 1.1 Occupied vs empty cells | FIXED | FIXED (holds on the round-2 plates; 1.1 above) |
| 1.2 Value order | FIXED, two holes (S2) | FIXED: both holes closed (C3, C4) |
| 1.3 Corp hue on a ring | DOC (DR-6) + FIXED | DOC + FIXED; Solace now teal (C16) |
| 1.4 COLD on Meridian | FIXED | FIXED |
| 1.5 Bill | FIXED | FIXED; rows reserved (C8) |
| 1.6 Effects above the HUD | FIXED | FIXED on the round-1 effects set; not re-rendered in round 2 |
| 1.7 Transitions CONCEPT frames | FIXED | FIXED; re-rendered (C13) |
| 1.8 GAIN on kill marks | FIXED | FIXED |
| 2.1 Eleven techniques | DOC (DR-8) | DOC |
| 2.2 Type colours | DOC (DR-5) + FIXED | DOC + FIXED |
| 2.3 Wireframe played slots | FIXED | FIXED |
| 2.4 Hover duplicates the HUD | FIXED | FIXED |
| 2.5 Pencil (board p2 / p2b) | NOT FIXED (S2) | FIXED (C1) |
| 2.6 Hand collisions (h02) | NOT FIXED (S2) | **NOT FIXED on h02 x4**; FIXED on board p2 and 22 hover plates (C6) |
| 2.7 Card bottoms | FIXED | FIXED |
| 2.8 Room | DOC (DR-9) + FIXED | DOC + FIXED; scrim reading by call C9 |
| 2.9 Clock materials | FIXED | FIXED |
| 2.10 Loudness | FIXED | FIXED on the round-1 effects set |
| 2.11 Beat length | FIXED | FIXED on the round-1 effects set |
| 2.12 FAR trim | FIXED | FIXED |
| 2.13 Adjuster | FIXED | FIXED |
| 2.14 Tickets | DOC (DR-1) + FIXED, one step missing (S3) | DOC + FIXED; the step is on the plate (C5) |
| 2.15 Tower | FIXED as prescribed | FIXED as prescribed; squint by call C10 |
| 3.1-3.14 S3 set | FIXED (3.4 DOC) | FIXED (3.4 DOC); 3.6 gains the h03 tab clearance, 3.10 the P-stock token |
| FOCUS on board p2b in #96FE46 as a joined bar | S2 | FIXED (C2) |
| Bezel cube-glyph discs and 1 px lines above HOT | S2 | FIXED (C3) |
| Ring-NOW token discs fail per disc | S3 | FIXED (C4) |
| W5 edge shows no 70 % step | S3 | FIXED (C5); the NOTES claim corrected |
| h03 dying cell 2.62:1 | S3 | FIXED (C7) |
| Wrong TWIST glyph by render order | S2 | FIXED (C14), with the assert |
| Hover HUD 45 px taller | S2 | FIXED (C8) |
| Stale docs | S3 | DOC: fixed in this pass |
| N1 Card titles clipped by the lifted card | S3 | FIXED on board p2 and 22 hover plates (title band in the protected set); **NOT FIXED on h02 x4** (Spin 3 title 208 px) |
| N2 Solace rim green next to the hub HP green | S3 | FIXED (C16): dE76 53.4 (median) / 44.1 (modal) from the hub HP green; 0 % green-hue px in the rim band |
| N3 h04 full-circumference PLAN ring on the frame band | S3 | FIXED (C17): 0 PLAN px on the frame band; the halo sits on the legal rings |
| N4 T6 pull-out; tile flash at the limit | S3 | Flash FIXED (C13: 2 in any 1 s). Pull-out not composited; T6 holds on the room (call); the room-to-street hand-over is open |
| N5 Corp theme colour-only at squint | note | FIXED (C18): the rims differ in luma (L* 48.4 vs 25.1; 52 vs 18 cycles per turn); the 2.4 note keeps "material and hue" with the measure |

By the re-review's own tiers, one of its six S2 items is still open: 2.6 on h02. The effects set not being re-rendered on the round-2 board is a new open item (build order step 4). The tiering is the reviewer's to do.

### The re-review's questions for the designer: the art-pass calls taken

All of these are art-pass calls, open to the designer.

| # | Question | Call |
|---|---|---|
| 1 | Tower loudness: the squint target vs the 2.15 ink prescription | **C10.** The value gate governs the tower (tower p95 under HOT and SEND IT); the squint share is reported, not gated (57.0-68.7 %). No texture rework |
| 2 | Room under the UI scrim reads about L* 25 on p2 / p3 | **C9.** Accepted. The gate is on the room itself (31.0-32.1 on the board, 31.6-32.4 on the backdrop plates); the as-seen value is reported. No scrim change |
| 3 | Hover HUD height | **C8.** The board HUD reserves the option rows at all times, so no row moves when a hover starts. Measured: bill y 76-427 on board and hover |
| 4 | h02 slot-0 lift | **C6**, option (a). Done on board p2 and 22 hover plates. On h02 it does not fit within 12-16 px; the three options are listed under C6 for the designer |
| 5 | HOT carried by its white-hot core | **C11.** Accepted: core 3 px or more at 1x, 4.5:1 or more against its cell; fill reported. Met on the cell chevrons; small side-arc marks are 2.0-2.5 px (open) |
| 6 | T5 / T6 tile flash at the limit | **C13.** Density lowered until the worst tile is 2 in any 1 s; T6 holds on the room because no pull-out variant stayed within that limit |
| 7 | Shove bump HP and the Twist draw in the resolve beat | **RULES.** Unchanged: they stay with the GDD. The art shows no HP change for Shove, and the beat's Twist workaround stays marked NOT TO SHIP |

### Docs changed in this pass (2026-11-04)

- `VISUAL_PLAN.md`: G rewritten to the published effects; round-2 lines for C1-C18 in A.1-A.7, B, E and H; `P_STOCK` in the E token table (already added by the board stage).
- `final/NOTES.md`: the stale "Not done" claims about hover, effects and transitions replaced with their status; the round-2 numbers checked against `checks.json` (one range corrected: the dying glass 4.49-6.07:1).
- `GODOT_PORT_SPEC.md`: appendices and tables regenerated from `port/*.json` (`skin_tables.json` and `cards_atlas.json` re-made on the round-2 generator) by `port/src/port_spec_r2.py`; sections 9, 10 and 14 brought to round 2.
- `ART_BIBLE_COMBAT_DRAFT.md`: aligned with DR-1..DR-10 and C1-C18; still a draft.
- `docs/concepts/DIRECTION_REVIEW.md`: a dated line for round 2.
- `docs/ART_BIBLE.md` 2.4: C18 landed, so "material and hue" stays (the board stage added the measured line).

## The reviewer's decision table

| Question | Call |
|---|---|
| Tower loudness | Reject 58 %; slice inks at L* 72 or less (2.15). |
| Card colours | Keep a different hue per type (designer); re-pick the hues for token dE (2.2). |
| Corp skin (O-27) | The designer wants a corp theme; carry it by material and rim/lip/crest hue, with neutral cell fills (1.3). |
| Effect layer | Under the HUD (1.6). |
| Effect lengths | Shorten, with no overrides (2.11). |
| Movement arrows | Yellow in hover, pink in resolve. This was already written in VISUAL_PLAN E ("R51 review: motion colour"); the reviewer agrees. |
| Shove bump, Twist render | RULES. Open for the designer and the GDD. Until they rule, the art shows no HP change for Shove, and the resolve beat's Twist workaround is marked as not to ship. |
| D4 scope | Not until this board passes. |
| Sign-off / A-116 | No, until the rebuild passes the new checks and a full review that opens every sheet. |

## Process

- **The four checks** (occupied vs empty contrast, family value order, cap height, token dE) go into corp/src before any render, together with the hand vs buttons and sibling-card checks. A plate that fails any of them is not published.
- **One source of truth.** One generator, one room grade, and port-spec appendices regenerated from data. "Leftovers" that are a second source are fixed, not listed.
- **The final review opens every sheet,** not a sample.
- **The bare `python -` rule** needs a hook, as the reviewer says. That is the designer's settings change to make; art-pass has not made it.
