# Card layout spec and title legibility rule

Base: F1 black-book card (`finalist_1/p1_decide.png`). The designer likes this LAYOUT. Every punk style keeps the zones below and restyles what fills them (paper, band, icon art, type band, text face). Cohesion with the style beats copying the black-book look; the zones and the legibility rules do not change.

## Card geometry
Design box 176 x 250 px (origin top-left). On the 1920x1080 plate it is drawn at 1.15 (202 x 288 px), fanned 4 deg, pitch 182 px. The rest of the hand sits at 88 percent value; the lifted card is at 1.10 x and full value. All boxes below are in design px (multiply by 1.15 for screen px).

| Zone | Box (x0,y0 - x1,y1) | Content | Rule |
|---|---|---|---|
| Card | 0,0 - 176,250 | sheet, torn or die-cut edge | safe margin 9 px inside the edge; nothing but the cost badge and loud tab may cross it |
| Cost badge | 0,2 - 36,38 (circle r 17.5 at 18,20) | RAM cost digit | top-left, overlaps the corner; digit >= 20 px cap; system cyan coin so cost always reads as RAM |
| Loud tab | 102,5 - 142,29 | eye + "+N" Trace | only on loud cards; top-right, never over the icon disc |
| Art band | 9,10 - 167,128 | style art, spray bloom, ring | all the style lives here; it must still give the icon >= 4.5:1 |
| Icon | 48,26 - 128,106 (glyph 66 px at 88,66) | big white stencil glyph, ink keyline | glyph 66 px, keyline 2.6 px; it is the first read of the card |
| Multiplier | 106,84 - 146,116 | x3 (Spin) | inside the band, bottom-right of icon |
| TITLE | 14,118 - 162,164 (text centre 87,141) | card name | the legibility rule below; overlaps the band's lower edge by about 10 px |
| Type band | 40,160 - 138,182 (centre y 170, 66-74 wide) | TOWER / WAVE | tape, label or tab in the style; text >= 17 px; sits just under the title, may touch it, may not cover it |
| Rules text | 34,192 - 142,222 (centre y 206) | one line, 14-21 px, shrinks to fit 108 px | marker or hand face, >= 14 px, ink on paper >= 7:1; underline on the number |
| Owner mark | 120,222 - 160,242 | pink scribble tag | the owner stamp: this is what says "player card" (pink is owned by the icon and this mark) |

Title width: `<= 128` px, centred at x 87 (the tag overhangs the paper by design). Vertical centre y 141.

## Title legibility rule (any style must meet all)
1. Size: cap height >= 30 px at 1920x1080 (26 design px). Default is 42 px Anton-class condensed capitals (cap 36 design, 41.5 screen). Names up to 7 letters fit at full size; longer names shrink to fit 128 px but never below the floor; if they would, abbreviate the name.
2. Contrast: letter fill vs its own edge >= 7:1 (WCAG luminance). The edge (keyline) vs whatever is behind it, on BOTH the paper and the dark art band, >= 4.5:1. The title straddles the band edge, so it must pass on light and dark at once. A two-ring (fill + keyline of the opposite value) satisfies this by construction.
3. Keyline: exactly one hard keyline, 2.5-3.2 px, opposite value to the fill. No chrome rim, no glow, no gradient fill, no blurred shadow.
4. Drop: optional single hard offset 3-4 px (ink or the owner pink). It may never be the only edge.
5. Colour: title fill is neutral (ink, paper, white). Not the owner pink (pink on cream measured 2.8:1, the cause of the ART CALL 52 complaint). Not yellow, which is the plan mark colour in the grammar.
6. Shape: capitals only, tracking +0.8 to +1.2 px, skew <= 0.16, rotation <= 3 deg, wobble <= 0.5 px. Counters (A, R, B, 3) must stay open at 320 px wide hand strip.
7. Test: 4-card hand at 1x and at 320 px wide; all four names readable at 320 px with no zoom. Fail = restyle.
8. Nowords proxy (no text mode): a single bar at the title position, the same width.

## Measured (design colours)
| Treatment | Fill vs edge | Edge vs paper | Edge vs dark band |
|---|---|---|---|
| F1 original (pink, chrome rim) | 6.2 | 2.8 | 4.7 |
| A black tag, white keyline | 20.2 (white keyline vs black fill) | 17.4 (black fill vs paper) | 15.3 (white keyline vs band) |
| B white chisel, black outline | 20.2 | 17.4 | 1.3 (outline merges with band; white fill carries it) |
| C yellow, black outline | 16.2 | 17.4 | 1.3 |
| D cream on black tape | 16.1 | 16.1 (tape vs paper) | 1.2 (tape merges with band) |
