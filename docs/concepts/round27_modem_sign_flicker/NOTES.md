# Round 27: the shop sign's broken-neon takeover

When the REBEL_CELL takes the shop over, the sign's controller is hijacked. Letters stutter, the
unused tubes die (snapped glass, soot), and the surviving letters flash a message **in place**, one
word at a time, in Cell lime. The plate, frame, PCB traces and chips use the round 4 MODEM sign style
on the round 12 F1b night facade. In the takeover the frame tube goes dark and the traces drop to a dim red.

## Files
- `market_neon_sequence.gif` (primary): normal -> stutter -> dead letters drop out -> NO -> MRE -> MAN
  (twice, with stutters) -> the old sign flashes back -> loop.
- `market_neon_more_sequence.gif`: the same with a partial stroke, NO -> MoRE -> MAN.
- `market_neon_storyboard.jpg`, `market_neon_more_storyboard.jpg`: key frames of each sequence.
- `market_normal.png` and `market_takeover_{no,mre,man}.png`; `market_more_*` the same.
- Secondary options: `<key>_normal.jpg`, `<key>_takeover_<word>.jpg` and `<key>_sequence.gif`.
- `signs_compare.jpg`: every option, normal next to each flashed word.
- `scripts/`:
  - `make_all.py` builds everything; `--no-bg` reuses the backdrops.
  - `flicker_sign.py` holds the layouts, glyphs, sequences, takeover render and broken tubes.
  - `modem_sign_r4.py` and `lightpen.py` are copies from round 4 and round 3.
  - `scene.py`, `flib.py` and `post.py` are copied from round 12. The env var `MF_SIGN_PNG` sets the
    sign texture, and `MF_SPILL` / `MF_SPILL_K` set the spill colour and strength.
  - `render_bg.py` drives the backdrop renders.

## Letter maps (index = position in the sign, spaces skipped; capitals = lit)

**MARKET NEON** (primary): M0 A1 R2 K3 E4 T5 N6 E7 O8 N9
| flash | lit | reads |
|---|---|---|
| 1 | m a r k e t **N** e **O** n | NO |
| 2 | **M** a **R** k **E** t n e o n | MRE |
| 3 | **M** **A** r k e t n e o **N** | MAN |

The N comes from the far end of NEON, so in flash 3 it sits apart from MA. K, T and the E in NEON are
never used, so they get the snapped tubes.

**Variant: NO MORE MAN.** Lighting only the top half of the A (both shoulders, the top bar and the
crossbar) makes a closed loop that reads as an **o**. The A sits right between M and R, so flash 2
becomes **M (A-top=o) R E** -> **MoRE**. It reads clearly in the stills and the GIF; it's the smaller,
upper-case-height o of a neon sign. Recommend this one if the designer accepts the partial stroke.

**NEON MODEM / REPAIR & MAINTENANCE** (keeps the MODEM brand). The letters are NEON 0-3, MODEM 4-8,
REPAIR & 9-15 and MAINTENANCE 16-26.
- NO = N0, O2
- MORE = M4, O5, R9, E10 (the O is a real O)
- MAN = M16, A17, N19

The small lower rows are hard to read on the facade at game size, which is its weakness.

**REPAIRS / SECURE UPGRADES**. The letters are REPAIRS 0-6, SECURE 7-12 and UPGRADES 13-20.
- RISE = R0, I4, S6, E8
- UP = U13, P14
- US = U10, S20

**TECH HELP / CELL / REPAIR** (own idea; a plausible phone-repair shop). The letters are TECH 0-3,
HELP 4-7, CELL 8-11 and REPAIR 12-17.
- THE = T0, H3, E5
- CELL = C8 to L11 (the whole hero word)
- HERE = H4, E5, R12, E13

This reads THE / CELL / HERE: the Cell announces itself with the giant hero word.

## MARKET NEON can't spell NO MORE MAN without a trick
There's no O between M and R. It needs either the flash sequence (MRE) or the partial-A "o".

Other in-order words MARKET NEON allows:
- MAKE ON, MARK TEN, MAN ON, MET ON, KEEN, MEN, ART, NEO

None is stronger than NO / M(o)RE / MAN.

## Building it in Godot
Each letter is its own tube mask (sprite or SDF channel) with an emission level and a colour. The
takeover is a timeline of per-letter levels; the dead letters swap to a broken-tube sprite. The partial
A-top is a second mask on the A. The spill light swaps from pink to lime at about 50% energy.
