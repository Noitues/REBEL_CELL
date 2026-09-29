# Short Circuit (`short_circuit`), unique art

RARE · HACK CARD on pink stock. Family base:
[Breach](../breach.md). Stand-in: `CardArt` seeded from the card id (a mirrored or
shifted variation of the family plate plus pink accents). Printed on holographic foil stock in game (the foil is the card's, not the art's: don't paint a sheen).

## Subject
Rare. A hub core with fractures and a fried wire looping out of it.

## Composition (3:2, 768 x 512 master)
Breach base; a pink looped wire sparks from one crack; foil card. Base layout: Hex centred with a pink core; five crack lines radiating to the frame.

## Inks
Stock `STICKER_PINK` #F5AFCB; key `INK`, spot `CELL_PINK`.

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
- the hub is the target
- one subject, read in half a second at 100 px wide
- hand-cut, stamped, photocopied feel (ART_BIBLE 1, 2)
- silhouette first: it must read in greyscale (ART_BIBLE 12)
- keep the family's silhouette recognisable: this card must still read as its family

## Don't
- no explosion fire
- no text, numbers or UI glyphs in the art (the band and rules carry them)
- no third ink, no gradients, no glow
- no chrome-and-hologram cyberpunk, no characters or logos from any IP (ART_BIBLE 1)
