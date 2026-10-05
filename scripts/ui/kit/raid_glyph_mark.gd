class_name RaidGlyphMark
extends Control
## ART-6 3A: a node's socket glyph as a small mark beside its row in YOUR NETWORK (round 21
## terminal "node" rows: the type glyph, never a tag). Draws RaidSocket.draw_glyph.

const SIZE := 20.0

var glyph: String = RaidSocket.GLYPH_RELAY
var col: Color = Palette.GAIN


func _init(p_glyph: String = RaidSocket.GLYPH_RELAY, p_col: Color = Palette.GAIN) -> void:
	glyph = p_glyph
	col = p_col
	name = "Glyph"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2.ONE * SIZE * Settings.text_scale
	size_flags_vertical = Control.SIZE_SHRINK_CENTER


func _draw() -> void:
	RaidSocket.draw_glyph(self, glyph, size * 0.5, minf(size.x, size.y) * 0.45, col)
