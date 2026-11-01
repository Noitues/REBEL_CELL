# Zine collage (G5): the player family as a pasted-up photocopied zine

Stream: style designer, direction G5 of VISUAL_PLAN A.1. Date 2026-11-01. Nothing committed. Scratch and generator copy: `D:/rc_scratch/combat_redesign/zine_collage/` (`src/zn*.py` are the new style; the rest is an untouched copy of `combat_e10_design/final/src`).

Files in this folder:

| File | What |
|---|---|
| `style_board.jpg` | swatches, hand tools (cut, tear, marker, pen, hatch, tape, staple, stamp, ransom alphabet), HP chips, squint test, one slice and one card large, manifesto |
| `plate_A.png`, `plate_B.png` | full 1920x1080 p1_decide (state f1), enemy side and HUD from the E10 generator toned to the corp family |
| `plate_A_wheel_2x.png`, `plate_B_wheel_2x.png` | true 2x of the wheel (the tower is rebuilt at 2x, not upscaled) |
| `plate_A_hand_2x.png`, `plate_B_hand_2x.png` | true 2x of the hand and SEND IT |

## 1. The idea

A rebel cell does not have a studio. It has a photocopier, scissors, a glue stick, tape, a stapler, a rubber stamp and a pile of magazines. So everything the player owns is **cut, pasted and stapled**, and the rest of the screen is the opposite: clean vector glass (corp), machined metal (clock), a CRT (HUD). The ownership read is material, not colour: *if it is torn, it is ours.*

One hand, four tools, shared by the tower and the cards (plan A.1 "the same hand made them"):

1. **Scissors.** Every player shape is a polygon of straight chords, not a circle: wedges are 4 outer chords plus 2 inner chords with a lean of up to 0.9 deg and 0.9 px of radius jitter per piece; the hub is an 18-gon; chips are 3-chord strips. Each cut leaves a **white paper core** of variable width (0.1 to 2.4 px) and a two-layer cast shadow (soft plus contact). This is our L2 (see section 3).
2. **Photocopier.** Black is toner, not ink: density wanders, dust specks pit it, a faint copier streak runs down it. Art is photocopied to **stochastic grain** (blue-ish random threshold, no regular screen), so there are no halftone dots anywhere (VISUAL_PLAN A.1: dots belong to X).
3. **Tape and staples.** Seams and corners. Kraft tape is the style's one secondary ink (plan: "one secondary ink of its own"), pink tape is the identity. They sit only where a real person would put them: the hub end of the spokes, card corners, the ends of the YOU strip, SEND IT.
4. **Ransom alphabet.** Every title and tag the player reads is cut out letter by letter from nine faces (Anton, Impact, Georgia Bold, Times Bold, Courier Bold, Rockwell Bold, Arial Narrow Bold, Permanent Marker, Arial Bold) on six paper stocks, tilted up to 4.5 deg. Rules text is the exception: it stays IBM Plex Sans Condensed on a clean cut label, because it is read most.

Plus two small tools: a **marker** (guns: pink felt tracers with an ink key offset 0.6 px, ending in a cut-paper hit chip) and a **pen** (doodles, cross-hatch).

## 2. The two variants

Both use identical shapes and identical tools, so the style is one thing. They differ in which of the two stocks is the figure and which the ground.

| | **A NEGATIVE (wheatpaste night)** | **B POSITIVE (zine page)** |
|---|---|---|
| Tower ground | hot pink paper disc, creased | black toner disc |
| Wedges | black xerox sheets with a white core; pink shows only in the gutters | newsprint with toner shading near the hub; black spokes |
| Icons | white cut-out with ink key | white cut-out on a black punched badge |
| Hub | cream sticker, pink crest stamp | pink sticker, ink crest |
| Seam tape | kraft | pink |
| Cards | black toner sheet, pink torn art block with a dithered toner ghost, white cut-out glyph, cream label | cream flyer with copier-edge bars, black toner block, pink misregistered ghost, typed label on newsprint |
| SEND IT | pink slab, black toner panel, ransom letters | cream slab, pink torn block, ransom letters |
| YOU strip | black toner strip, kraft tape | cream strip, pink tape |
| Strength | the tower recedes into the board, the hatch is loudest (red on black) | the strongest ownership read at any size, hatch and icons are easiest to read |
| Weakness | black on a dark board has less silhouette (the white core rim carries it) | a large cream mass is the brightest thing on the screen |

