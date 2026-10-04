# Round 32: MAINFRAME sign

The shop sign is now one word, **MAINFRAME**, a vertical circuit-board neon in the round 4 MODEM
style, on the round 12 F1b night facade.
- **Normal**: blue neon with blue spill.
- **REBEL_CELL**: the same sign rewired red and fully lit.
- **Takeover**: the hijacked controller flashes NO → MoRE → MAN in red, one word at a time. The
  unused letters are dead (snapped tubes, soot) and the frame and traces go dim.

## Files
- `mainframe_blue.png`: the normal sign, blue.
- `mainframe_red.png`: the REBEL_CELL version, fully lit.
- `mainframe_takeover_{no,more,man}.png`: the three flashed words.
- `mainframe_sequence.gif` and `mainframe_storyboard.jpg`:
  - red sign → stutter → dead letters drop out;
  - NO → MoRE → MAN, twice, with stutters between words;
  - the full red sign flashes back, then the loop restarts.
- Bonus:
  - `iamin_sequence.gif` and `iamin_storyboard.jpg` (I AM / IN);
  - stills `noname_*.jpg`, `armme_*.jpg` and `aiframe_*.jpg`.
- `signs_compare.jpg`: blue, red, then every flashed word for each sequence.
- `scripts/`: copies of the round 27 / round 12 / round 4 scripts.
  - `make_all.py` builds everything; `--no-bg` reuses the facade renders.
  - `flicker_sign.py` holds the layout, glyphs, partial strokes, sequences and palettes.

## Letter map: M0 A1 I2 N3 F4 R5 A6 M7 E8
Capitals = lit; `(o)` = only the top bowl of that letter is lit, which reads as an o.

| flash | lit | reads |
|---|---|---|
| 1 | m a i **N** f **R(o)** a m e | NO |
| 2 | **M** **A(o)** i n f **R** a m **E** | MoRE |
| 3 | **M** **A** i **N** f r a m e | MAN |

- **R(o)** is the R's closed top bowl (stem top, bowl, bar).
- **A(o)** is the A's two shoulders, top bar and crossbar.
- **I, F, the second A and the second M** are never lit, so they get the broken tubes.

## Bonus sequences (in order, partials allowed)
| sequence | letters | note |
|---|---|---|
| **I AM / IN** (rendered as a GIF) | I2 A6 M7 / I2 N3 | the hacker's "I'm in"; the I stays lit across both words |
| NO / NAME | N3 R5(o) / N3 A6 M7 E8 | "no name": the Cell is anonymous |
| ARM / ME | A1 R5 M7 / M7 E8 | a call to arms |
| AI / FRAME | A1 I2 / F4 R5 A6 M7 E8 | "AI frame(d)": the machine took the blame |

Other in-order words:
- MAIN, MAN, MANE, MINE (M0 I2 N3 E8)
- AIM, AIR (A1 I2 R5), FAR, FARM, FAME, FRAME
- NAME, RAM, ARM, IN, I AM, AI

NEAR and AMEN can't be spelled.

## Readability
- The partial R(o) is a closed bowl and reads as a small o, but it is squarer than a real O. Read
  slowly, NO could pass for "ND".
- The partial A(o) in MoRE reads better, because it sits right under the M.
- Both partials work best in motion, when the rest of the letter flickers out first.

## Godot
- **Letters:** each letter is its own tube mask with an emission level and a colour.
- **Partials:** the two partials are extra masks on R and A.
- **Takeover:** a timeline of per-letter levels; dead letters swap to the broken-tube sprite.
- **Spill:** the light swaps from blue to red, and drops to about 10% during the words.
