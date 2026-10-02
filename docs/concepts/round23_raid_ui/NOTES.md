# Round 23: raid UI fixes

Locked and unchanged: remove-to-hand (click the node to return the defence), plus the frozen link and frozen unit ice (round 22), and everything locked before that.

## Files
| File | What |
|---|---|
| `interactions_gifs/02_drag_dock_preview.gif` | One drag across two nodes and away. See note 1. Replaces round 22's 02 and 03. |
| `interactions_gifs/06_swap_one_motion.gif` | The swap with a truthful cursor path. See note 2. |
| `interactions_gifs/21_node_taken.gif` | A brief pencil **TAKEN** over the node, which then wipes like DOWN; the node is removed. |
| `interactions_gifs/26_home_breached.gif` | Slowed down: 44 frames at 120 ms. See note 4. |
| `interactions_gifs/index.md` / `index.jpg`, `contact_sheet.jpg` | The index links back to the locked round 21 and 22 gifs. |
| `scripts/` | `screens23.py` (`dock_arrow`, `link_dying`) is built on `screens22.py` / `screens21.py`. |

Rebuild:
1. `python scripts/run_blender.py`
2. `blender -b --factory-startup --python scripts/vehicles.py -- <abs>/scratch/bl sprites`
3. `python scripts/screens23.py`

## Notes
1. **Dock preview while dragging:**
   - When the cursor comes within 95 px of any node, the arrow **stops**: its tip parks just outside the node's circle and is not redrawn.
   - The circle draws on at once: **yellow** for valid (the Vault, with the IF PLACED terminal), **red circle + red X** for invalid (the full Firewall, with the NO SLOT terminal). The arrow itself stays yellow in both cases.
   - When the cursor leaves the node, the circle is erased and the arrow tip snaps back to the cursor.
2. **Swap:**
   - The cursor starts **on** the placed unit (Firewall) and presses there.
   - The sticker peels off, its model disappears, and it flies to its parking spot above its slot.
   - The arrow starts at the sticker under the cursor and follows the cursor's real path to the Relay, where the dock preview draws the yellow circle.
3. **TAKEN:** the word is written right over the node in grease pencil, holds a moment, then wipes away like DOWN. The node is then removed (burnt socket).
4. **BREACHED, slowed:**
   - CORE drains, then a slow bit explosion plays.
   - CORE and every link to it de-power **segment by segment from the node outward** (the last lit segment flickers).
   - BREACHED writes slowly as one heavy pass, then the underline goes in under it.

## Weakest
- **Swap path is short:** the ICE LOCK parking spot sits close to the Relay on screen, so in the swap the final arrow is short.
