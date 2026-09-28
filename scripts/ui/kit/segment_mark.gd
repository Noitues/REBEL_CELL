class_name SegmentMark
extends Control
## ANIM-R3 A7: the pictogram on a Rank 3 ring swap chip (the loadout view's drag chips were
## beige chips with words only): the inner ring drawn small, its segments round a hub, the
## one the chip swaps in lit (the class default: every segment plain and the hub lit). It
## sits on the chip's top-left corner like a sticker's badge, so the chip keeps its size and
## its words their room. Draw-only.

## The badge's radius at text scale 1.0 (px), how far its centre sits in from the corner
## (share of the radius), and its ring's width (share of the radius).
const RADIUS := 9.0
const INSET := 0.35
const RING_WIDTH := 0.36
## The swap's segment lit on the ring (the top one), and the gap between segments (rad).
const LIT_SEGMENT := 0
const SEGMENT_GAP := 0.16

## True for the class default chip (no segment swapped in).
var default: bool = false
var color: Color = Palette.CELL_ACID


## Puts the badge on chip button `b`; `p_default` for the class default chip.
static func attach(b: Button, p_default: bool, p_color: Color = Palette.CELL_ACID) -> SegmentMark:
	var m := SegmentMark.new()
	m.name = "SegmentMark"
	m.default = p_default
	m.color = p_color
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	m.focus_mode = Control.FOCUS_NONE
	b.set_meta(&"icon_kind", &"ring_segment")
	b.add_child(m)
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return m


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED or what == NOTIFICATION_THEME_CHANGED:
		queue_redraw()


func _draw() -> void:
	var r := RADIUS * Settings.text_scale
	var c := Vector2(r * INSET, r * INSET)
	var w := r * RING_WIDTH
	draw_circle(c, r + 2.0, Palette.INK)
	draw_circle(c, r, Palette.NIGHT_SKY)
	var n: int = RC.RING_SEGMENTS
	for k in n:
		var a0 := -PI * 0.5 + TAU * (k - 0.5) / n + SEGMENT_GAP * 0.5
		var a1 := -PI * 0.5 + TAU * (k + 0.5) / n - SEGMENT_GAP * 0.5
		var lit := not default and k == LIT_SEGMENT
		draw_arc(c, r - w * 0.5 - 1.0, a0, a1, 10, color if lit else Color(Palette.PAPER, 0.55), w, true)
	draw_circle(c, r * 0.3, color if default else Color(Palette.PAPER, 0.7))
