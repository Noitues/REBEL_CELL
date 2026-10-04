# Round 33: the shop's offscreen slice wheel and the recycle bin

This round follows the designer's round 32 notes. Two parts of the shop are mid-redesign elsewhere:
- the MAINFRAME sign is still the round 32 placeholder (the sign work is in another round);
- Microchips and Daemons are labelled placeholders (they get their own design pass).

## Files

| File | What it shows |
|---|---|
| `shop_v3_layout.png` | The whole shop: the slice wheel mostly offscreen, the RECYCLE BIN on the sidewalk, and the round 32 placeholders, clerk and LEAVE sticker. |
| `slice_wheel_compare.png` | **A** (round 32: the whole wheel on the board, now with padlocks) next to **B** (the designer's version: wheel mostly offscreen). **Recommended: B.** |
| `slice_wheel_offscreen.gif` (2.8 MB) | B on entering the shop. The arc spins with motion blur and eases to a stop. Then the locked slices grey out and get padlocks, the 3 for sale get yellow arcs, and their tags drop in. |
| `recycle_bin.png` | Removal as a cel-shaded wire-mesh bin with a recycle sticker and a flap lid. A card mid-drop is half crumpled into a faceted ball; a slice is parked ("slices too"); a CRT readout shows the bin's contents. |
| `recycle_bin.gif` (0.6 MB) | The card hovers. The lid flaps open with an overshoot. The card falls in and crumples into a low-poly ball. Bits fizz up. The lid slams shut with a rebound. A count badge shows 1 and a RECYCLED readout appears. |

## The offscreen slice wheel

- **Wheel.** 12 slices; the hub sits about 170 px below the screen, so only the top arc rises out of the counter. A 12-slice wheel means the 3 slices for sale are a 90° arc at the top. They are big, readable slices from the locked slice kit. The next two slices on each side peek in at the screen edges.
- **What's for sale (designer: make it obvious).**
  - For sale: the slice is at full brightness, has a yellow arc on its rim and edges, and has a kraft price tag hanging on a string from the pegboard above it, with the slice name next to the tag.
  - Not for sale: the slice is greyscale and darkened by 60 %, carries a padlock glyph (the locked LOCKED state icon), and isn't clickable.
- **Prices.** 100 per slice, 150 for a MISS slot (GDD). The 120 on the centre slice is still a proposal, and the number belongs in config.
- **Spin.** It spins once on entry from the seeded shop stream; this is a random event, so it sets a checkpoint. The spin eases out over about 1.5 s with a radial blur that follows angular speed. Then there's a 0.6 s reveal: dim, padlocks, arcs, then the tags drop in.
- **To-do (designer idea).** A campaign upgrade could add NUDGES to the shop wheel (nudge the stock wheel ±1 before buying), the same verb as in combat. This would be a profile or campaign unlock; it needs a GDD/DECISIONS entry.

## Recycle bin

- **Interaction.** Drop a card sticker or a slice onto the bin.
  1. The lid flaps open.
  2. The sticker crumples. It's a triangle-mesh warp into a faceted ball (the Cv2 triangulated look), with the facets toon-shaded.
  3. It drops in, and bits fizz out of the mouth (lime and pink, the locked dissolve A palette).
  4. The lid slams shut.
- **Price.** 50 Cycles, +25 each time (GDD 11.2).
- **Undo (proposal).** Items stay "in the bin" (you can see them through the mesh, and the count badge shows how many) and can be fished back out until you LEAVE THE MAINFRAME. Leaving empties the bin. This needs a decision.
- **Sound cues** (the designer liked the natural sounds):

| Cue | Sound | When |
|---|---|---|
| Lid open | Metal clank and a spring creak | Hover lands on the bin |
| Crumple | Vinyl/paper crunch | The sticker starts to crumple |
| Fizz | Digital fizz | The bits rise |
| Lid shut | Lid slam and a rattle | The lid closes |
| Badge | Soft tick | The badge counts up |

- **Godot build notes.**
  - The bin is three layers: the back interior, the contents, and the front mesh. The front mesh is semi-transparent, so the contents show through the wires.
  - The lid is a separate sprite on a hinge pivot. Animate its scale.y and position with an AnimationPlayer, and add the overshoot/rebound with a tween (TRANS_BACK).
  - Pre-bake the crumple as a 6-frame flipbook per card (or use a vertex-warp shader on a subdivided quad), then hand off to the dissolve shader.

## Scripts (in `scripts/`)

| Script | What it does |
|---|---|
| `assets.py` | Renders the slice tiles and the wheels, including the 12-slice `shop_wheel12.png`. |
| `shop3.py` (`layout\|compare\|gif`) | Builds the layout, the A/B compare and the offscreen GIF. |
| `recycle.py` (`still\|gif`) | Builds the bin, its 3D-projected lid, the crumple warp, and the still and GIF. |
| Round 31/32 copies | `r31lib.py`, `sticker_lib19.py`, `lib17/`, `shop.py`, `shop2.py` (the clerk's price line now reads "bin 50+"), `removal.py`, `reward.py`. |
| `clear_scratch.py` | Removes the scratch folder and the caches. |

All randomness is seeded.
