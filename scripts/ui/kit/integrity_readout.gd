class_name IntegrityReadout
extends Control
## B4 (round 44 `hq_node_selected.png`): a node's integrity on its terminal card at the HQ: the
## value as a bare Anton number in the node's state colour, "/ max" in the mono, and a pip bar
## (PIPS segments, the lit share = value / max). A drawn readout, never a sticker (it changes).
## View only.

## Lettering (px at text scale 1.0), the gap after the number, the pip bar's segments, a pip's
## size and the gap between pips.
const NUMBER_PX := 30
const MAX_PX := 13
const GAP := 10.0
const PIPS := 10
const PIP := Vector2(9, 14)
const PIP_GAP := 3.0
## An unlit pip's share of the colour.
const DIM := 0.22

var value: int = 0
var most: int = 1
var color: Color = Palette.CELL_ACID


func _init(p_value: int = 0, p_most: int = 1, p_color: Color = Palette.CELL_ACID) -> void:
	value = p_value
	most = maxi(1, p_most)
	color = p_color
	mouse_filter = Control.MOUSE_FILTER_PASS
	custom_minimum_size = needed_size()


## The pips lit for `v` of `m` (rounded up while any integrity is left).
static func lit_pips(v: int, m: int) -> int:
	if v <= 0:
		return 0
	return clampi(ceili(float(v) * PIPS / float(maxi(1, m))), 1, PIPS)


func _k() -> float:
	return Settings.text_scale


## The readout's size at the current text scale.
func needed_size() -> Vector2:
	var k := _k()
	var disp := Palette.display()
	var mono := Palette.mono()
	var nw := disp.get_string_size(str(value), HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(NUMBER_PX * k)).x
	var mw := mono.get_string_size("/ %d" % most, HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(MAX_PX * k)).x
	var bar := (PIP.x * PIPS + PIP_GAP * (PIPS - 1)) * k
	return Vector2(nw + GAP * k + mw + GAP * 2.0 * k + bar, disp.get_height(roundi(NUMBER_PX * k)))


func _draw() -> void:
	var k := _k()
	var disp := Palette.display()
	var mono := Palette.mono()
	var npx := roundi(NUMBER_PX * k)
	var mpx := roundi(MAX_PX * k)
	var base := disp.get_ascent(npx)
	draw_string(disp, Vector2(0, base), str(value), HORIZONTAL_ALIGNMENT_LEFT, -1, npx, color)
	var x := disp.get_string_size(str(value), HORIZONTAL_ALIGNMENT_LEFT, -1, npx).x + GAP * k
	draw_string(mono, Vector2(x, base), "/ %d" % most, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx, Palette.TEXT_MID)
	x += mono.get_string_size("/ %d" % most, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx).x + GAP * 2.0 * k
	var lit := lit_pips(value, most)
	var y := (size.y - PIP.y * k) * 0.5
	for i in PIPS:
		draw_rect(Rect2(Vector2(x + i * (PIP.x + PIP_GAP) * k, y), PIP * k), color if i < lit else Color(color, DIM))
