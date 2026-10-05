class_name SliceIcon
extends RefCounted
## A slice type's icon anywhere it is drawn (wheels, tags, cards, the FX layer, spinners, the
## Mainframe's slice tiles): since ART-2 2A the one glyph source is 1C's atlas through
## `WheelGlyphs` (`glyph_table.tres`), so a slice reads the same everywhere (audit P2: one slice
## had three icon sets). The drawn vector icons and the text symbols are gone. Draw on any
## CanvasItem; a GlyphIcon node (`GlyphIcon.make`) is the same glyph as a Control.

## Kept for the `--demo-iconstyle=N` flags of older captures: the atlas glyph has one look.
static var style: int = 4
const STYLE_NAMES: Array[String] = ["ATLAS"]


## A slice's icon on its wedge: the white glyph with its ink outline (ART_BIBLE 3.5); `r` is half
## the glyph box. `_slice_col` is kept for the callers' signature (colour never carries the type).
static func draw_on_slice(ci: CanvasItem, c: Vector2, r: float, type: int, _slice_col: Color) -> void:
	WheelGlyphs.draw(ci, GlyphTableData.key_for_slice_type(type), c, r * 2.0, Palette.GLYPH_FILL)


## The icon for `type` centred on `c` (`r` = half the box) filled with `col` over its ink outline.
static func draw_icon(ci: CanvasItem, c: Vector2, r: float, type: int, col: Color, _outline: Color = Palette.GLYPH_INK) -> void:
	WheelGlyphs.draw(ci, GlyphTableData.key_for_slice_type(type), c, r * 2.0, col)
