# XEROX FLYER: per-slice colour and texture pass

Designer request: each unique slice type gets its own colour and texture instead of one magenta for all. Designer follow-up: no colour needs to be avoided, so there are no reserved colours in this pass.

Files: `slice_key.jpg` (each type large, in colour, in grey, and with the red cross-hatch), `plate_A.png`, `plate_B.png` (full p1_decide, bio cutaway, 1920x1080), `wheel_crop.jpg` (old single colour vs A vs B at 2x).
Generator: `D:/rc_scratch/combat_redesign/punk_slices/xerox_flyer/src` (new module `xf_slices.py`; the slice drawing in `xf_tower.py` reads it). The concept's own files one folder up are untouched.

## Slice types on the wheel
The state has four kinds: BURST (the rocket, 2 slices on the board), SHIELD (2 slices), TURRET, REPAIR. Slices of one type match exactly (same fill, same texture).

## Palette and texture
| Type | Texture (tone-on-tone, drawn in the slice's own frame) | A fill / ink | B fill / ink |
|---|---|---|---|
| BURST | big staggered dots, a coarse halftone | `#FF3DA8` / `#B3126F` | `#FF5A14` / `#A12D00` |
| SHIELD | scalloped fish-scale plates (armour) | `#2A58F0` / `#142C86` | `#7A3CF0` / `#3B1A8A` |
| TURRET | checkerboard (targeting grid) | `#FFD21F` / `#A97D00` | `#3FE0F5` / `#0A7C8C` |
| REPAIR | sparse bold plus crosses (first-aid), kept upright | `#4BD67E` / `#11703A` | `#C5F42E` / `#5C7A00` |

- **A, white sheet:** riso-style spot inks (magenta, cobalt, sun yellow, green). Grey values of the fills: 131, 91, 203, 162, so the four types also separate by value.
- **B, black toner sheet:** the inks are re-dealt as fluoro inks (orange, violet, aqua, lime). Grey values: 131, 99, 178, 207.
- Texture shape carries the type when colour fails: the grey column of `slice_key.jpg` shows dots, scales, checker and crosses are four different patterns even at a glance. The rim and hub halftone and the black key line stay the same on every slice, so the set still reads as one punk family against the clean corp glass.

## Unchanged
Black key outline and block drop, the off-register edge, stencil highlight, icon discs and icons, HP pips, hub (BREAKER tiles, black disc in A, white disc in B), cards, hand, guns, SEND IT, the rest of the board, no needle, same game information. The hand cards stay magenta and black (the player's own set); the slice colours are the only change.

## Shift from the earlier reserved-colour pass
An earlier draft in the scratch folder avoided the grammar colours (red, green, yellow, orange, blue, cyan) and used magenta, teal, dark grey and tan. With the designer's note that no colour has to be avoided, those restrictions are dropped: A now uses cobalt, yellow and green, B uses orange, violet, aqua and lime. Consequences to know about, not blockers:
- Yellow (A TURRET) is the PLAN colour elsewhere, and orange (B BURST) is close to the SCHEDULE orange. Green REPAIR sits near the green HP pips and aqua (B TURRET) near NET_CYAN. The pips keep their black casing, so they still read on the green slice; checking the slice with the key line first, the slice outline and the pips remain separate shapes.
- These slices now share hues with board meanings. The texture and the icon identify the slice, so the hue is not the meaning.

## Red cross-hatch legibility (pending HP loss this END TURN)
Tested on every slice colour in both variants (third column of `slice_key.jpg`, and `plate_A.png` / `plate_B.png` which show hatched slices).
- The slice is dimmed with toner, then each hatch line gets a black casing 0.85 px wider than the red line, then the red line, and the slice gets a red edge and a red X. The casing is what makes red readable on yellow, orange, green and magenta.
- Weakest case: red on the orange BURST in B (hue neighbours). Fix applied on that slice only: a heavier toner dim (0.6 instead of 0.24), so the red hatch sits on near-black brown. The slice colour is unchanged; the icon disc keeps the orange so the type still reads.
- Remaining softest reads: red over yellow in A (readable because of the casing and the X), and red over magenta in A (readable, as in the original).
- The red hatch is still the only straight crossing hatch on the board; the textures use dots, scallops, squares and plus shapes, none a continuous diagonal cross-hatch. The checker is the nearest, and it is an axis-aligned fill of squares, not lines.

## Not done or not measured
- No squint or loudness measurement was run; A with four bright inks is louder than the old single magenta. Measure before approval.
- Only p1_decide was rendered; the wheel's other states use the same code but were not rendered.
- Game names in the key (ZERO-DAY, SANDBOX, EXPLOIT, PATCH) are the in-game names as I read them from the generator and state; verify them before the key is used outside this folder.

## Process note
Python scripts were run from files by path. One command accidentally contained a bare stdin-reading `python -` with no input; it hung, was stopped by task id at once, and produced no output or changes. No Godot or Blender, nothing committed, nothing written under D:/Godot/rebel_cell. A prior attempt in the scratch folder `punk_slices/xerox_flyer` (its `xf_slices.py`, `sl_*.py` tools) was reused and the palette rewritten.