My pick: **A**. The cream tower in B wins a one-second ownership test but competes with the HOT red marks around it (section 4, risk 1); in A the tower sits in the board and the pink spokes, kraft tape and white icons still say ours. Do not mix the two: the board needs one stock.

## 3. How it meets the plan

### Family and line grammar (only P is redrawn)

The tower, slices, slice pips, HP ring, guns, hub, cards, SEND IT, nameplate and YOU strip are P. The enemy cells, tokens, K bezel and schedule, T trim and chevrons, the S HUD and the backdrop are the E10 generator, with the plan's A.2 toning (cool slate unit washes; neutral enamel lane outlines; the +2 outline is dotted). That toning is only the same one-call patch the other streams use; the dashed wave arcs, white landing lanes and landing-arc dots that the plan retires are still drawn by the generator and belong to the enemy and clock designers, not to this style.

| Plan line | In this style | Where |
|---|---|---|
| L1 ink keyline | the 1.3 to 2.4 px ink halo under every pasted chip and cut-out | icons, HP chips, stickers |
| **L2 painted stroke ("owned by the player")** | the **scissor cut with a white core**, plus the **felt marker** for tracers | wedges, hub, cards, slabs; guns |
| L3 vector hairline | not used by P (this is what makes P read as not-corp) | none |
| L5 arrowed outline | untouched (hover path, schedule step) | not part of this plate |
| L6 grease pencil | untouched (plan family N); on commit it would burn into marker (FX-T): the marker is what that becomes | none in p1 |
| **L7 cross-hatch** | **pen hatch**: two directions at 45 and 135 deg (each line leaned +-1.6 deg), pitch 2.7 px on chips, 3.9 to 4.6 px on slices, 1.0 to 2.1 px strokes with 0.5 px bow, broken into 6 to 60 px runs, clipped to the shape, with a solid 1.4 to 1.6 px edge in the same colour | HP ring, slice pips, YOU strip, breaking slices |
| L9 glow | the 3 to 4.5 px bloom under HOT hatch only (HP, pips, breaking wedge). Paper never glows | hatch only |
| L10 double line | not on screen in f1. Design intent: a second paper plate pasted over the outer 40 percent of the wedge with two ink edges and a strip of tape (Brace); a stack of two cut plates for SHIELD block | h02, FX-P |
| dashed | none. The only segmented line is the hatch, whose segments cross a shape, never run along an edge. Staples were removed from the HP ring (they read as dashes at 1x) and survive only on cards and slabs as hardware with visible prongs | |

### Time grammar (plan C)

HOT = the pending hatch with its 3 to 4.5 px glow. On this tower the only HOT things are the six hatched HP chips, the six hatched slice pips and the two hatched breaking wedges, so the screen has one P hot mass, as the plan requires. Nothing in the future is hatched. The T trim (solid + notch, thin, dotted) is the generator's and unchanged.

### HP grammar (plan D)

| State | In the hand |
|---|---|
| lit | green cut-paper chip, ink key, tiny shadow |
| lost this END TURN, enemy / soak / us | dark socket, pen hatch in HARM / SOAK / CELL_PINK, solid 1.4 px edge, bloom |
| mend pending | dark socket, 1.6 px GAIN edge, pen plus |
| gone | dark socket, 1.1 px hairline #3A4150 |
| blocked / enemy shield / armor | not P (the block plate is P, see L10 above; not on screen in f1) |

