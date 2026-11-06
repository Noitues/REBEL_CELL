### 6.2 Card atlas (baked in this pass from the new card sheet's module)
- **Bake:** `port/src/bake_cards.py` imports `corp/src/card_render.py` read-only (the module `final_cards.py` renders `final/card_sheet.jpg` with) and wraps four of its calls for the bake only: `text` (returns an empty mask in the art pass and logs every call: text, anchor, size, font, tracking, rotation, and the colour of the paint that follows), `rules_lines` and `poly` (to catch the rules bar), and `Cv.paint` (skips the one pink bar paint after the rules layout in the art pass). Nothing in `card_render` is edited; the `bake_art_only` flag the 2026-11-02 draft asked for is not needed. It draws `draw_card(name, 2 x CW, state)` for the 11 cards in `card_render.ORDER`, in the normal, played and unaffordable states.
- **Result** (atlases in scratch, `D:/rc_scratch/combat_redesign/locked/port_rb/work/`; `port/cards_atlas.json` and `port/cards_proof.jpg` beside this spec):

<!-- gen:atlas begin -->
<!-- gen:atlas end -->

- **Looked at** (`cards_proof.jpg`, at the in-hand size): every art card keeps its type plate, title plate, cost hex, Trace tab, multiplier plate, owner triangles, icon and facets with no words and no rules bar; the worded card matches `final/card_sheet.jpg`; the liner keeps its torn rim and ghost glyph with no words.
- **Also bake** `cards_nowords_atlas.png` only if a no-words mode ships (`state='nowords'`).
- **Game card ids:** the atlas key is the game id (`spin2` and so on). The open rows in 0.2 (Firewall/scorch, Hold, bug) need art before their cells exist.

