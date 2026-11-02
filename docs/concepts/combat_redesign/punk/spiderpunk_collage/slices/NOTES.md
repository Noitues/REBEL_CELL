# Spider-Punk collage: per-slice colour and texture pass (ART CALL 52 follow-up)

Designer request: each unique slice a different colour and texture instead of one colour for all. Designer ruling: "I don't think we need to avoid any colors", so no colour is reserved here (the VISUAL_PLAN rule "no slice-type colours, no lane colours" is lifted for the wheel slices).

Files: `slice_key.jpg` (each type large: colour | grey | red cross-hatch, with hex), `plate_A.png`, `plate_B.png` (full p1_decide, 1920x1080, bio cutaway), `wheel_crop.jpg` (old one-colour A | new A | new B, 2x), `src_snapshot/sps2_*.py` (patch layer over the sp_*.py generator in the parent `src_snapshot`; run `sps2_plates.py A|B`).

Slice types on the wheel (state `wheel[].t`): BURST, SHIELD, TURRET, REPAIR. Slices of one type match exactly.

## Palette and texture (variant A, POSTER: purple page, white cut edges, bone lightning)
| Type | Colour | Fill / shade | Texture (ink) | Grey value |
|---|---|---|---|---|
| BURST | hot magenta | #FF2D96 / #EC1680 | coarse staggered Ben-Day dots (#A0065C) | 119 |
| SHIELD | cobalt | #2C5CF6 / #1C3ED4 | overlapping fish-scale plates (#0A1678) | 95 |
| TURRET | print yellow | #FFD000 / #FFB200 | concentric target rings around the icon (#B05400) | 198 |
| REPAIR | mint green | #46E082 / #22C468 | bold plus crosses (#066034) | 167 |

## Palette and texture (variant B, GIG FLYER: newsprint page, yellow cut edges, ink lightning)
| Type | Colour | Fill / shade | Texture (ink) | Grey value |
|---|---|---|---|---|
| BURST | tangerine | #FF7418 / #F05408 | coarse staggered dots (#962400) | 147 |
| SHIELD | aqua | #089EB8 / #007E9E | fish-scale plates (#022C50) | 116 |
| TURRET | acid lime | #ACEE14 / #8ADA08 | concentric target rings (#346200) | 193 |
| REPAIR | violet | #9C58FF / #7A3AEE | bold plus crosses, pale (#FAECFF) | 127 |

Texture is the type carrier: dots, scales, rings, pluses stay different in the grey column of the key. Values are also spread apart (A 95 to 198; B 116 to 193). In B, SHIELD and REPAIR are close in grey (116 and 127), so only texture separates them there.

## One punk set, still opposed to the corp side
Every slice, whatever its type, shares: the same jagged cut-paper silhouette, a scissor-cut edge (white in A, print yellow in B), the black offset drop, a thin ink trace inside the edge, masking tape and a newsprint scrap, a darker Ben-Day shade toward the lower right, a white icon with an ink outline and a misregistered colour plate under it, and the same saturated print finish. The page, lightning (bone in A, ink in B) and hub are unchanged except the lightning recolour. The corp board stays muted slate glass, so the loud print set reads as the Cell's.

## Shift away from reserved colours
Previously reserved: yellow (PLAN), orange (SCHEDULE), cyan/teal (HUD, corp), green (GAIN), blue (SOAK), red (HARM). Now used on slices: yellow and mint green (A), tangerine, aqua, acid lime and violet (B), cobalt (A). Consequences handled:
- A's yellow lightning shards became bone, so yellow is only the TURRET slice. The icon plate under a yellow slice is magenta.
- The cobalt of A's SHIELD is near the SOAK indigo; the soak hatch would be read as "indigo on cobalt". Soak keeps its own hatch (indigo plus the keyline) but this pairing was not rendered (no soaked slice in the state); flag it for a later check.
- Green HP pips sit on mint green (A REPAIR) and acid lime (B TURRET): pips keep their ink outline and sit on their own band, and still read in the plates, but the mint slice is the weakest pip background.
- The tape on all slices is now neutral masking tape (was yellow).

## Red cross-hatch legibility (tested on all 8 slice colours, `slice_key.jpg` third column)
Red HARM (#FF4433) has a poor luminance contrast against several slices (1.0:1 on magenta, 1.2:1 on violet, 1.3:1 on tangerine, 1.5:1 on cobalt), so hue alone does not carry it. The fix is on the hatch, not the slice: the cross-hatch now has a keyline under it (a 3.0 px line under the 1.7 px red line, pitch 6.0) and the same keyline under the pending-loss outline. The keyline is ink (#111111) on magenta, yellow, mint, tangerine, aqua and lime, and deep navy (#0E0A38) on cobalt and violet. A light dark wash (0.17 to 0.23) lies under it. The slice colour still reads through the hatch, and the clear disc around the icon keeps the type colour at full strength.
- Reads best: yellow, lime, mint, aqua.
- Weakest: tangerine (red on orange): readable only because of the ink keyline, and the slice turns brown-orange. Cobalt and violet go dark and purple but the type stays identifiable by texture and icon halo.
- The grammar is unchanged: cross-hatch plus the corner X means loss at END TURN; partial damage (white crack) and hatched pips are the F1 draws.

## Not changed / not done
- Hub, cards, SEND IT, nameplate, rings and HUD are as in the concept (the cards keep their yellow title strips from ART CALL 52). Needle stays removed.
- Only p1_decide was rendered. Hover, plan beats and effect overlays on the new slice colours were not rendered. Dash audit and info check not re-run.
- Loudness is higher than the single-colour wheel (four hues instead of one); the squint target was not re-measured.
- Textures are kept out of a 24 px disc around the icon and fade in over 7 px; their contrast is moderate, not capped at the 18 percent plan figure.
