# Round 33: MAINFRAME sign, filled neon

This round applies the designer feedback on round 32:
- **Filled letters.** Each letter is now a solid glowing tube with a hot centre line, not a hollow
  double outline. Unlit tubes show as solid dark glass.
- **NO uses the second A.** NO now uses the top half of the second A as its o (the R top read as a D).
- **New sequence.** I AM / IN is replaced by I AM → AI.

The style (circuit-board plate, traces, chips) and the F1b night facade are unchanged.

## Files
- `mainframe_blue.png`: the normal blue sign.
- `mainframe_red.png`: the REBEL_CELL red version, fully lit.
- `mainframe_takeover_{no,more,man}.png`: the three flashed words.
- `mainframe_sequence.gif` and `mainframe_storyboard.jpg`:
  - red sign → stutter → dead letters drop out;
  - NO → MoRE → MAN, twice;
  - the full red sign flashes back, then the loop restarts.
- `iamai_sequence.gif` and `iamai_storyboard.jpg`: I AM → AI.
- `iamnoman_sequence.gif` and `iamnoman_storyboard.jpg`: the extra GIF, I AM → NO → MAN.
- Stills for the other proposals: `noname_*`, `manframe_*`, `aimarm_*`, `mine_*`.
- `signs_compare.jpg`: blue, red, then every flashed word for each sequence.
- `scripts/`: copied from round 32. `make_all.py` builds everything; `--no-bg` reuses the facade
  renders.

## Letter map: M0 A1 I2 N3 F4 R5 A6 M7 E8
`A(o)` = only the top half of that A is lit (both shoulders, top bar, crossbar), which reads as an o.

| sequence | frames (lit letters) |
|---|---|
| **NO / MoRE / MAN** (main) | N3 A6(o) / M0 A1(o) R5 E8 / M0 A1 N3 |
| **I AM / AI** | I2 A6 M7 / A1 I2 |
| **I AM / NO / MAN** (extra GIF, the best new one) | I2 A6 M7 / N3 A6(o) / M0 A1 N3 |
| NO / NAME | N3 A6(o) / N3 A6 M7 E8 |
| MAN / IN / FRAME | M0 A1 N3 / I2 N3 / F4 R5 A6 M7 E8 |
| AIM / ARM | A1 I2 M7 / A1 R5 M7 |
| MINE / NO / MoRE | M0 I2 N3 E8 / N3 A6(o) / M0 A1(o) R5 E8 |

I AM / NO / MAN was picked for the extra GIF because it reuses the main sequence's NO and MAN, so it
can play as an alternate loop of the same takeover.

The dead (broken) letters in each takeover are the ones that sequence never lights. In the main
sequence those are I2, F4 and M7.

## Godot
- **Letters:** each letter is a filled tube mask with an emission level and a colour, plus a core mask
  for the hot centre.
- **Partials:** the A-top is an extra mask on both A's.
- **Takeover:** a timeline of per-letter levels.
- **Spill:** the light swaps from blue to red, and drops to about 10% while the words flash.
