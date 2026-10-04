# Round 39: portrait fixes

This round fixes five classes from round 38. Approved and unchanged since round 38:
- portrait states and contexts;
- Wrecker, Overclocker and Botnet.

`portraits_classes.png` re-renders all 8 classes with 3 rookie variants each.

| Class | Fix |
|---|---|
| Breaker | The chin piece is gone. Beards are off for Breaker, and the hood is cut above the jaw, so only the hood and the visor bar remain. |
| Ghost | Ninja wrap: a single cloth wrap over the head and face, an open band showing the real eyes (no eye slits), a fold line, and a cyan headband with knot tails behind. Variants: cloth tone, tail length, and no headband (then the tails are cloth-coloured). |
| Phantom | A full face mask with round robotic eyes (a dark ring, a glowing lilac lens, a pupil) and vent slots. Variants: mask tone, eye size, vent count. |
| Rigger | One strap runs through both goggle cups (placed on the strap's circle) with a nose bridge between them. The lenses sit in the cups. Goggles are up on the forehead or down over the eyes. |
| Hivemind | One eye is now a square glowing lens in a housing, like the Overclocker's lens, joined to the hex circlet by an arm and a glowing cable. |

## Scripts

- `patch_r39.py` and `patch_r39b.py` patch the copied round 38 `bust_rig.py`. They have been applied; `bust_rig.py` is now the source.
- `render_busts.py classes` renders the busts in Blender.
- `portraits.py classes` builds the sheet.
- `sheet.py` makes a review sheet in scratch.

Everything else is copied from round 38 (`portraits.py` also builds `states` and `contexts`). Scratch is cleared.