Sizes follow the plan: ring r 150 to 157, 15 chips in 3 groups of 5 (9 deg group gap, 2.5 deg chip gap), slice pips 2 per slice 38 px long and 7 px thick at r 123.5, YOU strip 15 chips in groups of 5.

### Colour (plan E)

Only the identity inks plus one secondary: CELL_PINK #FF3DA8, PAPER #F2EEE4, ZINE_INK #111111 and **KRAFT #C69A62** (the secondary; newsprint #DED8C8 is a paper tone, neutral). HARM, SOAK and GAIN appear only as the meaning colours of the hatch and the lit chips. The outlines carry no colour: every cut piece has a white (or ink) core and nothing else, which answers designer note 5 for P.

Colour-vision check (Machado 2009, severity 1.0, CIELAB dE, script `cvd.py` in scratch): CELL_PINK vs HARM = 65.7 normal, 62.2 deutan, 67.4 protan, **23.2 tritan** (limit 12), so the fallback pink is not needed. HARM vs GAIN is the tightest pair in deutan (26.8) and is carried by shape (hatched socket vs solid chip).

### Readability caps (plan A.1)

- Icons: white silhouette with a 2.1 px ink key, 46 px, survive the nowords plate (`p1_nowords` renders exist in scratch `out/`; the card and wedge icons are the same shapes).
- No glow on paper; only HOT hatch.
- No P texture on ring cells, landing arcs, threat marks or the terminal: the tower disc stops at r 157 (ring cells start at r 161) and the only HUD piece is the taped YOU strip.
- Texture near icons: A's toner dust (0.35 percent coverage, 0.85 px specks) is on the whole wedge, so it comes within 6 px of an icon; B's toner shading is confined to r 49 to 74 (the icon starts at r 69), so it touches the inner end of the icon. Both are far below the 18 percent contrast cap but both break the "6 px" rule literally. Fix if the designer wants it strict: mask the dust and the shade with a 6 px disc round the icon (one extra multiply in `speckle` / `xerox_shade`).
- Squint (greyscale at 280 px, on the style board): P is the only rough, high-contrast, paper-edged family in both variants; E is thin, K is engraved, S is flat glass.

## 4. Legibility risks, honestly

1. **B puts the brightest object on the screen in the middle of the board.** At 280 px greyscale the cream tower out-shouts the HOT chevrons around it, which the plan says must be the only saturated hot mass. Mitigation: darken newsprint by 10 to 15 percent, or switch to A.
2. **Ransom titles.** Mixed faces cost letters: `TWIST` reads, `TRIGGER` and `SPIN 3` read at 1x; the three words in this hand are 5 to 7 letters. Longer titles (FIREWALL, 8 letters; SHOVE) must fit the 118 px cap, which drops the chip height from 24.5 to about 17 px. Not tested on all 11 cards. BREAKER on the hub (14 px chips, 62 px wide) is the smallest ransom text on screen and is readable but the least robust. Mitigation: titles are left-aligned inside the 148 px visible part of each fanned card, and rules text is plain Plex.
3. **Hatch on cream (B)** is a thinner read than red on black (A). It needed a dark under-wash (150 alpha) and 2.1 px strokes to hold; at tritan and at 320 px it is still the weakest hatch.
4. **A black on dark.** Wedge and card silhouettes rely on the 1.1 to 2.2 px white paper core and the shadow; in a bright backdrop room (the other rooms) the black cards would be strong, in a dark one they are weaker than B's.
5. **The fan hides the right 20 px of each card**, as in E10; nothing important (title, cost, tag, rules start) is right of x = 150 on the card.
6. **Staples and tape can read as dashes** at 1x. Removed from the HP ring; on cards they are 16 px bars with prongs and a cast shadow and appear once per card.
7. **Pink next to red** passes the colour-vision check by colour; pink hit chips and tracers cross red threat chevrons on the board, where shape (felt line vs stencil chevron) is the only separation.
8. **Static only.** The style is paper; it does not animate. The X family supplies motion. The one P animation the plan asks for (FX-T, pencil to paint) becomes "pencil to marker": 8 frames of the plan's yellow wax line turning into the pink felt line; not built.

