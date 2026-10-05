class_name GlyphBatch
extends Control
## Atlas glyphs (ART-1 1C, `GlyphIcon`'s atlas and shader) drawn for an immediate-mode layer: the
## layer queues `add` calls while it draws, and this child (over it, with the glyph shader's material
## for one fill / outline pair) draws them all. View only.

var _items: Array = []


## A batch over its parent, filled `fill` with the `ink` outline (Palette tokens).
static func make(fill: Color = Palette.GLYPH_FILL, ink: Color = Palette.GLYPH_INK) -> GlyphBatch:
	var b := GlyphBatch.new()
	b.material = GlyphIcon.material_for(fill, ink)
	return b


func _init() -> void:
	name = "Glyphs"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Forgets the queued glyphs (the layer calls it as it starts drawing).
func clear() -> void:
	_items.clear()
	queue_redraw()


## Queues glyph `glyph` (atlas name) with its box of `box_px` centred on `at` (parent-local), at `alpha`.
func add(glyph: StringName, at: Vector2, box_px: float, alpha: float = 1.0) -> void:
	if glyph == &"" or box_px <= 0.0 or alpha <= 0.0:
		return
	_items.append([glyph, at, box_px, alpha])
	queue_redraw()


## True when the atlas has `glyph`.
static func has_glyph(glyph: StringName) -> bool:
	return GlyphIcon.table().cell_region(glyph).size != Vector2.ZERO


func _draw() -> void:
	var t := GlyphIcon.table()
	if t == null or t.atlas == null:
		return
	for it in _items:
		var region := t.cell_region(it[0])
		if region.size == Vector2.ZERO:
			continue
		var cell := GlyphIcon.cell_size_for(float(it[2]))
		draw_texture_rect_region(t.atlas, Rect2(Vector2(it[1]) - cell * 0.5, cell), region, Color(Palette.NO_TINT, float(it[3])))
