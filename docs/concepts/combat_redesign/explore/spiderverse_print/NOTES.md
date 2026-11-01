# Spider-Verse print (G3), player wheel + hand

Style designer notes for the "offset print" direction. Deliverables in this folder: `style_board.jpg`, `plate_A.png`, `plate_B.png` (1920x1080 p1_decide, state f1), `crop_wheel_A/B.png` and `crop_hand_A/B.png` (2x). Generator copy: `D:/rc_scratch/combat_redesign/spiderverse_print/src` (new files `sv_lib.py sv_icons.py sv_tower.py sv_cards.py sv_ui.py sv_plate.py sv_board.py`; the E10 source is untouched). Run `python sv_plate.py A` (or `B`) from that folder.

## The idea

The Cell runs its own offset press. Everything the player owns is a **print**: the tower, slices, our HP, guns, cards, SEND IT, the nameplate and the taped YOU strip. Everything else (enemy cells, clock, HUD terminal) stays clean digital. The ownership read is a material read: printed and slightly off-register versus perfect and machine-made.

The signature is **misregistration**. The pink plate sits 2-4 px off the black key plate, a press-cyan plate peeks out on the opposite side, and the key lines are hand-inked with a varied weight (heavier on the lower-right shadow side). One shared "hand" (a 1.3 px low-frequency coordinate warp plus ink-bleed edges) cuts every player shape, so the tower and the cards are visibly made by the same hand.

Two variants of the same style, same information:

| | A "comic page" | B "print shop" |
|---|---|---|
| Tower ground | Paper page disc with a heavy inked contour; slices are inked comic panels, paper gutters | Ink-black ground; flat spot-colour plates, big 4.6 px misregistration, registration targets round every icon seat and the hub, crop marks at the HP group gaps |
| Shading | Hand hatching in deep magenta (domain-warped lines that wander and stop short) | Stochastic riso grain plus a ragged overprint plate (no hand hatching) |
| Hub | Kirby hit-frame burst, caption strip, Ben-Day dots at 10 percent | Registration target rings in offset pink and cyan, ink caption strip |
| Cards | Comic panel: kirby rays and dots in the art band, paper title box, ink-on-paper caption box for rules | Print ticket: registration rings, ink title slab, pink quote bar, test-strip bar, crop marks |
| SEND IT | Hit-frame burst with a tilted paper slab | Ink slab with a pink plate offset and corner trim marks |

## How it meets the plan

**Families.** P is the only family with paper, ink, pink and a wobble field. E, K and S are untouched in material (E recoloured to slate, see below). X (effects) keeps the halftone: this direction allows Ben-Day only in the hub art and the card art band, at 10 percent coverage (plan A.1 cap is 12), so if G3 wins the X family must switch to its light-leak fallback.

