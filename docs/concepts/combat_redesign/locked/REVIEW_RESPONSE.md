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
| 1.1 | Occupied and empty enemy cells look the same | IMPL | Accepted. Occupied cells get a visible glass wash and a programme screen (L* 40-45, empty cells L* 28), HP ticks readable at 1x, and a width read. A new check fails the plate below 3:1. |
| 1.2 | The value order is inverted | IMPL | Accepted. The THIS TURN sweep and the clock go down to gunmetal at L* 45-55; HOT chevrons go up to second place under SEND IT; token discs are capped. A.1 now lists the clock. A new check sorts p95 L* per family. |
| 1.3 | Corp hue on a ring breaks 2.4 LOCKED | DOC+IMPL | The designer explicitly asked for corp-themed enemy layers: "prefer the corp layers have more of a theme related to the corporation, even if just a color shift". That ruling is newer than 2.4, and 2.4 now records it as a combat-ring exception. The way it was drawn is wrong: hue on the cell fill flattened the occupied/empty read. **Call:** the theme is carried by material and by hue on the rim, lip, crest and cell edges. Cell fills stay a neutral slate ladder, with only a low-chroma tint. The corp hue must sit at dE 15 or more from Cell lime, GAIN, FOCUS and HARM (this was the reason behind 2.4). |
| 1.4 | COLD is lost on Meridian | IMPL | Accepted. COLD gets a keyline and value separation on every skin, checked by the token dE test against each skin's cell colour. |
| 1.5 | The bill is unreadable | IMPL | Accepted. Labels are at least 16 px cap height (Mono 18/22); numbers become digits with the tally as a second mark; NEXT is at 70 % value; SPLIT gets written operators. A new cap-height check is added. |
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
