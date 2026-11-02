# Card system, locked style (ART CALL 53)

WPAP card (chamfered die-cut, flat facet planes, slanted plates, hard offset drops), the black-book layout (LAYOUT.md zones), a type band colour per card type, band art from the other punk styles, and the xerox icon recoloured per card. All 11 Shifting Waves cards, 5 states.

Files: `card_sheet.jpg` (11 cards x normal / lifted / played liner / unaffordable / nowords), `hand_p1.jpg` (p1 hand at 1x and 2x on the bio cutaway, plus Trigger lifted), `type_band_key.jpg`, `legibility_1x_320.jpg`, `checks.json` (measured numbers), `src_snapshot/` (the module). Working copy: `D:/rc_scratch/combat_redesign/locked/cards/src/`.

## Entry point (for the assembler)
`card_render.draw_card(card, size, state) -> PIL RGBA`
- `card`: name ('Brace', 'Spin3', ...) or dict `{'name':..., 'cost':..., 'loud':..., 'txt':..., 'nm':..., 'fam':...}` overrides.
- `size`: card box width in px (or (w,h)). Output = box + 18 design px margin each side (`margin_px(size)`); card centre = image centre. 1.15 x = 202 px; for the lifted card pass 1.10 x that.
- `state`: `'normal' | 'hover' | 'played' | 'unaffordable' | 'nowords'` or `{'mode':..., 'dim':0.88, 'nowords':bool}`. `dim` is the 88 percent value of a resting hand card.
- Pure numpy/scipy/PIL. Glyph PNGs (`glyphs/`, dumped once from the E10 glyph library by `dump_glyphs.py`) and fonts (Anton, IBM Plex Sans Condensed, Share Tech Mono; copy from `assets/fonts` into `src/fonts`) sit beside it. The 11 cards take about 1 min at 1x; bases are cached per size.
- Card data (cost, Trace, name, rules text, family) is from `state_e10.json` `cards` and the E10 `build10.py` text. Nothing invented. The multiplier plate on Nudge / Spin 2 / Spin 3 is the E10 `x` field.

## Types and palette
The state has exactly two card types (the `fam` field): TOWER and WAVE. There is no third type in Shifting Waves, so there are two band colours; I did not invent finer types. Effect kinds (h01-h09 in VISUAL_PLAN) are carried by the band art, not the type colour. Spare slot if build adds a type: cobalt #2F5BFF (white text) or bone #F1EAD6.

| Type | Colour | Text | Cards | Ink text on plate |
|---|---|---|---|---|
| TOWER | teal #19D3BC (dark #0B7F73) | ink | Nudge, Spin 2, Spin 3, Brace, Strike | 9.8:1 |
| WAVE | violet #A683FF (dark #5A33C9) | ink | Firewall, Pull, Shove, Twist, Hold, Trigger | 6.5:1 |

The type colour appears in three places only: the type plate under the title, a thin rule on the top edge of the title plate, and the bottom-left paper facet (plus the multiplier plate on Spin cards, in teal). Pink stays owner (rules underline, owner triangles, title offset, disc accents), cyan stays the RAM coin, yellow and orange stay the plan and schedule marks, red stays harm, green stays HP. Teal vs violet in grey is 1.52:1, so they depend on hue and on the printed word; the nowords proxy uses plate width (TOWER wider). On paper the plates are 1.6 and 2.5:1; the ink keyline and hard drop carry the edge.

## Style per card
| Card | Type | Band style | Why | Icon disc (second ink) |
|---|---|---|---|---|
| Nudge | TOWER | Ben-Day sky blue, 1 speed arc | the Spin family turns the tower; arcs count the turns (1, 2, 3) | magenta #C81E78 (yellow) |
| Spin 2 | TOWER | Ben-Day mint, 2 arcs | same | cobalt #2A4BE0 (pink) |
| Spin 3 | TOWER | Ben-Day tangerine, 3 arcs | same | indigo #2B1F9E (cyan) |
| Brace | TOWER | linocut: cobalt plate, black radial gouges, bone scissor halo | solid, carved, protective | owner pink (black) |
| Strike | TOWER | collage: torn paper shards, halftone, tape, two bolts | impact | ink black (pink) |
| Firewall | WAVE | mural: teal night sky, skyline, spray ring | the burn belongs to the city | owner pink (yellow) |
| Pull | WAVE | linocut: green plate, straight-down gouges | a pull is a straight carved line inward | owner pink (black) |
| Shove | WAVE | collage: sliding paper strips, three speed bars | sideways slide | indigo #3A1C9E (orange) |
| Twist | WAVE | mural: violet-to-orange sunset, skyline, white ring | the ring turns around the city | violet #5B2BE0 (black) |
| Hold | WAVE | xerox: black toner, white halftone, cyan spot block | dead copier stillness for a pause | owner pink (cyan) |
| Trigger | WAVE | Jinx: night ink, neon cyan and pink scribbles | aim and lock-on | violet #7A2CFF (lime) |

