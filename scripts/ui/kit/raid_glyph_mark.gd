class_name RaidGlyphMark
extends Control
## ART-6 3A: a node's socket as a small mark beside its row in YOUR NETWORK (round 21
## terminal "node" rows: the type glyph, never a tag): the same baked concept socket the map
## draws (RaidSocket), live or DOWN.

const SIZE := 24.0

var glyph: String = RaidSocket.GLYPH_RELAY
var down: bool = false


func _init(p_glyph: String = RaidSocket.GLYPH_RELAY, p_down: bool = false) -> void:
	glyph = p_glyph
	down = p_down
	name = "Glyph"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2.ONE * SIZE * Settings.text_scale
	size_flags_vertical = Control.SIZE_SHRINK_CENTER


func _draw() -> void:
	var box := minf(size.x, size.y)
	var r := box * 0.5 * RaidSocket.ART_HALF_PX / (RaidSocket.ART_PX * 0.5 * RaidSocket.HALF.x)
	var spec := {"glyph": glyph}
	if down:
		spec["state"] = RaidSocket.STATE_DOWN
	# the mark shows the socket alone: no bolt at row size (the chip beside it says DOWN)
	var tex := RaidSocket.texture(spec)
	if tex != null:
		draw_texture_rect(tex, RaidSocket.rect(size * 0.5, r), false)
