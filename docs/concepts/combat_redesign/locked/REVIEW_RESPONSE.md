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
| Not re-rendered: 1.6, 1.7, 2.4, 2.5, 2.6, 2.10, 2.11, 3.9, 3.10, 3.12, 3.13 (hover, effects, transitions) | IMPL | **Not done in gate 1.** The calls above stand; the sets still show the older board. See `final/NOTES.md`, "Not done (gate item 4)". 1.7 and 3.12: done 2026-11-04 (next section). |

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
  - Stale docs: VISUAL_PLAN G, final/NOTES, and the "not re-rendered" row above.

Round 2 makes art-pass calls on the open questions in `REVIEW_REBUILD.md` and records them here when it lands.

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
