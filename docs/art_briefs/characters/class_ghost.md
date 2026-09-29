# Ghost — operative portrait brief

**Family:** operative class (ART_BIBLE §7.1). **Content id:** `ghost` (`content/classes/ghost.tres`).
**Deliverable:** painted portrait, 1:1, **1024 px master**, strong value contrast; four expressions; per-operative variation layers. Drops into `ClassData.portrait` / `Polaroid.portrait` with no code change.
**Concepts:** `docs/art_review/W5/concepts/class_ghost_*.png` (pixel art, not final). Stand-in: `PortraitArt` (NEON BUST).

## Pitch
The infiltrator nobody remembers: present in the camera feed as a smear.

## Silhouette (head and shoulders)
A peaked hood that is the whole head outline (point slightly off-centre), falling straight to narrow, sloped shoulders. Inside the hood opening, the face is covered by a fine face-mesh grid.

It must read from the outline alone (fill it black and it is still a Ghost):
- The only peaked outline.
- The narrowest shoulders.

## Prop
The face-mesh (a grid over the face), eyes as two small points of light through it.

## Accent
`Palette.class_accent(&"ghost")` = **#9FE8FF** (Ghost accent). The accent lives **only** on the portrait (rim light, eyes, prop lights), the wheel's bezel ornament (*Flickering translucent rim*, W3) and the dossier stripe. Never on UI roles.

## Value and light
- Figure mass near black (`NIGHT_SKY` #060816) against a backdrop that falls from night to a dark accent at the bottom.
- One rim light down the lit side in the accent; eyes are the brightest point.
- Details in the accent at lower value: The mesh grid, the two eye points, a fringe of hair under the hood on some operatives.
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
- Don't: Never a ninja mask or a skull. Never a cloak cape: the hood ends at the shoulders.
- Don't copy characters, logos or doodles from any existing IP (ART_BIBLE §1).