Mix: Ben-Day x3, linocut x2, collage x2, mural x2, xerox x1, Jinx x1. The WPAP facets (four flat translucent planes plus one glint plane per card, seeded) are laid over every band so the set reads as one family.

## Icon approach (xerox, recoloured)
Paper-white glyph with a 2.5 px black key line and a hard black drop, on a spot-ink disc with a second ink misprinted as a crescent, then a black ring and a white scissor-cut halo with an ink drop (the linocut halo, so the icon separates from any band). Rule used for the disc colour: a warm band gets a deep cool disc (Spin 3, Shove), a cool band gets pink or magenta (Brace, Pull, Firewall, Nudge), a dark band gets pink, violet or ink.
Measured (`checks.json`), glyph fill vs disc: Strike 17.7, Spin 3 11.2, Shove 10.9, Twist 7.0, Spin 2 6.3, Trigger 5.5, Nudge 5.1, owner-pink discs 3.1 (Brace, Pull, Firewall, Hold). The pink-disc cards pass on the keyline: glyph fill vs its black key line is 17.7:1. Halo vs the art just outside it: 2.6 to 12.3; lowest are Spin 2, Strike and Nudge (about 2.6-2.8), which are carried by the black ring and the ink drop, not by the halo's value. Disc vs the art around it is hue-led on several cards (Nudge 1.9, Shove 1.5, Twist 1.4), so the ring and halo are what separate it; this is a known soft spot, not a fail of the glyph read.

## Legibility checks
- Title (all 11): Anton 38 px; only FIREWALL shrinks (34.25 px, 127 of 128 px wide). Cap height 32.7 design px = 37.6 screen px at 1.15 x (rule: >= 26 design / 30 screen); FIREWALL 29.5 / 33.9. White fill on an ink plate with a 1.4 px ink keyline (fill vs keyline 17.7:1; plate vs paper 16.0:1). One hard pink offset (2.6, 3.0), never the only edge. Capitals, tracking 1.0, rotation -2 deg, no skew, glow or gradient.
- Rules text: Plex Condensed 21 px (floor 15), ink on cream 16.0:1; every line fits 120 px at 17 px or more.
- Cost digit: 27 px Anton on the cyan hex. Type word: 19 px Anton.
- 1x (true 1920x1080 pixels): all four names, type words and rules lines read (`hand_p1.jpg`, top row).
- 320 px wide (`legibility_1x_320.jpg`): BRACE, SPIN 3, TRIGGER, TWIST read with open counters; TOWER / WAVE and the cost digits read; the rules lines are small and only partly readable (same limit as every earlier style). The nowords strip shows distinct plate widths, cost tallies and the x-tally.
- Squint check: not run (cards only here, no full plate).

## States
- normal: full value. In a hand, resting cards use `dim: 0.88`.
- hover: the caller scales the box 1.10 x; draw_card adds the pink misregistered print (-9, +6 design px) and a longer hard drop; full value. The hand pushes the cards to its right by 30 px.
- played: solid blue-grey keyline silhouette (no dash), faint glyph and PLAYED (mono); no word in nowords.
- unaffordable: dim glass, value x0.5 and chroma x0.4, two flat glass planes; no hatch (hatch is reserved for pending loss, ART CALL 51).
- nowords: bars for title, type word and rules; tally strokes for cost, Trace and multiplier; the glyph and art stay.

## Known limits
- Hover and nowords render at their own sizes (separate cache entries).
- The Ben-Day arcs, Strike bolts and Shove bars are decoration, not game data. The Spin arcs repeat the multiplier on purpose.
- The Trace tab eye is a two-shape glyph, not the system eye glyph; swap it if the assembler has one.
- Strike has a bolt glyph on a band with bolts; the band bolts could go if it reads busy.
- Rules text is left-biased (centre x 80) because the hand overlaps 20 px; the owner triangles sit bottom right and are partly covered in the hand.
- No Godot, no Blender; D: only; nothing committed.
- Process note: two `python -c` one-liners and one empty `python -` heredoc were run early (inspection only, no file effect); all real work runs from script files.
