# XEROX FLYER: punk-rock concept for the player wheel and hand (ART CALL 52)

Style refs: 5 (xerox punk flyer) and 9 (posterized stencil). Built from a copy of the F1 generator at `D:/rc_scratch/combat_redesign/punk/xerox_flyer/src` (new files: `xf_gfx.py`, `xf_tower.py`, `xf_cards.py`, `xf_ui.py`, `xf_guns.py`, `xf_render.py`, `xf_board.py`). F1 itself was not edited. No needle: the marker at 12 o'clock on the outer schedule ring is removed (the THIS TURN tape marks its own start).

## Files
| File | What |
|---|---|
| `style_board.jpg` | palette, textures, line samples, one slice, both hubs, card A and B large, 3-line manifesto |
| `plate_A.png` | full p1_decide (bio cutaway), variant A: white photocopy sheet |
| `plate_B.png` | same screen, variant B: black toner sheet with a die-cut white border |
| `wheel_crop.jpg` | A and B wheels at 2x, side by side |
| `hand_crop.jpg` | A and B hands at 1x |

## The idea
The Cell stole the copier. Everything the player owns is a black photocopy with a coarse halftone, flat spot-ink blocks (magenta, with cyan as the misprint plate) slapped on crooked, toner grain and a copier-lid edge shadow. Solace stays clean glass and enamel, so ownership reads from material even in grey.

- **A "white sheet".** A dirty-white page (80 percent value, under the L* 75 cap), six flat magenta blocks off-register from a heavy black key line with a block drop, coarse black halftone at the hub end and rim end of each slice, a paper-white stencil highlight on the lit edge, a cyan halftone fringe on the margin, registration marks, a copier-lid shadow. Hub: black disc and magenta starburst.
- **B "black toner".** The same board photocopied on black: die-cut white sticker edge, white keylines, magenta blocks. Darker on the board, so it is quieter in the squint than F1 and than A. Hub: white disc.
- **Hub lettering (both):** BREAKER as ransom-note tiles, each letter cut from a different scrap (white, magenta, cyan, black), tilted.
- **Cards (same layout as F1):** cost coin top-left, big icon in an art band, title, type band, rules text, Trace tab top-right.
  - A: white sheet; black art band with white halftone dots; magenta disc with a cyan crescent behind the icon; the title sits on a white label slab in black Anton with a magenta ghost; TOWER/WAVE on a flat cyan block; rules in black.
  - B: black sheet with a white die-cut border; magenta art band with black halftone; paper-white disc; the title is paper white on black inside a white-rimmed slab, magenta ghost; type on a white block; rules in white.
- **Title fix (ART CALL 52 note 1):** F1's pink-on-dark tag is gone. Titles are black on white (A) or white on black (B), 38 px Anton, with the magenta ghost only 1.7 to 2.2 px off, so the letter stays the highest-contrast thing on the card. Rules text is IBM Plex Sans Condensed Medium at about 22 px (fit-to-width, left-weighted so the overlapped hand never clips it; measured on the 1x hand crop).
- **Other player pieces restyled to match:** YOU strip (a pasted photocopy strip), SEND IT (magenta slab with halftone, black key block drop, white stencil letters; B is a white slab with black letters), nameplate, and the guns (black key stroke, magenta stroke 1.6 px off, jagged white burst with a magenta core).

## How it keeps the ART CALL 51 grammar
- **No dashed lines.** Nothing is dashed. Halftone dots are a fill, not a line. The only dots on the board remain the existing +2 trim.
- **Time marks** (HOT, COLD, FAR) are the F1 T-family trim, untouched and composited on the tower (flat stencil, ink keyline). Board rings, schedule and landing arcs are unchanged.
- **Cross-hatch = lost at this END TURN.** Pending HP blocks, pending slice pips and a breaking slice use a hard straight cross-hatch in the cause colour (red = enemy). It is the only straight, mechanical hatch in the P family; the shading is halftone dots, never hatch, so the two never read alike. Pending blocks bulge 2 px, as before.
- **Arrowed outline = movement** only. Not touched.
- **One enamel outline for enemy cells** and gold for the boss: untouched.
- **W4-W6 tickets**, 12 colours and their meanings: untouched. Cyan appears only as the off-register plate and the RAM coin (unchanged), never as a meaning; magenta stays "ours"; yellow is not used by the Cell (it stays PLAN).
- **Same game information:** same sim state `f1` (12 to 6, YOU 9 kept and 6 hatched, hand Brace, Spin 3, Trigger, Twist, same costs, rules text, x3 multiplier, Trace +1 tab). The slice pips, brace plate, soak mark, break X and crack zig-zag exist in the generator for the other states.

