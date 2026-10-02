# Round 22: raid UI fixes (everything else is locked in round 21)

Locked and kept as they were: the raid report, the setup, the path rules, node health, the YOUR NETWORK panel with its status chips, and all other round 21 gifs.

## Files
| File | What |
|---|---|
| `interactions_gifs/` | The redone gifs (each ≤ 2 MB, shared-palette encoding) plus `index.md` / `index.jpg`. The index links back to the unchanged round 21 gifs. |
| `parked_eval.png` | The one labelled **evaluation** frame that shows a faint parking outline. No gif draws it. |
| `node_status_key.png` | The round 19 key with the lost state renamed **TAKEN**. |
| `contact_sheet.jpg`, `scripts/` | `screens22.py` (built on `screens21.py`), `ui22.py` (hand, parked positions, ice crystals). |

Rebuild:
1. `python scripts/run_blender.py` (`setup1`, `setup1_noice` without the Firewall's ICE LOCK model, and `wave2`)
2. `blender -b --factory-startup --python scripts/vehicles.py -- <abs>/scratch/bl sprites`
3. `python scripts/screens19.py key`
4. `python scripts/screens22.py`

## Changes
1. **Parked sticker:**
   - It sits **just above the slot in the hand it was taken from** (`ui22.PARK_Y`).
   - The slot below it stays visibly empty.
   - No outline in the gifs; the outline appears only in `parked_eval.png`.
   - Gifs 01, 02 and 03.
2. **LOST is now TAKEN:**
   - `21_node_taken.gif`.
   - The pencil word on a seized node is now TAKEN (`20_node_seized.gif`).
   - The key's label is "TAKEN (node removed)".
3. **BREACHED:** one heavy wax pass (9.5) with the underline. The doubled second stroke is removed (`26_home_breached.gif`).
4. **Move / swap is two actions:**
   - **Remove to hand** (`05_remove_to_hand.gif`):
     - The placed ICE LOCK sticker peels off the Firewall node, and its 3D model disappears (a render without it).
     - It flies to the **hidden parked zone at the bottom**, just above its slot.
     - It slots back into the hand: ICE LOCK x1 becomes x2.
   - **One-motion swap** (`06_swap_one_motion.gif`):
     - The sticker leaves the node for its parking spot above its slot.
     - Meanwhile the pencil arrow draws from the moving sticker to the cursor's **current** position on the Relay. The cursor never moves.
     - Once parked, the arrow resolves into the yellow circle.
5. **ICE** (`ui22.ice`):
   - The foggy frost is gone.
   - The masked area gets a light-blue translucent fill and a crisp blue rim.
   - Blue/white **ice crystals** (spikes with side branches) grow inward from the inside border.
   - Used on the **frozen link** (`10_link_frozen.gif`) and on the **held unit**, which is encased in an ice block (`15_threat_held_ice.gif`).

## Weakest
- **The swap's empty slot:** in the one-motion swap the hand already holds an ICE LOCK. The flying sticker parks above that slot without a separate gap, so the game needs a rule for which copy is "in hand" while it is parked.
- **The TAKEN key:** it still uses the round 19 socket drawing for the other states. Health v2 is shown in round 21's `node_health.png`.
