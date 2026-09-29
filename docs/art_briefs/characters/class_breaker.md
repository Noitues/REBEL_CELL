# Breaker — operative portrait brief

**Family:** operative class (ART_BIBLE §7.1). **Content id:** `breaker` (`content/classes/breaker.tres`).
**Deliverable:** painted portrait, 1:1, **1024 px master**, strong value contrast; four expressions; per-operative variation layers. Drops into `ClassData.portrait` / `Polaroid.portrait` with no code change.
**Concepts:** `docs/art_review/W5/concepts/class_breaker_*.png` (pixel art, not final). Stand-in: `PortraitArt` (NEON BUST).

## Pitch
The Cell's front door: the one who goes through walls. Heavy, grounded, stubborn.

## Silhouette (head and shoulders)
A heavy padded work jacket whose squared shoulders reach the frame edges, collar popped. A crowbar bent into an antenna rises from behind the right shoulder and hooks over the head.

It must read from the outline alone (fill it black and it is still a Breaker):
- The widest shoulders of any class.
- The hook of the crowbar breaks the top edge of the head's outline on the right.

## Prop
The crowbar-antenna (hooked tip, a small LED at the end).

## Accent
`Palette.class_accent(&"breaker")` = **#FF3DA8** (CELL_PINK). The accent lives **only** on the portrait (rim light, eyes, prop lights), the wheel's bezel ornament (*Riveted plates*, W3) and the dossier stripe. Never on UI roles.

## Value and light
- Figure mass near black (`NIGHT_SKY` #060816) against a backdrop that falls from night to a dark accent at the bottom.
- One rim light down the lit side in the accent; eyes are the brightest point.
- Details in the accent at lower value: Jacket seams and zip, the crowbar's LED, the visor band.
- Test: at 64 px and in greyscale, the silhouette and the eye feature still read.

## Expressions
| Expression | Beat | Notes |
|---|---|---|
| Neutral | Default on every screen. | Eyes/visor lit in the accent, mouth a short line, head level. |
| Hurt | HP loss, low HP (combat Polaroid glitch). | Head turned ~8° and dropped, eyes squinted to half, a grimace, two `HARM` (#FF4433) scratches on the cheek and a crack across the eye feature. Accent stays. |
| Triumphant | Victory, a Perfect, level up. | Chin up ~6°, eyes glowing brighter (a wider bloom, highlights to `TEXT_HI`), a grin, one fist raised at the lower right (breaks the frame edge). |
| Flatlined | Death (FLATLINED screen, downed dossier). | The whole portrait greyed (luma) and dimmed ~30%, head slumped ~14°, eyes crossed out, a heart-monitor line that blips once and runs flat across the lower fifth. No accent colour anywhere. |

## Per-operative variation
Per-operative variation comes from a hash of the operative id (`PortraitArt.operative_subject`, deterministic); it must stay **inside** the class:
- **Hair** (4 styles, under or around the prop): short spikes, swept fringe, cap, top knot (per class: the prop always dominates the outline).
- **Visor** (3 variants of the class's eye feature): band / twin lenses / thin slit, or the class equivalent (slit width, goggle lens size, LED segment count, mask slit angle).
- **Tint** (3 shades): the class accent lightened 7%, as is, or darkened 7%. Never another hue: every shade stays nearer its own accent than any other class's (tested).
The painted set needs the base portrait per class plus overlay layers for 4 hair x 3 visor (or a painted set per combination), with the tint applied as a colour grade on the accent layer only.

## Material
Shown through the screen's material: a Polaroid print on PAPER (HQ dossier, combat Polaroid, wanted poster) and scan lines in the net. Paint clean; the shaders add grain and scan.

## Do / don't
- Do keep the prop inside the 1:1 frame (it may touch the top edge, never crop the head).
- Do keep the face readable through the eye feature at 96 px.
- Don't: Never a sword, gun or baseball bat: the crowbar is a tool, not a weapon. Never a hood (that is Ghost).
- Don't copy characters, logos or doodles from any existing IP (ART_BIBLE §1).
