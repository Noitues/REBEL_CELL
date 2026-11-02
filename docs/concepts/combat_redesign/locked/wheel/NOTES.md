# Locked wheel: player family across the board (ART CALL 53, roadmap step 1)

Plates (1920x1080, bio cutaway, E10 state, same game information, nothing invented): `p1_decide.png`, `p2_preview.png`, `p2b_hover.png`, `p3_resolve.png`, `p1_nowords.png`.
Also: `wheel_crop.jpg` (spinner at 2x), `grey_proof.jpg` (p1 in grey), `wheel_crop_colour_grey.jpg` (colour next to grey, 2x), `src_snapshot/` (the new modules).
Cards are the CURRENT F1 cards, placeholders only (the WPAP card system is built in parallel). Generator: `D:/rc_scratch/combat_redesign/locked/wheel/src` (run `python lw_render.py p1|p2|p2b|p3|nowords`, then `python lw_pack.py`; ~4 min per beat, they can run in parallel).

## Player layers (xerox A + linocut key line and halo + Ben-Day shapes)
| Layer | What it is | Function (`lw_tower.py` unless noted) |
|---|---|---|
| Halo | pink scissor-cut sticker edge round the whole spinner, black chisel nicks | `page()`, `jag_ring()`, radii `R_HALO/R_KEY/R_PAPER` |
| Page | black key ring, then the paper disc with toner speckle; cyan misprint fringe and copier-lid shade dropped | `page()` |
| Slice | scissor-cut (straight, kinked) wedge: black key line 3 px + block drop, paper keyline, spot ink printed 2.8 px off register (paper sliver one side, ink over the key on the other), stencil highlight | `draw_wedge()`, `wedge_pts()`, `jag_arc/jag_path()` |
| Texture | BURST big dots (xerox), SHIELD scales (xerox), REPAIR plus crosses (xerox), TURRET Ben-Day bullseye rings centred on the icon. The xerox checker was replaced because it read as the red hatch grid | `texture()`, `tex_rings()`, `TEXKIND` |
| Icon seat (O-28) | solid slice-ink disc, paper scissor ring, black key ring, on every slice. The hatch stops at 37 px, so on a hatched slice the seat alone carries the type | `draw_seat()`, `SEAT_*`, `draw_break_state()` |
| Icon | white stencil glyph, black key line and drop (cyan ghost removed) | `draw_icon()` |
| Pending loss | cross-hatch, colour = cause (red harm, blue soak), black casing under it, X mark | `draw_break_state()` |
| Hub | pink starburst off register, black key, paper disc, bolt, ONE clean black name tile (ransom letters removed; nowords has the bolt only) | `draw_hub()` |
| HP ring, pips, brace clamp, soak chevron, margin marks, HOT/COLD/FAR trim | unchanged game marks | `xf_tower.*`, `f1_tower.draw_trim` |
| Assembler | `render_tower()` |  |

Slice inks (xerox A, unchanged): BURST #FF3DA8, SHIELD #2A58F0, TURRET #FFD21F, REPAIR #4BD67E (`xf_slices.PAL['A']`). Seats grey values in `grey_proof.jpg`: pink mid, cobalt dark, yellow and green light, so the four types separate in grey by seat as well as by texture.

## Other player-owned pieces (`lw_ui.py`)
Same family: paper body, black key line, pink scissor halo, off-register ink, scissor-cut edges.
- `nameplate()` CELL-9 tag with the pink crest disc; `you_strip()` the YOU strip with HP cells (hatch = pending loss); `send_it()` pink slab with the toner halftone, white lettering with black edge; `undo()` NEW, a paper tab with a black Z keycap (was F1 slate). Shared helpers `jag_rect()`, `sticker()`.
- The terminal hint line (`> turn_resolve.exe`) stays system text on purpose.
- UNDO is swapped in by `lw_render.stack_layer()`, which blanks the F1 UNDO box and composites `undo()`.

## Neutral corp-side base and the corp-skin hooks (`lw_skin.py`, `lw_install.py`, `cs_skin.py`)
Enemy rings, frame, rim, tickets are a clean neutral graphite enamel (no corp hue, no grit), so punk reads as the player's and clean as the corp's.
A skin is one object, `lw_skin.NeutralSkin(cs_skin.Skin)`, with a palette `pal` and one function per layer, all `(X, Y, RHO, TH) -> (rgb, alpha)` unless noted:
| Layer | Hook | Neutral treatment | Installed over |
|---|---|---|---|
| Cells (empty and unit) | `cell()` + `cell_detail()` | graphite tint 30 %, polar index lines, soft gloss, hairline edge | `R.paint_cells` |
| Landing / frame arcs | `arcframe()` | dark enamel, fine rings | `A.A2.frame` |
| Unit token frame | `token_frame()` | steel ring with ink groove | `A.W2U.halo` |
| Landing disc frame | `disc_frame()` | smaller steel ring | `A.A2.disc` |
| Bezel | `bezel()` | brushed graphite, pale lips | `A.G2.bezel_layer` |
| Landing annulus | `annulus()` | dark with fine rings | `A.G2.plate` |
| Rim | `rim()` + `rim_vector()` + `crest()` | steel band with a degree scale, six neutral roundel plates | `A.G2.plate` |
| Future-wave tickets | `ticket()` | chamfered graphite plate, pale edge | `GR.engraved_plate`, `FB.ticket` |
To make a corp: subclass `NeutralSkin` (or copy `cs_skin.Solace` / `Meridian` from `corp_skins/material/src_snapshot`), set `pal`, override the layers, and call `lw_install.install(skin)`. `lw_install.py` is the previous `cs_run.py` with the linocut dependency and the per-skin tape removed.

### THIS TURN tape (corp independent)
`lw_skin.NeutralTape.remap()`: one treatment for every corp. It maps the SCHEDULE orange fill (hue 8 to 36 degrees) to cool silver, keeping the generator's chevrons and text as tone; HOLD amber and plan yellow are untouched. `lw_install._remap()` calls it and never reads the skin, so a corp swap cannot change the tape. In Godot: one tape colour pair, not a skin token.

## Checks and open points
- Looked at all five plates and the wheel crop at 2x. Not run: the draw asserts, the game-info check, the squint metric, the dash audit (render beats were run without `check=True`).
- The pink halo is thin and mostly lost in grey; it is a silhouette cue, not a type cue.
- The silver tape and the steel rim are close in value. The rim was darkened to #74808F so the tape is the brightest corp-side element; measure before the corp skins land.
- Scissor jag on the wedges is subtle at 1x (about 1 px); misregistration (2.8 px) does read.
- Slice names in the earlier xerox key (ZERO-DAY etc.) are still unverified labels and are not used here.
- Process note: one command accidentally ran a bare `python -` with an empty heredoc; it hung, was stopped by task id, and wrote nothing. Nothing committed, nothing under D:/Godot/rebel_cell, no Godot or Blender.