**Line grammar.** L1 ink keyline: every mark carries it. L2 painted stroke: gun tracers (tapered pink, ink-sheathed), muzzle beads, hit stars. L7 cross-hatch: red on the 6 pending HP segments (tower ring and YOU strip), on slice pips that go this turn, and on the two slices that break (panel goes dark, red hatch, solid red edge, stencil X in the outer corner, never over the icon). L8 dotted: the future threat trim and the +2 board outline; no dashes anywhere on the board (the generator's dash routine is replaced with dots for pale lines and solid for the rest). L9 glow only on HOT red marks (this-turn trim, pending hatch). L10 is not shown in f1 (no Brace or SHIELD block active in this state).

**Time.** The tower's threat trim follows C: this turn is solid HARM red with a keyline, glow and an inward END notch; +1 is a thinner desaturated solid bar with one turn pip; +2 is dotted with two pips.

**HP.** 15 segments in 3 groups of 5 at r 149.5-156.5; the pending run starts at the needle and runs clockwise (6 red-hatched, 9 green lit). The YOU tally on the terminal uses the same grammar in the same order, on a paper strip with masking tape. Slice pips: 2 per slice, lit green, lost red-hatched. The white slash is gone.

**Colour.** Pink = ours. Press cyan is used only as the misregistration fringe and the back plate, never as a meaning. The RAM cost coin stays system cyan (plan I), the loud tab stays Trace violet. Slice frames are all the same painted frame; the type is the icon only. Lane outlines are neutral enamel with value stepping by depth, mauve units are graded to slate (post-process hue shift on the board layer).

**Wave info (note 6).** Not redesigned here (it belongs to the clock stream); the plate still has the E10 W4-W6 arcs. The plan's queue strip is a separate deliverable.

## Legibility risks

1. **Pink beside red.** The player pink (#FF3DA8) sits close to HARM (#FF4433) on the same tower. Mitigation built in: red only ever appears as hatch, trim or X on dark or paper, never as a flat fill on pink; a breaking panel turns ink-dark so the red hatch is not drawn on pink. The plan's colour-blindness check has **not been run on this plate**; it must be before a pick.
2. **Red trim next to red pending HP** on the right of the ring (sectors 1-2). The 5.5 px gap and the two ink keylines separate them at 1080p, but at 320 px they merge. Moving the pending run is a plan-level decision.
3. **Texture near icons.** Hatch, grain and overprint are cut away within 6 px of each icon seat and the pips; checked by eye at 2x only.
4. **Misregistration reads as blur** at small size or on a bad scaler. It is 2 px in A (survives 1080p) and 4.6 px in B (reads as a deliberate offset, costs more outline clarity). Reduce-effects mode: render with offsets 0.
5. **B card colour bar** at the bottom of each ticket looks like a pip row; it is decoration and should be dropped if it confuses (content guard: no extra counts).
6. **Board still carries E10 leftovers** outside this stream: hazard tape at the bezel, some ring-separator dashes in the lane tracks, the W4-W6 arcs, ring tags in red/white chips. They are not part of this style pass.
7. **Not shown:** the other beats (p2, p2b, p3, nowords), Brace/soak/mend states, the hover plates. The nowords variant is supported by the tower and card functions (text suppressed) but was not rendered.

## Godot build

- **Hand-cut shapes.** Slice wedges, pips, HP segments and card panels are authored as vector polygons (Line2D / Polygon2D or SVG import) with a shared **wobble** applied in a canvas-item shader: sample a tiling 256 px noise texture in screen space and offset the UV by up to 1.3 px. Same noise on tower and cards is what makes it "one hand".
- **Misregistration** is a two-pass shader on each player sprite: pass 1 draws the colour plate (pink) offset by `uniform vec2 misreg` (2 px A, 4 px B), pass 2 draws the key plate (ink lines) at the origin, and a third tinted copy offset the other way supplies the cyan fringe. The offset is a uniform, so reduce-effects sets it to 0 and the style survives. Can be baked per asset into a 3-layer sprite (colour, key, fringe) and recombined with `CanvasItemMaterial` blend modes, which is cheaper for 4 cards.
- **Paper, grain, ink bleed** are tileable textures (paper 512 px, grain 256 px) multiplied in the shader; ink-bleed edges come from thresholding a blurred SDF-style mask against the grain (an `smoothstep` on `texture(mask)+noise`), the same trick as `rough()` in `sv_lib.py`.
- **Hatching** (hand hatch, L7 cross-hatch) is a shader on the region mask: stripes in rotated UV space with a domain warp from the noise texture, broken by a second noise threshold. L7 uses two angles (45/135), pitch 5-6 px at 1080p, plus a solid 2 px edge. Colour is a uniform (HARM, SOAK, CELL_PINK) so the cause colour is data-driven.
- **Ben-Day dots** (hub and card art band only) use the shader's `halftone()`: rotated grid, dot radius = `sqrt(value)`, value capped at 0.10. Or a baked 6 px tile texture.
- **Icons** (rocket, shield, turret, bandage, brace, spin, crosshair, twist, eye, emblem) are single-colour silhouette SVGs with a "cut" layer; the shader stack is white fill, ink outline (SDF grow 1.9 px), pink offset plate. 44 px.
- **HP ring and pips** are 15 + 12 pooled `Polygon2D`s driven by `hp`, `pending`, `soaked`; state selects the material (lit paint, lost hatch + glow, gone socket).
- **Cards** are a `SubViewport` per card baked on state change (cost, title, rules text) and rotated in the fan; the print offset is applied to the whole card in the viewport texture. Titles use Anton with a pink offset duplicate (a label shadow with 0 blur); rules text uses IBM Plex Sans Condensed. Marker (`Permanent Marker`) is used only for the `x3` hand note.
- **Guns** are `Line2D` with a width curve (taper), pink with an ink outline sibling, wobble from the shared shader.
- **Sprite sheets** needed: icons x10, burst/hit star (6 frames, hit frames at 3 per second max), hub burst, caption strips, tape pieces. Everything else is shader-driven, so a re-skin (G1, G2) swaps textures, not geometry.
- **Cost.** One 4-texture material per player canvas item; the tower is one SubViewport re-baked only when slice HP or `hp` changes.

## Reproduce

`D:/rc_scratch/combat_redesign/spiderverse_print/src`: `python sv_plate.py A`, `python sv_plate.py B` (writes `out/plate_X.png`; tower and hand are cached in `out/`; the tower render takes about a minute), `python sv_board.py` for the style board. State: `state_e10.json` f1, unchanged.
