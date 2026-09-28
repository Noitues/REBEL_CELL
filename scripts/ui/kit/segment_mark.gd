class_name SegmentMark
extends Control
## ANIM-R3 A7: the pictogram on a Rank 3 ring swap chip (the loadout view's drag chips were
## beige chips with words only): the inner ring drawn small, its segments round a hub, the
## one the chip swaps in lit in its colour (the class default: every segment outlined and
## the hub lit). Like IconMark it gives its button an empty icon slot at the button's font
## size (so the text moves over) and draws in it. Draw-only.

## The mark's side relative to the button's font size, and its ring's width (share of
## its radius).
const SIZE_FACTOR := 1.3
const RING_WIDTH := 0.34
## The swap's segment lit on the ring (the top one), and the gap between segments (rad).
const LIT_SEGMENT := 0
const SEGMENT_GAP := 0.14

## True for the class default chip (no segment swapped in).
var default: bool = false
var color: Color = Palette.CELL_ACID
var _slot: ImageTexture = null


## Puts the mark on chip button `b`; `p_default` for the class default chip.
static func attach(b: Button, p_default: bool, p_color: Color = Palette.CELL_ACID) -> SegmentMark:
	var m := SegmentMark.new()
	m.name = "SegmentMark"
	m.default = p_default
	m.color = p_color
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	m.focus_mode = Control.FOCUS_NONE
	var clear := Image.create_empty(1, 1, false, Image.FORMAT_RGBA8)
	clear.fill(Color(0, 0, 0, 0))
	m._slot = ImageTexture.create_from_image(clear)
	b.icon = m._slot
	b.set_meta(&"icon_kind", &"ring_segment")
	b.add_child(m)
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m._fit()
	return m


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		_fit()
		queue_redraw()
	elif what == NOTIFICATION_RESIZED:
		queue_redraw()


func _px() -> float:
	var b := get_parent() as Button
	return roundf(b.get_theme_font_size(&"font_size") * SIZE_FACTOR) if b != null else minf(size.x, size.y)


func _fit() -> void:
	if _slot == null:
		return
	var px := _px()
	if Vector2(_slot.get_size()) != Vector2(px, px):
		_slot.set_size_override(Vector2i(roundi(px), roundi(px)))
		var b := get_parent() as Button
		if b != null:
			b.update_minimum_size()


func _draw() -> void:
	var b := get_parent() as Button
	var px := float(_slot.get_height()) if _slot != null else minf(size.x, size.y)
	var left := 0.0
	if b != null:
		var sb := b.get_theme_stylebox(&"normal")
		left = sb.get_margin(SIDE_LEFT) if sb != null else 0.0
	var c := Vector2(left + px * 0.5, size.y * 0.5)
	var r := px * 0.45
	var w := r * RING_WIDTH
	var ink := b.get_theme_color(&"font_color") if b != null else Palette.INK
	var n: int = RC.RING_SEGMENTS
	for k in n:
		var a0 := -PI * 0.5 + TAU * (k - 0.5) / n + SEGMENT_GAP * 0.5
		var a1 := -PI * 0.5 + TAU * (k + 0.5) / n - SEGMENT_GAP * 0.5
		var lit := not default and k == LIT_SEGMENT
		draw_arc(c, r - w * 0.5, a0, a1, 10, Palette.INK if lit else Color(ink, 0.55), w + 2.0, true)
		draw_arc(c, r - w * 0.5, a0, a1, 10, color if lit else Color(Palette.NOTE_PAPER, 0.9), w, true)
	draw_circle(c, r * 0.28, color if default else Color(ink, 0.7))
