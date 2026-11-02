# MURAL GRAFFITI: per-slice colour and texture pass (ART CALL 52 follow-up)

Designer request: each unique slice a different colour and texture, not all the same pink. Designer note: no colours need avoiding.

Files: `slice_key.jpg` (each type large, colour / grey / red cross-hatch, plus the whole wheel in colour and grey), `plate_A.png`, `plate_B.png` (full p1_decide, 1920x1080, bio cutaway), `wheel_crop.jpg` (old one-colour A, new A, new B at 2x). Generator: copy of the mural concept in `D:/rc_scratch/combat_redesign/punk_slices/mural_graffiti/` (changes are in `src/mu_art.py`, plus `sl_tw.py`, `sl_key.py`, `sl_crops.py`).

The wheel has four slice types (from the state: BURST, TURRET, SHIELD, REPAIR; two BURST and two SHIELD slices on the plate). Same type = same colour and texture. Everything else (hub, cards, rings, HUD, grammar, no needle, game information) is unchanged.

## Palette and texture per type (mid-tone of the paint gradient)

| Type | A (brick, airbrush) | B (concrete, cel) | Texture (both) |
|---|---|---|---|
| BURST | hot pink `#FF3DA8` | tangerine `#FF6C1E` | sunburst rays out of the icon, light and dark spatter dots thickening toward the rim |
| TURRET | sun yellow `#FFD41E` | acid lime `#A0E22C` | concentric target rings around the icon |
| SHIELD | cobalt `#2C64F2` | aqua `#22B8EE` | overlapping scales (armour plating) |
| REPAIR | mint green `#22D086` | violet `#9854EE` | plus signs, staggered grid |

Each type has its own light-to-shadow gradient, lit-edge glow, shade, icon drop colour, overspray and drip colour, so a slice reads as its own spray colour, not a tint of one. The icon drop shifts per type (A: orange, orange-red, cyan, yellow; B: magenta, blue, magenta, yellow).
A applies the texture as soft airbrushed stencil, B as hard cel marks. Textures are kept clear of a 30 px disc around the icon, so the icon stays on clean paint.

## One punk set

All slices share the A or B family rules: full-saturation spray, the ink outline plus white keyline, cast shadow and block drop, the same overspray speckle and drips, the same wall showing through. The player wheel is still one object against the muted slate corp rings. A keeps pink as the anchor (BURST). B drops pink and uses a hot cool-warm set; its ownership read comes from the shared outline grammar, not from one hue.

## Shift away from reserved colours

None avoided, as asked. Overlaps to know about: SHIELD blue in A and aqua in B sit near the HUD cyan and the SOAK blue; REPAIR green (A) sits near the HP block green around the hub; REPAIR violet (B) is near the TRACE purple; BURST orange (B) and TURRET yellow (A) are near the HOT / plan marks of the grammar. The ink-outlined, textured slices keep them apart from the thin HUD marks, but the art director should check these on the full board.

## Red cross-hatch legibility

Tested by rendering all four types in pending-loss state (slice_key.jpg, bottom row of each variant, and the real broken slices on the plates: SHIELD and TURRET).
The slice colour was never changed for it. The hatch got a treatment instead, applied to every slice: an ink keyline under each red line (about 1 px each side), a wider 7 px pitch so the paint and texture show between the lines, a thin ink line inside the red outline, a faint dark wash (10 percent). The red X has its ink edge as before.
- Reads well: yellow, green (A), blue, violet, pink, aqua.
- Weakest: orange (B BURST) and the orange-yellow shade of yellow (A TURRET), where red and paint are close in hue; the ink keyline carries it. It reads, but is the one to look at first on the real screen. If it needs more, thicken the keyline on those two only.
- The slice type still reads under the hatch through the cleared icon disc, which keeps the slice colour, and the paint colour between lines. The texture is mostly hidden by the hatch (by design: hatch wins).

## Grey proof

In `slice_key.jpg`, grey row and whole-wheel grey: values separate by type (yellow / lime lightest, pink and mint mid, blue darkest), and the four textures differ in shape (dots and rays, rings, scales, plus signs), so a type reads without colour. A: BURST vs REPAIR are close in value, the texture separates them. B: TURRET and SHIELD are both fairly light, rings vs scales separate them.

## Risks and notes

1. More colours make the wheel louder. I did not re-run the squint (loudness) metrics.
2. Spatter on BURST is the busiest texture; if it competes with the pips on the outer rim, cut the dot count first (230 dots, one number in `mu_art.py`).
3. The cards, hub and SEND IT stay pink / warm, so on A the BURST slice is the only one that matches the cards. A matching colour per card type was not asked and not done.
4. Not re-run: dash audit, game-info check, p2/p3 beats. No dashed draw calls were added.
5. The slice key crops are rotated so every wedge sits at the top; icons appear tilted there only.
