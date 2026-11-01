# Linocut (punk concept, ART CALL 52)

## Idea
The Cell cuts its own board in lino and pulls a print: one carved black key block, one hot-pink second block printed about 1.5 px off register, bone paper, scissor-cut edges. Everything the player owns uses it: wheel, cards, SEND IT, nameplate, YOU strip. The corp stays clean lime vector, so ownership reads by technique, not just colour.
- Plate A: black key plate, pink slices, bone hub starburst, pink scissor-cut sticker halo (the ref 6 halo).
- Plate B: the reverse pull. Pink plate, black slices with pink gouges, black hub, bone halo. Darker overall (lower tower value).
- Cards: F1 black-book layout kept (cost coin top-left, big icon in an art band, title, type band, rules text, Trace tab top-right), restyled for cohesion. Titles are black Anton on bone (B: on a bone strip) with a pink off-register print, so they are easy to read. Rules text is 23 px Plex Condensed (about 25 px on screen). Hand scale 1.10, step 190 so no rules text is clipped by the next card.
- The needle is removed (patched out); the THIS TURN tape marks its own start. Sector digit 0 is now clear.

## Grammar kept (ART CALL 51)
Unchanged f1_tower functions drive: HP blocks (lit green, cross-hatch pending in the cause colour red/blue/pink), slice pips, break state hatch plus X, soak chevron, brace clamp strip, HOT/COLD/FAR threat trim, hover arcs. No dashed lines (the old hub ring ticks were removed; rim ticks are carved lenses, not a line). Arrowed outlines, enemy enamel outline, W4-W6 tickets and all numbers and rules text are the F1 board. Game colours (RAM cyan, Trace violet, harm red, soak blue, HP green) stay flat.

## Legibility risks
- Loud: pink is the largest area on screen in A (F1 had the same issue). B is calmer; prefer B if squint value matters.
- Hatch gouges (black on pink) sit near the pending red cross-hatch; both are diagonal. Pending slices keep a cleared disc around the icon and a heavier red edge to separate them.
- Black icons on pink in A and pink on black in B: contrast about 6.5:1. The shield inner panel flips to bone.
- Ink speckle is subtle at 1x; do not raise it, it will fight small text.
- Pink guns lines now touch the pink halo (A); they read by their bead ends.
- Not run: grey proof, squint metric, CVD (designer said ignore CVD). Game info only checked by eye against F1.

## Godot build
- Wheel: bake the plate, halo, rim ticks and slice bodies to textures from a gouge/hatch generator (or paint them), one atlas per variant. Slice hatch, icons, hub, halo are static Sprite2D/Polygon2D layers rotating with the tower; the misregistered pink shade is a second sprite offset (1.5, 1.1).
- Dynamic state stays shader/draw code: HP blocks and pips (existing), cross-hatch via a diagonal-stripe canvas shader clipped to the block, break X, soak chevron, trim marks.
- Cards: one 9-patch-style scissor-cut stock texture per variant, art band with a per-card icon and a shared ray texture, title in Anton with a second Label offset (2.6, 2.4) in pink as the off-register print, rules in Plex Condensed. Text is live (Label), so the localisation and numbers stay real.
- Ink grain: a single full-screen-free noise texture multiplied into the player-owned CanvasItems with a shader (speckle voids on dark, flecks on light), so it stays one draw pass per piece.
- Source: src_snapshot/lc_tower.py, lc_cards.py, lc_ui.py, lc_lib.py (patches over the F1 generator; run with lc_run.py A|B).
