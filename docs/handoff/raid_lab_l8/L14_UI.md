# L14 UI: show the deck, the second sealed beam and the hidden best response (main scene, board, README)

The rules are already in l8_rules.gd (L14_RULES.md). The view only calls L8Rules. Keep the L13 behavior unless this
spec changes it.

1. **Hand and deck.**
   - **Hand row.** After CAPTURE, a DRAW beat deals `L8Rules.hand(...)` as a row of cards at the bottom of the
     screen.
   - **Card look:** a type shape in the type color (triangle D, square N, circle E) plus a verb glyph:
     - GUARD: shield;
     - SHIFT: curved arrow;
     - JAM: zigzag;
     - a wound: cracked gray, with no shape.
   - **PLAN:** pick a card, then a district. A placed card shrinks onto the district as the sentry, and the sentry
     keeps the card's verb glyph.
   - **Response cards:** the unplaced cards stay in the row as the response hand. Highlight SHIFT and JAM as "held for
     response".
   - **Deck strip** at the left edge: one pip per card, wounds as red cracked pips. Hovering it shows the counts.
   - Shot name: `rN_draw`.
2. **Wounds land in the deck.** Whenever a district turns TAKEN (hit, decay or sacrifice), a cracked card flies from
   that district into the deck strip.
   - The score breakdown shows "wounds × 5".
   - BETWEEN offers CLEAN ("remove a wound, 4") next to the build options, and the build options read "add D/N/E
     guard card".
3. **Two sealed beams.**
   - **REVEAL A,** as in L13.
   - **RESPONSE.**
   - **Sealed A fires.**
   - **REVEAL B:** the two remaining routes pulse with a "?". One ignites and the other dissolves. Shot name:
     `rN_reveal_b`.
   - **Sealed B fires.**
   - **Hunter reveal,** then the hunter.
   - The forecast panel shows per A a 2 × 2 mini-table, B route × hunter street, with tier icons.
   - The launch list and the confirm read the worst and best of the 12 outcomes.
4. **Hand size from Heat.** The corp tower's heat ghosts (L13) each carry a small "+1 card" tag. When Heat is
   ≥ 50 / 75, the DRAW beat deals the extra card with a gold edge.
5. **Hidden best response (R14).**
   - Remove "best response: …" and the "One fix" line.
   - Response rows show their own results (range over B × hunter) only on hover.
   - Add a **SCAN (+3 Heat)** button. It calls `buy_hint` and marks the `best_response` row with a gold edge. It can
     be bought once per raid.
   - The launch confirm still triggers on the same conditions, but it no longer names the fix.
   - `--auto` never scans.
6. **Responses show their card.** Each REDEPLOY, DEPLOY or JAM row shows the hand card it needs. Rows whose card is
   missing are hidden; `response_options` already filters them.
7. **Readability:** text at least 13 px, no clipping, and the hand row must not cover the board.
   - Shrink the forecast panel if needed.
   - Board API additions stay additive.
