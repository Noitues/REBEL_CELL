# Heavy spin (family `spin_heavy`)

Base illustration, shared by every non-unique card of this family and **tinted per card
type** (ART_BIBLE 7.3, designer ruling Q1). Stand-in: `CardArt` family `spin_heavy`. Concept:
[`spin_heavy.png`](../../art_review/W4/concepts/spin_heavy.png) (pixel-art concept only, Q6).

## Subject
The same wheel thrown hard: a double arrow, heavy speed lines.

## Composition (3:2, 768 x 512 master)
Wheel centred and larger; a key arrow and a pink arrow wrap it in two rings; streaks both sides.

## Inks
Tints needed for this family: WHEEL (paper).

| Card type | Stock (window) | Key ink | Spot ink |
|---|---|---|---|
| WHEEL (paper) | `PAPER_ALT` #E9E4D6 | `INK` | `CELL_PINK` |
| SYSTEM (black) | `INK` #111111 | `PAPER` (light ink) | `CELL_PINK` |
| HACK (pink) | `STICKER_PINK` #F5AFCB | `INK` | `CELL_PINK` |

## Print spec
- **Master:** 768 x 512 px (3:2), flat RGB, no transparency. Keep the subject inside the
  centre 540 x 460 px: the hand card shows a centre crop about 1.17:1 (the full 3:2 shows
  only in the detail view), and the top-right 60 px corner carries the rarity tab.
- **Two inks** (riso passes), each its own halftone screen:
  - key pass: `INK` #111111 (printed `PAPER` #F2EEE4 on black-stock cards), screen 45°;
  - spot pass: `CELL_PINK` #FF3DA8, screen 15°, multiplied over the stock.
- **Halftone:** round dots, cell about 10 px at the master (about 1/50 of the height);
  solids above 92% tone. No gradients left unscreened.
- **Misregistration:** the spot pass sits 4-7 px off the key pass, diagonally, the same
  direction across the whole print. Never more than 8 px (it must still read at 100 px).
- **Stock:** photocopy grain, a few toner specks, one faint copier streak, a slightly burnt
  edge. The stock colour is the card type's (see "Inks by type").

## Do
- more force than Spin: thicker arrows, more lines
- one subject, read in half a second at 100 px wide
- hand-cut, stamped, photocopied feel (ART_BIBLE 1, 2)
- silhouette first: it must read in greyscale (ART_BIBLE 12)

## Don't
- don't blur the wheel (riso has no blur)
- no text, numbers or UI glyphs in the art (the band and rules carry them)
- no third ink, no gradients, no glow
- no chrome-and-hologram cyberpunk, no characters or logos from any IP (ART_BIBLE 1)

## Cards using this base
| Card id | Name | Type | Rarity |
|---|---|---|---|
| `brute_spin` | Brute Spin | WHEEL (paper) | COMMON |
| `heavy_spin` | Heavy Spin | WHEEL (paper) | COMMON |
| `spin_cycle` | Spin Cycle | WHEEL (paper) | UNCOMMON |
| `whirl` | Whirl | WHEEL (paper) | COMMON |

Unique variations of this family: none.