## 5. Build in Godot

The whole look is **baked, not computed**. Nothing here needs a per-frame shader except the hatch.

- **Source art.** `zn.py` and friends are the baking tool: run it offline to emit sprite sheets (PNG, 3x then downsampled to the 1x or 2x the project uses). The same seeds give the same pieces, so a rebuild is stable.
- **Tower (about 60 Sprite2D, 1 atlas).**
  - `tower_ground` (2 sprites: A pink, B black), `wedge_0..5` (each baked with its own cut chords, rim, shadow), `hub` and `crest` (baked), `icon_*` (4 slice icons, white cut-out with the ink key baked in, one per variant), `badge` (B only).
  - Tape and doodles: 3 spoke tape sprites, 6 doodle sprites, baked.
  - HP: 15 `hp_chip` slots and 12 `pip` slots, each a Sprite2D whose texture swaps between 6 baked states (lit, gone, mend, plus the three hatch states). The hatch colour is **not** baked: the chip sprite is the dark socket and a child `hatch.gdshader` quad draws the hatch.
- **`hatch.gdshader`** (canvas_item, about 25 lines): samples a 256x256 tileable hand-hatch tile (two directions, jittered pitch, broken runs) in a mask channel, multiplies by the chip's alpha, tints by a `cause_colour` uniform (HARM / SOAK / CELL_PINK), and draws the 1.4 px edge from a signed-distance channel baked beside the chip. A sibling additive sprite (a blurred copy of the edge, 35 percent) gives the 4 px HOT bloom; it is toggled by the same HOT flag as the T glow, so "hot" has one switch.
- **Cards.**
  - `card_body_A/B` (the sheet or flyer, baked with its cut edge and shadow) and `art_block_{effect_type}` (the plan has 9 effect types; each baked once per variant, with the white glyph cut-out and the ghost).
  - `cost_sticker` (baked paper) plus the shared RAM coin scene from S (`obj2` in the generator), `loud_tab`, `type_stamp_{TOWER,WAVE}` (two baked tags), `label_slip` (NinePatch with torn ends).
  - **Ransom titles** are a `RansomLabel` Node2D: a glyph atlas (9 faces x 36 characters x 6 stocks = 1944 chips at 64 px, about 3 MB) and a deterministic per-string seed picks face, stock, tilt and offset, so the same word always cuts the same way and localisation works at runtime. For shipped English titles the 11 card titles can also be pre-rendered.
  - Rules text is a normal `Label` (IBM Plex Sans Condensed) over the label slip.
  - Hover grow, fan layout and dimming are unchanged (kcard2 / kscene2 logic).
- **Shadows.** Baked into each piece's sprite as a second sprite (blurred alpha, offset 1.6, 2.2 px) so there is no runtime blur; the fan's group shadow is the existing one.
- **Grain.** One 512x512 tileable blue-noise texture drives toner grain in any shader that needs it (stochastic, so no moire with the board). No halftone screen is ever shipped for P.
- **Reduce-effects variant.** The style has no animation and no glow except the hatch bloom; reduce-effects simply turns the bloom off.
- **Cost.** The tower plus hand is about 120 sprites and 1 shader (hatch); the plate bakes took 30 s each on CPU with Pillow/SciPy, so a baking step is a minute at most.

## 6. Open questions for the designer

1. A or B (or A tower and B cards)? I would not mix them.
2. Is ransom lettering acceptable for the card titles, or should titles be a single hand-cut headline per card? A single cut headline is more legible and removes risk 2; ransom would stay on the hub, SEND IT and the YOU strip.
3. Do you want the strict 6 px texture rule applied (cheap, listed in section 3)?
4. Confirm that the plan's "arrowed outline" reading (hover path plus THIS TURN cell) is yours; it does not touch this style.