## Legibility risks
1. **Halftone under icons.** Dots are cleared in a 27 to 41 px radius around each icon and the cap is a 0.6 coverage ramp, but the rim-end dots on a 1x screen are 6.4 px pitch and shimmer when the wheel turns. Fix in motion by snapping the screen to the wheel, not the screen (see build).
2. **Hatch on magenta (broken slices).** Red hatch over a darkened magenta is lower contrast than F1's wash; the solid red edge and the stencil X carry the read. Check at 320 px.
3. **BREAKER ransom tiles** are 15 px letters at 1x and are the least legible text in the set. The tiles read at 2x; at 1x the word is guessable from the tile rhythm. If this fails, use one plain Anton line for the name.
4. **Card B's pink slab edge** competes with the title; the title itself is white on black and survives, the rim is the first thing to drop.
5. **Loudness.** A is about F1's loudness with a duller tower (grey paper); B is quieter (black disc). A squint and loud-share measurement was not run (colour-blind checks are ignored per ART CALL 52, and the squint tooling was not re-run on these plates). Measure before approval.
6. **Cyan** (process cyan #12A9E6) sits near NET_CYAN. Material tells them apart (halftone fringe vs glass terminal), but if the HUD and the cards ever sit adjacent, shift the misprint plate to a teal.
7. The hand overlaps by about 20 px; text is centred on the visible 158 px, and the last card is fully visible.

## How it would be built in Godot
- **Slices, hub and cards are flat 2D sprites, not a shader stack.** Each slice is a Polygon2D (magenta) with a black key outline that is a second Polygon2D offset (3 px, 3 px) for the block drop; the off-register is a 2 to 3 px offset between plates, authored once and baked into the mesh transforms, never animated.
- **Halftone** is one `canvas_item` shader on a shared mask texture: `dot = step(length(fract(rot(uv, 45 deg) * pitch) - 0.5), radius(value))`, with the value taken from a baked gradient texture per slice (hub end, rim end). Screen-locked to the wheel (UV in wheel space), so it rotates with the slice; otherwise it shimmers.
- **Toner grain and dropout:** one 512 px tiling noise texture multiplied into every P sprite (alpha dropout 7 percent); a 1 px speckle layer on the page. Static, no per-frame cost.
- **Page, copier-lid edge, registration marks, doodles:** one baked PNG per variant (the page disc is static); the wedges, icons, pips, HP blocks and hub are separate nodes so they can animate (turn, hit, break).
- **Hatch (L7):** a tiled hatch texture (45 and 135 degrees) clipped by the block or wedge polygon as a mask; colour from the cause token. Pending blocks bulge 2 px (scale the polygon).
- **Cards:** one Control scene with a nine-patch sheet (A white, B black), an art-band texture with the halftone baked per card type, a Label for the title (Anton, black or white, with a 2 px offset shadow in magenta), a Label for rules text (Plex Condensed Medium), the cyan or white type band, the RAM coin and the Trace tab. All text stays live Label text for localisation.
- **Hub lettering:** seven small tile sprites with a Label each; or one baked texture per language.
- **Guns:** Line2D (black, width 9) plus Line2D (magenta, width 5, offset 1.6 px) and a burst sprite at the target.
- **Cost:** about 14 sprites and 2 materials (halftone, grain), no per-frame CPU work; the wheel turn is a Node2D rotation.

## Process note
One accidental empty `python -` heredoc was started once and stopped at once (no input, no output); every other script was a file run by path.
